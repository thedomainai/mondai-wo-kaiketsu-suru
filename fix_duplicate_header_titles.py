#!/usr/bin/env python3
"""Remove body-level title blocks duplicated by standardized headers."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path("/private/tmp/slides")
SLIDE_GLOB = "slide_*.html"

# Slides that still carry a standalone hero/title block after the standardized
# header was inserted. These blocks sit at left:80 / top:160 and contain only
# text, so removing them preserves the actual slide content.
TOP_TITLE_BLOCK_RE = re.compile(
    r'\s*<!--\s*(?:Section Title(?: and Subtitle)?|Title(?:\s*&\s*Subtitle)?|Subtitle)\s*(?:\([^)]+\))?\s*-->\s*'
    r'<div\s+data-object="true"\s+data-object-type="textbox"\s+'
    r'style="position:\s*absolute;\s*left:\s*80px;\s*top:\s*160px;[^"]*">'
    r'(?:(?!<div\b).)*?</div>\s*',
    re.DOTALL,
)

# Two slides repeat the standardized header title inside a richer left panel.
# Remove only the duplicated heading line and keep the actual content block.
SPECIAL_REPLACEMENTS = {
    "slide_33.html": [
        (
            re.compile(
                r'\s*<p style="font-family: \'Noto Sans JP\', sans-serif; '
                r'font-weight: 900; font-size: 38px; line-height: 1\.2; '
                r'color: #000000; margin-bottom: 16px; letter-spacing: 1px;">'
                r'良い仮説の条件</p>\s*'
                r'<p style="font-family: \'Noto Sans JP\', sans-serif; '
                r'font-weight: 700; font-size: 20px; line-height: 1\.6; '
                r'color: #000000; margin-bottom: 24px; padding-bottom: 8px; '
                r'border-bottom: 2px solid #000;">4つの必須条件</p>\s*'
            ),
            "\n",
        ),
    ],
    "slide_24.html": [
        (
            re.compile(
                r'\s*<p style="font-family: \'Noto Sans JP\', sans-serif; '
                r'font-weight: 900; font-size: 32px; line-height: 1\.3; '
                r'color: #000000; margin-bottom: 30px; letter-spacing: 1px;">'
                r'原則2：<br/>1階層ずつ、網羅的かつ<br/>MECEに分解する</p>\s*'
            ),
            "\n",
        ),
    ],
    "slide_53.html": [
        (
            re.compile(
                r'\s*<p style="font-family: \'Noto Sans JP\', sans-serif; '
                r'font-weight: 900; font-size: 34px; line-height: 1\.4; '
                r'color: #000000; margin-bottom: 28px; letter-spacing: 1px;">'
                r'2\. 根拠：センターピンに<br/>接続する</p>\s*'
            ),
            "\n",
        ),
    ],
}


def cleanup_slide(text: str, name: str) -> str:
    updated = TOP_TITLE_BLOCK_RE.sub("\n", text)
    for pattern, replacement in SPECIAL_REPLACEMENTS.get(name, []):
        updated = pattern.sub(replacement, updated)
    return updated


def main() -> None:
    changed: list[str] = []
    for path in sorted(ROOT.glob(SLIDE_GLOB)):
        original = path.read_text(encoding="utf-8")
        updated = cleanup_slide(original, path.name)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed.append(path.name)

    print(f"Updated {len(changed)} slides")
    for name in changed:
        print(f"  - {name}")


if __name__ == "__main__":
    main()
