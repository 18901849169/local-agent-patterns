import contextlib
import importlib
import io
import json
import os
import unittest
from unittest.mock import patch


class ScriptedLLM:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.messages = []

    def think(self, messages, temperature=0):
        self.messages.append(messages)
        return next(self.responses)


class AgentTests(unittest.TestCase):
    def test_executor_rejects_empty_plan(self):
        from executor import Executor
        with self.assertRaises(ValueError):
            Executor(ScriptedLLM([])).execute('question', [])

    def test_planner_rejects_non_string_steps(self):
        from plan_solve_agent import Planner
        self.assertEqual(Planner(ScriptedLLM(['```python\n[1, None]\n```'])).plan('q'), [])

    def test_plan_solve_returns_final_answer_and_carries_history(self):
        from plan_solve_agent import PlanAndSolveAgent
        llm = ScriptedLLM(['```python\n["step one", "step two"]\n```', '15', '40'])
        self.assertEqual(PlanAndSolveAgent(llm).run('question'), '40')
        self.assertIn('15', llm.messages[-1][0]['content'])

    def test_react_calls_tool_then_finishes(self):
        from react_agent import ReActAgent
        from tool_executor import ToolExecutor
        tools = ToolExecutor()
        tools.registerTool('Search', 'test search', lambda query: f'found {query}')
        llm = ScriptedLLM(['Thought: search\nAction: Search[demo]',
                           'Thought: answer\nAction: Finish[done]'])
        agent = ReActAgent(llm, tools)
        self.assertEqual(agent.run('question'), 'done')
        self.assertIn('found demo', llm.messages[-1][0]['content'])

    def test_react_handles_malformed_finish(self):
        from react_agent import ReActAgent
        from tool_executor import ToolExecutor
        llm = ScriptedLLM(['Thought: answer\nAction: Finish without brackets'])
        self.assertIsNone(ReActAgent(llm, ToolExecutor(), max_steps=1).run('q'))

    def test_reflection_refines_generated_code(self):
        from reflection_agent import ReflectionAgent
        llm = ScriptedLLM(['original code', 'use a sieve', 'refined code'])
        agent = ReflectionAgent(llm, max_iterations=1)
        self.assertEqual(agent.run('prime numbers'), 'refined code')
        self.assertEqual(len(agent.memory.records), 3)

    def test_core_imports_without_optional_dependencies(self):
        with patch.dict('sys.modules', {'dotenv': None, 'serpapi': None}):
            for name in ['llm_client', 'search_tool', 'tool_executor', 'react_agent']:
                importlib.reload(importlib.import_module(name))

    def test_ollama_request_has_expected_payload(self):
        from llm_client import HelloAgentsLLM
        response = io.BytesIO(json.dumps({'response': 'hello'}).encode())
        with patch('llm_client.urlopen', return_value=response) as request:
            llm = HelloAgentsLLM(model='test-model', base_url='http://localhost:11434/api/generate')
            self.assertEqual(llm.think([{'role': 'user', 'content': 'hi'}]), 'hello')
        payload = json.loads(request.call_args.args[0].data)
        self.assertFalse(payload['stream'])
        self.assertEqual(payload['model'], 'test-model')

    def test_search_requires_key_without_network(self):
        from search_tool import search
        with patch.dict(os.environ, {}, clear=True):
            self.assertIn('SERPAPI_API_KEY', search('demo'))

    def test_search_prefers_direct_answer(self):
        import search_tool
        response = io.BytesIO(json.dumps({'answer_box': {'answer': '42'}}).encode())
        with patch.dict(os.environ, {'SERPAPI_API_KEY': 'test-placeholder'}):
            with patch('search_tool.urlopen', return_value=response):
                self.assertEqual(search_tool.search('demo'), '42')

    def test_search_does_not_disclose_request_errors(self):
        import search_tool
        with patch.dict(os.environ, {'SERPAPI_API_KEY': 'test-placeholder'}):
            with patch('search_tool.urlopen', side_effect=OSError('sensitive request details')):
                self.assertNotIn('sensitive request details', search_tool.search('demo'))


if __name__ == '__main__':
    unittest.main()
