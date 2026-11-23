# 2026-11-23 · 第一轮 A/B 基线

**结果：A 与 B 各 9/9，没有观察到核实准确性的提升。** 新版在这批用例中没有新增关键误判。不要把它当作跨 Agent 兼容性或开源工具排位。

- A：不加载本 Skill；B：显式读取本版 `SKILL.md`，Git blob `9fdfd5948213b9ee0aab09001dc72806432cbaf6`。三个用例各条件独立运行一次，六个新 Codex 子会话沿用同一父会话模型设置，未记录模型快照 ID。工作目录使用中性编号，运行顺序为第 1 题 A/B、第 2 题 B/A、第 3 题 A/B（启动顺序，执行有重叠）。
- 固定每题相同的合成输入和任务；题目列出待核实的主张，但不给预期结论。使用同样的只读任务范围（不是 OS 沙箱）；不连接真实项目、CI 或模型业务接口。评分只算预设结论、引用及基本输出，结合 [评判标准](../../cases.json) 人工核对证据含义。

| 用例 | A（无 Skill） | B（有 Skill） | 关键观察 |
| --- | --- | --- | --- |
| 当前实现与旧档案 | [3/3](standalone-stale-A.json) | [3/3](standalone-stale-B.json) | 两组都从当前源码确认「返回待确认、没有自动重发」，没有拿旧档案证明生产验证。B 把纸上推演具体化为可运行的替身练习。 |
| CI 配置不是验收 | [3/3](ci-is-not-a-run-A.json) | [3/3](ci-is-not-a-run-B.json) | 两组都区分了 CI 配置、实际通过和部署验收。 |
| 个人归属与范围 | [3/3](mapped-ownership-and-scope-A.json) | [3/3](mapped-ownership-and-scope-B.json) | 两组都识别了顺序通过记录，没冒认并发通过或独立交付。核对这两组读取轨迹，均未打开 `restricted/`。 |

另做一次不计入 A/B 的自由输出验证：只给 [Parcel Notes 档案](../../../assets/demo/parcel-notes.md)，不填地图、不指定输出格式。B 直接给了个人复盘：只确认设计评阅，不声称实现、部署或个人职责；给出两笔预约冲突的失败场景，以及「恰好一条确认，另一条重新选时段」的通过条件。没有生成简历，没有执行所提实验。

## 复算

在仓库根目录执行，例如：

```text
python -B evals/check.py score standalone-stale evals/results/2026-11-23/standalone-stale-A.json evals/results/2026-11-23/standalone-stale-B.json
```

其他两个用例替换用例名及对应文件名。JSON 保留实际回答内容，仅整理了排版。本轮基线已经全对；下次要测差异，优先换成**不给主张清单、证据散在若干不同版本和位置**的开放复盘题，不加更多同难度小题。
