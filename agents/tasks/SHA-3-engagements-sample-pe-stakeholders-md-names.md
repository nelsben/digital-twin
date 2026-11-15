---
id: SHA-3
title: engagements/sample-pe/stakeholders.md names a fictional person for every role and gives the engagement RACI for Example Capital Partners
domain: shared
tier: standard
tier_reason: structured docs from existing playbook and discovery pages
effort: low
effort_reason: docs-only, structure fixed by the playbook
status: merged
issue: 26
parent: 24
scope: [engagements/sample-pe/stakeholders.md, engagements/sample-pe/README.md]
forbid: []
red_test: none
gate: test
budget: 2-attempts
spend: 10
---
## Why

The playbook says to name a person for every customer and partner role in discovery; the sample engagement needs that worked example so later design, backlog and sign-off documents can refer to people by role and name consistently.

## Done when

- Before writing, the worker reads docs/playbook/03-stakeholders.md and engagements/sample-pe/discovery.md, and nothing in stakeholders.md contradicts discovery.md (the sponsor is the COO; the Director of IT is technical owner and Primary Owner; an IT administrator is the backup Owner; the RevOps manager is business owner; Compliance / legal owns C2 and C3; Security owns E6; Source-system admins own G2)
- engagements/sample-pe/stakeholders.md has a customer-roles table with every role from 03-stakeholders.md (executive sponsor, technical owner, backup Owner, business owner, compliance / legal, security, source-system admins (Salesforce, HubSpot, M365 as separate rows), skill owners (at least two deal-team members), pilot users (6, by title only)) with columns: Role, Name (invented), Title, Responsible for in this engagement, Open items owned (from discovery.md)
- Names are obviously fictional, diverse, and use no real public figures; a banner at the top repeats that all names are invented
- A partner-roles table names an invented consultant for each partner role in 03-stakeholders.md
- The RACI table reuses the activity rows and columns from 03-stakeholders.md, and changes a cell only where this customer differs, with each changed cell explained in a note below the table (or a line saying none differ)
- A 'Sign-offs' table lists each phase gate from docs/playbook/01-engagement-model.md (phases 1-6) with who signs for the customer, by name and role
- A 'Communication' section gives a cadence: weekly working session, fortnightly steering with the sponsor, and who attends each
- engagements/sample-pe/README.md: the stakeholders.md row changes from 'coming' to a link, and nothing else in the README changes
- Relative links resolve from engagements/sample-pe/

## Review

Brain review: every playbook role named (fictional), open items match discovery, RACI unchanged with a note, sign-offs per phase. Accepted three skill owners instead of two.
