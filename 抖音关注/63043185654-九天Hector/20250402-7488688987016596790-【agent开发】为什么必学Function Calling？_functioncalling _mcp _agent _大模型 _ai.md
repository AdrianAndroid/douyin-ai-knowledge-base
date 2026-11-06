# 【agent开发】为什么必学Function Calling？#functioncalling #mcp #agent #大模型 #ai

> 作者：九天Hector
> 抖音号：63043185654
> 作品ID：7488688987016596790
> 创作时间：2025-04-02
> 标签：#functioncalling #mcp #agent #大模型 #ai

---

这是博主「九天 Hector」讲 Agent 开发学习路径的科普视频，核心观点是：从零学 Agent 开发，最该先啃的是 Function Calling，因为它是所有上层框架的底层逻辑。

作者给出的两条入门路线

低代码路线：Coze、Dify 这类平台，靠点击和拖拽就能跑通完整的 Agent 开发流程，适合先建立整体概念。
代码路线：直接用大模型原生的 Function Calling 功能搭 Agent。作者强调这部分底层调用并不复杂，是性价比最高的起点。

为什么说它是 “必学” 作者认为 LangChain、LangGraph、LlamaIndex 这些框架，本质上都是在普通 Function Calling 的执行流程上，围绕基础 Agent 理论做了更多工具和更高层的类封装，底层开发逻辑没有区别。所以先掌握 Function Calling，再上框架会轻松很多。

对 MCP 和 Multi-Agent 的判断 视频提到 OpenAI 的 Agents SDK（语音识别为 “油滴 Python”，即 OpenAI Agents Python 框架）已集成 MCP，看起来酷炫；但作者结合自己讲过的 MCP 公开课指出，用 MCP 搭智能体时，无论功能设计还是性能优化，仍是 Function Calling 逻辑下的产物。熟悉它之后，学其他框架甚至 Multi-Agent 框架都会很便捷。

一个容易误解的点：Function Calling 不是模型真的 “执行” 了函数，而是模型按约定格式输出 “要调用哪个函数、传什么参数”，真正执行代码、把结果回传给模型的是你的程序。这也是为什么它看起来简单，却是整个 Agent 循环的骨架。

画面里那张 “大模型 Agent 开发框架概览” 表格把路线分成了低代码框架、原生框架、代码框架、Multi-Agent 框架几类，和口播内容一一对应。

想继续的话，可以聊聊 Function Calling 一次完整调用循环里，模型和你的代码具体怎么来回交接。

---

> 以上内容由AI生成，仅供参考
