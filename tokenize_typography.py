#!/usr/bin/env python3
from pathlib import Path

ROOT = Path("/private/tmp/slides")
SLIDES = sorted(ROOT.glob("slide_*.html"))


def replace_once(text: str, old: str, new: str) -> str:
    return text.replace(old, new)


for path in SLIDES:
    html = path.read_text(encoding="utf-8")
    original = html

    if './slides.css' not in html:
        html = html.replace("<style>", '<link href="./slides.css" rel="stylesheet"/>\n<style>', 1)

    html = replace_once(
        html,
        "font-size: 12px; color: #000; letter-spacing: 1px; background:",
        "font-size: var(--font-size-header-pill); color: #000; letter-spacing: 1px; background:",
    )
    html = replace_once(
        html,
        "font-size: 12px; color: #999; letter-spacing: 0.5px;",
        "font-size: var(--font-size-header-chapter); color: #999; letter-spacing: 0.5px;",
    )
    html = replace_once(
        html,
        "font-size: 32px; color: #000; letter-spacing: 1px; line-height: 1.2;",
        "font-size: var(--font-size-header-title); color: #000; letter-spacing: var(--letter-spacing-header-title); line-height: var(--line-height-header-title);",
    )
    html = replace_once(
        html,
        "font-size: 14px; color: #888; line-height: 1.4;",
        "font-size: var(--font-size-header-subtitle); color: #888; line-height: var(--line-height-header-subtitle);",
    )
    html = replace_once(
        html,
        "font-size: 11px; color: #bbb; letter-spacing: 1.5px;",
        "font-size: var(--font-size-footer-meta); color: #bbb; letter-spacing: 1.5px;",
    )
    html = replace_once(
        html,
        "font-size: 11px; color: #bbb; letter-spacing: 0.5px;",
        "font-size: var(--font-size-footer-meta); color: #bbb; letter-spacing: 0.5px;",
    )

    html = replace_once(
        html,
        "font-size: 13px;",
        "font-size: var(--font-size-center-chapter);",
    ) if ".chapter {" in html else html
    html = replace_once(
        html,
        "font-size: 64px;",
        "font-size: var(--font-size-center-title);",
    ) if ".title {" in html else html
    html = replace_once(
        html,
        "font-size: 22px;",
        "font-size: var(--font-size-center-subtitle);",
    ) if ".subtitle {" in html else html

    if ".title {" in html:
        html = replace_once(
            html,
            "let size = 64;",
            "let size = parseFloat(getComputedStyle(title).fontSize);",
        )

    if path.name == "slide_01.html":
        html = replace_once(
            html,
            "font-size:88px;",
            "font-size:var(--font-size-cover-title);",
        )
        html = replace_once(
            html,
            "font-size: 88px;",
            "font-size: var(--font-size-cover-title);",
        )
        html = replace_once(
            html,
            "font-size:22px;",
            "font-size:var(--font-size-cover-subtitle);",
        )
        html = replace_once(
            html,
            "font-size: 22px;",
            "font-size: var(--font-size-cover-subtitle);",
        )

    if html != original:
        path.write_text(html, encoding="utf-8")
