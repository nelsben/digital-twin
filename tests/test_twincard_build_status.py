"""Tests for build status in the backlog and the dashboard (OPS-77).

The design of record is partner-kit/docs/design.md, sections 8, 8a and 9. When <persona>/build/build.json
exists, backlog.py gives each task story's write-skill, write-evals, trigger-evals, publish-in-role-plugin
and runtime setup tasks an `artifact` key {id, path, status}, and raises (never lowers) the task's status
from the artifact's status; backlog.json's source gains build_sha256; the dashboard gains a Build section
after the plan. With no build.json both outputs are what they were before.

Every test that changes build.json works on a temporary copy of a fictional sample customer.

Standard library only. Run with: python3 -m unittest tests.test_twincard_build_status
"""

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
ROOT = TESTS_DIR.parent
PLUGIN_DIR = ROOT / "partner-kit" / "plugins" / "twin-consultant"
CLI = PLUGIN_DIR / "scripts" / "twincard" / "cli.py"
DESIGN = ROOT / "partner-kit" / "docs" / "design.md"
DATE = "2026-11-15"
PE = (ROOT / "engagements" / "sample-pe", "deal-team-associate")
CS = (ROOT / "engagements" / "sample-team-cs", "customer-success-manager")
SAMPLES = (PE, CS)
GENERATED = ("levelled.json", "backlog.json", "backlog.md", "dashboard.html")
AUTHORING = ("write-skill", "write-evals", "trigger-evals")
PUBLISH = ("publish-in-role-plugin", "publish-in-role-plugin-team")
SETUP = ("setup-scheduled-task", "setup-tag-routine", "setup-managed-agents", "setup-managed-agents-self-hosted",
         "setup-agent-sdk")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dump(path, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def cli(*args):
    return subprocess.run([sys.executable, str(CLI)] + [str(a) for a in args], capture_output=True, text=True,
                          encoding="utf-8")


class Copy(object):
    """A temporary copy of a sample customer; yields (customer folder, persona folder)."""

    def __init__(self, sample):
        self.customer, self.persona = sample

    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name) / "engagements" / self.customer.name
        shutil.copytree(str(self.customer), str(root))
        return root, root / "personas" / self.persona

    def __exit__(self, *exc):
        self.tmp.cleanup()


def tasks_of(persona):
    """{task id: task} of the persona's backlog.json."""
    backlog = load(Path(persona) / "backlog.json")
    return dict((t["id"], t) for f in backlog["epic"]["features"] for s in f["stories"] for t in s["tasks"])


def set_build(persona, statuses, history=None):
    path = Path(persona) / "build" / "build.json"
    data = load(path)
    for item in data["artifacts"]:
        if item["id"] in statuses:
            item["status"] = statuses[item["id"]]
        if history and item["id"] in history:
            item["history"] = history[item["id"]]
    dump(path, data)


def fresh_backlog(persona, reset=True):
    """Run the backlog command; with reset, from no earlier backlog.json, so every status starts at todo."""
    if reset and (Path(persona) / "backlog.json").exists():
        (Path(persona) / "backlog.json").unlink()
    out = cli("backlog", persona)
    return out


def of_story(tasks, story, templates):
    return dict((t["template"], t) for tid, t in tasks.items() if tid.startswith(story + ".")
                and t["template"] in templates)


def strip_artifacts(text):
    return "\n".join(line for line in text.split("\n") if not line.startswith("  - Artifact:"))


def strip_backlog_json(data):
    for feature in data["epic"]["features"]:
        for story in feature["stories"]:
            for task in story["tasks"]:
                task.pop("artifact", None)
    data["source"].pop("build_sha256", None)
    return data


def strip_build_section(page):
    page = re.sub(r'<section data-section="Build".*?</section>\n', "", page, flags=re.S)
    return page.replace('<li><a href="#build">Build</a></li>', "")


class MappingTests(unittest.TestCase):
    def check(self, sample, tid, status, expected, story_templates, history=None):
        with Copy(sample) as (_, persona):
            set_build(persona, {tid: status}, history)
            out = fresh_backlog(persona)
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
            got = of_story(tasks_of(persona), "S-" + tid, story_templates)
            for template, want in expected.items():
                self.assertEqual(got[template]["status"], want, "%s at %s" % (template, status))
            return got

    def test_scaffolded_changes_nothing_but_links(self):
        got = self.check(CS, "C1", "scaffolded", {"write-skill": "todo", "write-evals": "todo",
                                                  "publish-in-role-plugin-team": "todo"},
                         AUTHORING + PUBLISH)
        for task in got.values():
            self.assertEqual(task["artifact"]["status"], "scaffolded")

    def test_drafted_puts_write_skill_in_progress(self):
        self.check(CS, "C1", "drafted", {"write-skill": "in-progress", "write-evals": "todo",
                                         "publish-in-role-plugin-team": "todo"}, AUTHORING + PUBLISH)

    def test_evals_passing_finishes_the_authoring_tasks(self):
        got = self.check(CS, "C1", "evals-passing", {"write-skill": "done", "write-evals": "done",
                                                     "publish-in-role-plugin-team": "todo"}, AUTHORING + PUBLISH)
        if "trigger-evals" in got:
            self.assertEqual(got["trigger-evals"]["status"], "done")

    def test_packaged_puts_publish_in_progress(self):
        self.check(CS, "C1", "packaged", {"write-skill": "done", "write-evals": "done",
                                          "publish-in-role-plugin-team": "in-progress"}, AUTHORING + PUBLISH)

    def test_deployed_finishes_publish(self):
        self.check(CS, "C1", "deployed", {"write-skill": "done", "publish-in-role-plugin-team": "done"},
                   AUTHORING + PUBLISH)

    def test_verified_changes_nothing_beyond_deployed_and_leaves_the_handover(self):
        got = self.check(CS, "C1", "verified", {"write-skill": "done", "publish-in-role-plugin-team": "done"},
                         AUTHORING + PUBLISH + ("owner-handover",))
        if "owner-handover" in got:
            self.assertEqual(got["owner-handover"]["status"], "todo")
            self.assertNotIn("artifact", got["owner-handover"])

    def test_publish_task_of_the_other_tier(self):
        got = self.check(PE, "T1", "packaged", {"publish-in-role-plugin": "in-progress", "write-skill": "done"},
                         AUTHORING + PUBLISH)
        self.assertEqual(got["publish-in-role-plugin"]["artifact"]["id"], "T1")

    def test_setup_task_follows_packaged_and_deployed(self):
        for status, want in (("drafted", "todo"), ("packaged", "in-progress"), ("deployed", "done")):
            got = self.check(PE, "T3", status, {"setup-managed-agents-self-hosted": want},
                             AUTHORING + SETUP + ("start-wiring",))
            task = got["setup-managed-agents-self-hosted"]
            self.assertEqual(task["artifact"]["id"], "T3")
            self.assertIn("/agents/T3", task["artifact"]["path"])
            self.assertEqual(got["start-wiring"]["artifact"]["id"], "T3")
            self.assertEqual(got["start-wiring"]["status"], "todo")

    def test_other_tasks_carry_no_artifact_key(self):
        with Copy(CS) as (_, persona):
            self.assertEqual(fresh_backlog(persona).returncode, 0)
            linked = AUTHORING + PUBLISH + SETUP + ("start-wiring",)
            for task in tasks_of(persona).values():
                if task["template"] not in linked:
                    self.assertNotIn("artifact", task, task["id"])

    def test_story_and_feature_statuses_follow_the_raised_task(self):
        with Copy(CS) as (_, persona):
            set_build(persona, {"C1": "drafted"})
            self.assertEqual(fresh_backlog(persona).returncode, 0)
            backlog = load(persona / "backlog.json")
            stories = dict((s["id"], s) for f in backlog["epic"]["features"] for s in f["stories"])
            self.assertEqual(stories["S-C1"]["status"], "in-progress")
            self.assertEqual(backlog["epic"]["status"], "in-progress")


class RaiseNeverLowerTests(unittest.TestCase):
    def test_a_done_task_stays_done_when_build_says_drafted(self):
        with Copy(CS) as (_, persona):
            set_build(persona, {"C1": "scaffolded"})
            self.assertEqual(fresh_backlog(persona).returncode, 0)
            data = load(persona / "backlog.json")
            for feature in data["epic"]["features"]:
                for story in feature["stories"]:
                    for task in story["tasks"]:
                        if task["id"] in ("S-C1.write-skill", "S-C1.publish-in-role-plugin-team"):
                            task["status"] = "done"
                        if task["id"] == "S-C1.write-evals":
                            task["status"] = "in-progress"
            dump(persona / "backlog.json", data)
            set_build(persona, {"C1": "drafted"})
            self.assertEqual(cli("backlog", persona).returncode, 0)
            tasks = tasks_of(persona)
            self.assertEqual(tasks["S-C1.write-skill"]["status"], "done")
            self.assertEqual(tasks["S-C1.publish-in-role-plugin-team"]["status"], "done")
            self.assertEqual(tasks["S-C1.write-evals"]["status"], "in-progress")

    def test_a_raise_is_kept_when_build_goes_quiet_again(self):
        with Copy(CS) as (_, persona):
            self.assertEqual(cli("backlog", persona).returncode, 0)
            self.assertEqual(tasks_of(persona)["S-C1.write-skill"]["status"], "in-progress")
            set_build(persona, {"C1": "scaffolded"})
            self.assertEqual(cli("backlog", persona).returncode, 0)
            self.assertEqual(tasks_of(persona)["S-C1.write-skill"]["status"], "in-progress")


class ArtifactKeyTests(unittest.TestCase):
    def test_key_shape_and_backlog_md_line(self):
        with Copy(CS) as (customer, persona):
            self.assertEqual(fresh_backlog(persona).returncode, 0)
            task = tasks_of(persona)["S-C1.write-skill"]
            self.assertEqual(list(task["artifact"]), ["id", "path", "status"])
            self.assertEqual(task["artifact"]["id"], "C1")
            self.assertEqual(task["artifact"]["status"], "drafted")
            self.assertEqual(
                task["artifact"]["path"],
                "engagements/%s/personas/%s/build/plugin/twin-customer-success-manager/skills/"
                "account-brief-before-a-customer-call" % (customer.name, persona.name))
            self.assertTrue((persona / "build" / "plugin" / "twin-customer-success-manager" / "skills" /
                             "account-brief-before-a-customer-call").is_dir())
            md = (persona / "backlog.md").read_text(encoding="utf-8")
            lines = [l for l in md.split("\n") if l.startswith("  - Artifact: C1,")]
            self.assertTrue(lines)
            self.assertIn("drafted", lines[0])
            self.assertIn(task["artifact"]["path"], lines[0])
            # the line sits under its task, after its Done when line
            at = md.index("**S-C1.write-skill**")
            self.assertLess(at, md.index("  - Artifact: C1,", at))
            self.assertLess(md.index("  - Done when:", at), md.index("  - Artifact: C1,", at))


class StalenessTests(unittest.TestCase):
    def test_source_has_build_sha256_only_with_a_build_json(self):
        with Copy(CS) as (_, persona):
            self.assertEqual(fresh_backlog(persona).returncode, 0)
            want = hashlib.sha256((persona / "build" / "build.json").read_bytes()).hexdigest()
            self.assertEqual(load(persona / "backlog.json")["source"]["build_sha256"], want)
            shutil.rmtree(str(persona / "build"))
            self.assertEqual(fresh_backlog(persona).returncode, 0)
            self.assertNotIn("build_sha256", load(persona / "backlog.json")["source"])

    def test_dashboard_refuses_after_build_json_changes_until_backlog_runs_again(self):
        with Copy(CS) as (_, persona):
            self.assertEqual(cli("all", persona, "--date", DATE).returncode, 0)
            self.assertEqual(cli("dashboard", persona, "--date", DATE).returncode, 0)
            set_build(persona, {"C1": "evals-passing"})
            out = cli("dashboard", persona, "--date", DATE)
            self.assertEqual(out.returncode, 1, out.stdout + out.stderr)
            self.assertIn("backlog.json is out of date", out.stdout)
            self.assertIn("Next: run the backlog command", out.stdout)
            self.assertEqual(cli("backlog", persona).returncode, 0)
            self.assertEqual(cli("dashboard", persona, "--date", DATE).returncode, 0)
            self.assertEqual(tasks_of(persona)["S-C1.write-evals"]["status"], "done")


class NoBuildTests(unittest.TestCase):
    def test_no_build_json_shows_nothing_of_build(self):
        for sample in SAMPLES:
            with Copy(sample) as (_, persona):
                shutil.rmtree(str(persona / "build"))
                self.assertEqual(cli("all", persona, "--date", DATE).returncode, 0)
                text = (persona / "backlog.json").read_text(encoding="utf-8")
                self.assertNotIn('"artifact"', text)
                self.assertNotIn("build_sha256", text)
                self.assertNotIn("  - Artifact:", (persona / "backlog.md").read_text(encoding="utf-8"))
                page = (persona / "dashboard.html").read_text(encoding="utf-8")
                self.assertNotIn('data-section="Build"', page)
                self.assertNotIn('href="#build"', page)

    def test_output_is_the_build_output_less_what_build_adds(self):
        """With every artifact at scaffolded nothing is raised, so a run with no build.json differs from a run
        with one only by the artifact keys, the build_sha256, the Artifact lines and the Build section."""
        for sample in SAMPLES:
            with Copy(sample) as (_, persona):
                every = dict((a["id"], "scaffolded") for a in load(persona / "build" / "build.json")["artifacts"])
                set_build(persona, every)
                (persona / "backlog.json").unlink()
                self.assertEqual(cli("all", persona, "--date", DATE).returncode, 0)
                with_build = dict((n, (persona / n).read_text(encoding="utf-8")) for n in GENERATED)
                (persona / "backlog.json").unlink()
                shutil.rmtree(str(persona / "build"))
                self.assertEqual(cli("all", persona, "--date", DATE).returncode, 0)
                bare = dict((n, (persona / n).read_text(encoding="utf-8")) for n in GENERATED)
                self.assertEqual(bare["levelled.json"], with_build["levelled.json"])
                self.assertEqual(bare["backlog.md"], strip_artifacts(with_build["backlog.md"]))
                self.assertNotEqual(bare["backlog.md"], with_build["backlog.md"])
                stripped = strip_backlog_json(json.loads(with_build["backlog.json"]))
                self.assertEqual(bare["backlog.json"], json.dumps(stripped, indent=2, ensure_ascii=False) + "\n")
                self.assertEqual(bare["dashboard.html"], strip_build_section(with_build["dashboard.html"]))
                self.assertNotEqual(bare["dashboard.html"], with_build["dashboard.html"])


class DashboardBuildTests(unittest.TestCase):
    HISTORY = [
        {"status": "evals-passing", "by": "Sam Rivera", "evidence": "build/evidence/C1/benchmark.json",
         "pass_rate": 0.9, "baseline_rate": 0.4, "pass_mark": 90, "approved_by": "Sam Rivera"},
        {"status": "packaged", "by": "package", "evidence": None, "pass_rate": None, "baseline_rate": None,
         "pass_mark": None, "approved_by": None},
    ]

    def page(self, persona):
        self.assertEqual(cli("all", persona, "--date", DATE).returncode, 0)
        return (persona / "dashboard.html").read_text(encoding="utf-8")

    def section(self, page):
        found = re.search(r'<section data-section="Build" id="build">.*?</section>', page, flags=re.S)
        self.assertIsNotNone(found)
        return found.group(0)

    def test_section_follows_the_backlog_and_is_in_the_contents(self):
        with Copy(CS) as (_, persona):
            page = self.page(persona)
            names = re.findall(r'<section data-section="([^"]+)"', page)
            self.assertEqual(names[names.index("Backlog") + 1], "Build")
            self.assertIn('<li><a href="#build">Build</a></li>', page)

    def test_one_row_per_artifact_with_its_columns(self):
        with Copy(CS) as (customer, persona):
            set_build(persona, {"C1": "packaged"}, {"C1": self.HISTORY})
            section = self.section(self.page(persona))
            rows = re.findall(r'<tr data-artifact="([^"]+)">(.*?)</tr>', section, flags=re.S)
            self.assertEqual([r[0] for r in rows], ["C1", "C2", "C3", "C4", "C5"])
            c1 = re.sub(r"<[^>]+>", " ", rows[0][1])
            for text in ("skill", "account-brief-before-a-customer-call", "packaged"):
                self.assertIn(text, c1)
            self.assertIn("engagements/%s/personas/%s/build/plugin/twin-customer-success-manager/skills/"
                          "account-brief-before-a-customer-call" % (customer.name, persona.name), c1)
            self.assertIn("starter-kit/runbooks/identity-devices-publishing.md#6-publish-the-marketplace", c1)
            self.assertIn("package", c1)
            # the last history entry has no rates: shown as not recorded, never as 0
            self.assertNotIn("90%", c1)
            self.assertNotIn('href="starter-kit', section)

    def test_rates_of_the_last_entry_are_shown_as_percent(self):
        with Copy(CS) as (_, persona):
            set_build(persona, {"C1": "evals-passing"}, {"C1": self.HISTORY[:1]})
            row = re.search(r'<tr data-artifact="C1">(.*?)</tr>', self.section(self.page(persona)), flags=re.S)
            text = re.sub(r"<[^>]+>", " ", row.group(1))
            self.assertIn("90%", text)
            self.assertIn("40%", text)

    def test_a_row_without_a_record_says_so(self):
        with Copy(CS) as (_, persona):
            row = re.search(r'<tr data-artifact="C2">(.*?)</tr>', self.section(self.page(persona)), flags=re.S)
            self.assertIn("no record yet", row.group(1))

    def test_count_line_per_status(self):
        with Copy(CS) as (_, persona):
            set_build(persona, {"C2": "evals-passing", "C3": "evals-passing", "C5": "packaged"})
            section = self.section(self.page(persona))
            line = re.search(r'<p data-field="build-counts">(.*?)</p>', section).group(1)
            self.assertEqual(line, "Build status: scaffolded 1, drafted 1, evals-passing 2, packaged 1, "
                                   "deployed 0, verified 0, not-built 0.")

    def test_no_script_and_one_static_page(self):
        for sample in SAMPLES:
            with Copy(sample) as (_, persona):
                page = self.page(persona)
                self.assertNotIn("<script", page.lower())
                self.assertNotIn("http://", self.section(page))
                self.assertNotIn("https://", self.section(page))


class SampleTests(unittest.TestCase):
    def test_committed_samples_match_a_fresh_run(self):
        for sample in SAMPLES:
            with Copy(sample) as (_, persona):
                self.assertEqual(cli("all", persona, "--date", DATE).returncode, 0)
                committed = sample[0] / "personas" / sample[1]
                for name in GENERATED:
                    self.assertEqual((persona / name).read_bytes(), (committed / name).read_bytes(), name)

    def test_only_team_c1_write_skill_is_in_progress(self):
        for sample in SAMPLES:
            tasks = tasks_of(sample[0] / "personas" / sample[1])
            moved = dict((tid, t["status"]) for tid, t in tasks.items() if t["status"] != "todo")
            want = {"S-C1.write-skill": "in-progress"} if sample is CS else {}
            self.assertEqual(moved, want, sample[1])

    def test_sample_tasks_link_their_artifacts(self):
        for sample in SAMPLES:
            persona = sample[0] / "personas" / sample[1]
            tasks = tasks_of(persona)
            build = load(persona / "build" / "build.json")
            status = dict((a["id"], a["status"]) for a in build["artifacts"])
            linked = [t for t in tasks.values() if "artifact" in t]
            self.assertTrue(linked)
            for task in linked:
                self.assertEqual(task["artifact"]["status"], status[task["artifact"]["id"]])
                self.assertTrue((ROOT / task["artifact"]["path"]).exists(), task["artifact"]["path"])


class DocsTests(unittest.TestCase):
    def test_design_names_build_sha256_the_artifact_key_and_the_build_section(self):
        text = DESIGN.read_text(encoding="utf-8")
        self.assertIn("build_sha256", text)
        self.assertIn("`artifact`", text)
        self.assertRegex(text, r"(?s)## 9\. Dashboard.*Build section")

    def test_readmes_give_the_order(self):
        for path in (ROOT / "partner-kit" / "README.md", PLUGIN_DIR / "README.md"):
            text = path.read_text(encoding="utf-8")
            self.assertRegex(text, r"(?is)all,? build,? then (the )?backlog and dashboard", str(path))


if __name__ == "__main__":
    unittest.main()
