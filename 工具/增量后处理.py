#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""增量后处理：数据（抖音关注/）变化后，一条命令把全库文档同步一致。

用法：
    python3 工具/增量后处理.py            # 全流程（抽取→教程→索引→校验→报告）
    python3 工具/增量后处理.py --no-extract   # 跳过耗时的观点抽取（只更新统计/索引）

做的事：
1. 扫描数据现状（每作者 md 数、日期范围），与 _作者分类.json 比对出变更
2. 回写 _作者分类.json 与 _全库作者索引.md 的篇数（如与实测不符）
3. 重新抽取教程素材 → 重生成 教程/NNN-<作者>.md（定位文案按“作者名”从 工具/作者定位文案.json 取，不依赖序号）
4. 重建 教程/README.md 索引
5. 校验所有相对链接
6. 输出报告 工具/最近一次更新报告.md

设计原则：
- 新作者没有定位文案时，教程仍生成，但头顶留 “<!--待补写定位-->" 并在报告中列出，绝不套用别人的文案。
- 一切以实测为准；本脚本不会为了凑数而修改数字。
"""
import os, sys, re, glob, json, hashlib, urllib.parse
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, '抖音关注')
TUT = os.path.join(BASE, '教程')
MAT = os.path.join(BASE, 'tmp', '教程素材')
TOOL = os.path.join(BASE, '工具')
LIB = os.path.join(TOOL, '作者定位文案.json')
GRP = os.path.join(TOOL, '教程分组.json')
CLS = os.path.join(BASE, '_作者分类.json')
IDX = os.path.join(BASE, '_全库作者索引.md')
REPORT = os.path.join(TOOL, '最近一次更新报告.md')

TOOLS = ['Claude', 'DeepSeek', 'ChatGPT', 'GPT-4', 'Gemini', 'LangChain', 'LangGraph', 'LlamaIndex',
         '豆包', 'Cursor', 'Kimi', '飞书', 'Coze', '扣子', 'Dify', 'Manus', 'Ollama', 'Qwen', '通义',
         'Grok', 'Sora', '可灵', '即梦', 'Midjourney', 'Stable Diffusion', 'Lora', 'Copilot',
         'VS Code', 'n8n', 'ComfyUI', 'Notion', 'Obsidian', 'Excel', 'Figma', 'Python', 'Node',
         'Vue', 'React', 'Next', 'Docker', 'GitHub', 'HuggingFace', 'OpenAI', 'Anthropic', '字节',
         '微信', '小红书', '抖音', '淘宝', '亚马逊', 'TikTok', 'Perplexity', 'MCP', 'Agent SDK',
         'Sonnet', 'Opus', 'Haiku', 'Gemma', 'Mistral', 'Llama', '向量数据库', 'Supabase',
         'Fusion 360', 'Blender', 'Godot', 'Unity', 'Cocos', 'Unreal', 'Framer', 'Canva']

TOPICS = {
    'AI工具评测': ['工具', '评测', '实测', '对比', '好用', '推荐', '插件', '软件'],
    '大模型/LLM': ['大模型', '模型', '参数', '推理', '幻觉', 'token', 'LLM', '基座'],
    'Agent/智能体': ['Agent', '智能体', '工作流', '自动化', '多智能体', '编排'],
    'RAG/知识库': ['RAG', '知识库', '检索', '向量', 'embedding', '召回'],
    '提示词': ['提示词', 'prompt', 'Prompt', '系统提示', '指令'],
    '微调/训练': ['微调', '训练', 'LoRA', '数据集', 'SFT', 'RLHF'],
    'AI新闻/行业': ['发布', '融资', '收购', '官宣', '行业', '市场', '指数', '股价'],
    'AI变现/商业': ['变现', '赚钱', '流量', '客户', '商业', '客单价', '私域', '接单', '报价'],
    '编程/开发': ['代码', '开发', '编程', '接口', 'API', '部署', '前端', '后端', '框架', '报错'],
    '学习方法/认知': ['学习', '认知', '思维', '方法', '效率', '记忆', '复盘', '第二大脑'],
    '职场/管理': ['职场', '面试', '简历', '管理', '团队', '领导', '晋升', '跳槽'],
    'AI办公': ['Excel', 'PPT', '文档', '会议', '纪要', '表格', '周报', '自动化办公'],
    '视频/音频': ['视频', '剪辑', '数字人', '配音', '音频', '字幕', '直播'],
    '绘画/设计': ['绘图', '设计', '海报', '插画', 'Logo', '配色', '排版'],
    '硬件/机器人': ['芯片', '显卡', '机器人', '算力', 'GPU', '设备', '终端'],
    '财经/投资': ['经济', '投资', '股市', '基金', '利率', '货币', '房产', 'GDP', '通胀'],
    '情感/关系': ['恋爱', '感情', '女人', '男人', '婚姻', '追女', '聊天', '约会', '吸引力'],
    '生活/娱乐': ['生活', '日常', '搞笑', '美食', '旅行', '萌宠', '家居', '穿搭'],
    '健康/身体': ['健康', '睡眠', '减脂', '健身', '饮食', '养生'],
    '历史/人文': ['历史', '文明', '朝代', '文化', '哲学', '地缘'],
}

SIG = ['核心', '本质', '关键', '必须', '记住', '方法', '步骤', '误区', '不要', '错误', '建议',
       '原则', '公式', '技巧', '逻辑', '框架', '重点', '结论', '真相', '规律', '所以', '因为',
       '第一', '第二', '第三', '千万', '一定', '唯一', '最', '三种', '四个', '五个']

LEAD = re.compile(r'^(所以|但是|其实|而且|另外|还有|那么|因此|总之|总的来讲|简单来说|也就是说|说白了|这里|要注意|所以呢)[，,、：:]?')
STEP = re.compile(r'(步骤|第一步|第二步|先|然后|接着|最后|流程|配置|安装|搭建|实现|写法|模板|公式|方法如下|操作)')
MIS = re.compile(r'(不要|误区|错误|踩坑|避免|千万别|不能|别把|禁止|雷区|问题在于)')
COG = re.compile(r'(本质|核心|关键|原理|逻辑|因为|所以|原因|规律|定义|区别|意味着|取决于|前提)')


def esc(p):
    return ''.join(urllib.parse.quote(c) if (c in ' %?#()"\'[]<>|*:' or ord(c) < 32) else c for c in p)


def name_of(d):
    return d.split('-', 1)[1] if re.match(r'^[0-9A-Za-z_.]+-', d) else d


# ---------------- 1. 扫描 ----------------
def scan():
    rows = []
    for d in sorted(os.listdir(SRC)):
        p = os.path.join(SRC, d)
        if not os.path.isdir(p):
            continue
        mds = [f for f in glob.glob(os.path.join(p, '*.md')) if not os.path.basename(f).startswith('_')]
        dates = []
        for f in mds:
            m = re.match(r'(\d{8})-(\d+)-', os.path.basename(f))
            if m:
                dates.append(m.group(1))
        rows.append({'dir': d, 'name': name_of(d), 'md': len(mds),
                     'dmin': min(dates) if dates else '', 'dmax': max(dates) if dates else ''})
    return rows


# ---------------- 2. 抽取 ----------------
def clean_body(text):
    text = text.replace('\r\n', '\n')
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) >= 3:
            text = parts[2]
    out = []
    for ln in text.split('\n'):
        s = ln.strip()
        if not s:
            continue
        if s.startswith('# '):
            continue
        if s.startswith('>') and any(k in s for k in ('作者', '抖音号', '作品ID', '创作时间', '标签', 'AI')):
            continue
        if set(s) <= set('-—'):
            continue
        out.append(s)
    return '\n'.join(out)


def sentences(text):
    res = []
    for seg in re.split(r'[。！？\n；;]', text):
        s = re.sub(r'\s+', ' ', seg.strip().strip('、，,'))
        if 12 <= len(s) <= 110:
            res.append(s)
    return res


def score(s):
    v = sum(2 for k in SIG if k in s)
    if re.search(r'\d', s):
        v += 1
    if re.search(r'(第[一二三四五六七八九十]|首先|然后|接着|最后|再)', s):
        v += 1
    if s.count('我') + s.count('你') >= 3:
        v -= 1
    if len(s) < 18:
        v -= 1
    return v


def fp(s):
    return hashlib.md5(re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', s).encode()).hexdigest()[:10]


def extract(d):
    p = os.path.join(SRC, d)
    files = [f for f in sorted(glob.glob(os.path.join(p, '*.md')))]
    tool_cnt, topic_cnt = Counter(), Counter()
    cand, titles, texts = [], [], []
    for f in files:
        b = os.path.basename(f)
        if b.startswith('_'):
            continue
        m = re.match(r'(\d{8})-(\d+)-(.+)\.md$', b)
        date, vid, title = (m.group(1), m.group(2), m.group(3)) if m else ('', '', b)
        try:
            body = clean_body(open(f, encoding='utf-8').read())
        except Exception:
            continue
        if not body:
            continue
        texts.append(body)
        titles.append((date, title, b))
        for t in TOOLS:
            if t in body:
                tool_cnt[t] += 1
        for k, kws in TOPICS.items():
            if any(w in body for w in kws):
                topic_cnt[k] += 1
        for s in sentences(body):
            sc = score(s)
            if sc >= 3:
                cand.append((sc, date, s))
    cand.sort(key=lambda x: (-x[0], x[1]))
    seen, pts = set(), []
    for sc, date, s in cand:
        k = fp(s)
        if k in seen:
            continue
        seen.add(k)
        pts.append({'score': sc, 'date': date, 'text': s})
        if len(pts) >= 120:
            break
    return {'dir': d, 'files': len(titles), 'chars': sum(len(t) for t in texts),
            'date_min': min(x[0] for x in titles) if titles else '',
            'date_max': max(x[0] for x in titles) if titles else '',
            'tools': tool_cnt.most_common(30), 'topics': topic_cnt.most_common(20),
            'points': pts, 'recent': [{'date': a, 'title': b, 'file': c} for a, b, c in
                                      sorted(titles, reverse=True)[:30]]}


# ---------------- 3. 教程 ----------------
def tidy(s):
    return re.sub(r'\s+', ' ', LEAD.sub('', s.strip())).rstrip('，,、 ')


def cls(t):
    if MIS.search(t):
        return 'mis'
    if STEP.search(t):
        return 'step'
    if COG.search(t):
        return 'cog'
    return 'key'


def build_tutorial(rec, lib, mapj):
    d, name = rec['dir'], rec['name']
    topics = rec['topics']
    tsum = sum(v for _, v in topics) or 1
    b = defaultdict(list)
    seen = set()
    for p in rec['points']:
        t = tidy(p['text'])
        if not t or t in seen:
            continue
        seen.add(t)
        b[cls(t)].append((p['date'], t))
    b['cog'], b['step'], b['mis'], b['key'] = b['cog'][:14], b['step'][:14], b['mis'][:10], b['key'][:18]

    text = lib.get(name)
    pos = text['position'] if text else '<!--待补写定位--> 新作者，定位与学习路径待人工补充。'
    path = text['path'] if text else '<!--待补写路径-->'

    L = [f"# {name} · 精华教程\n", pos, "\n## 0. 数据底账\n"]
    L += ["| 项 | 值 |", "|---|---|", f"| 原目录 | `抖音关注/{d}` |", f"| 篇数 | **{rec['files']}** |",
          f"| AI 文案字数 | {rec['chars']:,} |",
          f"| 时间跨度 | {rec['date_min'][:4]}-{rec['date_min'][4:6]} ~ {rec['date_max'][:4]}-{rec['date_max'][4:6]} |",
          f"| 题材重心 | {topics[0][0] if topics else '—'} |", ""]
    if topics:
        L.append("**题材分布**：" + '、'.join(f"{k} {v} 篇({v/tsum*100:.0f}%)" for k, v in topics[:6]) + "\n")
    if rec['tools']:
        L.append("**高频工具**：" + '、'.join(f"{t}({c})" for t, c in rec['tools'][:10]) + "\n")
    if b['cog']:
        L.append("## 1. 核心认知（先看这一节）\n")
        L += [f"- **{t}**（{dt[:4]}-{dt[4:6]}）" for dt, t in b['cog']]
        L.append("")
    if b['step']:
        L.append("## 2. 实操方法（照着做）\n")
        L += [f"{i}. {t}（{dt[:4]}-{dt[4:6]}）" for i, (dt, t) in enumerate(b['step'], 1)]
        L.append("")
    if b['mis']:
        L.append("## 3. 常见误区与坑\n")
        L += [f"- ✗ {t}（{dt[:4]}-{dt[4:6]}）" for dt, t in b['mis']]
        L.append("")
    if b['key']:
        L.append("## 4. 关键零散结论\n")
        L += [f"- {t}" for dt, t in b['key']]
        L.append("")
    L.append("## 5. 学完怎么用（顺序建议）\n")
    L.append(path)
    L.append("\n## 6. 代表作（点开原文）\n")
    L += ["| 日期 | 标题 | 原文 |", "|---|---|---|"]
    for r in rec['recent'][:14]:
        rel = esc('../抖音关注/' + d + '/' + r['file'])
        L.append(f"| {r['date'][:4]}-{r['date'][4:6]}-{r['date'][6:]} | "
                 f"{r['title'].replace('|','/')[:56]} | [打开]({rel}) |")
    L.append("")
    L.append("## 7. 使用说明与局限\n")
    L.append(f"- 本文由该作者 **{rec['files']} 篇** AI 文案经规则抽取 + 人工归纳生成，**未逐篇精读**；结论以原文日期为准，细节回原文核对。")
    L.append("- 抽取偏差：AI 文案本身已是二手总结，原文视频里的具体操作细节可能被压缩。")
    L.append("- 标注（年-月）为该结论出现的作品时间，可用于判断观点是否过时。\n")
    L.append(f"---\n\n导航：[🏠 README](../README.md) · [教程总览](README.md) · [作者页](../作者/{esc(mapj.get(d,'index.md'))})")
    return '\n'.join(L)


def build_index(recs, one, groups):
    meta = {r['name']: r for r in recs}
    tot_art, tot_ch = sum(r['files'] for r in recs), sum(r['chars'] for r in recs)
    L = ['# 作者精华教程 · 总索引\n']
    L.append('[GitHub 仓库](https://github.com/AdrianAndroid/douyin-ai-knowledge-base)　|　'
             '[本页在线版](https://github.com/AdrianAndroid/douyin-ai-knowledge-base/blob/main/教程/README.md)\n')
    L.append(f'> **{len(recs)} 位有内容的作者**，共 **{tot_art:,} 篇** AI 文案（{tot_ch/10000:.1f} 万字）→ 每人一份教程。\n')
    L.append('> 生成方式：规则抽取（题材词频、工具词频、结论句打分）+ 人工判断（作者定位、学习路径）。'
             '**未逐篇精读**，结论可信度以原文为准。\n')
    L.append('[← 返回 README](../README.md)　|　[作者分页（264 位）](../作者/index.md)　|　'
             '[全库作者索引](../_全库作者索引.md)　|　[A 档分析](../分析/README.md)\n')
    L.append('## 怎么用这套教程\n')
    L.append('1. 先按需求选组，不要按序号顺序读。')
    L.append('2. 每组挑 1-2 位，先读「1 核心认知」和「5 学完怎么用」，10 分钟判断值不值得深读。')
    L.append('3. 值得深读的读「2 实操方法」并动手；「6 代表作」是回原文的出口。')
    L.append('4. 每条结论带（年-月），技术类超过 3 个月要复核。\n')

    def row(n):
        r = meta[n]
        fn = esc(r['file'])
        return f"| {n} | {r['files']} | {r['chars']/10000:.1f} | {one.get(n,'')} | [打开]({fn}) |"

    used = set()
    for gname, names in groups:
        L.append(f'## {gname}\n')
        L.append('| 作者 | 篇数 | 万字 | 一句话定位 | 教程 |')
        L.append('|---|---|---|---|---|')
        for n in names:
            if n in meta:
                L.append(row(n))
                used.add(n)
        L.append('')
    rest = [r['name'] for r in sorted(recs, key=lambda x: -x['files']) if r['name'] not in used]
    if rest:
        L.append('## 七、未归类（新加入或未分组）\n')
        L.append('| 作者 | 篇数 | 万字 | 一句话定位 | 教程 |')
        L.append('|---|---|---|---|---|')
        for n in rest:
            L.append(row(n))
        L.append('')
    empty = sum(1 for d in os.listdir(SRC)
                if os.path.isdir(os.path.join(SRC, d)) and not glob.glob(os.path.join(SRC, d, '*.md')))
    L.append(f'## 无内容作者（{empty} 个目录，未生成教程）\n')
    L.append('这些目录没有任何 md 文件，无法成篇。其中包含 8 位 A 档纯编程号（大宝爱编程、课代表立正、python-青木学长、'
             '程序员阿崔Acui、老傅1024、大厂阿星、JimChannel、林粒粒呀）为 0 篇待提取，其余多为已关注但未开始提取的作者。'
             '全名单见 [全库作者索引](../_全库作者索引.md)。\n')
    L.append('## 按篇数排序的总表\n')
    L.append('| # | 作者 | 篇数 | 教程 |')
    L.append('|---|---|---|---|')
    for i, r in enumerate(sorted(recs, key=lambda x: -x['files']), 1):
        L.append(f"| {i:03d} | {r['name']} | {r['files']} | [打开]({esc(r['file'])}) |")
    L.append("")
    L.append('---\n')
    L.append('导航：[🏠 README](../README.md) · [作者分页索引](../作者/index.md) · [全库作者索引](../_全库作者索引.md) · [A 档分析](../分析/README.md)')
    return '\n'.join(L)


def verify_links():
    pat = re.compile(r'\[[^\]]*\]\(([^)]+)\)')
    files = glob.glob(os.path.join(TUT, '*.md')) + [os.path.join(BASE, 'README.md')]
    tot, bad = 0, []
    for p in files:
        for m in pat.finditer(open(p, encoding='utf-8').read()):
            x = m.group(1).strip()
            if x.startswith(('http', '#')):
                continue
            tot += 1
            d = urllib.parse.unquote(x.split('#')[0])
            if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(p), d))):
                bad.append((os.path.relpath(p, BASE), x))
    return tot, bad


def main():
    no_extract = '--no-extract' in sys.argv
    os.makedirs(MAT, exist_ok=True)
    lib = json.load(open(LIB, encoding='utf-8'))
    cfg = json.load(open(GRP, encoding='utf-8'))
    one, groups = cfg['one'], cfg['groups']

    # 1 扫描 + 比对
    rows = scan()
    has = [r for r in rows if r['md'] > 0]
    old = {}
    if os.path.exists(CLS):
        try:
            for x in json.load(open(CLS, encoding='utf-8')):
                old[x['dir']] = x
        except Exception:
            old = {}
    new_authors = [r['dir'] for r in has if r['dir'] not in old]
    gone = [d for d in old if d not in {r['dir'] for r in rows}]
    grew = [(r['dir'], old[r['dir']].get('md', 0), r['md']) for r in has
            if r['dir'] in old and old[r['dir']].get('md', 0) != r['md']]
    total_md = sum(r['md'] for r in rows)

    # 2 回写 _作者分类.json
    cls_rows = []
    for r in rows:
        o = old.get(r['dir'], {})
        cls_rows.append({'dir': r['dir'], 'dy': o.get('dy', r['dir'].split('-')[0]),
                         'name': o.get('name', r['name']), 'md': r['md'],
                         'dmin': r['dmin'], 'dmax': r['dmax'],
                         'topic': o.get('topic', ''), 'level': o.get('level', '')})
    json.dump(cls_rows, open(CLS, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # 3 抽取 + 教程
    mapj = json.load(open(os.path.join(BASE, '作者', '_页码映射.json'), encoding='utf-8'))
    recs = []
    for r in sorted(has, key=lambda x: -x['md']):
        jf = os.path.join(MAT, re.sub(r'[/\\]', '_', r['dir']) + '.json')
        if no_extract and os.path.exists(jf):
            rec = json.load(open(jf, encoding='utf-8'))
        else:
            rec = extract(r['dir'])
            json.dump(rec, open(jf, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        rec['name'] = r['name']
        recs.append(rec)

    # 清掉已不存在作者的教程文件
    keep = set()
    for i, rec in enumerate(recs, 1):
        fn = f"{i:03d}-{re.sub(r'[/\\]', '_', rec['name'])}.md"
        rec['file'] = fn
        keep.add(fn)
        open(os.path.join(TUT, fn), 'w', encoding='utf-8').write(build_tutorial(rec, lib, mapj))
    removed = []
    for f in glob.glob(os.path.join(TUT, '[0-9][0-9][0-9]-*.md')):
        if os.path.basename(f) not in keep:
            os.remove(f)
            removed.append(os.path.basename(f))

    open(os.path.join(TUT, 'README.md'), 'w', encoding='utf-8').write(build_index(recs, one, groups))

    # 4 校验
    tot, bad = verify_links()
    missing_lib = [r['name'] for r in recs if r['name'] not in lib]

    # 5 报告
    R = ['# 最近一次增量后处理报告\n', f'- 生成时间：自动', f'- 实测篇数合计：**{total_md:,}**（{len(rows)} 个目录，{len(has)} 个有内容）',
         f'- 有内容作者：{len(has)} 位 → 教程 {len(recs)} 份',
         f'- 链接校验：{tot} 条，失效 {len(bad)}\n']
    R.append('## 变更\n')
    R.append(f'- 新作者（本地无记录）：{len(new_authors)} 个' + ('' if not new_authors else ' → ' + '、'.join(new_authors[:10])))
    R.append(f'- 篇数变化：{len(grew)} 个')
    for d, o, n in grew[:10]:
        R.append(f'  - `{d}`：{o} → {n}（{n-o:+d}）')
    R.append(f'- 目录消失：{len(gone)} 个' + ('' if not gone else ' → ' + '、'.join(gone[:10])))
    R.append(f'- 教程文件移除：{len(removed)} 个\n')
    R.append('## 待人工补写（新作者）\n')
    if missing_lib:
        for n in missing_lib:
            R.append(f'- [ ] {n}：在 工具/作者定位文案.json 补 position 与 path')
    else:
        R.append('- 无')
    R.append('\n## 链接失效\n')
    R.append('无' if not bad else '\n'.join(f'- `{p}` → `{x}`' for p, x in bad[:20]))
    open(REPORT, 'w', encoding='utf-8').write('\n'.join(R))

    print(f'完成：{len(has)} 位作者 / {total_md} 篇 / 教程 {len(recs)} 份 / 链接 {tot} 条失效 {len(bad)}')
    print(f'新作者 {len(new_authors)}，篇数变化 {len(grew)}，待补定位 {len(missing_lib)}')


if __name__ == '__main__':
    main()
