"""Checks for the role-plugin template: starter-kit/templates/role-plugin.

The template is the folder a consultant copies to start one role plugin (one per
role, never per person). These tests check that its plugin.json parses and has
name, version and description, that its README gives the steps in order, that
the template is not listed in the root marketplace, and that the shared plugin
carries no role-specific rules.

Standard library only. Run with: python3 -m unittest tests.test_role_plugin_template
(or: python3 -m unittest discover -s tests)

Plugin manifest fields: https://code.claude.com/docs/en/plugins-reference
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "starter-kit" / "templates" / "role-plugin"
TEMPLATE_README = TEMPLATE / "README.md"
PLUGIN = TEMPLATE / "twin-your-role"
MANIFEST = PLUGIN / ".claude-plugin" / "plugin.json"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
SHARED = ROOT / "starter-kit" / "plugins" / "twin-shared"

# The steps the template README gives, in order: (label, a pattern the step's line must match).
STEPS = (
    ("copy and rename the folder into starter-kit/plugins/", r"copy.*renam.*starter-kit/plugins/"),
    ("fill the persona", r"fill.*persona"),
    ("add skills from templates/skill", r"add.*skills.*templates/skill"),
    ("add the entry to .claude-plugin/marketplace.json", r"add.*entry.*\.claude-plugin/marketplace\.json"),
    ("run the tests", r"run.*tests"),
)

# A rule from a role (here private equity) must not sit in the plugin every twin installs.
ROLE_WORDS = re.compile(r"(?<![\w-])(deal|target|mnpi)(?![\w-])", re.IGNORECASE)


def read(test, path):
    if not path.is_file():
        test.fail(f"{path.relative_to(ROOT)} is missing")
    return path.read_text(encoding="utf-8")


def load_json(test, path):
    try:
        return json.loads(read(test, path))
    except json.JSONDecodeError as err:
        test.fail(f"{path.relative_to(ROOT)} is not valid JSON: {err}")


class TemplateFilesTest(unittest.TestCase):
    def test_template_layout(self):
        for rel in (
            "README.md",
            "twin-your-role/.claude-plugin/plugin.json",
            "twin-your-role/README.md",
            "twin-your-role/skills/.gitkeep",
            "twin-your-role/output-styles/.gitkeep",
            "twin-your-role/persona/README.md",
        ):
            self.assertTrue((TEMPLATE / rel).is_file(), f"templates/role-plugin/{rel} is missing")

    def test_skills_and_output_styles_are_empty(self):
        for folder in ("skills", "output-styles"):
            found = sorted(p.name for p in (PLUGIN / folder).iterdir()) if (PLUGIN / folder).is_dir() else None
            self.assertEqual(found, [".gitkeep"], f"twin-your-role/{folder}/ must hold only .gitkeep")

    def test_persona_folder_links_to_the_persona_template(self):
        text = read(self, PLUGIN / "persona" / "README.md")
        self.assertIn("starter-kit/templates/persona", text)
        targets = [
            (PLUGIN / "persona" / m.group(1)).resolve() for m in re.finditer(r"\]\(([^)#]+)(?:#[^)]*)?\)", text)
        ]
        self.assertIn(
            (ROOT / "starter-kit" / "templates" / "persona" / "README.md").resolve(),
            targets,
            "the persona README must link to templates/persona/README.md",
        )
        self.assertFalse(
            [p for p in (PLUGIN / "persona").iterdir() if p.name != "README.md"],
            "the persona folder holds only README.md: do not copy the persona template's content here",
        )


class ManifestTest(unittest.TestCase):
    def test_plugin_json_has_name_version_description(self):
        data = load_json(self, MANIFEST)
        self.assertEqual(data.get("name"), "twin-your-role")
        self.assertEqual(data.get("version"), "0.1.0")
        description = data.get("description")
        self.assertTrue(isinstance(description, str) and description.strip(), "description is empty")
        self.assertIn("FILL IN", description, "the description is a FILL IN placeholder")


class ReadmeTest(unittest.TestCase):
    def test_readme_names_each_step_in_order(self):
        text = read(self, TEMPLATE_README)
        lines = [normalised.lower() for normalised in (" ".join(l.split()) for l in text.splitlines())]
        position = -1
        for label, pattern in STEPS:
            hits = [i for i, line in enumerate(lines) if i > position and re.search(pattern, line)]
            self.assertTrue(hits, f"the README has no step, in order, to {label}")
            position = hits[0]

    def test_readme_shows_the_marketplace_entry(self):
        text = read(self, TEMPLATE_README)
        for key in ('"name"', '"source"', '"description"', "./starter-kit/plugins/"):
            self.assertIn(key, text, f"the README's marketplace entry lacks {key}")

    def test_readme_says_one_plugin_per_role(self):
        text = " ".join(read(self, TEMPLATE_README).split()).lower()
        self.assertIn("one role plugin per role", text)
        self.assertIn("never per person", text)


class MarketplaceTest(unittest.TestCase):
    def test_template_is_not_listed_in_the_marketplace(self):
        data = load_json(self, MARKETPLACE)
        for entry in data.get("plugins", []):
            source = str(entry.get("source", "")) if isinstance(entry, dict) else ""
            name = entry.get("name") if isinstance(entry, dict) else None
            self.assertNotIn("templates", source, f"marketplace entry {name!r} points into templates/")
            self.assertNotIn("role-plugin", source, f"marketplace entry {name!r} points at the template")
            self.assertNotEqual(name, "twin-your-role", "the template must not be listed in the marketplace")


class SharedPluginIsNeutralTest(unittest.TestCase):
    def test_shared_rules_carry_no_deal_wording(self):
        files = [
            SHARED / ".claude-plugin" / "plugin.json",
            SHARED / "README.md",
            SHARED / "skills" / "writing-in-house-style" / "SKILL.md",
            SHARED / "skills" / "writing-in-house-style" / "references" / "house-style.md",
        ]
        for path in files:
            text = read(self, path)
            for number, line in enumerate(text.splitlines(), 1):
                match = ROLE_WORDS.search(line)
                self.assertIsNone(
                    match,
                    f"{path.relative_to(ROOT)}:{number} says {match.group(0) if match else ''!r}: "
                    "role rules belong in the role plugin, not in twin-shared",
                )

    def test_shared_version_and_readme_note(self):
        data = load_json(self, SHARED / ".claude-plugin" / "plugin.json")
        self.assertEqual(data.get("version"), "0.3.0")
        readme = " ".join(read(self, SHARED / "README.md").split())
        self.assertIn("moved to", readme)
        self.assertIn("twin-pe-deal-team", readme)


if __name__ == "__main__":
    unittest.main()
