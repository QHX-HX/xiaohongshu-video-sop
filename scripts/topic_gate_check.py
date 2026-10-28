#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
选题三问检测器：发布前最后一关，任一问题答案为 no 则回去重改，不要开拍。

三问（详见 references/traffic-funnel-topic-upgrade.md）：
    1. 覆盖度：这个话题我家楼下卖煎饼的大妈能听懂吗？
    2. 关联度：能让观众觉得「这说的不就是我吗」？
    3. 情绪度：能让人产生哪怕一丝生气、惊讶甚至想笑吗？

纯本地处理，不访问任何网络接口。

用法：
    python topic_gate_check.py --topic "选题标题"                 # 交互式三问
    python topic_gate_check.py --topic "选题标题" --yes --yes --no  # 直接给结论
    python topic_gate_check.py --input gates.csv                  # 批量（CSV 列：title,coverage,relevance,emotion，值为 yes/no）
"""
import argparse
import csv
import sys
import os

QUESTIONS = [
    ("coverage",  "覆盖度：这个话题我家楼下卖煎饼的大妈能听懂吗？"),
    ("relevance", "关联度：能让观众觉得「这说的不就是我吗」？"),
    ("emotion",   "情绪度：能让人产生哪怕一丝生气、惊讶甚至想笑吗？"),
]

def normalize(val: str) -> bool:
    """把 yes/true/1/过/y 视为通过，其余视为 no。"""
    return val.strip().lower() in ("yes", "true", "1", "y", "过", "是", "pass")

def check_one(title: str, answers: dict) -> dict:
    passed = {k: normalize(v) for k, v in answers.items()}
    gate = "PASS" if all(passed.values()) else "REVISE"
    return {"title": title, "passed": passed, "gate": gate}

def render_result(r: dict) -> str:
    marks = " / ".join(
        f"{label.split('：')[0]}{'✓' if r['passed'][k] else '✗'}"
        for k, label in QUESTIONS
    )
    hint = "" if r["gate"] == "PASS" else "（回去重改：对照三招 私事公办/痛点嫁接/极度反差 撑大漏斗开口）"
    return f"[{r['gate']}] {r['title']} — {marks}{hint}"

def interactive(topic: str):
    print(f"\n选题三问检测：{topic}\n（y=通过，n=不通过）")
    answers = {}
    for k, label in QUESTIONS:
        while True:
            try:
                val = input(f"  {label} (y/n): ").strip()
            except EOFError:
                val = ""
            if val.lower() in ("y", "n"):
                answers[k] = val
                break
            print("  请输入 y 或 n")
    print("\n" + render_result(check_one(topic, answers)))

def from_csv(path: str):
    if not os.path.exists(path):
        print(f"错误：文件不存在 {path}", file=sys.stderr)
        sys.exit(1)
    results = []
    for enc in ("utf-8-sig", "gbk"):
        try:
            with open(path, "r", encoding=enc, newline="") as f:
                rows = list(csv.DictReader(f))
            break
        except UnicodeDecodeError:
            continue
    else:
        print(f"错误：无法解码 CSV 文件 {path}，请另存为 UTF-8 编码后重试", file=sys.stderr)
        sys.exit(1)

    for row in rows:
        title = row.get("title", "").strip()
        if not title:
            continue
        answers = {k: row.get(k, "no") for k, _ in QUESTIONS}
        results.append(check_one(title, answers))

    print(f"\n共 {len(results)} 条选题，三问检测结果：\n")
    for r in results:
        print(render_result(r))
    revise = [r for r in results if r["gate"] == "REVISE"]
    print(f"\n--- 汇总：PASS {len(results) - len(revise)} 条 / REVISE {len(revise)} 条 ---")
    for r in revise:
        print(f"  需回改：{r['title']}")

def main():
    parser = argparse.ArgumentParser(description="选题三问检测器（本地）")
    parser.add_argument("--topic", help="单条选题标题")
    parser.add_argument("--input", help="批量检测 CSV（列：title,coverage,relevance,emotion）")
    parser.add_argument("--yes", dest="flags", action="append_const", const="yes", help="按顺序给三问答案：通过")
    parser.add_argument("--no", dest="flags", action="append_const", const="no", help="按顺序给三问答案：不通过")
    args = parser.parse_args()

    if args.input:
        from_csv(args.input)
    elif args.topic:
        if args.flags and len(args.flags) == len(QUESTIONS):
            answers = {k: v for (k, _), v in zip(QUESTIONS, args.flags)}
            print(render_result(check_one(args.topic, answers)))
        else:
            interactive(args.topic)
    else:
        print("请提供 --topic <选题> 或 --input <csv>", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
