"""OPS-69: the compendium's spend section, the Claude Code seat condition, and the Google runbook link."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMP = ROOT / "docs" / "compendium"
P09 = (COMP / "09-plans-and-it-controls.md").read_text(encoding="utf-8")
P11 = (COMP / "11-connectors.md").read_text(encoding="utf-8")
P15 = (COMP / "15-governance-and-performance.md").read_text(encoding="utf-8")
SOURCES = (COMP / "sources.md").read_text(encoding="utf-8")

HEADING = "## Spend and usage limits"
LINK = re.compile(r"\]\((https?://[^)\s]+|(?:\./)?\d\d-[a-z0-9-]+\.md[^)\s]*)\)")
URL = re.compile(r"https?://[^)\s>\]]+")


def spend_section():
    lines = P09.splitlines()
    start = lines.index(HEADING)
    out = []
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        out.append(line)
    return out


def norm(url):
    return url.rstrip(".,;").split("#")[0].rstrip("/")


class SpendAndSeats(unittest.TestCase):
    def test_heading_present_after_what_it_can_do(self):
        self.assertIn(HEADING, P09.splitlines())
        self.assertLess(P09.index("## What IT can do on each plan"), P09.index(HEADING))

    def test_every_line_has_source_or_unverified(self):
        for line in spend_section():
            if not line.strip():
                continue
            self.assertTrue(LINK.search(line) or "⚠ Unverified" in line, f"unsourced line: {line[:100]}")

    def test_spend_controls_row_links_section(self):
        row = next(l for l in P09.splitlines() if l.startswith("| Spend controls"))
        self.assertIn("#spend-and-usage-limits", row)

    def test_claude_code_enterprise_cell(self):
        row = next(l for l in P09.splitlines() if l.startswith("| Claude Code |"))
        cell = row.split("|")[4]
        self.assertIn("Premium", cell)
        self.assertIn("11845131", cell)

    def test_page_11_runbook_link(self):
        self.assertNotIn("Our runbooks don't cover these connectors", P11)
        self.assertIn("google-docs-sheets-slides-connectors.md", P11)

    def test_page_15_links_section(self):
        row = next(l for l in P15.splitlines() if "Tooling and spend" in l)
        self.assertIn("spend-and-usage-limits", row)

    def test_section_urls_in_sources(self):
        listed = {norm(u) for u in URL.findall(SOURCES)}
        for line in spend_section():
            for u in URL.findall(line):
                self.assertIn(norm(u), listed, f"not in sources.md: {u}")


if __name__ == "__main__":
    unittest.main()
