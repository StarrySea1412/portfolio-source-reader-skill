# portfolio-source-reader

从本地仓库、GitHub/Gitee 和历史项目档案中采集经历素材，保留来源、版本、数字口径与个人贡献依据。输出可用于简历选材、项目复盘和面试准备。

## 能解决什么

- 多处项目资料：先定位实际来源，再针对目标问题回查。
- 历史数字过期：记录快照与口径，保留历史结果和当前核查的区别。
- 项目功能与个人贡献混在一起：按具体改动核对本人、团队、上游和 AI 参与。
- “验证通过”含义模糊：写明静态核查、测试、模拟、浏览器、部署或业务验收的实际范围。

单个项目也可以使用。素材准备好后，可以交给用户选定的简历排版或文档工具；本 skill 的交付重点是内容及依据。

## 安装

安装到所用 agent 的 skills 目录，目录名使用 `portfolio-source-reader`。以 Codex 常用的本地目录为例：

```bash
git clone https://github.com/StarrySea1412/portfolio-source-reader-skill.git ~/.codex/skills/portfolio-source-reader
```

PowerShell：

```powershell
git clone https://github.com/StarrySea1412/portfolio-source-reader-skill.git "$env:USERPROFILE/.codex/skills/portfolio-source-reader"
```

Linux 或 Git Bash 下，已有源码副本时，也可从任意工作目录运行 `bash /path/to/install.sh <skills目录>`；例如指定 `~/.codex/skills`。安装器从自身目录取完整运行时包，现有目标默认保留；默认 `~/.zcode/skills` 作为旧入口兼容。README、验收记录和测试留在源码仓库。

也可以把完整 skill 目录放入项目，让 agent 按 [SKILL.md](SKILL.md) 工作。保留 references、assets 和 scripts 的相对目录。

## 使用

可以直接给路径和问题：

> 按 portfolio-source-reader，分析这个项目的并发保存修复。只看这个项目，给面试讲述和证据附注。

也可以给目标方向：

> 用我仓库里的 SOURCES.md，为 Python 后端岗位选材。优先挑能讲清本人改动和验证结果的项目。

有地图就沿入口采集；没有地图先从已授权目录发现信息，只询问影响定位或表述的缺口。需要长期维护时，再用 [地图模板](references/sources-map-template.md) 保存实际入口。[虚构示例地图](assets/sources-map.example.md) 展示填法。

可选的只读发现助手需要 Python 3.10+，只依赖标准库；git 可用时会补充本地仓库元数据：

```text
python scripts/discover_sources.py --root <项目路径> --format json
python scripts/discover_sources.py --root <多个项目的父目录> --scan-children --max-repos 40 --format markdown
```

默认检查一个目录；批量只看直属目录并设上限。助手读取入口与 git 元数据，输出待核查草稿；它不判断仓库公开性、个人责任或测试结果。没有 Python 时，agent 也可直接按采集协议工作。

## 输出带什么

正文按需要采用 [简历、档案或面试格式](references/star-template.md)。重要结论保留一张简短证据卡：

```text
主张与状态 → 来源 → 版本/日期 → 口径/条件 → 验证 → 本人贡献 → 未覆盖与披露
```

例如源码可以支持同一跳板、N 台目标主机的握手操作次数推导；没有延迟基准时，素材就停在这个结论。[示例](references/examples.md) 展示了这种边界，也说明如何处理只有历史档案或 fork 的情况。

## 文件

- [SKILL.md](SKILL.md)：agent 入口与采集流程。
- [证据规则](references/evidence-rules.md)：材料强度、数字口径、责任与冲突处理。
- [STAR 模板](references/star-template.md)：三种交付格式及证据卡。
- [地图模板](references/sources-map-template.md) 与 [示例地图](assets/sources-map.example.md)：首次建图和迁移入口。
- [示例](references/examples.md)：有证据的表述与缺口处理。
- [发现助手](scripts/discover_sources.py)：可选的本地只读定位。

## 验证

```text
python -m unittest discover -s tests -v
```

发现与安装测试使用隔离临时目录，检查读取范围、源项目不被修改、git 状态与 remote 脱敏，以及安装完整性与已有目标不被覆盖。行为验证另用真实请求检查素材是否保留证据和贡献边界；具体记录见 [本次验收](ACCEPTANCE.md)。

## License

[MIT](LICENSE)
