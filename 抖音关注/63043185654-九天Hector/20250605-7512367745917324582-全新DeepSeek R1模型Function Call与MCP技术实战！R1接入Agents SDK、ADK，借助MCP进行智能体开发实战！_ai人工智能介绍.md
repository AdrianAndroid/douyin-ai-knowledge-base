# 全新DeepSeek R1模型Function Call与MCP技术实战！R1接入Agents SDK、ADK，借助MCP进行智能体开发实战！#ai人工智能介绍 #mcp #deepseek #ai新星计划

> 作者：九天Hector
> 抖音号：63043185654
> 作品ID：7512367745917324582
> 创作时间：2025-06-05
> 标签：#ai人工智能介绍 #mcp #deepseek #ai新星计划

---

这是「九天 Hector」的一期 DeepSeek R1 智能体开发实战教程，时长约 1 小时 46 分。核心是讲怎么用 R1 配合 Function Call 和 MCP 协议，把模型接进 Agents SDK、ADK 这类框架，做出能调用工具的智能体。

内容主线

Function Call 基础：画面里在讲函数描述字典的写法，name 是函数名（只允许字母、数字、下划线，最长 64 字符），description 是给模型看的用途说明，parameters 用 JSON Schema 描述参数。作者强调 description 写得好不好，直接决定模型会不会正确调用。
接入框架：演示了在代码里配置模型、跑通 agent 的流程，中间还提到 Qwen-Agent 作为对照。
MCP 实战：用 MCPToolset 配置 StdioServerParameters，通过 npx 拉起 @modelcontextprotocol/server-filesystem 这个文件系统服务，把本地目录作为参数传进去，让智能体获得读写文件的能力。
效果演示：最后跑了一个对话，让智能体自我介绍，输出里能看到它自称基于 DeepSeek R1，并列出知识面、写作、编程、文件处理、联网等能力。

评论区情况 互动比较浅，主要是社交需求：不少人问「怎么加群」，作者只回了「群内聊聊」，没给具体入口；也有人提醒看进度条。没有形成技术层面的讨论。

想跟着做的话，最容易卡住的是 MCP 那段的 npx 配置和路径参数，需要我按画面把这段代码结构拆开讲讲吗？

---

> 以上内容由AI生成，仅供参考
