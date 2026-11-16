"""OPS-68: rule fix texts agree with the backlog, new runbooks are linked, the README lines are pinned.

Residue from the kit-alignment chain and #228 (issue #233). Checks that:

- the two rule fix texts say Blocked where the backlog tasks say Blocked, and the Slack and HubSpot
  rules say what compendium page 11 says;
- evidence-level-2 names no tool setting for a task whose output a routine posts itself;
- the Claude Code step links the runbook the kit now has;
- twin-marker-hubspot and twin-marker-zendesk exist, link real sections, and twin-marker-crm leaves
  HubSpot to the new template, in the Team sample's backlog too;
- both samples' README.md carry the completeness line exactly as validate prints it;
- the spend-limits link, the retention step, the PE design line and the old codes in
  tests/test_partner_kit_skills.py are as the card says.

Standard library only. Run with: python3 -m unittest tests.test_twincard_followups
"""

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "partner-kit" / "plugins" / "twin-consultant"
SCRIPTS = PLUGIN / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from twincard import validate as V  # noqa: E402

RULES = json.loads((PLUGIN / "data" / "rules.json").read_text(encoding="utf-8"))["rules"]
LIBRARY = json.loads((PLUGIN / "data" / "task-library.json").read_text(encoding="utf-8"))["templates"]
PACK = json.loads((PLUGIN / "data" / "industry-packs" / "general.json").read_text(encoding="utf-8"))
PE = ROOT / "engagements" / "sample-pe"
TEAM = ROOT / "engagements" / "sample-team-cs"
PERSONAS = {
    PE: PE / "personas" / "deal-team-associate",
    TEAM: TEAM / "personas" / "customer-success-manager",
}
PAGE_09 = ROOT / "docs" / "compendium" / "09-plans-and-it-controls.md"


def rule(rule_id):
    return next(r for r in RULES if r["id"] == rule_id)


def template(template_id):
    return next((t for t in LIBRARY if t["id"] == template_id), None)


def slug(heading):
    text = re.sub(r"[^a-z0-9 -]", "", heading.lower())
    return text.strip().replace(" ", "-")


def anchors(path):
    found = set()
    fence = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            fence = not fence
            continue
        m = None if fence else re.match(r"^#{1,6} (.+?)\s*$", line)
        if m:
            found.add(slug(m.group(1)))
    return found


def resolves(link):
    """True when a repo-relative link names a file, and an anchor that is a heading in it."""
    target, _, anchor = link.partition("#")
    path = ROOT / target
    if not path.is_file():
        return False
    return not anchor or anchor in anchors(path)


def backlog_tasks(persona_dir):
    found = []

    def walk(node):
        if isinstance(node, dict):
            if "template" in node and "done_when" in node:
                found.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(json.loads((persona_dir / "backlog.json").read_text(encoding="utf-8")))
    return found


class RuleFixTexts(unittest.TestCase):
    def test_untrusted_input_with_send_fix(self):
        self.assertEqual(
            rule("warn-untrusted-input-with-send")["fix"],
            "Keep the send tool Blocked, or at Needs approval once it opens and never Always allow, "
            "and keep the task at level 2 or below.")

    def test_unmanaged_connectors_read_only_fix(self):
        self.assertEqual(
            rule("warn-unmanaged-connectors-read-only")["fix"],
            "Keep the task's write tools Blocked for people on unmanaged devices, or at Needs approval "
            "and never Always allow once the customer has accepted the write in writing; "
            "or split the role by device.")

    def test_slack_rule_says_what_page_11_says(self):
        r = rule("warn-slack-directory-send-unverified")
        self.assertTrue(r["unverified"])
        self.assertEqual(r["then"], "slack-directory-send-unverified")
        for tool in ("slack_send_message", "slack_create_canvas", "slack_update_canvas"):
            self.assertIn(tool, r["reason"])
        self.assertIn("documents only search", r["reason"])
        self.assertNotIn("Whether the Slack directory connector can post is Unverified", r["reason"])
        self.assertEqual(
            r["fix"],
            "Post through Claude Tag or the Slack MCP server, or, if the plan uses the directory "
            "connector's send tool, set it to Blocked or Needs approval after the Slack runbook's check.")

    def test_hubspot_rule_says_what_page_11_says(self):
        r = rule("warn-hubspot-super-admin-approval")
        self.assertEqual(r["then"], "hubspot-super-admin-approval")
        self.assertNotIn("(or a user with App Marketplace access)", r["reason"])
        for phrase in ("App Marketplace Access", "without prior", "a Super Admin must approve"):
            self.assertIn(phrase, r["reason"])
        self.assertIn("Super Admin who approves", r["fix"])


class Templates(unittest.TestCase):
    def test_evidence_level_2_done_when(self):
        self.assertEqual(
            template("evidence-level-2")["done_when"],
            "The business owner has approved the move to level 2 on scorecard evidence, and every write "
            "or send tool the task uses at level 2 is at Needs approval; a task whose output a routine "
            "posts itself changes no tool setting.")

    def test_no_step_says_the_kit_has_no_claude_code_runbook(self):
        stale = "No runbook: the kit has no runbook for giving users a Claude Code seat"
        for t in LIBRARY:
            for step in t["how"]:
                self.assertFalse(step["text"].startswith(stale), t["id"])

    def test_claude_code_step_links_the_runbook(self):
        steps = template("warning-claude-code-not-in-role")["how"]
        step = next(s for s in steps if s["text"].startswith("Give each person a Claude Code seat"))
        self.assertEqual(
            step["text"], "Give each person a Claude Code seat, install it and sign in, as the runbook says.")
        self.assertEqual(step["link"], "starter-kit/runbooks/claude-code-for-a-role.md#steps")
        self.assertTrue(resolves(step["link"]))

    def test_twin_marker_hubspot(self):
        t = template("twin-marker-hubspot")
        self.assertIsNotNone(t)
        self.assertEqual(t["title"], "Create the HubSpot twin marker (Last updated by twin)")
        self.assertEqual(t["per"], "connector")
        self.assertEqual(t["owner_role"], "source-system-admin")
        self.assertEqual(t["part"], template("twin-marker-salesforce")["part"])
        self.assertEqual(t["when"], {"connector.kind": "crm", "connector.product": "HubSpot",
                                     "connector.access": "write", "writes.crm_opens": ["now", "later"]})
        links = [s["link"] for s in t["how"]]
        self.assertIn("starter-kit/connectors/hubspot/README.md#create-it-the-hubspot-admin-does-this", links)
        self.assertIn("starter-kit/connectors/hubspot/README.md#limit-who-can-set-it", links)
        for link in links:
            self.assertTrue(resolves(link), link)
        self.assertTrue(t["done_when"].endswith(".") and t["done_when"].count(". ") == 0)

    def test_twin_marker_zendesk(self):
        t = template("twin-marker-zendesk")
        self.assertIsNotNone(t)
        self.assertEqual(t["title"], "Create the Zendesk twin marker (Last updated by twin field)")
        self.assertEqual(t["per"], "connector")
        self.assertEqual(t["owner_role"], "source-system-admin")
        self.assertEqual(t["part"], template("twin-marker-crm")["part"])
        self.assertEqual(t["when"], {"connector.product": "Zendesk", "connector.access": "write"})
        links = [s["link"] for s in t["how"]]
        self.assertIn("starter-kit/connectors/zendesk/README.md#create-it-the-zendesk-admin-does-this", links)
        self.assertIn("starter-kit/connectors/zendesk/README.md#make-the-skill-set-it", links)
        for link in links:
            self.assertTrue(resolves(link), link)
        self.assertTrue(t["done_when"].endswith(".") and t["done_when"].count(". ") == 0)

    def test_twin_marker_crm_leaves_hubspot_to_the_new_template(self):
        when = template("twin-marker-crm")["when"]
        self.assertEqual(sorted(when["not"]["connector.product"]), ["HubSpot", "Salesforce"])
        self.assertEqual(when["connector.kind"], "crm")
        self.assertEqual(when["writes.crm_opens"], ["now", "later"])

    def test_skill_and_report_markers_keep_their_when(self):
        for template_id in ("twin-marker-skill", "twin-marker-report"):
            self.assertEqual(template(template_id)["when"],
                             {"writes.kinds": "crm", "writes.crm_opens": ["now", "later"]})

    def test_spend_limits_link_follows_page_09(self):
        links = [s["link"] for s in template("spend-limits")["how"]]
        if "## Spend and usage limits" in PAGE_09.read_text(encoding="utf-8").splitlines():
            self.assertIn("docs/compendium/09-plans-and-it-controls.md#spend-and-usage-limits", links)
            self.assertNotIn("docs/compendium/09-plans-and-it-controls.md#feature-matrix", links)
        else:
            self.assertIn("docs/compendium/09-plans-and-it-controls.md#feature-matrix", links)
        self.assertIn("docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often", links)
        for link in links:
            self.assertTrue(resolves(link), link)

    def test_retention_step_gives_the_compliance_api_condition(self):
        step = template("retention-and-feedback-settings")["how"][1]
        self.assertIn("with the Compliance API on", step["text"])
        self.assertIn("local Claude Code and Cowork sessions 6 years", step["text"])
        self.assertEqual(step["link"],
                         "docs/compendium/10-sensitive-data.md#questions-to-settle-with-compliance-and-legal")

    def test_outlook_entry_points_to_section_6a(self):
        entry = self._find_outlook(PACK)
        self.assertIsNotNone(entry)
        self.assertIn("Section 6a of the Microsoft 365 runbook", entry["how"])
        self.assertNotIn("does not cover mail and calendar", entry["how"])

    @staticmethod
    def _find_outlook(node):
        if isinstance(node, dict):
            if node.get("product") == "Outlook" and "how" in node:
                return node
            for value in node.values():
                found = Templates._find_outlook(value)
                if found:
                    return found
        elif isinstance(node, list):
            for value in node:
                found = Templates._find_outlook(value)
                if found:
                    return found
        return None


class TeamBacklogMarkers(unittest.TestCase):
    def setUp(self):
        self.tasks = backlog_tasks(PERSONAS[TEAM])
        self.card = json.loads((PERSONAS[TEAM] / "card.json").read_text(encoding="utf-8"))

    def test_hubspot_write_connector_gets_the_hubspot_marker_and_not_the_crm_one(self):
        hubspot = [t for t in self.tasks if t["template"] == "twin-marker-hubspot"]
        self.assertTrue(hubspot, "no twin-marker-hubspot task in the Team backlog")
        for task in hubspot:
            self.assertIn("hubspot", task["id"])
            self.assertEqual(task["owner_role"], "source-system-admin")
        self.assertEqual([t["id"] for t in self.tasks
                          if t["template"] == "twin-marker-crm" and "hubspot" in t["id"]], [])

    def test_every_hubspot_write_with_an_opening_crm_write_has_a_task(self):
        levelled = json.loads((PERSONAS[TEAM] / "levelled.json").read_text(encoding="utf-8"))
        wanted = set()
        for task_id, task in levelled["tasks"].items():
            for conn in task["connectors"]:
                if conn.get("system") == "hubspot" and conn.get("access") == "write":
                    wanted.add(task_id)
        self.assertTrue(wanted, "the Team sample has no HubSpot write connector")
        have = {t["id"].split(".")[0] for t in self.tasks if t["template"] == "twin-marker-hubspot"}
        self.assertEqual({"S-" + w for w in wanted}, have)


class ReadmeLines(unittest.TestCase):
    def test_each_readme_carries_the_completeness_line_validate_prints(self):
        for sample, persona in PERSONAS.items():
            done = V.validate(str(persona))["completeness"]
            line = "Completeness: %d%% (%d of %d required fields answered or default)" % (
                done["percent"], done["satisfied"], done["required"])
            readme = (sample / "README.md").read_text(encoding="utf-8")
            self.assertIn(line, readme, sample.name)


class PeDesign(unittest.TestCase):
    def test_opentelemetry_line_says_the_metric_list_is_unverified(self):
        text = (PE / "design.md").read_text(encoding="utf-8")
        line = next(l for l in text.splitlines() if l.startswith("| OpenTelemetry (Claude Code, Agent SDK)"))
        self.assertNotIn("Check the exact metric list", line)
        self.assertIn("**⚠ Unverified:** the exact metric list", line)

    def test_eval_copy_is_byte_identical(self):
        copy = (PLUGIN / "skills" / "filling-persona-cards" / "evals" / "files" / "engagements" / "sample-pe"
                / "design.md")
        self.assertEqual(copy.read_bytes(), (PE / "design.md").read_bytes())


class OldCodesInASkillsTest(unittest.TestCase):
    def test_removed_codes_are_gone_from_the_skills_test(self):
        text = (ROOT / "tests" / "test_partner_kit_skills.py").read_text(encoding="utf-8")
        for old in ("connector-cannot-write", "mail-read-only"):
            self.assertNotIn(old, text)


if __name__ == "__main__":
    unittest.main()
