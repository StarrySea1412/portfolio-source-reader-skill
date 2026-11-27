# portfolio-source-reader

从本地仓库、GitHub/Gitee 和项目档案提取可核对的个人贡献、技术栈和成果。用于更新投递简历、写项目档案或准备面试。

## 使用

给 agent 一份现稿、项目目录或来源链接，有目标岗位描述也可以一起提供。多项目可用 `SOURCES.md` 持续维护来源，参考 [地图模板](references/sources-map-template.md) 与 [合成示例](assets/sources-map.example.md)。

- 「按这个 Python 后端 JD 优化我的简历，保留实习经历，用仓库实测成果写清认证和支付项目。」
- 「根据这份项目档案，回查我改过的模块和验证记录，写一段面试案例。」

简历模式先核对工作和项目归属，把和目标岗位相关的技术栈放到容易找到的位置，再用 STAR 写清业务问题、本人动作和结果。AI 项目与有据可查的常规后端、前端或业务交付一起纳入选材。数字附样本和验证环境，正式任职缺口单独提示。

阅读 [skill 入口](SKILL.md)、[STAR 模板](references/star-template.md) 和 [合成样例](references/examples.md) 了解规则与输出格式。

## 安装

克隆到当前 agent 的 skills 目录。以下为 Codex 示例。

```bash
git clone https://github.com/StarrySea1412/portfolio-source-reader-skill.git ~/.codex/skills/portfolio-source-reader
```

也可以在仓库根目录运行 `bash install.sh <skills-dir>`。已经通过 Git 克隆的安装可在对应目录内执行 `git pull --ff-only` 更新。

## License

MIT
