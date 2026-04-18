#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SLIDES_DIR = ROOT / "slides"
DEFAULT_MD_OUT = ROOT / "docs" / "header-copy-revision.md"
DEFAULT_HTML_OUT = ROOT / "docs" / "header-copy-revision.html"

SLIDE_FILE_RE = re.compile(r"slide_(\d+)\.html$")
ATTR_RE = re.compile(r'([:\w-]+)="([^"]*)"')
CONTAINER_RE = re.compile(
    r'<div\b[^>]*class="[^"]*\bslide-container\b[^"]*"[^>]*>',
    re.IGNORECASE,
)


@dataclass
class HeaderCopyRow:
    page: int
    file_name: str
    chapter: str
    main_message: str
    slide_title: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync header-copy revision docs from slide HTML files."
    )
    parser.add_argument("--slides-dir", type=Path, default=DEFAULT_SLIDES_DIR)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--html-out", type=Path, default=DEFAULT_HTML_OUT)
    return parser.parse_args()


def parse_slide_row(path: Path) -> HeaderCopyRow | None:
    match = SLIDE_FILE_RE.match(path.name)
    if not match:
        return None

    text = path.read_text(encoding="utf-8")
    container_match = CONTAINER_RE.search(text)
    if not container_match:
        return None

    attrs = dict(ATTR_RE.findall(container_match.group(0)))
    if "data-header-title" not in attrs or "data-footer-page" not in attrs:
        return None

    try:
        page = int(attrs["data-footer-page"])
    except ValueError:
        return None

    return HeaderCopyRow(
        page=page,
        file_name=path.name,
        chapter=attrs.get("data-header-chapter", ""),
        # User convention:
        # data-header-title => main message
        # data-header-subtitle => slide title
        main_message=attrs.get("data-header-title", ""),
        slide_title=attrs.get("data-header-subtitle", ""),
    )


def collect_rows(slides_dir: Path) -> list[HeaderCopyRow]:
    rows = []
    for path in sorted(slides_dir.glob("slide_*.html")):
        row = parse_slide_row(path)
        if row is not None:
            rows.append(row)
    return sorted(rows, key=lambda row: (row.page, row.file_name))


def render_markdown(rows: list[HeaderCopyRow], slides_dir: Path) -> str:
    lines = [
        "# Header Copy Revision",
        "",
        "## Semantics",
        "",
        "- `header--title` (`data-header-title`) = main message",
        "- `header--subtitle` (`data-header-subtitle`) = slide title",
        "- Source of truth: slide HTML files under "
        f"`{slides_dir}`",
        "",
        "## Sync Command",
        "",
        "```bash",
        "python3 /private/tmp/slides/tools/sync_header_copy_revision.py",
        "```",
        "",
        "## Current Mapping",
        "",
        "| Page | File | Chapter | Main Message (`data-header-title`) | Slide Title (`data-header-subtitle`) |",
        "|---|---|---|---|---|",
    ]

    for row in rows:
        lines.append(
            f"| {row.page} | `{row.file_name}` | {escape_md(row.chapter)} | "
            f"{escape_md(row.main_message)} | {escape_md(row.slide_title)} |"
        )

    lines.append("")
    return "\n".join(lines)


def render_html(rows: list[HeaderCopyRow], slides_dir: Path) -> str:
    cards = []
    for row in rows:
        cards.append(
            "  <div class=\"card\">\n"
            f"    <div class=\"num\">SLIDE {row.page:02d}</div>\n"
            f"    <div class=\"chapter\">{html.escape(row.chapter)}</div>\n"
            f"    <div class=\"msg\">{html.escape(row.main_message)}</div>\n"
            f"    <div class=\"ttl\">{html.escape(row.slide_title)}</div>\n"
            f"    <div class=\"meta\">{html.escape(row.file_name)}</div>\n"
            "  </div>"
        )

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Header Copy Revision</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  font-family: "Helvetica Neue", sans-serif;
  background: #f5f5f3;
  color: #1a1a1a;
  padding: 16px;
}}
h1 {{
  font-size: 16px;
  font-weight: 900;
  margin-bottom: 6px;
  padding-bottom: 10px;
  border-bottom: 2px solid #1a1a1a;
}}
.legend {{
  font-size: 12px;
  color: rgba(0,0,0,.58);
  margin-bottom: 16px;
  padding-top: 6px;
  line-height: 1.8;
}}
.legend code {{
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 11px;
}}
.cards {{ display: flex; flex-direction: column; gap: 8px; }}
.card {{
  background: #fff;
  border-radius: 8px;
  border: 1px solid rgba(0,0,0,.1);
  padding: 12px 14px;
}}
.num {{
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1.5px;
  color: rgba(0,0,0,.32);
  margin-bottom: 4px;
}}
.chapter {{
  font-size: 11px;
  font-weight: 700;
  color: rgba(0,0,0,.52);
  margin-bottom: 6px;
}}
.msg {{
  font-size: 16px;
  font-weight: 900;
  color: #1a1a1a;
  line-height: 1.35;
  margin-bottom: 4px;
}}
.ttl {{
  font-size: 12px;
  font-weight: 400;
  color: rgba(0,0,0,.56);
  line-height: 1.55;
}}
.meta {{
  margin-top: 8px;
  font-size: 10px;
  color: rgba(0,0,0,.34);
}}
</style>
</head>
<body>
<h1>Header Copy Revision</h1>
<div class="legend">
  <div><code>data-header-title</code> = main message</div>
  <div><code>data-header-subtitle</code> = slide title</div>
  <div>Source of truth: {html.escape(str(slides_dir))}</div>
</div>
<div class="cards">
{chr(10).join(cards)}
</div>
</body>
</html>
"""


def escape_md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br/>")


def main() -> int:
    args = parse_args()
    rows = collect_rows(args.slides_dir)
    args.md_out.write_text(render_markdown(rows, args.slides_dir), encoding="utf-8")
    args.html_out.write_text(render_html(rows, args.slides_dir), encoding="utf-8")
    print(
        f"Wrote {len(rows)} rows to {args.md_out} and {args.html_out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
