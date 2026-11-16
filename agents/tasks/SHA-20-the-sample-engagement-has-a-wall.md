---
id: SHA-20
title: The sample engagement has a wall-test protocol with executable test cases, evidence to capture and pass rules
domain: shared
tier: frontier
tier_reason: security test design that gates the pilot; must reason about leak routes and false passes
status: merged
issue: 30
parent: 29
fixes: []
scope: [engagements/sample-pe/wall-test-protocol.md, engagements/sample-pe/README.md]
forbid: []
red_test: test -f engagements/sample-pe/wall-test-protocol.md
gate: test
budget: 2-attempts
spend: 25
---
## Why

The design says no pilot user connects until the wall test passes, but the protocol it points to was never written. It was parked as needing customer access; the protocol itself needs none. Compliance relies on this document to sign the walls, so the cases must cover every leak route the design names and must not be passable by accident.

## Done when

- The worker reads first: engagements/sample-pe/design.md sections 5, 6, 7 and 9; docs/compendium/14-private-equity.md; docs/playbook/04-stories.md (the spike row); engagements/sample-pe/stakeholders.md; the three runbooks in starter-kit/runbooks/; starter-kit/plugins/twin-governance/README.md; and both SKILL.md files in starter-kit/plugins/twin-pe-deal-team/skills/
- engagements/sample-pe/wall-test-protocol.md exists, is under 220 lines, keeps the folder's 'fictional customer' notice at the top, and links to the design and compendium pages instead of copying them
- It follows the five-step outline in design section 7 ('Proof before the pilot') and turns it into numbered test cases in a table. Each case has: an id, the actor (deal-team test user, investor-relations test user, or an Owner), the route, the exact action, the expected result, the evidence to capture, and a pass rule that a reviewer can apply without judgment
- The cases cover at least: reading the other side's opportunity, account, contact and activity through the Salesforce connector; search and list views that could leak a name or a count without opening a record; an aggregate or count query; the other side's SharePoint site, folder, file and search results through the Microsoft 365 connector; HubSpot records, marked 'for the test only' as the design says; asking the twin to brief on or update a deal the user cannot see (the two skills' no-access paths); getting the twin to carry facts across the wall through a Project, memory, a skill or a shared file; a write attempt at autonomy level 1; and what an org Owner can see
- Every blocked-read case has a matching control case in which the same user reads a record on their own side by the same route, so that a connector that returns nothing for everyone is not read as a pass
- A preconditions section covers: the written confirmations from the two system admins (design step 1), the two test users and their roles, synthetic test records on each side with invented names, who creates them, and cleanup after the test
- An evidence section says what is captured for each case from the source system's own audit and from the governance log (which fields; metadata only), and states the log's known limit: it records ids only in the formats the twin-governance README lists, so whether a SharePoint file read leaves an id in the log is marked as to be checked in the test, not assumed
- A results section gives the sign-off rule: all cases pass or the wall is not signed; on any failure the source-system roles are fixed and the whole protocol is run again; and it lists what triggers a re-run later (a change to roles or sharing, a new connector, a skill that gains a write, and a fixed interval the worker proposes)
- A section 'What this test cannot prove' says plainly what a soft wall leaves open (configuration drift after the test, Owner access, facts already in a user's head or local transcript) and links design section 7 'What would move us to a hard wall'
- Each case is marked as either 'can be dry-run at the API level in a scratch org' or 'needs the live connector in the customer's org', because a later card (issue #82) dry-runs the first kind
- Product behaviour the worker cannot confirm from Anthropic's, Salesforce's, HubSpot's or Microsoft's own docs is marked with the compendium's unverified marker, not stated as fact
- Only the invented people in stakeholders.md are named, by the roles the design gives them. No real company, person or data appears
- In engagements/sample-pe/README.md only the wall-test-protocol.md row changes: the file name becomes a link and the status becomes 'Protocol written. Dry run: #82. Live run needs a customer org.'
- The gate passes: python3 -m unittest discover -s tests

## Review

Worker attempts 1-2, then hand fixes by the brain after four refuting reviews (attempts 3-6 are verify passes on brain commits 8a58560, 3c52a91, f10760b, 584720a, 2dfbeaa). Fixed: shared-file carry token seeded so WT-46 cannot pass vacuously (WT-44 plant, WT-44a write attempt); P6 values defined; every cited audit code has a WT-E check; L covers names and counts; write cases must reach the tool or show it Blocked; R defined for non-connector routes; Owner cases need the attempt; shared-identity connections block the run; hosted agents named as untested; WT-E rows are checks, and WT-E1 allows for permission-refused calls. Attempt 6 review: 20 confirmed, 0 refuted, 3 unverifiable (vendor behaviour, all marked in the protocol). Follow-up noted: verify reviews of brain commits carry no claims, so each re-audits the whole card.
