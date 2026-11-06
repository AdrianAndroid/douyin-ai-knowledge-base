# 五 worker 槽位 A 执行记录：凯哥恋爱说

- run：`run_573b10a4429c`
- task：`task_4ec80a8b1b81`
- dispatch：`ctx_b1f5e1508517`
- 当前阶段：阶段 1 预检；尚未收到 `AUTHOR_EXTRACTION_GO`，未启动真实提取。
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

## 5. 预检结论

**AUTHOR_PREFLIGHT_BLOCKED**。未收到 `AUTHOR_EXTRACTION_GO`，但离线测试偏差意外处理了 2 个作品；现已停止，所有实际变化保留并记录。Git 写操作为零，主队列、其他 worktree、其他作者及共享计划/记录均未修改；当前变化均在允许的 TMP/OUT 边界内。等待协调器决定如何处置这 2 个意外新增结果及是否/如何重新预检，不自行继续。
