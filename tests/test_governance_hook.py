"""Checks for the twin-governance hook: starter-kit/plugins/twin-governance/hooks.

The hook appends one metadata-only JSON line per tool call. These tests run the
script as a subprocess with sample hook JSON on stdin and a temp log path.

Standard library only. Run with: python3 -m unittest tests.test_governance_hook
(or: python3 -m unittest discover -s tests)

Hook input shape: https://code.claude.com/docs/en/hooks (PostToolUse input,
PostToolUseFailure input). hooks.json shape:
https://code.claude.com/docs/en/plugins-reference (hooks).
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN_DIR = ROOT / "starter-kit" / "plugins" / "twin-governance"
HOOKS_DIR = PLUGIN_DIR / "hooks"
SCRIPT = HOOKS_DIR / "governance_log.py"
HOOKS_JSON = HOOKS_DIR / "hooks.json"

FAKE_SECRET = "sk-test-FAKE-SECRET-0123456789abcdef"
FAKE_PROMPT = "Summarise the confidential Project Falcon term sheet for me"
FAKE_FILE_BODY = "BEGIN FILE BODY: EBITDA was 41.7m and the seller wants out"
FAKE_RESPONSE = "RESPONSE-CONTENT-should-never-be-logged"
FULL_PATH = "/Users/someone/deals/project-falcon"
FILE_PATH = FULL_PATH + "/term-sheet.docx"

SF_ID_18 = "0065e00000AbCdEfGH"
SF_ID_15 = "0065e00000AbCdE"
HUBSPOT_ID = "51234567890"
GUID = "3f2504e0-4f89-11d3-9a0c-0305e82c3301"
SALT = "test-salt-do-not-log"

REQUIRED_FIELDS = (
    "schema_version",
    "ts",
    "session_id",
    "event",
    "tool",
    "outcome",
    "os_user",
    "twin_id",
    "org_label",
)


def sample_input(**overrides):
    data = {
        "session_id": "sess-123",
        "transcript_path": "/Users/someone/.claude/projects/x/abc.jsonl",
        "cwd": FULL_PATH,
        "permission_mode": "default",
        "hook_event_name": "PostToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": FILE_PATH, "content": FAKE_FILE_BODY},
        "tool_response": {"filePath": FILE_PATH, "type": "create", "note": FAKE_RESPONSE},
        "tool_use_id": "toolu_01ABC",
        "duration_ms": 12,
    }
    data.update(overrides)
    return data


class HookTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.log = self.tmp / "nested" / "dir" / "log.jsonl"

    def run_hook(self, stdin, log=None, extra_env=None, raw=False):
        env = dict(os.environ)
        env.pop("TWIN_GOVERNANCE_MODE", None)
        env.pop("TWIN_GOVERNANCE_SALT", None)
        env.update({
            "TWIN_GOVERNANCE_LOG": str(log if log is not None else self.log),
            "TWIN_GOVERNANCE_TWIN_ID": "twin-pe-deal-team",
            "TWIN_GOVERNANCE_ORG_LABEL": "pe-org",
        })
        env.update(extra_env or {})
        payload = stdin if raw else json.dumps(stdin)
        return subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=payload,
            capture_output=True,
            text=True,
            env=env,
            timeout=30,
        )

    def lines(self):
        text = self.log.read_text(encoding="utf-8")
        return [line for line in text.split("\n") if line]


class TestHooksJson(unittest.TestCase):
    def test_files_present(self):
        self.assertTrue(SCRIPT.is_file(), "hooks/governance_log.py is missing")
        self.assertTrue(HOOKS_JSON.is_file(), "hooks/hooks.json is missing")
        self.assertFalse((HOOKS_DIR / ".gitkeep").exists(), "hooks/.gitkeep should be removed")

    def test_registered_for_all_tools_with_short_timeout(self):
        data = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
        self.assertIn("hooks", data, "hooks.json needs the top-level 'hooks' wrapper")
        events = data["hooks"]
        for event in ("PostToolUse", "PostToolUseFailure"):
            self.assertIn(event, events)
            groups = events[event]
            self.assertTrue(groups)
            for group in groups:
                self.assertIn(group.get("matcher", "*"), ("*", ""), "must match all tools")
                self.assertTrue(group["hooks"])
                for handler in group["hooks"]:
                    self.assertEqual(handler["type"], "command")
                    self.assertIn("${CLAUDE_PLUGIN_ROOT}", handler["command"])
                    self.assertIn("governance_log.py", handler["command"])
                    self.assertLessEqual(handler["timeout"], 5)


class TestGovernanceHook(HookTestCase):
    def test_one_line_per_call_and_required_fields(self):
        for _ in range(3):
            result = self.run_hook(sample_input())
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "")
        lines = self.lines()
        self.assertEqual(len(lines), 3)
        for line in lines:
            entry = json.loads(line)
            for field in REQUIRED_FIELDS:
                self.assertIn(field, entry)
            self.assertEqual(entry["schema_version"], 2)
            self.assertEqual(entry["session_id"], "sess-123")
            self.assertEqual(entry["event"], "PostToolUse")
            self.assertEqual(entry["tool"], "Write")
            self.assertEqual(entry["outcome"], "success")
            self.assertNotIn("cwd_basename", entry)
            self.assertEqual(entry["twin_id"], "twin-pe-deal-team")
            self.assertEqual(entry["org_label"], "pe-org")
            self.assertTrue(entry["os_user"])
            self.assertTrue(entry["ts"].endswith("Z"), "timestamp must be UTC")

    def test_failure_event_outcome(self):
        data = sample_input(hook_event_name="PostToolUseFailure", error="Exit code 1\n" + FAKE_SECRET)
        del data["tool_response"]
        result = self.run_hook(data)
        self.assertEqual(result.returncode, 0, result.stderr)
        entry = json.loads(self.lines()[0])
        self.assertEqual(entry["event"], "PostToolUseFailure")
        self.assertEqual(entry["outcome"], "failure")
        self.assertNotIn(FAKE_SECRET, self.log.read_text(encoding="utf-8"))

    def test_content_never_logged(self):
        data = sample_input(
            tool_input={
                "file_path": FILE_PATH,
                "content": FAKE_FILE_BODY,
                "prompt": FAKE_PROMPT,
                "api_key": FAKE_SECRET,
                "headers": {"Authorization": "Bearer " + FAKE_SECRET},
                "nested": [{"body": FAKE_FILE_BODY}],
                "id": SF_ID_18,
            },
            prompt=FAKE_PROMPT,
            user_prompt=FAKE_PROMPT,
            error=FAKE_SECRET,
        )
        result = self.run_hook(data)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        text = self.log.read_text(encoding="utf-8")
        for secret in (FAKE_SECRET, FAKE_PROMPT, FAKE_FILE_BODY, FAKE_RESPONSE,
                       FULL_PATH, FILE_PATH, "term-sheet", "transcript", "/Users/someone",
                       "toolu_01ABC"):
            self.assertNotIn(secret, text, f"{secret!r} leaked into the log")
        entry = json.loads(text)
        self.assertEqual(entry["record_ids"], [SF_ID_18])

    def test_content_never_logged_in_mode_variants(self):
        # There is no content mode: an unknown or 'content' mode still logs metadata only.
        for mode in ("metadata", "content", "full", ""):
            self.log.unlink(missing_ok=True)
            result = self.run_hook(sample_input(), extra_env={"TWIN_GOVERNANCE_MODE": mode})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "")
            text = self.log.read_text(encoding="utf-8")
            self.assertNotIn(FAKE_FILE_BODY, text)
            self.assertNotIn(FAKE_RESPONSE, text)

    def test_record_ids_allowlist_kept(self):
        data = sample_input(
            tool_name="mcp__salesforce__update_record",
            tool_input={
                "id": SF_ID_18,
                "Id": SF_ID_15,
                "recordId": HUBSPOT_ID,
                "record_id": GUID,
                "account_id": GUID.upper(),
                "fields": {"opportunity_id": 12345, "Amount": "1000000"},
                "list": [{"recordId": SF_ID_18}],
            },
        )
        result = self.run_hook(data)
        self.assertEqual(result.returncode, 0, result.stderr)
        entry = json.loads(self.lines()[0])
        self.assertEqual(
            sorted(entry["record_ids"]),
            sorted([SF_ID_18, SF_ID_15, HUBSPOT_ID, GUID, GUID.upper(), "12345", SF_ID_18]),
        )
        self.assertNotIn("1000000", self.log.read_text(encoding="utf-8"))

    def test_falcon_target_logs_no_record_id(self):
        data = sample_input(
            tool_name="mcp__salesforce__update_record",
            tool_input={"id": "Falcon_target", "account_id": "Falcon_target", "deal_id": "Falcon-target"},
        )
        result = self.run_hook(data)
        self.assertEqual(result.returncode, 0, result.stderr)
        entry = json.loads(self.lines()[0])
        self.assertEqual(entry["record_ids"], [])
        self.assertNotIn("Falcon", self.log.read_text(encoding="utf-8"))

    def test_record_ids_other_shapes_dropped(self):
        rejected = [
            "001A", "006ABC123", "001-E_f", "has spaces so it is rejected", "x" * 65,
            'quote"inside', "", "Falcon_target",
            "0065e00000AbCdEf",        # 16 chars: not a Salesforce id length
            "0065e00000AbCdEfGHI",     # 19 chars
            "0065e00000AbCd_",         # 15 chars with an underscore
            "12345678-1234-1234-1234-12345678901",    # GUID one char short
            "12345678-1234-1234-1234-1234567890123",  # GUID one char long
            "1234567812341234123412345678901z",       # not hex, no dashes
            "123\n",                   # trailing newline after digits
            SF_ID_18 + "\n",
            "12.5", "-7",
        ]
        for value in rejected:
            with self.subTest(value=value):
                self.log.unlink(missing_ok=True)
                result = self.run_hook(sample_input(tool_input={"id": value}))
                self.assertEqual(result.returncode, 0, result.stderr)
                entry = json.loads(self.lines()[0])
                self.assertEqual(entry["record_ids"], [])
        self.log.unlink(missing_ok=True)
        self.run_hook(sample_input(tool_input={"id": True, "record_id": 3.5}))
        self.assertEqual(json.loads(self.lines()[0])["record_ids"], [])

    def test_record_ids_capped_at_20(self):
        data = sample_input(
            tool_name="mcp__salesforce__bulk_update",
            tool_input={"records": [{"id": str(1000 + i)} for i in range(50)]},
        )
        result = self.run_hook(data)
        self.assertEqual(result.returncode, 0, result.stderr)
        entry = json.loads(self.lines()[0])
        self.assertEqual(len(entry["record_ids"]), 20)

    def test_cwd_never_in_log_line(self):
        for salt in (None, SALT):
            with self.subTest(salt=salt):
                self.log.unlink(missing_ok=True)
                extra = {"TWIN_GOVERNANCE_SALT": salt} if salt else {}
                result = self.run_hook(sample_input(cwd="/x/project-falcon"), extra_env=extra)
                self.assertEqual(result.returncode, 0, result.stderr)
                text = self.log.read_text(encoding="utf-8")
                self.assertNotIn("project-falcon", text)
                self.assertNotIn("falcon", text.lower())
                self.assertNotIn("cwd_basename", text)
                if salt:
                    self.assertNotIn(salt, text)

    def test_cwd_hash_with_salt(self):
        cwd = "/x/project-falcon"
        result = self.run_hook(sample_input(cwd=cwd), extra_env={"TWIN_GOVERNANCE_SALT": SALT})
        self.assertEqual(result.returncode, 0, result.stderr)
        entry = json.loads(self.lines()[0])
        expected = hashlib.sha256((SALT + cwd).encode("utf-8")).hexdigest()[:12]
        self.assertEqual(entry["cwd_hash"], expected)
        self.assertRegex(entry["cwd_hash"], r"^[0-9a-f]{12}$")
        # Same cwd and salt give the same hash; another cwd or salt does not.
        self.log.unlink()
        self.run_hook(sample_input(cwd=cwd), extra_env={"TWIN_GOVERNANCE_SALT": SALT})
        self.run_hook(sample_input(cwd="/x/other"), extra_env={"TWIN_GOVERNANCE_SALT": SALT})
        self.run_hook(sample_input(cwd=cwd), extra_env={"TWIN_GOVERNANCE_SALT": SALT + "2"})
        hashes = [json.loads(line)["cwd_hash"] for line in self.lines()]
        self.assertEqual(hashes[0], expected)
        self.assertNotEqual(hashes[1], expected)
        self.assertNotEqual(hashes[2], expected)

    def test_cwd_hash_absent_without_salt(self):
        env = {"TWIN_GOVERNANCE_SALT": ""}
        for extra in (None, env):
            self.log.unlink(missing_ok=True)
            result = self.run_hook(sample_input(), extra_env=extra)
            self.assertEqual(result.returncode, 0, result.stderr)
            entry = json.loads(self.lines()[0])
            self.assertNotIn("cwd_hash", entry)
            self.assertNotIn("cwd_basename", entry)

    def test_cwd_hash_absent_when_cwd_not_a_string(self):
        self.run_hook(sample_input(cwd=42), extra_env={"TWIN_GOVERNANCE_SALT": SALT})
        self.assertNotIn("cwd_hash", json.loads(self.lines()[0]))

    def test_no_record_ids_gives_empty_list(self):
        self.run_hook(sample_input())
        entry = json.loads(self.lines()[0])
        self.assertEqual(entry["record_ids"], [])

    def test_mcp_tool_name_split(self):
        result = self.run_hook(sample_input(tool_name="mcp__salesforce__query_records"))
        self.assertEqual(result.returncode, 0, result.stderr)
        entry = json.loads(self.lines()[0])
        self.assertEqual(entry["tool"], "mcp__salesforce__query_records")
        self.assertEqual(entry["mcp_server"], "salesforce")
        self.assertEqual(entry["mcp_tool"], "query_records")

    def test_mcp_tool_name_with_double_underscore_in_tool(self):
        self.run_hook(sample_input(tool_name="mcp__plugin_x_y__get__thing"))
        entry = json.loads(self.lines()[0])
        self.assertEqual(entry["mcp_server"], "plugin_x_y")
        self.assertEqual(entry["mcp_tool"], "get__thing")

    def test_non_mcp_tool_has_no_server(self):
        self.run_hook(sample_input(tool_name="Bash", tool_input={"command": "echo " + FAKE_SECRET}))
        entry = json.loads(self.lines()[0])
        self.assertIsNone(entry["mcp_server"])
        self.assertIsNone(entry["mcp_tool"])
        self.assertNotIn(FAKE_SECRET, self.log.read_text(encoding="utf-8"))

    def test_creates_missing_directories(self):
        self.assertFalse(self.log.parent.exists())
        self.run_hook(sample_input())
        self.assertTrue(self.log.is_file())

    def test_default_log_path_under_home(self):
        home = self.tmp / "home"
        home.mkdir()
        env = {"HOME": str(home), "USERPROFILE": str(home)}
        full_env = dict(os.environ)
        full_env.pop("TWIN_GOVERNANCE_LOG", None)
        full_env.update(env)
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=json.dumps(sample_input()),
            capture_output=True,
            text=True,
            env=full_env,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        default = home / ".claude" / "twin-governance" / "log.jsonl"
        self.assertTrue(default.is_file())
        self.assertEqual(len(default.read_text(encoding="utf-8").splitlines()), 1)

    def test_unset_twin_id_and_org_label_are_null(self):
        env = dict(os.environ)
        env.pop("TWIN_GOVERNANCE_TWIN_ID", None)
        env.pop("TWIN_GOVERNANCE_ORG_LABEL", None)
        env["TWIN_GOVERNANCE_LOG"] = str(self.log)
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=json.dumps(sample_input()),
            capture_output=True,
            text=True,
            env=env,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        entry = json.loads(self.lines()[0])
        self.assertIsNone(entry["twin_id"])
        self.assertIsNone(entry["org_label"])


class TestHookNeverBlocks(HookTestCase):
    def assert_silent_success(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_malformed_stdin(self):
        for payload in ("not json at all", "{", "", "[1, 2, 3]", "null", '"a string"', "\x00\xff"):
            with self.subTest(payload=payload):
                self.assert_silent_success(self.run_hook(payload, raw=True))
        if self.log.exists():
            self.assertEqual(self.lines(), [])

    def test_wrong_field_types(self):
        data = sample_input(tool_name=["a"], cwd=42, session_id={"x": 1}, tool_input="a string")
        self.assert_silent_success(self.run_hook(data))
        for line in (self.lines() if self.log.exists() else []):
            json.loads(line)

    def test_unwritable_log_path(self):
        blocker = self.tmp / "afile"
        blocker.write_text("x")
        # A directory cannot be created under a regular file.
        result = self.run_hook(sample_input(), log=blocker / "sub" / "log.jsonl")
        self.assert_silent_success(result)
        self.assertIn("twin-governance", result.stderr)

    def test_log_path_is_a_directory(self):
        directory = self.tmp / "adir"
        directory.mkdir()
        self.assert_silent_success(self.run_hook(sample_input(), log=directory))

    @unittest.skipIf(os.name == "nt" or (hasattr(os, "geteuid") and os.geteuid() == 0),
                     "read-only directory check needs a non-root POSIX user")
    def test_read_only_directory(self):
        ro = self.tmp / "ro"
        ro.mkdir()
        ro.chmod(0o500)
        self.addCleanup(ro.chmod, 0o700)
        self.assert_silent_success(self.run_hook(sample_input(), log=ro / "log.jsonl"))


if __name__ == "__main__":
    unittest.main()
