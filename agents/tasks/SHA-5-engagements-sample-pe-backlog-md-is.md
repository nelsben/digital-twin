---
id: SHA-5
title: engagements/sample-pe/backlog.md is the prioritized story backlog for the deal-team twin, with full story cards for T1 and T2
domain: shared
tier: standard
tier_reason: structured docs from existing engagement pages
status: merged
issue: 28
parent: 24
scope: [engagements/sample-pe/backlog.md, engagements/sample-pe/README.md]
forbid: []
red_test: none
gate: test
budget: 2-attempts
spend: 10
---
## Why

The prioritized backlog is the second Phase 2 deliverable the business owner signs, and it is what Phase 3 builds from. It must use the playbook's story template so it doubles as the worked example consultants copy.

## Done when

- Before writing, the worker reads docs/playbook/04-stories.md, engagements/sample-pe/discovery.md, stakeholders.md and design.md; nothing contradicts them, and people are named as in stakeholders.md
- A ranked table of every candidate task T1-T6 from discovery F with columns: Rank, Task, Type (story / spike / task), Value (minutes saved per week from F1 baselines: frequency x minutes x users), Risk (cost of a mistake from F4), Autonomy start level, Surface (from design), Blocked by (design open decisions OD-n and discovery open items), Pilot (yes / later)
- T1 (company brief) and T2 (post-meeting CRM update) are full story cards using the exact template in 04-stories.md, every field filled from discovery and design, at least 3 acceptance criteria each written so they become skill-creator eval cases, plus the guardrail line (no web tools, twin marker on writes, governance log) and a target
- Supporting items listed with their GitHub issue numbers where they already exist: wall-test spike #30, company-brief skill #32, CRM-update skill #34, house-style skill #36, persona #37, governance hook #21; and new items not yet filed listed as 'to file' (for example the OD-1 review spike of Anthropic's private-equity plugin, the Salesforce External Client App setup task, the M365 tenant consent task)
- Each story card says its Definition of ready status against the checklist in 04-stories.md (e.g. 'not ready: real examples F3 open, due 2026-12-04')
- A short 'Not in the pilot' section explains why T3-T6 wait, each citing design.md
- A 'Sign-off' line names the RevOps manager as approver of priority, as in stakeholders.md
- engagements/sample-pe/README.md: only the backlog.md row changes, to a link with status Done; relative links resolve from engagements/sample-pe/

## Review

Brain review: T1-T6 ranked with value and risk; T1 and T2 full story cards with 6 eval-shaped criteria each, honestly marked not ready (F3 gives fewer than 3 examples, connectors not set up, compliance sign-off pending). Accepted proposed targets labelled as OD-11 proposals.
