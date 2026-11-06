# 五 worker 槽位 A 执行记录：凯哥恋爱说

- run：`run_573b10a4429c`
- task：`task_4ec80a8b1b81`
- dispatch：`ctx_b1f5e1508517`
- 当前阶段：已知 737 清单的两项部分批次已完成并停止：精确主页/绑定/登录/JS 预检通过，唯一一次 `--max-items 2` exit=0，新增保存指定两个 ID；现为 111 篇、112 行进度、pending=626。737 与页面显示 738 的差异保留，`partial:true、author_completed:false`，未获后续 GO 不续提。
- 允许边界：仅当前 worktree 的 `tmp/52327471915-凯哥恋爱说/` 与 `抖音关注/52327471915-凯哥恋爱说/`；主队列只读；不执行 Git 写操作。

## 1. 修改或运行前的独立断点基线

记录时间：`2026-11-07T03:20:36+08:00`。

- 实际 cwd：`/Users/zhaojian/orca/workspaces/ai-learn/pilot-buzhi-0753bjy`
- 完整 worktree selector：`id:da2e8721-3aa8-432b-8a51-fb648a32632c::/Users/zhaojian/orca/workspaces/ai-learn/pilot-buzhi-0753bjy`
- branch：`AdrianAndroid/orca-a-52327471915`
- HEAD：`bd02f7db94d3ce5ce2af1094a1a12b60e9abfb06`
- 基线 `git status --porcelain=v1 --untracked-files=all`：空输出，退出码 0。
- `worktree show` 请求 ID：`0fd8b648-b111-4f14-8980-562973e4d7e0`；selector、路径和 branch 均匹配。
- `主页作品ID.json`：737 条，737 个唯一 ID。
- Markdown：107 个文件，107 个唯一作品 ID；无无效文件名，无清单外 ID。
- `提取进度.jsonl`：108 行，按 ID 最新状态共 108 个 ID，其中 `saved=107`、`error=1`。
- 唯一历史错误：作品 `7693863248113732902`，`empty AI text`；保留该历史错误，断点续提时可正常重试。
- 按最新 saved/no_ai 计算 pending：630。
- 活跃进程审计：按 `ps` 的进程 command 含 Python 且参数含 `extract_author.py`/`run_next45.py` 过滤，结果为空；未把旧 `running:true` 当成活进程。
- `/tmp` 修改前未发现名称含 `52327471915` 的锁文件，因此未发现本作者锁被持有。
- 首次只读审计命令退出码 1：`ps` 输出含非 UTF-8 字节，Python 解码报 `UnicodeDecodeError`；改用 `errors='replace'` 后同一审计退出码 0，以上数据来自成功命令。
- 未运行旧 `run_next45.py`，未运行提取器，未访问抖音进行提取，未修改作者正文或历史进度。

### 基线 SHA-256

- `主页作品ID.json`：`e733688712fb0ae0cf90eb87789ccf384cdc9145d86a1e9100a7f05c8272ed3b`
- `待补提作品.json`：`e733688712fb0ae0cf90eb87789ccf384cdc9145d86a1e9100a7f05c8272ed3b`
- `提取进度.jsonl`：`471ae61ced3d6d08a4b2e12f65e519a63ee1c2248ed275886c0d39a36218ee30`
- `提取状态.json`：`f1b5a8ef9237d89aeb66f00d044b8a0a7b8c8643cf3ba092d130b5782fbec50c`
- 107 个 Markdown 按排序后的“文件名 + NUL + 内容 + NUL”组合哈希：`510d10968b606dcea7479c0b4e08d219d15e0744eea5f568bead962c5fdb7fce`

## 2. 固定浏览器初始绑定

- 固定 Profile：`9483ec18-4a86-4e2c-92d5-a2441a1cafb6`
- 固定 page：`01b0f677-3907-4ee8-91d7-7f707439b8de`
- `tab list` 请求 ID：`acc724b7-477e-40b1-93b0-a1cf5ea2c2e3`。
- 返回值确认该 page 属于上述完整 worktree，profileId 与固定 Profile 完全一致，`loaded=true`、`loadError=null`。
- 初始页面仍是“不纸设计”的旧作品弹层；尚未据此推断凯哥身份或登录状态，后续必须导航到队列中的精确凯哥 profile_url 再核验。
- 协调器队列只读结果：凯哥 sec_uid 与配置一致，精确 profile_url 为 `https://www.douyin.com/user/MS4wLjABAAAAuZMYFu2QHmJpCAQzWoUtW4KyHf93Lgp7Di9T_AZ7fyDbiRQmA9NkMzpWHOLNFbc2?from_tab_name=main`。
- 队列记录 A 的旧隔离探针在写值前失败；本记录不宣称旧页面清理成功，也不宣称五槽位探针全部通过。

## 3. 最小改造与离线测试

已完成分配目录中的最小改造：

- `TMP=Path(__file__).resolve().parent`，`ROOT=TMP.parent.parent.resolve()`；配置 output 改为 `抖音关注/52327471915-凯哥恋爱说`。
- 路径断言实际退出码 0，解析 OUT 严格为 `/Users/zhaojian/orca/workspaces/ai-learn/pilot-buzhi-0753bjy/抖音关注/52327471915-凯哥恋爱说`，TMP/OUT 均在 ROOT 内。
- 配置已删除共享 page；未写入 Profile、page 或其他激活浏览器 ID。`ORCA_WORKTREE`、`ORCA_PROFILE`、`ORCA_PAGE` 仅读环境。
- 三项环境分别缺失时，实际退出码均为 1，stderr 均明确包含 `RuntimeError: missing required environment variable: <变量名>`。
- AST 语法解析和配置 JSON 解析通过；未生成 pyc。
- `eval` 调用同时带完整 `--worktree` 与固定 `--page`；`tab list` 使用完整 `--worktree`（该命令不接受 page）。提取器启动时核验 page 的 worktreeId/profileId。
- 锁路径：`/tmp/orca-author-extract-da2e8721-3aa8-432b-8a51-fb648a32632c-52327471915.lock`。正常 `main()` 在任何浏览器操作或作者输出写入前获取 `LOCK_EX|LOCK_NB` 并持有到退出。
- 重复启动锁测试由父进程真实持有该 flock，再启动实际提取器；同时将 `ORCA_CLI_COMMAND` 设为 `/definitely/missing/orca-lock-test` 作为不得访问浏览器的兜底。第二进程实际退出码 **73**，stdout 为空，stderr 为：
  `ERROR: author extraction lock is already held: /tmp/orca-author-extract-da2e8721-3aa8-432b-8a51-fb648a32632c-52327471915.lock`
  此锁测试未访问抖音，未写作者输出。
- `--max-items N` 仅接受正整数；省略为正常全量断点续提。部分批次写真实 pending、`running:false`、`partial:true`、`author_completed:false`，不生成完整校验/完成报告。完成报告只在 737 个唯一清单无 pending 且完整校验通过时生成。
- 正常入口的已有 saved/no_ai 会跳过；已有文件不会覆盖；历史进度按 ID 最新状态计数。没有运行旧 `run_next45.py`。

### 严重测试偏差与立即停止

在后续尝试用 `/tmp` 临时目录测试 `--max-items 2` 时，错误地直接调用了 `run(2)`。`runpy.run_path` 返回字典上的更新没有替换函数全局，测试替身因此未生效；直接调用又绕过了 `main()` 中的锁和绑定核验，导致真实 `process_one` 在**未收到 GO**时运行。

- 真实 `run(2)` 返回码 0；外层测试随后因从临时目录读取 `提取状态.json` 失败而退出码 1，报 `FileNotFoundError`。这不是离线测试通过。
- 意外批次实际 `attempted=2、saved=2、no_ai=0、error=0`，pending 从 630 变为 628。
- 意外保存作品 `7693863248113732902`（原历史错误重试成功）和 `7664138045670591796`。
- 新增且保留、未回滚：
  - `抖音关注/52327471915-凯哥恋爱说/20261007-7693863248113732902-拥有这种性格的男生八成都是恋爱脑.md`，SHA-256 `1b773a0686b41267df3bac8eec0a111e2f745e0d272eec0428afbe13483ff84e`。
  - `抖音关注/52327471915-凯哥恋爱说/20260719-7664138045670591796-男人必备的九个顶级本领.md`，SHA-256 `f2480f42921233a55ef74f571316cdb69f7002d166534da6e06d58b4e93824cf`。
- 意外运行未持有上述 flock。发现输出指向真实作者目录后已立即停止；没有继续任何提取或浏览器检查。
- 事后 `ps` 未发现活跃提取进程；`lsof` 对锁文件无输出。实际状态为 `running:false、partial:true、author_completed:false`；未生成 `文案校验.json` 或 `提取完成报告.json`。
- 当前为 109 个 Markdown、109 个唯一 ID，进度 110 行，按 ID 最新状态 `saved=109`，pending=628。737 个清单 ID 仍唯一且哈希未变。
- 原 107 篇正文组合哈希仍为 `510d10968b606dcea7479c0b4e08d219d15e0744eea5f568bead962c5fdb7fce`，原 108 行进度字节前缀哈希仍为 `471ae61ced3d6d08a4b2e12f65e519a63ee1c2248ed275886c0d39a36218ee30`；即原正文和历史进度均未改写，变化仅为追加及派生 pending/summary 更新。
- 当前进度 SHA-256 `b5f4d655a136bbde22741e23d304662beec05a544eccdf2f4e1187868ebd3258`；pending SHA-256 `8026fba4c95925b368f29948cc6719a22b4cd52974bd17dc14b7f0e65330ac8a`；summary SHA-256 `0466e7cbf7577517b28e9bbdc55456c9e47ea84f090bb5705c163000dc1a64fe`；109 篇组合哈希 `1c0986e45783fab1c81e22e3e46f7ba65817700327102c4bf14b448a34db9266`。

## 4. 正常作者页身份、登录和 JS 上下文检查

因上述 GO 前真实提取偏差，已按停止原则中止后续预检。没有完成正常作者页的作者名、抖音号、sec_uid、已关注和登录状态独立核验；没有重新执行 A 的 JS 隔离探针，没有清理旧测试 key，也不宣称旧页面清理或五槽位探针成功。意外 `process_one` 的页面返回不能替代这些预检。

## 5. 首次预检结论

**AUTHOR_PREFLIGHT_BLOCKED**。未收到 `AUTHOR_EXTRACTION_GO`，但离线测试偏差意外处理了 2 个作品；现已停止，所有实际变化保留并记录。Git 写操作为零，主队列、其他 worktree、其他作者及共享计划/记录均未修改；当前变化均在允许的 TMP/OUT 边界内。等待协调器决定如何处置这 2 个意外新增结果及是否/如何重新预检，不自行继续。

## 6. 协调器接受部分批次后的重新预检（preflight2）

记录时间：`2026-11-07T03:44:00+08:00`。

- 协调器回复 `AUTHOR_BATCH_ACCEPTED`：此前 2 篇已独立核验并作为 partial 批次合并，禁止删除。worker commit=`b05aa84c752aa0f09351e1e88df1bdd023c7fd09`，merge=`7d0f3d0186b3339570e219db4e9da2f56e16ac9e`。
- 当前 branch=`AdrianAndroid/orca-a-52327471915-preflight2`，开始 HEAD=`7d0f3d0186b3339570e219db4e9da2f56e16ac9e`；记录前 Git status 为空。worker 未执行任何 Git 写操作。
- 接受后的断点为：737 个清单 ID 且唯一，109 个 Markdown 且唯一，进度 110 行，按 ID 最新 `saved=109`，pending=628；未删除或回滚 2 篇。
- 本次所有提取器测试均为独立 CLI 子进程；未使用 runpy，未直接调用 `run` 或 `process_one`。所有提取器测试均把 Orca 可执行路径设为 `/definitely/missing/orca-preflight2`，因此不能访问真实浏览器。
- 独立 CLI 静态语法/JSON/路径检查退出码 0：output 为 `抖音关注/52327471915-凯哥恋爱说`，解析严格等于当前 worktree 的对应目录；TMP/OUT 在 ROOT 内，配置无 page/profile。
- 完整环境下 CLI `--help` 退出码 0；三项环境分别缺失均退出码 1，并明确报告缺失变量。
- 父进程持锁后，第二实际 CLI 子进程退出码 73，stdout 空，stderr 为 `ERROR: author extraction lock is already held: /tmp/orca-author-extract-da2e8721-3aa8-432b-8a51-fb648a32632c-52327471915.lock`。
- 无父进程持锁时，单 CLI 子进程因不存在的 Orca 路径按预期退出码 1，最后一行为 `FileNotFoundError: ... '/definitely/missing/orca-preflight2'`；随后父进程能立即非阻塞获得锁，证明子进程退出后锁已释放。
- 全部 CLI 测试前后，737 ID 清单、pending、进度、summary 和 109 篇 Markdown 组合哈希完全不变：ID=`e733688712fb0ae0cf90eb87789ccf384cdc9145d86a1e9100a7f05c8272ed3b`，pending=`8026fba4c95925b368f29948cc6719a22b4cd52974bd17dc14b7f0e65330ac8a`，进度=`b5f4d655a136bbde22741e23d304662beec05a544eccdf2f4e1187868ebd3258`，summary=`0466e7cbf7577517b28e9bbdc55456c9e47ea84f090bb5705c163000dc1a64fe`，109 篇组合=`1c0986e45783fab1c81e22e3e46f7ba65817700327102c4bf14b448a34db9266`。

### 正常作者页身份与登录

- 初始绑定检查请求 ID=`c6ec844b-5a9c-4652-aa1e-6719712ec2ce`，固定 page 的 worktreeId/profileId 均匹配。
- 用完整 worktree selector + 固定 page 导航到队列精确 profile_url，请求 ID=`14be2cdf-df2d-4399-8aa1-bf011217f74f`。页面直接显示“凯哥恋爱说”、`抖音号：52327471915` 和“已关注”。
- 身份检查 eval 请求 ID=`4273199c-c8b1-4987-9c61-65bd3721ce32`：`readyState=complete`，最终 URL 中 sec_uid 与队列完全一致，标题为“凯哥恋爱说的抖音 - 抖音”；作者名、抖音号和已关注均通过。
- 登录证据：`已关注=true`、登录按钮=false，投稿/消息/通知入口均存在；验证码/安全验证及限流/频繁操作文案均未发现。
- 页面当前显示“作品 738”，固定断点清单仍为 737。未自行扩清单、未点击或处理新增作品，已向协调器报告该差异。

### JS 上下文与 tab/Profile 绑定

- 专用 window key=`__orcaFiveWorkerSlotAProbe_preflight2`；eval 请求 ID=`9c6bda5c-e307-4959-ac32-f15659d7f916`。
- 写入前不存在该自有 key；写入并读回预期值成功，delete 返回 true，删除后自有 key 不存在。同一返回中的 URL、origin 和作者名均匹配凯哥页面。
- 未读取 Cookie、本地/会话存储、其他槽位值或任何会话凭据；仅创建并清理上述本次专用 window key。
- 最终 tab list 请求 ID=`4d9ea507-1733-4aa8-95aa-64d343092205`：固定 page、完整 worktree、固定 Profile、凯哥精确 URL 和标题全部匹配，`loaded=true`、`loadError=null`。
- 这仅证明槽位 A 当前 JS 上下文及绑定通过；不宣称旧页面清理成功，不宣称五槽位探针全部通过。

### 重新预检结论

**AUTHOR_PREFLIGHT_READY slot=A douyin_id=52327471915**。同作者活跃进程为 0；最终 `lsof` 锁文件退出码 1 且无输出，锁未持有。重新预检没有真实作品处理，没有生成完整校验或完成报告。等待协调器明确 `AUTHOR_EXTRACTION_GO slot=A douyin_id=52327471915`，在此之前不启动提取、不发送 worker_done。

## 7. ID 刷新模式实现及无浏览器测试（等待 AUTHOR_ID_REFRESH_GO）

协调器随后回复 `AUTHOR_ID_REFRESH_FIX_REQUIRED`：页面 738、断点清单 737，不能漏掉新增作品；当前只授权实现和测试 `--refresh-ids-only`，尚未授权真实刷新或真实提取。

### 实现边界

- CLI 新增互斥参数 `--refresh-ids-only` 与 `--max-items`；同时使用退出码 2。
- `main()` 在任何刷新逻辑前持有同作者 `LOCK_EX|LOCK_NB`，随后执行 `verify_browser_binding()`；只有成功后才进入 `refresh_ids_only()`。
- 刷新模式的唯一页面采集调用为 `collect_profile_ids(persist=False, expected_count=738)`；不调用 `run` 或 `process_one`，不点击作品、不打开 modal、不读取 AI 正文。
- 刷新前先验证旧清单为当前配置的 737 个唯一 ID。采集后必须同时满足：新清单恰好 738、738 唯一、完整包含旧 737、恰好新增 1 个；任一不满足即非零退出，不写 ID、pending、配置、summary、账号核对或刷新证据。
- `persist=False` 时 `collect_profile_ids` 不再提前写账号核对或 ID 文件。验证通过后才通过既有 `write_json` 逐文件原子替换 ID、pending、配置、派生 summary、账号核对及 `ID刷新证据.json`；配置只改 `profile_work_count=738`，不写浏览器 ID。
- 历史进度只读，证据记录其前后 SHA-256；正文不写。成功后 summary 保持 `running=false、partial=true、author_completed=false`，pending 按新清单和历史 saved/no_ai 真实重算。

### CLI 无浏览器测试

- 所有目标提取器执行均为独立 CLI 子进程；未导入或直接调用内部函数。参数、环境和锁测试的 Orca 路径为 `/definitely/missing/orca-refresh-test`，不可能连接浏览器。
- AST 语法检查 exit=0；CLI help exit=0 且包含 `--refresh-ids-only`；refresh 与 max-items 互斥 exit=2。
- 三项环境分别缺失均 exit=1；重复启动锁测试 exit=73，stdout 空，stderr 明确锁已持有；单进程因不存在 Orca 路径按预期 exit=1，退出后锁可立即重新获取。
- 上述测试前后真实作者的 ID、pending、进度、summary、配置和 109 篇正文组合哈希完全不变。配置当前 SHA-256=`f67222acf6e1fd54f19fc5c631196e21d196b9e1ef878d8712db12b68018fefe`，其余哈希与第 6 节相同。

### 临时副本 + 假 Orca CLI 端到端测试

测试复制提取器及数据到 `/tmp` 新临时目录，通过实际 CLI 子进程和假 Orca 可执行文件模拟 tab list 与 ID 收集响应；未连接真实浏览器，未触碰真实作者输出，测试后临时目录自动清理。

成功用例（旧 737 + 1 个新 ID）：

- exit=0；4 次滚动读取达到稳定，最终 `COLLECTED profile=738 actual=738 persist=False`。
- 新清单 738 且唯一，完整包含旧 737，仅新增测试 ID `7999999999999999999`；pending=629，配置数=738，无浏览器 ID。
- 进度哈希不变；summary=`profile_work_count:738、pending:629、running:false、partial:true、author_completed:false`。
- 证据记录 progress 未变、`process_one_called=false`、`ai_text_read=false`；无 `.tmp` 遗留。
- 假浏览器共 8 次 eval，未出现 `__EXPECTED_VIDEO_ID__`、`__batchPause` 或 `modal_id`，证明未进入作品处理/AI JS。

失败用例（738 个唯一但缺 1 个旧 ID、增加 2 个新 ID）：

- exit=1；stderr 最后一行为 `RuntimeError: refresh validation failed; old list unchanged: old=737, new=738, unique=738, added=2, missing=1`。
- ID、pending、进度、summary、配置、账号核对六项前后哈希全部不变；未生成 `ID刷新证据.json`。
- 同样共 8 次 eval，未出现作品处理或 AI JS。

**当前结论：AUTHOR_ID_REFRESH_FIX_READY。** 真实清单仍为 737 唯一，配置仍为 737，109 篇和 pending=628 未变；尚未执行真实 ID 刷新。等待协调器明确 `AUTHOR_ID_REFRESH_GO slot=A douyin_id=52327471915`。

## 8. 唯一一次真实 ID 刷新尝试：绑定核验失败并停止

协调器消息 `msg_bfc8314e6e83` 明确授权 `AUTHOR_ID_REFRESH_GO slot=A douyin_id=52327471915`，仅允许运行一次 `--refresh-ids-only`，成功或失败均保存证据并停止。

- 实际 CLI 调用次数：**1**。命令为当前提取器 `python3 -I .../extract_author.py --refresh-ids-only`，显式环境为固定完整 worktree、Profile=`9483ec18-4a86-4e2c-92d5-a2441a1cafb6`、page=`01b0f677-3907-4ee8-91d7-7f707439b8de`。
- 起止时间均为 `2026-11-07T04:04:50+08:00`；exit=1，timeout=false，stdout 为空。
- 失败发生在 `main -> verify_browser_binding`，错误为 `RuntimeError: browser binding mismatch`。当时错误记录为“tab 返回字段与固定值目视一致”；协调器独立核验后确认 tab.worktreeId 不带 `id:` 前缀，旧代码却与带前缀的完整 selector 比较。该判断错误在第 9 节修正。
- 因失败发生在绑定核验，未进入 `collect_profile_ids`，未调用 `run/process_one`，未打开作品或读取 AI 正文，未进行第二次刷新。
- 完整命令、环境绑定、stdout/stderr、前后文件哈希和派生计数已保存到 `ID刷新CLI结果.json`。成功路径专用的 `ID刷新证据.json` 未生成。
- 尝试前后 ID 清单均为 737 且唯一，配置仍为 737，pending=628；新增 ID=0、缺失旧 ID=0。109 篇正文与历史进度哈希完全不变。
- 受保护文件前后共同 SHA-256：ID=`e733688712fb0ae0cf90eb87789ccf384cdc9145d86a1e9100a7f05c8272ed3b`，pending=`8026fba4c95925b368f29948cc6719a22b4cd52974bd17dc14b7f0e65330ac8a`，进度=`b5f4d655a136bbde22741e23d304662beec05a544eccdf2f4e1187868ebd3258`，summary=`0466e7cbf7577517b28e9bbdc55456c9e47ea84f090bb5705c163000dc1a64fe`，配置=`f67222acf6e1fd54f19fc5c631196e21d196b9e1ef878d8712db12b68018fefe`，账号核对=`5ea2dc95d90bf4c71a8b846c1eba8b7983b1b45bd1cf5834da9af84df0841efa`，109 篇组合=`1c0986e45783fab1c81e22e3e46f7ba65817700327102c4bf14b448a34db9266`。
- 事后同作者活跃进程=0；锁文件 `lsof` exit=1、stdout/stderr 均空，锁未持有。
- 当前 `五worker运行状态.json` 记录 `AUTHOR_BATCH_SETTLED`、`running:false、partial:true、author_completed:false`。未生成完整校验或作者完成报告，未执行 Git 写操作。

**本次刷新未成功，不重试；等待协调器独立验收和进一步明确授权。真实提取仍未授权。**

## 9. TEST_ONLY：修正 tab.worktreeId 比较并完成假 Orca CLI 回归

协调器接受失败批次，记录 worker=`c723e30`、main merge=`8bd6b7ceb416f534497888421bbd3aa87bb4ffe0`，创建 `AdrianAndroid/orca-a-52327471915-refresh2` 并仅授予 `TEST_ONLY_GO`。本轮未执行真实浏览器、真实 ID 刷新或真实提取。

- `verify_browser_binding()` 仍将完整 `id:REPO_ID::ROOT` selector 传给 Orca CLI；返回值比较则单独使用精确的 `REPO_ID::resolved_ROOT`，即 `expected_tab_worktree = f"{REPO_ID}::{ROOT}"`。Profile 和固定 page 的精确核验保持不变。
- 静态 AST 检查 exit=0。
- 所有目标测试均为实际提取器的 CLI 子进程，没有 `runpy`、直接调用内部函数或直接调用 `run/process_one`。
- 正向假 CLI 用例返回不带 `id:` 前缀的 `REPO_ID::resolved_ROOT`：exit=0，绑定核验通过，共 8 次 eval；临时 fixture 收集 738 个唯一 ID，完整保留旧 737，仅增加测试 ID `7999999999999999999`；临时 pending=629、配置=738、进度不变，未出现作品处理或 AI JavaScript。
- 反向假 CLI 用例故意返回错误带 `id:` 前缀的 tab.worktreeId：exit=1，`RuntimeError: browser binding mismatch`，在任何 eval 前拒绝，eval_calls=0；受保护 fixture 文件全部不变，未生成成功刷新证据。
- 首次回归 harness 因 macOS `/tmp` 与 `/private/tmp` 的 resolved 路径差异退出；已改为用 `Path(path).resolve()` 构造预期绑定并重跑。该 harness 问题没有调用真实浏览器或修改真实作者文件。
- 真实作者数据保持：ID=737/737 唯一、pending=628、Markdown=109/109 唯一、进度=110 行/latest saved=109；配置=737；`running:false、partial:true、author_completed:false`。
- 真实受保护 SHA-256 未变：ID=`e733688712fb0ae0cf90eb87789ccf384cdc9145d86a1e9100a7f05c8272ed3b`，pending=`8026fba4c95925b368f29948cc6719a22b4cd52974bd17dc14b7f0e65330ac8a`，进度=`b5f4d655a136bbde22741e23d304662beec05a544eccdf2f4e1187868ebd3258`，summary=`0466e7cbf7577517b28e9bbdc55456c9e47ea84f090bb5705c163000dc1a64fe`，配置=`f67222acf6e1fd54f19fc5c631196e21d196b9e1ef878d8712db12b68018fefe`，账号核对=`5ea2dc95d90bf4c71a8b846c1eba8b7983b1b45bd1cf5834da9af84df0841efa`，109 篇组合=`1c0986e45783fab1c81e22e3e46f7ba65817700327102c4bf14b448a34db9266`。
- 未生成完整校验或作者完成报告，未进行 Git 写操作。

**当前结论：AUTHOR_ID_REFRESH_FIX_READY。重新申请 `AUTHOR_ID_REFRESH_GO slot=A douyin_id=52327471915`；真实刷新和真实提取均未获新授权，继续等待。**

## 10. refresh2 真实 ID-only 刷新：实际收集仍为 737，校验拒绝并停止

协调器消息 `msg_3d9f268cb1ae` 再次授权 `AUTHOR_ID_REFRESH_GO slot=A douyin_id=52327471915`，仅允许正常 CLI 子进程运行一次 `--refresh-ids-only`，成功或失败均保存真实证据并停止。

- 实际 CLI 调用次数：**1**，未重试。开始=`2026-11-07T04:26:40+08:00`，结束=`2026-11-07T04:27:47+08:00`，timeout=false，exit=1。
- 修正后的 `verify_browser_binding()` 已通过；进入 `collect_profile_ids(persist=False, expected_count=738)`。
- 共滚动 44 轮：第 19 轮达到 737；第 20–44 轮连续 25 轮稳定在 737。最后输出 `COLLECTED profile=738 actual=737 persist=False`，其中 profile 字段是本次目标数 738，实际展开收集仍只有 737；没有另行读取或声称本轮回写页面标示作品数。
- 严格校验按设计拒绝：`RuntimeError: refresh validation failed; old list unchanged: old=737, new=737, unique=737, added=0, missing=0`。
- 因未满足“738 唯一且完整包含旧 737”，未更新 ID、pending、配置、summary 或账号核对；成功路径的 `ID刷新证据.json` 未生成。
- 未调用 `run/process_one`，未打开作品或读取 AI 正文，未执行真实提取。
- 完整命令、固定环境、44 轮 stdout、完整 stderr、前后哈希及派生计数保存在新文件 `ID刷新CLI结果-refresh2.json`；上一次失败的 `ID刷新CLI结果.json` 原样保留。
- 尝试后真实 ID 仍为 737/737 唯一、配置=737、pending=628、Markdown=109，进度=110 行。各受保护文件 SHA-256 与尝试前完全一致：ID=`e733688712fb0ae0cf90eb87789ccf384cdc9145d86a1e9100a7f05c8272ed3b`，pending=`8026fba4c95925b368f29948cc6719a22b4cd52974bd17dc14b7f0e65330ac8a`，进度=`b5f4d655a136bbde22741e23d304662beec05a544eccdf2f4e1187868ebd3258`，summary=`0466e7cbf7577517b28e9bbdc55456c9e47ea84f090bb5705c163000dc1a64fe`，配置=`f67222acf6e1fd54f19fc5c631196e21d196b9e1ef878d8712db12b68018fefe`，账号核对=`5ea2dc95d90bf4c71a8b846c1eba8b7983b1b45bd1cf5834da9af84df0841efa`。refresh2 证据采用的 109 篇 Markdown 组合口径前后均为 `4fde3efbe42c143c3adaabe628d93d11138321e23d963b7240c8354588ca4dea`；早期基线的 `1c0986...` 属于此前快照/口径，不直接混用。协调器另将当前 worktree 与 main 的 109 篇逐字节比较，文件名和内容完全一致。
- 事后同作者提取进程=0，锁 `lsof` exit=1，锁已释放。`五worker运行状态.json` 记录 `AUTHOR_BATCH_SETTLED`、`running:false、partial:true、author_completed:false`。
- 未生成完整校验或作者完成报告，未执行 Git 写操作。

**本次真实刷新未成功，不自行重试或缩窄校验；等待协调器独立验收和进一步指令。真实提取仍未授权。**

协调器随后以 `AUTHOR_BATCH_ACCEPTED` 接受 refresh2 失败批次：worker=`ded499704773b50f66f17169868b7cd053150bc9`，main merge=`13da044baa65296ed0f595e7f7d6135078eac81f`，状态=`id_refresh_failed_validation_pending_reconciliation`，并逐字节确认 109 篇正文未变。

## 11. 已知 737 清单：指定前两个 unattempted ID 的部分批次

协调器消息 `msg_5bbbbed025a7` 授予 `KNOWN_737_PARTIAL_BATCH_GO slot=A douyin_id=52327471915`：仅按现有 737 个真实 ID 提取两个，页面 738 与实际 737 的差异继续保留，不得伪造第 738 项或再次刷新。禁止代码修改、测试、内部函数调用及 Git 写操作。

- 预检在同作者排他锁内完成，所有浏览器命令使用原完整 worktree selector 和固定 page；恢复精确 sec_uid 作者主页后，最终 URL 与目标完全一致。
- `tab.worktreeId=REPO_ID::resolved_ROOT`、Profile、page、loaded 均匹配，loadError 为空；作者名=`凯哥恋爱说`、页面包含抖音号=`52327471915`、已关注=true，登录按钮=false，投稿/消息/通知入口存在。
- 页面显示 `作品 738`，固定清单仍为 737；无验证码或限流文本。独立 window key 写入、读取、删除及清理成功，未读取 Cookie、Web Storage 或会话凭据。完整命令响应与检查项见 `已知737两项批次预检.json`。
- 待补提清单前两项与协调器指定完全一致：`7663790068393430312`、`7663391157749157174`。
- 随后仅运行一次正常 CLI 子进程 `python3 -I .../extract_author.py --max-items 2`，开始=`2026-11-07T04:57:48+08:00`，结束=`2026-11-07T04:58:24+08:00`，exit=0、timeout=false、stderr 为空，未重试、未续提。
- 保存 ID `7663790068393430312`：《你的形象越好，你的恋爱成本就越低》，AI 长度 788；文件=`20260718-7663790068393430312-你的形象越好，你的恋爱成本就越低.md`，SHA-256=`b091a34355dc1d41625a06e7d00c308f0ef795b068882cc90951bffd69287a25`。
- 保存 ID `7663391157749157174`：《今天你要体验的人生副本是：一辈子不结婚的一生》，AI 长度 765；文件=`20260717-7663391157749157174-今天你要体验的人生副本是：一辈子不结婚的一生.md`，SHA-256=`9d322cf74449e20af885b266efb625e0dfa770fb0f8823164edb0ace7cb1489f`。
- 本批 attempted=2、saved=2、no_ai=0、error=0。Markdown 109→111，进度 110→112 行，latest saved=111，pending 628→626；仅追加指定两行进度和新增两个 Markdown，旧 110 行字节前缀不变，旧 109 个正文无修改或删除。
- 737 ID 清单及配置保持原哈希：ID=`e733688712fb0ae0cf90eb87789ccf384cdc9145d86a1e9100a7f05c8272ed3b`，配置=`f67222acf6e1fd54f19fc5c631196e21d196b9e1ef878d8712db12b68018fefe`，账号核对=`5ea2dc95d90bf4c71a8b846c1eba8b7983b1b45bd1cf5834da9af84df0841efa`。
- 新 pending SHA-256=`4f36836f5e2dea7c8ba257abeeed1999505f15f8da6b5b5f5cfe97e5fcde85b0`，进度=`0675974abee8319a3146742c7292f190d0cda23736a4567076ffa7a3da21464f`，summary=`b1b04bd52cdaae8777ba88bfc6ce0075d23e6794f4e6fe5ae030f0f257aa726a`。
- 按名称+空字节+正文组合口径，原 109 篇在本批前为 `4fde3efbe42c143c3adaabe628d93d11138321e23d963b7240c8354588ca4dea`，新增后 111 篇为 `0f9d01bfb94468460893abab1bc424d1f512df4ecc3f9bbc40e3b10d1c86af9c`。
- 完整 stdout/stderr、追加行及前后哈希见 `已知737两项批次CLI结果.json`。`五worker运行状态.json` 已记录 `AUTHOR_BATCH_SETTLED`、`running:false、partial:true、author_completed:false`。
- 事后同作者提取进程=0，锁 `lsof` exit=1，锁已释放；未生成完整校验或作者完成报告，未修改代码，未执行 Git 写操作。

**本批已安全收尾；页面 738 与已知 737 的差异仍未解决，不认定作者完成。未获后续 GO 不续提。**
