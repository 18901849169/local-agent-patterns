# 来源与修改说明

- 上游项目：Datawhale / Hello-Agents。
- 来源：https://github.com/datawhalechina/hello-agents/tree/623d8148f83d53365e39c21cb592b62b0f8e7b1b/code/chapter4
- 许可：https://creativecommons.org/licenses/by-nc-sa/4.0/
- 本仓库整理者：饶安康。
- 本仓库为个人学习改编，不代表上游官方实现或背书。

本地实践已将模型客户端调整为 Ollama，并将规划执行、工具注册和记忆拆分为模块。
本次发布整理进一步完成以下修改：

1. 将 dotenv 设为可选依赖，搜索接口改为标准库 HTTP 调用。
2. 空执行计划显式报错，过滤非法计划步骤。
3. Plan-and-Solve 返回最终答案，避免仅打印结果。
4. 处理不合法的 Finish 动作，避免正则匹配失败后崩溃。
5. 移除执行器文件中重复且缺少 Planner 定义的智能体类。
6. 搜索失败不返回可能包含密钥的底层请求异常。
7. 补充 11 项离线测试与运行文档。

上游及修改版本按现状提供，不作保证。完整授权与免责声明见 LICENSE.txt。
