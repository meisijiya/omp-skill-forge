# NOTICE

本仓库是 [Everything Claude Code (ECC)](https://github.com/affaan-m/ECC) 的派生作品。

- 上游许可：MIT，版权归 Affaan Mustafa（完整文本见 `LICENSE`）。
- 上游版本：2.2.3
- 上游 commit：`4adeee6732a12d1540f49a4d50a38ce8c97f9a53`（与 `manifest/upstream.json` 的 pin 一致）
- 上游内容来源：仓库的 `pi/core/`（138 skills + 24 commands，官方为 Pi 生态生成的精简档）
  与 `agents/`（72 个 agent 定义）。

## 本 fork 的改动

1. **裁剪**：`pool/` 保留上游全量快照，`skills/` `agents/` 只物化被选中的部分。
   物化出来的 skill / agent 统一带 `forge-` 前缀（上游名不带），前缀只用于
   与别的插件的同名资产区分；`pool/` 与 `manifest/` 里保留上游名。
   本 fork **不发布命令**：上游的 24 个 command 只留在 `pool/` 里，不物化。
2. **omp 适配**：
   - 移除 agent frontmatter 的 `model: sonnet|opus|haiku`（Claude 专有别名，omp 无对应模型，
     保留会导致 agent 无法解析模型而不可用）。
   - agent frontmatter 的 `tools:` 归一化为 omp 的工具名，丢弃 Claude 专有工具
     （`WebFetch` / `NotebookEdit` / `SlashCommand` 等）。
   - `package.json` 保留上游 `pi.skills` 声明，omp 的 `omp-plugins` provider
     据此发现 `skills/`。
3. **正文改写**（由 `tools/apply_selection.py` 在物化时确定性执行，`tools/check_refs.py`
   用同一套判定做门禁）：
   - Claude 专有工具名与交互机制（`AskUserQuestion`、`TodoWrite`、`PreToolUse` hook 等）
     换成 omp 的对应写法。
   - 路径约定：`CLAUDE.md` → `AGENTS.md`，`.claude/prds/` → `docs/prds/` 等。
   - **悬空引用清除**：指向本 fork 不提供的资产（上游全量 ECC 才有的命令、被当前 profile
     排除的兄弟 skill、嵌套 `rules/react/*.md`、上游 `docs/`）的引用会被删除；指向可读资产的
     相对 markdown 链接会改写成 omp 能跟随的规范 URI（`skill://<name>` 等）。
   - **资产名改写**：指向被改名资产的引用（`skill://api-design` → `skill://forge-api-design`、
     反引号裸名 → 带前缀的运行名）会一并改写；散文里不是资产引用的普通词不动。
4. **工具化**：新增 `tools/`（上游更新、重放选择、部署、生成目录、引用门禁）。
5. **自有资产**：`own/skills/` 下除选路表 `forge-router` 外，另有六条本 fork 原创的 skill
   ——发布与运维三条（`forge-release-management`、`forge-observability`、
   `forge-incident-response`），插件自身的运维三条（`forge-pipeline`、`forge-ci-triage`、
   `forge-absorb-third-party-skill`），随 fork 一起分发（MIT）。
   第三方正文见下节「第三方收纳资产」。

正文改动由脚本确定性生成，`pool/` 中的上游快照保持原样，便于逐条比对。

## 第三方收纳资产

`absorbed/` 下的 skill 来自三个 MIT 许可的仓库与一个 Apache-2.0 许可的仓库，经
`tools/absorbed_fixups.py` 的声明式规则改写后随本 fork 发布。来源 commit、逐文件摘要与
许可声明记在 `manifest/absorbed.json`，刷新用 `python tools/sync_absorbed.py`；
决策记录见 `docs/adr/0010-absorbed-pool-for-third-party-skills.md`。

| 来源 | 许可 | 随附文本 |
| --- | --- | --- |
| [backnotprop/pstack](https://github.com/backnotprop/pstack) | MIT，Copyright (c) 2026 Lauren Tan | `absorbed/pstack/LICENSE` |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | MIT，Copyright (c) 2025 Addy Osmani | `absorbed/addyosmani/LICENSE` |
| [fishzjp/qa-skills](https://github.com/fishzjp/qa-skills) | MIT，Copyright (c) 2026 fishzjp | `absorbed/qa-skills/LICENSE` |
| [youlaitech/youlai-skills](https://github.com/youlaitech/youlai-skills) | Apache-2.0，Copyright (c) 2026 youlaitech | `absorbed/youlai/LICENSE` |

`youlaitech/youlai-skills` 仓库本身没有随附许可文件，此处按同组织其它仓库
（`youlai-cloud`、`youlai-boot` 等）一致的 Apache-2.0 收录，并把该组织的版权声明写在上表。
Apache-2.0 §4 要求的改动声明见下节「youlai 的改动」。

收纳池共 35 条，进入运行树的是 34 条（`full` profile 全部，`java-python` 收 21 条，
`lite` 一条不收）：

- pstack 与 addyosmani：`forge-correct`、`forge-sharpen`、`forge-engineering-principles`
  （由 8 份 principle 快照拼接生成）、`forge-constraint-driven-development`、
  `forge-statechart`。`forge-constraint-driven-development` 与 `forge-statechart` 只进
  `full` profile；pstack 的 `forge-typescript-best-practices` 留在收纳池里但不再物化，
  它的职责由 ECC 上游的 `forge-typescript-patterns` 承担（同一件事只留一个入口）。
- qa-skills 的 QA 套件：`forge-qa`、`forge-requirement-analysis`、`forge-test-strategy`、
  `forge-test-case-writing`、`forge-test-case-review`、`forge-exploratory-testing`、
  `forge-automated-e2e-testing`、`forge-api-testing`、`forge-bug-analysis`、
  `forge-regression-testing`、`forge-test-reliability`、`forge-qa-memory`、
  `forge-ai-system-testing`（测 AI 功能的不确定性、评测集设计与 judge 校准），以及承载它们
  共享方法、模板与校验脚本的依赖单元 `forge-core`。整套进 `full` 与 `java-python`，
  `lite` 一条不收纳（正文里指向未启用 skill 的反引号裸名会降级为 notice，见
  `docs/adr/0014-qa-skills-absorption.md`）。

### youlai 的改动

Apache-2.0 §4(b) 要求标注对原作的改动。`youlaitech/youlai-skills` 的 15 条 skill 在本 fork
里的改动只有三类，都由脚本确定性执行：

1. **改名**：运行名统一加 `forge-` 前缀（`spring-boot` → `forge-spring-boot`），避免与其它
   插件的同名资产冲突；上游原名保留在 `manifest/absorbed.json` 与 `pool/` 记录里。
2. **描述替换**：frontmatter 的 `description` 换成中文触发描述（`manifest/skill_descriptions.zh.json`），
   正文只改两处——NestJS 的 `` `/page` `` 与 Element Plus 的 `` `/redirect` `` 写成了
   斜杠命令的形状，改成中文说法（本 fork 不发布命令，不改会被物化器当悬空引用删行）；
   其余正文一字未改、未翻译、未补写任何内容。
3. **profile 分流**：`full` 收全部 15 条，`java-python` 只收 `forge-doc-standard`、
   `forge-blog-writing`、`forge-git-version` 三条与 Java/Python 主力栈无关的通用条目。

### 许可正文


本插件分发的 `NOTICE.md` 自身即携带下列许可全文（MIT 要求版权声明与许可正文随副本分发）。

#### backnotprop/pstack

```
MIT License

Copyright (c) 2026 Lauren Tan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

#### addyosmani/agent-skills

```
MIT License

Copyright (c) 2025 Addy Osmani

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

#### fishzjp/qa-skills

```
MIT License

Copyright (c) 2026 fishzjp

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

#### youlaitech/youlai-skills

```
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright [yyyy] [name of copyright owner]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
```
