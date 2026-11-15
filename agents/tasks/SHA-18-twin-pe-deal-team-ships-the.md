---
id: SHA-18
title: twin-pe-deal-team ships the deal-team persona as one source with an output style and a system prompt, and its README and version are current
domain: shared
tier: frontier
tier_reason: always-loaded instruction that governs how the twin handles MNPI; wording and judgment matter more than volume
status: merged
issue: 37
parent: 35
fixes: [SHA-13, SHA-14]
scope: [starter-kit/plugins/twin-pe-deal-team/output-styles/**, starter-kit/plugins/twin-pe-deal-team/persona/**, starter-kit/plugins/twin-pe-deal-team/README.md, starter-kit/plugins/twin-pe-deal-team/.claude-plugin/plugin.json, starter-kit/plugins/twin-pe-deal-team/skills/.gitkeep, tests/test_persona.py]
forbid: [starter-kit/plugins/twin-shared/**]
red_test: python3 -m unittest tests.test_persona
gate: test
budget: 2-attempts
spend: 25
---
## Why

Setting the persona was the first thing the user asked for, and only an unfilled template exists. The deal-team twin needs its persona written once and shipped in the two forms the template defines, so it behaves the same in Claude Code and on hosted surfaces. The plugin README is also stale: it says version 0.1.0 with one skill, and the plugin is at 0.2.0 with two.

## Done when

- The worker reads first: starter-kit/templates/persona/README.md and its three template files, docs/compendium/02-persona.md, 06-autonomy.md and 14-private-equity.md, engagements/sample-pe/design.md sections 3, 7 and 8, and both SKILL.md files in the plugin. It also reads https://code.claude.com/docs/en/output-styles and https://code.claude.com/docs/en/plugins-reference to confirm the output-style frontmatter keys and how a plugin ships output styles (folder name, any plugin.json field). The docs win over this card; differences are listed in the report
- starter-kit/plugins/twin-pe-deal-team/persona/persona.md is the single source, with all the template's sections filled in the second person, every rule with its reason, and no FILL IN marker or template comment left
- The persona is written for the role, not for one customer: it says 'your firm' and names roles (deal owner, Compliance, IT), never Example Capital Partners or any person from engagements/sample-pe
- The persona covers, at least: who it serves (associates, principals, partners on a deal team) and the jobs it does today (company briefs, CRM updates after meetings); voice (direct, brief, source-first); deal data is MNPI, so no web search or fetch, facts come only from the connectors or files the user supplies, and each fact carries its source; never carry facts from one deal or team into work for another, and never put deal facts into memory, skills or shared files; autonomy level 1 by default (draft, a person acts), and a user's request does not raise the level; if a system refuses access, say so and reveal nothing about the record; what to do with missing or conflicting data; who to hand off to (by role); the twin marker Last_Updated_By_Twin__c on every write to the opportunity
- Nothing in the persona contradicts either SKILL.md or references/level-2-writes.md. The report lists the points the worker cross-checked
- Procedures stay in the skills: the persona does not repeat the steps of either skill. The output style body is at most 600 words
- starter-kit/plugins/twin-pe-deal-team/output-styles/pe-deal-team-twin.md is the output style built from persona.md, with name, description, keep-coding-instructions set to false (deal-team users are not coding) and, if the docs confirm the key and that it makes the style apply when the plugin is enabled, force-for-plugin set to true. output-styles/.gitkeep is deleted
- starter-kit/plugins/twin-pe-deal-team/persona/system-prompt.md is the system-prompt form built from the same sections, using the template's tags
- tests/test_persona.py checks: the three files exist; none contains 'FILL IN'; every section heading in persona.md has matching content in both forms (the test compares the section text after normalising whitespace, so the forms cannot drift); the output style frontmatter has only the allowed keys; none of the three files contains 'Example Capital' or any name from engagements/sample-pe/stakeholders.md; the output style body is at most 600 words
- starter-kit/plugins/twin-pe-deal-team/README.md is corrected and updated: version 0.3.0; the Skills table lists both skills (preparing-company-briefs, T1, #32; drafting-crm-updates, T2, #34); a Persona section links the three files and says which form goes on which surface (link the template README, do not copy it) and that hard limits are enforced by settings and connector permissions, not by the persona; the sentence 'One skill is written ... placeholders kept with .gitkeep' is removed; the Upstream plugins section is kept
- plugin.json version becomes 0.3.0, and gains an output-style field only if the docs require one. skills/.gitkeep is deleted
- If the claude CLI is on PATH the worker runs claude plugin validate . from the repo root and pastes the result in the report
- The README says the persona has not been evaluated with users or with behavioural evals yet
- The gate passes: python3 -m unittest discover -s tests

## Review

Opus, attempt 1, verifier consistent. Sonnet review: 27 confirmed, 0 refuted, 3 unverifiable (doc-page contents, plugin validate output, red-file timing). The brain read persona.md in full: ten sections, roles only, every rule carries a reason, no deal-to-deal carry, no deal facts in memory, skills or shared files, level 1 by default and a request does not raise it, refused access reveals nothing, escalation by role (Compliance for MNPI and wall questions), the twin marker rule matches level-2-writes.md, no web tools for deal work. The output style is 598 of 600 words, so later additions need cuts. test_persona.py holds the three forms in sync and blocks the sample's invented names.
