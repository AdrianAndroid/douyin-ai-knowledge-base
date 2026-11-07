#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从作者 md 中抽取教程素材包：统计 + 高信号句 + 工具/主题词频 + 代表作。
只读取，不修改任何成品文件。输出 tmp/教程素材/<作者目录>.json
"""
import os, re, glob, json, hashlib
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(BASE, '抖音关注')
OUT = os.path.join(BASE, 'tmp', '教程素材')
os.makedirs(OUT, exist_ok=True)

TOOLS = ['Claude', 'DeepSeek', 'ChatGPT', 'GPT-4', 'Gemini', 'LangChain', 'LangGraph', 'LlamaIndex',
         '豆包', 'Cursor', 'Kimi', '飞书', 'Coze', '扣子', 'Dify', 'Manus', 'Ollama', 'Qwen', '通义',
         'Grok', 'Sora', '可灵', '即梦', 'Midjourney', 'Stable Diffusion', 'Lora', 'Copilot',
         'VS Code', 'n8n', 'ComfyUI', 'Notion', 'Obsidian', 'Excel', 'Figma', 'Python', 'Node',
         'Vue', 'React', 'Next', 'Docker', 'GitHub', 'HuggingFace', 'OpenAI', 'Anthropic', '字节',
         '微信', '小红书', '抖音', '淘宝', '亚马逊', 'TikTok', 'Perplexity', 'MCP', 'Agent SDK',
         'Mimo', 'Sonnet', 'Opus', 'Haiku', 'Gemma', 'Mistral', 'Llama', '向量数据库', 'Supabase',
         'Fusion 360', 'Blender', 'Godot', 'Unity', 'Cocos', 'Unreal', 'Framer', 'Canva']

TOPICS = {
    'AI工具评测': ['工具', '评测', '实测', '对比', '好用', '推荐', '插件', '软件'],
    '大模型/LLM': ['大模型', '模型', '参数', '推理', '幻觉', 'token', 'LLM', '基座'],
    'Agent/智能体': ['Agent', '智能体', '工作流', '自动化', '多智能体', '编排'],
    'RAG/知识库': ['RAG', '知识库', '检索', '向量', 'embedding', '召回'],
    '提示词': ['提示词', 'prompt', 'Prompt', '系统提示', '指令'],
    '微调/训练': ['微调', '训练', 'LoRA', '数据集', 'SFT', 'RLHF'],
    'AI新闻/行业': ['发布', '融资', '收购', '官宣', '行业', '市场', '指数', '股价'],
    'AI变现/商业': ['变现', '赚钱', '流量', '变现', '客户', '商业', '客单价', '私域', '接单', '报价'],
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


def clean_body(text):
    """去掉 YAML/头部元信息和分隔线，返回正文（AI 文案主体）"""
    text = text.replace('\r\n', '\n')
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) >= 3:
            text = parts[2]
    # 去掉 '# 标题' 行与 '> ' 元信息行、分隔线
    lines = []
    for ln in text.split('\n'):
        s = ln.strip()
        if not s:
            continue
        if s.startswith('# '):
            continue
        if s.startswith('>') and ('作者' in s or '抖音号' in s or '作品ID' in s or '创作时间' in s or '标签' in s or 'AI' in s):
            continue
        if set(s) <= set('-—'):
            continue
        lines.append(s)
    return '\n'.join(lines)


def sentences(text):
    out = []
    for seg in re.split(r'[。！？\n；;]', text):
        s = seg.strip().strip('、，,')
        s = re.sub(r'\s+', ' ', s)
        if 12 <= len(s) <= 110:
            out.append(s)
    return out


def score(s):
    v = 0
    for k in SIG:
        if k in s:
            v += 2
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


def process_dir(d):
    p = os.path.join(SRC, d)
    files = sorted(glob.glob(os.path.join(p, '*.md')))
    files = [f for f in files if not os.path.basename(f).startswith('_')]
    recs = []
    alltext = []
    tool_cnt = Counter()
    topic_cnt = Counter()
    topic_hits = defaultdict(list)
    cand = []
    titles = []
    for f in files:
        b = os.path.basename(f)
        m = re.match(r'(\d{8})-(\d+)-(.+)\.md$', b)
        date = m.group(1) if m else ''
        vid = m.group(2) if m else ''
        title = m.group(3) if m else b
        try:
            raw = open(f, encoding='utf-8').read()
        except Exception:
            continue
        body = clean_body(raw)
        if not body:
            continue
        alltext.append(body)
        titles.append((date, title, b))
        for t in TOOLS:
            c = body.count(t)
            if c:
                tool_cnt[t] += 1
        for k, kws in TOPICS.items():
            if any(kw in body for kw in kws):
                topic_cnt[k] += 1
                topic_hits[k].append(b)
        for s in sentences(body):
            sc = score(s)
            if sc >= 3:
                cand.append((sc, date, s, b))
    # 去重 + 排序（保留高分，同类句只留一条）
    cand.sort(key=lambda x: (-x[0], x[1]))
    seen = set()
    picked = []
    for sc, date, s, b in cand:
        k = fp(s)
        if k in seen:
            continue
        seen.add(k)
        picked.append({'score': sc, 'date': date, 'text': s, 'src': b})
        if len(picked) >= 120:
            break
    # 代表作：标题含数字/干货词优先 + 最新
    rep = sorted(titles, key=lambda x: (x[0]), reverse=True)[:30]
    rep = [{'date': d0, 'title': t, 'file': f} for d0, t, f in rep]
    rec = {
        'dir': d,
        'files': len(files),
        'parsed': len(alltext),
        'chars': sum(len(t) for t in alltext),
        'date_min': min(x[0] for x in titles) if titles else '',
        'date_max': max(x[0] for x in titles) if titles else '',
        'tools': tool_cnt.most_common(30),
        'topics': topic_cnt.most_common(20),
        'topic_files': {k: v[:6] for k, v in topic_hits.items()},
        'points': picked,
        'recent': rep,
    }
    fn = re.sub(r'[/\\]', '_', d) + '.json'
    open(os.path.join(OUT, fn), 'w', encoding='utf-8').write(json.dumps(rec, ensure_ascii=False, indent=1))
    return rec


if __name__ == '__main__':
    dirs = [d for d in sorted(os.listdir(SRC))
            if os.path.isdir(os.path.join(SRC, d))
            and any(not os.path.basename(f).startswith('_')
                    for f in glob.glob(os.path.join(SRC, d, '*.md')))]
    total = 0
    summary = []
    for d in dirs:
        r = process_dir(d)
        total += r['parsed']
        summary.append(f"{r['files']:5d}篇 {r['chars']:9d}字 {r['date_min']}~{r['date_max']} 工具{len(r['tools'])} 观点{len(r['points'])}  {d}")
        print('done', d, r['parsed'])
    open(os.path.join(OUT, '_index.txt'), 'w', encoding='utf-8').write(
        f"作者数={len(dirs)} 解析篇数={total}\n" + '\n'.join(summary) + '\n')
    print('TOTAL', len(dirs), 'authors', total, 'files')
