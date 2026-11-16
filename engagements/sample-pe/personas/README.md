# Personas: Example Capital Partners (fictional)

> All names and figures are invented. This folder holds the persona deal-team-associate; the customer profile is [../customer-profile.json](../customer-profile.json).

| Path in `deal-team-associate/` | What it is | Who makes it |
|---|---|---|
| [interviews/](deal-team-associate/interviews/) | Notes from the three deal-team interviews | A person writes it |
| [card.json](deal-team-associate/card.json) | The persona card: role, voice, features, tasks, open questions | A person writes it (Claude fills it from the interviews with the consultant) |
| [levelled.json](deal-team-associate/levelled.json) | The levelled plan: each task's decisions with rule, cite and reason, plus blockers and warnings | A command generates it |
| [backlog.json](deal-team-associate/backlog.json) | The generated backlog: epic, features, stories, tasks and their status | A command generates it; a person edits only a task's `status` |
| [backlog.md](deal-team-associate/backlog.md) | The same backlog, readable | A command generates it |
| [dashboard.html](deal-team-associate/dashboard.html) | One self-contained status page for the persona | A command generates it |

Regenerate the four generated files with:

```
python3 partner-kit/plugins/twin-consultant/scripts/twincard/cli.py all engagements/sample-pe/personas/deal-team-associate --date 2026-11-15
```

The hand-written [backlog.md](../backlog.md) came first and is kept as the worked design record; the generated [backlog.md](deal-team-associate/backlog.md) is what the workflow produces from the card. See the [plugin README](../../../partner-kit/plugins/twin-consultant/README.md#all) for the command.
