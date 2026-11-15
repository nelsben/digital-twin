---
id: SHA-1
title: Compendium page 16 inventories Anthropic's out-of-the-box skills, plugins and best-practice docs, with adopt/adapt/skip for each
domain: shared
tier: standard
tier_reason: web research and synthesis into a table; no code
status: merged
issue: 12
parent: 11
scope: [docs/compendium/16-oob-skills-and-references.md, docs/compendium/README.md, docs/compendium/sources.md]
forbid: []
red_test: none
gate: test
budget: 2-attempts
spend: 10
---
## Why

The starter kit should reuse what Anthropic already ships instead of rebuilding it, and every kit page needs a trusted index of Anthropic best-practice docs to link to. This spike answers what exists today, where it lives, and whether a digital-twin engagement should adopt, adapt or skip it.

## Done when

- docs/compendium/16-oob-skills-and-references.md exists and follows the style of the other compendium pages (plain English, tables, '⚠ Unverified' where a claim could not be confirmed from a primary source, 'our recommendation' for opinions)
- Section 1 is a table of out-of-the-box skills from github.com/anthropics/skills (at least skill-creator, the template skill, the document skills docx/xlsx/pptx/pdf, mcp-builder, and any others in that repo), each with: what it does, its licence as stated in the repo, which twin roles or kit steps would use it, and adopt / adapt / skip with a one-line reason
- Section 2 is a table of Anthropic plugin marketplaces and plugins relevant to twins (the official Claude Code plugin marketplace, the knowledge-work plugins and the financial-services plugins if they exist), with the install command or source URL for each and adopt / adapt / skip
- Section 3 lists the skills built into Claude apps (claude.ai / Desktop) that a twin gets without installing anything, and notes which plans they need
- Section 4 is a reference index of Anthropic best-practice docs the kit will link to, grouped by topic: Agent Skills overview and best practices, skill authoring, evals, plugins and marketplaces, plugin reference, hooks, output styles, managed settings, MCP, Claude Code security, org skills administration on claude.ai, prompt engineering and system prompts. Each entry is a full URL that the worker opened and confirmed loads, with a one-line note on what it is for
- Every factual claim cites a URL from a primary Anthropic source (anthropic.com, docs.claude.com / platform.claude.com, code.claude.com, support.claude.com, github.com/anthropics); nothing is stated from memory without a '⚠ Unverified' flag
- A short 'What the starter kit takes from this' section ends the page: the 3-6 concrete reuse decisions the kit should follow (e.g. 'use skill-creator to scaffold and eval every skill')
- docs/compendium/README.md gains one row or line for page 16 in its reading order, and nothing else in that file changes
- docs/compendium/sources.md gains the new URLs under a heading for page 16, and nothing else in that file changes

## Review

Brain review: four sections plus 6 reuse decisions; conflicts and unverified items flagged; ~60 URLs checked live. Key finding: anthropics/financial-services ships a private-equity plugin; the deal-team epic (#23) should start from it rather than build skills from scratch.
