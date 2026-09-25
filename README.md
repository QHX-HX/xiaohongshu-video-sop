# xiaohongshu-video-sop

小红书知识输出类视频 SOP 技能包（AgentSkills 格式），专注职场/管理/个人成长领域的知识分享视频，覆盖 **选题 → 知识梳理 → 脚本 → 拍摄 → 剪辑 → 发布 → 复盘 → 知识沉淀** 完整链路。

适用于支持 [AgentSkills](https://github.com/anthropics/skills) 规范（`SKILL.md`）的 AI Agent（如 Claude Code、灵犀等）。

## 功能特性

- **完整 SOP 流程**：起号、爆款选题、口播脚本创作、标题/文案生成、拍摄剪辑清单、发布复盘、长尾流量优化、Obsidian 知识库沉淀
- **认知纠偏脚本法**：进阶叙事模板，把「输出答案」变成「完成一次认知纠偏」
- **12 字段单文件交付**：每期视频一份 md 完整档案（选题档案/脚本/提词器稿/标题/封面文案/发布正文/标签/互动/违禁词检查等）
- **内置本地脚本**：选题生成、选题打分、标题生成、官方导出数据复盘分析、Obsidian 批量归档

## 目录结构

```
xiaohongshu-video-sop/
├── SKILL.md              # 技能主文件（Agent 读取入口）
├── topics.csv            # 示例选题数据（可替换为你自己的）
├── references/           # 12 个模板与清单（按需加载）
│   ├── deliverables-checklist.md   # 单期 12 字段交付清单
│   ├── cognitive-reframe-template.md # 认知纠偏脚本模板
│   ├── prohibited-words.md         # 违规词与内容红线清单
│   └── ...
└── scripts/              # 5 个纯本地 Python 脚本
    ├── generate_topic_ideas.py     # 选题草稿生成
    ├── score_topics.py             # 选题打分排序
    ├── make_titles.py              # 标题候选生成
    ├── analyze_exported_data.py    # 官方导出数据复盘分析
    └── build_obsidian_library.py   # Obsidian 知识库批量归档
```

## 脚本用法

所有脚本均为**纯本地处理**，不访问平台接口、不爬取、不逆向，依赖仅需 Python 3.10+（标准库）。

```bash
# 生成选题草稿
python scripts/generate_topic_ideas.py --domain 职场成长 --count 12

# 选题打分排序
python scripts/score_topics.py --input topics.csv

# 生成标题候选
python scripts/make_titles.py --keyword 向上管理 --count 8

# 分析官方后台导出的笔记数据（兼容 UTF-8 / GBK 编码）
python scripts/analyze_exported_data.py --input notes.csv --out report.txt

# 批量生成 Obsidian 笔记
python scripts/build_obsidian_library.py --type topic --input topics.csv --out vault/选题库
```

## 安装使用

1. 克隆本仓库：
   ```bash
   git clone https://github.com/<你的用户名>/xiaohongshu-video-sop.git
   ```
2. 将 `xiaohongshu-video-sop/` 目录放入 Agent 的技能目录（如 Claude Code 的 `~/.claude/skills/`，灵犀的「技能 - 我的技能」）。
3. 对 Agent 说「帮我做一期小红书知识类视频」「给这个选题打分」等即可触发。

## 合规声明

- 获取热门选题、竞品数据等，必须通过**官方公开渠道**（小红书创作中心、公开搜索页面、第三方公开统计）
- 内置脚本均为本地处理，**严禁**用于逆向平台接口、突破反爬、绕过登录、批量采集他人隐私数据
- 对标拆解仅学习逻辑与结构，禁止抄袭、搬运他人原创内容
- 发布前请对照 `references/prohibited-words.md` 自查内容合规

## License

[MIT](LICENSE) © qianhuixuan
