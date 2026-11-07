#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 教程/README.md 总索引（按用途分组）"""
import os, glob, re, json, urllib.parse

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TUT = os.path.join(BASE, '教程')

ONE = {
    1: '生活整活，无可复用方法论', 2: '宏观/产业财经快评，指标拆解', 3: '学习方法与认知模型',
    4: 'AI 行业深度日更，认知图谱', 5: '地缘/军事/国别因果分析', 6: '男性聊天话术体系（最完整）',
    7: '男性成长与关系框架（观念）', 8: '恋爱清单式技巧，条目化', 9: '商业案例拆解，钱怎么流',
    10: '男性情感短口播（价值观输出）', 11: '科技产业深度访谈（一手）', 12: 'AI 工程手把手：Harness/RAG/知识库',
    13: 'Agent/RAG 面试题拆解（最系统）', 14: '沟通结构技巧，反常识钩子', 15: 'AI 工具实测做项目',
    16: '女性视角关系心理与识别', 17: 'AI 交付一线观察，纠正乐观', 18: '学习法+人文书单',
    19: '程序员工具折腾，踩坑实录', 20: 'AI 转型四阶段路线图', 21: '成长/硅谷/读书方法',
    22: '每日财经快评（时效型）', 23: '青少年科创/3D打印（垂类唯一）', 24: '科技思想对谈（安全/EA）',
    25: 'AI 工具尝鲜与开发评测', 26: '生活方式 vlog（D 档）', 27: '聊天心理机制，伏笔回收',
    28: '大模型学习路线+职业转型', 29: '哲学观念史，思辨训练', 30: '手绘通识科普（历史/科学）',
    31: '产业季报与具身/智驾情报', 32: '两性社会学视角，反简化', 33: '商业人物深度访谈',
    34: 'AI 应用真实演示，效果优先', 35: 'Agent 架构与产品判断', 36: '赚钱认知，反暴富',
    37: '企业 AI 转型与组织视角', 38: 'Agent 面试求职实战', 39: '职场表达与话语权',
    40: '科技人物访谈（更新稀疏）', 41: 'Agent 面试速补，一日可读', 42: '住宅改造案例（垂类）',
    43: '建筑×AI 交叉观察', 44: 'AI 小生意案例集（选题金矿）', 45: 'AI 投资研究（非建议）',
    46: '小老板 AI 落地，先卖后做', 47: '财经三层拆解（样本少方法硬）', 48: '相亲纪实（样本不足）',
    49: '性教育科普（样本不足）',
}

GROUPS = [
    ('一、AI 工程与工具（能直接动手）', [13, 12, 35, 15, 20, 28, 19, 25, 41, 34, 38, 17, 23, 46]),
    ('二、AI 行业与商业认知（判断与视野）', [4, 11, 31, 33, 24, 40, 44, 37, 45, 36, 43]),
    ('三、财经与投资', [2, 9, 47, 22, 5, 21, 11, 33, 45]),
    ('四、情感与关系（尽力过滤价值观）', [6, 8, 27, 14, 7, 16, 10, 32, 48, 49]),
    ('五、学习法与认知', [3, 18, 29, 30, 39, 21, 32, 36]),
    ('六、生活/娱乐（低价值档，仅参考）', [1, 26, 42]),
]


def esc(p):
    return ''.join(urllib.parse.quote(c) if (c in ' %?#()"\'[]<>|*:' or ord(c) < 32) else c for c in p)


def main():
    files = sorted(glob.glob(os.path.join(TUT, '[0-9][0-9][0-9]-*.md')))
    meta = {}
    for f in files:
        num = int(os.path.basename(f)[:3])
        t = open(f, encoding='utf-8').read()
        name = t.split('\n', 1)[0].replace('# ', '').replace(' · 精华教程', '')
        m = re.search(r'\| 篇数 \| \*\*(\d+)\*\* \|', t)
        cnt = int(m.group(1)) if m else 0
        m2 = re.search(r'\| AI 文案字数 \| ([\d,]+) \|', t)
        chars = int(m2.group(1).replace(',', '')) if m2 else 0
        meta[num] = (name, cnt, chars, os.path.basename(f))

    tot_art = sum(v[1] for v in meta.values())
    tot_ch = sum(v[2] for v in meta.values())

    L = ['# 作者精华教程 · 总索引\n']
    L.append('[GitHub 仓库](https://github.com/AdrianAndroid/douyin-ai-knowledge-base)　|　'
             '[本页在线版](https://github.com/AdrianAndroid/douyin-ai-knowledge-base/blob/main/教程/README.md)\n')
    L.append(f'> **{len(meta)} 位有内容的作者**，共 **{tot_art:,} 篇** AI 文案（{tot_ch/10000:.1f} 万字）'
             f'→ 每人一份教程。另 **215 个作者目录无任何 md**（未提取或纯编程号待补），无法成篇，名单见文末。\n')
    L.append('> 生成方式：规则抽取（题材词频、工具词频、结论句打分）+ 人工判断（作者定位、学习路径）。'
             '**未逐篇精读**，结论可信度以原文为准，回链到单篇原文可直接核对。\n')
    L.append('[← 返回 README](../README.md)　|　[作者分页（264 位）](../作者/index.md)　|　'
             '[全库作者索引](../_全库作者索引.md)　|　[A 档分析](../分析/README.md)\n')

    L.append('## 怎么用这套教程\n')
    L.append('1. 先按需求选组（下面六组），不要从 001 顺序读。')
    L.append('2. 每组挑 **1-2 位**，读它的「1 核心认知」和「5 学完怎么用」，10 分钟能判断值不值得深读。')
    L.append('3. 值得深读的，再读「2 实操方法」并动手；「6 代表作」给的是原文出口。')
    L.append('4. 每条结论带（年-月），超过 3 个月的技术类结论要复核。\n')

    for gname, ids in GROUPS:
        L.append(f'## {gname}\n')
        L.append('| 作者 | 篇数 | 万字 | 一句话定位 | 教程 |')
        L.append('|---|---|---|---|---|')
        for i in ids:
            if i not in meta:
                continue
            name, cnt, ch, fn = meta[i]
            L.append(f'| {name} | {cnt} | {ch/10000:.1f} | {ONE.get(i,"")} | [打开]({esc(fn)}) |')
        L.append('')

    # 未分组/其余作者
    used = {i for _, ids in GROUPS for i in ids}
    rest = [i for i in sorted(meta) if i not in used]
    L.append('## 七、未归类（其余作者）\n')
    L.append('| 作者 | 篇数 | 万字 | 一句话定位 | 教程 |')
    L.append('|---|---|---|---|---|')
    for i in rest:
        name, cnt, ch, fn = meta[i]
        L.append(f'| {name} | {cnt} | {ch/10000:.1f} | {ONE.get(i,"")} | [打开]({esc(fn)}) |')
    L.append('')

    L.append('## 按篇数排序的总表\n')
    L.append('| # | 作者 | 篇数 | 教程 |')
    L.append('|---|---|---|---|')
    for i in sorted(meta, key=lambda x: -meta[x][1]):
        name, cnt, ch, fn = meta[i]
        L.append(f'| {i:03d} | {name} | {cnt} | [打开]({esc(fn)}) |')
    L.append('')

    L.append('## 无内容作者（215 个目录，未生成教程）\n')
    L.append('这些目录没有任何 md 文件：**8 位 A 档纯编程号 0 篇待提取**（大宝爱编程、课代表立正、python-青木学长、'
             '程序员阿崔Acui、老傅1024、大厂阿星、JimChannel、林粒粒呀），其余多为关注了但未开始提取的作者。'
             '全名单见 [全库作者索引](../_全库作者索引.md) 的 E 档与空目录部分。\n')

    L.append('---\n')
    L.append('导航：[🏠 README](../README.md) · [作者分页索引](../作者/index.md) · [全库作者索引](../_全库作者索引.md) · [A 档分析](../分析/README.md)')

    open(os.path.join(TUT, 'README.md'), 'w', encoding='utf-8').write('\n'.join(L))
    print('索引生成：', len(meta), '位，', tot_art, '篇')


if __name__ == '__main__':
    main()
