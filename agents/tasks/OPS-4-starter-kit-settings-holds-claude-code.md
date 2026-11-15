---
id: OPS-4
title: starter-kit/settings holds Claude Code managed-settings baselines for four data classes, checked by tests/test_settings.py
domain: ops
tier: standard
tier_reason: config plus tests; keys must be verified against live docs
status: merged
issue: 20
parent: 19
scope: [starter-kit/settings/**, tests/test_settings.py]
forbid: []
red_test: python3 -m unittest tests.test_settings
gate: test
budget: 2-attempts
spend: 10
---
## Why

IT deploys these files by MDM to enforce the data-class rules in compendium 10, 13 and 14 on every device; they are the technical half of 'which data can go where'. A test keeps them valid and stops a later edit from quietly turning web tools back on for private-equity data.

## Done when

- Before writing, the worker reads https://code.claude.com/docs/en/settings, the managed-settings / IAM / server-managed settings pages and the plugin-marketplace restriction docs linked from docs/compendium/16-oob-skills-and-references.md section 4, plus compendium 09, 10, 13 and 14. Every key used must appear in those docs; the report lists each key with the URL it came from. If a key this card names does not exist, leave it out and say so
- Four files: starter-kit/settings/general.managed-settings.json, confidential.managed-settings.json, pe-zdr.managed-settings.json, hipaa.managed-settings.json. Each is valid JSON and is a complete managed-settings file for that data class, not a diff
- All four: restrict plugin marketplaces to the kit's one reviewed marketplace (the strict known-marketplaces style key from the docs), lock the org with the force-login org key using a placeholder value REPLACE-WITH-ORG-UUID, and turn off bypass-permissions mode if the docs offer that key
- confidential, pe-zdr and hipaa additionally: only managed hooks are allowed if the docs offer that key, and permissions deny reading common secret files (.env, credential files)
- pe-zdr and hipaa additionally: permissions deny WebFetch and WebSearch (MNPI and PHI, per compendium 14 and 10), and the governance hook from the twin-governance plugin is referenced as a placeholder comment in the README, not wired yet (issue #21 owns it)
- starter-kit/settings/README.md (under 80 lines) gives: a table of the four files with which org and data class each is for (compendium 12 starting plan), what each key does with its doc URL, how IT deploys them (MDM paths for macOS and Windows and the server-managed alternative, from the docs), the warning from compendium 13 that server-managed settings are not a security boundary on unmanaged devices, and that settings do not replace ZDR or org-level controls on claude.ai
- tests/test_settings.py (stdlib only): every *.managed-settings.json parses; every top-level key is in an allowlist constant at the top of the test, with a comment linking the settings doc; pe-zdr and hipaa deny WebFetch and WebSearch; every file restricts marketplaces; no file contains a real-looking UUID (only the placeholder)
- python3 -m unittest discover -s tests passes

## Review

Brain review: templates only (starter-kit/settings), nothing applied to this repo's own settings. Every key cited to code.claude.com; disableBypassPermissionsMode correctly nested under permissions. Open: bare WebSearch deny rule inferred from the WebFetch rule; confirm in a sandbox before a customer deploy.
