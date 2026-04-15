#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path("/private/tmp/slides")

HEADER_PATTERN = re.compile(
    r"""<!-- === STANDARDIZED HEADER === -->\s*
<div style="position: absolute; left: 0; top: 0; width: 1280px; height: 148px; background-color: (?P<bg>[^;]+); z-index: 50;"></div>\s*
<div style="position: absolute; right: 80px; top: 16px; z-index: 55;">\s*
<p style="[^"]*background: (?P<pill_bg>[^;]+); display: inline-block;">(?P<pill_text>.*?)</p>\s*
</div>\s*
<div style="position: absolute; left: 80px; top: 22px; z-index: 55;">\s*
<p style="[^"]*">(?P<chapter>.*?)</p>\s*
</div>\s*
<div style="position: absolute; left: 80px; top: 52px; width: 1120px; z-index: 55;">\s*
<p style="[^"]*">(?P<title>.*?)</p>\s*
</div>\s*
<div style="position: absolute; left: 80px; top: 100px; width: 1120px; z-index: 55;">\s*
<p style="[^"]*">(?P<subtitle>.*?)</p>\s*
</div>\s*
<!-- === END HEADER === -->""",
    re.DOTALL,
)


def make_header(bg: str, pill_bg: str, pill_text: str, chapter: str, title: str, subtitle: str) -> str:
    return f"""<!-- === STANDARDIZED HEADER === -->
<div style="position: absolute; left: 0; top: 0; width: 1280px; height: var(--header-band-height); background-color: {bg}; z-index: 50;"></div>
<div style="position: absolute; right: 80px; top: var(--header-pill-top); z-index: 55;">
<p style="margin: 0; padding: 3px 12px; border: 2px solid #000; border-radius: 9999px; font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: var(--font-size-header-pill); color: #000; letter-spacing: 0.8px; background: {pill_bg}; display: inline-block; white-space: nowrap;">{pill_text}</p>
</div>
<div style="position: absolute; left: 80px; top: var(--header-text-top); width: 960px; z-index: 55; display: flex; flex-direction: column; align-items: flex-start; gap: var(--header-text-gap);">
<p style="margin: 0; font-family: 'Noto Sans JP', sans-serif; font-weight: 400; font-size: var(--font-size-header-chapter); color: #999; letter-spacing: 0.5px; white-space: nowrap;">{chapter}</p>
<p style="margin: 0; font-family: 'Noto Sans JP', sans-serif; font-weight: 900; font-size: var(--font-size-header-title); color: #000; letter-spacing: var(--letter-spacing-header-title); line-height: var(--line-height-header-title); white-space: nowrap;">{title}</p>
<p style="margin: 0; font-family: 'Noto Sans JP', sans-serif; font-weight: 400; font-size: var(--font-size-header-subtitle); color: #888; line-height: var(--line-height-header-subtitle); white-space: nowrap;">{subtitle}</p>
</div>
<!-- === END HEADER === -->"""


for path in sorted(ROOT.glob("slide_*.html")):
    html = path.read_text(encoding="utf-8")
    match = HEADER_PATTERN.search(html)
    if not match:
        continue
    new_header = make_header(
        match.group("bg"),
        match.group("pill_bg"),
        match.group("pill_text"),
        match.group("chapter"),
        match.group("title"),
        match.group("subtitle"),
    )
    updated = HEADER_PATTERN.sub(new_header, html, count=1)
    if updated != html:
        path.write_text(updated, encoding="utf-8")
