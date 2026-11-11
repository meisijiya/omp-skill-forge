# ADR-0018: mcode-stack 审计结论——本轮不吸收，候选与前置条件留档

**Date**: 2026-11-11
**Status**: accepted
**Deciders**: 本 fork 维护者

## Context

`MiniMax-AI/mcode-stack`（MIT，MiniMax Code 团队）是四个「个人/团队真实工作流 stack」的集合：
`ronny`（19 条）、`jiachen`（7 条）、`req-tpm`（6 条）、`youfang`（1 条），共 33 条 skill。
按 ADR-0010 的口径逐条审了一遍，判据三条：

1. **是否独立**——只按名字提到兄弟 skill 可以，硬引用栈外的 `checklists/`、`templates/`、
   `ci/`、`private/` 或不在本仓的第三方 skill 则不能独立分发。
2. **是否有别的 harness 痕迹**——`MiniMax Code` / `mcode -p` 措辞、`.claude/`、`~/.codex/`、
   读宿主私有会话目录等。
3. **是否与本仓已有资产重复**——本仓已有的不只是 `absorbed/` 的 20 条，还有 ECC 上游
   134 条（其中 G9 一组 15 条 agent 相关 skill 只进 `full`）、本 fork 自有的 7 条，
   以及本机已启用的其它 omp 插件（`mattpocock-skills` 提供 `code-review`、`handoff`、
   `pr`、`retro`、`tdd`、`implement` 等）。

第 3 条权重最大：本仓的硬约束是「一 concern 一入口」（ADR-0008、ADR-0009），
重复条目不管来自哪个上游都不该进本仓。

另有两条与「吸不吸收」同等重要的环境事实：

- mcode-stack 本身已经是 omp 的 marketplace 源（`mcode-stack` 与用户自维护的
  `mcode-stack-meisijiya` 都在 `omp plugin marketplace list` 里），
  `omp plugin install ronny@mcode-stack` 可直接装。走插件路线拿到的就是上游形态：
  英文描述、`MiniMax Code` 措辞、5 条 skill 的清单引用指向栈根的 `checklists/`
  而不是技能目录。
- 用户自维护的 `meisijiya/mcode-stack` fork 里 `ronny` 停在 0.2.6，比上游 0.3.1 少
  4 条（`agent-brief`、`evidence-first-review`、`review-capacity-check`、`taste-to-checks`）。

## Decision

1. **本轮不吸收 mcode-stack 的任何资产。** 理由分两层：
   - **重叠的不能进**（ADR-0009 的硬约束）：
     `ronny/independent-review`、`ronny/engineering-code-review`、
     `ronny/engineering-review-comments` 与已启用的 `mattpocock-skills` 的 `code-review`
     同一 concern；`ronny/handoff-doc` 与 `handoff` 同一 concern；
     `ronny/engineering-change-descriptions` 与 ECC 上游 `conventional-commit-review`
     （本仓运行名 `forge-conventional-commit-review`）及 `mattpocock` 的 `pr` 同一 concern；
     `ronny/taste-to-checks` 与 ECC 上游 `correct`（本仓运行名 `forge-correct`）同一 concern；
     `jiachen/pr-description` 与 `mattpocock` 的 `pr` 同一 concern；
     `ronny/engineering-emergency-changes` 与本 fork 自有的 `forge-incident-response`
     同一 concern。
   - **不重叠的先不吸收**：`ronny` 的 6 条（`tool-budget-audit`、`context-tax-audit`、
     `long-session-check`、`long-command-check`、`trajectory-review`、
     `evidence-first-review`）确实本仓与已装插件都没有，值得收。但它们只能以
     `ronny@mcode-stack` 插件形态零成本拿到；为它们在 fork 里新增第四个收纳来源
     （新 pin、新逐文件摘要、新 `NOTICE.md` 段落、台账第四个来源），代价与收益不成比例。
     真要收，走 ADR-0010 的既有链路另开一轮。
2. **明确不吸收的**（不可独立分发或与本仓主题无关）：
   - `req-tpm` 全 6 条：硬引用栈根 `templates/meegle-field-mapping.md`、
     `templates/requirement-doc.md`，依赖不存在的 `meegle` skill 与 `mql-*` / `sop-*` 文档，
     还要求飞书文档 + Meegle 工作项互链。这是「一个人的需求管理台账」，不是可分发的 skill。
   - `jiachen/pr-review-ci`：依赖栈级 `ci/`（`ci/review.mjs`、`ci/config/repos/*.json`、
     `ci/github/mcode-review.yml`）与 `docs/pr-review.md`，跑不起来就不是 skill。
   - `jiachen/pr-review-tuning`：Node 工程 + GitHub/GitLab token + 模型预算的周更机器，
     正文还带 `Claude Code scheduled run`。
   - `jiachen/pr-quiz`：description 自明「仅当 MCode Review pipeline 要求时用」。
   - `jiachen/making-content`：硬依赖三个不在本仓的兄弟 skill
     （`lieflat-less-ai-tone`、`chinese-writing-style`、`humanizer`），
     并要 Volcengine key / ffmpeg / Playwright。
   - `jiachen/lifting-loops`：核心动作是扫 `~/.claude/CLAUDE.md`、`~/.codex/memories/`、
     claude.ai export 与 Obsidian vault——改造即失其价值。
   - `youfang/magic-move-deck`：2.5M 体量、幻灯片场景与本仓的工程/测试主题无关、
     frontmatter 带宿主专属 `license` / `compatibility` 键、还要 Playwright 与 ffmpeg 运行时。
3. **`ronny` 的 6 条 `engineering-*` 单独决策**：它们按 `ronny/NOTICE.md` 是
   **CC-BY 3.0**（改编自 Google Engineering Practices），不是 MIT；吸收要额外保留署名与
   改编说明，而现有收纳池三家都是 MIT。先把 MIT 的那 6 条落地，CC-BY 那批留到确有需求时
   单独决策，届时先更新 `NOTICE.md` 的第三方段落。
4. **若将来决定吸收上述 6 条候选**，前置条件已查明：
   - 5 条引用栈级 `checklists/*.md`（`tool-budget`、`context-tax`、`long-session`、
     `long-command`、`subagent-split`）——清单文件要随 skill 收进技能目录并改写引用，
     不能留悬空相对路径；
   - `evidence-first-review` 与 `review-capacity-check` 的 description 带
     `MiniMax Code session` 字样，改写时去掉宿主名与斜杠触发词；
   - 兄弟 skill 的裸名引用按 ADR-0002 的唯一判定改成 `skill://` 形式；
   - 走 ADR-0010 的既有链路：新来源 pin + 逐文件摘要 + `absorbed_fixups.py` 声明式规则
     + `NOTICE.md` 段落 + 台账来源 + 中文触发描述 + profile 分流。
5. **另记一条与本仓无关但对用户有用的观察**：`meisijiya/mcode-stack` 里 `ronny` 停在
   0.2.6，比上游 0.3.1 少 4 条 skill（`agent-brief`、`evidence-first-review`、
   `review-capacity-check`、`taste-to-checks`）。要跟上游就重新同步那个 fork，
   与本仓无关。

## Alternatives

- **整包吸收 `ronny`（19 条）**：省掉逐条判断，但把 6 条重复 concern 一起带进来，
  提示行多出六个入口，且其中 5 条的 `checklists/` 引用在插件布局下就是断的。否决。
- **把 6 条候选直接吸进本仓**：内容确实值得收，但它们已能以插件形态零成本获得；
  为此在 fork 里新增第四个收纳来源，收益不抵成本。等确有必要时再走既有链路。否决。
- **只靠 `omp plugin install ronny@mcode-stack`**：零维护成本，但拿到的就是上游形态——
  英文描述、`MiniMax Code` 措辞、5 条 skill 的清单引用指向栈根而非技能目录。
  本仓的价值恰是「改写后再接纳 + 中文触发描述 + profile 分流」，两条路径不是替代关系。否决。
- **把 `mattpocock-skills` 的能力也吸进本仓**：范围失控，且本机已装该插件，
  没有理由在 fork 里再养一份。否决。

## Consequences

- 收纳池维持 20 条，插件资产维持 90 个 skill（默认 profile `java-python`）、22 个 agent。
- 本仓与 mcode-stack 的边界有据可查：重叠的 6 组不收、不可分发的 11 条不收、
  值得收的 6 条候选与其前置条件留档在本 ADR。
- 若之后要把那 6 条候选吸进本仓，本 ADR 的第 4 条即是实施清单；
  若改从插件路线拿，本仓无需改动，但那 6 条会以英文描述与上游形态进入提示行。
