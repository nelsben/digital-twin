"""Shape checks for the four connector runbooks in starter-kit/runbooks/.

hubspot-connector.md, google-workspace-connectors.md, slack-connector.md and
zendesk-connector.md must exist, carry the eight level-2 headings in order,
carry the 'Checked 2026-11-16' sentence, avoid two words the customer-facing
kit does not use, define every source tag in 'Pages used' with an https URL on
an accepted domain, resolve every relative link, and stay 100 to 260 lines.

The one relative link allowed to dangle is claude-tag-routine.md, named from
slack-connector.md (the page that holds it lands through another card).

Standard library only. Run with: python3 -m unittest discover -s tests
"""

import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
RUNBOOKS = ROOT / "starter-kit" / "runbooks"

FILES = [
    "hubspot-connector.md",
    "google-workspace-connectors.md",
    "slack-connector.md",
    "zendesk-connector.md",
]

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

CHECKED_SENTENCE = re.compile(
    r"Checked 2026-11-16 by the author against the pages listed\. "
    r"Every claim was checked again on \d{4}-\d{2}-\d{2} by a second reader; "
    r"the results are in the \[verification log\]\(verification-log\.md\)\."
)

BANNED = ("partner-kit", "levelled")
UNVERIFIED = "**⚠ Unverified:**"
MIN_LINES, MAX_LINES = 100, 260
MIN_RISK_ROWS = 4

# Accepted hosts (exact match). slack.com is accepted only under /help.
ACCEPTED_HOSTS = {
    "support.claude.com",
    "claude.com",
    "code.claude.com",
    "platform.claude.com",
    "modelcontextprotocol.io",
    "knowledge.hubspot.com",
    "developers.hubspot.com",
    "support.google.com",
    "developers.google.com",
    "workspace.google.com",
    "docs.slack.dev",
    "support.zendesk.com",
    "developer.zendesk.com",
}
SLACK_HELP_HOSTS = {"slack.com", "www.slack.com"}

# Relative links that may point at a file this branch does not hold.
DANGLING_OK = {("slack-connector.md", "claude-tag-routine.md")}

FENCE = re.compile(r"^\s*(```|~~~)")
H2 = re.compile(r"^## (.+?)\s*$")
H3 = re.compile(r"^### (.+?)\s*$")
LINK = re.compile(r"\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
DEFINITION = re.compile(r"^- \[([A-Z])\]\s")
TAG = re.compile(r"\[([A-Z])\](?!\()")
STEP = re.compile(r"^\d+\. ")
STEP_END = re.compile(r"\[[A-Z]\]\)?\.?\s*$")
EXTERNAL = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//)", re.IGNORECASE)


def host_ok(url):
    parsed = urlparse(url)
    if parsed.scheme != "https":
        return False
    host = (parsed.hostname or "").lower()
    if host in ACCEPTED_HOSTS:
        return True
    return host in SLACK_HELP_HOSTS and parsed.path.startswith("/help")


def prose(text):
    """Return the lines outside fenced code blocks."""
    out, fence = [], None
    for line in text.splitlines():
        m = FENCE.match(line)
        if m:
            marker = m.group(1)
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
            continue
        if fence is None:
            out.append(line)
    return out


def sections(lines):
    """Map each level-2 heading to its lines; also return the heading order."""
    order, body, current = [], {}, None
    for line in lines:
        m = H2.match(line)
        if m:
            current = m.group(1)
            order.append(current)
            body[current] = []
        elif current is not None:
            body[current].append(line)
    return order, body


class ConnectorRunbookTests(unittest.TestCase):
    def read(self, name):
        path = RUNBOOKS / name
        self.assertTrue(path.is_file(), f"{name} is missing from starter-kit/runbooks/")
        return path.read_text(encoding="utf-8")

    def each(self):
        for name in FILES:
            with self.subTest(file=name):
                yield name, self.read(name)

    def test_files_exist(self):
        for name in FILES:
            with self.subTest(file=name):
                self.assertTrue((RUNBOOKS / name).is_file(), f"{name} is missing")

    def test_line_count(self):
        for name, text in self.each():
            n = len(text.splitlines())
            self.assertTrue(MIN_LINES <= n <= MAX_LINES, f"{name} has {n} lines; want {MIN_LINES} to {MAX_LINES}")

    def test_headings_in_order(self):
        for name, text in self.each():
            order, _ = sections(prose(text))
            self.assertEqual(order, HEADINGS, f"{name}: level-2 headings differ")

    def test_checked_sentence(self):
        for name, text in self.each():
            _, body = sections(prose(text))
            first = " ".join(" ".join(body.get("Read this first", [])).split())
            self.assertRegex(first, CHECKED_SENTENCE, f"{name}: the 'Checked 2026-11-16' sentence is not in 'Read this first'")

    def test_banned_words(self):
        for name, text in self.each():
            for word in BANNED:
                self.assertNotIn(word, text, f"{name} contains '{word}'")

    def test_pages_used_and_tags(self):
        for name, text in self.each():
            lines = prose(text)
            _, body = sections(lines)
            defined = {}
            for line in body.get("Read this first", []):
                m = DEFINITION.match(line)
                if not m:
                    continue
                urls = [u for u in LINK.findall(line) if u.startswith("http")]
                urls += re.findall(r"(?<![(<])https?://[^\s)>]+", line)
                self.assertTrue(urls, f"{name}: source [{m.group(1)}] has no URL")
                for u in urls:
                    self.assertTrue(host_ok(u), f"{name}: source [{m.group(1)}] uses a URL that is not https on an accepted domain: {u}")
                defined[m.group(1)] = urls
            self.assertTrue(defined, f"{name}: 'Pages used' defines no sources")
            used = set()
            for line in lines:
                if DEFINITION.match(line):
                    continue
                used.update(TAG.findall(line))
            self.assertTrue(used, f"{name}: no source tag is used")
            undefined = sorted(used - set(defined))
            self.assertFalse(undefined, f"{name}: tags used but not defined in 'Pages used': {undefined}")
            unused = sorted(set(defined) - used)
            self.assertFalse(unused, f"{name}: sources defined but never used: {unused}")

    def test_all_link_urls_accepted(self):
        for name, text in self.each():
            for target in LINK.findall("\n".join(prose(text))):
                if target.startswith("http"):
                    self.assertTrue(host_ok(target), f"{name}: link not https on an accepted domain: {target}")

    def test_relative_links_resolve(self):
        for name, text in self.each():
            for target in LINK.findall("\n".join(prose(text))):
                if EXTERNAL.match(target) or target.startswith("#"):
                    continue
                rel = unquote(target.split("#", 1)[0])
                if not rel:
                    continue
                if (name, Path(rel).name) in DANGLING_OK:
                    continue
                dest = (RUNBOOKS / rel).resolve()
                self.assertTrue(dest.exists(), f"{name}: relative link does not resolve: {target}")

    def test_slack_names_the_tag_runbook(self):
        text = self.read("slack-connector.md")
        self.assertIn("claude-tag-routine.md", text)

    def test_steps_end_with_a_tag(self):
        for name, text in self.each():
            _, body = sections(prose(text))
            steps = [ln for ln in body.get("Steps", []) if STEP.match(ln)]
            self.assertTrue(steps, f"{name}: 'Steps' has no numbered steps")
            for ln in steps:
                self.assertTrue(
                    STEP_END.search(ln) or UNVERIFIED in ln,
                    f"{name}: step does not end with a source tag or carry the unverified marker: {ln[:80]}",
                )

    def test_what_this_is_ends_with_role_table(self):
        for name, text in self.each():
            _, body = sections(prose(text))
            part = [ln for ln in body.get("What this is", []) if ln.strip()]
            self.assertIn("03-stakeholders.md", "\n".join(part), f"{name}: no link to 03-stakeholders.md")
            self.assertTrue(part and part[-1].lstrip().startswith("|"), f"{name}: 'What this is' does not end with the role table")

    def test_inputs_link_autonomy(self):
        for name, text in self.each():
            _, body = sections(prose(text))
            self.assertIn("06-autonomy.md", "\n".join(body.get("Inputs you need", [])), f"{name}: 'Inputs you need' does not link 06-autonomy.md")

    def test_what_can_go_wrong_rows(self):
        for name, text in self.each():
            _, body = sections(prose(text))
            rows = [ln for ln in body.get("What can go wrong", []) if ln.lstrip().startswith("|")][2:]
            self.assertGreaterEqual(len(rows), MIN_RISK_ROWS, f"{name}: 'What can go wrong' has {len(rows)} rows")
            for r in rows:
                self.assertTrue(TAG.search(r) or UNVERIFIED in r, f"{name}: risk row has no source tag or unverified marker: {r[:80]}")

    def test_google_has_three_steps_headings(self):
        text = self.read("google-workspace-connectors.md")
        _, body = sections(prose(text))
        h3 = [m.group(1) for m in (H3.match(ln) for ln in body.get("Steps", [])) if m]
        for want in ("Google Drive", "Gmail", "Google Calendar"):
            self.assertIn(want, h3, f"google-workspace-connectors.md: no '### {want}' heading inside 'Steps'")

    def test_check_it_worked_has_read_test(self):
        for name, text in self.each():
            _, body = sections(prose(text))
            part = "\n".join(body.get("Check it worked", [])).lower()
            self.assertIn("read test", part, f"{name}: 'Check it worked' has no read test")
            self.assertIn("expected", part, f"{name}: 'Check it worked' states no expected result")

    def test_hand_over_names_engagement_folder(self):
        for name, text in self.each():
            _, body = sections(prose(text))
            self.assertIn("engagements/", "\n".join(body.get("Hand over", [])), f"{name}: 'Hand over' does not name engagements/")


if __name__ == "__main__":
    unittest.main()
