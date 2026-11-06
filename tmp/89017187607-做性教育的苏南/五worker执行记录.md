# 五 worker 槽位 D：做性教育的苏南预检记录

- run：`run_573b10a4429c`
- task：`task_df9665928b9c`
- dispatch：`ctx_9e33cb20e7dd`
- 预检时间：2026-11-07T03:33:17+08:00
- 结论：`AUTHOR_PREFLIGHT_READY slot=D douyin_id=89017187607`
- 真实提取：未启动；未运行 `run_next45.py`；必须等待协调器明确发送 `AUTHOR_EXTRACTION_GO slot=D douyin_id=89017187607`。

## 1. 启动身份与既有状态

- cwd：`/Users/zhaojian/orca/workspaces/ai-learn/dugong`
- 完整 selector：`id:da2e8721-3aa8-432b-8a51-fb648a32632c::/Users/zhaojian/orca/workspaces/ai-learn/dugong`
- branch：`AdrianAndroid/orca-d-89017187607`
- HEAD：`bd02f7db94d3ce5ce2af1094a1a12b60e9abfb06`
- Profile：`a3385429-07ca-4470-ade7-241ede7f5697`
- page：`a09cac76-e55d-450b-9333-8b3ab59a485a`
- `worktree current` 请求：`4e9f79cd-0d5f-4d2f-9374-556a5635d042`；`worktree show` 请求：`0671c590-594a-4442-95a2-273ef9e46412`。
- 修改前 Git 干净；本作者 Markdown=0、进度文件不存在、输出目录不存在、无本作者活跃提取进程、无本作者锁。
- 原配置输出为主 checkout 绝对路径 `/Volumes/wd/ai-learn/抖音关注/89017187607-做性教育的苏南`，旧 page 为 `6c482e4f-531e-453d-bf33-1518b3fa88fe`；未向这些旧位置写入。

## 2. 本作者最小改造

- `配置.json` 的 output 改为 `抖音关注/89017187607-做性教育的苏南`，移除共享 page 配置。
- `extract_author.py` 由 `TMP.parent.parent` 得到 ROOT，严格断言 TMP、OUT、作者、完整 worktree、Profile 和 page。
- `ORCA_WORKTREE`、`ORCA_PROFILE`、`ORCA_PAGE` 只从环境读取，任一缺失即失败；所有提取器浏览器调用同时显式携带完整 worktree 与固定 page。
- 在任何提取器浏览器操作或输出写入前获取 `/tmp/orca-da2e8721-3aa8-432b-8a51-fb648a32632c-89017187607-extract.lock` 非阻塞排他锁。
- 保留既有断点、正文保存、进度追加和原子替换；加入 `--max-items N`、连续两次浏览器超时/约五分钟无实质进展停止，以及真实 partial 批次状态。部分批次不写完整校验或作者完成报告。

## 3. 静态、路径和锁测试

- AST 语法解析：退出码 0，`SYNTAX_OK`。
- 配置路径断言：退出码 0，`CONFIG_PATH_OK`；`git diff --check` 退出码 0。
- 锁持有实例：PID 93517，`--lock-only --lock-hold-seconds 3`，退出码 0，stderr 为空。
- 正常提取入口第二实例（`--max-items 1`）：退出码 **73**，stdout 为空，stderr 为 `LOCK_BUSY path=/tmp/orca-da2e8721-3aa8-432b-8a51-fb648a32632c-89017187607-extract.lock`。
- 第二实例未访问抖音、未创建输出目录、未创建进度或状态文件；随后非阻塞加锁复核成功，证明持有实例退出后锁已释放。
- 分别缺少 `ORCA_WORKTREE`、`ORCA_PROFILE`、`ORCA_PAGE`：退出码均为 1，末行分别为对应 `KeyError`。

## 4. 固定 page 作者预检

- 导航前 tab list 请求 `932a45d2-46c0-4614-8d4d-0cc475f636eb`：原 Profile/page 均匹配，loaded=true，loadError=null。
- 精确 profile_url 导航请求 `a27b79af-bc95-456d-b141-dea9252f646d`：settled=true，标题为“做性教育的苏南的抖音 - 抖音”；未创建 page。
- load 等待请求 `b95779eb-3191-47b4-a68e-3c885564e91b`；身份核验请求 `1affc46d-4dc3-4e53-b11c-3ade0273181b`。
- 页面 `readyState=complete`，URL 中 sec_uid 精确匹配，h1=做性教育的苏南，抖音号 89017187607 存在，作品标题为“作品 110”。
- 页面显示“已关注”“私信”“消息”“通知”；登录按钮、验证码、限流及页面失效信号均为空，正常 JavaScript 执行上下文已重新确认。
- 导航后 tab list 请求 `adbaa7b4-3d45-46bf-b397-0eab73b32a66`：仍为同一 worktree/Profile/page，loaded=true，loadError=null。
- 未读取 Cookie、其他存储、二维码、密码或任何会话凭据；未收集作品 ID，未点击作品或 AI 按钮。

## 5. 文件和 Git 边界

只修改本作者 `tmp/89017187607-做性教育的苏南/` 内的脚本、配置和三份预检证据；本作者输出目录在预检后仍不存在。未修改共享调度状态、共享计划、README、总记录、主 checkout、其他 worktree 或其他作者，未执行 commit、merge、rebase、push、reset 或 clean。

## 6. GO 后首个部分批次（等待独立验收）

- 协调器 GO 消息：`msg_3c4a1c229eb3`；独立 tab 复核请求：`389b7470-a3d7-4e77-819b-77ca5c9d75a8`。
- 起止时间：2026-11-07T03:43:33 至 2026-11-07T03:51:31；正常完整模式启动，未预设数量上限。
- 主页清单 110 个 ID 且全部唯一；attempted=4、saved=2、no_ai=0、errors=2、pending=108（108 个 ID 全部唯一）。
- 停止原因：约 5 分钟无实质作品进展；进程退出码 2，已确认无本作者提取进程，锁可立即非阻塞获取，即锁已释放。
- 保存并人工读取核验：`20260525-7643659000369679626-恋爱检查，应该怎么查？（上）.md`（AI 正文 385 字）和 `20260709-7660433974442888484-亲密结束后，要不要复盘？.md`（AI 正文 156 字）。两篇作者、抖音号、作品 ID、日期、AI 标记及正文均匹配，无重复文件 ID，均不在 pending。
- 错误 ID：`7675722470506171654`、`7704580351188617977`，均为 `AI text or metadata timeout`，仍保留在真实 pending，未误记 no_ai。
- `提取状态.json` 与 `五worker运行状态.json` 均为 `running:false`、`partial:true`、`author_completed:false`；未生成 `文案校验.json` 或 `提取完成报告.json`。
- 下一批建议：协调器验收后使用 `--max-items 5` 断点续提；本批停止后未继续提取，未执行任何 Git 写操作。
