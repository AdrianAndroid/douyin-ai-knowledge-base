#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把素材包整理成教程骨架（草稿），输出 tmp/教程草稿/<序号>-<作者>.md
需要人工/LLM 补写的位置标记为 <!--TODO:定位--> 等。
"""
import os, re, json, glob, urllib.parse
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MAT = os.path.join(BASE, 'tmp', '教程素材')
OUT = os.path.join(BASE, 'tmp', '教程草稿')
os.makedirs(OUT, exist_ok=True)

TOPIC_KW = {
    '大模型/LLM': ['大模型', '模型', '推理', '幻觉', 'token', 'LLM', '基座', '上下文', '参数'],
    'Agent/智能体': ['Agent', '智能体', '工作流', '自动化', '编排', '工具调用', 'MCP'],
    'RAG/知识库': ['RAG', '知识库', '检索', '向量', 'embedding', '召回', '重排'],
    '编程/开发': ['代码', '开发', '编程', '接口', 'API', '部署', '前端', '后端', '框架', '报错'],
    'AI工具评测': ['工具', '评测', '实测', '对比', '好用', '推荐', '插件', '软件'],
    '学习方法/认知': ['学习', '认知', '思维', '方法', '效率', '记忆', '复盘', '知识库'],
    '职场/管理': ['职场', '面试', '简历', '管理', '团队', '领导', '晋升', '跳槽'],
    'AI变现/商业': ['变现', '赚钱', '流量', '客户', '商业', '客单价', '私域', '接单', '报价'],
    'AI办公': ['Excel', 'PPT', '文档', '会议', '纪要', '表格', '周报', '办公'],
    '视频/音频': ['视频', '剪辑', '数字人', '配音', '音频', '字幕', '直播'],
    '绘画/设计': ['绘图', '设计', '海报', '插画', 'Logo', '配色', '排版'],
    '提示词': ['提示词', 'prompt', 'Prompt', '系统提示', '指令'],
    '微调/训练': ['微调', '训练', 'LoRA', '数据集', 'SFT', 'RLHF'],
    'AI新闻/行业': ['发布', '融资', '收购', '官宣', '行业', '市场', '指数', '股价'],
    '硬件/机器人': ['芯片', '显卡', '机器人', '算力', 'GPU', '设备', '终端'],
    '财经/投资': ['经济', '投资', '股市', '基金', '利率', '货币', '房产', 'GDP', '通胀', '赚钱'],
    '情感/关系': ['恋爱', '感情', '女人', '男人', '婚姻', '追女', '聊天', '约会', '吸引力'],
    '生活/娱乐': ['生活', '日常', '搞笑', '美食', '旅行', '萌宠', '家居', '穿搭'],
    '健康/身体': ['健康', '睡眠', '减脂', '健身', '饮食', '养生'],
    '历史/人文': ['历史', '文明', '朝代', '文化', '哲学', '地缘'],
}

LV = 'yb|md|pp|zzp|QLab|ai实验室|LumaAgent|研究AI生意|不纸设计|南院|小饺'
MARK = '<!--TODO:%s-->'


def esc(p):
    """相对链接编码，与既有导航体系一致：只编码危险字符"""
    return ''.join(urllib.parse.quote(c) if (c in ' %?#()"\'[]<>|*:' or ord(c) < 32) else c for c in p)


def build(rec, idx):
    d = rec['dir']
    files = rec['files']
    name = d.split('-', 1)[1] if re.match(r'^[0-9A-Za-z_.]+-', d) else d
    # 主题排序
    topics = [(k, v) for k, v in rec['topics']]
    tsum = sum(v for _, v in topics) or 1
    main = topics[0][0] if topics else ''
    # 观点按主题分组
    grouped = defaultdict(list)
    used = set()
    for p in rec['points']:
        t = p['text']
        g = None
        for k, kws in TOPIC_KW.items():
            if any(kw in t for kw in kws):
                g = k
                break
        if g is None:
            g = '综合'
        if len(grouped[g]) >= 8:
            continue
        grouped[g].append(p)
        used.add(t)
    rest = [p for p in rec['points'] if p['text'] not in used][:10]
    # 代表作（按时间倒序，取 12）
    reps = rec['recent'][:12]

    L = []
    L.append(f"# {name} · 精华教程\n")
    L.append("<!--TODO:定位-->\n")
    L.append("## 数据规模\n")
    L.append(f"| 项 | 值 |")
    L.append(f"|---|---|")
    L.append(f"| 抖音目录 | `{d}` |")
    L.append(f"| 已提取篇数 | **{files}** |")
    L.append(f"| AI 文案总字数 | {rec['chars']:,} |")
    L.append(f"| 覆盖时间 | {rec['date_min']} ~ {rec['date_max']} |")
    L.append(f"| 主要题材 | {main} |")
    L.append("")
    L.append("## 题材分布（按涉及篇数占比）\n")
    L.append("| 题材 | 篇数 | 占比 |")
    L.append("|---|---|---|")
    for k, v in topics[:8]:
        L.append(f"| {k} | {v} | {v/tsum*100:.1f}% |")
    L.append("")
    if rec['tools']:
        L.append("## 工具/技术涉及篇数 Top\n")
        L.append("| 工具 | 提及篇数 |")
        L.append("|---|---|")
        for t, c in rec['tools'][:12]:
            L.append(f"| {t} | {c} |")
        L.append("")
    L.append("## 核心干货（按题材归组，标注出现日期）\n")
    order = [k for k, _ in topics[:8]] + ['综合']
    for k in order:
        if k not in grouped:
            continue
        L.append(f"### {k}\n")
        for p in grouped[k][:8]:
            L.append(f"- [{p['date'][:4]}-{p['date'][4:6]}] {p['text']}")
        L.append("")
    if rest:
        L.append("### 其他要点\n")
        for p in rest:
            L.append(f"- [{p['date'][:4]}-{p['date'][4:6]}] {p['text']}")
        L.append("")
    L.append("## 学习路径\n")
    L.append("<!--TODO:路径-->\n")
    L.append("## 代表作（可直接点开原文）\n")
    L.append("| 日期 | 标题 | 原文 |")
    L.append("|---|---|---|")
    for r in reps:
        rel = esc(f"../../抖音关注/{d}/{r['file']}")
        title = r['title'].replace('|', '/')[:60]
        L.append(f"| {r['date'][:4]}-{r['date'][4:6]}-{r['date'][6:]} | {title} | [打开]({rel}) |")
    L.append("")
    L.append("## 局限与注意\n")
    L.append("<!--TODO:局限-->")
    L.append("")
    L.append(f"---\n\n导航：[🏠 README](../README.md) · [作者总览](../教程/README.md) · [作者原页](../作者/{esc_mapping(d)})")
    return '\n'.join(L)


def esc_mapping(d):
    import json as j
    m = j.load(open(os.path.join(BASE, '作者', '_页码映射.json'), encoding='utf-8'))
    return esc(m.get(d, 'index.md'))


if __name__ == '__main__':
    recs = [json.load(open(f, encoding='utf-8')) for f in glob.glob(os.path.join(MAT, '[!_]*.json'))]
    recs.sort(key=lambda r: -r['files'])
    for i, rec in enumerate(recs, 1):
        fn = f"{i:03d}-{re.sub(r'[/\\\\]', '_', rec['dir'])}.md"
        open(os.path.join(OUT, fn), 'w', encoding='utf-8').write(build(rec, i))
    print('生成草稿', len(recs))
