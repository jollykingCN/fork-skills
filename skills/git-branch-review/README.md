# git-branch-review

基于 git-branch-diff 差异报告的结构化代码审查工具。

## 功能

1. 自动调用 `git-branch-diff` 生成差异报告
2. 按检查清单（`checklist.md`）逐文件审查变更
3. diff 片段不足以判断时，读取完整文件补充上下文
4. 输出结构化 CSV 文件供人工复核

## 前置条件

- Python 3（git-branch-diff 依赖）
- Git
- 在目标 git 仓库目录下执行
- `git-branch-diff` skill 已安装

## 使用方式

在 Claude Code 中直接说：

- "帮我做 code review，分支是 feature-xxx"
- "审查 feature-xxx 相对于 main 的代码改动"
- "code review feature-xxx 分支"

## 输出

在工作目录生成 `code_review_<分支名>.csv`，列结构：

| 列 | 说明 |
|---|------|
| 问题类别 | 资源泄漏/并发安全/错误处理/安全/配置与硬编码/数据一致性/死代码与可维护性/性能/运行时与运维/其他 |
| 严重程度 | 🔴 严重 / 🟡 需关注 / 🟢 建议 |
| 问题置信度 | 高（确定性缺陷）/ 中（大概率有问题）/ 低（疑似，需人工确认） |
| 问题 | 一句话概括 |
| 文件 | 文件路径和行号 |
| 说明 | 详细描述 |

状态列（已修复/待修复/已忽略）由人工后续处理时填写，skill 不填写。

## 文件说明

- `SKILL.md` — Skill 定义和工作流程
- `checklist.md` — 代码审查检查清单
