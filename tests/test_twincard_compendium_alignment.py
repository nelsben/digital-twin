"""The kit says what compendium pages 05, 11 and 18 say about connector write access, Outlook and the
Agent SDK (OPS-62).

Page 11 marks Gmail and Google Calendar write access ⚠ Conflict, its Slack row names send tools, it has an
Outlook row, and page 05 marks the Agent SDK's release status unverified. These tests check that the
industry packs, the levelling rules, the task library and the runbook restate that and no longer state the
old facts.

Standard library only. Run with: python3 -m unittest tests.test_twincard_compendium_alignment
"""

import json
import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

import test_twincard_level as LT  # noqa: E402
import test_twincard_backlog as TB  # noqa: E402

ROOT = TESTS_DIR.parent
DATA = LT.PLUGIN_DIR / "data"
PACKS = ("general", "b2b-software")
OLD_PHRASES = ("reads and searches only", "Read and search only", "It reads only", "Read only: it can",
               "Whether it can post is unconfirmed", "whether it exposes send tools",
               "asks a person to confirm each change")
OLD_CODES = ("mail-read-only", "connector-cannot-write")
RUNNER = ROOT / "starter-kit" / "runbooks" / "agent-sdk-runner.md"
NEW_TEMPLATE = "warning-mail-write-unconfirmed"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def defaults(pack_id):
    return load(DATA / "industry-packs" / ("%s.json" % pack_id))["connector_defaults"]


class PackTests(unittest.TestCase):
    def test_no_old_phrase_in_any_how(self):
        for pack_id in PACKS:
            for entry in defaults(pack_id):
                for phrase in OLD_PHRASES:
                    with self.subTest(pack=pack_id, product=entry["product"], phrase=phrase):
                        self.assertNotIn(phrase, entry["how"])

    def test_gmail_and_calendar_say_conflict(self):
        for pack_id in PACKS:
            found = [e for e in defaults(pack_id) if e["product"] in ("Gmail", "Google Calendar")]
            self.assertEqual(sorted(e["product"] for e in found), ["Gmail", "Google Calendar"], pack_id)
            for entry in found:
                with self.subTest(pack=pack_id, product=entry["product"]):
                    self.assertIn("conflict", entry["how"].lower())
                    self.assertIs(entry["unverified"], True)

    def test_general_has_outlook(self):
        outlook = [e for e in defaults("general") if e["product"] == "Outlook"]
        self.assertEqual(len(outlook), 1)
        entry = outlook[0]
        self.assertEqual(entry["system_kind"], "email-calendar")
        self.assertTrue(entry["runbook"])
        self.assertTrue((ROOT / entry["runbook"]).is_file(), entry["runbook"])
        self.assertIs(entry["unverified"], True)


class RuleTests(unittest.TestCase):
    def test_no_cannot_write_rule(self):
        rules = load(LT.RULES)["rules"]
        self.assertEqual([r["id"] for r in rules if r["then"] == "connector-cannot-write"], [])
        found = [r for r in rules if r["id"] == "warn-mail-write-unconfirmed"]
        self.assertEqual(len(found), 1)
        self.assertIs(found[0]["unverified"], True)
        self.assertEqual(found[0]["then"], "mail-write-unconfirmed")

    def test_team_c4_gmail_send(self):
        out = LT.run_level(LT.TEAM, LT.team_c4_gmail_send)
        self.assertNotIn("connector-cannot-write", [b["code"] for b in out["blockers"]])
        self.assertIn(("mail-write-unconfirmed", "C4"), [(w["code"], w["about"]) for w in out["warnings"]])


class TextTests(unittest.TestCase):
    def test_no_old_code_in_the_kits(self):
        for top in ("partner-kit", "starter-kit"):
            for path in sorted((ROOT / top).rglob("*")):
                if not path.is_file():
                    continue
                try:
                    text = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue
                for code in OLD_CODES:
                    with self.subTest(path=str(path.relative_to(ROOT)), code=code):
                        self.assertFalse(code in text, "%s names %s" % (path.relative_to(ROOT), code))

    def test_agent_sdk_runner(self):
        text = RUNNER.read_text(encoding="utf-8")
        self.assertFalse("lists the Agent SDK as generally available" in text,
                         "agent-sdk-runner.md still says page 05 lists the Agent SDK as generally available")

    def test_new_template_links_resolve(self):
        templates = dict((t["id"], t) for t in load(DATA / "task-library.json")["templates"])
        self.assertIn(NEW_TEMPLATE, templates)
        steps = templates[NEW_TEMPLATE]["how"]
        self.assertTrue(steps)
        for step in steps:
            with self.subTest(link=step["link"]):
                self.assertTrue(step["link"])
                self.assertIsNone(TB.link_problem(step["link"]))


if __name__ == "__main__":
    unittest.main()
