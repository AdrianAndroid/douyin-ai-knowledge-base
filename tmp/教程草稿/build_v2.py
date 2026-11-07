#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""正式教程生成器 v2：自动分章（认知/实操/误区/工具/代表作），TODO 留人工补写。
输出 教程/NNN-<作者>.md
"""
import os, re, json, glob, urllib.parse
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MAT = os.path.join(BASE, 'tmp', '教程素材')
OUT = os.path.join(BASE, '教程')
os.makedirs(OUT, exist_ok=True)

TOPIC_KW = {
    '大模型/LLM': ['大模型', '模型', '推理', '幻觉', 'token', 'LLM', '基座', '上下文', '微调'],
    'Agent/智能体': ['Agent', '智能体', '工作流', '编排', '工具调用', 'MCP', '多智能体'],
    'RAG/知识库': ['RAG', '知识库', '检索', '向量', 'embedding', '召回', '重排'],
    '编程/开发': ['代码', '开发', '编程', '接口', 'API', '部署', '前端', '后端', '框架', '报错', '报错'],
    'AI工具评测': ['工具', '评测', '实测', '对比', '好用', '推荐', '插件', '软件'],
    '学习方法/认知': ['学习', '认知', '思维', '方法', '效率', '复盘', '知识体系'],
    '职场/管理': ['职场', '面试', '简历', '管理', '团队', '领导', '晋升', '跳槽'],
    'AI变现/商业': ['变现', '赚钱', '流量', '客户', '商业', '客单价', '私域', '接单', '报价', '生意'],
    'AI办公': ['Excel', 'PPT', '文档', '会议', '纪要', '表格', '周报', '办公'],
    '视频/音频': ['视频', '剪辑', '数字人', '配音', '音频', '字幕', '直播'],
    '绘画/设计': ['绘图', '设计', '海报', '插画', 'Logo', '配色', '排版'],
    '提示词': ['提示词', 'prompt', 'Prompt', '系统提示', '指令'],
    '硬件/机器人': ['芯片', '显卡', '机器人', '算力', 'GPU', '设备', '终端'],
    '财经/投资': ['经济', '投资', '股市', '基金', '利率', '货币', '房产', 'GDP', '通胀', '资本'],
    '情感/关系': ['恋爱', '感情', '女人', '男人', '婚姻', '追女', '聊天', '约会', '吸引力', '女生'],
    '生活/娱乐': ['生活', '日常', '搞笑', '美食', '旅行', '萌宠', '家居', '穿搭'],
    '健康/身体': ['健康', '睡眠', '减脂', '健身', '饮食', '养生'],
    '历史/人文': ['历史', '文明', '朝代', '文化', '哲学', '地缘'],
    'AI新闻/行业': ['发布', '融资', '收购', '官宣', '行业', '指数', '股价', '市值'],
}

LEAD = re.compile(r'^(所以|但是|其实|而且|另外|还有|那么|因此|总之|总的来讲|简单来说|也就是说|说白了|这里|要注意|所以呢)[，,、：:]?')
STEP = re.compile(r'(步骤|第一步|第二步|先|然后|接着|最后|流程|配置|安装|搭建|实现|写法|模板|公式|方法如下|操作)')
MIS = re.compile(r'(不要|误区|错误|踩坑|避免|千万别|不能|别把|禁止|雷区|问题在于)')
COG = re.compile(r'(本质|核心|关键|原理|逻辑|因为|所以|原因|规律|定义|区别|意味着|取决于|前提)')


def esc(p):
    return ''.join(urllib.parse.quote(c) if (c in ' %?#()"\'[]<>|*:' or ord(c) < 32) else c for c in p)


def tidy(s):
    s = LEAD.sub('', s.strip())
    s = re.sub(r'\s+', ' ', s)
    return s.rstrip('，,、 ')


def cls(text):
    if MIS.search(text):
        return 'mis'
    if STEP.search(text):
        return 'step'
    if COG.search(text):
        return 'cog'
    return 'key'


def mapping():
    return json.load(open(os.path.join(BASE, '作者', '_页码映射.json'), encoding='utf-8'))


MAP = mapping()


def build(rec, idx):
    d = rec['dir']
    name = d.split('-', 1)[1] if re.match(r'^[0-9A-Za-z_.]+-', d) else d
    topics = [t for t in rec['topics']]
    tsum = sum(v for _, v in topics) or 1
    pts = [p for p in rec['points']]
    # 分桶
    buckets = defaultdict(list)
    seen = set()
    for p in pts:
        t = tidy(p['text'])
        if not t or t in seen:
            continue
        seen.add(t)
        c = cls(t)
        buckets[c].append((p['date'], t))
    for c, mx in [('cog', 14), ('step', 14), ('mis', 10), ('key', 18)]:
        buckets[c] = buckets[c][:mx]

    L = [f"# {name} · 精华教程\n"]
    L.append("<!--TODO:position-->\n")

    L.append("## 0. 数据底账\n")
    L.append("| 项 | 值 |")
    L.append("|---|---|")
    L.append(f"| 原目录 | `抖音关注/{d}` |")
    L.append(f"| 篇数 | **{rec['files']}** |")
    L.append(f"| AI 文案字数 | {rec['chars']:,} |")
    L.append(f"| 时间跨度 | {rec['date_min'][:4]}-{rec['date_min'][4:6]} ~ {rec['date_max'][:4]}-{rec['date_max'][4:6]} |")
    L.append(f"| 题材重心 | {topics[0][0] if topics else '—'} |")
    L.append("")
    if topics:
        L.append("**题材分布**：" + '、'.join(f"{k} {v} 篇({v/tsum*100:.0f}%)" for k, v in topics[:6]) + "\n")
    if rec['tools']:
        L.append("**高频工具**：" + '、'.join(f"{t}({c})" for t, c in rec['tools'][:10]) + "\n")

    if buckets['cog']:
        L.append("## 1. 核心认知（先看这一节）\n")
        for dt, t in buckets['cog']:
            L.append(f"- **{t}**（{dt[:4]}-{dt[4:6]}）")
        L.append("")
    if buckets['step']:
        L.append("## 2. 实操方法（照着做）\n")
        for i, (dt, t) in enumerate(buckets['step'], 1):
            L.append(f"{i}. {t}（{dt[:4]}-{dt[4:6]}）")
        L.append("")
    if buckets['mis']:
        L.append("## 3. 常见误区与坑\n")
        for dt, t in buckets['mis']:
            L.append(f"- ✗ {t}（{dt[:4]}-{dt[4:6]}）")
        L.append("")
    if buckets['key']:
        L.append("## 4. 关键零散结论\n")
        for dt, t in buckets['key']:
            L.append(f"- {t}")
        L.append("")

    L.append("## 5. 学完怎么用（顺序建议）\n")
    L.append("<!--TODO:path-->\n")

    L.append("## 6. 代表作（点开原文）\n")
    L.append("| 日期 | 标题 | 原文 |")
    L.append("|---|---|---|")
    for r in rec['recent'][:14]:
        rel = esc(f"../抖音关注/{d}/{r['file']}")
        title = r['title'].replace('|', '/')[:56]
        L.append(f"| {r['date'][:4]}-{r['date'][4:6]}-{r['date'][6:]} | {title} | [打开]({rel}) |")
    L.append("")
    L.append("## 7. 使用说明与局限\n")
    L.append("- 本文由该作者 **" + str(rec['files']) + " 篇** AI 文案经规则抽取 + 人工归纳生成，**未逐篇精读**；结论以原文日期为准，细节回原文核对。")
    L.append("- 抽取偏差：AI 文案本身已是二手总结，原文视频里的具体操作细节可能被压缩。")
    L.append("- 标注（年-月）为该结论出现的作品时间，可用于判断观点是否过时。\n")
    L.append(f"---\n\n导航：[🏠 README](../README.md) · [教程总览](README.md) · [作者页](../作者/{esc(MAP.get(d, 'index.md'))})")
    return '\n'.join(L)


if __name__ == '__main__':
    recs = [json.load(open(f, encoding='utf-8')) for f in glob.glob(os.path.join(MAT, '[!_]*.json'))]
    recs.sort(key=lambda r: -r['files'])
    names = []
    for i, rec in enumerate(recs, 1):
        d = rec['dir']
        name = d.split('-', 1)[1] if re.match(r'^[0-9A-Za-z_.]+-', d) else d
        fn = f"{i:03d}-{re.sub(r'[/\\\\]', '_', name)}.md"
        open(os.path.join(OUT, fn), 'w', encoding='utf-8').write(build(rec, i))
        names.append((i, fn, name))
    open(os.path.join(BASE, 'tmp', '教程草稿', '_names.json'), 'w', encoding='utf-8').write(
        json.dumps(names, ensure_ascii=False, indent=1))
    print('生成', len(recs), '份教程骨架')
