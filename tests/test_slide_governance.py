from __future__ import annotations

import tempfile
import unittest
from collections import Counter
from pathlib import Path

from tools import slide_governance


class SlideGovernanceTests(unittest.TestCase):
    def test_extract_authored_title_prefers_visible_runtime_title(self) -> None:
        content_text = """
        <html><head><title>旧タイトル</title></head><body>
        <div class="slide-container" data-slide-kind="content" data-header-title="表示タイトル"></div>
        </body></html>
        """
        center_text = """
        <html><head><title>旧タイトル</title></head><body>
        <div class="slide-container slide-center-title" data-slide-kind="center-title">
          <p class="title">中央タイトル</p>
        </div>
        </body></html>
        """

        self.assertEqual(
            slide_governance.extract_authored_title(content_text, "content", {}, "slide_01.html"),
            "表示タイトル",
        )
        self.assertEqual(
            slide_governance.extract_authored_title(center_text, "center-title", {}, "slide_02.html"),
            "中央タイトル",
        )

    def test_inventory_matches_actual_files(self) -> None:
        manifest = slide_governance.build_manifest_data(slide_governance.ROOT)
        actual_files = [path.name for path in slide_governance.discover_slide_paths(slide_governance.ROOT)]
        actual_counts = Counter(slide["kind"] for slide in manifest["slides"])
        expected_counts = {
            kind: actual_counts[kind]
            for kind in slide_governance.CANONICAL_KINDS
            if actual_counts[kind]
        }

        self.assertEqual(manifest["counts"]["total_slides"], len(actual_files))
        self.assertEqual([slide["file"] for slide in manifest["slides"]], actual_files)
        self.assertEqual(
            manifest["counts"]["by_kind"],
            expected_counts,
        )

    def test_agenda_manifest_round_trip(self) -> None:
        manifest = slide_governance.build_manifest_data(slide_governance.ROOT)
        agenda_slides = [slide for slide in manifest["slides"] if slide["kind"] == "agenda"]
        self.assertGreaterEqual(len(agenda_slides), 1)
        overview_agenda = next(
            (slide for slide in agenda_slides if slide["agenda"]["mode"] == "timed-overview"),
            None,
        )
        if overview_agenda is not None:
            self.assertEqual(len(overview_agenda["agenda"]["items"]), len(manifest["chapters"]))
        for slide in agenda_slides:
            self.assertEqual(len(slide["agenda"]["items"]), len(manifest["chapters"]))

    def test_sync_index_html_uses_manifest_as_single_source_of_truth(self) -> None:
        manifest = {
            "deck": {"title": "テストデッキ"},
            "counts": {"total_slides": 2},
            "slides": [
                {"index_title": "表紙", "index_type": "normal", "file": "slide_01.html"},
                {"index_title": "本編", "index_type": "chapter-title", "file": "slide_02.html"},
            ],
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            (tmp_root / "index.html").write_text(
                slide_governance.INDEX_PATH.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            slide_governance.sync_index_html(tmp_root, manifest)
            synced = (tmp_root / "index.html").read_text(encoding="utf-8")

        self.assertIn("テストデッキ — 全2スライド", synced)
        self.assertIn("1 / 2", synced)
        self.assertIn(slide_governance.render_index_slides(manifest), synced)

    def test_sync_slide_titles_uses_index_title(self) -> None:
        manifest = {
            "slides": [
                {"file": "slide_01.html", "index_title": "表紙"},
                {"file": "slide_02.html", "index_title": "アジェンダ｜第01章 ワーク"},
            ]
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            (tmp_root / "slide_01.html").write_text("<title>old</title>", encoding="utf-8")
            (tmp_root / "slide_02.html").write_text("<title>old</title>", encoding="utf-8")
            updated = slide_governance.sync_slide_titles(tmp_root, manifest)

            self.assertEqual(updated, 2)
            self.assertIn("<title>表紙</title>", (tmp_root / "slide_01.html").read_text(encoding="utf-8"))
            self.assertIn(
                "<title>アジェンダ｜第01章 ワーク</title>",
                (tmp_root / "slide_02.html").read_text(encoding="utf-8"),
            )

    def test_derive_sections_treats_leading_agenda_as_deck_overview(self) -> None:
        slides = [
            {"file": "slide_01.html", "kind": "intro", "title": "Intro"},
            {
                "file": "slide_02.html",
                "kind": "agenda",
                "title": "アジェンダ",
                "_raw_agenda": {"mode": "progress", "active_item": None, "items": []},
            },
            {
                "file": "slide_03.html",
                "kind": "agenda",
                "title": "アジェンダ — 第01章",
                "_raw_agenda": {
                    "mode": "progress",
                    "active_item": "01",
                    "items": [
                        {"index": "01", "label": "ワーク", "state": "active", "duration": None},
                    ],
                },
            },
            {"file": "slide_04.html", "kind": "divider", "title": "第01章 ワーク"},
            {"file": "slide_05.html", "kind": "content", "title": "ワーク"},
        ]

        sections, overview_agenda_file = slide_governance.derive_sections(slides)

        self.assertEqual(overview_agenda_file, "slide_02.html")
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0]["title"], "ワーク")
        self.assertEqual(sections[0]["agenda_file"], "slide_03.html")
        self.assertEqual(sections[0]["divider_file"], "slide_04.html")

    def test_derive_sections_merges_divider_then_agenda_when_titles_match(self) -> None:
        slides = [
            {"file": "slide_01.html", "kind": "divider", "title": "第04章 論点を定義する"},
            {
                "file": "slide_02.html",
                "kind": "agenda",
                "title": "アジェンダ — 第04章",
                "_raw_agenda": {
                    "mode": "progress",
                    "active_item": "04",
                    "items": [
                        {"index": "04", "label": "論点を定義する", "state": "active", "duration": None},
                    ],
                },
            },
            {"file": "slide_03.html", "kind": "content", "title": "論点の定義"},
        ]

        sections, overview_agenda_file = slide_governance.derive_sections(slides)

        self.assertIsNone(overview_agenda_file)
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0]["title"], "論点を定義する")
        self.assertEqual(sections[0]["divider_file"], "slide_01.html")
        self.assertEqual(sections[0]["agenda_file"], "slide_02.html")

    def test_build_navigation_title_adds_context_for_agenda_and_divider(self) -> None:
        self.assertEqual(
            slide_governance.build_navigation_title(
                {
                    "kind": "agenda",
                    "title": "アジェンダ",
                    "section_number": 4,
                    "section_title": "論点を定義する",
                }
            ),
            "アジェンダ｜第04章 論点を定義する",
        )
        self.assertEqual(
            slide_governance.build_navigation_title(
                {
                    "kind": "divider",
                    "title": "論点を定義する",
                    "section_number": 4,
                    "section_title": "論点を定義する",
                }
            ),
            "第04章 論点を定義する",
        )

    def test_resolve_slide_target_accepts_page_and_title_when_they_point_to_same_slide(self) -> None:
        slides = [
            {"file": "slide_64.html", "page_label": "64", "title": "2. 根拠", "index_title": "2. 根拠"},
            {"file": "slide_65.html", "page_label": "65", "title": "3. ネクストアクション", "index_title": "3. ネクストアクション"},
        ]

        resolved = slide_governance.resolve_slide_target(
            slides,
            page_ref="P65",
            title="3. ネクストアクション",
        )

        self.assertEqual(resolved["file"], "slide_65.html")

    def test_resolve_slide_target_rejects_page_and_title_when_they_point_to_different_slides(self) -> None:
        slides = [
            {"file": "slide_61.html", "page_label": "60", "title": "第08章 問題解決におけるコミュニケーション", "index_title": "第08章 問題解決におけるコミュニケーション"},
            {"file": "slide_65.html", "page_label": "64", "title": "3-1. 意思決定構造を押さえる", "index_title": "3-1. 意思決定構造を押さえる"},
            {"file": "slide_66.html", "page_label": "65", "title": "4. 内容設計", "index_title": "4. 内容設計"},
        ]

        with self.assertRaisesRegex(
            ValueError,
            "page P65 -> P65 / slide_66.html / 4. 内容設計.*title '3-1. 意思決定構造を押さえる' -> P64 / slide_65.html / 3-1. 意思決定構造を押さえる",
        ):
            slide_governance.resolve_slide_target(
                slides,
                page_ref="P65",
                title="3-1. 意思決定構造を押さえる",
            )

    def test_smoke_test_generation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            generated = slide_governance.write_smoke_samples(Path(tmp_dir))
            self.assertEqual(len(generated), 6)
            for path in generated:
                text = path.read_text(encoding="utf-8")
                self.assertIn("data-slide-kind", text)
                self.assertIn("./slides.css", text)
                self.assertIn("./slides.js", text)
            qa_text = next(path.read_text(encoding="utf-8") for path in generated if "qa" in path.name)
            self.assertIn("stack-optical", qa_text)

    def test_content_contract_failure_detection(self) -> None:
        manifest = slide_governance.build_manifest_data(slide_governance.ROOT)
        slide = next(entry for entry in manifest["slides"] if entry["kind"] == "content")
        bad_text = slide_governance.build_smoke_slide("content", "01").replace('data-slide-kind="content" ', "")
        kind_spec = slide_governance.load_kind_specs()["content"]
        findings = slide_governance.validate_kind_contract(slide, bad_text, kind_spec, slide_governance.ROOT)
        codes = {finding.code for finding in findings}
        self.assertIn("missing-required-attr", codes)

    def test_page_number_failure_detection(self) -> None:
        slide = {"file": "smoke_summary.html", "kind": "summary", "page_label": "09"}
        bad_text = slide_governance.build_smoke_slide("summary", "08")
        findings = slide_governance.validate_page_number(slide, bad_text)
        self.assertTrue(any(finding.code == "manual-footer-page-drift" for finding in findings))

    def test_title_failure_detection(self) -> None:
        slide = {"file": "slide_09.html", "index_title": "アジェンダ｜第01章 ワーク"}
        findings = slide_governance.validate_slide_title(slide, "<title>アジェンダ</title>")
        self.assertTrue(any(finding.code == "slide-title-drift" for finding in findings))

    def test_undefined_ds_class_detection(self) -> None:
        shared_defined_classes = {"ds-card", "ds-stage"}
        bad_text = '<div class="ds-card ds-ghost"></div>'
        findings = slide_governance.validate_defined_ds_classes(
            "slide_01.html",
            bad_text,
            shared_defined_classes,
        )
        self.assertTrue(any(finding.code == "undefined-ds-class" for finding in findings))

    def test_undefined_ds_class_ignores_local_style_definition(self) -> None:
        shared_defined_classes = {"ds-card", "ds-stage"}
        text = """
        <style>
          .ds-local-stack { display: flex; }
        </style>
        <div class="ds-card ds-local-stack"></div>
        """
        findings = slide_governance.validate_defined_ds_classes(
            "slide_01.html",
            text,
            shared_defined_classes,
        )
        self.assertFalse(any(finding.code == "undefined-ds-class" for finding in findings))

    def test_footer_safe_area_reserve_warns_when_conclusion_is_not_docked(self) -> None:
        text = """
        <div class="slide-container" data-footer="standard">
          <main class="ds-stage">
            <section class="ds-comparison"></section>
            <section aria-label="結論"></section>
          </main>
        </div>
        """
        findings = slide_governance.validate_footer_safe_area_reserve("slide_13.html", text)
        self.assertTrue(any(finding.code == "footer-safe-area-overlap-risk" for finding in findings))

    def test_footer_safe_area_reserve_accepts_reserved_stage_and_summary_dock(self) -> None:
        text = """
        <div class="slide-container" data-footer="standard">
          <main class="ds-stage ds-stage--summary-reserve">
            <section class="ds-comparison ds-comparison--cards">
              <article class="ds-compare-card"></article>
            </section>
          </main>
          <section class="ds-summary-dock" aria-label="結論"></section>
        </div>
        """
        findings = slide_governance.validate_footer_safe_area_reserve("slide_13.html", text)
        self.assertFalse(findings)

    def test_comparison_conclusion_archetype_warns_when_cards_are_ad_hoc(self) -> None:
        text = """
        <div class="slide-container">
          <main class="ds-stage">
            <section class="ds-comparison">
              <article class="ds-panel"></article>
            </section>
            <section aria-label="結論"></section>
          </main>
        </div>
        """
        findings = slide_governance.validate_comparison_conclusion_archetype("slide_13.html", text)
        self.assertTrue(any(finding.code == "comparison-conclusion-archetype-missing" for finding in findings))

    def test_review_rules_cover_parallel_card_alignment(self) -> None:
        review_rules_text = slide_governance.REVIEW_RULES_PATH.read_text(encoding="utf-8")
        self.assertIn("parallel-card-track-alignment", review_rules_text)

    def test_design_tokens_document_optical_gap(self) -> None:
        design_tokens_text = (slide_governance.DOCS_DIR / "design-tokens.md").read_text(encoding="utf-8")
        self.assertIn("Optical gap", design_tokens_text)
        self.assertIn("stack-optical", design_tokens_text)


if __name__ == "__main__":
    unittest.main()
