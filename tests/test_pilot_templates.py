"""Checks for the pilot kit templates in starter-kit/templates/pilot: the files
exist, hold the headings and FILL IN markers they promise, every relative link
resolves, every anchor into the compendium or playbook matches a heading, and
the files stay free of partner-only wording.

Standard library only. Run with: python3 -m unittest tests.test_pilot_templates
(or: python3 -m unittest discover -s tests)
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PILOT = ROOT / "starter-kit" / "templates" / "pilot"
FILES = ("README.md", "scorecard.md", "memory-policy.md", "pilot-training.md")
LAYERS = ("Adoption", "Quality", "Value", "Safety")
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def slug(heading):
    text = re.sub(r"[^a-z0-9 -]", "", heading.lower())
    return text.strip().replace(" ", "-")


def read(name):
    return (PILOT / name).read_text(encoding="utf-8")


def headings(text, level=None):
    marks = "#+" if level is None else "#{%d}" % level
    return re.findall(r"^" + marks + r" (.+?)\s*$", text, re.M)


class PilotFilesTest(unittest.TestCase):
    def test_four_files_exist(self):
        for name in FILES:
            self.assertTrue((PILOT / name).is_file(), name)

    def test_readme_headings(self):
        found = headings(read("README.md"), 2)
        for heading in ("What is here", "Fill them in", "When to use them"):
            self.assertIn(heading, found)

    def test_readme_is_short(self):
        self.assertLess(len(read("README.md").splitlines()), 40)

    def test_scorecard_headings_and_layers(self):
        text = read("scorecard.md")
        found = headings(text)
        for heading in ("Per task", "Decision this month", "Actions"):
            self.assertIn(heading, found)
        for layer in LAYERS:
            self.assertTrue(any(layer in h for h in found), layer)

    def test_fill_in_markers(self):
        for name in ("memory-policy.md", "pilot-training.md"):
            self.assertGreaterEqual(read(name).count("FILL IN"), 5, name)

    def test_training_headings(self):
        found = headings(read("pilot-training.md"))
        for heading in ("Session outline", "Report a failure or a wrong draft"):
            self.assertTrue(any(heading in h for h in found), heading)

    def test_no_partner_wording(self):
        for name in FILES:
            text = read(name).lower()
            self.assertNotIn("partner-kit", text, name)
            self.assertNotIn("levelled", text, name)


class PilotLinksTest(unittest.TestCase):
    def test_links_resolve(self):
        checked = 0
        for name in FILES:
            for target in LINK.findall(read(name)):
                if re.match(r"[a-z]+:", target) or target.startswith("#"):
                    continue
                path, _, anchor = target.partition("#")
                dest = (PILOT / path).resolve()
                self.assertTrue(dest.exists(), "%s links to missing %s" % (name, target))
                checked += 1
                if anchor and dest.suffix == ".md":
                    slugs = [slug(h) for h in headings(dest.read_text(encoding="utf-8"))]
                    self.assertIn(anchor, slugs, "%s: no heading for %s" % (name, target))
        self.assertGreater(checked, 0)


if __name__ == "__main__":
    unittest.main()
