#!/usr/bin/env python3
"""EPUB 全文检索工具：在指定 epub 文件内搜索关键词，输出上下文。"""
import sys
import re
from pathlib import Path
from ebooklib import epub, ITEM_DOCUMENT
from bs4 import BeautifulSoup


def extract_text(epub_path: str):
    """返回 [(chapter_title, plain_text), ...]"""
    book = epub.read_epub(epub_path, options={"ignore_ncx": True})
    chapters = []
    for item in book.get_items_of_type(ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_content(), "lxml")
        # 尝试获取章节标题
        title_tag = soup.find(["h1", "h2", "h3", "title"])
        title = title_tag.get_text(strip=True) if title_tag else item.get_name()
        text = soup.get_text("\n", strip=True)
        chapters.append((title, text))
    return chapters


def search(epub_path: str, keywords: list, context_chars: int = 120, max_hits: int = 8):
    chapters = extract_text(epub_path)
    pattern = re.compile("|".join(re.escape(k) for k in keywords))
    hits = []
    for title, text in chapters:
        for m in pattern.finditer(text):
            start = max(0, m.start() - context_chars)
            end = min(len(text), m.end() + context_chars)
            snippet = text[start:end].replace("\n", " ")
            hits.append((title, m.group(), snippet))
            if len(hits) >= max_hits:
                return hits
    return hits


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: query_epub.py <epub路径> <关键词1> [关键词2] ...")
        sys.exit(1)
    epub_path = sys.argv[1]
    keywords = sys.argv[2:]
    results = search(epub_path, keywords)
    if not results:
        print(f"未找到关键词: {keywords}")
    for i, (title, kw, snippet) in enumerate(results, 1):
        print(f"[{i}] 章节: {title}")
        print(f"    命中: {kw}")
        print(f"    原文: ...{snippet}...")
        print()
