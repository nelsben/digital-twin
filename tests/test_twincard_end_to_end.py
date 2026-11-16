"""End-to-end check of the 'all' command on the two fictional worked examples.

Each test copies a customer folder (customer-profile.json and the persona folder with card.json and
interviews/) into a temporary folder, runs cli.py as a subprocess the way a consultant runs it, and
compares what it writes with the files committed under engagements/. Nothing is written outside the
temporary folder.

Standard library only. Run with: python3 -m unittest discover -s tests
"""

import copy
import datetime
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "partner-kit" / "plugins" / "twin-consultant" / "scripts" / "twincard" / "cli.py"
SCRIPTS_DIR = ROOT / "partner-kit" / "plugins" / "twin-consultant" / "scripts"
EXPECTATIONS = ROOT / "tests" / "fixtures" / "twincard" / "expectations.json"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from twincard import fields as tc_fields  # noqa: E402

GENERATED = ("levelled.json", "backlog.json", "backlog.md", "dashboard.html")
DATE = "2026-11-15"


def load_expectations():
    return json.loads(EXPECTATIONS.read_text(encoding="utf-8"))


def run_all(persona_dir, *extra):
    """Run 'cli.py all <persona_dir> ...' as a subprocess; return the CompletedProcess."""
    return subprocess.run([sys.executable, str(CLI), "all", str(persona_dir)] + list(extra),
                          capture_output=True, text=True, encoding="utf-8")


def copy_customer(fixture, dest_root):
    """Copy a fixture's customer folder into dest_root without the generated files.

    Keeps the layout <customer>/personas/<persona-id>/; returns the copied persona folder.
    """
    persona_src = ROOT / fixture["persona_dir"]
    customer_src = persona_src.parent.parent
    customer_dst = Path(dest_root) / customer_src.name
    persona_dst = customer_dst / "personas" / persona_src.name
    persona_dst.mkdir(parents=True)
    shutil.copy2(customer_src / "customer-profile.json", customer_dst / "customer-profile.json")
    shutil.copy2(persona_src / "card.json", persona_dst / "card.json")
    shutil.copytree(persona_src / "interviews", persona_dst / "interviews")
    return persona_dst


def first_difference(name, got, want):
    got_lines, want_lines = got.splitlines(), want.splitlines()
    for number in range(max(len(got_lines), len(want_lines))):
        a = got_lines[number] if number < len(got_lines) else "<end of file>"
        b = want_lines[number] if number < len(want_lines) else "<end of file>"
        if a != b:
            return "%s line %d:\n  generated: %s\n  committed: %s" % (name, number + 1, a[:300], b[:300])
    return "%s differs only in its line endings or trailing newline" % name


def resolve(record, data, path, keys, create):
    """Walk an instance path such as tasks.C4.writes[1].action; return (parent, key).

    Same walk as tests/test_twincard_acceptance.py: a list keyed by a field is addressed by that
    field's value (tasks.C4), a positional list by an index (writes[1]).
    """
    tokens = path.split(".")
    node, cat, i = data, [], 0
    while i < len(tokens):
        token = tokens[i]
        m = re.fullmatch(r"([A-Za-z_]+)\[(\d+)\]", token)
        name = m.group(1) if m else token
        list_path = ".".join(cat + [name])
        last = i == len(tokens) - 1
        if m:
            items = node.setdefault(name, []) if create else node.get(name, [])
            index = int(m.group(2))
            if index == len(items) and create:
                items.append({})
            node = items[index]
            cat.append(name + "[]")
            i += 1
        elif keys.get(list_path) is not None and not last:
            matches = [item for item in node.get(name, []) if item.get(keys[list_path]) == tokens[i + 1]]
            node = matches[0]
            cat.append(name + "[]")
            i += 2
        elif last:
            return node, name
        else:
            node = node.setdefault(name, {}) if create else node[name]
            cat.append(name)
            i += 1
    raise KeyError(path)


def apply_changes(persona_dir, changes):
    """Apply an expectations 'change' list to the copied card and profile."""
    persona_dir = Path(persona_dir)
    catalogue = tc_fields.load_catalogue()
    paths = {"card": persona_dir / "card.json",
             "profile": persona_dir.parent.parent / "customer-profile.json"}
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in paths.items()}
    touched = set()
    for change in changes:
        record, path, value = change["record"], change["path"], copy.deepcopy(change["value"])
        data = records[record]
        if path.startswith("provenance."):
            data.setdefault("provenance", {})[path[len("provenance."):]] = value
        else:
            parent, key = resolve(record, data, path, catalogue["keys"][record], create=True)
            parent[key] = value
        touched.add(record)
    for name in touched:
        paths[name].write_text(json.dumps(records[name], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_generated(persona_dir):
    return {name: (Path(persona_dir) / name).read_bytes() for name in GENERATED}


class EndToEndTest(unittest.TestCase):
    def setUp(self):
        self.expectations = load_expectations()
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.counter = 0

    def fresh_copy(self, key):
        self.counter += 1
        return copy_customer(self.expectations["fixtures"][key], self.tmp / ("copy%d" % self.counter))

    def test_all_reproduces_committed_files(self):
        for key, fixture in self.expectations["fixtures"].items():
            with self.subTest(fixture=key):
                persona = self.fresh_copy(key)
                for name in GENERATED:
                    self.assertFalse((persona / name).exists(), "%s must not be copied" % name)
                result = run_all(persona, "--date", DATE)
                expected_exit = 0 if not fixture["blockers"] else 1
                self.assertEqual(result.returncode, expected_exit, result.stdout + result.stderr)
                committed_dir = ROOT / fixture["persona_dir"]
                for name in GENERATED:
                    self.assertTrue((persona / name).is_file(), "%s was not written" % name)
                    got = (persona / name).read_bytes()
                    want = (committed_dir / name).read_bytes()
                    if got != want:
                        self.fail(first_difference(
                            "%s/%s" % (key, name), got.decode("utf-8"), want.decode("utf-8")))

    def test_second_run_changes_nothing(self):
        for key in self.expectations["fixtures"]:
            with self.subTest(fixture=key):
                persona = self.fresh_copy(key)
                self.assertIn(run_all(persona, "--date", DATE).returncode, (0, 1))
                before = read_generated(persona)
                self.assertIn(run_all(persona, "--date", DATE).returncode, (0, 1))
                self.assertEqual(read_generated(persona), before)

    def test_blocker_still_writes_every_file(self):
        variant = next(v for v in self.expectations["variants"] if v["id"] == "team-c4-gmail-send")
        persona = self.fresh_copy(variant["base"])
        apply_changes(persona, variant["change"])
        result = run_all(persona, "--date", DATE)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        for name in GENERATED:
            self.assertTrue((persona / name).is_file(), "%s was not written" % name)
        levelled = json.loads((persona / "levelled.json").read_text(encoding="utf-8"))
        self.assertIn("connector-cannot-write", [b["code"] for b in levelled["blockers"]])
        self.assertIn('data-code="connector-cannot-write"', (persona / "dashboard.html").read_text(encoding="utf-8"))
        self.assertIn("blocked", result.stdout)

    def test_validation_failure_writes_nothing(self):
        persona = self.fresh_copy("team")
        card = json.loads((persona / "card.json").read_text(encoding="utf-8"))
        del card["role"]["name"]
        (persona / "card.json").write_text(json.dumps(card, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        result = run_all(persona, "--date", DATE)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        for name in GENERATED:
            self.assertFalse((persona / name).exists(), "%s must not be written" % name)
        self.assertIn("role.name", result.stdout)
        self.assertIn("failed", result.stdout)
        for step in ("level", "backlog", "dashboard"):
            self.assertRegex(result.stdout, r"(?i)skipped.*\b%s\b" % step)

    def test_task_status_is_kept(self):
        persona = self.fresh_copy("team")
        self.assertEqual(run_all(persona, "--date", DATE).returncode, 0)
        path = persona / "backlog.json"
        backlog = json.loads(path.read_text(encoding="utf-8"))
        task = backlog["epic"]["features"][0]["stories"][0]["tasks"][0]
        task_id = task["id"]
        task["status"] = "done"
        path.write_text(json.dumps(backlog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        self.assertEqual(run_all(persona, "--date", DATE).returncode, 0)
        kept = json.loads(path.read_text(encoding="utf-8"))
        statuses = {t["id"]: t["status"] for f in kept["epic"]["features"] for s in f["stories"] for t in s["tasks"]}
        self.assertEqual(statuses[task_id], "done")
        self.assertIn("- [x] **%s**" % task_id, (persona / "backlog.md").read_text(encoding="utf-8"))
        page = (persona / "dashboard.html").read_text(encoding="utf-8")
        self.assertIn('[x] done</span> <code>%s</code>' % task_id, page)

    def test_usage_errors_exit_2(self):
        result = subprocess.run([sys.executable, str(CLI), "all"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        result = run_all(self.tmp / "no-such-folder")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_no_path_or_today_in_generated_files(self):
        today = datetime.date.today().isoformat()
        for key in self.expectations["fixtures"]:
            with self.subTest(fixture=key):
                persona = self.fresh_copy(key)
                self.assertIn(run_all(persona, "--date", DATE).returncode, (0, 1))
                for name in GENERATED:
                    text = (persona / name).read_text(encoding="utf-8")
                    self.assertNotIn(str(self.tmp), text, name)
                    self.assertNotIn(str(self.tmp.resolve()), text, name)
                    if today != DATE:
                        self.assertNotIn(today, text, name)


if __name__ == "__main__":
    unittest.main()
