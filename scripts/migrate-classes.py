#!/usr/bin/env python3
"""
Phase 2: Replace local class definitions (.stage, .kicker, .summary, .grid, .card)
with shared ds-* classes from slides.css.

For each slide:
1. Remove the local CSS rule from <style> block
2. Update the class attribute in HTML to use ds-* class
3. Move per-slide overrides (top, gap) into style="--stage-top:..." on the element

Run: python3 scripts/migrate-classes.py [--dry-run]
"""

import re
import glob
import sys
import os

DRY_RUN = "--dry-run" in sys.argv

def remove_css_rule(style_content, selector):
    """Remove a CSS rule for the given selector from a style block."""
    # Match .selector { ... } including nested content
    pattern = re.escape(selector) + r'\s*\{[^}]*\}'
    return re.sub(pattern, '', style_content)

def extract_prop(css_text, prop_name):
    """Extract a property value from CSS text."""
    m = re.search(rf'{prop_name}\s*:\s*([^;}}]+)', css_text)
    return m.group(1).strip() if m else None

def process_stage(filepath, content):
    """Replace local .stage with ds-stage."""
    changes = 0

    # Find .stage definition in <style>
    for block_match in re.finditer(r'(<style[^>]*>)(.*?)(</style>)', content, re.DOTALL):
        block = block_match.group(2)
        stage_match = re.search(r'\.stage\s*\{([^}]+)\}', block)
        if not stage_match:
            continue

        css = stage_match.group(1)
        top_val = extract_prop(css, 'top')
        gap_val = extract_prop(css, 'gap') or extract_prop(css, 'row-gap')

        # Build inline style for overrides
        overrides = []
        if top_val and top_val not in ('156px', '160px', '164px'):
            # These are close to header-band-height (156px); only override if significantly different
            overrides.append(f"--stage-top:{top_val}")
        elif top_val:
            overrides.append(f"--stage-top:{top_val}")

        if gap_val and gap_val not in ('18px', '20px'):
            overrides.append(f"--stage-gap:{gap_val}")
        elif gap_val == '18px':
            overrides.append(f"--stage-gap:var(--sp-20)")  # normalize 18→20

        # Remove .stage rule from <style>
        new_block = remove_css_rule(block, '.stage')
        content = content.replace(block_match.group(0),
                                  f"{block_match.group(1)}{new_block}{block_match.group(3)}")
        changes += 1

        # Replace class="stage" with class="ds-stage" in HTML
        override_style = ";".join(overrides)
        if override_style:
            # Add style attribute with overrides
            content = re.sub(
                r'class="stage"',
                f'class="ds-stage" style="{override_style}"',
                content
            )
            # If stage already has a style attribute
            content = re.sub(
                r'class="stage"\s+style="([^"]*)"',
                lambda m: f'class="ds-stage" style="{override_style};{m.group(1)}"',
                content
            )
        else:
            content = re.sub(r'class="stage"', 'class="ds-stage"', content)

    return content, changes

def process_kicker(filepath, content):
    """Replace local .kicker with ds-kicker."""
    changes = 0

    for block_match in re.finditer(r'(<style[^>]*>)(.*?)(</style>)', content, re.DOTALL):
        block = block_match.group(2)
        kicker_match = re.search(r'\.kicker\s*\{([^}]+)\}', block)
        if not kicker_match:
            continue

        css = kicker_match.group(1)
        font_size = extract_prop(css, 'font-size')
        margin = extract_prop(css, 'margin')

        # Remove .kicker rule from <style>
        new_block = remove_css_rule(block, '.kicker')
        content = content.replace(block_match.group(0),
                                  f"{block_match.group(1)}{new_block}{block_match.group(3)}")
        changes += 1

        # Determine variant
        cls = "ds-kicker"
        if font_size and 'fs-14' in font_size:
            cls = "ds-kicker ds-kicker--sm"

        # Handle margin override
        style_override = ""
        if margin and margin != "0" and "24px" in margin:
            style_override = f' style="margin-bottom:var(--sp-24)"'

        content = re.sub(
            r'class="kicker"',
            f'class="{cls}"{style_override}',
            content
        )

    return content, changes

def process_summary(filepath, content):
    """Replace local .summary with ds-summary."""
    changes = 0

    for block_match in re.finditer(r'(<style[^>]*>)(.*?)(</style>)', content, re.DOTALL):
        block = block_match.group(2)
        summary_match = re.search(r'\.summary\s*\{([^}]+)\}', block)
        if not summary_match:
            continue

        css = summary_match.group(1)
        padding_top = extract_prop(css, 'padding-top')
        padding = extract_prop(css, 'padding')
        has_border_radius = 'border-radius' in css

        # Remove .summary rule from <style>
        new_block = remove_css_rule(block, '.summary')
        # Also remove .summary p rule if present
        new_block = remove_css_rule(new_block, '.summary p')
        content = content.replace(block_match.group(0),
                                  f"{block_match.group(1)}{new_block}{block_match.group(3)}")
        changes += 1

        # Determine variant and overrides
        cls = "ds-summary"
        style_override = ""

        if has_border_radius:
            cls = "ds-summary ds-summary--box"
        elif padding_top and padding_top not in ('14px', '16px'):
            style_override = f' style="--summary-pad:{padding_top}"'

        content = re.sub(
            r'class="summary"',
            f'class="{cls}"{style_override}',
            content
        )

    return content, changes

def clean_empty_style_blocks(content):
    """Remove <style> blocks that are now empty (only whitespace)."""
    def check_empty(match):
        block = match.group(2).strip()
        if not block or all(c in ' \n\t\r' for c in block):
            return ''
        return match.group(0)

    return re.sub(r'(<style[^>]*>)(.*?)(</style>)', check_empty, content, flags=re.DOTALL)

def process_file(filepath):
    """Process a single HTML file."""
    with open(filepath) as f:
        original = f.read()

    content = original
    total_changes = 0

    content, c = process_stage(filepath, content)
    total_changes += c

    content, c = process_kicker(filepath, content)
    total_changes += c

    content, c = process_summary(filepath, content)
    total_changes += c

    # Clean up empty style blocks
    content = clean_empty_style_blocks(content)

    if content != original:
        return content, total_changes
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
            print(f"  slide_{sn:02d}: {changes} class(es) {action}")

            if not DRY_RUN:
                with open(filepath, 'w') as f:
                    f.write(new_content)

    mode = "DRY RUN" if DRY_RUN else "DONE"
    print(f"\n[{mode}] {modified_files} files, {total_changes} class migrations")


if __name__ == "__main__":
    main()
