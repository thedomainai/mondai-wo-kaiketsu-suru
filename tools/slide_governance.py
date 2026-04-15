#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import html
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs" / "ai-slide-system"
MANIFEST_PATH = DOCS_DIR / "deck-manifest.yaml"
KINDS_PATH = DOCS_DIR / "slide-kinds.yaml"
LEGACY_MAP_PATH = DOCS_DIR / "legacy-map.yaml"
REVIEW_RULES_PATH = DOCS_DIR / "review-rules.yaml"
DEFAULT_QA_REPORT_PATH = DOCS_DIR / "qa-report.md"

SLIDE_GLOB = "slide_*.html"
SLIDE_NAME_RE = re.compile(r"slide_(\d+)\.html$")
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
TITLE_SUFFIX_RE = re.compile(r"\s+-\s+.+$")
CONTAINER_RE = re.compile(r'(<div\b[^>]*class="slide-container\b[^"]*"[^>]*)(>)', re.IGNORECASE)
ATTR_RE = re.compile(r'([:\w-]+)="([^"]*)"')
AGENDA_LIST_BLOCK_RE = re.compile(
    r'(?P<open><div class="agenda-panel__list">)\s*(?P<body>.*?)(?P<close>\n\s{4}</div>\s*\n\s{2}</div>)',
    re.DOTALL,
)
AGENDA_ROW_RE = re.compile(
    r'<div class="agenda-panel__row(?P<row_mods>[^"]*)">\s*'
    r'<span class="agenda-panel__index(?P<index_mods>[^"]*)">(?P<index>.*?)</span>\s*'
    r'<span class="agenda-panel__item(?P<item_mods>[^"]*)">(?P<label>.*?)</span>'
    r'(?:\s*<span class="agenda-panel__duration">(?P<duration>.*?)</span>)?\s*'
    r'</div>',
    re.DOTALL,
)
FOOTER_META_P_RE = re.compile(
    r"(<p[^>]*font-size:\s*var\(--font-size-footer-meta\)[^>]*>)(.*?)(</p>)",
    re.IGNORECASE | re.DOTALL,
)
STANDARD_FOOTER_RE = re.compile(r'(data-footer="standard")(?:\s+data-footer-page="[^"]*")?')
RELATIVE_ASSET_RE = re.compile(r'''(?:src|href)=["'](?P<path>\./[^"']+)["']''')
CSS_URL_RE = re.compile(r"""url\((?:'|")?(?P<path>\./[^)'"]+)(?:'|")?\)""")
TOTAL_SLIDES_RE = re.compile(r"TOTAL_SLIDES\s*=\s*(\d+)")

CANONICAL_KINDS = [
    "cover",
    "intro",
    "agenda",
    "divider",
    "center-title",
    "content",
    "summary",
    "closing",
    "cta",
    "qa",
]

RUNTIME_SHAPE_BY_KIND = {
    "cover": "custom",
    "intro": "custom",
    "agenda": "agenda",
    "divider": "divider",
    "center-title": "center-title",
    "content": "content",
    "summary": "custom",
    "closing": "custom",
    "cta": "custom",
    "qa": "custom",
}

CUSTOM_KIND_BY_FILE = {
    "slide_01.html": "cover",
    "slide_02.html": "intro",
    "slide_03.html": "intro",
    "slide_04.html": "intro",
    "slide_71.html": "summary",
    "slide_72.html": "closing",
    "slide_73.html": "cta",
    "slide_74.html": "qa",
}

LEGACY_EXCEPTIONS_BY_FILE = {
    "slide_01.html": ["manual-cover-layout", "no-standard-footer"],
    "slide_02.html": ["manual-intro-layout", "manual-footer"],
    "slide_03.html": ["manual-intro-layout", "manual-footer"],
    "slide_04.html": ["manual-intro-layout", "manual-footer"],
    "slide_05.html": ["timed-deck-agenda"],
    "slide_70.html": ["summary-agenda-without-divider"],
    "slide_71.html": ["manual-header-reimplementation", "manual-footer-reimplementation"],
    "slide_72.html": ["manual-closing-layout", "manual-footer-reimplementation"],
    "slide_73.html": ["manual-cta-layout", "manual-footer-reimplementation"],
    "slide_74.html": ["manual-qa-layout", "manual-footer-reimplementation"],
}

SECTION_DEFINITIONS = [
    {
        "id": "section-01-work",
        "number": 1,
        "title": "ワーク",
        "agenda_file": "slide_06.html",
        "divider_file": "slide_07.html",
        "slide_files": ["slide_08.html", "slide_09.html", "slide_10.html", "slide_11.html"],
    },
    {
        "id": "section-02-background",
        "number": 2,
        "title": "前提・背景",
        "agenda_file": "slide_12.html",
        "divider_file": "slide_13.html",
        "slide_files": ["slide_14.html", "slide_15.html", "slide_16.html", "slide_17.html", "slide_18.html"],
    },
    {
        "id": "section-03-overview",
        "number": 3,
        "title": "問題解決の概要",
        "agenda_file": "slide_19.html",
        "divider_file": "slide_20.html",
        "slide_files": [
            "slide_21.html",
            "slide_22.html",
            "slide_23.html",
            "slide_24.html",
            "slide_25.html",
            "slide_26.html",
        ],
    },
    {
        "id": "section-04-issue-definition",
        "number": 4,
        "title": "論点を定義する",
        "agenda_file": "slide_27.html",
        "divider_file": "slide_28.html",
        "slide_files": ["slide_29.html", "slide_30.html", "slide_31.html", "slide_32.html"],
    },
    {
        "id": "section-05-decomposition",
        "number": 5,
        "title": "論点を分解する",
        "agenda_file": None,
        "divider_file": "slide_33.html",
        "slide_files": [
            "slide_34.html",
            "slide_35.html",
            "slide_36.html",
            "slide_37.html",
            "slide_38.html",
            "slide_39.html",
            "slide_40.html",
            "slide_41.html",
        ],
    },
    {
        "id": "section-06-hypothesis",
        "number": 6,
        "title": "仮説を構築する",
        "agenda_file": "slide_42.html",
        "divider_file": "slide_43.html",
        "slide_files": ["slide_44.html", "slide_45.html", "slide_46.html", "slide_47.html", "slide_48.html", "slide_49.html", "slide_50.html"],
    },
    {
        "id": "section-07-validation",
        "number": 7,
        "title": "論点と仮説を検証する",
        "agenda_file": "slide_51.html",
        "divider_file": "slide_52.html",
        "slide_files": ["slide_53.html", "slide_54.html", "slide_55.html", "slide_56.html", "slide_57.html"],
    },
    {
        "id": "section-08-communication",
        "number": 8,
        "title": "問題解決におけるコミュニケーション",
        "agenda_file": "slide_58.html",
        "divider_file": "slide_59.html",
        "slide_files": [
            "slide_60.html",
            "slide_61.html",
            "slide_62.html",
            "slide_63.html",
            "slide_64.html",
            "slide_65.html",
            "slide_66.html",
            "slide_67.html",
            "slide_68.html",
            "slide_69.html",
        ],
    },
    {
        "id": "section-09-summary",
        "number": 9,
        "title": "まとめ",
        "agenda_file": "slide_70.html",
        "divider_file": None,
        "slide_files": ["slide_71.html", "slide_72.html", "slide_73.html", "slide_74.html"],
    },
]

SMOKE_SAMPLE_ORDER = ["content", "agenda", "divider", "center-title", "summary", "qa"]

DECK_OVERVIEW_AGENDA_ITEMS = [
    {"index": "01", "label": "ワーク", "state": "timed", "duration": "10 min"},
    {"index": "02", "label": "前提・背景", "state": "timed", "duration": "10 min"},
    {"index": "03", "label": "問題解決の概要", "state": "timed", "duration": "5 min"},
    {"index": "04", "label": "論点を定義する", "state": "timed", "duration": "10 min"},
    {"index": "05", "label": "論点を分解する", "state": "timed", "duration": "20 min"},
    {"index": "06", "label": "仮説を構築する", "state": "timed", "duration": "15 min"},
    {"index": "07", "label": "論点と仮説を検証する", "state": "timed", "duration": "15 min"},
    {"index": "08", "label": "問題解決におけるコミュニケーション", "state": "timed", "duration": "15 min"},
    {"index": "09", "label": "Q&A", "state": "timed", "duration": "20 min"},
]

SECTION_PROGRESS_AGENDA_ITEMS = [
    ("01", "ワーク"),
    ("02", "前提・背景"),
    ("03", "問題解決の概要"),
    ("04", "論点を定義する"),
    ("05", "論点を分解する"),
    ("06", "仮説を構築する"),
    ("07", "論点と仮説を検証する"),
    ("08", "問題解決におけるコミュニケーション"),
    ("09", "まとめ"),
]


@dataclass
class Finding:
    severity: str
    code: str
    message: str
    file: str | None = None


def normalize_whitespace(text: str) -> str:
    return " ".join(text.replace("<br/>", " ").replace("<br>", " ").split())


def normalize_title(title: str) -> str:
    return TITLE_SUFFIX_RE.sub("", html.unescape(normalize_whitespace(title))).strip()


def discover_slide_paths(root: Path = ROOT) -> list[Path]:
    slide_paths = sorted(root.glob(SLIDE_GLOB), key=slide_sort_key)
    invalid = [path.name for path in slide_paths if not SLIDE_NAME_RE.fullmatch(path.name)]
    if invalid:
        raise RuntimeError(
            "Slide filenames must use numeric sequential names only: " + ", ".join(invalid)
        )

    actual_numbers = [int(SLIDE_NAME_RE.fullmatch(path.name).group(1)) for path in slide_paths]
    expected_numbers = list(range(1, len(slide_paths) + 1))
    if actual_numbers != expected_numbers:
        raise RuntimeError(
            "Slide filenames must be contiguous: expected "
            + ", ".join(f"slide_{n:02d}.html" for n in expected_numbers)
        )
    return slide_paths


def slide_sort_key(slide_path: Path) -> int:
    match = SLIDE_NAME_RE.search(slide_path.name)
    return int(match.group(1)) if match else 10**9


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_title(path: Path) -> str:
    text = read_text(path)
    match = TITLE_RE.search(text)
    if not match:
        raise RuntimeError(f"<title> not found in {path}")
    return normalize_title(match.group(1))


def parse_container_attrs(text: str) -> dict[str, str]:
    match = CONTAINER_RE.search(text)
    if not match:
        return {}
    return {key: value for key, value in ATTR_RE.findall(match.group(1))}


def detect_runtime_shape(text: str) -> str:
    if "agenda-panel" in text:
        return "agenda"
    if 'data-divider-title=' in text:
        return "divider"
    if "slide-center-title" in text:
        return "center-title"
    if 'data-header-title=' in text:
        return "content"
    return "custom"


def canonical_kind_for(path: Path, runtime_shape: str) -> str:
    if path.name in CUSTOM_KIND_BY_FILE:
        return CUSTOM_KIND_BY_FILE[path.name]
    mapping = {
        "agenda": "agenda",
        "divider": "divider",
        "center-title": "center-title",
        "content": "content",
        "custom": "content",
    }
    return mapping[runtime_shape]


def build_section_lookup() -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    for section in SECTION_DEFINITIONS:
        for key in ("agenda_file", "divider_file"):
            slide_file = section.get(key)
            if slide_file:
                lookup[slide_file] = section
        for slide_file in section["slide_files"]:
            lookup[slide_file] = section
    return lookup


def page_label_for_order(order: int) -> str | None:
    if order == 1:
        return None
    return f"{order - 1:02d}"


def index_type_for_entry(kind: str, slide_file: str) -> str:
    if kind == "divider":
        return "chapter-title"
    if kind == "agenda" and slide_file != "slide_05.html":
        return "chapter-agenda"
    return "normal"


def extract_agenda_spec(text: str) -> dict[str, Any] | None:
    match = AGENDA_LIST_BLOCK_RE.search(text)
    if not match:
        return None

    items = []
    for row_match in AGENDA_ROW_RE.finditer(match.group("body")):
        row_mods = row_match.group("row_mods") or ""
        index_mods = row_match.group("index_mods") or ""
        item_mods = row_match.group("item_mods") or ""
        state = "normal"
        if "--active" in row_mods or "--active" in index_mods or "--active" in item_mods:
            state = "active"
        elif "--timed" in row_mods or "--timed" in index_mods or "--timed" in item_mods:
            state = "timed"
        elif "--soft" in item_mods:
            state = "soft"

        items.append(
            {
                "index": normalize_whitespace(row_match.group("index")),
                "label": normalize_whitespace(row_match.group("label")),
                "state": state,
                "duration": normalize_whitespace(row_match.group("duration")) if row_match.group("duration") else None,
            }
        )

    mode = "timed-overview" if any(item["state"] == "timed" for item in items) else "progress"
    active_item = next((item["index"] for item in items if item["state"] == "active"), None)
    return {"mode": mode, "active_item": active_item, "items": items}


def deck_overview_agenda() -> dict[str, Any]:
    return {
        "mode": "timed-overview",
        "active_item": None,
        "items": [dict(item) for item in DECK_OVERVIEW_AGENDA_ITEMS],
    }


def section_progress_agenda(active_number: int) -> dict[str, Any]:
    items = []
    for index, label in SECTION_PROGRESS_AGENDA_ITEMS:
        number = int(index)
        if number == active_number:
            state = "active"
        elif number < active_number:
            state = "normal"
        else:
            state = "soft"
        items.append({"index": index, "label": label, "state": state, "duration": None})
    return {"mode": "progress", "active_item": f"{active_number:02d}", "items": items}


def render_agenda_items(agenda: dict[str, Any]) -> str:
    lines = []
    items = agenda["items"]
    for idx, item in enumerate(items):
        row_classes = ["agenda-panel__row"]
        index_classes = ["agenda-panel__index"]
        item_classes = ["agenda-panel__item"]
        if item["state"] == "active":
            row_classes.append("agenda-panel__row--active")
            index_classes.append("agenda-panel__index--active")
            item_classes.append("agenda-panel__item--active")
        elif item["state"] == "timed":
            row_classes.append("agenda-panel__row--timed")
            index_classes.append("agenda-panel__index--timed")
            item_classes.append("agenda-panel__item--timed")
        elif item["state"] == "soft":
            item_classes.append("agenda-panel__item--soft")
        if idx == len(items) - 1:
            row_classes.append("agenda-panel__row--last")

        lines.append(f'      <div class="{" ".join(row_classes)}">')
        lines.append(
            f'        <span class="{" ".join(index_classes)}">{item["index"]}</span>'
        )
        lines.append(
            f'        <span class="{" ".join(item_classes)}">{item["label"]}</span>'
        )
        if item.get("duration"):
            lines.append(f'        <span class="agenda-panel__duration">{item["duration"]}</span>')
        lines.append("      </div>")
        lines.append("")
    if lines:
        lines.pop()
    return "\n".join(lines)


def build_slide_entries(root: Path = ROOT) -> list[dict[str, Any]]:
    section_lookup = build_section_lookup()
    slides = []
    for order, path in enumerate(discover_slide_paths(root), start=1):
        text = read_text(path)
        runtime_shape = detect_runtime_shape(text)
        kind = canonical_kind_for(path, runtime_shape)
        section = section_lookup.get(path.name)
        title = extract_title(path)
        entry: dict[str, Any] = {
            "order": order,
            "file": path.name,
            "page_label": page_label_for_order(order),
            "kind": kind,
            "runtime_shape": runtime_shape,
            "title": title,
            "index_title": title,
            "index_type": index_type_for_entry(kind, path.name),
            "section_id": section["id"] if section else None,
            "section_title": section["title"] if section else None,
        }
        if kind == "agenda":
            if path.name == "slide_05.html":
                entry["agenda"] = deck_overview_agenda()
            elif section:
                entry["agenda"] = section_progress_agenda(section["number"])
            else:
                entry["agenda"] = extract_agenda_spec(text)
        if path.name in LEGACY_EXCEPTIONS_BY_FILE:
            entry["legacy_exceptions"] = LEGACY_EXCEPTIONS_BY_FILE[path.name]
        slides.append(entry)
    return slides


def build_manifest_data(root: Path = ROOT) -> dict[str, Any]:
    slides = build_slide_entries(root)
    counts = Counter(slide["kind"] for slide in slides)
    agenda_slides = [
        {
            "file": slide["file"],
            "mode": slide["agenda"]["mode"],
            "active_item": slide["agenda"]["active_item"],
            "items": copy.deepcopy(slide["agenda"]["items"]),
        }
        for slide in slides
        if slide["kind"] == "agenda" and slide.get("agenda")
    ]
    chapters = []
    for section in SECTION_DEFINITIONS:
        chapter_slides = [
            slide["file"]
            for slide in slides
            if slide["section_id"] == section["id"]
        ]
        chapters.append(
            {
                "id": section["id"],
                "number": section["number"],
                "title": section["title"],
                "agenda_file": section["agenda_file"],
                "divider_file": section["divider_file"],
                "slide_files": chapter_slides,
            }
        )

    return {
        "deck": {
            "id": "problem-solving-framework",
            "title": "問題を解決する",
            "subtitle": "問題解決フレームワークの原理原則と実践",
            "language": "ja",
            "runtime": {
                "format": "html",
                "width": 1280,
                "height": 720,
                "shared_css": "slides.css",
                "shared_js": "slides.js",
            },
            "page_numbering": {
                "cover_file": "slide_01.html",
                "first_labeled_file": "slide_02.html",
                "label_format": "zero-padded-2",
                "max_label": page_label_for_order(len(slides)),
            },
            "agenda_source": "manifest.slides[].agenda",
            "allowed_slide_kinds": CANONICAL_KINDS,
        },
        "counts": {
            "total_slides": len(slides),
            "by_kind": {kind: counts[kind] for kind in CANONICAL_KINDS if counts[kind]},
        },
        "chapters": chapters,
        "agendas": agenda_slides,
        "slides": slides,
    }


def build_legacy_map_data(root: Path = ROOT) -> dict[str, Any]:
    slides = build_slide_entries(root)
    return {
        "deck": {
            "total_slides": len(slides),
            "runtime_shapes": sorted({slide["runtime_shape"] for slide in slides}),
            "ssot": {
                "shared_css": "slides.css",
                "shared_js": "slides.js",
                "manifest": "docs/ai-slide-system/deck-manifest.yaml",
            },
        },
        "legacy_scripts": [
            {
                "file": "standardize_headers.py",
                "role": "legacy-migration",
                "declared_total_slides": extract_declared_total_slides(ROOT / "standardize_headers.py"),
            },
            {
                "file": "standardize_headers_v2.py",
                "role": "legacy-migration",
                "declared_total_slides": extract_declared_total_slides(ROOT / "standardize_headers_v2.py"),
            },
        ],
        "slides": {
            slide["file"]: {
                "canonical_kind": slide["kind"],
                "runtime_shape": slide["runtime_shape"],
                "section_id": slide["section_id"],
                "page_label": slide["page_label"],
                "legacy_exceptions": slide.get("legacy_exceptions", []),
            }
            for slide in slides
        },
    }


def extract_declared_total_slides(path: Path) -> int | None:
    if not path.exists():
        return None
    match = TOTAL_SLIDES_RE.search(read_text(path))
    return int(match.group(1)) if match else None


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
    )


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def ensure_attr(tag: str, attr: str, value: str) -> str:
    if re.search(rf'{re.escape(attr)}="[^"]*"', tag):
        return re.sub(rf'{re.escape(attr)}="[^"]*"', f'{attr}="{value}"', tag)
    return f'{tag} {attr}="{value}"'


def sync_slide_kinds(root: Path = ROOT, manifest: dict[str, Any] | None = None) -> int:
    manifest = manifest or load_yaml(MANIFEST_PATH)
    updated = 0
    for slide in manifest["slides"]:
        path = root / slide["file"]
        text = read_text(path)
        match = CONTAINER_RE.search(text)
        if not match:
            continue
        new_tag = ensure_attr(match.group(1), "data-slide-kind", slide["kind"])
        if new_tag != match.group(1):
            new_text = text[: match.start(1)] + new_tag + text[match.end(1) :]
            path.write_text(new_text, encoding="utf-8")
            updated += 1
    return updated


def sync_agenda_slides(root: Path = ROOT, manifest: dict[str, Any] | None = None) -> int:
    manifest = manifest or load_yaml(MANIFEST_PATH)
    updated = 0
    for slide in manifest["slides"]:
        if slide["kind"] != "agenda" or not slide.get("agenda"):
            continue
        path = root / slide["file"]
        text = read_text(path)
        rendered = render_agenda_items(slide["agenda"])
        match = AGENDA_LIST_BLOCK_RE.search(text)
        if not match:
            continue
        new_text = text[: match.start("body")] + rendered + text[match.end("body") :]
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            updated += 1
    return updated


def render_index_slides(manifest: dict[str, Any]) -> str:
    lines = ["// BEGIN GENERATED SLIDES", "const slides = ["]
    for slide in manifest["slides"]:
        title = json.dumps(slide["index_title"], ensure_ascii=False)
        slide_type = json.dumps(slide["index_type"], ensure_ascii=False)
        slide_file = json.dumps(slide["file"], ensure_ascii=False)
        lines.append(
            f"  {{ title: {title}, type: {slide_type}, file: {slide_file} }},"
        )
    lines.extend(["];", "// END GENERATED SLIDES"])
    return "\n".join(lines)


def relative_asset_paths(text: str) -> list[str]:
    paths = [match.group("path") for match in RELATIVE_ASSET_RE.finditer(text)]
    paths.extend(match.group("path") for match in CSS_URL_RE.finditer(text))
    return sorted(set(paths))


def find_missing_assets(root: Path, text: str) -> list[str]:
    missing = []
    for rel_path in relative_asset_paths(text):
        if rel_path.startswith("./"):
            target = root / rel_path[2:]
            if not target.exists():
                missing.append(rel_path)
    return missing


def load_kind_specs() -> dict[str, Any]:
    return load_yaml(KINDS_PATH)["kinds"]


def load_legacy_map() -> dict[str, Any]:
    return load_yaml(LEGACY_MAP_PATH)


def has_inline_footer_reimplementation(text: str) -> bool:
    return "LOGICAL THINKING TRAINING" in text and 'data-footer="standard"' not in text


def has_inline_header_reimplementation(text: str) -> bool:
    return "PROBLEM SOLVING" in text and 'data-header-title=' not in text


def validate_kind_contract(slide: dict[str, Any], text: str, kind_spec: dict[str, Any], root: Path) -> list[Finding]:
    findings: list[Finding] = []
    attrs = parse_container_attrs(text)
    slide_file = slide["file"]

    for attr in kind_spec.get("required_container_attrs", []):
        if attr not in attrs:
            findings.append(Finding("error", "missing-required-attr", f"Missing `{attr}` on slide container", slide_file))

    for attr, expected in kind_spec.get("required_attr_values", {}).items():
        actual = attrs.get(attr)
        if actual != expected:
            findings.append(
                Finding(
                    "error",
                    "unexpected-attr-value",
                    f"Expected `{attr}={expected}` but found `{actual}`",
                    slide_file,
                )
            )

    for marker in kind_spec.get("required_markers", []):
        if marker not in text:
            findings.append(Finding("error", "missing-required-marker", f"Expected marker `{marker}`", slide_file))

    for marker in kind_spec.get("forbidden_markers", []):
        if marker in text:
            findings.append(Finding("error", "forbidden-marker", f"Found forbidden marker `{marker}`", slide_file))

    allowed_backgrounds = kind_spec.get("allowed_backgrounds")
    if allowed_backgrounds:
        background = attrs.get("data-background", "none")
        if background not in allowed_backgrounds:
            findings.append(
                Finding(
                    "error",
                    "invalid-background",
                    f"Background `{background}` is not allowed for kind `{slide['kind']}`",
                    slide_file,
                )
            )

    if slide["kind"] == "content":
        if has_inline_footer_reimplementation(text):
            findings.append(Finding("error", "inline-footer-reimplementation", "Content slides must not hand-roll footer markup", slide_file))
        if has_inline_header_reimplementation(text):
            findings.append(Finding("error", "inline-header-reimplementation", "Content slides must not hand-roll header markup", slide_file))

    missing_assets = find_missing_assets(root, text)
    for rel_path in missing_assets:
        findings.append(Finding("error", "missing-asset", f"Missing asset `{rel_path}`", slide_file))

    return findings


def validate_page_number(slide: dict[str, Any], text: str) -> list[Finding]:
    findings: list[Finding] = []
    expected = slide["page_label"]
    if not expected:
        return findings

    slide_file = slide["file"]
    attrs = parse_container_attrs(text)
    if attrs.get("data-footer") == "standard":
        actual = attrs.get("data-footer-page")
        if actual != expected:
            findings.append(Finding("error", "page-number-drift", f"Expected `data-footer-page={expected}` but found `{actual}`", slide_file))
        return findings

    matches = list(FOOTER_META_P_RE.finditer(text))
    if matches:
        actual = normalize_whitespace(matches[-1].group(2))
        if actual != expected:
            findings.append(Finding("error", "manual-footer-page-drift", f"Expected footer page `{expected}` but found `{actual}`", slide_file))
    return findings


def validate_agenda_source(slide: dict[str, Any], text: str) -> list[Finding]:
    findings: list[Finding] = []
    if slide["kind"] != "agenda" or not slide.get("agenda"):
        return findings
    current = extract_agenda_spec(text)
    if current != slide["agenda"]:
        findings.append(
            Finding(
                "error",
                "agenda-drift",
                "Agenda rows do not match the manifest-backed agenda source",
                slide["file"],
            )
        )
    return findings


def validate_inventory(root: Path, manifest: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    actual_files = [path.name for path in discover_slide_paths(root)]
    manifest_files = [slide["file"] for slide in manifest["slides"]]
    if actual_files != manifest_files:
        findings.append(Finding("error", "manifest-file-order-drift", "Manifest slide order does not match on-disk slide order"))

    manifest_counts = manifest["counts"]["by_kind"]
    actual_counts = Counter(slide["kind"] for slide in manifest["slides"])
    for kind in CANONICAL_KINDS:
        expected = manifest_counts.get(kind, 0)
        actual = actual_counts.get(kind, 0)
        if expected != actual:
            findings.append(Finding("error", "manifest-kind-count-drift", f"Kind `{kind}` expected {expected} but found {actual}"))
    return findings


def validate_stale_totals(root: Path, manifest: dict[str, Any], legacy_map: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    total = manifest["counts"]["total_slides"]
    legacy_files = {item["file"] for item in legacy_map.get("legacy_scripts", [])}
    for path in sorted(root.glob("*.py")):
        text = read_text(path)
        match = TOTAL_SLIDES_RE.search(text)
        if not match:
            continue
        declared = int(match.group(1))
        if declared == total:
            continue
        severity = "warning" if path.name in legacy_files else "error"
        findings.append(
            Finding(
                severity,
                "stale-total-slides",
                f"`TOTAL_SLIDES` declares {declared}, expected canonical deck total {total}",
                path.name,
            )
        )
    return findings


def audit_deck(root: Path = ROOT) -> list[Finding]:
    manifest = load_yaml(MANIFEST_PATH)
    kind_specs = load_kind_specs()
    legacy_map = load_legacy_map()
    findings: list[Finding] = []
    findings.extend(validate_inventory(root, manifest))

    for slide in manifest["slides"]:
        path = root / slide["file"]
        text = read_text(path)
        kind_spec = kind_specs[slide["kind"]]
        findings.extend(validate_kind_contract(slide, text, kind_spec, root))
        findings.extend(validate_page_number(slide, text))
        findings.extend(validate_agenda_source(slide, text))

    findings.extend(validate_stale_totals(root, manifest, legacy_map))
    return findings


def render_markdown_report(manifest: dict[str, Any], findings: list[Finding]) -> str:
    severity_order = {"error": 0, "warning": 1, "info": 2}
    findings = sorted(findings, key=lambda item: (severity_order[item.severity], item.file or "", item.code))
    lines = [
        "# AI Slide System QA Report",
        "",
        f"- Deck: `{manifest['deck']['title']}`",
        f"- Total slides: `{manifest['counts']['total_slides']}`",
        f"- Findings: `{len(findings)}`",
        "",
        "## Inventory",
        "",
    ]
    for kind, count in manifest["counts"]["by_kind"].items():
        lines.append(f"- `{kind}`: `{count}`")

    lines.extend(["", "## Findings", ""])
    if not findings:
        lines.append("- No findings.")
        return "\n".join(lines) + "\n"

    for finding in findings:
        location = f" `{finding.file}`" if finding.file else ""
        lines.append(f"- **{finding.severity.upper()}** `{finding.code}`{location}: {finding.message}")
    return "\n".join(lines) + "\n"


def write_manifest_bundle(root: Path = ROOT) -> None:
    write_yaml(MANIFEST_PATH, build_manifest_data(root))
    write_yaml(LEGACY_MAP_PATH, build_legacy_map_data(root))


def sync_repo(root: Path = ROOT) -> None:
    write_manifest_bundle(root)
    manifest = load_yaml(MANIFEST_PATH)
    sync_slide_kinds(root, manifest)
    sync_agenda_slides(root, manifest)


def write_qa_report(root: Path = ROOT, report_path: Path = DEFAULT_QA_REPORT_PATH) -> list[Finding]:
    manifest = load_yaml(MANIFEST_PATH)
    findings = audit_deck(root)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_markdown_report(manifest, findings), encoding="utf-8")
    return findings


def build_smoke_slide(kind: str, page_label: str) -> str:
    if kind == "content":
        return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Smoke Content</title>
<link href="./slides.css" rel="stylesheet"/>
<script defer src="./slides.js"></script>
</head>
<body>
<div class="slide-container slide-theme-paper" data-slide-kind="content" data-header-chapter="Smoke" data-header-title="Content" data-header-subtitle="Manifest contract" data-footer="standard" data-footer-page="{page_label}">
  <div style="position:absolute; left:80px; top:220px; width:1120px;">
    <p class="ui-kicker">SMOKE</p>
    <p class="ui-display-30">Content contract</p>
  </div>
</div>
</body>
</html>
"""
    if kind == "agenda":
        agenda = {
            "items": [
                {"index": "01", "label": "Intro", "state": "normal", "duration": None},
                {"index": "02", "label": "Now", "state": "active", "duration": None},
                {"index": "03", "label": "Next", "state": "soft", "duration": None},
            ]
        }
        return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Smoke Agenda</title>
<link href="./slides.css" rel="stylesheet"/>
<script defer src="./slides.js"></script>
</head>
<body>
<div class="slide-container slide-theme-mist" data-slide-kind="agenda" data-background="grain" data-grain-opacity="0.5" data-vignette="true">
  <div class="agenda-panel">
    <p class="agenda-panel__eyebrow">Agenda</p>
    <h1 class="agenda-panel__title agenda-panel__title--spaced">アジェンダ</h1>
  </div>
  <div class="agenda-panel__list-wrap">
    <div class="agenda-panel__list">
{render_agenda_items(agenda)}
    </div>
  </div>
</div>
</body>
</html>
"""
    if kind == "divider":
        return """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Smoke Divider</title>
<link href="./slides.css" rel="stylesheet"/>
<script defer src="./slides.js"></script>
</head>
<body>
<div class="slide-container slide-theme-mist" data-slide-kind="divider" data-background="halftone" data-divider-brand="Smoke Deck" data-divider-index="99" data-divider-kicker="Chapter 99" data-divider-title="Divider" data-divider-subtitle="Contract test">
</div>
</body>
</html>
"""
    if kind == "center-title":
        return """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Smoke Center Title</title>
<link href="./slides.css" rel="stylesheet"/>
<script defer src="./slides.js"></script>
</head>
<body>
<div class="slide-container slide-theme-paper slide-center-title" data-slide-kind="center-title">
  <div class="content">
    <div class="inner">
      <p class="chapter">Smoke</p>
      <p class="title">Center Title</p>
      <p class="subtitle">Contract test</p>
    </div>
  </div>
</div>
</body>
</html>
"""
    if kind == "summary":
        return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Smoke Summary</title>
<link href="./slides.css" rel="stylesheet"/>
<script defer src="./slides.js"></script>
</head>
<body>
<div class="slide-container slide-theme-paper" data-slide-kind="summary">
  <div style="position:absolute; left:80px; top:160px; width:1120px;">
    <p class="ui-kicker">SUMMARY</p>
    <p class="ui-display-30">Summary contract</p>
  </div>
  <div style="position:absolute; left:0; top:660px; width:1280px; height:60px; background:#ffffff; z-index:50;"></div>
  <div style="position:absolute; left:80px; top:680px; z-index:55;">
    <p style="margin:0; font-family:'Space Grotesk',sans-serif; font-weight:600; font-size:var(--font-size-footer-meta); color:#bbb; letter-spacing:1.5px;">LOGICAL THINKING TRAINING</p>
  </div>
  <div style="position:absolute; right:80px; top:680px; z-index:55;">
    <p style="margin:0; font-family:'Space Grotesk',sans-serif; font-weight:600; font-size:var(--font-size-footer-meta); color:#bbb; letter-spacing:0.5px;">{page_label}</p>
  </div>
</div>
</body>
</html>
"""
    if kind == "qa":
        return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Smoke QA</title>
<link href="./slides.css" rel="stylesheet"/>
<script defer src="./slides.js"></script>
</head>
<body>
<div class="slide-container slide-theme-paper" data-slide-kind="qa">
  <div style="position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:18px; text-align:center;">
    <p style="font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:14px; letter-spacing:2px; color:rgba(0,0,0,0.34);">FINAL</p>
    <p style="font-family:'Space Grotesk',sans-serif; font-weight:900; font-size:92px; line-height:1; color:var(--soft-black);">Q&amp;A</p>
  </div>
  <div style="position:absolute; left:0; top:660px; width:1280px; height:60px; background:#ffffff; z-index:50;"></div>
  <div style="position:absolute; left:80px; top:680px; z-index:55;">
    <p style="margin:0; font-family:'Space Grotesk',sans-serif; font-weight:600; font-size:var(--font-size-footer-meta); color:#bbb; letter-spacing:1.5px;">LOGICAL THINKING TRAINING</p>
  </div>
  <div style="position:absolute; right:80px; top:680px; z-index:55;">
    <p style="margin:0; font-family:'Space Grotesk',sans-serif; font-weight:600; font-size:var(--font-size-footer-meta); color:#bbb; letter-spacing:0.5px;">{page_label}</p>
  </div>
</div>
</body>
</html>
"""
    raise ValueError(f"Unsupported smoke slide kind: {kind}")


def write_smoke_samples(out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    generated = []
    for order, kind in enumerate(SMOKE_SAMPLE_ORDER, start=1):
        page_label = f"{order:02d}"
        path = out_dir / f"smoke_{order:02d}_{kind.replace('-', '_')}.html"
        path.write_text(build_smoke_slide(kind, page_label), encoding="utf-8")
        generated.append(path)
    return generated


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Slide governance utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("sync-docs", help="Generate deck manifest and legacy map from the current deck")
    subparsers.add_parser("sync-slide-kinds", help="Sync data-slide-kind onto slide containers")
    subparsers.add_parser("sync-agendas", help="Rewrite agenda slide rows from the manifest")
    subparsers.add_parser("sync", help="Generate docs and sync slide metadata")

    qa_parser = subparsers.add_parser("qa", help="Run deterministic QA checks")
    qa_parser.add_argument("--report", default=str(DEFAULT_QA_REPORT_PATH), help="Markdown report output path")

    smoke_parser = subparsers.add_parser("smoke-test", help="Generate sample slides for authoring smoke tests")
    smoke_parser.add_argument("--out-dir", required=True, help="Output directory for generated sample slides")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "sync-docs":
        write_manifest_bundle(ROOT)
        return 0
    if args.command == "sync-slide-kinds":
        updated = sync_slide_kinds(ROOT)
        print(f"Updated {updated} slides with data-slide-kind")
        return 0
    if args.command == "sync-agendas":
        updated = sync_agenda_slides(ROOT)
        print(f"Updated {updated} agenda slides from manifest")
        return 0
    if args.command == "sync":
        sync_repo(ROOT)
        print("Generated manifest/legacy map and synced slide kinds/agendas")
        return 0
    if args.command == "qa":
        findings = write_qa_report(ROOT, Path(args.report))
        print(f"Wrote QA report with {len(findings)} finding(s) to {args.report}")
        return 0 if not any(finding.severity == "error" for finding in findings) else 1
    if args.command == "smoke-test":
        generated = write_smoke_samples(Path(args.out_dir))
        print(f"Generated {len(generated)} smoke-test slides in {args.out_dir}")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
