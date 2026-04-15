from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from tools import slide_governance


class SlideGovernanceTests(unittest.TestCase):
    def test_inventory_matches_canonical_counts(self) -> None:
        manifest = slide_governance.build_manifest_data(slide_governance.ROOT)
        self.assertEqual(manifest["counts"]["total_slides"], 74)
        self.assertEqual(
            manifest["counts"]["by_kind"],
            {
                "cover": 1,
                "intro": 3,
                "agenda": 9,
                "divider": 8,
                "center-title": 7,
                "content": 42,
                "summary": 1,
                "closing": 1,
                "cta": 1,
                "qa": 1,
            },
        )

    def test_agenda_manifest_round_trip(self) -> None:
        manifest = slide_governance.build_manifest_data(slide_governance.ROOT)
        agenda_slides = [slide for slide in manifest["slides"] if slide["kind"] == "agenda"]
        self.assertEqual(len(agenda_slides), 9)
        deck_agenda = next(slide for slide in agenda_slides if slide["file"] == "slide_05.html")
        self.assertEqual(deck_agenda["agenda"]["mode"], "timed-overview")
        self.assertEqual(len(deck_agenda["agenda"]["items"]), 9)

    def test_smoke_test_generation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            generated = slide_governance.write_smoke_samples(Path(tmp_dir))
            self.assertEqual(len(generated), 6)
            for path in generated:
                text = path.read_text(encoding="utf-8")
                self.assertIn("data-slide-kind", text)
                self.assertIn("./slides.css", text)
                self.assertIn("./slides.js", text)

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

    def test_review_rules_cover_parallel_card_alignment(self) -> None:
        review_rules = yaml.safe_load(slide_governance.REVIEW_RULES_PATH.read_text(encoding="utf-8"))
        semantic_rule_ids = {rule["id"] for rule in review_rules["semantic_rules"]}
        self.assertIn("parallel-card-track-alignment", semantic_rule_ids)


if __name__ == "__main__":
    unittest.main()
