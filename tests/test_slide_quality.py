"""Slide deck quality tests — visual, structural, and regression checks.

Complements test_slide_governance.py (manifest / metadata / sync logic)
with tests that inspect actual slide HTML files on disk.

Design principles:
  - Every loop-and-skip test has a count guard (assertGreater) so that
    zero-item passes are impossible.
  - Kind contract checks are driven by slide-kinds.yaml, not hardcoded
    attribute lists, so spec changes are picked up automatically.
  - Agenda drift and title drift tests parse HTML independently instead
    of delegating to governance validate_*() functions.

Categories:
  1. Page number continuity    — off-by-one regression guard
  2. Font link presence        — Google Fonts CDN on every slide
  3. Color scheme compliance   — border-top limited to greyscale palette
  4. Kind contract             — spec-driven from slide-kinds.yaml
  5. FontAwesome removal       — CDN regression guard
  6. Agenda drift              — independent HTML <-> manifest comparison
"""
from __future__ import annotations

import re
import unittest

from tools import slide_governance


SLIDES_DIR = slide_governance.SLIDES_DIR

FONTAWESOME_RE = re.compile(r'fontawesome|font-awesome', re.IGNORECASE)

BORDER_TOP_RE = re.compile(r'border-top\s*:\s*([^;}"]+)', re.IGNORECASE)
RGBA_RE = re.compile(
    r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*[\d.]+\s*)?\)',
)
ALLOWED_BORDER_TOP_HEX_AND_NAMED = {
    '#000', '#000000', 'black',
    '#333', '#333333',
    '#fff', '#ffffff', 'white',
    '#ccc', '#cccccc',
    '#ddd', '#dddddd',
    '#eee', '#eeeeee',
    '#e0e0e0',
    '#bbb', '#bbbbbb',
    '#999', '#999999',
    'transparent', 'none', 'inherit',
}
COLOR_TOKEN_RE = re.compile(r'var\(--[^)]+\)')

AGENDA_ROW_RE = re.compile(
    r'<div class="agenda-panel__row[^"]*">\s*'
    r'<span class="agenda-panel__index[^"]*">(?P<index>.*?)</span>\s*'
    r'<span class="agenda-panel__item[^"]*">(?P<label>.*?)</span>',
    re.DOTALL,
)


def _load_slides():
    paths = slide_governance.discover_slide_paths(SLIDES_DIR)
    return [(p.name, slide_governance.read_text(p)) for p in paths]


def _load_manifest():
    return slide_governance.load_yaml(slide_governance.MANIFEST_PATH)


def _load_kind_specs():
    return slide_governance.load_yaml(slide_governance.KINDS_PATH)['kinds']


# ── 1. Page number continuity ──────────────────────────────────────


class PageNumberContinuityTests(unittest.TestCase):
    """Guard against off-by-one bugs in data-footer-page (occurred twice)."""

    def test_footer_page_matches_ordinal_position(self):
        """Each slide's data-footer-page must equal its 1-based file position.

        Slides without data-footer-page (cover, agenda, divider, etc.) are
        skipped, but the checked count must exceed half the total to prevent
        silent pass on empty scans.
        """
        slides = _load_slides()
        drift = []
        checked = 0
        for order, (filename, text) in enumerate(slides, start=1):
            match = re.search(r'data-footer-page="(\d+)"', text)
            if not match:
                continue
            checked += 1
            actual = int(match.group(1))
            if actual != order:
                drift.append(
                    '%s: expected %02d, got %02d' % (filename, order, actual)
                )
        self.assertGreater(
            checked, len(slides) // 2,
            'Only %d/%d slides had data-footer-page — scanner may be broken'
            % (checked, len(slides)),
        )
        self.assertEqual(drift, [], 'Page number drift:\n' + '\n'.join(drift))

    def test_no_duplicate_page_numbers(self):
        slides = _load_slides()
        seen = {}
        dupes = []
        checked = 0
        for filename, text in slides:
            match = re.search(r'data-footer-page="(\d+)"', text)
            if not match:
                continue
            checked += 1
            page = match.group(1)
            if page in seen:
                dupes.append('page %s: %s and %s' % (page, seen[page], filename))
            seen[page] = filename
        self.assertGreater(
            checked, len(slides) // 2,
            'Only %d/%d slides had data-footer-page' % (checked, len(slides)),
        )
        self.assertEqual(dupes, [], 'Duplicate pages:\n' + '\n'.join(dupes))


# ── 2. Font link presence ──────────────────────────────────────────


class FontLinkPresenceTests(unittest.TestCase):

    def test_every_slide_has_google_fonts_link(self):
        slides = _load_slides()
        self.assertGreater(len(slides), 0, 'No slides found')
        missing = [fn for fn, text in slides if 'fonts.googleapis.com' not in text]
        self.assertEqual(
            missing, [],
            '%d slides missing Google Fonts link:\n%s'
            % (len(missing), '\n'.join(missing)),
        )

    def test_google_fonts_includes_both_families(self):
        """Each slide must reference both Space Grotesk and Noto Sans JP.

        Independent of test_every_slide_has_google_fonts_link — a slide with
        no fonts link will appear in both failure lists.
        """
        slides = _load_slides()
        self.assertGreater(len(slides), 0, 'No slides found')
        incomplete = []
        for filename, text in slides:
            has_sg = 'Space+Grotesk' in text or 'Space%20Grotesk' in text
            has_noto = 'Noto+Sans+JP' in text or 'Noto%20Sans%20JP' in text
            if not (has_sg and has_noto):
                incomplete.append(filename)
        self.assertEqual(
            incomplete, [],
            '%d slides have incomplete font families:\n%s'
            % (len(incomplete), '\n'.join(incomplete)),
        )


# ── 3. Color scheme compliance ─────────────────────────────────────


class ColorSchemeComplianceTests(unittest.TestCase):

    @staticmethod
    def _extract_border_top_color(decl):
        """Extract the color token from a border-top declaration.

        Handles rgba/rgb (most common in this codebase), hex, named colors,
        and CSS custom properties.
        """
        rgba_match = RGBA_RE.search(decl)
        if rgba_match:
            return rgba_match.group(0)
        for part in decl.strip().split():
            p = part.lower().rstrip(';').strip()
            if p.startswith('#') or p.startswith('var('):
                return p
            if p in ('black', 'white', 'transparent', 'none', 'inherit'):
                return p
        return None

    @staticmethod
    def _is_allowed_color(color):
        """Return True if *color* belongs to the allowed greyscale palette.

        Accepts hex/named greyscale, CSS custom properties, and rgba/rgb
        where r == g == b (greyscale at any opacity).
        """
        c = color.lower()
        if c in ALLOWED_BORDER_TOP_HEX_AND_NAMED:
            return True
        if COLOR_TOKEN_RE.match(c):
            return True
        m = RGBA_RE.match(c)
        if m:
            r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
            return r == g == b
        return False

    def test_border_top_uses_allowed_colors_only(self):
        slides = _load_slides()
        violations = []
        checked = 0
        for filename, text in slides:
            for match in BORDER_TOP_RE.finditer(text):
                color = self._extract_border_top_color(match.group(1))
                if color is None:
                    continue
                checked += 1
                if not self._is_allowed_color(color):
                    violations.append(
                        '%s: border-top color "%s"' % (filename, color)
                    )
        self.assertGreater(
            checked, 0,
            'No border-top colors were checked — parser may be broken',
        )
        self.assertEqual(
            violations, [],
            '%d border-top color violations:\n%s'
            % (len(violations), '\n'.join(violations)),
        )


# ── 4. Kind contract (spec-driven) ────────────────────────────────


class KindContractTests(unittest.TestCase):
    """Verify each slide satisfies its kind's contract from slide-kinds.yaml.

    Replaces individual hardcoded tests for content/agenda/divider/center-title
    with a single data-driven test that stays in sync with the spec file.
    """

    def test_all_slides_satisfy_kind_contract(self):
        """For every manifest slide, check required attrs, markers, and forbidden markers."""
        manifest = _load_manifest()
        kind_specs = _load_kind_specs()
        violations = []
        checked = 0

        for entry in manifest['slides']:
            kind = entry['kind']
            spec = kind_specs.get(kind)
            if not spec:
                violations.append(
                    '%s: kind "%s" not defined in slide-kinds.yaml' % (entry['file'], kind)
                )
                continue
            text = slide_governance.read_text(SLIDES_DIR / entry['file'])
            checked += 1

            # required_container_attrs: attr="..." must appear in the HTML
            for attr in spec.get('required_container_attrs', []):
                if (attr + '="') not in text:
                    violations.append(
                        '%s (%s): missing required attr %s'
                        % (entry['file'], kind, attr)
                    )

            # required_attr_values: attr="exact_value" must appear
            for attr, value in spec.get('required_attr_values', {}).items():
                expected = '%s="%s"' % (attr, value)
                if expected not in text:
                    violations.append(
                        '%s (%s): expected %s' % (entry['file'], kind, expected)
                    )

            # required_markers: substring must exist in HTML
            for marker in spec.get('required_markers', []):
                if marker not in text:
                    violations.append(
                        '%s (%s): missing required marker "%s"'
                        % (entry['file'], kind, marker)
                    )

            # forbidden_markers: substring must NOT exist in HTML
            for marker in spec.get('forbidden_markers', []):
                if marker in text:
                    violations.append(
                        '%s (%s): forbidden marker "%s" present'
                        % (entry['file'], kind, marker)
                    )

        self.assertGreater(checked, 60, 'Too few slides checked (%d)' % checked)
        self.assertEqual(
            violations, [],
            '%d kind contract violations:\n%s'
            % (len(violations), '\n'.join(violations)),
        )

    def test_every_slide_has_data_slide_kind(self):
        """Disk-level check independent of manifest: every slide file must declare kind."""
        slides = _load_slides()
        self.assertGreater(len(slides), 0, 'No slides found')
        missing = [
            fn for fn, text in slides
            if 'slide-container' in text and 'data-slide-kind="' not in text
        ]
        self.assertEqual(
            missing, [],
            'Slides missing data-slide-kind:\n' + '\n'.join(missing),
        )

    def test_all_slides_reference_shared_css_and_js(self):
        slides = _load_slides()
        self.assertGreater(len(slides), 0, 'No slides found')
        missing = []
        for filename, text in slides:
            if 'slides.css' not in text:
                missing.append('%s: missing slides.css' % filename)
            if 'slides.js' not in text:
                missing.append('%s: missing slides.js' % filename)
        self.assertEqual(
            missing, [],
            'Missing shared resources:\n' + '\n'.join(missing),
        )


# ── 5. FontAwesome removal ─────────────────────────────────────────


class FontAwesomeRemovalTests(unittest.TestCase):

    def test_no_fontawesome_cdn_references(self):
        slides = _load_slides()
        self.assertGreater(len(slides), 0, 'No slides found')
        violations = [fn for fn, text in slides if FONTAWESOME_RE.search(text)]
        self.assertEqual(
            violations, [],
            '%d slides still reference FontAwesome:\n%s'
            % (len(violations), '\n'.join(violations)),
        )

    def test_no_fa_icon_classes(self):
        fa5_re = re.compile(r'\bfa[srldb]?\s+fa-[\w-]+')
        fa6_re = re.compile(r'\bfa-(solid|regular|light|brands|duotone)\s+fa-[\w-]+')
        slides = _load_slides()
        self.assertGreater(len(slides), 0, 'No slides found')
        violations = []
        for filename, text in slides:
            matches = fa5_re.findall(text) + fa6_re.findall(text)
            if matches:
                violations.append('%s: %s' % (filename, matches[:3]))
        self.assertEqual(
            violations, [],
            '%d slides still use fa-* classes:\n%s'
            % (len(violations), '\n'.join(violations)),
        )


# ── 6. Agenda drift ───────────────────────────────────────────────


class AgendaDriftTests(unittest.TestCase):

    def test_agenda_html_rows_match_manifest(self):
        """Parse agenda rows directly from HTML and compare with manifest items.

        Does NOT delegate to validate_agenda_source() — this test independently
        extracts index/label pairs from HTML and compares them against the
        manifest's agenda.items list.
        """
        manifest = _load_manifest()
        drift = []
        checked = 0

        for entry in manifest['slides']:
            if entry['kind'] != 'agenda' or not entry.get('agenda'):
                continue
            text = slide_governance.read_text(SLIDES_DIR / entry['file'])
            checked += 1

            html_rows = [
                (m.group('index').strip(),
                 slide_governance.normalize_markup_text(m.group('label')))
                for m in AGENDA_ROW_RE.finditer(text)
            ]
            manifest_items = [
                (str(item['index']), item['label'])
                for item in entry['agenda']['items']
            ]

            if len(html_rows) != len(manifest_items):
                drift.append(
                    '%s: HTML has %d rows, manifest has %d items'
                    % (entry['file'], len(html_rows), len(manifest_items))
                )
                continue

            for i, ((h_idx, h_label), (m_idx, m_label)) in enumerate(
                zip(html_rows, manifest_items)
            ):
                if h_idx != m_idx:
                    drift.append(
                        '%s row %d: index "%s" != manifest "%s"'
                        % (entry['file'], i + 1, h_idx, m_idx)
                    )
                if h_label != m_label:
                    drift.append(
                        '%s row %d: label "%s" != manifest "%s"'
                        % (entry['file'], i + 1, h_label, m_label)
                    )

        self.assertGreater(checked, 0, 'No agenda slides were checked')
        self.assertEqual(drift, [], 'Agenda drift:\n' + '\n'.join(drift))

    def test_agenda_slides_have_agenda_panel_list(self):
        manifest = _load_manifest()
        missing = []
        checked = 0
        for entry in manifest['slides']:
            if entry['kind'] != 'agenda':
                continue
            checked += 1
            text = slide_governance.read_text(SLIDES_DIR / entry['file'])
            if 'agenda-panel__list' not in text:
                missing.append(entry['file'])
        self.assertGreater(checked, 0, 'No agenda slides found in manifest')
        self.assertEqual(
            missing, [],
            'Agenda slides missing agenda-panel__list:\n' + '\n'.join(missing),
        )

    def test_agenda_html_row_count_matches_chapter_count(self):
        """Count actual agenda rows in HTML and compare with manifest chapter count.

        Unlike the previous version that only checked manifest-internal
        consistency, this test parses the HTML to count rows.
        """
        manifest = _load_manifest()
        expected = len(manifest['chapters'])
        self.assertGreater(expected, 0, 'No chapters in manifest')
        wrong = []
        checked = 0

        for entry in manifest['slides']:
            if entry['kind'] != 'agenda':
                continue
            text = slide_governance.read_text(SLIDES_DIR / entry['file'])
            row_count = len(AGENDA_ROW_RE.findall(text))
            if row_count == 0:
                continue
            checked += 1
            if row_count != expected:
                wrong.append(
                    '%s: expected %d rows, HTML has %d'
                    % (entry['file'], expected, row_count)
                )

        self.assertGreater(checked, 0, 'No agenda slides with parseable rows')
        self.assertEqual(
            wrong, [],
            'Agenda row count mismatch:\n' + '\n'.join(wrong),
        )


# ── Supplementary: filename integrity & title drift ────────────────


class SlideFilenameIntegrityTests(unittest.TestCase):

    def test_filenames_are_contiguous(self):
        paths = sorted(
            SLIDES_DIR.glob('slide_*.html'),
            key=slide_governance.slide_sort_key,
        )
        self.assertGreater(len(paths), 0, 'No slide files found')
        numbers = [
            int(slide_governance.SLIDE_NAME_RE.fullmatch(p.name).group(1))
            for p in paths
        ]
        self.assertEqual(numbers, list(range(1, len(numbers) + 1)))

    def test_total_slide_count_matches_manifest(self):
        manifest = _load_manifest()
        actual = len(list(SLIDES_DIR.glob('slide_*.html')))
        self.assertEqual(manifest['counts']['total_slides'], actual)


class TitleDriftTests(unittest.TestCase):

    def test_slide_titles_match_manifest(self):
        """Parse <title> directly from HTML and compare with manifest index_title.

        Does NOT delegate to validate_slide_title() — extracts and normalizes
        the HTML <title> tag content independently.

        Compares against ``index_title`` (the browser-tab title that includes
        chapter context for agenda/divider slides), not ``title`` (the
        semantic-only title).
        """
        manifest = _load_manifest()
        self.assertGreater(len(manifest['slides']), 0, 'No slides in manifest')
        drift = []
        for entry in manifest['slides']:
            text = slide_governance.read_text(SLIDES_DIR / entry['file'])
            title_match = re.search(
                r'<title>(.*?)</title>', text, re.IGNORECASE | re.DOTALL,
            )
            if not title_match:
                drift.append('%s: no <title> tag found' % entry['file'])
                continue
            html_title = slide_governance.normalize_title(title_match.group(1))
            manifest_title = entry['index_title']
            if html_title != manifest_title:
                drift.append(
                    '%s: HTML "%s" != manifest "%s"'
                    % (entry['file'], html_title, manifest_title)
                )
        self.assertEqual(drift, [], 'Title drift:\n' + '\n'.join(drift))


if __name__ == '__main__':
    unittest.main()
