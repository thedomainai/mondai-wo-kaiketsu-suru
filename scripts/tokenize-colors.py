#!/usr/bin/env python3
"""
Safe color tokenization script for slides.
ONLY replaces color values with DS token variables.
NEVER touches HTML structure, class names, or layout properties.

Strategy:
- Exact matches only (no fuzzy matching)
- Replace literal color values in:
  1. inline style="..." attributes
  2. <style>...</style> blocks (block itself preserved, only colors changed)
  3. SVG fill="..." and stroke="..." attributes
- NEVER modifies class names, HTML structure, or layout dimensions
"""

import re
import sys
import os
from pathlib import Path

# ===== SAFE COLOR MAPPINGS =====
# Only colors with EXACT match to DS tokens or trivially equivalent
# Grouped by safety level

EXACT_MATCHES = {
    # Surface tokens
    '#ffffff': 'var(--surface-white)',
    '#fff': 'var(--surface-white)',
    '#f7f7f7': 'var(--surface-mist)',

    # Ink-100 (soft-black) - exact
    '#1a1a1a': 'var(--ink-100)',

    # Accent colors - exact
    '#5a4970': 'var(--accent-purple)',
    '#5b476d': 'var(--accent-purple)',  # variant used in some slides
    '#9e3434': 'var(--accent-red)',
}

# rgba exact matches (normalize spacing variants)
RGBA_EXACT = {
    # Format: (r, g, b, alpha) -> token
    # Black with opacity
    (0, 0, 0, 0.84): 'var(--ink-84)',
    (0, 0, 0, 0.82): 'var(--ink-82)',
    (0, 0, 0, 0.78): 'var(--ink-78)',
    (0, 0, 0, 0.68): 'var(--ink-68)',
    (0, 0, 0, 0.50): 'var(--ink-50)',
    (0, 0, 0, 0.5):  'var(--ink-50)',
    (0, 0, 0, 0.34): 'var(--ink-34)',
    (0, 0, 0, 0.30): 'var(--ink-30)',
    (0, 0, 0, 0.3):  'var(--ink-30)',
    (0, 0, 0, 0.22): 'var(--ink-22)',
    (0, 0, 0, 0.18): 'var(--ink-18)',
    (0, 0, 0, 0.16): 'var(--ink-16)',
    (0, 0, 0, 0.14): 'var(--ink-14)',
    (0, 0, 0, 0.12): 'var(--ink-12)',
    (0, 0, 0, 0.10): 'var(--ink-10)',
    (0, 0, 0, 0.1):  'var(--ink-10)',
    (0, 0, 0, 0.08): 'var(--ink-08)',
    (0, 0, 0, 0.04): 'var(--ink-04)',
}


def normalize_rgba(match_str):
    """Parse rgba string to tuple (r, g, b, a)"""
    # Handle rgba(0,0,0,.34) and rgba(0, 0, 0, 0.34) and rgba(0,0,0,0.34)
    m = re.match(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([\d.]+)\s*\)', match_str)
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)), float(m.group(4)))
    return None



def replace_colors_in_text(text):
    """Replace color values in any CSS text (inline style or style block)."""
    result = text
    replacements = 0

    # 1. Replace hex colors (case-insensitive)
    for hex_color, token in EXACT_MATCHES.items():
        pattern = re.compile(
            r'(?<![a-zA-Z0-9#-])' + re.escape(hex_color) + r'(?![a-zA-Z0-9])',
            re.IGNORECASE
        )
        new_result = pattern.sub(token, result)
        if new_result != result:
            # Count actual replacements
            replacements += len(pattern.findall(result))
            result = new_result

    # 2. Replace rgba exact matches
    rgba_pattern = re.compile(r'rgba?\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[\d.]+\s*\)')

    def rgba_replacer(m):
        nonlocal replacements
        parsed = normalize_rgba(m.group(0))
        if parsed and parsed in RGBA_EXACT:
            replacements += 1
            return RGBA_EXACT[parsed]
        return m.group(0)

    result = rgba_pattern.sub(rgba_replacer, result)

    return result, replacements


def process_slide(filepath, dry_run=False):
    """Process a single slide file, replacing colors everywhere safely."""
    content = Path(filepath).read_text(encoding='utf-8')
    original = content
    total_replacements = 0

    # 1. Replace colors inside <style>...</style> blocks
    def style_block_replacer(m):
        nonlocal total_replacements
        open_tag = m.group(1)
        css_content = m.group(2)
        close_tag = m.group(3)

        new_css, count = replace_colors_in_text(css_content)
        total_replacements += count
        return open_tag + new_css + close_tag

    content = re.sub(
        r'(<style[^>]*>)(.*?)(</style>)',
        style_block_replacer,
        content,
        flags=re.DOTALL
    )

    # 2. Replace colors in inline style="..." attributes
    def style_attr_replacer(m):
        nonlocal total_replacements
        prefix = m.group(1)
        style_val = m.group(2)
        suffix = m.group(3)

        new_val, count = replace_colors_in_text(style_val)
        total_replacements += count
        return prefix + new_val + suffix

    content = re.sub(
        r'(style=["\'])([^"\']*?)(["\'])',
        style_attr_replacer,
        content
    )

    # 3. Replace colors in SVG fill="..." and stroke="..." attributes
    for attr in ['fill', 'stroke']:
        def svg_attr_replacer(m):
            nonlocal total_replacements
            prefix = m.group(1)
            val = m.group(2).strip()
            suffix = m.group(3)

            lower_val = val.lower()
            if lower_val in EXACT_MATCHES:
                total_replacements += 1
                return prefix + EXACT_MATCHES[lower_val] + suffix

            parsed = normalize_rgba(val)
            if parsed and parsed in RGBA_EXACT:
                total_replacements += 1
                return prefix + RGBA_EXACT[parsed] + suffix

            return m.group(0)

        content = re.sub(
            rf'({attr}=["\'])([^"\']*?)(["\'])',
            svg_attr_replacer,
            content
        )

    if content != original:
        if not dry_run:
            Path(filepath).write_text(content, encoding='utf-8')
        return total_replacements, True
    return 0, False


def main():
    slides_dir = Path('/private/tmp/slides/slides')
    dry_run = '--dry-run' in sys.argv

    if dry_run:
        print("=== DRY RUN MODE (no files modified) ===\n")

    total_files = 0
    total_changes = 0
    modified_files = []

    for i in range(1, 70):  # slide_01 to slide_69
        filepath = slides_dir / f'slide_{i:02d}.html'
        if not filepath.exists():
            continue

        count, changed = process_slide(filepath, dry_run=dry_run)
        total_files += 1
        total_changes += count

        if changed:
            modified_files.append((filepath.name, count))
            print(f"  {filepath.name}: {count} replacements")

    print(f"\n=== Summary ===")
    print(f"Files scanned: {total_files}")
    print(f"Files modified: {len(modified_files)}")
    print(f"Total replacements: {total_changes}")

    if dry_run:
        print("\nRe-run without --dry-run to apply changes.")


if __name__ == '__main__':
    main()
