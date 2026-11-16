---
id: OPS-26
title: The kit has a role-plugin template, the shared house style carries no private-equity rules, and the persona test covers every role plugin
domain: ops
tier: standard
tier_reason: Template, test and doc edits with every decision in the card
effort: high
effort_reason: Cross-cutting three persona forms, evals and two tests must stay in step
status: merged
issue: 169
scope: [starter-kit/templates/role-plugin/**, tests/test_persona.py, tests/test_role_plugin_template.py, starter-kit/plugins/twin-shared/**, starter-kit/plugins/twin-pe-deal-team/**, starter-kit/README.md]
forbid: [starter-kit/settings/**, starter-kit/runbooks/**, starter-kit/templates/persona/**, starter-kit/templates/skill/**, .claude-plugin/**, engagements/**, docs/**, partner-kit/**]
red_test: python3 -m unittest tests.test_role_plugin_template tests.test_persona
gate: test
budget: 2-attempts
spend: 10
---
## Why

The 2026-11-15 adversarial review walked a second, non-PE customer through the kit and found that the plugin every twin installs carries deal rules, that 'rename the role plugin' has no template behind it, and that the persona test is hard-wired to one plugin. The generated backlog will tell consultants to create one role plugin per persona, so that step must exist.

## Done when

- Read the findings first: /Users/bennelsen/Documents/digital-twin/.delegation/reviews/2026-11-15/end-to-end/findings.md findings 4 and 5, and /Users/bennelsen/Documents/digital-twin/.delegation/reviews/2026-11-15/starter-kit/findings.md findings 4 and 5.
- Shared house style is neutral: starter-kit/plugins/twin-shared/skills/writing-in-house-style/references/house-style.md has no section on deal code names (later sections renumbered, check list updated), and its SKILL.md has no rule that mentions a deal. In their place SKILL.md keeps two neutral rules: names are written exactly as the source gives them, and a missing fact is reported and asked about, never filled from web search or web fetch. No file under starter-kit/plugins/twin-shared says deal, target or MNPI as a rule; eval fixtures may keep their invented project names.
- The twin-shared evals still match the skill: any expectation that tested the deal code-name rule is reworded to the neutral names rule or removed, and the report lists each case changed. twin-shared's plugin.json version is 0.3.0 and its README says the PE rules moved to twin-pe-deal-team.
- The private-equity rules live in starter-kit/plugins/twin-pe-deal-team: the deal code-name rule (never expand or guess a code name, with its reason) and the rule against web search or web fetch for material that may concern a deal are stated in persona/persona.md and, in the same words, in persona/system-prompt.md and the output style, unless they already are; and each of the two PE skills states both in one line each unless it already does. The plugin's version gets a minor bump.
- starter-kit/templates/role-plugin/ exists with a README.md and a folder twin-your-role/ holding .claude-plugin/plugin.json (name twin-your-role, version 0.1.0, a FILL IN description), README.md, and empty skills/ and output-styles/ folders kept by a .gitkeep, and a persona/ folder whose README line says to copy starter-kit/templates/persona into it (link, do not copy the persona template's content). The template README gives the steps in order: copy and rename the folder into starter-kit/plugins/, fill the persona, add skills from templates/skill, add the entry to .claude-plugin/marketplace.json (show the JSON entry), run the tests. It says one role plugin per role, never per person.
- tests/test_role_plugin_template.py checks the template: plugin.json parses and has name, version and description; the README names each step above; the template is not listed in the root marketplace.
- tests/test_persona.py no longer hard-codes twin-pe-deal-team. It finds every folder under starter-kit/plugins that holds persona/persona.md, requires at least one, and runs the drift checks on each, taking the single .md file in that plugin's output-styles/ as the output style. The stakeholder-name check keeps its present meaning for twin-pe-deal-team.
- Starter-kit lane finding 4: the Inputs tables of drafting-crm-updates and preparing-company-briefs name the real Salesforce Hosted MCP tools from the step 5 table in starter-kit/runbooks/salesforce-hosted-mcp.md (dispatch_readonly for reads; dispatch only in the level-2 text), and the line 'confirm the tool names at setup' is gone. Say that the server prefix is the name the Owner gave the connector. Keep the Unverified marker only where that runbook keeps one. Skills stay within 200 description characters and 150 body lines.
- starter-kit/README.md: step 2 of 'Start a new customer' points at templates/role-plugin instead of 'rename the role plugin'; the parts table lists the role-plugin template; item 3 of 'Reuse before you build' and the skill-creator install line say these are installed on the consultant's own unmanaged machine and link the 'Install skill-creator' section of docs/authoring-skills.md instead of repeating it.
- python3 -m unittest discover -s tests passes. The report lists the files changed per item and every eval case touched.

## Review

Brain read the diff for twin-shared, the PE persona and skills, starter-kit/README.md and tests/test_persona.py. Shared house style is neutral (section 7 removed, two neutral rules in SKILL.md, version 0.3.0); the code-name rule sits in the three PE persona forms and both PE skills; role-plugin template added with its test; persona test iterates every plugin with persona/persona.md; Inputs tables name dispatch_readonly and link the runbook; README points at templates/role-plugin and the unmanaged-machine install advice. Accepted worker choices: two sentences trimmed from the persona forms to stay within the 600-word limit; eval results are from 0.2.0 and noted as not re-run.
