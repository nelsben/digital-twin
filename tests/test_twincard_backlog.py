"""Tests for the backlog builder: scripts/twincard/backlog.py and data/task-library.json.

The expected epic, feature and story ids for the two fictional fixtures are checked in
test_twincard_acceptance.py; this file checks the builder itself: loading the task library, its links
and its coverage of design section 7.2, statuses kept across runs, retired items, the command line, the
--plan-out shape and byte-identical output.

Standard library only. Anything the tests write goes to a temporary folder.
Run with: python3 -m unittest discover -s tests
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
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
PLUGIN_DIR = ROOT / "partner-kit" / "plugins" / "twin-consultant"
SCRIPTS_DIR = PLUGIN_DIR / "scripts"
CLI = SCRIPTS_DIR / "twincard" / "cli.py"
LIBRARY = PLUGIN_DIR / "data" / "task-library.json"
DESIGN = ROOT / "partner-kit" / "docs" / "design.md"
EXPECTATIONS = ROOT / "tests" / "fixtures" / "twincard" / "expectations.json"
PE = ROOT / "engagements" / "sample-pe" / "personas" / "deal-team-associate"
TEAM = ROOT / "engagements" / "sample-team-cs" / "personas" / "customer-success-manager"
BROKER = ROOT / "tests" / "fixtures" / "twincard" / "sample-insurance-broker" / "personas" / "claims-handler"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from twincard import fields as F  # noqa: E402
from twincard import level as L  # noqa: E402
from twincard import backlog as B  # noqa: E402

STALE = "levelled.json is missing or out of date. Next: run the level command."
CLIENT_SKILL_SIX = ["collect-examples", "write-evals", "write-skill", "trigger-evals", "second-review",
                    "publish-in-role-plugin"]
FOUNDATION = ["S-persona-voice", "S-connectors-and-identity", "S-guardrails-and-settings", "S-distribution",
              "S-governance-log", "S-memory-policy", "S-pilot-rollout-and-scorecard"]
TOP_KEYS = ["backlog_version", "customer", "persona", "source", "unnamed_roles", "epic", "retired"]
STORY_KEYS = ["id", "title", "statement", "part", "in_pilot", "priority", "status", "fields", "acceptance",
              "gated_by", "tasks"]
TASK_KEYS = ["id", "template", "title", "part", "how", "done_when", "owner_role", "owner_name", "acting_owner",
             "status"]


# --- Markdown anchors (the same rules as test_twincard_acceptance.py) ------------------------------

def slug(heading):
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading)
    text = text.replace("`", "").replace("*", "").strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def anchors_of(page_text):
    anchors, seen, in_fence = set(), {}, False
    for line in page_text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^#{1,6}\s+(.*?)\s*#*\s*$", line)
        if not m:
            continue
        base = slug(m.group(1))
        n = seen.get(base, 0)
        anchors.add(base if n == 0 else "%s-%d" % (base, n))
        seen[base] = n + 1
    return anchors


def runbook_links(link, when):
    """A library link, with {connector.runbook} filled in from each pack runbook the template's 'when' admits."""
    if not link or not link.startswith(B.RUNBOOK_PLACEHOLDER):
        return [link] if link else []
    known = set(B.allowed_facts("task-story", "connector"))
    out = []
    for path in sorted((PLUGIN_DIR / "data" / "industry-packs").glob("*.json")):
        for default in load(path).get("connector_defaults") or []:
            facts = dict((name, None) for name in known)
            facts.update({"connector.runbook": default.get("runbook"), "connector.kind": default.get("system_kind")})
            if default.get("runbook") and L.matches(when, facts, known):
                target = default["runbook"] + link[len(B.RUNBOOK_PLACEHOLDER):]
                if target not in out:
                    out.append(target)
    return out


def link_problem(target):
    """None when a repo-relative path (with an optional #anchor) resolves; otherwise what is wrong."""
    path, _, anchor = target.partition("#")
    full = (ROOT / path).resolve()
    if not full.is_file():
        return "%s: no such file" % target
    if anchor and anchor not in anchors_of(full.read_text(encoding="utf-8")):
        return "%s: no heading with that anchor" % target
    return None


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


# --- Scenarios: a changed temporary copy of a fixture, levelled ------------------------------------

class Scenario(object):
    """A temporary copy of a fixture's engagement, changed by a function of (profile, card), then levelled.

    after(persona) runs once levelled.json is written, for changes to levelled.json itself. An after
    with patch = True instead returns a patch that is in force from before levelling until the scenario
    ends, so a backlog built inside the scenario levels again under it.
    """

    def __init__(self, persona_dir, change=None, level=True, after=None):
        self.persona_dir, self.change, self.level, self.after = Path(persona_dir), change, level, after

    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        engagement = self.persona_dir.parent.parent
        root = Path(self.tmp.name) / engagement.name
        shutil.copytree(engagement, root)
        persona = root / self.persona_dir.relative_to(engagement)
        for name in ("backlog.json", "backlog.md"):
            if (persona / name).exists():
                (persona / name).unlink()
        if self.change:
            profile, card = load(root / "customer-profile.json"), load(persona / "card.json")
            self.change(profile, card)
            (root / "customer-profile.json").write_text(json.dumps(profile, indent=2), encoding="utf-8")
            (persona / "card.json").write_text(json.dumps(card, indent=2), encoding="utf-8")
        self.patcher = None
        if self.after is not None and getattr(self.after, "patch", False):
            self.patcher = self.after()
            self.patcher.start()
            self.after = None
        if self.level:
            result = L.write_levelled(str(persona))
            if not result["ok"]:
                raise AssertionError("scenario does not validate: %s" % result["validation"]["errors"])
        if self.after:
            self.after(persona)
        return persona

    def __exit__(self, *exc):
        if self.patcher is not None:
            self.patcher.stop()
        self.tmp.cleanup()


def task(card, tid):
    return next(t for t in card["tasks"] if t["id"] == tid)


def set_task(tid, **values):
    def change(profile, card):
        task(card, tid).update(values)
    return change


def override(tid, decision, value):
    def change(profile, card):
        card["overrides"] = [{"task": tid, "decision": decision, "value": value,
                              "reason": "Invented reason for a test.", "approved_by": "Test approver"}]
    return change


def team_c2_writes_hubspot(profile, card):
    task(card, "C2")["writes"][0].update({"system": "hubspot", "action": "create"})


def bad_plugin_name(profile, card):
    card["role"]["plugin_name"] = "Deal Team"


def open_task_field(profile, card):
    task(card, "C1")["reads_untrusted_input"] = None
    card["provenance"]["tasks.C1.reads_untrusted_input"] = {
        "status": "open", "source": "interviews/2026-11-06-csm.md#F8", "owner": "Test owner", "due": "2026-12-11"}


def open_persona_field(profile, card):
    profile["governance"]["action_log_required"] = None
    profile["provenance"]["governance.action_log_required"] = {
        "status": "open", "source": "discovery.md#G1", "owner": "Test owner", "due": "2026-12-11"}


def inject_unknown_target():
    """override-unknown-target cannot pass validation through a card, and a hand-edited levelled.json is
    now refused as out of date, so level itself is patched to raise it (OPS-47)."""
    real = L.override_problems

    def with_unknown_target(overrides, task_ids, catalogue=None):
        return real(overrides, task_ids, catalogue) + [(None, {
            "code": "override-unknown-target", "about": "persona", "cite": L.DESIGN_CITE, "unverified": False,
            "message": "overrides[0] names a task that levelling does not have.",
            "fix": "Name a task id on the card."})]
    return mock.patch.object(L, "override_problems", with_unknown_target)


inject_unknown_target.patch = True


def profile_value(key, value):
    def change(profile, card):
        profile[key] = value
    return change


def profile_section(section_name, key, value):
    def change(profile, card):
        profile[section_name][key] = value
    return change


def role_device(value):
    def change(profile, card):
        card["role"]["device"] = value
    return change


def team_inside_network_only(profile, card):
    """No IP allowlist, and C1 (a client skill) reads the private usage database."""
    profile["network"]["can_allowlist_anthropic_ips"] = False
    inputs = task(card, "C1")["inputs"]
    inputs.append({"system": "usage-db", "objects": "usage aggregates", "access": "read"})
    card["provenance"]["tasks.C1.inputs[%d].access" % (len(inputs) - 1)] = {
        "status": "answered", "source": "interviews/2026-11-06-csm.md#F7"}


# Local scenarios for templates that neither fixture nor any expectations variant reaches.
LOCAL_SCENARIOS = [
    ("pe with the b2b-software pack (empty baseline fact)", PE, profile_value("industry", "b2b-software"), None),
    ("pe T1 schedule-own", PE, set_task("T1", trigger="schedule-own"), None),
    ("team no allowlist, C1 reads usage-db", TEAM, team_inside_network_only, None),
    ("pe mixed devices", PE, role_device("mixed"), None),
    ("team custom-30-day retention", TEAM, profile_section("compliance", "retention", "custom-30-day"), None),
    ("team C1 schedule-own", TEAM, set_task("C1", trigger="schedule-own"), None),
    ("team C5 event-started", TEAM, set_task("C5", trigger="event"), None),
    ("team C2 writes HubSpot (managed-agents)", TEAM, team_c2_writes_hubspot, None),
    ("team C4 starts at level 2", TEAM, override("C4", "autonomy.start", 2), None),
    ("team C2 starts at level 2", TEAM, override("C2", "autonomy.start", 2), None),
    ("pe T3 override agent-sdk", PE, override("T3", "runtime", "agent-sdk"), None),
    ("pe bad plugin name", PE, bad_plugin_name, None),
    ("team C1 plan_fit override", TEAM, override("C1", "plan_fit", "ok"), None),
    ("team C1 open field", TEAM, open_task_field, None),
    ("team open persona field", TEAM, open_persona_field, None),
    ("team unknown override target", TEAM, None, inject_unknown_target),
    ("insurance broker (fictional, tests only)", BROKER, None, None),
]


def _resolve(record, data, path, catalogue):
    """Walk an instance path such as tasks.C4.writes[1].action; return (parent, key)."""
    keys = catalogue["keys"][record]
    tokens = path.split(".")
    node, cat, i = data, [], 0
    while i < len(tokens):
        token = tokens[i]
        m = re.fullmatch(r"([A-Za-z_]+)\[(\d+)\]", token)
        name = m.group(1) if m else token
        list_path = ".".join(cat + [name])
        last = i == len(tokens) - 1
        if m:
            items = node.setdefault(name, [])
            index = int(m.group(2))
            if index == len(items):
                items.append({})
            node = items[index]
            cat.append(name + "[]")
            i += 1
        elif list_path in keys and keys[list_path] is not None and not last:
            node = next(item for item in node.get(name, []) if item.get(keys[list_path]) == tokens[i + 1])
            cat.append(name + "[]")
            i += 2
        elif last:
            return node, name
        else:
            node = node.setdefault(name, {})
            cat.append(name)
            i += 1
    raise KeyError(path)


def variant_change(variant, catalogue):
    def change(profile, card):
        records = {"profile": profile, "card": card}
        for item in variant["change"]:
            data = records[item["record"]]
            if item["path"].startswith("provenance."):
                data.setdefault("provenance", {})[item["path"][len("provenance."):]] = item["value"]
                continue
            parent, key = _resolve(item["record"], data, item["path"], catalogue)
            parent[key] = item["value"]
    return change


def all_scenarios():
    """(name, persona_dir, change, after) for both fixtures, every expectations variant and the local ones."""
    exp = load(EXPECTATIONS)
    catalogue = F.load_catalogue()
    out = [("pe", PE, None, None), ("team", TEAM, None, None)]
    for variant in exp["variants"]:
        base = ROOT / exp["fixtures"][variant["base"]]["persona_dir"]
        out.append(("variant " + variant["id"], base, variant_change(variant, catalogue), None))
    return out + list(LOCAL_SCENARIOS)


def stories_of(backlog):
    return [story for feature in backlog["epic"]["features"] for story in feature["stories"]]


def tasks_of(backlog):
    return [t for story in stories_of(backlog) for t in story["tasks"]]


def when_values(when, fact):
    """Every value a condition compares the named fact against, inside any/all/not too."""
    out = []
    for key, want in when.items():
        if key in ("any", "all"):
            for item in want:
                out.extend(when_values(item, fact))
        elif key == "not":
            out.extend(when_values(want, fact))
        elif key == fact:
            out.extend(want if isinstance(want, list) else [want])
    return out


def design_runtimes():
    text = DESIGN.read_text(encoding="utf-8")
    row = re.search(r"^\| `runtime` \| (.*)\|$", text, re.MULTILINE)
    return re.findall(r"`([a-z0-9-]+)`", re.sub(r"\([^)]*\)", "", row.group(1)))


def cli(*args):
    return subprocess.run([sys.executable, str(CLI)] + [str(a) for a in args], capture_output=True, text=True,
                          cwd=str(Path(tempfile.gettempdir())), timeout=120)


# --- The task library -------------------------------------------------------------------------------

class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.data = load(LIBRARY)

    def load_changed(self, change):
        data = copy.deepcopy(self.data)
        change(data)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "task-library.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            return B.load_library(path)

    def assertLoadError(self, change, *needles):
        with self.assertRaises(B.BacklogError) as ctx:
            self.load_changed(change)
        for needle in needles:
            self.assertIn(needle, str(ctx.exception))

    def test_shipped_library_loads(self):
        library = B.load_library()
        self.assertEqual(library["library_version"], 1)
        self.assertEqual(list(self.data), ["library_version", "owner_roles", "templates"])
        self.assertIn("consultant", library["owner_roles"])
        self.assertIn("skill-owner", library["owner_roles"])

    def test_duplicate_id(self):
        def change(data):
            data["templates"].append(copy.deepcopy(data["templates"][0]))
        self.assertLoadError(change, data_id(self.data, 0), "duplicate")

    def test_unknown_part(self):
        def change(data):
            data["templates"][0]["part"] = "A10"
        self.assertLoadError(change, data_id(self.data, 0), "A10")

    def test_unknown_owner_role(self):
        def change(data):
            data["templates"][0]["owner_role"] = "astronaut"
        self.assertLoadError(change, data_id(self.data, 0), "astronaut")

    def test_unknown_fact_in_when(self):
        def change(data):
            data["templates"][0]["when"] = {"any": [{"task.colour": "red"}]}
        self.assertLoadError(change, data_id(self.data, 0), "task.colour")

    def test_item_fact_needs_its_per(self):
        def change(data):
            data["templates"][0]["per"] = None
            data["templates"][0]["when"] = {"connector.kind": "crm"}
        self.assertLoadError(change, data_id(self.data, 0), "connector.kind")

    def test_foundation_template_cannot_read_task_facts(self):
        def change(data):
            found = next(t for t in data["templates"] if t["applies_to"] != "task-story")
            found["when"] = {"task.trigger": "person"}
        found = next(t for t in self.data["templates"] if t["applies_to"] != "task-story")
        self.assertLoadError(change, found["id"], "task.trigger")

    def test_fewer_than_two_how_steps(self):
        def change(data):
            data["templates"][0]["how"] = data["templates"][0]["how"][:1]
        self.assertLoadError(change, data_id(self.data, 0), "how")

    def test_empty_done_when(self):
        def change(data):
            data["templates"][0]["done_when"] = " "
        self.assertLoadError(change, data_id(self.data, 0), "done_when")

    def test_unknown_applies_to(self):
        def change(data):
            data["templates"][0]["applies_to"] = "S-somewhere"
        self.assertLoadError(change, data_id(self.data, 0), "S-somewhere")

    def test_template_shape(self):
        keys = ["id", "title", "part", "applies_to", "per", "when", "how", "done_when", "owner_role"]
        for template in self.data["templates"]:
            with self.subTest(template=template["id"]):
                self.assertEqual(list(template), keys)
                self.assertRegex(template["id"], r"^[a-z0-9]+(-[a-z0-9]+)*$")
                for step in template["how"]:
                    self.assertEqual(list(step), ["text", "link"])
                    self.assertTrue(step["text"].strip().endswith("."), step["text"])

    def test_every_how_link_resolves(self):
        for template in self.data["templates"]:
            for step in template["how"]:
                if step["link"] is None:
                    continue
                for link in runbook_links(step["link"], template["when"]):
                    with self.subTest(template=template["id"], link=link):
                        self.assertFalse(link.startswith("/") or "://" in link, link)
                        self.assertIsNone(link_problem(link))

    def test_every_code_and_runtime_in_design_has_a_template(self):
        codes = L.design_codes()
        self.assertTrue(codes)
        covered = set()
        for template in self.data["templates"]:
            covered.update(when_values(template["when"], "codes"))
        for code in sorted(codes):
            self.assertIn(code, covered, "no task-library template for code %s" % code)
        self.assertFalse(covered - codes, "templates name codes design 7.2 does not list")
        runtimes = design_runtimes()
        self.assertEqual(len(runtimes), 7, runtimes)
        reached = set()
        for template in self.data["templates"]:
            reached.update(when_values(template["when"], "runtime"))
        for runtime in runtimes:
            self.assertIn(runtime, reached, "no task-library template for runtime %s" % runtime)

    def test_every_pack_runbook_has_a_connect_template(self):
        runbooks = set()
        for path in (PLUGIN_DIR / "data" / "industry-packs").glob("*.json"):
            for default in load(path).get("connector_defaults") or []:
                if default.get("runbook"):
                    runbooks.add(default["runbook"])
        connect = [t for t in self.data["templates"] if t["id"].startswith("connect-")]
        known = set(B.allowed_facts("task-story", "connector"))

        def covering(runbook):
            facts = dict((name, None) for name in known)
            facts["connector.runbook"] = runbook
            return [t["id"] for t in connect if L.matches(t["when"], facts, known)]
        for runbook in sorted(runbooks):
            self.assertTrue(covering(runbook), "no connect template for runbook %s" % runbook)
        covered = set()
        for template in self.data["templates"]:
            covered.update(when_values(template["when"], "connector.runbook"))
        self.assertIn(None, covered, "no template says plainly that a connector has no runbook")

    def test_owner_roles_are_listed_in_design_section_8(self):
        text = DESIGN.read_text(encoding="utf-8")
        section = re.search(r"^## 8\..*?(?=^## 9\.)", text, re.MULTILINE | re.DOTALL).group(0)
        for role in self.data["owner_roles"]:
            self.assertIn("`%s`" % role, section, role)

    def test_no_template_names_a_customer_person_or_fixture(self):
        text = json.dumps(self.data["templates"], ensure_ascii=False)
        names = {"sample-pe", "sample-team-cs", "deal-team-associate", "customer-success-manager"}
        for persona in (PE, TEAM):
            card = load(persona / "card.json")
            profile = load(persona.parent.parent / "customer-profile.json")
            names.update([profile["customer"], profile["display_name"], card["customer"]])
            names.update(t["skill_owner"] for t in card["tasks"] if t.get("skill_owner"))
            names.update(q["owner"] for q in card.get("open_questions") or [] if q.get("owner"))
            names.update(v for v in (profile.get("owners") or {}).values() if isinstance(v, str) and v)
        for name in sorted(names):
            self.assertNotIn(name, text, name)


def data_id(data, index):
    return data["templates"][index]["id"]


# --- Building ---------------------------------------------------------------------------------------

class BuildTests(unittest.TestCase):
    def test_build_never_writes_and_has_the_shape(self):
        with Scenario(TEAM) as persona:
            result = B.build(str(persona))
            self.assertTrue(result["ok"], result)
            self.assertFalse((persona / "backlog.json").exists())
            self.assertFalse((persona / "backlog.md").exists())
        backlog = result["backlog"]
        self.assertEqual(list(backlog), TOP_KEYS)
        self.assertEqual(list(backlog["source"]), ["card_sha256", "levelled_sha256", "library_version"])
        self.assertEqual(list(backlog["epic"]), ["id", "title", "status", "features"])
        self.assertEqual(backlog["epic"]["id"], "E")
        for feature in backlog["epic"]["features"]:
            self.assertEqual(list(feature), ["id", "title", "kind", "status", "stories"])
            self.assertIn(feature["kind"], ("capability", "foundation"))
            for story in feature["stories"]:
                self.assertEqual(list(story), STORY_KEYS, story["id"])
                self.assertTrue(story["tasks"], "%s has no task" % story["id"])
                for item in story["tasks"]:
                    self.assertEqual(list(item), TASK_KEYS)
                    self.assertTrue(item["id"].startswith(story["id"] + "." + item["template"]), item["id"])
                    self.assertEqual(item["status"], "todo")
        foundation = backlog["epic"]["features"][-1]
        self.assertEqual(foundation["id"], "F-twin-foundation")
        self.assertEqual([s["id"] for s in foundation["stories"]], FOUNDATION)

    def test_task_ids_are_unique(self):
        for persona_dir in (PE, TEAM):
            backlog = B.build(str(persona_dir))["backlog"]
            ids = [t["id"] for t in tasks_of(backlog)] + [s["id"] for s in stories_of(backlog)]
            self.assertEqual(len(ids), len(set(ids)))

    def test_statement_fields_and_acceptance(self):
        backlog = B.build(str(PE))["backlog"]
        story = next(s for s in stories_of(backlog) if s["id"] == "S-T4")
        self.assertEqual(story["statement"],
                         "As a Deal-team associate, I want my twin to screen an inbound CIM or teaser so that I get "
                         "the screening summary with a pursue-or-pass suggestion.")
        self.assertEqual(story["fields"]["autonomy"], "1 to 3")
        self.assertEqual(story["fields"]["data_class"], "highly-sensitive")
        self.assertIn("Plus: no web tools are used.", story["acceptance"])
        self.assertIn("Plus: each tool call reaches the governance log.", story["acceptance"])
        t2 = next(s for s in stories_of(backlog) if s["id"] == "S-T2")
        self.assertEqual(t2["fields"]["baseline"], "10 per week x 15 minutes each x 18 users")
        # T2's Salesforce write is Blocked at the starting level, so the twin writes nothing to the CRM yet.
        self.assertNotIn("Plus: every write carries the twin marker.", t2["acceptance"])
        self.assertIn("Plus: the twin writes nothing to the CRM at the starting level; a person files the result.",
                      t2["acceptance"])
        team = B.build(str(TEAM))["backlog"]
        c1 = next(s for s in stories_of(team) if s["id"] == "S-C1")
        self.assertNotIn("Plus: no web tools are used.", c1["acceptance"])
        self.assertFalse([a for a in c1["acceptance"] if "governance log" in a])
        self.assertEqual(len([a for a in c1["acceptance"] if a.startswith("Eval")]), 3)

    def test_stories_sort_in_pilot_then_priority_then_card_order(self):
        backlog = B.build(str(PE))["backlog"]
        pre = next(f for f in backlog["epic"]["features"] if f["id"] == "F-pre-meeting-preparation")
        self.assertEqual([s["id"] for s in pre["stories"]], ["S-T1", "S-T5"])
        pipe = next(f for f in backlog["epic"]["features"] if f["id"] == "F-pipeline-upkeep-and-reporting")
        self.assertEqual([s["id"] for s in pipe["stories"]], ["S-T2", "S-T3"])

    def test_client_skill_stories_get_the_six_tasks_in_order(self):
        for persona_dir in (PE, TEAM):
            levelled = load(persona_dir / "levelled.json")
            backlog = B.build(str(persona_dir))["backlog"]
            for story in stories_of(backlog):
                tid = story["id"][2:]
                if tid not in levelled["tasks"] or levelled["tasks"][tid]["runtime"]["value"] != "client-skill":
                    continue
                # On Team the skill is published to every member, so the Team publish template ends the six.
                six = CLIENT_SKILL_SIX[:-1] + ["publish-in-role-plugin-team" if persona_dir == TEAM
                                               else "publish-in-role-plugin"]
                with self.subTest(story=story["id"]):
                    seen = [t["template"] for t in story["tasks"] if t["template"] in six]
                    self.assertEqual(seen, six)

    def test_open_questions_and_blockers_gate_stories(self):
        backlog = B.build(str(PE))["backlog"]
        t1 = next(s for s in stories_of(backlog) if s["id"] == "S-T1")
        self.assertIn("E4", [g["id"] for g in t1["gated_by"] if g["kind"] == "open-question"])
        for g in t1["gated_by"]:
            self.assertEqual(list(g), ["kind", "id", "text"])
        with Scenario(TEAM, set_task("C1", data_class="highly-sensitive")) as persona:
            backlog = B.build(str(persona))["backlog"]
        c1 = next(s for s in stories_of(backlog) if s["id"] == "S-C1")
        blockers = {g["id"] for g in c1["gated_by"] if g["kind"] == "blocker"}
        self.assertEqual(blockers, {"highly-sensitive-needs-zdr-org", "unmanaged-device-no-access"})
        self.assertTrue(c1["tasks"])

    def test_per_item_templates_name_the_item(self):
        backlog = B.build(str(PE))["backlog"]
        t2 = next(s for s in stories_of(backlog) if s["id"] == "S-T2")
        ids = [t["id"] for t in t2["tasks"]]
        self.assertIn("S-T2.tool-blocked.salesforce-update", ids)
        blocked = next(t for t in t2["tasks"] if t["id"] == "S-T2.tool-blocked.salesforce-update")
        self.assertIn("salesforce-update", blocked["title"])
        unverified = [t for t in t2["tasks"] if t["template"] == "confirm-unverified-decision"]
        self.assertEqual([t["id"] for t in unverified], ["S-T2.confirm-unverified-decision.connectors.salesforce"])
        self.assertIn("connectors.salesforce", unverified[0]["title"])


class ReachTests(unittest.TestCase):
    """Every template reaches a story somewhere, and every raised code gives a task in its story."""

    @classmethod
    def setUpClass(cls):
        cls.library = B.load_library()
        cls.runs = []
        for name, persona_dir, change, after in all_scenarios():
            with Scenario(persona_dir, change, after=after) as persona:
                levelled = load(persona / "levelled.json")
                result = B.build(str(persona))
            cls.runs.append((name, levelled, result))

    def test_every_scenario_builds(self):
        for name, _, result in self.runs:
            self.assertTrue(result["ok"], "%s: %s" % (name, result.get("error")))

    def test_every_template_reaches_a_story(self):
        used = set()
        for _, _, result in self.runs:
            used.update(t["template"] for t in tasks_of(result["backlog"]))
        for template in self.library["templates"]:
            self.assertIn(template["id"], used, "template %s reaches no story in any fixture, expectations "
                                                "variant or local scenario" % template["id"])

    def test_every_raised_code_gives_a_task(self):
        by_template = dict((t["id"], t) for t in self.library["templates"])
        for name, levelled, result in self.runs:
            stories = dict((s["id"], s) for s in stories_of(result["backlog"]))
            for item in levelled["blockers"] + levelled["warnings"]:
                with self.subTest(scenario=name, code=item["code"], about=item["about"]):
                    if item["about"] == "persona":
                        candidates = [s for sid, s in stories.items() if sid in FOUNDATION]
                    else:
                        candidates = [stories["S-" + item["about"]]]
                    found = [t for s in candidates for t in s["tasks"]
                             if item["code"] in when_values(by_template[t["template"]]["when"], "codes")]
                    self.assertTrue(found, "%s: code %s about %s gives no task" % (name, item["code"], item["about"]))
                    self.assertIn(item["code"], found[0]["title"])

    def test_every_blocker_gates_its_story(self):
        for name, levelled, result in self.runs:
            stories = dict((s["id"], s) for s in stories_of(result["backlog"]))
            for item in levelled["blockers"]:
                targets = FOUNDATION if item["about"] == "persona" else ["S-" + item["about"]]
                for sid in targets:
                    gates = [(g["kind"], g["id"]) for g in stories[sid]["gated_by"]]
                    self.assertIn(("blocker", item["code"]), gates, "%s %s" % (name, sid))


class LevelledCheckTests(unittest.TestCase):
    def test_missing_levelled_json(self):
        with Scenario(TEAM) as persona:
            (persona / "levelled.json").unlink()
            result = B.build(str(persona))
            self.assertFalse(result["ok"])
            self.assertEqual(result["error"], STALE)
            proc = cli("backlog", persona)
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            self.assertIn(STALE, proc.stdout + proc.stderr)
            self.assertFalse((persona / "backlog.json").exists())
            self.assertFalse((persona / "backlog.md").exists())

    def test_out_of_date_card(self):
        with Scenario(TEAM) as persona:
            card = load(persona / "card.json")
            task(card, "C1")["minutes_each"] = 31
            (persona / "card.json").write_text(json.dumps(card, indent=2), encoding="utf-8")
            result = B.build(str(persona))
            self.assertFalse(result["ok"])
            self.assertEqual(result["error"], STALE)

    def test_out_of_date_profile(self):
        with Scenario(TEAM) as persona:
            path = persona.parent.parent / "customer-profile.json"
            path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            self.assertEqual(B.build(str(persona))["error"], STALE)

    def test_validation_errors_build_nothing(self):
        with Scenario(TEAM) as persona:
            card = load(persona / "card.json")
            task(card, "C1")["trigger"] = "sometimes"
            (persona / "card.json").write_text(json.dumps(card, indent=2), encoding="utf-8")
            result = B.build(str(persona))
            self.assertFalse(result["ok"])
            self.assertTrue(result["validation"]["errors"])
            proc = cli("backlog", persona)
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            self.assertFalse((persona / "backlog.json").exists())


class StatusTests(unittest.TestCase):
    def edit_status(self, persona, changes):
        path = persona / "backlog.json"
        data = load(path)
        for story in stories_of(data):
            for item in story["tasks"]:
                if item["id"] in changes:
                    item["status"] = changes[item["id"]]
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def test_status_is_kept_and_parents_are_derived(self):
        with Scenario(TEAM) as persona:
            B.write_backlog(str(persona))
            first = load(persona / "backlog.json")
            c1 = next(s for s in stories_of(first) if s["id"] == "S-C1")
            ids = [t["id"] for t in c1["tasks"]]
            self.edit_status(persona, {ids[0]: "done", ids[1]: "in-progress"})
            result = B.write_backlog(str(persona))
            self.assertTrue(result["ok"])
            data = load(persona / "backlog.json")
            c1 = next(s for s in stories_of(data) if s["id"] == "S-C1")
            self.assertEqual([t["status"] for t in c1["tasks"][:3]], ["done", "in-progress", "todo"])
            self.assertEqual(c1["status"], "in-progress")
            feature = next(f for f in data["epic"]["features"] if f["id"] == "F-call-preparation-and-follow-up")
            self.assertEqual(feature["status"], "in-progress")
            self.assertEqual(data["epic"]["status"], "in-progress")
            other = next(f for f in data["epic"]["features"] if f["id"] == "F-renewals")
            self.assertEqual(other["status"], "todo")
            md = (persona / "backlog.md").read_text(encoding="utf-8")
            self.assertIn("- [x] **%s**" % ids[0], md)
            self.assertIn("- [~] **%s**" % ids[1], md)
            self.assertIn("- [ ] **%s**" % ids[2], md)
            # Every task done: the story, and a feature of one story, become done.
            escalations = next(f for f in data["epic"]["features"] if f["id"] == "F-escalations")
            self.edit_status(persona, dict((t["id"], "done") for s in escalations["stories"] for t in s["tasks"]))
            B.write_backlog(str(persona))
            data = load(persona / "backlog.json")
            escalations = next(f for f in data["epic"]["features"] if f["id"] == "F-escalations")
            self.assertEqual(escalations["status"], "done")
            self.assertEqual(escalations["stories"][0]["status"], "done")

    def test_derived_status(self):
        self.assertEqual(B.derive_status(["done", "done"]), "done")
        self.assertEqual(B.derive_status(["todo", "todo"]), "todo")
        self.assertEqual(B.derive_status(["todo", "done"]), "in-progress")
        self.assertEqual(B.derive_status(["in-progress"]), "in-progress")

    def test_items_no_longer_generated_are_retired(self):
        with Scenario(TEAM) as persona:
            B.write_backlog(str(persona))
            self.edit_status(persona, {"S-C1.publish-in-role-plugin-team": "done", "S-C1.write-skill": "in-progress"})
            card = load(persona / "card.json")
            task(card, "C1")["trigger"] = "schedule-own"
            (persona / "card.json").write_text(json.dumps(card, indent=2), encoding="utf-8")
            L.write_levelled(str(persona))
            proc = cli("backlog", persona)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            data = load(persona / "backlog.json")
            retired = dict((r["id"], r) for r in data["retired"])
            # C1 moves from a client skill to a Claude Code scheduled task: publishing in the role
            # plugin no longer applies, but the skill tasks apply on every runtime, so they stay.
            self.assertEqual(set(retired), {"S-C1.publish-in-role-plugin-team"})
            self.assertEqual(list(retired["S-C1.publish-in-role-plugin-team"]), ["id", "title", "status"])
            self.assertEqual(retired["S-C1.publish-in-role-plugin-team"]["status"], "done")
            self.assertNotIn("S-C1.write-skill", retired)
            kept = next(t for f in data["epic"]["features"] for s in f["stories"] for t in s["tasks"]
                        if t["id"] == "S-C1.write-skill")
            self.assertEqual(kept["status"], "in-progress")
            for rid in retired:
                self.assertEqual(len([line for line in proc.stdout.splitlines() if rid in line]), 1, proc.stdout)
            self.assertIn("S-C1.publish-in-role-plugin-team", (persona / "backlog.md").read_text(encoding="utf-8"))
            # Retired items stay retired on the next run, with their status.
            B.write_backlog(str(persona))
            self.assertEqual(load(persona / "backlog.json")["retired"], data["retired"])

    def test_unknown_status_is_a_usage_error(self):
        with Scenario(TEAM) as persona:
            B.write_backlog(str(persona))
            self.edit_status(persona, {"S-C1.write-evals": "finished"})
            with self.assertRaises(B.UsageError) as ctx:
                B.build(str(persona))
            self.assertIn("S-C1.write-evals", str(ctx.exception))
            proc = cli("backlog", persona)
            self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
            self.assertIn("S-C1.write-evals", proc.stderr)


class CliTests(unittest.TestCase):
    def test_exit_0_writes_both_files_and_prints_counts(self):
        with Scenario(PE) as persona:
            proc = cli("backlog", persona)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertTrue((persona / "backlog.json").is_file())
            self.assertTrue((persona / "backlog.md").is_file())
            data = load(persona / "backlog.json")
        lines = proc.stdout.splitlines()
        self.assertIn(data["epic"]["title"], lines)
        for feature in data["epic"]["features"]:
            n_tasks = sum(len(s["tasks"]) for s in feature["stories"])
            self.assertIn("%s: %d stories, %d tasks" % (feature["id"], len(feature["stories"]), n_tasks),
                          proc.stdout)
        total = "Total: %d features, %d stories, %d tasks" % (
            len(data["epic"]["features"]), len(stories_of(data)), len(tasks_of(data)))
        self.assertIn(total, proc.stdout)

    def test_blocker_exits_1_and_still_writes(self):
        def change(profile, card):
            profile["plan"]["tier"] = "individual"
        with Scenario(TEAM, change) as persona:
            proc = cli("backlog", persona)
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            self.assertTrue((persona / "backlog.json").is_file())
            self.assertTrue((persona / "backlog.md").is_file())

    def test_usage_errors_exit_2(self):
        self.assertEqual(cli("backlog", ROOT / "no-such-folder").returncode, 2)
        self.assertEqual(cli("backlog").returncode, 2)
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(cli("backlog", tmp).returncode, 2)

    def test_json_prints_the_backlog(self):
        with Scenario(TEAM) as persona:
            proc = cli("backlog", "--json", persona)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(json.loads(proc.stdout), load(persona / "backlog.json"))

    def test_plan_out_shape(self):
        with Scenario(TEAM) as persona, tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            proc = cli("backlog", persona, "--plan-out", plan_path)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            plan = load(plan_path)
            data = load(persona / "backlog.json")
        self.assertEqual(list(plan), ["version", "items"])
        self.assertEqual(plan["version"], 1)
        self.assertEqual(len(plan["items"]), 1)
        counts = {}

        def walk(item, depth):
            self.assertEqual(list(item), ["type", "title", "note", "children"])
            self.assertEqual(item["type"], ["epic", "feature", "story", "task"][depth])
            counts[item["type"]] = counts.get(item["type"], 0) + 1
            if item["type"] == "task":
                self.assertEqual(item["children"], [])
                self.assertIn("Done when:", item["note"])
                self.assertIn("1. ", item["note"])
            for child in item["children"]:
                walk(child, depth + 1)
        walk(plan["items"][0], 0)
        self.assertEqual(counts, {"epic": 1, "feature": len(data["epic"]["features"]),
                                  "story": len(stories_of(data)), "task": len(tasks_of(data))})
        self.assertTrue(plan["items"][0]["note"].startswith("E"))
        ids = [t["id"] for t in tasks_of(data)]
        notes = []

        def collect(item):
            notes.append(item["note"])
            for child in item["children"]:
                collect(child)
        collect(plan["items"][0])
        for tid in ids:
            self.assertTrue(any(note.startswith(tid + "\n") or note == tid for note in notes), tid)

    def test_validate_and_level_still_work(self):
        with Scenario(TEAM) as persona:
            self.assertEqual(cli("validate", persona).returncode, 0)
            self.assertEqual(cli("level", persona).returncode, 0)


class OutputTests(unittest.TestCase):
    def test_two_runs_give_the_same_bytes(self):
        with Scenario(PE) as persona:
            B.write_backlog(str(persona))
            first = [(persona / n).read_bytes() for n in ("backlog.json", "backlog.md")]
            B.write_backlog(str(persona))
            second = [(persona / n).read_bytes() for n in ("backlog.json", "backlog.md")]
        self.assertEqual(first, second)
        self.assertTrue(first[0].endswith(b"\n") and not first[0].endswith(b"\n\n"))
        self.assertNotRegex(first[0].decode("utf-8") + first[1].decode("utf-8"),
                            r"20[0-9]{2}-[0-9]{2}-[0-9]{2}T|/Users/|/home/|/tmp/|\\\\")

    def test_markdown_heads_and_says_it_is_generated(self):
        backlog = B.build(str(TEAM))["backlog"]
        lines = B.render_md(backlog).splitlines()
        self.assertEqual(lines[0], "# " + backlog["epic"]["title"])
        self.assertEqual(lines[1], "")
        self.assertIn("generated from card.json and levelled.json", lines[2].lower())
        self.assertIn("never edit", lines[2].lower())
        self.assertIn("cli.py backlog engagements/sample-team-cs/personas/customer-success-manager", lines[2])
        for feature in backlog["epic"]["features"]:
            self.assertIn("## %s: %s" % (feature["id"], feature["title"]), lines)
            for story in feature["stories"]:
                self.assertIn("### %s: %s" % (story["id"], story["title"]), lines)

    def test_markdown_links_resolve_from_the_persona_folder(self):
        for persona_dir in (PE, TEAM):
            text = B.render_md(B.build(str(persona_dir))["backlog"])
            links = re.findall(r"\]\(([^)\s]+)\)", text)
            self.assertTrue(links)
            for link in sorted(set(links)):
                with self.subTest(persona=persona_dir.name, link=link):
                    self.assertFalse("://" in link or link.startswith("/"), link)
                    path, _, anchor = link.partition("#")
                    full = (persona_dir / path).resolve()
                    self.assertTrue(full.is_file(), link)
                    if anchor:
                        self.assertIn(anchor, anchors_of(full.read_text(encoding="utf-8")), link)


if __name__ == "__main__":
    unittest.main()
