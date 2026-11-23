---
name: portfolio-source-reader
description: >-
  Read a developer's scattered project sources (local repos, GitHub/Gitee, case-study archives) and extract STAR-structured material for resume writing, project archives, and interview prep — with verified numbers and no fabricated metrics.
  当用户说"帮我写简历/做简历/项目档案/面试准备/分析我的项目/总结我的项目/我的项目有什么含金量/挖一下我在 X 项目做了什么"时使用。
  Use only for reading this user's own project sources to produce resume/archive/interview material.
  Do NOT use for general writing or code analysis unrelated to the user's own projects.
---

# Portfolio Source Reader

把散落在多个地方的你的项目信息（本地仓库、GitHub、Gitee、档案），按"事实→数字→难点→反思"的链路读出来，产出可直接进简历 / 项目档案 / 面试准备的结构化素材。

## 核心理念

1. **事实优先**：不编造。数字必须数出来（代码、git log、docs），数不到写"无量化数据"。
2. **多源分层**：先读二手档案拿摘要，需要细节 cd 到原始项目挖——两层各司其职。
3. **诚实边界**：独立开发 / 协作 / AI 辅助，必须标注。
4. **脱敏**：商业项目只写技术方案，不写客户名 / 真实域名 / 内部产品名。

## 何时使用

触发词：
- "写简历 / 做简历 / 简历润色 / 简历生成 / resume"
- "项目档案 / case study / 项目总结"
- "面试准备 / 面试会问什么 / 我的难点"
- "分析我的项目 / 我的项目有哪些 / 挖一下我在 X 项目做了什么"
- "我的项目有什么含金量 / 哪些能写进简历"

**不要**用于：一般性写作、与本人项目无关的代码分析。

## 工作流（三阶段）

### 第 1 阶段：定位信息源

1. **读 `references/sources-map-template.md`**——理解"信息源地图"是什么。
2. **读用户仓库的 `SOURCES.md`**（如果存在）——拿到"项目→本地路径/git/公开仓库/档案路径/关键文档"对照表。
3. **读 `projects/index.md`**（如果存在）——拿到项目概览。
4. **如果没有 SOURCES.md**：先问用户 4 个问题，生成一份：
   - 项目本地路径在哪？
   - 每个项目的 git remote / 公开仓库？
   - 每个项目的 portfolio 档案在哪？
   - 每个项目最关键的 1-2 个文档 / 模块是什么？

### 第 2 阶段：按 STAR 挖素材

对选定项目（2-4 个，按主方向选，不要全挖），按优先级读：

| 优先级 | 信息源 | 挖什么 | 怎么读 |
|--------|--------|--------|--------|
| 1 | portfolio 档案 | 已核实的难点、数字、反思 | 直接读 case-study.md |
| 2 | git log | 做了什么、为什么、什么时候 | `git -C <path> log --oneline` |
| 3 | 代码 + 配置 | 实现细节、参数、行数、测试数 | `find`/`wc -l`/`grep` 数出来 |
| 4 | docs/ | 难点四要素、踩坑、验证数据 | 读 README/ROADMAP/checklist |
| 5 | 公开仓库 README/CI | release、CI 配置、对外说明 | gh api 或浏览器 |

**铁律**：
- **数字优先**：235 项测试、284 个测试函数、2N→N+1、代码缩减 80%——能数就数，数不到写"无量化数据"。
- **不编造**：找不到的数字不要凑；业务数据（用户量、日活）代码里没有，标注"需用户口述"。
- **标边界**：独立开发 / 协作 / AI 辅助——诚实标注。
- **脱敏**：商业项目只写技术方案，不写客户名 / 真实域名 / 内部产品名。

### 第 3 阶段：按 STAR 输出

每条经历产出四要素 + 难点五段：

```
【S 背景】什么业务问题、谁在用、我的角色
【T 任务】我要解决的具体问题
【A 行动】我做了什么（动词开头：设计/重构/优化/攻坚/落地）
【R 结果】量化结果（数字/状态/验证方式）

【难点 N：<一句话现象>】
- 现象：
- 定位：
- 根因：
- 解法：
- 验证：
```

输出格式三选（见 `references/star-template.md`）：
- **简历版**：每条 1-2 行，强动词 + 数字
- **档案版**：四要素 + 难点五段展开
- **面试版**：90 秒讲述 + 追问弹药

## 输出前自检

- [ ] 每个数字都核实过（数了代码 / 查了 git log / 读了 docs），不是凭印象
- [ ] 每条经历都有"我"做了什么，不是"团队做了什么"
- [ ] 商业项目已脱敏
- [ ] 没有编造业务数据
- [ ] 标了哪些是独立开发、哪些是协作
- [ ] 数字口径统一（测试数说清是"测试函数"还是"测试文件"还是"check() 调用"）

## 目录

- `references/sources-map-template.md` — 信息源地图模板（空白版，用户填）
- `references/star-template.md` — STAR 输出模板（简历/档案/面试三版）
- `references/examples.md` — 3 个挖好的样例（hermes-watch / identity-service / Easel，已脱敏）
- `assets/sources-map.example.md` — 填好的信息源地图示例