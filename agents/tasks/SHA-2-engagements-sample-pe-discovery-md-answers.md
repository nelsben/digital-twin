---
id: SHA-2
title: engagements/sample-pe/discovery.md answers the full discovery questionnaire for the fictional Example Capital Partners
domain: shared
tier: standard
tier_reason: structured docs from fixed facts and existing playbook pages
effort: low
effort_reason: docs-only, all facts given in the card
status: merged
issue: 25
parent: 24
scope: [engagements/sample-pe/discovery.md, engagements/sample-pe/README.md]
forbid: []
red_test: none
gate: test
budget: 2-attempts
spend: 10
---
## Why

The sample engagement proves the partner playbook end to end; discovery is its first deliverable and every later design decision cites it. It also becomes the worked example new consultants copy for real customers.

## Done when

- engagements/sample-pe/discovery.md answers every question A1-G4 from docs/playbook/02-discovery.md, in the same section order and numbering, as tables with columns: #, Question (short), Answer, Design impact, Status (answered / open), and for open items an Owner (a role from docs/playbook/03-stakeholders.md) and a due date
- engagements/sample-pe/README.md exists: a one-paragraph description of the fictional customer, a banner saying all names, people and figures are invented, and a table linking each engagement file (discovery.md now; stakeholders.md, design.md, wall-test-protocol.md and backlog.md marked 'coming' with their issue numbers #26, #27, #30, #28)
- The customer facts are exactly these (the worker invents nothing that contradicts them): Example Capital Partners, a mid-market private-equity firm, about $4B AUM, 65 staff; first role is the deal team (18 people: partners, principals, associates), pilot of 6; Claude Enterprise with 40 seats, plus 8 people on individual Pro plans bought on the company domain; Okta with SCIM; Microsoft Intune manages all staff laptops, while 5 operating partners and some contractors use unmanaged personal devices; Salesforce Enterprise Edition holds the deal pipeline; HubSpot Marketing Hub Professional holds investor relations and fundraising contacts; documents in SharePoint and OneDrive; Microsoft Teams internally, Slack Connect with some portfolio companies; MNPI is present in deal work; soft walls are required between the deal team and investor relations, enforced through Salesforce and HubSpot role-based access; no PHI today, but one portfolio company is a healthcare services business, so C2 is open for compliance; Splunk is the security log system; no Salesforce-Anthropic integration exists today
- Where our playbook has a default stance (30-day retention for private-equity chat, soft walls via source-system role-based access, Director of IT as technical owner, RevOps manager as business owner, IT owns tooling and spend, the log destination is a customer discussion), the answer states the customer's position and says whether it confirms or changes the default, linking the compendium page
- At least 4 questions are left open with an owner and a date, including C2 (PHI), C3 (acceptance of the ZDR exceptions), E6 (IP allowlisting) and G1/G2 (where the governance log goes, and Salesforce Event Monitoring)
- Section F is answered for the deal team with at least 5 candidate tasks, each with frequency, minutes per task, inputs and systems, output and audience, cost of a mistake, and trigger (person / schedule / event); 'prepare a one-page company brief' and 'update the CRM after a meeting' are two of them
- A closing 'Discovery summary' section lists the 5-8 findings that drive design, each linked to the compendium page that explains the options
- Links to compendium and playbook pages are relative and resolve from engagements/sample-pe/

## Review

Brain review: all A1-G4 answered in playbook order; defaults confirmed or flagged; 7 open items with role owners and dates; summary findings link the right compendium pages. Accepted invented T3-T6 tasks and figures as sample data.
