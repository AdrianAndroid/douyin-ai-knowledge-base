# Orca 五 worker 复用提取记录

> 创建时间：2026-11-07T02:56:37+08:00
> 协调器：当前主会话
> Orca run：`run_573b10a4429c`
> 当前阶段：用户已完成五个槽位扫码，登录和隔离已核验；首批五位作者进入预检准备，尚未开始真实提取。

## 一、用户目标与当前范围

- 用户确认双 worker 方案可行，要求再创建 3 个 worktree，先由用户扫码登录，然后复用 5 个 worktree 依次提取剩余作者，以减少重新登录和 Profile 失效带来的中断。
- 用户补充：遇到特别卡顿或长时间不响应时，主动缩小单个 worktree 当次处理的数据量。
- 当前以既有 `后续45位作者提取计划.json` 的实际逐条状态为范围：45 位中 19 位已有 `completed`，A/B 两位已独立 settled，剩余 **24 位**。协调器曾口头误算为 23 位，已向用户更正；后续只以逐条清单和实际文件为准。
- 剩余 24 位包括旧状态为 `running` 的“凯哥恋爱说”和 23 位 `ready` 作者。凯哥已有 107 篇 Markdown 和历史进度、无完成报告；当前没有活跃旧提取进程，必须先独立审查断点，不能直接作为全新作者启动。
- 不自动扩展到 README 中此 45 人计划之外的其他作者，不恢复旧 `run_next45.py`，不修改共享 45 人计划/状态，不推送 GitHub。

## 二、五个固定槽位与浏览器绑定

| 槽位 | worktree 路径 | 分支 | Profile | 固定 page | 当前状态 |
|---|---|---|---|---|---|
| A | `/Users/zhaojian/orca/workspaces/ai-learn/pilot-buzhi-0753bjy` | 首批 `AdrianAndroid/orca-a-52327471915` | `9483ec18-4a86-4e2c-92d5-a2441a1cafb6` | `01b0f677-3907-4ee8-91d7-7f707439b8de` | 登录已核验；凯哥恋爱说预检准备 |
| B | `/Users/zhaojian/orca/workspaces/ai-learn/pilot-wei-qishun` | 首批 `AdrianAndroid/orca-b-wangxiaolangk` | `2bd87da7-ccc5-4110-b058-691269a45eef` | `eb12641b-ca19-470e-8bc2-8e9bce2aed98` | 登录、隔离探针已核验；王小浪预检准备 |
| C | `/Users/zhaojian/orca/workspaces/ai-learn/puffin` | 首批 `AdrianAndroid/orca-c-81957333169` | `888988a3-faae-454c-931b-b975a8a862c4` | `262c9f33-264f-442b-aec4-88fe21cb8f5b` | 登录、隔离探针已核验；宋那个辞预检准备 |
| D | `/Users/zhaojian/orca/workspaces/ai-learn/dugong` | 首批 `AdrianAndroid/orca-d-89017187607` | `a3385429-07ca-4470-ade7-241ede7f5697` | `a09cac76-e55d-450b-9333-8b3ab59a485a` | 登录、隔离探针已核验；苏南预检准备 |
| E | `/Users/zhaojian/orca/workspaces/ai-learn/jellyfish` | 首批 `AdrianAndroid/orca-e-54771197908` | `ffa4d1f5-6874-4817-ae7e-085f3293bb54` | `f826d2ef-8be3-469f-a41d-037a4ffeb85a` | 登录、隔离探针已核验；宅男相亲记预检准备 |

所有 worktree 的完整 selector 均为 `id:da2e8721-3aa8-432b-8a51-fb648a32632c::<上述路径>`。后续浏览器命令必须同时显式携带对应 worktree 和 page，不能只依赖当前活跃 tab。

## 三、逐步执行记录

### 步骤 1：双 worker 收尾

- A：不纸设计 26 篇有效 AI 文案；worker 提交 `12df38bd884ab3be2f48d10a64b5d788d28d9341`，本地合并 `c7732396c628ab0180b230bb3c50e7fc511b3216`。
- B：根据用户在 worker 中的现场确认，41 个作品最终均记录为无 AI；saved=0、no_ai=41、errors=0、pending=0，5 篇早期草稿可逆隔离保留。worker 提交 `27a7f4d94552d48a4f9cb5ee0b28501053324c6f`，本地合并 `d862370c55346db2e3b4e833649c7488bb081a94`。
- 双 worker 详细记录已提交到本地 main：`c9c0c85a5f5daa0c6fc2ca386044790c1988330b`。未推送 GitHub。

### 步骤 2：创建 C/D/E，仅用于登录引导

三个任务均使用受监督 Claude worker、`--worktree new-top-level`、基线 `main`；创建时基线 HEAD 均为 `d862370c55346db2e3b4e833649c7488bb081a94`。任务规格明确禁止作者导航、提取、仓库写入和 Git 操作。

| 槽位 | dispatch | task | terminal | 创建结果 |
|---|---|---|---|---|
| C | `ctx_8e1bc2a8484c` | `task_e8c3ce0170b2` | `term_d4d9e738-34a5-4fa1-9d15-248c5438b3cd` | 成功，worktree `puffin` |
| D | `ctx_d41dcf3af8c5` | `task_04db95f603a9` | `term_98a1f698-f01d-49e2-affb-36d2d21f9275` | 成功，worktree `dugong` |
| E | `ctx_d41c76500776` | `task_e9b0efbec2a4` | `term_65c33d07-1676-4919-b9f7-f9421d862991` | 成功，worktree `jellyfish` |

- 三个 worktree 的分支和 HEAD 均由协调器复查，Git 工作区干净。
- C 登录就绪消息：`msg_9fecde7ad91b`；协调器回复 `msg_fdeb9472e162`。
- D 登录就绪消息：`msg_33e0e57b3859`；协调器回复 `msg_806dc3d83990`。
- E 登录就绪消息：`msg_5e8372974390`；协调器回复 `msg_5e3077b516ac`。
- 三个 Profile 均为 isolated，均只创建一个固定 page。worker 未点击登录、未读取或保存二维码、Cookie、密码或会话凭据，未复制其他 Profile 会话。

### 步骤 3：agent 回合结束后的资源复查

- Orca 分别发出 `msg_stop_1978cadc94445d8c9fdfb782`（C）、`msg_stop_64b91cebd0e510107dbcc113`（E）、`msg_stop_e959f284990e3a4cef51f94a`（D）：agent 在等待用户扫码时结束回合，没有 `worker_done`。dispatch 仍 open；这不等于 worktree 或浏览器被删除，不重复创建资源。
- C `tab show` 请求 `5c452a24-1e24-41b8-a1e3-f719976ea494`：原 Profile/page 存在，`https://www.douyin.com/jingxuan`，loaded=true，loadError=null。
- D `tab show` 请求 `e8463032-491a-44d4-b177-8cb319e77f5a`：原 Profile/page 存在，抖音精选页正常。
- E 首次复查请求 `cc5e14e1-b895-4f6d-9de5-fa1c3d8ec516`：原 Profile/page 存在，但 URL 和 title 为空。协调器只在原 page 执行恢复导航，请求 `b1a1bb3c-ee6c-4e29-a595-402dfe9ec94e`；复查 `aa986339-0fe3-4d16-bf54-b28d1e66a26e` 已恢复抖音精选页，loaded=true，loadError=null。未新建 Profile/page。
- 用户随后明确回复“全都都扫码完成，开始”。收到确认前未分配作者，也未启动剩余作者提取器。

### 步骤 4：扫码完成后的登录、页面恢复与隔离复核

- A 登录检查请求 `203a5453-7ab5-4cb4-8801-0096b9194cae`：当前作者页有“已关注、私信”，未出现登录按钮、验证码或限流。
- B 登录检查请求 `3c274f3b-5b4d-40cb-b891-23f50c336416`：当前作者页有“已关注、私信”，未出现登录按钮、验证码或限流。
- C 登录检查请求 `81954498-3c9f-4cd3-b2fb-a781815f36cb`：有“消息、通知”，未出现登录按钮、验证码或限流。
- D 扫码后原 page 一度为 `about:blank`。协调器只在原 worktree/Profile/page 恢复抖音首页，导航请求 `d4d3b8b2-963e-460a-919c-6243ce559dde`；复查请求 `556099c9-47bd-419b-815c-2c9308445b7e` 有“消息、通知”，未出现登录按钮、验证码或限流。没有新建 Profile/page。
- E 登录检查请求 `310ef6b2-a64b-433e-8cb2-6bcdc2a00347`：有“消息、通知”，未出现登录按钮、验证码或限流。
- B/C/D/E 在同一抖音 origin 分别写入不同的非敏感 localStorage 专用测试值，各自只能读到自己的值：B=`B`、C=`C`、D=`D`、E=`E`。没有读取 Cookie 或其他既有存储。四个槽位的专用测试 key 已分别清理成功，请求为 `32cb2788-3645-44af-97a3-1c423c8eed41`、`0dc5456c-4e2c-4660-8693-4ae64613056c`、`8a503fe6-d5a0-432e-9555-c0a026a97a6c`、`e74071b2-da95-40ca-a8f4-38c9ee263b22`。
- A 的探针写入请求 `4fb5c5e3-d67a-4986-9efc-59a3ce6fcb7c` 报 `Cannot find default execution context`，因此不能宣称 A 写入了测试值；随后清理请求 `e5e37a66-b32e-4ceb-80b0-e6abc04c826b` 又报当前文档禁止访问 localStorage。A 在首批正常作者页预检时必须重新验证执行上下文，并只清理这个专用测试 key；不能写成“五槽位隔离探针全部通过”。

### 步骤 5：凯哥旧断点审计与首批独立队列

- 凯哥主页清单共 737 个唯一作品 ID；历史进度 108 行，按最新状态为 saved=107、error=1；Markdown 107 个且 ID 唯一。旧状态仍显示 running、pending=630，但实际旧提取进程为 0，且无完成报告。首批必须保留这 107 篇和历史错误并断点续提，不得从头覆盖。
- 已建立协调器单写者文件 `Orca五worker调度状态.json`，只包含本轮剩余 24 位作者。它不修改、不替代共享 45 人计划/旧状态；worker 无权写此队列。
- 首批按原 45 人计划顺序分配：A=凯哥恋爱说（`52327471915`，737 个作品，从 107 篇断点恢复）；B=王小浪不浪成都恋商情感文化传播有限公司（`wangxiaolangk`，490 个作品）；C=宋那个辞 成都恋商文化（`81957333169`，407 个作品）；D=做性教育的苏南（`89017187607`，110 个作品）；E=宅男相亲记迷你版（`54771197908`，68 个作品）。其余 19 位保持 pending，不自动领取。
- 当前队列状态为 `preflight`，首批五位为 `assigned_preflight`，active_count=0。下一步只进行分支、提取器最小改造、静态/锁测试及作者身份/登录预检；协调器逐项复核后才放行真实提取。

### 步骤 6：首批分支与五个受监督预检 worker

- 独立调度清单和本记录首先提交到本地 main：`bd02f7d`（提交信息 `建立五worker剩余作者独立调度清单`）。提交只含这两个文件，既有调研文档 SHA-256 仍为 `7a7c11857635bd9db7df6c03eab0c5b273ef55317da55b4f0705f8f442f7d781`。
- 五个原 worktree 在切分支前均干净；首批分支均从上述最新 main 基线创建，没有新建 worktree/Profile/page。
- 新任务规格保存在 `/tmp/orca-a-kaige-preflight-spec.md`、`/tmp/orca-b-wangxiaolang-preflight-spec.md`、`/tmp/orca-c-songnageci-preflight-spec.md`、`/tmp/orca-d-sunan-preflight-spec.md`、`/tmp/orca-e-zhainan-preflight-spec.md`。规格明确只有协调器的 `AUTHOR_EXTRACTION_GO` 才能放行真实提取。

| 槽位 | dispatch | task | terminal | 启动结果 |
|---|---|---|---|---|
| A | `ctx_b1f5e1508517` | `task_4ec80a8b1b81` | `term_b7115e09-4f03-4956-8b56-ecbee23d3b70` | ready |
| B | `ctx_505ffd5a8c58` | `task_64b819ccc5db` | `term_8b6e06ff-8368-4d81-a799-e36bfc876397` | ready |
| C | `ctx_f78f85235fd4` | `task_0d58aeec79d0` | `term_7063e895-d363-4c0f-92e1-8fcb63d5fbb7` | ready |
| D | `ctx_9e33cb20e7dd` | `task_df9665928b9c` | `term_db01d40f-9ce7-45fa-b599-2036e201ba98` | ready |
| E | `ctx_7060b58aff01` | `task_b597bbadc1a0` | `term_8a98e5b8-7cb2-4f23-a9e7-31ede30fd3e1` | ready |

- 当前仅 `preflight_running`，队列 active_count 仍为 0。worker 可做允许目录内的最小改造、静态/锁测试及作者身份/登录预检；真实作品提取尚未获放行。协调器等待 Orca 唤醒后逐项复核，不做无意义轮询。

### 步骤 7：E 预检独立复核与单项放行

- E 通过 `msg_3b509921ace3` 报告 `AUTHOR_PREFLIGHT_READY`。协调器读取其预检状态、浏览器绑定和执行记录，检查完整脚本/配置 diff、git status 与 diff-check；改动仅在宅男相亲记允许目录，输出目录尚未创建，真实提取尚未发生。
- 协调器独立 `tab show` 请求 `31efba45-f3ad-4360-85fc-9a76ee96d8ce`：URL/sec_uid 匹配，标题为“宅男相亲记迷你版的抖音”，Profile/page/worktree 均与 E 固定绑定一致，loaded=true、loadError=null。worker 的身份记录还包含抖音号 `54771197908`、已关注、作品 68、登录有效及无验证码/限流。
- 锁测试实际退出码 1，第二实例在浏览器操作和输出前因排他锁失败，测试后锁释放；缺环境变量及非法 max-items 也分别按预期失败。协调器据此只放行 E。
- 首次较长回复被权限分类器拒绝，没有送达；改用简短的同授权回复后成功，消息 ID `msg_f6cb3e043c07`。授权内容仅为 `AUTHOR_EXTRACTION_GO slot=E douyin_id=54771197908`，并要求继续遵守自适应批次和验收闸门。队列 active_count 更新为 1，其他槽位未获放行。

### 步骤 8：A 的 GO 前 2 项测试偏差、部分批次验收与重新预检

- A 通过 `msg_0c297077d1db` 报告 `AUTHOR_PREFLIGHT_BLOCKED`：离线测试错误地用 runpy 字典替换函数全局并直接调用 `run(2)`，测试替身未生效且绕过 main 锁，导致未收到 GO 时真实处理 2 个作品。worker 随即停止，没有继续作者身份/登录预检。
- 协调器独立核验：新增 ID `7693863248113732902`、`7664138045670591796` 均属于 737 个主页清单，正文作者/抖音号/作品 ID/日期/AI 标记完整；当前 109 个 Markdown、109 个唯一 ID、110 行进度、最新 saved=109、pending=628，状态 running=false、partial=true、author_completed=false，无完成报告，进程为 0，锁可重新排他获取。
- 原 107 篇组合 SHA-256 仍为 `510d10968b606dcea7479c0b4e08d219d15e0744eea5f568bead962c5fdb7fce`，与主 checkout 原有文件一致；原 108 行进度前缀 SHA-256 仍为 `471ae61ced3d6d08a4b2e12f65e519a63ee1c2248ed275886c0d39a36218ee30`。没有删除或改写历史成果。
- 将这次意外运行如实作为 2 项部分批次保留，而不是伪装成预检通过或作者完成。staged 仅凯哥 TMP/OUT 10 个文件，diff-check 通过；worker 提交 `b05aa84c752aa0f09351e1e88df1bdd023c7fd09`，本地 main 顺序合并 `7d0f3d0186b3339570e219db4e9da2f56e16ac9e`。合并后 109 篇组合哈希 `1c0986e45783fab1c81e22e3e46f7ba65817700327102c4bf14b448a34db9266` 完全一致，pending 仍为 628。
- 首次合并长命令被权限分类器拒绝且未执行；拆成逐条 stage、检查、commit、merge 后成功，没有绕过文件边界。
- 已在原 worktree 从合并后的 main 建立 `AdrianAndroid/orca-a-52327471915-preflight2`，回复 `msg_1a9672867979`：只允许重新预检，测试必须经 CLI 子进程，禁止直接调用 run/process_one 或真实处理；补齐身份、登录、JS 上下文和锁测试后再次 ask。A 仍未获得真实提取 GO。

### 步骤 9：C/D 放行，B 的作品数差异修正闸门

- B `msg_01f0cd750d62`、C `msg_3e01798c6d80`、D `msg_a63484a24de3` 分别报告预检就绪。协调器读取三份预检状态，检查各自完整提取器 diff、git status 和 diff-check；所有改动都只在对应作者 TMP，未创建输出目录或开始真实提取。
- 独立 tab 复核：B 请求 `2129f400-3e9c-4f68-b4ab-1bdbcbe918e5` 为王小浪精确 sec_uid、固定 Profile/page；C 请求 `b20a8862-c442-4dc0-b7a5-56838f43db3b` 为宋那个辞精确 sec_uid、固定 Profile/page；D 请求 `389b7470-a3d7-4e77-819b-77ca5c9d75a8` 为苏南精确 sec_uid、固定 Profile/page。三者 loaded=true、loadError=null，标题均匹配。
- C 的作者名、抖音号 `81957333169`、作品 407、已关注和登录均匹配；重复实例退出 73 且未访问浏览器/写输出。回复 `msg_8e66ccef04d4` 发放仅限 C 的 GO。
- D 的作者名、抖音号 `89017187607`、作品 110、已关注和登录均匹配；锁测试、环境缺失测试和输出边界通过，代码含连续两次超时和约 5 分钟停滞停止条件。回复 `msg_3c4a1c229eb3` 发放仅限 D 的 GO。
- B 身份、登录、路径和锁均通过，但页面当前作品数为 **491**，配置及旧计划快照为 **490**。为避免最终报告继续使用旧数量，回复 `msg_0f1d36b1a172` 要求只更新本作者配置和预检证据为 491，保留 490→491 的差异记录，不改共享队列；重新检查后再次 ask。B 尚未获 GO。
- 当前真实提取槽位为 C/D/E，active_count=3；A 重新预检中，B 修正预检中。

### 步骤 10：B 放行，A 增加仅 ID 刷新闸门

- B 通过 `msg_1694b6567cd9` 报告 490→491 修正完成。协调器独立读取配置和预检状态，确认二者均为 491，保留旧快照 490 的差异记录；输出仍不存在、Markdown=0，重复锁测试和相对路径复测通过，变更仍只在王小浪 TMP。回复 `msg_48834b2e1a6f` 发放仅限 B 的 GO。
- A 通过 `msg_b9175c3c4df2` 报告安全重预检完成：这次所有提取器测试均经 CLI 子进程，没有直接 run/process_one；109 篇及进度/pending/summary 哈希在测试前后不变。正常作者页身份、已关注、登录和 JS 执行上下文均通过，专用 window 测试 key 写入/读回/删除成功，未读取 Cookie/存储/凭据。
- 协调器独立 A tab 请求 `c2826337-597d-4d86-a26b-8a696f2cf0bb`，凯哥 sec_uid、Profile/page/worktree 均匹配，loaded=true。
- 但 A 页面当前作品数为 **738**，固定断点清单仍为 **737**。为避免漏掉新增作品，回复 `msg_9d2096fe6a3a` 要求实现独立 CLI `--refresh-ids-only`：必须由 main 持锁并核验浏览器绑定，只采集 ID，不调用 run/process_one、不读取 AI 正文；新清单必须 738 唯一且完整包含旧 737，否则不得覆盖。代码及无浏览器测试后须再申请 `AUTHOR_ID_REFRESH_GO`，当前既未授权刷新也未授权真实提取。
- 当前 B/C/D/E 四路真实提取，active_count=4；A 处于 ID 刷新修正阶段。

## 四、复用与防冲突规则（后续任务必须执行）

1. **固定浏览器资源**：复用上表 5 个 worktree/Profile/page。登录失效时只暂停对应槽位并让用户在原 Profile/page 重新扫码，不通过新建 Profile 绕过。
2. **受监督复用**：仍 open 的 dispatch 使用 `orchestration send` 继续；需要新 agent 时，用 `worker-start --worktree id:<完整ID>` 在现有 worktree 创建受监督 agent，不创建额外 worktree。
3. **一个槽位一个作者**：同一时刻一个槽位只能领取一个作者；同一作者跨 worktree 使用 `/tmp` 排他锁。作者未 settled 前仍归原槽位，不被其他槽位抢走。
4. **每作者独立分支**：开始下一作者前，确认上一任务进程退出、锁释放、工作区干净，再从最新本地 main 创建新的作者分支。禁止 `reset --hard`、`clean -fd`、历史改写和并行 merge。
5. **严格路径边界**：worker 只能修改分配作者的 `tmp/<folder>/` 和 `抖音关注/<folder>/`，输出必须是当前 worktree 相对路径；协调器只暂存这两个目录。
6. **逐作者验收与合并**：每个完整或自适应小批次结束后，协调器独立核验进程、锁、ID 集合、正文/无 AI 状态、pending、路径和 whitespace，再提交 worker 分支并用 `--no-ff` 顺序合并本地 main。部分批次必须 `partial:true`，不得生成作者完成结论。
7. **总记录单写者**：只有协调器写本文件和后续五 worker 调度状态；worker 各自写分配作者目录内的执行证据，不写共享队列、README 或其他作者目录。
8. **登录与安全停止**：登录失效、验证码、限流、页面失效或作者身份不符立即停止对应槽位并保留断点；不索要密码，不保存 Cookie、二维码或会话凭据。
9. **不推送**：所有提交和合并仅存在本地，除非用户以后明确要求推送。

## 五、自适应小批量规则（用户 2026-11-07 补充）

- 正常响应时按作者完整模式断点续提，不预设 2/30 个上限。
- 连续 2 次浏览器操作超时，或约 5 分钟没有实质作品进展时，不继续扩大重试；在当前作品安全收尾并原子保存进度后停止当批。
- 下一批缩小到最多 5 个作品；仍明显卡顿则缩小到最多 2 个。缩小的是当次工作量，不是放弃剩余作品。
- 每批如实记录 attempted/saved/no_ai/errors/pending、起止时间、慢响应证据和下一批建议。剩余作品必须保留在 pending，`partial:true`、`author_completed:false`。
- 页面恢复稳定后，可从 2/5 个逐步扩大；只有完整清单无 pending 且校验通过，才能写 `partial:false` 和作者完成报告。
- fatal 登录、验证码、限流或页面失效不属于“缩小批量后继续”的情况，必须立即停止。

## 六、当前验收状态

- [x] 原有 A/B 两个 worktree、Profile、page 保留。
- [x] 新增 C/D/E 三个受监督 worktree，基线干净。
- [x] C/D/E 各有独立 isolated Profile 和固定 page。
- [x] 新登录阶段未提取作者、未写仓库文件、未 commit/merge/push。
- [x] 用户完成五个槽位扫码。
- [x] 协调器逐一核验五个槽位当前登录状态与绑定；D 空白页已在原资源恢复。
- [x] B/C/D/E 隔离探针通过；A 写入失败已如实记录，待正常作者页重新预检。
- [x] 审查凯哥旧断点，建立不含共享计划写入的 24 位独立调度清单。
- [ ] 首批五作者在独立分支完成提取器改造、静态/锁测试和作者预检。
- [ ] 协调器逐项放行后执行真实提取，并落实卡顿时缩小批量。
- [ ] 每作者或批次独立核验、提交并顺序合并。
