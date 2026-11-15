#!/usr/bin/env python3
"""twin-governance hook: append one metadata-only JSON line per tool call.

Registered in hooks/hooks.json on PostToolUse and PostToolUseFailure for all
tools. Python 3 standard library only.

Contract:
  * Reads the hook JSON from stdin (https://code.claude.com/docs/en/hooks,
    "PostToolUse input" and "PostToolUseFailure input").
  * Appends exactly one JSON line to the governance log.
  * Always exits 0 and prints nothing to stdout, so it never blocks or changes
    a tool call, even on bad input or an unwritable log. Problems go to stderr.
  * Logs metadata only. tool_input, tool_response, error text, prompts, file
    contents and full paths are never written. The only thing read from
    tool_input is a capped list of record ids (see extract_record_ids).

Configuration (environment variables; see the plugin README):
  TWIN_GOVERNANCE_LOG        log path (default ~/.claude/twin-governance/log.jsonl)
  TWIN_GOVERNANCE_TWIN_ID    twin id written to every line
  TWIN_GOVERNANCE_ORG_LABEL  org label written to every line
  TWIN_GOVERNANCE_MODE       "metadata" (default). There is no content mode.
"""

import datetime
import getpass
import json
import os
import re
import sys

SCHEMA_VERSION = 1
DEFAULT_LOG = os.path.join("~", ".claude", "twin-governance", "log.jsonl")
MAX_RECORD_IDS = 20
MAX_FIELD_CHARS = 200
RECORD_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
RECORD_ID_KEYS = frozenset({"id", "Id", "recordId", "record_id"})
MAX_WALK_DEPTH = 20
MAX_WALK_NODES = 10000
MCP_PREFIX = "mcp__"


def warn(message):
    try:
        sys.stderr.write("twin-governance: " + message + "\n")
    except Exception:
        pass


def short_text(value):
    """A string field, trimmed to a sane length, or None if it is not a string."""
    if isinstance(value, str):
        return value[:MAX_FIELD_CHARS]
    return None


def env_text(name):
    value = os.environ.get(name)
    return short_text(value) if value else None


def cwd_basename(cwd):
    """Last path component only (never the full path). Handles / and \\ separators."""
    if not isinstance(cwd, str):
        return None
    parts = [p for p in re.split(r"[\\/]+", cwd) if p]
    return parts[-1][:MAX_FIELD_CHARS] if parts else None


def os_user():
    try:
        return getpass.getuser()
    except Exception:
        return os.environ.get("USER") or os.environ.get("USERNAME") or "unknown"


def parse_mcp(tool_name):
    """mcp__server__tool -> (server, tool); (None, None) for any other tool."""
    if not isinstance(tool_name, str) or not tool_name.startswith(MCP_PREFIX):
        return None, None
    parts = tool_name[len(MCP_PREFIX):].split("__", 1)
    server = parts[0] or None
    tool = parts[1] if len(parts) > 1 and parts[1] else None
    return (server[:MAX_FIELD_CHARS] if server else None,
            tool[:MAX_FIELD_CHARS] if tool else None)


def is_record_id_key(key):
    return isinstance(key, str) and (key in RECORD_ID_KEYS or key.endswith("_id"))


def extract_record_ids(tool_input):
    """Values of id-like keys in tool_input that look like ids; at most 20.

    Keys: id, Id, recordId, record_id, or any key ending in _id. Values must be
    strings (or ints) matching ^[A-Za-z0-9_-]{1,64}$. Nested dicts and lists are
    searched, bounded in depth and size. Nothing else is read from tool_input.
    """
    found = []
    stack = [(tool_input, 0)]
    visited = 0
    while stack and len(found) < MAX_RECORD_IDS and visited < MAX_WALK_NODES:
        node, depth = stack.pop()
        visited += 1
        if depth > MAX_WALK_DEPTH:
            continue
        if isinstance(node, dict):
            children = []
            for key, value in node.items():
                if is_record_id_key(key):
                    if isinstance(value, int) and not isinstance(value, bool):
                        value = str(value)
                    if isinstance(value, str) and RECORD_ID_PATTERN.match(value):
                        found.append(value)
                        if len(found) >= MAX_RECORD_IDS:
                            break
                        continue
                if isinstance(value, (dict, list)):
                    children.append((value, depth + 1))
            # reversed so the first child is processed first (document order)
            stack.extend(reversed(children))
        elif isinstance(node, list):
            stack.extend((item, depth + 1) for item in reversed(node))
    return found[:MAX_RECORD_IDS]


def outcome_for(event):
    if event == "PostToolUse":
        return "success"
    if event == "PostToolUseFailure":
        return "failure"
    return "unknown"


def build_entry(data):
    event = short_text(data.get("hook_event_name"))
    tool = short_text(data.get("tool_name"))
    mcp_server, mcp_tool = parse_mcp(tool)
    now = datetime.datetime.now(datetime.timezone.utc)
    return {
        "schema_version": SCHEMA_VERSION,
        "ts": now.strftime("%Y-%m-%dT%H:%M:%S.") + "%03dZ" % (now.microsecond // 1000),
        "session_id": short_text(data.get("session_id")),
        "event": event,
        "tool": tool,
        "outcome": outcome_for(event),
        "cwd_basename": cwd_basename(data.get("cwd")),
        "os_user": os_user(),
        "twin_id": env_text("TWIN_GOVERNANCE_TWIN_ID"),
        "org_label": env_text("TWIN_GOVERNANCE_ORG_LABEL"),
        "mcp_server": mcp_server,
        "mcp_tool": mcp_tool,
        "record_ids": extract_record_ids(data.get("tool_input")),
    }


def log_path():
    configured = os.environ.get("TWIN_GOVERNANCE_LOG") or DEFAULT_LOG
    return os.path.expanduser(configured)


def append_line(path, line):
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, mode=0o700, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        # One write call for the whole line, so concurrent hooks do not interleave.
        os.write(fd, (line + "\n").encode("utf-8"))
    finally:
        os.close(fd)


def main():
    mode = (os.environ.get("TWIN_GOVERNANCE_MODE") or "metadata").strip().lower()
    if mode != "metadata":
        warn("unknown TWIN_GOVERNANCE_MODE %r; logging metadata only (the only mode)" % mode)

    raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    try:
        data = json.loads(raw)
    except ValueError as exc:
        warn("hook input is not valid JSON, nothing logged: %s" % exc)
        return
    if not isinstance(data, dict):
        warn("hook input is not a JSON object, nothing logged")
        return

    line = json.dumps(build_entry(data), separators=(",", ":"), ensure_ascii=True)
    append_line(log_path(), line)


if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:  # never block or alter a tool call
        warn("%s: %s" % (type(exc).__name__, exc))
    sys.exit(0)
