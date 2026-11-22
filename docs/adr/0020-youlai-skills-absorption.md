# ADR-0020: 以收纳池纳入 youlaitech/youlai-skills，许可按同组织的 Apache-2.0 认定

**Date**: 2026-11-22
**Status**: accepted
**Deciders**: 本 fork 维护者

## Context

`youlaitech/youlai-skills` 是「有来」项目家族（`youlai-boot`、`youlai-django`、
`youlai-fastapi`、`youlai-gin`、`youlai-laravel`、`youlai-nest`、`youlai-think`、
`youlai-axum`、`youlai-aspnet`、`vue3-element-admin`、`vue-uniapp-template`）沉淀出来的
15 条 skill：Spring Boot、Django、FastAPI、NestJS、Gin、Rust、Laravel、ASP.NET、
ThinkPHP、uni-app、Vue 3 + Element Plus 管理后台、MySQL 表设计、项目文档规范、
中文技术博客写作、提交与版本。

它的写法与本 fork 的取向一致：先读仓库再动手、约定与框架机制分开写、正文短、
细节按任务放进 `references/`，而且**没有**别的 harness 残留——没有斜杠触发词、
没有 `CLAUDE.md`、没有兄弟 skill 硬引用、没有宿主专用的 frontmatter 键。

三件事要拍板：

1. **许可**：该仓库本身**没有随附任何 LICENSE 文件**，GitHub 页面也没有许可声明。
   同组织的其它仓库（`youlai-cloud`、`youlai-boot`、`youlai-django` 等）都是
   Apache-2.0，且这些 skill 就是那些项目的实现规范。
2. **重叠**：15 条里 9 条与本 fork 已有资产同一技术栈（`spring-boot` 对
   `forge-springboot-*`、`django` 对 `forge-django-*`、`fastapi` 对
   `forge-fastapi-patterns`、`nestjs` 对 `forge-nestjs-patterns`、`rust` 对
   `forge-rust-*`、`gin` 对 `forge-golang-*`、`mysql-design` 对 `forge-mysql-patterns`、
   `laravel` 对 `forge-laravel-*`、`aspnet` 对 `forge-dotnet-patterns`）。
   ECC 那些是通用模式，youlai 这些是「有来」参考实现的项目约定（`sys_` / `biz_` 前缀、
   固定目录树、`Form` / `Query` / `DTO` / `VO` 分层）。
3. **同名不同物**：收纳的运行名是 `forge-django`、`forge-fastapi` 这类短名，与上游
   ECC 的 `forge-django-patterns` 并不重名，但描述里说的是同一件事。

## Decision

1. **15 条整套收纳**，pin 到 `3825a481f1f6`（仓库当前 HEAD）。重叠的 9 条也收，
   与 ECC 版并存；「同一技术栈留哪一套」按技术栈逐条另议，不在收纳这一步决定。
2. **许可按 Apache-2.0 认定**：
   - `manifest/absorbed.json` 的来源条目写 `"spdx": "Apache-2.0"` 与
     `Copyright (c) 2026 youlaitech`；
   - 许可正文随内容走：`absorbed/youlai/LICENSE`（取自同组织 `youlai-cloud` 的
     Apache-2.0 全文），`NOTICE.md` 附同一份全文与版权声明，并按 §4(b) 写明改动
     （改名、描述替换、profile 分流，正文未删改）；
   - `tools/check_absorbed.py` 的许可门禁从「只认 MIT」改成按来源声明的许可族校验：
     MIT 要求许可文本与版权行都在许可文本里，Apache-2.0 要求许可文本在
     `absorbed/<source>/LICENSE`、版权行在 `NOTICE.md`。未声明 `spdx` 的来源按 MIT 处理，
     既有三个来源不受影响。
   - **这是推断，不是上游声明**：`youlai-skills` 仓库本身没有许可文件。上游若补上
   其它许可或提出异议，按 pin 移除这 15 条即可，机制已经就位（`manifest/absorbed.json`
   删条目 + `sync_absorbed.py` 重放 + 门禁）。
3. **只改两处**：上游正文本来就没有需要改的东西，收纳副本与上游逐字节一致，只有
   frontmatter 的 `name` 被改成运行名（`forge-spring-boot` 等）。例外是两处 HTTP 路由
   写成了斜杠命令的形状（NestJS 的 `` `/page` ``、Element Plus 的 `` `/redirect` ``），
   本 fork 不发布命令（ADR-0008），不改会被物化器当成悬空引用整行删掉——两条声明式
   规则把它们改写成中文说法（`tools/absorbed_fixups.py`）。
4. **profile 分流**：`full` 收全部 15 条；`java-python` 只收与 Java/Python 主力栈无关的
   三条通用条目 `doc-standard`、`blog-writing`、`git-version`；`lite` 一条不收。
   与技术栈重叠的 9 条先留在 `full`，等逐栈对照表定案后再决定是否进 `java-python`。
5. **保留 ECC 版**：本轮不淘汰任何现有 `forge-` skill。ECC 版是通用模式，youlai 版是
   一套具体项目约定，两者的适用面不同；淘汰属于「同一件事只留一个入口」的判断，
   要拿逐栈对照表说话，不能顺手删。
6. **与既有约束的冲突及解决路径**：
   - **ADR-0008 / ADR-0009 的「一 concern 一入口」**：那两条约束的是「与本机其它插件
     提供的同名能力重复」，而本轮是**本仓内部**两条资产指向同一技术栈，形态更接近
     ADR-0016 的去重决定。用户 2026-11-22 明确拍板「两条并存，靠描述与 profile 分流
     区分」，等于暂时悬置这条约束。悬置的范围被 profile 限住：9 条重叠项**只进 `full`**，
     默认 profile（`java-python`）里 ECC 版仍然是唯一入口，双入口不进入每轮提示。
     解决路径：逐栈对照表定案后，要么从 `full` 去掉 ECC 对应条目，要么把 youlai 对应项
     从 `full` 去掉，恢复一 concern 一入口；在那之前，`full` profile 的双入口是已知
     的待清理状态，不是遗漏。
   - **ADR-0018 的许可前提**：该文预料过「非 MIT 来源要额外保留署名与改编说明」，本轮
     是本仓第一个非 MIT 收纳来源（Apache-2.0），做法是 §4(b) 的改动声明 + 许可全文
     随内容走 + 门禁按 `spdx` 分类。
   - **ADR-0018 的「插件形态零成本」替代路线**：`youlai-skills` 不是 omp marketplace
     源，没有「让用户装插件、本仓只做去重」的省事办法，只能走收纳池。

## Alternatives

- **不纳入**：保住「只有 MIT 来源」的整齐，但丢掉 15 条高质量的栈覆盖，其中
  ThinkPHP、uni-app、Element Plus 管理后台、中文博客写作本 fork 完全没有。
- **只收 6 条无重叠的**：提示行更省，但用户明确要整套收；重叠与否本就该按栈讨论，
  不该在收纳阶段替用户裁掉。
- **等上游补 LICENSE 再收**：最保守，但本轮没有可推进的动作，用户选择按同组织的
  Apache-2.0 推进并把依据写进 NOTICE，风险由上面的移除路径兜底。

## Consequences

- 收纳池从 20 条涨到 35 条；`full` 物化后 159 → 174 个 skill（提示行约 +0.6K token），
  `java-python` 90 → 93 个（约 +0.1K token）。
- `manifest/absorbed.json` 的 `skills` 从 20 条变 35 条，逐资产台账从 4 个来源 230 条
  变 5 个来源 245 条；上游维护面多一个来源（一条 pin、一次 `sync_absorbed.py`）。
- 许可门禁多一条分支（按来源声明的许可族），既有三个 MIT 来源的判定不变。
- 收进来的 9 条重叠 skill 在 `full` profile 里会与 ECC 版同时出现，两套描述都在提示行里，
  模型可能挑错——逐栈对照表定案后要在 `java-python` 侧分流或收窄。
