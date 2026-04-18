#!/usr/bin/env python3
from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V1_PATH = ROOT / "docs" / "header-copy-revision.md"
V2_PATH = ROOT / "docs" / "header-copy-revision-ver2.md"
OUT_PATH = ROOT / "docs" / "header-copy-revision-v1-v2-compare.html"

V1_ROW_RE = re.compile(
    r"^\|\s*(?P<page>\d+)\s*\|\s*`(?P<file>[^`]+)`\s*\|\s*(?P<chapter>.*?)\s*\|\s*(?P<main>.*?)\s*\|\s*(?P<title>.*?)\s*\|$",
    re.MULTILINE,
)

V2_ROW_RE = re.compile(
    r"^\|\s*(?P<page>\d+)\s*\|\s*(?P<chapter>.*?)\s*\|\s*(?P<current_main>.*?)\s*\|\s*(?P<current_title>.*?)\s*\|\s*(?P<ver2_main>.*?)\s*\|\s*(?P<ver2_title>.*?)\s*\|$",
    re.MULTILINE,
)


@dataclass
class V1Row:
    page: int
    file_name: str
    chapter: str
    main_message: str
    slide_title: str


@dataclass
class V2Row:
    page: int
    chapter: str
    main_message: str
    slide_title: str


def parse_v1(text: str) -> dict[int, V1Row]:
    rows: dict[int, V1Row] = {}
    for match in V1_ROW_RE.finditer(text):
        row = V1Row(
            page=int(match.group("page")),
            file_name=match.group("file").strip(),
            chapter=match.group("chapter").strip(),
            main_message=match.group("main").strip(),
            slide_title=match.group("title").strip(),
        )
        rows[row.page] = row
    return rows


def parse_v2(text: str) -> dict[int, V2Row]:
    rows: dict[int, V2Row] = {}
    for match in V2_ROW_RE.finditer(text):
        row = V2Row(
            page=int(match.group("page")),
            chapter=match.group("chapter").strip(),
            main_message=match.group("ver2_main").strip(),
            slide_title=match.group("ver2_title").strip(),
        )
        rows[row.page] = row
    return rows


def diff_class(a: str, b: str) -> str:
    return "same" if a == b else "changed"


def diff_label(a: str, b: str) -> str:
    return "Same" if a == b else "Changed"


def render_card(page: int, v1: V1Row | None, v2: V2Row | None) -> str:
    chapter = v1.chapter if v1 else (v2.chapter if v2 else "")
    file_name = v1.file_name if v1 else "-"
    v1_main = v1.main_message if v1 else "-"
    v1_title = v1.slide_title if v1 else "-"
    v2_main = v2.main_message if v2 else "-"
    v2_title = v2.slide_title if v2 else "-"
    main_state = diff_label(v1_main, v2_main)
    title_state = diff_label(v1_title, v2_title)
    main_class = diff_class(v1_main, v2_main)
    title_class = diff_class(v1_title, v2_title)
    card_class = "card same-card" if main_class == "same" and title_class == "same" else "card changed-card"

    return f"""
  <section class="{card_class}">
    <div class="card-head">
      <div>
        <p class="page">SLIDE {page:02d}</p>
        <p class="chapter">{html.escape(chapter)}</p>
      </div>
      <p class="file">{html.escape(file_name)}</p>
    </div>
    <div class="compare-grid">
      <div class="panel">
        <p class="panel-label">V1</p>
        <div class="field">
          <p class="field-name">Main Message</p>
          <p class="field-value">{html.escape(v1_main)}</p>
        </div>
        <div class="field">
          <p class="field-name">Slide Title</p>
          <p class="field-value">{html.escape(v1_title)}</p>
        </div>
      </div>
      <div class="panel panel-diff">
        <div class="diff-row">
          <p class="diff-name">Main Message</p>
          <p class="badge {main_class}">{main_state}</p>
        </div>
        <div class="field">
          <p class="field-name">V2</p>
          <p class="field-value">{html.escape(v2_main)}</p>
        </div>
        <div class="diff-row">
          <p class="diff-name">Slide Title</p>
          <p class="badge {title_class}">{title_state}</p>
        </div>
        <div class="field">
          <p class="field-name">V2</p>
          <p class="field-value">{html.escape(v2_title)}</p>
        </div>
      </div>
    </div>
  </section>"""


def render_html(v1_rows: dict[int, V1Row], v2_rows: dict[int, V2Row]) -> str:
    pages = sorted(set(v1_rows) | set(v2_rows))
    same_count = 0
    changed_count = 0
    cards = []
    for page in pages:
        v1 = v1_rows.get(page)
        v2 = v2_rows.get(page)
        main_same = (v1.main_message if v1 else None) == (v2.main_message if v2 else None)
        title_same = (v1.slide_title if v1 else None) == (v2.slide_title if v2 else None)
        if main_same and title_same:
            same_count += 1
        else:
            changed_count += 1
        cards.append(render_card(page, v1, v2))

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Header Copy Revision V1 vs V2</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  font-family: "Helvetica Neue", sans-serif;
  background: #f5f5f3;
  color: #1a1a1a;
  padding: 20px;
}}
.wrap {{
  max-width: 1180px;
  margin: 0 auto;
}}
h1 {{
  font-size: 18px;
  font-weight: 900;
  margin-bottom: 8px;
}}
.lead {{
  font-size: 13px;
  line-height: 1.7;
  color: rgba(0,0,0,.62);
  margin-bottom: 16px;
}}
.summary {{
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 18px;
}}
.summary-card {{
  background: #fff;
  border: 1px solid rgba(0,0,0,.1);
  border-radius: 8px;
  padding: 12px 14px;
}}
.summary-card__label {{
  font-size: 11px;
  color: rgba(0,0,0,.42);
  margin-bottom: 6px;
}}
.summary-card__value {{
  font-size: 24px;
  font-weight: 900;
}}
.cards {{
  display: flex;
  flex-direction: column;
  gap: 10px;
}}
.card {{
  background: #fff;
  border: 1px solid rgba(0,0,0,.1);
  border-radius: 8px;
  padding: 14px;
}}
.same-card {{
  border-color: rgba(0,0,0,.08);
}}
.changed-card {{
  border-color: rgba(0,0,0,.18);
}}
.card-head {{
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 12px;
}}
.page {{
  font-size: 10px;
  letter-spacing: 1.6px;
  color: rgba(0,0,0,.36);
  font-weight: 700;
  margin-bottom: 4px;
}}
.chapter {{
  font-size: 13px;
  font-weight: 700;
}}
.file {{
  font-size: 11px;
  color: rgba(0,0,0,.38);
}}
.compare-grid {{
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}}
.panel {{
  border: 1px solid rgba(0,0,0,.08);
  border-radius: 8px;
  padding: 12px;
  background: rgba(255,255,255,.72);
}}
.panel-diff {{
  background: rgba(0,0,0,.015);
}}
.panel-label {{
  font-size: 11px;
  font-weight: 700;
  color: rgba(0,0,0,.42);
  margin-bottom: 10px;
  letter-spacing: 1.2px;
}}
.field + .field {{
  margin-top: 12px;
}}
.field-name, .diff-name {{
  font-size: 11px;
  color: rgba(0,0,0,.45);
  margin-bottom: 5px;
}}
.field-value {{
  font-size: 15px;
  font-weight: 900;
  line-height: 1.45;
}}
.diff-row {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 6px;
}}
.badge {{
  font-size: 10px;
  font-weight: 900;
  letter-spacing: 1px;
  text-transform: uppercase;
  border-radius: 999px;
  padding: 4px 8px;
}}
.badge.same {{
  background: rgba(0,0,0,.06);
  color: rgba(0,0,0,.54);
}}
.badge.changed {{
  background: #111;
  color: #fff;
}}
@media (max-width: 900px) {{
  .summary {{ grid-template-columns: 1fr; }}
  .compare-grid {{ grid-template-columns: 1fr; }}
  .card-head {{ flex-direction: column; }}
}}
</style>
</head>
<body>
  <div class="wrap">
    <h1>Header Copy Revision: V1 vs V2</h1>
    <p class="lead">V1 = <code>header-copy-revision.md</code> の current mapping。V2 = <code>header-copy-revision-ver2.md</code> の proposed mapping。各 slide の main message と slide title を横並びで比較しています。</p>
    <div class="summary">
      <div class="summary-card">
        <p class="summary-card__label">Slides Compared</p>
        <p class="summary-card__value">{len(pages)}</p>
      </div>
      <div class="summary-card">
        <p class="summary-card__label">Fully Same</p>
        <p class="summary-card__value">{same_count}</p>
      </div>
      <div class="summary-card">
        <p class="summary-card__label">Changed</p>
        <p class="summary-card__value">{changed_count}</p>
      </div>
    </div>
    <div class="cards">
      {''.join(cards)}
    </div>
  </div>
</body>
</html>
"""


def main() -> int:
    v1_text = V1_PATH.read_text(encoding="utf-8")
    v2_text = V2_PATH.read_text(encoding="utf-8")
    v1_rows = parse_v1(v1_text)
    v2_rows = parse_v2(v2_text)
    OUT_PATH.write_text(render_html(v1_rows, v2_rows), encoding="utf-8")
    print(f"Wrote comparison HTML to {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
