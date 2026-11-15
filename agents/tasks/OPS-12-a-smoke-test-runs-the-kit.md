---
id: OPS-12
title: A smoke test runs the kit's three plugins in a real headless Claude Code session and records whether plugins load, both skills trigger and the governance log is written
domain: ops
tier: standard
tier_reason: scripting against the live CLI; no deep design, but flags must match the installed version
effort: high
effort_reason: live tooling with unknown flag behaviour; results must be recorded exactly, failures included
status: merged
issue: 80
parent: 23
fixes: []
scope: [starter-kit/smoke/**]
forbid: [starter-kit/settings/**, tests/test_settings.py, starter-kit/runbooks/identity-devices-publishing.md, docs/compendium/README.md, starter-kit/runbooks/salesforce-hosted-mcp.md, starter-kit/runbooks/microsoft-365-connector.md]
red_test: test -f starter-kit/smoke/README.md
gate: test
budget: 2-attempts
spend: 10
---
## Why

Nothing in the starter kit has run end to end. The plugins were validated but never loaded in a live session with the hook running, the skills were tested by agents reading SKILL.md, and the trigger evals were a simulation. Before the kit goes to a customer we need one real run and an honest record of what it proves.

## Done when

- Before writing, the worker runs claude --version and claude --help and reads https://code.claude.com/docs/en/plugins-reference and https://code.claude.com/docs/en/headless (or the pages they redirect to) to confirm the flags for loading a plugin from a folder for one session, for headless output as stream JSON, and for limiting the allowed tools. The installed CLI and the docs win over this card; differences are listed in the report
- starter-kit/smoke/smoke.py (Python 3 standard library only) runs claude headless (claude -p) from the repo root, loading starter-kit/plugins/twin-shared, twin-pe-deal-team and twin-governance from their folders for that session only. It installs nothing, adds no marketplace and writes nothing under the user's ~/.claude plugin or settings files
- Each run sets TWIN_GOVERNANCE_LOG to a new temporary file outside the repo, TWIN_GOVERNANCE_TWIN_ID=twin-pe-deal-team and a throwaway TWIN_GOVERNANCE_SALT, uses the sonnet model, and allows only read-type tools plus the Skill tool (no Write, Edit, Bash, WebFetch or WebSearch)
- Run 1 prompt uses a trigger phrase and does not name the skill: 'Prep a brief on Larch. The deal files are in <absolute path to starter-kit/plugins/twin-pe-deal-team/skills/preparing-company-briefs/evals/files>.' Run 2 prompt: 'Update the CRM for my meeting with Larch. My notes and the opportunity export are in <absolute path to the drafting-crm-updates evals/files folder>.'
- For each run the script checks and prints pass or fail for: (a) the session's init event lists all three plugins and both skills; (b) the expected skill was actually invoked (the Skill tool call or the equivalent event names it); (c) no write, shell or web tool was called; (d) the governance log file has at least one line per tool call in the stream, every line parses as JSON with schema_version 2 and twin_id twin-pe-deal-team; (e) the log file contains none of these strings: Larch, the fixture folder path, any fixture file name; (f) the final answer for run 1 has no claim that anything was saved, and for run 2 says nothing was written to the CRM
- The script exits non-zero if any check fails, and prints the claude version and model used
- starter-kit/smoke/README.md says how to run it, that it costs model usage and is therefore not part of the unittest gate, and holds a results table from the worker's own run: date, claude version, model, each check per run as pass or fail, copied from real output and not written by hand from expectation
- The README has a 'What this does not prove' section that names at least: it is not a managed device and allowManagedHooksOnly is not in force; the marketplace install path and managed-settings delivery are not exercised; connectors are not live (the deal data is fixture files read with file tools, so no record ids reach the log); one run per prompt, so no measure of variance
- If a check fails, the worker records the failure in the README and the report with the evidence, and does not change any file outside starter-kit/smoke/ to make it pass
- If the worker cannot run claude headless at all (not signed in, permission denied, nested sessions blocked), it stops and hands back saying exactly what blocked it. It does not write results it did not observe
- No transcript, session id, user name, home path or token is committed; the results table holds only the check names and outcomes
- The gate passes: python3 -m unittest discover -s tests

## Review

Brain review: smoke.py runs both card prompts through claude -p with the three plugins via --plugin-dir; all six checks passed on 2.1.322 / sonnet; checks shown to fail on bad input. README has results table and a 'What this does not prove' section covering the card's four items plus three. No transcript, path or token committed. Accepted choice: --bare avoided because it skips plugin hooks.
