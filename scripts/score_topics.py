#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
选题打分工具：基于「选题判断标准」对候选选题批量打分排序。

纯本地处理，不访问任何网络接口。输入为 CSV（或交互输入），输出排序结果。

用法：
    python score_topics.py --input topics.csv
    python score_topics.py --input topics.csv --threshold 12
    python score_topics.py --topic "如何高效学习"   # 交互式单条打分

CSV 列：title,info_gap,utility,virality,personality （维度 0-5）
"""
import argparse
import csv
import sys
import os

CRITERIA = ["info_gap", "utility", "virality", "personality"]
CRITERIA_CN = {
    "info_gap": "信息差",
    "utility": "实用性",
    "virality": "传播性",
    "personality": "个人特色",
}


def _read_csv_rows(path: str):
    """读取 CSV 全部行，兼容 UTF-8(-BOM) 与 GBK（中文 Excel 默认另存编码）。"""
    for enc in ("utf-8-sig", "gbk"):
        try:
            with open(path, "r", encoding=enc, newline="") as f:
                return list(csv.DictReader(f))
        except UnicodeDecodeError:
            continue
    print(f"错误：无法解码 CSV 文件 {path}，请另存为 UTF-8 编码后重试", file=sys.stderr)
    sys.exit(1)

def score_one(title: str, scores: dict) -> dict:
    total = sum(scores.get(k, 0) for k in CRITERIA)
    if total >= 12:
        verdict = "值得做"
    elif total >= 10:
        verdict = "可观望"
    else:
        verdict = "建议放弃"
    return {"title": title, "scores": scores, "total": total, "verdict": verdict}


def render_result(r: dict) -> str:
    parts = []
    for k in CRITERIA:
        parts.append(f"{CRITERIA_CN[k]}={r['scores'].get(k, 0)}")
    return f"[{r['total']:>2}/20] {r['verdict']} | {r['title']}（{' '.join(parts)}）"


def interactive(topic: str):
    print(f"\n为选题打分（0-5）：{topic}")
    scores = {}
    for k in CRITERIA:
        while True:
            try:
                val = int(input(f"  {CRITERIA_CN[k]}（0-5）: "))
                if 0 <= val <= 5:
                    scores[k] = val
                    break
                print("  请输入 0-5 的整数")
            except (ValueError, EOFError):
                print("  请输入 0-5 的整数")
    r = score_one(topic, scores)
    print("\n" + render_result(r))


def from_csv(path: str, threshold: int):
    if not os.path.exists(path):
        print(f"错误：文件不存在 {path}", file=sys.stderr)
        sys.exit(1)
    results = []
    for row in _read_csv_rows(path):
        title = row.get("title", "").strip()
        if not title:
            continue
        scores = {}
        for k in CRITERIA:
            try:
                scores[k] = int(float(row.get(k, 0)))
            except (ValueError, TypeError):
                scores[k] = 0
        results.append(score_one(title, scores))

    results.sort(key=lambda x: x["total"], reverse=True)

    print(f"\n共 {len(results)} 条选题，按总分排序（≥{threshold} 为值得做）：\n")
    for r in results:
        print(render_result(r))
    print("\n--- 建议优先做（total>=threshold）---")
    for r in results:
        if r["total"] >= threshold:
            print(f"  {r['title']}")
    print("\n--- 建议观望/放弃（total<threshold）---")
    for r in results:
        if r["total"] < threshold:
            print(f"  {r['title']}（{r['total']}/20）")


def main():
    parser = argparse.ArgumentParser(description="小红书选题打分工具（本地）")
    parser.add_argument("--input", help="选题 CSV 文件路径")
    parser.add_argument("--topic", help="单条选题（交互式打分）")
    parser.add_argument("--threshold", type=int, default=12, help="值得做的总分阈值，默认 12")
    args = parser.parse_args()

    if args.input:
        from_csv(args.input, args.threshold)
    elif args.topic:
        interactive(args.topic)
    else:
        print("请提供 --input <csv> 或 --topic <选题>", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
