#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
复盘数据分析工具：分析「用户从小红书官方创作中心/专业号后台导出」的笔记数据 CSV，
输出完播率、收藏率、转发率、互动率等复盘指标与 TOP 排行。

完全本地处理。数据来源必须是用户通过官方后台导出的公开统计数据，
本脚本不访问任何平台接口、不爬取、不逆向。

用法：
    python analyze_exported_data.py --input notes.csv
    python analyze_exported_data.py --input notes.csv --out report.txt

CSV 常见列（兼容多种命名，支持 UTF-8 与 GBK/Excel 另存编码）：
    笔记标题/title | 播放量/观看量/阅读量/views | 完播率/completion
    收藏数/收藏/collects | 转发数/分享数/转发/shares | 点赞数/点赞/likes
    评论数/评论/comments | 发布时间/date
"""
import argparse
import csv
import os
import sys


def _pick(row: dict, keys: list[str], default=0):
    """从 row 中按多个可能的列名取第一个存在的值。"""
    for k in keys:
        if k in row and row[k] not in ("", None):
            try:
                return float(row[k])
            except ValueError:
                return default
    return default


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

def analyze(path: str):
    if not os.path.exists(path):
        print(f"错误：文件不存在 {path}", file=sys.stderr)
        sys.exit(1)

    records = []
    for row in _read_csv_rows(path):
        title = row.get("笔记标题") or row.get("title") or row.get("标题") or "未命名"
        views = _pick(row, ["播放量", "观看量", "阅读量", "views", "播放", "播放数"])
        completion = _pick(row, ["完播率", "completion", "完播"])  # 百分比或小数
        collects = _pick(row, ["收藏数", "收藏", "collects"])
        shares = _pick(row, ["转发数", "分享数", "转发", "shares"])
        likes = _pick(row, ["点赞数", "点赞", "likes", "赞"])
        comments = _pick(row, ["评论数", "评论", "comments"])

        # 完播率统一为百分比数值；若是 0~1 小数则乘 100
        if 0 < completion <= 1:
            completion *= 100
        # 收藏率/转发率/互动率 基于播放量计算
        collect_rate = (collects / views * 100) if views else 0
        share_rate = (shares / views * 100) if views else 0
        interact = likes + collects + comments + shares
        interact_rate = (interact / views * 100) if views else 0

        records.append({
            "title": title, "views": views, "completion": completion,
            "collects": collects, "shares": shares, "likes": likes,
            "comments": comments, "collect_rate": collect_rate,
            "share_rate": share_rate, "interact_rate": interact_rate,
        })

    if not records:
        print("警告：没有解析到任何有效数据行", file=sys.stderr)
        return []

    n = len(records)
    avg = lambda key: sum(r[key] for r in records) / n

    print(f"\n===== 复盘分析（共 {n} 条笔记）=====\n")
    print(f"平均播放:   {avg('views'):.0f}")
    print(f"平均完播率: {avg('completion'):.1f}%")
    print(f"平均收藏率: {avg('collect_rate'):.2f}%")
    print(f"平均转发率: {avg('share_rate'):.2f}%")
    print(f"平均互动率: {avg('interact_rate'):.2f}%（赞藏评转/播放）")
    print()

    def top(key, label, limit=5, reverse=True):
        ranked = sorted(records, key=lambda r: r[key], reverse=reverse)[:limit]
        print(f"-- TOP{limit} {label} --")
        for i, r in enumerate(ranked, 1):
            print(f"  {i}. {r['title']}  ({r[key]:.1f})")
        print()

    top("views", "播放量")
    top("completion", "完播率")
    top("collect_rate", "收藏率")
    top("interact_rate", "互动率")

    print("-- 爆款基因建议 --")
    print("对比 TOP 笔记与平均，提取标题/开场/埋词的共性。")

    return records


def main():
    parser = argparse.ArgumentParser(description="小红书复盘数据分析（本地，仅处理官方导出数据）")
    parser.add_argument("--input", required=True, help="笔记数据 CSV（官方后台导出）")
    parser.add_argument("--out", help="输出报告文件路径（可选）")
    args = parser.parse_args()

    records = analyze(args.input)

    if args.out and records:
        import io
        buf = io.StringIO()
        _old = sys.stdout
        sys.stdout = buf
        try:
            # 重跑一次把输出捕获到文件
            analyze(args.input)
        finally:
            sys.stdout = _old
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(buf.getvalue())
        print(f"\n报告已写入: {args.out}")


if __name__ == "__main__":
    main()
