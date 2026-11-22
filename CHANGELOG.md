# 变更记录

本文件记录本插件的对外变更，格式按 Keep-a-Changelog，版本号遵循 SemVer。
版本号记在 `package.json` 的 `version`，发布 tag 一律用 `v<semver>`。

## [0.7.1] - 2026-11-22

### Fixed

- **ADR-0020 补记与既有约束的冲突**：写清「两条并存」是用户拍板的暂时悬置，范围限在
  `full` profile（默认 profile 里 ECC 版仍是唯一入口，双入口不进每轮提示），并写明
  逐栈对照表定案后的两条收尾路径；同时记下本仓首个非 MIT 收纳来源的许可做法与
  「`youlai-skills` 不是 marketplace 源、没有插件形态替代路线」两条前提。
- **选路表表头订正**：`forge-router` 的「补缺（收纳资产）」原写「上游 ECC 与 mattpocock
  都没有对应条目」，但新增三行里 `forge-doc-standard` 与 `forge-git-version` 在 ECC 有
  邻近条目；改为「大多没有」，并注明与 `forge-docs-governance`、`forge-git-workflow`
  的分工。

## [0.7.0] - 2026-11-22

### Added

- **收纳 youlaitech/youlai-skills 的 15 条 skill**：pin 到 `3825a481f1f6`，新增
  `forge-spring-boot`、`forge-django`、`forge-fastapi`、`forge-nestjs`、`forge-gin`、
  `forge-rust`、`forge-laravel`、`forge-aspnet`、`forge-thinkphp`、`forge-uniapp`、
  `forge-vue3-element-admin`、`forge-mysql-design`、`forge-doc-standard`、
  `forge-blog-writing`、`forge-git-version`。上游正文没有 harness 残留，只有两处 HTTP 路由
  写成了斜杠命令的形状（NestJS 的 `/page`、Element Plus 的 `/redirect`），加两条声明式
  规则改写成中文说法；其余正文与上游逐字节一致，只有 frontmatter 的 `name` 换成运行名。
  许可按同组织其它仓库一致的 Apache-2.0 认定（该仓库自身没有 LICENSE 文件，
  依据写进 [ADR-0020](docs/adr/0020-youlai-skills-absorption.md) 与 `NOTICE.md`）。
  `full` 收全部 15 条，`java-python` 只收与主力栈无关的 `doc-standard`、`blog-writing`、
  `git-version`，`lite` 一条不收。
- **许可门禁支持多许可族**：`tools/check_absorbed.py` 不再只认 MIT，按来源声明的
  `spdx` 校验——MIT 要许可文本与版权行都在文本里，Apache-2.0 要许可文本随内容走、
  版权行在 `NOTICE.md`；未声明 `spdx` 的来源仍按 MIT 处理。
- **上游 ECC 新增 4 条 skill 与 1 个 agent**：pin 前进到 `4adeee6732a1`，上游新增
  `godot-patterns`、`godot-testing`（Godot 4 / GDScript）、`rails-security`（Rails 7.1+ 安全）
  与 `yoruba-localization-testing`（约鲁巴语—英语双语界面测试），新增 agent `gdscript-reviewer`。
  新增分组 `G11`「游戏开发 / Godot（GDScript）」，只进 `full`；`rails-security` 进 `G5`
  （与 `rails-patterns` 同组）、`yoruba-localization-testing` 进 `G9`（与 `bengali-nlp` 同组），
  `gdscript-reviewer` 进 `A6`。`java-python` 排除 `rails-security`（与既有 `rails-patterns`
  一致），`lite` 不变。
- 收纳池 pin 前进：pstack → `c3464c11c60b`（`sharpen` 与 `statechart` 正文修正，
  `statechart` 脚本新增 `janitor.ts` 与 `kill.ts`），addyosmani → `8c99fa36d900`
  （`constraint-driven-development` 的 dependency-cruiser 命令修正）。

### Changed

- 收纳池从 20 条变 35 条。`full` 物化后 155 → 174 个 skill（133 上游 + 34 收纳 + 7 自有），
  49 → 50 个 agent；`java-python` 90 → 93 个 skill（65 上游 + 21 收纳 + 7 自有）；
  `lite` 仍 46 + 11。
- `full` 的提示行开销：描述 4,904 → 5,489 token，名称 1,003 → 1,092 token，合计约 6.6K；
  `java-python` 合计约 3.5K。
- README 的规模表、token 表、`pool/` 快照计数（138 skills / 72 agents）与
  `own/skills/` 行数（7 条）同步订正。

## [0.6.0] - 2026-11-13

### Added

- **每轮维护推送后发一个版本**：新增 `tools/release.py`（发版前检查工作区干净、`package.json`
  的版本号、`CHANGELOG.md` 的版本段落、tag 未被用过，然后打 annotated tag）与
  `README.md` → 「版本与发布」；版本号按 SemVer 判级别，tag 是单向门。
- **`upstream_versions.py diff`**：按上游自己的目录树对比两个提交之间**新增、删除、内容变了**
  的资产——`check` 只能报已声明资产的漂移，上游新增的资产不在本 fork 清单里，那正是例行维护
  要先知道的事。`--since` / `--to` 指定两端，`--offline` 不联网。
- **收纳 qa-skills 的 `ai-system-testing`**：测 AI 功能的不确定性风险、评测集与 rubric 设计、
  容错断言、judge 校准与注入面移交，进 `full` 与 `java-python` profile。
  上游 qa-skills 新增这条后 `qa`、`core`、`core/test-type-matrix` 都引用它，随源整体接纳。
- **收纳池 pin 前进**：pstack → `0854796`（`forge-statechart` 的脚本改用 CRLF 安全的切行与
  win32 `taskkill`），qa-skills → `5053e04`（8 条 skill 正文更新，`core` 新增
  `scripts/case_lint.py` 与 `scripts/report_meta_check.py`）。
- **上游 pin 只在资产内容有变化时推进**（[ADR-0017](docs/adr/0017-upstream-pin-advances-on-asset-change.md)）：
  ECC 与 addyosmani 的资产 tree oid 未变，本轮不动 pin。

### Changed

- 收纳池从 19 条变 20 条；默认 profile `java-python` 89 → 90 个 skill（65 上游 + 18 收纳 +
  7 自有），`full` 154 → 155。描述 token 约 2.9K，名称 token 约 0.5K。
- **上游 pin 门禁加第 5 项**：`tools/check_upstream_pin.py` 现在校验 `NOTICE.md` 的上游版本
  等于 pin 的版本、资产计数等于 `pool/` 实况，手改 NOTICE 会被打出来。
- `AGENTS.md` 的门禁说明订正：七条命令里六条在 CI 跑，第七条（插件启停隔离）只在本地跑。

### Fixed

- **上游同步的定时任务恢复可用**：`.github/workflows/sync-upstream.yml` 连挂三周且从未开过
  PR——`tools/sync_upstream.py` 推进 pin 时没有同步 `NOTICE.md`，而 pin 门禁要求 `NOTICE.md`
  引用的 sha 等于 pin。现在 pin 由脚本一次写三处镜像（`manifest/upstream.json`、
  `manifest/groups.json`、`NOTICE.md`），且只在 `pool/` 内容变化时前进；CI 无变更时不再开 PR，
  pin 前进后自动重录资产台账。详见
  [ADR-0019](docs/adr/0019-upstream-pin-mirrors-written-together.md)。
- **台账与 pin 的一致性进门禁**：`tools/upstream_versions.py check --offline` 现在比对每个
  来源在 `manifest/asset_versions.json` 里记录的 commit 与它当前的 pin，不一致即失败并提示
  重录——pin 前进后忘记 `record` 不再能悄悄溜过去。
- **上游没有 VERSION 文件时三处镜像不再各说各话**：pin 推进时版本沿用已记录的值，
  `NOTICE.md` 不再被写成「上游版本：unknown」，与 `manifest/groups.json` 的处理一致。
- **ADR-0014 的命中数补修订说明**：该文记录的是 2026-11-03 的数字（命中数 5 / 141 / 19 / 13、
  146 处引用、收纳 19 条），上游前进后已过时，文中加了一节列出现状与真源。
- **QA 套件里的执行指令不再被改成只读 URI**：上游 qa-skills 自 `5053e04` 起有 10 处不带解释器的
  脚本路径（`` `../core/scripts/x.py` ``），它们是「运行 … 无错误（退出码 0）」这类执行指令，
  却被通用 `../core/` 规则改写成了 `skill://forge-core/scripts/x.py`——URI 跑不了。新增一条整源
  规则，裸路径改写成可执行占位 `python3 <forge-core-skill>/scripts/x.py`，涉及 `qa`、
  `test-case-review`、`test-case-writing` 三条 skill 与 `core` 的两份说明。
- **上游 pin 的三处镜像改成先算后写**：`sync_upstream.py` 先算出三份新文本并全部通过模式校验，
  再统一落盘。此前 `NOTICE.md` 的校验失败会留下 `manifest/upstream.json` 与 `manifest/groups.json`
  已改写、`NOTICE.md` 仍旧值的半写状态，与 ADR-0004「脚本报错即不产生半写状态」相反。

## [0.5.0] - 2026-11-03

### Breaking

- **运行名与安装根改名**：skill / agent 运行名从 `ecc-omp-*` 改为 `forge-*`，插件 id 与安装根
  从 `ecc-omp-fork` 改为 `omp-skill-forge`（`~/.omp/agent/local/omp-skill-forge`）。
  旧名的资产不再存在，旧安装需要 `omp plugin uninstall ecc-omp-fork` 后重装。
  详见 [ADR-0013](docs/adr/0013-repository-renamed-to-omp-skill-forge.md)。
- **GitHub 仓库改名**：`meisijiya/ecc-omp-fork` → `meisijiya/omp-skill-forge`（旧地址会自动跳转）。
- **TypeScript 入口去重**：收纳池里的 `forge-typescript-best-practices` 不再物化，
  TypeScript 写法改由上游的 `forge-typescript-patterns` 承担。

### Added

- **qa-skills 全套收纳**：13 条 QA skill（含共享知识库 `forge-core`）进收纳池，
  进 `full` 与 `java-python` profile。覆盖需求分析、测试策略、用例写作与评审、探索式测试、
  端到端与接口测试执行、Bug 根因、回归范围、flaky 治理、跨会话质量知识库。
  详见 [ADR-0014](docs/adr/0014-qa-skills-absorption.md)。
- **逐资产上游版本台账**：`tools/upstream_versions.py` 与 `manifest/asset_versions.json`，
  按 git tree oid 记 4 个来源 224 个资产的内容指纹（ECC 205 / pstack 5 / qa-skills 13 /
  addyosmani 1），`check` 报漂移、`check --offline`
  校验覆盖并接入 CI。详见 [ADR-0015](docs/adr/0015-per-asset-upstream-version-ledger.md)。
- **插件自己的运维 skill**：`forge-pipeline`（更新与发布流水线）、`forge-ci-triage`
  （CI 失败定位）、`forge-absorb-third-party-skill`（收纳第三方 skill），随插件分发。
- **收纳池的整源批量改写规则**：`absorbed_fixups.py` 新增 `SOURCE_RULES`，每条带期望命中
  总数，上游改了写法而规则没跟上时同步直接失败。

### Changed

- **上游 pin 前进**：`90606c8` → `b38be6a`，pool 随之刷新（134 skills / 24 commands /
  71 agents），新增上游 skill `typescript-patterns` 与 `module-governance` 已分类进 group。
- **提示行规模**（默认 profile `java-python`）：73 → 89 个 skill；`full` 137 → 154；
  `lite` 43 → 46。描述 token 约 2.8K，名称 token 约 0.5K。
- **中文触发描述**扩到 153 条 skill 与 71 条 agent。

### Fixed

- **收纳 skill 的内容不再被静默丢弃**：`refscan.source_exists()` 补上 `absorbed/` 探测，
  物化期出现 drop 动作直接失败。修复了 `forge-constraint-driven-development` 丢失
  「Loading Constraints」整节与阶段表命令列、`forge-typescript-best-practices` 误判工具名
  等问题。
- **上游示例里的宿主命令行改写**：`claude -p --allowedTools --dangerously-skip-permissions`
  改成 omp 的 `omp -p --tools= --auto-approve`。

## [0.4.0] - 2026-11-02

- agent 的提示行描述全量改成中文，与 skill 侧复用同一张描述表机制。

## [0.3.0] - 2026-11-01

- 新增发布 / 可观测性 / 事故响应三条运维 skill；引入收纳资产池（6 条第三方补缺 skill）。
