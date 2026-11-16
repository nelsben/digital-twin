---
name: drafting-crm-updates
description: Drafts the Salesforce activity log and next-step text for an opportunity from meeting notes or a Teams transcript. Use for "update the CRM", "log my meeting", "post-meeting update", "next steps for".
---

# Drafting CRM updates after a meeting

## Purpose

Turns a deal-team member's meeting notes or Teams transcript into draft text for two fields on the Salesforce opportunity: the activity log and the next step. At autonomy level 1 (the default) the twin shows the text and the person pastes it. At level 2 the twin writes it after the person approves.

It does not write emails, minutes, call preparation or pipeline summaries, and it does not change stage, amount or any other field. No upstream Anthropic plugin skill covers this task (compendium 17, section 4), so this skill stands alone.

## Inputs and connectors

| Source | What it gives | Data class | Access |
|---|---|---|---|
| Salesforce Hosted MCP: `dispatch_readonly` for the read of one opportunity (`discover` and `describe` find the call) | Opportunity name, account, stage, owner, latest activity log entry, current next step | Highly sensitive (MNPI) | read |
| Microsoft 365 connector, or a file the user attaches | Meeting notes (OneDrive or SharePoint) or the Teams transcript | Highly sensitive (MNPI) | read |
| Salesforce Hosted MCP: the one tool that writes | Writes the two fields | Highly sensitive (MNPI) | write, level 2 only. See [references/level-2-writes.md](references/level-2-writes.md) |

The tool names are those in step 5 of the [Salesforce Hosted MCP runbook](../../../../runbooks/salesforce-hosted-mcp.md#5-plan-the-tool-permissions-autonomy-level-1). Each tool sits under a server prefix, which is the name the Owner gave the connector in the Claude org (runbook step 6). **⚠ Unverified:** that `dispatch_readonly` cannot create or update; the runbook keeps the same mark until it is confirmed at setup.

Required from the user: which company or opportunity, and the notes or transcript. If either is missing, follow "Guardrails".

## Autonomy level

Work at **level 1 (draft only)** unless the user's role setup says level 2 and the Salesforce update tool is set to Needs approval. A user saying "go ahead and save it" does not raise the level. If the level is not stated, it is level 1.

## Steps

1. **Read the opportunity.** Fetch it with the read tool, or use the export the user attached. If Salesforce returns no record or an access error, stop: say the user has no access to this opportunity, show no field value from it, draft nothing, and suggest asking the deal owner or IT to review the user's access.
2. **Read the notes or transcript.** If the file is empty or no transcript exists, say what is missing, ask for the notes or a transcript, and draft nothing.
3. **Check they match.** The company in the notes must be the company on the opportunity. If not, say both names, ask which opportunity is meant, and draft nothing against either record.
4. **Extract the facts.** Meeting date, attendees (as the notes or transcript name them), topics, decisions, the next step with its action, owner and date. From a transcript, use the last stated version of a changed fact (a date corrected mid-call is the corrected date; give the old date only as the old date). Leave out small talk and filler.
5. **Draft the two fields** in the format below. Every statement comes from the notes or the opportunity. Do not add facts, names, figures or dates from anywhere else.
6. **Handle what is unconfirmed.** A rumour or hint stays out of the draft, or goes in as "unconfirmed" with no name and no figures. Tell the user either way. Never look the other party up.
7. **Present the draft.** At level 1, show the text in the session for the user to paste, and say the twin did not write to Salesforce. Then stop.
8. **At level 2 only:** follow [references/level-2-writes.md](references/level-2-writes.md) for the approval, the edit-access check and the write.

## Output format

```markdown
**Activity log (draft)**
2026-11-12: Management meeting with Larch. Attendees: Robin Placeholder (CEO), Sam Example (CFO), Pat Sample, Dana Example. Topics: Q3 trading; customer concentration; plant capex plan. Decisions: monthly KPI pack from October; management presentation moved from 2026-11-18 to 2026-11-20; rollover left open.

**Next step (draft)**
Send the revised data request list to Sam Example. Owner: Pat Sample. Date: 2026-11-17.

Not written to Salesforce. Paste each into its field.
```

- Date first, in ISO format, then one entry in the shape of the opportunity's latest log entry.
- Name the person, not "we". Keep each draft short enough to read in a few seconds.
- **No next step in the notes:** write "No next step was stated in the notes." Do not invent an action, owner or date, and do not repeat the opportunity's current next step as if it were new. Ask the user whether a next step should be added.
- **No decisions made:** write "Decisions: none." Do not infer one.

## Guardrails

- **Draft only at level 1.** At level 1 make no Salesforce create, update or delete call. Never claim anything was saved. Offer the text to paste.
- **Twin marker on every write.** At level 2, every update call sets `Last_Updated_By_Twin__c` in the same call as the field changes. Never set it on a read, and never write an update without it. Rules: [references/level-2-writes.md](references/level-2-writes.md). At level 1 there are no writes and so no marker.
- **Never write a record the user cannot already edit.** Read access is not enough for a write. If edit access cannot be confirmed, do not write; fall back to level 1 and show the draft.
- **Code names stay as given.** Never expand or guess a deal code name; write it exactly as the source gives it, because a wrong expansion can leak the deal or name the wrong company.
- **No web tools.** Notes from a deal meeting are highly sensitive (MNPI) and a search query can reveal deal intent. Do not use web search or web fetch for any part of this task. If the user asks for outside facts (who another bidder is, what they pay), say web sources are not used for deal work and that the sources name no such party. The user can supply facts themselves.
- **Ask, do not guess.** If an input is missing, empty or contradictory, say exactly what is missing and ask. Do not fill gaps with plausible values.
- **Stay in the two fields.** Do not draft changes to stage, amount, owner or close date. If the notes suggest one, mention it in a line to the user and leave it out of the draft.

## Evals

The cases in [evals/evals.json](evals/evals.json) and [evals/trigger-evals.json](evals/trigger-evals.json) were written before this skill. Re-run them after every change. The fixtures are synthetic; the skill owner replaces them with redacted real examples (see [evals/README.md](evals/README.md)).
