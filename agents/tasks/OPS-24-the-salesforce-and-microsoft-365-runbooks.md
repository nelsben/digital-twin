---
id: OPS-24
title: The Salesforce and Microsoft 365 runbooks name the MCP host values, give one setting per real tool, call their checks a pre-check, and describe the move to level 2
domain: ops
tier: standard
tier_reason: Runbook edits in five files with the decisions made in the card
status: merged
issue: 165
scope: [starter-kit/runbooks/salesforce-hosted-mcp.md, starter-kit/runbooks/microsoft-365-connector.md, starter-kit/runbooks/verification-log.md, starter-kit/connectors/salesforce/README.md, starter-kit/plugins/twin-pe-deal-team/skills/drafting-crm-updates/references/level-2-writes.md]
forbid: [starter-kit/settings/**, starter-kit/runbooks/identity-devices-publishing.md, starter-kit/connectors/salesforce/wall-test/**, starter-kit/connectors/salesforce/force-app/**, engagements/**, docs/**, partner-kit/**]
red_test: none
gate: test
budget: 2-attempts
spend: 10
---
## Why

The 2026-11-15 adversarial review found that an admin following the connector runbooks cannot fill the pe-zdr MCP host placeholders, gets two different settings for one Salesforce tool, and can pass the Microsoft 365 wall check with no wall in place. These runbooks are what the generated backlog will send an admin to.

## Done when

- Read the findings first: /Users/bennelsen/Documents/digital-twin/.delegation/reviews/2026-11-15/connectors-runbooks/findings.md section 2, findings 1, 2, 3, 4, 7, 10 and 11. Each names file and line. Findings 5, 6, 8 and 9 belong to other cards: leave them. Every statement an admin acts on carries a row in starter-kit/runbooks/verification-log.md with a source you fetched, or the compendium's exact Unverified marker (docs/compendium/README.md defines it). Invent no host name, tool name or setting.
- Finding 1 (blocker): salesforce-hosted-mcp.md step 4 has one line that names the exact serverUrl value to paste over REPLACE-WITH-SALESFORCE-HOSTED-MCP-HOST in starter-kit/settings/pe-zdr.managed-settings.json, taken from the URL the runbook already gives. microsoft-365-connector.md step 3 has the matching line for REPLACE-WITH-MICROSOFT-365-MCP-HOST: if a source you fetch or the verification log confirms the host, state it with the source; if not, say it is unverified with the marker and tell the admin where in their own tenant or connector entry to read it. Do not edit the settings file or the identity runbook.
- Finding 2: microsoft-365-connector.md section 8b has a setup line that adds user 2 to the Entra app assignment from step 4 for the test, and a control row where user 2 finds a file on their own side, so a pass on 8.2 and 8.3 shows SharePoint permissions and not a missing assignment.
- Finding 3: the step 5 table in salesforce-hosted-mcp.md has one row per real tool (discover, describe, dispatch, dispatch_readonly, display_widget) with one setting each, and no row for a tool that does not exist. dispatch is Blocked at level 1. The text says which tools the wall-test cases WT-05 to WT-16 need. Where Salesforce's 'should be blocked' advice conflicts with what the wall test needs, the runbook says so and names the choice made. The paragraph after the table agrees with the table.
- Finding 4: the closing paragraphs of both runbooks call the 9.x and 8.x checks a pre-check, say the gate before the pilot is engagements/sample-pe/wall-test-protocol.md (as the worked example of the protocol), and link it.
- Finding 7: salesforce-hosted-mcp.md has a section 'Move to level 2' that names the tool that carries updates (dispatch, the only write route), says what Needs approval allows and does not allow, repeats Salesforce's 'should be blocked' advice as a risk the customer accepts in writing, and names the marker check from starter-kit/connectors/salesforce/README.md. level-2-writes.md line 3 names that tool instead of 'the Salesforce update tool'.
- Finding 10: the statements at microsoft-365-connector.md line 178 and connectors/salesforce/README.md lines 22, 62 and 84 each have a verification-log row or the exact Unverified marker. Leave the two identity-runbook statements to the other card.
- Finding 11: the open-items lists at the end of both runbooks include every statement marked Unverified in that runbook, and the dangling reference at microsoft-365-connector.md line 61 points at the paragraph that explains how to revoke a permission.
- python3 -m unittest discover -s tests passes. The report lists, per finding, the file and line changed, each URL fetched with what it confirmed, and every statement left Unverified.

## Review

Brain read the Salesforce runbook diff at fc6c76c. Findings 1, 2, 3, 4, 7, 10 and 11 of the connectors lane are met. The Microsoft 365 MCP host stays Unverified (no fetched source names it); discover and describe are set to Always allow against Salesforce's advice, recorded as a Conflict with the reason. The identity runbook link to the new serverUrl lines belongs to the Team deploy path card (#166).
