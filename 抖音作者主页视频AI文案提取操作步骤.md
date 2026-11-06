# 抖音作者主页 视频AI文案提取 - 操作步骤（模拟人工点击版）

> 记录时间：2026-11-03
> 适用对象：凯哥的恋爱课堂（抖音号 40618523363）等作者主页
> 核心结论：**用 `browser_use`（bu）操作，所有点击一律用 `click_xy` 模拟人工点击，且必须使用 0-1000 归一化坐标，否则竖向会偏移。**

---

## 一、整体流程（从主页点开视频到翻页）

```
1. 打开作者主页
2. 点击第 N 个视频（弹窗形式打开）
3. 悬停"AI抖音"按钮，展开上下翻页箭头
4. 点击"向下箭头"翻到下一个视频
5. 读取右侧 AI 解读面板文案
6. 按命名规范保存为 Markdown 文档
```

---

## 二、关键坐标换算（最容易出错的地方 ⚠️）

**`bu.click_xy` 使用的坐标是 0-1000 的归一化坐标，不是像素坐标！**

换算公式：
```
归一化X = 像素X / 视口宽(1131) × 1000
归一化Y = 像素Y / 视口高(1064) × 1000
```

示例（视口 1131×1064）：
| 目标 | 像素坐标 | 归一化坐标（click_xy 填这个） |
| --- | --- | --- |
| 主页第7个视频 | (约横, 竖) | 用 `read_all("a[href*='/video/']")` 定位后 bu.click(ref) |
| 向下翻页箭头 | (744, 276) | (658, 259) |

> **教训**：直接把像素坐标填进 `click_xy` 会导致水平正确、竖向偏移一段距离，点击无效或点错目标。

---

## 三、分步操作详解

### 步骤1：打开作者主页
```python
# 搜索进入用户主页
bu.navigate("https://www.douyin.com/search/凯哥的恋爱课堂?type=user")
bu.wait_for_load(timeout=10)
# 找到目标账号卡片（注意区分同名的"阿恺的恋爱课堂"等）
m = bu.find("凯哥的恋爱课堂", search_type="all", limit=10)
# 取 href 含 /user/ 的链接，导航过去
```

### 步骤2：点击主页中的某个视频（弹窗打开）
```python
# 读取作品列表（video 链接）
rows = bu.read_all("a[href*='/video/']", fields=["text","href"], limit=30)
# rows[6] 即第7个视频，拿到 ref（如 n587）
bu.click("n587")
bu.wait_for_load(timeout=10)
# 视频以弹窗打开，URL 变为 ...?modal_id=XXXX
```

### 步骤3：悬停"AI抖音"按钮，展开上下翻页箭头
```python
# AI 入口按钮 class 含 ai-douyin-entry，找到视口内可见的那个
# 用 JS 派发鼠标事件模拟悬停（bu.hover 对 offscreen 元素会失败，改用 JS 事件）
bu.js("""
(() => {
  const els = document.querySelectorAll('[class*=ai-douyin-entry]');
  let target = null;
  for (const el of els) {
    const r = el.getBoundingClientRect();
    if (r.top>=0 && r.top<1064 && r.left>=0 && r.left<1131) { target = el; break; }
  }
  if (!target) return;
  const r = target.getBoundingClientRect();
  const cx = r.left + r.width/2, cy = r.top + r.height/2;
  for (const type of ['pointerover','pointerenter','mouseover','mouseenter','pointermove','mousemove']) {
    target.dispatchEvent(new MouseEvent(type, {bubbles:true, cancelable:true, clientX:cx, clientY:cy}));
  }
})()
""")
```
- 悬停后"AI抖音"文字才出现，且 AI 按钮上方出现**一上一下两个箭头**
- 向上箭头 / 向下箭头是两个 `semi-icon`，位于 AI 按钮上方

### 步骤4：模拟人工点击"向下翻页箭头"
```python
# 先定位 AI 按钮和上方箭头的像素坐标
# 向下箭头像素中心约 (744, 276)
# 换算成归一化坐标：744/1131*1000≈658，276/1064*1000≈259
bu.click_xy(658, 259)   # 点击向下箭头，翻到下一个视频
bu.wait_for_load(timeout=8)
```
- 翻页成功的标志：URL 中 `modal_id` 变为下一个视频的 ID（如 7699769117015854390 → 7699097554484153615）

### 步骤5：读取右侧 AI 解读面板文案
```python
# get_page_text 拿不到面板正文，需用 JS 抓取包含"以上内容由AI生成"的可见容器
# 完整文案包含：导语 + 各时间节点要点 + 需要留意部分
```

### 步骤6：保存为 Markdown 文档
- 路径：`/Volumes/wd/ai-learn/抖音关注/{抖音号-昵称}/{创作时间YYYYMMDD}-{作品ID}-{标题}.md`
- 格式参照已有文档（标题/作者/抖音号/作品ID/创作时间/标签 + 文案 + "以上内容由AI生成，仅供参考"）

---

## 四、本次实测结果（凯哥的恋爱课堂）

| 视频 | 作品ID | 保存文件 |
| --- | --- | --- |
| 让女生对你投降的5大软肋 | 7699769117015854390 | 20261023-7699769117015854390-让女生对你投降的5大软肋.md（已有） |
| 哪种女生才是最好追的？ | 7699097554484153615 | 20261021-7699097554484153615-哪种女生才是最好追的？.md（本次新建） |

---

## 五、常见坑与对策

| 问题 | 现象 | 对策 |
| --- | --- | --- |
| 坐标竖向偏移 | 点不到目标，翻页失败 | `click_xy` 必须用 0-1000 归一化坐标，先换算 |
| AI 按钮 offscreen | `bu.hover` 报 offscreen | 改用 JS 派发 mouseover/mouseenter 事件模拟悬停 |
| get_page_text 拿不到AI文案 | 只有主页列表 | 用 JS 抓取含"以上内容由AI生成"的可见容器 |
| 同名账号混淆 | 搜到多个"凯哥" | 用抖音号 + 简介区分，取 href 含 `/user/` 的正确账号 |
| 有的视频无AI总结 | 面板为空 | 跳过即可 |

---

## 六、重大修正：OCR box 坐标本身就是 0-1000 归一化（X轴偏移的根因）⚠️⚠️

**关键发现（2026-11-03 深夜，用户洞察 + 实测确认）：**

**`bu.screenshot()` 返回的 OCR 里，每个 `box` 的坐标已经是 0-1000 的归一化千分比坐标！**（截图元信息明确标注"左上角(0,0)，右下角(1000,1000)"）

**之前的致命错误**：把 OCR 的 box 坐标当成"像素坐标"，再用 `X/1131*1000、Y/1064*1000` 换算一遍，导致坐标被二次缩放。

**后果**：X 被多除一次（1131/1000≈1.13），Y 被多除一次（1064/1000≈1.06）。因为 Y 偏差比例小、X 偏差比例大，所以表现为"**Y 轴总是对的，X 轴总是偏左/偏右**"——正是用户反复观察到的现象。

**正确做法**：
```
1. 从 OCR 拿到元素 box，例如 AI 按钮 box(934,310,974,355)
2. 直接取中心：( (934+974)/2, (310+355)/2 ) = (954, 332)
3. bu.click_xy(954, 332)   ← 直接填，不再做任何换算！
```
> 注意：这是针对 **OCR box** 的用法。若你用像素工具自行测量（如 Read 本地图片的坐标），才需要换算成归一化。

---

## 七、纯视觉操作流程（最可靠，推荐）⚠️

**背景**：`bu.js` / `bu.read_all` / `bu.extract_content` / `bu.navigate` 频繁报"工具不存在"，且 DOM/JS 类操作易触发抖音反自动化。**只有 `bu.screenshot()` 和 `bu.click_xy()` 相对稳定。**

**因此改用"纯视觉 + 模拟人工点击"**，并解决"翻页切到别的作者"问题：

```
1. 打开作者主页，用 read_all 取作品 ref（若失败，用截图 + click_xy 点网格卡片）
2. 从主页点击目标视频（弹窗打开，URL 带 modal_id）
3. 【先暂停视频】点击视频画面中央（归一化约 400,450），减少动态渲染、降低失败率
4. 【截图确认】确认右侧操作栏是否有 AI 按钮；若没有：
   → 【先点击评论】点击右侧"评论"按钮，AI 按钮会重新出现/靠边
5. 【点击评论后顶部出现标签栏】AI/TA的作品/评论/相关推荐
6. 【点击顶部 AI 标签】(OCR 直接取中心) → 右侧切换为 AI 解读面板
7. 【等 AI 文案加载完成】等待 3-5 秒，确认出现"以上内容由AI生成，仅供参考"
8. 【截图读取文案】用 OCR 读取右侧面板文本（或 JS 抓取，若可用）
9. 保存 Markdown 文档
```

**翻页安全规则（用户反复强调）**：
- **绝不能停留在"相关推荐"栏翻页**，否则会切到其他作者的视频（曾跳到 kenny慢慢说）
- 必须切到 AI 栏（或从主页重新点开下一个视频）
- 最可靠：**每次从主页作品网格重新点开下一个视频**（播放队列才是本作者的作品）

**无 AI 功能的视频**：右侧只有点赞/评论/收藏/转发/听抖音，没有 AI 按钮，且点 AI 标签后检测"以上内容由AI生成"为空 → 跳过。

---

## 八、工具调用失败的根因与修复（2026-11-03 深夜，重大）⚠️⚠️⚠️

**现象**：所有 `browser_use` 相关调用（navigate/read_all/js/screenshot/click_xy）间歇性报 `Tool "" was not found or is not available.`，注意报错里工具名是**空字符串**。

**根因**：`browser_use` 是 **deferred（延迟加载）工具**，其参数 schema 在长对话中被压缩/丢失后，如果继续用 `execute_defer_tool(toolName="browser_use", ...)` 调用，框架无法解析工具名 → 报"工具不存在"。**浏览器会话本身一直活着**（`bu.page_info()` 能返回当前 URL 和视口）。

**修复（绕开办法）**：
```
1. 先调用 tool_search 重新获取 browser_use 的真实 schema（关键词搜 "browser_use"）
2. 之后【直接调用 browser_use 工具本身】（不是 execute_defer_tool）
3. 参数用真实 schema：{ code, plane:"bu", title, timeout_ms }
```
> 修复后工具完全稳定，批量处理不再失败。**每次长对话若再次出现"工具不存在"，先 tool_search 重新激活 schema，再直接调 browser_use。**

---

## 九、已验证的完整可复制流程（当前最稳，逐视频执行）✅

**单视频提取步骤**（每步截图确认）：
```
A. 从主页打开目标视频：
   rows = bu.read_all("a[href*='/video/{作品ID}']", fields=["text","href"], limit=3)
   bu.click(rows[0]['ref'])   # 或用 click_xy 点网格卡片
B. 暂停视频：bu.click_xy(400, 450)   # 点视频画面中央，减少动态渲染
C. 截图确认：frame = bu.screenshot(with_cursor=False)
   - 若右侧操作栏有 AI 按钮（OCR 找 "AI"）→ 跳到 E
   - 若没有（只有点赞/评论/收藏/转发/听抖音）→ 先 D
D. 点评论让 AI 按钮重现：点击右侧"评论"按钮（OCR 找评论数据所在列）
E. 点击 AI 按钮（OCR 中 AI 的 box 中心，直接点）
   - 点击后顶部出现标签栏 AI/TA的作品/评论/相关推荐
F. 点击顶部 AI 标签（OCR 中顶部 "AI" box 中心，归一化约 715-730,24）
G. 等 AI 文案加载完成（3-5 秒），确认出现"以上内容由AI生成，仅供参考"
H. 提取文案：
   ai = bu.js("找含'以上内容由AI生成'的可见文本块，返回 textContent")
   # 注意：匹配到的元素可能是 script/CSS（输出会混入大量脚本源码）
   # 改进：限定 div/span 且 getBoundingClientRect().left>600 且不是 script/style
I. 保存文档：/Volumes/wd/ai-learn/抖音关注/40618523363-凯哥的恋爱课堂/{创作时间YYYYMMDD}-{作品ID}-{标题}.md
```

**AI 文案 JS 提取要点**：
- 直接匹配"以上内容由AI生成"可能命中页面里的 script/CSS 源码，输出会混入几万字符的脚本。
- **改进**：`querySelectorAll('div,section,article,p,span')` + 过滤 `getBoundingClientRect().left>=600 && top>=40 && width>=200`，取最长的含该标记的文本容器。
- 文案结构：导语 + 多个"时间点 小标题"章节 + 结尾引导语 + "以上内容由AI生成，仅供参考"。

**命名规范**（与已有文档一致）：`创作时间(YYYYMMDD)-作品ID-标题.md`
- 创作时间来自视频左下角"@凯哥的恋爱课堂·10月XX日"，需换算成 YYYYMMDD
- 标题去掉话题标签

**已知无 AI 视频**（右侧操作栏无 AI 按钮，跳过）：已确认第9、10个无 AI。

---

## 十、当前批量最稳流程（2026-11-03 深夜确认，逐视频 100% 稳定）✅✅

**核心变化**：不再每次回主页点开视频，而是**在 AI 栏打开状态下直接按键盘下键翻页**。用户确认：当前视频 AI 栏打开时，AI 按钮上方有一个下翻按钮，点它或按键盘 `ArrowDown` 都能翻到作者下一个视频；**只要不停留在"相关推荐"栏，向下翻就是本作者下一个视频**。

### 单视频流程（17 个视频全部成功，无失败轮）

```
1. 翻页：AI 栏打开状态下 bu.press_key("ArrowDown") → sleep 4+3
   → 打印 URL，确认 modal_id 变为同作者下一个视频（若落到"相关推荐"栏立即中止）
2. 主路径提取 AI_LEN：
   ai = bu.js("遍历 div/section/article/p，排除 SCRIPT/STYLE，
              getBoundingClientRect().left<680 || width<150 跳过，
              textContent 截断到'以上内容由AI生成'前，取最长的一段")
3. 若 AI_LEN=0 → 转 fallback（右侧 >300 字符的大文本块）
   两者皆空 → sleep 6 后重试（本段出现 3 次，重试全部命中）
4. 日期确认：DATEJS = bu.js("取含'凯哥的恋爱课堂'+'月'、top 850–1000 的容器文本")
   # 2025 年视频常带"点击推荐@"前缀，取"2025年X月X日"即可
   # 【重要】默认不截图，DATEJS 本身就是 bu.js 纯 DOM，不耗 OCR/额度
5. 仅当 AI_LEN 明显被截断（缺收尾）或 DATEJS 拿不到日期时，才：
   bu.js("对 r.left>680 && width>200 && scrollHeight>clientHeight 的元素 scrollTop=scrollHeight")
   → sleep 2 → 截图补读（这是唯一需要 OCR 的场景，尽量少用）
6. 写入 Markdown：{创作时间YYYYMMDD}-{作品ID}-{标题}.md
   # 头：标题 / 作者 / 抖音号 / 作品ID / 创作时间(YYYY-MM-DD) / 标签
   # 正文：`---` + AI文案 + `---` + `> 以上内容由AI生成，仅供参考`
```

> **避免 OCR 的关键**（2026-11-03 用户反馈，OCR/截图很耗额度）：日期确认完全可以用 `bu.js`（DATEJS）完成，不需要截图；文案提取用 `bu.js` 主路径也无需截图。只有面板结尾被截断需补读时才滚动+截图。

### 年份口径（延续既定惯例）
- 2026 年 2 月–1 月 → 文件名用 `2026` 前缀
- 2025 年 12 月及更早 → 文件名一律用 `2025` 前缀

### 翻页安全（用户反复强调，最高优先级）
- **绝不能停留在"相关推荐"栏翻页**，否则会切到其他作者的视频。
- 必须停留在 AI 栏（或作者视频播放队列）翻页。
- 翻页成功后核对 URL `modal_id` 是否为本作者下一个视频。
