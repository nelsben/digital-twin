"""Checks the verification-log sections for the four runtime runbooks (OPS-59).

For each file in VERIFIED_RUNBOOKS:

- starter-kit/runbooks/verification-log.md has a level-2 section whose heading
  starts with the file name, holding a five-column table of at least 15 rows;
- every row's state is Confirmed, Corrected or Unverified;
- every Confirmed or Corrected row has a source: one https URL on an accepted
  domain, or 'repo: <path>' where the path exists in this repository;
- every Corrected row has old-to-new text;
- the summary table has a row for the file whose four numbers match the
  section, Total being the sum;
- the runbook no longer says 'Not yet independently verified' and carries the
  second-reader sentence with a link to verification-log.md.

The sections for the earlier runbooks are not checked here. Standard library only.
"""

import re
import unittest
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
RUNBOOKS = ROOT / "starter-kit" / "runbooks"
LOG = RUNBOOKS / "verification-log.md"

VERIFIED_RUNBOOKS = [
    "claude-code-scheduled-task.md",
    "claude-tag-routine.md",
    "managed-agents.md",
    "agent-sdk-runner.md",
]

STATES = ("Confirmed", "Corrected", "Unverified")
MIN_ROWS = 15

ACCEPTED_HOSTS = ("platform.claude.com", "code.claude.com", "support.claude.com")
ACCEPTED_GITHUB_ORGS = ("anthropics", "anthropic-ai", "modelcontextprotocol")

NEW_SENTENCE = re.compile(
    r"Checked 2026-11-16 by the author against the pages listed\. "
    r"Every claim was checked again on \d{4}-\d{2}-\d{2} by a second reader; "
    r"the results are in the \[verification log\]\(verification-log\.md\)\."
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


def section_rows(text, file_name):
    """Body rows of the table under '## <file_name>...', or None if no section."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.startswith("## ") and line[3:].strip().startswith(file_name):
            start = i + 1
            break
    if start is None:
        return None
    table = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        if line.lstrip().startswith("|"):
            table.append(line)
    rows = [cells(r) for r in table if not is_separator(r)]
    return rows[1:] if rows else []  # drop the header row


def summary_counts(text, file_name):
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        row = cells(line)
        if len(row) == 5 and row[0] == file_name and all(c.isdigit() for c in row[1:]):
            return tuple(int(c) for c in row[1:])
    return None


def accepted_url(url):
    parsed = urlparse(url)
    if parsed.scheme != "https":
        return False
    host = parsed.hostname or ""
    if host in ACCEPTED_HOSTS:
        return True
    if host == "claude.com":
        return parsed.path.startswith("/docs/") or parsed.path.startswith("/connectors")
    if host == "github.com":
        parts = [p for p in parsed.path.split("/") if p]
        return bool(parts) and parts[0] in ACCEPTED_GITHUB_ORGS
    return False


def source_ok(source):
    source = source.strip()
    if source.startswith("repo:"):
        path = source[len("repo:"):].strip()
        return bool(path) and (ROOT / path).exists()
    return bool(re.fullmatch(r"https://\S+", source)) and accepted_url(source)


class VerificationLogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.log = LOG.read_text(encoding="utf-8")

    def rows(self, name):
        rows = section_rows(self.log, name)
        self.assertIsNotNone(rows, "verification-log.md has no section headed '## %s ...'" % name)
        return rows

    def test_sections_have_enough_rows(self):
        for name in VERIFIED_RUNBOOKS:
            with self.subTest(runbook=name):
                rows = self.rows(name)
                self.assertGreaterEqual(len(rows), MIN_ROWS, "%s: %d rows" % (name, len(rows)))
                for row in rows:
                    self.assertEqual(len(row), 5, "%s: row does not have five cells: %s" % (name, row))

    def test_states_and_sources(self):
        for name in VERIFIED_RUNBOOKS:
            with self.subTest(runbook=name):
                for row in self.rows(name):
                    self.assertEqual(len(row), 5, "%s: %s" % (name, row))
                    step, claim, state, source, change = row
                    self.assertIn(state, STATES, "%s: bad state %r in row %s" % (name, state, step))
                    if state in ("Confirmed", "Corrected"):
                        self.assertTrue(
                            source_ok(source),
                            "%s row %s (%s): source is not an accepted https URL or an existing repo path: %r"
                            % (name, step, claim[:40], source),
                        )
                    if state == "Corrected":
                        self.assertIn("→", change, "%s row %s: Corrected row lacks old → new text" % (name, step))
                        old, _, new = change.partition("→")
                        self.assertTrue(old.strip() and new.strip(), "%s row %s: empty old or new text" % (name, step))

    def test_summary_matches_section(self):
        for name in VERIFIED_RUNBOOKS:
            with self.subTest(runbook=name):
                rows = self.rows(name)
                counts = tuple(sum(1 for r in rows if len(r) == 5 and r[2] == s) for s in STATES)
                expected = counts + (sum(counts),)
                found = summary_counts(self.log, name)
                self.assertIsNotNone(found, "summary table has no row for %s" % name)
                self.assertEqual(found, expected, "%s: summary row vs section (Confirmed, Corrected, Unverified, Total)" % name)

    def test_runbook_points_at_the_log(self):
        for name in VERIFIED_RUNBOOKS:
            with self.subTest(runbook=name):
                text = " ".join((RUNBOOKS / name).read_text(encoding="utf-8").split())
                self.assertNotIn("Not yet independently verified", text)
                self.assertRegex(text, NEW_SENTENCE)


if __name__ == "__main__":
    unittest.main()
