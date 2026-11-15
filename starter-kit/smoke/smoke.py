#!/usr/bin/env python3
"""Smoke test: run the kit's three plugins in a real headless Claude Code session.

Runs `claude -p` twice from the repo root, loading starter-kit/plugins/twin-shared,
twin-pe-deal-team and twin-governance from their folders for that session only
(`--plugin-dir`). It installs nothing, adds no marketplace and writes nothing under
the user's ~/.claude plugin or settings files (`--no-session-persistence` also
keeps the session transcript off disk). Each run uses a fresh temporary governance
log outside the repo.

Python 3 standard library only. Costs model usage; not part of the unittest gate.
See README.md in this folder.

Exit code: 0 if every check of both runs passes, 1 if any check fails, 2 if claude
could not be run at all (not found, not signed in, timeout, no stream output).
"""

import argparse
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGINS_DIR = REPO_ROOT / "starter-kit" / "plugins"
PLUGIN_NAMES = ("twin-shared", "twin-pe-deal-team", "twin-governance")
TWIN_ID = "twin-pe-deal-team"
BRIEFS_SKILL = "twin-pe-deal-team:preparing-company-briefs"
CRM_SKILL = "twin-pe-deal-team:drafting-crm-updates"
BRIEFS_FILES = PLUGINS_DIR / TWIN_ID / "skills" / "preparing-company-briefs" / "evals" / "files"
CRM_FILES = PLUGINS_DIR / TWIN_ID / "skills" / "drafting-crm-updates" / "evals" / "files"

# Read-type tools plus the Skill tool. No Write, Edit, Bash, WebFetch or WebSearch.
ALLOWED_TOOLS = ("Read", "Glob", "Grep", "Skill")

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")
NEGATION = re.compile(r"\b(no|not|nothing|never|none|without|neither|nor|cannot)\b|n't", re.I)
SAVE_VERBS = (r"saved|stored|uploaded|exported|posted|wrote|written|filed|created|updated|"
              r"logged|published|pushed|sent|emailed")
# Positive claim that something was saved: first person, or passive with a destination.
SAVE_CLAIM = re.compile(
    r"\b(?:I|I've|I'll|we|we've)\b[^.\n]{0,40}\b(?:%s)\b"
    r"|\b(?:has|have) been\b[^.\n]{0,20}\b(?:%s)\b[^.\n]{0,60}"
    r"\b(?:to|in|into|at|on)\b[^.\n]{0,40}\b(?:file|folder|disk|SharePoint|Salesforce|CRM|record)\b"
    % (SAVE_VERBS, SAVE_VERBS), re.I)
NOTHING_WRITTEN = re.compile(
    r"\b(?:written|wrote|write|saved|save|updated|update|posted|post|changed|change|pushed|touched|"
    r"made any changes)\b", re.I)
CRM_WORDS = re.compile(r"\b(CRM|Salesforce|opportunity|record|records)\b", re.I)


def sentences(text):
    return [s.strip() for s in SENTENCE_SPLIT.split(text) if s.strip()]


def claude_version(binary):
    out = subprocess.run([binary, "--version"], capture_output=True, text=True, timeout=60,
                         stdin=subprocess.DEVNULL)
    return (out.stdout or out.stderr).strip()


def build_command(binary, model, prompt):
    command = [binary, "-p", prompt, "--model", model,
               "--output-format", "stream-json", "--verbose"]
    for name in PLUGIN_NAMES:
        command += ["--plugin-dir", str(PLUGINS_DIR / name)]
    command += [
        # Session-only: no user, project or local settings, so only the three plugins
        # (plus built-ins) shape the run, and nothing is read from or written to them.
        "--setting-sources", "",
        "--strict-mcp-config",
        # The built-in tool set is limited to read tools plus Skill; the allow list
        # lets those run without a prompt and dontAsk denies everything else.
        "--tools", ",".join(ALLOWED_TOOLS),
        "--allowedTools", ",".join(ALLOWED_TOOLS),
        "--permission-mode", "dontAsk",
        "--no-session-persistence",
    ]
    return command


def run_claude(binary, model, prompt, log_path, salt, timeout):
    env = dict(os.environ)
    env["TWIN_GOVERNANCE_LOG"] = str(log_path)
    env["TWIN_GOVERNANCE_TWIN_ID"] = TWIN_ID
    env["TWIN_GOVERNANCE_SALT"] = salt
    proc = subprocess.run(build_command(binary, model, prompt), cwd=str(REPO_ROOT), env=env,
                          capture_output=True, text=True, timeout=timeout,
                          stdin=subprocess.DEVNULL)
    events = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except ValueError:
            pass
    return proc, events


def init_event(events):
    for event in events:
        if event.get("type") == "system" and event.get("subtype") == "init":
            return event
    return None


def tool_calls(events):
    """(id, name, input) for every tool_use block in the stream, subagents included."""
    calls = []
    for event in events:
        if event.get("type") != "assistant":
            continue
        content = (event.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                calls.append((block.get("id"), block.get("name"), block.get("input") or {}))
    return calls


def tool_errors(events):
    errors = set()
    for event in events:
        if event.get("type") != "user":
            continue
        content = (event.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_result" and block.get("is_error"):
                errors.add(block.get("tool_use_id"))
    return errors


def final_answer(events):
    for event in reversed(events):
        if event.get("type") == "result":
            return event.get("result") or ""
    return ""


def read_log(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def fixture_strings():
    names = {p.name for folder in (BRIEFS_FILES, CRM_FILES) for p in folder.iterdir() if p.is_file()}
    paths = set()
    for folder in (BRIEFS_FILES, CRM_FILES):
        paths.add(str(folder))
        paths.add(str(folder.relative_to(REPO_ROOT)))
    return sorted(names), sorted(paths)


def check_init(events):
    init = init_event(events)
    if init is None:
        return False, "no system/init event in the stream"
    plugins = {p.get("name") for p in init.get("plugins", []) if isinstance(p, dict)}
    skills = set(init.get("skills", []))
    missing = [n for n in PLUGIN_NAMES if n not in plugins]
    missing += [s for s in (BRIEFS_SKILL, CRM_SKILL) if s not in skills]
    errors = init.get("plugin_errors")
    if errors:
        return False, "plugin_errors: %s" % json.dumps(errors)
    if missing:
        return False, "missing from init: %s" % ", ".join(missing)
    return True, "plugins %s and skills %s listed" % (", ".join(PLUGIN_NAMES), ", ".join((BRIEFS_SKILL, CRM_SKILL)))


def check_skill_invoked(events, expected):
    errored = tool_errors(events)
    for call_id, name, tool_input in tool_calls(events):
        if name == "Skill" and tool_input.get("skill") == expected:
            if call_id in errored:
                return False, "Skill call for %s returned an error" % expected
            return True, "Skill tool call names %s" % expected
    seen = [tool_input.get("skill") for _, name, tool_input in tool_calls(events) if name == "Skill"]
    return False, "no Skill call for %s (Skill calls seen: %s)" % (expected, seen or "none")


def check_no_forbidden_tools(events):
    calls = tool_calls(events)
    bad = sorted({name for _, name, _ in calls if name not in ALLOWED_TOOLS})
    if bad:
        return False, "tools outside the allowed set were called: %s" % ", ".join(bad)
    return True, "%d tool calls, all in %s" % (len(calls), "/".join(ALLOWED_TOOLS))


def check_log_lines(events, log_text):
    calls = tool_calls(events)
    lines = [line for line in log_text.splitlines() if line.strip()]
    problems = []
    for number, line in enumerate(lines, 1):
        try:
            entry = json.loads(line)
        except ValueError:
            problems.append("line %d is not JSON" % number)
            continue
        if not isinstance(entry, dict):
            problems.append("line %d is not a JSON object" % number)
            continue
        if entry.get("schema_version") != 2:
            problems.append("line %d schema_version is %r" % (number, entry.get("schema_version")))
        if entry.get("twin_id") != TWIN_ID:
            problems.append("line %d twin_id is %r" % (number, entry.get("twin_id")))
    if not calls:
        problems.append("the stream has no tool calls, so the log cannot be checked against them")
    if len(lines) < len(calls) or not lines:
        problems.append("%d log lines for %d tool calls" % (len(lines), len(calls)))
    if problems:
        return False, "; ".join(problems[:5])
    return True, "%d log lines for %d tool calls; all JSON, schema_version 2, twin_id %s" % (
        len(lines), len(calls), TWIN_ID)


def check_log_content(log_text):
    names, paths = fixture_strings()
    found = []
    if "larch" in log_text.lower():
        found.append("Larch")
    found += ["path %s" % p for p in paths if p in log_text]
    found += ["file name %s" % n for n in names if n in log_text]
    if found:
        return False, "log contains: %s" % "; ".join(found[:5])
    return True, "log has no Larch, fixture folder path or fixture file name"


def check_run1_answer(answer):
    if not answer.strip():
        return False, "the final answer is empty"
    claims = [s for s in sentences(answer) if SAVE_CLAIM.search(s) and not NEGATION.search(s)]
    if claims:
        return False, "possible claim that something was saved: %s" % claims[0][:160]
    return True, "no sentence claims that anything was saved (string check, see README)"


def check_run2_answer(answer):
    if not answer.strip():
        return False, "the final answer is empty"
    for s in sentences(answer):
        if NEGATION.search(s) and NOTHING_WRITTEN.search(s) and CRM_WORDS.search(s):
            return True, "says nothing was written: %s" % s[:160]
    return False, "no sentence says that nothing was written to the CRM"


def run_once(label, binary, model, prompt, expected_skill, answer_check, keep, timeout, tmp_root):
    log_path = Path(tmp_root) / ("%s.jsonl" % label)
    salt = secrets.token_hex(16)
    print("\n== %s ==" % label)
    proc, events = run_claude(binary, model, prompt, log_path, salt, timeout)
    init = init_event(events)
    if init is None:
        raise RuntimeError("no system/init event; exit code %s; stderr: %s" % (
            proc.returncode, proc.stderr.strip()[:300]))
    log_text = read_log(log_path)
    answer = final_answer(events)
    results = [
        ("a", "init lists all three plugins and both skills", check_init(events)),
        ("b", "expected skill was invoked", check_skill_invoked(events, expected_skill)),
        ("c", "no write, shell or web tool was called", check_no_forbidden_tools(events)),
        ("d", "governance log: one valid line per tool call", check_log_lines(events, log_text)),
        ("e", "governance log holds no deal name, path or file name", check_log_content(log_text)),
        ("f", "final answer says nothing was saved or written", answer_check(answer)),
    ]
    for key, name, (ok, detail) in results:
        print("%s) %-52s %s" % (key, name, "PASS" if ok else "FAIL"))
        print("     %s" % detail)
    print("model reported by init: %s; claude_code_version: %s; exit code %s" % (
        init.get("model"), init.get("claude_code_version"), proc.returncode))
    if keep:
        print("log kept at %s" % log_path)
    return [ok for _, _, (ok, _) in results], init


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--claude", default="claude", help="claude binary (default: claude)")
    parser.add_argument("--model", default="sonnet", help="model alias (default: sonnet)")
    parser.add_argument("--timeout", type=int, default=600, help="seconds per run (default: 600)")
    parser.add_argument("--keep-logs", action="store_true",
                        help="keep the temporary governance logs instead of deleting them")
    args = parser.parse_args(argv)

    binary = shutil.which(args.claude) or args.claude
    try:
        version = claude_version(binary)
    except (OSError, subprocess.TimeoutExpired) as exc:
        print("cannot run claude: %s" % exc, file=sys.stderr)
        return 2
    print("claude version: %s" % version)
    print("model requested: %s" % args.model)

    prompts = [
        ("run 1 (preparing-company-briefs)",
         "Prep a brief on Larch. The deal files are in %s." % BRIEFS_FILES,
         BRIEFS_SKILL, check_run1_answer),
        ("run 2 (drafting-crm-updates)",
         "Update the CRM for my meeting with Larch. My notes and the opportunity export are in %s."
         % CRM_FILES,
         CRM_SKILL, check_run2_answer),
    ]
    tmp_root = tempfile.mkdtemp(prefix="twin-smoke-")
    all_ok = True
    models = set()
    try:
        for label, prompt, skill, answer_check in prompts:
            try:
                oks, init = run_once(label, binary, args.model, prompt, skill, answer_check,
                                     args.keep_logs, args.timeout, tmp_root)
            except (RuntimeError, subprocess.TimeoutExpired, OSError) as exc:
                print("cannot complete %s: %s" % (label, exc), file=sys.stderr)
                return 2
            models.add(str(init.get("model")))
            all_ok = all_ok and all(oks)
    finally:
        if args.keep_logs:
            print("\nlogs in %s" % tmp_root)
        else:
            shutil.rmtree(tmp_root, ignore_errors=True)
    print("\nclaude version: %s; model used: %s" % (version, ", ".join(sorted(models))))
    print("RESULT: %s" % ("all checks passed" if all_ok else "at least one check FAILED"))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
