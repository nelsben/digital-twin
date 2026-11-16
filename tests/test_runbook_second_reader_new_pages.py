"""Checks the second-reader sections for the five pages written after OPS-60 (OPS-70).

The five pages are section 6a of the Microsoft 365 runbook, the Google Docs, Sheets and
Slides runbook, the Claude Code for a role runbook, and the HubSpot and Zendesk marker READMEs.

starter-kit/runbooks/verification-log.md must have, for each page:

- a level-2 section with the exact heading in SECTIONS, holding a five-column table
  (Line or step, Claim, State, Source URL, Old wording -> new wording) of at least 8 rows;
- a state of Confirmed, Corrected or Unverified in every row;
- an http(s) source URL, on an accepted host, in every Confirmed or Corrected row;
- old-to-new text in every Corrected row;
- a summary-table row whose Confirmed, Corrected, Unverified and Total match the section;
- one 'Updated 2026-11-16 (OPS-70)' bullet, and the sections before 'Sources that could not be read'.

Each page no longer says 'not yet checked by a second reader', says it was checked again by a
second reader and links the log. Section 6a of the Microsoft 365 runbook carries the Always-allow
limit with its 'November 9, 2026' condition.

The older sections are not checked here. Standard library only.
Run with: python3 -m unittest tests.test_runbook_second_reader_new_pages
"""

import re
import unittest
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
RUNBOOKS = ROOT / "starter-kit" / "runbooks"
LOG = RUNBOOKS / "verification-log.md"

# summary-table key -> (section heading, page path, how the page links the log)
PAGES = {
    "microsoft-365-connector.md section 6a": (
        "microsoft-365-connector.md section 6a (OPS-70)",
        RUNBOOKS / "microsoft-365-connector.md",
        "verification-log.md",
    ),
    "google-docs-sheets-slides-connectors.md": (
        "google-docs-sheets-slides-connectors.md (OPS-70)",
        RUNBOOKS / "google-docs-sheets-slides-connectors.md",
        "verification-log.md",
    ),
    "claude-code-for-a-role.md": (
        "claude-code-for-a-role.md (OPS-70)",
        RUNBOOKS / "claude-code-for-a-role.md",
        "verification-log.md",
    ),
    "starter-kit/connectors/hubspot/README.md": (
        "starter-kit/connectors/hubspot/README.md (OPS-70)",
        ROOT / "starter-kit" / "connectors" / "hubspot" / "README.md",
        "../../runbooks/verification-log.md",
    ),
    "starter-kit/connectors/zendesk/README.md": (
        "starter-kit/connectors/zendesk/README.md (OPS-70)",
        ROOT / "starter-kit" / "connectors" / "zendesk" / "README.md",
        "../../runbooks/verification-log.md",
    ),
}

STATES = ("Confirmed", "Corrected", "Unverified")
MIN_ROWS = 8
OLD_SENTENCE = "not yet checked by a second reader"
UPDATED_BULLET = "**Updated 2026-11-16 (OPS-70):**"
UNREADABLE_HEADING = "## Sources that could not be read"

ACCEPTED_HOSTS = (
    "support.claude.com",
    "platform.claude.com",
    "code.claude.com",
    "knowledge.hubspot.com",
    "developers.hubspot.com",
    "support.google.com",
    "knowledge.workspace.google.com",
    "developers.google.com",
    "support.zendesk.com",
    "developer.zendesk.com",
    "learn.microsoft.com",
)
ACCEPTED_GITHUB_ORGS = ("anthropics", "anthropic-ai", "modelcontextprotocol")

NEW_SENTENCE = re.compile(
    r"Checked 2026-11-16 by the author against the pages listed\. "
    r"Every claim (?:in this section )?was checked again on \d{4}-\d{2}-\d{2} by a second reader; "
    r"the results are in the \[verification log\]\((?P<link>[^)]+)\)\."
)


def cells(row):
    """Split a markdown table row into stripped cells; '\\|' is a literal pipe."""
    body = row.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|") and not body.endswith("\\|"):
        body = body[:-1]
    parts = re.split(r"(?<!\\)\|", body)
    return [p.replace("\\|", "|").strip() for p in parts]


def is_separator(row):
    return all(re.fullmatch(r":?-{3,}:?", c) for c in cells(row))


def section_lines(text, heading):
    """Lines under the level-2 heading '## <heading>' (exact), or None."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == "## " + heading:
            body = []
            for later in lines[i + 1:]:
                if later.startswith("## "):
                    break
                body.append(later)
            return body
    return None


def section_rows(text, heading):
    body = section_lines(text, heading)
    if body is None:
        return None
    table = [ln for ln in body if ln.lstrip().startswith("|")]
    rows = [cells(r) for r in table if not is_separator(r)]
    return rows[1:] if rows else []  # drop the header row


def summary_counts(text, key):
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        row = cells(line)
        if len(row) == 5 and row[0] == key and all(c.isdigit() for c in row[1:]):
            return tuple(int(c) for c in row[1:])
    return None


def accepted_url(url):
    if not re.fullmatch(r"https?://\S+", url):
        return False
    parsed = urlparse(url)
    host = parsed.hostname or ""
    if host in ACCEPTED_HOSTS:
        return True
    if host == "claude.com":
        return parsed.path.startswith("/docs/") or parsed.path.startswith("/connectors")
    if host == "github.com":
        parts = [p for p in parsed.path.split("/") if p]
        return bool(parts) and parts[0] in ACCEPTED_GITHUB_ORGS
    return False


class SecondReaderNewPages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.log = LOG.read_text(encoding="utf-8")

    def rows(self, key):
        heading = PAGES[key][0]
        rows = section_rows(self.log, heading)
        self.assertIsNotNone(rows, "verification-log.md has no section headed '## %s'" % heading)
        return rows

    def test_each_section_exists_with_enough_rows(self):
        for key in PAGES:
            with self.subTest(page=key):
                rows = self.rows(key)
                self.assertGreaterEqual(len(rows), MIN_ROWS, "%s: %d rows" % (key, len(rows)))
                for row in rows:
                    self.assertEqual(len(row), 5, "%s: row does not have five cells: %s" % (key, row))

    def test_every_state_is_known(self):
        for key in PAGES:
            with self.subTest(page=key):
                for row in self.rows(key):
                    self.assertEqual(len(row), 5, "%s: %s" % (key, row))
                    self.assertIn(row[2], STATES, "%s: bad state %r in row %s" % (key, row[2], row[0]))

    def test_confirmed_and_corrected_rows_have_an_http_source(self):
        for key in PAGES:
            with self.subTest(page=key):
                for row in self.rows(key):
                    step, claim, state, source, change = row
                    if state in ("Confirmed", "Corrected"):
                        self.assertTrue(
                            re.fullmatch(r"https?://\S+", source),
                            "%s row %s (%s): no http(s) source URL: %r" % (key, step, claim[:40], source),
                        )
                        self.assertTrue(
                            accepted_url(source),
                            "%s row %s: source host is not an accepted vendor host: %r" % (key, step, source),
                        )

    def test_corrected_rows_have_old_and_new_wording(self):
        for key in PAGES:
            with self.subTest(page=key):
                for row in self.rows(key):
                    step, claim, state, source, change = row
                    if state == "Corrected":
                        self.assertIn("→", change, "%s row %s: Corrected row lacks old → new text" % (key, step))
                        old, _, new = change.partition("→")
                        self.assertTrue(old.strip() and new.strip(), "%s row %s: empty old or new text" % (key, step))

    def test_summary_counts_match_sections(self):
        for key in PAGES:
            with self.subTest(page=key):
                rows = self.rows(key)
                counts = tuple(sum(1 for r in rows if len(r) == 5 and r[2] == s) for s in STATES)
                expected = counts + (sum(counts),)
                found = summary_counts(self.log, key)
                self.assertIsNotNone(found, "summary table has no row for %s" % key)
                self.assertEqual(found, expected, "%s: summary row vs section (Confirmed, Corrected, Unverified, Total)" % key)

    def test_updated_bullet_and_section_order(self):
        self.assertEqual(self.log.count(UPDATED_BULLET), 1, "want one 'Updated 2026-11-16 (OPS-70)' bullet")
        unreadable = self.log.index(UNREADABLE_HEADING)
        for key, (heading, _, _) in PAGES.items():
            with self.subTest(page=key):
                self.assertIn("## " + heading, self.log)
                self.assertLess(self.log.index("## " + heading), unreadable, "%s comes after the unreadable-sources list" % heading)

    def test_pages_are_checked_and_link_the_log(self):
        for key, (heading, path, link) in PAGES.items():
            with self.subTest(page=key):
                text = " ".join(path.read_text(encoding="utf-8").split())
                self.assertNotIn(OLD_SENTENCE, text)
                match = NEW_SENTENCE.search(text)
                self.assertIsNotNone(match, "%s has no 'checked again by a second reader' sentence" % path.name)
                self.assertEqual(match.group("link"), link)
                self.assertTrue((path.parent / link).resolve() == LOG.resolve(), "%s: log link does not resolve" % path.name)

    def test_outlook_section_carries_the_always_allow_date(self):
        text = (RUNBOOKS / "microsoft-365-connector.md").read_text(encoding="utf-8")
        lines = text.splitlines()
        start = next(i for i, ln in enumerate(lines) if ln.startswith("## 6a. Outlook mail and calendar"))
        end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
        section = " ".join(" ".join(lines[start:end]).split())
        self.assertIn("November 9, 2026", section)
        self.assertIn("first time after November 9, 2026", section)
        self.assertIn("Always allow", section)
        self.assertNotIn("9 November 2026", section)


if __name__ == "__main__":
    unittest.main()
