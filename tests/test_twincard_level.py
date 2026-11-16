"""Tests for the levelling engine: scripts/twincard/level.py, data/rules.json and data/plan-fit.json.

The expected results for the two fictional fixtures are checked in test_twincard_acceptance.py; this
file checks the engine itself: loading, conditions, combining, open fields, overrides, shared tools,
the command line, byte-identical output, cites, and that every rule fires somewhere.

Standard library only. Run with: python3 -m unittest discover -s tests
"""

import copy
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN_DIR = ROOT / "partner-kit" / "plugins" / "twin-consultant"
SCRIPTS_DIR = PLUGIN_DIR / "scripts"
CLI = SCRIPTS_DIR / "twincard" / "cli.py"
RULES = PLUGIN_DIR / "data" / "rules.json"
PLAN_FIT = PLUGIN_DIR / "data" / "plan-fit.json"
DESIGN = ROOT / "partner-kit" / "docs" / "design.md"
PE = ROOT / "engagements" / "sample-pe" / "personas" / "deal-team-associate"
TEAM = ROOT / "engagements" / "sample-team-cs" / "personas" / "customer-success-manager"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from twincard import level as L  # noqa: E402

# Plan-fit entries that are Unverified because no compendium section states their per-plan value (design 7.3).
NO_PER_PLAN_VALUE = {"managed-settings-and-hooks", "governance-action-log", "managed-agents-hosted",
                     "managed-agents-self-hosted", "agent-sdk"}
UNVERIFIED_MARKER = re.compile(r"unverified|not confirmed", re.IGNORECASE)
TOP_KEYS = ["levelled_version", "customer", "persona", "source", "persona_plan", "tasks", "tools",
            "blockers", "warnings", "complete"]
DECISION_KEYS = ["value", "rule", "cite", "reason", "unverified", "basis", "overridden"]
ITEM_KEYS = ["code", "about", "cite", "unverified", "message", "fix"]
CONNECTOR_KEYS = ["system", "access", "identity", "how", "runbook", "permission", "cite", "unverified"]


def slug(heading):
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading)
    text = text.replace("`", "").replace("*", "").strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def sections_of(page_text):
    """Map each heading anchor to the text of its section (up to the next heading at its level or above)."""
    lines, heads, seen, in_fence = page_text.splitlines(), [], {}, False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if m:
            base = slug(m.group(2))
            n = seen.get(base, 0)
            seen[base] = n + 1
            heads.append((i, len(m.group(1)), base if n == 0 else "%s-%d" % (base, n)))
    out = {}
    for k, (i, depth, anchor) in enumerate(heads):
        end = len(lines)
        for j, d, _ in heads[k + 1:]:
            if d <= depth:
                end = j
                break
        out[anchor] = "\n".join(lines[i:end])
    return out


def section(cite):
    path, _, anchor = cite.partition("#")
    target = ROOT / path
    if not target.is_file():
        return None
    return sections_of(target.read_text(encoding="utf-8")).get(anchor)


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


class Scenario(object):
    """A temporary copy of a fixture's engagement, changed by a function of (profile, card)."""

    def __init__(self, persona_dir, change=None):
        self.persona_dir, self.change = Path(persona_dir), change

    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        engagement = self.persona_dir.parent.parent
        root = Path(self.tmp.name) / engagement.name
        shutil.copytree(engagement, root)
        persona = root / self.persona_dir.relative_to(engagement)
        profile, card = load(root / "customer-profile.json"), load(persona / "card.json")
        if self.change:
            self.change(profile, card)
        (root / "customer-profile.json").write_text(json.dumps(profile, indent=2), encoding="utf-8")
        (persona / "card.json").write_text(json.dumps(card, indent=2), encoding="utf-8")
        return persona

    def __exit__(self, *exc):
        self.tmp.cleanup()


def task(card, tid):
    return next(t for t in card["tasks"] if t["id"] == tid)


def run_level(persona_dir, change=None, fired=None):
    with Scenario(persona_dir, change) as persona:
        result = L.level(str(persona), fired=fired)
    if not result["ok"]:
        raise AssertionError("scenario does not validate: %s" % result["validation"]["errors"])
    return result["levelled"]


def codes(levelled, kind):
    return {(item["code"], item["about"]) for item in levelled[kind]}


def override(card, tid, decision, value):
    card["overrides"] = [{"task": tid, "decision": decision, "value": value,
                          "reason": "Invented reason for a test.", "approved_by": "Test approver"}]


# --- Scenarios that, with the two fixtures, make every rule fire ---------------------------------

def set_task(tid, **values):
    def change(profile, card):
        task(card, tid).update(values)
    return change


def all_tasks(data_class):
    def change(profile, card):
        for t in card["tasks"]:
            t["data_class"] = data_class
    return change


def pe_phi(profile, card):
    profile["compliance"]["phi"] = True
    task(card, "T3")["data_class"] = "phi"


def pe_t1_phi(profile, card):
    profile["compliance"]["phi"] = True
    task(card, "T1")["data_class"] = "phi"


def pe_private_salesforce(profile, card):
    profile["network"]["can_allowlist_anthropic_ips"] = False
    next(s for s in profile["systems"] if s["id"] == "salesforce")["private_network"] = True


def team_shared_hubspot(profile, card):
    task(card, "C1")["writes"] = [{"system": "hubspot", "objects": "note on the company record", "action": "create"}]
    card["provenance"]["tasks.C1.writes[0].action"] = {"status": "answered",
                                                       "source": "interviews/2026-11-06-csm.md#F7"}


def team_c2_writes_hubspot(profile, card):
    task(card, "C2")["writes"][0].update({"system": "hubspot", "action": "create"})


def team_c4_action(action):
    def change(profile, card):
        task(card, "C4")["writes"][0]["action"] = action
    return change


def team_c4_gmail_send(profile, card):
    task(card, "C4")["writes"].append({"system": "gmail", "objects": "follow-up email", "action": "send"})
    card["provenance"]["tasks.C4.writes[1].action"] = {"status": "answered",
                                                       "source": "interviews/2026-11-06-csm.md#F7"}


def profile_set(section_name, key, value):
    def change(profile, card):
        profile[section_name][key] = value
    return change


def pe_override_agent_sdk(profile, card):
    override(card, "T3", "runtime", "agent-sdk")


def chain(*changes):
    def change(profile, card):
        for c in changes:
            c(profile, card)
    return change


def team_c1_reads_usage_db(profile, card):
    inputs = task(card, "C1")["inputs"]
    inputs.append({"system": "usage-db", "objects": "usage aggregates", "access": "read"})
    card["provenance"]["tasks.C1.inputs[%d].access" % (len(inputs) - 1)] = {
        "status": "answered", "source": "interviews/2026-11-06-csm.md#F7"}


def role_device(value):
    def change(profile, card):
        card["role"]["device"] = value
    return change


SCENARIOS = [
    ("pe", PE, None),
    ("team", TEAM, None),
    ("team C1 schedule-own", TEAM, set_task("C1", trigger="schedule-own")),
    ("team self-hosting required", TEAM, profile_set("runtime_preferences", "self_hosting_required", True)),
    ("team C2 writes HubSpot", TEAM, team_c2_writes_hubspot),
    ("team C4 deletes", TEAM, team_c4_action("delete")),
    ("team C4 irreversible", TEAM, set_task("C4", reversible=False)),
    ("team C1 internal", TEAM, set_task("C1", data_class="internal")),
    ("team C1 PHI", TEAM, set_task("C1", data_class="phi")),
    ("team C1 highly sensitive", TEAM, set_task("C1", data_class="highly-sensitive")),
    ("team individual plan", TEAM, profile_set("plan", "tier", "individual")),
    ("team action log required", TEAM, profile_set("governance", "action_log_required", True)),
    ("team no IP allowlist", TEAM, profile_set("network", "can_allowlist_anthropic_ips", False)),
    ("team C4 Gmail send", TEAM, team_c4_gmail_send),
    ("team shared HubSpot write", TEAM, team_shared_hubspot),
    ("pe PHI hosted task", PE, pe_phi),
    ("pe T1 PHI", PE, pe_t1_phi),
    ("pe T1 confidential", PE, set_task("T1", data_class="confidential")),
    ("pe T5 internal", PE, set_task("T5", data_class="internal")),
    ("pe private Salesforce", PE, pe_private_salesforce),
    ("pe all confidential", PE, all_tasks("confidential")),
    ("pe all internal", PE, all_tasks("internal")),
    ("pe T3 override agent-sdk", PE, pe_override_agent_sdk),
    ("pe private Salesforce, all confidential", PE, chain(pe_private_salesforce, all_tasks("confidential"))),
    ("team no IP allowlist, C1 reads usage-db", TEAM,
     chain(profile_set("network", "can_allowlist_anthropic_ips", False), team_c1_reads_usage_db)),
    ("pe T1 schedule-own", PE, set_task("T1", trigger="schedule-own")),
    ("pe T1 PHI schedule-own", PE, chain(pe_t1_phi, set_task("T1", trigger="schedule-own"))),
    ("pe mixed devices", PE, role_device("mixed")),
]


# --- Loading --------------------------------------------------------------------------------------

class LoadTests(unittest.TestCase):
    def setUp(self):
        self.rules = load(RULES)
        self.plan_fit = L.load_plan_fit()

    def load_changed(self, change, codes=None):
        data = copy.deepcopy(self.rules)
        change(data)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rules.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            return L.load_rules(path, plan_fit=self.plan_fit, codes=codes)

    def assertLoadError(self, change, *needles, **kwargs):
        with self.assertRaises(L.LevelError) as ctx:
            self.load_changed(change, **kwargs)
        for needle in needles:
            self.assertIn(needle, str(ctx.exception))

    def test_shipped_rules_and_plan_fit_load(self):
        data = L.load_rules(plan_fit=self.plan_fit, codes=L.design_codes(DESIGN))
        self.assertEqual(data["rules_version"], 1)
        self.assertEqual(self.plan_fit["plan_fit_version"], 1)
        self.assertEqual(sorted(load(PLAN_FIT)), ["capabilities", "plan_fit_version"])

    def test_unknown_fact_names_the_rule(self):
        def change(data):
            data["rules"][0]["when"] = {"task.no_such_fact": True}
        self.assertLoadError(change, self.rules["rules"][0]["id"], "task.no_such_fact")

    def test_unknown_fact_inside_any_names_the_rule(self):
        def change(data):
            data["rules"][3]["when"] = {"any": [{"task.trigger": "person"}, {"nope": 1}]}
        self.assertLoadError(change, self.rules["rules"][3]["id"], "nope")

    def test_unknown_decision_names_the_rule(self):
        def change(data):
            data["rules"][1]["decides"] = "colour"
        self.assertLoadError(change, self.rules["rules"][1]["id"], "colour")

    def test_unknown_decision_in_the_table(self):
        def change(data):
            data["decisions"]["colour"] = {"combine": "first"}
        self.assertLoadError(change, "colour")

    def test_bad_combine(self):
        def change(data):
            data["decisions"]["runtime"] = {"combine": "average"}
        self.assertLoadError(change, "runtime", "combine")

    def test_duplicate_id(self):
        def change(data):
            data["rules"][2]["id"] = data["rules"][1]["id"]
        self.assertLoadError(change, self.rules["rules"][1]["id"], "twice")

    def test_code_not_in_design(self):
        def change(data):
            rule = next(r for r in data["rules"] if r["decides"] == "warning")
            rule["then"] = "no-such-code"
        self.assertLoadError(change, "no-such-code", "7.2", codes=L.design_codes(DESIGN))

    def test_a_later_decision_cannot_be_read_by_an_earlier_one(self):
        def change(data):
            rule = next(r for r in data["rules"] if r["decides"] == "runtime")
            rule["when"] = {"memory": "on"}
        self.assertLoadError(change, "memory")

    def test_cite_needs_an_anchor_and_basis_a_known_value(self):
        def no_anchor(data):
            data["rules"][0]["cite"] = "docs/compendium/05-decision-matrix.md"
        self.assertLoadError(no_anchor, self.rules["rules"][0]["id"], "anchor")

        def bad_basis(data):
            data["rules"][0]["basis"] = "judgment"
        self.assertLoadError(bad_basis, self.rules["rules"][0]["id"], "basis")

    def test_rule_shape_and_ids(self):
        ids = [rule["id"] for rule in self.rules["rules"]]
        self.assertEqual(len(ids), len(set(ids)))
        for rule in self.rules["rules"]:
            self.assertRegex(rule["id"], r"^[a-z0-9]+(-[a-z0-9]+)*$")
            self.assertIn(rule["basis"], ("compendium", "our-recommendation"), rule["id"])
            self.assertIsInstance(rule["unverified"], bool, rule["id"])
            self.assertIn(rule["decides"], set(self.rules["decisions"]) | {"blocker", "warning"}, rule["id"])
        for name, spec in self.rules["decisions"].items():
            self.assertIn(spec["combine"], ("first", "strictest"), name)

    def test_every_code_is_listed_in_design(self):
        listed = L.design_codes(DESIGN)
        for rule in self.rules["rules"]:
            if rule["decides"] in ("blocker", "warning"):
                self.assertIn(rule["then"], listed, rule["id"])
        for code in L.ENGINE_CODES:
            self.assertIn(code, listed)

    def test_plan_fit_shape(self):
        ids = [cap["id"] for cap in self.plan_fit["capabilities"]]
        self.assertEqual(len(ids), len(set(ids)))
        for cap in self.plan_fit["capabilities"]:
            self.assertEqual(list(cap), list(L.CAPABILITY_KEYS), cap["id"])
            for tier in ("team", "enterprise", "individual"):
                self.assertIn(cap[tier], ("yes", "no", "limited"), cap["id"])

    def test_bad_plan_fit_value(self):
        data = copy.deepcopy(load(PLAN_FIT))
        data["capabilities"][0]["team"] = "maybe"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "plan-fit.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(L.LevelError) as ctx:
                L.load_plan_fit(path)
        self.assertIn(data["capabilities"][0]["id"], str(ctx.exception))


# --- Conditions -----------------------------------------------------------------------------------

class MatchesTests(unittest.TestCase):
    def test_unknown_fact_raises_whatever_comes_first(self):
        with self.assertRaises(L.LevelError):
            L.matches({"a": 1, "zzz": 2}, {"a": 2})
        with self.assertRaises(L.LevelError):
            L.matches({"any": [{"a": 2}, {"not": {"zzz": 1}}]}, {"a": 2})
        with self.assertRaises(L.LevelError):
            L.matches({"zzz": 1}, {})

    def test_values_lists_and_list_facts(self):
        facts = {"a": "x", "b": ["p", "q"], "c": None, "d": 3}
        self.assertTrue(L.matches({}, facts))
        self.assertTrue(L.matches({"a": "x"}, facts))
        self.assertTrue(L.matches({"a": ["y", "x"]}, facts))
        self.assertFalse(L.matches({"a": "y"}, facts))
        self.assertTrue(L.matches({"b": "q"}, facts))
        self.assertTrue(L.matches({"b": ["z", "p"]}, facts))
        self.assertFalse(L.matches({"b": "z"}, facts))
        self.assertTrue(L.matches({"c": None}, facts))
        self.assertTrue(L.matches({"d": [2, 3]}, facts))

    def test_booleans_are_not_numbers(self):
        self.assertFalse(L.matches({"a": True}, {"a": 1}))
        self.assertFalse(L.matches({"a": 1}, {"a": True}))
        self.assertTrue(L.matches({"a": False}, {"a": False}))
        self.assertFalse(L.matches({"a": 0}, {"a": False}))

    def test_any_all_not(self):
        facts = {"a": 1, "b": 2}
        self.assertTrue(L.matches({"any": [{"a": 5}, {"b": 2}]}, facts))
        self.assertFalse(L.matches({"any": [{"a": 5}, {"b": 5}]}, facts))
        self.assertTrue(L.matches({"all": [{"a": 1}, {"b": 2}]}, facts))
        self.assertFalse(L.matches({"all": [{"a": 1}, {"b": 5}]}, facts))
        self.assertTrue(L.matches({"not": {"a": 5}}, facts))
        self.assertFalse(L.matches({"not": {"a": 1, "b": 2}}, facts))
        self.assertTrue(L.matches({"not": {"a": 1, "b": 5}}, facts))

    def test_open_fact_raises_only_when_reached(self):
        facts = {"a": 1, "o": L.Open("card", "role.device")}
        with self.assertRaises(L.FactOpen):
            L.matches({"o": "managed"}, facts)
        self.assertFalse(L.matches({"a": 2, "o": "managed"}, facts))
        self.assertTrue(L.matches({"any": [{"o": "x"}, {"a": 1}]}, facts))
        with self.assertRaises(L.FactOpen):
            L.matches({"any": [{"o": "x"}, {"a": 2}]}, facts)

    def test_a_bad_condition_is_an_error(self):
        with self.assertRaises(L.LevelError):
            L.matches({"any": []}, {})
        with self.assertRaises(L.LevelError):
            L.matches(["a"], {})


# --- Combining ------------------------------------------------------------------------------------

class CombineTests(unittest.TestCase):
    def run_for(self, decisions, rules):
        data = {"rules_version": 1, "decisions": decisions, "rules": rules}
        run = L._Run(data, L.load_plan_fit(), set())
        return run

    def rule(self, rid, decides, when, then):
        return {"id": rid, "decides": decides, "when": when, "then": then,
                "cite": "docs/compendium/06-autonomy.md#rules-for-moving-up-a-level", "unverified": False,
                "basis": "compendium", "reason": "Because %s." % rid}

    def test_first_takes_the_first_rule_that_holds(self):
        run = self.run_for({"memory": {"combine": "first"}}, [
            self.rule("r-no", "memory", {"a": 2}, "on"),
            self.rule("r-one", "memory", {"a": 1}, "off"),
            self.rule("r-two", "memory", {}, "on")])
        decision, undecided = run.decide("memory", {"a": 1}, "T1")
        self.assertEqual((decision["value"], decision["rule"], undecided), ("off", "r-one", False))
        self.assertEqual(run.fired, {"r-one"})
        self.assertEqual(list(decision), DECISION_KEYS)

    def test_strictest_takes_the_lowest_level_and_the_first_on_a_tie(self):
        run = self.run_for({"autonomy.ceiling": {"combine": "strictest"}}, [
            self.rule("r-four", "autonomy.ceiling", {}, 4),
            self.rule("r-two-a", "autonomy.ceiling", {}, 2),
            self.rule("r-two-b", "autonomy.ceiling", {}, 2),
            self.rule("r-fact", "autonomy.ceiling", {}, {"fact": "x"})])
        decision, _ = run.decide("autonomy.ceiling", {"x": 3}, "T1")
        self.assertEqual((decision["value"], decision["rule"]), (2, "r-two-a"))
        self.assertEqual(run.fired, {"r-four", "r-two-a", "r-two-b", "r-fact"})
        decision, _ = run.decide("autonomy.ceiling", {"x": 1}, "T1")
        self.assertEqual((decision["value"], decision["rule"]), (1, "r-fact"))
        decision, _ = run.decide("autonomy.ceiling", {"x": None}, "T1")
        self.assertEqual(decision["value"], 2)

    def test_strictest_real_value_beats_undecided(self):
        run = self.run_for({"autonomy.ceiling": {"combine": "strictest"}}, [
            self.rule("r-one", "autonomy.ceiling", {}, 1),
            self.rule("r-undecided", "autonomy.ceiling", {}, "undecided")])
        decision, undecided = run.decide("autonomy.ceiling", {}, "T1")
        self.assertEqual((decision["value"], decision["rule"], undecided), (1, "r-one", False))
        self.assertEqual(run.last_outranked["id"], "r-undecided")

    def test_strictest_undecided_alone_stays_undecided(self):
        run = self.run_for({"autonomy.ceiling": {"combine": "strictest"}}, [
            self.rule("r-undecided", "autonomy.ceiling", {}, "undecided"),
            self.rule("r-fact", "autonomy.ceiling", {}, {"fact": "x"})])
        decision, undecided = run.decide("autonomy.ceiling", {"x": None}, "T1")
        self.assertEqual((decision["value"], decision["rule"], undecided), (None, "r-undecided", True))

    def test_strictest_with_an_order(self):
        order = ["blocked", "needs-approval", "always-allow"]
        run = self.run_for({"connectors.permission": {"combine": "strictest", "order": order}}, [
            self.rule("r-allow", "connectors.permission", {}, "always-allow"),
            self.rule("r-approve", "connectors.permission", {}, "needs-approval")])
        decision, _ = run.decide("connectors.permission", {}, "T1")
        self.assertEqual((decision["value"], decision["rule"]), ("needs-approval", "r-approve"))

    def test_no_rule_is_undecided_not_a_guess(self):
        run = self.run_for({"memory": {"combine": "first"}}, [self.rule("r-no", "memory", {"a": 2}, "on")])
        decision, undecided = run.decide("memory", {"a": 1}, "T1")
        self.assertEqual((decision["value"], decision["rule"], undecided), (None, None, True))

    def test_the_shipped_decisions_use_each_combine_mode(self):
        modes = {spec["combine"] for spec in load(RULES)["decisions"].values()}
        self.assertEqual(modes, {"first", "strictest"})


# --- Open fields ------------------------------------------------------------------------------------

class OpenFieldTests(unittest.TestCase):
    def test_open_field_gives_null_and_a_warning(self):
        def change(profile, card):
            task(card, "C1")["reads_untrusted_input"] = None
            card["provenance"]["tasks.C1.reads_untrusted_input"] = {
                "status": "open", "source": "interviews/2026-11-06-csm.md#F8", "owner": "Marisol Quenby",
                "due": "2026-12-11"}
        out = run_level(TEAM, change)
        memory = out["tasks"]["C1"]["memory"]
        self.assertIsNone(memory["value"])
        self.assertEqual(memory["rule"], "memory-off-untrusted-input")
        opened = [w for w in out["warnings"] if w["code"] == "field-open"]
        self.assertEqual([w["about"] for w in opened], ["C1"])
        self.assertIn("tasks.C1.reads_untrusted_input", opened[0]["message"])
        self.assertTrue(section(opened[0]["cite"]))

    def test_an_open_field_with_a_value_uses_the_value(self):
        out = run_level(PE)
        self.assertFalse([w for w in out["warnings"] if w["code"] == "field-open"])
        self.assertEqual(out["tasks"]["T1"]["data_controls"]["retention"]["value"], "zdr")


# --- Overrides ------------------------------------------------------------------------------------

class OverrideTests(unittest.TestCase):
    def test_ceiling_override_keeps_the_rule_and_shows_the_result(self):
        out = run_level(TEAM, lambda p, c: override(c, "C1", "autonomy.ceiling", 2))
        ceiling = out["tasks"]["C1"]["autonomy"]["ceiling"]
        self.assertEqual(ceiling["value"], 2)
        self.assertEqual(ceiling["rule"], "ceiling-person-started")
        self.assertEqual(ceiling["overridden"], {"rule_result": 3, "reason": "Invented reason for a test.",
                                                 "approved_by": "Test approver"})
        applied = [w for w in out["warnings"] if w["code"] == "override-applied"]
        self.assertEqual([(w["about"], w["cite"]) for w in applied], [("C1", ceiling["cite"])])

    def test_data_controls_override_replaces_only_the_parts_given(self):
        out = run_level(TEAM, lambda p, c: override(c, "C1", "data_controls", {"web_tools": "off"}))
        controls = out["tasks"]["C1"]["data_controls"]
        self.assertEqual(controls["web_tools"]["value"], "off")
        self.assertEqual(controls["web_tools"]["overridden"]["rule_result"], "on")
        self.assertIsNone(controls["surfaces"]["overridden"])
        self.assertEqual(controls["surfaces"]["value"], ["claude-ai"])

    def test_plan_fit_and_connectors_cannot_be_overridden(self):
        for decision, value in (("plan_fit", "ok"), ("connectors", [])):
            with self.subTest(decision=decision):
                out = run_level(TEAM, lambda p, c: override(c, "C1", decision, value))
                self.assertIn(("override-not-allowed", "C1"), codes(out, "blockers"))
                self.assertEqual(out["tasks"]["C1"]["plan_fit"]["value"], "ok-with-limits")
                self.assertIsNone(out["tasks"]["C1"]["plan_fit"]["overridden"])
                self.assertFalse(out["complete"])

    def test_unknown_target_is_a_blocker(self):
        problems = L.override_problems([{"task": "C9", "decision": "runtime", "value": "client-skill"},
                                        {"task": "C1", "decision": "colour", "value": "red"},
                                        {"task": "C1", "decision": "runtime", "value": "client-skill"}],
                                       ["C1", "C2"])
        self.assertEqual([(i, b["code"], b["about"]) for i, b in problems],
                         [(0, "override-unknown-target", "persona"), (1, "override-unknown-target", "C1")])
        for _, blocker in problems:
            self.assertEqual(list(blocker), ITEM_KEYS)

    def test_overriding_a_high_cost_ceiling_removes_the_warning(self):
        out = run_level(PE, lambda p, c: override(c, "T4", "autonomy.ceiling", 2))
        self.assertNotIn(("high-cost-ceiling-unconfirmed", "T4"), codes(out, "warnings"))
        self.assertIn(("high-cost-ceiling-unconfirmed", "T6"), codes(out, "warnings"))
        self.assertEqual(out["tasks"]["T4"]["autonomy"]["ceiling"]["overridden"]["rule_result"], 3)

    def test_agent_sdk_override_rests_on_an_unverified_fact(self):
        out = run_level(PE, pe_override_agent_sdk)
        runtime = out["tasks"]["T3"]["runtime"]
        self.assertEqual(runtime["value"], "agent-sdk")
        self.assertTrue(runtime["unverified"])
        warning = [w for w in out["warnings"] if w["code"] == "agent-sdk-cover-unverified"]
        self.assertEqual([(w["about"], w["unverified"]) for w in warning], [("T3", True)])
        self.assertEqual(out["tasks"]["T3"]["identity"]["value"], "api-key-vault")


# --- Shared tools -----------------------------------------------------------------------------------

class ToolTests(unittest.TestCase):
    def test_tools_list_each_system_and_use(self):
        out = run_level(TEAM)
        tools = {(t["system"], t["use"]): t for t in out["tools"]}
        self.assertEqual(tools[("hubspot", "read")]["tasks"], ["C1", "C2", "C3"])
        self.assertEqual(tools[("slack", "send")]["permission"]["value"], "blocked")
        self.assertEqual(tools[("slack", "send")]["wanted"], {"C2": "needs-approval"})
        self.assertEqual(out["tasks"]["C4"]["connectors"][1]["permission"], "blocked")
        for entry in out["tasks"]["C2"]["connectors"]:
            self.assertEqual(list(entry), CONNECTOR_KEYS)

    def test_shared_tool_runs_at_the_stricter_level(self):
        out = run_level(TEAM, team_shared_hubspot)
        ceiling = out["tasks"]["C1"]["autonomy"]["ceiling"]
        self.assertEqual((ceiling["value"], ceiling["rule"]), (2, "ceiling-shared-tool"))
        self.assertEqual(out["tasks"]["C4"]["autonomy"]["ceiling"]["value"], 2)
        shared = [w for w in out["warnings"] if w["code"] == "shared-tool-strictest"]
        self.assertEqual([w["about"] for w in shared], ["C1"])
        tool = next(t for t in out["tools"] if (t["system"], t["use"]) == ("hubspot", "create"))
        self.assertEqual(tool["tasks"], ["C1", "C4"])
        self.assertEqual(tool["wanted"], {"C1": "needs-approval", "C4": "needs-approval"})
        self.assertEqual(tool["permission"]["value"], "blocked")

    def test_no_shared_warning_when_the_tasks_agree(self):
        out = run_level(TEAM)
        self.assertNotIn("shared-tool-strictest", {w["code"] for w in out["warnings"]})


# --- Persona plan ---------------------------------------------------------------------------------

class PersonaPlanTests(unittest.TestCase):
    def test_plugin_name_follows_the_card_or_the_persona_id(self):
        self.assertEqual(run_level(PE)["persona_plan"]["plugin_name"]["value"], "twin-pe-deal-team")
        self.assertEqual(run_level(TEAM)["persona_plan"]["plugin_name"]["value"], "twin-customer-success-manager")

    def test_bad_plugin_name_is_a_blocker(self):
        def change(profile, card):
            card["role"]["plugin_name"] = "Deal Team"
        out = run_level(PE, change)
        self.assertIn(("plugin-name-invalid", "persona"), codes(out, "blockers"))

    def test_individual_plan_installs_by_hand(self):
        out = run_level(TEAM, profile_set("plan", "tier", "individual"))
        self.assertEqual(out["persona_plan"]["distribution"]["value"], "manual")


# --- Command line ---------------------------------------------------------------------------------

class CliTests(unittest.TestCase):
    def cli(self, *args):
        return subprocess.run([sys.executable, str(CLI)] + list(args), capture_output=True, text=True,
                              cwd=str(Path(tempfile.gettempdir())))

    def test_exit_0_and_writes_levelled_json(self):
        with Scenario(TEAM) as persona:
            (persona / "levelled.json").unlink()
            proc = self.cli("level", str(persona))
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertTrue((persona / "levelled.json").is_file())
            self.assertIn("complete: yes", proc.stdout)

    def test_exit_1_on_validation_errors_and_writes_nothing(self):
        with Scenario(TEAM, set_task("C1", trigger="sometimes")) as persona:
            (persona / "levelled.json").unlink()
            proc = self.cli("level", str(persona))
            self.assertEqual(proc.returncode, 1)
            self.assertFalse((persona / "levelled.json").exists())
            self.assertIn("tasks.C1.trigger", proc.stdout)

    def test_exit_1_on_a_blocker_and_still_writes(self):
        with Scenario(TEAM, profile_set("plan", "tier", "individual")) as persona:
            (persona / "levelled.json").unlink()
            proc = self.cli("level", "--json", str(persona))
            self.assertEqual(proc.returncode, 1)
            data = json.loads(proc.stdout)
            self.assertIn("plan-below-team", [b["code"] for b in data["blockers"]])
            self.assertTrue((persona / "levelled.json").is_file())

    def test_exit_2_on_usage_errors(self):
        self.assertEqual(self.cli().returncode, 2)
        self.assertEqual(self.cli("level").returncode, 2)
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self.cli("level", str(Path(tmp) / "missing")).returncode, 2)
            self.assertEqual(self.cli("level", tmp).returncode, 2)


# --- Output -----------------------------------------------------------------------------------------

class OutputTests(unittest.TestCase):
    def test_byte_identical_and_fixed_layout(self):
        with Scenario(TEAM) as persona:
            L.write_levelled(str(persona))
            first = (persona / "levelled.json").read_bytes()
            L.write_levelled(str(persona))
            second = (persona / "levelled.json").read_bytes()
        self.assertEqual(first, second)
        text = first.decode("utf-8")
        self.assertTrue(text.endswith("}\n"))
        self.assertTrue(text.startswith('{\n  "levelled_version": 1,'))
        data = json.loads(text)
        self.assertEqual(list(data), TOP_KEYS)
        self.assertEqual(list(data["source"]), ["card_sha256", "profile_sha256", "rules_version", "pack"])
        self.assertEqual(list(data["persona_plan"]), ["plugin_name", "distribution", "settings_baseline",
                                                      "starting_points"])
        for tid, entry in data["tasks"].items():
            self.assertEqual(list(entry), ["runtime", "identity", "autonomy", "data_controls", "connectors",
                                           "memory", "plan_fit"], tid)
            self.assertEqual(list(entry["data_controls"]), ["settings_baseline", "web_tools", "surfaces",
                                                            "retention"])
            for decision in [entry["runtime"], entry["autonomy"]["ceiling"], entry["data_controls"]["surfaces"]]:
                self.assertEqual(list(decision), DECISION_KEYS, tid)
        for item in data["warnings"] + data["blockers"]:
            self.assertEqual(list(item), ITEM_KEYS)

    def test_level_never_writes(self):
        with Scenario(TEAM) as persona:
            (persona / "levelled.json").unlink()
            result = L.level(str(persona))
            self.assertTrue(result["ok"])
            self.assertFalse((persona / "levelled.json").exists())

    def test_no_levelling_when_validation_fails(self):
        with Scenario(TEAM, set_task("C1", trigger="sometimes")) as persona:
            result = L.level(str(persona))
        self.assertFalse(result["ok"])
        self.assertIsNone(result["levelled"])
        self.assertTrue(result["validation"]["errors"])


# --- Cites ------------------------------------------------------------------------------------------

class CiteTests(unittest.TestCase):
    def test_rule_cites_resolve_and_unverified_rules_cite_a_marked_section(self):
        for rule in load(RULES)["rules"]:
            text = section(rule["cite"])
            self.assertIsNotNone(text, "%s: %s does not resolve" % (rule["id"], rule["cite"]))
            if rule["unverified"]:
                self.assertRegex(text, UNVERIFIED_MARKER, "%s cites a section with no marker" % rule["id"])

    def test_plan_fit_cites_resolve_and_unverified_entries_cite_a_marked_section(self):
        for cap in load(PLAN_FIT)["capabilities"]:
            text = section(cap["cite"])
            self.assertIsNotNone(text, "%s: %s does not resolve" % (cap["id"], cap["cite"]))
            if cap["unverified"] and cap["id"] not in NO_PER_PLAN_VALUE:
                self.assertRegex(text, UNVERIFIED_MARKER, cap["id"])

    def test_engine_cites_resolve(self):
        for cite in (L.DESIGN_CITE, L.DESIGN_VALUES_CITE, L.DESIGN_PROVENANCE_CITE, L.UNREACHED_CONNECTOR_CITE,
                     "starter-kit/templates/role-plugin/README.md#steps"):
            self.assertIsNotNone(section(cite), cite)

    def test_worked_example_cites_into_engagements_name_files_that_exist(self):
        def cites(node):
            if isinstance(node, dict):
                for key, value in node.items():
                    if key == "cite" and isinstance(value, str):
                        yield value
                    else:
                        yield from cites(value)
            elif isinstance(node, list):
                for value in node:
                    yield from cites(value)

        for persona in (PE, TEAM):
            for cite in cites(load(persona / "levelled.json")):
                if cite.startswith("engagements/"):
                    path = cite.partition("#")[0]
                    self.assertTrue((ROOT / path).is_file(), "%s: %s names no file" % (persona.name, cite))

    def test_the_05_decision_flow_is_cited_both_ways(self):
        flow = "docs/compendium/05-decision-matrix.md#decision-flow-our-recommendation"
        flags = {rule["unverified"] for rule in load(RULES)["rules"] if rule["cite"] == flow}
        self.assertEqual(flags, {True, False})


# --- Coverage ---------------------------------------------------------------------------------------

class CoverageTests(unittest.TestCase):
    def test_every_rule_fires_in_some_scenario(self):
        fired = set()
        for name, persona_dir, change in SCENARIOS:
            with self.subTest(scenario=name):
                run_level(persona_dir, change, fired)
        missing = [rule["id"] for rule in load(RULES)["rules"] if rule["id"] not in fired]
        self.assertEqual(missing, [], "rules that no scenario fires")


if __name__ == "__main__":
    unittest.main()
