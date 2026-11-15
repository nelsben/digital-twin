---
id: OPS-1
title: Repo root is a Claude plugin marketplace listing three plugin skeletons: twin-shared, twin-pe-deal-team, twin-governance
domain: ops
tier: standard
tier_reason: small scaffold but must match current plugin docs exactly
status: merged
issue: 14
parent: 13
scope: [.claude-plugin/marketplace.json, starter-kit/plugins/**]
forbid: []
red_test: python3 -m json.tool .claude-plugin/marketplace.json
gate: test
budget: 2-attempts
spend: 10
---
## Why

The starter kit is delivered to customers as Claude plugins, so the repo itself must be an installable marketplace (one plugin per role plus a shared and a governance plugin, per docs/compendium/01-anatomy.md). Later stories add skills, output styles and hooks into these skeletons.

## Done when

- Before writing, the worker reads https://code.claude.com/docs/en/plugin-marketplaces and https://code.claude.com/docs/en/plugins-reference and follows the file layout and field names they give; if they differ from this card, the docs win and the worker lists the difference in its report
- .claude-plugin/marketplace.json exists at the repo root with a marketplace name 'digital-twin-kit', an owner object, and exactly three plugin entries whose source paths point at ./starter-kit/plugins/twin-shared, ./starter-kit/plugins/twin-pe-deal-team and ./starter-kit/plugins/twin-governance
- Each of the three plugin folders has .claude-plugin/plugin.json with name (matching the folder), version 0.1.0, a one-sentence description, and author; no other manifest fields unless the docs mark them required
- Each plugin folder has a README.md (under 40 lines) saying what the plugin is for, which compendium pages explain it (relative links into docs/compendium), and which later issues fill it in: twin-shared -> #36; twin-pe-deal-team -> #32, #34, #37; twin-governance -> #21
- twin-shared and twin-pe-deal-team each contain an empty skills/ folder kept with a .gitkeep; twin-pe-deal-team also has output-styles/.gitkeep; twin-governance has hooks/.gitkeep. No SKILL.md, hook script or output style is written in this card
- All JSON files parse with python3 -m json.tool
- If the claude CLI is on PATH, the worker runs 'claude plugin validate .' (or the validate command the docs name) and pastes the result in its report; if it is not available, it says so
- The existing gate passes: python3 -m unittest discover -s tests

## Review

Brain review: marketplace and three plugin.json files match the card; `claude plugin validate .` passed. Accepted choices: placeholder owner name, per-plugin compendium links. Install-line advice deferred until the customer repo owner is known.
