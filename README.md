# portfolio-source-reader

> 给有多源项目（本地 + GitHub + Gitee + 档案）的工程师用的 agent skill：把散落的 项目信息按 STAR 挖出来，产出可直接进简历/档案/面试准备的结构化素材。
>
> **不是**简历生成器（那是 resume-builder-skill 的事）。**是**素材采集器——回答"AI 怎么知道你到底做了什么"。

## 这是什么

你做过 10+ 个项目，信息散落在：
- 本地 `c:\project\*`（源码 + docs + git log）
- GitHub 50 个仓库（公开 README + CI）
- Gitee 2 个仓库
- portfolio 14 份 case-study 档案（二手摘要）

通用简历 skill 的问题是：**它不知道你的项目在哪、不知道哪些数字可信、不知道哪些该脱敏**。这个 skill 解决的就是这件事。

## 核心机制

1. **信息源地图（SOURCES.md）**：用户填一张表，告诉 agent"项目→本地路径/git/公开仓库/档案/关键文档"。agent 进来先读这个。
2. **分层核实**：先读二手档案拿摘要（快），需要细节 cd 到原始项目挖 git log / 代码 / docs（准）。
3. **STAR 输出**：四要素（S/T/A/R）+ 难点五段（现象→定位→根因→解法→验证），三版格式（简历/档案/面试）。
4. **铁律**：数字必须数出来、不编造、标边界（独立/协作/AI）、商业脱敏。

## 与同类 skill 的区别

| skill | 挖什么 | 局限 |
|-------|--------|------|
| resume-builder-skill | 帮用户把信息做成简历 PDF | 不知道用户项目在哪，靠用户喂内容 |
| earino/resumasher | 从一个项目文件夹挖证据 | 单源，不支持本地+GitHub+Gitee+档案多源 |
| **本 skill** | **多源信息地图 + 分层核实** | **需要用户先填 SOURCES.md** |

## 安装

### 方式 1：直接 clone 到 skills 目录

```bash
git clone https://github.com/<your-name>/portfolio-source-reader-skill.git ~/.zcode/skills/portfolio-source-reader
# 或 ~/.codex/skills/、~/.claude/skills/（看你的 agent）
```

### 方式 2：作为参考文档

直接把 `SKILL.md` 和 `references/` 放进你的项目，agent 读 `SKILL.md` 时按里面的工作流走。

## 使用

### 第 1 步：填信息源地图

复制 `references/sources-map-template.md` 到你的 portfolio 仓库根目录，命名为 `SOURCES.md`，按模板填：

```markdown
### hermes-watch（全栈 AI 巡检平台）
- 本地路径：`c:\project\hermes-watch`
- Git：69 commits，最后 2026-09-16
- 公开仓库：https://github.com/you/hermes-watch
- 档案：`projects/hermes-watch/case-study.md`
- 关键文档：`backend/app/`、`docs/LLM.md`、`backend/run_tests.py`
- 挖什么：并发轮换行锁 / 跳板连接池 / metrics 降采样 / 审批制执行
- ⚠️ 脱敏：否
```

填好 `assets/sources-map.example.md` 是填好的样例，可参考。

### 第 2 步：触发

对 agent 说：
- "按 portfolio-source-reader skill 帮我挖 identity-service 的难点"
- "帮我写简历，主攻后端"
- "分析我的项目，准备面试"

agent 会自动：
1. 读 `SOURCES.md` 找项目
2. 读 `projects/index.md` 拿概览
3. 按优先级挖（档案→git log→代码→docs）
4. 按 STAR 输出（简历/档案/面试三选一）

### 第 3 步：输出

agent 产出的素材可直接喂给 resume-builder-skill 或其他简历工具，或自己手改成简历。

## 目录

```
portfolio-source-reader-skill/
├── SKILL.md                         # skill 主文件（agent 入口）
├── README.md                        # 本文件
├── LICENSE                          # MIT
├── references/
│   ├── sources-map-template.md      # 空白信息源地图模板
│   ├── star-template.md             # STAR 输出模板（三版）
│   └── examples.md                  # 3 个挖好的样例（已脱敏）
└── assets/
    └── sources-map.example.md       # 填好的信息源地图示例
```

## 设计哲学

1. **事实 > 形容词**：数字必须数出来，不能编。"235 项测试"比"大量测试"值钱。
2. **分层核实**：档案是摘要，源码是事实源。摘要快、源码准，各司其职。
3. **诚实边界**：独立/协作/AI 辅助必须标注，这是信任基础。
4. **脱敏默认**：商业项目默认不写客户/域名/产品名。
5. **不替代简历工具**：这个 skill 挖素材，resume-builder-skill 排版——分工明确。

## 适用场景

- 有多源项目的工程师（本地 + GitHub + Gitee + 档案）
- 项目做完没时间写档案，需要 agent 帮挖
- 准备面试，需要把项目难点系统梳理
- 写简历，需要带数字的事实弹药

## 不适用

- 单个项目、信息集中（直接用简历工具即可）
- 与本人项目无关的代码分析
- 一般性写作

## License

MIT