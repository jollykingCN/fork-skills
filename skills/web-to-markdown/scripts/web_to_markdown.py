#!/usr/bin/env python3
"""
网页转Markdown工具

将在线网页转换为Markdown格式，支持：
- JavaScript渲染的动态内容
- 图片下载和链接更新
- 登录状态（通过cookies）

依赖:
    pip install requests playwright markdownify beautifulsoup4 lxml
    playwright install chromium
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse, urljoin
from typing import Optional, Dict, Any

import requests
from playwright.sync_api import sync_playwright
from markdownify import markdownify as md
from bs4 import BeautifulSoup


def clean_html(html: str) -> str:
    """
    清理HTML，删除不需要的标签及其内容

    使用 DOM 树解析而非正则表达式，确保正确处理嵌套、注释等复杂情况。

    Args:
        html: 原始HTML字符串

    Returns:
        清理后的HTML字符串
    """
    # 使用 lxml 解析器，速度快且健壮
    soup = BeautifulSoup(html, 'lxml')

    # 删除不需要的标签及其所有子内容
    for tag in soup(['script', 'style', 'noscript', 'link', 'meta', 'head']):
        tag.decompose()

    # 删除 HTML 注释
    for comment in soup.find_all(string=lambda text: isinstance(text, str) and text.strip().startswith('<!--')):
        comment.extract()

    return str(soup)


def sanitize_filename(url: str) -> str:
    """从URL生成安全的文件名"""
    parsed = urlparse(url)
    # 移除 scheme 和 www
    netloc = parsed.netloc.replace("www.", "")
    # 处理路径
    path = parsed.path.strip("/").replace("/", "-")
    # 移除特殊字符
    safe_name = re.sub(r'[^\w\-\.]', '-', f"{netloc}-{path}")
    # 限制长度
    safe_name = safe_name[:200]
    return safe_name + ".md"


def download_image(img_url: str, base_url: str, output_dir: Path, session: Optional[requests.Session] = None) -> Optional[str]:
    """下载图片并返回相对路径"""
    try:
        # 解析完整URL
        full_url = urljoin(base_url, img_url)
        if not full_url.startswith(("http://", "https://")):
            return None

        # 从URL生成图片文件名
        parsed = urlparse(full_url)
        filename = os.path.basename(parsed.path)
        if not filename or '.' not in filename:
            filename = f"image_{int(time.time() * 1000)}.png"

        # 下载图片
        if session:
            response = session.get(full_url, timeout=10)
        else:
            response = requests.get(full_url, timeout=10)

        if response.status_code == 200:
            # 确保目录存在
            output_dir.mkdir(parents=True, exist_ok=True)

            # 处理重复文件名
            output_path = output_dir / filename
            counter = 1
            while output_path.exists():
                name, ext = os.path.splitext(filename)
                output_path = output_dir / f"{name}_{counter}{ext}"
                counter += 1

            # 保存图片
            output_path.write_bytes(response.content)
            # 返回相对路径
            return str(output_path)

    except Exception as e:
        print(f"下载图片失败 {img_url}: {e}", file=sys.stderr)

    return None


def convert_to_markdown(
    url: str,
    output_path: Optional[str] = None,
    cookies_file: Optional[str] = None,
    download_images: bool = True,
    images_dir: str = "images",
    timeout: int = 30
) -> str:
    """
    将网页转换为Markdown

    Args:
        url: 目标网页URL
        output_path: 输出文件路径，未指定则自动生成
        cookies_file: cookies文件路径（JSON格式）
        download_images: 是否下载图片
        images_dir: 图片保存目录
        timeout: 页面加载超时时间（秒）

    Returns:
        输出文件路径

    Raises:
        ValueError: 无效的URL
        RuntimeError: 转换失败
    """
    # 验证URL
    if not url or not url.startswith(("http://", "https://")):
        raise ValueError(f"无效的URL: {url}")

    # 确定输出路径
    if output_path is None:
        output_path = sanitize_filename(url)
    output_path = Path(output_path)

    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 加载cookies
    cookies = None
    if cookies_file and os.path.exists(cookies_file):
        with open(cookies_file, 'r', encoding='utf-8') as f:
            cookies = json.load(f)

    # 图片目录
    images_path = output_path.parent / images_dir

    downloaded_images: Dict[str, str] = {}

    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        # 设置cookies
        if cookies:
            for cookie in cookies:
                try:
                    context.add_cookies([cookie])
                except Exception as e:
                    print(f"设置cookie失败: {e}", file=sys.stderr)

        page = context.new_page()

        try:
            print(f"正在加载页面: {url}")
            # 加载页面并等待网络空闲
            page.goto(url, wait_until="networkidle", timeout=timeout * 1000)

            # 获取HTML内容
            html = page.content()

            # 获取页面标题
            title = page.title()
            print(f"页面标题: {title}")

            # 如果需要下载图片
            if download_images:
                print("正在下载图片...")
                session = requests.Session()
                if cookies:
                    session.cookies.update({c['name']: c['value'] for c in cookies})

                # 查找所有图片
                img_elements = page.query_selector_all("img")
                for i, img in enumerate(img_elements):
                    src = img.get_attribute("src")
                    if src:
                        print(f"  下载图片 {i+1}/{len(img_elements)}: {src[:50]}...")
                        rel_path = download_image(src, url, images_path, session)
                        if rel_path:
                            downloaded_images[src] = rel_path

                session.close()

            # 关闭浏览器
            browser.close()

        except Exception as e:
            browser.close()
            raise RuntimeError(f"加载页面失败: {e}")

    # 清理HTML：删除不需要的标签及其内容
    print("正在清理HTML...")
    html = clean_html(html)

    # 转换为Markdown
    print("正在转换为Markdown...")
    markdown_content = md(
        html,
        heading_style="ATX",
        bullets="*",
        strip=["nav", "footer"]
    )

    # 替换图片链接
    if downloaded_images:
        print("更新图片链接...")
        for original_url, new_path in downloaded_images.items():
            # 转义特殊字符用于正则
            escaped_url = re.escape(original_url)
            # 替换为相对路径
            markdown_content = re.sub(
                rf'!\[.*?\]\({escaped_url}\)',
                lambda m: m[0].replace(original_url, new_path),
                markdown_content
            )

    # 添加来源信息
    header = f"# {title}\n\n> 来源: {url}\n\n---\n\n"
    markdown_content = header + markdown_content

    # 写入文件
    output_path.write_text(markdown_content, encoding='utf-8')
    print(f"\n✓ 转换完成: {output_path}")
    if downloaded_images:
        print(f"✓ 下载了 {len(downloaded_images)} 张图片到 {images_path}")

    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="将在线网页转换为Markdown格式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s https://example.com
  %(prog)s https://example.com -o mydoc.md
  %(prog)s https://private.com -c cookies.json
  %(prog)s https://example.com --no-images
        """
    )

    parser.add_argument("url", help="目标网页URL")
    parser.add_argument("-o", "--output", help="输出Markdown文件路径")
    parser.add_argument("-c", "--cookies", help="cookies文件路径（JSON格式）")
    parser.add_argument("--no-images", action="store_true", help="不下载图片")
    parser.add_argument("--images-dir", default="images", help="图片保存目录（默认: images）")
    parser.add_argument("--timeout", type=int, default=30, help="页面加载超时时间（秒，默认: 30）")

    args = parser.parse_args()

    try:
        result = convert_to_markdown(
            url=args.url,
            output_path=args.output,
            cookies_file=args.cookies,
            download_images=not args.no_images,
            images_dir=args.images_dir,
            timeout=args.timeout
        )
        sys.exit(0)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
