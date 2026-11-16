"""The pack's starting skills and data providers reach the tasks that use them (OPS-57).

Covers:
* the card field tasks[].starts_from: names from the anthropic_starting_points of the customer's pack or
  the general pack, use start-from or reuse; an unknown name or a reference entry is one validation error;
* the write-skill task of a story whose card task has starts_from: one 'Start from' step per starting
  point before its own steps, linked to the starting point's cite, and a title naming the first one;
* the foundation's data-provider list and its decision task, present only for a pack with providers;
* the two foundation templates for retention and feedback, and for spend limits;
* required_when: skill_owner and the example counts are required for an in-pilot task only;
* both committed worked examples match a fresh run of the 'all' command.

Standard library only. Run with: python3 -m unittest tests.test_twincard_starting_points
"""

import json
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
PACKS_DIR = PLUGIN_DIR / "data" / "industry-packs"
LIBRARY = PLUGIN_DIR / "data" / "task-library.json"
FIELDS = PLUGIN_DIR / "data" / "fields.json"
CARD_TEMPLATE = PLUGIN_DIR / "templates" / "card.json"
DESIGN = ROOT / "partner-kit" / "docs" / "design.md"
PE = ROOT / "engagements" / "sample-pe" / "personas" / "deal-team-associate"
TEAM = ROOT / "engagements" / "sample-team-cs" / "personas" / "customer-success-manager"
GENERATED = ("levelled.json", "backlog.json", "backlog.md", "dashboard.html")
DATE = "2026-11-15"
FIX = "use a name from the pack's starting points, or remove it."
PROVIDERS_HEADING = "Data providers the pack knows (none is on by default)"
UNVERIFIED = "⚠ Unverified"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from twincard import backlog as B  # noqa: E402
from twincard import fields as F  # noqa: E402
from twincard import level as L  # noqa: E402
from twincard import packs as P  # noqa: E402
from twincard import validate as V  # noqa: E402


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def pack(pack_id):
    return load(PACKS_DIR / (pack_id + ".json"))


def starting_point(pack_id, name):
    return next(p for p in pack(pack_id)["anthropic_starting_points"] if p["name"] == name)


def task(card, tid):
    return next(t for t in card["tasks"] if t["id"] == tid)


def stories(backlog):
    return dict((s["id"], s) for f in backlog["epic"]["features"] for s in f["stories"])


def item(story, template):
    found = [t for t in story["tasks"] if t["template"] == template]
    return found[0] if found else None


class Copy(object):
    """A temporary copy of a sample's engagement, changed by change(profile, card)."""

    def __init__(self, persona_dir, change=None):
        self.persona_dir, self.change = Path(persona_dir), change

    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        engagement = self.persona_dir.parent.parent
        root = Path(self.tmp.name) / engagement.name
        shutil.copytree(engagement, root)
        persona = root / self.persona_dir.relative_to(engagement)
        for name in GENERATED:
            if (persona / name).exists():
                (persona / name).unlink()
        if self.change:
            profile, card = load(root / "customer-profile.json"), load(persona / "card.json")
            self.change(profile, card)
            (root / "customer-profile.json").write_text(json.dumps(profile, indent=2), encoding="utf-8")
            (persona / "card.json").write_text(json.dumps(card, indent=2), encoding="utf-8")
        return persona

    def __exit__(self, *exc):
        self.tmp.cleanup()


def validate(persona_dir, change=None):
    with Copy(persona_dir, change) as persona:
        return V.validate(str(persona), F.load_catalogue())


def build(persona_dir, change=None):
    """Level and build the backlog of a changed copy; return (backlog, backlog.md text)."""
    with Copy(persona_dir, change) as persona:
        levelled = L.write_levelled(str(persona))
        if not levelled["ok"]:
            raise AssertionError("the copy does not validate: %s" % levelled["validation"]["errors"])
        result = B.build(str(persona))
        if not result["ok"]:
            raise AssertionError("the backlog does not build: %s" % result["error"])
        return result["backlog"], B.render_md(result["backlog"], str(persona))


def starts(tid, names):
    def change(profile, card):
        task(card, tid)["starts_from"] = list(names)
    return change


def errors_at(result, path):
    return [e for e in result["errors"] if e["record"] == "card" and e["path"] == path]


# --- The card field ----------------------------------------------------------------------------------

class FieldTest(unittest.TestCase):
    def test_catalogue_entry(self):
        entry = F.entry_for("card", "tasks[].starts_from")
        self.assertIsNotNone(entry, "fields.json has no tasks[].starts_from")
        self.assertEqual((entry["type"], entry["required"], entry["key"], entry["part"]),
                         ("string-list", False, False, "A2"))
        self.assertEqual(entry["asked_by"], [])
        self.assertEqual(entry["feeds"], ["backlog:task"])
        self.assertIsInstance(entry["default"], dict)
        self.assertEqual(entry["default"]["value"], [])
        self.assertNotIn("required_when", entry)

    def test_template_carries_it_empty(self):
        for item_ in load(CARD_TEMPLATE)["tasks"]:
            self.assertEqual(item_.get("starts_from"), [])

    def test_required_when_on_the_three_fields(self):
        for path in ("tasks[].skill_owner", "tasks[].examples.good", "tasks[].examples.bad"):
            entry = F.entry_for("card", path)
            self.assertEqual(entry.get("required_when"), {"in_pilot": True}, path)
            self.assertFalse(entry["required"], path)

    def test_a_bad_required_when_is_refused(self):
        catalogue = load(FIELDS)
        entry = next(e for e in catalogue["fields"] if e["path"] == "tasks[].skill_owner")
        entry["required_when"] = {"data_class": "phi"}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fields.json"
            path.write_text(json.dumps(catalogue), encoding="utf-8")
            with self.assertRaises(F.CatalogueError) as caught:
                F.load_catalogue(path)
        self.assertIn("required_when", str(caught.exception))


class ValidateStartsFromTest(unittest.TestCase):
    def test_an_unknown_name_is_one_error(self):
        result = validate(TEAM, starts("C3", ["no-such-skill"]))
        found = errors_at(result, "tasks.C3.starts_from")
        self.assertEqual(len(found), 1, result["errors"])
        self.assertIn("C3", found[0]["message"])
        self.assertIn("no-such-skill", found[0]["message"])
        self.assertEqual(found[0]["fix"], FIX)

    def test_a_reference_entry_is_refused(self):
        self.assertEqual(starting_point("b2b-software", "sales")["use"], "reference")
        result = validate(TEAM, starts("C1", ["sales"]))
        found = errors_at(result, "tasks.C1.starts_from")
        self.assertEqual(len(found), 1, result["errors"])
        self.assertIn("sales", found[0]["message"])
        self.assertIn("reference", found[0]["message"])
        self.assertEqual(found[0]["fix"], FIX)

    def test_a_general_pack_name_is_accepted(self):
        self.assertEqual(starting_point("general", "pptx")["use"], "start-from")
        result = validate(TEAM, starts("C2", ["pptx", "draft-response"]))
        self.assertTrue(result["ok"], result["errors"])

    def test_the_command_line_names_the_task_and_ends_with_the_fix(self):
        with Copy(TEAM, starts("C3", ["no-such-skill"])) as persona:
            proc = subprocess.run([sys.executable, str(CLI), "validate", str(persona)],
                                  capture_output=True, text=True, encoding="utf-8")
        lines = [line for line in proc.stdout.splitlines() if "tasks.C3.starts_from" in line]
        self.assertEqual(len(lines), 1, proc.stdout)
        self.assertTrue(lines[0].startswith("card:tasks.C3.starts_from: "), lines[0])
        self.assertTrue(lines[0].endswith("Next: " + FIX), lines[0])
        self.assertNotEqual(proc.returncode, 0)

    def test_it_changes_no_levelling_decision_and_no_completeness(self):
        plain = validate(TEAM)
        changed = validate(TEAM, starts("C3", ["draft-response"]))
        self.assertEqual(plain["completeness"], changed["completeness"])
        with Copy(TEAM) as persona:
            before = L.level(str(persona))["levelled"]["tasks"]
        with Copy(TEAM, starts("C3", ["draft-response"])) as persona:
            after = L.level(str(persona))["levelled"]["tasks"]
        self.assertEqual(before, after)


class PackSuggestionTest(unittest.TestCase):
    def test_every_suggestion_names_a_starting_point(self):
        general = pack("general")
        for pack_id in P.list_packs():
            data = pack(pack_id)
            for entry in data["typical_tasks"]:
                for name in entry.get("starts_from", []):
                    found = P.find_starting_point(name, data, general)
                    self.assertIsNotNone(found, "%s %s: %s" % (pack_id, entry["id"], name))
                    self.assertIn(found["use"], ("start-from", "reuse"), "%s %s: %s" % (pack_id, entry["id"], name))

    def test_the_supported_suggestions(self):
        got = dict((p, dict((t["id"], t.get("starts_from")) for t in pack(p)["typical_tasks"]))
                   for p in ("private-equity", "b2b-software"))
        self.assertEqual(got["private-equity"], {"T1": None, "T2": None, "T4": ["deal-screening"],
                                                 "T5": ["dd-meeting-prep"], "T6": ["ic-memo"]})
        self.assertEqual(got["b2b-software"], {"C1": None, "C2": None, "C3": ["draft-response"],
                                               "C4": ["draft-response"], "C5": ["customer-escalation"]})

    def test_a_bad_suggestion_is_a_pack_problem(self):
        data = pack("b2b-software")
        data["typical_tasks"][0]["starts_from"] = ["no-such-skill", "sales"]
        paths = [p["path"] for p in P.pack_problems(data)]
        self.assertIn("typical_tasks[0].starts_from[0]", paths)
        self.assertIn("typical_tasks[0].starts_from[1]", paths)


# --- The skill task ------------------------------------------------------------------------------------

class SkillTaskTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template = next(t for t in load(LIBRARY)["templates"] if t["id"] == "write-skill")
        cls.plain, _ = build(TEAM, starts("C3", []))
        cls.one, _ = build(TEAM, starts("C3", ["draft-response"]))
        cls.several, _ = build(TEAM, starts("C3", ["draft-response", "customer-research", "pptx"]))
        cls.unverified, _ = build(TEAM, starts("C3", ["template-skill"]))

    def write_skill(self, backlog, story="S-C3"):
        return item(stories(backlog)[story], "write-skill")

    def test_one_starting_point(self):
        plain, got = self.write_skill(self.plain), self.write_skill(self.one)
        point = starting_point("b2b-software", "draft-response")
        self.assertEqual(got["id"], "S-C3.write-skill")
        self.assertEqual(got["title"], "Write the skill from draft-response until the evals pass")
        self.assertEqual(got["how"][0], {"text": "Start from draft-response (%s): Adapt, for C3 and C4." % point["where"],
                                         "link": point["cite"]})
        self.assertEqual(got["how"][1:], plain["how"])
        self.assertNotIn(UNVERIFIED, got["how"][0]["text"])

    def test_several_starting_points(self):
        plain, got = self.write_skill(self.plain), self.write_skill(self.several)
        self.assertEqual(got["title"], "Write the skill from draft-response and 2 more until the evals pass")
        self.assertEqual([s["link"] for s in got["how"][:3]],
                         [starting_point("b2b-software", "draft-response")["cite"],
                          starting_point("b2b-software", "customer-research")["cite"],
                          starting_point("general", "pptx")["cite"]])
        self.assertTrue(got["how"][1]["text"].startswith("Start from customer-research ("))
        self.assertTrue(got["how"][2]["text"].startswith("Start from pptx ("))
        self.assertEqual(got["how"][3:], plain["how"])
        for step in got["how"][:3]:
            self.assertTrue(step["text"].endswith("."), step["text"])

    def test_an_unverified_starting_point_carries_the_marker(self):
        point = starting_point("general", "template-skill")
        self.assertTrue(point["unverified"])
        step = self.write_skill(self.unverified)["how"][0]
        self.assertTrue(step["text"].startswith("Start from template-skill (%s): Adopt." % point["where"]), step)
        self.assertIn(UNVERIFIED, step["text"])
        self.assertTrue(step["text"].endswith("."), step["text"])
        self.assertEqual(step["link"], point["cite"])

    def test_a_task_without_starts_from_is_unchanged(self):
        for backlog in (self.plain, self.one):
            got = self.write_skill(backlog, "S-C2")
            self.assertEqual(got["title"], self.template["title"])
            self.assertEqual(got["how"][:len(self.template["how"])], self.template["how"])
        self.assertEqual(self.write_skill(self.plain)["title"], self.template["title"])
        self.assertEqual(self.write_skill(self.plain)["how"][:len(self.template["how"])], self.template["how"])


# --- The foundation ------------------------------------------------------------------------------------

class FoundationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pe, cls.pe_md = build(PE)
        cls.team, cls.team_md = build(TEAM)
        cls.pe_profile = load(PE.parent.parent / "customer-profile.json")
        cls.team_profile = load(TEAM.parent.parent / "customer-profile.json")

    def test_providers_for_a_pack_with_providers(self):
        story = stories(self.pe)["S-connectors-and-identity"]
        providers = pack("private-equity")["data_providers"]
        self.assertTrue(providers)
        want = [dict((k, p[k]) for k in ("name", "kind", "access", "note", "cite", "unverified")) for p in providers]
        self.assertEqual(story.get("data_providers"), want)
        self.assertIn(PROVIDERS_HEADING, self.pe_md)
        for p in providers:
            self.assertIn(p["name"], self.pe_md)
        decide = item(story, "data-providers-decide")
        self.assertIsNotNone(decide)
        self.assertEqual((decide["id"], decide["owner_role"], decide["part"]),
                         ("S-connectors-and-identity.data-providers-decide", "compliance", "A3"))
        links = [s["link"] for s in decide["how"]]
        self.assertTrue(1 <= len(links) <= 3, links)
        self.assertNotIn(None, links)
        self.assertEqual(set(links), set(p["cite"] for p in providers))

    def test_no_providers_for_a_pack_without(self):
        self.assertEqual(pack("b2b-software")["data_providers"], [])
        story = stories(self.team)["S-connectors-and-identity"]
        self.assertNotIn("data_providers", story)
        self.assertIsNone(item(story, "data-providers-decide"))
        self.assertNotIn(PROVIDERS_HEADING, self.team_md)

    def test_retention_and_feedback(self):
        for backlog in (self.pe, self.team):
            got = item(stories(backlog)["S-guardrails-and-settings"], "retention-and-feedback-settings")
            self.assertIsNotNone(got)
            self.assertEqual((got["owner_role"], got["part"]), ("technical-owner", "A7"))
            links = [s["link"] for s in got["how"]]
            self.assertIn("docs/compendium/15-governance-and-performance.md#retention-decided", links)
            self.assertTrue([l for l in links if l and l.startswith("docs/compendium/10-sensitive-data.md#")], links)

    def test_spend_limits(self):
        for backlog, profile in ((self.pe, self.pe_profile), (self.team, self.team_profile)):
            got = item(stories(backlog)["S-guardrails-and-settings"], "spend-limits")
            self.assertIsNotNone(got)
            self.assertEqual((got["owner_role"], got["part"]), ("technical-owner", "A9"))
            self.assertEqual(got["owner_name"], profile["governance"]["spend_owner"])
            self.assertIsNone(got["acting_owner"])
            self.assertIn("docs/compendium/09-plans-and-it-controls.md#spend-and-usage-limits", [s["link"] for s in got["how"]])

    def test_spend_limits_without_a_spend_owner(self):
        def change(profile, card):
            profile["governance"]["spend_owner"] = None
            profile["provenance"]["governance.spend_owner"] = {
                "status": "open", "source": "discovery.md#G1", "owner": "Test owner", "due": "2026-12-11"}
        backlog, _ = build(TEAM, change)
        got = item(stories(backlog)["S-guardrails-and-settings"], "spend-limits")
        self.assertEqual(got["owner_name"], self.team_profile["owners"]["technical_owner"])


# --- Completeness ---------------------------------------------------------------------------------------

class RequiredWhenTest(unittest.TestCase):
    def test_pilot_gaps_count_against_completeness(self):
        result = validate(PE)
        self.assertTrue(result["ok"], result["errors"])
        missing = result["completeness"]["missing"]
        for path in ("tasks.T1.examples.good", "tasks.T1.examples.bad",
                     "tasks.T2.examples.good", "tasks.T2.examples.bad"):
            self.assertIn("card:" + path, missing)
        self.assertNotIn("card:tasks.T3.skill_owner", missing)
        self.assertNotIn("card:tasks.T3.examples.good", missing)

    def test_answered_pilot_fields_are_counted(self):
        plain = validate(TEAM)

        def out_of_pilot(profile, card):
            task(card, "C1")["in_pilot"] = False
        fewer = validate(TEAM, out_of_pilot)
        self.assertTrue(plain["ok"] and fewer["ok"], plain["errors"] + fewer["errors"])
        self.assertEqual(plain["completeness"]["percent"], 100)
        self.assertEqual(plain["completeness"]["required"] - fewer["completeness"]["required"], 3)

    def test_a_pilot_task_with_no_skill_owner_is_an_error(self):
        def change(profile, card):
            task(card, "C1")["skill_owner"] = ""
            del card["provenance"]["tasks.C1.skill_owner"]
        result = validate(TEAM, change)
        self.assertTrue(errors_at(result, "tasks.C1.skill_owner"), result["errors"])

    def test_the_same_gap_outside_the_pilot_is_not(self):
        def change(profile, card):
            task(card, "C2")["skill_owner"] = ""
            del card["provenance"]["tasks.C2.skill_owner"]
            task(card, "C2")["examples"]["good"] = None
            del card["provenance"]["tasks.C2.examples.good"]
        result = validate(TEAM, change)
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual(result["completeness"]["percent"], 100)

    def test_an_open_gap_with_an_owner_lowers_completeness(self):
        def change(profile, card):
            task(card, "C4")["examples"]["bad"] = None
            card["provenance"]["tasks.C4.examples.bad"] = {
                "status": "open", "source": "interviews/2026-11-06-csm.md#F3", "owner": "Test owner",
                "due": "2026-12-11"}
        result = validate(TEAM, change)
        self.assertTrue(result["ok"], result["errors"])
        self.assertIn("card:tasks.C4.examples.bad", result["completeness"]["missing"])
        self.assertLess(result["completeness"]["percent"], 100)

    def test_an_answered_zero_is_a_value(self):
        def change(profile, card):
            task(card, "C4")["examples"]["bad"] = 0
        result = validate(TEAM, change)
        self.assertTrue(result["ok"], result["errors"])
        self.assertNotIn("card:tasks.C4.examples.bad", result["completeness"]["missing"])
        self.assertEqual(result["completeness"]["percent"], 100)

    def test_the_design_states_the_rule(self):
        text = DESIGN.read_text(encoding="utf-8")
        self.assertIn("required_when", text)
        self.assertIn("names its skill owner and says how many examples exist", text)
        self.assertIn("## What the generator does not produce", text)
        self.assertIn("starts_from", text)
        self.assertIn("data-providers-decide", text)


# --- The committed worked examples ----------------------------------------------------------------------

class SamplesTest(unittest.TestCase):
    def test_samples_set_the_supported_starting_points(self):
        pe = dict((t["id"], t.get("starts_from")) for t in load(PE / "card.json")["tasks"])
        team = dict((t["id"], t.get("starts_from")) for t in load(TEAM / "card.json")["tasks"])
        self.assertEqual((pe["T4"], pe["T5"], pe["T6"]), (["deal-screening"], ["dd-meeting-prep"], ["ic-memo"]))
        self.assertEqual((team["C3"], team["C4"], team["C5"]),
                         (["draft-response"], ["draft-response"], ["customer-escalation"]))
        backlog = load(PE / "backlog.json")
        self.assertEqual(item(stories(backlog)["S-T4"], "write-skill")["title"],
                         "Write the skill from deal-screening until the evals pass")

    def test_committed_samples_match_a_fresh_run(self):
        for persona_dir in (PE, TEAM):
            with tempfile.TemporaryDirectory() as tmp:
                engagement = persona_dir.parent.parent
                root = Path(tmp) / engagement.name
                persona = root / "personas" / persona_dir.name
                persona.mkdir(parents=True)
                for entry in engagement.iterdir():
                    if entry.is_file():
                        shutil.copy2(entry, root / entry.name)
                shutil.copy2(persona_dir / "card.json", persona / "card.json")
                shutil.copytree(persona_dir / "interviews", persona / "interviews")
                runs = []
                for _ in range(2):
                    proc = subprocess.run([sys.executable, str(CLI), "all", str(persona), "--date", DATE],
                                          capture_output=True, text=True, encoding="utf-8")
                    self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                    runs.append(dict((name, (persona / name).read_bytes()) for name in GENERATED))
                self.assertEqual(runs[0], runs[1], "%s: a second run is not byte-identical" % persona_dir.name)
                for name in GENERATED:
                    self.assertEqual(runs[0][name], (persona_dir / name).read_bytes(),
                                     "%s/%s is stale; run cli.py all %s --date %s"
                                     % (persona_dir.name, name, persona_dir.relative_to(ROOT), DATE))


if __name__ == "__main__":
    unittest.main()
