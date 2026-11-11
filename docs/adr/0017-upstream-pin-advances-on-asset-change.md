# ADR-0017: 上游 pin 只在资产内容有变化时推进

**Date**: 2026-11-11
**Status**: accepted
**Deciders**: 本 fork 维护者

## Context

例行维护要回答一个问题：上游动了什么，本仓哪些 skill 需要跟上更新。四个来源各有不同的
「动了」形态：

- **ECC（主池）**：HEAD 前进 27 个提交，但 `pi/core/skills`、`pi/core/commands`、`agents`
  三个 tree oid 与当前 pin 完全一致——改动全在 CI、lib、hooks 上，不进物化产物。
- **pstack**：`skills/statechart/` 的三个脚本变了（Windows CRLF 处理、win32 用 `taskkill`
  杀进程组、janitor 清理），`principle-*` 未变。
- **qa-skills**：8 条 skill 正文更新，`core` 新增 `scripts/case_lint.py` 与
  `scripts/report_meta_check.py`、`scripts/validate_schema.py` 重写，并新增一条 skill
  `ai-system-testing`（测 AI 功能的不确定性、评测集设计、judge 校准）。
- **addyosmani**：HEAD 前进，但唯一收录资产的 tree oid 未变。

「有提交就推进 pin」会把无关改动带进来：ECC 侧要改 `manifest/upstream.json`、
`manifest/groups.json`、`NOTICE.md`（只允许一个 40 位 sha）与 `manifest/asset_versions.json`
四处，pool 内容却一字节不变。反过来，「内容没变就不动 pin」也要有明确判据，
否则每次维护都在同一件事上摇摆。

## Decision

1. **pin 的推进判据是物化产物，不是提交数**：来源的「资产 tree oid 集合」发生变化才推进
   pin；只有 CI、脚本、文档等不进物化产物的改动，一律不动。
   - 本轮据此：ECC **不推进**（三个 tree oid 未变），addyosmani **不推进**（收录资产
     tree oid 未变），pstack 与 qa-skills **推进**。
2. **推进 pin 走既有链路，不手工改文件**：改 `manifest/absorbed.json` 的 `commit` 后跑
   `python tools/sync_absorbed.py`（拉取 → 重放 `tools/absorbed_fixups.py` 的声明式规则 →
   刷逐文件摘要 → 重新生成 bundle），再跑 `python tools/upstream_versions.py record`
   刷新 `manifest/asset_versions.json` 的内容指纹。规则命中数与声明值不符即失败，
   不静默通过。
3. **上游新增的 skill 随源整体接纳**：qa-skills 上游新增 `ai-system-testing` 后，
   `qa/SKILL.md`、`core/SKILL.md` 与 `core/test-type-matrix.md` 都引用它。不接纳就得
   另写规则把上游引用删掉，那属于静默丢内容。所以它进收纳池，进 `full` 与 `java-python`
   profile，与 QA 套件其余成员同待遇（ADR-0014 的「整套收纳」）。
4. **新成员需要自己的触发描述**：按 ADR-0011 补 `manifest/skill_descriptions.zh.json`
   条目，两句、中文触发词，门禁 `tools/check_zh_descriptions.py` 验收。

## Alternatives

- **所有来源一律推进到 HEAD**：统一做法，但 ECC 侧零内容收益却要动四处事实源，
  且 `NOTICE.md` 的 sha 引用要跟着改，徒增漂移面。否决。
- **qa-skills 新增 skill 不接纳，另写规则删掉上游引用**：保住收纳条数不变，但等于在
  本仓制造一份与上游不一致的 QA 套件，正文里的引用被裁掉后读起来是断的。否决。
- **把 `ai-system-testing` 也放进 `lite`**：lite 的定位是每轮提示开销最低的档，
  QA 套件整批不进；单条破例会让 lite 的口径不再一致。否决。

## Consequences

- pstack 的 `forge-statechart` 在 Windows 上可用：脚本按 CRLF 切行、用 `taskkill` 杀
  进程组，不再依赖 `/bin/sh`。
- 收纳池从 19 条变 20 条，`full` 物化 155 个 skill、`java-python` 90 个。
- 规则命中数是「上游写法」的断言：qa-skills 改写 `../core/` 的写法会直接让
  `sync_absorbed.py` 失败，需要先改规则再重放，不会带着半适配的文本进运行树。
