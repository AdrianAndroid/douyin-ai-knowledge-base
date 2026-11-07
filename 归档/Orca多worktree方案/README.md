# Orca 多 worktree 工作方案：原理总结与归档

> 归档时间：2026-11-07T11:00:14+08:00  
> 当前状态：**已归档、永久停止用于本项目的后续提取。**  
> 后续工作方式：只使用当前主工作区 `/Volumes/wd/ai-learn`，不再创建多个 worktree 或多个 Orca worker 并行提取。

## 一、归档结论

多 worktree 方案已经完成了调研、双 worker 真实并行验证和五槽位复用试验。它证明了“分作者、分目录、分浏览器会话、协调器顺序合并”在技术上可行，但也暴露出较高的协调成本、登录与页面维护成本，以及难以彻底排除的页面超时和服务端共同限流风险。

根据用户最新决定，**后续不再采用多 worktree 工作方式**。本目录中的 GO、dispatch、Profile、page、槽位和恢复说明都只具有历史价值，不能作为新的执行授权。

归档前已经完成：

- 五个目标 worktree 均无未提交改动。
- 没有 `extract_author.py` 或 `run_next45.py` 活跃进程。
- 五个 worktree 的 HEAD 均已确认是当前本地 `main` 的祖先，已提交成果不会因删除 worktree 而丢失。
- 已通过 `orca worktree rm --force --json` 删除 A–E 五个 worktree。
- 删除后 Orca `worktree list` 返回 `totalCount=1`，只剩 `/Volumes/wd/ai-learn`；五个目录也均已确认不存在。
- 没有删除主工作区、作者文案、断点数据、Git 提交历史或 worker 分支，没有推送 GitHub。

## 二、多 worktree 的基本原理

### 2.1 Git worktree 解决的是 checkout 隔离

Git worktree 让同一个仓库同时拥有多个工作目录，每个目录可以检出不同分支：

```text
同一 Git 仓库
├── 主 worktree：main
├── worker A worktree：作者 A 分支
└── worker B worktree：作者 B 分支
```

worker 可以在自己的目录修改文件并产生提交，协调器验收后再合并到 `main`。它**不会自动隔离**：

- 写死的绝对输出路径；
- 共同使用的浏览器 page；
- 同一个作者目录的并发写入；
- 共享队列、计划或状态文件；
- 外部网站的账号、IP、频率限制。

因此，“创建了不同 worktree”本身并不等于任务已经隔离。

### 2.2 Orca worktree 还承载 agent 与浏览器工作区状态

Orca 在 Git checkout 之上管理 agent、terminal、browser tab 和 UI 状态。试验采用的完整绑定模型是：

> **一个作者 = 一个 Orca worktree = 一个独立分支 = 一个受监督 agent = 一个 isolated Profile = 一个固定 page ID**

协调器通过 dispatch 与 worker 通信，worker 在预检后等待明确 GO，完成或暂停后交回协调器验收。worker 不直接写主 checkout，也不自行 commit、merge 或领取其他作者。

### 2.3 浏览器 Profile 与 page 是两种不同的隔离

- **Profile 隔离**：隔离 Cookie、localStorage 和登录会话等浏览器状态。
- **page 固定**：确保每条浏览器命令操作指定页面，而不是跟随“当前标签页”。

所有命令必须同时携带完整 `--worktree` 和 `--page`。只传 page 不够，因为 page ID 可以跨 worktree 被找到；只创建不同 page 也不够，因为它们仍可能共享 Profile。

isolated Profile/page **不等于独立 OS 浏览器进程**，也不能保证抖音服务端不会因同账号、IP 或访问频率而限流。

## 三、保证安全执行所需的六层边界

### 1. 作者任务唯一

- 每个作者同一时间只属于一个槽位。
- 作者未 settled 前不得转交或重复领取。
- 不启动完整 `run_next45.py` 充当并行 worker。
- 共享 45 人计划/状态只读，不能由 worker 并发改写。

### 2. 文件路径隔离

- 输出必须改为当前 worktree 内的相对路径。
- 启动时断言 TMP/OUT 位于当前 checkout，且精确匹配当前作者。
- worker 只能修改该作者的 `tmp/<作者>/` 和 `抖音关注/<作者>/`。
- 总记录、调度 JSON 和 README 只能由协调器维护。

### 3. 浏览器绑定与登录隔离

- 每个 worker 使用独立 Profile 和固定 page。
- 启动前核对 worktree、Profile、page、作者主页 `sec_uid`、作者名和抖音号。
- 用无害页面实际验证 localStorage 和导航互不影响，不能只看 ID 不同就宣称隔离成功。
- 新 Profile 需要登录时，只能在原 Profile/page 扫码；不得复制默认 Profile 会话或保存 Cookie、二维码、密码。

### 4. 同一作者运行互斥

- 使用按 repo ID + 抖音号派生的排他锁。
- 第二个同作者进程必须在任何浏览器操作或目录写入前失败。
- 不能以锁文件是否存在代替真实锁状态；完成后要验证进程退出且锁可重新获取。

### 5. 明确 GO、真实并发上限与自适应小批量

- 预检通过不等于提取授权，每批都需要明确 GO。
- 五槽位虽然同时保留，真实提取并发最多为 2。
- 卡顿后把批次缩到 5 项、再缩到 2 项；稳定后才逐步扩大。
- 登录失效、验证码、限流或页面失效属于 fatal，不能靠缩小批次继续。
- `--skip-ids` 只改变当批顺序；跳过项仍是 pending，不能记为 saved/no_ai，也不能虚增进度。

### 6. 独立验收、worker 提交与顺序合并

- worker 停止后，协调器直接核验磁盘，不能只相信聊天报告。
- 检查 attempted/saved/no_ai/error、唯一 ID、Markdown 内容、pending、进度前缀、进程和锁。
- 部分批次必须保持 `partial:true`、`author_completed:false`，不得生成完整完成报告。
- 只暂存对应作者的允许目录，检查 staged 清单和 `diff --check`。
- worker 分支提交后，由协调器在本地 `main` 逐个 `git merge --no-ff`，禁止并行 merge、历史改写和破坏性清理。

## 四、实际验证得到的结果

### 4.1 双 worker 试点

- 双 Profile 的 localStorage 与导航隔离实测 **7/7 通过**。
- A/B 的真实提取时间重叠 **3 分 36 秒**，证明不是仅先后运行。
- 不纸设计：26/26 篇有效 AI 文案，独立验收、提交并合并。
- 魏起顺会拍照：根据用户现场确认，41 个作品最终记录为无 AI；早期 5 篇草稿可逆隔离，不计为有效文案。
- 两个试点的提交均已合并到本地 `main`。

### 4.2 五槽位复用试验

| 槽位 | 作者 | 最终历史状态 |
|---|---|---|
| A | 凯哥恋爱说 | 最近一批 5 项成功；累计 116 篇、621 pending。页面显示 738、实际展开清单 737，差异未解决，作者未完成 |
| B | 王小浪不浪成都恋商情感文化传播有限公司 | 累计 4 条唯一 error、491 pending、Markdown=0；连续新 ID 超时后暂停诊断 |
| C | 宋那个辞 成都恋商文化 | 页面显示 407、实际清单 409；累计 4 条唯一 error、409 pending、Markdown=0 |
| D | 做性教育的苏南 | saved=2、最新唯一 error=4、pending=108、Markdown=2；暂停诊断 |
| E | 宅男相亲记迷你版 | saved=2、最新唯一 error=4、pending=66、Markdown=2；暂停诊断 |

五槽位阶段没有新增任何一位“完整完成”的作者。A 的连续成功说明并非所有槽位或作品都必然失败，但 B/C/D/E 的集中超时不能被武断归因于并发、登录、验证码或限流。

## 五、重要教训

1. **worktree 不能修复绝对路径和共享浏览器状态。** 必须先改代码和绑定，再运行。
2. **agent 状态不等于作品结果。** “Worker stopped without reporting”常是按要求结束回合；429 也可能发生在 CLI 已完成后。最终只能以进程、锁、磁盘和独立验收为准。
3. **页面作品数与实际 ID 清单是不同数据源。** 738/737、407/409 应并列保留，不能强行改数或伪造缺失 ID。
4. **失败项和跳过项不能记成无 AI。** 保留 pending 才能避免数据被误封账。
5. **测试也可能触发真实提取。** 禁止用 `runpy` 字典打桩后直接调用内部 `run/process_one/main`；测试应使用隔离临时副本、假 Orca CLI 和真正的 CLI 子进程。
6. **扩大并发不是唯一提速手段。** 小批量、断点续提、明确验收和减少无效重试更重要。
7. **历史文档中的保留/恢复指令会过期。** 所以归档文件已统一加上停用横幅，调度 JSON 也标记为不可执行。

## 六、后续唯一工作方式

后续如继续提取，只在当前主工作区进行：

1. 一次处理一个作者，不创建额外 worktree 或并行 worker。
2. 使用当前明确指定的单个浏览器 Profile/page，操作前核对作者身份。
3. 保留同作者互斥、断点续提、小批量、真实 pending 和逐批验收。
4. 不根据旧 PID 或旧暂停文档直接恢复 `run_next45.py`；任何恢复都重新检查实际进程和状态。
5. **抖音作品页的 AI Tab 若不是自动生成，就不提取该作品。** 不手动触发生成，不记 saved/no_ai/完成，保留 pending 并记录原因；既有真实历史结果不回溯改写。
6. 不自动扩大作者范围，不自动推送 GitHub。

## 七、归档文件索引

| 文件 | 内容 |
|---|---|
| `Orca多worktree并行提取调研.md` | 最初的 Orca 能力、风险、隔离设计和验收方案 |
| `Orca双worker小批量验证记录.md` | 双 worker 从创建、隔离、登录、GO 到验收合并的完整记录 |
| `Orca五worker复用提取记录.md` | 五槽位复用、逐批 GO、卡顿缩批、错误、提交与合并记录 |
| `Orca五worker调度状态.json` | 机器可读历史快照；顶层已标记 `archived_multi_worktree_retired`，不得作为执行队列 |
| `README.md` | 本原理总结、实际结论、停用状态和后续单工作区规则 |

根目录 `当前提取任务暂停记录.md` 也已添加历史提示和本归档入口。所有原始记录保留，是为了审计和理解历史，不代表仍允许按其中步骤执行。
