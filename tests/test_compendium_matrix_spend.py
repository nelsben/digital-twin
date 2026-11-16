"""OPS-71: page 09's feature matrix agrees with its spend section and with the pricing page."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P09 = (ROOT / "docs" / "compendium" / "09-plans-and-it-controls.md").read_text(encoding="utf-8")


def cells(prefix):
    row = next(l for l in P09.splitlines() if l.startswith(prefix))
    return [c.strip() for c in row.strip().strip("|").split("|")]


class MatrixSpend(unittest.TestCase):
    def test_team_spend_cell_says_org_wide_and_per_user_limited(self):
        team = cells("| Spend controls")[2]
        self.assertIn("org-wide", team)
        self.assertIn("per-user", team)
        self.assertIn("support.claude.com/en/articles/12005970", team)

    def test_enterprise_spend_cell_keeps_per_user_and_adds_groups(self):
        ent = cells("| Spend controls")[3]
        self.assertIn("per-user", ent)
        self.assertIn("group", ent)
        self.assertIn("#spend-and-usage-limits", ent)

    def test_claude_code_individual_cell_links_pricing(self):
        indiv = cells("| Claude Code |")[1]
        self.assertIn("Pro and up", indiv)
        self.assertIn("claude.com/pricing", indiv)


if __name__ == "__main__":
    unittest.main()
