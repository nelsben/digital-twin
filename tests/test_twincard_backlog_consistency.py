"""The generated backlog never contradicts itself (OPS-55).

Every scenario the backlog tests build (both fictional samples, every expectations variant and the
local scenarios) is checked for:

- one permission per tool: no task in a story states a permission for a tool other than the levelled one;
- delivery: every task story says how its output is delivered, in exactly one of four forms, and a
  story where a person sends or files the draft has a deliver-draft task;
- links: no library step has a null link, every link resolves, and the kit's runbooks and pilot
  templates are linked where the backlog is about them;
- owners: a task of a customer role the profile names carries that name, and a customer role it
  cannot name has an acting owner;
- parts: a confirm-unverified-decision task carries the part of the decision it confirms.

Facts come from levelled.json and the profile, never from backlog.py, so the checks are independent
of the code they check. Design of record: partner-kit/docs/design.md, section 8.
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

ROOT = BT.ROOT
PACKS_DIR = BT.PLUGIN_DIR / "data" / "industry-packs"
PERMISSION_NAMES = {"always-allow": "Always allow", "needs-approval": "Needs approval", "blocked": "Blocked"}
TOOL_TEMPLATES = {"tool-always-allow": "always-allow", "tool-needs-approval": "needs-approval",
                  "tool-blocked": "blocked"}
RUNBOOK_PLACEHOLDER = "{connector.runbook}"
CONSTRAINTS_STEP_START = "Make the skill keep these rules from the interviews"
GENERAL_PREFIXES = ("starter-kit/runbooks/", "starter-kit/templates/", "starter-kit/plugins/",
                    "starter-kit/settings/", "engagements/")
PROFILE_ROLES = {"executive-sponsor": "sponsor", "technical-owner": "technical_owner",
                 "business-owner": "business_owner", "backup-owner": "backup_owner", "compliance": "compliance"}
PARTNER_ROLES = ("engagement-lead", "solution-architect", "skill-engineer", "integration-engineer",
                 "change-and-enablement-lead", "consultant")
ACTING_ROLES = ("security", "source-system-admin", "pilot-user")
# The anatomy part of each decision a confirm-unverified-decision task confirms (design section 8).
DECISION_PARTS = {"runtime": "A4", "identity": "A5", "autonomy.start": "A7", "autonomy.ceiling": "A7",
                  "data_controls.settings_baseline": "A7", "data_controls.web_tools": "A7",
                  "data_controls.surfaces": "A7", "data_controls.retention": "A7", "memory": "A6",
                  "plan_fit": "A9"}
SETUP_RUNBOOKS = {
    "setup-scheduled-task": "starter-kit/runbooks/claude-code-scheduled-task.md",
    "setup-tag-routine": "starter-kit/runbooks/claude-tag-routine.md",
    "setup-managed-agents": "starter-kit/runbooks/managed-agents.md",
    "setup-managed-agents-self-hosted": "starter-kit/runbooks/managed-agents.md",
    "setup-agent-sdk": "starter-kit/runbooks/agent-sdk-runner.md",
}
PILOT_TEMPLATES = {
    "pilot-scorecard": "starter-kit/templates/pilot/scorecard.md",
    "memory-policy": "starter-kit/templates/pilot/memory-policy.md",
    "pilot-training": "starter-kit/templates/pilot/pilot-training.md",
}
PACK_RUNBOOKS = {
    "HubSpot": "starter-kit/runbooks/hubspot-connector.md",
    "Google Drive": "starter-kit/runbooks/google-workspace-connectors.md",
    "Google Drive / Sheets": "starter-kit/runbooks/google-workspace-connectors.md",
    "Gmail": "starter-kit/runbooks/google-workspace-connectors.md",
    "Google Calendar": "starter-kit/runbooks/google-workspace-connectors.md",
    "Slack": "starter-kit/runbooks/slack-connector.md",
    "Zendesk": "starter-kit/runbooks/zendesk-connector.md",
}
RUNBOOK_HEADINGS = ("#before-you-start", "#steps", "#check-it-worked", "#hand-over")
FORMS = {
    "twin-writes": re.compile(r"^The twin writes it with tools? \S.*\.$"),
    "runtime-posts": re.compile(r"^The \S.* posts it .*itself, and the connector's send tool \S+ is not used\.$"),
    "person-sends": re.compile(r"^A person sends or files it: the twin produces a draft, \S.* Blocked at the "
                               r"starting level.*\.$"),
    "stays-local": re.compile(r"^The output stays in the conversation or a local file\.$"),
}
STATED = re.compile(r"\b(Always allow|Needs approval|Blocked)\b")
NEVER = re.compile(r"\bnever (Always allow|Needs approval|Blocked)\b")


def tool_id(tool):
    return "%s-%s" % (tool["system"], tool["use"])


def story_tools(levelled, tid):
    """{tool id: levelled tool} for the tools that list the task."""
    return dict((tool_id(t), t) for t in levelled.get("tools") or [] if tid in (t.get("tasks") or []))


def permission(tool):
    return (tool.get("permission") or {}).get("value")


def opens(tool):
    """True when the tool is not Blocked once every task that uses it is at its ceiling."""
    wanted = tool.get("wanted") or {}
    return bool(wanted) and all(value != "blocked" for value in wanted.values())


def expected_form(levelled, tid):
    writes = dict((k, t) for k, t in story_tools(levelled, tid).items() if t["use"] != "read")
    runtime = (((levelled.get("tasks") or {}).get(tid) or {}).get("runtime") or {}).get("value")
    if not writes:
        return "stays-local"
    if runtime == "claude-tag-routine" and all(t["system"] == "slack" and t["use"] == "send"
                                                for t in writes.values()):
        return "runtime-posts"
    if any(permission(t) == "blocked" for t in writes.values()):
        return "person-sends"
    return "twin-writes"


def clauses(text):
    return [c for c in re.split(r"(?<=[.;:])\s+", text) if c.strip()]


def pack_runbooks():
    out = {}
    for path in sorted(PACKS_DIR.glob("*.json")):
        for default in BT.load(path).get("connector_defaults") or []:
            if default.get("runbook"):
                out.setdefault(default["runbook"], default["system_kind"])
    return out


def expand(link, when=None):
    """A library link, with the connector-runbook placeholder filled in from every pack runbook the
    template's 'when' admits."""
    if link and link.startswith(RUNBOOK_PLACEHOLDER):
        known = set(BT.B.allowed_facts("task-story", "connector"))
        out = []
        for runbook, kind in sorted(pack_runbooks().items()):
            facts = dict((name, None) for name in known)
            facts.update({"connector.runbook": runbook, "connector.kind": kind})
            if when is None or BT.L.matches(when, facts, known):
                out.append(runbook + link[len(RUNBOOK_PLACEHOLDER):])
        return out
    return [link]


class Runs(object):
    """Every scenario built once: (name, profile, card, levelled, backlog, markdown)."""
    _runs = None

    @classmethod
    def get(cls):
        if cls._runs is None:
            runs = []
            for name, persona_dir, change, after in BT.all_scenarios():
                with BT.Scenario(persona_dir, change, after=after) as persona:
                    levelled = BT.load(persona / "levelled.json")
                    card = BT.load(persona / "card.json")
                    profile = BT.load(persona.parent.parent / "customer-profile.json")
                    result = BT.B.build(str(persona))
                    md = BT.B.render_md(result["backlog"]) if result["ok"] else ""
                if result["ok"]:
                    runs.append((name, profile, card, levelled, result["backlog"], md))
            cls._runs = runs
        return cls._runs


def task_stories(backlog, levelled):
    for story in BT.stories_of(backlog):
        tid = story["id"][2:]
        if tid in (levelled.get("tasks") or {}):
            yield tid, story


def sample_story(persona_dir, story_id):
    backlog = BT.B.build(str(persona_dir))["backlog"]
    return next(s for s in BT.stories_of(backlog) if s["id"] == story_id)


class OnePermissionPerToolTests(unittest.TestCase):
    """No two tasks in a story state different permissions for one tool."""

    def test_tool_tasks_state_the_levelled_permission(self):
        for name, _, _, levelled, backlog, _ in Runs.get():
            for tid, story in task_stories(backlog, levelled):
                tools = story_tools(levelled, tid)
                seen = {}
                for item in story["tasks"]:
                    if item["template"] not in TOOL_TEMPLATES:
                        continue
                    key = item["id"].split(".", 2)[2]
                    with self.subTest(scenario=name, task=item["id"]):
                        self.assertNotIn(key, seen, "two tool tasks for %s" % key)
                        seen[key] = TOOL_TEMPLATES[item["template"]]
                        self.assertEqual(seen[key], permission(tools[key]))

    def test_no_other_task_states_a_second_permission(self):
        for name, _, _, levelled, backlog, _ in Runs.get():
            for tid, story in task_stories(backlog, levelled):
                tools = story_tools(levelled, tid)
                writes = dict((k, t) for k, t in tools.items() if t["use"] != "read")
                texts = [("fields.delivery", story["fields"].get("delivery") or "")]
                for item in story["tasks"]:
                    if item["template"] in TOOL_TEMPLATES:
                        continue
                    texts += [(item["id"], step["text"]) for step in item["how"]]
                    texts.append((item["id"], item["done_when"]))
                for where, text in texts:
                    for clause in clauses(text):
                        if "moves up" in clause or "opens at level" in clause or "open at level" in clause:
                            continue
                        stated = set(STATED.findall(NEVER.sub("", clause)))
                        if not stated:
                            continue
                        named = [k for k in tools if re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(k), clause)]
                        if not named and re.search(r"\bsend tool", clause):
                            named = [k for k, t in writes.items() if t["use"] == "send"]
                        if not named and re.search(r"\bwrite tools?\b", clause):
                            named = list(writes)
                        for key in named:
                            with self.subTest(scenario=name, where=where, tool=key, clause=clause):
                                self.assertEqual(stated, {PERMISSION_NAMES[permission(tools[key])]},
                                                 "%s states %s for %s, levelled %s"
                                                 % (where, sorted(stated), key, permission(tools[key])))


class DeliveryTests(unittest.TestCase):
    def test_every_task_story_has_one_delivery_form(self):
        for name, _, _, levelled, backlog, md in Runs.get():
            for tid, story in task_stories(backlog, levelled):
                with self.subTest(scenario=name, story=story["id"]):
                    sentence = story["fields"].get("delivery")
                    self.assertIsInstance(sentence, str, "no delivery field")
                    forms = [form for form, pattern in FORMS.items() if pattern.match(sentence)]
                    self.assertEqual(len(forms), 1, sentence)
                    self.assertEqual(forms[0], expected_form(levelled, tid), sentence)
                    drafts = [t for t in story["tasks"] if t["template"] == "deliver-draft"]
                    self.assertEqual(len(drafts), 1 if forms[0] == "person-sends" else 0, story["id"])
                    self.assertIn("| Delivery | ", md)

    def test_the_sentence_names_the_tools_and_when_they_open(self):
        for name, _, _, levelled, backlog, _ in Runs.get():
            for tid, story in task_stories(backlog, levelled):
                sentence = story["fields"].get("delivery") or ""
                writes = dict((k, t) for k, t in story_tools(levelled, tid).items() if t["use"] != "read")
                form = expected_form(levelled, tid)
                with self.subTest(scenario=name, story=story["id"]):
                    if form == "twin-writes":
                        for key, tool in writes.items():
                            self.assertIn("%s (%s)" % (key, PERMISSION_NAMES[permission(tool)]), sentence)
                    if form == "person-sends":
                        blocked = [t for t in writes.values() if permission(t) == "blocked"]
                        for tool in blocked:
                            self.assertIn(tool_id(tool), sentence)
                        if all(opens(t) for t in blocked):
                            self.assertRegex(sentence, r"opens? at level 2")
                        if not any(opens(t) for t in blocked):
                            self.assertIn("not planned at any level", sentence)

    def test_deliver_draft_links_autonomy_and_the_destination(self):
        library = dict((t["id"], t) for t in BT.B.load_library()["templates"])
        template = library.get("deliver-draft")
        self.assertIsNotNone(template, "no deliver-draft template")
        self.assertEqual((template["owner_role"], template["part"]), ("business-owner", "A4"))
        found = 0
        for name, _, card, levelled, backlog, _ in Runs.get():
            destinations = dict((t["id"], (t.get("output") or {}).get("destination")) for t in card["tasks"])
            for tid, story in task_stories(backlog, levelled):
                for item in story["tasks"]:
                    if item["template"] != "deliver-draft":
                        continue
                    found += 1
                    links = [s["link"] or "" for s in item["how"]]
                    with self.subTest(scenario=name, task=item["id"]):
                        self.assertTrue([l for l in links if l.startswith("docs/compendium/06-autonomy.md")])
                        self.assertTrue([s for s in item["how"] if destinations[tid] in s["text"]],
                                        "no step names the destination %r" % destinations[tid])
        self.assertGreater(found, 0)

    def test_the_samples(self):
        self.assertTrue(FORMS["person-sends"].match(sample_story(BT.PE, "S-T3")["fields"].get("delivery") or ""))
        self.assertTrue(FORMS["runtime-posts"].match(sample_story(BT.TEAM, "S-C2")["fields"].get("delivery") or ""))

    def test_team_c2_ends_in_one_posting_route(self):
        """A warning in the routine's story that names another route says it applies only without the routine."""
        story = sample_story(BT.TEAM, "S-C2")
        for item in story["tasks"]:
            if item["template"] in TOOL_TEMPLATES:
                continue
            for text in [s["text"] for s in item["how"]] + [item["done_when"], item["title"]]:
                for clause in clauses(text):
                    other = ("Slack MCP server" in clause or
                             (re.search(r"\bsend tool", clause) and
                              re.search(r"Needs approval|Always allow", NEVER.sub("", clause))))
                    if other:
                        with self.subTest(task=item["id"], clause=clause):
                            self.assertIn("only if the routine route is not used", text)


class AcceptanceTests(unittest.TestCase):
    MARKER = "Plus: every write carries the twin marker."
    NOTHING = "Plus: the twin writes nothing to the CRM at the starting level; a person files the result."

    def test_the_marker_line_needs_an_open_crm_write(self):
        for name, profile, _, levelled, backlog, _ in Runs.get():
            kinds = dict((s.get("id"), s.get("kind")) for s in profile.get("systems") or [])
            for tid, story in task_stories(backlog, levelled):
                crm = [t for t in story_tools(levelled, tid).values()
                       if t["use"] != "read" and kinds.get(t["system"]) == "crm"]
                with self.subTest(scenario=name, story=story["id"]):
                    if not crm:
                        self.assertNotIn(self.MARKER, story["acceptance"])
                        self.assertNotIn(self.NOTHING, story["acceptance"])
                        continue
                    open_now = any(permission(t) != "blocked" for t in crm)
                    self.assertEqual(self.MARKER in story["acceptance"], open_now)
                    self.assertEqual(self.NOTHING in story["acceptance"], not open_now)
                    markers = [t for t in story["tasks"] if t["template"].startswith("twin-marker-")]
                    if open_now or any(opens(t) for t in crm):
                        self.assertTrue(markers, "the CRM write opens, but no twin-marker task")
                    else:
                        self.assertFalse(markers, "the CRM write never opens, but a twin-marker task is kept")
                    if not open_now:
                        for item in markers:
                            first = item["how"][0]["text"]
                            self.assertIn("Blocked at the starting level", first, item["id"])


class LinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.library = BT.B.load_library()
        cls.templates = dict((t["id"], t) for t in cls.library["templates"])

    def test_no_library_step_has_a_null_link(self):
        for template in self.library["templates"]:
            for index, step in enumerate(template["how"]):
                with self.subTest(template=template["id"], step=index + 1):
                    self.assertTrue(isinstance(step["link"], str) and step["link"].strip(), step["text"])

    def test_no_generated_step_has_a_null_link(self):
        for name, _, _, _, backlog, _ in Runs.get():
            for item in BT.tasks_of(backlog):
                for step in item["how"]:
                    with self.subTest(scenario=name, task=item["id"], step=step["text"]):
                        self.assertTrue(step["link"])

    def test_every_how_link_resolves(self):
        targets = set()
        for template in self.library["templates"]:
            for step in template["how"]:
                targets.update(expand(step["link"], template["when"]))
        for name, _, _, _, backlog, _ in Runs.get():
            for item in BT.tasks_of(backlog):
                targets.update(step["link"] for step in item["how"] if step["link"])
        targets.discard(None)
        for target in sorted(targets):
            with self.subTest(link=target):
                self.assertFalse(target.startswith("/") or "://" in target or "{" in target, target)
                self.assertIsNone(BT.link_problem(target))
        files = set(t.partition("#")[0] for t in targets)
        for path in sorted(set(SETUP_RUNBOOKS.values()) | set(PILOT_TEMPLATES.values()) |
                           set(PACK_RUNBOOKS.values())):
            self.assertIn(path, files, "no step links %s" % path)

    def test_setup_and_pilot_templates_link_their_kit_page(self):
        for tid, page in list(SETUP_RUNBOOKS.items()) + list(PILOT_TEMPLATES.items()):
            with self.subTest(template=tid):
                links = [s["link"] or "" for s in self.templates[tid]["how"]]
                self.assertTrue([l for l in links if l.partition("#")[0] == page], links)
        for tid, page in SETUP_RUNBOOKS.items():
            anchors = [l.partition("#")[2] for l in (s["link"] or "" for s in self.templates[tid]["how"])
                       if l.partition("#")[0] == page]
            with self.subTest(template=tid):
                self.assertTrue(all(anchors), "a link to %s names no heading" % page)
                self.assertIn("steps", anchors)

    def test_no_step_says_no_runbook_where_one_exists(self):
        for template in self.library["templates"]:
            if template["id"] in ("connect-no-runbook", "warning-claude-code-not-in-role"):
                continue
            text = " ".join([template["title"]] + [s["text"] for s in template["how"]])
            with self.subTest(template=template["id"]):
                self.assertNotRegex(text.lower(), r"no (kit )?runbook")

    def test_pack_runbooks(self):
        for pack in ("general", "b2b-software"):
            for default in BT.load(PACKS_DIR / ("%s.json" % pack))["connector_defaults"]:
                if default["product"] in PACK_RUNBOOKS:
                    with self.subTest(pack=pack, product=default["product"]):
                        self.assertEqual(default["runbook"], PACK_RUNBOOKS[default["product"]])

    def test_each_pack_runbook_has_exactly_one_connect_template(self):
        connect = [t for t in self.library["templates"] if t["id"].startswith("connect-")]
        known = set(BT.B.allowed_facts("task-story", "connector"))
        for runbook, kind in sorted(pack_runbooks().items()) + [(None, "crm"), (None, "product-data")]:
            facts = dict((name, None) for name in known)
            facts.update({"connector.runbook": runbook, "connector.kind": kind, "connector.access": "read"})
            matching = [t["id"] for t in connect if BT.L.matches(t["when"], facts, known)]
            with self.subTest(runbook=runbook, kind=kind):
                self.assertEqual(len(matching), 1, matching)
        generic = self.templates.get("connect-kit-runbook")
        self.assertIsNotNone(generic, "no connect-kit-runbook template")
        links = [s["link"] for s in generic["how"]]
        self.assertEqual(links[:3], [RUNBOOK_PLACEHOLDER + a for a in RUNBOOK_HEADINGS[:3]])

    def test_team_publish_links_the_team_section(self):
        backlog = BT.B.build(str(BT.TEAM))["backlog"]
        publish = [t for t in BT.tasks_of(backlog) if t["template"].startswith("publish-in-role-plugin")]
        self.assertTrue(publish)
        for item in publish:
            links = [s["link"] for s in item["how"]]
            self.assertIn("starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member",
                          links)
            self.assertFalse([l for l in links if "#6-publish" in l], links)

    def test_usage_db_gets_our_own_server(self):
        story = sample_story(BT.TEAM, "S-C2")
        item = next(t for t in story["tasks"] if t["template"].startswith("connect-") and t["id"].endswith("usage-db"))
        self.assertEqual(item["how"][0]["link"], "docs/compendium/11-connectors.md#building-our-own-mcp-server")

    def test_private_network_allowlist_names_salesforce_only_for_salesforce(self):
        story = sample_story(BT.TEAM, "S-C2")
        item = next(t for t in story["tasks"] if t["template"] == "warning-private-network-allowlist")
        links = [s["link"] for s in item["how"]]
        self.assertIn("docs/compendium/11-connectors.md#adding-a-connector-that-isnt-in-the-directory", links)
        self.assertFalse([l for l in links if "salesforce" in l], links)

        def salesforce_private(profile, card):
            profile["network"]["can_allowlist_anthropic_ips"] = True
            profile["provenance"]["network.can_allowlist_anthropic_ips"] = {
                "status": "answered", "source": "discovery.md#E6"}
            next(s for s in profile["systems"] if s["id"] == "salesforce")["private_network"] = True
        with BT.Scenario(BT.PE, salesforce_private) as persona:
            backlog = BT.B.build(str(persona))["backlog"]
        items = [t for t in BT.tasks_of(backlog) if t["template"] == "warning-private-network-allowlist"]
        self.assertTrue(items)
        for item in items:
            self.assertIn("starter-kit/runbooks/salesforce-hosted-mcp.md#8-ip-allowlist-discovery-e6",
                          [s["link"] for s in item["how"]])


class OwnerTests(unittest.TestCase):
    def test_owner_name_and_acting_owner(self):
        for name, profile, card, levelled, backlog, md in Runs.get():
            owners = profile.get("owners") or {}
            technical = owners.get("technical_owner") or None
            skill_owners = dict((t["id"], t.get("skill_owner")) for t in card["tasks"])
            counted = {}
            for story in BT.stories_of(backlog):
                tid = story["id"][2:]
                for item in story["tasks"]:
                    role = item["owner_role"]
                    with self.subTest(scenario=name, task=item["id"]):
                        self.assertIn("owner_name", item)
                        self.assertIn("acting_owner", item)
                        if role in PROFILE_ROLES and owners.get(PROFILE_ROLES[role]):
                            self.assertEqual(item["owner_name"], owners[PROFILE_ROLES[role]])
                        elif role == "skill-owner" and tid in skill_owners and skill_owners[tid]:
                            self.assertEqual(item["owner_name"], skill_owners[tid])
                        else:
                            self.assertIsNone(item["owner_name"])
                        if role in PARTNER_ROLES:
                            self.assertIsNone(item["acting_owner"])
                        if role in ACTING_ROLES:
                            self.assertEqual(item["acting_owner"], technical)
                        if item["owner_name"] is None and role not in PARTNER_ROLES:
                            counted[role] = counted.get(role, 0) + 1
            with self.subTest(scenario=name):
                unnamed = backlog.get("unnamed_roles")
                self.assertIsInstance(unnamed, list)
                listed = dict((r["role"], r) for r in unnamed)
                for role in PARTNER_ROLES:
                    self.assertNotIn(role, listed)
                for role in ACTING_ROLES:
                    if role in counted:
                        self.assertEqual(listed[role]["tasks"], counted[role])
                        self.assertEqual(listed[role]["acting_owner"], technical)
                for role, entry in listed.items():
                    self.assertEqual(list(entry), ["role", "tasks", "acting_owner"])
                    self.assertEqual(entry["tasks"], counted.get(role), role)
                self.assertEqual(md.count("Roles with no named person"), 1)

    def test_the_team_sample_names_its_people(self):
        backlog = BT.B.build(str(BT.TEAM))["backlog"]
        md = BT.B.render_md(backlog)
        review = next(t for t in BT.tasks_of(backlog) if t["id"] == "S-connectors-and-identity.connector-review")
        self.assertEqual(review.get("acting_owner"), "Teodor Amsel (IT and operations lead)")
        persona_review = next(t for t in BT.tasks_of(backlog) if t["id"] == "S-persona-voice.persona-review")
        self.assertEqual(persona_review.get("owner_name"), "Marisol Quenby (Customer success team lead)")
        self.assertIn("(owner: business-owner, Marisol Quenby (Customer success team lead), part A1)", md)


class PartTests(unittest.TestCase):
    def test_confirm_unverified_decision_takes_the_part_of_its_decision(self):
        found = 0
        for name, _, _, _, backlog, _ in Runs.get():
            for item in BT.tasks_of(backlog):
                if item["template"] != "confirm-unverified-decision":
                    continue
                found += 1
                decision = item["id"].split(".confirm-unverified-decision.", 1)[1]
                want = "A3" if decision.startswith("connectors.") else DECISION_PARTS[decision]
                with self.subTest(scenario=name, task=item["id"]):
                    self.assertEqual(item["part"], want)
        self.assertGreater(found, 0)

    def test_high_cost_ceiling_is_a_guardrail(self):
        library = dict((t["id"], t) for t in BT.B.load_library()["templates"])
        self.assertEqual(library["warning-high-cost-ceiling-unconfirmed"]["part"], "A7")


def general_only_count(backlog):
    """Tasks whose every link is a general page (no link into a kit runbook, template, plugin, setting or engagement)."""
    return sum(1 for item in BT.tasks_of(backlog)
               if not any((s["link"] or "").startswith(GENERAL_PREFIXES) for s in item["how"]))


if __name__ == "__main__":
    unittest.main()
