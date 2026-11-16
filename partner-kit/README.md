# Partner kit

Tooling for us, the partner, to run the persona-card workflow: interview notes become a persona card, and the card becomes a build plan for one role twin. The design of record is [docs/design.md](docs/design.md).

**Partner-only.** Nothing here is ever installed in a customer org. It has its own marketplace, `digital-twin-partner` ([.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)), and is never listed in the customer marketplace at the repo root.

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
| [docs/design.md](docs/design.md) | The design of the whole workflow: records, field catalogue, levelling, backlog, dashboard |
| [plugins/twin-consultant/](plugins/twin-consultant/README.md) | The consultant plugin: record templates, the field catalogue and the validator |

## Validate a persona card

```
python3 partner-kit/plugins/twin-consultant/scripts/twincard/cli.py validate <persona-dir>
```

`<persona-dir>` holds `card.json`; the customer profile is read from `../../customer-profile.json`. Add `--json` for the full result. Exit code 0 means no errors, 1 means validation failed, 2 means a usage error or a missing folder.

## Not built yet

The interview guide and the interview-to-card skill; `level`, `backlog`, `dashboard` and `all`; `rules.json`, `plan-fit.json`, `task-library.json` and the industry packs; the fictional fixtures. See [docs/design.md](docs/design.md), sections 3 and 6 to 10.
