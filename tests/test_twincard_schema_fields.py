"""Schema fields added by OPS-53: ZDR cover on the profile, constraints, wanted change and wanted surfaces.

compliance.zdr_cover says whether a zero-data-retention agreement covers the org the highly sensitive work
runs in: none raises the highly-sensitive-needs-zdr-org blocker, planned or open raises the
zdr-org-not-confirmed warning, in-place raises neither. tasks[].constraints and tasks[].wanted_change reach
the backlog story and the dashboard's task panel; role.wanted_surfaces shows in the A4 panel. None of the
three card fields changes levelling.

Every fixture here is fictional and is copied to a temporary folder before it is changed.
Standard library only. Run with: python3 -m unittest discover -s tests
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
TEMPLATES = PLUGIN_DIR / "templates"
PE_ROOT = ROOT / "engagements" / "sample-pe"
PE_PERSONA = Path("personas") / "deal-team-associate"
BROKER_ROOT = ROOT / "tests" / "fixtures" / "twincard" / "sample-insurance-broker"
BROKER_PERSONA = Path("personas") / "claims-handler"
DATE = "2026-11-15"

BLOCKER = "highly-sensitive-needs-zdr-org"
WARNING = "zdr-org-not-confirmed"
STORY_FIELD_KEYS = ["data_class", "surface", "autonomy", "connectors_and_identity", "wall_impact", "inputs",
                    "output_and_audience", "skill_owner", "baseline"]

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from twincard import backlog as B  # noqa: E402
from twincard import dashboard as D  # noqa: E402
from twincard import fields as F  # noqa: E402
from twincard import level as L  # noqa: E402


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dump(path, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


class Copy(object):
    """A temporary copy of a fictional engagement, with helpers to change its card and profile."""

    def __init__(self, test, source, persona):
        tmp = tempfile.TemporaryDirectory()
        test.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name) / source.name
        shutil.copytree(source, self.root)
        self.persona = self.root / persona
        self.card_path = self.persona / "card.json"
        self.profile_path = self.root / "customer-profile.json"

    def card(self, change):
        data = load(self.card_path)
        change(data)
        dump(self.card_path, data)

    def profile(self, change):
        data = load(self.profile_path)
        change(data)
        dump(self.profile_path, data)

    def zdr_cover(self, value, status="answered"):
        def change(profile):
            profile["compliance"]["zdr_cover"] = value
            entry = {"status": status, "source": "discovery.md#C3"}
            if status in ("assumed", "open"):
                entry.update({"owner": "Compliance / legal"})
            if status == "open":
                entry.update({"due": "2026-12-04"})
            profile["provenance"]["compliance.zdr_cover"] = entry
        self.profile(change)

    def run(self, test):
        """Level, build the backlog and render the page in memory; return (levelled, backlog, md, page)."""
        result = L.level(str(self.persona))
        test.assertTrue(result["ok"], "does not validate: %s" % (result["validation"]["errors"],))
        card, profile = load(self.card_path), load(self.profile_path)
        built = B.assemble(self.persona, result["validation"], card, profile, result["levelled"])
        test.assertTrue(built["ok"], built.get("error"))
        inputs = {"card": card, "profile": profile, "levelled": result["levelled"], "backlog": built["backlog"],
                  "validation": result["validation"], "catalogue": F.load_catalogue()}
        page, _ = D.build_page(inputs, D.parse_date(DATE))
        return result["levelled"], built["backlog"], B.render_md(built["backlog"], self.persona), page


def about(levelled, kind, code):
    return set(item["about"] for item in levelled[kind] if item["code"] == code)


def stories(backlog):
    return dict((story["id"], story) for feature in backlog["epic"]["features"] for story in feature["stories"])


def highly_sensitive(card_path):
    return set(t["id"] for t in load(card_path)["tasks"] if t.get("data_class") == "highly-sensitive")


def set_task_fields(tid, constraints=None, wanted_change=None):
    def change(card):
        task = next(t for t in card["tasks"] if t["id"] == tid)
        for key, value in (("constraints", constraints), ("wanted_change", wanted_change)):
            path = "tasks.%s.%s" % (tid, key)
            if value is None:
                task.pop(key, None)
                card["provenance"].pop(path, None)
            else:
                task[key] = value
                card["provenance"][path] = {"status": "assumed", "source": "interviews/2026-11-12-associate.md#F4",
                                            "owner": "Callum Nwosu"}
    return change


def strip_new_card_fields(card):
    card["role"].pop("wanted_surfaces", None)
    card["provenance"].pop("role.wanted_surfaces", None)
    for task in card["tasks"]:
        for key in ("constraints", "wanted_change"):
            task.pop(key, None)
            card["provenance"].pop("tasks.%s.%s" % (task["id"], key), None)


class CatalogueTests(unittest.TestCase):
    def setUp(self):
        self.entries = dict(((e["record"], e["path"]), e) for e in F.load_catalogue()["fields"])

    def test_zdr_cover_is_a_required_profile_enum_asked_at_c3(self):
        entry = self.entries[("profile", "compliance.zdr_cover")]
        self.assertEqual(entry["type"], "enum")
        self.assertEqual(entry["values"], ["in-place", "planned", "none"])
        self.assertIs(entry["required"], True)
        self.assertIsNone(entry["default"])
        self.assertEqual(entry["asked_by"], ["C3"])
        self.assertEqual(entry["part"], "A7")

    def test_three_optional_card_fields(self):
        constraints = self.entries[("card", "tasks[].constraints")]
        self.assertEqual((constraints["type"], constraints["required"]), ("string-list", False))
        wanted = self.entries[("card", "tasks[].wanted_change")]
        self.assertEqual((wanted["type"], wanted["required"]), ("string", False))
        surfaces = self.entries[("card", "role.wanted_surfaces")]
        works_in = self.entries[("card", "role.works_in")]
        self.assertEqual((surfaces["type"], surfaces["required"]), ("enum-list", False))
        self.assertEqual(surfaces["values"], works_in["values"])
        for entry in (constraints, wanted, surfaces):
            self.assertTrue(entry["asked_by"], entry["path"])
            self.assertFalse([f for f in entry["feeds"] if f.startswith("rule:")], entry["path"])

    def test_templates_carry_the_new_fields_empty(self):
        card = load(TEMPLATES / "card.json")
        profile = load(TEMPLATES / "customer-profile.json")
        self.assertEqual(profile["compliance"]["zdr_cover"], "")
        self.assertEqual(card["role"]["wanted_surfaces"], [])
        self.assertEqual(card["tasks"][0]["constraints"], [])
        self.assertEqual(card["tasks"][0]["wanted_change"], "")


class OpenMatchTests(unittest.TestCase):
    def test_an_open_fact_matches_a_null_want(self):
        facts = {"x": L.Open("profile", "x")}
        self.assertTrue(L.matches({"x": ["planned", None]}, facts))
        self.assertTrue(L.matches({"x": None}, facts))

    def test_an_open_fact_still_raises_when_null_is_not_wanted(self):
        with self.assertRaises(L.FactOpen):
            L.matches({"x": ["planned"]}, {"x": L.Open("profile", "x")})


class ZdrCoverTests(unittest.TestCase):
    """The PE sample is on Enterprise, so only the cover decides the outcome for its highly sensitive tasks."""

    def outcome(self, value, status="answered"):
        copy = Copy(self, PE_ROOT, PE_PERSONA)
        copy.zdr_cover(value, status)
        levelled = L.level(str(copy.persona))
        self.assertTrue(levelled["ok"], levelled["validation"]["errors"])
        hs = highly_sensitive(copy.card_path)
        self.assertTrue(hs)
        return levelled["levelled"], hs

    def test_none_raises_the_blocker(self):
        levelled, hs = self.outcome("none")
        self.assertEqual(about(levelled, "blockers", BLOCKER), hs)
        blocker = next(b for b in levelled["blockers"] if b["code"] == BLOCKER)
        self.assertIn("compliance.zdr_cover", blocker["message"])

    def test_planned_raises_the_warning_and_no_blocker(self):
        levelled, hs = self.outcome("planned", "assumed")
        self.assertEqual(about(levelled, "warnings", WARNING), hs)
        self.assertFalse(about(levelled, "blockers", BLOCKER))
        warning = next(w for w in levelled["warnings"] if w["code"] == WARNING)
        self.assertIn("compliance.zdr_cover", warning["message"])

    def test_open_raises_the_warning_and_no_blocker(self):
        levelled, hs = self.outcome("", "open")
        self.assertEqual(about(levelled, "warnings", WARNING), hs)
        self.assertFalse(about(levelled, "blockers", BLOCKER))

    def test_in_place_raises_neither(self):
        levelled, _ = self.outcome("in-place")
        self.assertFalse(about(levelled, "warnings", WARNING))
        self.assertFalse(about(levelled, "blockers", BLOCKER))

    def test_the_warning_no_longer_reads_retention(self):
        rule = next(r for r in L.load_rules()["rules"] if r["id"] == "warn-zdr-org-not-confirmed")
        self.assertNotIn("compliance.retention", L.fact_names(rule["when"]))
        self.assertIn("compliance.zdr_cover", L.fact_names(rule["when"]))

    def test_the_pe_sample_keeps_the_warning_and_gains_no_blocker(self):
        result = L.level(str(PE_ROOT / PE_PERSONA))
        self.assertTrue(result["ok"], result["validation"]["errors"])
        self.assertEqual(load(PE_ROOT / "customer-profile.json")["compliance"]["zdr_cover"], "planned")
        self.assertEqual(about(result["levelled"], "warnings", WARNING), highly_sensitive(PE_ROOT / PE_PERSONA /
                                                                                           "card.json"))
        self.assertFalse(about(result["levelled"], "blockers", BLOCKER))


class ConstraintTests(unittest.TestCase):
    def setUp(self):
        self.copy = Copy(self, PE_ROOT, PE_PERSONA)
        self.copy.card(set_task_fields("T1", ["Reply within <b>24 hours</b>", "A reviewer checks every brief"],
                                       "Start it when the meeting is booked & <i>not</i> later"))
        self.levelled, self.backlog, self.md, self.page = self.copy.run(self)
        self.story = stories(self.backlog)["S-T1"]

    def test_backlog_json_story_fields(self):
        fields = self.story["fields"]
        self.assertEqual(fields["constraints"], ["Reply within <b>24 hours</b>", "A reviewer checks every brief"])
        self.assertEqual(fields["wanted_change"],
                         "Asked for, not planned: Start it when the meeting is booked & <i>not</i> later")

    def test_acceptance_keeps_each_constraint(self):
        keeps = [line for line in self.story["acceptance"] if line.startswith("Keeps: ")]
        self.assertEqual(keeps, ["Keeps: Reply within <b>24 hours</b>", "Keeps: A reviewer checks every brief"])
        plus = [i for i, line in enumerate(self.story["acceptance"]) if line.startswith("Plus: ")]
        last_keep = max(i for i, line in enumerate(self.story["acceptance"]) if line.startswith("Keeps: "))
        self.assertTrue(all(i > last_keep for i in plus))

    def test_write_skill_lists_the_constraints(self):
        task = next(t for t in self.story["tasks"] if t["template"] == "write-skill")
        text = " ".join([s["text"] for s in task["how"]] + [task["done_when"]])
        self.assertIn("Reply within <b>24 hours</b>", text)
        self.assertIn("A reviewer checks every brief", text)

    def test_a_wanted_change_creates_no_task(self):
        plain = Copy(self, PE_ROOT, PE_PERSONA)
        plain.card(set_task_fields("T1", ["Reply within <b>24 hours</b>", "A reviewer checks every brief"], None))
        _, backlog, _, _ = plain.run(self)
        self.assertEqual([t["id"] for t in stories(backlog)["S-T1"]["tasks"]],
                         [t["id"] for t in self.story["tasks"]])

    def test_backlog_md(self):
        self.assertIn("| Constraints | Reply within &lt;b>24 hours&lt;/b>; A reviewer checks every brief |", self.md)
        self.assertIn("| Wanted change | Asked for, not planned: Start it when the meeting is booked & &lt;i>not"
                      "&lt;/i> later |", self.md)
        self.assertIn("Keeps: Reply within &lt;b>24 hours&lt;/b>", self.md)

    def test_dashboard_shows_them_escaped(self):
        self.assertIn('data-field="T1.constraints"', self.page)
        self.assertIn("<li>Reply within &lt;b&gt;24 hours&lt;/b&gt;</li>", self.page)
        self.assertNotIn("<b>24 hours</b>", self.page)
        self.assertIn('data-field="T1.wanted_change"', self.page)
        self.assertIn("Start it when the meeting is booked &amp; &lt;i&gt;not&lt;/i&gt; later", self.page)
        self.assertNotIn("<script", self.page)

    def test_they_never_change_levelling(self):
        plain = Copy(self, PE_ROOT, PE_PERSONA)
        plain.card(strip_new_card_fields)
        levelled = L.level(str(plain.persona))["levelled"]
        for key in ("tasks", "tools", "persona_plan", "blockers", "warnings"):
            self.assertEqual(levelled[key], self.levelled[key], key)


class WithoutNewFieldsTests(unittest.TestCase):
    def test_a_card_without_the_new_fields_validates_and_renders_as_before(self):
        copy = Copy(self, PE_ROOT, PE_PERSONA)
        copy.card(strip_new_card_fields)
        _, backlog, md, page = copy.run(self)
        for story_id, story in stories(backlog).items():
            if story_id.startswith("S-T"):
                self.assertEqual(list(story["fields"]), STORY_FIELD_KEYS, story_id)
                self.assertFalse([a for a in story["acceptance"] if a.startswith("Keeps: ")], story_id)
        self.assertNotIn("| Constraints |", md)
        self.assertNotIn("| Wanted change |", md)
        self.assertNotIn(".constraints\"", page)
        self.assertNotIn(".wanted_change\"", page)
        self.assertNotIn('data-field="role.wanted_surfaces"', page)


class WantedSurfaceTests(unittest.TestCase):
    def page_with(self, surfaces):
        copy = Copy(self, PE_ROOT, PE_PERSONA)

        def change(card):
            card["role"].pop("wanted_surfaces", None)
            card["provenance"].pop("role.wanted_surfaces", None)
            if surfaces is not None:
                card["role"]["wanted_surfaces"] = surfaces
                card["provenance"]["role.wanted_surfaces"] = {
                    "status": "answered", "source": "interviews/2026-11-12-associate.md#P1"}
        copy.card(change)
        return copy.run(self)

    def test_shown_beside_the_planned_surfaces_as_a_wish(self):
        _, _, _, page = self.page_with(["teams"])
        start = page.index('data-field="role.wanted_surfaces"')
        works = page.index("<dt>Works in</dt>")
        self.assertLess(works, start)
        self.assertIn("teams (a wish, not planned)", page[start:start + 400])

    def test_not_shown_when_absent_or_empty(self):
        for surfaces in (None, []):
            _, _, _, page = self.page_with(surfaces)
            self.assertNotIn('data-field="role.wanted_surfaces"', page, surfaces)

    def test_never_changes_levelling(self):
        with_wish, _, _, _ = self.page_with(["teams", "slack"])
        without, _, _, _ = self.page_with(None)
        for key in ("tasks", "tools", "persona_plan", "blockers", "warnings"):
            self.assertEqual(with_wish[key], without[key], key)


class BrokerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = load(BROKER_ROOT / "customer-profile.json")
        cls.card = load(BROKER_ROOT / BROKER_PERSONA / "card.json")

    def setUp(self):
        copy = Copy(self, BROKER_ROOT, BROKER_PERSONA)
        self.levelled, self.backlog, self.md, self.page = copy.run(self)

    def test_no_zdr_cover_blocks_the_highly_sensitive_task(self):
        self.assertEqual(self.profile["compliance"]["zdr_cover"], "none")
        self.assertIn("T3", highly_sensitive(BROKER_ROOT / BROKER_PERSONA / "card.json"))
        self.assertIn("T3", about(self.levelled, "blockers", BLOCKER))
        self.assertNotIn("T3", about(self.levelled, "warnings", WARNING))

    def test_constraints_and_wishes_are_on_the_card(self):
        tasks = dict((t["id"], t) for t in self.card["tasks"])
        self.assertTrue(any("24 hours" in c for c in tasks["T1"].get("constraints") or []))
        self.assertTrue(any("vulnerable" in c for t in tasks.values() for c in t.get("constraints") or []))
        self.assertIn("fourteen days", tasks["T4"].get("wanted_change") or "")
        self.assertEqual(self.card["role"].get("wanted_surfaces"), ["teams"])

    def test_constraints_reach_the_backlog_story_and_the_dashboard(self):
        story = stories(self.backlog)["S-T1"]
        constraint = next(c for c in story["fields"]["constraints"] if "24 hours" in c)
        self.assertIn("Keeps: " + constraint, story["acceptance"])
        self.assertIn('data-field="T1.constraints"', self.page)
        self.assertIn(D.esc(constraint), self.page)
        self.assertIn('data-field="T4.wanted_change"', self.page)
        self.assertIn('data-field="role.wanted_surfaces"', self.page)


if __name__ == "__main__":
    unittest.main()
