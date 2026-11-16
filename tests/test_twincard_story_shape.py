"""Every generated task story reads as the playbook's story template (OPS-56).

docs/playbook/04-stories.md gives a story a statement ("As a <role>, I want my twin to <task> so that
<outcome>"), acceptance criteria that are evals, a target line, a definition of ready and a definition of
done; and an open question is a spike. This file checks the backlog the kit generates against that:

- the statement is built from the card's story_want and story_benefit, with the fallbacks of design
  section 8 when either is empty, and statement_source says which;
- the target line, set from outcome.scorecard_targets or saying it is not set;
- the one "To write:" acceptance line when a task has no counted examples, and the trigger line on
  client skills only;
- the four ready checks, the compliance sign-off task and gate above "confidential", owner-handover;
- spikes: one per open question, the stories each blocks, statuses kept and retired;
- both committed samples are what a fresh run gives.

Standard library only. Anything the tests write goes to a temporary folder.
Run with: python3 -m unittest discover -s tests
"""

import json
import re
import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

import test_twincard_backlog as BT  # noqa: E402
import test_twincard_backlog_consistency as TC  # noqa: E402

from twincard import validate as V  # noqa: E402

B, L, F = BT.B, BT.L, BT.F
PE, TEAM, ROOT = BT.PE, BT.TEAM, BT.ROOT
PLAYBOOK = ROOT / "docs" / "playbook" / "04-stories.md"
CARD_TEMPLATE = BT.PLUGIN_DIR / "templates" / "card.json"
DRAFTED_LINE = "(Statement drafted by the kit: confirm the wording with the interviewee.)"
NOT_SET = "Target: not set. Agree the scorecard targets with the sponsor before the pilot starts."
TRIGGER_LINE = "Plus: the skill triggers on the phrases its trigger evals list and stays quiet on the near-misses."
READY_CHECKS = ["fields", "examples", "connectors"]
ABOVE_CONFIDENTIAL = ("highly-sensitive", "phi")
SIGN_OFF_LINK = "docs/playbook/04-stories.md#definition-of-ready-before-building"
STATEMENT = re.compile(r"^As an? (?P<role>.+?), I want my twin to (?P<want>.+) so that (?P<benefit>.+)\.$")


def load(path):
    return BT.load(path)


def stories(backlog):
    return dict((s["id"], s) for s in BT.stories_of(backlog))


def task_stories(backlog, card):
    ids = set("S-" + t["id"] for t in card["tasks"])
    return [s for s in BT.stories_of(backlog) if s["id"] in ids]


def card_task(card, tid):
    return BT.task(card, tid)


def lower_first(text):
    return text[:1].lower() + text[1:]


def build(persona):
    result = B.build(str(persona))
    if not result["ok"]:
        raise AssertionError(result["error"])
    return result["backlog"]


def build_in(persona_dir, change=None):
    """(card, backlog, markdown) for a changed temporary copy of a fixture."""
    with BT.Scenario(persona_dir, change) as persona:
        backlog = build(persona)
        return load(persona / "card.json"), backlog, B.render_md(backlog, persona)


def variant(variant_id):
    exp = load(BT.EXPECTATIONS)
    found = next(v for v in exp["variants"] if v["id"] == variant_id)
    return ROOT / exp["fixtures"][found["base"]]["persona_dir"], BT.variant_change(found, F.load_catalogue())


def edit_backlog(persona, statuses):
    """Set statuses in backlog.json by id, for a task or a spike."""
    path = persona / "backlog.json"
    data = load(path)
    for story in BT.stories_of(data):
        for item in story["tasks"]:
            if item["id"] in statuses:
                item["status"] = statuses[item["id"]]
    for spike in data.get("spikes") or []:
        if spike["id"] in statuses:
            spike["status"] = statuses[spike["id"]]
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def rewrite_card(persona, change):
    card = load(persona / "card.json")
    change(card)
    (persona / "card.json").write_text(json.dumps(card, indent=2), encoding="utf-8")
    result = L.write_levelled(str(persona))
    if not result["ok"]:
        raise AssertionError(result["validation"]["errors"])


def open_field(tid, field, value, source):
    def change(profile, card):
        item = card_task(card, tid)
        node, key = item, field
        if "." in field:
            head, key = field.split(".", 1)
            node = item[head]
        node[key] = value
        card["provenance"]["tasks.%s.%s" % (tid, field)] = {
            "status": "open", "source": source, "owner": "Test owner", "due": "2026-12-11"}
    return change


def chain(*changes):
    def change(profile, card):
        for item in changes:
            item(profile, card)
    return change


class SampleCache(object):
    _built = None

    @classmethod
    def get(cls):
        if cls._built is None:
            cls._built = {}
            for key, persona in (("pe", PE), ("team", TEAM)):
                backlog = build(persona)
                cls._built[key] = (load(persona / "card.json"), backlog, B.render_md(backlog, persona))
        return cls._built


# --- The card fields ------------------------------------------------------------------------------

class CardFieldTests(unittest.TestCase):
    def test_catalogue_entries(self):
        entries = dict((e["path"], e) for e in F.load_catalogue()["fields"] if e["record"] == "card")
        for path, asked in (("tasks[].story_want", ["F1"]), ("tasks[].story_benefit", ["F1", "F3"])):
            with self.subTest(path=path):
                entry = entries[path]
                self.assertEqual(entry["type"], "string")
                self.assertFalse(entry["required"])
                self.assertFalse(entry["key"])
                self.assertEqual(entry["part"], "A2")
                self.assertEqual(entry["asked_by"], asked)
                self.assertIn("backlog:story", entry["feeds"])
                self.assertFalse([f for f in entry["feeds"] if f.startswith("rule:")])

    def test_card_template_carries_them_empty(self):
        item = load(CARD_TEMPLATE)["tasks"][0]
        self.assertEqual(item["story_want"], "")
        self.assertEqual(item["story_benefit"], "")

    def test_they_change_no_levelling_decision_or_completeness(self):
        def fill(profile, card):
            for item in card["tasks"]:
                item["story_want"] = "do something invented for a test"
                item["story_benefit"] = "an invented benefit holds"

        def plan(persona):
            levelled = load(persona / "levelled.json")
            levelled.pop("source")
            return levelled

        catalogue = F.load_catalogue()
        with BT.Scenario(PE) as persona:
            before, completeness = plan(persona), V.validate(str(persona), catalogue)["completeness"]
        with BT.Scenario(PE, fill) as persona:
            self.assertEqual(plan(persona), before)
            self.assertEqual(V.validate(str(persona), catalogue)["completeness"], completeness)


# --- The statement --------------------------------------------------------------------------------

class StatementTests(unittest.TestCase):
    def test_from_the_card(self):
        card, backlog, md = SampleCache.get()["team"]
        story = stories(backlog)["S-C1"]
        self.assertEqual(story["statement"],
                         "As a customer success manager, I want my twin to brief me on the account before each "
                         "call so that I walk into the call already knowing the account.")
        self.assertEqual(story["statement_source"], "card")
        for item in card["tasks"]:
            with self.subTest(task=item["id"]):
                story = stories(backlog)["S-" + item["id"]]
                self.assertEqual(story["statement"], "As a %s, I want my twin to %s so that %s." % (
                    lower_first(card["role"]["name"]), item["story_want"], item["story_benefit"]))
                self.assertEqual(story["statement_source"], "card")
        self.assertNotIn(DRAFTED_LINE, md)

    def test_fallback_from_the_output_and_the_minutes(self):
        card, backlog, md = SampleCache.get()["pe"]
        t6 = card_task(card, "T6")
        self.assertEqual((t6["story_want"], t6["story_benefit"]), ("", ""))
        story = stories(backlog)["S-T6"]
        self.assertEqual(story["statement"],
                         "As a deal-team associate, I want my twin to produce the draft memo section so that I get "
                         "back the 240 minutes it takes me each time.")
        self.assertEqual(story["statement_source"], "drafted")
        self.assertIn("\n\n%s\n\n%s\n" % (story["statement"], DRAFTED_LINE), md)
        for tid in ("T1", "T2", "T3", "T4", "T5"):
            with self.subTest(task=tid):
                self.assertEqual(stories(backlog)["S-" + tid]["statement_source"], "card")

    def test_fallback_from_the_task_name_and_no_minutes(self):
        change = chain(open_field("T6", "output.what", "", "interviews/2026-11-10-partner.md#F2"),
                       open_field("T6", "minutes_each", None, "interviews/2026-11-10-partner.md#F1"))
        card, backlog, _ = build_in(PE, change)
        story = stories(backlog)["S-T6"]
        self.assertEqual(story["statement"],
                         'As a deal-team associate, I want my twin to do the task "%s" so that I do not have to do '
                         'it by hand.' % card_task(card, "T6")["name"])
        self.assertEqual(story["statement_source"], "drafted")

    def test_one_card_part_is_still_drafted(self):
        def want_only(profile, card):
            card_task(card, "T6")["story_want"] = "draft the memo section from the diligence notes"
        _, backlog, _ = build_in(PE, want_only)
        story = stories(backlog)["S-T6"]
        self.assertEqual(story["statement"],
                         "As a deal-team associate, I want my twin to draft the memo section from the diligence "
                         "notes so that I get back the 240 minutes it takes me each time.")
        self.assertEqual(story["statement_source"], "drafted")

    def test_every_want_part_starts_with_a_verb(self):
        """No statement in any sample or test scenario reads 'twin to <a noun phrase>'."""
        for name, _, card, _, backlog, _ in TC.Runs.get():
            for story in task_stories(backlog, card):
                with self.subTest(scenario=name, story=story["id"]):
                    match = STATEMENT.match(story["statement"])
                    self.assertTrue(match, story["statement"])
                    first = match.group("want").split()[0]
                    want = (card_task(card, story["id"][2:]).get("story_want") or "").split()
                    self.assertIn(first, want[:1] + ["produce", "do"], story["statement"])

    def test_foundation_statements_are_kept(self):
        card, backlog, _ = SampleCache.get()["pe"]
        story = stories(backlog)["S-persona-voice"]
        self.assertEqual(story["statement"], "As a Deal-team associate, I want my twin's persona voice in place so "
                                             "that every task story runs safely.")
        self.assertNotIn("statement_source", story)


# --- The target -----------------------------------------------------------------------------------

class TargetTests(unittest.TestCase):
    def test_set_from_the_scorecard_targets(self):
        card, backlog, md = SampleCache.get()["team"]
        targets = card["outcome"]["scorecard_targets"]
        self.assertEqual(len(targets), 2)
        self.assertEqual(stories(backlog)["S-C1"]["target"], {
            "text": "Target: %s: %s; %s: %s. Today: 6 per week, 30 minutes each, 8 users." % (
                targets[0]["metric"], targets[0]["value"], targets[1]["metric"], targets[1]["value"]),
            "set": True})
        for story in task_stories(backlog, card):
            with self.subTest(story=story["id"]):
                self.assertTrue(story["target"]["set"])
                self.assertIn("\n\n" + story["target"]["text"] + "\n", md)
        self.assertNotIn("Stories with no target", md)

    def test_not_set(self):
        card, backlog, md = SampleCache.get()["pe"]
        self.assertEqual(card["outcome"]["scorecard_targets"], [])
        for story in task_stories(backlog, card):
            with self.subTest(story=story["id"]):
                self.assertEqual(story["target"], {"text": NOT_SET, "set": False})
        self.assertIn("Stories with no target: 6", md)
        self.assertNotIn("target", stories(backlog)["S-persona-voice"])

    def test_target_follows_the_acceptance_lines(self):
        _, backlog, md = SampleCache.get()["pe"]
        story = stories(backlog)["S-T1"]
        last = "%d. %s" % (len(story["acceptance"]), story["acceptance"][-1])
        section = md.split("### S-T1:")[1].split("\n### ")[0]
        self.assertLess(section.index(last), section.index(NOT_SET))


# --- Acceptance -----------------------------------------------------------------------------------

class AcceptanceTests(unittest.TestCase):
    def test_one_to_write_line_without_examples(self):
        _, backlog, _ = SampleCache.get()["pe"]
        t1, t3 = stories(backlog)["S-T1"], stories(backlog)["S-T3"]
        self.assertEqual([a for a in t1["acceptance"] if a.startswith(("To write", "Eval"))],
                         ["To write: collect at least 3 real examples from Callum Nwosu and write one eval case "
                          "from each."])
        self.assertIn("To write: collect at least 3 real examples from the skill owner (not named yet) and write "
                      "one eval case from each.", t3["acceptance"])
        self.assertEqual(t1["acceptance"][0][:9], "To write:")

    def test_real_example_lines_are_kept(self):
        _, backlog, _ = SampleCache.get()["team"]
        c1 = stories(backlog)["S-C1"]
        self.assertEqual([a for a in c1["acceptance"] if a.startswith("Eval")], [
            "Eval from good example 1 of 2 (Shared drive 'CS examples' (invented)): the twin's output matches what "
            "a person accepted.",
            "Eval from good example 2 of 2 (Shared drive 'CS examples' (invented)): the twin's output matches what "
            "a person accepted.",
            "Eval from bad example 1 of 1 (Shared drive 'CS examples' (invented)): the twin does not repeat the "
            "mistake."])
        self.assertFalse([a for a in c1["acceptance"] if a.startswith("To write")])

    def test_trigger_line_only_on_client_skills(self):
        for key in ("pe", "team"):
            card, backlog, _ = SampleCache.get()[key]
            levelled = load((PE if key == "pe" else TEAM) / "levelled.json")
            for story in task_stories(backlog, card):
                runtime = levelled["tasks"][story["id"][2:]]["runtime"]["value"]
                with self.subTest(story=story["id"], runtime=runtime):
                    self.assertEqual(TRIGGER_LINE in story["acceptance"], runtime == "client-skill")
                    if runtime == "client-skill":
                        plus = [a for a in story["acceptance"] if a.startswith("Plus: ")]
                        self.assertEqual(plus[0], TRIGGER_LINE)


# --- Ready ----------------------------------------------------------------------------------------

class ReadyTests(unittest.TestCase):
    def check(self, story, name):
        return next(c for c in story["ready"] if c["check"] == name)

    def test_shape_and_order(self):
        for key in ("pe", "team"):
            card, backlog, _ = SampleCache.get()[key]
            for story in task_stories(backlog, card):
                with self.subTest(story=story["id"]):
                    data_class = card_task(card, story["id"][2:])["data_class"]
                    want = READY_CHECKS + (["compliance-sign-off"] if data_class in ABOVE_CONFIDENTIAL else [])
                    self.assertEqual([c["check"] for c in story["ready"]], want)
                    for item in story["ready"]:
                        self.assertEqual(list(item), ["check", "met", "note"])
                        self.assertIsInstance(item["met"], bool)
                        self.assertTrue(item["note"].strip())

    def test_team_c1_is_ready(self):
        _, backlog, md = SampleCache.get()["team"]
        c1 = stories(backlog)["S-C1"]
        self.assertEqual([c["met"] for c in c1["ready"]], [True, True, True])
        self.assertIn("3", self.check(c1, "examples")["note"])
        section = md.split("### S-C1:")[1].split("\n### ")[0]
        self.assertIn("\nReady to build: yes\n", section)

    def test_examples_and_sign_off_unmet(self):
        _, backlog, md = SampleCache.get()["pe"]
        t1 = stories(backlog)["S-T1"]
        self.assertTrue(self.check(t1, "fields")["met"])
        self.assertFalse(self.check(t1, "examples")["met"])
        self.assertIn("0", self.check(t1, "examples")["note"])
        self.assertFalse(self.check(t1, "compliance-sign-off")["met"])
        section = md.split("### S-T1:")[1].split("\n### ")[0]
        self.assertIn("\nReady to build: no\n", section)
        self.assertIn("- examples: %s" % self.check(t1, "examples")["note"], section)
        self.assertIn("- compliance-sign-off: %s" % self.check(t1, "compliance-sign-off")["note"], section)
        self.assertNotIn("- fields:", section)

    def test_summary_counts(self):
        for key, ready in (("pe", 0), ("team", None)):
            card, backlog, md = SampleCache.get()[key]
            told = task_stories(backlog, card)
            n = sum(1 for s in told if all(c["met"] for c in s["ready"]))
            if ready is not None:
                self.assertEqual(n, ready)
            self.assertIn("Stories ready to build: %d of %d" % (n, len(told)), md)

    def test_fields_unmet_names_the_undecided(self):
        change = open_field("C1", "data_class", "", "interviews/2026-11-06-csm.md#F2")
        _, backlog, _ = build_in(TEAM, change)
        fields = self.check(stories(backlog)["S-C1"], "fields")
        self.assertFalse(fields["met"])
        self.assertIn("data class", fields["note"])

    def test_examples_count_two_is_unmet(self):
        def two(profile, card):
            card_task(card, "C1")["examples"]["bad"] = 0
        _, backlog, _ = build_in(TEAM, two)
        examples = self.check(stories(backlog)["S-C1"], "examples")
        self.assertFalse(examples["met"])
        self.assertIn("2", examples["note"])

    def test_connectors_unmet_names_the_system(self):
        persona_dir, change = variant("team-c4-gmail-send")
        card, backlog, _ = build_in(persona_dir, change)
        connectors = self.check(stories(backlog)["S-C4"], "connectors")
        self.assertFalse(connectors["met"])
        self.assertIn("gmail", connectors["note"].lower())
        self.assertTrue(self.check(stories(backlog)["S-C1"], "connectors")["met"])


# --- Compliance sign-off and owner handover ---------------------------------------------------------

class SignOffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.templates = dict((t["id"], t) for t in B.load_library()["templates"])

    def test_template(self):
        template = self.templates["compliance-sign-off"]
        self.assertEqual((template["owner_role"], template["part"], template["applies_to"]),
                         ("compliance", "A7", "task-story"))
        self.assertEqual(template["how"][0]["link"], SIGN_OFF_LINK)
        self.assertTrue(all(step["link"] for step in template["how"]))

    def test_only_above_confidential(self):
        for key in ("pe", "team"):
            card, backlog, _ = SampleCache.get()[key]
            for story in task_stories(backlog, card):
                above = card_task(card, story["id"][2:])["data_class"] in ABOVE_CONFIDENTIAL
                with self.subTest(story=story["id"]):
                    templates = [t["template"] for t in story["tasks"]]
                    self.assertEqual("compliance-sign-off" in templates, above)
                    gates = [g for g in story["gated_by"] if g["kind"] == "sign-off"]
                    self.assertEqual(gates and [(g["id"]) for g in gates], ["compliance"] if above else [])

    def test_raised_data_class_adds_it(self):
        persona_dir, change = variant("team-highly-sensitive-task")
        _, backlog, _ = build_in(persona_dir, change)
        c1 = stories(backlog)["S-C1"]
        self.assertIn("S-C1.compliance-sign-off", [t["id"] for t in c1["tasks"]])
        self.assertEqual(c1["ready"][-1]["check"], "compliance-sign-off")

    def test_done_meets_the_check_and_lifts_the_gate(self):
        with BT.Scenario(PE) as persona:
            B.write_backlog(str(persona))
            edit_backlog(persona, {"S-T1.compliance-sign-off": "done"})
            t1 = stories(build(persona))["S-T1"]
        sign_off = next(c for c in t1["ready"] if c["check"] == "compliance-sign-off")
        self.assertTrue(sign_off["met"])
        self.assertFalse([g for g in t1["gated_by"] if g["kind"] == "sign-off"])

    def test_owner_handover(self):
        template = self.templates["owner-handover"]
        self.assertEqual(template["owner_role"], "skill-engineer")
        self.assertTrue(all(step["link"] for step in template["how"]))
        for key in ("pe", "team"):
            card, backlog, _ = SampleCache.get()[key]
            for story in task_stories(backlog, card):
                with self.subTest(story=story["id"]):
                    item = next(t for t in story["tasks"] if t["template"] == "owner-handover")
                    self.assertEqual(item["part"], story["part"])

    def test_design_maps_every_done_line(self):
        playbook = PLAYBOOK.read_text(encoding="utf-8")
        done = playbook.split("## Definition of done")[1].split("\n## ")[0]
        lines = [line[2:].strip() for line in done.splitlines() if line.startswith("- ")]
        self.assertEqual(len(lines), 5)
        design = BT.DESIGN.read_text(encoding="utf-8")
        rows = [row for row in design.splitlines() if row.startswith("| ")]
        for line in lines:
            with self.subTest(line=line):
                row = next((r for r in rows if line in r), None)
                self.assertIsNotNone(row, "design.md has no row for: " + line)
                named = re.findall(r"`([a-z0-9-]+)`", row)
                self.assertTrue(named)
                for tid in named:
                    self.assertIn(tid, self.templates)


# --- Spikes ---------------------------------------------------------------------------------------

class SpikeTests(unittest.TestCase):
    def test_one_per_open_question(self):
        for key in ("pe", "team"):
            card, backlog, _ = SampleCache.get()[key]
            questions = card["open_questions"]
            with self.subTest(sample=key):
                self.assertEqual([s["id"] for s in backlog["spikes"]], ["SP-" + q["id"] for q in questions])
                for spike, question in zip(backlog["spikes"], questions):
                    self.assertEqual(list(spike), ["id", "kind", "title", "question", "blocks", "owner", "due",
                                                   "status"])
                    self.assertEqual(spike["kind"], "spike")
                    self.assertEqual(spike["question"], question["question"])
                    self.assertEqual(spike["blocks"], ["S-" + t for t in question["blocks"]])
                    self.assertEqual((spike["owner"], spike["due"], spike["status"]),
                                     (question["owner"], question["due"], "todo"))
                    self.assertLessEqual(len(spike["title"]), 120)
                    self.assertTrue(question["question"].startswith(spike["title"].rstrip("…")))
        self.assertEqual(list(SampleCache.get()["pe"][1])[-2:], ["spikes", "retired"])

    def test_title_is_the_first_sentence(self):
        _, backlog, _ = SampleCache.get()["pe"]
        od8 = next(s for s in backlog["spikes"] if s["id"] == "SP-OD-8")
        self.assertEqual(od8["title"], "Identity for the hosted Monday summary, whether it may post to Teams, and "
                                       "whether a wrapper server is needed.")
        _, backlog, _ = SampleCache.get()["team"]
        self.assertEqual(backlog["spikes"][0]["blocks"], [])

    def test_gates_name_their_spike_and_stories_do_not_hold_spikes(self):
        _, backlog, md = SampleCache.get()["pe"]
        for story in BT.stories_of(backlog):
            self.assertFalse(story["id"].startswith("SP-"))
            for gate in story["gated_by"]:
                if gate["kind"] == "open-question":
                    self.assertEqual(list(gate), ["kind", "id", "text", "spike"])
                    self.assertEqual(gate["spike"], "SP-" + gate["id"])
        self.assertIn("\n## Spikes\n", md)
        self.assertLess(md.index("## F-twin-foundation"), md.index("\n## Spikes\n"))
        self.assertLess(md.index("\n## Spikes\n"), md.index("\n## Retired\n"))
        section = md.split("\n## Spikes\n")[1].split("\n## ")[0]
        self.assertIn("SP-E6", section)
        self.assertIn("S-T1, S-T2, S-T3", section)
        self.assertIn("2026-11-27", section)

    def test_status_kept_retired_and_section_left_out(self):
        with BT.Scenario(TEAM) as persona:
            B.write_backlog(str(persona))
            edit_backlog(persona, {"SP-OQ-1": "in-progress"})
            kept = build(persona)
            self.assertEqual(kept["spikes"][0]["status"], "in-progress")
            B.write_backlog(str(persona))
            rewrite_card(persona, lambda card: card.update({"open_questions": []}))
            result = B.write_backlog(str(persona))
            self.assertTrue(result["ok"], result["error"])
            data = load(persona / "backlog.json")
            md = (persona / "backlog.md").read_text(encoding="utf-8")
        self.assertEqual(data["spikes"], [])
        retired = dict((r["id"], r) for r in data["retired"])
        self.assertEqual(retired["SP-OQ-1"]["status"], "in-progress")
        self.assertNotIn("## Spikes", md)


# --- The committed samples ------------------------------------------------------------------------

class SampleTests(unittest.TestCase):
    def test_committed_samples_match_a_fresh_run(self):
        for persona in (PE, TEAM):
            with self.subTest(persona=persona.name):
                backlog = build(persona)
                self.assertEqual(B.render_json(backlog), (persona / "backlog.json").read_text(encoding="utf-8"))
                self.assertEqual(B.render_md(backlog, persona), (persona / "backlog.md").read_text(encoding="utf-8"))

    def test_constraints_step_links_the_card_section(self):
        def constrained(profile, card):
            card_task(card, "T1")["constraints"] = ["A reviewer checks every brief."]
        _, backlog, _ = build_in(PE, constrained)
        step = next(s for t in stories(backlog)["S-T1"]["tasks"] if t["template"] == "write-skill"
                    for s in t["how"] if s["text"].startswith(TC.CONSTRAINTS_STEP_START))
        self.assertEqual(step["link"], "partner-kit/docs/design.md#42-persona-card-cardjson")


if __name__ == "__main__":
    unittest.main()
