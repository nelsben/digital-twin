"""Tests for the package command and the higher record statuses (OPS-76).

The design of record is partner-kit/docs/design.md, section 8a (Package and deploy). `package` reads every
persona's build/build.json under a customer folder and writes the customer marketplace
(build/marketplace/) and the agent, routine, scheduled and SDK bundles (build/bundles/) from artifacts at
evals-passing or above, records packaged for each, and writes build/deploy.md, an ordered view of the
deployment tasks already in each persona's backlog.json. `--include-drafts` writes build/marketplace-draft/
and build/bundles-draft/ instead, includes drafted artifacts and records nothing. `record` then moves an
artifact from packaged to deployed and from deployed to verified on a note under build/evidence/<id>/.

Neither fictional sample has an artifact at evals-passing, so every test of the packaged path works on a
temporary copy whose build.json statuses the test sets: no result is recorded under engagements/.

Standard library only. Run with: python3 -m unittest tests.test_twincard_package
"""

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from test_twincard_build import SECRET_PATTERNS as BUILD_SECRET_PATTERNS, secret_findings as build_findings  # noqa: E402

ROOT = TESTS_DIR.parent
PLUGIN_DIR = ROOT / "partner-kit" / "plugins" / "twin-consultant"
if str(PLUGIN_DIR / "scripts") not in sys.path:
    sys.path.insert(0, str(PLUGIN_DIR / "scripts"))
from twincard import package as package_mod  # noqa: E402
CLI = PLUGIN_DIR / "scripts" / "twincard" / "cli.py"
DESIGN = ROOT / "partner-kit" / "docs" / "design.md"
SKILL = PLUGIN_DIR / "skills" / "building-twin-artifacts" / "SKILL.md"
PLAYBOOK = ROOT / "docs" / "playbook" / "05-persona-card-workflow.md"
PE_CUSTOMER = ROOT / "engagements" / "sample-pe"
CS_CUSTOMER = ROOT / "engagements" / "sample-team-cs"
CUSTOMERS = (PE_CUSTOMER, CS_CUSTOMER)
CS_PERSONA = "customer-success-manager"
PE_PERSONA = "deal-team-associate"
CS_PLUGIN = "twin-customer-success-manager"
HISTORY_KEYS = ["status", "by", "evidence", "pass_rate", "baseline_rate", "pass_mark", "approved_by"]
SECTIONS = [
    "1. Org settings and data policy",
    "2. Identity and groups",
    "3. Connectors and tool permissions",
    "4. Publish the marketplace",
    "5. Hosted agents, routines and scheduled tasks",
    "6. Governance hook",
    "7. Check it worked and hand over",
]
# OPS-74's patterns, plus passwords and tenant ids (a GUID), which this card adds.
EXTRA_PATTERNS = (
    ("a password", re.compile(r"(?i)\bpass(?:word|wd)\s*[:=]\s*\S+")),
    ("a tenant id", re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")),
)
STEP = re.compile(r"^- \[[ x]\] ")
TASK_IDS = re.compile(r"`(S-[A-Za-z0-9-]+\.[A-Za-z0-9_.\-]+)`")
LINK = re.compile(r"\]\(([^)\s]+)\)")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dump(path, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_cli(*args):
    return subprocess.run([sys.executable, str(CLI)] + [str(a) for a in args],
                          capture_output=True, text=True, encoding="utf-8")


def secret_findings(text):
    return build_findings(text) + [name for name, pattern in EXTRA_PATTERNS if pattern.search(text)]


def snapshot(folder):
    folder = Path(folder)
    if not folder.is_dir():
        return {}
    return {p.relative_to(folder).as_posix(): p.read_bytes() for p in sorted(folder.rglob("*")) if p.is_file()}


def artifact(data, tid):
    return next(a for a in data["artifacts"] if a["id"] == tid)


class Copy(object):
    """A temporary copy of a sample customer folder; yields the copy's path."""

    def __init__(self, customer):
        self.customer = Path(customer)

    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name) / "engagements" / self.customer.name
        shutil.copytree(str(self.customer), str(root))
        return root

    def __exit__(self, *exc):
        self.tmp.cleanup()


def manifest_path(customer, persona):
    return Path(customer) / "personas" / persona / "build" / "build.json"


def set_status(customer, persona, statuses):
    """Set statuses in a temporary copy's build.json (a test stand-in for record's history), and fill in the
    role plugin's own files, which a packaged plugin needs."""
    plugin = Path(customer) / "personas" / persona / "build" / "plugin"
    for meta in plugin.glob("*/.claude-plugin/plugin.json"):
        data = load(meta)
        data["description"] = "Role twin for the test: its skills and output style."
        dump(meta, data)
    for readme in plugin.glob("*/README.md"):
        readme.write_text(readme.read_text(encoding="utf-8").replace("FILL IN", "Filled in"), encoding="utf-8")
    path = manifest_path(customer, persona)
    data = load(path)
    for item in data["artifacts"]:
        if item["id"] in statuses:
            item["status"] = statuses[item["id"]]
    dump(path, data)


def all_cs(status):
    return dict((tid, status) for tid in ("C1", "C2", "C3", "C4", "C5"))


def backlog_tasks(customer, persona):
    backlog = load(Path(customer) / "personas" / persona / "backlog.json")
    tasks = {}
    for feature in backlog["epic"]["features"]:
        for story in feature["stories"]:
            for task in story["tasks"]:
                tasks[task["id"]] = (story, task)
    return tasks


def sections(text):
    """[(heading, [step lines with their continuation lines])] for each '## ' section of deploy.md."""
    out = []
    for line in text.split("\n"):
        if line.startswith("## "):
            out.append((line[3:].strip(), []))
        elif out and STEP.match(line):
            out[-1][1].append(line)
        elif out and out[-1][1] and line.startswith("  ") and line.strip():
            out[-1][1][-1] += "\n" + line
    return out


# --- Package: the marketplace, bundles and statuses ------------------------------------------------------

class MarketplaceTests(unittest.TestCase):
    def test_marketplace_shape_name_and_plugin_copy(self):
        with Copy(CS_CUSTOMER) as customer:
            set_status(customer, CS_PERSONA, all_cs("evals-passing"))
            out = run_cli("package", customer)
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
            market = customer / "build" / "marketplace"
            data = load(market / ".claude-plugin" / "marketplace.json")
            self.assertEqual(list(data), ["name", "description", "owner", "plugins"])
            self.assertEqual(data["name"], "example-software-co-twins")
            self.assertIsInstance(data["owner"]["name"], str)
            self.assertEqual([p["name"] for p in data["plugins"]], [CS_PLUGIN])
            entry = data["plugins"][0]
            self.assertEqual(list(entry), ["name", "source", "description"])
            self.assertEqual(entry["source"], "./plugins/%s" % CS_PLUGIN)
            self.assertFalse(entry["description"].startswith("DRAFT"))
            source = customer / "personas" / CS_PERSONA / "build" / "plugin" / CS_PLUGIN
            self.assertEqual(snapshot(market / "plugins" / CS_PLUGIN), snapshot(source))
            self.assertNotIn("twin-consultant", json.dumps(data))

    def test_name_from_the_profile(self):
        with Copy(CS_CUSTOMER) as customer:
            profile = load(customer / "customer-profile.json")
            profile["marketplace_name"] = "example-software-co-roles"
            dump(customer / "customer-profile.json", profile)
            set_status(customer, CS_PERSONA, all_cs("evals-passing"))
            out = run_cli("package", customer)
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
            data = load(customer / "build" / "marketplace" / ".claude-plugin" / "marketplace.json")
            self.assertEqual(data["name"], "example-software-co-roles")

    def test_bundle_placement(self):
        with Copy(CS_CUSTOMER) as customer:
            set_status(customer, CS_PERSONA, {"C2": "evals-passing"})
            out = run_cli("package", customer)
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
            bundle = customer / "build" / "bundles" / CS_PERSONA / "C2"
            persona_build = customer / "personas" / CS_PERSONA / "build"
            self.assertEqual((bundle / "routine.md").read_bytes(),
                             (persona_build / "routines" / "C2" / "routine.md").read_bytes())
            skill = persona_build / "plugin" / CS_PLUGIN / "skills" / "weekly-renewal-risk-digest"
            self.assertEqual(snapshot(bundle / "weekly-renewal-risk-digest"), snapshot(skill))
        with Copy(PE_CUSTOMER) as customer:
            set_status(customer, PE_PERSONA, {"T3": "evals-passing"})
            out = run_cli("package", customer)
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
            bundle = customer / "build" / "bundles" / PE_PERSONA / "T3"
            for name in ("agent.json", "environment.json"):
                self.assertTrue((bundle / name).is_file(), name)
            self.assertTrue((bundle / "weekly-pipeline-summary-for-the-monday-deal-meeting" / "SKILL.md").is_file())

    def test_packaged_is_recorded_for_each(self):
        with Copy(CS_CUSTOMER) as customer:
            set_status(customer, CS_PERSONA, all_cs("evals-passing"))
            self.assertEqual(run_cli("package", customer).returncode, 0)
            data = load(manifest_path(customer, CS_PERSONA))
            for tid in ("C1", "C2", "C3", "C4", "C5"):
                with self.subTest(task=tid):
                    item = artifact(data, tid)
                    self.assertEqual(item["status"], "packaged")
                    entry = item["history"][-1]
                    self.assertEqual(list(entry), HISTORY_KEYS)
                    self.assertEqual(entry["status"], "packaged")
                    self.assertTrue(entry["evidence"].startswith("engagements/sample-team-cs/build/"), entry)

    def test_one_unevaluated_skill_keeps_the_plugin_out(self):
        with Copy(CS_CUSTOMER) as customer:
            statuses = all_cs("evals-passing")
            statuses["C5"] = "drafted"
            set_status(customer, CS_PERSONA, statuses)
            out = run_cli("package", customer)
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
            self.assertFalse((customer / "build" / "marketplace" / "plugins" / CS_PLUGIN).exists())
            self.assertRegex(out.stderr, r"%s.*C5.*drafted" % CS_PLUGIN)
            data = load(manifest_path(customer, CS_PERSONA))
            for tid in ("C1", "C3", "C4"):
                self.assertEqual(artifact(data, tid)["status"], "evals-passing")
            self.assertEqual(artifact(data, "C2")["status"], "packaged")
            self.assertTrue((customer / "build" / "bundles" / CS_PERSONA / "C2" / "routine.md").is_file())

    def test_a_plugin_still_saying_fill_in_is_not_packaged(self):
        with Copy(CS_CUSTOMER) as customer:
            set_status(customer, CS_PERSONA, all_cs("evals-passing"))
            readme = customer / "personas" / CS_PERSONA / "build" / "plugin" / CS_PLUGIN / "README.md"
            readme.write_text("# FILL IN the role\n", encoding="utf-8")
            out = run_cli("package", customer)
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
            self.assertRegex(out.stderr, r"README.md still say FILL IN")
            self.assertFalse((customer / "build" / "marketplace" / "plugins" / CS_PLUGIN).exists())

    def test_samples_package_nothing_and_say_why(self):
        for sample, persona in ((PE_CUSTOMER, PE_PERSONA), (CS_CUSTOMER, CS_PERSONA)):
            with self.subTest(sample=sample.name), Copy(sample) as customer:
                before = manifest_path(customer, persona).read_bytes()
                out = run_cli("package", customer)
                self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
                self.assertRegex(out.stderr, r"%s: nothing to package" % persona)
                self.assertRegex(out.stderr, r"evals-passing")
                self.assertFalse((customer / "build" / "marketplace").exists())
                self.assertFalse((customer / "build" / "bundles").exists())
                self.assertTrue((customer / "build" / "deploy.md").is_file())
                self.assertEqual(manifest_path(customer, persona).read_bytes(), before)

    def test_reruns_are_byte_identical(self):
        with Copy(CS_CUSTOMER) as customer:
            set_status(customer, CS_PERSONA, all_cs("evals-passing"))
            self.assertEqual(run_cli("package", customer).returncode, 0)
            first = snapshot(customer)
            out = run_cli("package", customer)
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
            self.assertEqual(snapshot(customer), first)
            self.assertEqual(run_cli("package", customer, "--include-drafts").returncode, 0)
            drafts = snapshot(customer)
            self.assertEqual(run_cli("package", customer, "--include-drafts").returncode, 0)
            self.assertEqual(snapshot(customer), drafts)

    def test_the_partner_kit_is_never_packaged(self):
        with Copy(CS_CUSTOMER) as customer:
            data = load(manifest_path(customer, CS_PERSONA))
            data["plugin"]["name"] = "twin-consultant"
            for item in data["artifacts"]:
                item["status"] = "evals-passing"
            dump(manifest_path(customer, CS_PERSONA), data)
            build = customer / "personas" / CS_PERSONA / "build" / "plugin"
            shutil.move(str(build / CS_PLUGIN), str(build / "twin-consultant"))
            out = run_cli("package", customer)
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
            self.assertIn("twin-consultant", out.stderr)
            self.assertFalse((customer / "build" / "marketplace" / "plugins" / "twin-consultant").exists())

    def test_usage_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = run_cli("package", tmp)
            self.assertEqual(out.returncode, 2, out.stdout + out.stderr)
            self.assertIn("Next:", out.stderr)
        out = run_cli("package", ROOT / "no-such-folder")
        self.assertEqual(out.returncode, 2)


class DraftTests(unittest.TestCase):
    def test_include_drafts_writes_the_draft_folders_and_records_nothing(self):
        with Copy(CS_CUSTOMER) as customer:
            set_status(customer, CS_PERSONA, {"C2": "drafted"})
            before = manifest_path(customer, CS_PERSONA).read_bytes()
            out = run_cli("package", customer, "--include-drafts")
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
            self.assertEqual(manifest_path(customer, CS_PERSONA).read_bytes(), before)
            self.assertFalse((customer / "build" / "marketplace").exists())
            self.assertFalse((customer / "build" / "bundles").exists())
            market = customer / "build" / "marketplace-draft"
            data = load(market / ".claude-plugin" / "marketplace.json")
            for entry in data["plugins"]:
                self.assertTrue(entry["description"].startswith("DRAFT, not evaluated:"), entry)
                plugin = load(market / "plugins" / entry["name"] / ".claude-plugin" / "plugin.json")
                self.assertTrue(plugin["description"].startswith("DRAFT, not evaluated:"), plugin)
            skills = market / "plugins" / CS_PLUGIN / "skills"
            self.assertTrue((skills / "account-brief-before-a-customer-call" / "SKILL.md").is_file())
            self.assertFalse((skills / "renewal-quote-email-to-the-customer").exists())
            self.assertTrue((customer / "build" / "bundles-draft" / CS_PERSONA / "C2" / "routine.md").is_file())
            self.assertTrue((customer / "build" / "deploy.md").is_file())

    def test_deploy_md_is_the_same_with_or_without_drafts(self):
        with Copy(CS_CUSTOMER) as customer:
            self.assertEqual(run_cli("package", customer).returncode, 0)
            plain = (customer / "build" / "deploy.md").read_bytes()
            self.assertEqual(run_cli("package", customer, "--include-drafts").returncode, 0)
            self.assertEqual((customer / "build" / "deploy.md").read_bytes(), plain)


# --- record: packaged, deployed, verified ------------------------------------------------------------------

def note(customer, persona, tid, text, name="deployed.md"):
    folder = Path(customer) / "personas" / persona / "build" / "evidence" / tid
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / name
    path.write_text(text, encoding="utf-8")
    return path


def record(customer, persona, tid, status, evidence, by="Test admin"):
    return run_cli("record", Path(customer) / "personas" / persona, tid, "--status", status,
                   "--evidence", evidence, "--by", by)


DEPLOYED_NOTE = ("Published in the Claude org's Plugins & skills to every member, from the example-software-co-twins "
                 "marketplace, plugin version 0.1.0.\n")
VERIFIED_NOTE = "Runbook check-it-worked: a pilot user saw the skill listed and ran it on a test account. Pass.\n"


class RecordTests(unittest.TestCase):
    def packaged_copy(self):
        copy = Copy(CS_CUSTOMER)
        customer = copy.__enter__()
        self.addCleanup(copy.__exit__)
        set_status(customer, CS_PERSONA, all_cs("evals-passing"))
        self.assertEqual(run_cli("package", customer).returncode, 0)
        return customer

    def test_deployed_then_verified(self):
        customer = self.packaged_copy()
        out = record(customer, CS_PERSONA, "C1", "deployed", note(customer, CS_PERSONA, "C1", DEPLOYED_NOTE))
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        out = record(customer, CS_PERSONA, "C1", "verified",
                     note(customer, CS_PERSONA, "C1", VERIFIED_NOTE, "verified.md"), by="Test consultant")
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        item = artifact(load(manifest_path(customer, CS_PERSONA)), "C1")
        self.assertEqual(item["status"], "verified")
        self.assertEqual([h["status"] for h in item["history"]], ["packaged", "deployed", "verified"])
        for entry in item["history"]:
            self.assertEqual(list(entry), HISTORY_KEYS)
        self.assertEqual(item["history"][1]["by"], "Test admin")
        self.assertEqual(item["history"][1]["evidence"],
                         "engagements/sample-team-cs/personas/customer-success-manager/build/evidence/C1/deployed.md")

    def refused(self, customer, tid, status, evidence, pattern):
        before = manifest_path(customer, CS_PERSONA).read_bytes()
        out = record(customer, CS_PERSONA, tid, status, evidence)
        self.assertEqual(out.returncode, 1, out.stdout + out.stderr)
        self.assertRegex(out.stdout, pattern)
        self.assertIn("Next:", out.stdout)
        self.assertEqual(manifest_path(customer, CS_PERSONA).read_bytes(), before)

    def test_packaged_is_set_only_by_package(self):
        with Copy(CS_CUSTOMER) as customer:
            set_status(customer, CS_PERSONA, {"C1": "evals-passing"})
            self.refused(customer, "C1", "packaged", note(customer, CS_PERSONA, "C1", DEPLOYED_NOTE),
                         r"package command")

    def test_refusals(self):
        customer = self.packaged_copy()
        good = note(customer, CS_PERSONA, "C1", DEPLOYED_NOTE)
        self.refused(customer, "C1", "verified", good, r"(?i)one status at a time")
        self.refused(customer, "C1", "deployed", note(customer, CS_PERSONA, "C1", "  \n", "empty.md"),
                     r"(?i)empty")
        self.refused(customer, "C1", "deployed",
                     note(customer, CS_PERSONA, "C1", "Created agent with key sk-ant-api03-abc\n", "secret.md"),
                     r"(?i)secret")
        outside = customer / "deployed.md"
        outside.write_text(DEPLOYED_NOTE, encoding="utf-8")
        self.refused(customer, "C1", "deployed", outside, r"evidence/C1/")
        self.assertEqual(record(customer, CS_PERSONA, "C1", "deployed", good).returncode, 0)
        self.refused(customer, "C1", "deployed", good, r"(?i)already")

    def test_deployed_needs_packaged(self):
        with Copy(CS_CUSTOMER) as customer:
            set_status(customer, CS_PERSONA, {"C1": "evals-passing"})
            self.refused(customer, "C1", "deployed", note(customer, CS_PERSONA, "C1", DEPLOYED_NOTE),
                         r"package")


# --- deploy.md -----------------------------------------------------------------------------------------------

    def test_never_backwards_on_the_new_statuses(self):
        customer = self.packaged_copy()
        deployed = note(customer, CS_PERSONA, "C1", DEPLOYED_NOTE)
        self.assertEqual(record(customer, CS_PERSONA, "C1", "deployed", deployed).returncode, 0)
        self.refused(customer, "C1", "packaged", deployed, r"(?i)never moves a status backwards")
        verified = note(customer, CS_PERSONA, "C1", VERIFIED_NOTE, "verified.md")
        self.assertEqual(record(customer, CS_PERSONA, "C1", "verified", verified).returncode, 0)
        self.refused(customer, "C1", "deployed", deployed, r"(?i)never moves a status backwards")
        self.refused(customer, "C1", "packaged", deployed, r"(?i)never moves a status backwards")

    def no_by(self, customer, status, evidence):
        """A missing --by is argparse's exit 2; an empty or blank one is record's usage refusal, also exit 2."""
        before = manifest_path(customer, CS_PERSONA).read_bytes()
        persona = Path(customer) / "personas" / CS_PERSONA
        out = run_cli("record", persona, "C1", "--status", status, "--evidence", evidence)
        self.assertEqual(out.returncode, 2, out.stdout + out.stderr)
        self.assertIn("--by", out.stderr)
        for by in ("", "   "):
            out = record(customer, CS_PERSONA, "C1", status, evidence, by=by)
            self.assertEqual(out.returncode, 2, out.stdout + out.stderr)
            self.assertIn("--by is empty", out.stderr)
            self.assertIn("Next:", out.stderr)
        self.assertEqual(manifest_path(customer, CS_PERSONA).read_bytes(), before)

    def test_by_is_required_for_deployed_and_verified(self):
        customer = self.packaged_copy()
        deployed = note(customer, CS_PERSONA, "C1", DEPLOYED_NOTE)
        self.no_by(customer, "deployed", deployed)
        self.assertEqual(record(customer, CS_PERSONA, "C1", "deployed", deployed).returncode, 0)
        self.no_by(customer, "verified", note(customer, CS_PERSONA, "C1", VERIFIED_NOTE, "verified.md"))


class DeployChecklistTests(unittest.TestCase):
    def test_sections_in_order(self):
        for sample in CUSTOMERS:
            with self.subTest(sample=sample.name):
                text = (sample / "build" / "deploy.md").read_text(encoding="utf-8")
                self.assertEqual([h for h, _ in sections(text)], SECTIONS)

    def test_every_step_maps_to_backlog_tasks(self):
        for sample, persona in ((PE_CUSTOMER, PE_PERSONA), (CS_CUSTOMER, CS_PERSONA)):
            tasks = backlog_tasks(sample, persona)
            text = (sample / "build" / "deploy.md").read_text(encoding="utf-8")
            count = 0
            for heading, steps in sections(text):
                for step in steps:
                    count += 1
                    with self.subTest(sample=sample.name, step=step.split("\n")[0][:80]):
                        ids = TASK_IDS.findall(step.split("\n")[0])
                        self.assertTrue(ids, "no backlog task id")
                        for tid in ids:
                            self.assertIn(tid, tasks)
                        story, task = tasks[ids[0]]
                        self.assertIn("Owner: %s" % task["owner_role"], step)
                        self.assertRegex(step, r"Package: ")
            self.assertGreater(count, 10)

    def test_publishing_follows_the_distribution(self):
        pe = (PE_CUSTOMER / "build" / "deploy.md").read_text(encoding="utf-8")
        cs = (CS_CUSTOMER / "build" / "deploy.md").read_text(encoding="utf-8")
        pe_publish = dict(sections(pe))["4. Publish the marketplace"]
        cs_publish = dict(sections(cs))["4. Publish the marketplace"]
        self.assertTrue(any("S-distribution.distribute-group" in s for s in pe_publish))
        self.assertTrue(any("S-distribution.distribute-everyone" in s for s in cs_publish))
        self.assertIn("group-targeted", pe)
        self.assertIn("everyone", cs)
        self.assertTrue(any("build/marketplace/" in s for s in cs_publish))
        hosted = dict(sections(cs))["5. Hosted agents, routines and scheduled tasks"]
        self.assertTrue(any("S-C2.setup-tag-routine" in s and "build/bundles/%s/C2/" % CS_PERSONA in s
                            for s in hosted))

    def test_gated_steps_say_so(self):
        text = (PE_CUSTOMER / "build" / "deploy.md").read_text(encoding="utf-8")
        tasks = backlog_tasks(PE_CUSTOMER, PE_PERSONA)
        checked = 0
        for _, steps in sections(text):
            for step in steps:
                ids = TASK_IDS.findall(step.split("\n")[0])
                gated = [t for t in ids if tasks[t][0].get("gated_by")]
                with self.subTest(step=step.split("\n")[0][:80]):
                    if gated:
                        checked += 1
                        self.assertIn("Gated", step)
                        for gate in tasks[gated[0]][0]["gated_by"]:
                            self.assertIn(gate["id"], step)
                    else:
                        self.assertNotIn("Gated", step)
        self.assertGreater(checked, 0)

    def test_links_resolve_and_no_secrets(self):
        for sample in CUSTOMERS:
            path = sample / "build" / "deploy.md"
            text = path.read_text(encoding="utf-8")
            for target in LINK.findall(text):
                with self.subTest(sample=sample.name, link=target):
                    self.assertFalse(re.match(r"^[a-z]+:", target), "an external link")
                    self.assertTrue((path.parent / target.split("#")[0]).resolve().exists())
            self.assertEqual(secret_findings(text), [])


# --- No secrets, and the committed samples ------------------------------------------------------------------

class ExclusionTests(unittest.TestCase):
    """deploy.md places a template (package.SECTIONS, HANDOVER) or leaves it out by name (package.EXCLUDED)."""

    def test_every_library_template_is_placed_or_excluded_never_both(self):
        placed = set(t for _, templates in package_mod.SECTIONS for t in templates) | {package_mod.HANDOVER}
        library = load(PLUGIN_DIR / "data" / "task-library.json")["templates"]
        ids = [t["id"] for t in library] if isinstance(library, list) else list(library)
        self.assertEqual(sorted(placed - set(ids)), [], "placed templates the library lacks")
        for template in ids:
            reason = package_mod.excluded(template)
            with self.subTest(template=template):
                self.assertTrue((template in placed) != bool(reason),
                                "placed and excluded" if reason else "neither placed nor excluded")
        for name, reason in package_mod.EXCLUDED:
            with self.subTest(entry=name):
                self.assertTrue(reason.strip())
                self.assertTrue(any(t == name or (name.endswith("*") and t.startswith(name[:-1])) for t in ids),
                                "an exclusion that matches no template")

    def test_design_names_every_exclusion(self):
        text = DESIGN.read_text(encoding="utf-8")
        section = text[text.index("### Package and deploy"):text.index("## 9. Dashboard")]
        for name, _ in package_mod.EXCLUDED:
            self.assertIn("| `%s` |" % name, section)

    def test_every_design_exclusion_row_is_in_excluded(self):
        text = DESIGN.read_text(encoding="utf-8")
        section = text[text.index("### Package and deploy"):text.index("## 9. Dashboard")]
        table = section[section.index("| Template | Why it is left out |"):]
        rows = []
        for line in table.split("\n")[2:]:
            if not line.startswith("|"):
                break
            rows.append(re.match(r"^\| `([^`]+)` \|", line).group(1))
        names = [name for name, _ in package_mod.EXCLUDED]
        for row in rows:
            self.assertIn(row, names, "a design.md exclusion row that package.EXCLUDED lacks")
        self.assertEqual(sorted(rows), sorted(names))

    def test_every_sample_task_is_in_deploy_md_or_excluded(self):
        for customer in CUSTOMERS:
            placed, persona = {}, None
            for line in (customer / "build" / "deploy.md").read_text(encoding="utf-8").split("\n"):
                if line.startswith("### "):
                    persona = line[4:].strip()
                elif STEP.match(line):
                    ids = re.findall(r"`([^`]+)`", line.split("`: ", 1)[0] + "`")
                    placed.setdefault(persona, set()).update(ids)
            for backlog in sorted((customer / "personas").glob("*/backlog.json")):
                pid = backlog.parent.name
                for tid, (story, task) in sorted(backlog_tasks(customer, pid).items()):
                    reason = package_mod.excluded(task["template"])
                    with self.subTest(customer=customer.name, task=tid):
                        if reason:
                            self.assertNotIn(tid, placed.get(pid, set()), "an excluded task in deploy.md")
                        else:
                            self.assertIn(tid, placed.get(pid, set()), "neither in deploy.md nor excluded")


class SampleTests(unittest.TestCase):
    def test_no_secrets_in_any_build_folder(self):
        folders = []
        for sample in CUSTOMERS:
            folders.append(sample / "build")
            folders += sorted((sample / "personas").glob("*/build"))
        files = [p for folder in folders for p in sorted(folder.rglob("*")) if p.is_file()]
        self.assertTrue(any("/build/deploy.md" in p.as_posix() for p in files))
        for path in files:
            with self.subTest(path=str(path.relative_to(ROOT))):
                self.assertEqual(secret_findings(path.read_text(encoding="utf-8")), [])

    def test_the_scan_finds_planted_secrets(self):
        self.assertTrue(BUILD_SECRET_PATTERNS)
        for text in ("password: hunter2", "tenant 3f2504e0-4f89-11d3-9a0c-0305e82c3301", "sk-ant-api03-x",
                     "https://example.my.salesforce.com"):
            with self.subTest(text=text):
                self.assertTrue(secret_findings(text))
        self.assertEqual(secret_findings("the runner reads $ANTHROPIC_API_KEY from its environment"), [])

    def test_committed_samples_match_a_fresh_run(self):
        for sample in CUSTOMERS:
            with self.subTest(sample=sample.name), Copy(sample) as customer:
                shutil.rmtree(str(customer / "build"), ignore_errors=True)
                for args in ((), ("--include-drafts",)):
                    out = run_cli("package", customer, *args)
                    self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
                self.assertEqual(snapshot(customer / "build"), snapshot(sample / "build"))
                for persona in sorted((sample / "personas").glob("*/build/build.json")):
                    rel = persona.relative_to(sample)
                    self.assertEqual((customer / rel).read_bytes(), persona.read_bytes())

    def test_samples_hold_drafts_only(self):
        self.assertFalse((PE_CUSTOMER / "build" / "marketplace").exists())
        self.assertFalse((CS_CUSTOMER / "build" / "marketplace").exists())
        self.assertTrue((CS_CUSTOMER / "build" / "marketplace-draft" / ".claude-plugin" / "marketplace.json").is_file())
        for sample in CUSTOMERS:
            for path in sorted((sample / "personas").glob("*/build/build.json")):
                for item in load(path)["artifacts"]:
                    self.assertIn(item["status"], ("scaffolded", "drafted", "not-built"))


class DocsTests(unittest.TestCase):
    def test_design_and_readmes(self):
        design = DESIGN.read_text(encoding="utf-8")
        section = design.split("## 8a. Build", 1)[1].split("## 9.", 1)[0]
        for text in ("cli.py package", "--include-drafts", "deploy.md", "marketplace-draft", "bundles/",
                     "deployed", "verified", "DRAFT, not evaluated:"):
            self.assertIn(text, section)
        layout = design.split("## 3. Where things live", 1)[1].split("## 4.", 1)[0]
        for text in ("deploy.md", "marketplace/", "bundles/", "cli.py package"):
            self.assertIn(text, layout)
        for path in (PLUGIN_DIR / "README.md", ROOT / "partner-kit" / "README.md"):
            with self.subTest(path=str(path.relative_to(ROOT))):
                self.assertIn("cli.py package", path.read_text(encoding="utf-8"))

    def test_skill_and_playbook(self):
        skill = SKILL.read_text(encoding="utf-8")
        self.assertIn("deploy.md", skill)
        self.assertRegex(skill, r"(?i)secret store")
        playbook = PLAYBOOK.read_text(encoding="utf-8")
        self.assertIn("## Build, evaluate and deploy", playbook)
        section = playbook.split("## Build, evaluate and deploy", 1)[1].split("\n## ", 1)[0]
        self.assertIn("partner-kit/docs/design.md#8a-build", section)
        self.assertIn("building-twin-artifacts", section)
        self.assertNotIn("There are four skills", playbook)


if __name__ == "__main__":
    unittest.main()
