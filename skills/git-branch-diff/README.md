# git-branch-diff

基于 `git diff`（三点语法）的 Git 分支差异报告生成器。

## 功能

输入基础分支和特性分支名称，自动生成完整的差异报告，包含：

- 分支信息（commit hash、merge base）
- 文件分类清单（新增 / 删除 / 修改）
- 变更统计（每个文件的增删行数）
- 详细差异（unified diff 格式）

## 前置条件

- Python 3
- Git
- 在目标 git 仓库目录下执行

## 使用方式

在 Claude Code 中直接说：

- "帮我看看 feature-xxx 分支相对于 main 的差异"
- "生成 feature 分支的 diff 报告"
- "比较 main 和 my-feature 分支"

或手动运行脚本：

```bash
python3 scripts/gen_diff.py <基础分支> <特性分支>
```

示例：

```bash
python3 scripts/gen_diff.py main feature-concurrent-send
```

## 原理

使用 `git diff base...feature`（三点语法），找到两个分支的 merge base，然后比较 merge base 到特性分支 HEAD 的内容差异。

**特点：**
- 只显示特性分支独有的改动，不包含基础分支上别人的提交
- 即使特性分支曾多次 merge 基础分支，结果仍然准确
- 自动执行 `git fetch` 确保远程数据最新
- 不需要 checkout 分支文件，比较的是 commit 快照

## 输出

脚本会在同目录下生成 `diff_report.md`。
