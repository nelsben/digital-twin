---
id: SHA-4
title: engagements/sample-pe/design.md is the Phase 2 solution design for Example Capital Partners, every decision traced to discovery and the compendium
domain: shared
tier: standard
tier_reason: synthesis across many pages but every decision is already in the compendium
effort: high
effort_reason: cross-cutting must stay consistent with discovery, stakeholders and 10 compendium pages
status: merged
issue: 27
parent: 24
scope: [engagements/sample-pe/design.md, engagements/sample-pe/README.md]
forbid: []
red_test: none
gate: test
budget: 2-attempts
spend: 10
---
## Why

The design document is the Phase 2 deliverable the technical and business owners sign; it turns discovery answers into the org plan, data and device policy, connector plan, wall design and governance-log design. It is the worked example consultants copy for real customers, so every decision must cite where it came from.

## Done when

- Before writing, the worker reads engagements/sample-pe/discovery.md, engagements/sample-pe/stakeholders.md, docs/playbook/01-engagement-model.md, and compendium pages 05, 06, 09, 10, 11, 12, 13, 14, 15 and 16. Nothing in design.md contradicts discovery.md or stakeholders.md; people are named exactly as in stakeholders.md
- Sections, in order: 1 Summary (one paragraph plus a decisions table: #, Decision, Choice, Why (discovery question id), See (compendium link)); 2 Org plan; 3 Data classes and surfaces; 4 Devices; 5 Identity and access; 6 Connector plan; 7 Wall design; 8 Plugins and skills; 9 Governance log and audit; 10 Retention; 11 Spend; 12 Open design decisions; 13 Sign-off
- Org plan follows compendium 12's starting plan as it applies here: which orgs exist for this customer, who is Primary Owner and backup Owner, how the 8 domain Pro accounts migrate, and the trigger that would add a HIPAA org (discovery C2)
- Data classes and surfaces: a table mapping each data class from discovery C1 to allowed surfaces, ZDR status and web-tool status, consistent with compendium 10 and 14 (MNPI means web search and fetch off and ZDR surfaces only)
- Devices: managed (Intune) versus unmanaged rules per data class from compendium 13; operating partners and contractors on unmanaged devices get no direct access to highly sensitive data, and the design says what they get instead
- Connector plan: a row per system from discovery E1-E6 (Salesforce, HubSpot, SharePoint/OneDrive, Teams, Slack Connect, Splunk) with connector, identity (per-user OAuth or shared), read/write, setup owner from stakeholders.md, and the use/buy/build/host verdict from compendium 11
- Wall design: soft walls between deal team and investor relations, enforced by Salesforce and HubSpot role-based access with per-user identity; names spike #30 as the proof before the pilot; states what would trigger moving to a hard wall (compendium 14)
- Plugins and skills: the marketplace from .claude-plugin/marketplace.json (twin-shared, twin-pe-deal-team, twin-governance), the first skills T1 and T2 with autonomy level 1 (compendium 06), and the managed-settings restriction to this one reviewed marketplace (compendium 16 decision 5)
- Open design decisions includes, as OD-1, whether the deal-team plugin is layered on Anthropic's private-equity and financial-analysis plugins from anthropics/financial-services (compendium 16) or built from scratch: our recommendation is to layer, pending partner sign-off and a review spike; and lists every still-open discovery item that blocks design (C2, C3, E6, G1, G2, G3) with owner and date
- Governance log: what is recorded (metadata only for private-equity, per compendium 15), candidate destination Splunk pending G1, Salesforce Event Monitoring pending G2, and who can read the log
- Sign-off table: Director of IT and RevOps manager as approvers, CCO for retention and walls, as in stakeholders.md
- engagements/sample-pe/README.md: only the design.md row changes, to a link with status Done; relative links resolve from engagements/sample-pe/

## Review

Brain review: 13 sections, 17-row decisions table each traced to discovery ids and compendium pages; 12 open decisions with owners. Accepted the stricter choices (web tools off org-wide; MNPI only on Claude Code ZDR and hosted ZDR, not Desktop chat). OD-1 stays a recommendation pending Ben.
