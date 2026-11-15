"""Checks for the managed-settings baselines in starter-kit/settings.

Standard library only. Run with: python3 -m unittest discover -s tests
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SETTINGS_DIR = ROOT / "starter-kit" / "settings"

EXPECTED_FILES = (
    "general.managed-settings.json",
    "confidential.managed-settings.json",
    "pe-zdr.managed-settings.json",
    "hipaa.managed-settings.json",
)
WEB_DENY_FILES = ("pe-zdr.managed-settings.json", "hipaa.managed-settings.json")

# Allowed top-level keys. Each is documented in the settings reference:
# https://code.claude.com/docs/en/settings-reference
# (settings files: https://code.claude.com/docs/en/settings ;
#  managed deployment: https://code.claude.com/docs/en/managed-settings ;
#  marketplace keys: https://code.claude.com/docs/en/plugins/org)
ALLOWED_TOP_LEVEL_KEYS = frozenset({
    "strictKnownMarketplaces",
    "forceLoginOrgUUID",
    "forceLoginMethod",
    "allowedProviders",
    "cleanupPeriodDays",
    "allowManagedHooksOnly",
    "permissions",
})

UUID_PATTERN = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)
PLACEHOLDER = "REPLACE-WITH-ORG-UUID"


def load(name):
    return json.loads((SETTINGS_DIR / name).read_text(encoding="utf-8"))


class ManagedSettingsTests(unittest.TestCase):
    def test_all_four_files_exist_and_no_others(self):
        found = sorted(p.name for p in SETTINGS_DIR.glob("*.managed-settings.json"))
        self.assertEqual(found, sorted(EXPECTED_FILES))

    def test_files_parse(self):
        for name in EXPECTED_FILES:
            with self.subTest(file=name):
                self.assertIsInstance(load(name), dict)

    def test_top_level_keys_allowlisted(self):
        for name in EXPECTED_FILES:
            with self.subTest(file=name):
                unknown = set(load(name)) - ALLOWED_TOP_LEVEL_KEYS
                self.assertFalse(unknown, f"keys not in allowlist: {sorted(unknown)}")

    def test_every_file_restricts_marketplaces(self):
        for name in EXPECTED_FILES:
            with self.subTest(file=name):
                sources = load(name).get("strictKnownMarketplaces")
                self.assertIsInstance(sources, list)
                self.assertEqual(len(sources), 1, "exactly one reviewed marketplace")
                self.assertIn("source", sources[0])

    def test_org_lock_uses_placeholder(self):
        for name in EXPECTED_FILES:
            with self.subTest(file=name):
                self.assertEqual(load(name).get("forceLoginOrgUUID"), PLACEHOLDER)

    def test_bypass_permissions_disabled(self):
        for name in EXPECTED_FILES:
            with self.subTest(file=name):
                perms = load(name).get("permissions", {})
                self.assertEqual(perms.get("disableBypassPermissionsMode"), "disable")

    def test_sensitive_classes_managed_hooks_and_secret_denies(self):
        for name in EXPECTED_FILES[1:]:
            with self.subTest(file=name):
                data = load(name)
                self.assertIs(data.get("allowManagedHooksOnly"), True)
                deny = data.get("permissions", {}).get("deny", [])
                self.assertIn("Read(**/.env)", deny)
                self.assertTrue(any("credentials" in d for d in deny))

    def test_pe_zdr_and_hipaa_deny_web_tools(self):
        for name in WEB_DENY_FILES:
            with self.subTest(file=name):
                deny = load(name).get("permissions", {}).get("deny", [])
                self.assertIn("WebFetch", deny)
                self.assertIn("WebSearch", deny)

    def test_no_real_looking_uuid(self):
        for path in SETTINGS_DIR.glob("*.managed-settings.json"):
            with self.subTest(file=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIsNone(UUID_PATTERN.search(text))
                self.assertIn(PLACEHOLDER, text)

    def test_readme_under_80_lines(self):
        readme = SETTINGS_DIR / "README.md"
        self.assertTrue(readme.exists())
        self.assertLess(len(readme.read_text(encoding="utf-8").splitlines()), 80)


if __name__ == "__main__":
    unittest.main()
