import ast
from executor import Executor

from llm_client import HelloAgentsLLM

PLANNER_PROMPT_TEMPLATE = """
你是一个顶级的AI规划专家。你的任务是将用户提出的复杂问题分解成一个由多个简单步骤组成的行动计划。
请确保计划中的每个步骤都是一个独立的、可执行的子任务，并且严格按照逻辑顺序排列。
你的输出必须是一个Python列表，其中每个元素都是一个描述子任务的字符串。

问题: {question}

请严格按照以下格式输出你的计划,```python与```作为前后缀是必要的:
```python
["步骤1", "步骤2", "步骤3", ...]
```
"""
class Planner:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def plan(self, question: str) -> list[str]:
        prompt = PLANNER_PROMPT_TEMPLATE.format(question=question)

        messages = [{"role": "user", "content": prompt}]

        print("正在生成计划...")
        response_text = self.llm_client.think(messages=messages) or ""

        print(f"计划已生成:\n{response_text}")

        try:
            plan_str = response_text.split("```python")[1].split("```")[0].strip()
            plan = ast.literal_eval(plan_str)
            return plan if isinstance(plan, list) and all(isinstance(step, str) and step.strip() for step in plan) else []

        except (ValueError, SyntaxError, IndexError) as error:
            print(f"解析计划时出错: {error}")
            print(f"原始响应: {response_text}")
            return []

        except Exception as error:
            print(f"解析计划时发生未知错误: {error}")
            return []
class PlanAndSolveAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.planner = Planner(self.llm_client)
        self.executor = Executor(self.llm_client)

    def run(self, question: str):
        print(f"\n--- 开始处理问题 ---\n问题: {question}")

        plan = self.planner.plan(question)

        if not plan:
            print("\n--- 任务终止 ---\n无法生成有效的行动计划。")
            return

        final_answer = self.executor.execute(question, plan)

        print(f"\n--- 任务完成 ---\n最终答案: {final_answer}")
        return final_answer


if __name__ == "__main__":
    llm_client = HelloAgentsLLM()
    agent = PlanAndSolveAgent(llm_client)

    question = "一个水果店周一卖出15个苹果，周二卖出数量是周一的两倍，周三比周二少卖5个，三天总共卖出多少个苹果？"
    agent.run(question)
