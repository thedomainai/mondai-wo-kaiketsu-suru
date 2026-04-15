#!/usr/bin/env python3
"""Sync deck metadata from the actual slide HTML files."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path("/private/tmp/slides")
INDEX_PATH = ROOT / "index.html"
SLIDE_GLOB = "slide_*.html"
SLIDE_NUM_RE = re.compile(r"slide_(\d+)\.html$")
SLIDE_SUFFIX_RE = re.compile(r"\s+-\s+.+$")
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
SLIDES_BLOCK_RE = re.compile(
    r"// BEGIN GENERATED SLIDES\s*\nconst slides = \[\n.*?\n\];\n// END GENERATED SLIDES",
    re.DOTALL,
)
HEADER_RE = re.compile(r"(<h1 id=\"deckTitle\">)(.*?)(</h1>)", re.DOTALL)
COUNTER_RE = re.compile(r"(<span id=\"counter\">)(.*?)(</span>)", re.DOTALL)
MOBILE_COUNTER_RE = re.compile(r"(<div id=\"mCounter\"[^>]*>)(.*?)(</div>)", re.DOTALL)
FOOTER_META_P_RE = re.compile(
    r"(<p[^>]*font-size:\s*var\(--font-size-footer-meta\)[^>]*>)(.*?)(</p>)",
    re.IGNORECASE | re.DOTALL,
)
STANDARD_FOOTER_RE = re.compile(r'(data-footer="standard")(?:\s+data-footer-page="[^"]*")?')


def normalize_whitespace(text: str) -> str:
    return " ".join(text.replace("<br/>", " ").replace("<br>", " ").split())


def slide_sort_key(slide_path: Path) -> int:
    match = SLIDE_NUM_RE.search(slide_path.name)
    if match:
        return int(match.group(1))
    return 10**9


def discover_slide_paths() -> list[Path]:
    slide_paths = sorted(ROOT.glob(SLIDE_GLOB), key=slide_sort_key)
    actual_numbers = [int(SLIDE_NUM_RE.fullmatch(path.name).group(1)) for path in slide_paths]
    expected_numbers = list(range(1, len(slide_paths) + 1))
    if actual_numbers != expected_numbers:
        raise RuntimeError(
            "Slide filenames must be contiguous: expected "
            + ", ".join(f"slide_{n:02d}.html" for n in expected_numbers)
        )
    return slide_paths


def extract_title(slide_path: Path) -> str:
    raw = slide_path.read_text(encoding="utf-8")
    match = TITLE_RE.search(raw)
    if not match:
        raise ValueError(f"<title> not found in {slide_path.name}")
    title = html.unescape(normalize_whitespace(match.group(1)))
    return SLIDE_SUFFIX_RE.sub("", title).strip()


def classify_slide(title: str) -> dict[str, str]:
    if title.startswith("アジェンダ — 第"):
        chapter_match = re.search(r"第(\d+)章", title)
        if chapter_match:
            title = f"━ Ch{int(chapter_match.group(1)):02d} アジェンダ"
        return {"title": title, "type": "chapter-agenda"}

    if title.startswith("アジェンダ"):
        return {"title": "アジェンダ", "type": "normal"}

    if re.match(r"^第\d+章", title):
        return {"title": title, "type": "chapter-title"}

    return {"title": title, "type": "normal"}


def build_slides() -> list[dict[str, str]]:
    slides = []
    for path in discover_slide_paths():
        title = extract_title(path)
        slide = classify_slide(title)
        slide["file"] = path.name
        slides.append(slide)
    return slides


def sync_footer_page_numbers(slide_paths: list[Path]) -> int:
    updated_count = 0

    for position, slide_path in enumerate(slide_paths, start=1):
        html_text = slide_path.read_text(encoding="utf-8")
        page_number = f"{position - 1:02d}"
        updated_html = html_text

        if position > 1 and 'data-footer="standard"' in updated_html:
            updated_html = STANDARD_FOOTER_RE.sub(
                rf'\1 data-footer-page="{page_number}"',
                updated_html,
                count=1,
            )

        matches = list(FOOTER_META_P_RE.finditer(html_text))
        if position > 1 and len(matches) >= 2:
            last_match = matches[-1]
            updated_html = (
                updated_html[: last_match.start()]
                + last_match.group(1)
                + page_number
                + last_match.group(3)
                + updated_html[last_match.end() :]
            )

        if updated_html != html_text:
            slide_path.write_text(updated_html, encoding="utf-8")
            updated_count += 1

    return updated_count


def render_slides_block(slides: list[dict[str, str]]) -> str:
    lines = ["// BEGIN GENERATED SLIDES", "const slides = ["]
    for slide in slides:
        title = json.dumps(slide["title"], ensure_ascii=False)
        slide_type = json.dumps(slide["type"], ensure_ascii=False)
        slide_file = json.dumps(slide["file"], ensure_ascii=False)
        lines.append(
            f"  {{ title: {title}, type: {slide_type}, file: {slide_file} }},"
        )
    lines.extend(["];", "// END GENERATED SLIDES"])
    return "\n".join(lines)


def sync_index() -> None:
    slide_paths = discover_slide_paths()
    slides = build_slides()
    deck_title = slides[0]["title"] if slides else "スライド"
    index_html = INDEX_PATH.read_text(encoding="utf-8")

    new_block = render_slides_block(slides)
    if not SLIDES_BLOCK_RE.search(index_html):
        raise RuntimeError("Generated slides block not found in index.html")
    updated = SLIDES_BLOCK_RE.sub(new_block, index_html)

    updated = HEADER_RE.sub(
        rf"\1{deck_title} — 全{len(slides)}スライド\3",
        updated,
        count=1,
    )
    updated = COUNTER_RE.sub(
        rf"\g<1>1 / {len(slides)}\g<3>",
        updated,
        count=1,
    )
    updated = MOBILE_COUNTER_RE.sub(
        rf"\g<1>1 / {len(slides)}\g<3>",
        updated,
        count=1,
    )

    INDEX_PATH.write_text(updated, encoding="utf-8")
    footer_updates = sync_footer_page_numbers(slide_paths)
    print(
        f"Synced {len(slides)} slides into {INDEX_PATH.name} "
        f"and updated {footer_updates} slide footers"
    )


if __name__ == "__main__":
    sync_index()
