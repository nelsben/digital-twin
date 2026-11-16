"""Walk tests: the rules a fictional insurance broker's claims handler card needs (OPS-49).

The fixture in tests/fixtures/twincard/sample-insurance-broker/ is invented. These tests level it and
build its backlog in a temporary copy, and check the action-log blocker on non-Claude Code surfaces, the
private-network fact for writes, Claude Code missing from the role, mixed devices, memory for highly
sensitive work, the general-pack connector fallback, the no-entry connector wording, and the skill and
start-wiring tasks on every runtime.

Standard library only. Anything the tests write goes to a temporary folder.
Run with: python3 -m unittest discover -s tests
"""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN_DIR = ROOT / "partner-kit" / "plugins" / "twin-consultant"
SCRIPTS_DIR = PLUGIN_DIR / "scripts"
RULES = PLUGIN_DIR / "data" / "rules.json"
GENERAL_PACK = PLUGIN_DIR / "data" / "industry-packs" / "general.json"
BROKER = ROOT / "tests" / "fixtures" / "twincard" / "sample-insurance-broker"
PERSONA = Path("personas") / "claims-handler"
GENERAL_CITE = "docs/compendium/11-connectors.md#what-exists-for-our-systems"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from twincard import level as L  # noqa: E402
from twincard import packs as P  # noqa: E402
from twincard import backlog as B  # noqa: E402


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def mentions(node, text):
    """True when any key or string value inside a JSON node equals or contains text."""
    if isinstance(node, dict):
        return any(text in key or mentions(value, text) for key, value in node.items())
    if isinstance(node, list):
        return any(mentions(item, text) for item in node)
    return isinstance(node, str) and text in node


class BrokerWalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(tmp.cleanup)
        root = Path(tmp.name) / BROKER.name
        shutil.copytree(BROKER, root)
        persona = root / PERSONA
        result = L.write_levelled(str(persona))
        if not result["ok"]:
            raise AssertionError("the broker fixture does not validate: %s" % result["validation"]["errors"])
        cls.levelled = load(persona / "levelled.json")
        built = B.build(str(persona))
        if not built["ok"]:
            raise AssertionError("the broker backlog does not build: %s" % built.get("error"))
        cls.backlog = built["backlog"]
        cls.profile = load(root / "customer-profile.json")

    def about(self, kind, code):
        return set(item["about"] for item in self.levelled[kind] if item["code"] == code)

    def connector(self, tid, system):
        return next(c for c in self.levelled["tasks"][tid]["connectors"] if c["system"] == system)

    def stories(self):
        return dict((story["id"], story) for feature in self.backlog["epic"]["features"]
                    for story in feature["stories"])

    def test_action_log_blocker_on_surfaces_other_than_claude_code(self):
        self.assertTrue({"T2", "T4"} <= self.about("blockers", "log-every-action-not-met"))
        listed = [(b["code"], b["about"]) for b in self.levelled["blockers"]]
        self.assertEqual(len(listed), len(set(listed)), "a task is listed once per code")

    def test_writes_to_a_private_network_reach_plan_fit(self):
        self.assertNotEqual(self.levelled["tasks"]["T1"]["plan_fit"]["value"], "ok")

    def test_claude_code_not_in_role(self):
        self.assertTrue({"T2", "T3"} <= self.about("warnings", "claude-code-not-in-role"))
        messages = dict((w["about"], w["message"]) for w in self.levelled["warnings"]
                        if w["code"] == "claude-code-not-in-role")
        self.assertIn("claude-code-scheduled-task", messages["T2"])
        self.assertIn("surfaces", messages["T3"])

    def test_highly_sensitive_memory_is_off(self):
        memory = self.levelled["tasks"]["T3"]["memory"]
        self.assertEqual(memory["value"], "off")
        self.assertEqual(memory["rule"], "memory-off-sensitive-class")

    def test_mixed_fleet_unmanaged_surfaces(self):
        self.assertIn("T4", self.about("warnings", "mixed-fleet-unmanaged-surfaces"))
        self.assertNotIn("T3", self.about("warnings", "mixed-fleet-unmanaged-surfaces"))

    def test_general_pack_fallback_and_no_entry(self):
        general = load(GENERAL_PACK)
        hows = set(d["how"] for d in general.get("connector_defaults") or [])
        for tid, system in (("T3", "sharepoint"), ("T1", "dynamics")):
            conn = self.connector(tid, system)
            self.assertEqual(conn["cite"], GENERAL_CITE, system)
            self.assertIn(conn["how"], hows, system)
        systems = L._systems(self.profile, P.load_pack(self.profile["industry"]))
        for system in ("sharepoint", "teams", "dynamics"):
            default = systems[system]["default"]
            self.assertIsNotNone(default, system)
            self.assertEqual(default["cite"], GENERAL_CITE, system)
            self.assertIn(default["how"], hows, system)
        self.assertIsNone(systems["outlook"]["default"])
        products = [d["product"] for d in general.get("connector_defaults") or []]
        self.assertTrue(any("SharePoint" in p for p in products))
        self.assertTrue(any("Teams" in p for p in products))
        self.assertTrue(any("Dynamics" in p for p in products))
        outlook = self.connector("T1", "outlook")["how"] or ""
        self.assertIn("compendium has no entry", outlook)
        self.assertIn("Claude connector directory", outlook)
        self.assertIn("custom connector", outlook)
        self.assertNotIn("not in the directory", outlook)
        self.assertNotIn("isn't in the directory", outlook)

    def test_every_task_story_has_write_skill_and_t1_has_start_wiring(self):
        stories = self.stories()
        for tid in self.levelled["tasks"]:
            templates = [t["template"] for t in stories["S-" + tid]["tasks"]]
            self.assertIn("write-skill", templates, tid)
        self.assertIn("start-wiring", [t["template"] for t in stories["S-T1"]["tasks"]])

    def test_old_private_network_fact_is_gone(self):
        for rule in load(RULES)["rules"]:
            self.assertFalse(mentions(rule["when"], "task.reads_private_network"), rule["id"])


if __name__ == "__main__":
    unittest.main()
