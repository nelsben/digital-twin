"""Compendium pages 11 and 15 say what the Microsoft 365 security guide and HubSpot's
connector page say about Outlook write limits and audit attribution (OPS-72).

Standard library only. Run with: python3 -m unittest tests.test_compendium_outlook_and_audit
(or: python3 -m unittest discover -s tests)
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPENDIUM = ROOT / "docs" / "compendium"
P11 = COMPENDIUM / "11-connectors.md"
P15 = COMPENDIUM / "15-governance-and-performance.md"
SOURCES = COMPENDIUM / "sources.md"

SECURITY_GUIDE = "12684923"
URL = re.compile(r"https?://[^\s)>\]`|]+")


def row(path, label):
    """The table row of a page whose first cell contains label."""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| **") and label in line.split("|")[1]:
            return line
    return None


def sentences_with(text, needle):
    return [s for s in re.split(r"(?<=[.;])\s+", text) if needle in s]


class OutlookRowTest(unittest.TestCase):
    def setUp(self):
        self.row = row(P11, "Outlook")
        self.assertIsNotNone(self.row)

    def test_always_allow_limit_and_dates(self):
        self.assertIn("November 9, 2026", self.row)
        self.assertIn("December 9, 2026", self.row)
        self.assertIn(SECURITY_GUIDE, self.row)
        self.assertIn("Always allow", self.row)

    def test_confirm_before_send_is_no_longer_unverified(self):
        self.assertNotIn("whether Claude asks before each send", self.row)
        self.assertIn("confirm before it sends or forwards an email", self.row)

    def test_write_start_is_answered_in_part(self):
        self.assertIn("blocked by default", self.row)
        self.assertIn("**⚠ Unverified:**", self.row)
        self.assertNotIn("whether write actions start off for a work account", self.row)

    def test_calendar_read_is_a_conflict(self):
        self.assertNotIn("whether reading calendar events needs write actions", self.row)
        self.assertIn("**⚠ Conflict:**", self.row)
        self.assertIn("find_meeting_availability", self.row)
        self.assertIn("find meeting times", self.row)
        self.assertIn("Calendars.Read", self.row)

    def test_entra_role_disagreement_is_marked(self):
        hits = sentences_with(self.row, "Application Administrator")
        self.assertTrue(hits)
        for s in hits:
            self.assertIn("**⚠ Conflict:**", s)
            self.assertIn("Global Administrator", s)

    def test_hipaa_sentence(self):
        self.assertIn("HIPAA", self.row)

    def test_dated_limit_is_not_an_unconditional_one(self):
        # The old row said nothing of the limit; the new one carries its two exceptions.
        self.assertIn("for the first time after November 9, 2026", self.row)
        self.assertIn("Needs approval", self.row)


class AuditRowTest(unittest.TestCase):
    def setUp(self):
        self.row = row(P15, "Source-system audit")
        self.assertIsNotNone(self.row)

    def test_no_longer_says_changes_look_like_the_users(self):
        self.assertNotIn("look like the user's", self.row)
        self.assertNotIn("look like the user’s", self.row)

    def test_hubspot_names_user_and_connector(self):
        hubspot = sentences_with(self.row, "HubSpot")
        self.assertTrue(any("connector" in s and "user" in s for s in hubspot), self.row)
        self.assertIn("set-up-and-use-the-hubspot-connector-for-claude", self.row)

    def test_salesforce_is_marked_unverified(self):
        self.assertIn("Salesforce", self.row)
        self.assertIn("**⚠ Unverified:**", self.row)

    def test_microsoft_365_is_not_left_as_the_user(self):
        self.assertIn("Microsoft 365", self.row)
        self.assertIn("audit log", self.row)

    def test_page_11_hubspot_row_agrees(self):
        h11 = row(P11, "HubSpot")
        self.assertIsNotNone(h11)
        self.assertIn("user and the connector", h11)


class SourcesTest(unittest.TestCase):
    def test_every_url_in_the_changed_rows_is_in_sources(self):
        sources = SOURCES.read_text(encoding="utf-8")
        missing = []
        for path, label in ((P11, "Outlook"), (P11, "HubSpot"), (P15, "Source-system audit")):
            for url in URL.findall(row(path, label)):
                if url.rstrip(".,;") not in sources:
                    missing.append(url)
        self.assertEqual(missing, [])

    def test_new_pages_are_listed(self):
        sources = SOURCES.read_text(encoding="utf-8")
        for page in ("12684923-microsoft-365-connector-security-guide", "12542951-set-up-the-microsoft-365-connector"):
            self.assertIn(page, sources)


class NothingRenamedTest(unittest.TestCase):
    def test_headings_kept(self):
        t11 = P11.read_text(encoding="utf-8")
        for h in ("## What exists for our systems", "## Building our own MCP server"):
            self.assertIn(h, t11)


if __name__ == "__main__":
    unittest.main()
