# Sample engagement: Example Software Co (Team plan)

> **All names, people and figures in this folder are invented.** Example Software Co is a fictional customer. Copy the structure for a real customer, not the content.

Example Software Co is an invented B2B software company of 60 people. It runs Claude **Team**, signs in with Google Workspace (no SSO, no SCIM), and has no device management: everyone works on their own laptop. Its customer success team keeps accounts in HubSpot, documents in Google Drive, mail and meetings in Gmail and Google Calendar, talks in Slack, handles tickets in Zendesk, and has an internal product-usage database on a private network. Its data is internal or confidential only: no PHI, no MNPI, no walls.

## What this sample proves

The Team path. The [private-equity sample](../sample-pe/README.md) is Enterprise with ZDR, SCIM and managed devices; this one has none of those. It is the fixture that shows what a twin gets on Team with no device management ([compendium 13](../../docs/compendium/13-devices.md#team-plan-with-no-device-management), [15](../../docs/compendium/15-governance-and-performance.md#team-plan-with-no-device-management)), with the `b2b-software` industry pack and [compendium 18](../../docs/compendium/18-customer-success.md). The persona card is complete; `cli.py validate` prints `Completeness: 100% (104 of 104 required fields answered or default)` and `Valid.`; its expected levelling results are fixed in [tests/fixtures/twincard/expectations.json](../../tests/fixtures/twincard/expectations.json).

Discovery for this customer was a single call with the IT and operations lead. The sponsor, the VP Customer Success, joined the call for section A and stated the six-month goal: each customer success manager spends less time preparing for calls and writing follow-ups, and no renewal is missed for lack of warning. The team is 8 managers, with 4 in the pilot. The answers are in [discovery.md](discovery.md), one row per question id of the [questionnaire](../../docs/playbook/02-discovery.md), and the profile and the card cite its rows (`discovery.md#D1`, `discovery.md#A1`). A short follow-up with the team lead settled three task answers.

| File | What it is | Status |
|---|---|---|
| [discovery.md](discovery.md) | The discovery answers, A1 to G4, all answered | Done |
| [customer-profile.json](customer-profile.json) | The customer profile: plan, identity, devices, compliance, systems, governance | Done |
| [personas/customer-success-manager/card.json](personas/customer-success-manager/card.json) | The persona card: role, voice, three features, five tasks C1 to C5 | Done; validates at 100% |
| [personas/customer-success-manager/interviews/2026-11-06-csm.md](personas/customer-success-manager/interviews/2026-11-06-csm.md) | Interview notes: a customer success manager (C1, C4) | Done |
| [personas/customer-success-manager/interviews/2026-11-07-senior-csm.md](personas/customer-success-manager/interviews/2026-11-07-senior-csm.md) | Interview notes: a senior customer success manager (C2, C3, C5) | Done |
| [personas/customer-success-manager/interviews/2026-11-10-team-lead.md](personas/customer-success-manager/interviews/2026-11-10-team-lead.md) | Follow-up notes: the team lead (C1, C3, C4) | Done |

The four files below are generated from the card; none is written by hand. Regenerate them with:

```
python3 partner-kit/plugins/twin-consultant/scripts/twincard/cli.py all engagements/sample-team-cs/personas/customer-success-manager --date 2026-11-15
```

| File | What it is | Person or command |
|---|---|---|
| [personas/customer-success-manager/levelled.json](personas/customer-success-manager/levelled.json) | The levelled plan: each task's decisions with rule, cite and reason, plus blockers and warnings | Command |
| [personas/customer-success-manager/backlog.json](personas/customer-success-manager/backlog.json) | The generated backlog; a person edits only a task's `status` | Command |
| [personas/customer-success-manager/backlog.md](personas/customer-success-manager/backlog.md) | The same backlog, readable | Command |
| [personas/customer-success-manager/dashboard.html](personas/customer-success-manager/dashboard.html) | One self-contained status page | Command |

The discovery answers, the card and the interview notes above are written by a person. See the [plugin README](../../partner-kit/plugins/twin-consultant/README.md#all) for the command.
