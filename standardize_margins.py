#!/usr/bin/env python3
"""
Standardize left/right margins across all slides.
Target: 80px left margin, 80px right margin (right: 80px = 1200px from left)

Changes to standardized header:
  - Chapter label: left: 40px → left: 80px
  - Branding pill: right: 40px → right: 80px

Changes to standardized footer:
  - Footer text: left: 40px → left: 80px
  - Page number: right: 40px → right: 80px
"""

import re
import os
import glob

SLIDES_DIR = "/tmp/slides"

# Slides with standardized headers/footers (40 slides)
# Excluded: 1(title), 2(agenda), 5,9,13,16,25,33,39(section covers), 50(Q&A)
STANDARDIZED_SLIDES = [
    3, 4, 6, 7, 8, 10, 11, 12, 14, 15, 17, 18, 19, 20,
    21, 22, 23, 24, 26, 27, 28, 29, 30, 31, 32, 34, 35,
    36, 37, 38, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49
]

def fix_header_footer_margins(html):
    """Fix header and footer x-margins from 40px to 80px."""
    changes = []

    # === HEADER FIXES ===

    # Fix chapter label: left: 40px → left: 80px (in header section)
    # Pattern: <div style="position: absolute; left: 40px; top: 22px; z-index: 55;">
    # followed by chapter label text
    old_chapter = 'position: absolute; left: 40px; top: 22px; z-index: 55;'
    new_chapter = 'position: absolute; left: 80px; top: 22px; z-index: 55;'
    if old_chapter in html:
        html = html.replace(old_chapter, new_chapter)
        changes.append("header chapter label: left 40→80")

    # Fix branding pill: right: 40px → right: 80px (in header section)
    # Pattern: <div style="position: absolute; right: 40px; top: 16px; z-index: 55;">
    old_pill = 'position: absolute; right: 40px; top: 16px; z-index: 55;'
    new_pill = 'position: absolute; right: 80px; top: 16px; z-index: 55;'
    if old_pill in html:
        html = html.replace(old_pill, new_pill)
        changes.append("header branding pill: right 40→80")

    # === FOOTER FIXES ===

    # Fix footer text: left: 40px → left: 80px
    # Pattern: <div style="position: absolute; left: 40px; top: 680px; z-index: 55;">
    old_footer_left = 'position: absolute; left: 40px; top: 680px; z-index: 55;'
    new_footer_left = 'position: absolute; left: 80px; top: 680px; z-index: 55;'
    if old_footer_left in html:
        html = html.replace(old_footer_left, new_footer_left)
        changes.append("footer text: left 40→80")

    # Fix page number: right: 40px → right: 80px
    # Pattern: <div style="position: absolute; right: 40px; top: 680px; z-index: 55;">
    old_footer_right = 'position: absolute; right: 40px; top: 680px; z-index: 55;'
    new_footer_right = 'position: absolute; right: 80px; top: 680px; z-index: 55;'
    if old_footer_right in html:
        html = html.replace(old_footer_right, new_footer_right)
        changes.append("footer page number: right 40→80")

    return html, changes


def process_slides():
    """Process all standardized slides."""
    total_changes = 0

    for slide_num in STANDARDIZED_SLIDES:
        filepath = os.path.join(SLIDES_DIR, f"slide_{slide_num:02d}.html")
        if not os.path.exists(filepath):
            print(f"  SKIP slide_{slide_num:02d}.html (not found)")
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            html = f.read()

        new_html, changes = fix_header_footer_margins(html)

        if changes:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_html)
            print(f"  slide_{slide_num:02d}.html: {', '.join(changes)}")
            total_changes += len(changes)
        else:
            print(f"  slide_{slide_num:02d}.html: no changes needed")

    print(f"\nTotal changes: {total_changes}")


if __name__ == "__main__":
    print("=== Standardizing header/footer margins to 80px ===\n")
    process_slides()
    print("\nDone.")
