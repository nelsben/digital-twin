---
id: SHA-19
title: The sample engagement says what done means for a worked example, and its backlog marks invented-customer actions as illustrative and cites the filed issues
domain: shared
tier: standard
tier_reason: docs edit in two files with a fixed mapping given in the card
effort: low
effort_reason: mechanical edits; every decision is made in the card
status: merged
issue: 81
parent: 23
fixes: [SHA-5]
scope: [engagements/sample-pe/README.md, engagements/sample-pe/backlog.md]
forbid: [starter-kit/settings/**, tests/test_settings.py, starter-kit/runbooks/identity-devices-publishing.md, starter-kit/smoke/**, docs/compendium/README.md, starter-kit/runbooks/salesforce-hosted-mcp.md, starter-kit/runbooks/microsoft-365-connector.md]
red_test: python3 -c "import sys;sys.exit('to file' in open('engagements/sample-pe/backlog.md').read().lower())"
gate: test
budget: 2-attempts
spend: 10
---
## Why

The sample engagement is fictional, but its tracker mixes real kit work with actions only the invented customer could take, such as naming pilot users or signing off a design. Those were reported to the user as things they owed. The backlog also still lists as 'to file' ten items that have been filed. The sample needs a stated finish line and a clear split between real work and illustration.

## Done when

- engagements/sample-pe/README.md gains a section 'What this sample is for, and when it is done', under 20 lines, that says: (1) the sample is a worked example of the playbook, not a live engagement; (2) it is done when every deliverable of phases 1 to 3 in docs/playbook/01-engagement-model.md has a file here or in the starter kit that the table links, the kit parts it uses have passed the smoke test (issue #80), and the wall-test protocol exists with a dry run (issues #30 and #82); (3) actions that only the invented customer could take (naming pilot users, sign-offs, contract checks with Anthropic, due dates, open discovery answers) are illustrative: they show what a real engagement tracks and are never completed in this repo
- The README table is otherwise unchanged; the wall-test-protocol.md row is left exactly as it is (another card updates it)
- In engagements/sample-pe/backlog.md section 2, the 'To file' table becomes 'Filed after the first backlog' with an Issue column and a Kind column, using this mapping: OD-1 plugin review spike = #51, kit work; Salesforce External Client App and per-user OAuth = #52, kit work (runbook); Microsoft 365 tenant consent and SharePoint check = #53, kit work (runbook); 'Last updated by twin' marker field = #54, kit work; F3 examples and T1/T2 evals = #55, kit work (evals written from synthetic fixtures; collecting real examples is a customer action, illustrative); name the 6 pilot users = #57, customer action, illustrative; Okta SCIM groups, Intune settings file and publishing = #56, kit work (runbook); Anthropic contract checks (OD-9) = #58, customer action, illustrative; hosted twin front end = #59, kit work for the Scale phase, not started; HubSpot connector = #60, kit work for the Scale phase, not started
- The sentence above the tables that says items marked 'to file' have no issue yet is rewritten to match, and a two-line key explains Kind: 'kit work' is real work done in this repo; 'customer action, illustrative' is something only the invented customer could do and is never completed here
- Every '(to file)' in the ranked backlog table and in the two Definition of ready tables is replaced by the issue numbers from the mapping. The phrase 'to file' appears nowhere in backlog.md in any letter case
- Section 3 (Pilot users) gains one sentence saying the seats are left unnamed on purpose because naming them is a customer action, illustrative in this sample
- Nothing else in backlog.md changes: ranks, values, story cards, acceptance criteria, targets and the sign-off table stay as they are. No new invented people, companies or figures are added, and the 'fictional customer' notice at the top of each file stays
- Every relative link in the two files resolves to a file that exists on the branch
- The gate passes: python3 -m unittest discover -s tests

## Review

Sonnet, attempt 1, verifier consistent. Brain read the README diff: the new done-when section links the engagement model and the starter kit, and names #80, #30 and #82 as the finish line. In backlog.md, "To file" became "Filed after the first backlog" with Issue and Kind columns for #51-#60, and no "to file" phrase is left. Customer-only actions are marked illustrative. The row order was kept as it was (#57 before #56).
