"""Tests for the build command: it scaffolds each task's skill and runtime wrapper from levelled.json.

The design of record is partner-kit/docs/design.md, section 8a. The kinds are data
(partner-kit/plugins/twin-consultant/data/build-kinds.json); build never re-decides a runtime, it
records levelled.json's value with its rule and cite. Each test works on a temporary copy of a
fictional sample engagement, so nothing is written under engagements/.

Standard library only. Run with: python3 -m unittest tests.test_twincard_build
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

ROOT = Path(__file__).resolve().parent.parent
PLUGIN_DIR = ROOT / "partner-kit" / "plugins" / "twin-consultant"
SCRIPTS_DIR = PLUGIN_DIR / "scripts"
CLI = SCRIPTS_DIR / "twincard" / "cli.py"
KINDS = PLUGIN_DIR / "data" / "build-kinds.json"
RULES = PLUGIN_DIR / "data" / "rules.json"
FIELDS = PLUGIN_DIR / "data" / "fields.json"
DESIGN = ROOT / "partner-kit" / "docs" / "design.md"
TEMPLATES = PLUGIN_DIR / "templates" / "build"
STARTER = ROOT / "starter-kit" / "templates"
PE = ROOT / "engagements" / "sample-pe" / "personas" / "deal-team-associate"
CS = ROOT / "engagements" / "sample-team-cs" / "personas" / "customer-success-manager"
SAMPLES = (PE, CS)

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from twincard import level as tc_level  # noqa: E402
from twincard import validate as tc_validate  # noqa: E402

RUNTIMES = ("client-skill", "claude-code-scheduled-task", "claude-tag-routine", "managed-agents",
            "managed-agents-self-hosted", "agent-sdk", "none")
STATUSES = ("scaffolded", "drafted", "evals-passing", "packaged", "deployed", "verified", "not-built")
SKILL_FILES = ("SKILL.md", "evals/evals.json", "evals/trigger-evals.json", "references/example-reference.md")
# The copies the build reads, and the starter-kit file each must equal byte for byte.
TEMPLATE_SOURCES = {
    "skill/SKILL.md": "skill/your-skill-name/SKILL.md",
    "skill/evals/evals.json": "skill/your-skill-name/evals/evals.json",
    "skill/evals/trigger-evals.json": "skill/your-skill-name/evals/trigger-evals.json",
    "skill/references/example-reference.md": "skill/your-skill-name/references/example-reference.md",
    "role-plugin/.claude-plugin/plugin.json": "role-plugin/twin-your-role/.claude-plugin/plugin.json",
}
# Hosts a build file may link to: the docs and vendor-docs hosts the runbooks already cite.
ALLOWED_HOSTS = {
    "platform.claude.com", "code.claude.com", "claude.com", "support.claude.com", "docs.claude.com",
    "github.com", "learn.microsoft.com", "support.microsoft.com", "developer.salesforce.com",
    "help.salesforce.com", "knowledge.hubspot.com", "developers.hubspot.com", "support.zendesk.com",
    "developer.zendesk.com", "docs.slack.dev", "slack.com", "support.google.com", "developers.google.com",
    "help.okta.com",
}
SECRET_PATTERNS = (
    ("an Anthropic key", re.compile(r"sk-ant-")),
    ("a Slack token", re.compile(r"xox")),
    ("a Salesforce org id", re.compile(r"(?i)\borg(?:[ _-]?id)?\W{1,3}(?=[A-Za-z0-9]*\d)[A-Za-z0-9]{15}(?:[A-Za-z0-9]{3})?\b")),
    ("a Salesforce org id", re.compile(r"\b00D[A-Za-z0-9]{12}(?:[A-Za-z0-9]{3})?\b")),
)
URL = re.compile(r"https://([A-Za-z0-9.-]+)")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def run_cli(*args):
    return subprocess.run([sys.executable, str(CLI)] + [str(a) for a in args],
                          capture_output=True, text=True, encoding="utf-8")


def task_of(card, tid):
    return next(t for t in card["tasks"] if t["id"] == tid)


def runtime_overrides(*pairs):
    return [{"task": tid, "decision": "runtime", "value": value, "reason": "Invented reason for a test.",
             "approved_by": "Test approver"} for tid, value in pairs]


def snapshot(folder):
    folder = Path(folder)
    return {str(p.relative_to(folder)): p.read_bytes() for p in sorted(folder.rglob("*")) if p.is_file()}


def secret_findings(text):
    found = [name for name, pattern in SECRET_PATTERNS if pattern.search(text)]
    found += ["a link to %s" % host for host in URL.findall(text) if host.lower() not in ALLOWED_HOSTS]
    return found


class Copy(object):
    """A temporary copy of a sample engagement without its build/ folder; change(card) edits the card,
    then levelled.json is written again unless relevel is False."""

    def __init__(self, persona_dir, change=None, relevel=True):
        self.persona_dir, self.change, self.relevel = Path(persona_dir), change, relevel

    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        engagement = self.persona_dir.parent.parent
        root = Path(self.tmp.name) / engagement.name
        shutil.copytree(str(engagement), str(root))
        persona = root / self.persona_dir.relative_to(engagement)
        if (persona / "build").exists():
            shutil.rmtree(str(persona / "build"))
        if self.change:
            card = load(persona / "card.json")
            self.change(card)
            (persona / "card.json").write_text(json.dumps(card, indent=2, ensure_ascii=False) + "\n",
                                               encoding="utf-8")
            if self.relevel:
                tc_level.write_levelled(str(persona))
        return persona

    def __exit__(self, *exc):
        self.tmp.cleanup()


def build(persona, *extra):
    return run_cli("build", persona, *extra)


def manifest(persona):
    return load(Path(persona) / "build" / "build.json")


def artifact(data, tid):
    return next(a for a in data["artifacts"] if a["id"] == tid)


def local(persona, repo_path):
    """The file a manifest path names, inside a temporary copy."""
    marker = "/personas/%s/" % Path(persona).name
    return Path(persona) / repo_path.split(marker, 1)[1]


def all_kinds(card):
    card["overrides"] = runtime_overrides(("C3", "claude-code-scheduled-task"), ("C4", "managed-agents"),
                                          ("C5", "agent-sdk"))


def pe_t4_none(card):
    card["overrides"] = runtime_overrides(("T4", "none"))


# --- Kinds are data ------------------------------------------------------------------------------------

def design_runtimes():
    for line in DESIGN.read_text(encoding="utf-8").splitlines():
        if line.startswith("| `runtime` |"):
            return set(re.findall(r"`([a-z-]+)`", line.split("|")[2]))
    raise AssertionError("design 7.2 has no runtime row")


def runbook_labels(path):
    """The bold labels of a runbook's 'Inputs you need' list, as written."""
    text, labels, inside = (ROOT / path).read_text(encoding="utf-8"), [], False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = line.strip() == "## Inputs you need"
            continue
        match = re.match(r"^- \*\*([^*]+)\*\*", line)
        if inside and match:
            labels.append(match.group(1))
    return labels


class KindTests(unittest.TestCase):
    def setUp(self):
        self.kinds = load(KINDS)
        self.by_runtime = dict((k["runtime"], k) for k in self.kinds["kinds"])

    def test_every_runtime_has_a_kind(self):
        values = set(RUNTIMES) | design_runtimes()
        values |= set(load(FIELDS)["override_values"]["runtime"]["values"])
        values |= {r["then"] for r in load(RULES)["rules"] if r["decides"] == "runtime" and isinstance(r["then"], str)}
        for value in sorted(values):
            with self.subTest(runtime=value):
                self.assertIn(value, self.by_runtime)
        self.assertEqual(len(self.kinds["kinds"]), len(self.by_runtime), "a runtime is listed twice")

    def test_kinds_and_wrappers(self):
        expected = {"client-skill": ("skill", "plugin", None),
                    "claude-code-scheduled-task": ("scheduled-task", "plugin", "scheduled"),
                    "claude-tag-routine": ("tag-routine", "plugin", "routine"),
                    "managed-agents": ("agent-bundle", "skills", "agent"),
                    "managed-agents-self-hosted": ("agent-bundle", "skills", "agent"),
                    "agent-sdk": ("sdk-runner", "skills", "sdk"),
                    "none": ("none", None, None)}
        for runtime, (kind, location, wrapper) in expected.items():
            entry = self.by_runtime[runtime]
            with self.subTest(runtime=runtime):
                self.assertEqual((entry["kind"], entry["skill_location"], entry["wrapper"]), (kind, location, wrapper))

    def test_runbook_links_resolve(self):
        for entry in self.kinds["kinds"]:
            with self.subTest(runtime=entry["runtime"]):
                if entry["runtime"] == "none":
                    self.assertIsNone(entry["runbook"])
                    self.assertTrue(entry["reason"])
                    self.assertEqual(entry["scaffolds"], [])
                    continue
                path, _, anchor = entry["runbook"].partition("#")
                self.assertTrue(path.startswith("starter-kit/runbooks/"), entry["runbook"])
                self.assertTrue(anchor, entry["runbook"])
                text = (ROOT / path).read_text(encoding="utf-8")
                slugs = {tc_validate.github_slug(line.lstrip("#").strip())
                         for line in text.splitlines() if line.startswith("#")}
                self.assertIn(anchor, slugs, entry["runbook"])
                self.assertTrue(entry["scaffolds"])

    def test_location_basis_quotes_the_runbook(self):
        for entry in self.kinds["kinds"]:
            basis = entry.get("skill_location_basis")
            if not basis or not basis.get("quote"):
                continue
            with self.subTest(runtime=entry["runtime"]):
                text = (ROOT / basis["link"].partition("#")[0]).read_text(encoding="utf-8")
                self.assertIn(basis["quote"], text)
        tag = self.by_runtime["claude-tag-routine"]["skill_location_basis"]
        self.assertIn("the plugin that carries it", tag["quote"])

    def test_input_labels_match_the_runbooks(self):
        for entry in self.kinds["kinds"]:
            if entry["wrapper"] not in ("routine", "scheduled", "sdk"):
                continue
            with self.subTest(runtime=entry["runtime"]):
                self.assertEqual(entry["inputs"], runbook_labels(entry["runbook"].partition("#")[0]))


class TemplateCopyTests(unittest.TestCase):
    def test_copies_equal_their_sources(self):
        for copy, source in TEMPLATE_SOURCES.items():
            with self.subTest(copy=copy):
                self.assertEqual((TEMPLATES / copy).read_bytes(), (STARTER / source).read_bytes())

    def test_no_other_template_files(self):
        found = {str(p.relative_to(TEMPLATES)) for p in TEMPLATES.rglob("*") if p.is_file()}
        self.assertEqual(found, set(TEMPLATE_SOURCES))


# --- Skill names -----------------------------------------------------------------------------------------

def skill_name_errors(change):
    with Copy(CS, change, relevel=False) as persona:
        result = tc_validate.validate(str(persona))
        out = run_cli("validate", persona)
    return [e for e in result["errors"] if e["path"].endswith(".skill_name")], out


class SkillNameTests(unittest.TestCase):
    def check_refused(self, value, other=None):
        def change(card):
            task_of(card, "C1")["skill_name"] = value
            if other:
                task_of(card, "C3")["skill_name"] = other
        errors, out = skill_name_errors(change)
        self.assertTrue(errors, value)
        self.assertEqual(out.returncode, 1)
        lines = [line for line in out.stdout.splitlines() if ".skill_name" in line]
        self.assertTrue(lines)
        for line in lines:
            self.assertRegex(line, r"^card:tasks\.C[13]\.skill_name: .*task C[13].*\. Next: .+")
        return errors

    def test_too_long(self):
        self.check_refused("a" * 65)

    def test_bad_characters(self):
        self.check_refused("Account_Brief")
        self.check_refused("account brief")

    def test_reserved_words(self):
        self.check_refused("claude-account-brief")
        self.check_refused("brief-by-anthropic")

    def test_duplicate(self):
        errors = self.check_refused("account-brief", other="account-brief")
        self.assertEqual([e["path"] for e in errors], ["tasks.C3.skill_name"])

    def test_good_name_and_empty_pass(self):
        def change(card):
            task_of(card, "C1")["skill_name"] = "a" * 64
            task_of(card, "C3")["skill_name"] = ""
        errors, out = skill_name_errors(change)
        self.assertEqual(errors, [])
        self.assertEqual(out.returncode, 0, out.stdout)

    def test_catalogue_entry(self):
        entry = next(e for e in load(FIELDS)["fields"] if e["path"] == "tasks[].skill_name")
        self.assertEqual((entry["record"], entry["part"], entry["feeds"], entry["asked_by"], entry["required"]),
                         ("card", "A2", ["build"], [], False))
        template = load(PLUGIN_DIR / "templates" / "card.json")
        self.assertEqual(template["tasks"][0]["skill_name"], "")


class DerivationTests(unittest.TestCase):
    def test_derived_with_collision(self):
        from twincard import build as tc_build
        tasks = [{"id": "T1", "name": "Weekly Summary!"},
                 {"id": "T2", "name": "weekly summary"},
                 {"id": "T3", "name": "Anything", "skill_name": "weekly-summary-3"},
                 {"id": "T4", "name": "Weekly summary"},
                 {"id": "T5", "name": "Ask Claude: " + "x" * 80}]
        names = tc_build.derive_skill_names(tasks)
        self.assertEqual(names["T1"], ("weekly-summary", True))
        self.assertEqual(names["T2"], ("weekly-summary-2", True))
        self.assertEqual(names["T3"], ("weekly-summary-3", False))
        self.assertEqual(names["T4"], ("weekly-summary-4", True))
        name, derived = names["T5"]
        self.assertTrue(derived)
        self.assertLessEqual(len(name), 64)
        self.assertNotIn("claude", name)
        self.assertRegex(name, r"^[a-z0-9]+(-[a-z0-9]+)*$")

    def test_derived_names_in_the_manifest(self):
        data = manifest(PE)
        self.assertEqual((artifact(data, "T1")["skill_name"], artifact(data, "T1")["skill_name_derived"]),
                         ("preparing-company-briefs", False))
        self.assertEqual((artifact(data, "T2")["skill_name"], artifact(data, "T2")["skill_name_derived"]),
                         ("drafting-crm-updates", False))
        self.assertIs(artifact(data, "T3")["skill_name_derived"], True)
        self.assertIs(artifact(manifest(CS), "C1")["skill_name_derived"], True)


# --- Scaffold ---------------------------------------------------------------------------------------------

def skill_dir(persona, data, item):
    return local(persona, next(f["path"] for f in item["files"] if f["path"].endswith("/SKILL.md"))).parent


class KindCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cs = Copy(CS, all_kinds)
        cls.cs_dir = cls.cs.__enter__()
        cls.cs_out = build(cls.cs_dir, "--all-tasks")
        cls.pe = Copy(PE, pe_t4_none)
        cls.pe_dir = cls.pe.__enter__()
        cls.pe_out = build(cls.pe_dir, "--all-tasks")

    @classmethod
    def tearDownClass(cls):
        cls.cs.__exit__()
        cls.pe.__exit__()

    def test_exit_ok(self):
        self.assertEqual(self.cs_out.returncode, 0, self.cs_out.stdout + self.cs_out.stderr)
        self.assertEqual(self.pe_out.returncode, 0, self.pe_out.stdout + self.pe_out.stderr)

    def test_every_kind(self):
        kinds = {a["runtime"]["value"]: a["kind"] for p in (self.cs_dir, self.pe_dir) for a in manifest(p)["artifacts"]}
        self.assertEqual(set(kinds), set(RUNTIMES))

    def test_runtime_recorded_from_levelled(self):
        for persona in (self.cs_dir, self.pe_dir):
            levelled = load(persona / "levelled.json")
            for item in manifest(persona)["artifacts"]:
                decision = levelled["tasks"][item["id"]]["runtime"]
                with self.subTest(task=item["id"]):
                    self.assertEqual(item["runtime"]["value"], decision["value"])
                    self.assertEqual(item["runtime"]["rule"], decision["rule"])
                    self.assertEqual(item["runtime"]["cite"], decision["cite"])

    def test_skill_location(self):
        for persona in (self.cs_dir, self.pe_dir):
            data = manifest(persona)
            plugin = load(persona / "levelled.json")["persona_plan"]["plugin_name"]["value"]
            for item in data["artifacts"]:
                if item["kind"] == "none":
                    continue
                folder = skill_dir(persona, data, item)
                with self.subTest(task=item["id"], kind=item["kind"]):
                    if item["kind"] in ("skill", "scheduled-task", "tag-routine"):
                        self.assertEqual(folder, persona / "build" / "plugin" / plugin / "skills" / item["skill_name"])
                    else:
                        self.assertEqual(folder, persona / "build" / "skills" / item["skill_name"])
                    for name in SKILL_FILES:
                        self.assertTrue((folder / name).is_file(), name)

    def test_plugin_manifest(self):
        plugin = self.cs_dir / "build" / "plugin" / "twin-customer-success-manager"
        data = load(plugin / ".claude-plugin" / "plugin.json")
        template = load(TEMPLATES / "role-plugin" / ".claude-plugin" / "plugin.json")
        self.assertEqual(list(data), list(template))
        self.assertEqual(data["name"], "twin-customer-success-manager")
        self.assertTrue((plugin / "README.md").is_file())

    def test_agent_bundles(self):
        for persona, tid in ((self.cs_dir, "C4"), (self.pe_dir, "T3")):
            folder = persona / "build" / "agents" / tid
            agent, env = load(folder / "agent.json"), load(folder / "environment.json")
            name = artifact(manifest(persona), tid)["skill_name"]
            with self.subTest(task=tid):
                self.assertEqual(agent["model"], "FILL IN")
                self.assertIn("FILL IN", agent["system"])
                self.assertIn(name, json.dumps(agent["skills"]))
                self.assertEqual(env["config"]["networking"]["type"], "limited")
                self.assertEqual(env["config"]["networking"]["allowed_hosts"], [])

    def test_fill_in_sheets(self):
        kinds = dict((k["runtime"], k) for k in load(KINDS)["kinds"])
        for path, runtime in (("routines/C2/routine.md", "claude-tag-routine"),
                              ("scheduled/C3/task.md", "claude-code-scheduled-task"),
                              ("sdk/C5/README.md", "agent-sdk")):
            text = (self.cs_dir / "build" / path).read_text(encoding="utf-8")
            with self.subTest(path=path):
                for label in kinds[runtime]["inputs"]:
                    self.assertIn("**%s**" % label, text)
                self.assertIn("FILL IN", text)
                self.assertIn(kinds[runtime]["runbook"], text)
        sdk = (self.cs_dir / "build" / "sdk" / "C5" / "README.md").read_text(encoding="utf-8")
        self.assertIn("$ANTHROPIC_API_KEY", sdk)

    def test_none_is_not_built(self):
        item = artifact(manifest(self.pe_dir), "T4")
        self.assertEqual((item["kind"], item["status"], item["files"]), ("none", "not-built", []))
        self.assertTrue(item["reason"])
        self.assertFalse((self.pe_dir / "build" / "skills" / item["skill_name"]).exists())

    def test_manifest_shape(self):
        data = manifest(self.cs_dir)
        self.assertEqual(data["build_version"], 1)
        levelled = tc_level.render(load(self.cs_dir / "levelled.json")).encode("utf-8")
        self.assertEqual(data["source"]["levelled_sha256"], sha(levelled))
        self.assertNotIn("generated", json.dumps(data))
        self.assertEqual(manifest(CS)["source"]["levelled_sha256"],
                         load(CS / "backlog.json")["source"]["levelled_sha256"])
        for item in data["artifacts"]:
            self.assertIn(item["status"], STATUSES)
            for entry in item["files"]:
                self.assertTrue(entry["path"].startswith("engagements/sample-team-cs/personas/customer-success-manager/build/"))
                self.assertEqual(entry["sha256"], sha(local(self.cs_dir, entry["path"]).read_bytes()))


class SeedingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.copy = Copy(CS)
        cls.persona = cls.copy.__enter__()
        build(cls.persona, "--all-tasks")
        cls.data = manifest(cls.persona)

    @classmethod
    def tearDownClass(cls):
        cls.copy.__exit__()

    def folder(self, tid):
        return skill_dir(self.persona, self.data, artifact(self.data, tid))

    def test_skill_md(self):
        item = artifact(self.data, "C4")
        text = (self.folder("C4") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: %s\n" % item["skill_name"], text)
        self.assertRegex(text, r"(?m)^Start from draft-response .*")
        self.assertIn("tasks.C4.story_want", text)
        self.assertIn("draft the follow-up email and the call note for HubSpot", text)
        rows = [line for line in text.splitlines() if line.startswith("|") and "hubspot" in line]
        self.assertTrue(any("create" in row and "blocked" in row and "confidential" in row for row in rows), rows)
        self.assertIn("FILL IN", text)
        self.assertIn("examples.good", text)

    def test_evals(self):
        data = load(self.folder("C4") / "evals" / "evals.json")
        self.assertEqual(data["skill_name"], artifact(self.data, "C4")["skill_name"])
        self.assertGreaterEqual(len(data["evals"]), 3)
        self.assertEqual(len(data["evals"]), 2 + 2)  # two good examples, then the template's two edge cases
        self.assertEqual([case["id"] for case in data["evals"]], list(range(1, len(data["evals"]) + 1)))
        for case in data["evals"]:
            self.assertIn("FILL IN", case["prompt"])
            self.assertIn("FILL IN", case["expected_output"])
        self.assertNotIn("model", json.dumps(data))

    def test_at_least_three_cases_without_examples(self):
        with Copy(PE) as persona:
            build(persona)
            data = manifest(persona)
            evals = load(skill_dir(persona, data, artifact(data, "T1")) / "evals" / "evals.json")
        self.assertEqual(len(evals["evals"]), 3)

    def test_trigger_evals(self):
        data = load(self.folder("C4") / "evals" / "trigger-evals.json")
        true = [e for e in data if e["should_trigger"] is True]
        false = [e for e in data if e["should_trigger"] is False]
        self.assertGreaterEqual(len(true), 1)
        self.assertEqual(len(false), 2)
        for entry in true:
            self.assertIn("tasks.C4.trigger", entry["query"])
        for entry in data:
            self.assertIn("FILL IN", entry["query"])


# --- Never overwrite, statuses and refusals ----------------------------------------------------------------

class RerunTests(unittest.TestCase):
    def test_second_run_is_byte_identical(self):
        with Copy(CS) as persona:
            self.assertEqual(build(persona).returncode, 0)
            first = snapshot(persona / "build")
            self.assertEqual(build(persona).returncode, 0)
            self.assertEqual(snapshot(persona / "build"), first)

    def test_pilot_only_by_default(self):
        with Copy(PE) as persona:
            out = build(persona)
            self.assertEqual(out.returncode, 0, out.stderr)
            self.assertEqual([a["id"] for a in manifest(persona)["artifacts"]], ["T1", "T2"])
            build(persona, "--all-tasks")
            self.assertEqual([a["id"] for a in manifest(persona)["artifacts"]], ["T1", "T2", "T3", "T4", "T5", "T6"])

    def test_edited_file_is_kept(self):
        with Copy(CS) as persona:
            build(persona)
            data = manifest(persona)
            entry = next(f for f in artifact(data, "C1")["files"] if f["path"].endswith("/SKILL.md"))
            path = local(persona, entry["path"])
            path.write_text("edited by a person\n", encoding="utf-8")
            missing = next(f for f in artifact(data, "C4")["files"] if f["path"].endswith("trigger-evals.json"))
            local(persona, missing["path"]).unlink()
            out = build(persona)
            self.assertEqual(out.returncode, 0)
            self.assertEqual(path.read_text(encoding="utf-8"), "edited by a person\n")
            self.assertRegex(out.stderr, r"kept: .*%s" % re.escape(entry["path"]))
            self.assertTrue(local(persona, missing["path"]).is_file())
            again = next(f for f in artifact(manifest(persona), "C1")["files"] if f["path"] == entry["path"])
            self.assertEqual(again["sha256"], entry["sha256"])

    def test_drafted_when_no_fill_in_remains(self):
        with Copy(CS) as persona:
            build(persona)
            item = artifact(manifest(persona), "C1")
            self.assertEqual(item["status"], "scaffolded")
            for entry in item["files"]:
                path = local(persona, entry["path"])
                path.write_text(path.read_text(encoding="utf-8").replace("FILL IN", "Done"), encoding="utf-8")
            out = build(persona)
            self.assertEqual(out.returncode, 0)
            self.assertEqual(artifact(manifest(persona), "C1")["status"], "drafted")

    def test_recorded_higher_status_is_kept(self):
        with Copy(CS) as persona:
            build(persona)
            data = manifest(persona)
            artifact(data, "C1")["status"] = "deployed"
            (persona / "build" / "build.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            self.assertEqual(build(persona).returncode, 0)
            self.assertEqual(artifact(manifest(persona), "C1")["status"], "deployed")
            self.assertEqual(artifact(manifest(persona), "C4")["status"], "scaffolded")

    def test_unknown_status_is_exit_2(self):
        with Copy(CS) as persona:
            build(persona)
            data = manifest(persona)
            artifact(data, "C1")["status"] = "shipped"
            (persona / "build" / "build.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            out = build(persona)
            self.assertEqual(out.returncode, 2)
            self.assertRegex(out.stderr.strip(), r"build\.json.*Next: .+")
            self.assertEqual(len(out.stderr.strip().splitlines()), 1)

    def test_build_json_not_json_is_exit_2(self):
        with Copy(CS) as persona:
            (persona / "build").mkdir()
            (persona / "build" / "build.json").write_text("{not json", encoding="utf-8")
            out = build(persona)
            self.assertEqual(out.returncode, 2)
            self.assertIn("Next:", out.stderr)


class RefusalTests(unittest.TestCase):
    def check_nothing_written(self, persona, out):
        self.assertEqual(out.returncode, 1, out.stdout + out.stderr)
        self.assertIn("Next:", out.stdout + out.stderr)
        self.assertFalse((persona / "build").exists())

    def test_stale_levelled(self):
        def change(card):
            task_of(card, "C1")["name"] = "Account brief before every customer call"
        with Copy(CS, change, relevel=False) as persona:
            self.check_nothing_written(persona, build(persona))

    def test_missing_levelled(self):
        with Copy(CS) as persona:
            (persona / "levelled.json").unlink()
            self.check_nothing_written(persona, build(persona))

    def test_blocker(self):
        def change(card):
            card["overrides"] = [{"task": "C1", "decision": "plan_fit", "value": "ok",
                                  "reason": "Invented reason for a test.", "approved_by": "Test approver"}]
        with Copy(CS, change) as persona:
            self.assertTrue(load(persona / "levelled.json")["blockers"])
            self.check_nothing_written(persona, build(persona))

    def test_usage_errors_are_exit_2(self):
        out = run_cli("build", ROOT / "engagements" / "no-such-customer" / "personas" / "nobody")
        self.assertEqual(out.returncode, 2)
        self.assertIn("Next:", out.stderr)
        out = run_cli("build", PE, "--no-such-flag")
        self.assertEqual(out.returncode, 2)

    def test_all_keeps_four_steps(self):
        with Copy(CS) as persona:
            out = run_cli("all", persona, "--date", "2026-11-15")
            self.assertEqual(out.returncode, 0, out.stdout)
            self.assertFalse((persona / "build").exists())


# --- The committed samples ---------------------------------------------------------------------------------

DRAFTED = {(CS, "C1"): "plugin/twin-customer-success-manager/skills/account-brief-before-a-customer-call/"}


class SampleTests(unittest.TestCase):
    def test_samples_match_a_fresh_run(self):
        """A fresh build gives the committed bytes, except the Team sample's C1, which a person drafted
        (OPS-75): its four skill files and its status. build.json still records the scaffold's hashes."""
        for sample in SAMPLES:
            with self.subTest(sample=sample.name), Copy(sample) as persona:
                out = build(persona, "--all-tasks")
                self.assertEqual(out.returncode, 0, out.stderr)
                fresh, committed = snapshot(persona / "build"), snapshot(sample / "build")
                self.assertEqual(sorted(fresh), sorted(committed))
                drafted = [folder for (where, _), folder in DRAFTED.items() if where == sample]
                for name in fresh:
                    if name == "build.json" or any(name.startswith(folder) for folder in drafted):
                        continue
                    self.assertEqual(fresh[name], committed[name], name)
                data = json.loads(fresh["build.json"].decode("utf-8"))
                for item in data["artifacts"]:
                    if (sample, item["id"]) in DRAFTED:
                        self.assertEqual(item["status"], "scaffolded")
                        item["status"] = "drafted"
                self.assertEqual(data, json.loads(committed["build.json"].decode("utf-8")))

    def test_a_rerun_over_the_committed_build_changes_nothing(self):
        for sample in SAMPLES:
            with self.subTest(sample=sample.name), tempfile.TemporaryDirectory() as tmp:
                engagement = sample.parent.parent
                shutil.copytree(str(engagement), str(Path(tmp) / engagement.name))
                persona = Path(tmp) / engagement.name / sample.relative_to(engagement)
                out = build(persona, "--all-tasks")
                self.assertEqual(out.returncode, 0, out.stderr)
                self.assertEqual(snapshot(persona / "build"), snapshot(sample / "build"))

    def test_every_artifact_is_honestly_scaffolded(self):
        """Nothing is above drafted; only the Team sample's C1 is drafted, with no FILL IN and no history."""
        for sample in SAMPLES:
            for item in manifest(sample)["artifacts"]:
                with self.subTest(sample=sample.name, task=item["id"]):
                    self.assertEqual(item["history"], [])
                    if (sample, item["id"]) not in DRAFTED:
                        self.assertIn(item["status"], ("scaffolded", "not-built"))
                        continue
                    self.assertEqual(item["status"], "drafted")
                    for entry in item["files"]:
                        path = ROOT / entry["path"]
                        self.assertNotIn("FILL IN", path.read_text(encoding="utf-8"), entry["path"])

    def test_no_secrets_in_the_build_folders(self):
        for sample in SAMPLES:
            files = [p for p in sorted((sample / "build").rglob("*")) if p.is_file()]
            self.assertTrue(files)
            for path in files:
                with self.subTest(path=str(path.relative_to(ROOT))):
                    self.assertEqual(secret_findings(path.read_text(encoding="utf-8")), [])

    def test_the_scan_finds_planted_secrets(self):
        for text in ("key sk-ant-api03-abc", "token xoxb-1-2", "org id: 00D5g000004ABCD",
                     "org 00D5g000004ABCDEAA", "see https://example.my.salesforce.com/x",
                     "https://acme.zendesk.com/mcp"):
            with self.subTest(text=text):
                self.assertTrue(secret_findings(text))
        self.assertEqual(secret_findings("https://platform.claude.com/docs and $ANTHROPIC_API_KEY"), [])

    def test_docs_list_the_command(self):
        design = DESIGN.read_text(encoding="utf-8")
        self.assertIn("## 8a. Build", design)
        self.assertIn("cli.py build", design)
        for path in (PLUGIN_DIR / "README.md", ROOT / "partner-kit" / "README.md"):
            with self.subTest(path=str(path.relative_to(ROOT))):
                self.assertIn("cli.py build", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
