---
id: OPS-6
title: starter-kit/templates/persona gives a twin persona template as both a Claude Code output style and a system prompt, from one shared source
domain: ops
tier: standard
tier_reason: templates from compendium 02 and current docs
status: merged
issue: 18
parent: 16
scope: [starter-kit/templates/persona/**]
forbid: []
red_test: none
gate: test
budget: 2-attempts
spend: 10
---
## Why

Every role twin needs a consistent persona across surfaces: an output style in Claude Code, and a system prompt for hosted agents and claude.ai project instructions. Compendium 02 sets out the persona fields; the template makes them copyable and keeps the two forms from drifting.

## Done when

- Before writing, the worker reads docs/compendium/02-persona.md, the output-styles page at https://code.claude.com/docs/en/output-styles (frontmatter fields, where plugins ship output styles, and keep-coding-instructions or its current name), and Anthropic's system-prompt / prompting best-practices URL from docs/compendium/16-oob-skills-and-references.md section 4. Every frontmatter key used is in the docs; the report lists each key with its URL
- starter-kit/templates/persona/persona.md is the single source: the persona fields from compendium 02 (role, who it serves, voice and tone, what it does and never does, how it handles uncertainty and missing data, escalation, the twin marker on writes, data-class reminders), each a FILL IN section with one-line guidance
- starter-kit/templates/persona/output-style/your-twin-name.md is a Claude Code output style built from persona.md, with valid frontmatter per the docs, and a comment saying it must be copied into a plugin's output-styles/ folder
- starter-kit/templates/persona/system-prompt.md is the same persona written as a system prompt for the Messages API, Managed Agents, or claude.ai project instructions, following Anthropic's prompting guidance (clear role, context before rules, explained reasons for rules, XML-tagged sections if the guidance recommends them)
- starter-kit/templates/persona/README.md (under 60 lines): which form goes on which surface (table: Claude Code -> output style in the role plugin; claude.ai -> project instructions; hosted -> system prompt), how to fill persona.md first and then both forms, and a rule that a persona change updates both forms in the same PR
- A short worked example for the private-equity deal team is NOT written here (issue #37 owns it); the template only references it
- python3 -m unittest discover -s tests passes

## Review

Brain review: one source (persona.md, 10 sections) plus output style and XML-tagged system prompt; frontmatter keys cited to code.claude.com output-styles. Sync between forms is a README rule only, no test; acceptable for a template.
