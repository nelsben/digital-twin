"""Tests for the check and record commands: a built artifact goes from drafted to evals-passing only on
real eval evidence (OPS-75).

The design of record is partner-kit/docs/design.md, section 8a. `check` runs deterministic checks on each
artifact in build/build.json; `record` moves an artifact one status at a time, never backwards, and only
from drafted to evals-passing, on skill-creator's benchmark.json or `claude plugin eval`'s JSON result
under build/evidence/<artifact-id>/. The evidence fixtures under tests/fixtures/twincard/evidence/ say in
their note key that they are test fixtures, not real runs. Every test that writes works on a temporary
copy of a fictional sample engagement, build folder included, so nothing is written under engagements/.

Standard library only. Run with: python3 -m unittest tests.test_twincard_build_record
"""

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
CLI = PLUGIN_DIR / "scripts" / "twincard" / "cli.py"
DESIGN = ROOT / "partner-kit" / "docs" / "design.md"
SKILL_DIR = PLUGIN_DIR / "skills" / "building-twin-artifacts"
FIXTURES = ROOT / "tests" / "fixtures" / "twincard" / "evidence"
BENCHMARK = FIXTURES / "skill-creator-benchmark.json"
PLUGIN_EVAL = FIXTURES / "plugin-eval-result.json"
PE = ROOT / "engagements" / "sample-pe" / "personas" / "deal-team-associate"
CS = ROOT / "engagements" / "sample-team-cs" / "personas" / "customer-success-manager"
SAMPLES = (PE, CS)
C1_SKILL = "build/plugin/twin-customer-success-manager/skills/account-brief-before-a-customer-call"
T3_SKILL = "build/skills/weekly-pipeline-summary-for-the-monday-deal-meeting"
HISTORY_KEYS = ["status", "by", "evidence", "pass_rate", "baseline_rate", "pass_mark", "approved_by"]
ABOVE = ("packaged", "deployed", "verified")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dump(path, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_cli(*args):
    return subprocess.run([sys.executable, str(CLI)] + [str(a) for a in args],
                          capture_output=True, text=True, encoding="utf-8")


def artifact(data, tid):
    return next(a for a in data["artifacts"] if a["id"] == tid)


class Copy(object):
    """A temporary copy of a sample engagement with its build/ folder."""

    def __init__(self, persona_dir):
        self.persona_dir = Path(persona_dir)

    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        engagement = self.persona_dir.parent.parent
        root = Path(self.tmp.name) / engagement.name
        shutil.copytree(str(engagement), str(root))
        return root / self.persona_dir.relative_to(engagement)

    def __exit__(self, *exc):
        self.tmp.cleanup()


def manifest(persona):
    return load(Path(persona) / "build" / "build.json")


def problem_lines(out):
    return [line for line in out.stdout.splitlines() if "Next:" in line]


def lines_naming(out, name):
    return [line for line in problem_lines(out) if name in line]


def put_evidence(persona, tid, source, name=None, change=None):
    """Copy a fixture into build/evidence/<tid>/, optionally changed; returns its path."""
    data = load(source)
    if change:
        change(data)
    folder = Path(persona) / "build" / "evidence" / tid
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / (name or Path(source).name)
    dump(path, data)
    return path


def record(persona, tid, evidence, *extra, status="evals-passing", by="Test consultant"):
    return run_cli("record", persona, tid, "--status", status, "--evidence", evidence, "--by", by, *extra)


# --- check: skills -----------------------------------------------------------------------------------------

class CheckSkillTests(unittest.TestCase):
    """Each rule on the Team sample's drafted C1: it passes as committed, and fails once broken."""

    def check_c1(self, change, expect):
        with Copy(CS) as persona:
            skill = persona / C1_SKILL
            change(skill)
            out = run_cli("check", persona, "C1")
            self.assertEqual(out.returncode, 1, out.stdout + out.stderr)
            found = [line for line in problem_lines(out) if re.search(expect, line)]
            self.assertTrue(found, "no problem line matches %r in:\n%s" % (expect, out.stdout))
            for line in problem_lines(out):
                self.assertRegex(line, r"^engagements/sample-team-cs/personas/customer-success-manager/build/\S+: .+"
                                       r"\. Next: .+")
            return out

    def edit(self, rel, old, new):
        def change(skill):
            path = skill / rel
            text = path.read_text(encoding="utf-8")
            self.assertIn(old, text)
            path.write_text(text.replace(old, new, 1), encoding="utf-8")
        return change

    def test_committed_c1_passes(self):
        out = run_cli("check", CS, "C1")
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertEqual(problem_lines(out), [])

    def test_frontmatter_has_only_name_and_description(self):
        self.check_c1(self.edit("SKILL.md", "\ndescription:", "\nlicense: Apache-2.0\ndescription:"),
                      r"SKILL\.md: .*frontmatter.*license")

    def test_name_equals_the_folder(self):
        self.check_c1(self.edit("SKILL.md", "name: account-brief-before-a-customer-call",
                                "name: account-brief"), r"SKILL\.md: .*name.*folder")

    def test_name_meets_the_rule(self):
        def change(skill):
            new = skill.parent / "claude-account-brief"
            skill.rename(new)
            path = new / "SKILL.md"
            path.write_text(path.read_text(encoding="utf-8").replace(
                "name: account-brief-before-a-customer-call", "name: claude-account-brief", 1), encoding="utf-8")
            evals = load(new / "evals" / "evals.json")
            evals["skill_name"] = "claude-account-brief"
            dump(new / "evals" / "evals.json", evals)
            # The manifest names the folder by the artifact's skill_name, so the check finds no SKILL.md
            # there unless the manifest follows; follow it the way a person renaming the skill would.
            data = load(skill.parents[3] / "build.json")
            artifact(data, "C1")["skill_name"] = "claude-account-brief"
            dump(skill.parents[3] / "build.json", data)
        self.check_c1(change, r"SKILL\.md: .*reserved word claude")

    def test_description_under_200(self):
        def change(skill):
            path = skill / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            head, rest = text.split("\ndescription: ", 1)
            line, tail = rest.split("\n", 1)
            path.write_text(head + "\ndescription: " + "x" * 200 + "\n" + tail, encoding="utf-8")
        out = self.check_c1(change, r"SKILL\.md: .*description is 200 characters")
        self.assertTrue(lines_naming(out, "1,024"), "the message says why: the 1,024 and 200 conflict")

    def test_body_under_500_lines(self):
        def change(skill):
            path = skill / "SKILL.md"
            path.write_text(path.read_text(encoding="utf-8") + "\nfiller\n" * 500, encoding="utf-8")
        self.check_c1(change, r"SKILL\.md: .*body is \d+ lines")

    def test_no_fill_in_in_any_file(self):
        self.check_c1(self.edit("references/example-reference.md", "\n", "\nFILL IN: one more check.\n"),
                      r"references/example-reference\.md: .*FILL IN")

    def test_no_fill_in_in_an_added_file(self):
        def change(skill):
            (skill / "references" / "extra.md").write_text("# Extra\n\nFILL IN later.\n", encoding="utf-8")
        self.check_c1(change, r"references/extra\.md: .*FILL IN")

    def test_linked_file_exists(self):
        def change(skill):
            path = skill / "SKILL.md"
            path.write_text(path.read_text(encoding="utf-8") + "\nSee [the glossary](references/glossary.md).\n",
                            encoding="utf-8")
        self.check_c1(change, r"SKILL\.md: .*references/glossary\.md.*does not exist")

    def test_linked_file_one_level_deep(self):
        def change(skill):
            (skill / "references" / "deep").mkdir()
            (skill / "references" / "deep" / "x.md").write_text("# X\n", encoding="utf-8")
            path = skill / "SKILL.md"
            path.write_text(path.read_text(encoding="utf-8") + "\nSee [x](references/deep/x.md).\n",
                            encoding="utf-8")
        self.check_c1(change, r"SKILL\.md: .*references/deep/x\.md.*one level")

    def test_linked_file_inside_the_folder(self):
        def change(skill):
            path = skill / "SKILL.md"
            path.write_text(path.read_text(encoding="utf-8") + "\nSee [card](../../../../../card.json).\n",
                            encoding="utf-8")
        self.check_c1(change, r"SKILL\.md: .*card\.json.*outside")

    def test_evals_shape(self):
        def change(skill):
            dump(skill / "evals" / "evals.json", [{"prompt": "x"}])
        self.check_c1(change, r"evals/evals\.json: .*skill_name and an evals list")

    def test_evals_skill_name(self):
        def change(skill):
            data = load(skill / "evals" / "evals.json")
            data["skill_name"] = "other-skill"
            dump(skill / "evals" / "evals.json", data)
        self.check_c1(change, r"evals/evals\.json: .*skill_name")

    def test_evals_at_least_three_cases(self):
        def change(skill):
            data = load(skill / "evals" / "evals.json")
            data["evals"] = data["evals"][:2]
            dump(skill / "evals" / "evals.json", data)
        self.check_c1(change, r"evals/evals\.json: .*2 case")

    def test_evals_case_has_a_prompt(self):
        def change(skill):
            data = load(skill / "evals" / "evals.json")
            data["evals"][0]["prompt"] = ""
            dump(skill / "evals" / "evals.json", data)
        self.check_c1(change, r"evals/evals\.json: case 1 .*prompt")

    def test_evals_case_has_an_expectation(self):
        def change(skill):
            data = load(skill / "evals" / "evals.json")
            data["evals"][1]["expectations"] = []
            dump(skill / "evals" / "evals.json", data)
        self.check_c1(change, r"evals/evals\.json: case 2 .*expectation")

    def test_trigger_evals_need_a_true_entry(self):
        def change(skill):
            data = [q for q in load(skill / "evals" / "trigger-evals.json") if not q["should_trigger"]]
            dump(skill / "evals" / "trigger-evals.json", data)
        self.check_c1(change, r"evals/trigger-evals\.json: .*should_trigger true")

    def test_trigger_evals_need_a_false_entry(self):
        def change(skill):
            data = [q for q in load(skill / "evals" / "trigger-evals.json") if q["should_trigger"]]
            dump(skill / "evals" / "trigger-evals.json", data)
        self.check_c1(change, r"evals/trigger-evals\.json: .*should_trigger false")

    def test_inputs_table_names_every_system(self):
        def change(skill):
            path = skill / "SKILL.md"
            lines = path.read_text(encoding="utf-8").splitlines(True)
            kept = [l for l in lines if not (l.startswith("|") and re.search(r"(?i)google.?drive", l))]
            self.assertLess(len(kept), len(lines))
            path.write_text("".join(kept), encoding="utf-8")
        self.check_c1(change, r"SKILL\.md: .*Inputs table.*google-drive")


# --- check: wrappers ---------------------------------------------------------------------------------------

def fill_t3(persona):
    """Fill the PE sample's T3 agent bundle as a person would, so no agent rule fires."""
    agents = Path(persona) / "build" / "agents" / "T3"
    agent = load(agents / "agent.json")
    agent["model"] = "a-pinned-model-id"
    agent["system"] = "You are the deal team's weekly pipeline twin. Draft; never send."
    for server in agent["mcp_servers"]:
        server["url"] = "$%s_MCP_URL" % server["name"].upper()
    agent["skills"] = [{"type": "custom", "skill_id": "skill_test_fixture", "version": "1"}]
    dump(agents / "agent.json", agent)
    env = load(agents / "environment.json")
    env["config"]["type"] = "self-hosted-test"
    dump(agents / "environment.json", env)
    return agents


class CheckWrapperTests(unittest.TestCase):
    def check_t3(self, change=None):
        with Copy(PE) as persona:
            agents = fill_t3(persona)
            if change:
                change(agents, persona)
            out = run_cli("check", persona, "T3")
            return [l for l in problem_lines(out) if "/agents/T3/" in l], out

    def test_filled_agent_bundle_has_no_agent_problem(self):
        lines, out = self.check_t3()
        self.assertEqual(lines, [], out.stdout)

    def test_scaffolded_agent_bundle_fails(self):
        out = run_cli("check", PE, "T3")
        self.assertEqual(out.returncode, 1)
        self.assertTrue(lines_naming(out, "agents/T3/agent.json"))

    def test_agent_json_parses(self):
        lines, _ = self.check_t3(lambda a, p: (a / "agent.json").write_text("{not json", encoding="utf-8"))
        self.assertTrue([l for l in lines if re.search(r"agent\.json: .*not JSON", l)], lines)

    def test_environment_json_parses(self):
        lines, _ = self.check_t3(lambda a, p: (a / "environment.json").write_text("[", encoding="utf-8"))
        self.assertTrue([l for l in lines if re.search(r"environment\.json: .*not JSON", l)], lines)

    def test_model_is_set(self):
        def change(agents, persona):
            data = load(agents / "agent.json")
            data["model"] = ""
            dump(agents / "agent.json", data)
        lines, _ = self.check_t3(change)
        self.assertTrue([l for l in lines if re.search(r"agent\.json: .*model", l)], lines)

    def test_system_is_set(self):
        def change(agents, persona):
            data = load(agents / "agent.json")
            del data["system"]
            dump(agents / "agent.json", data)
        lines, _ = self.check_t3(change)
        self.assertTrue([l for l in lines if re.search(r"agent\.json: .*system", l)], lines)

    def test_networking_is_limited(self):
        def change(agents, persona):
            data = load(agents / "environment.json")
            data["config"]["networking"] = {"type": "unrestricted"}
            dump(agents / "environment.json", data)
        lines, _ = self.check_t3(change)
        self.assertTrue([l for l in lines if re.search(r"environment\.json: .*limited", l)], lines)

    def test_names_a_skill(self):
        def change(agents, persona):
            data = load(agents / "agent.json")
            data["skills"] = []
            dump(agents / "agent.json", data)
        lines, _ = self.check_t3(change)
        self.assertTrue([l for l in lines if re.search(r"agent\.json: .*skill", l)], lines)

    def test_the_skill_exists(self):
        def change(agents, persona):
            shutil.rmtree(str(Path(persona) / T3_SKILL))
        lines, _ = self.check_t3(change)
        self.assertTrue([l for l in lines if re.search(r"agent\.json: .*does not exist", l)], lines)

    def test_routine_sheet_has_no_fill_in(self):
        out = run_cli("check", CS, "C2")
        self.assertEqual(out.returncode, 1)
        self.assertTrue([l for l in problem_lines(out) if re.search(r"routines/C2/routine\.md: .*FILL IN", l)])
        with Copy(CS) as persona:
            path = persona / "build" / "routines" / "C2" / "routine.md"
            path.write_text(path.read_text(encoding="utf-8").replace("FILL IN", "Done"), encoding="utf-8")
            out = run_cli("check", persona, "C2")
            self.assertEqual(lines_naming(out, "routine.md"), [], out.stdout)

    def test_scheduled_and_sdk_sheets_have_no_fill_in(self):
        with Copy(CS) as persona:
            card = load(persona / "card.json")
            card["overrides"] = [
                {"task": "C3", "decision": "runtime", "value": "claude-code-scheduled-task",
                 "reason": "Invented reason for a test.", "approved_by": "Test approver"},
                {"task": "C5", "decision": "runtime", "value": "agent-sdk",
                 "reason": "Invented reason for a test.", "approved_by": "Test approver"}]
            dump(persona / "card.json", card)
            self.assertIn(run_cli("level", persona).returncode, (0, 1))
            self.assertEqual(run_cli("build", persona, "--all-tasks").returncode, 0)
            out = run_cli("check", persona)
            self.assertTrue([l for l in problem_lines(out) if re.search(r"scheduled/C3/task\.md: .*FILL IN", l)])
            self.assertTrue([l for l in problem_lines(out) if re.search(r"sdk/C5/README\.md: .*FILL IN", l)])
            for rel in ("scheduled/C3/task.md", "sdk/C5/README.md"):
                path = persona / "build" / rel
                path.write_text(path.read_text(encoding="utf-8").replace("FILL IN", "Done"), encoding="utf-8")
            out = run_cli("check", persona)
            self.assertEqual(lines_naming(out, "task.md") + lines_naming(out, "README.md"), [], out.stdout)


class CheckCommandTests(unittest.TestCase):
    def test_whole_persona_exits_1_while_any_artifact_is_scaffolded(self):
        out = run_cli("check", CS)
        self.assertEqual(out.returncode, 1)
        self.assertTrue(lines_naming(out, "weekly-renewal-risk-digest"))
        self.assertEqual(lines_naming(out, "account-brief-before-a-customer-call"), [])

    def test_check_writes_nothing(self):
        with Copy(CS) as persona:
            before = {p: p.read_bytes() for p in persona.rglob("*") if p.is_file()}
            run_cli("check", persona)
            after = {p: p.read_bytes() for p in persona.rglob("*") if p.is_file()}
            self.assertEqual(before, after)

    def test_usage_errors_are_exit_2(self):
        out = run_cli("check", CS, "C9")
        self.assertEqual(out.returncode, 2)
        self.assertIn("Next:", out.stderr)
        with Copy(CS) as persona:
            shutil.rmtree(str(persona / "build"))
            out = run_cli("check", persona)
            self.assertEqual(out.returncode, 2)
            self.assertRegex(out.stderr, r"build\.json.*Next: .*build")


# --- record ------------------------------------------------------------------------------------------------

class RecordTests(unittest.TestCase):
    def test_fixtures_say_they_are_fixtures(self):
        for path in (BENCHMARK, PLUGIN_EVAL):
            with self.subTest(fixture=path.name):
                note = load(path).get("note", "")
                self.assertIn("test fixture", note.lower())
                self.assertIn("not a real run", note.lower())

    def assert_recorded(self, persona, evidence, pass_rate, baseline_rate, pass_mark=100, approved_by=None):
        item = artifact(manifest(persona), "C1")
        self.assertEqual(item["status"], "evals-passing")
        self.assertEqual(len(item["history"]), 1)
        entry = item["history"][0]
        self.assertEqual(list(entry), HISTORY_KEYS)
        self.assertEqual(entry["status"], "evals-passing")
        self.assertEqual(entry["by"], "Test consultant")
        self.assertEqual(entry["evidence"], "engagements/sample-team-cs/personas/customer-success-manager/build/"
                                            "evidence/C1/" + Path(evidence).name)
        self.assertAlmostEqual(entry["pass_rate"], pass_rate)
        self.assertAlmostEqual(entry["baseline_rate"], baseline_rate)
        self.assertEqual(entry["pass_mark"], pass_mark)
        self.assertEqual(entry["approved_by"], approved_by)

    def test_skill_creator_benchmark(self):
        with Copy(CS) as persona:
            evidence = put_evidence(persona, "C1", BENCHMARK)
            out = record(persona, "C1", evidence)
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
            fixture = load(BENCHMARK)["run_summary"]
            self.assert_recorded(persona, evidence, fixture["with_skill"]["pass_rate"]["mean"],
                                 fixture["without_skill"]["pass_rate"]["mean"])

    def test_plugin_eval_result(self):
        with Copy(CS) as persona:
            evidence = put_evidence(persona, "C1", PLUGIN_EVAL)
            out = record(persona, "C1", evidence)
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
            cases = load(PLUGIN_EVAL)["cases"]
            score = sum(c["aggregates"]["score"] for c in cases) / len(cases)
            baseline = sum(c["aggregates"]["score"] - c["aggregates"]["delta"] for c in cases) / len(cases)
            self.assert_recorded(persona, evidence, score, baseline)

    def test_lower_mark_with_approval(self):
        def lower(data):
            data["run_summary"]["with_skill"]["pass_rate"]["mean"] = 0.9
        with Copy(CS) as persona:
            evidence = put_evidence(persona, "C1", BENCHMARK, change=lower)
            out = record(persona, "C1", evidence, "--pass-mark", "90", "--approved-by", "Marisol Quenby")
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
            self.assert_recorded(persona, evidence, 0.9, load(BENCHMARK)["run_summary"]["without_skill"]
                                 ["pass_rate"]["mean"], pass_mark=90, approved_by="Marisol Quenby")

    def test_history_kept_across_a_build_rerun(self):
        with Copy(CS) as persona:
            evidence = put_evidence(persona, "C1", BENCHMARK)
            self.assertEqual(record(persona, "C1", evidence).returncode, 0)
            before = artifact(manifest(persona), "C1")
            out = run_cli("build", persona, "--all-tasks")
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
            after = artifact(manifest(persona), "C1")
            self.assertEqual(after["status"], "evals-passing")
            self.assertEqual(after["history"], before["history"])
            out = run_cli("build", persona)
            self.assertEqual(artifact(manifest(persona), "C1")["history"], before["history"])

    def test_every_artifact_has_a_history_list(self):
        for sample in SAMPLES:
            for item in manifest(sample)["artifacts"]:
                with self.subTest(sample=sample.name, task=item["id"]):
                    self.assertEqual(item["history"], [])


class RecordRefusalTests(unittest.TestCase):
    """Every refusal exits 1, says what to do next and leaves build.json as it was."""

    def refused(self, persona, out, expect):
        self.assertEqual(out.returncode, 1, out.stdout + out.stderr)
        text = out.stdout + out.stderr
        self.assertRegex(text, expect)
        self.assertIn("Next:", text)

    def run_refusal(self, expect, tid="C1", source=BENCHMARK, change=None, extra=(), status="evals-passing",
                    evidence=None, persona_dir=CS, prepare=None):
        with Copy(persona_dir) as persona:
            if prepare:
                prepare(persona)
            path = evidence(persona) if evidence else put_evidence(persona, tid, source, change=change)
            before = (persona / "build" / "build.json").read_bytes()
            out = record(persona, tid, path, *extra, status=status)
            self.refused(persona, out, expect)
            self.assertEqual((persona / "build" / "build.json").read_bytes(), before)

    def test_check_failing(self):
        def prepare(persona):
            path = persona / C1_SKILL / "SKILL.md"
            path.write_text(path.read_text(encoding="utf-8") + "\nFILL IN\n", encoding="utf-8")
        self.run_refusal(r"check", prepare=prepare)

    def test_evidence_missing(self):
        self.run_refusal(r"(?i)evidence.*(missing|no such|does not exist)",
                         evidence=lambda p: p / "build" / "evidence" / "C1" / "benchmark.json")

    def test_evidence_outside_build_evidence(self):
        def outside(persona):
            path = persona / "benchmark.json"
            shutil.copy(str(BENCHMARK), str(path))
            return path
        self.run_refusal(r"build/evidence/C1", evidence=outside)

    def test_evidence_of_another_artifact(self):
        self.run_refusal(r"build/evidence/C1", evidence=lambda p: put_evidence(p, "C4", BENCHMARK))

    def test_evidence_escaping_with_dot_dot(self):
        def escape(persona):
            shutil.copy(str(BENCHMARK), str(persona / "benchmark.json"))
            (persona / "build" / "evidence" / "C1").mkdir(parents=True)
            return persona / "build" / "evidence" / "C1" / ".." / ".." / ".." / "benchmark.json"
        self.run_refusal(r"build/evidence/C1", evidence=escape)

    def test_evidence_not_a_known_shape(self):
        self.run_refusal(r"(?i)benchmark|plugin eval", change=lambda d: d.pop("run_summary"))

    def test_evidence_not_json(self):
        def bad(persona):
            folder = persona / "build" / "evidence" / "C1"
            folder.mkdir(parents=True)
            (folder / "benchmark.json").write_text("{not json", encoding="utf-8")
            return folder / "benchmark.json"
        self.run_refusal(r"(?i)json", evidence=bad)

    def test_benchmark_for_another_skill(self):
        self.run_refusal(r"skill_name", change=lambda d: d["metadata"].update(skill_name="another-skill"))

    def test_benchmark_without_baseline(self):
        def drop(data):
            data["run_summary"].pop("without_skill")
            data["runs"] = [r for r in data["runs"] if r["configuration"] == "with_skill"]
        self.run_refusal(r"without_skill", change=drop)

    def test_benchmark_missing_a_case(self):
        def drop(data):
            data["runs"] = [r for r in data["runs"] if r["eval_id"] != 2]
        self.run_refusal(r"(?i)case|eval", change=drop)

    def test_plugin_eval_without_baseline(self):
        def drop(data):
            for case in data["cases"]:
                case["aggregates"].pop("delta")
            data["aggregates"].pop("meanDelta")
        self.run_refusal(r"delta", source=PLUGIN_EVAL, change=drop)

    def test_plugin_eval_partial(self):
        def partial(data):
            data["partial"] = True
            data["partialReason"] = "cost_ceiling"
        self.run_refusal(r"partial", source=PLUGIN_EVAL, change=partial)

    def test_plugin_eval_skipped_graders(self):
        def skipped(data):
            data["cases"][0]["arms"]["with"][0]["skippedPaidGraders"] = True
        self.run_refusal(r"skippedPaidGraders", source=PLUGIN_EVAL, change=skipped)

    def test_pass_rate_below_the_mark(self):
        def lower(data):
            data["run_summary"]["with_skill"]["pass_rate"]["mean"] = 0.9
        self.run_refusal(r"(?i)pass rate.*below", change=lower)

    def test_plugin_eval_below_the_mark(self):
        def lower(data):
            data["cases"][0]["aggregates"]["score"] = 0.5
        self.run_refusal(r"(?i)pass rate.*below", source=PLUGIN_EVAL, change=lower)

    def test_lower_mark_without_approval(self):
        def lower(data):
            data["run_summary"]["with_skill"]["pass_rate"]["mean"] = 0.9
        self.run_refusal(r"approved-by", change=lower, extra=("--pass-mark", "90"))

    def test_skipping_a_status(self):
        self.run_refusal(r"(?i)scaffolded", tid="C4")

    def test_going_backwards(self):
        def prepare(persona):
            evidence = put_evidence(persona, "C1", BENCHMARK)
            self.assertEqual(record(persona, "C1", evidence).returncode, 0)
        self.run_refusal(r"(?i)backwards", status="drafted", prepare=prepare)
        self.run_refusal(r"(?i)already", status="evals-passing", prepare=prepare)

    def test_packaged_and_above(self):
        for status in ABOVE:
            with self.subTest(status=status):
                self.run_refusal(r"package", status=status)

    def test_usage_errors_are_exit_2(self):
        with Copy(CS) as persona:
            evidence = put_evidence(persona, "C1", BENCHMARK)
            before = (persona / "build" / "build.json").read_bytes()
            for args in (("C9", "--status", "evals-passing"), ("C1", "--status", "shipped"),
                         ("C1", "--status", "evals-passing", "--pass-mark", "120"),
                         ("C1", "--status", "evals-passing", "--pass-mark", "0")):
                with self.subTest(args=args):
                    out = run_cli("record", persona, *(args + ("--evidence", evidence, "--by", "Test consultant")))
                    self.assertEqual(out.returncode, 2, out.stdout + out.stderr)
                    self.assertIn("Next:", out.stderr)
            self.assertEqual((persona / "build" / "build.json").read_bytes(), before)


# --- The samples, the skill and the docs ---------------------------------------------------------------------

class SampleTests(unittest.TestCase):
    def test_team_c1_is_drafted_and_passes_check(self):
        self.assertEqual(artifact(manifest(CS), "C1")["status"], "drafted")
        out = run_cli("check", CS, "C1")
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)

    def test_nothing_above_drafted_and_no_evidence(self):
        for sample in SAMPLES:
            self.assertFalse((sample / "build" / "evidence").exists())
            for item in manifest(sample)["artifacts"]:
                with self.subTest(sample=sample.name, task=item["id"]):
                    self.assertIn(item["status"], ("scaffolded", "drafted", "not-built"))
                    if (sample, item["id"]) != (CS, "C1"):
                        self.assertNotEqual(item["status"], "drafted")


class SkillAndDocsTests(unittest.TestCase):
    def test_the_skill_exists(self):
        for rel in ("SKILL.md", "evals/evals.json", "evals/trigger-evals.json"):
            self.assertTrue((SKILL_DIR / rel).is_file(), rel)
        self.assertGreaterEqual(len(load(SKILL_DIR / "evals" / "evals.json")["evals"]), 3)
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        for word in ("check", "record", "build", "Haiku", "Sonnet", "Opus", "without"):
            self.assertIn(word, text)

    def test_design_lists_check_and_record(self):
        design = DESIGN.read_text(encoding="utf-8")
        section = design.split("## 8a. Build", 1)[1].split("## 9.", 1)[0]
        for text in ("cli.py check", "cli.py record", "run_summary.with_skill.pass_rate.mean",
                     "run_summary.without_skill.pass_rate.mean", "cases[].aggregates.score",
                     "cases[].aggregates.delta", "building-twin-artifacts"):
            self.assertIn(text, section)
        concrete = next(l for l in design.splitlines() if l.startswith("- **Concrete eval cases**"))
        self.assertIn("building-twin-artifacts", concrete)

    def test_readmes_list_the_commands_and_the_skill(self):
        for path in (PLUGIN_DIR / "README.md", ROOT / "partner-kit" / "README.md"):
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=str(path.relative_to(ROOT))):
                for word in ("check", "record", "building-twin-artifacts"):
                    self.assertIn(word, text)


if __name__ == "__main__":
    unittest.main()
