"""validate opens every answered source, and an open field holds no value (OPS-46).

The design of record is partner-kit/docs/design.md, section 4.3. A provenance source is one
source or several separated by '; '. Each is '<file>' or '<file>#<anchor>', looked up in the
record's own folder and then in the customer folder, never outside the customer folder. For an
entry with status answered every source must open:

* a file under interviews/ needs a question-id anchor and a heading line ('## F2.' to
  '###### F2.') for it; for a tasks.<id>.* field the heading is inside that task's block;
* discovery.md needs an anchor and a table row whose first cell is that id;
* any other file must exist, and an anchor, when given, is the GitHub slug of one of its headings.

Entries with status default, assumed or open are not opened. An open entry's field is empty:
null, an empty string or an empty list (false is a value).

Every case runs on a temporary copy of a committed sample. Standard library only.
Run with: python3 -m unittest discover -s tests
"""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "partner-kit" / "plugins" / "twin-consultant" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from twincard import dashboard  # noqa: E402
from twincard.validate import validate  # noqa: E402

SAMPLES = {
    "pe": ROOT / "engagements" / "sample-pe" / "personas" / "deal-team-associate",
    "team": ROOT / "engagements" / "sample-team-cs" / "personas" / "customer-success-manager",
}
OWNED = {"owner": "Test owner", "due": "2026-12-11"}


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def task(card, task_id):
    return next(t for t in card["tasks"] if t["id"] == task_id)


def run(sample, change):
    """Copy the sample's customer folder, apply change(profile, card, customer_dir), validate the copy."""
    persona_src = SAMPLES[sample]
    customer_src = persona_src.parent.parent
    with tempfile.TemporaryDirectory() as tmp:
        customer = Path(tmp) / "engagements" / customer_src.name
        shutil.copytree(customer_src, customer)
        persona = customer / "personas" / persona_src.name
        profile, card = load(customer / "customer-profile.json"), load(persona / "card.json")
        change(profile, card, customer)
        (customer / "customer-profile.json").write_text(json.dumps(profile, indent=2), encoding="utf-8")
        (persona / "card.json").write_text(json.dumps(card, indent=2), encoding="utf-8")
        return validate(str(persona))


def errors_at(result, record, path):
    return [e for e in result["errors"] if e["record"] == record and e["path"] == path]


class AnsweredSourcesOpen(unittest.TestCase):
    def assert_source_error(self, result, record, path, names):
        found = errors_at(result, record, path)
        self.assertTrue(found, "no error for %s:%s; errors: %s" % (record, path, result["errors"]))
        text = " ".join(e["message"] for e in found)
        self.assertIn(names, text)
        self.assertTrue(all("point the source at the notes or discovery line" in e["fix"].lower() for e in found), found)

    def test_a_missing_file_is_an_error(self):
        def change(profile, card, customer):
            card["provenance"]["voice.tone"] = {"status": "answered", "source": "interviews/2026-01-01-nobody.md#P4"}
        result = run("team", change)
        self.assertFalse(result["ok"])
        self.assert_source_error(result, "card", "voice.tone", "interviews/2026-01-01-nobody.md")

    def test_a_missing_question_heading_is_an_error(self):
        def change(profile, card, customer):
            card["provenance"]["voice.tone"] = {"status": "answered", "source": "interviews/2026-11-06-csm.md#P7"}
        self.assert_source_error(run("team", change), "card", "voice.tone", "#P7")

    def test_an_interview_source_needs_a_question_anchor(self):
        def change(profile, card, customer):
            card["provenance"]["voice.tone"] = {"status": "answered", "source": "interviews/2026-11-06-csm.md"}
        self.assert_source_error(run("team", change), "card", "voice.tone", "interviews/2026-11-06-csm.md")

    def test_a_heading_only_in_another_tasks_block_is_an_error(self):
        # The senior CSM's notes have F2 headings for C2, C3 and C5, not for C1.
        def change(profile, card, customer):
            card["provenance"]["tasks.C1.data_class"] = {
                "status": "answered", "source": "interviews/2026-11-07-senior-csm.md#F2"}
            card["provenance"]["tasks.C2.data_class"] = {
                "status": "answered", "source": "interviews/2026-11-07-senior-csm.md#F2"}
        result = run("team", change)
        self.assert_source_error(result, "card", "tasks.C1.data_class", "C1")
        self.assertEqual(errors_at(result, "card", "tasks.C2.data_class"), [])

    def test_a_discovery_id_with_no_row_is_an_error(self):
        def change(profile, card, customer):
            profile["provenance"]["display_name"] = {"status": "answered", "source": "discovery.md#A9"}
            profile["provenance"]["industry"] = {"status": "answered", "source": "discovery.md#A2"}
        result = run("pe", change)
        self.assert_source_error(result, "profile", "display_name", "#A9")
        self.assertEqual(errors_at(result, "profile", "industry"), [])

    def test_a_discovery_source_needs_an_anchor(self):
        def change(profile, card, customer):
            profile["provenance"]["industry"] = {"status": "answered", "source": "discovery.md"}
        self.assert_source_error(run("pe", change), "profile", "industry", "discovery.md")

    def test_a_card_finds_discovery_in_the_customer_folder(self):
        def change(profile, card, customer):
            card["provenance"]["role.headcount"] = {"status": "answered", "source": "discovery.md#A3"}
        self.assertEqual(errors_at(run("pe", change), "card", "role.headcount"), [])

    def test_a_source_outside_the_record_and_customer_folders_is_an_error(self):
        def change(profile, card, customer):
            card["provenance"]["role.headcount"] = {"status": "answered", "source": "../../discovery.md#A3"}
            profile["provenance"]["industry"] = {"status": "answered", "source": "../sample-pe/discovery.md#A2"}
        result = run("pe", change)
        self.assert_source_error(result, "card", "role.headcount", "../../discovery.md")
        self.assert_source_error(result, "profile", "industry", "../sample-pe/discovery.md")

    def test_a_two_source_entry_with_one_bad_source_is_an_error(self):
        def change(profile, card, customer):
            card["provenance"]["voice.tone"] = {
                "status": "answered",
                "source": "interviews/2026-11-06-csm.md#P4; interviews/2026-11-07-senior-csm.md#P8"}
            card["provenance"]["voice.serves"] = {
                "status": "answered",
                "source": "interviews/2026-11-06-csm.md#P2; interviews/2026-11-07-senior-csm.md#P2"}
        result = run("team", change)
        found = errors_at(result, "card", "voice.tone")
        self.assertEqual(len(found), 1, found)
        self.assertIn("2026-11-07-senior-csm.md#P8", found[0]["message"])
        self.assertNotIn("2026-11-06-csm.md#P4", found[0]["message"])
        self.assertEqual(errors_at(result, "card", "voice.serves"), [])

    def test_two_bad_sources_on_one_entry_give_two_errors(self):
        def change(profile, card, customer):
            card["provenance"]["voice.tone"] = {
                "status": "answered",
                "source": "interviews/2026-11-06-csm.md#P8; interviews/2026-11-07-senior-csm.md#P9"}
        self.assertEqual(len(errors_at(run("team", change), "card", "voice.tone")), 2)

    def test_an_anchor_on_another_file_must_match_a_heading(self):
        def change(profile, card, customer):
            profile["owners"]["compliance"] = "Chief Compliance Officer"
            profile["provenance"]["owners.compliance"] = {"status": "answered", "source": "stakeholders.md#no-such-heading"}
            profile["provenance"]["owners.sponsor"] = {"status": "answered", "source": "stakeholders.md#customer-roles"}
            profile["provenance"]["owners.business_owner"] = {"status": "answered", "source": "stakeholders.md"}
            profile["provenance"]["owners.backup_owner"] = {"status": "answered", "source": "no-such-file.md"}
        result = run("pe", change)
        self.assert_source_error(result, "profile", "owners.compliance", "#no-such-heading")
        self.assertEqual(errors_at(result, "profile", "owners.sponsor"), [])
        self.assertEqual(errors_at(result, "profile", "owners.business_owner"), [])
        self.assert_source_error(result, "profile", "owners.backup_owner", "no-such-file.md")


class OpenFieldIsEmpty(unittest.TestCase):
    def test_an_open_entry_holding_a_value_is_an_error(self):
        def change(profile, card, customer):
            for path in ("tasks.C1.touches_money", "voice.tone", "voice.never"):
                card["provenance"][path] = dict({"status": "open", "source": "interviews/2026-11-06-csm.md#F7"}, **OWNED)
            task(card, "C1")["touches_money"] = False
            card["voice"]["tone"] = "Warm"
            card["voice"]["never"] = ["Send an email to a customer"]
        result = run("team", change)
        for path in ("tasks.C1.touches_money", "voice.tone", "voice.never"):
            with self.subTest(path=path):
                found = errors_at(result, "card", path)
                self.assertEqual(len(found), 1, result["errors"])
                self.assertIn("open", found[0]["message"])
                self.assertIn("empty the value, or set the status to assumed with an owner", found[0]["fix"].lower())

    def test_an_open_entry_with_an_empty_value_is_not_an_error(self):
        def change(profile, card, customer):
            for path in ("tasks.C1.touches_money", "voice.tone", "voice.never"):
                card["provenance"][path] = dict({"status": "open", "source": "interviews/2026-11-06-csm.md#F7"}, **OWNED)
            task(card, "C1")["touches_money"] = None
            card["voice"]["tone"] = ""
            card["voice"]["never"] = []
        result = run("team", change)
        for path in ("tasks.C1.touches_money", "voice.tone", "voice.never"):
            self.assertEqual(errors_at(result, "card", path), [], path)


class OtherStatusesAreNotOpened(unittest.TestCase):
    def test_default_assumed_and_open_sources_are_not_opened(self):
        def change(profile, card, customer):
            card["provenance"]["tasks.C1.data_class"] = {"status": "default", "source": "data/industry-packs/nowhere.json"}
            card["provenance"]["voice.tone"] = {"status": "assumed", "source": "interviews/2026-01-01-nobody.md#P4",
                                                "owner": "Test owner"}
            card["voice"]["never"] = []
            card["provenance"]["voice.never"] = dict({"status": "open", "source": "nowhere.md#nothing"}, **OWNED)
        result = run("team", change)
        for path in ("tasks.C1.data_class", "voice.tone", "voice.never"):
            self.assertEqual(errors_at(result, "card", path), [], path)


class CommittedSamples(unittest.TestCase):
    def test_both_samples_validate_with_no_error(self):
        for name, persona in SAMPLES.items():
            with self.subTest(sample=name):
                result = validate(str(persona))
                self.assertEqual(result["errors"], [])


class DashboardListsEverySource(unittest.TestCase):
    def test_a_two_source_entry_lists_both_files(self):
        ctx = {
            "card": {"provenance": {
                "voice.serves": {"status": "answered",
                                 "source": "interviews/2026-11-06-a.md#P2; interviews/2026-11-07-b.md#P2"},
                "voice.tone": {"status": "assumed", "owner": "Test owner",
                               "source": "interviews/2026-11-08-c.md#P4; discovery.md#A1"},
            }},
            "profile": {"provenance": {}},
        }
        html = dashboard.render_provenance(ctx)
        for name in ("2026-11-06-a.md", "2026-11-07-b.md", "2026-11-08-c.md"):
            self.assertIn("<li><code>interviews/%s</code></li>" % name, html)
        self.assertIn("2026-11-08-c.md#P4; discovery.md#A1", html)


class DiscoveryTemplate(unittest.TestCase):
    TEMPLATE = ROOT / "partner-kit" / "plugins" / "twin-consultant" / "templates" / "discovery.md"
    PLAYBOOK = ROOT / "docs" / "playbook" / "02-discovery.md"

    @staticmethod
    def row_ids(text):
        return [line.split("|")[1].strip() for line in text.splitlines()
                if line.startswith("|") and line.split("|")[1].strip()[:1] in "ABCDEFG"
                and line.split("|")[1].strip()[1:].isdigit()]

    def test_its_ids_are_the_playbook_ids_in_order(self):
        template = self.TEMPLATE.read_text(encoding="utf-8")
        playbook = self.PLAYBOOK.read_text(encoding="utf-8")
        self.assertEqual(self.row_ids(template), self.row_ids(playbook))
        self.assertEqual(len(self.row_ids(template)), len(set(self.row_ids(template))))

    def test_one_table_per_section_with_the_five_columns(self):
        lines = self.TEMPLATE.read_text(encoding="utf-8").splitlines()
        sections = [line[3] for line in lines if line.startswith("## ")]
        self.assertEqual(sections, list("ABCDEFG"))
        headers = [line for line in lines if line.startswith("| #")]
        self.assertEqual(headers, ["| # | Answer | Status | Owner | Due |"] * 7)

    def test_it_holds_no_question_text_and_states_the_status_rule(self):
        text = self.TEMPLATE.read_text(encoding="utf-8")
        self.assertNotIn("?", text)
        head = "\n".join(text.splitlines()[:4])
        self.assertIn("docs/playbook/02-discovery.md", head)
        self.assertIn("answered or open", head)
        self.assertIn("Every open row needs an owner and a due date", head)


if __name__ == "__main__":
    unittest.main()
