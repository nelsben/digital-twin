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
| [templates/interview-guide.md](templates/interview-guide.md) | Plain-language role interview: questions P1 to P6 and F1 to F9, each with the card fields it fills |
| [templates/interview-notes.md](templates/interview-notes.md) | Notes template with one slot per question, saved under the persona's `interviews/` folder |
| [data/fields.json](data/fields.json) | The field catalogue: type, values, required flag, the questions that ask for each field, and what reads it |
| [scripts/twincard/](scripts/twincard/) | Standard-library Python 3.9+: `fields.py` loads the catalogue, `validate.py` checks both records, `packs.py` loads and checks industry packs, `level.py` levels a card by rule, `cli.py` is the command line |
| [data/rules.json](data/rules.json) | The levelling rules: each decides one thing, from facts on the card and profile, and cites the compendium section it comes from; the format is in [design section 7.3](../../docs/design.md) |
| [data/plan-fit.json](data/plan-fit.json) | What each capability the twin relies on is on Team, Enterprise and individual plans, and what Team loses, with its compendium cite |
| [data/industry-packs/](data/industry-packs/) | One JSON file per industry; the format is in [design section 7.1](../../docs/design.md) |

## Validate

```
python3 partner-kit/plugins/twin-consultant/scripts/twincard/cli.py validate <persona-dir>
python3 partner-kit/plugins/twin-consultant/scripts/twincard/cli.py validate --json <persona-dir>
```

Each error prints as `<record>:<path>: <message>. Next: <fix>`, then a completeness line: the share of required fields whose provenance status is `answered` or `default`. Exit code 0 means no errors, 1 means validation failed, 2 means a usage error or a missing folder.

## Level

```
python3 partner-kit/plugins/twin-consultant/scripts/twincard/cli.py level <persona-dir>
python3 partner-kit/plugins/twin-consultant/scripts/twincard/cli.py level --json <persona-dir>
```

`level` validates first and levels nothing when there are errors. Otherwise it applies `data/rules.json` and `data/plan-fit.json` to the card, its profile and the profile's industry pack, writes `<persona-dir>/levelled.json` and prints each blocker and warning as `<kind>: <task or persona> <code>: <message> Next: <fix>`. Every decision in `levelled.json` carries its value, the rule that made it, the compendium cite, the reason, whether it rests on an Unverified fact, and whether a card override replaced it. A decision the compendium does not settle is `null`, with a `decision-undecided` warning. Exit code 0 means levelled with no blocker, 1 means validation failed (nothing written) or there is a blocker (the file is still written), 2 means a usage error or a missing folder. The same card and profile always give the same bytes, so a committed `levelled.json` shows in a diff exactly what a change moved.

```python
from twincard import level
level.level(persona_dir)           # {"ok", "validation", "levelled"}; never writes
level.write_levelled(persona_dir)  # the same, and writes levelled.json when validation passes
level.matches(when, facts)         # one rule condition against flat facts; an unknown fact raises LevelError
```

## Industry packs

A customer profile's `industry` is `general` or the id of a pack; `validate` reports anything else. Every entry in a pack cites a compendium page, and carries `unverified: true` where that page marks the fact Unverified or Not confirmed.

| Pack | For |
|---|---|
| [b2b-software](data/industry-packs/b2b-software.json) | A customer-success role at a B2B software company: Anthropic's customer-support plugin and the skills to adapt, HubSpot, Google Drive, Gmail, Google Calendar, Slack, Zendesk and product-usage connector defaults, no settings baseline, and the typical customer-success tasks, from compendium [11](../../../docs/compendium/11-connectors.md), [16](../../../docs/compendium/16-oob-skills-and-references.md) and [18](../../../docs/compendium/18-customer-success.md) |
| [general](data/industry-packs/general.json) | A customer with no pack: Anthropic skills, plugins and references that apply to any role, from [compendium 16](../../../docs/compendium/16-oob-skills-and-references.md) |
| [private-equity](data/industry-packs/private-equity.json) | A private-equity deal team: Anthropic's financial-services plugins and skills, the data vendors they bring, Salesforce and Microsoft 365 connector defaults with their runbooks, compliance defaults, settings baseline `pe-zdr`, and the typical deal-team tasks, from compendium [11](../../../docs/compendium/11-connectors.md), [14](../../../docs/compendium/14-private-equity.md), [16](../../../docs/compendium/16-oob-skills-and-references.md) and [17](../../../docs/compendium/17-anthropic-pe-plugins-review.md) |

The loader is `scripts/twincard/packs.py`:

```python
from twincard import packs
packs.list_packs()          # ["b2b-software", "general", "private-equity"]
packs.load_pack("general")  # the pack; an unknown id raises PackError naming the ids that exist
packs.pack_problems(pack)   # [{"path", "message", "fix"}], empty when the pack is well formed
```

## Not built yet

Skills (interview to card), `backlog.py`, `dashboard.py`, the `backlog`, `dashboard` and `all` commands, and `task-library.json`.
