"""Hardening of the persona-card commands (OPS-47).

Each test replays one attempt from the 2026-11-16 commands review that the commands got wrong, on a
temporary copy of a fictional sample (and, where the attempt edits the kit's data, on a temporary copy
of the plugin). Nothing is written outside the temporary folder. The attempt id is in each test name.

Standard library only. Run with: python3 -m unittest tests.test_twincard_hardening
"""

import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "partner-kit" / "plugins" / "twin-consultant"
CLI = PLUGIN / "scripts" / "twincard" / "cli.py"
SCRIPTS_DIR = PLUGIN / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from twincard import level as L  # noqa: E402

PE = ("sample-pe", "deal-team-associate")
CS = ("sample-team-cs", "customer-success-manager")
GENERATED = ("levelled.json", "backlog.json", "backlog.md", "dashboard.html")
DATE = "2026-11-15"
NEXT_LINE = re.compile(r"Next: \S.*$")
ALLOWED_RUNTIMES = ("client-skill", "claude-code-scheduled-task", "claude-tag-routine", "managed-agents",
                    "managed-agents-self-hosted", "agent-sdk", "none")


def override(task, decision, value, reason="Invented reason for a test.", approved_by="Invented approver"):
    return {"task": task, "decision": decision, "value": value, "reason": reason, "approved_by": approved_by}


class Base(unittest.TestCase):
    """A temporary folder holding copies of the samples and, when asked, of the plugin."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="twincard-hardening-"))
        self.addCleanup(self._remove)
        self.cli_path = CLI

    def _remove(self):
        for path in self.tmp.rglob("*"):
            try:
                os.chmod(path, stat.S_IRWXU)
            except OSError:
                pass
        shutil.rmtree(self.tmp, ignore_errors=True)

    def sample(self, which):
        customer, persona = which
        dest = self.tmp / "engagements" / customer
        if not dest.is_dir():
            shutil.copytree(ROOT / "engagements" / customer, dest)
        return dest / "personas" / persona

    def plugin_copy(self):
        """Copy the plugin's scripts and data (and design.md) to the temporary folder; run that cli.py."""
        kit = self.tmp / "kit" / "partner-kit"
        shutil.rmtree(kit, ignore_errors=True)
        shutil.copytree(PLUGIN / "scripts", kit / "plugins" / "twin-consultant" / "scripts",
                        ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(PLUGIN / "data", kit / "plugins" / "twin-consultant" / "data")
        (kit / "docs").mkdir(parents=True)
        shutil.copy2(ROOT / "partner-kit" / "docs" / "design.md", kit / "docs" / "design.md")
        self.cli_path = kit / "plugins" / "twin-consultant" / "scripts" / "twincard" / "cli.py"
        return kit / "plugins" / "twin-consultant" / "data"

    def cli(self, *args):
        return subprocess.run([sys.executable, str(self.cli_path)] + [str(a) for a in args],
                              capture_output=True, text=True, encoding="utf-8")

    @staticmethod
    def edit(path, change):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        change(data)
        Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    @staticmethod
    def card_task(card, tid):
        return next(t for t in card["tasks"] if t["id"] == tid)

    def snapshot(self, persona):
        return {name: (persona / name).read_bytes() if (persona / name).is_file() else None for name in GENERATED}

    def assert_unchanged(self, persona, before):
        self.assertEqual(self.snapshot(persona), before, "a refused command wrote a file")

    def assert_one_line(self, proc, code, *words):
        """Exit code, no traceback, and exactly one stderr line that ends 'Next: ...' and names each word."""
        output = proc.stdout + proc.stderr
        self.assertEqual(proc.returncode, code, output)
        self.assertNotIn("Traceback", output)
        lines = [line for line in proc.stderr.splitlines() if line.strip()]
        self.assertEqual(len(lines), 1, proc.stderr)
        self.assertRegex(lines[0], NEXT_LINE)
        for word in words:
            self.assertIn(word, lines[0])
        return lines[0]

    def assert_stderr_has_next(self, proc):
        for line in proc.stderr.splitlines():
            if line.strip():
                self.assertRegex(line, NEXT_LINE, proc.stderr)

    def validation_errors(self, persona):
        proc = self.cli("validate", "--json", persona)
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        return json.loads(proc.stdout)["errors"]

    def error_at(self, errors, record, path):
        found = [e for e in errors if e["record"] == record and e["path"] == path]
        self.assertTrue(found, "no error at %s:%s in %s" % (record, path, [(e["path"], e["message"]) for e in errors]))
        return found[0]


# --- Findings 1 and 6: override values; finding 2: reason and approver; finding 13: duplicates --------

class OverrideValueTests(Base):

    def set_overrides(self, persona, *items):
        self.edit(persona / "card.json", lambda card: card.__setitem__("overrides", list(items)))

    def test_4_10_autonomy_outside_0_to_4(self):
        persona = self.sample(PE)
        self.set_overrides(persona, override("T1", "autonomy.ceiling", 9), override("T2", "autonomy.start", "high"),
                           override("T3", "autonomy.start", True))
        errors = self.validation_errors(persona)
        for index in range(3):
            error = self.error_at(errors, "card", "overrides[%d].value" % index)
            self.assertIn("0", error["message"])
            self.assertIn("4", error["message"])
        before = self.snapshot(persona)
        self.assertEqual(self.cli("level", persona).returncode, 1)
        self.assert_unchanged(persona, before)

    def test_4_11_runtime_memory_identity_not_in_vocabulary(self):
        persona = self.sample(PE)
        self.set_overrides(persona, override("T1", "runtime", "banana"), override("T2", "memory", "maybe"),
                           override("T5", "identity", 7))
        errors = self.validation_errors(persona)
        runtime = self.error_at(errors, "card", "overrides[0].value")
        for value in ALLOWED_RUNTIMES:
            self.assertIn(value, runtime["message"] + runtime["fix"])
        self.assertIn("off", self.error_at(errors, "card", "overrides[1].value")["message"])
        self.assertIn("service-account", self.error_at(errors, "card", "overrides[2].value")["message"])
        before = self.snapshot(persona)
        proc = self.cli("all", persona, "--date", DATE)
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("card:overrides[0].value", proc.stdout)
        self.assertRegex(proc.stdout, r"card:overrides\[0\]\.value: .*\. Next: \S")
        self.assert_unchanged(persona, before)

    def test_4_13_bad_runtime_cannot_remove_a_blocker(self):
        persona = self.sample(CS)
        self.edit(persona / "card.json", lambda card: self.card_task(card, "C1").__setitem__(
            "data_class", "highly-sensitive"))
        self.assertEqual(self.cli("level", persona).returncode, 1)
        levelled = json.loads((persona / "levelled.json").read_text(encoding="utf-8"))
        codes = sorted(b["code"] for b in levelled["blockers"] if b["about"] == "C1")
        self.set_overrides(persona, override("C1", "runtime", "banana"))
        before = self.snapshot(persona)
        proc = self.cli("level", persona)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("card:overrides[0].value", proc.stdout)
        self.assert_unchanged(persona, before)
        levelled = json.loads((persona / "levelled.json").read_text(encoding="utf-8"))
        self.assertEqual(sorted(b["code"] for b in levelled["blockers"] if b["about"] == "C1"), codes)

    def test_4_14_match_is_exact(self):
        persona = self.sample(CS)
        self.edit(persona.parent.parent / "customer-profile.json",
                  lambda p: p["network"].__setitem__("can_allowlist_anthropic_ips", False))
        self.set_overrides(persona, override("C2", "runtime", "Client-Skill"))
        error = self.error_at(self.validation_errors(persona), "card", "overrides[0].value")
        self.assertIn("client-skill", error["message"])
        self.set_overrides(persona, override("C2", "runtime", "client-skill "))
        self.error_at(self.validation_errors(persona), "card", "overrides[0].value")

    def test_4_16_data_controls_shape(self):
        persona = self.sample(PE)
        self.set_overrides(persona, override("T1", "data_controls", "off"),
                           override("T2", "data_controls", {"webtools": "on"}),
                           override("T3", "data_controls", {}),
                           override("T4", "data_controls", {"surfaces": ["nowhere"]}),
                           override("T5", "data_controls", {"settings_baseline": "top-secret"}),
                           override("T6", "data_controls", {"retention": "forever"}))
        errors = self.validation_errors(persona)
        self.error_at(errors, "card", "overrides[0].value")
        misspelt = [e for e in errors if e["path"].startswith("overrides[1].value")]
        self.assertTrue(misspelt, errors)
        self.assertIn("webtools", misspelt[0]["message"])
        self.assertIn("web_tools", misspelt[0]["message"] + misspelt[0]["fix"])
        for index in (2, 3, 4, 5):
            self.assertTrue([e for e in errors if e["path"].startswith("overrides[%d].value" % index)],
                            "overrides[%d]: %s" % (index, errors))

    def test_good_values_validate(self):
        persona = self.sample(PE)
        self.set_overrides(persona, override("T1", "runtime", "agent-sdk"), override("T2", "autonomy.start", 0),
                           override("T2", "autonomy.ceiling", 4), override("T3", "memory", "on"),
                           override("T4", "identity", "service-account"),
                           override("T5", "data_controls", {"settings_baseline": None, "web_tools": "off",
                                                            "surfaces": ["claude-ai"], "retention": "zdr"}))
        proc = self.cli("validate", persona)
        self.assertEqual(proc.returncode, 0, proc.stdout)
        proc = self.cli("level", "--json", persona)
        levelled = json.loads(proc.stdout)
        self.assertEqual(levelled["tasks"]["T1"]["runtime"]["value"], "agent-sdk")
        self.assertEqual(levelled["tasks"]["T5"]["data_controls"]["web_tools"]["value"], "off")

    def test_4_7_targets_are_unchanged(self):
        persona = self.sample(PE)
        self.set_overrides(persona, override("T1", "connectors", []), override("T1", "plan_fit", "ok"))
        self.assertEqual(self.cli("validate", persona).returncode, 0)
        proc = self.cli("level", "--json", persona)
        self.assertEqual(proc.returncode, 1)
        levelled = json.loads(proc.stdout)
        blocked = [b for b in levelled["blockers"] if b["code"] == "override-not-allowed"]
        self.assertEqual(len(blocked), 2, blocked)

    def test_unknown_decision_is_an_unknown_target(self):
        problems = L.override_problems([override("T1", "mood", "calm")], ["T1"])
        self.assertEqual([item["code"] for _, item in problems], ["override-unknown-target"])

    def test_level_guard_refuses_a_bad_value(self):
        for item in (override("T1", "runtime", "banana"), override("T1", "autonomy.ceiling", 9),
                     override("T1", "autonomy.start", True), override("T1", "data_controls", "off"),
                     override("T1", "memory", "maybe"), override("T1", "identity", 7)):
            problems = L.override_problems([item], ["T1"])
            self.assertEqual([p["code"] for _, p in problems], ["override-unknown-target"], item)
        self.assertEqual(L.override_problems([override("T1", "runtime", "agent-sdk")], ["T1"]), [])

    def test_4_9_reason_and_approver_required(self):
        persona = self.sample(PE)
        self.set_overrides(persona, {"task": "T1", "decision": "runtime", "value": "agent-sdk"},
                           override("T2", "runtime", "agent-sdk", reason="   ", approved_by="\t"))
        errors = self.validation_errors(persona)
        for path in ("overrides[0].reason", "overrides[0].approved_by", "overrides[1].reason",
                     "overrides[1].approved_by"):
            self.error_at(errors, "card", path)
        before = self.snapshot(persona)
        self.assertEqual(self.cli("level", persona).returncode, 1)
        self.assert_unchanged(persona, before)

    def test_4_9_catalogue_says_required(self):
        catalogue = json.loads((PLUGIN / "data" / "fields.json").read_text(encoding="utf-8"))
        required = {e["path"]: e["required"] for e in catalogue["fields"] if e["path"].startswith("overrides")}
        self.assertTrue(required["overrides[].reason"])
        self.assertTrue(required["overrides[].approved_by"])

    def test_4_15_duplicate_override(self):
        persona = self.sample(PE)
        self.set_overrides(persona, override("T1", "runtime", "agent-sdk"), override("T1", "runtime", "managed-agents"))
        errors = self.validation_errors(persona)
        both = [e for e in errors if "overrides[0]" in e["message"] + e["path"] and "overrides[1]" in
                e["message"] + e["path"]]
        self.assertTrue(both, errors)

    def test_dedupe_keeps_two_override_messages(self):
        items = [{"code": "override-not-allowed", "about": "T1", "message": "one", "fix": "f", "cite": "c",
                  "unverified": False},
                 {"code": "override-not-allowed", "about": "T1", "message": "two", "fix": "f", "cite": "c",
                  "unverified": False}]
        self.assertEqual(len(L._dedupe(items)), 2)


# --- Findings 3 and 14: the task list, unknown keys, versions and numbers ---------------------------

class RecordShapeTests(Base):

    def test_2_10_no_tasks(self):
        persona = self.sample(PE)
        before = self.snapshot(persona)
        self.edit(persona / "card.json", lambda card: card.__setitem__("tasks", []))
        proc = self.cli("all", persona, "--date", DATE)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("a card needs at least one task", proc.stdout)
        self.assert_unchanged(persona, before)

    def test_tasks_missing_or_not_a_list(self):
        persona = self.sample(PE)
        for value in (None, "T1", {}):
            def change(card, value=value):
                if value is None:
                    del card["tasks"]
                else:
                    card["tasks"] = value
            shutil.copy2(ROOT / "engagements" / PE[0] / "personas" / PE[1] / "card.json", persona / "card.json")
            self.edit(persona / "card.json", change)
            errors = self.validation_errors(persona)
            self.assertIn("a card needs at least one task", self.error_at(errors, "card", "tasks")["message"])

    def test_2_11_unknown_top_level_key(self):
        persona = self.sample(CS)

        def change(card):
            card["taks"] = card.pop("tasks")
            card["open_questions"] = []
        self.edit(persona / "card.json", change)
        error = self.error_at(self.validation_errors(persona), "card", "taks")
        self.assertIn("tasks", error["message"] + error["fix"])

    def test_unknown_key_names_the_closest(self):
        persona = self.sample(PE)

        def change(card):
            card["overides"] = card.pop("overrides")
        self.edit(persona / "card.json", change)
        self.edit(persona.parent.parent / "customer-profile.json",
                  lambda p: p.__setitem__("complience", p["compliance"]))
        errors = self.validation_errors(persona)
        card = self.error_at(errors, "card", "overides")
        self.assertIn("overrides", card["message"] + card["fix"])
        profile = self.error_at(errors, "profile", "complience")
        self.assertIn("compliance", profile["message"] + profile["fix"])

    def test_2_13_version_must_be_the_integer(self):
        persona = self.sample(CS)
        self.edit(persona / "card.json", lambda card: card.__setitem__("card_version", True))
        self.error_at(self.validation_errors(persona), "card", "card_version")
        self.edit(persona / "card.json", lambda card: card.__setitem__("card_version", 1.0))
        self.error_at(self.validation_errors(persona), "card", "card_version")
        self.edit(persona / "card.json", lambda card: card.__setitem__("card_version", 1))
        self.edit(persona.parent.parent / "customer-profile.json", lambda p: p.__setitem__("profile_version", True))
        self.error_at(self.validation_errors(persona), "profile", "profile_version")

    def test_2_14_numbers_finite_and_not_negative(self):
        persona = self.sample(CS)

        def change(card):
            task = self.card_task(card, "C1")
            task["frequency_per_week"], task["users"], task["minutes_each"] = -4, -3, float("nan")
            self.card_task(card, "C2")["minutes_each"] = float("inf")
        self.edit(persona / "card.json", change)
        self.assertIn("NaN", (persona / "card.json").read_text(encoding="utf-8"))
        errors = self.validation_errors(persona)
        for path in ("tasks.C1.frequency_per_week", "tasks.C1.users", "tasks.C1.minutes_each",
                     "tasks.C2.minutes_each"):
            self.error_at(errors, "card", path)
        before = self.snapshot(persona)
        self.assertEqual(self.cli("all", persona, "--date", DATE).returncode, 1)
        self.assert_unchanged(persona, before)


# --- Finding 4: a plan that is no longer what the inputs give ----------------------------------------

class FreshnessTests(Base):

    def test_1_12_rules_changed_after_level(self):
        persona = self.sample(PE)
        data = self.plugin_copy()
        levelled = json.loads((persona / "levelled.json").read_text(encoding="utf-8"))
        rule_id = levelled["tasks"]["T1"]["runtime"]["rule"]

        def change(rules):
            rule = next(r for r in rules["rules"] if r["id"] == rule_id)
            rule["reason"] = "An invented reason, changed after level ran."
        self.edit(data / "rules.json", change)
        before = self.snapshot(persona)
        proc = self.cli("backlog", persona)
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("levelled.json is missing or out of date", proc.stdout + proc.stderr)
        proc = self.cli("dashboard", persona, "--date", DATE)
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("levelled.json is out of date", proc.stdout + proc.stderr)
        self.assert_unchanged(persona, before)
        self.assertEqual(self.cli("all", persona, "--date", DATE).returncode, 0)
        self.assertIn("changed after level ran", (persona / "levelled.json").read_text(encoding="utf-8"))

    def test_1_13_levelled_hand_edited(self):
        persona = self.sample(PE)

        def change(levelled):
            levelled["tasks"]["T1"]["runtime"]["value"] = "managed-agents"
            levelled["warnings"].pop()
        self.edit(persona / "levelled.json", change)
        before = self.snapshot(persona)
        proc = self.cli("backlog", persona)
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("levelled.json is missing or out of date", proc.stdout)
        proc = self.cli("dashboard", persona, "--date", DATE)
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("levelled.json is out of date", proc.stdout)
        self.assertIn("Next: run the level command", proc.stdout)
        self.assert_unchanged(persona, before)

    def test_layout_alone_is_not_a_difference(self):
        persona = self.sample(PE)
        for name in ("levelled.json", "backlog.json"):
            data = json.loads((persona / name).read_text(encoding="utf-8"))
            (persona / name).write_text(json.dumps(data, sort_keys=True), encoding="utf-8")
        proc = self.cli("dashboard", persona, "--date", DATE)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("Wrote", proc.stdout)
        self.assertEqual((persona / "dashboard.html").read_bytes(),
                         (ROOT / "engagements" / PE[0] / "personas" / PE[1] / "dashboard.html").read_bytes())

    def test_backlog_hand_edited_is_refused_by_dashboard(self):
        persona = self.sample(CS)

        def change(backlog):
            backlog["epic"]["features"][0]["stories"][0]["title"] = "Edited by hand"
        self.edit(persona / "backlog.json", change)
        before = self.snapshot(persona)
        proc = self.cli("dashboard", persona, "--date", DATE)
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("backlog.json is out of date", proc.stdout)
        self.assertIn("run the backlog command", proc.stdout)
        self.assert_unchanged(persona, before)

    def test_status_change_needs_backlog_first(self):
        persona = self.sample(CS)

        def change(backlog):
            # A task whose story the build has not started, so the derived parents change with it.
            backlog["epic"]["features"][-1]["stories"][0]["tasks"][0]["status"] = "done"
        self.edit(persona / "backlog.json", change)
        proc = self.cli("dashboard", persona, "--date", DATE)
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("run the backlog command", proc.stdout)
        self.assertEqual(self.cli("backlog", persona).returncode, 0)
        proc = self.cli("dashboard", persona, "--date", DATE)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("Backlog: 1 of", proc.stdout)


# --- Finding 5: backlog.md text ----------------------------------------------------------------------

INJECTED = ('# Injected heading\r\nline two\n```\n<!-- <details open><summary>x</summary> '
            '<a href="javascript:alert(1)">click</a>\n> quote\n- item')
PLAIN = "Plain words for a heading, a second line, a fence, a comment, a details block, a link and a list"
HEADING = re.compile(r"^\s*(?:(?:[-*+]|\d+[.)])\s+)*#{1,6}(?:\s|$)")


class MarkdownTests(Base):

    def build(self, text):
        self.tmp = Path(tempfile.mkdtemp(prefix="twincard-md-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        persona = self.sample(PE)
        data = self.plugin_copy()

        def card_change(card):
            task = self.card_task(card, "T1")
            task["name"] = text
            task["output"]["what"] = text
            for question in card["open_questions"]:
                if "T1" in question["blocks"]:
                    question["question"] = text

        def library_change(library):
            for template in library["templates"]:
                template["done_when"] = text
                template["how"][0]["text"] = text + "."
        self.edit(persona / "card.json", card_change)
        self.edit(data / "task-library.json", library_change)
        proc = self.cli("all", persona, "--date", DATE)
        self.assertNotIn("Traceback", proc.stderr)
        self.assertTrue((persona / "backlog.md").is_file(), proc.stdout + proc.stderr)
        md = (persona / "backlog.md").read_text(encoding="utf-8")
        backlog = json.loads((persona / "backlog.json").read_text(encoding="utf-8"))
        return md, backlog

    @staticmethod
    def shape(md):
        lines = md.split("\n")
        return {"headings": sum(1 for line in lines if HEADING.match(line)),
                "table rows": sum(1 for line in lines if line.startswith("|")),
                "lines": len(lines),
                "quotes": sum(1 for line in lines if re.match(r"^\s*(?:(?:[-*+]|\d+[.)])\s+)*>", line)),
                "fences": sum(1 for line in lines if re.match(r"^\s*(?:(?:[-*+]|\d+[.)])\s+)*(```|~~~)", line))}

    def test_6_5_6_6_6_9_control_text_keeps_the_shape(self):
        plain_md, _ = self.build(PLAIN)
        injected_md, backlog = self.build(INJECTED)
        self.assertEqual(self.shape(injected_md), self.shape(plain_md))
        self.assertNotIn("<", injected_md)
        self.assertNotIn("\r", injected_md)
        self.assertIn("&lt;details open>", injected_md)
        self.assertIn("### S-T1: # Injected heading line two ``` &lt;!-- &lt;details open>", injected_md)
        # backlog.json keeps the raw value
        story = next(s for f in backlog["epic"]["features"] for s in f["stories"] if s["id"] == "S-T1")
        self.assertEqual(story["title"], INJECTED)

    def test_plan_out_keeps_raw_values(self):
        persona = self.sample(PE)
        self.edit(persona / "card.json", lambda card: self.card_task(card, "T1").__setitem__("name", INJECTED))
        self.assertEqual(self.cli("level", persona).returncode, 0)
        plan = self.tmp / "plan.json"
        proc = self.cli("backlog", persona, "--plan-out", plan)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        titles = []

        def walk(node):
            titles.append(node["title"])
            for child in node["children"]:
                walk(child)
        for item in json.loads(plan.read_text(encoding="utf-8"))["items"]:
            walk(item)
        self.assertIn(INJECTED, titles)


# --- Findings 7, 9 and 10: no traceback ---------------------------------------------------------------

class NoTracebackTests(Base):

    def test_7_7_read_only_outputs(self):
        persona = self.sample(PE)
        for name in ("levelled.json", "backlog.json"):
            os.chmod(persona / name, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
        before = self.snapshot(persona)
        self.assert_one_line(self.cli("level", persona), 2, "levelled.json")
        self.assert_one_line(self.cli("backlog", persona), 2, "backlog.json")
        self.assert_one_line(self.cli("all", persona, "--date", DATE), 2, "levelled.json")
        self.assert_unchanged(persona, before)

    def test_read_only_dashboard(self):
        persona = self.sample(CS)
        os.chmod(persona / "dashboard.html", stat.S_IRUSR)
        self.assert_one_line(self.cli("dashboard", persona, "--date", DATE), 2, "dashboard.html")

    def test_9_10_plan_out_into_a_missing_folder(self):
        persona = self.sample(PE)
        (persona / "backlog.json").unlink()
        (persona / "backlog.md").unlink()
        proc = self.cli("backlog", persona, "--plan-out", self.tmp / "no-such-folder" / "plan.json")
        self.assert_one_line(proc, 2, "plan.json")
        self.assertFalse((persona / "backlog.json").exists())
        self.assertFalse((persona / "backlog.md").exists())

    def test_1_14_backlog_features_not_a_list(self):
        persona = self.sample(PE)
        self.edit(persona / "backlog.json", lambda b: b["epic"].__setitem__("features", 5))
        before = self.snapshot(persona)
        self.assert_one_line(self.cli("backlog", persona), 2, "backlog.json")
        self.assert_one_line(self.cli("dashboard", persona, "--date", DATE), 2, "backlog.json")
        self.assert_unchanged(persona, before)

    def test_1_15_backlog_task_not_an_object(self):
        persona = self.sample(PE)
        self.edit(persona / "backlog.json",
                  lambda b: b["epic"]["features"][0]["stories"][0].__setitem__("tasks", ["x"]))
        before = self.snapshot(persona)
        self.assert_one_line(self.cli("backlog", persona), 2, "backlog.json")
        self.assert_unchanged(persona, before)

    def test_backlog_not_json(self):
        persona = self.sample(CS)
        (persona / "backlog.json").write_text("{not json", encoding="utf-8")
        self.assert_one_line(self.cli("backlog", persona), 2, "backlog.json")
        (persona / "backlog.json").write_text("[1, 2]", encoding="utf-8")
        self.assert_one_line(self.cli("backlog", persona), 2, "backlog.json")
        self.assert_one_line(self.cli("dashboard", persona, "--date", DATE), 2, "backlog.json")

    def data_fault(self, name, text, command, which=PE):
        persona = self.sample(which)
        data = self.plugin_copy()
        target = data / name
        if text is None:
            target.unlink()
        else:
            target.write_text(text, encoding="utf-8")
        args = [command, persona] + (["--date", DATE] if command in ("dashboard", "all") else [])
        return self.assert_one_line(self.cli(*args), 2, Path(name).name)

    def test_9_15_rule_cite_invalid(self):
        persona = self.sample(PE)
        data = self.plugin_copy()

        def change(rules):
            rules["rules"][0]["cite"] = "x"
        self.edit(data / "rules.json", change)
        rule_id = json.loads((data / "rules.json").read_text(encoding="utf-8"))["rules"][0]["id"]
        self.assert_one_line(self.cli("level", persona), 2, "rules.json", rule_id)
        self.assert_one_line(self.cli("all", persona, "--date", DATE), 2, "rules.json")

    def test_rules_missing_or_not_json(self):
        self.data_fault("rules.json", None, "level")
        self.data_fault("rules.json", "{", "level")

    def test_plan_fit_faults(self):
        self.data_fault("plan-fit.json", "[]", "level")
        self.data_fault("plan-fit.json", None, "all")

    def test_task_library_faults(self):
        self.data_fault("task-library.json", "{", "backlog")
        self.data_fault("task-library.json", '{"library_version": 1}', "backlog")
        self.data_fault("task-library.json", None, "dashboard")

    def test_fields_faults(self):
        self.data_fault("fields.json", "{", "validate")
        self.data_fault("fields.json", '{"fields": 5}', "level")
        self.data_fault("fields.json", "[]", "backlog")
        self.data_fault("fields.json", None, "all")

    def test_pack_faults(self):
        self.data_fault("industry-packs/private-equity.json", "{", "level")
        self.data_fault("industry-packs/private-equity.json", "[]", "level")
        self.data_fault("industry-packs/private-equity.json", '{"pack_version": 1, "id": 5}', "dashboard")


# --- Finding 8: --json prints one JSON document --------------------------------------------------------

class JsonOutputTests(Base):

    def parse(self, proc):
        try:
            return json.loads(proc.stdout)
        except ValueError:
            self.fail("stdout is not one JSON document:\n" + proc.stdout[-500:])

    def test_success(self):
        persona = self.sample(CS)
        level = self.parse(self.cli("level", "--json", persona))
        self.assertIn("tasks", level)
        proc = self.cli("backlog", "--json", persona)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(self.parse(proc), json.loads((persona / "backlog.json").read_text(encoding="utf-8")))

    def test_blocked_backlog_prints_only_json(self):
        persona = self.sample(CS)
        self.edit(persona.parent.parent / "customer-profile.json", lambda p: p["plan"].__setitem__("tier", "individual"))
        self.assertEqual(self.cli("level", persona).returncode, 1)
        proc = self.cli("backlog", "--json", persona)
        self.assertEqual(proc.returncode, 1)
        self.parse(proc)
        self.assertIn("Blocked", proc.stderr)

    def test_9_8_validation_failure(self):
        persona = self.sample(PE)
        self.edit(persona / "card.json", lambda card: self.card_task(card, "T1").__setitem__("trigger", "manual"))
        for command in ("level", "backlog"):
            proc = self.cli(command, "--json", persona)
            self.assertEqual(proc.returncode, 1, command)
            body = self.parse(proc)
            self.assertFalse(body["ok"], command)
            self.assertTrue(body["errors"], command)
            self.assertIn("validation errors", body["error"], command)
            self.assertIn("Next:", body["error"], command)

    def test_9_7_stale_plan(self):
        persona = self.sample(PE)
        self.edit(persona / "card.json", lambda card: self.card_task(card, "T1").__setitem__(
            "minutes_each", self.card_task(card, "T1")["minutes_each"] + 1))
        before = self.snapshot(persona)
        proc = self.cli("backlog", "--json", persona)
        self.assertEqual(proc.returncode, 1)
        body = self.parse(proc)
        self.assertFalse(body["ok"])
        self.assertIn("levelled.json is missing or out of date", body["error"])
        self.assertEqual(body["errors"], [])
        self.assert_unchanged(persona, before)

    def test_data_fault_with_json(self):
        persona = self.sample(PE)
        data = self.plugin_copy()
        (data / "rules.json").write_text("{", encoding="utf-8")
        proc = self.cli("level", "--json", persona)
        self.assertEqual(proc.returncode, 2)
        body = self.parse(proc)
        self.assertFalse(body["ok"])
        self.assertIn("rules.json", body["error"])


# --- Findings 11 and 15: status and date --------------------------------------------------------------

class StatusAndDateTests(Base):

    def test_8_5_dashboard_refuses_an_unknown_status(self):
        persona = self.sample(CS)
        self.edit(persona / "backlog.json",
                  lambda b: b["epic"]["features"][0]["stories"][0]["tasks"][0].__setitem__("status", "blocked"))
        before = self.snapshot(persona)
        from_backlog = self.assert_one_line(self.cli("backlog", persona), 2, "blocked")
        from_dashboard = self.assert_one_line(self.cli("dashboard", persona, "--date", DATE), 2, "blocked")
        self.assertEqual(from_backlog.split(": ", 1)[1], from_dashboard.split(": ", 1)[1])
        self.assert_unchanged(persona, before)

    def test_7_9_date_must_be_ascii_digits(self):
        persona = self.sample(CS)
        before = self.snapshot(persona)
        for bad in ("２０２６-１１-１５", "٢٠٢٦-١١-١٥", "2026-11-15\n", "2026-02-30", "20261115", ""):
            for command in ("dashboard", "all"):
                proc = self.cli(command, persona, "--date", bad)
                self.assert_one_line(proc, 2, "--date")
        self.assert_unchanged(persona, before)
        self.assertEqual(self.cli("dashboard", persona, "--date", DATE).returncode, 0)


# --- Finding 12: every refusal says what to do next ---------------------------------------------------

class NextTests(Base):

    def test_9_14_refusals_end_with_next(self):
        persona = self.sample(PE)
        empty = self.tmp / "empty"
        empty.mkdir()
        for command in ("validate", "level", "backlog", "dashboard", "all"):
            self.assert_one_line(self.cli(command, self.tmp / "no-such-folder"), 2, "no-such-folder")
        for command in ("level", "backlog", "dashboard", "all"):
            self.assert_one_line(self.cli(command, empty), 2, "card.json")
        self.assert_one_line(self.cli("dashboard", persona, "--date", "2026-02-30"), 2, "2026-02-30")
        self.assert_one_line(self.cli(), 2)
        self.assert_one_line(self.cli("level"), 2)
        self.assert_one_line(self.cli("level", persona, "--bogus"), 2)
        self.assert_one_line(self.cli("dashboard", persona, "--date"), 2)

    def test_1_8_1_9_refusal_lines(self):
        persona = self.sample(PE)
        (persona / "backlog.json").unlink()
        proc = self.cli("dashboard", persona, "--date", DATE)
        self.assertEqual(proc.returncode, 1)
        self.assertRegex(proc.stdout.strip().splitlines()[-1], NEXT_LINE)
        self.assert_stderr_has_next(proc)
        (persona / "levelled.json").unlink()
        proc = self.cli("backlog", persona)
        self.assertEqual(proc.returncode, 1)
        self.assertRegex(proc.stdout.strip().splitlines()[-1], NEXT_LINE)
        self.assert_stderr_has_next(proc)

    def test_8_3_unknown_status_line(self):
        persona = self.sample(CS)
        self.edit(persona / "backlog.json",
                  lambda b: b["retired"].append({"id": "S-old.task", "title": "Old", "status": "parked"}))
        self.assert_one_line(self.cli("backlog", persona), 2, "S-old.task")


if __name__ == "__main__":
    unittest.main()
