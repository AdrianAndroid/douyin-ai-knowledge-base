# Orca 多 worktree 并行提取 AI 文案调研

> **归档说明（2026-11-07）：多 worktree 方案已由用户决定停用。本文仅保留当时调研结论，不再作为创建 worktree、worker、Profile 或 page 的执行指令。归档总结见同目录 `README.md`。**

> 调研日期：2026-11-07  
> Orca 版本：1.4.246  
> 调研方式：只读检查 Orca CLI、浏览器 Profile 能力、现有提取脚本和进程状态。  
> 状态：**仅完成调研，尚未创建测试 worktree、浏览器 Profile 或并行提取任务，也未完成代码改造。**

## 一、结论

可以通过 Orca 实现并行提取，但当前代码不能直接安全地并行运行。

推荐的目标模型是：

> **一个作者 = 一个 Orca worktree = 一个受监督 agent = 一个独立浏览器 Profile = 一个固定 page ID**

必须同时完成以下四层隔离：

1. 作者任务唯一，不能重复领取同一作者。
2. 文件路径按 worktree 隔离，不能写回主 checkout。
3. 浏览器 Profile 独立，不能共享登录会话和页面状态。
4. 浏览器命令固定到明确的 worktree 和 page，不能依赖“当前标签页”。

需要注意：Orca 内置浏览器可以提供标签页和浏览器会话隔离，但这不等于每个 worktree 都运行一个独立的 Chrome/Chromium 操作系统进程。如果要求进程级隔离，需要为每个 worker 单独启动 Chromium。

## 二、已确认的 Orca 能力

本机 Orca CLI 为 `/Applications/Orca.app/Contents/Resources/bin/orca`，版本为 1.4.246。

| 能力 | Orca 接口 | 用途 |
|---|---|---|
| 创建 worktree 并启动 agent | `orca worktree create --agent claude` | 为独立任务创建 checkout 和 agent |
| 创建受监督 worker | `orca orchestration worker-start --worktree new-top-level` | 让协调器分派任务并接收结果 |
| 指定 worktree 的浏览器 | `--worktree <完整worktreeID>` | 限定标签页所属工作区 |
| 固定浏览器页面 | `--page <browserPageId>` | 避免“当前标签页”变化导致误操作 |
| 创建隔离浏览器会话 | `orca tab profile create --scope isolated` | 为 worker 创建独立 Profile |
| 将标签页绑定到 Profile | `orca tab create --profile <profileID>` | 建立页面与会话的对应关系 |
| 检查页面 Profile | `orca tab profile show --page <pageID>` | 启动前验证浏览器绑定 |

浏览器操作可以固定为以下形式：

```bash
orca eval \
  --worktree id:<repoId>::<worktreePath> \
  --page <browserPageId> \
  --expression '<JS>' \
  --json
```

Orca 文档明确说明：

- 内置浏览器标签页按 worktree 组织。
- `--page` 使用稳定的 `browserPageId`，适合并发工作流。
- `--page` 可以跨 worktree 找到页面，因此仅创建多个 worktree 并不能防止脚本操作同一个页面。
- 页面引用 `@e1` 等只所属一个标签页，并会在导航或切换后失效。

本次只读检查时，机器上仅存在默认浏览器 Profile。尚未实际创建多个隔离 Profile，因此 Cookie、localStorage、登录态和导航隔离仍需通过后续试验验收。

## 三、当前代码的阻塞问题

### 3.1 后续 45 位作者共用同一个浏览器页面

只读汇总后续 45 位作者的 `配置.json` 得到：

| 检查项 | 结果 |
|---|---:|
| 计划作者数 | 45 |
| 不同的 `page` ID 数 | 1 |
| 使用该页面的配置数 | 45 |

以凯哥恋爱说为例：

- `tmp/52327471915-凯哥恋爱说/配置.json:5` 写死 `page`。
- `tmp/52327471915-凯哥恋爱说/extract_author.py:16` 读取该固定页面。
- `tmp/52327471915-凯哥恋爱说/extract_author.py:106-117` 调用 `orca eval --page <固定页面ID>`。

提取器没有为每个任务设置独立页面，也没有同时传入自己的 worktree。直接并行会造成多个作者互相：

- 导航页面；
- 打开或关闭作品弹层；
- 修改页面中的暂停和 AI 点击状态；
- 读取其他任务刚切换的作品；
- 将导航或页面失效错误误记为提取结果。

### 3.2 新 worktree 仍会写回主目录

凯哥恋爱说的配置在 `tmp/52327471915-凯哥恋爱说/配置.json:7` 使用：

```text
/Volumes/wd/ai-learn/抖音关注/52327471915-凯哥恋爱说
```

提取器在 `extract_author.py:18` 直接读取该绝对输出路径。

45 位作者的配置全部指向以下主目录：

```text
/Volumes/wd/ai-learn/抖音关注
/Volumes/wd/ai-learn/tmp
```

因此，即使在新 worktree 中执行，文案和中间状态仍可能写回主 checkout，Git worktree 的文件隔离会失效。

### 3.3 顺序执行器不适合直接并行

`tmp/批次-商业人文知识-20261104/run_next45.py` 会顺序处理整个队列，并修改共享文件：

- `后续45位作者提取计划.json`
- `后续45位顺序执行状态.json`

相关逻辑位于 `run_next45.py:28-61`，其中计划读取、状态写入和子进程启动没有并行锁或合并机制。

多个 worker 如果同时启动该执行器，可能出现：

- 同一作者被重复领取；
- 计划和状态相互覆盖；
- 进度回退；
- 断点文件竞争；
- 同一作者目录被多个进程同时写入。

因此每个并行 worker 只能运行分配给自己的单作者提取器，不能启动完整的 `run_next45.py`。

### 3.4 同一作者仍需互斥

单作者脚本已经有一些可复用的相对路径设计：

- `extract_author.py:11` 根据 `__file__` 确定 `TMP`。
- `extract_author.py:20-23` 将进度、状态、作品 ID 和待补提文件放在该目录。

但同一作者若被启动两次，仍会竞争以下文件：

- `提取进度.jsonl`
- `提取状态.json`
- `待补提作品.json`
- `文案校验.json`
- `提取完成报告.json`
- 同一个 AI 文案输出目录

所以仍需要“一个作者最多一个活跃 worker”的互斥机制。

## 四、推荐隔离设计

### 4.1 任务隔离

由协调器维护作者分配表，每个 worker 只处理一个作者：

```text
worker A → 作者 A → worktree A → branch A
worker B → 作者 B → worktree B → branch B
```

worker 不得：

- 自行领取其他作者；
- 启动完整顺序队列；
- 修改其他作者的目录；
- 修改全局 README、总计划和汇总报告。

全局文档由协调器在结果验证和合并后统一更新。

### 4.2 浏览器隔离

每个 worker 必须拥有独立且明确的：

- `worktreeId`
- `profileId`
- `browserPageId`

概念性创建和检查流程：

```bash
orca tab profile create --label douyin-<作者ID> --scope isolated --json

orca tab create \
  --worktree id:<repoId>::<worktreePath> \
  --profile <profileId> \
  --url <作者主页URL> \
  --json

orca tab profile show \
  --worktree id:<repoId>::<worktreePath> \
  --page <browserPageId> \
  --json
```

启动提取前必须断言：

1. 三个 ID 均存在。
2. 任意两个 worker 的 `profileId` 和 `browserPageId` 不相同。
3. `tab profile show` 返回预期的 Profile。
4. 页面所属 worktree 与 worker 一致。
5. 当前作者主页 `sec_uid` 与分配任务一致。

所有浏览器命令必须同时携带 `--worktree` 和 `--page`。禁止：

- 使用默认 Profile；
- 使用“当前标签页”；
- 依赖 `tab switch` 后再操作；
- 不带 `--page` 的 `eval`、`goto`、`click`、`keypress` 等命令；
- 在任务中途切换到其他 worker 的 Profile 或页面。

新的隔离 Profile 可能需要分别完成抖音登录。是否可以安全复用或导入现有登录态，尚未实测，不能默认认为新 Profile 已登录。

### 4.3 文件隔离

将配置和批次计划中的绝对路径改为当前 worktree 内路径：

```text
<当前worktree>/抖音关注/<作者>/
<当前worktree>/tmp/<作者>/
```

启动时增加以下检查：

- 输出路径必须位于当前 worktree。
- 输出目录必须匹配分配的作者和抖音号。
- 禁止写入 `/Volumes/wd/ai-learn` 主目录。
- 禁止修改其他作者目录。
- 文案继续使用临时文件和原子替换。
- 同一作者的锁文件不得只放在所有 worktree 都能无条件修改的共享位置。

每个作者一个分支，只提交自己的文案和进度；协调器逐个验证并合并，避免共享汇总文件产生冲突。

### 4.4 运行隔离

- 一个作者一把互斥锁，防止重复启动。
- 每个 worker 只执行单作者脚本。
- worker 的失败、重试和退出不能自动触发其他 worker 重试。
- 一个 worker 的页面失效不能由另一个 worker 代为修复。
- 协调器统一处理结果、更新总进度和合并分支。
- 初次只启动两个 worker，通过验收后再考虑增加并发。

## 五、必须通过的验收试验

在正式并行提取前，至少完成以下测试：

### 5.1 浏览器绑定测试

- worker A、B 的 worktree ID 不同。
- Profile ID 不同。
- page ID 不同。
- 两个页面均返回预期 Profile 和 worktree。

### 5.2 浏览器会话隔离测试

在无害测试页面中验证：

- A 设置的 Cookie 或 localStorage 不会出现在 B。
- A 导航页面不会改变 B 的 URL。
- A 关闭或打开弹层不会改变 B。
- A 的页面刷新不会使 B 的元素引用失效。
- 停止 A 后，B 仍能继续读写自己的进度。

### 5.3 文件隔离测试

- 两个 worker 只能写各自 worktree 的作者目录。
- 主 checkout 不出现新增或变化。
- 不出现跨作者作品 ID。
- 不出现共享进度文件覆盖。
- 重复启动同一作者会被互斥锁拒绝。

### 5.4 小规模真实提取测试

- 仅选择两个不同作者，各处理少量作品。
- 每条结果核对作者、抖音号、作品 ID、日期和 AI 正文。
- 检查无重复 Markdown、无列表外作品、无跨作者文案。
- 验证暂停、恢复和失败重试不会产生重复结果。
- 试验通过前不扩大并发，不处理完整作者队列。

## 六、保证范围和限制

### 6.1 Orca 内置浏览器不是独立 OS 浏览器进程

独立 Profile 和 page 可以提供会话与页面隔离，但不能据此声称每个 worker 使用独立浏览器进程。

如果必须实现进程级隔离，应在每个 worktree 中启动独立 Chromium，并分别设置：

- 独立 `--user-data-dir`；
- 独立远程调试端口；
- 独立浏览器 PID；
- 提取器只连接自己的调试地址。

### 6.2 无法保证抖音服务端绝对互不影响

即使本机文件和浏览器完全隔离，相同账号、IP 或访问频率仍可能触发：

- 验证码；
- 限流；
- 登录失效；
- AI 功能暂时不可用；
- 服务端风险控制。

因此不能承诺平台侧绝对互不影响，应限制并发并保留失败断点。

### 6.3 旧暂停记录不能直接作为当前进程依据

调研时未检测到正在运行的 `run_next45.py` 或 `extract_author.py`，旧暂停记录中的三个 PID 也已不存在。

后续不能直接依赖旧文档中的 `kill -CONT` 恢复命令，也不能让旧顺序执行器与新的并行 worker 同时运行。

## 七、后续实施顺序

1. 将单作者提取器改为接收明确的 worktree、Profile 和 page 配置。
2. 移除输出和中间目录的主 checkout 绝对路径。
3. 增加浏览器绑定和文件路径的启动前断言。
4. 增加作者级互斥和 worker 分配记录。
5. 禁止并行 worker 启动完整顺序执行器。
6. 创建两个测试 worker，完成浏览器和文件隔离验收。
7. 通过两位作者的小规模真实提取后，再决定是否扩大并发。

**最终判断：方案可行，但当前版本直接多开不安全；必须先改造并完成双 worker 验收。**
