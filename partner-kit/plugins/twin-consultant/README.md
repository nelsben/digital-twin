# twin-consultant

The consultant plugin for the persona-card workflow. Design of record: [partner-kit/docs/design.md](../../docs/design.md).

**Partner-only.** It is listed only in the partner marketplace, `digital-twin-partner`, and is never installed in a customer org.

## Terms

| Term | Means | Is NOT |
|---|---|---|
| **Persona card** | The JSON record for one role at one customer: `card.json`. Holds what the interviews found and what the consultant decided. | The persona voice file (`starter-kit/templates/persona/persona.md`, the twin's tone and limits). Not a chassis task card in `agents/tasks/`. |
| **Customer profile** | The JSON record for one customer: `customer-profile.json`. Plan, identity, devices, systems, compliance, owners. Shared by all that customer's persona cards. | The discovery questionnaire. The profile stores its answers in machine-readable form and links back to the question ids. |
| **Persona voice** | The existing persona template and its two forms (output style, system prompt). The card feeds it. | The persona card. |
| **Levelling** | Deriving, per task, the runtime, identity, autonomy level and ceiling, data-class controls and plan fit, by rule. | A judgment call. A consultant can override a rule's result, with a reason recorded on the card. |
| **Plan fit** | Whether a component works on Claude Team, Enterprise, or both. | Pricing. |
| **Industry pack** | A JSON file per industry: Anthropic plugins and skills to start from, data-provider connectors, compliance defaults, typical tasks. | A compendium page. The pack links to compendium pages for its facts. |
| **Backlog** | The generated epic → features → stories → tasks for one persona. | This repo's own GitHub issues (the platform build). Keep the two apart. |

## What is here

| Path | What it is |
|---|---|
| [templates/customer-profile.json](templates/customer-profile.json) | Blank customer profile: one per customer, at `engagements/<customer>/customer-profile.json` |
| [templates/card.json](templates/card.json) | Blank persona card: one per role, at `engagements/<customer>/personas/<persona-id>/card.json` |
| [data/fields.json](data/fields.json) | The field catalogue: type, values, required flag, the questions that ask for each field, and what reads it |
| [scripts/twincard/](scripts/twincard/) | Standard-library Python 3.9+: `fields.py` loads the catalogue, `validate.py` checks both records, `cli.py` is the command line |

## Validate

```
python3 partner-kit/plugins/twin-consultant/scripts/twincard/cli.py validate <persona-dir>
python3 partner-kit/plugins/twin-consultant/scripts/twincard/cli.py validate --json <persona-dir>
```

Each error prints as `<record>:<path>: <message>. Next: <fix>`, then a completeness line: the share of required fields whose provenance status is `answered` or `default`. Exit code 0 means no errors, 1 means validation failed, 2 means a usage error or a missing folder.

## Not built yet

Skills (interview to card), the interview guide and notes templates, `level.py`, `backlog.py`, `dashboard.py`, and the `level`, `backlog`, `dashboard` and `all` commands, `rules.json`, `plan-fit.json`, `task-library.json` and the industry packs.
