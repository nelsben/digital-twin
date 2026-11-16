"""OPS-63: validate compares compliance.retention with compliance.zdr_cover.

retention 'zdr' with zdr_cover 'none' is a validation error, 'zdr' with 'planned' is a warning, every other
pair is silent. In-memory variants of the Team sample only; nothing is written under engagements/.

Standard library only. Run with: python3 -m unittest discover -s tests
"""

import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

import test_twincard_level as LT  # noqa: E402

from twincard import level as L  # noqa: E402
from twincard import validate as V  # noqa: E402

DESIGN = LT.ROOT / "partner-kit" / "docs" / "design.md"
PATH = "compliance.retention"


def pair(retention, cover, retention_status=None, cover_status=None):
    def change(profile, card):
        profile["compliance"]["retention"] = retention
        profile["compliance"]["zdr_cover"] = cover
        for key, status in (("compliance.retention", retention_status), ("compliance.zdr_cover", cover_status)):
            if status:
                entry = {"status": status, "source": "discovery.md#C3"}
                if status in ("assumed", "open"):
                    entry.update({"owner": "Compliance / legal", "due": "2026-12-04"})
                profile["provenance"][key] = entry
    return change


def check(change, persona=LT.TEAM):
    """The errors and warnings at profile compliance.retention."""
    with LT.Scenario(persona, change) as persona_dir:
        result = V.validate(str(persona_dir))
    # The required-field and enum checks report at this path too; this check's texts name compliance.zdr_cover.
    hit = lambda items: [i for i in items if (i["record"], i["path"]) == ("profile", PATH)
                         and "zdr_cover" in i["message"]]
    return hit(result["errors"]), hit(result["warnings"])


class RetentionCoverTests(unittest.TestCase):
    def test_zdr_with_none_is_one_error(self):
        errors, warnings = check(pair("zdr", "none"))
        self.assertEqual(len(errors), 1)
        self.assertEqual(warnings, [])
        error = errors[0]
        self.assertIn("compliance.zdr_cover", error["message"])
        self.assertIn("no zero-data-retention agreement", error["message"])
        for word in ("standard", "custom-30-day", "planned", "in-place"):
            self.assertIn(word, error["fix"])

    def test_assumed_status_on_either_field_still_errors(self):
        for kwargs in ({"retention_status": "assumed"}, {"cover_status": "assumed"},
                       {"retention_status": "assumed", "cover_status": "assumed"}):
            errors, _ = check(pair("zdr", "none", **kwargs))
            self.assertEqual(len(errors), 1, kwargs)

    def test_zdr_with_planned_is_one_warning(self):
        errors, warnings = check(pair("zdr", "planned"))
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 1)
        self.assertIn("signed", warnings[0]["message"])
        self.assertIn("compliance.zdr_cover", warnings[0]["message"])

    def test_zdr_with_in_place_is_silent(self):
        self.assertEqual(check(pair("zdr", "in-place")), ([], []))

    def test_other_retentions_are_silent_with_every_cover(self):
        for retention in ("standard", "custom-30-day"):
            for cover in ("none", "planned", "in-place"):
                self.assertEqual(check(pair(retention, cover)), ([], []), (retention, cover))

    def test_open_or_missing_fields_are_silent(self):
        self.assertEqual(check(pair("zdr", "", cover_status="open")), ([], []))
        self.assertEqual(check(pair("", "none", retention_status="open")), ([], []))

        def drop(profile, card):
            del profile["compliance"]["zdr_cover"]
        self.assertEqual(check(drop), ([], []))

    def test_off_catalogue_values_are_silent_here(self):
        self.assertEqual(check(pair("forever", "none")), ([], []))
        self.assertEqual(check(pair("zdr", "maybe")), ([], []))

    def test_malformed_compliance_section_raises_nothing(self):
        for bad in (None, [], ["zdr"], "zdr", 7):
            def change(profile, card, bad=bad):
                profile["compliance"] = bad
            check(change)

    def test_level_refuses_the_error_like_any_validation_error(self):
        with LT.Scenario(LT.TEAM, pair("zdr", "none")) as persona_dir:
            result = L.level(str(persona_dir))
        self.assertFalse(result["ok"])
        self.assertIsNone(result["levelled"])
        self.assertTrue([e for e in result["validation"]["errors"] if e["path"] == PATH])

    def test_the_committed_profiles_are_silent(self):
        for persona in (LT.PE, LT.TEAM, LT.BROKER):
            self.assertEqual(check(None, persona), ([], []), persona.name)

    def test_design_names_both_fields_in_the_rule_paragraph(self):
        text = DESIGN.read_text(encoding="utf-8")
        paragraphs = [p for p in text.split("\n") if "zdr_cover" in p and "retention" in p
                      and "validation error" in p and "warning" in p]
        self.assertTrue(paragraphs)
        self.assertTrue(any("compliance.zdr_cover" in p and "compliance.retention" in p for p in paragraphs))


if __name__ == "__main__":
    unittest.main()
