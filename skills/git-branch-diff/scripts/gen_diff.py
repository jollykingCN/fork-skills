#!/usr/bin/env python3
"""
基于 git diff，生成特性分支相对于基础分支的差异报告
用法: python3 gen_diff.py <基础分支> <特性分支>
示例: python3 gen_diff.py main feature-branch
"""
import subprocess
import sys
import os


def run_git(*args):
    result = subprocess.run(["git"] + list(args), capture_output=True, text=True)
    if result.returncode != 0:
        print(f"git 命令失败: git {' '.join(args)}", file=sys.stderr)
        print(result.stderr.strip(), file=sys.stderr)
        sys.exit(1)
    return result.stdout


def resolve_upstream_branch(branch):
    """尝试将本地分支名解析为其远程跟踪分支（如 main → origin/main）。
    如果远程跟踪分支存在且领先于本地分支，优先使用远程版本。
    返回 (实际使用的分支名, 是否做了替换)。"""
    # 获取该分支的远程跟踪引用
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", f"{branch}" + "@{u}"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        # 没有设置 upstream，尝试直接用 origin/<branch>
        result2 = subprocess.run(
            ["git", "rev-parse", "--verify", f"origin/{branch}"],
            capture_output=True, text=True,
        )
        if result2.returncode == 0:
            return f"origin/{branch}", True
        return branch, False

    upstream = result.stdout.strip()
    # 比较本地和远程的 commit
    local_commit = run_git("rev-parse", branch).strip()
    upstream_commit = run_git("rev-parse", upstream).strip()

    if local_commit != upstream_commit:
        return upstream, True
    return branch, False


def main():
    if len(sys.argv) != 3:
        print("用法: python3 gen_diff.py <基础分支> <特性分支>")
        print("示例: python3 gen_diff.py main my-feature")
        sys.exit(1)

    base_branch = sys.argv[1]
    feature_branch = sys.argv[2]

    # 确认在 git 仓库中
    run_git("rev-parse", "--git-dir")

    # 先 fetch 远程分支数据，确保本地有最新的 commit 快照
    print("正在 fetch 远程分支数据...")
    run_git("fetch", "--all", "--quiet")

    # 解析基础分支：优先使用远程跟踪分支，避免本地分支落后导致误判
    resolved_base, was_replaced = resolve_upstream_branch(base_branch)
    if was_replaced:
        local_hash = run_git("rev-parse", base_branch).strip()[:8]
        remote_hash = run_git("rev-parse", resolved_base).strip()[:8]
        print(f"⚠ 本地 '{base_branch}' ({local_hash}) 与远程不同步，自动使用 '{resolved_base}' ({remote_hash})")

    display_base = base_branch
    base_branch = resolved_base

    # 确认两个分支都存在
    for branch in [base_branch, feature_branch]:
        result = subprocess.run(
            ["git", "rev-parse", "--verify", branch],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(f"分支不存在: {branch}", file=sys.stderr)
            sys.exit(1)

    # 获取 merge base 信息
    merge_base = run_git("merge-base", base_branch, feature_branch).strip()
    base_commit = run_git("rev-parse", base_branch).strip()
    feature_commit = run_git("rev-parse", feature_branch).strip()

    # 三点 diff：merge_base → feature 的变化
    diff_stat = run_git("diff", "--stat", f"{base_branch}...{feature_branch}")
    diff_detail = run_git("diff", f"{base_branch}...{feature_branch}")

    # 分类文件
    name_status = run_git("diff", "--name-status", f"{base_branch}...{feature_branch}")
    added, deleted, modified = [], [], []
    for line in name_status.strip().splitlines():
        if not line.strip():
            continue
        parts = line.split("\t", 1)
        status, filepath = parts[0], parts[1]
        if status.startswith("A"):
            added.append(filepath)
        elif status.startswith("D"):
            deleted.append(filepath)
        elif status.startswith("M"):
            modified.append(filepath)

    total = len(added) + len(deleted) + len(modified)

    # 输出分支信息
    print(f"\n{'='*80}")
    print(f"差异报告: {feature_branch} 相对于 {display_base}")
    print(f"{'='*80}")
    print(f"  基础分支:   {display_base}  ({base_commit[:8]})")
    print(f"  特性分支:   {feature_branch}  ({feature_commit[:8]})")
    print(f"  Merge Base: {merge_base[:8]}")
    print(f"  文件变更:   新增 {len(added)} | 删除 {len(deleted)} | 修改 {len(modified)} | 共 {total} 个")
    print()

    # 输出变更文件清单
    if added:
        print(f"  新增文件 ({len(added)}):")
        for f in added:
            print(f"    + {f}")
        print()
    if deleted:
        print(f"  删除文件 ({len(deleted)}):")
        for f in deleted:
            print(f"    - {f}")
        print()
    if modified:
        print(f"  修改文件 ({len(modified)}):")
        for f in modified:
            print(f"    ~ {f}")
        print()

    # 写入报告文件
    report_path = os.path.join(os.getcwd(), "diff_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# 差异报告: {feature_branch} vs {display_base}\n\n")
        f.write(f"- 基础分支: `{display_base}` ({base_commit[:8]})\n")
        f.write(f"- 特性分支: `{feature_branch}` ({feature_commit[:8]})\n")
        f.write(f"- Merge Base: `{merge_base[:8]}`\n")
        f.write(f"- 文件变更: 新增 {len(added)} | 删除 {len(deleted)} | 修改 {len(modified)} | 共 {total} 个\n\n")

        if added:
            f.write("## 新增文件\n\n")
            for filepath in added:
                f.write(f"- `{filepath}`\n")
            f.write("\n")
        if deleted:
            f.write("## 删除文件\n\n")
            for filepath in deleted:
                f.write(f"- `{filepath}`\n")
            f.write("\n")
        if modified:
            f.write("## 修改文件\n\n")
            for filepath in modified:
                f.write(f"- `{filepath}`\n")
            f.write("\n")

        f.write("## 变更统计\n\n```\n")
        f.write(diff_stat)
        f.write("```\n\n")

        f.write("## 详细差异\n\n```diff\n")
        f.write(diff_detail)
        f.write("```\n")

    print(f"报告已写入: {report_path}")


if __name__ == "__main__":
    main()
