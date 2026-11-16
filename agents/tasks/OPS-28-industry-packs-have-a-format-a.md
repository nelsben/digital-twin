---
id: OPS-28
title: Industry packs have a format, a loader and a validator check, with a general pack and a private-equity pack whose every entry cites a compendium page
domain: ops
tier: standard
tier_reason: A data format, a small loader and two data files, with the format decided in the card
effort: high
effort_reason: Every pack entry must match what its cited page says, flag included
status: merged
issue: 116
scope: [partner-kit/plugins/twin-consultant/data/industry-packs/**, partner-kit/plugins/twin-consultant/scripts/twincard/packs.py, partner-kit/plugins/twin-consultant/scripts/twincard/validate.py, tests/test_twincard_packs.py, tests/test_twincard_validate.py, partner-kit/docs/design.md, partner-kit/plugins/twin-consultant/README.md]
forbid: [partner-kit/plugins/twin-consultant/data/fields.json, partner-kit/plugins/twin-consultant/templates/**, starter-kit/**, engagements/**, docs/**, .claude-plugin/**]
red_test: python3 -m unittest tests.test_twincard_packs
gate: test
budget: 2-attempts
spend: 10
---
## Why

Ben's target is a levelled agent that uses industry information from Anthropic and data providers. The review found that industry knowledge sits only in prose pages. A pack is the machine-readable form the levelling and backlog steps read; it links to compendium pages for its facts and never restates an unconfirmed fact as settled.

## Done when

- Read partner-kit/docs/design.md (sections 2, 3, 4, 7 and the contributor rules) first. A pack is data inside the plugin: partner-kit/plugins/twin-consultant/data/industry-packs/<id>.json, found relative to the script's own file.
- Pack format, version 1. Top level: pack_version (1), id (equals the file name), name, summary (one sentence), sources (repo-relative compendium page paths), settings_baseline (the name of a file stem in starter-kit/settings, or null), and five lists. anthropic_starting_points: {kind (plugin, skill, agent-template or reference), name, where (URL or marketplace name), use (start-from, reuse or reference), note}. data_providers: {name, kind, access (connector, mcp, api or none), note}. connector_defaults: {system_kind, product, how, identity, runbook (a repo-relative path under starter-kit/runbooks, or null)}. compliance_defaults: {field (a customer-profile path in data/fields.json), value, reason}. typical_tasks: {id, name, feature, trigger, data_class, inputs (system kinds)}, where trigger and data_class use the catalogue's values for tasks[].trigger and tasks[].data_class.
- Every entry in every list also carries cite (a repo-relative path to an existing page under docs/compendium, with an optional #anchor that matches a heading on that page) and unverified (true when the cited page marks the fact with the Unverified marker). A pack states nothing the cited page does not say. Add this format to partner-kit/docs/design.md as a new subsection of section 7 or a new section, in the same style.
- partner-kit/plugins/twin-consultant/scripts/twincard/packs.py (standard library, Python 3.9+): list_packs() returns the ids; load_pack(id) returns the pack or raises an error whose message names the ids that exist; pack_problems(pack) returns a list of {path, message, fix} for every format fault, reading enumerations and profile field types from the catalogue, not from a second list.
- validate.py reports an error with a fix when the customer profile's industry is neither general nor an existing pack id, and tests/test_twincard_validate.py covers it. Nothing else in the validator changes.
- data/industry-packs/general.json exists for customers with no pack: starting points that apply to any role, taken from docs/compendium/16-oob-skills-and-references.md, and empty lists where nothing general applies.
- data/industry-packs/private-equity.json is built from docs/compendium/14-private-equity.md, 16 and 17, and 11 for connectors: the Anthropic plugins, skills and agent templates for financial services that those pages name; the data providers they name; connector defaults for Salesforce and Microsoft 365 with the two starter-kit runbooks; compliance defaults for MNPI, walls and retention; settings_baseline pe-zdr; and at least four typical deal-team tasks taken from the pages. Where page 14 or 17 marks something Unverified or Not confirmed, the entry has unverified true.
- tests/test_twincard_packs.py checks, for every pack file: it parses and pack_problems is empty; id equals the file name; every cite path exists and every anchor matches a heading; every runbook path exists; every compliance_defaults field is a profile path in the catalogue and its value has the catalogue's type; an entry with unverified true cites a page that contains the Unverified marker; load_pack of an unknown id fails with the known ids in the message; and at least six malformed packs each give the expected problem path.
- The plugin README lists the packs and the loader. python3 -m unittest discover -s tests passes. The report lists each private-equity entry with its cite and its unverified flag, and any fact you wanted in the pack but could not find on a page, as 'gap: <what> is not on <page>'.

## Review

Brain read the diff at 7f48d88 (packs.py, the validator change, design section 7.1, the README and every entry of both packs); attempt 2 only rebased onto OPS-27 and resolved one README line. The validator change is one check (profile industry must be general or a pack id). Every private-equity entry cites a compendium page listed in sources; all 12 data vendors and the Salesforce connector default carry unverified true, and each vendor note says it is not allowed in the pilot. The pack leaves out T3 (page 17 gives it no trigger) and its feature ids (pre-meeting-prep, post-meeting-follow-up, deal-screening, ic-drafting) differ from the four feature names the sample engagement uses; the customer-success pack card (#120) aligns them. Task trigger (person) and data class (highly-sensitive) are the author's choice, not page 17's, as the format section allows.
