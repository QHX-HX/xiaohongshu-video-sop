#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Obsidian 知识库批量生成器：把「选题 / 知识卡片 / 脚本」批量归档为 Obsidian 笔记。

纯本地文件生成，不访问网络。用于把一次创作的内容沉淀为可复用的知识资产。

用法：
    # 从选题 CSV 生成选题库笔记
    python build_obsidian_library.py --type topic --input topics.csv --out vault/选题库

    # 从知识卡片 CSV 生成知识卡片笔记
    python build_obsidian_library.py --type knowledge --input cards.csv --out vault/知识卡片

    # 生成默认模板预览（不写文件）
    python build_obsidian_library.py --preview
"""
import argparse
import csv
import os
import sys
from datetime import datetime

FRONTMATTER = "---\ntype: {type}\ndate: {date}\ntags: {tags}\n---\n\n"

TEMPLATES = {
    "topic": {
        "hint": "CSV 列: title,info_gap,utility,virality,personality,keyword",
        "body": """# 选题：{title}

## 基本信息
- 知识类型：{kw}
- 打分：信息差 {info_gap} / 实用 {utility} / 传播 {virality} / 特色 {personality}
- 总分：{total} / 20

## 状态
- [ ] 待选 → 已采纳 → 已发布

## 标题候选
1. 
2. 
3. 
""",
    },
    "knowledge": {
        "hint": "CSV 列: title,core,concepts,method,sources",
        "body": """# 知识卡片：{title}

## 核心观点（1 句话）
> {core}

## 关键概念
{concepts}

## 方法论 / 步骤
{method}

## 参考来源
{sources}
""",
    },
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

def _parse_tags(tags_str: str) -> str:
    tags = [t.strip() for t in tags_str.split(",") if t.strip()]
    return "[" + ", ".join(f"#{t}" for t in tags) + "]" if tags else "[]"


def make_note(note_type: str, row: dict) -> str:
    tpl = TEMPLATES[note_type]
    today = datetime.now().strftime("%Y-%m-%d")
    if note_type == "topic":
        try:
            total = sum(int(row.get(k, 0)) for k in
                        ["info_gap", "utility", "virality", "personality"])
        except ValueError:
            total = 0
        kw = row.get("keyword", "方法论")
        body = tpl["body"].format(
            title=row.get("title", "未命名"),
            kw=kw, info_gap=row.get("info_gap", 0), utility=row.get("utility", 0),
            virality=row.get("virality", 0), personality=row.get("personality", 0),
            total=total,
        )
    else:  # knowledge
        body = tpl["body"].format(
            title=row.get("title", "未命名"),
            core=row.get("core", ""), concepts=row.get("concepts", ""),
            method=row.get("method", ""), sources=row.get("sources", ""),
        )
    tags = _parse_tags(row.get("tags", ""))
    return FRONTMATTER.format(type=note_type, date=today, tags=tags) + body


def build(note_type: str, input_csv: str, out_dir: str):
    if note_type not in TEMPLATES:
        print(f"错误：未知类型 {note_type}，可选 {list(TEMPLATES.keys())}", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(input_csv):
        print(f"错误：文件不存在 {input_csv}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(out_dir, exist_ok=True)
    count = 0
    for row in _read_csv_rows(input_csv):
        title = row.get("title", "").strip()
        if not title:
            continue
        note = make_note(note_type, row)
        fname = f"{out_dir}/{title}.md"
        with open(fname, "w", encoding="utf-8") as nf:
            nf.write(note)
        count += 1
    print(f"已生成 {count} 篇 {note_type} 笔记到 {out_dir}")
    print(f"模板提示：{TEMPLATES[note_type]['hint']}")


def main():
    parser = argparse.ArgumentParser(description="Obsidian 知识库批量生成（本地）")
    parser.add_argument("--type", choices=list(TEMPLATES.keys()), help="笔记类型")
    parser.add_argument("--input", help="输入 CSV")
    parser.add_argument("--out", help="输出目录")
    parser.add_argument("--preview", action="store_true", help="预览各类型模板结构")
    args = parser.parse_args()

    if args.preview:
        print("可生成的类型与模板结构：")
        for t, cfg in TEMPLATES.items():
            print(f"\n[{t}] {cfg['hint']}")
        return

    if not (args.type and args.input and args.out):
        print("请提供 --type --input --out，或 --preview 预览", file=sys.stderr)
        sys.exit(1)
    build(args.type, args.input, args.out)


if __name__ == "__main__":
    main()
