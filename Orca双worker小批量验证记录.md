# Orca 双 worker 小批量验证记录

> 开始时间：2026-11-07T01:54:17+0800
> 协调器：当前主会话
> Orca：1.4.246
> 目标：两个作者、两个 worktree、两个 isolated Profile、两个固定 page。2026-11-07 用户最新指令已将范围从每位 2 个（随后曾改为 30 个）扩大为两位作者各自主页的全部作品 AI 文案。每个 worker 经核验后提交并顺序合并到本地 `main`，不推送 GitHub。

## 一、固定边界

| Worker | 作者 | 抖音号 | 允许修改的目录 | 最新任务范围 |
|---|---|---|---|---|
| A | 不纸设计 | `0753bjy` | `tmp/0753bjy-不纸设计/`、`抖音关注/0753bjy-不纸设计/` | 该作者全部作品 |
| B | 魏起顺会拍照 | `WEI_QISHUN` | `tmp/WEI_QISHUN-魏起顺会拍照/`、`抖音关注/WEI_QISHUN-魏起顺会拍照/` | 该作者全部作品 |

禁止恢复或启动旧顺序队列；禁止修改 README、共享 45 人计划/状态；worker 不写主 checkout、不操作其他作者的页面或目录、不执行 Git commit/merge。

## 二、逐步执行记录

### 步骤 1：执行前基线检查

- 时间：2026-11-07T01:54:17+0800
- 执行者：协调器
- 操作：检查 HEAD、Git 状态、候选目录、共享文件 SHA-256 和活跃提取进程。
- HEAD：`a6b1a7172ccd624f73bf604d4650e709a185de41`（`main`）。
- Git：被跟踪文件无改动；已有未跟踪文件 `Orca多worktree并行提取调研.md`，本试点不得改动或删除它。
- 活跃 `run_next45.py` / `extract_author.py` 进程：0。
- 不纸设计：已有 `搜索账号核对.json`、`账号核对.json`；无提取进度、作品 ID、待补提、校验或完成报告；Markdown 0。
- 魏起顺会拍照：已有 `搜索账号核对.json`、`账号核对.json`；无提取进度、作品 ID、待补提、校验或完成报告；Markdown 0。
- 结果：通过，允许创建两个 worker。

基线 SHA-256：

| 文件 | SHA-256 |
|---|---|
| `README.md` | `00fff279d1caacffa5db70588ddc4501bbe15b81eddc985fe93cdd54cf1ad46b` |
| `Orca多worktree并行提取调研.md` | `7a7c11857635bd9db7df6c03eab0c5b273ef55317da55b4f0705f8f442f7d781` |
| `tmp/批次-商业人文知识-20261104/run_next45.py` | `87fe3252f28887e8dbfe6294b096203b515649c16c3df12437203b0b8dbdfaa2` |
| `后续45位作者提取计划.json` | `f1b3b552223d962994301264acd14455347de2983ae3bd34c8c23bc3647b1a66` |
| `后续45位顺序执行状态.json` | `9f65fcd9c231d665b27e0eb465d5b904ffb00c7e97baa795bf2bfa7c04616661` |

### 步骤 2：创建受监督 worker

- 时间：2026-11-07T01:57:42+0800
- 执行者：协调器
- 命令：`orca orchestration worker-start --spec-file <对应spec> --worktree new-top-level --repo id:da2e8721-3aa8-432b-8a51-fb648a32632c --base-branch main --agent claude --setup skip --json`。
- Worker A：创建成功，run `run_573b10a4429c`，dispatch `ctx_10721956fa22`，task `task_1392fdc11b89`，terminal `term_8916d347-e587-44c3-89eb-8effc7fb0040`。
- A worktree：`da2e8721-3aa8-432b-8a51-fb648a32632c::/Users/zhaojian/orca/workspaces/ai-learn/pilot-buzhi-0753bjy`。
- A 分支：`AdrianAndroid/pilot-buzhi-0753bjy`；基线 HEAD 与主分支一致。
- Worker B：第一次与 A 并行调用 `worker-start` 时被 Claude Code 自动权限分类器以 `Create Unsafe Agents` 拒绝，未创建 worktree 或浏览器资源。调整为单独创建一个受监督 worker；不改为不受监督任务，不绕过权限。
- Worker B：改为单独顺序调用后，于 2026-11-07T01:58:41+0800 创建成功；run 同为 `run_573b10a4429c`，dispatch `ctx_5c442e77c481`，task `task_27d7a2362aa5`，terminal `term_7c376d28-c981-44a7-aae5-f81ce7ab0beb`。
- B worktree：`da2e8721-3aa8-432b-8a51-fb648a32632c::/Users/zhaojian/orca/workspaces/ai-learn/pilot-wei-qishun`。
- B 分支：`AdrianAndroid/pilot-wei-qishun`；基线 HEAD 与主分支一致。
- 当前状态：A、B 可在各自边界内准备代码和第一闸门；双方均未获准进入抖音或提取。

### 步骤 3：核对 Orca 后台与界面可见性，并变更为全量提取

- 时间：2026-11-07T02:02:34+0800
- 用户反馈：Orca 界面未看到 worktree 列表或浏览器 tab。
- 实际检查：`worktree list` 返回主 checkout、A、B 共 3 个；两个 worker 均为 `live / in_progress`。
- A tab：`01b0f677-3907-4ee8-91d7-7f707439b8de`，Profile `9483ec18-4a86-4e2c-92d5-a2441a1cafb6`，URL `https://example.com/`。
- B tab：第一次查询时尚未创建；随后 worker 完成创建并复查到 `eb12641b-ca19-470e-8bc2-8e9bce2aed98`，Profile `2bd87da7-ccc5-4110-b058-691269a45eef`，URL `https://example.com/`。
- 判断：后台资源已实际存在；tab 按 worktree 分组，不会出现在主 checkout 的 tab 列表。若界面列表未同步，不能据此判定创建失败，也不能重复创建。
- 主 checkout 检查：只有既有调研文档和本总记录未跟踪，没有作者提取结果或共享文件改动。

- 时间：2026-11-07T02:05:21+0800
- 用户最新指令：先提出每位 30 个视频，随后明确“直接提取全部的AI文案看效果吧”；以后者为准，即两位作者各自主页全部作品，不再限 2 个或 30 个。
- 协调器已向 A 发送 `msg_a3e5eb47b14c`、向 B 发送 `msg_ec69b0d19ffa`，要求正式运行不带 `--max-items`，使用完整模式、三轮既有重试及完整校验/完成报告。
- 保持不变：独立 worktree/Profile/page、作者互斥、显式 worktree+page、隔离与登录闸门、只处理各自作者、详细记录、完成后顺序合并本地 `main`、不推送。
- 当前状态：尚未收到双方第一闸门的 ask，协调器未回复任何抖音导航或提取许可。

### 步骤 4：Worker A 第一闸门独立复核（尚未放行）

- 时间：2026-11-07T02:11:49+0800
- 收到 A 问题 `msg_4cf97e3b8d24`，明确任务已改为 FULL AUTHOR；B 尚未提交第一闸门问题。
- A 的 `tab show`、`tab profile show` 由协调器重新执行：page `01b0f677-3907-4ee8-91d7-7f707439b8de`、Profile `9483ec18-4a86-4e2c-92d5-a2441a1cafb6`、worktree 和 `https://example.com/` 均匹配。
- A Git 改动仅位于 `tmp/0753bjy-不纸设计/`；`git diff --check` 通过。
- `静态路径测试.json`：语法、ROOT/TMP/OUT 边界、共享 page 移除均通过，浏览器调用和抖音访问均为 0。
- `互斥锁测试.json`：锁竞争第二进程返回 4，在浏览器调用前退出，未创建浏览器审计或 TMP 新文件。
- `环境参数测试.json`：缺少 worktree/Profile/page 均失败且没有浏览器调用。
- 当前决定：A 单项证据通过，但必须等 B 就绪后共同执行跨 Profile 存储与导航隔离；尚未回复 A，未允许导航抖音或提取。

### 步骤 5：Worker B 复核及双 Profile 隔离验收

- 时间：2026-11-07T02:15:42+0800
- 收到 B 问题 `msg_26063553f17c`，明确 FULL AUTHOR。协调器复查 B 的 worktree/Profile/page、`静态与锁测试.json` 和 Git 边界，均通过；锁竞争第二进程返回 73，TMP 未变、OUT 未创建。
- 两个 worktree、分支、Profile、page、TMP 和 OUT 均不同，输出路径无重叠。
- 协调器在 `https://example.com/` 使用显式 worktree+page 执行跨 Profile 测试，结果 7/7 通过：
  1. A 写入值不出现在 B。
  2. B 写入值不出现在 A。
  3. A 自己的值在测试和导航后均保留。
  4. B 自己的值在 A 导航前后均保留。
  5. A 导航时 B 的 URL 不变。
  6. A 导航后 B 仍不能读取 A 的值。
  7. A 自身导航实际发生，证明对照有效。
- 非敏感测试值均从双方 localStorage 清理，没有读取或记录 Cookie/登录凭据。
- 协调器回复 A：第一闸门通过消息 `msg_ef44bc8e4abb`；回复 B：`msg_6414767c8b8f`。仅允许各自打开自己的作者主页核对身份和登录，尚未允许提取。
- 主 checkout 复核：两个作者 Markdown 仍均为 0；只有既有调研文档和本总记录未跟踪，没有 worker 写回主目录。

### 步骤 6：登录阻断及当前状态复核

- 时间：2026-11-07T02:21:33+0800
- A 问题 `msg_045480b64476`、B 问题 `msg_7a2c8870080d` 均报告：作者名、抖音号、sec_uid 和作品数正确，但当时出现登录/关注，已关注=false；双方均未开始提取。
- 协调器尝试仅点击明确的“登录”按钮以展示扫码面板；A 请求 `70a99743-28cf-4f30-9321-bc50e220cba1`、B 请求 `12025b5d-3b24-4367-a78e-64aeddb4b094` 均返回 `clicked:false`，未执行点击。
- 随后协调器直接读取当前页面：A `bd49aa7c-3db0-48d9-907f-7386cf56adb1`、B `8190583a-d8b0-48ef-bcd9-279288690790` 均显示正确 h1、“已关注”和“私信”，登录按钮不存在。未读取或保存 Cookie、二维码或凭据，不推测状态变化来源。
- 当前无需用户扫码。已回复 A `msg_4ec7e1adc231`、B `msg_4b5e30071c20`，要求各自重新核对当前身份、登录态和绑定；仍需第二闸门才能全量运行。

### 步骤 7：第二闸门复核并放行全量提取

- 时间：2026-11-07T02:27:08+0800
- 收到 A `msg_19fb2b1c1c60`、B `msg_7ac4803e5856` 的 `FULL_AUTHOR_READY`。
- 协调器审查两份完整 diff：正式命令不带 `--max-items`，完整模式最多三轮并调用 `validate()`；fatal 登录、验证码、限流或页面失效停止。环境绑定、相对输出、作者锁和显式 worktree+page 均在代码中落实。
- 组合式只读预检脚本被自动权限分类器拒绝，未执行；随后改为分别执行简单 Orca eval。
- A 最终实时检查 `6caea9d6-9071-42ae-a5db-62ff1879f316`：不纸设计、`0753bjy`、作品 26、已关注=true、登录/验证码/限流=false。
- B 最终实时检查 `aada5f3d-a460-49fe-ae4c-748b2c33ee8d`：魏起顺会拍照、`WEI_QISHUN`、作品 41、已关注=true、登录/验证码/限流=false。
- 活跃 `run_next45.py` / `extract_author.py` 进程为 0；主 checkout 仍只有两份协调器文档未跟踪。
- 统一计时命令也被权限分类器拒绝，未执行；不等待额外计时，改为同时回复立即启动，后续用实际日志验证运行重叠。
- 全量放行：A 回复 `msg_e320db73daad`，B 回复 `msg_6054e844494d`。仅允许各自作者、各自 worktree/page，完整提取和校验；不 commit/merge。

### 步骤 8：Worker A 全量完成、独立核验、提交及合并

- 完成通知：A 报告全量提取 26/26，退出码 0；实际运行区间为 2026-11-07T02:27:47 至 2026-11-07T02:31:28（本地时间），saved=26、no_ai=0、errors=0、pending=0。A 未执行 commit/merge/push。
- 协调器独立核验：A 活跃提取进程为 0，作者互斥锁可立即获取，确认进程已退出且锁已释放。
- 内容核验：主页清单 26 个唯一 ID；26 个 Markdown 含 26 个唯一 ID，文件集合与主页清单精确相等；无无效文件、重复 ID 或列表外作品。逐篇作者、抖音号、作品 ID、创作日期、AI 标记、正文长度及进度文件名均通过；Markdown 长度范围 332–1180 字符。
- 状态核验：`试点运行状态.json` 为 `full_author:true`、`max_items:null`、`author_completed:true`、`运行结果:full_author_completed`；`提取状态.json` 为 `running:false`、`partial:false`；待补提列表为空；完成报告为 saved=26、no_ai=0、error=0。
- 内容清单 SHA-256：`d8aec846f43e3ae7ace584c38aa342de46dd820382814662f326f629629e55b5`。计算方式：按文件名排序，依次写入 UTF-8 文件名、NUL、文件字节、NUL。
- Git 合并闸门：`git diff --check` 通过；变更共 45 项，其中作者 Markdown 26 项，越界路径为空。只暂存 `tmp/0753bjy-不纸设计/` 和 `抖音关注/0753bjy-不纸设计/`，staged 清单复核和 `git diff --cached --check` 均通过。
- Worker A 提交：`12df38bd884ab3be2f48d10a64b5d788d28d9341`，提交信息“完成不纸设计全量AI文案提取”。
- 本地合并：2026-11-07T02:41:38+08:00 前完成 `git merge --no-ff AdrianAndroid/pilot-buzhi-0753bjy`，合并提交 `c7732396c628ab0180b230bb3c50e7fc511b3216`；父提交为原基线 `a6b1a7172ccd624f73bf604d4650e709a185de41` 与 A 提交 `12df38bd884ab3be2f48d10a64b5d788d28d9341`。
- 合并后复验：26 篇内容清单 SHA-256 完全一致，全部内容/状态检查再次通过；相对原基线共 45 个变更路径，越界为空。README、既有调研文档、共享 45 人计划/状态及 `run_next45.py` 的 SHA-256 均与基线相同。主 checkout 仅有协调器总记录和既有调研文档两个未跟踪文件；未推送 GitHub。
- 当前状态：A 已 settled 并合并；B 的结果尚未在本节记录，继续等待其 Orca 完成通知，不重复启动 worker 或提取器。

### 步骤 9：Worker B 用户确认全作者无 AI、独立核验、提交及合并

- 完成通知：B 最终报告 saved=0、no_ai=41、errors=0、pending=0，有效输出 Markdown=0；未 commit/merge/push。
- 实际执行：首次完整运行 2026-11-07T02:27:52+08:00 启动；用户先指示单个作品无 AI，随后明确“我看了一下，这个作者所有的视频都没有AI文案，记录”。worker 停止两次运行并确认进程消失；被停止 wrapper 未产生退出码，记录中未伪造成 0。最终完整模式校验和状态刷新分别于 02:38:41–02:38:43、02:40:26–02:40:27 运行，退出码均为 0，本轮不再尝试作品。
- 用户判定及历史保留：41 个主页 ID 的最新进度均为 `no_ai`，来源为用户直接指令；累计自动尝试 7 个不同 ID，两个历史 timeout 和此前 saved 行仍保留在进度历史。先前生成的 5 篇 Markdown 被可逆移动到 `tmp/WEI_QISHUN-魏起顺会拍照/用户确认无AI-误提取隔离/`，未删除，不计入最终有效 AI 文案。
- 协调器独立核验：B 活跃提取进程为 0，作者锁可立即获取；主页 41 个 ID 唯一，49 行历史进度收敛为 41 个最新 ID，最新状态全部 no_ai；有效输出 Markdown=0，隔离目录 5 个非空 Markdown；待补提为空；`full_author:true`、`max_items:null`、`author_completed:true`、`running:false`、`partial:false`；完成报告为 saved=0、no_ai=41、error=0。所有检查通过。
- Git 合并闸门：初次 `git diff --cached --check` 发现 `试点执行记录.md` 末尾多一个空行，仅修正该空白后重新检查通过。最终 staged 23 项，其中有效输出 Markdown=0、隔离 Markdown=5；越界路径为空。
- Worker B 提交：`27a7f4d94552d48a4f9cb5ee0b28501053324c6f`，提交信息“记录魏起顺会拍照全作者无AI文案”。
- 本地合并：`git merge --no-ff AdrianAndroid/pilot-wei-qishun`，合并提交 `d862370c55346db2e3b4e833649c7488bb081a94`；父提交为 `c7732396c628ab0180b230bb3c50e7fc511b3216` 与 B 提交 `27a7f4d94552d48a4f9cb5ee0b28501053324c6f`。合并后 `git diff --check` 通过；未推送 GitHub。
- 并行时间核验：A 运行区间 02:27:47–02:31:28，B 首次运行从 02:27:52 开始，二者至少在 02:27:52–02:31:28 重叠 3 分 36 秒，因此真实并行执行成立，不只是两个任务先后运行。

## 三、验收结论

- **隔离与互斥通过**：双 Profile 的 localStorage 与导航隔离实测 7/7 通过，环境绑定、相对输出路径、显式 worktree+page 和作者互斥锁测试通过。
- **真实并行通过**：A/B 实际运行区间重叠 3 分 36 秒；提取期间未写主 checkout，作者输出路径无重叠。
- **Worker A 内容完成**：不纸设计 26/26 篇有效 AI 文案，0 无 AI、0 错误、0 待补提；独立提交 `12df38bd884ab3be2f48d10a64b5d788d28d9341`，合并提交 `c7732396c628ab0180b230bb3c50e7fc511b3216`，合并后内容清单 SHA-256 不变。
- **Worker B 按用户现场确认完成**：魏起顺会拍照 41 个作品最终均为无 AI，saved=0、errors=0、pending=0；5 篇早期草稿可逆隔离保留，未计为有效文案。独立提交 `27a7f4d94552d48a4f9cb5ee0b28501053324c6f`，合并提交 `d862370c55346db2e3b4e833649c7488bb081a94`。
- **边界保持**：README、既有调研文档、共享 45 人计划/状态及旧队列脚本未被 worker 修改；不恢复旧队列，不处理其他作者；worktree、Profile 和 page 保留；未推送 GitHub。
