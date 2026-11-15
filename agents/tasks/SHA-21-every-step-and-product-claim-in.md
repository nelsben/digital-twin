---
id: SHA-21
title: Every step and product claim in the three runbooks is checked against the vendor's own documentation, corrected where wrong, and logged as confirmed, corrected or unverified
domain: shared
tier: frontier
tier_reason: independent accuracy review of work a weaker model got wrong; needs careful reading of sources against claims
status: merged
issue: 83
parent: 23
fixes: [SHA-8, SHA-9, SHA-11]
scope: [starter-kit/runbooks/**]
forbid: [starter-kit/smoke/**, engagements/sample-pe/README.md, engagements/sample-pe/backlog.md]
red_test: test -f starter-kit/runbooks/verification-log.md
gate: test
budget: 2-attempts
spend: 25
---
## Why

The identity runbook was written by the cheapest model and held two false statements that passed review, so the user asked for the runbooks to be checked for accuracy. A customer's IT director and system admins will follow these documents step by step in real tenants, so a wrong setting name or menu path costs them time or weakens a control. Two earlier cards check the runbooks' statements about this repo; this one checks everything else, by a stronger model that did not write them.

## Done when

- The three runbooks are starter-kit/runbooks/identity-devices-publishing.md, salesforce-hosted-mcp.md and microsoft-365-connector.md. The worker treats each as untrusted: it does not assume a claim is right because it carries a source tag
- For every numbered step, every row of every table and every factual sentence about a product (Claude, Claude Code, claude.ai admin settings, Okta, Intune, Jamf, Kandji, Salesforce, Microsoft 365, SharePoint, Entra), the worker opens the source the runbook cites, or the vendor's own documentation for that feature when none is cited or the citation does not support the claim, and compares the claim with what the page says today
- Sources must be the vendor's own pages: code.claude.com, platform.claude.com, claude.com/docs, support.claude.com or support.anthropic.com for Anthropic; help.salesforce.com, developer.salesforce.com or Salesforce's official GitHub for Salesforce; learn.microsoft.com for Microsoft; help.okta.com or developer.okta.com for Okta. A blog, forum answer or third-party tutorial never confirms a claim
- Each claim ends in one of three states. Confirmed: the vendor page says it; the runbook keeps or gains the link to that page. Corrected: the vendor page says something else; the runbook is changed to match and links the page. Unverified: no vendor page could be read that settles it (for example the page returns 403); the claim carries the compendium's unverified marker (docs/compendium/README.md, Conventions) and is worded as something to confirm at setup, not as fact
- A claim that was marked unverified and that the worker now confirms from a vendor page loses its marker and gains the link. A claim the worker cannot confirm is never promoted to fact, and the worker never fills a gap from memory: what it knows without a page in front of it counts as unverified
- Exact strings get the most care: settings keys, menu paths, role names, permission and scope names, OAuth settings, URLs, IP ranges, file paths, registry keys and CLI commands are each compared character by character with the source
- Statements about files in this repo are checked against the files on the branch too (two earlier cards did this; this is the second pass). In particular the identity runbook must agree with starter-kit/settings/*.json and starter-kit/settings/README.md as they are on the branch
- starter-kit/runbooks/verification-log.md is created. It has one table per runbook with a row per claim checked: the runbook line or step number, the claim in a few words, the state (confirmed, corrected, unverified), the source URL, and for corrections the old and the new wording. The top gives the date of the check, the model that did it, and the counts per state for each runbook
- The log has a short section 'Sources that could not be read' listing every URL that failed and how (403, redirect to login, not found), so a person can check those by hand
- The worker does not restructure the runbooks, add new steps of its own design or change their audience or tone. If a correction shows that a step is missing or the order is wrong, it makes the smallest change that makes the runbook true and notes it in the log
- No real customer name, tenant id, org id or host name is added. Placeholders stay placeholders
- Every relative link in the four files resolves to a file on the branch
- The report gives the counts per state for each runbook and lists the corrections that change what an admin would do, most serious first
- The gate passes: python3 -m unittest discover -s tests

## Review

Opus worker re-checked all three runbooks against the live vendor pages: identity 55 confirmed / 16 corrected / 4 unverified; Salesforce 34/11/12; Microsoft 365 44/8/7. A Sonnet reviewer read the diff: 12 claims confirmed, 0 refuted, 3 unverifiable. The three unverifiable rows are the vendor-page wording, the model and date in the log header, and the Salesforce 403s, none of which can be decided from the tree. Out-of-scope issues it raised for follow-up cards: compendium 11 does not list 153.61.208.0/20; in the settings README, the .env deny rule only covers the current directory, and one row's link label is wrong.
