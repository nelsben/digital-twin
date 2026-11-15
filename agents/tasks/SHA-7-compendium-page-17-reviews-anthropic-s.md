---
id: SHA-7
title: Compendium page 17 reviews Anthropic's private-equity and financial-analysis plugins and settles OD-1
domain: shared
tier: frontier
tier_reason: compliance judgement on MNPI and ZDR data flows that gates two stories
status: merged
issue: 51
parent: 23
scope: [docs/compendium/17-anthropic-pe-plugins-review.md, docs/compendium/README.md, docs/compendium/sources.md, engagements/sample-pe/design.md]
forbid: []
red_test: none
gate: test
budget: 2-attempts
spend: 25
---
## Why

Design OD-1 recommends layering the deal-team twin on anthropics/financial-services rather than building from scratch. Before #32 and #34 are built on top, someone must read every skill, agent, hook and connector in those two plugins and judge each data flow against our MNPI, ZDR and connector rules. Issue #51.

## Done when

- The worker reads the current anthropics/financial-services repo on GitHub (gh or WebFetch) and lists, for the private-equity and financial-analysis plugins, every skill, agent, command, hook and MCP connector with a one-line purpose and a link to the file
- For each connector and any web or external tool, the page states where data goes, whether it is first-party or third-party, and whether it is acceptable in the private-equity ZDR org per docs/compendium/10 and 11; MNPI exposure is called out explicitly
- Each skill gets a verdict: adopt as-is, adapt (say what changes), or skip (say why), with the deal-team stories T1 (#32) and T2 (#34) mapped to the skills they would layer on
- The page says how to pin a reviewed copy: fork or vendor into digital-twin-kit versus listing the upstream marketplace under strictKnownMarketplaces, with the trade-off and a recommendation, and what the re-review trigger is when upstream changes
- Facts are cited with links and the commit sha reviewed; anything not verified is marked unverified
- docs/compendium/README.md lists page 17 and docs/compendium/sources.md has a page-17 section
- engagements/sample-pe/design.md records the outcome against OD-1 (decided or still open, with the reason), without rewriting other sections
- Page 17 is under 250 lines and written in plain language for a partner consultant

## Review

Brain review: reviewer confirmed 21 claims, 0 refuted. Brain checked upstream at 3e32c22 via gh api: 12 connectors in financial-analysis .mcp.json, 23 SKILL.md files across both plugins, both hooks.json empty, no tags. Accepted: OD-1 left open pending the named reviewer and sign-off; vendoring recommended. Follow-up filed as #67 (OPS-10, MCP allowlist in pe-zdr settings). Unverified items stay marked on the page.
