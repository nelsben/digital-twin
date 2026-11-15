---
id: OPS-7
title: Governance log records only real system ids and no folder name, so deal code names cannot leak
domain: ops
tier: standard
effort: high
effort_reason: security-sensitive filter; a loose regex reopens the leak
status: merged
issue: 50
parent: 19
fixes: [OPS-5]
scope: [starter-kit/plugins/twin-governance/hooks/governance_log.py, starter-kit/plugins/twin-governance/README.md, starter-kit/plugins/twin-governance/.claude-plugin/plugin.json, tests/test_governance_hook.py]
forbid: []
red_test: python3 -m unittest tests.test_governance_hook
gate: test
budget: 2-attempts
spend: 10
---
## Why

The governance log is meant to be metadata only for private-equity data, but record_ids accepts any id-shaped string (so a code name like Falcon_target is logged) and cwd_basename logs the working folder, which on a deal team is often the deal name. Issue #50.

## Done when

- record_ids keeps only values matching known id formats: Salesforce 15- or 18-character ids (alphanumeric, the 15-character form with a 3-digit key prefix pattern is fine), HubSpot numeric ids, and GUIDs (Microsoft Graph); every other value is dropped, not truncated or hashed
- cwd_basename is removed from the record; in its place a field cwd_hash holds the first 12 hex characters of sha256 over a salt plus the full cwd, with the salt read from TWIN_GOVERNANCE_SALT and the field omitted when no salt is set
- schema_version is bumped by one and twin-governance plugin.json version goes to 0.3.0
- New tests in tests/test_governance_hook.py: the Falcon_target case logs no record id; a Salesforce 18-character id, a HubSpot numeric id and a GUID are kept; a cwd of /x/project-falcon never appears anywhere in the log line; cwd_hash is present with a salt and absent without
- The twin-governance README documents the id allowlist, the salt variable, and says why folder names are not logged
- The hook still never blocks a tool call and still exits 0 on bad input
- The gate passes: python3 -m unittest discover -s tests

## Review

Brain review: allowlist with fullmatch and salted cwd_hash match the card; 51 tests pass. Accepted choices: no key-prefix check, plain salt+cwd concatenation, key omitted when no salt. Residual gap: an 18-letter code name (e.g. FalconAcquisitions) still matches the Salesforce pattern; follow-up card adds the 18-character checksum and a digit requirement for 15-character ids.
