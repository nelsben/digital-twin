"""Tests for the dashboard renderer (partner-kit/plugins/twin-consultant/scripts/twincard/dashboard.py).

The page is read with html.parser. Anything the tests write goes to a temporary folder holding a copy of
the fixture's engagement. Design of record: partner-kit/docs/design.md, section 9.

Standard library only. Run with: python3 -m unittest discover -s tests
"""

import datetime
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "partner-kit" / "plugins" / "twin-consultant" / "scripts"
CLI = SCRIPTS_DIR / "twincard" / "cli.py"
EXPECTATIONS = ROOT / "tests" / "fixtures" / "twincard" / "expectations.json"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

DATE = "2026-11-15"
SECTIONS = ["Header", "Anatomy grid", "Feature list", "Blockers and warnings", "Backlog",
            "Open questions", "Where each answer came from"]
TASK_DECISIONS = ("runtime", "identity", "autonomy.start", "autonomy.ceiling", "data_controls", "memory",
                  "plan_fit", "connectors")
PARTS = [("A1", "Persona"), ("A2", "Skills"), ("A3", "Connectors"), ("A4", "Runtime"), ("A5", "Identity"),
         ("A6", "Memory"), ("A7", "Guardrails"), ("A8", "Evaluation"), ("A9", "Distribution and governance")]
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
PAYLOAD = "<script>alert(1)</script>"
MAX_BYTES = 600 * 1024


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def fixtures():
    return load_json(EXPECTATIONS)["fixtures"]


def variant(variant_id):
    for item in load_json(EXPECTATIONS)["variants"]:
        if item["id"] == variant_id:
            return item
    raise KeyError(variant_id)


def kebab(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


class Page(HTMLParser):
    """Reads a dashboard: tag balance, ids, attributes, and the text of each marked element."""

    def __init__(self, text):
        HTMLParser.__init__(self, convert_charrefs=True)
        self.problems, self.ids, self.tags, self.attrs = [], [], [], []
        self.stack = []
        self.sections = []
        self.decisions = {}
        self.codes = []
        self.fields = {}
        self.parts = []
        self.headings = []
        self.style = ""
        self.texts = {}
        self.feed(text)
        self.close()
        if self.stack:
            self.problems.append("unclosed: %s" % [s[0] for s in self.stack])

    def section(self):
        for tag, _, attrs in reversed(self.stack):
            if tag == "section" and "data-section" in attrs:
                return attrs["data-section"]
        return None

    def handle_starttag(self, tag, attrs):
        attrs_d = dict(attrs)
        self.tags.append(tag)
        self.attrs.append((tag, attrs_d))
        if "id" in attrs_d:
            self.ids.append(attrs_d["id"])
        keys = []
        if tag == "section" and "data-section" in attrs_d:
            self.sections.append((attrs_d["data-section"], attrs_d.get("id")))
            keys.append("section:" + attrs_d["data-section"])
        where = self.section()
        if "data-decision" in attrs_d:
            name = attrs_d["data-decision"]
            if name in self.decisions:
                self.problems.append("data-decision %s is used twice" % name)
            self.decisions[name] = {"attrs": attrs_d, "section": where}
            keys.append("decision:" + name)
        if "data-code" in attrs_d:
            self.codes.append({"attrs": attrs_d, "section": where})
            keys.append("code:%s:%s" % (attrs_d["data-code"], attrs_d.get("data-about")))
        if "data-field" in attrs_d:
            keys.append("field:" + attrs_d["data-field"])
        if "data-part" in attrs_d:
            self.parts.append((attrs_d["data-part"], where))
            keys.append("part:" + attrs_d["data-part"])
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.headings.append(int(tag[1]))
        if tag == "style":
            keys.append("style")
        if tag in VOID:
            return
        self.stack.append((tag, keys, attrs_d))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1][0] != tag:
            self.problems.append("end tag %s does not close %s" % (tag, self.stack[-1][0] if self.stack else None))
            return
        self.stack.pop()

    def handle_data(self, data):
        for _, keys, _ in self.stack:
            for key in keys:
                self.texts.setdefault(key, []).append(data)

    def text(self, key):
        return re.sub(r"\s+", " ", "".join(self.texts.get(key, []))).strip()


def set_path(data, path, value):
    """Set a dotted path such as overrides[0].task or plan.tier, creating list items as needed."""
    tokens = path.split(".")
    node = data
    for i, token in enumerate(tokens):
        m = re.fullmatch(r"([A-Za-z_]+)\[(\d+)\]", token)
        last = i == len(tokens) - 1
        if m:
            items = node.setdefault(m.group(1), [])
            index = int(m.group(2))
            while len(items) <= index:
                items.append({})
            if last:
                items[index] = value
            node = items[index]
        elif last:
            node[token] = value
        else:
            node = node.setdefault(token, {})


class Copy(object):
    """A fixture's engagement copied to a temporary folder, with helpers to edit and regenerate it."""

    def __init__(self, fid, tmp):
        fixture = fixtures()[fid]
        persona = ROOT / fixture["persona_dir"]
        engagement = persona.parent.parent
        self.root = Path(tmp) / engagement.name
        shutil.copytree(str(engagement), str(self.root))
        self.persona = self.root / persona.relative_to(engagement)
        self.card_path = self.persona / "card.json"
        self.profile_path = self.root / "customer-profile.json"
        for page in self.root.glob("personas/*/dashboard.html"):  # start with no page, so a write is visible
            page.unlink()

    def edit(self, record, change):
        path = self.card_path if record == "card" else self.profile_path
        data = load_json(path)
        change(data)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def apply_variant(self, variant_id):
        for change in variant(variant_id)["change"]:
            self.edit(change["record"], lambda data, c=change: set_path(data, c["path"], c["value"]))

    def regenerate(self):
        for command in ("level", "backlog"):
            proc = run_cli(command, str(self.persona))
            if proc.returncode not in (0, 1):
                raise AssertionError(proc.stdout + proc.stderr)
        return self


def run_cli(*args):
    return subprocess.run([sys.executable, str(CLI)] + list(args), capture_output=True, text=True,
                          cwd=str(ROOT), timeout=120)


def dashboard_module():
    from twincard import dashboard
    return dashboard


class FixturePageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dash = dashboard_module()
        cls.pages = {}
        for fid, fixture in fixtures().items():
            text = cls.dash.render(str(ROOT / fixture["persona_dir"]), DATE)
            cls.pages[fid] = (text, Page(text))

    def test_page_parses_with_every_tag_closed_and_no_duplicate_id(self):
        for fid, (text, page) in self.pages.items():
            self.assertTrue(text.startswith("<!DOCTYPE html>"), fid)
            self.assertEqual(page.problems, [], fid)
            self.assertEqual(len(page.ids), len(set(page.ids)), fid)
            self.assertEqual(page.tags.count("html"), 1, fid)

    def test_no_script_no_handler_no_external_reference(self):
        for fid, (text, page) in self.pages.items():
            self.assertNotIn("script", page.tags, fid)
            self.assertNotIn("<script", text.lower(), fid)
            self.assertEqual(page.tags.count("style"), 1, fid)
            for tag in ("link", "img", "iframe", "object", "embed", "source", "audio", "video", "form", "base"):
                self.assertNotIn(tag, page.tags, "%s: %s" % (fid, tag))
            for tag, attrs in page.attrs:
                for name, value in attrs.items():
                    self.assertFalse(name.startswith("on"), "%s: %s has %s" % (fid, tag, name))
                    self.assertNotIn(name, ("src", "srcset", "action", "formaction", "background"), fid)
                    if name == "href":
                        self.assertTrue(value.startswith("#"), "%s: href %s" % (fid, value))
                    self.assertNotRegex(value or "", r"(?i)javascript:|https?:|^//", "%s: %s" % (fid, name))
            style = page.text("style")
            self.assertNotIn("url(", style, fid)
            self.assertNotIn("@import", style, fid)
            self.assertNotIn("//", style, fid)

    def test_seven_sections_in_order_with_kebab_ids_and_contents_links(self):
        for fid, (_, page) in self.pages.items():
            self.assertEqual([name for name, _ in page.sections], SECTIONS, fid)
            self.assertEqual([sid for _, sid in page.sections], [kebab(n) for n in SECTIONS], fid)
            hrefs = [attrs.get("href") for tag, attrs in page.attrs if tag == "a"]
            for name in SECTIONS:
                self.assertIn("#" + kebab(name), hrefs, fid)

    def test_nine_anatomy_panels(self):
        for fid, (_, page) in self.pages.items():
            parts = [p for p, where in page.parts if where == "Anatomy grid"]
            self.assertEqual(parts, [p for p, _ in PARTS], fid)
            for part, name in PARTS:
                text = page.text("part:" + part)
                self.assertIn(part, text, fid)
                self.assertIn(name, text, fid)
                self.assertRegex(text, r"Required fields answered: \d+ of \d+", "%s %s" % (fid, part))
                self.assertRegex(text, r"Backlog tasks done: \d+ of \d+", "%s %s" % (fid, part))

    def test_every_card_task_appears_with_all_its_decisions(self):
        for fid, fixture in fixtures().items():
            _, page = self.pages[fid]
            card = load_json(ROOT / fixture["persona_dir"] / "card.json")
            features = page.text("section:Feature list")
            for task in card["tasks"]:
                self.assertIn(task["name"], features, fid)
                for name in TASK_DECISIONS:
                    key = "%s.%s" % (task["id"], name)
                    self.assertIn(key, page.decisions, fid)
                    self.assertEqual(page.decisions[key]["section"], "Feature list", key)

    def test_null_ceiling_shows_undecided(self):
        # Every trigger now has a ceiling rule with a level, so neither fixture has a null ceiling.
        # A null ceiling is still possible (a rule whose fact is empty), so set one by hand and rebuild.
        with tempfile.TemporaryDirectory() as tmp:
            work = Copy("pe", tmp).regenerate()
            path = work.persona / "levelled.json"
            levelled = load_json(path)
            levelled["tasks"]["T4"]["autonomy"]["ceiling"]["value"] = None
            path.write_text(json.dumps(levelled, indent=2), encoding="utf-8")
            proc = run_cli("backlog", str(work.persona))
            self.assertIn(proc.returncode, (0, 1), proc.stdout + proc.stderr)
            page = Page(self.dash.render(str(work.persona), DATE))
        self.assertIn("undecided", page.text("decision:T4.autonomy.ceiling"))

    def test_header(self):
        for fid, fixture in fixtures().items():
            _, page = self.pages[fid]
            want = fixture["validate"]
            self.assertEqual(page.text("field:completeness"), "%d%%" % want["completeness_pct"], fid)
            self.assertEqual(page.text("field:complete"), "Complete" if want["complete"] else "Not complete", fid)
            header = page.text("section:Header")
            self.assertIn("Fictional sample", header, fid)
            self.assertIn("Generated " + DATE, header, fid)
            self.assertRegex(page.text("field:sponsor-line"),
                             r"Tasks in the pilot: \d+\. Blockers: \d+\. Backlog tasks done: \d+ of \d+\.", fid)

    def test_title_is_the_role_plus_twin(self):
        for fid, (text, _) in self.pages.items():
            title = re.search(r"<title>(.*?)</title>", text).group(1)
            self.assertTrue(title.endswith(" twin"), title)
            self.assertTrue(2 <= len(title.split()) <= 4, title)

    def test_headings_in_order(self):
        for fid, (_, page) in self.pages.items():
            self.assertEqual(page.headings[0], 1, fid)
            self.assertEqual(page.headings.count(1), 1, fid)
            self.assertLessEqual(max(page.headings), 3, fid)
            for before, after in zip(page.headings, page.headings[1:]):
                self.assertLessEqual(after, before + 1, fid)

    def test_three_theme_rules_print_rule_and_body_colours(self):
        for fid, (_, page) in self.pages.items():
            style = page.text("style")
            self.assertRegex(style, r":root\s*\{[^}]*--", fid)
            self.assertIn("@media (prefers-color-scheme: dark)", style, fid)
            self.assertIn(':root:not([data-theme="light"])', style, fid)
            self.assertIn(':root[data-theme="dark"]', style, fid)
            self.assertRegex(style, r"body\s*\{[^}]*background:[^}]*color:", fid)
            self.assertRegex(style, r"@media print\s*\{[^@]*details", fid)

    def test_blockers_section_says_none_in_words(self):
        for fid, (_, page) in self.pages.items():
            self.assertIn("No blockers.", page.text("section:Blockers and warnings"), fid)

    def test_every_warning_is_an_entry_in_the_blockers_section(self):
        for fid, fixture in fixtures().items():
            _, page = self.pages[fid]
            levelled = load_json(ROOT / fixture["persona_dir"] / "levelled.json")
            got = [(c["attrs"]["data-code"], c["attrs"]["data-about"]) for c in page.codes
                   if c["section"] == "Blockers and warnings"]
            want = [(w["code"], w["about"]) for w in levelled["blockers"] + levelled["warnings"]]
            self.assertEqual(sorted(got), sorted(want), fid)

    def test_size_under_600_kb(self):
        for fid, (text, _) in self.pages.items():
            self.assertLess(len(text.encode("utf-8")), MAX_BYTES, fid)

    def test_same_inputs_and_date_give_the_same_bytes(self):
        for fid, fixture in fixtures().items():
            again = self.dash.render(str(ROOT / fixture["persona_dir"]), DATE)
            self.assertEqual(again, self.pages[fid][0], fid)


class EscapingTests(unittest.TestCase):
    def test_card_text_and_system_name_are_escaped(self):
        dash = dashboard_module()
        with tempfile.TemporaryDirectory() as tmp:
            work = Copy("team", tmp)
            work.edit("card", lambda c: c["tasks"][0].update(name='Brief %s "quoted brief"' % PAYLOAD))
            work.edit("profile", lambda p: p["systems"][0].update(product='HubSpot %s "crm name"' % PAYLOAD))
            work.regenerate()
            text = dash.render(str(work.persona), DATE)
        page = Page(text)
        self.assertNotIn(PAYLOAD, text)
        self.assertNotIn("script", page.tags)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", text)
        self.assertNotIn('"quoted brief"', text)
        self.assertNotIn('"crm name"', text)
        self.assertIn("&quot;quoted brief&quot;", text)
        self.assertIn("&quot;crm name&quot;", text)
        self.assertIn("&quot;crm name&quot;", text[text.index('data-part="A3"'):])


class VariantPageTests(unittest.TestCase):
    def test_override_variant_shows_overridden_with_rule_result_and_reason(self):
        dash = dashboard_module()
        item = variant("team-override-c1-ceiling")
        key, want = next((k, d) for k, d in item["expect"]["decisions"].items() if d.get("overridden"))
        with tempfile.TemporaryDirectory() as tmp:
            work = Copy("team", tmp)
            work.apply_variant(item["id"])
            work.regenerate()
            page = Page(dash.render(str(work.persona), DATE))
        cell = page.text("decision:" + key)
        self.assertIn("Overridden", cell)
        self.assertIn("rule's result: %s" % want["rule_result"], cell)
        self.assertIn(want["override_reason"], cell)
        self.assertIn("Marisol Quenby", cell)
        self.assertIn(str(want["expected"]), cell)

    def test_blocker_variant_shows_the_blocker_and_not_complete(self):
        item = variant("team-individual-plan")
        with tempfile.TemporaryDirectory() as tmp:
            work = Copy("team", tmp)
            work.apply_variant(item["id"])
            work.regenerate()
            proc = run_cli("dashboard", str(work.persona), "--date", DATE)
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            out = work.persona / "dashboard.html"
            self.assertTrue(out.is_file(), "a blocker still writes the page")
            page = Page(out.read_text(encoding="utf-8"))
        self.assertEqual(page.text("field:complete"), "Not complete")
        blockers = [(c["attrs"]["data-code"], c["attrs"]["data-about"]) for c in page.codes
                    if c["section"] == "Blockers and warnings"]
        for b in item["expect"]["blockers_added"]:
            self.assertIn((b["code"], b["about"]), blockers)
        self.assertNotIn("No blockers.", page.text("section:Blockers and warnings"))
        self.assertIn("1 blocker", page.text("field:complete-reasons"))


class InputTests(unittest.TestCase):
    def check_refused(self, work, file_name, command):
        dash = dashboard_module()
        with self.assertRaises(dash.DashboardError) as caught:
            dash.render(str(work.persona), DATE)
        message = str(caught.exception)
        self.assertIn(file_name, message)
        self.assertIn("run the %s command" % command, message)
        proc = run_cli("dashboard", str(work.persona), "--date", DATE)
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn(file_name, proc.stdout + proc.stderr)
        self.assertFalse((work.persona / "dashboard.html").exists())

    def test_missing_levelled(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Copy("pe", tmp)
            (work.persona / "levelled.json").unlink()
            self.check_refused(work, "levelled.json is missing", "level")

    def test_missing_backlog(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Copy("pe", tmp)
            (work.persona / "backlog.json").unlink()
            self.check_refused(work, "backlog.json is missing", "backlog")

    def test_out_of_date_levelled(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Copy("team", tmp)
            work.edit("card", lambda c: c["tasks"][0].update(minutes_each=31))
            self.check_refused(work, "levelled.json is out of date", "level")

    def test_out_of_date_levelled_after_a_profile_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Copy("team", tmp)
            work.edit("profile", lambda p: p["plan"].update(seats=61))
            self.check_refused(work, "levelled.json is out of date", "level")

    def test_out_of_date_backlog(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Copy("team", tmp)
            work.edit("card", lambda c: c["tasks"][0].update(minutes_each=31))
            self.assertEqual(run_cli("level", str(work.persona)).returncode, 0)
            self.check_refused(work, "backlog.json is out of date", "backlog")

    def test_validation_errors_write_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Copy("team", tmp)
            work.edit("card", lambda c: c["tasks"][0].update(trigger="whenever"))
            proc = run_cli("dashboard", str(work.persona), "--date", DATE)
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            self.assertIn("tasks.C1.trigger", proc.stdout)
            self.assertFalse((work.persona / "dashboard.html").exists())


class DateAndCommandTests(unittest.TestCase):
    def test_the_generated_date_is_the_only_thing_the_date_changes(self):
        dash = dashboard_module()
        persona = str(ROOT / fixtures()["team"]["persona_dir"])
        first, second = dash.render(persona, "2031-01-02"), dash.render(persona, "2032-03-04")
        self.assertEqual(first.count("2031-01-02"), 1)
        self.assertNotIn("2032-03-04", first)
        self.assertEqual(first.replace("2031-01-02", "2032-03-04"), second)

    def test_a_date_that_is_not_a_calendar_date_is_a_usage_error(self):
        dash = dashboard_module()
        persona = str(ROOT / fixtures()["team"]["persona_dir"])
        for bad in ("2026-02-30", "2026-13-01", "2026-11-5", "15/11/2026", "20261115", "tomorrow"):
            with self.assertRaises(dash.UsageError, msg=bad):
                dash.render(persona, bad)
            with tempfile.TemporaryDirectory() as tmp:
                work = Copy("team", tmp)
                proc = run_cli("dashboard", str(work.persona), "--date", bad)
                self.assertEqual(proc.returncode, 2, bad)
                self.assertFalse((work.persona / "dashboard.html").exists(), bad)

    def test_no_date_means_today(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Copy("team", tmp)
            before = datetime.date.today().isoformat()
            proc = run_cli("dashboard", str(work.persona))
            after = datetime.date.today().isoformat()
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            text = (work.persona / "dashboard.html").read_text(encoding="utf-8")
        self.assertTrue("Generated " + before in text or "Generated " + after in text)

    def test_command_writes_prints_and_exits_0_and_is_byte_identical(self):
        for fid in fixtures():
            with tempfile.TemporaryDirectory() as tmp:
                work = Copy(fid, tmp)
                out = work.persona / "dashboard.html"
                if out.exists():
                    out.unlink()
                proc = run_cli("dashboard", str(work.persona), "--date", DATE)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertIn(str(out), proc.stdout)
                self.assertRegex(proc.stdout, r"Completeness: \d+%.*Blockers: \d+.*Warnings: \d+.*"
                                              r"Backlog: \d+ of \d+ tasks done")
                first = out.read_bytes()
                self.assertEqual(run_cli("dashboard", str(work.persona), "--date", DATE).returncode, 0)
                self.assertEqual(out.read_bytes(), first, fid)

    def test_usage_errors_exit_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(run_cli("dashboard", str(Path(tmp) / "nowhere"), "--date", DATE).returncode, 2)
            self.assertEqual(run_cli("dashboard", tmp, "--date", DATE).returncode, 2)

    def test_write_dashboard_writes_and_render_does_not(self):
        dash = dashboard_module()
        with tempfile.TemporaryDirectory() as tmp:
            work = Copy("team", tmp)
            out = work.persona / "dashboard.html"
            if out.exists():
                out.unlink()
            text = dash.render(str(work.persona), DATE)
            self.assertFalse(out.exists())
            result = dash.write_dashboard(str(work.persona), DATE)
            self.assertTrue(result["ok"])
            self.assertEqual(out.read_bytes(), text.encode("utf-8"))

    def test_other_commands_still_work(self):
        persona = fixtures()["team"]["persona_dir"]
        self.assertEqual(run_cli("validate", persona).returncode, 0)
        with tempfile.TemporaryDirectory() as tmp:
            work = Copy("team", tmp)
            self.assertEqual(run_cli("level", str(work.persona)).returncode, 0)
            self.assertEqual(run_cli("backlog", str(work.persona)).returncode, 0)


if __name__ == "__main__":
    unittest.main()
