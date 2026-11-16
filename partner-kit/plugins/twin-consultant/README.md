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
| [scripts/twincard/](scripts/twincard/) | Standard-library Python 3.9+: `fields.py` loads the catalogue, `validate.py` checks both records, `packs.py` loads and checks industry packs, `level.py` levels a card by rule, `backlog.py` builds the backlog from the levelled card, `dashboard.py` renders the dashboard page, `cli.py` is the command line |
| [data/rules.json](data/rules.json) | The levelling rules: each decides one thing, from facts on the card and profile, and cites the compendium section it comes from; the format is in [design section 7.3](../../docs/design.md) |
| [data/plan-fit.json](data/plan-fit.json) | What each capability the twin relies on is on Team, Enterprise and individual plans, and what Team loses, with its compendium cite |
| [data/industry-packs/](data/industry-packs/) | One JSON file per industry; the format is in [design section 7.1](../../docs/design.md) |
| [data/task-library.json](data/task-library.json) | The backlog's task templates: each has an anatomy part, the story it applies to, a `when` condition in the rules language, numbered `how` steps that link the kit template, runbook or compendium page to use, `done_when` and an owner role; the format is in [design section 8](../../docs/design.md#8-backlog-backlogpy-datatask-libraryjson) |
| [skills/](skills/) | The two interview skills: `preparing-role-interviews` and `filling-persona-cards` |
| [scripts/twincard/backlog.py](scripts/twincard/backlog.py) | Builds `backlog.json` and `backlog.md` from `card.json`, `levelled.json` and the task library, keeping each task's status across runs |

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

`level` validates first and levels nothing when there are errors. Otherwise it applies `data/rules.json` and `data/plan-fit.json` to the card, its profile and the profile's industry pack, writes `<persona-dir>/levelled.json`, prints one line per task, then each blocker and warning as `<kind>: <task or persona> <code>: <message> Next: <fix>`. The task line is the task id and its seven decisions, for example `T1: runtime client-skill; identity user; autonomy 1 to 3; settings baseline pe-zdr; memory off; plan fit ok; connectors salesforce read, sharepoint read` (`undecided` for a null autonomy start or ceiling, `none` for no settings baseline). Every decision in `levelled.json` carries its value, the rule that made it, the compendium cite, the reason, whether it rests on an Unverified fact, and whether a card override replaced it. A decision the compendium does not settle is `null`, with a `decision-undecided` warning. Exit code 0 means levelled with no blocker, 1 means validation failed (nothing written) or there is a blocker (the file is still written), 2 means a usage error or a missing folder. The same card and profile always give the same bytes, so a committed `levelled.json` shows in a diff exactly what a change moved.

```python
from twincard import level
level.level(persona_dir)           # {"ok", "validation", "levelled"}; never writes
level.write_levelled(persona_dir)  # the same, and writes levelled.json when validation passes
level.matches(when, facts)         # one rule condition against flat facts; an unknown fact raises LevelError
```

## Backlog

```
python3 partner-kit/plugins/twin-consultant/scripts/twincard/cli.py backlog <persona-dir>
python3 partner-kit/plugins/twin-consultant/scripts/twincard/cli.py backlog --json <persona-dir> --plan-out plan.json
```

`backlog` validates the card, checks that `levelled.json` was made from the current card and profile, then writes `<persona-dir>/backlog.json` and `<persona-dir>/backlog.md`: the epic (the role twin), one feature per card feature plus `F-twin-foundation`, one story per task plus the seven foundation stories, and the tasks `data/task-library.json` gives each story. It prints the epic title, the story and task count per feature and a total line. `--json` prints `backlog.json` instead; `--plan-out FILE` also writes the backlog in the `tree_import` plan shape for a tracker. If `levelled.json` is missing or out of date it writes nothing and says: `levelled.json is missing or out of date. Next: run the level command.`

Both files are generated and never hand-edited. To mark a task, change only its `status` in `backlog.json` to `todo`, `in-progress` or `done`, then run `backlog` again: statuses are kept, story, feature and epic statuses are derived, and `backlog.md` shows the task as `[ ]`, `[~]` or `[x]`. A task the card no longer generates that had been started moves to `retired`, and the command prints one line for it.

Exit code 0 means written with no blocker; 1 means validation failed or `levelled.json` is missing or out of date (nothing written), or levelling reports a blocker (both files are still written, and the blocker gates the stories it is about); 2 means a usage error, a missing folder or an unknown status in `backlog.json` (the message names the task id).

```python
from twincard import backlog
backlog.build(persona_dir)          # {"ok", "validation", "error", "backlog", "retired_now"}; never writes
backlog.write_backlog(persona_dir)  # the same, and writes backlog.json and backlog.md when it builds
backlog.load_library()              # task-library.json, checked; a fault raises BacklogError naming the template
```

## Dashboard

```
python3 partner-kit/plugins/twin-consultant/scripts/twincard/cli.py dashboard <persona-dir> --date 2026-11-15
```

`dashboard` validates the card, checks that `levelled.json` and `backlog.json` exist and were made from the current card, profile and levelled plan, then writes `<persona-dir>/dashboard.html`: one self-contained page with seven sections (header, anatomy grid, feature list, blockers and warnings, backlog, open questions, and where each answer came from). It prints the path written and one line with the completeness, the blocker and warning counts and the backlog tasks done. If an input is missing or out of date it writes nothing and names the file and the command to run next. The page has no JavaScript and makes no external request; cites are text, not links. `--date YYYY-MM-DD` sets the generated date shown on the page (default: today), so the same inputs and the same date give the same bytes.

`dashboard.html` is generated and never hand-edited: change the card or a task's status in `backlog.json`, then run `level`, `backlog` and `dashboard` again. Only a fictional sample, such as the two under `engagements/sample-*`, may be published from this repo; a real customer's page stays with that customer.

Exit code 0 means written with no blocker; 1 means validation failed or `levelled.json` or `backlog.json` is missing or out of date (nothing written), or levelling reports a blocker (the page is still written and shows it); 2 means a usage error, a missing folder, a folder with no `card.json`, or a `--date` that is not a real calendar date.

```python
from twincard import dashboard
dashboard.render(persona_dir, "2026-11-15")           # the page as a string; never writes
dashboard.write_dashboard(persona_dir, "2026-11-15")  # {"ok", "validation", "error", "path", "summary"}; writes when it renders
```

`render` raises `DashboardError` (validation errors, or an input missing or out of date) and `UsageError` (a bad date).

## All

```
python3 partner-kit/plugins/twin-consultant/scripts/twincard/cli.py all <persona-dir> [--date 2026-11-15]
```

`all` runs `validate`, `level`, `backlog` and `dashboard` in that order, by the same functions the single commands call, so a persona folder gets `levelled.json`, `backlog.json`, `backlog.md` and `dashboard.html` from one command. It prints one line per step (the step name, `ok`, `blocked` or `failed`, and the file written) and the per-task lines from `level` once.

- **Stop rule.** It stops only when validation fails: then nothing is written, it prints the validator's `<record>:<path>: <message>. Next: <fix>` lines, names the steps it skipped (level, backlog, dashboard) and exits 1. A levelling blocker does not stop it: all four files are written, so the dashboard shows the blocker, and it exits 1.
- **Exit codes.** 0 only when validation passes and there is no blocker; 1 when validation fails or levelling reports a blocker; 2 for a usage error, a missing folder, a folder with no `card.json`, an unknown status in `backlog.json` or a `--date` that is not a real calendar date.
- **`--date`** goes to the dashboard step only and defaults to today. Run twice with the same date and the same card, it changes no file, and a task's `status` in `backlog.json` is kept.

The two worked examples under [engagements/](../../../engagements/README.md) are checked end to end by `tests/test_twincard_end_to_end.py`: `all --date 2026-11-15` on a copy of each gives the committed files byte for byte.

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

The `planning-a-twin` and `building-twin-stories` skills.
