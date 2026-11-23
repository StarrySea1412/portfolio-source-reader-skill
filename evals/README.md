# 评测：用 Skill 是否更会核实？

只用本目录的合成资料，不读取真实简历、公司项目或运行环境。目标是区分**检查器能工作**和**模型用了 Skill 真的更准**：前者可离线测，后者必须有实际的模型输出作证。

| 用例 | 检查的判断 |
| --- | --- |
| `standalone-stale` | 没有地图也能开始；当前实现与旧档案分开；旧文档的上线说法没有实测证据。 |
| `ci-is-not-a-run` | 配了 CI、写了用例、CI 跑过、已上线，是不同结论。 |
| `mapped-ownership-and-scope` | 找到正确的本地记录；顺序检查不外推到并发；不猜个人归属、不读出界资料。 |

## 运行一次 A/B

需要 Python 3.10+（仅标准库），以及你已有的 Agent 或模型会话。下面以一个用例为例；其余两个替换用例名和输出目录。Windows 若没有 `python` 命令，可用 `py -3`。

1. 在本仓库运行 `python -B evals/check.py prepare standalone-stale ../eval-standalone-stale`。目标目录必须尚不存在，且位于 Skill 仓库外。脚本只复制输入：`A/` 无 Skill，`B/` 带本版 Skill，两边的 `input/` 字节相同。
2. 用两个新会话，分别以 `A/`、`B/` 为只读工作范围，提交其中的 `prompt.md` 内容。固定模型、推理设置和工具权限；A 不加载全局已安装的本 Skill，B 显式读 `skill/SKILL.md`。**不要给任一组评判标准或另一组输出**；没有真实隔离时至少检查工具读取记录，不把同一对话的两次问答当作对照。不许可联网、执行 fixture 或写项目文件。
3. 把两个回答的纯 JSON 分别保存为 `answer.json`，然后回到本仓库运行：

   ```text
   python -B evals/check.py score standalone-stale ../eval-standalone-stale/A/answer.json ../eval-standalone-stale/B/answer.json
   ```

4. 对照 [`cases.json`](cases.json) 的 `review` 和 `exercise_review` 人工核对。脚本检查结论标签、可解析的引用路径/行号和指定的泄露标记，**不证明引用段落真的支持结论，也不能靠输出证明没有打开过越界文件**。核对正文、读取轨迹和练习的通过条件，补记错误。命令退出成功只表示生成了计分报告。

## 如何判定

每组记录模型/版本、运行顺序、所用 Skill 的提交、得分、关键误判和人工复核结果。B 要过基础门槛：三个用例的结论与出处能核对，且没有把未证实的验证/归属写成事实、没有打开越界资料。**只有实测 B 减少了 A 的错误，才记录这批用例上的收益；A 和 B 一样好时就写「没观察到提升」**。小样本不证明通用兼容或比其他开源项目好。

已跑结果：[2026-11-23 首轮对照与原始回答](results/2026-11-23/README.md)。

离线自检（验证的是评测工具）：

```text
python -B -m unittest discover -s evals -p 'test_*.py' -v
```
