"""Shape checks for the HubSpot and Zendesk twin-marker READMEs.

starter-kit/connectors/hubspot/README.md and starter-kit/connectors/zendesk/README.md
must each exist, carry the nine level-2 headings in order, stay 50 to 160 lines,
open with the 'checked again by a second reader' line, carry the recommendation
label, link the Salesforce marker README (once) and authoring-skills.md, resolve
every relative link, define every source on an accepted https host, and keep the
warning sign inside the two bold labels. starter-kit/README.md must link both,
the rows directly after the zendesk-connector.md row.

Standard library only. Run with: python3 -m unittest tests.test_twin_marker_hubspot_zendesk
"""

import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
KIT = ROOT / "starter-kit"
KIT_README = KIT / "README.md"
SALESFORCE = KIT / "connectors" / "salesforce" / "README.md"
AUTHORING = KIT / "docs" / "authoring-skills.md"
READMES = {
    "hubspot": KIT / "connectors" / "hubspot" / "README.md",
    "zendesk": KIT / "connectors" / "zendesk" / "README.md",
}

HEADINGS = [
    "What this is",
    "Why this marker",
    "Create it (the {admin} admin does this)",
    "Limit who can set it",
    "Make the skill set it",
    "Check it worked",
    "Report on it",
    "What can go wrong",
    "Pages used",
]
ADMIN = {"hubspot": "HubSpot", "zendesk": "Zendesk"}
HOSTS = {
    "knowledge.hubspot.com",
    "developers.hubspot.com",
    "support.zendesk.com",
    "developer.zendesk.com",
    "support.claude.com",
    "claude.com",
}
MIN_LINES, MAX_LINES = 50, 160
SECOND_READER = "Checked 2026-11-16 by the author against the pages listed."
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
    h = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading).replace("`", "")
    h = h.strip().lower()
    h = re.sub(r"[^\w\- ]", "", h)
    return h.replace(" ", "-")


def anchors(path):
    return {slug(m.group(1)) for m in map(HEADING.match, prose(path.read_text(encoding="utf-8"))) if m}


class TwinMarkerReadmes(unittest.TestCase):
    def each(self):
        for name, path in READMES.items():
            with self.subTest(readme=name):
                self.assertTrue(path.is_file(), f"{path.relative_to(ROOT)} is missing")
                yield name, path, path.read_text(encoding="utf-8")

    @staticmethod
    def links(text):
        return LINK.findall("\n".join(prose(text)))

    def test_line_count(self):
        for name, path, text in self.each():
            n = len(text.splitlines())
            self.assertTrue(MIN_LINES <= n <= MAX_LINES, f"{n} lines; want {MIN_LINES} to {MAX_LINES}")

    def test_headings_in_order(self):
        for name, path, text in self.each():
            order = [m.group(1) for m in map(H2.match, prose(text)) if m]
            self.assertEqual(order, [h.format(admin=ADMIN[name]) for h in HEADINGS])

    def test_first_line_and_recommendation(self):
        for name, path, text in self.each():
            first = next((ln for ln in text.splitlines() if ln.strip()), "")
            self.assertIn(SECOND_READER, first)
            self.assertIn("was checked again on 2026-11-16 by a second reader", first)
            self.assertIn("(Our recommendation):", text)

    def test_links_salesforce_pattern_once_and_authoring_skills(self):
        for name, path, text in self.each():
            targets = [(path.parent / unquote(t.partition("#")[0])).resolve() for t in self.links(text) if not EXTERNAL.match(t)]
            self.assertEqual(targets.count(SALESFORCE.resolve()), 1, "Salesforce marker README must be linked once")
            self.assertIn(AUTHORING.resolve(), targets)

    def test_sources_defined_on_accepted_hosts(self):
        for name, path, text in self.each():
            lines = prose(text)
            defined = set()
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
                defined.add(m.group(1))
            used = set()
            for ln in lines:
                if not DEFINITION.match(ln):
                    used.update(TAG.findall(ln))
            self.assertTrue(used, "no source tag is used")
            self.assertEqual(sorted(used - defined), [], "tags used but not defined")

    def test_link_urls_on_accepted_hosts(self):
        for name, path, text in self.each():
            for t in self.links(text):
                if t.startswith("http"):
                    p = urlparse(t)
                    self.assertEqual(p.scheme, "https", t)
                    self.assertIn((p.hostname or "").lower(), HOSTS, t)

    def test_relative_links_and_anchors_resolve(self):
        for name, path, text in self.each():
            for t in self.links(text):
                if EXTERNAL.match(t):
                    continue
                path_part, _, frag = t.partition("#")
                dest = (path.parent / unquote(path_part)).resolve() if path_part else path
                self.assertTrue(dest.exists(), f"does not resolve: {t}")
                if frag and dest.suffix == ".md" and not re.fullmatch(r"L\d+(-L\d+)?", frag):
                    self.assertIn(frag, anchors(dest), f"anchor does not exist: {t}")

    def test_warning_sign_only_inside_labels(self):
        for name, path, text in self.each():
            t = "\n".join(prose(text))
            for label in LABELS:
                t = t.replace(label, "")
            self.assertNotIn("⚠", t)

    def test_kit_readme_rows_follow_zendesk_runbook_row(self):
        rows = [ln for ln in KIT_README.read_text(encoding="utf-8").splitlines() if ln.startswith("|")]
        i = next(i for i, ln in enumerate(rows) if "runbooks/zendesk-connector.md" in ln)
        for offset, name in enumerate(("hubspot", "zendesk"), start=1):
            row = rows[i + offset]
            self.assertIn(f"connectors/{name}/README.md", row)
            self.assertRegex(row, r"^\| \[connectors/[^\]]+\]\(connectors/[^)]+\) \| .+ \|$")


if __name__ == "__main__":
    unittest.main()
