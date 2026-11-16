"""The sample PE design's Slack Connect (E3) row says what compendium page 11 says
about the Slack directory connector, and the filling-persona-cards eval copy of the
design is byte-identical to it (OPS-73).

Standard library only. Run with: python3 -m unittest tests.test_sample_pe_slack_connect
(or: python3 -m unittest discover -s tests)
"""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DESIGN = ROOT / "engagements" / "sample-pe" / "design.md"
EVAL_COPY = (
    ROOT
    / "partner-kit"
    / "plugins"
    / "twin-consultant"
    / "skills"
    / "filling-persona-cards"
    / "evals"
    / "files"
    / "engagements"
    / "sample-pe"
    / "design.md"
)
ROW_PREFIX = "| **Slack Connect** (E3)"


class SlackConnectRowTest(unittest.TestCase):
    def slack_row(self):
        rows = [
            line
            for line in DESIGN.read_text(encoding="utf-8").splitlines()
            if line.startswith(ROW_PREFIX)
        ]
        self.assertEqual(len(rows), 1, "expected exactly one Slack Connect (E3) row")
        return rows[0]

    def test_row_drops_slack_admin_approval_and_names_the_app(self):
        row = self.slack_row()
        self.assertNotIn("Slack admin approval", row)
        self.assertIn("Claude in Slack app", row)

    def test_eval_copy_is_byte_identical_to_design(self):
        self.assertEqual(DESIGN.read_bytes(), EVAL_COPY.read_bytes())


if __name__ == "__main__":
    unittest.main()
