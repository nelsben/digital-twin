---
id: OPS-72
title: Compendium pages 11 and 15 say what the Microsoft 365 security guide and HubSpot's connector page say about Outlook write limits and audit attribution
domain: ops
tier: standard
tier_reason: two compendium rows against four downloaded pages, every decision made in the card; same shape as OPS-69
effort: high
effort_reason: compendium facts with quotes; a misquote is the failure mode (OPS-69 attempt 1 had two)
status: merged
issue: 250
fixes: [OPS-61]
scope: [docs/compendium/11-connectors.md, docs/compendium/15-governance-and-performance.md, docs/compendium/sources.md, tests/test_compendium_outlook_and_audit.py]
forbid: [starter-kit/**, partner-kit/**, engagements/**, CLAUDE.md, agents/**, docs/compendium/README.md, docs/playbook/**]
red_test: python3 -m unittest tests.test_compendium_outlook_and_audit
gate: test
budget: 3-attempts
spend: 10
---
## Why

The second read of the new runbooks (OPS-70, PR #249) found the compendium behind two vendor pages it already cites. Page 11's Outlook row omits the Always-allow limit and its dates and leaves confirm-before-send unverified when the security guide states it. Page 15 says a twin's changes in a source system look like the user's, while HubSpot's own page and our page 11 say the audit log names both the user and the connector. The compendium holds the defaults every engagement reads, so it must match its sources.

## Done when

- Read first: docs/compendium/README.md (markers: **⚠ Conflict:**, **⚠ Unverified:**, (Our recommendation):, (Our reading):), the OPS-70 sections of starter-kit/runbooks/verification-log.md (the disagreement notes), docs/compendium/11-connectors.md Outlook row (line ~15) and HubSpot row, docs/compendium/15-governance-and-performance.md line ~22 (Source-system audit row), and starter-kit/runbooks/microsoft-365-connector.md section 6a as corrected by OPS-70. Those runbook files are read-only here.
- Method: download each page with curl (user agent 'Mozilla/5.0 (compatible; docs-check)') into a scratch folder, strip tags (and markdown ** and backticks for .md pages), and find every quote you add word for word. A summarising fetch is not evidence. Pages: https://support.claude.com/en/articles/12684923-microsoft-365-connector-security-guide [C], https://support.claude.com/en/articles/12542951-set-up-the-microsoft-365-connector [B], https://claude.com/docs/connectors/microsoft/365.md [A], https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude.
- OUTLOOK ALWAYS-ALLOW. Page 11's Outlook row states, quoting [C]: on Team and Enterprise users cannot choose Always allow for the listed Outlook write tools unless an admin set that tool to Always allow on or after November 9, 2026; the limit does not apply to organizations that added the Microsoft 365 connector for the first time after November 9, 2026; and the December 9, 2026 change to Needs approval for tools an admin has not set, as [C] words it. Each with a link to [C].
- OUTLOOK CONFIRM. The row's Unverified item 'whether Claude asks before each send' is replaced by what [C] says (confirmation before it sends or forwards an email in chat and Cowork, quoted), with the link. If [C] limits it to some surfaces, say which and keep the rest Unverified.
- OUTLOOK WRITE START. Where [B] or [C] answers 'whether write actions start off' (organizations that used the connector before write tools launched have some write tools blocked by default), state that with the quote and keep Unverified only the part neither page answers (a new organization's starting setting per tool).
- CALENDAR READ CONFLICT. 'whether reading calendar events needs write actions' becomes a **⚠ Conflict:** quoting [A] ('find meeting times' listed with write actions) and [C] (find_meeting_availability as a read tool needing Calendars.Read), with the safer reading: test meeting-time search with the write tools blocked.
- ENTRA ROLE. The sentence naming 'a Global Administrator or Application Administrator' is checked against [B] and [C]. If neither page names Application Administrator, mark the disagreement as a **⚠ Conflict:** naming the page that does say it (or (Our reading): if no page does), and give Global Administrator as the safe choice.
- HIPAA NOTE. If [B] or [C] says organizations that enabled HIPAA are not part of the default-block changes, add that one sentence with its quote.
- AUDIT ATTRIBUTION. Page 15's Source-system audit row no longer says changes simply look like the user's. Per system: HubSpot records both the user and the Claude connector (quote the HubSpot page); Salesforce and Microsoft 365 keep the existing wording only where a cited page supports it, otherwise **⚠ Unverified:** for that system. Page 11's HubSpot row and page 15 agree.
- No compendium heading is renamed or removed. docs/compendium/sources.md lists every new URL. No file outside scope changes; the runbooks are not edited.
- Test: a new file tests/test_compendium_outlook_and_audit.py, committed first alone and seen failing through the lease, checks: page 11's Outlook row contains 'November 9, 2026' and 'December 9, 2026' and links 12684923; it no longer marks confirm-before-send Unverified; it carries a Conflict about calendar reads; page 15's audit row no longer contains 'look like the user's' and names the connector for HubSpot; every URL in the two changed rows is in sources.md. The whole suite passes: python3 -m unittest discover -s tests.
- Hand-back lists every sentence added or changed (old -> new) with the exact quote and URL behind it, and every item left Unverified with the reason.
- Test runs: run tests only through `node /Users/bennelsen/WorkflowBridge/bin/wb lease gate-mac --wait 600 -- <command>`; never bypass it or run tests outside it. Keep the red output file under 1 MB. files= lists every file changed since origin/main.

## Review

Verdict consistent, accepted with no reviewer agent (standard tier). The brain downloaded the M365 security guide [C], the set-up article [B] and the docs page [A], and found all 13 added quotes word for word, including the December 9 sentence (whose only difference was tag spacing before a comma) and "show the timestamp, user, operation performed, and resource accessed". The HubSpot quote was already checked in OPS-70. The Entra role is now a Conflict ([A] names Application Administrator, [B] and [C] name only Global Administrator; safer value Global Administrator). Page 15's audit row is per system; Salesforce attribution and M365 connector naming are Unverified. Gate: 841 OK.
