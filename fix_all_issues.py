#!/usr/bin/env python3
"""Comprehensive fix script for all identified slide issues."""

import re
import os

SLIDES_DIR = "/private/tmp/slides"


def fix_file(filepath, fixes):
    """Apply a list of (old, new) string replacements to a file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    for old, new in fixes:
        if old in content:
            content = content.replace(old, new, 1)

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def fix_page_number(slide_num):
    """Fix data-footer-page to match file number."""
    filepath = os.path.join(SLIDES_DIR, f"slide_{slide_num:02d}.html")
    if not os.path.exists(filepath):
        return None

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Find current page number
    match = re.search(r'data-footer-page="(\d+)"', content)
    if not match:
        return None

    current_page = match.group(1)
    expected_page = f"{slide_num:02d}"

    if current_page != expected_page:
        new_content = content.replace(
            f'data-footer-page="{current_page}"',
            f'data-footer-page="{expected_page}"',
            1,
        )
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        return f"  slide_{slide_num:02d}: page {current_page} -> {expected_page}"

    return None


def main():
    changes = []

    # ============================================================
    # Phase 1: Fix all page numbers
    # ============================================================
    print("=" * 60)
    print("Phase 1: Fixing page numbers")
    print("=" * 60)

    for i in range(1, 74):
        result = fix_page_number(i)
        if result:
            changes.append(result)
            print(result)

    # ============================================================
    # Phase 2: Fix chapter headers
    # ============================================================
    print("\n" + "=" * 60)
    print("Phase 2: Fixing chapter headers")
    print("=" * 60)

    chapter_fixes = {
        24: ('data-header-chapter="第2章 前提・背景"', 'data-header-chapter="第3章 問題解決の概要"'),
        29: ('data-header-chapter="第3章 論点を定義する"', 'data-header-chapter="第4章 論点を定義する"'),
        30: ('data-header-chapter="第3章 論点を定義する"', 'data-header-chapter="第4章 論点を定義する"'),
        31: ('data-header-chapter="第5章 論点を分解する"', 'data-header-chapter="第4章 論点を定義する"'),
    }

    for slide_num, (old, new) in chapter_fixes.items():
        filepath = os.path.join(SLIDES_DIR, f"slide_{slide_num:02d}.html")
        if fix_file(filepath, [(old, new)]):
            msg = f"  slide_{slide_num:02d}: {old} -> {new}"
            changes.append(msg)
            print(msg)

    # ============================================================
    # Phase 3: Fix slide_04 title tag
    # ============================================================
    print("\n" + "=" * 60)
    print("Phase 3: Fixing slide_04 title tag")
    print("=" * 60)

    filepath_04 = os.path.join(SLIDES_DIR, "slide_04.html")
    if fix_file(filepath_04, [
        ("<title>私生活全般 - 自己紹介</title>", "<title>苦手なこと - 自己紹介</title>")
    ]):
        msg = "  slide_04: title '私生活全般' -> '苦手なこと'"
        changes.append(msg)
        print(msg)

    # ============================================================
    # Phase 4: Fix slide_36 theme (mist -> paper)
    # ============================================================
    print("\n" + "=" * 60)
    print("Phase 4: Fixing slide_36 theme")
    print("=" * 60)

    filepath_36 = os.path.join(SLIDES_DIR, "slide_36.html")
    if fix_file(filepath_36, [
        ("slide-theme-mist", "slide-theme-paper")
    ]):
        msg = "  slide_36: theme mist -> paper"
        changes.append(msg)
        print(msg)

    # ============================================================
    # Phase 5: Fix index.html title for slide_04
    # ============================================================
    print("\n" + "=" * 60)
    print("Phase 5: Fixing index.html slide titles")
    print("=" * 60)

    index_path = os.path.join(SLIDES_DIR, "index.html")
    index_fixes = [
        ('{ title: "私生活全般", type: "normal", file: "slide_04.html" }',
         '{ title: "苦手なこと", type: "normal", file: "slide_04.html" }'),
    ]
    if fix_file(index_path, index_fixes):
        msg = "  index.html: slide_04 title '私生活全般' -> '苦手なこと'"
        changes.append(msg)
        print(msg)

    # ============================================================
    # Summary
    # ============================================================
    print("\n" + "=" * 60)
    print(f"Total changes: {len(changes)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
