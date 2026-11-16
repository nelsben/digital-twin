# Engagements

Each customer gets one folder here: `engagements/<customer>/`. It holds the customer's profile, the notes from discovery and the role interviews, and one folder per persona under `personas/<persona-id>/` with the persona card and everything generated from it. The [playbook](../docs/playbook/README.md) says how an engagement runs.

## The samples

| Folder | What it proves |
|---|---|
| [sample-pe/](sample-pe/README.md) | The Enterprise path for a private-equity deal team: Enterprise plan, ZDR, soft walls between teams, managed devices. |
| [sample-team-cs/](sample-team-cs/README.md) | The Team path for a customer-success team: Team plan, unmanaged devices, and what is lost on Team. |

Both are fictional: every company, person and figure in them is invented. A real customer's names and data never go into a `sample-*` folder.

## Starting a real customer folder

1. Create `engagements/<customer>/` and copy [customer-profile.json](../partner-kit/plugins/twin-consultant/templates/customer-profile.json) and [discovery.md](../partner-kit/plugins/twin-consultant/templates/discovery.md) into it. Write the discovery answers in `discovery.md`; the profile and the card cite its rows (`discovery.md#A1`).
2. Create `engagements/<customer>/personas/<persona-id>/` and copy [card.json](../partner-kit/plugins/twin-consultant/templates/card.json) into it, with the interview notes in an `interviews/` folder beside it.
3. Follow the steps in the [twin-consultant plugin README](../partner-kit/plugins/twin-consultant/README.md).

## Regenerating a persona folder

One command validates the card, then writes `levelled.json`, `backlog.json`, `backlog.md` and `dashboard.html` next to it:

```
python3 partner-kit/plugins/twin-consultant/scripts/twincard/cli.py all engagements/<customer>/personas/<persona-id>
```

Add `--date YYYY-MM-DD` to fix the date shown on the dashboard. The stop rule and exit codes are in the [plugin README](../partner-kit/plugins/twin-consultant/README.md#all).
