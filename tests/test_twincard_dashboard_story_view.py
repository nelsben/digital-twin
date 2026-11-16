"""Tests for the dashboard as a sponsor and an engineer read it (OPS-58).

A sponsor reads the top of the page with nothing opened: the goal, the targets, the owners and what is
blocked. An engineer reads every pilot story open, with its fields, acceptance lines and steps, and every
path in full, on screen and in print. Each page is read with html.parser into a small tree; the figures are
recomputed from card.json, customer-profile.json, levelled.json and backlog.json.

Anything the tests write goes to a temporary folder holding a copy of a sample's engagement.
Design of record: partner-kit/docs/design.md, section 9.

Standard library only. Run with: python3 -m unittest discover -s tests
"""

import json
import re
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest import mock

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

import test_twincard_dashboard as TD  # noqa: E402

ROOT = TD.ROOT
DATE = TD.DATE
DESIGN = ROOT / "partner-kit" / "docs" / "design.md"
FIELDS = ROOT / "partner-kit" / "plugins" / "twin-consultant" / "data" / "fields.json"

from twincard import backlog as B  # noqa: E402
from twincard import dashboard as D  # noqa: E402
from twincard import fields as F  # noqa: E402
from twincard import level as L  # noqa: E402
from twincard import validate as V  # noqa: E402

VOID = TD.VOID
SECTION_ORDER = ["Header", "What is blocked", "Anatomy grid", "Feature list", "Blockers and warnings", "Overrides",
                 "Backlog", "Open questions", "Where each answer came from"]
OWNERS = (("sponsor", "Sponsor"), ("technical_owner", "Technical owner"), ("business_owner", "Business owner"),
          ("backup_owner", "Backup owner"), ("compliance", "Compliance"))
STATUS_WORDS = {"todo": "[ ] todo", "in-progress": "[~] in progress", "done": "[x] done"}
TASK_STORY_PARTS = ["statement", "target", "ready", "delivery", "fields", "starting-points", "acceptance", "gates",
                    "tasks"]
FOUNDATION_PARTS = ["statement", "fields", "acceptance", "gates", "providers", "tasks"]
DRAFTED = "(statement drafted by the kit: confirm the wording)"
PATHS_NOTE = "Paths are relative to the delivery repository."
BARE_FILE = re.compile(r"^[A-Za-z0-9_.-]+\.(md|json)(#\S*)?$")

# How a boolean field reads on the page.
BOOLEAN_TEXT = {
    ("profile", "fictional"): {True: "Fictional sample"},
    ("profile", "identity.sso"): {True: "SSO yes", False: "SSO no"},
    ("profile", "identity.scim"): {True: "SCIM yes", False: "SCIM no"},
    ("profile", "compliance.phi"): {True: "PHI yes", False: "PHI no"},
    ("profile", "compliance.baa"): {True: "BAA yes", False: "BAA no"},
    ("profile", "compliance.mnpi"): {True: "MNPI yes", False: "MNPI no"},
    ("profile", "governance.action_log_required"): {True: "action log required: yes",
                                                     False: "action log required: no"},
    ("profile", "systems[].private_network"): {True: "private network: yes", False: "private network: no"},
    ("profile", "runtime_preferences.self_hosting_required"): {True: "Self-hosting required yes",
                                                               False: "Self-hosting required no"},
    ("card", "tasks[].in_pilot"): {True: "In pilot", False: "Later"},
    ("card", "memory.personal_memory_wanted"): {True: "Role wants personal memory yes",
                                                False: "Role wants personal memory no"},
}
# What the page says when the sample holds no value for a field.
EMPTY_TEXT = {
    ("card", "outcome.scorecard_targets[].metric"): "Targets not set",
    ("card", "outcome.scorecard_targets[].value"): "Targets not set",
    ("card", "overrides[].task"): "No overrides.",
    ("card", "overrides[].decision"): "No overrides.",
    ("card", "overrides[].value"): "No overrides.",
    ("card", "overrides[].reason"): "No overrides.",
    ("card", "overrides[].approved_by"): "No overrides.",
}
# Card text the page shows as the statement does: trimmed, one trailing full stop dropped.
CLAUSES = {("card", "tasks[].story_want"), ("card", "tasks[].story_benefit")}


# --- A small tree of the page ------------------------------------------------------------------------------

class Node(object):
    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.parent, self.children = tag, attrs, parent, []

    def walk(self):
        for child in self.children:
            if isinstance(child, Node):
                yield child
                for inner in child.walk():
                    yield inner

    def find(self, tag=None, **attrs):
        out = []
        for node in self.walk():
            if tag is not None and node.tag != tag:
                continue
            if all(node.attrs.get(k.replace("_", "-")) == v if v is not True else k.replace("_", "-") in node.attrs
                   for k, v in attrs.items()):
                out.append(node)
        return out

    def first(self, tag=None, **attrs):
        found = self.find(tag, **attrs)
        return found[0] if found else None

    def strings(self):
        for child in self.children:
            if isinstance(child, Node):
                for inner in child.strings():
                    yield inner
            else:
                yield child

    def text(self):
        return re.sub(r"\s+", " ", " ".join(self.strings())).strip()

    def ancestors(self):
        node = self.parent
        while node is not None:
            yield node
            node = node.parent

    def children_nodes(self):
        return [c for c in self.children if isinstance(c, Node)]


class Tree(HTMLParser):
    def __init__(self, text):
        HTMLParser.__init__(self, convert_charrefs=True)
        self.root = Node("#root", {}, None)
        self.current = self.root
        self.problems = []
        self.order = []
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, attrs):
        node = Node(tag, dict(attrs), self.current)
        self.current.children.append(node)
        self.order.append(node)
        if tag not in VOID:
            self.current = node

    def handle_startendtag(self, tag, attrs):
        node = Node(tag, dict(attrs), self.current)
        self.current.children.append(node)
        self.order.append(node)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.current.tag != tag:
            self.problems.append("end tag %s does not close %s" % (tag, self.current.tag))
            return
        self.current = self.current.parent

    def handle_data(self, data):
        self.current.children.append(data)


def tree(text):
    return Tree(text).root


def section(root, name):
    return root.first("section", data_section=name)


def code_texts(node):
    return [c.text() for c in node.find("code")]


def norm(text):
    return re.sub(r"\s+", " ", str(text)).strip()


def clause(text):
    text = norm(text)
    return text[:-1].rstrip() if text.endswith(".") else text


def fmt_number(value):
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def records(persona):
    persona = Path(persona)
    return {
        "card": load(persona / "card.json"),
        "profile": load(persona / ".." / ".." / "customer-profile.json"),
        "levelled": load(persona / "levelled.json"),
        "backlog": load(persona / "backlog.json"),
        "md": (persona / "backlog.md").read_text(encoding="utf-8"),
    }


def stories_of(backlog):
    return [s for f in backlog["epic"]["features"] for s in f["stories"]]


def task_stories(backlog):
    return [s for s in stories_of(backlog) if "ready" in s]


def is_ready(story):
    return all(c["met"] for c in story["ready"])


def owner_text(item):
    if item.get("owner_name"):
        return "%s, %s" % (item["owner_role"], item["owner_name"])
    if item.get("acting_owner"):
        return "%s, acting: %s" % (item["owner_role"], item["acting_owner"])
    return item["owner_role"]


def unnamed_line(backlog):
    roles = backlog.get("unnamed_roles") or []
    if not roles:
        return "Roles with no named person: none."
    return "Roles with no named person: %s." % "; ".join(
        "%s, %d task%s, %s" % (r["role"], r["tasks"], "" if r["tasks"] == 1 else "s",
                              "acting owner %s" % r["acting_owner"] if r["acting_owner"] else "no acting owner")
        for r in roles)


def md_field_rows(md, story_id):
    """The story's field table in backlog.md as [(label, value)], with backlog.md's escaping undone."""
    lines = md.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("### %s: " % story_id))
    head = next(i for i in range(start, len(lines)) if lines[i] == "| Field | Value |")
    rows = []
    for line in lines[head + 2:]:
        if not line.startswith("| "):
            break
        label, value = line[2:-2].split(" | ", 1)
        rows.append((label, value.replace("&lt;", "<")))
    return rows


def settings_baseline_in_md(md):
    return md_field_rows(md, "S-guardrails-and-settings") and dict(
        md_field_rows(md, "S-guardrails-and-settings"))["Settings baseline"]


def unverified_decisions(levelled, card):
    """The decisions that rest on an unverified fact: persona decisions, task decision cells, tool permissions."""
    count = sum(1 for name in ("plugin_name", "distribution", "settings_baseline")
                if levelled["persona_plan"][name].get("unverified"))
    for task in card["tasks"]:
        lt = levelled["tasks"].get(task["id"])
        if lt is None:
            continue
        for name in ("runtime", "identity", "memory", "plan_fit"):
            count += 1 if lt[name].get("unverified") else 0
        for name in ("start", "ceiling"):
            count += 1 if lt["autonomy"][name].get("unverified") else 0
        count += 1 if any(d.get("unverified") for d in lt["data_controls"].values()) else 0
        count += 1 if any(c.get("unverified") for c in lt["connectors"]) else 0
    count += sum(1 for tool in levelled.get("tools") or [] if tool["permission"].get("unverified"))
    return count


def providers_of(backlog):
    for story in stories_of(backlog):
        if story["id"] == "S-connectors-and-identity":
            return story.get("data_providers") or []
    return []


def page_for(persona):
    return D.render(str(persona), DATE)


# --- Scenarios ---------------------------------------------------------------------------------------------

def build_scenarios(tmp):
    """{name: (persona folder, page text)} for the scenarios the samples do not cover."""
    out = {}

    work = TD.Copy("team", tmp + "/blocker")
    work.apply_variant("team-individual-plan")
    work.regenerate()
    proc = TD.run_cli("dashboard", str(work.persona), "--date", DATE)
    out["blocker"] = (work.persona, (work.persona / "dashboard.html").read_text(encoding="utf-8"), proc.returncode)

    work = TD.Copy("team", tmp + "/override")
    work.apply_variant("team-override-c1-ceiling")
    work.regenerate()
    out["override"] = (work.persona, page_for(work.persona), 0)

    # No open questions (so no spikes), a drafted statement on C4, no backup owner, and S-C1 done.
    work = TD.Copy("team", tmp + "/edited")

    def card_change(card):
        card["open_questions"] = []
        task = next(t for t in card["tasks"] if t["id"] == "C4")
        task.pop("story_want", None)
        card["provenance"].pop("tasks.C4.story_want", None)

    def profile_change(profile):
        profile["owners"].pop("backup_owner", None)
        profile["provenance"].pop("owners.backup_owner", None)
    work.edit("card", card_change)
    work.edit("profile", profile_change)
    work.regenerate()
    path = work.persona / "backlog.json"
    backlog = load(path)
    for story in stories_of(backlog):
        if story["id"] == "S-C1":
            for task in story["tasks"]:
                task["status"] = "done"
    path.write_text(json.dumps(backlog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    proc = TD.run_cli("backlog", str(work.persona))
    if proc.returncode not in (0, 1):
        raise AssertionError(proc.stdout + proc.stderr)
    out["edited"] = (work.persona, page_for(work.persona), 0)

    # A null settings baseline on the PE sample: level itself is patched, as the null-ceiling test does.
    work = TD.Copy("pe", tmp + "/null-baseline").regenerate()
    real = L.level

    def null_baseline(*args, **kwargs):
        result = real(*args, **kwargs)
        if result["ok"]:
            result["levelled"]["persona_plan"]["settings_baseline"]["value"] = None
        return result
    with mock.patch.object(L, "level", null_baseline):
        L.write_levelled(str(work.persona))
        B.write_backlog(str(work.persona))
        out["null-baseline"] = (work.persona, page_for(work.persona), 0)
        out["null-baseline-records"] = records(work.persona)
    return out


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.samples = {}
        for fid, fixture in TD.fixtures().items():
            persona = ROOT / fixture["persona_dir"]
            text = page_for(persona)
            cls.samples[fid] = {"persona": persona, "text": text, "root": tree(text), "rec": records(persona)}


class ScenarioBase(Base):
    @classmethod
    def setUpClass(cls):
        Base.setUpClass.__func__(cls)
        cls._tmp = tempfile.TemporaryDirectory()
        built = build_scenarios(cls._tmp.name)
        cls.scenarios = {}
        for name in ("blocker", "override", "edited", "null-baseline"):
            persona, text, code = built[name]
            rec = built["null-baseline-records"] if name == "null-baseline" else records(persona)
            cls.scenarios[name] = {"persona": persona, "text": text, "root": tree(text), "rec": rec, "code": code}

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def all_pages(self):
        pages = dict(self.samples)
        pages.update(self.scenarios)
        return pages


# --- 1. At a glance ----------------------------------------------------------------------------------------

class AtAGlanceTests(ScenarioBase):
    def test_header_has_no_details_and_comes_first(self):
        for name, page in self.all_pages().items():
            header = section(page["root"], "Header")
            self.assertIsNotNone(header, name)
            self.assertEqual(header.find("details"), [], name)
            sections = [s.attrs["data-section"] for s in page["root"].find("section")]
            self.assertEqual(sections, SECTION_ORDER, name)

    def test_customer_role_plan_goal_and_targets(self):
        for name, page in self.all_pages().items():
            card, profile = page["rec"]["card"], page["rec"]["profile"]
            header = section(page["root"], "Header")
            text = header.text()
            self.assertIn(profile["display_name"], header.first(data_field="customer").text(), name)
            self.assertIn(card["role"]["name"], header.first(data_field="role").text(), name)
            self.assertIn(profile["plan"]["tier"], header.first(data_field="plan").text(), name)
            self.assertEqual(header.first(data_field="sponsor-goal").text(), norm(card["outcome"]["sponsor_goal"]), name)
            targets = [t for t in card["outcome"].get("scorecard_targets") or []]
            got = header.first(data_field="targets").text()
            if targets:
                self.assertEqual(got, "; ".join("%s: %s" % (t["metric"], fmt_number(t["value"])) for t in targets),
                                 name)
            else:
                self.assertEqual(got, "Targets not set", name)
            self.assertIn(PATHS_NOTE, text, name)

    def test_targets_not_set_on_the_pe_sample(self):
        self.assertEqual(section(self.samples["pe"]["root"], "Header").first(data_field="targets").text(),
                         "Targets not set")

    def test_completeness_counts_and_ready(self):
        for name, page in self.all_pages().items():
            rec = page["rec"]
            header = section(page["root"], "Header")
            self.assertRegex(header.first(data_field="completeness").text(), r"^\d+%$", name)
            self.assertIn(header.first(data_field="complete").text(), ("Complete", "Not complete"), name)
            self.assertEqual(header.first(data_field="blocker-count").text(), str(len(rec["levelled"]["blockers"])),
                             name)
            self.assertEqual(header.first(data_field="warning-count").text(), str(len(rec["levelled"]["warnings"])),
                             name)
            self.assertEqual(header.first(data_field="unverified-count").text(),
                             str(unverified_decisions(rec["levelled"], rec["card"])), name)
            told = task_stories(rec["backlog"])
            self.assertEqual(header.first(data_field="ready-count").text(),
                             "Stories ready to build: %d of %d" % (sum(1 for s in told if is_ready(s)), len(told)),
                             name)

    def test_all_five_owners_and_the_unnamed_roles(self):
        for name, page in self.all_pages().items():
            owners = page["rec"]["profile"].get("owners") or {}
            header = section(page["root"], "Header")
            items = header.find("li", data_owner=True)
            self.assertEqual([i.attrs["data-owner"] for i in items], [k for k, _ in OWNERS], name)
            for item, (key, label) in zip(items, OWNERS):
                self.assertEqual(item.text(), "%s: %s" % (label, owners.get(key) or "not named"), name)
            self.assertEqual(header.first(data_field="unnamed-roles").text(), unnamed_line(page["rec"]["backlog"]),
                             name)

    def test_a_missing_owner_reads_not_named(self):
        header = section(self.scenarios["edited"]["root"], "Header")
        self.assertEqual(header.first("li", data_owner="backup_owner").text(), "Backup owner: not named")


# --- 2. What is blocked ------------------------------------------------------------------------------------

class WhatIsBlockedTests(ScenarioBase):
    def blocked(self, page):
        return section(page["root"], "What is blocked")

    def test_it_comes_directly_under_the_header(self):
        for name, page in self.all_pages().items():
            sections = [s.attrs["data-section"] for s in page["root"].find("section")]
            self.assertEqual(sections[:2], ["Header", "What is blocked"], name)

    def test_every_blocker_with_what_it_is_about_and_its_message(self):
        for name, page in self.all_pages().items():
            items = self.blocked(page).find("li", data_blocked="blocker")
            blockers = page["rec"]["levelled"]["blockers"]
            self.assertEqual(len(items), len(blockers), name)
            for item, b in zip(items, blockers):
                self.assertIn(norm(b["message"]), item.text(), name)
                self.assertIn(b["about"], item.text(), name)
            if not blockers:
                self.assertIn("No blockers.", self.blocked(page).text(), name)
        self.assertTrue(self.scenarios["blocker"]["rec"]["levelled"]["blockers"])
        self.assertNotIn("No blockers.", self.blocked(self.scenarios["blocker"]).text())

    def test_every_spike_not_done(self):
        for name, page in self.all_pages().items():
            spikes = [s for s in page["rec"]["backlog"].get("spikes") or [] if s["status"] != "done"]
            items = self.blocked(page).find("li", data_blocked="spike")
            self.assertEqual([i.attrs.get("data-id") for i in items], [s["id"] for s in spikes], name)
            for item, spike in zip(items, spikes):
                text = item.text()
                self.assertIn("Spike", text, name)
                self.assertIn(norm(spike["question"]), text, name)
                self.assertIn("Owner: %s" % (spike["owner"] or "not named"), text, name)
                self.assertIn("Due: %s" % (spike["due"] or "not set"), text, name)
                self.assertIn("Blocks: %s" % (", ".join(spike["blocks"]) or "no story"), text, name)
            if not spikes:
                self.assertIn("No open spikes.", self.blocked(page).text(), name)
        self.assertFalse(self.scenarios["edited"]["rec"]["backlog"]["spikes"])
        self.assertTrue(self.blocked(self.samples["pe"]).find("li", data_blocked="spike"))

    def test_every_story_waiting_on_a_compliance_sign_off(self):
        for name, page in self.all_pages().items():
            waiting = [s for s in stories_of(page["rec"]["backlog"])
                       if any(g["kind"] == "sign-off" for g in s["gated_by"])]
            items = self.blocked(page).find("li", data_blocked="sign-off")
            self.assertEqual([i.attrs.get("data-id") for i in items], [s["id"] for s in waiting], name)
            if not waiting:
                self.assertIn("No story is waiting on a compliance sign-off.", self.blocked(page).text(), name)
        self.assertTrue(self.blocked(self.samples["pe"]).find("li", data_blocked="sign-off"))


# --- 3. Stories open ---------------------------------------------------------------------------------------

class StoriesOpenTests(ScenarioBase):
    def test_epic_and_features_are_headings_and_only_stories_collapse(self):
        for name, page in self.all_pages().items():
            backlog_section = section(page["root"], "Backlog")
            headings = [h.text() for h in backlog_section.walk() if h.tag in ("h3", "h4")]
            epic = page["rec"]["backlog"]["epic"]
            self.assertTrue(any(epic["title"] in h for h in headings), name)
            for feature in epic["features"]:
                self.assertTrue(any(feature["id"] in h and feature["title"] in h for h in headings),
                                "%s %s" % (name, feature["id"]))
            for details in backlog_section.find("details"):
                self.assertIn("data-story", details.attrs, name)
                self.assertEqual(details.find("details"), [], "%s: something inside a story collapses" % name)

    def test_a_story_is_open_when_in_the_pilot_and_not_done(self):
        for name, page in self.all_pages().items():
            shown = dict((d.attrs["data-story"], "open" in d.attrs) for d in page["root"].find("details", data_story=True))
            want = dict((s["id"], bool(s["in_pilot"]) and s["status"] != "done")
                        for s in stories_of(page["rec"]["backlog"]))
            self.assertEqual(shown, want, name)
            count = section(page["root"], "Backlog").first(data_field="story-count").text()
            m = re.match(r"Stories shown open: (\d+)\. Stories closed: (\d+)", count)
            self.assertIsNotNone(m, count)
            self.assertEqual((int(m.group(1)), int(m.group(2))),
                             (sum(want.values()), len(want) - sum(want.values())), name)

    def test_every_pilot_story_is_open_in_both_samples(self):
        for fid, page in self.samples.items():
            for story in stories_of(page["rec"]["backlog"]):
                if story["in_pilot"]:
                    node = page["root"].first("details", data_story=story["id"])
                    self.assertIn("open", node.attrs, "%s %s" % (fid, story["id"]))

    def test_a_done_story_is_closed(self):
        page = self.scenarios["edited"]
        story = next(s for s in stories_of(page["rec"]["backlog"]) if s["id"] == "S-C1")
        self.assertEqual(story["status"], "done")
        self.assertTrue(story["in_pilot"])
        self.assertNotIn("open", page["root"].first("details", data_story="S-C1").attrs)


# --- 4. Inside a story -------------------------------------------------------------------------------------

class InsideAStoryTests(ScenarioBase):
    def node(self, page, story_id):
        return page["root"].first("details", data_story=story_id)

    def test_parts_come_in_order(self):
        for name, page in self.all_pages().items():
            card_tasks = dict((t["id"], t) for t in page["rec"]["card"]["tasks"])
            for story in stories_of(page["rec"]["backlog"]):
                parts = [n.attrs["data-story-part"] for n in self.node(page, story["id"]).find(data_story_part=True)]
                if "ready" in story:
                    want = list(TASK_STORY_PARTS)
                    if not card_tasks.get(story["id"][2:], {}).get("starts_from"):
                        want.remove("starting-points") if "starting-points" not in parts else None
                else:
                    want = [p for p in FOUNDATION_PARTS if p != "providers" or story.get("data_providers")]
                self.assertEqual(parts, want, "%s %s" % (name, story["id"]))

    def test_statement_target_ready_and_delivery(self):
        for name, page in self.all_pages().items():
            for story in stories_of(page["rec"]["backlog"]):
                node = self.node(page, story["id"])
                statement = node.first(data_story_part="statement").text()
                self.assertTrue(statement.startswith(norm(story["statement"])), "%s %s" % (name, story["id"]))
                self.assertEqual(DRAFTED in statement, story.get("statement_source") == "drafted", story["id"])
                if "ready" not in story:
                    continue
                self.assertEqual(node.first(data_story_part="target").text(), norm(story["target"]["text"]))
                ready = node.first(data_story_part="ready")
                self.assertTrue(ready.text().startswith("Ready to build: %s" % ("yes" if is_ready(story) else "no")))
                unmet = [c for c in story["ready"] if not c["met"]]
                self.assertEqual(len(ready.find("li")), len(unmet), story["id"])
                for item, check in zip(ready.find("li"), unmet):
                    self.assertIn(check["check"], item.text())
                    self.assertIn(norm(check["note"]), item.text())
                self.assertIn(norm(story["fields"]["delivery"]), node.first(data_story_part="delivery").text())

    def test_a_drafted_statement_says_so(self):
        page = self.scenarios["edited"]
        story = next(s for s in stories_of(page["rec"]["backlog"]) if s["id"] == "S-C4")
        self.assertEqual(story["statement_source"], "drafted")
        self.assertIn(DRAFTED, self.node(page, "S-C4").first(data_story_part="statement").text())

    def test_field_table_is_the_backlog_md_table(self):
        for name, page in self.all_pages().items():
            for story in stories_of(page["rec"]["backlog"]):
                table = self.node(page, story["id"]).first(data_story_part="fields")
                rows = [(r.first("th").text(), r.first("td").text()) for r in table.find("tr") if r.first("td")]
                self.assertEqual(rows, [(k, norm(v)) for k, v in md_field_rows(page["rec"]["md"], story["id"])],
                                 "%s %s" % (name, story["id"]))

    def test_starting_points_the_task_builds_from(self):
        for name, page in self.all_pages().items():
            for task in page["rec"]["card"]["tasks"]:
                names = task.get("starts_from") or []
                part = self.node(page, "S-" + task["id"]).first(data_story_part="starting-points")
                if not names:
                    continue
                for point in names:
                    self.assertIn(point, part.text(), "%s %s" % (name, task["id"]))

    def test_acceptance_numbered_and_gates(self):
        for name, page in self.all_pages().items():
            for story in stories_of(page["rec"]["backlog"]):
                node = self.node(page, story["id"])
                ol = node.first(data_story_part="acceptance")
                self.assertEqual(ol.tag, "ol")
                self.assertEqual([li.text() for li in ol.find("li")], [norm(a) for a in story["acceptance"]])
                gates = node.first(data_story_part="gates").text()
                for gate in story["gated_by"]:
                    self.assertIn(gate["id"], gates)
                    self.assertIn(norm(gate["text"]), gates)
                if not story["gated_by"]:
                    self.assertIn("Nothing", gates)

    def test_one_task_table_with_every_column_and_numbered_steps(self):
        for name, page in self.all_pages().items():
            for story in stories_of(page["rec"]["backlog"]):
                table = self.node(page, story["id"]).first(data_story_part="tasks")
                self.assertEqual(table.tag, "table")
                header = [th.text() for th in table.first("thead").find("th")]
                self.assertEqual(header, ["Task", "Title", "Part", "Owner", "Status"])
                groups = table.find("tbody")
                self.assertEqual([g.attrs.get("data-task") for g in groups], [t["id"] for t in story["tasks"]])
                for group, item in zip(groups, story["tasks"]):
                    text = group.text()
                    for want in (item["id"], norm(item["title"]), item["part"], owner_text(item),
                                 STATUS_WORDS[item["status"]], norm(item["done_when"])):
                        self.assertIn(want, text, "%s %s" % (name, item["id"]))
                    steps = group.first("ol")
                    self.assertEqual(len(steps.find("li")), len(item["how"]), item["id"])
                    for li, step in zip(steps.find("li"), item["how"]):
                        self.assertIn(norm(step["text"]), li.text(), item["id"])
                        if step["link"]:
                            self.assertIn(step["link"], code_texts(li), item["id"])


# --- 5. Full paths -----------------------------------------------------------------------------------------

class FullPathTests(Base):
    def cites(self, levelled, backlog):
        out = set()
        plan = levelled["persona_plan"]
        for name in ("plugin_name", "distribution", "settings_baseline"):
            out.add(plan[name].get("cite"))
        for point in plan.get("starting_points") or []:
            out.add(point.get("cite"))
        for lt in levelled["tasks"].values():
            for name in ("runtime", "identity", "memory", "plan_fit"):
                out.add(lt[name].get("cite"))
            for d in list(lt["autonomy"].values()) + list(lt["data_controls"].values()):
                out.add(d.get("cite"))
            for c in lt["connectors"]:
                out.add(c.get("cite"))
                out.add(c.get("runbook"))
        for item in levelled["blockers"] + levelled["warnings"]:
            out.add(item.get("cite"))
        for p in providers_of(backlog):
            out.add(p.get("cite"))
        return set(c for c in out if c)

    def test_every_how_link_and_cite_is_its_full_path_in_code(self):
        for fid, page in self.samples.items():
            codes = set(code_texts(page["root"]))
            links = set(step["link"] for s in stories_of(page["rec"]["backlog"]) for t in s["tasks"]
                        for step in t["how"] if step["link"])
            self.assertTrue(links)
            self.assertEqual(links - codes, set(), fid)
            self.assertEqual(self.cites(page["rec"]["levelled"], page["rec"]["backlog"]) - codes, set(), fid)

    def test_no_bare_file_name_outside_the_record_sources(self):
        for fid, page in self.samples.items():
            for name in SECTION_ORDER:
                if name in ("Where each answer came from",):
                    continue
                for text in code_texts(section(page["root"], name)):
                    self.assertIsNone(BARE_FILE.match(text), "%s %s: %s" % (fid, name, text))

    def test_paths_stay_text_and_the_note_is_near_the_top(self):
        for fid, page in self.samples.items():
            for a in page["root"].find("a"):
                self.assertTrue(a.attrs.get("href", "").startswith("#"), fid)
            self.assertIn(PATHS_NOTE, section(page["root"], "Header").text(), fid)


# --- 6. One word for undecided -----------------------------------------------------------------------------

class UndecidedTests(ScenarioBase):
    def check_baseline(self, name, page):
        md_value = settings_baseline_in_md(page["rec"]["md"])
        decision = page["rec"]["levelled"]["persona_plan"]["settings_baseline"]
        header = page["root"].first(data_decision="persona.settings_baseline").text()
        self.assertTrue(header.startswith(md_value), "%s: %s against %s" % (name, header, md_value))
        if decision["value"] is None:
            self.assertEqual(md_value, "undecided", name)
            self.assertIn(norm(decision["reason"]), header, name)
        story = page["root"].first("details", data_story="S-guardrails-and-settings")
        rows = dict((r.first("th").text(), r.first("td").text())
                    for r in story.first(data_story_part="fields").find("tr") if r.first("td"))
        self.assertEqual(rows["Settings baseline"], md_value, name)
        a7 = page["root"].first(data_part="A7").text()
        self.assertIn("Settings baseline %s" % md_value, a7, name)
        self.assertNotRegex(page["root"].text(), r"(?i)settings baseline:? none\b", name)

    def test_settings_baseline_reads_as_backlog_md_has_it(self):
        for name in ("pe", "team"):
            self.check_baseline(name, self.samples[name])
        self.check_baseline("null-baseline", self.scenarios["null-baseline"])
        self.assertIsNone(self.scenarios["null-baseline"]["rec"]["levelled"]["persona_plan"]["settings_baseline"]
                          ["value"])

    def test_a_null_task_baseline_reads_undecided_in_its_cell(self):
        page = self.samples["team"]
        for task in page["rec"]["card"]["tasks"]:
            d = page["rec"]["levelled"]["tasks"][task["id"]]["data_controls"]["settings_baseline"]
            if d["value"] is None:
                cell = page["root"].first(data_decision="%s.data_controls" % task["id"]).text()
                self.assertIn("settings baseline undecided", cell)


# --- 7. What was left out ----------------------------------------------------------------------------------

class LeftOutTests(ScenarioBase):
    def test_data_providers_in_the_connectors_panel(self):
        for name, page in self.all_pages().items():
            panel = page["root"].first(data_part="A3")
            providers = providers_of(page["rec"]["backlog"])
            rows = panel.find("tr", data_provider=True)
            if not providers:
                self.assertEqual(rows, [], name)
                self.assertIn("The industry pack lists no data providers.", panel.text(), name)
                continue
            self.assertIn("none is on by default", panel.text(), name)
            table = rows[0].parent if rows[0].parent.tag == "table" else rows[0].parent.parent
            self.assertEqual([th.text() for th in table.first("thead").find("th")],
                             ["Name", "Kind", "Access", "Note", "Source"], name)
            self.assertEqual([r.attrs["data-provider"] for r in rows], [p["name"] for p in providers], name)
            for row, p in zip(rows, providers):
                text = row.text()
                for key in ("name", "kind", "access", "note"):
                    self.assertIn(norm(p[key]), text, name)
                self.assertIn(p["cite"], code_texts(row), name)
                self.assertEqual("Unverified" in text, bool(p.get("unverified")), "%s %s" % (name, p["name"]))
        self.assertTrue(providers_of(self.samples["pe"]["rec"]["backlog"]))
        self.assertFalse(providers_of(self.samples["team"]["rec"]["backlog"]))

    def test_overrides_section(self):
        for name, page in self.all_pages().items():
            overrides = page["rec"]["card"].get("overrides") or []
            node = section(page["root"], "Overrides")
            rows = node.find("tr", data_override=True)
            self.assertEqual(len(rows), len(overrides), name)
            if not overrides:
                self.assertIn("No overrides.", node.text(), name)
            for row, ov in zip(rows, overrides):
                text = row.text()
                for key in ("task", "decision", "reason", "approved_by"):
                    self.assertIn(norm(ov[key]), text, name)
                self.assertIn(D.fmt(ov["value"]) if not isinstance(ov["value"], dict) else "", text, name)
        self.assertTrue(self.scenarios["override"]["rec"]["card"]["overrides"])

    def test_where_each_answer_came_from_is_a_closed_block_at_the_end(self):
        for name, page in self.all_pages().items():
            node = section(page["root"], "Where each answer came from")
            blocks = [d for d in node.find("details") if d.first("summary")
                      and d.first("summary").text().startswith("Where each answer came from")]
            self.assertEqual(len(blocks), 1, name)
            block = blocks[0]
            self.assertNotIn("open", block.attrs, name)
            all_details = page["root"].find("details")
            self.assertIs(all_details[-1], block, name)
            rows = block.find("tr", data_provenance=True)
            entries = [("card", p, e) for p, e in (page["rec"]["card"].get("provenance") or {}).items()] + \
                      [("profile", p, e) for p, e in (page["rec"]["profile"].get("provenance") or {}).items()]
            self.assertEqual([r.attrs["data-provenance"] for r in rows], ["%s:%s" % (r, p) for r, p, _ in entries],
                             name)
            for row, (_, path, entry) in zip(rows, entries):
                text = row.text()
                self.assertIn(path, text)
                self.assertIn(entry["status"], text)
                for one in V.split_sources(entry.get("source")):
                    self.assertIn(one, text)
                self.assertIn(entry.get("owner") or "not named", text)
                self.assertIn(entry.get("due") or "not set", text)


class CatalogueTests(Base):
    def test_every_dashboard_field_appears_on_both_samples(self):
        catalogue = F.load_catalogue()
        for fid, page in self.samples.items():
            text = page["root"].text()
            for record in ("profile", "card"):
                data = page["rec"][record]
                _, _, values = V._check_record(data, record, catalogue, V._Report())
                for entry in F.fields_for(record, catalogue):
                    if not [f for f in entry["feeds"] if f.startswith("dashboard:")]:
                        continue
                    key = (record, entry["path"])
                    got = [v for _, v in values.get(entry["path"], []) if not type(v) is object]
                    flat = []
                    for v in got:
                        flat.extend(v if isinstance(v, list) else [v])
                    flat = [v for v in flat if v is not None and v != ""]
                    if not flat:
                        if key in EMPTY_TEXT:
                            self.assertIn(EMPTY_TEXT[key], text, "%s %s" % (fid, key))
                        continue
                    for v in flat:
                        if isinstance(v, bool):
                            want = BOOLEAN_TEXT[key].get(v)
                            if want:
                                self.assertIn(want, text, "%s %s=%s" % (fid, key, v))
                        elif isinstance(v, (int, float)):
                            self.assertIn(fmt_number(v), text, "%s %s" % (fid, key))
                        elif isinstance(v, str):
                            want = clause(v) if key in CLAUSES else norm(v)
                            self.assertIn(want, text, "%s %s" % (fid, key))

    def test_the_design_names_every_field_the_page_does_not_show(self):
        design = DESIGN.read_text(encoding="utf-8")
        nine = design[design.index("## 9. Dashboard"):design.index("## 10. Fixtures")]
        for entry in load(FIELDS)["fields"]:
            if not [f for f in entry["feeds"] if f.startswith("dashboard:")]:
                self.assertIn("`%s`" % entry["path"], nine, entry["path"])


# --- 8. Print ----------------------------------------------------------------------------------------------

def print_rules(style):
    start = style.index("@media print")
    depth, i = 0, style.index("{", start)
    for j in range(i, len(style)):
        if style[j] == "{":
            depth += 1
        elif style[j] == "}":
            depth -= 1
            if depth == 0:
                return re.sub(r"\s+", "", style[i + 1:j])
    raise AssertionError("unclosed @media print")


class PrintTests(Base):
    def test_print_rules(self):
        for fid, page in self.samples.items():
            rules = print_rules(page["root"].first("style").text())
            self.assertNotRegex(rules, r"(^|\})nav\{[^}]*display:none", fid)
            self.assertNotRegex(rules, r"\.toc[^{]*\{[^}]*display:none", fid)
            self.assertIn("details:not([open])>*{display:block", rules, fid)
            self.assertRegex(rules, r"details::details-content\{[^}]*content-visibility:visible", fid)
            self.assertRegex(rules, r"\.scroll\{[^}]*overflow:visible", fid)
            self.assertRegex(rules, r"details\.story\{[^}]*break-inside:avoid", fid)


# --- 9. Kept -----------------------------------------------------------------------------------------------

class KeptTests(ScenarioBase):
    def test_structure(self):
        for name, page in self.all_pages().items():
            self.assertEqual(Tree(page["text"]).problems, [], name)
            tags = [n.tag for n in page["root"].walk()]
            self.assertNotIn("script", tags, name)
            for node in page["root"].walk():
                for attr in node.attrs:
                    self.assertFalse(attr.startswith("on"), "%s: %s" % (name, attr))
                self.assertNotIn(node.tag, ("link", "img", "iframe", "object", "embed"), name)
            levels = [int(n.tag[1]) for n in page["root"].walk() if re.match(r"^h[1-6]$", n.tag)]
            self.assertEqual(levels[0], 1, name)
            for before, after in zip(levels, levels[1:]):
                self.assertLessEqual(after, before + 1, name)
            for table in page["root"].find("table"):
                self.assertTrue(table.find("th"), name)

    def test_same_bytes_and_a_blocker_still_writes_the_page(self):
        for fid, page in self.samples.items():
            self.assertEqual(page_for(page["persona"]), page["text"], fid)
        self.assertEqual(self.scenarios["blocker"]["code"], 1)
        self.assertTrue(section(self.scenarios["blocker"]["root"], "What is blocked").find("li", data_blocked="blocker"))


class RecomputeTests(ScenarioBase):
    def test_header_figures_recompute(self):
        for name, page in self.all_pages().items():
            rec = page["rec"]
            root = page["root"]
            header = section(root, "Header")
            card = rec["card"]
            pilot = [t["id"] for t in card["tasks"] if t.get("in_pilot")]
            tasks = [t for s in stories_of(rec["backlog"]) for t in s["tasks"]]
            self.assertEqual(header.first(data_field="sponsor-line").text(),
                             "Tasks in the pilot: %d. Blockers: %d. Backlog tasks done: %d of %d." % (
                                 len(pilot), len(rec["levelled"]["blockers"]),
                                 sum(1 for t in tasks if t["status"] == "done"), len(tasks)), name)
            stories = stories_of(rec["backlog"])
            open_n = sum(1 for s in stories if s["in_pilot"] and s["status"] != "done")
            self.assertEqual(len(root.find("details", data_story=True, open=True)), open_n, name)
            self.assertEqual(len(root.find("tr", data_provider=True)), len(providers_of(rec["backlog"])), name)
            self.assertEqual(len(root.find("tr", data_override=True)), len(card.get("overrides") or []), name)
            self.assertEqual(len(root.find("tr", data_provenance=True)),
                             len(card.get("provenance") or {}) + len(rec["profile"].get("provenance") or {}), name)


if __name__ == "__main__":
    unittest.main()
