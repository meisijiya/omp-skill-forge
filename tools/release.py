#!/usr/bin/env python
"""发版前的检查与打标：版本号、changelog、tag 三者必须是同一件事。

用法：

    python tools/release.py --version 0.6.0 --summary "上游 pin 前进、吸纳 ai-system-testing"
    python tools/release.py --version 0.6.0 --summary "..." --push

检查项（全过才打标）：

  1. 工作区干净——tag 代表一份确定的制品，不能打在半改的状态上。
  2. `package.json` 的 version 等于 `--version`（插件的版本号来自这里）。
  3. `CHANGELOG.md` 里有 `## [<version>]` 段落（发出去的版本要能看出改了什么）。
  4. `v<version>` 这个 tag 还没打过（版本号是承诺，不可改写）。

打的是 annotated tag，message 为 `release: <version> —— <summary>`。
`--push` 会把 tag 推到 origin；GitHub Release 由 `gh release create` 另发，
步骤写在 `README.md` → 「版本与发布」。
"""

import argparse
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKAGE = os.path.join(ROOT, "package.json")
CHANGELOG = os.path.join(ROOT, "CHANGELOG.md")
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def git(args):
    return subprocess.run(
        ["git", "-C", ROOT] + args, capture_output=True, text=True
    )


def main():
    ap = argparse.ArgumentParser(description="发版前的检查与打标。")
    ap.add_argument("--version", required=True, help="版本号，如 0.6.0")
    ap.add_argument("--summary", required=True, help="一句话摘要，进 tag message")
    ap.add_argument("--push", action="store_true", help="把 tag 推到 origin")
    args = ap.parse_args()

    version = args.version
    if not VERSION_RE.match(version):
        fail(f"版本号 {version!r} 不是 MAJOR.MINOR.PATCH")

    status = git(["status", "--porcelain"])
    if status.returncode != 0:
        fail(f"git status 失败: {status.stderr.strip()}")
    if status.stdout.strip():
        fail("工作区不干净，先提交或清理再打 tag:\n" + status.stdout.strip())

    with open(PACKAGE, encoding="utf-8") as f:
        pkg_version = json.load(f).get("version")
    if pkg_version != version:
        fail(
            f"package.json 的 version 是 {pkg_version!r}，与 --version {version!r} 不一致"
        )

    with open(CHANGELOG, encoding="utf-8") as f:
        changelog = f.read()
    if not re.search(r"(?m)^## \[" + re.escape(version) + r"\]", changelog):
        fail(f"CHANGELOG.md 里没有 `## [{version}]` 段落")

    tag = f"v{version}"
    if git(["rev-parse", "-q", "--verify", f"refs/tags/{tag}"]).returncode == 0:
        fail(f"tag {tag} 已经存在；版本号是承诺，不可改写，要发就发新版本号")

    message = f"release: {version} —— {args.summary}"
    result = git(["tag", "-a", tag, "-m", message])
    if result.returncode != 0:
        fail(f"打 tag 失败: {result.stderr.strip()}")
    print(f"已打 {tag}: {message}")

    if args.push:
        pushed = git(["push", "origin", tag])
        if pushed.returncode != 0:
            fail(f"推 tag 失败: {pushed.stderr.strip()}")
        print(f"已推 {tag} 到 origin")
    else:
        print(f"下一步: git push origin {tag}")
    print(
        "下一步: gh release create "
        f"{tag} --title \"{tag} —— {args.summary}\" --generate-notes"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
