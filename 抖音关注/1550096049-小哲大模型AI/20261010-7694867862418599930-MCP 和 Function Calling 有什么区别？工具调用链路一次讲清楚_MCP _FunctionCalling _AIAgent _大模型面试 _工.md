# MCP 和 Function Calling 有什么区别？工具调用链路一次讲清楚#MCP #FunctionCalling #AIAgent #大模型面试 #工具调用

> 作者：小哲大模型AI
> 抖音号：1550096049
> 作品ID：7694867862418599930
> 创作时间：2026-10-10
> 标签：#MCP #FunctionCalling #AIAgent #大模型面试 #工具调用

---

章节要点
MCP和Function Calling在Agent架构中的职责和工作层不同。MCP负责工具的发现、接入和标准化调用，而Function Calling负责模型的工具选择和调用参数生成。两者是上下游关系，共同构成完整的工具调用链路。在生产中，MCP和Function Calling需配合使用，以实现高效的工具调用。
00:00
引言
00:26
MCP和Function...

Function Calling是LLM层能力，解决工具选择和参数生成问题；MCP是应用层协议，解决工具发现、连接和标准化调用问题。

01:16
MCP为何被认为会取代F...

媒体混淆概念，MCP标准化工具描述和发现，Function Calling仍需使用。

02:05
MCP解决的痛点

MCP解决工具接入定制化问题，实现标准化流程，但鉴权与权限控制需结合上层实现。

02:51
生产中MCP和Funct...

生产中，MCP和Function Calling配合，构成完整工具调用链路。

03:37
面试官考察的要点

面试官考察分层认知、关系理解和工程落地。

---

> 以上内容由AI生成，仅供参考
