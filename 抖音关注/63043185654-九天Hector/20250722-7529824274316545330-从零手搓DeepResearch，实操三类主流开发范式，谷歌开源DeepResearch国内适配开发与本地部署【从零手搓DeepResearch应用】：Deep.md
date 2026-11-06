# 从零手搓DeepResearch，实操三类主流开发范式，谷歌开源DeepResearch国内适配开发与本地部署【从零手搓DeepResearch应用】：DeepResearch应用架构设计、DeepResearch应用Chain与Graph开发流程、DeepResearch应用部署与上线流程【主流DeepResearch架构精讲】：LangChain Open DeepResearch项目部署、深度检索工作流实现方法与功能测试、Multi DeepResearch Agent实现方法与功能测试、交互式澄清意图工作流流实现方法与功能测试【谷歌DeepResearch项目实战】：gemini-fullstack-langgraph-quickstart、DeepSeek DeepResearch应用二次开发、DeepSeek DeepResearch本地部署流程、DeepSeek DeepResearch问答对话性能测试#deepresearch #deepseek #gemini #ai开发 #ai新星计划

> 作者：九天Hector
> 抖音号：63043185654
> 作品ID：7529824274316545330
> 创作时间：2025-07-22
> 标签：#deepresearch #deepseek #gemini #ai开发 #ai新星计划

---

这是一节近两小时的DeepResearch 开发公开课，主讲人（账号「九天 Hector」）的核心主张是：DeepResearch 是解决大模型 “无中生有、胡乱编造” 的最佳方案，也是当前最热门的智能体落地方式之一。课程分三块：从零手搓一个迷你版、精讲三类主流架构、部署谷歌开源项目并做国内适配。

一、为什么需要 DeepResearch 作者认为它比普通 RAG 多做三件事：把模糊问题拆成完整搜索链条、从网页或本地知识库大规模检索并汇总、回答时不断反思、发现不足就自主补搜。他给了一个新说法 ——RAG 叫 “知识检索增强”，DeepResearch 叫信息检索增强。他还引用浙大论文的界定：具备认知推理、工具集成、流程自动化中两项以上，即可算 DeepResearch 应用。

二、三类主流架构（课程重点）

深度检索工作流：线性 Pipeline，先规划、再分头检索、最后合并写长文；支持 “先确认规划、再逐步执行” 的人在闭环。
Multi DeepResearch Agent：基于 Supervisor 架构，一个监督者调度多个研究员并行检索、汇总，范围更大、速度更快。
交互式澄清意图工作流：自我反思式查询，反复优化搜索结果直到模型判断能解决问题。

三、从零手搓迷你版（实操主线） 作者用 LangChain + LangGraph 搭了三个环节：planner_chain 把问题拆成 5–20 个搜索词（每个带 reason 和 query 两个字段，用 Pydantic 结构化输出约束格式）→ search_agent 用 Tavily 逐个搜索并各写两三百字小结 → writer_chain 汇总成不少于 1500 字、10–20 页的报告，输出 short summary、markdown report、follow up questions 三段。最后把三个节点封装成图，用 LangGraph CLI 打包上线、接前端对话。他特别提醒：报告长度受模型上下文限制，换成 128K 上下文的模型后篇幅会明显变长。

四、两个开源项目

LangChain 官方 Open Deep Research：含 graph 工作流和 multi-agent 两种模式，原版在 Windows 上有小 bug，课程提供了改版源码。
谷歌 gemini-fullstack-langgraph-quickstart：GitHub 约 15.6K Stars，原版只支持 Gemini 且全英文；团队改源码接入 DeepSeek、提示词全面汉化，改名 “DeepSeek Full Stack LangGraph”。其最大特色是知识空白分析—— 判断现有信息能否构成完整逻辑链，不够就再开搜索补齐。

五、需要留意的两点 一是视频中段有较长篇幅的付费课程推广（2025 大模型智能体开发实战课夏季班），属于广告内容，不是技术讲解；二是评论区有从业者提醒：企业落地常因基础数据链路没梳理就急着上 Agent，最后卡在工程化返工，制造业、物流行业尤其常见 —— 这和课程 “先手搓再上框架” 的思路其实是一致的。

想继续的话，可以聊聊 Tavily 每月 1000 次免费额度够不够跑通这套流程，或者 Supervisor 多智能体并行检索具体怎么调度。

---

> 以上内容由AI生成，仅供参考
