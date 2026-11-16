"""Shape checks for the Google Docs, Sheets and Slides connectors runbook.

starter-kit/runbooks/google-docs-sheets-slides-connectors.md must exist, carry
the eight level-2 headings in order and a 'Pages used' list, stay 100 to 260
lines, name each of the three connectors in a heading or a step, carry the
Blocked / Needs approval / recommendation wording and the 'checked again by a
second reader' sentence, define every source tag with an https URL on an
accepted domain, resolve every relative link, and keep the warning sign inside
the two bold labels. google-workspace-connectors.md and starter-kit/README.md
must link to it.

Standard library only. Run with: python3 -m unittest tests.test_runbook_google_docs_sheets_slides
"""

import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
RUNBOOKS = ROOT / "starter-kit" / "runbooks"
NAME = "google-docs-sheets-slides-connectors.md"
RUNBOOK = RUNBOOKS / NAME
WORKSPACE = RUNBOOKS / "google-workspace-connectors.md"
README = ROOT / "starter-kit" / "README.md"

HEADINGS = [
    "What this is",
    "Read this first",
    "Inputs you need",
    "Before you start",
    "Steps",
    "Check it worked",
    "Hand over",
    "What can go wrong",
]
HOSTS = {
    "support.claude.com",
    "claude.com",
    "support.google.com",
    "knowledge.workspace.google.com",
    "developers.google.com",
}
MIN_LINES, MAX_LINES = 100, 260
SECOND_READER = "was checked again on 2026-11-16 by a second reader"
LABELS = ("**⚠ Conflict:**", "**⚠ Unverified:**")

FENCE = re.compile(r"^\s*(```|~~~)")
H2 = re.compile(r"^## (.+?)\s*$")
LINK = re.compile(r"\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
DEFINITION = re.compile(r"^- \[([A-Z])\]\s")
TAG = re.compile(r"\[([A-Z])\](?!\()")
EXTERNAL = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//)", re.IGNORECASE)


def prose(text):
    """Return the lines outside fenced code blocks."""
    out, fence = [], None
    for line in text.splitlines():
        m = FENCE.match(line)
        if m:
            if fence is None:
                fence = m.group(1)
            elif fence == m.group(1):
                fence = None
            continue
        if fence is None:
            out.append(line)
    return out


class GoogleDocsSheetsSlidesRunbook(unittest.TestCase):
    def text(self):
        self.assertTrue(RUNBOOK.is_file(), f"{NAME} is missing from starter-kit/runbooks/")
        return RUNBOOK.read_text(encoding="utf-8")

    def test_line_count(self):
        n = len(self.text().splitlines())
        self.assertTrue(MIN_LINES <= n <= MAX_LINES, f"{n} lines; want {MIN_LINES} to {MAX_LINES}")

    def test_headings_in_order(self):
        order = [m.group(1) for m in map(H2.match, prose(self.text())) if m]
        self.assertEqual(order, HEADINGS)

    def test_pages_used_list(self):
        t = self.text()
        self.assertIn("Pages used", t)
        self.assertTrue([ln for ln in prose(t) if DEFINITION.match(ln)], "no source is defined")

    def test_each_connector_in_a_heading_or_step(self):
        lines = [ln for ln in prose(self.text()) if ln.startswith("#") or re.match(r"^\d+\. ", ln)]
        joined = "\n".join(lines)
        for name in ("Google Docs", "Google Sheets", "Google Slides"):
            self.assertIn(name, joined, f"{name} is in no heading or step")

    def test_required_wording(self):
        t = self.text()
        for s in ("Blocked", "Needs approval", "(Our recommendation):", SECOND_READER):
            self.assertIn(s, t)

    def test_sources_defined_with_https_urls(self):
        lines = prose(self.text())
        defined = {}
        for ln in lines:
            m = DEFINITION.match(ln)
            if not m:
                continue
            urls = [u for u in LINK.findall(ln) if u.startswith("http")]
            urls += re.findall(r"(?<![(<])https?://[^\s)>]+", ln)
            self.assertTrue(urls, f"source [{m.group(1)}] has no URL")
            for u in urls:
                p = urlparse(u)
                self.assertEqual(p.scheme, "https", u)
                self.assertIn((p.hostname or "").lower(), HOSTS, u)
            defined[m.group(1)] = urls
        used = set()
        for ln in lines:
            if not DEFINITION.match(ln):
                used.update(TAG.findall(ln))
        self.assertTrue(used, "no source tag is used")
        self.assertEqual(sorted(used - set(defined)), [], "tags used but not defined")

    def test_link_urls_on_accepted_hosts(self):
        for target in LINK.findall("\n".join(prose(self.text()))):
            if target.startswith("http"):
                p = urlparse(target)
                self.assertEqual(p.scheme, "https", target)
                self.assertIn((p.hostname or "").lower(), HOSTS, target)

    def test_relative_links_resolve(self):
        for target in LINK.findall("\n".join(prose(self.text()))):
            if EXTERNAL.match(target) or target.startswith("#"):
                continue
            rel = unquote(target.split("#", 1)[0])
            if rel:
                self.assertTrue((RUNBOOKS / rel).resolve().exists(), f"does not resolve: {target}")

    def test_warning_sign_only_inside_labels(self):
        t = "\n".join(prose(self.text()))
        for label in LABELS:
            t = t.replace(label, "")
        self.assertNotIn("⚠", t)

    def test_workspace_runbook_links_it(self):
        self.assertIn(NAME, WORKSPACE.read_text(encoding="utf-8"))

    def test_readme_row_follows_workspace_row(self):
        rows = [ln for ln in README.read_text(encoding="utf-8").splitlines() if ln.startswith("|")]
        i = next(i for i, ln in enumerate(rows) if "runbooks/google-workspace-connectors.md" in ln)
        self.assertIn(f"runbooks/{NAME}", rows[i + 1])
        self.assertRegex(rows[i + 1], r"^\| \[runbooks/[^\]]+\]\(runbooks/[^)]+\) \| .+ \|$")


if __name__ == "__main__":
    unittest.main()
