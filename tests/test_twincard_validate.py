"""Tests for the twincard field catalogue, templates, validator and validate CLI.

The design of record is partner-kit/docs/design.md (sections 4 and 5 define the
two records and the field catalogue).

Standard library only. Run with: python3 -m unittest discover -s tests
"""

import copy
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN_DIR = ROOT / "partner-kit" / "plugins" / "twin-consultant"
SCRIPTS_DIR = PLUGIN_DIR / "scripts"
CLI = SCRIPTS_DIR / "twincard" / "cli.py"
FIELDS_JSON = PLUGIN_DIR / "data" / "fields.json"
CARD_TEMPLATE = PLUGIN_DIR / "templates" / "card.json"
PROFILE_TEMPLATE = PLUGIN_DIR / "templates" / "customer-profile.json"
DISCOVERY = ROOT / "docs" / "playbook" / "02-discovery.md"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from twincard import fields as tc_fields  # noqa: E402
from twincard.validate import validate  # noqa: E402

# Interview-guide question ids (design section 6).
INTERVIEW_IDS = {"P%d" % n for n in range(1, 7)} | {"F%d" % n for n in range(1, 10)}

# The feeds vocabulary (design section 5).
RULE_DECISIONS = {"runtime", "identity", "autonomy", "data_controls", "connectors", "memory", "plan_fit"}
BACKLOG_LEVELS = {"epic", "feature", "story", "task"}
DASHBOARD_SECTIONS = {"header", "anatomy", "features", "blockers", "backlog", "open_questions", "provenance"}
FEEDS = (
    {"rule:" + d for d in RULE_DECISIONS}
    | {"backlog:" + level for level in BACKLOG_LEVELS}
    | {"dashboard:" + s for s in DASHBOARD_SECTIONS}
    | {"voice"}
)
PARTS = {"A%d" % n for n in range(1, 10)} | {"context"}


def discovery_ids():
    ids = set()
    for line in DISCOVERY.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\|\s*([A-G]\d+)\s*\|", line)
        if match:
            ids.add(match.group(1))
    return ids


def template_paths(value, prefix=""):
    """Flatten a template into catalogue paths. Lists of objects use their first example object."""
    paths = set()
    if isinstance(value, dict):
        for key, child in value.items():
            path = prefix + "." + key if prefix else key
            paths |= template_paths(child, path)
        return paths
    if isinstance(value, list) and value and isinstance(value[0], dict):
        return template_paths(value[0], prefix + "[]")
    paths.add(prefix)
    return paths


# --- A complete, valid customer profile and persona card -------------------------

PROFILE_REQUIRED = [
    "display_name", "industry", "plan.tier", "identity.sso", "identity.scim", "devices.mdm",
    "compliance.data_classes", "compliance.phi", "compliance.baa", "compliance.mnpi",
    "compliance.retention", "compliance.walls",
    "systems.crm.kind", "systems.crm.product", "systems.crm.edition", "systems.crm.private_network",
    "network.can_allowlist_anthropic_ips",
]

CARD_REQUIRED = [
    "role.name", "role.team", "role.works_in", "role.device", "outcome.sponsor_goal",
    "voice.serves", "voice.jobs", "voice.tone", "voice.norms", "voice.never",
    "voice.ask_before", "voice.escalate_to",
    "tasks.T1.trigger", "tasks.T1.inputs.crm.access", "tasks.T1.output.audience",
    "tasks.T1.writes.crm.action", "tasks.T1.data_class", "tasks.T1.cost_of_mistake.level",
    "tasks.T1.reversible", "tasks.T1.touches_money", "tasks.T1.reads_untrusted_input",
    "tasks.T1.in_pilot", "memory.personal_memory_wanted",
]


def answered(paths, source):
    return {path: {"status": "answered", "source": source} for path in paths}


def valid_profile():
    return {
        "profile_version": 1,
        "customer": "sample-co",
        "display_name": "Sample Co",
        "fictional": True,
        "industry": "general",
        "plan": {"tier": "enterprise", "seats": 40, "individual_accounts_on_domain": 0},
        "identity": {"idp": "okta", "sso": True, "scim": True},
        "devices": {"mdm": "intune", "managed_share": "all staff", "unmanaged_users": "none"},
        "compliance": {
            "data_classes": ["internal", "confidential"],
            "phi": False, "baa": False, "mnpi": False,
            "retention": "standard", "walls": "none",
        },
        "systems": [
            {"id": "crm", "kind": "crm", "product": "Salesforce", "edition": "Enterprise",
             "access_model": "roles and sharing rules", "private_network": False},
        ],
        "network": {"can_allowlist_anthropic_ips": True},
        "governance": {"log_destination": "SIEM", "existing_source_audit": "none",
                       "spend_owner": "IT", "spend_limits": "per user"},
        "owners": {"sponsor": "Sponsor", "technical_owner": "Tech", "business_owner": "Biz",
                   "backup_owner": "Backup", "compliance": "Compliance"},
        "provenance": answered(PROFILE_REQUIRED, "discovery#A1"),
    }


def valid_card():
    return {
        "card_version": 1,
        "id": "analyst",
        "customer": "sample-co",
        "role": {"name": "Analyst", "team": "Research", "headcount": 10, "pilot_users": 3,
                 "works_in": ["claude-code", "desktop"], "device": "managed"},
        "outcome": {"sponsor_goal": "Less time on prep",
                    "scorecard_targets": [{"metric": "edit_rate_below_pct", "value": 30}]},
        "voice": {"serves": "Analysts", "jobs": ["Prepare briefs"], "tone": "Direct",
                  "norms": ["Cite every source"], "never": ["Send email"],
                  "ask_before": ["Updating the CRM"], "escalate_to": ["Team lead"]},
        "features": [{"id": "prep", "name": "Preparation", "why": "Saves time"}],
        "tasks": [{
            "id": "T1", "feature": "prep", "name": "Prepare a brief",
            "frequency_per_week": 4, "minutes_each": 90, "users": 3,
            "trigger": "person",
            "inputs": [{"system": "crm", "objects": "account", "access": "read"}],
            "output": {"what": "Brief", "audience": "internal", "destination": "none"},
            "writes": [{"system": "crm", "objects": "task", "action": "create"}],
            "data_class": "confidential",
            "cost_of_mistake": {"level": "medium", "what_happens": "Rework"},
            "reversible": True, "touches_money": False, "reads_untrusted_input": False,
            "examples": {"good": 2, "bad": 1, "where": "shared drive"},
            "skill_owner": "Analyst lead", "priority": 1, "in_pilot": True,
        }],
        "memory": {"personal_memory_wanted": False, "notes": ""},
        "overrides": [{"task": "T1", "decision": "autonomy.start", "value": 1,
                       "reason": "Pilot", "approved_by": "Business owner"}],
        "open_questions": [{"id": "OQ-1", "question": "Which template?", "blocks": ["T1"],
                            "owner": "Consultant", "due": "2026-12-04"}],
        "provenance": answered(CARD_REQUIRED, "interviews/2026-11-14-analyst.md#F1"),
    }


class PersonaFolder:
    """A temporary engagements/<customer>/personas/<persona> folder."""

    def __init__(self, profile, card, customer_folder="acme", profile_text=None, card_text=None):
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name) / "engagements" / customer_folder
        self.persona_dir = base / "personas" / "analyst"
        self.persona_dir.mkdir(parents=True)
        (base / "customer-profile.json").write_text(
            profile_text if profile_text is not None else json.dumps(profile), encoding="utf-8")
        (self.persona_dir / "card.json").write_text(
            card_text if card_text is not None else json.dumps(card), encoding="utf-8")

    def __enter__(self):
        return self.persona_dir

    def __exit__(self, *exc):
        self._tmp.cleanup()


def run_validate(profile=None, card=None, **kwargs):
    profile = valid_profile() if profile is None else profile
    card = valid_card() if card is None else card
    with PersonaFolder(profile, card, **kwargs) as persona_dir:
        return validate(str(persona_dir))


# --- The catalogue --------------------------------------------------------------

class CatalogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalogue = json.loads(FIELDS_JSON.read_text(encoding="utf-8"))
        cls.entries = cls.catalogue["fields"]

    def test_loader_reads_the_same_file(self):
        self.assertEqual(tc_fields.load_catalogue()["fields"], self.entries)

    def test_entries_have_the_catalogue_shape(self):
        keys = {"path", "record", "type", "values", "required", "asked_by", "default", "feeds", "part"}
        paths = set()
        for entry in self.entries:
            with self.subTest(path=entry.get("path")):
                self.assertEqual(set(entry), keys)
                self.assertIn(entry["record"], ("profile", "card"))
                self.assertIn(entry["part"], PARTS)
                self.assertIsInstance(entry["required"], bool)
                if entry["type"] in ("enum", "enum-list"):
                    self.assertTrue(entry["values"], "an enumeration lists its values")
                key = (entry["record"], entry["path"])
                self.assertNotIn(key, paths, "paths are unique within a record")
                paths.add(key)

    def test_every_entry_is_asked_or_has_a_sourced_default(self):
        for entry in self.entries:
            with self.subTest(path=entry["path"]):
                if entry["asked_by"]:
                    continue
                default = entry["default"]
                self.assertIsInstance(default, dict, "no asked_by, so a default with a source")
                source = default.get("source", "")
                self.assertTrue(source.startswith(("docs/compendium/", "docs/playbook/")), source)
                self.assertTrue((ROOT / source.split("#")[0]).is_file(), source)

    def test_asked_by_ids_exist(self):
        known = discovery_ids() | INTERVIEW_IDS
        self.assertIn("A1", known)
        self.assertIn("G4", known)
        for entry in self.entries:
            for qid in entry["asked_by"]:
                with self.subTest(path=entry["path"], question=qid):
                    self.assertIn(qid, known)

    def test_every_entry_feeds_something_from_the_vocabulary(self):
        for entry in self.entries:
            with self.subTest(path=entry["path"]):
                self.assertTrue(entry["feeds"], "a field nothing reads is deleted")
                for feed in entry["feeds"]:
                    self.assertIn(feed, FEEDS)

    def test_templates_and_catalogue_agree(self):
        envelope = self.catalogue["envelope"]
        for record, template in (("profile", PROFILE_TEMPLATE), ("card", CARD_TEMPLATE)):
            with self.subTest(record=record):
                data = json.loads(template.read_text(encoding="utf-8"))
                for key in envelope[record]:
                    self.assertIn(key, data)
                    del data[key]
                in_template = template_paths(data)
                in_catalogue = {e["path"] for e in self.entries if e["record"] == record}
                self.assertEqual(in_template - in_catalogue, set(), "in the template, not the catalogue")
                self.assertEqual(in_catalogue - in_template, set(), "in the catalogue, not the template")

    def test_templates_are_blank(self):
        def leaves(value):
            if isinstance(value, dict):
                for child in value.values():
                    yield from leaves(child)
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                self.assertEqual(len(value), 1, "one example object per list")
                yield from leaves(value[0])
            else:
                yield value
        envelope = self.catalogue["envelope"]
        for record, template in (("profile", PROFILE_TEMPLATE), ("card", CARD_TEMPLATE)):
            data = json.loads(template.read_text(encoding="utf-8"))
            for key in envelope[record]:
                data.pop(key)
            for leaf in leaves(data):
                self.assertIn(leaf, ("", None, []))

    def test_writes_have_system_objects_action(self):
        writes = {e["path"] for e in self.entries if e["path"].startswith("tasks[].writes[].")}
        self.assertEqual(writes, {"tasks[].writes[].system", "tasks[].writes[].objects",
                                  "tasks[].writes[].action"})


# --- The validator --------------------------------------------------------------

class ValidCardTests(unittest.TestCase):
    def test_complete_card_passes_at_100_percent(self):
        result = run_validate()
        self.assertEqual(result["errors"], [])
        self.assertTrue(result["ok"])
        completeness = result["completeness"]
        self.assertEqual(completeness["required"], len(PROFILE_REQUIRED) + len(CARD_REQUIRED))
        self.assertEqual(completeness["satisfied"], completeness["required"])
        self.assertEqual(completeness["percent"], 100)
        self.assertEqual(completeness["missing"], [])

    def test_individual_plan_passes_with_a_warning(self):
        profile = valid_profile()
        profile["plan"]["tier"] = "individual"
        result = run_validate(profile=profile)
        self.assertEqual(result["errors"], [])
        self.assertIn("plan.tier", [w["path"] for w in result["warnings"]])


class FailingCardTests(unittest.TestCase):
    def assertError(self, result, path, record=None):
        errors = result["errors"]
        found = [e for e in errors if e["path"] == path and (record is None or e["record"] == record)]
        self.assertTrue(found, "expected an error at %r; got %r" % (path, [e["path"] for e in errors]))
        for error in found:
            self.assertTrue(error["message"])
            self.assertTrue(error["fix"])
        self.assertFalse(result["ok"])

    def test_card_does_not_parse(self):
        self.assertError(run_validate(card_text="{not json"), "card.json", "card")

    def test_profile_does_not_parse(self):
        self.assertError(run_validate(profile_text="[1, 2"), "customer-profile.json", "profile")

    def test_required_field_missing(self):
        card = valid_card()
        del card["voice"]["tone"]
        self.assertError(run_validate(card=card), "voice.tone", "card")

    def test_required_field_empty(self):
        profile = valid_profile()
        profile["display_name"] = ""
        self.assertError(run_validate(profile=profile), "display_name", "profile")

    def test_wrong_type(self):
        card = valid_card()
        card["role"]["headcount"] = "ten"
        self.assertError(run_validate(card=card), "role.headcount", "card")

    def test_boolean_is_not_an_integer(self):
        card = valid_card()
        card["tasks"][0]["users"] = True
        self.assertError(run_validate(card=card), "tasks.T1.users", "card")

    def test_value_not_in_enumeration(self):
        card = valid_card()
        card["tasks"][0]["trigger"] = "sometimes"
        self.assertError(run_validate(card=card), "tasks.T1.trigger", "card")

    def test_list_value_not_in_enumeration(self):
        card = valid_card()
        card["role"]["works_in"] = ["fax"]
        self.assertError(run_validate(card=card), "role.works_in", "card")

    def test_profile_enumeration(self):
        profile = valid_profile()
        profile["compliance"]["retention"] = "forever"
        self.assertError(run_validate(profile=profile), "compliance.retention", "profile")

    def test_customer_mismatch(self):
        card = valid_card()
        card["customer"] = "other-co"
        self.assertError(run_validate(card=card), "customer", "card")

    def test_input_system_not_in_profile(self):
        card = valid_card()
        card["tasks"][0]["inputs"][0]["system"] = "erp"
        card["provenance"]["tasks.T1.inputs.erp.access"] = card["provenance"].pop("tasks.T1.inputs.crm.access")
        self.assertError(run_validate(card=card), "tasks.T1.inputs.erp.system", "card")

    def test_write_system_not_in_profile(self):
        card = valid_card()
        card["tasks"][0]["writes"][0]["system"] = "erp"
        card["provenance"]["tasks.T1.writes.erp.action"] = card["provenance"].pop("tasks.T1.writes.crm.action")
        self.assertError(run_validate(card=card), "tasks.T1.writes.erp.system", "card")

    def test_write_action_not_in_enumeration(self):
        card = valid_card()
        card["tasks"][0]["writes"][0]["action"] = "archive"
        self.assertError(run_validate(card=card), "tasks.T1.writes.crm.action", "card")

    def test_task_feature_not_a_feature(self):
        card = valid_card()
        card["tasks"][0]["feature"] = "nope"
        self.assertError(run_validate(card=card), "tasks.T1.feature", "card")

    def test_duplicate_task_ids(self):
        card = valid_card()
        card["tasks"].append(copy.deepcopy(card["tasks"][0]))
        self.assertError(run_validate(card=card), "tasks.T1.id", "card")

    def test_duplicate_system_ids(self):
        profile = valid_profile()
        profile["systems"].append(copy.deepcopy(profile["systems"][0]))
        self.assertError(run_validate(profile=profile), "systems.crm.id", "profile")

    def test_task_without_id(self):
        card = valid_card()
        card["tasks"][0]["id"] = ""
        self.assertError(run_validate(card=card), "tasks[0].id", "card")

    def test_override_names_missing_task(self):
        card = valid_card()
        card["overrides"][0]["task"] = "T9"
        self.assertError(run_validate(card=card), "overrides[0].task", "card")

    def test_override_decision_not_in_enumeration(self):
        card = valid_card()
        card["overrides"][0]["decision"] = "mood"
        self.assertError(run_validate(card=card), "overrides[0].decision", "card")

    def test_open_question_blocks_missing_task(self):
        card = valid_card()
        card["open_questions"][0]["blocks"] = ["T9"]
        self.assertError(run_validate(card=card), "open_questions.OQ-1.blocks", "card")

    def test_required_field_without_provenance(self):
        card = valid_card()
        del card["provenance"]["voice.tone"]
        self.assertError(run_validate(card=card), "voice.tone", "card")

    def test_profile_required_field_without_provenance(self):
        profile = valid_profile()
        del profile["provenance"]["systems.crm.edition"]
        self.assertError(run_validate(profile=profile), "systems.crm.edition", "profile")

    def test_provenance_status_unknown(self):
        card = valid_card()
        card["provenance"]["voice.tone"] = {"status": "guessed", "source": "x"}
        self.assertError(run_validate(card=card), "voice.tone", "card")

    def test_assumed_needs_owner(self):
        card = valid_card()
        card["provenance"]["voice.tone"] = {"status": "assumed", "source": "consultant"}
        self.assertError(run_validate(card=card), "voice.tone", "card")

    def test_open_needs_owner(self):
        card = valid_card()
        card["provenance"]["voice.tone"] = {"status": "open", "due": "2026-12-01"}
        self.assertError(run_validate(card=card), "voice.tone", "card")

    def test_open_needs_due_date_in_iso_form(self):
        for due in (None, "next week", "2026-13-40"):
            with self.subTest(due=due):
                card = valid_card()
                entry = {"status": "open", "owner": "Consultant"}
                if due is not None:
                    entry["due"] = due
                card["provenance"]["voice.tone"] = entry
                self.assertError(run_validate(card=card), "voice.tone", "card")

    def test_sample_engagement_must_be_fictional(self):
        profile = valid_profile()
        profile["fictional"] = False
        result = run_validate(profile=profile, customer_folder="sample-acme")
        self.assertError(result, "fictional", "profile")
        self.assertTrue(run_validate(profile=profile)["ok"], "outside sample-* fictional may be false")


class CompletenessTests(unittest.TestCase):
    def test_assumed_and_open_count_against_completeness(self):
        card = valid_card()
        card["provenance"]["voice.tone"] = {"status": "assumed", "source": "consultant", "owner": "Lead"}
        card["provenance"]["tasks.T1.trigger"] = {"status": "assumed", "owner": "Lead"}
        card["role"]["device"] = None
        card["provenance"]["role.device"] = {"status": "open", "owner": "IT", "due": "2026-12-01"}
        profile = valid_profile()
        profile["provenance"]["plan.tier"] = {"status": "default", "source": "docs/compendium/09-plans-and-it-controls.md"}
        result = run_validate(profile=profile, card=card)
        self.assertEqual(result["errors"], [])
        completeness = result["completeness"]
        required = len(PROFILE_REQUIRED) + len(CARD_REQUIRED)
        self.assertEqual(completeness["required"], required)
        self.assertEqual(completeness["satisfied"], required - 3)
        self.assertEqual(completeness["percent"], (required - 3) * 100 // required)
        self.assertEqual(sorted(completeness["missing"]),
                         sorted(["card:voice.tone", "card:tasks.T1.trigger", "card:role.device"]))

    def test_percent_rounds_down(self):
        card = valid_card()
        card["provenance"]["voice.tone"] = {"status": "assumed", "owner": "Lead"}
        result = run_validate(card=card)
        required = result["completeness"]["required"]
        self.assertEqual(result["completeness"]["percent"], (required - 1) * 100 // required)
        self.assertLess(result["completeness"]["percent"], 100)


# --- The CLI --------------------------------------------------------------------

class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(CLI)] + list(args),
            capture_output=True, text=True, cwd=tempfile.gettempdir(), timeout=60,
        )

    def test_valid_card_exits_0(self):
        with PersonaFolder(valid_profile(), valid_card()) as persona_dir:
            proc = self.run_cli("validate", str(persona_dir))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("100%", proc.stdout)

    def test_invalid_card_exits_1_with_next_steps(self):
        card = valid_card()
        card["tasks"][0]["trigger"] = "sometimes"
        with PersonaFolder(valid_profile(), card) as persona_dir:
            proc = self.run_cli("validate", str(persona_dir))
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertRegex(proc.stdout, r"(?m)^card:tasks\.T1\.trigger: .+\. Next: .+")
        self.assertIn("Completeness", proc.stdout)

    def test_json_output(self):
        card = valid_card()
        card["tasks"][0]["trigger"] = "sometimes"
        with PersonaFolder(valid_profile(), card) as persona_dir:
            proc = self.run_cli("validate", "--json", str(persona_dir))
        self.assertEqual(proc.returncode, 1)
        data = json.loads(proc.stdout)
        self.assertIn("tasks.T1.trigger", [e["path"] for e in data["errors"]])
        self.assertIn("percent", data["completeness"])

    def test_usage_errors_exit_2(self):
        self.assertEqual(self.run_cli().returncode, 2)
        self.assertEqual(self.run_cli("level", ".").returncode, 2)
        with tempfile.TemporaryDirectory() as tmp:
            missing = str(Path(tmp) / "no-such-persona")
            self.assertEqual(self.run_cli("validate", missing).returncode, 2)


if __name__ == "__main__":
    unittest.main()
