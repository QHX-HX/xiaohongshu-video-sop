#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
选题草稿生成器：基于「领域 + 4 大方向」+ 关键词库，组合出选题草稿。

纯本地规则组合，不抓取任何平台数据、不逆向接口。
生成的是「选题方向草稿」，需人工按 topic-criteria 打分后决定是否采用。

用法：
    python generate_topic_ideas.py --domain "职场成长" --count 12
    python generate_topic_ideas.py --domain "学习方法" --direction 方法论 --count 6
    python generate_topic_ideas.py --domain "管理" --count 20 --seed 42
"""
import argparse
import random
import itertools

# 各方向的句式模板。{} 处填充核心词
DIRECTION_TEMPLATES = {
    "认知颠覆": [
        "关于{kw}，90% 的人都想错了",
        "{kw}的真相，和你想的不一样",
        "别再做{kw}的 3 个无效努力",
        "为什么越努力{kw}越差？答案反直觉",
        "停止{kw}，你才能真的进步",
    ],
    "方法论": [
        "{kw}的 5 个可复制步骤",
        "一套方法论，搞定{kw}",
        "{kw}新手到高手：SOP 拆解",
        "{kw}避坑清单（亲测有效）",
        "照着做：{kw}的傻瓜式流程",
    ],
    "经验总结": [
        "我踩过{kw}的 5 个坑，别再犯",
        "从菜鸟到老手，我关于{kw}的 3 个关键",
        "{kw}两年，我悟到的教训",
        "做{kw}的第 100 天，我才明白",
        "我的{kw}复盘：哪些有效哪些白费",
    ],
    "行业洞察": [
        "未来 3 年，{kw}会怎样变",
        "{kw}的底层规律，看懂的人赢",
        "{kw}正在悄悄洗牌，普通人怎么办",
        "关于{kw}的趋势，内行都在关注",
        "{kw}背后真正值钱的能力",
    ],
}

# 通用高频词池，用于填充（也可被 --kws 覆盖）
DEFAULT_KEYWORDS = [
    "职场沟通", "向上管理", "时间管理", "精力管理", "情绪管理", "副业", "学习", "阅读",
    "写作", "汇报", "加薪", "跳槽", "复盘", "目标管理", "拖延", "专注力", "自律", "习惯养成",
]


def generate(domain: str, direction: str | None, count: int, kws: list[str], seed: int | None):
    if seed is not None:
        random.seed(seed)

    if direction:
        directions = [direction]
    else:
        directions = list(DIRECTION_TEMPLATES.keys())

    # 按方向轮转，直到凑够 count 条，保证多方向覆盖且数量准确
    ideas = []
    titles_seen = set()
    kw_cycle = itertools.cycle(kws)
    dir_cycle = itertools.cycle(directions)
    attempts = 0
    while len(ideas) < count and attempts < count * 10:
        attempts += 1
        d = next(dir_cycle)
        kw = next(kw_cycle)
        tpl = random.choice(DIRECTION_TEMPLATES[d])
        idea = tpl.format(kw=kw)
        if idea not in titles_seen:
            titles_seen.add(idea)
            ideas.append((d, idea))
    return ideas


def main():
    parser = argparse.ArgumentParser(description="小红书知识类选题草稿生成器（本地规则组合）")
    parser.add_argument("--domain", required=True, help="领域，如 职场成长 / 学习方法")
    parser.add_argument("--direction", choices=list(DIRECTION_TEMPLATES.keys()),
                        help="限定某一方向，默认覆盖全部 4 方向")
    parser.add_argument("--count", type=int, default=12, help="生成条数，默认 12")
    parser.add_argument("--kws", help="自定义关键词，逗号分隔，覆盖默认词池")
    parser.add_argument("--seed", type=int, default=None, help="随机种子，便于复现")
    args = parser.parse_args()

    kws = [k.strip() for k in args.kws.split(",")] if args.kws else DEFAULT_KEYWORDS

    ideas = generate(args.domain, args.direction, args.count, kws, args.seed)

    print(f"\n领域：{args.domain}  生成 {len(ideas)} 条选题草稿（本地规则组合，需人工打分后采用）\n")
    for i, (d, idea) in enumerate(ideas, 1):
        print(f"{i:>2}. [{d}] {idea}")

    print("\n--- 下一步 ---")
    print("将这些选题写入 CSV（title,info_gap,utility,virality,personality）")
    print("运行 python scripts/score_topics.py --input topics.csv 打分排序")


if __name__ == "__main__":
    main()
