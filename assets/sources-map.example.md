# 项目信息源地图（SOURCES）

> 这份文件告诉 AI / 人类：**每个项目的原始信息在哪里、二手档案在哪里、核实细节去哪里挖。**
> 任何被要求"写简历 / 写项目档案 / 准备面试 / 分析我的项目"的 agent，先读本文件，再决定去哪儿找素材。

## 怎么用这份地图

1. **先读 `projects/index.md`**（portfolio 总表）——拿到 14 个项目的概览和"我负责什么"。
2. **按主方向选项目**（后端 / AI 应用 / 前端），每个项目看本文件对应的"原始源"和"档案"两行。
3. **快速摘要**：读 portfolio 档案（`projects/<name>/case-study.md`）——已经核实过的二手素材。
4. **需要细节 / 数字 / 代码佐证**：cd 到"本地路径"读源码 + git log + docs——这是事实源。
5. **需要公开仓库内容**：访问"公开仓库"——README、CI 配置、release 记录。
6. **核实规则见 `AGENTS.md` 的"素材采集协议"**——什么样的数据算证据、什么算编造。

## 项目 → 信息源对照表

### hermes-watch（全栈 AI 巡检平台）
- 本地路径：`c:\project\hermes-watch`
- Git：69 commits，最后 2026-09-16
- 公开仓库：https://github.com/<your-github-user>/hermes-watch
- 档案：`projects/hermes-watch/case-study.md`（含 3 分钟演示脚本 + 5 个难点）
- 关键文档：`backend/app/`（24 模块 6,275 行）、`docs/LLM.md`、`docs/竞品调研.md`、`backend/run_tests.py`（235 项）
- 挖什么：并发轮换行锁、跳板连接池、metrics 降采样、审批制执行、CI 配置

### identity-service（统一身份服务）
- 本地路径：`c:\project\identity-service`
- Git：96 commits，34 轮迭代，最后 2026-09-29
- 公开仓库：https://gitee.com/<your-gitee-user>/identity-service
- 档案：`projects/identity-service/case-study.md`（含 6 个难点）
- 关键文档：`docs/ROADMAP.md`（调研 Ory Kratos/CASdoor）、`docs/DRILL_CHECKLISTS.md`（演练踩坑）、`docs/DEPLOY_RIGHTQ.md`、`apps/accounts/security.py`（refresh 轮换）、`tests/`（39 模块 284 函数）
- 挖什么：JWT/JWKS kid、refresh 重放检测、TOTP、OIDC、密钥轮换演练、CI Postgres 并发套件

### recharge-service（支付网关，脱敏）
- 本地路径：`c:\project\recharge-service-staging`
- Git：127 commits，最后 2026-10-01
- 公开仓库：无（内部）
- 档案：`projects/recharge-service/case-study.md`（脱敏，含 6 个难点）
- 关键文档：`docs/接入主线.md`、`docs/operations/生产上线状态与门禁.md`、`contracts/`（QuickPay/HMAC 契约）、`apps/payments/services/idempotency.py`、`apps/payments/services/writer_fence.py`
- 挖什么：幂等租约接管、writer_fence 单写者、对账三方匹配、主密钥环轮换、四层上线状态
- ⚠️ 脱敏：不写客户名、真实域名、内部产品名

### AI-skills（AI 文档平台，脱敏）
- 本地路径：`c:\project\AI-skills`
- Git：134 commits，最后 2026-10-12
- 公开仓库：无（内部）
- 档案：`projects/ai-skills/case-study.md`（脱敏，含 5 个难点）
- 关键文档：`ai-skills-api/api/services/harness/`（ExecutionContext）、`scripts/eval/run_golden_set.py`（Golden-Set）、`scripts/ci/`（治理脚本）、`TESTING_POLICY.md`
- 挖什么：Harness 四级身份贯穿、Golden-Set 断言评测、CI 治理代码化、Job+Redis Stream 断点恢复
- ⚠️ 脱敏：不写业务方、内部域名

### Easel / easel-flow-desktop（AI 视频桌面端，脱敏）
- 本地路径：`c:\project\Easel`（457 commits，最后 2026-11-18）/ `c:\project\easel-flow-desktop`（Trizhi 品牌封装）
- Git：基于 ZJU-REAL/Easel 二次开发（保留 Apache-2.0 署名）
- 档案：`projects/easel/case-study.md`（脱敏，含 3 个难点）
- 关键文档：`CHANGELOG.md`（双语验证记录）、`docs/`（151 篇日期化调查）、`easel/runtime_limits.py`（准入控制 Pool+Lease）、`backend/`（3,533 测试文件）
- 挖什么：发布批次重复提交防线、Chromium 健康监督、准入控制按任务终态释放、验证文档纪律
- ⚠️ 脱敏：不写客户、真实平台账号、业务数据；注明 fork 来源

### qizhiSystem（奇点发明系统，脱敏）
- 本地路径：`c:\project\qizhiSystem\qizhiSystem`
- Git：47 commits，跨 2025-10 → 2026-10，最后 2026-10-19
- 公开仓库：无（内部）
- 档案：`projects/qizhi/case-study.md`（脱敏，含 3 个难点）
- 关键文档：`docs/`（15 篇，含 trizhi 技术框架 Agent 化、prompt cloud sync 契约）、`src/views/`（104 模块）
- 挖什么：双层防重复提交（useGuardedAction + axios adapter）、operateContent 重构（代码缩减 80%）、角色权限矩阵治理
- ⚠️ 脱敏：不写 trizhi 产品名、客户

### infringement（专利侵权检测，脱敏）
- 本地路径：`c:\project\infringement`
- Git：44 commits，最后 2026-10-27
- 公开仓库：无（内部）
- 档案：`projects/infringement/case-study.md`（脱敏，含 3 个难点）
- 关键文档：`docs/`（152 篇，含 FTO PDF 修复、TRO 刷新、monitor 系列 checklist）、`INFRINGEMENT_DEPLOYMENT_RUNBOOK.md`、`tests/`（65 文件）
- 挖什么：FTO If-Range CORS 预检、TRO 列表竞态、多后端失败语义、security smoke 进 verify 链

### hermes-agent-workbench（Agent 工作台，开源）
- 本地路径：`c:\project\hermes-watch` 之外的独立项目（注：GitHub 有但本地副本未确认，以 GitHub 为准）
- 公开仓库：https://github.com/<your-github-user>/hermes-agent-workbench
- 档案：`projects/hermes-agent-workbench/case-study.md`
- 挖什么：受控审批幂等、首 token 看门狗 90s 降级链、workspace_files 版本回滚、三级记忆

### ai-image-studio（画境，开源）
- 本地路径：`c:\project\ai-image-studio`
- Git：81 commits，最后 2026-11-18
- 公开仓库：https://gitee.com/<your-gitee-user>/ai-image-studio
- 档案：`projects/ai-image-studio/case-study.md`
- 关键文档：`docs/bugfix-verification-*.md`
- 挖什么：多模型服务管理、提示词词库、bugfix 验证文档习惯（造物手记 VOL.06 素材源）

### 造物手记系列（22 册 VOL + 4 手册 + 4 番外）
- 本地路径：散落在各 GitHub 仓库（每册一个 repo）
- 公开仓库 hub：https://github.com/<your-github-user>/makers-notebook
- 在线阅读：https://<your-github-user>.github.io/makers-notebook/
- 档案：`projects/notes-series/case-study.md`
- 单册 repo 示例：`imagestudio-story`、`rag-evidence-chain`、`agent-memory`、`agent-eval`、`agent-patrol`、`k8s-primer` 等
- 挖什么：零依赖单页、Playwright 截图验收、诚实性设计（实测 vs 示意）、系列导航、4 个交互 Demo/篇

### SmartGalleryAI（智能图库，开源）
- 公开仓库：https://github.com/<your-github-user>/SmartGalleryAI
- 档案：`projects/smartgalleryai/case-study.md`
- 挖什么：OCR + 语义 + 向量三路召回、本地优先隐私、Provider 抽象

### la-city / chongqing 城市生成器（3D 练习）
- 本地路径：`c:\project\la-city-generator` / `c:\project\la-city-studio`
- 公开仓库：https://github.com/<your-github-user>/chongqing-citygen-mimo-v2.6-flash（公开）/ chongqing-8d-city / chongqing-procedural-city-gpt-6.1-sol / chongqing-8d-city-glm-5.3-flash（部分私有）
- 档案：`projects/la-city/case-study.md` · `projects/chongqing-city/case-study.md`
- 挖什么：mulberry32 种子确定性、7 组 InstancedMesh 合批、台地量化楼不悬空、多模型对照实验

### dual-ai-video（工具链研究）
- 本地路径：`c:\project\dual-ai-video`
- 公开仓库：无（本地 + skill 固化到 ~/.zcode/skills/gpt-gemini-video）
- 档案：`projects/dual-ai-video/case-study.md`
- 挖什么：跨模型流水线、零安装约束、网页语义编排（非 DOM 选择器）、研究复核文档

## 跨项目通用素材（横向证据）

- **测试规模**：hermes-watch 235 项、identity-service 284 函数、recharge 243 文件、Easel 3,533 文件、infringement 65 文件
- **CI**：hermes-watch（ruff+回归+oxlint+go）、identity-service（Postgres+并发）、AI-skills（治理+compose contract）、infringement（verify 链，无 CI runner）
- **文档纪律**：Easel 151 篇、infringement 152 篇、recharge 28 篇、identity-service 8 篇（含 ROADMAP/演练/runbook）
- **性能优化**：hermes-watch 握手 2N→N+1 / 7 往返→2 波 / 行数恒定≤2160；qizhi 代码缩减 80%
- **安全深度**：identity-service 全套（JWT/JWKS/Argon2/MFA/OIDC/refresh 重放/HIBP）、hermes-watch（审批制/白名单/出站脱敏）、infringement（security smoke）

## 不能用的（研究/参考/别人项目）

- `c:\project\hermes-agent-research`：NousResearch/hermes-agent 的克隆（392k 行），**别人的项目**，仅作研究参考
- `c:\project\ComfyUI` / `canvas-editor` / `Seal` / `WeftCut`：开源仓库克隆，非你的作品
- `c:\project\Easel-live-*` / `Easel-merge-*` / `Easel-upstream-sync` / `easel-flow-desktop`：Easel 的工作副本，算 1 个项目
- `c:\project\athena*` / `zhishen*` / `backstageManageSystem` / `changeColor`：同一业务线前端族，见 `projects/family-and-copies.md`
- `_*` 下划线目录：一次性脚本、日志、归档

## 维护规则

- 新项目入库：在本文件加一行（本地路径 + git + 公开仓库 + 档案路径 + 关键文档 + 挖什么）
- 每季度核对：git commit 数、last 日期、公开仓库可达性
- 项目重构/迁移：同步更新路径
- 脱敏项目（recharge/AI-skills/Easel/qizhi/infringement）：在"挖什么"行加 ⚠️ 标注