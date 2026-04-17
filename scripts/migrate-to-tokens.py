#!/usr/bin/env python3
"""
Phase 1: Replace hardcoded CSS values with design-system tokens in all slide <style> blocks.
This makes all inline CSS reference the shared variables, so changing a token in slides.css
propagates to all slides.

Run: python3 scripts/migrate-to-tokens.py [--dry-run]
"""

import re
import glob
import sys
import os

DRY_RUN = "--dry-run" in sys.argv

# Color replacements: most specific patterns first
COLOR_MAP = [
    # Exact rgba values → ink tokens
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.82\)", "var(--ink-82)"),
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.80\)", "var(--ink-82)"),   # close enough → ink-82
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.76\)", "var(--ink-82)"),   # close → ink-82
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.72\)", "var(--ink-68)"),   # close → ink-68
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.70\)", "var(--ink-68)"),   # close → ink-68
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.68\)", "var(--ink-68)"),
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.66\)", "var(--ink-68)"),   # close → ink-68
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.64\)", "var(--ink-68)"),   # close → ink-68
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.62\)", "var(--ink-68)"),   # close → ink-68
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.60\)", "var(--ink-68)"),   # close → ink-68
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.58\)", "var(--ink-50)"),   # close → ink-50
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.56\)", "var(--ink-50)"),   # close → ink-50
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.55\)", "var(--ink-50)"),   # close → ink-50
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.54\)", "var(--ink-50)"),   # close → ink-50
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.50\)", "var(--ink-50)"),
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.48\)", "var(--ink-50)"),   # close → ink-50
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.46\)", "var(--ink-50)"),   # close → ink-50
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.44\)", "var(--ink-34)"),   # close → ink-34
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.42\)", "var(--ink-34)"),   # close → ink-34
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.40\)", "var(--ink-34)"),   # close → ink-34
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.38\)", "var(--ink-34)"),   # close → ink-34
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.36\)", "var(--ink-34)"),   # close → ink-34
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.35\)", "var(--ink-34)"),   # close → ink-34
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.34\)", "var(--ink-34)"),
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.32\)", "var(--ink-34)"),   # close → ink-34
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.30\)", "var(--ink-34)"),   # close → ink-34
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.28\)", "var(--ink-18)"),   # close → ink-18
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.18\)", "var(--ink-18)"),
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.08\)", "var(--ink-08)"),
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.05\)", "var(--ink-04)"),   # close → ink-04
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.045\)", "var(--ink-04)"),
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.04\)", "var(--ink-04)"),
    (r"rgba\(0\s*,\s*0\s*,\s*0\s*,\s*0?\.03\)", "var(--ink-04)"),   # close → ink-04

    # Hex colors
    (r"(?<![a-zA-Z])#1a1a1a(?![a-fA-F0-9])", "var(--ink-100)"),
    (r"(?<![a-zA-Z])#000000(?![a-fA-F0-9])", "var(--ink-100)"),
    (r"(?<![a-zA-Z])#111(?![a-fA-F0-9])", "var(--ink-100)"),

    # Accent colors
    (r"(?<![a-zA-Z])#5a4970(?![a-fA-F0-9])", "var(--accent-purple)"),
    (r"(?<![a-zA-Z])#5b476d(?![a-fA-F0-9])", "var(--accent-purple)"),
    (r"(?<![a-zA-Z])#9e3434(?![a-fA-F0-9])", "var(--accent-red)"),

    # Gray shades (keep #fff/#ffffff as-is, they map to surface-card or surface-white contextually)
    (r"(?<![a-zA-Z])#f7f7f7(?![a-fA-F0-9])", "var(--surface-mist)"),
]

# Font-size replacements: property: value → property: var()
FONT_SIZE_MAP = {
    "11px": "var(--fs-11)",
    "12px": "var(--fs-12)",
    "13px": "var(--fs-13)",
    "14px": "var(--fs-14)",
    "15px": "var(--fs-15)",
    "16px": "var(--fs-16)",
    "17px": "var(--fs-17)",
    "18px": "var(--fs-18)",
    "22px": "var(--fs-22)",
    "24px": "var(--fs-24)",
    "30px": "var(--fs-30)",
    "34px": "var(--fs-34)",
    "36px": "var(--fs-36)",
    "42px": "var(--fs-42)",
    "48px": "var(--fs-48)",
}


def migrate_style_block(block):
    """Apply token replacements to a <style> block."""
    result = block

    # Replace colors (in color/background-color/border-color properties)
    for pattern, replacement in COLOR_MAP:
        result = re.sub(pattern, replacement, result)

    # Replace font-sizes (only in font-size property to avoid matching padding/margin values)
    for px_val, var_val in FONT_SIZE_MAP.items():
        # Match font-size: 14px (with possible whitespace)
        result = re.sub(
            rf"(font-size\s*:\s*){re.escape(px_val)}",
            rf"\g<1>{var_val}",
            result,
        )

    return result


def process_file(filepath):
    """Process a single HTML file."""
    with open(filepath) as f:
        content = f.read()

    original = content

    # Find and replace within <style> blocks only
    def replace_style(match):
        return f"<style{match.group(1)}>{migrate_style_block(match.group(2))}</style>"

    content = re.sub(
        r"<style([^>]*)>(.*?)</style>",
        replace_style,
        content,
        flags=re.DOTALL,
    )

    if content != original:
        changes = sum(
            1
            for a, b in zip(original.split("\n"), content.split("\n"))
            if a != b
        )
        return content, changes
    return None, 0


def main():
    slides_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "slides")
    slides = sorted(
        glob.glob(os.path.join(slides_dir, "slide_*.html")),
        key=lambda f: int(re.search(r"slide_(\d+)", f).group(1)),
    )

    total_changes = 0
    modified_files = 0

    for filepath in slides:
        sn = int(re.search(r"slide_(\d+)", filepath).group(1))
        new_content, changes = process_file(filepath)

        if new_content and changes > 0:
            modified_files += 1
            total_changes += changes
            action = "would modify" if DRY_RUN else "modified"
            print(f"  slide_{sn:02d}: {changes} lines {action}")

            if not DRY_RUN:
                with open(filepath, "w") as f:
                    f.write(new_content)

    mode = "DRY RUN" if DRY_RUN else "DONE"
    print(f"\n[{mode}] {modified_files} files, {total_changes} line changes")


if __name__ == "__main__":
    main()
