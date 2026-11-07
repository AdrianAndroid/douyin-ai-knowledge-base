# 五 worker 槽位 B：王小浪预检执行记录

- run：`run_573b10a4429c`
- task：`task_64b819ccc5db`
- dispatch：`ctx_505ffd5a8c58`
- 作者：王小浪不浪成都恋商情感文化传播有限公司（`wangxiaolangk`）
- 记录时间：2026-11-07T03:31:38+08:00
- 最近修正：2026-11-07T03:44:15+08:00（协调器要求作品数 490→491）
- 当前阶段：首批已独立验收；`--skip-ids` 隔离 CLI 子进程测试完成，等待协调器明确 `NEXT_BATCH_GO`，真实续提尚未启动。

## 1. 版本指南与固定身份

已从本 session 的 `/Applications/Orca.app/Contents/Resources/bin/orca` 读取版本匹配的 `orca-cli`、`orchestration` 和 `references/browser.md` 指南。

核对结果：

- cwd / worktree：`/Users/zhaojian/orca/workspaces/ai-learn/pilot-wei-qishun`
- 完整 selector：`id:da2e8721-3aa8-432b-8a51-fb648a32632c::/Users/zhaojian/orca/workspaces/ai-learn/pilot-wei-qishun`
- branch：`AdrianAndroid/orca-b-wangxiaolangk`
- HEAD：`bd02f7db94d3ce5ce2af1094a1a12b60e9abfb06`
- Profile：`2bd87da7-ccc5-4110-b058-691269a45eef`
- page：`eb12641b-ca19-470e-8bc2-8e9bce2aed98`
- worktree show 请求 ID：`99f09bc0-21e9-4af0-bb30-1abac2bf0315`，退出码 0。
- tab list 请求 ID：`9c7faec3-7169-4ab2-93cf-64d3132989f0`，退出码 0。

所有浏览器命令均同时显式携带完整 worktree selector 和固定 page；未使用默认 tab，未创建替代 worktree、Profile 或 page。

## 2. 启动前作者状态

王小浪按新作者任务处理，不套用魏起顺会拍照的“全部无 AI”结论。

- 初始 Git 状态：clean。
- 初始作者 Markdown：0。
- `提取进度.jsonl`、`主页作品ID.json`、`待补提作品.json`、完成报告：均不存在。
- 未发现王小浪提取进程、`run_next45.py` 进程或作者锁；未运行 `run_next45.py`。
- 原配置 output 为主 checkout 绝对路径 `/Volumes/wd/ai-learn/抖音关注/wangxiaolangk-王小浪不浪成都恋商情感文化传播有限公司`。
- 原配置含旧 page `6c482e4f-531e-453d-bf33-1518b3fa88fe`。
- 既有 `账号核对.json` 和 `搜索账号核对.json` 仅为 2026-11-05 的历史核对材料，没有覆盖或当作本次页面预检结果。

## 3. 最小改造

仅修改本作者 `extract_author.py` 与 `配置.json`：

- output 改为 worktree 相对的 `抖音关注/wangxiaolangk-王小浪不浪成都恋商情感文化传播有限公司`。
- `ROOT = TMP.parent.parent.resolve()`，严格断言 TMP、OUT 均等于本作者的预期路径且位于 ROOT 内。
- 删除配置中的共享 page；`ORCA_WORKTREE`、`ORCA_PROFILE`、`ORCA_PAGE` 只从环境读取，任一缺失即失败。
- 所有提取器浏览器调用显式携带完整 worktree selector 和固定 page，并在启动时复核 worktree/page/Profile/作者 URL。
- 使用 `/tmp/orca-douyin-da2e8721-3aa8-432b-8a51-fb648a32632c-wangxiaolangk.lock` 的 `fcntl.flock(LOCK_EX | LOCK_NB)`；浏览器操作和文件输出前必须持锁，第二实例退出码 4。
- 保留既有正文提取、断点续提、进度追加和原子写逻辑；新增任意正整数 `--max-items N`，省略时为完整作者最多三轮断点续提。
- 部分批次结束写 `running:false`、`partial:true`、`author_completed:false` 和真实 pending，不执行完整校验或生成完成报告。
- 完整运行仍有 pending 时不生成完成报告；仅无 pending 且校验通过时写 `partial:false`、`author_completed:true` 与完成报告。
- 登录、验证码、限流、页面失效及致命浏览器错误会停止当前运行并安全写入真实状态。

## 4. 离线测试（未访问抖音、未写作品输出）

### 语法与路径

- Python 编译检查：退出码 0，输出 `SYNTAX_OK`；使用 `compile()`，未生成 `__pycache__`。
- 配置 JSON 解析、`git diff --check`：退出码 0。
- 从 `/private/tmp` 以绝对脚本路径做相对路径测试：退出码 0；TMP、OUT、完整 selector、Profile、page 全部匹配，未调用浏览器，未创建输出目录。

### 环境绑定

分别缺少三个变量时，真实子进程结果如下，均在锁、浏览器和输出前失败：

| 缺失变量 | 退出码 | 错误 |
| --- | ---: | --- |
| `ORCA_WORKTREE` | 2 | `extract_author.py: error: 缺少环境变量: ORCA_WORKTREE` |
| `ORCA_PROFILE` | 2 | `extract_author.py: error: 缺少环境变量: ORCA_PROFILE` |
| `ORCA_PAGE` | 2 | `extract_author.py: error: 缺少环境变量: ORCA_PAGE` |

### 重复启动锁

- 外部 flock holder PID：`91629`；holder 不访问浏览器。
- 在 holder 持锁时启动第二个真实提取器进程（`--max-items 1`）：退出码 4。
- stdout：空。
- stderr：`LOCK_BUSY path=/tmp/orca-douyin-da2e8721-3aa8-432b-8a51-fb648a32632c-wangxiaolangk.lock; exited before any browser operation or output write`。
- 新 TMP 条目：无；已有 TMP 条目内容/mtime 变化：无。
- 未创建 `浏览器调用.jsonl`，未创建输出目录，未访问抖音。
- holder 释放后可重新获取；最终独立重取检查输出 `LOCK_FREE_REACQUIRED`，退出码 0；当前 worker 不持锁。

## 5. 固定 page 主页预检

精确 profile URL：

`https://www.douyin.com/user/MS4wLjABAAAArdqNGZ5-cnvTgxNaN0jB38Kz6ZTeUqtWiuXsodLOEQgfcgK_vQ_D-kcOcmhQGyHk?from_tab_name=main`

请求与结果：

- goto：`b1123463-9974-4389-8190-edc3b6d28f13`，退出码 0。
- wait load：`5f1230da-a6a7-4ba3-a227-511c28ce7daf`，退出码 0。
- DOM 核对：`374ec9df-76ef-4558-b755-0a366d897b5f`，退出码 0。
- 最终 tab show：`5ea26400-9aaf-420b-a676-05efe21f7c01`，退出码 0。
- 最终 Profile show：`4f7eeea4-ca74-4006-ac38-8da587f84ef2`，退出码 0。

DOM 证据：

- 当前 URL 含精确 sec_uid；作者 h1 为 `王小浪不浪成都恋商情感文化传播有限公司`。
- `抖音号：wangxiaolangk` 匹配。
- 页面按钮包含两个 `已关注`，登录状态有效。
- 登录、验证码、限流、页面失效标记均为空。
- 页面作品标题当前为 `作品 491`，初次预检时队列快照及配置为 490；协调器复核后已要求并确认仅将本作者配置与预检证据更新为 491，保留旧快照 490→491 的记录，共享队列未修改。
- 仅读取 DOM；未读取 Cookie、其他存储或会话凭据。

## 6. 文件边界与下一步

预检阶段只修改本作者提取器/配置，并新增本记录、`浏览器绑定.json`、`五worker预检状态.json`。未写共享 `Orca五worker调度状态.json`，未写主 checkout、其他 worktree/作者、共享计划、README 或总记录；未执行 commit、merge、rebase、push、reset、clean。

最终进程检查未发现王小浪提取器或 `run_next45.py`；锁可立即重新获取且已释放；作品 Markdown 仍为 0。下一步仅发送 `AUTHOR_PREFLIGHT_READY slot=B douyin_id=wangxiaolangk` ask，结束回合等待协调器明确 GO。

## 7. 协调器修正与复测（2026-11-07T03:44:15+08:00）

第一次 ask 后收到 `msg_0f1d36b1a172`：`AUTHOR_PREFLIGHT_FIX_REQUIRED slot=B douyin_id=wangxiaolangk`。协调器已独立复核身份、登录和绑定，独立 tab 请求 ID 为 `2129f400-3e9c-4f68-b4ab-1bdbcbe918e5`；要求仅把本作者配置与预检证据的作品数从旧快照 490 更新为页面实际 491，不启动真实提取。

已严格执行：

- `配置.json` 的 `profile_work_count`：490→491。
- `浏览器绑定.json`、`五worker预检状态.json` 和本记录：当前配置/证据值更新为 491，保留旧快照 490 及协调器请求 ID。
- 未修改提取器、共享队列或其他文件，未启动真实提取。

修正后重新执行离线检查：

- JSON、Python 语法和 diff 检查：退出码 0；确认配置及浏览器证据均为 491，旧快照记录为 490。
- 从 `/private/tmp` 重跑相对路径检查：退出码 0；TMP/OUT/环境绑定匹配，`EXPECTED_COUNT=491`，未调用浏览器，未创建输出目录。
- 重跑重复启动锁：外部 holder PID `3947`，第二提取器退出码 4，stderr 为同一 `LOCK_BUSY ... before any browser operation or output write`；新 TMP 条目和已有条目变化均为空，未创建浏览器审计或输出目录，holder 释放后重取成功。

修正及复测后仍未收到 GO，王小浪提取进程和作品 Markdown 均为 0；再次 ask 后继续等待。

## 8. GO 后首批：停滞安全收尾（2026-11-07 03:50:08—03:56:16 +08:00）

协调器消息 `msg_48834b2e1a6f` 明确下发 `AUTHOR_EXTRACTION_GO slot=B douyin_id=wangxiaolangk`，仅授权王小浪正常完整作者断点续提，并要求连续两次超时或约 5 分钟无进展时安全收尾、下一批 5/2、fatal 立即停止、每批 ask 验收且不做 Git 写操作。

启动前确认配置 491、作者锁空闲、无王小浪提取进程。03:50:08 以固定 `ORCA_WORKTREE`、`ORCA_PROFILE`、`ORCA_PAGE` 启动当前 worktree 提取器，未设 `--max-items`。锁获取与绑定检查通过；完整主页展开得到 491 个唯一 ID，与配置一致，进入第一轮时 pending=491。

运行结果：

- `7214392743617940797`：`AI text or metadata timeout`，写入真实 error。
- `7667885557959698854`：同样超时，写入真实 error。
- 连续两条错误且清单收集后约 5 分钟无 saved/no_ai，按规则向 PID `9079` 发送 SIGINT。
- 第三个 ID `7669142308360781979` 已进入尝试，但在产生结果行前中断，保留 pending，未伪造 error/saved/no_ai。
- 进程执行 `finally` 写状态后退出，实际退出码 `130`；03:56:16 状态完成落盘，随后确认进程不存在、锁可立即重取并已释放。

批次核验（03:57:43）：

- attempted=3（其中两条有结果，一条中断）；saved=0；no_ai=0；errors=2；pending=491。
- `主页作品ID.json` 为 491 个唯一 ID；`待补提作品.json` 与其逐字一致，SHA-256 均为 `42f76bfe9aa6bfd8d726277c47708715e21aae45e6f8747e5b7c1dc3de045de8`。
- `提取进度.jsonl` 仅两条真实错误，SHA-256 为 `40051901dc0a95e01e7ae81363b7d64d06451755ccc58a1c2f8765511a068df5`。
- Markdown=0；`running:false`、`partial:true`、`author_completed:false`；未生成 `文案校验.json` 或 `提取完成报告.json`。
- 详细机器可读记录见 `五worker批次记录.json`；`五worker运行状态.json` 已补充真实退出码、进程/锁核验、停滞原因和下一批上限 5。

本批没有继续处理剩余作品，没有执行 Git 写操作。下一步仅发送 `AUTHOR_BATCH_SETTLED` ask，等待独立验收；下一批未启动。

## 9. TEST_ONLY_GO：`--skip-ids` 实现与隔离验证（2026-11-07 04:25:15 +08:00）

首批经协调器独立验收后，按 `TEST_ONLY_GO` 仅实现延后作品 ID 的选择逻辑，没有启动真实续提：

- `--skip-ids` 支持重复参数和逗号分隔，按 ASCII 数字校验并保持首次出现顺序去重。
- 被延后的 ID 不进入 attempted、不追加进度，仍保留在完整 pending；运行状态新增 `skip_ids`、`skipped_pending_ids` 和 `skipped_pending_count`。
- 真实 CLI `--help` 退出码 0；`abc`、`123,456x`、空字符串、`123,,456`、`-123` 均在锁、浏览器和输出前以退出码 2 拒绝，错误包含“只接受逗号分隔的数字作品ID”。

隔离测试使用 `TemporaryDirectory` 中的提取器副本、合成作者/作品状态和假 Orca CLI，仅通过 `python3 -I .../extract_author.py` CLI 子进程运行，未使用 runpy 或直接内部调用。保留的夹具排错过程：

1. 首次假 CLI 因先匹配 `passport`，误把作品状态脚本当成健康检查，子进程退出码 2，报 `'str' object has no attribute 'get'`；修正为优先识别 `hasAiButton` + `coauthorVerified`。
2. 第二次核心选择/状态/进度/隔离断言依次通过，但固定调用次数断言失败，未记为通过。
3. 诊断确认实际为 14 次假 Orca 调用（4 次绑定核验，加两个作品各 5 次），原夹具误写为 12；该诊断仍在旧计数断言退出，未记为通过。
4. 修正夹具计数后最终重跑退出码 0，输出 `SKIP_IDS_ISOLATED_CLI_TEST_OK exit=0 real_tmp_or_output_changed=false`。

最终隔离用例以 `--max-items 2` 和重复/逗号混合参数跳过 `7214392743617940797`、`7667885557959698854`、`7669142308360781979`。实际 attempted 仅为 `7704661060138041445`、`7704244490215990257`；三个跳过 ID 全部仍在 pending，第三个中断 ID 没有新增进度，前两条既有 error 原样保留。隔离结果 `pending=6`、新增进度仅两条、`partial:true`、`author_completed:false`，未生成完整校验或完成报告；14 次假浏览器调用均显式携带 worktree 和 page。

最终 Python 编译及 `git diff --check` 均通过。真实 TMP/OUT 前后条目、大小及 mtime 快照一致；三个真实首批文件 SHA-256 未变，真实 Markdown 仍为 0，状态仍为 attempted=3、saved=0、no_ai=0、errors=2、pending=491。机器可读证据见 `五worker跳过ID测试记录.json`。未访问真实浏览器、未写真实提取输出、未执行 Git 写操作；下一步仅 ask 申请 `NEXT_BATCH_GO`。
