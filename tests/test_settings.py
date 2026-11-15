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
    # MCP allowlist, documented at https://code.claude.com/docs/en/managed-mcp
    "allowManagedMcpServersOnly",
    "allowedMcpServers",
    # Plugin keys, documented at https://code.claude.com/docs/en/plugins/org
    "extraKnownMarketplaces",
    "enabledPlugins",
    # Environment variables, documented in the settings reference
    "env",
})

# The 12 third-party connectors registered by Anthropic's financial-analysis
# plugin (compendium 17). None may appear anywhere in the pe-zdr baseline.
UPSTREAM_FINANCIAL_VENDORS = (
    "daloopa", "morningstar", "kensho", "factset", "moodys", "blueskyapi",
    "aiera", "lseg", "pitchbook", "chronograph", "egnyte", "box",
)
MCP_ENTRY_KEYS = frozenset({"serverUrl", "serverCommand", "serverName"})

UUID_PATTERN = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)
PLACEHOLDER = "REPLACE-WITH-ORG-UUID"

MARKETPLACE = "digital-twin-kit"
SENSITIVE_FILES = EXPECTED_FILES[1:]
GOVERNANCE_LABELS = {
    "confidential.managed-settings.json": "confidential",
    "pe-zdr.managed-settings.json": "pe-zdr",
    "hipaa.managed-settings.json": "hipaa",
}
SALT_PLACEHOLDER = "REPLACE-WITH-GOVERNANCE-SALT"


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

    def test_pe_zdr_mcp_allowlist_is_managed_only(self):
        data = load("pe-zdr.managed-settings.json")
        self.assertIs(data.get("allowManagedMcpServersOnly"), True)
        allowed = data.get("allowedMcpServers")
        self.assertIsInstance(allowed, list)
        self.assertTrue(allowed, "allowlist must not be empty")
        for entry in allowed:
            with self.subTest(entry=entry):
                self.assertIsInstance(entry, dict)
                self.assertEqual(len(entry), 1, "one identifying key per entry")
                self.assertTrue(set(entry) <= MCP_ENTRY_KEYS)

    def test_pe_zdr_mcp_allowlist_has_placeholders_for_reviewed_connectors(self):
        allowed = load("pe-zdr.managed-settings.json")["allowedMcpServers"]
        urls = [e["serverUrl"] for e in allowed if "serverUrl" in e]
        for label in ("SALESFORCE", "MICROSOFT-365"):
            with self.subTest(connector=label):
                self.assertTrue(
                    any(f"REPLACE-WITH-{label}" in u for u in urls),
                    f"no REPLACE-WITH-{label} serverUrl placeholder",
                )

    def test_pe_zdr_names_no_upstream_financial_vendor(self):
        text = (SETTINGS_DIR / "pe-zdr.managed-settings.json").read_text(
            encoding="utf-8"
        ).lower()
        for vendor in UPSTREAM_FINANCIAL_VENDORS:
            with self.subTest(vendor=vendor):
                self.assertIsNone(re.search(rf"\b{vendor}\b", text))

    def test_marketplace_registered_from_the_allowlisted_source(self):
        for name in EXPECTED_FILES:
            with self.subTest(file=name):
                data = load(name)
                entry = data.get("extraKnownMarketplaces", {}).get(MARKETPLACE)
                self.assertIsInstance(entry, dict)
                self.assertEqual(list(data["extraKnownMarketplaces"]), [MARKETPLACE])
                self.assertEqual(entry["source"], data["strictKnownMarketplaces"][0])
                self.assertEqual(
                    entry["source"]["repo"], "REPLACE-WITH-GITHUB-ORG/digital-twin-kit"
                )

    def test_twin_shared_enabled_everywhere(self):
        for name in EXPECTED_FILES:
            with self.subTest(file=name):
                plugins = load(name).get("enabledPlugins", {})
                self.assertIs(plugins.get(f"twin-shared@{MARKETPLACE}"), True)

    def test_twin_governance_enabled_in_exactly_the_sensitive_files(self):
        key = f"twin-governance@{MARKETPLACE}"
        for name in EXPECTED_FILES:
            with self.subTest(file=name):
                plugins = load(name).get("enabledPlugins", {})
                if name in SENSITIVE_FILES:
                    self.assertIs(plugins.get(key), True)
                else:
                    self.assertNotIn(key, plugins)

    def test_no_role_plugin_enabled_in_any_baseline(self):
        allowed = {f"twin-shared@{MARKETPLACE}", f"twin-governance@{MARKETPLACE}"}
        for name in EXPECTED_FILES:
            with self.subTest(file=name):
                plugins = load(name).get("enabledPlugins", {})
                self.assertFalse(set(plugins) - allowed, "role plugins are per-group")
                for plugin_id in plugins:
                    self.assertTrue(plugin_id.endswith(f"@{MARKETPLACE}"))

    def test_governance_env_set_where_the_plugin_is_enabled(self):
        for name in EXPECTED_FILES:
            with self.subTest(file=name):
                env = load(name).get("env")
                if name not in GOVERNANCE_LABELS:
                    self.assertIsNone(env)
                    continue
                self.assertEqual(
                    set(env), {"TWIN_GOVERNANCE_ORG_LABEL", "TWIN_GOVERNANCE_SALT"}
                )
                self.assertEqual(env["TWIN_GOVERNANCE_ORG_LABEL"], GOVERNANCE_LABELS[name])
                self.assertEqual(env["TWIN_GOVERNANCE_SALT"], SALT_PLACEHOLDER)

    def test_pe_zdr_and_hipaa_force_the_same_login_method(self):
        hipaa = load("hipaa.managed-settings.json").get("forceLoginMethod")
        self.assertEqual(hipaa, "claudeai")
        self.assertEqual(load("pe-zdr.managed-settings.json").get("forceLoginMethod"), hipaa)

    def test_readme_names_the_salt_placeholder_and_drops_the_todo(self):
        text = (SETTINGS_DIR / "README.md").read_text(encoding="utf-8")
        self.assertIn(SALT_PLACEHOLDER, text)
        self.assertNotIn("TODO", text)
        self.assertNotIn("(placeholder)", text)

    def test_readme_under_80_lines(self):
        readme = SETTINGS_DIR / "README.md"
        self.assertTrue(readme.exists())
        self.assertLess(len(readme.read_text(encoding="utf-8").splitlines()), 80)


if __name__ == "__main__":
    unittest.main()
