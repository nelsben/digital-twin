"""Structure checks for the partner kit: its marketplace, the twin-consultant
plugin manifest, and the rule that partner tooling uses the standard library only.

The partner kit is partner-only tooling. It must never appear in the customer
marketplace at the repo root. Design: partner-kit/docs/design.md, section 3.

Standard library only. Run with: python3 -m unittest discover -s tests
"""

import ast
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARTNER_KIT = ROOT / "partner-kit"
PARTNER_MARKETPLACE = PARTNER_KIT / ".claude-plugin" / "marketplace.json"
PLUGIN_DIR = PARTNER_KIT / "plugins" / "twin-consultant"
PLUGIN_MANIFEST = PLUGIN_DIR / ".claude-plugin" / "plugin.json"
ROOT_MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"

# The one package of our own that partner-kit code may import.
OWN_PACKAGES = {"twincard"}


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def imported_top_level_modules(path):
    """Return the top-level module names a Python file imports (absolute imports only)."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                names.add(node.module.split(".")[0])
    return names


class PartnerMarketplaceTests(unittest.TestCase):
    def test_partner_marketplace_lists_only_twin_consultant(self):
        data = load_json(PARTNER_MARKETPLACE)
        self.assertEqual(data.get("name"), "digital-twin-partner")
        plugins = data.get("plugins")
        self.assertIsInstance(plugins, list)
        self.assertEqual(len(plugins), 1, "the partner marketplace lists exactly one plugin")
        self.assertEqual(plugins[0].get("name"), "twin-consultant")
        self.assertEqual(plugins[0].get("source"), "./plugins/twin-consultant")
        self.assertTrue((PARTNER_KIT / plugins[0]["source"]).resolve().is_dir())

    def test_plugin_manifest_names_twin_consultant(self):
        data = load_json(PLUGIN_MANIFEST)
        self.assertEqual(data.get("name"), "twin-consultant")
        self.assertEqual(data.get("version"), "0.1.0")

    def test_twin_consultant_not_in_root_marketplace(self):
        data = load_json(ROOT_MARKETPLACE)
        for entry in data.get("plugins", []):
            self.assertNotEqual(entry.get("name"), "twin-consultant")
            self.assertNotIn("partner-kit", str(entry.get("source", "")))


class StandardLibraryOnlyTests(unittest.TestCase):
    def test_no_imports_outside_stdlib_and_twincard(self):
        stdlib = getattr(sys, "stdlib_module_names", None)
        if stdlib is None:
            self.skipTest("sys.stdlib_module_names needs Python 3.10 or later")
        files = sorted(PARTNER_KIT.rglob("*.py"))
        self.assertTrue(files, "partner-kit holds Python files")
        allowed = set(stdlib) | OWN_PACKAGES | {"__future__"}
        for path in files:
            for name in imported_top_level_modules(path):
                with self.subTest(file=str(path.relative_to(ROOT)), module=name):
                    self.assertIn(name, allowed)


if __name__ == "__main__":
    unittest.main()
