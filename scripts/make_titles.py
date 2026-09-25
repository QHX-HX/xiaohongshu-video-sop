#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标题生成器：基于「5 大标题公式 + 关键词 + 情绪词」批量生成标题候选。

纯本地规则组合。生成的是候选，需人工按「埋词 + 情绪 + 精准」标准筛选。

用法：
    python make_titles.py --keyword "向上管理" --count 8
    python make_titles.py --keyword "如何高效学习" --style 方法论 --count 10
    python make_titles.py --keyword "副业" --count 12 --seed 7
    python make_titles.py --keyword "做自媒体" --style 认知纠偏 --count 8
"""
import argparse
import random
import itertools

# 5 大标题公式模板。
# {kw}=核心词，{emo}=情绪词，{n}=数字，{人群}=目标人群
# {错因}=观众原有的错误认知，{真因}=纠偏后的真正原因（仅「认知纠偏」风格用到）
STYLES = {
    "认知颠覆": [
        "关于{kw}，90% 的人都错了",
        "{kw}的{emo}真相，没人告诉你",
        "别再做{kw}了，{emo}",
        "{kw}越努力越糟？反直觉答案",
    ],
    # 认知纠偏：不直给结论，先否定观众原有认知、制造认知缺口，再暗示真正原因。
    # 对应认知纠偏脚本法：把「输出答案」变成「完成一次认知纠偏」。
    "认知纠偏": [
        "你以为{kw}靠{错因}？其实关键在{真因}",
        "{kw}最难的不是{错因}，而是{真因}",
        "别再{错因}了，{kw}越努力越错",
        "{kw}最大的误区：光靠{错因}根本没用",
        "为什么你{错因}却没用？{kw}真正要看的是{真因}",
        "{kw}做不好，问题不在{错因}，在{真因}",
    ],
    "方法论": [
        "{kw}的 {n} 个步骤，建议收藏",
        "一套方法论搞定{kw}",
        "{kw}避坑清单（亲测有效）",
        "{kw}新手到高手的 {n} 个关键",
    ],
    "结果导向": [
        "从新手到{kw}高手，我做对了什么",
        "我用 {n} 个月搞定了{kw}",
        "{kw}让我的人生{emo}改变",
    ],
    "人群定向": [
        "给{人群}的 {n} 个{kw}建议",
        "{人群}必看：{kw}的正确打开方式",
    ],
}

EMOTION_WORDS = ["惊人", "扎心", "颠覆", "值钱", "高效", "真实", "清醒", "狠"]
DEFAULT_AUDIENCES = ["职场新人", "管理者", "学生党", "副业人群", "想提升的人", "打工人"]
# 认知纠偏风格用词池：{错因}=观众常见错误认知，{真因}=纠偏后的真正原因
WRONG_CAUSES = ["自律", "努力", "坚持", "堆量", "拼命", "勤奋", "加班"]
TRUE_CAUSES = ["方法", "方法论", "竞争力", "选择", "系统", "认知", "策略"]


def generate(keyword: str, style: str | None, count: int, seed: int | None):
    if seed is not None:
        random.seed(seed)

    if style:
        styles = [style]
    else:
        styles = list(STYLES.keys())

    titles = []
    while len(titles) < count:
        for s in styles:
            templates = STYLES[s]
            tpl = random.choice(templates)
            n = random.randint(3, 7)
            emo = random.choice(EMOTION_WORDS)
            aud = random.choice(DEFAULT_AUDIENCES)
            wrong = random.choice(WRONG_CAUSES)
            truth = random.choice(TRUE_CAUSES)
            title = tpl.format(kw=keyword, emo=emo, n=n, 人群=aud, 错因=wrong, 真因=truth)
            if title not in titles:
                titles.append((s, title))
            if len(titles) >= count:
                break
        if len(titles) >= count:
            break
    return titles[:count]


def main():
    parser = argparse.ArgumentParser(description="小红书知识类标题生成器（本地规则组合）")
    parser.add_argument("--keyword", required=True, help="核心关键词/主题")
    parser.add_argument("--style", choices=list(STYLES.keys()), help="标题公式风格，默认全部")
    parser.add_argument("--count", type=int, default=8, help="生成条数，默认 8")
    parser.add_argument("--seed", type=int, default=None, help="随机种子")
    args = parser.parse_args()

    titles = generate(args.keyword, args.style, args.count, args.seed)

    print(f"\n关键词：{args.keyword}  生成 {len(titles)} 条标题候选\n")
    for i, (s, t) in enumerate(titles, 1):
        print(f"{i:>2}. [{s}] {t}")

    print("\n--- 筛选提示 ---")
    print("1) 包含核心关键词（利于搜索埋词） 2) 带情绪词/数字 3) 与正文一致不标题党")
    print("发布前对照 references/prohibited-words.md 检查是否含违规词。")


if __name__ == "__main__":
    main()
