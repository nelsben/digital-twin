---
id: OPS-5
title: twin-governance plugin ships a hook that appends one metadata-only JSON line per tool call to a local governance log, tested by tests/test_governance_hook.py
domain: ops
tier: standard
tier_reason: small stdlib script with clear tests; hook schema from docs
effort: high
effort_reason: a content leak in the audit log is the costly failure; test it hard
status: merged
issue: 21
parent: 19
scope: [starter-kit/plugins/twin-governance/**, tests/test_governance_hook.py]
forbid: []
red_test: python3 -m unittest tests.test_governance_hook
gate: test
budget: 2-attempts
spend: 10
---
## Why

Compendium 15 makes our own governance log the long-term audit record, because private-equity chat retention is 30 days and ZDR sessions are excluded from the Compliance API. For private-equity data the log must hold metadata only (who, when, which tool, which records), never prompts or content, so the hook must prove it drops content.

## Done when

- Before writing, the worker reads https://code.claude.com/docs/en/hooks and the plugin hooks section of https://code.claude.com/docs/en/plugins-reference, plus docs/compendium/15-governance-and-performance.md and starter-kit/plugins/twin-governance/README.md. Hook event names, the hooks.json shape, the stdin JSON fields and the plugin-root path variable follow the docs exactly; the report names the doc section for each
- starter-kit/plugins/twin-governance/hooks/hooks.json registers the script on PostToolUse for all tools (and on PostToolUseFailure or the docs' equivalent if it exists), with a timeout of 5 seconds or less; the hooks/.gitkeep is removed
- starter-kit/plugins/twin-governance/hooks/governance_log.py: Python 3 standard library only; reads the hook JSON from stdin; appends exactly one JSON line to the log file; always exits 0 and prints nothing to stdout, so it never blocks or changes a tool call, even on bad input or an unwritable log (errors go to stderr only)
- Each log line has: schema version, UTC timestamp, session id, hook event, tool name, outcome (success / failure if the input says), cwd basename (not the full path), the OS user name, a configured twin id and org label, and for MCP tools the server and tool parsed from the mcp__server__tool name
- Content is never logged in metadata-only mode, which is the default: no tool_input values, no tool_response, no prompt, no file contents, no full paths. The only thing taken from tool_input is a list of record ids: values of keys named id, Id, recordId, record_id or ending in _id, that match ^[A-Za-z0-9_-]{1,64}$, at most 20
- Configuration is by environment variables, documented in the plugin README: TWIN_GOVERNANCE_LOG (path; default ~/.claude/twin-governance/log.jsonl, directories created), TWIN_GOVERNANCE_TWIN_ID, TWIN_GOVERNANCE_ORG_LABEL, and TWIN_GOVERNANCE_MODE (metadata, the default; there is no content mode in this card)
- tests/test_governance_hook.py runs the script as a subprocess with sample stdin JSON and a temp log path, and checks: one line per call; required fields present; a tool_input holding a fake secret string, a prompt and a file body never appears anywhere in the log line; record ids are captured and capped at 20; an MCP tool name splits into server and tool; malformed stdin and an unwritable log path still exit 0 with empty stdout
- starter-kit/plugins/twin-governance/README.md is updated: what is logged and what is never logged, the env vars, how IT ships the log to their SIEM (the destination is a customer decision, per compendium 15), and that pe-zdr and hipaa settings set allowManagedHooksOnly, so the plugin must be deployed through the managed marketplace for the hook to run
- python3 -m unittest discover -s tests passes

## Review

Brain review: ran the hook on a sample with a SOQL query naming a deal, a tool_response body and a prompt; none reached the log, exit 0, stdout empty. Meets the card. Follow-up finding: any id-shaped value passes the record-id filter (e.g. record_id "Falcon_target", a deal codename), and cwd_basename can name a deal folder; proposed as a bug, not fixed here.
