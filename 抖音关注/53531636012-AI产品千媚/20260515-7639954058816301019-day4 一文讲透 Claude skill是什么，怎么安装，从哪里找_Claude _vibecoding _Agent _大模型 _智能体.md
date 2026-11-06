# day4 一文讲透 Claude skill是什么，怎么安装，从哪里找#Claude #vibecoding #Agent #大模型 #智能体

> 作者：AI产品千媚
> 抖音号：53531636012
> 作品ID：7639954058816301019
> 创作时间：2026-05-15
> 标签：#Claude #vibecoding #Agent #大模型 #智能体

---

这是一条讲 Claude Skills 的科普教程，作者是「AI 产品千媚」，属于她 “Claude Code Day” 系列的第 4 天。核心观点是：Claude 本身是通用大模型，而 Skills 是 Anthropic 给出的方案，用来把通用模型稳定地改造成匹配某个专业领域的工具。视频按 “是什么、去哪找、怎么装、怎么建、和 prompt/MCP/Subagent 的区别” 这条线讲完。

Skills 是什么 最简单的 Skill 就是一个 SKILL.md 文件，分两块：YAML 格式的头部（定义名称和 description），加上正文的任务说明（本质是提示词）。作者强调 description 最关键——Claude 会拿当前任务和每个 Skill 的 description 做语义匹配，匹配上才加载。所以 description 不是介绍，而是 “触发开关”，写得越贴近你平时说话的方式，触发越准。复杂一点的 Skill 是一个文件夹：SKILL.md 是说明书，scripts/ 放可执行脚本（做数据转换等），references/ 放 PRD、API 文档等资料，assets/ 放模板、示例文档等静态资源。

去哪找

Anthropic 官方 Skills 仓库：质量高，适合新手学写法。作者常用的有 frontend design（让页面更关注审美、布局、交互，而不只是功能跑通）、办公套件（PPT/PDF/Excel/Doc）、WebAPP testing（底层是 Playwright，让 Claude 能调浏览器）。
Vercel 推出的 Skills 市场：不少公司团队官方发布，适合参考大团队怎么设计。
skills.pub：聚合目录，个人开发者居多，数量多但质量参差。

作者特别提醒安全：Skill 可能带脚本，而脚本能读文件、执行命令、访问网络。比如一个 “帮你整理文件” 的 Skill，脚本里若偷偷加了往外发送文件的命令，信息就泄露了。所以第三方 Skill 尽量选官方或高 star 的，装之前看一眼脚本内容。

怎么装 桌面版 claude.ai 里官方 Skill 已内置，在设置里点 add skills 添加即可，注意 chat 模式和 code 模式可用的 Skill 不完全一样。在 VS Code 或终端用 Claude Code，要先运行一条命令把官方仓库注册成插件市场，之后用 Plugin 选择安装；第三方 Skill 最省事的办法是把 GitHub 链接直接丢给 Claude Code 让它装。安装位置分两种：个人 Skill 只对自己生效、所有项目可用（如个人周报、PRD 写作习惯）；项目 Skill 放在项目根目录、可提交到 Git，团队拉代码后共用（如统一的需求评审标准、PRD 模板）。

怎么建、怎么测 Claude 有个专门写 Skill 的 Skill 叫 skillsCreator。动手前先想清四件事：解决什么任务、什么时候该跳出来、输出长什么样、有哪些不能破的规矩。生成后一定要测试两件事：一是用平时真实说话方式描述任务，看会不会自动触发，不触发就改 description；二是触发后输出对不对，不对就改正文里的流程、约束和示例。

什么任务值得做成 Skill 作者给了四个判断：会不会重复出现（一次性任务不值得封装）、有没有固定流程（每次临场发挥的封装也没用）、有没有明确输出标准、是不是只在特定场景需要（场景太宽泛或太窄都不合适）。

和 prompt、MCP、Subagent 的区别 作者说区别不在内容，而在解决的维度：prompt 解决 “这次怎么做”，用完就没了；Skill 解决 “这类任务永远这么做”，配置一次后自动加载。MCP 是工具连接层，扩展 Claude 能接触到什么数据（读 Jira、查 Notion、连数据库）；Skill 扩展的是拿到数据后怎么处理，两者是 “MCP 取数、Skill 处理” 的配合关系。Subagent 的关键不是 “调用了大模型”，而是有没有独立目标和自主决策权 —— 像写 PRD 时调生图模型画架构图，本质是能力封装，适合做成 Skill；需要根据目标自主决策的，才交给 Subagent。

最后作者说，Skill 越攒越多之后，Claude 会从聊天工具变成 “懂你工作节奏的协作系统”。

想继续的话，可以聊聊 Skill 和 MCP 在实际项目里怎么搭配着用，或者 skillsCreator 生成后具体怎么调 description。

---

> 以上内容由AI生成，仅供参考
