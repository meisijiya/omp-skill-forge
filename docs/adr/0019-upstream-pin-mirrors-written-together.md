# ADR-0019: 上游 pin 的镜像同源维护，CI 无变更不开 PR

**Date**: 2026-11-12
**Status**: accepted
**Deciders**: 本 fork 维护者

## Context

定时任务 `.github/workflows/sync-upstream.yml` 连挂三周（2026-10-26 / 11-02 / 11-09），
从未开出过任何 PR。CI 日志把根因摊开了：`tools/sync_upstream.py` 推进 pin 时只写
`manifest/upstream.json` 与 `manifest/groups.json`，**不写 `NOTICE.md`**；而
`tools/check_upstream_pin.py` 的第 4 项要求 `NOTICE.md` 里恰好一个 40 位 sha 且等于 pin。
于是每次同步都必然把 pin 门禁打红——机制本身从建立起就没有跑通过一次。

同一处还带出两个连带问题：

- PR body 回报的是「解析出的目标 commit」，而内容判据下实际 pin 可能根本不动；
- 零差异时仍会调 `peter-evans/create-pull-request`，行为不可控（历史零 PR，无从验证）。

pin 是本仓唯一的跨文件事实源，它的镜像有三份：`manifest/upstream.json`（事实源）、
`manifest/groups.json`（upstream 镜像块）、`NOTICE.md`（署名文档里的 sha、版本与资产计数）。
三份里的后两份靠人手同步，漂移只是时间问题。

## Decision

1. **`tools/sync_upstream.py` 是 pin 的唯一写者，一次同步三处镜像**：事实源
   `manifest/upstream.json`、`manifest/groups.json` 的 upstream 块、`NOTICE.md` 顶部四行
   （上游版本 / commit / 资产计数）。NOTICE 的改写是定点替换，每个模式必须恰好命中一次，
   命中不到就非零退出——漏改一处就该让人看见，而不是安静地继续漂。
2. **pin 只在 `pool/` 内容变化时前进**（ADR-0017 判据的自动化实现）：刷新完 `pool/`
   后比摘要，与记录值相同就保持原 pin，`manifest/` 与 `NOTICE.md` 都不动；上游只改了
   CI、脚本、文档时，定时任务绿且不出 PR。
3. **pin 前进后台账必须重录**：台账记的是资产在 pin 提交下的 tree oid，pin 一动就过期。
   脚本在 pin 前进时打印重录命令，CI 在同步步骤之后按需跑
   `python tools/upstream_versions.py record --source ecc`，台账与 pin 在同一个 PR 里一起更新。
   离线台账门禁同时比对每个来源在台账里记录的 commit 与它当前的 pin，两者不一致即失败——
   「记得重录」由流程保证只是软约束，门禁才是硬约束。
4. **CI 用 `git status --porcelain` 判定是否真有改动**：无改动就跳过开 PR 的步骤，
   并在日志里说明「上游内容未变」；PR body 回报实际 pin、目标 commit 与「pin 是否移动」。

## Alternatives

- **让 `check_upstream_pin.py` 不再校验 NOTICE 的 sha**：NOTICE 是署名文档，sha 是溯源
  锚点，放弃校验等于放弃溯源。否决。
- **在 CI 里单独改写 NOTICE.md**：镜像继续靠人守，下次改 pin 的人不一定记得。否决。
- **每次同步都推进 pin**：哪怕内容没变也要改三处事实源，零内容收益还制造噪声 PR。否决。
- **零差异时照旧调 `peter-evans/create-pull-request`**，靠它自己判断该不该开 PR：该动作
  在空 diff 时的行为在本仓没有验证记录，用工作区状态判定更确定。否决。

## Consequences

- 定时任务在「上游内容没变」时绿且不开 PR；上游改了 `pi/core/` 或 `agents/` 时开 PR，
  PR 里带 `pool/`、pin 三处镜像与重录后的台账。
- 上游**新增或删除**资产时定时任务仍会红：`manifest/groups.json` 声明的成员必须与
  `pool/` 完全一致（ADR-0004），增删资产要人工补声明，脚本不替人做选择。
- 本地同步的行为与 CI 一致：本地跑 `python tools/sync_upstream.py` 同样只在内容变化时
  前进 pin，同样在 pin 前进时提示重录台账。
