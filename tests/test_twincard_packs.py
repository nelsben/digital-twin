"""Tests for the industry packs: the format, the loader and the shipped packs.

The format is in partner-kit/docs/design.md, section 7.1. Every shipped pack
is checked against the repo: its cite paths and anchors exist, its runbooks
and settings baseline exist, its compliance defaults are real profile paths
with the catalogue's type, and an unverified entry cites a page that carries
the Unverified marker.

Standard library only. Run with: python3 -m unittest discover -s tests
"""

import copy
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN_DIR = ROOT / "partner-kit" / "plugins" / "twin-consultant"
SCRIPTS_DIR = PLUGIN_DIR / "scripts"
PACKS_DIR = PLUGIN_DIR / "data" / "industry-packs"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from twincard import fields as tc_fields  # noqa: E402
from twincard import packs  # noqa: E402
from twincard import level  # noqa: E402
from twincard.validate import _type_ok  # noqa: E402

LISTS = ("anthropic_starting_points", "data_providers", "connector_defaults",
         "compliance_defaults", "typical_tasks")
UNVERIFIED_MARKER = re.compile(r"unverified|not confirmed", re.IGNORECASE)
# The kit's connector runbook for each product the general and b2b-software packs name (OPS-55).
KIT_RUNBOOKS = {
    "HubSpot": "starter-kit/runbooks/hubspot-connector.md",
    "Google Drive / Sheets": "starter-kit/runbooks/google-workspace-connectors.md",
    "Google Drive": "starter-kit/runbooks/google-workspace-connectors.md",
    "Gmail": "starter-kit/runbooks/google-workspace-connectors.md",
    "Google Calendar": "starter-kit/runbooks/google-workspace-connectors.md",
    "Slack": "starter-kit/runbooks/slack-connector.md",
    "Zendesk": "starter-kit/runbooks/zendesk-connector.md",
}


def slug(heading):
    """GitHub's anchor for a heading line's text."""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading)
    text = text.replace("`", "").replace("*", "").strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def anchors_of(page_text):
    found = set()
    counts = {}
    in_fence = False
    for line in page_text.splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        match = None if in_fence else re.match(r"^#{1,6}\s+(.*?)\s*#*\s*$", line)
        if match:
            base = slug(match.group(1))
            seen = counts.get(base, 0)
            counts[base] = seen + 1
            found.add(base if seen == 0 else "%s-%d" % (base, seen))
    return found


def entries(pack):
    for name in LISTS:
        for index, entry in enumerate(pack.get(name, [])):
            yield "%s[%d]" % (name, index), entry


def pack_files():
    return sorted(PACKS_DIR.glob("*.json"))


class SlugTests(unittest.TestCase):
    """The anchor rule the tests rely on, checked on headings the packs cite."""

    def test_slug_rules(self):
        self.assertEqual(slug("1. What's in `private-equity`"), "1-whats-in-private-equity")
        self.assertEqual(slug("1. Skills in github.com/anthropics/skills"), "1-skills-in-githubcomanthropicsskills")
        self.assertEqual(slug("Agent Skills: overview and best practices"), "agent-skills-overview-and-best-practices")
        self.assertEqual(slug("The private-equity twin at a glance (our recommendation)"),
                         "the-private-equity-twin-at-a-glance-our-recommendation")


class ShippedPackTests(unittest.TestCase):
    def test_general_and_private_equity_ship(self):
        self.assertEqual(packs.list_packs(), sorted(p.stem for p in pack_files()))
        self.assertIn("general", packs.list_packs())
        self.assertIn("private-equity", packs.list_packs())
        self.assertIn("b2b-software", packs.list_packs())

    def test_every_pack_file(self):
        self.assertTrue(pack_files())
        for path in pack_files():
            with self.subTest(pack=path.stem):
                pack = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(packs.pack_problems(pack), [])
                self.assertEqual(pack["id"], path.stem)
                self.assertEqual(packs.load_pack(path.stem), pack)

    def test_sources_exist(self):
        for path in pack_files():
            pack = json.loads(path.read_text(encoding="utf-8"))
            for source in pack["sources"]:
                with self.subTest(pack=path.stem, source=source):
                    self.assertTrue((ROOT / source).is_file(), source)

    def test_cites_exist_and_anchors_match_headings(self):
        for path in pack_files():
            pack = json.loads(path.read_text(encoding="utf-8"))
            for where, entry in entries(pack):
                with self.subTest(pack=path.stem, entry=where):
                    page, _, anchor = entry["cite"].partition("#")
                    page_path = ROOT / page
                    self.assertTrue(page_path.is_file(), entry["cite"])
                    self.assertTrue(page.startswith("docs/compendium/"), entry["cite"])
                    if anchor:
                        self.assertIn(anchor, anchors_of(page_path.read_text(encoding="utf-8")), entry["cite"])

    def test_runbooks_exist(self):
        for path in pack_files():
            pack = json.loads(path.read_text(encoding="utf-8"))
            for index, entry in enumerate(pack["connector_defaults"]):
                if entry["runbook"] is not None:
                    with self.subTest(pack=path.stem, entry=index):
                        self.assertTrue((ROOT / entry["runbook"]).is_file(), entry["runbook"])

    def test_settings_baseline_exists(self):
        for path in pack_files():
            pack = json.loads(path.read_text(encoding="utf-8"))
            if pack["settings_baseline"] is not None:
                with self.subTest(pack=path.stem):
                    baseline = ROOT / "starter-kit" / "settings" / (pack["settings_baseline"] + ".managed-settings.json")
                    self.assertTrue(baseline.is_file(), str(baseline))

    def test_compliance_defaults_are_profile_paths_with_the_catalogue_type(self):
        catalogue = tc_fields.load_catalogue()
        for path in pack_files():
            pack = json.loads(path.read_text(encoding="utf-8"))
            for index, entry in enumerate(pack["compliance_defaults"]):
                with self.subTest(pack=path.stem, entry=index):
                    field = tc_fields.entry_for("profile", entry["field"], catalogue)
                    self.assertIsNotNone(field, "%s is not a profile path in data/fields.json" % entry["field"])
                    self.assertTrue(_type_ok(field, entry["value"]),
                                    "%r is not a %s" % (entry["value"], field["type"]))

    def test_unverified_entries_cite_a_page_with_the_marker(self):
        for path in pack_files():
            pack = json.loads(path.read_text(encoding="utf-8"))
            for where, entry in entries(pack):
                if entry["unverified"] is True:
                    with self.subTest(pack=path.stem, entry=where):
                        page = (ROOT / entry["cite"].partition("#")[0]).read_text(encoding="utf-8")
                        self.assertRegex(page, UNVERIFIED_MARKER)

    def test_general_pack_has_starting_points_and_page_11_connectors(self):
        pack = packs.load_pack("general")
        self.assertTrue(pack["anthropic_starting_points"])
        for name in ("data_providers", "compliance_defaults", "typical_tasks"):
            self.assertEqual(pack[name], [], name)
        self.assertTrue(all(e["cite"].startswith("docs/compendium/16-") for e in pack["anthropic_starting_points"]))
        self.assertIn("docs/compendium/11-connectors.md", pack["sources"])
        products = [e["product"] for e in pack["connector_defaults"]]
        self.assertEqual(products, ["Salesforce", "HubSpot", "Microsoft Dynamics / Dataverse", "Google Drive / Sheets",
                                    "SharePoint / OneDrive", "Teams", "Slack", "Gmail", "Google Calendar", "Zendesk",
                                    "Intercom"])
        runbooks = dict((e["product"], e["runbook"]) for e in pack["connector_defaults"])
        self.assertEqual(runbooks.pop("Salesforce"), "starter-kit/runbooks/salesforce-hosted-mcp.md")
        self.assertEqual(runbooks.pop("SharePoint / OneDrive"), "starter-kit/runbooks/microsoft-365-connector.md")
        self.assertEqual(runbooks.pop("Teams"), "starter-kit/runbooks/microsoft-365-connector.md")
        for product, runbook in sorted(KIT_RUNBOOKS.items()):
            if product in runbooks:
                self.assertEqual(runbooks.pop(product), runbook, product)
        # Only the products the kit has no runbook for are left.
        self.assertEqual(runbooks, {"Microsoft Dynamics / Dataverse": None, "Intercom": None})
        for entry in pack["connector_defaults"]:
            self.assertEqual(entry["cite"], "docs/compendium/11-connectors.md#what-exists-for-our-systems")
        dynamics = next(e for e in pack["connector_defaults"] if "Dynamics" in e["product"])
        self.assertIn("Entra", dynamics["identity"])
        self.assertIn("tenant admin consent", dynamics["identity"])
        self.assertIn("Copilot Credits", dynamics["how"])

    def test_a_product_in_an_industry_pack_and_the_general_pack_has_one_runbook(self):
        general = packs.load_pack("general")["connector_defaults"]
        checked = 0
        for pack_id in packs.list_packs():
            if pack_id == "general":
                continue
            for entry in packs.load_pack(pack_id)["connector_defaults"]:
                match = level.match_default({"kind": entry["system_kind"], "product": entry["product"]}, general)
                if match is None:
                    continue
                checked += 1
                with self.subTest(pack=pack_id, product=entry["product"]):
                    self.assertEqual(entry["runbook"], match["runbook"])
                    if entry["product"] in KIT_RUNBOOKS:
                        self.assertEqual(entry["runbook"], KIT_RUNBOOKS[entry["product"]])
        self.assertGreater(checked, 0)

    def test_private_equity_pack_content(self):
        pack = packs.load_pack("private-equity")
        self.assertEqual(pack["settings_baseline"], "pe-zdr")
        names = {(e["kind"], e["name"]) for e in pack["anthropic_starting_points"]}
        self.assertIn(("plugin", "financial-analysis"), names)
        self.assertIn(("plugin", "private-equity"), names)
        self.assertTrue([e for e in pack["anthropic_starting_points"] if e["kind"] == "skill"])
        self.assertTrue([e for e in pack["anthropic_starting_points"] if e["kind"] == "agent-template"])
        self.assertTrue(pack["data_providers"])
        products = {e["product"] for e in pack["connector_defaults"]}
        self.assertIn("Salesforce", products)
        self.assertTrue([p for p in products if p.startswith("Microsoft 365")])
        runbooks = {e["runbook"] for e in pack["connector_defaults"]}
        self.assertIn("starter-kit/runbooks/salesforce-hosted-mcp.md", runbooks)
        self.assertIn("starter-kit/runbooks/microsoft-365-connector.md", runbooks)
        fields = {e["field"] for e in pack["compliance_defaults"]}
        self.assertTrue({"compliance.mnpi", "compliance.walls", "compliance.retention"} <= fields)
        self.assertGreaterEqual(len(pack["typical_tasks"]), 4)
        self.assertTrue([e for _, e in entries(pack) if e["unverified"] is True])

    def test_private_equity_task_features(self):
        pack = packs.load_pack("private-equity")
        features = {e["id"]: e["feature"] for e in pack["typical_tasks"]}
        self.assertEqual(features, {
            "T1": "pre-meeting-preparation",
            "T2": "pipeline-upkeep-and-reporting",
            "T4": "deal-screening",
            "T5": "pre-meeting-preparation",
            "T6": "investment-committee-drafting",
        })

    def test_b2b_software_pack_content(self):
        pack = packs.load_pack("b2b-software")
        self.assertEqual(pack["name"], "B2B software")
        self.assertIsNone(pack["settings_baseline"])
        for page in ("11-connectors", "16-oob-skills-and-references", "18-customer-success"):
            self.assertIn("docs/compendium/%s.md" % page, pack["sources"])
        names = {(e["kind"], e["name"]) for e in pack["anthropic_starting_points"]}
        self.assertIn(("plugin", "customer-support"), names)
        tasks = {e["id"]: e for e in pack["typical_tasks"]}
        expected = {
            "C1": ("Account brief", "call-preparation-and-follow-up", "person", ["crm", "documents"]),
            "C2": ("Weekly renewal-risk digest", "renewals", "schedule-team", ["crm", "product-data"]),
            "C3": ("Renewal quote email", "renewals", "person", ["crm"]),
            "C4": ("Follow-up email and CRM call note", "call-preparation-and-follow-up", "person", ["documents"]),
            "C5": ("Open-ticket summary on escalation", "escalations", "event", ["ticketing"]),
        }
        self.assertEqual(sorted(tasks), sorted(expected))
        for task_id, (name, feature, trigger, inputs) in expected.items():
            with self.subTest(task=task_id):
                task = tasks[task_id]
                self.assertEqual((task["name"], task["feature"], task["trigger"], task["inputs"]),
                                 (name, feature, trigger, inputs))
                self.assertEqual(task["data_class"], "confidential")
                self.assertEqual(task["cite"], "docs/compendium/18-customer-success.md#typical-customer-success-tasks-our-recommendation")
        kinds = {e["system_kind"] for e in pack["connector_defaults"]}
        self.assertTrue({"crm", "documents", "email-calendar", "messaging", "ticketing", "product-data"} <= kinds)
        products = {e["product"] for e in pack["connector_defaults"]}
        for product in ("HubSpot", "Google Drive", "Gmail", "Google Calendar", "Slack", "Zendesk"):
            self.assertIn(product, products)
        runbooks = dict((e["product"], e["runbook"]) for e in pack["connector_defaults"])
        for product in ("HubSpot", "Google Drive", "Gmail", "Google Calendar", "Slack", "Zendesk"):
            self.assertEqual(runbooks.pop(product), KIT_RUNBOOKS[product], product)
        self.assertTrue(all(value is None for value in runbooks.values()), runbooks)


class LoaderTests(unittest.TestCase):
    def test_unknown_id_names_the_known_ids(self):
        with self.assertRaises(packs.PackError) as caught:
            packs.load_pack("shipbuilding")
        message = str(caught.exception)
        self.assertIn("shipbuilding", message)
        for known in packs.list_packs():
            self.assertIn(known, message)

    def test_path_like_ids_are_unknown(self):
        for bad in ("../fields", "general/../general", "", "General"):
            with self.subTest(bad=bad):
                with self.assertRaises(packs.PackError):
                    packs.load_pack(bad)

    def test_packs_are_found_relative_to_the_script(self):
        self.assertEqual(packs.PACKS_DIR.resolve(), PACKS_DIR.resolve())


def good_pack():
    return {
        "pack_version": 1,
        "id": "sample",
        "name": "Sample",
        "summary": "A pack used only by the tests.",
        "sources": ["docs/compendium/14-private-equity.md"],
        "settings_baseline": "pe-zdr",
        "anthropic_starting_points": [
            {"kind": "plugin", "name": "private-equity", "where": "claude-for-financial-services",
             "use": "start-from", "note": "n", "cite": "docs/compendium/14-private-equity.md", "unverified": False},
        ],
        "data_providers": [
            {"name": "Vendor", "kind": "market-data", "access": "mcp", "note": "n",
             "cite": "docs/compendium/14-private-equity.md", "unverified": True},
        ],
        "connector_defaults": [
            {"system_kind": "crm", "product": "Salesforce", "how": "h", "identity": "per-user OAuth",
             "runbook": "starter-kit/runbooks/salesforce-hosted-mcp.md",
             "cite": "docs/compendium/14-private-equity.md#three-designs", "unverified": False},
        ],
        "compliance_defaults": [
            {"field": "compliance.retention", "value": "custom-30-day", "reason": "r",
             "cite": "docs/compendium/14-private-equity.md", "unverified": False},
        ],
        "typical_tasks": [
            {"id": "T1", "name": "Company brief", "feature": "pre-meeting-prep", "trigger": "person",
             "data_class": "highly-sensitive", "inputs": ["crm", "documents"],
             "cite": "docs/compendium/14-private-equity.md", "unverified": False},
        ],
    }


class PackProblemTests(unittest.TestCase):
    def test_good_pack_has_no_problems(self):
        self.assertEqual(packs.pack_problems(good_pack()), [])

    def assertProblem(self, pack, path):
        problems = packs.pack_problems(pack)
        self.assertIn(path, [p["path"] for p in problems], problems)
        for problem in problems:
            self.assertEqual(set(problem), {"path", "message", "fix"})
            self.assertTrue(problem["message"])
            self.assertTrue(problem["fix"])

    def mutated(self, mutate):
        pack = copy.deepcopy(good_pack())
        mutate(pack)
        return pack

    def test_malformed_packs_give_the_expected_path(self):
        cases = [
            ("pack_version", lambda p: p.update(pack_version=2)),
            ("id", lambda p: p.update(id="Private Equity")),
            ("summary", lambda p: p.pop("summary")),
            ("sources", lambda p: p.update(sources="docs/compendium/14-private-equity.md")),
            ("settings_baseline", lambda p: p.update(settings_baseline=7)),
            ("data_providers[0].access", lambda p: p["data_providers"][0].update(access="carrier-pigeon")),
            ("anthropic_starting_points[0].kind", lambda p: p["anthropic_starting_points"][0].update(kind="gadget")),
            ("anthropic_starting_points[0].use", lambda p: p["anthropic_starting_points"][0].update(use="adopt")),
            ("typical_tasks[0].trigger", lambda p: p["typical_tasks"][0].update(trigger="sometimes")),
            ("typical_tasks[0].data_class", lambda p: p["typical_tasks"][0].update(data_class="secret")),
            ("typical_tasks[0].inputs[1]", lambda p: p["typical_tasks"][0].update(inputs=["crm", "spreadsheet"])),
            ("connector_defaults[0].system_kind", lambda p: p["connector_defaults"][0].update(system_kind="erp")),
            ("connector_defaults[0].runbook", lambda p: p["connector_defaults"][0].update(runbook="docs/x.md")),
            ("compliance_defaults[0].field", lambda p: p["compliance_defaults"][0].update(field="compliance.nope")),
            ("compliance_defaults[0].value", lambda p: p["compliance_defaults"][0].update(value="forever")),
            ("data_providers[0].cite", lambda p: p["data_providers"][0].update(cite="README.md")),
            ("data_providers[0].cite", lambda p: p["data_providers"][0].update(
                cite="docs/compendium/10-sensitive-data.md")),  # a page the pack does not list in sources
            ("data_providers[0].unverified", lambda p: p["data_providers"][0].update(unverified="yes")),
            ("typical_tasks[0].cite", lambda p: p["typical_tasks"][0].pop("cite")),
            ("typical_tasks[0].colour", lambda p: p["typical_tasks"][0].update(colour="red")),
            ("typical_tasks[1].id", lambda p: p["typical_tasks"].append(dict(p["typical_tasks"][0]))),
            ("typical_tasks", lambda p: p.update(typical_tasks={})),
            ("data_providers", lambda p: p.pop("data_providers")),
            ("flavour", lambda p: p.update(flavour="mint")),
        ]
        for path, mutate in cases:
            with self.subTest(path=path):
                self.assertProblem(self.mutated(mutate), path)

    def test_a_pack_that_is_not_an_object(self):
        self.assertProblem([], "pack")

    def test_enumerations_come_from_the_catalogue(self):
        catalogue = copy.deepcopy(tc_fields.load_catalogue())
        for entry in catalogue["fields"]:
            if entry["path"] == "tasks[].trigger":
                entry["values"] = ["person"]
        pack = good_pack()
        pack["typical_tasks"][0]["trigger"] = "event"
        problems = packs.pack_problems(pack, catalogue=catalogue)
        self.assertIn("typical_tasks[0].trigger", [p["path"] for p in problems])
        self.assertEqual(packs.pack_problems(pack), [])


if __name__ == "__main__":
    unittest.main()
