"""Tests for the rule audit of 2026-11-16 (OPS-42): each decision the task card made, on the two fixtures.

Each test changes a fixture in memory (the way the acceptance test's variants do), levels it and checks the
decision value, the rule id and the blocker or warning code. The last class checks every rule's basis and
unverified flag against the cited section.

Standard library only. Run with: python3 -m unittest discover -s tests
"""

import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

import test_twincard_level as LT  # noqa: E402

L = LT.L
PE, TEAM = LT.PE, LT.TEAM
PACKS = LT.PLUGIN_DIR / "data" / "industry-packs"
TASK_LIBRARY = LT.PLUGIN_DIR / "data" / "task-library.json"

PHI_RULES = {"runtime-phi-none", "plan-fit-phi-no-runtime", "block-phi-no-hosted-runtime"}
NEW_CODES = {"high-cost-ceiling-unconfirmed", "scheduled-task-own-environment-only", "zdr-org-not-confirmed",
             "private-network-inside-only", "unmanaged-share-no-access", "confidential-standard-retention",
             "retention-not-covered"}


def level(persona_dir, change=None):
    return LT.run_level(persona_dir, change)


def task_of(out, tid):
    return out["tasks"][tid]


def ids_of(out, kind, code):
    return [item["about"] for item in out[kind] if item["code"] == code]


def rule(rid):
    return next(r for r in LT.load(LT.RULES)["rules"] if r["id"] == rid)


chain = LT.chain


def set_profile(section_name, key, value):
    return LT.profile_set(section_name, key, value)


def set_task(tid, **values):
    return LT.set_task(tid, **values)


def set_cost(tid, level_):
    def change(profile, card):
        LT.task(card, tid)["cost_of_mistake"]["level"] = level_
    return change


set_device = LT.role_device


# --- Engine change 1: strictest with 'undecided' and real values -----------------------------------

class StrictestTests(unittest.TestCase):
    def run_for(self, rules):
        data = {"rules_version": 1, "decisions": {"autonomy.ceiling": {"combine": "strictest"}}, "rules": rules}
        return L._Run(data, L.load_plan_fit(), set())

    def rule(self, rid, then):
        return {"id": rid, "decides": "autonomy.ceiling", "when": {}, "then": then,
                "cite": "docs/compendium/06-autonomy.md#rules-for-moving-up-a-level", "unverified": False,
                "basis": "compendium", "reason": "Because %s." % rid}

    def test_a_real_value_beats_undecided(self):
        run = self.run_for([self.rule("r-undecided", "undecided"), self.rule("r-three", 3), self.rule("r-two", 2)])
        decision, undecided = run.decide("autonomy.ceiling", {}, "T1")
        self.assertEqual((decision["value"], decision["rule"], decision["reason"], undecided),
                         (2, "r-two", "Because r-two.", False))

    def test_undecided_alone_stays_undecided(self):
        run = self.run_for([self.rule("r-undecided", "undecided")])
        decision, undecided = run.decide("autonomy.ceiling", {}, "T1")
        self.assertEqual((decision["value"], decision["rule"], undecided), (None, "r-undecided", True))

    def test_high_cost_customer_facing_task_keeps_the_level_2_cap(self):
        out = level(TEAM, set_cost("C3", "high"))
        ceiling = task_of(out, "C3")["autonomy"]["ceiling"]
        self.assertEqual((ceiling["value"], ceiling["rule"]), (2, "ceiling-customer-facing"))
        self.assertIn("C3", ids_of(out, "warnings", "high-cost-ceiling-unconfirmed"))
        self.assertNotIn(("decision-undecided", "C3"), LT.codes(out, "warnings"))
        message = next(w["message"] for w in out["warnings"]
                       if (w["code"], w["about"]) == ("high-cost-ceiling-unconfirmed", "C3"))
        self.assertIn("page 06 has no rule for", message)
        self.assertIn("level 2", message)
        self.assertIn("ceiling-customer-facing", message)
        self.assertIn("override", message)

    def test_high_cost_person_task_gets_level_3_and_the_warning(self):
        out = level(PE)
        ceiling = task_of(out, "T4")["autonomy"]["ceiling"]
        self.assertEqual((ceiling["value"], ceiling["rule"]), (3, "ceiling-person-started"))
        self.assertEqual(ids_of(out, "warnings", "high-cost-ceiling-unconfirmed"), ["T4", "T6"])
        self.assertNotIn("T4", ids_of(out, "warnings", "decision-undecided"))

    def test_an_override_confirms_the_cap_and_removes_the_warning(self):
        out = level(PE, lambda p, c: LT.override(c, "T4", "autonomy.ceiling", 2))
        self.assertEqual(ids_of(out, "warnings", "high-cost-ceiling-unconfirmed"), ["T6"])
        self.assertEqual(task_of(out, "T4")["autonomy"]["ceiling"]["overridden"]["rule_result"], 3)


# --- Engine change 2 and Finding 3: a 'then' fact that is empty ---------------------------------------

class EmptyFactTests(unittest.TestCase):
    def test_highly_sensitive_task_under_the_b2b_pack_is_undecided(self):
        out = level(PE, set_profile_value("industry", "b2b-software"))
        baseline = task_of(out, "T1")["data_controls"]["settings_baseline"]
        self.assertEqual((baseline["value"], baseline["rule"]), (None, "baseline-highly-sensitive-pack"))
        undecided = [w for w in out["warnings"] if (w["code"], w["about"]) == ("decision-undecided", "T1")]
        self.assertTrue(undecided)
        self.assertTrue(any("pack.settings_baseline" in w["message"] and "settings_baseline" in w["message"]
                            for w in undecided))
        persona = out["persona_plan"]["settings_baseline"]
        self.assertEqual((persona["value"], persona["rule"]), (None, "persona-baseline-highly-sensitive-pack"))
        self.assertIn("persona", ids_of(out, "warnings", "decision-undecided"))

    def test_a_literal_null_is_a_value_with_no_warning(self):
        out = level(TEAM)
        baseline = task_of(out, "C1")["data_controls"]["settings_baseline"]
        self.assertEqual((baseline["value"], baseline["rule"]), (None, "baseline-unmanaged-none"))
        self.assertNotIn("C1", ids_of(out, "warnings", "decision-undecided"))

    def test_an_open_then_fact_is_field_open(self):
        def change(profile, card):
            LT.task(card, "T1")["data_class"] = "confidential"
            card["role"]["works_in"] = []
            card["provenance"]["role.works_in"] = {"status": "open", "source": "interviews/2026-11-05-associate.md#Q1",
                                                   "owner": "Test owner", "due": "2026-12-01"}
        out = level(PE, change)
        surfaces = task_of(out, "T1")["data_controls"]["surfaces"]
        self.assertEqual((surfaces["value"], surfaces["rule"]), (None, "surfaces-managed-works-in"))
        self.assertIn("T1", ids_of(out, "warnings", "field-open"))


def set_profile_value(key, value):
    def change(profile, card):
        profile[key] = value
    return change


# --- Finding 1: a scheduled task with highly sensitive or PHI data ---------------------------------

class ScheduledTaskTests(unittest.TestCase):
    def test_highly_sensitive_scheduled_task_runs_in_the_customers_environment(self):
        out = level(PE, set_task("T1", trigger="schedule-own"))
        runtime = task_of(out, "T1")["runtime"]
        self.assertEqual((runtime["value"], runtime["rule"]),
                         ("claude-code-scheduled-task", "runtime-own-schedule-claude-code"))
        self.assertIn("T1", ids_of(out, "warnings", "scheduled-task-own-environment-only"))

    def test_phi_scheduled_task_gets_the_same_warning(self):
        out = level(PE, chain(LT.pe_t1_phi, set_task("T1", trigger="schedule-own")))
        self.assertIn("T1", ids_of(out, "warnings", "scheduled-task-own-environment-only"))

    def test_confidential_scheduled_task_does_not(self):
        out = level(TEAM, set_task("C1", trigger="schedule-own"))
        self.assertNotIn("C1", ids_of(out, "warnings", "scheduled-task-own-environment-only"))


# --- Finding 2: no Claude Tag routine under ZDR or a self-hosting requirement ---------------------------

class TagRoutineTests(unittest.TestCase):
    def test_the_fixture_slack_task_is_still_a_tag_routine(self):
        runtime = task_of(level(TEAM), "C2")["runtime"]
        self.assertEqual((runtime["value"], runtime["rule"]), ("claude-tag-routine", "runtime-team-slack-tag-routine"))
        self.assertEqual(runtime["basis"], "our-recommendation")
        self.assertIn("our choice", runtime["reason"])

    def test_schedule_team_slack_task_under_zdr_is_not_a_tag_routine(self):
        runtime = task_of(level(TEAM, set_profile("compliance", "retention", "zdr")), "C2")["runtime"]
        self.assertEqual((runtime["value"], runtime["rule"]), ("managed-agents-self-hosted", "runtime-zdr-self-hosted"))

    def test_self_hosting_required_is_not_a_tag_routine(self):
        out = level(TEAM, set_profile("runtime_preferences", "self_hosting_required", True))
        runtime = task_of(out, "C2")["runtime"]
        self.assertEqual((runtime["value"], runtime["rule"]),
                         ("managed-agents-self-hosted", "runtime-self-hosting-required"))


# --- Finding 4: plan fit for highly sensitive work, and the ZDR org ------------------------------------

class ZdrOrgTests(unittest.TestCase):
    def test_highly_sensitive_plan_fit_has_limits_and_a_warning(self):
        out = level(PE)
        plan = task_of(out, "T1")["plan_fit"]
        self.assertEqual((plan["value"], plan["rule"]), ("ok-with-limits", "plan-fit-highly-sensitive-zdr-org"))
        self.assertIn("confirm the customer has one", plan["reason"])
        self.assertEqual(ids_of(out, "warnings", "zdr-org-not-confirmed"), ["T1", "T2", "T3", "T4", "T5", "T6"])

    def test_no_warning_when_the_profile_shows_zdr(self):
        out = level(PE, set_profile("compliance", "retention", "zdr"))
        self.assertEqual(ids_of(out, "warnings", "zdr-org-not-confirmed"), [])


# --- Finding 5: no MCP tunnel for highly sensitive or PHI data -----------------------------------------

class SensitivePrivateNetworkTests(unittest.TestCase):
    def test_highly_sensitive_private_network_task_is_told_to_run_inside(self):
        plan = task_of(level(PE, LT.pe_private_salesforce), "T1")["plan_fit"]
        self.assertEqual((plan["value"], plan["rule"]), ("ok-with-limits", "plan-fit-private-network-sensitive"))
        self.assertIn("inside the network", plan["reason"])


# --- Finding 6: Claude Code inside the network ---------------------------------------------------------

team_c1_reads_usage_db = LT.team_c1_reads_usage_db


class InsideNetworkTests(unittest.TestCase):
    def change(self):
        return chain(set_profile("network", "can_allowlist_anthropic_ips", False), team_c1_reads_usage_db)

    def test_hosted_runtime_still_gets_the_blocker(self):
        out = level(TEAM, self.change())
        self.assertEqual(ids_of(out, "blockers", "private-network-unreachable"), ["C2"])
        plan = task_of(out, "C2")["plan_fit"]
        self.assertEqual((plan["value"], plan["rule"]), ("needs-enterprise", "plan-fit-private-network-no-route"))

    def test_client_skill_gets_a_warning_not_a_blocker(self):
        out = level(TEAM, self.change())
        self.assertNotIn("C1", ids_of(out, "blockers", "private-network-unreachable"))
        self.assertIn("C1", ids_of(out, "warnings", "private-network-inside-only"))
        plan = task_of(out, "C1")["plan_fit"]
        self.assertEqual((plan["value"], plan["rule"]), ("ok-with-limits", "plan-fit-private-network-inside-only"))


# --- Finding 7: a mixed device fleet ---------------------------------------------------------------------

class MixedDeviceTests(unittest.TestCase):
    def test_mixed_devices_give_the_managed_surface_and_a_warning(self):
        out = level(PE, set_device("mixed"))
        surfaces = task_of(out, "T1")["data_controls"]["surfaces"]
        self.assertEqual((surfaces["value"], surfaces["rule"]), (["claude-code"], "surfaces-sensitive-managed-claude-code"))
        self.assertIn("T1", ids_of(out, "warnings", "unmanaged-share-no-access"))
        self.assertEqual(ids_of(out, "blockers", "unmanaged-device-no-access"), [])

    def test_unmanaged_devices_still_get_no_surface_and_the_blocker(self):
        out = level(PE, set_device("unmanaged"))
        surfaces = task_of(out, "T1")["data_controls"]["surfaces"]
        self.assertEqual((surfaces["value"], surfaces["rule"]), ([], "surfaces-sensitive-unmanaged-none"))
        self.assertIn("T1", ids_of(out, "blockers", "unmanaged-device-no-access"))

    def test_read_only_connectors_cover_mixed_and_say_read_only(self):
        out = level(TEAM, set_device("mixed"))
        warning = [w for w in out["warnings"] if (w["code"], w["about"]) == ("unmanaged-connectors-read-only", "C4")]
        self.assertTrue(warning)
        self.assertIn("read-only", warning[0]["fix"])
        self.assertNotIn("Needs approval at most", warning[0]["fix"])


# --- Finding 8 is engine change 1. Finding 9: retention ------------------------------------------------

class RetentionTests(unittest.TestCase):
    def test_confidential_work_on_standard_retention_is_warned(self):
        out = level(TEAM)
        self.assertEqual(ids_of(out, "warnings", "confidential-standard-retention"), ["C1", "C2", "C3", "C4", "C5"])
        fix = next(w["fix"] for w in out["warnings"] if w["code"] == "confidential-standard-retention")
        self.assertIn("6 years", fix)
        retention = task_of(out, "C1")["data_controls"]["retention"]
        self.assertEqual((retention["value"], retention["rule"], retention["basis"]),
                         ("standard", "retention-profile", "our-recommendation"))

    def test_custom_retention_does_not_cover_a_tag_routine(self):
        out = level(TEAM, set_profile("compliance", "retention", "custom-30-day"))
        self.assertEqual(ids_of(out, "warnings", "retention-not-covered"), ["C2"])
        self.assertEqual(ids_of(out, "warnings", "confidential-standard-retention"), [])


# --- Finding 10: plan-fit entries ------------------------------------------------------------------------

class PlanFitTests(unittest.TestCase):
    def test_analytics_api_is_not_on_team_and_the_gaps_are_unverified(self):
        caps = {c["id"]: c for c in LT.load(LT.PLAN_FIT)["capabilities"]}
        self.assertEqual(caps["analytics-api"]["team"], "no")
        self.assertIn("dashboard", caps["analytics-api"]["lost_on_team"])
        for cid in ("managed-settings-and-hooks", "governance-action-log", "managed-agents-hosted",
                    "managed-agents-self-hosted", "agent-sdk"):
            self.assertTrue(caps[cid]["unverified"], cid)

    def test_design_defines_unverified_for_a_missing_per_plan_value(self):
        text = LT.DESIGN.read_text(encoding="utf-8")
        self.assertIn("no compendium section states the per-plan value", text)


# --- Finding 11: memory ------------------------------------------------------------------------------------

class MemoryTests(unittest.TestCase):
    def test_memory_rules_are_our_recommendation_and_say_it_is_org_wide(self):
        for rid in ("memory-off-not-wanted", "memory-off-untrusted-input", "memory-on", "warn-memory-poisoning-risk"):
            r = rule(rid)
            self.assertEqual(r["basis"], "our-recommendation", rid)
            self.assertIn("org-wide", r["reason"], rid)
        memory = task_of(level(TEAM), "C2")["memory"]
        self.assertEqual((memory["value"], memory["rule"], memory["basis"]),
                         ("off", "memory-off-untrusted-input", "our-recommendation"))


# --- Finding 12: PHI rules are Unverified ------------------------------------------------------------------

class PhiTests(unittest.TestCase):
    def test_phi_rules_are_unverified(self):
        for rid in PHI_RULES:
            self.assertTrue(rule(rid)["unverified"], rid)
        self.assertEqual(rule("block-phi-no-hosted-runtime")["basis"], "our-recommendation")
        out = level(PE, LT.pe_phi)
        runtime = task_of(out, "T3")["runtime"]
        self.assertEqual((runtime["value"], runtime["rule"], runtime["unverified"]), ("none", "runtime-phi-none", True))
        blocker = [b for b in out["blockers"] if (b["code"], b["about"]) == ("phi-no-hosted-runtime", "T3")]
        self.assertTrue(blocker and blocker[0]["unverified"])


# --- Finding 13: web tools for PHI -------------------------------------------------------------------------

class WebToolsTests(unittest.TestCase):
    def test_phi_web_tools_are_off_by_their_own_rule(self):
        out = level(PE, LT.pe_t1_phi)
        phi = task_of(out, "T1")["data_controls"]["web_tools"]
        self.assertEqual((phi["value"], phi["rule"], phi["basis"]), ("off", "web-tools-off-phi", "our-recommendation"))
        self.assertIn("web fetch", phi["reason"])
        sensitive = task_of(out, "T2")["data_controls"]["web_tools"]
        self.assertEqual((sensitive["value"], sensitive["rule"]), ("off", "web-tools-off-sensitive"))


# --- Finding 14: the b2b pack and the HubSpot warning ------------------------------------------------------

class B2bPackTests(unittest.TestCase):
    def test_pack_entries_say_what_page_11_and_18_say(self):
        pack = LT.load(PACKS / "b2b-software.json")
        defaults = {d["product"]: d for d in pack["connector_defaults"]}
        self.assertIn("App Marketplace access", defaults["HubSpot"]["how"])
        self.assertNotIn("admin approval", defaults["Slack"]["identity"])
        self.assertFalse(defaults["Google Calendar"]["unverified"])
        sales = next(p for p in pack["anthropic_starting_points"] if p["name"] == "sales")
        self.assertEqual(sales["cite"], "docs/compendium/18-customer-success.md#the-short-answer")

    def test_hubspot_warning_names_app_marketplace_access(self):
        out = level(TEAM)
        warning = next(w for w in out["warnings"] if w["code"] == "hubspot-super-admin-approval")
        self.assertIn("App Marketplace access", warning["message"])


# --- Finding 15 and the remaining audit rows --------------------------------------------------------------

class ReasonTests(unittest.TestCase):
    def test_ceiling_reasons_claim_only_what_they_test(self):
        for rid in ("ceiling-person-started", "ceiling-unattended"):
            self.assertNotIn("internal and reversible", rule(rid)["reason"], rid)
        self.assertEqual(rule("ceiling-irreversible-not-internal")["basis"], "our-recommendation")
        self.assertIn("another team", rule("ceiling-irreversible-not-internal")["reason"])

    def test_identity_rules_are_split_by_runtime(self):
        out = level(PE)
        identity = task_of(out, "T3")["identity"]
        self.assertEqual((identity["value"], identity["rule"]), ("api-key-vault", "identity-hosted-vault"))
        self.assertIn("per-user vault", identity["reason"])
        sdk = task_of(level(PE, LT.pe_override_agent_sdk), "T3")["identity"]
        self.assertEqual((sdk["value"], sdk["rule"]), ("api-key-vault", "identity-agent-sdk"))
        self.assertIn("credentials you pass in", sdk["reason"])

    def test_no_runtime_has_no_identity(self):
        out = level(PE, LT.pe_phi)
        identity = task_of(out, "T3")["identity"]
        self.assertEqual((identity["value"], identity["rule"]), (None, "identity-no-runtime"))
        self.assertEqual([c["identity"] for c in task_of(out, "T3")["connectors"]], [None, None])
        self.assertNotIn("T3", ids_of(out, "warnings", "decision-undecided"))

    def test_client_identity_names_the_exceptions(self):
        for rid in ("identity-client-user", "connector-identity-user"):
            reason = rule(rid)["reason"]
            self.assertIn("signed-in user", reason, rid)
            self.assertIn("Intercom", reason, rid)
            self.assertIn("Dynamics", reason, rid)
            self.assertIn("connectors[]", reason, rid)

    def test_mail_read_only_fires_only_for_a_mail_or_calendar_write(self):
        out = level(TEAM)
        self.assertEqual(ids_of(out, "warnings", "mail-read-only"), [])
        out = level(TEAM, LT.team_c4_gmail_send)
        self.assertEqual(ids_of(out, "warnings", "mail-read-only"), ["C4"])
        message = next(w["message"] for w in out["warnings"] if w["code"] == "mail-read-only")
        self.assertIn("Gmail", message)
        self.assertIn("Google Calendar", message)


# --- Every rule: basis and unverified ----------------------------------------------------------------------

class AuditTests(unittest.TestCase):
    def test_every_basis_is_one_of_two(self):
        for r in LT.load(LT.RULES)["rules"]:
            self.assertIn(r["basis"], ("compendium", "our-recommendation"), r["id"])

    def test_unverified_rules_cite_a_marked_section_or_are_the_phi_rules(self):
        for r in LT.load(LT.RULES)["rules"]:
            if r["unverified"] and r["id"] not in PHI_RULES:
                text = LT.section(r["cite"])
                self.assertIsNotNone(text, r["id"])
                self.assertRegex(text, LT.UNVERIFIED_MARKER, r["id"])

    def test_every_new_code_is_in_design_and_has_a_template(self):
        listed = L.design_codes()
        templates = {t["when"].get("codes") for t in LT.load(TASK_LIBRARY)["templates"] if isinstance(t["when"], dict)}
        for code in NEW_CODES:
            self.assertIn(code, listed, code)
            self.assertIn(code, templates, code)


if __name__ == "__main__":
    unittest.main()
