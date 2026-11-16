---
id: OPS-13
title: A scratch-org dry run of the wall test runs the protocol's API-level cases as a user on each side, and records the results and whether the twin-marker metadata deploys
domain: ops
tier: standard
tier_reason: Salesforce CLI scripting against a throwaway org; the cases come from the protocol
effort: high
effort_reason: live org work where a wrong target would touch a real org; results must be recorded exactly
status: merged
issue: 82
parent: 29
fixes: []
scope: [starter-kit/connectors/salesforce/wall-test/**, engagements/sample-pe/wall-test-protocol.md]
forbid: []
resources: [sfscratch]
red_test: test -f starter-kit/connectors/salesforce/wall-test/README.md
gate: test
budget: 2-attempts
spend: 10
---
## Why

The live wall test needs a customer org and the hosted connector, which we do not have. A throwaway Salesforce scratch org lets us run the record-access cases now, as a real test user on each side, and gives the kit a reusable setup script. It also checks two things nothing has tested: that the kit's twin-marker metadata deploys, and that the edit-access check the CRM-update skill relies on works.

## Done when

- The worker reads first: engagements/sample-pe/wall-test-protocol.md (the cases marked as dry-runnable at the API level), starter-kit/connectors/salesforce/README.md, and starter-kit/plugins/twin-pe-deal-team/skills/drafting-crm-updates/references/level-2-writes.md
- The only org the worker creates or changes is one new scratch org, created from the Dev Hub alias my-devhub with the alias twin-wall-test, Enterprise edition, duration 3 days. Every sf command that deploys, creates, updates, deletes or queries data names --target-org twin-wall-test or the alias of a test user created inside that scratch org. No command targets the default org or the aliases agent-probe, dev-enttrial, experimental-web or my-devhub, except the single scratch-org create call that names my-devhub as the Dev Hub
- If the scratch org cannot be created (limit reached, auth error, edition not allowed), the worker stops and hands back with the exact error. It does not try another Dev Hub or any other org, and it does not write results it did not observe
- If creation fails for lack of space (active or daily scratch-org limit, or Dev Hub data storage), the worker deletes nothing. It hands back a proposed deletion list for the brain to put to Ben: for each item the org alias, the org type (scratch, Developer Edition or sandbox only, never production), what would be deleted (an expired or unused scratch org, or named records with their object and count), and the space it frees. Read-only commands such as sf org list and sf org list limits are allowed to build the list. Nothing on the list is deleted until Ben approves it in the main session
- starter-kit/connectors/salesforce/wall-test/ holds: a scratch-org definition file; metadata that sets Opportunity sharing to private and defines two roles, Deal Team and Investor Relations, neither above the other in the hierarchy; a small data set with invented records on each side (reuse the kit's invented names such as Project Larch; no real company or person); and one script (Python 3 standard library or POSIX shell, calling the sf CLI) that sets the org up, creates one test user per role, runs the cases, prints a pass or fail table, and deletes the scratch org
- The script runs each API-level case from the protocol as the test user it names, including the control cases, and reports each by the protocol's case id
- The script also deploys the kit's marker metadata from starter-kit/connectors/salesforce/force-app to the scratch org and records whether it deploys cleanly, and runs the UserRecordAccess HasEditAccess query from level-2-writes.md as each test user against a record on each side and records the answers
- If a case fails, the marker metadata does not deploy, or the access query does not behave as the skill assumes, the worker records it in the README and the report with the error text. It changes no file outside its scope to make it pass
- starter-kit/connectors/salesforce/wall-test/README.md says how to run the script and what it needs (a Dev Hub alias passed as an argument, never hard-coded), and has a results table from the worker's own run: date, API version, each case id as pass or fail, the marker deploy result and the access-query result, copied from real output
- The README has a 'What this does not prove' section naming at least: calls were made through the API as each user, not through the Salesforce Hosted MCP connector or Claude; a scratch org's sharing model is not the customer's; SharePoint and HubSpot are not covered
- The scratch org is deleted at the end (sf org delete scratch with no prompt), the worker confirms with sf org list that twin-wall-test is gone, and the report says so. If deletion fails or the permission prompt for it is denied, the report says the org still exists and gives its alias, and the brain deletes it in the main session
- No user name, password, org id, instance URL, access token or auth file is committed. The Dev Hub alias appears nowhere in committed files
- In engagements/sample-pe/wall-test-protocol.md the worker adds at most three lines: a link to starter-kit/connectors/salesforce/wall-test/README.md as the place the dry-run script and results live. It changes nothing else in the protocol
- The gate passes: python3 -m unittest discover -s tests

## Review

Attempt 2/2 consistent, next=accept. Checked by hand: 11 files, 790 insertions, all inside scope; the protocol change is the one link line; the secret grep found no Dev Hub alias, org id, instance URL or token. Results from the real run (2026-11-15, API 68.0): WT-01 to WT-16 pass, ID-D and ID-I pass, and UserRecordAccess HasEditAccess answers as level-2-writes.md assumes. The marker metadata fails to deploy because the Twin_Marker_Edit description is 338 characters against a 255 limit. That is recorded, not fixed, since the file is outside this card's scope; a follow-up is proposed. Opportunity history must be on first, which confirms the marker README. The scratch org is deleted.
