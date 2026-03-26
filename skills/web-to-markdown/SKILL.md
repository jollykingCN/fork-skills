---
name: web-to-markdown
description: 将在线网页URL转换为Markdown格式文件。适用于需要抓取网页内容并保存为可编辑Markdown文档的场景。当用户提到"网页转markdown"、"URL转md"、"抓取网页为markdown"、"下载网页为md"、"保存网页为markdown"等需求时触发。也适用于需要保留网页格式（标题、列表、代码块、表格等）或 将网页内容导出为文档的情况。
---

# 网页转 Markdown

本技能将在线网页转换为Markdown格式文件，保留原网页的格式和样式。

## 触发条件

当用户表达以下意图时使用此技能：
- "把 https://example.com 转成 markdown"
- "下载这个网页为 md 文件"
- "抓取这个URL的内容保存为markdown"
- "将网页转为md格式"

## 工作流程

### 0. 检查并安装依赖

首次运行时，检查以下Python包是否已安装，未安装则自动安装：
- `requests`: HTTP请求库
- `playwright`: 浏览器自动化（用于处理JavaScript渲染）
- `markdownify`: HTML转Markdown

安装命令：
```bash
pip install -r requirements.txt
playwright install chromium
```

### 1. 获取用户输入

从用户请求中提取：
- **URL**: 目标网页地址
- **输出文件名**: 可选，未指定则自动从URL生成
- **Cookies/Session**: 可选，用于登录状态
- **图片处理**: 默认下载到images文件夹

### 2. 执行转换脚本

运行 `scripts/web_to_markdown.py`，参数格式：

```bash
python scripts/web_to_markdown.py <URL> [options]
```

可用选项：
- `-o, --output`: 输出文件路径
- `-c, --cookies`: cookies文件路径（JSON格式）
- `--no-images`: 不下载图片
- `--images-dir`: 图片保存目录（默认: images）

### 3. 返回结果

向用户报告：
- 转换成功的文件路径
- 下载的图片数量（如果有）
- 任何警告或错误

## 输出文件命名规则

未指定输出文件名时，自动生成：
- 从URL提取域名和路径
- 替换特殊字符为连字符
- 添加 `.md` 扩展名

示例：
- `https://example.com/docs/api` → `example.com-docs-api.md`
- `https://blog.site.com/post/123` → `blog.site.com-post-123.md`

## 支持的网页元素

转换脚本会保留以下Markdown格式：
- 标题层级（#、##、###）
- 段落和换行
- 有序和无序列表
- 代码块（支持语法高亮标记）
- 粗体（**text**）和斜体（*text*）
- 链接
- 表格
- 图片（相对路径引用）

## 错误处理

脚本会处理以下情况：
- 无效URL格式
- 网络连接失败
- 404/500等HTTP错误
- 渲染超时
- 文件写入权限问题

所有错误都会以清晰的中文消息返回给用户。

## 示例

### 基本用法
```
用户: 把 https://docs.python.org/3/library/json.html 转成markdown
```

### 指定输出文件
```
用户: 下载 https://example.com 保存为 mydoc.md
```

### 需要登录的页面
```
用户: 用这个cookies.json去抓取 https://private.example.com/page
```
