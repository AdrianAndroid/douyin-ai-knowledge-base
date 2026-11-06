# 五 worker 槽位 E 执行记录

- run：`run_573b10a4429c`
- task：`task_b597bbadc1a0`
- dispatch：`ctx_7060b58aff01`
- 作者：宅男相亲记迷你版；抖音号：`54771197908`
- 预检时间：2026-11-07T03:27:16+08:00
- 状态：**AUTHOR_BATCH_SETTLED；2 条已保存，66 条真实 pending，等待协调器验收**

## 身份与边界

当前 cwd 为 `/Users/zhaojian/orca/workspaces/ai-learn/jellyfish`，完整 selector 为 `id:da2e8721-3aa8-432b-8a51-fb648a32632c::/Users/zhaojian/orca/workspaces/ai-learn/jellyfish`，branch 为 `AdrianAndroid/orca-e-54771197908`，HEAD 为 `bd02f7db94d3ce5ce2af1094a1a12b60e9abfb06`。`orca worktree show` 请求 ID 为 `fe75f128-ed77-4df3-b334-0d8f84ae117d`，返回的 worktree、repoId、branch 均匹配。

启动前只有 `extract_author.py`、`配置.json`、2026-11-05 的 `账号核对.json` 与 `搜索账号核对.json`；Markdown=0，提取进度/主页 ID/pending/提取状态/完成报告均不存在。未发现相关提取进程、锁、已有断点或跨作者文件。没有执行 `run_next45.py`，没有真实提取，没有 commit/merge/rebase/push/reset/clean，也没有修改共享队列、主 checkout 或其他作者目录。

## 最小改造

- `配置.json` 移除旧共享 `page`，output 改为 worktree 相对的 `抖音关注/54771197908-宅男相亲记迷你版`。
- `extract_author.py` 由 `TMP.parent.parent` 得 ROOT，严格校验 TMP 与 OUT 都是当前 worktree 内本作者目录。
- `ORCA_WORKTREE`、`ORCA_PROFILE`、`ORCA_PAGE` 仅从环境读取，缺失即失败；selector 必须是完整 ID 且路径等于 ROOT。
- 所有提取器浏览器 eval 都显式携带 `--worktree <完整 selector>` 与固定 `--page`。
- 在创建目录、写输出或浏览器操作前取得 `/tmp/orca-extract-da2e8721-3aa8-432b-8a51-fb648a32632c-54771197908.lock` 的非阻塞排他锁；重复实例先失败。
- 复用原有进度追加、正文 Markdown 原子替换及 JSON 原子替换，保留断点续提，新增 `--max-items N`（N>=1）。部分批次保留真实 pending，`running:false`、`partial:true`、`author_completed:false`，且不写完整校验或完成报告；仅无 pending 且完整校验通过才写完成结论。

## 本地测试（未访问抖音、未写输出）

1. 语法 compile、配置及路径绑定导入检查：通过；TMP=`/Users/zhaojian/orca/workspaces/ai-learn/jellyfish/tmp/54771197908-宅男相亲记迷你版`，OUT=`/Users/zhaojian/orca/workspaces/ai-learn/jellyfish/抖音关注/54771197908-宅男相亲记迷你版`。
2. 缺少 `ORCA_PAGE`：实际退出码 **1**，stdout 为空；stderr 末行：`RuntimeError: missing required environment variable: ORCA_PAGE`。
3. `--max-items 0`：实际退出码 **2**，stdout 为空；stderr 末行：`extract_author.py: error: argument --max-items: must be at least 1`。
4. 由测试父进程先持锁，再以 `--max-items 1` 启动第二实例：实际退出码 **1**，stdout 为空；stderr 包含 `BlockingIOError: [Errno 35] Resource temporarily unavailable`，末行为 `RuntimeError: another extractor holds /tmp/orca-extract-da2e8721-3aa8-432b-8a51-fb648a32632c-54771197908.lock`。测试 PATH 固定为 `/nonexistent-orca-path`，若代码越过锁便无法调用 orca；实际先在锁处失败，作者文件前后 size/mtime 不变，输出目录未创建。
5. 测试后非阻塞排他锁可立即取得并释放，证明没有活跃 holder；相关提取进程为 0。`git diff --check` 退出码 **0**。

## 浏览器身份与登录复查

全程显式使用完整 worktree selector、Profile `ffa4d1f5-6874-4817-ae7e-085f3293bb54`、page `f826d2ef-8be3-469f-a41d-037a4ffeb85a`；未读取 Cookie、其他存储或会话凭据。

- tab list 请求 ID：`5f216372-422b-410b-897c-0bb87c44194a`；唯一 page 的 profileId、worktreeId 均精确匹配，profileLabel=`douyin-reusable-slot-e`，loaded=true，无 loadError。
- goto 请求 ID：`ffb8ddc3-0d71-49e1-a960-0f251799e116`；导航至队列中的精确 profile_url。
- context eval 请求 ID：`396f49b2-dca1-441e-95df-7566cd13a3b4`；URL 中 sec_uid 精确匹配，h1=`宅男相亲记迷你版`，页面包含抖音号 `54771197908`，`已关注`=true，作品数=68，document.readyState=`complete`。
- login_wall=false、captcha=false、rate_limited=false、page_unavailable=false；已关注与完整个人页表明登录有效。

## Git 状态与允许写入

写本记录、浏览器绑定和预检状态前，git status 只有本作者 `extract_author.py` 与 `配置.json` 两项 modified；新增的仅三份允许的预检文件。允许后续写入边界仅为本作者 TMP 与当前 worktree 的对应 `抖音关注/54771197908-宅男相亲记迷你版/`。下一步必须等待协调器发送 `AUTHOR_EXTRACTION_GO slot=E douyin_id=54771197908`，不得自行启动提取。

## 阶段 2：GO 后自适应批次（2026-11-07）

协调器消息 `msg_f6cb3e043c07` 明确回复 `AUTHOR_EXTRACTION_GO slot=E douyin_id=54771197908`，仅授权本作者。全程使用固定环境绑定，没有 Git 写操作。

### 批次 1：完整断点续提后卡顿收尾

- 起止：03:32:19 至 03:38:32（+08:00）；没有设置 2/30 上限。
- 完整展开并持久化 68 个主页作品 ID，与页面作品 68 一致。
- 记录 attempted=4、saved=2、no_ai=0、errors=2，停止时 pending=66。
- 保存 ID：`7631174028669078836`、`7593308836811869440`。
- 错误 ID：`7597740933051960591`、`7699798075400916266`，均为 `AI text or metadata timeout`。连续两次 150 秒超时且约 5 分钟无新增保存后，以 SIGINT 安全停止；进程退出码 130，异常收尾写回 pending 并释放锁。
- 停止后浏览器复查请求 ID `631f6e41-c1bc-4f0d-8f2b-a9b86ec4541a`：作者、抖音号与已关注匹配，login_wall/captcha/rate_limited/page_unavailable 均 false。

### 批次 2：缩减为最多 5 条后仍卡顿

- 起止：03:39:30 至 03:46:24（+08:00）；参数 `--max-items 5`，从 66 条真实 pending 断点续提。
- 记录 attempted=2、saved=0、no_ai=0、errors=2，停止时 pending=66。
- 上述两个 ID 再次分别在 150 秒后超时，无新增保存，因此再次 SIGINT 安全停止；进程退出码 130。
- 两批合计记录 attempted=6、saved=2、no_ai=0、errors=4（2 个不同错误 ID 各重复一次）；当前最新状态为 saved=2、error=2、pending=66。

### 收尾核验与等待

本槽位提取进程已退出，`/tmp/orca-extract-da2e8721-3aa8-432b-8a51-fb648a32632c-54771197908.lock` 可立即排他取得并释放。两份 Markdown 文件名 ID、正文作者/抖音号/作品 ID/日期及 AI 标记全部匹配，无重复或无效文件，正文字符数分别为 727 和 442。`待补提作品.json` 的 66 个 ID 与最新进度完全一致；`提取状态.json` 为 `running:false`、`partial:true`、`author_completed:false`，没有生成 `文案校验.json` 或 `提取完成报告.json`。

当前已写 `五worker运行状态.json` 并停止继续写输出，报告 `AUTHOR_BATCH_SETTLED` 后等待协调器独立验收、提交、合并。若协调器授权继续，下一批最多 2 条；等待期间没有启动该批次。

## 验收后 --skip-ids 改造及测试事故

协调器 `msg_555f463cb741` 独立核验合并 2 篇，worker=`7435a02`，merge=`78e60b25c678d4f3118e00c3688f708ae9b2847a`，当前 branch 为 `AdrianAndroid/orca-e-54771197908-batch3`。仅新增 CLI `--skip-ids`：支持重复参数与逗号分隔，数字 ID 校验；跳过项不增加 attempted、不写进度、不记 saved/no_ai，仍保留 pending。

`--help` 子进程测试退出 0，非法 `--skip-ids not-an-id` 退出 2。随后内存 CLI 夹具误用 runpy 返回字典，未替换被测 main 实际 globals，意外进入真实提取路径；发现超时后立即 SIGINT（exit 130）。经 `msg_1715de126f60` 如实报告，并由协调器 `msg_7a5cbd2e90d3` 独立确认：没有新增 Markdown 或进度，仍 2 篇、6 行进度、66 pending，仅 summary 时间/note 被异常收尾改写。此后未再做 runpy 或直接内部调用，也未再改提取代码。

## 批次 3：明确 NEXT_BATCH_GO 后仅运行指定 CLI

协调器 `msg_8b5bb59a0246` 明确授权仅运行一次：`extract_author.py --max-items 2 --skip-ids 7597740933051960591,7699798075400916266`，固定原 worktree/Profile/page 环境，不做任何额外测试。

- 起止：2026-11-07 04:13:34 至 04:18:44（+08:00）。
- 日志明确记录两个旧错误 ID 均为 `SKIP_REQUESTED ... remains_pending=true`；它们没有 attempted、没有新增进度，最终仍 pending。
- 仅处理两个新 ID：`7699441653064404258`、`7697195016107658547`；两者各发生一次 `AI text or metadata timeout`。
- 本批 attempted=2、saved=0、no_ai=0、errors=2、pending=66；达到 max-items=2 后正常部分批次收尾，退出码 2。
- 累计进度 8 行，记录 attempted=8、saved=2、no_ai=0、errors=6；最新唯一状态为 saved=2、error=4，真实 pending=66。

槽位 E 进程已退出，排他锁已释放。Markdown 仍只有原两篇，四个最新错误 ID 全部仍在 pending；`running:false`、`partial:true`、`author_completed:false`，未生成完整校验或完成报告。已更新 `五worker运行状态.json`，现在停止输出写入并报告 `AUTHOR_BATCH_SETTLED`，等待独立验收，不做 Git 写操作，不处理其他作者。
