"""Checks for the persona template: its steps point at the customer's delivery
repo, and its web rule leaves the reason for the customer to fill in.

Standard library only. Run with: python3 -m unittest tests.test_persona_template
(or: python3 -m unittest discover -s tests)
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "starter-kit" / "templates" / "persona"
README = TEMPLATE / "README.md"
PERSONA = TEMPLATE / "persona.md"
KIT_README = ROOT / "starter-kit" / "README.md"
ANCHOR = "start-a-new-customer"


def slug(heading):
    text = re.sub(r"[^a-z0-9 -]", "", heading.lower())
    return text.strip().replace(" ", "-")


class PersonaTemplateReadmeTest(unittest.TestCase):
    def setUp(self):
        self.text = README.read_text(encoding="utf-8")

    def test_headings_exist(self):
        headings = re.findall(r"^## (.+?)\s*$", self.text, re.M)
        for heading in ("Which form goes where", "Fill it in", "The rule"):
            self.assertIn(heading, headings)

    def test_no_this_repo_destination_or_test_run(self):
        self.assertNotIn("starter-kit/plugins/<role-plugin>", self.text)
        self.assertNotIn("discover -s tests", self.text)

    def test_links_to_start_a_new_customer(self):
        self.assertIn("../../README.md#" + ANCHOR, self.text)
        kit_headings = re.findall(r"^#+ (.+?)\s*$", KIT_README.read_text(encoding="utf-8"), re.M)
        self.assertIn(ANCHOR, [slug(h) for h in kit_headings])


class PersonaTemplateWebRuleTest(unittest.TestCase):
    def test_web_rule_reason_is_fill_in(self):
        lines = [
            line
            for line in PERSONA.read_text(encoding="utf-8").splitlines()
            if "Do not use web search or web fetch" in line
        ]
        self.assertTrue(lines)
        for line in lines:
            self.assertIn("FILL IN", line)


if __name__ == "__main__":
    unittest.main()
