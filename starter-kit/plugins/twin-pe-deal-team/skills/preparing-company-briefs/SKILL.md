---
name: preparing-company-briefs
description: Prepares a one-page company brief for a deal-team member from the Salesforce deal record and SharePoint deal folder. Use for "company brief for", "one-pager on", "prep a brief on", "brief me on".
---

# Preparing company briefs

## Purpose

An associate asks for a one-page brief on a deal before a management meeting. The skill reads the Salesforce deal record and the SharePoint deal folder and writes the brief as text in the session, with a source link on every fact. The associate spends the meeting prep on questions, not first-pass research, and a reviewer checks the brief before anyone relies on it.

It does not cover: pitch books or IC memo sections, CIM screening, call question lists, CRM updates after a meeting, a pipeline summary, or a plain status question such as "what stage is Elm in?". Those are other tasks.

It builds on Anthropic's `private-equity` and `financial-analysis` plugins in idea only, following [compendium 17](../../../../../docs/compendium/17-anthropic-pe-plugins-review.md): the deal-facts list comes from `deal-screening` and the source ranking and citation rule from `competitive-analysis`. No upstream text is copied and no upstream plugin has to be installed.

## Inputs and connectors

| Source | What it gives | Data class | Access |
|---|---|---|---|
| Salesforce Hosted MCP: `dispatch_readonly` for reads (`discover` and `describe` find the call) | Opportunity: stage, status, stage date, closed reason, contacts, activity history, open diligence tasks | Highly sensitive (MNPI) | read |
| Microsoft 365 connector, SharePoint read tools | Deal folder listing, prior memos, data-room files | Highly sensitive (MNPI) | read |
| Files the user attaches | The same records, when the connectors are not live | Highly sensitive (MNPI) | read |

The tool names are those in step 5 of the [Salesforce Hosted MCP runbook](../../../../runbooks/salesforce-hosted-mcp.md#5-plan-the-tool-permissions-autonomy-level-1). Each tool sits under a server prefix, which is the name the Owner gave the connector in the Claude org (runbook step 6). The skill uses no write tool. **⚠ Unverified:** that `dispatch_readonly` cannot create or update; the runbook keeps the same mark until it is confirmed at setup.

Required from the user: the deal or company name. If it is missing or matches more than one deal, ask which one.

The user's own Salesforce role and SharePoint permissions decide what comes back. That is the point: the skill never widens access.

## Steps

1. **Find the deal.** Search Salesforce for the opportunity and open the deal's SharePoint folder. If both refuse the user (no records, an access error, 403), stop: reply with the no-access reply in [references/output-template.md](references/output-template.md). Do not try another route to the deal, and say nothing about its contents, not even what you would guess from the name. If only one source refuses, brief from the other and say the first was not accessible.
2. **Read what is there.** Opportunity fields, contacts, activity history and open diligence tasks from Salesforce; then every memo and data-room file in the folder listing. Note what is absent as you go.
3. **Take status from the current record.** Stage, status (open or closed), stage date and closed reason come from Salesforce, never from a memo, because memos go stale. If the record is closed, say so first and do not present the deal as live or list open work. If a memo gives an older stage, you may note that the memo is out of date.
4. **Collect the facts the brief needs**, and only those that the files support: what the company does and where it stands, financials (revenue, EBITDA), customer concentration, the three key contacts, open diligence items, the last three interactions. Sort activity by date yourself, since it comes back unsorted, and take the three most recent. Say who supplied a figure and whether it is audited when the file says (for example "management-provided, unaudited").
5. **Check each fact against its source.** When two sources disagree on a figure, do not choose one: show both with their sources under Unverified. A figure the source itself gives no support for, such as a share or a growth rate with no basis, also goes under Unverified, not into the body as fact. Source order when it matters: the current Salesforce record for status and activity; then dated memos and data-room files, with the more recent dated first and management-supplied figures labelled as such.
6. **Write the brief** in the format in [references/output-template.md](references/output-template.md). Put what you could not fill under Not found, in plain words ("no prior memos found in the deal folder"). Leave those sections unfilled; do not write general knowledge about the company or sector into the gap.
7. **Check it** against the list at the end of the template, then present it as text in the session and ask the user where else to look or to add material.

## Output

One page, about 450 words at most, as text in the session. If it runs long, cut detail, never a source link or an Unverified item. The sections and an example are in [references/output-template.md](references/output-template.md).

Source link means a Salesforce record ID (for example `00TEX0000001AA3`) or a SharePoint path. Put it in brackets after the fact it supports.

## Guardrails

- **Draft only; no writes.** The skill makes no Salesforce create, update or delete call and writes no file in SharePoint, OneDrive or on disk. If the user asks you to save the brief or change a record (for example "save it to the deal folder" or "move the stage to Negotiation"), still give the brief with the stage as it stands in the record, say you cannot do that at this autonomy level (draft only), and offer the text for the user to copy and enter themselves. Never say a brief was saved or a record changed. Because nothing is written, there is no twin marker to add.
- **Code names stay as given.** Never expand or guess a deal code name; write it exactly as the source gives it, because a wrong expansion can leak the deal or name the wrong company.
- **No web tools.** Do not use web search or web fetch, and do not quote anything from the web. A query can reveal deal intent, and the deal is MNPI. If the user asks for something the files do not hold (headcount, what the company's website says), list it under Not found, say web sources are not used for deal work, and suggest the user add it from a source they have approved.
- **Ask, do not guess.** Missing, empty or contradictory input is named, not filled. Every fact links to its source; a fact without one is left out or listed as Unverified.
- **No access means no content.** The no-access reply contains no stage, amount, name, activity or file content.
- **Closed means closed.** Never present a closed opportunity as open.

## Reference files

- [references/output-template.md](references/output-template.md): the brief's sections, the no-access reply, and the check list. Open it at steps 1, 6 and 7.

## Evals

The cases in [evals/evals.json](evals/evals.json) and [evals/trigger-evals.json](evals/trigger-evals.json) were written before this skill. Re-run them after every change.
