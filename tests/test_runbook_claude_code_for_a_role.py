"""Shape checks for the 'Claude Code for a role' runbook.

starter-kit/runbooks/claude-code-for-a-role.md must exist, carry the eight
level-2 headings in order and a 'Pages used' list, stay 80 to 220 lines, name
macOS and Windows, link identity-devices-publishing.md sections 3, 4 or 5, and
6 by anchors that exist there, link compendium page 13, carry the
recommendation label and the 'not yet checked by a second reader' sentence,
define every source tag with an https URL on an accepted domain, resolve every
relative link and anchor, and keep the warning sign inside the two bold
labels. starter-kit/README.md must link it.

Standard library only. Run with: python3 -m unittest tests.test_runbook_claude_code_for_a_role
"""

import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
RUNBOOKS = ROOT / "starter-kit" / "runbooks"
NAME = "claude-code-for-a-role.md"
RUNBOOK = RUNBOOKS / NAME
IDENTITY_NAME = "identity-devices-publishing.md"
IDENTITY = RUNBOOKS / IDENTITY_NAME
DEVICES = ROOT / "docs" / "compendium" / "13-devices.md"
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
HOSTS = {"code.claude.com", "support.claude.com", "claude.com"}
MIN_LINES, MAX_LINES = 80, 220
SECOND_READER = "not yet checked by a second reader"
LABELS = ("**⚠ Conflict:**", "**⚠ Unverified:**")

FENCE = re.compile(r"^\s*(```|~~~)")
H2 = re.compile(r"^## (.+?)\s*$")
HEADING = re.compile(r"^#{1,6} (.+?)\s*#*\s*$")
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


def slug(heading):
    """GitHub-style anchor for a heading."""
    h = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading).replace("`", "")
    h = h.strip().lower()
    h = re.sub(r"[^\w\- ]", "", h)
    return h.replace(" ", "-")


def anchors(path):
    return {slug(m.group(1)) for m in map(HEADING.match, prose(path.read_text(encoding="utf-8"))) if m}


def identity_fragments(links):
    return [t.split("#", 1)[1] for t in links if t.split("#", 1)[0].endswith(IDENTITY_NAME) and "#" in t]


class ClaudeCodeForARoleRunbook(unittest.TestCase):
    def text(self):
        self.assertTrue(RUNBOOK.is_file(), f"{NAME} is missing from starter-kit/runbooks/")
        return RUNBOOK.read_text(encoding="utf-8")

    def links(self):
        return LINK.findall("\n".join(prose(self.text())))

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

    def test_names_both_operating_systems(self):
        t = self.text()
        self.assertIn("macOS", t)
        self.assertIn("Windows", t)

    def test_required_wording(self):
        t = self.text()
        for s in ("(Our recommendation):", SECOND_READER):
            self.assertIn(s, t)

    def test_links_identity_runbook_sections(self):
        frags = identity_fragments(self.links())
        a = anchors(IDENTITY)
        for f in frags:
            self.assertIn(f, a, f"anchor #{f} is not a heading in {IDENTITY_NAME}")
        joined = " ".join(frags)
        self.assertRegex(joined, r"(^|\s)3-", "no link to identity runbook section 3")
        self.assertRegex(joined, r"(^|\s)[45]-", "no link to identity runbook section 4 or 5")
        self.assertRegex(joined, r"(^|\s)6-", "no link to identity runbook section 6")

    def test_links_devices_page(self):
        self.assertTrue(any("compendium/13-devices.md" in t for t in self.links()))

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
        for target in self.links():
            if target.startswith("http"):
                p = urlparse(target)
                self.assertEqual(p.scheme, "https", target)
                self.assertIn((p.hostname or "").lower(), HOSTS, target)

    def test_relative_links_and_anchors_resolve(self):
        for target in self.links():
            if EXTERNAL.match(target):
                continue
            path_part, _, frag = target.partition("#")
            rel = unquote(path_part)
            dest = (RUNBOOKS / rel).resolve() if rel else RUNBOOK
            self.assertTrue(dest.exists(), f"does not resolve: {target}")
            if frag and dest.suffix == ".md" and not re.fullmatch(r"L\d+(-L\d+)?", frag):
                self.assertIn(frag, anchors(dest), f"anchor does not exist: {target}")

    def test_warning_sign_only_inside_labels(self):
        t = "\n".join(prose(self.text()))
        for label in LABELS:
            t = t.replace(label, "")
        self.assertNotIn("⚠", t)

    def test_readme_row_follows_identity_row(self):
        rows = [ln for ln in README.read_text(encoding="utf-8").splitlines() if ln.startswith("|")]
        i = next(i for i, ln in enumerate(rows) if f"runbooks/{IDENTITY_NAME}" in ln)
        self.assertIn(f"runbooks/{NAME}", rows[i + 1])
        self.assertRegex(rows[i + 1], r"^\| \[runbooks/[^\]]+\]\(runbooks/[^)]+\) \| .+ \|$")


if __name__ == "__main__":
    unittest.main()
