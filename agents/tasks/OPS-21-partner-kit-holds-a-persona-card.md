---
id: OPS-21
title: partner-kit holds a persona card and customer profile schema, a field catalogue, a validator and a validate CLI
domain: ops
tier: frontier
tier_reason: Keystone schema every later card builds on; a wrong field or rule here costs a rework of the whole pipeline
status: merged
issue: 99
scope: [partner-kit/**, tests/test_twincard_validate.py, tests/test_partner_kit_structure.py]
forbid: [starter-kit/**, .claude-plugin/**, engagements/**, docs/**]
red_test: python3 -m unittest tests.test_twincard_validate tests.test_partner_kit_structure
gate: test
budget: 2-attempts
spend: 25
---
## Why

The 2026-11-15 review found no single record that ties client interviews to a build plan. This card creates that record (the persona card, plus a customer profile) and the validator that says when it is complete. Every other part of the persona-card workflow reads these files, so it lands first and alone.

## Done when

- Read /Users/bennelsen/Documents/digital-twin/.delegation/plans/persona-card-spec.md first (an absolute path outside your worktree; read-only). Its sections 2, 3, 4, 5 and 11 bind this card. Terms: a PERSONA CARD is card.json, the record for one role at one customer. It is not the persona voice file (starter-kit/templates/persona/persona.md) and not a task card in agents/tasks/.
- partner-kit/docs/design.md is the committed design of record: the spec's sections 1 to 11 copied in, with the opening paragraph reworded so it reads as the design of the workflow (no mention of 'brain' or 'workers'; section 11 becomes 'Rules for contributors'). Later cards will cite this file.
- partner-kit/.claude-plugin/marketplace.json is named digital-twin-partner and lists exactly one plugin, twin-consultant, with source ./plugins/twin-consultant. partner-kit/plugins/twin-consultant/.claude-plugin/plugin.json names twin-consultant, version 0.1.0. The root .claude-plugin/marketplace.json and everything under starter-kit/ are unchanged.
- partner-kit/README.md and partner-kit/plugins/twin-consultant/README.md exist, are short, say the tooling is partner-only and is never installed in a customer org, carry the terms table from spec section 2, link to partner-kit/docs/design.md, and show the validate command. They describe only what this card builds; later steps are listed as 'not built yet'.
- partner-kit/plugins/twin-consultant/templates/customer-profile.json and templates/card.json are blank templates (empty strings, nulls, empty lists; one empty example object inside each list so the shape is visible) holding every field in spec sections 4.1 and 4.2, including writes[] as {system, objects, action}.
- partner-kit/plugins/twin-consultant/data/fields.json has one entry per field of both records in the shape of spec section 5 (path, record, type, values, required, asked_by, default, feeds, part). Every entry has a non-empty asked_by, or a default with a source link to a compendium or playbook page that exists. Every entry has a non-empty feeds drawn from the vocabulary in spec section 5. Every discovery id in asked_by (A1 to G4) exists in docs/playbook/02-discovery.md; interview ids are P1 to P6 and F1 to F9 as spec section 6 defines them.
- Left to you, and listed in the hand-back: which fields are required. Rule: a field is required when a levelling decision in spec section 7 or the persona voice needs it. List every optional field with a one-line reason.
- If a levelling decision in spec section 7 cannot be computed from the fields in 4.1 and 4.2, do not add a field. List the gap in the hand-back as 'gap: <decision> needs <what>'.
- partner-kit/plugins/twin-consultant/scripts/twincard/ is a package with __init__.py, fields.py (loads the catalogue relative to its own file), validate.py and cli.py. Standard library only, Python 3.9 compatible, no network. The validator takes its types, enumerations and required flags from fields.json; there is no second list of enumerations in code.
- validate.py exposes validate(persona_dir) returning errors (each with path, message, fix), warnings, and completeness (percent, required count, satisfied count, the list of missing or not-yet-answered paths). It finds the profile at ../../customer-profile.json from the persona folder. It checks: both files parse; required fields present; types and enumerations; card.customer equals the profile's customer; every inputs[].system and writes[].system is a system id in the profile; every tasks[].feature is a features[] id; ids are unique; overrides and open_questions name existing tasks; every required field has a provenance entry whose status is answered, default, assumed or open; assumed needs an owner; open needs an owner and a due date in YYYY-MM-DD; a profile under a folder named engagements/sample-* must have fictional true. plan.tier individual passes validation with a warning.
- Completeness is the share of required fields whose provenance status is answered or default, as a whole-number percentage rounded down. Provenance paths use ids, not positions: tasks.T1.minutes_each, features.pre-meeting-prep.name, systems.salesforce.edition. The profile carries its own provenance map for its own fields.
- cli.py runs as python3 partner-kit/plugins/twin-consultant/scripts/twincard/cli.py validate <persona-dir> from any working directory. It prints one line per error as '<path>: <message>. Next: <fix>', then a completeness line. --json prints the full result as JSON instead. Exit code 0 when there are no errors, 1 when validation fails, 2 on a usage error or a missing folder. Only the validate command exists in this card.
- tests/test_twincard_validate.py covers: every catalogue entry meets the asked_by-or-default rule and the feeds rule; the templates and the catalogue agree in both directions (no field in one and not the other); a complete valid card and profile built by the test in a temporary folder pass at 100 percent; at least 12 failing cases, one per check above, each asserting the error's path; completeness arithmetic with assumed and open fields; the three CLI exit codes, run with sys.executable in a subprocess.
- tests/test_partner_kit_structure.py covers: both JSON manifests parse and name what this card says; twin-consultant does not appear in the root marketplace; no file under partner-kit/ imports a module outside the standard library and the twincard package.
- python3 -m unittest discover -s tests passes, the 88 existing tests included. No file outside the scope changes.

## Review

Attempt 1 review refuted two claims (key fields flagged not required though they feed rules; inputs and writes keyed by system). Attempt 2 fixed both: 13 key fields are structurally required and outside completeness; inputs and writes are positional lists with a duplicate warning. Two profile fields added at the brain's request: runtime_preferences.self_hosting_required and governance.action_log_required. Second review: 19 confirmed, 0 refuted, 3 unverifiable (none about the code). Open item carried forward: governance.action_log_required is asked by G1, which asks where the log goes, not whether one is required; the docs card (#154) adds the discovery question.
