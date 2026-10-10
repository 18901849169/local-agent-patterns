# 本地大语言模型与经典智能体范式实践

基于 Python 与 Ollama 的学习实践，包含 ReAct、Plan-and-Solve、Reflection 三种智能体流程。
从本地学习源码整理，保留核心实现，补充运行说明、异常处理和离线测试。

## 实现范围

| 模块 | 内容 |
| --- | --- |
| `llm_client.py` | HelloAgentsLLM 客户端，通过 Ollama `/api/generate` 完成本地推理 |
| `react_agent.py` | Thought-Action-Observation 循环、动作解析和工具调用 |
| `tool_executor.py` / `search_tool.py` | 工具注册与 SerpApi 搜索，密钥从环境变量读取 |
| `plan_solve_agent.py` / `executor.py` | Planner 生成计划，Executor 携带历史逐步执行 |
| `reflection_agent.py` / `memory.py` | 代码生成、评审、优化和短期轨迹记录 |

这是学习演示，Reflection 只返回生成的代码，不自动执行代码；Memory 为单次进程内记录。
模型输出需要人工核验，搜索结果可能不完整。

## 运行

需要 Python 3.10+ 和运行中的 [Ollama](https://ollama.com/)。核心代码使用标准库，无需安装 Python 第三方依赖。
如果自行安装 `python-dotenv`，客户端也可以读取本地 `.env`，该文件不应提交。

在 PowerShell 中：

```powershell
ollama pull llama3.2:latest
$env:LLM_MODEL_ID='llama3.2:latest'
$env:LLM_BASE_URL='http://localhost:11434/api/generate'
$env:LLM_TIMEOUT='120'
python plan_solve_agent.py
python reflection_agent.py
```

ReAct 的示例注册了联网搜索工具，需要自行在进程环境配置 `SERPAPI_API_KEY`，然后运行：

```powershell
python react_agent.py
```

未配置搜索密钥时，工具返回配置提示。SerpApi 请求可能产生服务费用；Ollama 模型仅在本机运行。

## 测试

```powershell
python -m unittest discover -s tests -v
python -m compileall -q .
```

11 项离线测试覆盖计划校验、历史传递、工具调用、异常 Finish、反思迭代、Ollama 请求格式和搜索失败处理。
测试使用预设模型响应及模拟 HTTP 返回，验证程序控制流程，不代表真实模型生成质量或真实搜索服务已通过联调。

## 提示词实践

Zero-shot、Few-shot、Chain-of-Thought 和纠错提示的比较方法见 [提示词实验说明](docs/prompt-experiments.md)。
未公开可复核的模型实验输出，因此不在仓库中声称准确率、性能提升或稳定性指标。

## 来源与许可

智能体结构、部分提示词和基础实现参考并改编自 Datawhale 的
[Hello-Agents 第四章](https://github.com/datawhalechina/hello-agents/tree/main/code/chapter4)。
本仓库遵循上游 **CC BY-NC-SA 4.0**，具体来源、变更和限制见 [NOTICE.md](NOTICE.md) 与 [LICENSE.txt](LICENSE.txt)。
该授权包含署名、非商业、相同方式共享要求，不等同于允许商业使用的 MIT/Apache 开源许可。

本仓库不包含个人简历、真实密钥、候选人资料或本地环境文件。
