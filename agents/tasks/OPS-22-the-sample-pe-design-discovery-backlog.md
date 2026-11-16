---
id: OPS-22
title: The sample-pe design, discovery, backlog and README agree with each other and with the review findings
domain: ops
tier: standard
tier_reason: Docs edits across six files with every decision made in the card
status: merged
issue: 171
scope: [engagements/sample-pe/design.md, engagements/sample-pe/discovery.md, engagements/sample-pe/backlog.md, engagements/sample-pe/README.md, engagements/sample-pe/stakeholders.md, docs/playbook/04-stories.md]
forbid: [docs/compendium/**, starter-kit/**, partner-kit/**, engagements/sample-pe/personas/**, engagements/sample-pe/wall-test-protocol.md]
red_test: none
gate: test
budget: 2-attempts
spend: 10
---
## Why

The 2026-11-15 adversarial review found one blocker and ten other faults in the fictional sample engagement: deal records classed too low, an open item marked answered, design decisions with no build task, and stale or wrong citations. The persona-card fixtures are derived from these files next, so they must be consistent first.

## Done when

- Read the findings first: /Users/bennelsen/Documents/digital-twin/.delegation/reviews/2026-11-15/playbook-engagement/findings.md, section 2, findings 1 to 11. Each finding names file and line; the decisions below settle every choice the findings leave open. Everything stays fictional: reuse the people and companies already in the sample, invent no real company or person.
- Finding 1 (blocker): in design.md the data-class table puts Salesforce opportunity records and SharePoint deal-folder memos for a live deal under Highly sensitive (MNPI), allowed on ZDR surfaces only. Confidential keeps HubSpot contacts and records that name no live target. backlog.md gains a task, owned by Tomasz Hadjiev, to keep the Salesforce and Microsoft 365 connectors out of chat and Cowork for the deal-team group. If docs/compendium/09 or 11 confirms a control that does this, name it and link the page; if not, write the task as a spike that says what must be confirmed, with the compendium's Unverified marker.
- Finding 2: discovery.md E4 has status open, owners are the Salesforce and HubSpot admins named in stakeholders.md, with a due date earlier than the date of the spike the backlog calls #30. E4 is in the open-items table and every count of open items (discovery.md and stakeholders.md) says 8.
- Finding 3: backlog.md has one task each for the migration of the 8 Pro accounts (design decision 3), the 30-day retention and feedback settings (decision 6), and Okta device trust plus the IP allowlist (decision 7). Each is owned by Tomasz Hadjiev and named in the Blocked by cells of T1 and T2.
- Finding 4: T4 takes only documents the associate uploads or that sit in SharePoint. discovery.md T4 no longer says 'from email' (an emailed document is saved to SharePoint first), F2 stays true, and the backlog note about email not being in the connector plan is replaced by this decision. No mail connector row is added.
- Finding 5: design.md section 1 has a new decision 'Pilot scope: T1 and T2' with its reason taken from discovery.md, and design.md states the data class and surface for each of T3 to T6. Every citation in backlog.md that names a design decision or section points at a place that says what the backlog claims.
- Finding 6: design.md has a decision 'Scorecard' that names the metrics, the owner (Samir Castellanos) and the date by which the numeric targets are fixed (before the pilot start date the sample already uses), and cites discovery A1. discovery.md A1 points at that decision. Do not invent the numeric targets.
- Finding 7: docs/playbook/04-stories.md line 64 gives the example surface as Claude Code on a ZDR sign-in, on a managed device (no Desktop). Do not edit docs/compendium/**; another card fixes page 14.
- Finding 8: engagements/sample-pe/README.md shows design and backlog as 'Draft, awaiting sign-off', not 'Done'. The role-interview deliverable is shown as not yet in the sample, and the done-test sentence is reworded so it is true of the folder as it stands. Do not add an interview file; a later card adds interview notes with the persona card.
- Finding 9: every value in the backlog rank table is in minutes per week for the whole deal team where discovery gives the numbers. T6 keeps its per-live-deal figure, is labelled not comparable, and the text says its rank is a judgement. The phrase calling T5 and T6 of similar value is gone.
- Finding 10: the backlog table has a Feature column. T1 and T5 sit under 'Pre-meeting preparation'; the worker names the features for the other tasks, at most four features in all, and lists them in the report. T3 to T6 are marked as stubs against the story template.
- Finding 11: design.md says once, consistently, that the OD-1 review spike is done (lines near 275, 382, 389 agree), and the sign-off paragraph near line 422 says backlog.md exists and awaits sign-off. backlog.md no longer describes the item it calls #51 as work still to do.
- Also from the end-to-end lane: wherever backlog.md cites a number with #, the row says in words what the item is, and one sentence near the top says these numbers are issues in this repository's tracker that a customer does not see.
- Also: design.md section 5 no longer restates the Salesforce tool-permission rule ('Read tools: Always allow'). It says the only write route (the dispatch tool) is blocked at level 1 and links to starter-kit/runbooks/salesforce-hosted-mcp.md for the per-tool settings.
- python3 -m unittest discover -s tests passes. The report lists, per finding, the file and line changed.

## Review

Brain read the full diff. Deal records moved to Highly sensitive (MNPI); connector rule carried as spike BT-1 with the Unverified marker and OD-13; E4 open with owners and due date, count 8 in stakeholders; BT-2 to BT-4 cover decisions 3, 6, 7 and are named in T1/T2 Blocked by; T4 takes uploaded or SharePoint documents only; decisions 18 (pilot scope) and 19 (scorecard, no invented numbers) added; README statuses are Draft, awaiting sign-off; rank table values per whole team with T1 floor and T6 not comparable; Feature column with four features; # numbers explained in words. Worker choices accepted (E4 due 2026-11-27, scorecard date 2026-12-04, BT ids unfiled).
