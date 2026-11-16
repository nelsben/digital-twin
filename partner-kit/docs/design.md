# Persona-card workflow: design

This is the design of record for the persona-card workflow, decided on 2026-11-15. It fixes the records, the field catalogue, the levelling rules, the backlog and the dashboard, so each part of the workflow can be built and checked against one description.

## 1. What we are building

A consultant-driven pipeline, run from Claude, that turns client interviews into a build plan for one role twin:

```
interview notes ──► persona card ──► levelled plan ──► backlog ──► dashboard
  (people talk)     (card.json)     (levelled.json)   (backlog.json,   (dashboard.html)
                                                        backlog.md)
```

- The **interview → card** step is done by Claude with a skill (language work, checked by skill evals).
- Every later step is a **deterministic Python script** (standard library only, Python 3.9+), checked by unit tests. Same card in, same files out.
- The card is the single source of truth. Everything after it is a rendering and can be regenerated.

Design changes after 2026-11-15 are made in this file, in the same pull request as the code they describe.

## 2. Words (these collide with existing terms; use them exactly)

| Term | Means | Is NOT |
|---|---|---|
| **Persona card** | The JSON record for one role at one customer: `card.json`. Holds what the interviews found and what the consultant decided. | The persona voice file (`starter-kit/templates/persona/persona.md`, the twin's tone and limits). Not a chassis task card in `agents/tasks/`. |
| **Customer profile** | The JSON record for one customer: `customer-profile.json`. Plan, identity, devices, systems, compliance, owners. Shared by all that customer's persona cards. | The discovery questionnaire. The profile stores its answers in machine-readable form and links back to the question ids. |
| **Persona voice** | The existing persona template and its two forms (output style, system prompt). The card feeds it. | The persona card. |
| **Levelling** | Deriving, per task, the runtime, identity, autonomy level and ceiling, data-class controls and plan fit, by rule. | A judgment call. A consultant can override a rule's result, with a reason recorded on the card. |
| **Plan fit** | Whether a component works on Claude Team, Enterprise, or both. | Pricing. |
| **Industry pack** | A JSON file per industry: Anthropic plugins and skills to start from, data-provider connectors, compliance defaults, typical tasks. | A compendium page. The pack links to compendium pages for its facts. |
| **Backlog** | The generated epic → features → stories → tasks for one persona. | This repo's own GitHub issues (the platform build). Keep the two apart. |

## 3. Where things live

Consultant tooling is **partner-only**. It never goes into the customer marketplace (`.claude-plugin/marketplace.json`, name `digital-twin-kit`), and `tests/test_kit_structure.py::test_no_orphan_plugins` requires every folder under `starter-kit/plugins/` to be listed there. So it lives outside `starter-kit/`:

```
partner-kit/
  README.md
  .claude-plugin/marketplace.json          # name: digital-twin-partner; lists twin-consultant only
  plugins/twin-consultant/
    .claude-plugin/plugin.json
    README.md
    skills/<skill-name>/SKILL.md (+ evals/, references/)
    scripts/                               # twincard package: one module per pipeline step
      twincard/__init__.py
      twincard/fields.py      validate.py   level.py   backlog.py   dashboard.py   cli.py
    data/
      fields.json                          # the field catalogue (section 5)
      rules.json                           # levelling rules (section 7)
      plan-fit.json                        # Team vs Enterprise per capability
      task-library.json                    # implementation task templates per anatomy part (section 8)
      industry-packs/<industry>.json
    templates/
      card.json  customer-profile.json  discovery.md  interview-guide.md  interview-notes.md
```

A plugin is copied to a cache when installed, so **everything the scripts read sits inside the plugin folder**. Scripts find data relative to their own file, never by repo path.

Per customer, in the engagement folder:

```
engagements/<customer>/
  customer-profile.json
  discovery.md                             # the discovery answers, one table row per question id (from templates/discovery.md)
  personas/<persona-id>/
    interviews/<yyyy-mm-dd>-<who>.md       # notes or transcript
    card.json
    levelled.json   backlog.json   backlog.md   dashboard.html     # generated; never hand-edited
```

CLI (one entry point, run from anywhere):

```
python3 partner-kit/plugins/twin-consultant/scripts/twincard/cli.py validate  <persona-dir>
python3 .../cli.py level     <persona-dir>     # writes levelled.json
python3 .../cli.py level     <persona-dir> --json   # also prints levelled.json (or the refusal) as one JSON document
python3 .../cli.py backlog   <persona-dir>     # writes backlog.json, backlog.md
python3 .../cli.py backlog   <persona-dir> --json --plan-out plan.json   # also prints backlog.json and writes the tracker plan
python3 .../cli.py dashboard <persona-dir> [--date YYYY-MM-DD]   # writes dashboard.html; the date shown defaults to today
python3 .../cli.py all       <persona-dir>     # the four in order; stops only when validation fails; a levelling blocker still writes every file and exits 1
```

`<persona-dir>` holds `card.json`; the customer profile is found at `../../customer-profile.json`. Exit code 0 on success; 1 when validation fails (`level`, `backlog` and `dashboard` then write nothing), when `levelled.json` is missing or out of date (`backlog` and `dashboard` write nothing and say to run `level`; sections 8 and 9 say how "out of date" is decided), when `backlog.json` is missing or out of date (`dashboard` writes nothing and says to run `backlog`), or when levelling reports a blocker (`level` still writes `levelled.json`, `backlog` still writes both backlog files and `dashboard` still writes the page, so the blocker can be read); 2 on a usage error, a missing persona folder (for `level`, `backlog`, `dashboard` and `all`, a folder with no `card.json`), an output that cannot be written (checked for every file the command writes, `--plan-out` included, before anything is written), a kit data file that is missing, is not JSON or is not in its shape (`rules.json`, `plan-fit.json`, `task-library.json`, `fields.json`, an industry pack), a `backlog.json` that is not JSON or not in its shape, an unknown status in `backlog.json` (`backlog` and `dashboard` give the same message), or a `--date` that is not a real calendar date. Validation errors name the field path and end `Next: <fix>`. A usage error or refusal is one line on stderr, naming the file at fault and ending `Next: <what to do>`, never a traceback. `level` validates first. With `--json`, `level` and `backlog` print exactly one JSON document on stdout: `levelled.json` or `backlog.json` on success, and on a refusal (validation errors, a stale `levelled.json`, a data-file fault) `validate`'s result with `ok: false` and an `error` line added (`errors` is empty when validation passed); human-readable lines such as `Blocked:` go to stderr.

## 4. The two records

Both are JSON, because the repo's tools are standard-library Python (no YAML parser) and Claude fills them in, not a person typing.

### 4.1 Customer profile (`customer-profile.json`)

```json
{
  "profile_version": 1,
  "customer": "example-capital-partners",
  "display_name": "Example Capital Partners",
  "fictional": true,
  "industry": "private-equity",
  "plan": {"tier": "enterprise", "seats": 40, "individual_accounts_on_domain": 8},
  "identity": {"idp": "okta", "sso": true, "scim": true},
  "devices": {"mdm": "intune", "managed_share": "all staff", "unmanaged_users": "5 operating partners, some contractors"},
  "compliance": {
    "data_classes": ["internal", "confidential", "highly-sensitive"],
    "phi": false, "baa": false, "mnpi": true,
    "retention": "zdr", "zdr_cover": "in-place", "walls": "soft"
  },
  "systems": [
    {"id": "salesforce", "kind": "crm", "product": "Salesforce", "edition": "Enterprise", "access_model": "roles and sharing rules", "private_network": false}
  ],
  "network": {"can_allowlist_anthropic_ips": null},
  "runtime_preferences": {"self_hosting_required": false},
  "governance": {"log_destination": "open", "existing_source_audit": "", "spend_owner": "", "spend_limits": "", "action_log_required": true},
  "owners": {"sponsor": "", "technical_owner": "", "business_owner": "", "backup_owner": "", "compliance": ""},
  "provenance": {}
}
```

- `plan.tier`: `team` or `enterprise` (`individual` is accepted and always fails plan fit: compendium 09 makes Team the minimum).
- `industry`: the id of an industry pack, or `general`.
- `compliance.retention`: `standard`, `custom-30-day`, `zdr`.
- `compliance.zdr_cover`: `in-place` (a ZDR agreement covers the org or workspace the highly sensitive work will run in today), `planned` (the customer intends to get one and it is not signed) or `none` (the customer has none and does not plan one). Required, asked by discovery C3, and recorded as the customer says it even when the plan cannot have ZDR. It is the customer's answer about the agreement; `compliance.retention` is the retention the twin is set up with.
- `compliance.walls`: `none`, `soft`, `hard`.
- `systems[].kind`: `crm`, `documents`, `messaging`, `ticketing`, `email-calendar`, `finance`, `product-data`, `data-provider`, `other`.
- `fictional: true` is required for anything under `engagements/sample-*`.
- `network.can_allowlist_anthropic_ips`: `true` or `false`; `null` while its provenance is `open`.
- `runtime_preferences.self_hosting_required`: `true` when the customer wants event-driven work run on its own infrastructure even without ZDR or HIPAA (the "full control" branch of the compendium 05 decision flow). Not required; the default is `false`.
- `governance.action_log_required`: `true` when the customer needs an audit log of the twin's actions. Required: it decides whether confidential data can stay on Team ("Team acceptable with a lower audit need", compendium 10) and which data controls apply.

### 4.2 Persona card (`card.json`)

```json
{
  "card_version": 1,
  "id": "deal-team-associate",
  "customer": "example-capital-partners",
  "role": {
    "name": "Deal-team associate",
    "team": "Deal team",
    "headcount": 18, "pilot_users": 6,
    "works_in": ["claude-code", "desktop"],
    "wanted_surfaces": [],
    "device": "managed"
  },
  "outcome": {"sponsor_goal": "", "scorecard_targets": [{"metric": "edit_rate_below_pct", "value": 30}]},
  "voice": {
    "serves": "", "jobs": [], "tone": "", "norms": [], "never": [], "ask_before": [], "escalate_to": []
  },
  "features": [
    {"id": "pre-meeting-prep", "name": "Pre-meeting preparation", "why": ""}
  ],
  "tasks": [
    {
      "id": "T1", "feature": "pre-meeting-prep",
      "name": "Prepare a one-page company brief before a management meeting",
      "frequency_per_week": 4, "minutes_each": 90, "users": 3,
      "trigger": "person",
      "inputs": [{"system": "salesforce", "objects": "opportunity, account", "access": "read"}],
      "output": {"what": "One-page brief", "audience": "internal", "destination": "none"},
      "writes": [],
      "data_class": "highly-sensitive",
      "cost_of_mistake": {"level": "medium", "what_happens": ""},
      "reversible": true,
      "touches_money": false,
      "reads_untrusted_input": false,
      "examples": {"good": 2, "bad": 1, "where": ""},
      "constraints": ["A reviewer checks every brief before it goes further."],
      "wanted_change": "",
      "story_want": "", "story_benefit": "",
      "skill_owner": "",
      "priority": 1,
      "in_pilot": true
    }
  ],
  "memory": {"personal_memory_wanted": false, "notes": ""},
  "overrides": [
    {"task": "T1", "decision": "autonomy.start", "value": 1, "reason": "", "approved_by": ""}
  ],
  "open_questions": [
    {"id": "OQ-1", "question": "", "blocks": ["T1"], "owner": "", "due": "2026-12-04"}
  ],
  "provenance": {
    "tasks.T1.frequency_per_week": {"status": "answered", "source": "interviews/2026-11-14-associate-a.md#F1"}
  }
}
```

Enumerations:

- `role.works_in[]`: `claude-ai`, `desktop`, `claude-code`, `cowork`, `slack`, `teams`.
- `role.wanted_surfaces[]` (optional): the same values; where the interviewees said they would rather work (interview P1). It is a wish shown on the dashboard, not a plan: levelling never reads it.
- `tasks[].constraints[]` (optional): the rules or deadlines the task must always keep, one rule per item, in the interviewee's words (interview F4 and F7). Nothing is inferred.
- `tasks[].wanted_change` (optional): what the interviewee would change about how the task is done today, in their words (interview F3 and F5). It is asked for, not planned.
- `tasks[].story_want` and `tasks[].story_benefit` (optional): the two halves of the story statement (section 8), in the interviewee's words and in the first person of the role: what they want the twin to do (`brief me on the account before each call`, interview F1) and what that gives them (`I walk into the call already knowing the account`, F1 or F3). Both are empty when the notes do not say why; the kit never invents a benefit. Neither changes levelling or counts toward completeness.
- `tasks[].starts_from` (optional, default `[]`): the Anthropic skills or plugins the task's skill is built from, each the `name` of an `anthropic_starting_points` entry ([7.1](#71-industry-packs-dataindustry-packsidjson-packspy)) of the customer's industry pack or of the general pack whose `use` is `start-from` or `reuse`. The customer's pack is looked in first, so its entry wins when both packs have the name. The consultant sets it when filling the card, from the pack's suggestion for a matching typical task, and only when the consultant agrees; no interview question asks it. `validate` rejects a name that is in neither pack, or whose entry is a `reference` (read, not built from), with one line: `card:tasks.<id>.starts_from: task <id> starts from '<name>', which is not a starting point in the <pack> pack or the general pack. Next: use a name from the pack's starting points, or remove it.` It never changes a levelling decision and never counts toward completeness; the backlog reads it (section 8).
- `role.device`: `managed`, `unmanaged`, `mixed`.
- `role.plugin_name` (optional): the role plugin is named `twin-<role>` ([role-plugin template](../../starter-kit/templates/role-plugin/README.md#steps)). When `role.plugin_name` is empty, the levelling engine uses the persona id as the role, which is a decision of this design. When it is given it must match `^twin-[a-z0-9-]+$` (the levelling engine checks the pattern; the validator treats it as a string).
- `tasks[].trigger`: `person`, `schedule-own` (one person's recurring task), `schedule-team` (shared, lives in a channel), `event` (a system event or webhook).
- `tasks[].inputs[].system` and `tasks[].writes[].system`: system ids from the customer profile. A system the profile does not list is a validation error.
- `tasks[].inputs[]`: `{"system": "<profile system id>", "objects": "account", "access": "read"}`; `access` is `read` or `write`.
- `tasks[].writes[]`: `{"system": "<profile system id>", "objects": "opportunity", "action": "update"}`; `action` is `create`, `update`, `delete` or `send`.
- `inputs[]` and `writes[]` are positional lists with no key, like `overrides[]`: a task may read or write one system several times (update an opportunity and create a task in the same CRM). Their paths use the position: `tasks.T1.writes[0].action`, `tasks.T1.inputs[1].access`. An exact duplicate entry (the same system, objects and action, or the same system, objects and access) is a warning, not an error.
- `tasks[].output.audience`: `self`, `internal`, `other-team`, `external` (customers, investors, anyone outside the company).
- `tasks[].data_class`: `internal`, `confidential`, `highly-sensitive`, `phi`.
- `tasks[].cost_of_mistake.level`: `low`, `medium`, `high`.

### 4.3 Provenance and completeness

`provenance` maps a field path to `{"status", "source", "owner"?, "due"?}`.

- `status`: `answered` (a person said it; `source` points at the interview notes and question id, or at the discovery row), `default` (taken from a named default; `source` is the compendium page or pack that sets it), `assumed` (the consultant's working guess; needs an `owner` to confirm), `open` (no answer yet; needs `owner` and `due`; **the field is empty**: null, `""` or `[]`, and `false` counts as a value). A working guess is never open: it is `assumed`, with an owner.
- `source` is one source, or several separated by `; ` when more than one person gave the answer (`interviews/2026-11-06-csm.md#P2; interviews/2026-11-07-senior-csm.md#P2`). Each source is `<file>` or `<file>#<anchor>`. The file is looked up in the record's own folder (the persona folder for the card, the customer folder for the profile), then in the customer folder, and never outside the customer folder: a source with `..` or an absolute path is an error. So both records cite `discovery.md#A1`, and the card cites `interviews/<date>-<who>.md#F2`.
- `validate` opens every source of an `answered` entry. `default`, `assumed` and `open` entries are not opened.
  - A file under `interviews/` needs a question-id anchor and a heading line `## <id>.` to `###### <id>.` for it. For a `tasks.<id>.*` path the heading must sit inside that task's block, which runs from its `Task id: <id>` line to the next `Task id:` line or level-2 heading.
  - `discovery.md` needs a question-id anchor and a table row whose first cell is that id.
  - Any other file must exist, and an anchor, when given, must equal the GitHub slug of one of its headings (`stakeholders.md#customer-roles`).
  - A source that does not open is an error, one per source: `<record>:<path>: source <source> does not open: it <what is wrong>. Next: Point the source at the notes or discovery line that holds the answer, or set the status to assumed with an owner`.
- An `open` entry whose field holds a value is an error: `<record>:<path>: is open but holds the value <value>; an open field is empty. Next: Empty the value, or set the status to assumed with an owner if the value is your working guess`.
- Paths use ids, not array positions: `tasks.T1.minutes_each`, `voice.tone`, `systems.salesforce.edition`. Lists with no key (`inputs[]`, `writes[]`, `overrides[]`) use the position: `tasks.T1.writes[0].action`.
- A required field with no provenance entry is a validation error. This is what makes "every field traces to a source" checkable.
- **Required in the pilot.** A catalogue entry may carry `required_when` ([5](#5-field-catalogue-datafieldsjson)); the one condition is `{"in_pilot": true}`, on a `tasks[]` field. `tasks[].skill_owner`, `tasks[].examples.good` and `tasks[].examples.bad` carry it: for a task with `in_pilot` true they count as required, exactly as other required fields do (a provenance entry, and an empty value only when the entry is `open` with an owner and a due date, or `assumed` with an owner), and a missing answer lowers completeness until it is answered. An answered count of 0 is a value. For a task not in the pilot nothing changes.
- **Completeness** = required fields whose status is `answered` or `default`, over all required fields, as a percentage. `assumed` and `open` count against it.
- A card is **complete** when: validation passes, completeness is 100%, no open question blocks an in-pilot task, and levelling reports no blocker. So a card is Complete only when every pilot task names its skill owner and says how many examples exist. This is separate from a story's `examples` ready check (section 8), which asks for at least 3 examples before the skill is built: a pilot task with an answered count of 1 makes the card complete but its story not ready.

## 5. Field catalogue (`data/fields.json`)

One entry per field of both records:

```json
{"path": "tasks[].trigger", "record": "card", "type": "enum", "values": ["person","schedule-own","schedule-team","event"],
 "required": true, "key": false, "asked_by": ["F5"], "default": null,
 "feeds": ["rule:runtime", "backlog:story.surface"], "part": "A4"}
```

- `required`: true when a levelling decision (section 7) or the persona voice needs the field. A required field needs a provenance entry and counts in completeness, except for a path in the catalogue's `no_provenance` list (an override's `reason` and `approved_by`): it is recorded with the entry it belongs to, needs no provenance, is left out of completeness, and, when required, must be a non-empty string (whitespace only is empty).
- `key`: true for a field that names or links an entry rather than answering a question: the record ids (`id` and `customer` on the card, `customer` on the profile), the list keys (`systems[].id`, `features[].id`, `tasks[].id`, `open_questions[].id`, `outcome.scorecard_targets[].metric`) and the references (`tasks[].feature`, `tasks[].inputs[].system`, `tasks[].writes[].system`, `overrides[].task`, `open_questions[].blocks`). **A key field is always structurally required, carries no provenance and is left out of completeness**, so its `required` flag is false. A missing key is a validation error.
- `required_when` (optional): `{"in_pilot": true}` on a card `tasks[]` field, which makes the field required for a task in the pilot ([4.3](#43-provenance-and-completeness)). `fields.py` refuses any other condition, and the condition on any other path, naming the entry.
- `default`: `null`, or `{"value": ..., "source": "<compendium or playbook page>"}`.
- `asked_by`: discovery question ids (A1 to G4 in `docs/playbook/02-discovery.md`) or interview-guide question ids (section 6). Every field has at least one, or a `default` with a source link.
- `feeds`: the levelling rules, backlog generators or dashboard panels that read it. **Every field has at least one.** A field nothing reads is deleted.
- `feeds` vocabulary: `rule:<decision>` with decision one of `runtime`, `identity`, `autonomy`, `data_controls`, `connectors`, `memory`, `plan_fit`; `backlog:<level>` with level one of `epic`, `feature`, `story`, `task`; `dashboard:<section>` with section one of `header`, `anatomy`, `features`, `blockers`, `backlog`, `open_questions`, `provenance`; and `voice` (the persona voice file).
- `part`: the anatomy part it belongs to (A1 persona, A2 skills, A3 connectors, A4 runtime, A5 identity, A6 memory, A7 guardrails, A8 evaluation, A9 distribution and governance) or `context`.
- Tests enforce both rules and that the templates, the validator and the catalogue agree.

Rules `validate` applies to both records beyond the entries:

- **Unknown keys.** A top-level key that is neither an envelope key nor the first segment of a catalogue path is an error that names the closest known key (`card:taks: is not a field of card.json; the closest known key is tasks`).
- **Versions.** `card_version` and `profile_version` must be the integer in `record_versions`; `true` and `1.0` are errors. Adding fields does not change a version: OPS-53 added `compliance.zdr_cover`, `role.wanted_surfaces`, `tasks[].constraints` and `tasks[].wanted_change`, and OPS-56 added `tasks[].story_want` and `tasks[].story_benefit`; the record versions stay 1, and no migration is written (a record without `compliance.zdr_cover` fails validation until the field is filled in).
- **Numbers.** An `integer` or `number` field must be finite and not negative, unless the catalogue's `lower_bounds` gives the field (`record:path`) another least value.
- **Tasks.** A card needs a `tasks` list with at least one task: a missing, non-list or empty `tasks` is the error `card:tasks: a card needs at least one task`.
- **Overrides.** Each `overrides[].value` must fit its decision's vocabulary in the catalogue's `override_values`, the 7.2 values, matched exactly: `runtime` one of the seven runtimes; `identity` `user`, `service-account` or `api-key-vault`; `autonomy.start` and `autonomy.ceiling` an integer from 0 to 4 (a boolean is not an integer); `memory` `on` or `off`; `data_controls` an object with at least one of `settings_baseline` (`general`, `confidential`, `pe-zdr`, `hipaa` or `null`), `web_tools` (`on` or `off`), `surfaces` (a list of `role.works_in` values) and `retention` (a `compliance.retention` value). The error is at `overrides[<i>].value` (or `.value.<part>`) and lists the allowed values. `reason` and `approved_by` are required non-empty strings. The same task and decision overridden twice is an error naming both positions. An override of `connectors` or `plan_fit`, or of a decision levelling does not have, still validates; levelling reports it (7.3).

## 6. Interview guide

Client-facing: a consultant reads it to a role holder. Plain language, no Claude jargon. Question ids continue the discovery questionnaire's section F (F1 to F5 exist) with a `P` section for the persona itself:

- `P1`–`P6`: the role, who they serve, what a good week looks like, tone they expect, things the twin must never do, who they escalate to.
- `F1`–`F5` as in discovery, asked per task, extended with `F6` (who else sees or changes the output), `F7` (can it be undone; does it touch money), `F8` (does it read things written by outsiders: customer email, tickets, web pages), `F9` (would you want it to remember anything between sessions).
- A closing section turns tasks into a feature list: group tasks under a capability the role holder names.

A question may carry one **Also ask** line, a prompt read with it that collects a field the main question does not: F3 asks what the role holder would change about the task today (`tasks[].wanted_change`, with F5), F4 asks for a rule or deadline the task must always keep (`tasks[].constraints`, with F7), and F1 asks what the role holder would do with the time a task gives back, or what gets better (`tasks[].story_benefit`, with F3; the F1 answer also gives `tasks[].story_want`). P1 also fills `role.wanted_surfaces`.

Every question lists the card field paths it fills. Every required card field in parts A1–A8 is reachable from a question or a default.

## 7. Levelling (`data/rules.json`, `level.py`)

Rules are data, not if-statements buried in code: `{"id", "decides", "when", "then", "cite", "unverified", "basis", "reason"}`, plus `fix` on a blocker or warning rule. `cite` is a compendium page path with an anchor that matches a heading on that page. `unverified: true` when the cited section marks the underlying fact ⚠ Unverified or ⚠ Conflict; it is carried into `levelled.json`, the backlog and the dashboard so nobody builds on an unconfirmed fact unknowingly. `basis` is `compendium` when the page states the result, or `our-recommendation` when the page gives the facts and the rule is our reading of them. The format is in 7.3.

What it decides, per task:

| Decision | From | Source page |
|---|---|---|
| `runtime` (client skill, Claude Code scheduled task, Claude Tag routine, Managed Agents, Agent SDK) | `trigger`, `data_class`, `role.works_in` | compendium 05 decision flow |
| `identity` (the user, a service account, API key plus vault) | `runtime` | compendium 05 |
| `autonomy.start` and `autonomy.ceiling` (0–4) | start is 1 for every pilot task; ceiling from `audience`, `reversible`, `touches_money`, `cost_of_mistake`, `trigger` | compendium 06 |
| `data_controls` (settings baseline file, web tools on or off, surfaces allowed, retention) | `data_class`, profile `compliance` | compendium 10, 14; `starter-kit/settings/` |
| `connectors[]` (per system: how it is added, identity, read or write, per-tool permission) | `inputs`, `writes`, profile `systems`, industry pack | compendium 11 |
| `memory` | `memory`, `reads_untrusted_input`, `data_class` | compendium 02 |
| `plan_fit` (`ok`, `ok-with-limits`, `needs-enterprise`, `not-supported`), with the reason | all of the above against `plan-fit.json` | compendium 09 |

Per persona: the plugin name (`role.plugin_name`, else `twin-<persona-id>`), how it is distributed on this plan (group-targeted on Enterprise; to everyone on Team; installed by hand on a plan that cannot publish plugins), the settings baseline, the Anthropic plugins to start from (industry pack), and a list of **blockers** (a task that cannot be built as asked on this plan or data class) and **warnings**. A blocker rests only on a settled fact, so where the compendium marks the fact ⚠ Conflict, as page 11 does for Gmail and Google Calendar write access, the rule raises a warning (`mail-write-unconfirmed`) instead of a blocker.

Overrides on the card replace a rule's result and are shown as overridden, with the reason, everywhere.

### 7.1 Industry packs (`data/industry-packs/<id>.json`, `packs.py`)

A pack is the machine-readable form of what the compendium says about one industry. Levelling and the backlog read it; it links to compendium pages for its facts and never states an unconfirmed fact as settled. The profile's `industry` is `general` or the id of a pack, and the validator reports anything else. `general.json` is for a customer with no pack: starting points that apply to any role, the connector defaults that apply to any industry, and empty lists where nothing general applies.

Top level, `pack_version` 1:

```json
{
  "pack_version": 1,
  "id": "private-equity",
  "name": "Private equity",
  "summary": "One sentence.",
  "sources": ["docs/compendium/14-private-equity.md"],
  "settings_baseline": "pe-zdr",
  "anthropic_starting_points": [], "data_providers": [], "connector_defaults": [],
  "compliance_defaults": [], "typical_tasks": []
}
```

- `id` equals the file name without `.json`. `sources` lists repo-relative compendium pages. `settings_baseline` is the name of a baseline in `starter-kit/settings/` without `.managed-settings.json`, or `null`.
- `anthropic_starting_points[]`: `{kind, name, where, use, note}`. `kind` is `plugin`, `skill`, `agent-template` or `reference`; `where` is a URL or a marketplace name; `use` is `start-from`, `reuse` or `reference`.
- `data_providers[]`: `{name, kind, access, note}`. `access` is `connector`, `mcp`, `api` or `none`. A provider listed here is not thereby allowed; the note says whether it is.
- `connector_defaults[]`: `{system_kind, product, how, identity, runbook}`. `system_kind` is a value of `systems[].kind` in the catalogue; `runbook` is a path under `starter-kit/runbooks/`, or `null`.
- `compliance_defaults[]`: `{field, value, reason}`. `field` is a customer-profile path in `data/fields.json` and `value` has that field's catalogue type. A default is a starting answer: the profile's provenance for it is `default` until the customer confirms or overrides it.
- `typical_tasks[]`: `{id, name, feature, trigger, data_class, inputs}`, and optionally `starts_from`. `trigger` and `data_class` use the catalogue's values for `tasks[].trigger` and `tasks[].data_class`; `inputs` is a list of system kinds. `starts_from` is the pack's suggestion for a card task that matches the typical task: names held to the card's rule ([4.2](#42-persona-card-cardjson)), checked by `pack_problems` at `typical_tasks[<i>].starts_from[<j>]`. A pack suggests a name only where the page it cites names that skill for that job: private-equity T4 `deal-screening`, T5 `dd-meeting-prep` and T6 `ic-memo` ([compendium 17](../../docs/compendium/17-anthropic-pe-plugins-review.md)), and b2b-software C3 and C4 `draft-response` and C5 `customer-escalation` ([compendium 18](../../docs/compendium/18-customer-success.md)). The consultant copies a suggestion onto the card only after agreeing with it.
- Every entry in every list also carries `cite` and `unverified`. `cite` is a repo-relative path to a page under `docs/compendium/`, with an optional `#anchor` that matches a heading on that page, and the page is listed in `sources`. `unverified` is `true` when the cited page marks the fact Unverified, Not confirmed or in Conflict. A pack states nothing the cited page does not say; a value a task needs that the page does not give (for example its trigger) is the pack author's choice, listed in the pull request, not the page's.

Fallback: when the customer's pack has no connector default for a system, levelling looks in the general pack, and the customer's pack wins when both have one; `general.json` holds one default per product row of compendium 11's table, and a product that an industry pack and the general pack both list has the same `runbook` in each. A pack product written as `A / B` (as page 11's rows are) matches a system as `A` and as `B`.

`packs.py` has `list_packs()`, `load_pack(id)` (an unknown id raises an error that names the ids that exist) and `pack_problems(pack)`, which returns `{path, message, fix}` for each fault and reads enumerations and profile field types from the catalogue. `tests/test_twincard_packs.py` checks each shipped pack against the repo: cites, anchors, runbooks, the settings baseline and the unverified rule.

### 7.2 Decision values

The vocabulary that `tests/fixtures/twincard/expectations.json` and the levelling engine share. A decision the compendium does not settle is `null`, with a reason that says it is undecided and what the page lacks; it is never filled in by judgment.

| Decision | Values |
|---|---|
| `runtime` | `client-skill`, `claude-code-scheduled-task`, `claude-tag-routine`, `managed-agents` (the Anthropic-hosted form), `managed-agents-self-hosted` (Managed Agents with the harness and sandbox self-hosted; the only Managed Agents form the ZDR branch of the compendium 05 decision flow allows), `agent-sdk`, `none` (no runtime is allowed for this task) |
| `identity` | `user`, `service-account`, `api-key-vault`, or `null` when the runtime is `none` (a task with no runtime has no identity) |
| `autonomy.start`, `autonomy.ceiling` | an integer from 0 to 4 (the ladder in compendium 06) |
| `data_controls` | `{settings_baseline, web_tools, surfaces, retention}`: `settings_baseline` is a file stem in `starter-kit/settings/` (`general`, `confidential`, `pe-zdr`, `hipaa`) or `null`; `web_tools` is `on` or `off`; `surfaces` is a list of `role.works_in` values (empty for a hosted runtime); `retention` is a value of `compliance.retention` |
| `connectors` | a list of `{system, access, identity}`: `system` is a profile system id, `access` is `read` or `write`, `identity` is an `identity` value (`null` when the runtime is `none`) |
| `memory` | `on` or `off` |
| `plan_fit` | `ok`, `ok-with-limits`, `needs-enterprise`, `not-supported` |
| `persona.distribution` | `group-targeted` (Enterprise), `everyone` (Team), `manual` (a plan that cannot publish plugins, so users install them by hand) |
| `persona.settings_baseline` | a file stem in `starter-kit/settings/`, or `null` |
| `connectors[].permission`, `tools[].permission` | `always-allow`, `needs-approval`, `blocked` (the per-tool settings in compendium 06) |

Each decision in the expectations file is `{expected, cite, reason, unverified}`. A blocker or a warning is `{code, about, cite, unverified}`: `about` is a task id or `persona`, `cite` is a compendium page with an anchor, and `unverified` is true when the cited page marks the fact Unverified. An overridden decision also carries `overridden: true`, the rule's own result and the override's reason.

Blocker codes (the task cannot be built as asked on this plan or data class):

- `plan-below-team`: the plan is an individual plan; Team is the minimum for company data.
- `private-network-unreachable`: a task on an Anthropic-hosted runtime (Claude Tag or hosted Managed Agents) reads a system on a private network that it cannot reach on this plan (no MCP tunnel, no allowlisting).
- `log-every-action-not-met`: the customer requires a log of every action, and the twin runs where no governance hook can run (claude.ai on the web, no device management), or a client-skill or Claude Code scheduled task's planned surfaces include one other than `claude-code` (`claude-ai`, `desktop`, `cowork`, `slack`, `teams`); a task is listed once.
- `highly-sensitive-needs-zdr-org`: a task is highly sensitive, and either the plan has no Enterprise org with ZDR or the profile's `compliance.zdr_cover` is `none` (the customer has no ZDR agreement and does not plan one).
- `unmanaged-device-no-access`: a highly sensitive or PHI task would run on an unmanaged device, which gets no direct access.
- `phi-needs-hipaa-org`: PHI is in scope, and there is no dedicated HIPAA org with a signed BAA.
- `phi-no-hosted-runtime`: a PHI task needs a hosted runtime, and none is covered for PHI.
- `override-not-allowed`: a card override names `connectors` or `plan_fit`, which follow from the other decisions; the override is not applied.
- `override-unknown-target`: a card override names a task or a decision that levelling does not have; the override is not applied.
- `plugin-name-invalid`: `role.plugin_name` does not match `^twin-[a-z0-9-]+$`.

Warning codes (the task can be built, with a limit someone must see):

- `agent-sdk-cover-unverified`: a task wired into systems needs ZDR or HIPAA cover, and the Agent SDK cannot be used for it until Anthropic confirms that cover in writing (Unverified, compendium 05 decision flow), so the plan uses the route the page does confirm; when the page confirms no route (PHI), `phi-no-hosted-runtime` is raised instead of this warning.
- `decision-undecided`: the compendium does not decide one of the task's decisions, or the fact a rule takes its value from is empty, so a person must.
- `high-cost-ceiling-unconfirmed`: the cost of a mistake is high and page 06 has no rule for cost, so the ceiling another rule set (named in the message) applies until a person confirms it or lowers it by override.
- `shared-tool-strictest`: two tasks share a connector tool, so both run at the stricter task's setting.
- `override-applied`: a card override replaced a rule's result; the result is shown as overridden, with the reason.
- `field-open`: a decision or a rule needs a field whose status is `open` and which has no value yet, so that decision is `null` until the field is answered.
- `team-no-group-targeting`: on Team the role plugin is shared to everyone; group targeting needs Enterprise.
- `team-no-managed-settings`: claude.ai on the web with no device management gets no managed settings and no hooks.
- `team-no-governance-log`: the governance log is a Claude Code hook, so a Team twin on the web has none.
- `team-no-audit-log`: Team has no audit log and no Compliance API.
- `confidential-on-team`: confidential data on Team is acceptable only where the audit need is lower.
- `unmanaged-connectors-read-only`: confidential data on an unmanaged device (or the unmanaged share of a mixed fleet) calls for read-only connectors, and the task writes.
- `mail-write-unconfirmed`: the task sends email or puts an event on a calendar through Gmail or Google Calendar, and the sources conflict over whether those connectors can write (⚠ Conflict, compendium 11), so (our recommendation) the plan does not count on their send or event tools and the task ends in a draft a person sends or books, unless the write test in the Google Workspace runbook shows the tool in the customer's org and the business owner and Security agree to use it at Needs approval.
- `private-network-allowlist`: a system on a private network must be reachable from Anthropic's IP range, allowlisted at the edge.
- `tag-private-channel-only`: Claude Tag on confidential data belongs only in scoped private channels.
- `slack-directory-send-unverified`: whether the Slack directory connector can post is Unverified; post through Claude Tag or the Slack MCP server.
- `untrusted-input-with-send`: a task reads untrusted content and can send it out, so a person approves each send.
- `memory-poisoning-risk`: a task reads untrusted input while personal memory is wanted; memory on claude.ai is one org-wide switch, so the task's skill must write nothing to memory and only controlled steps write it.
- `event-source-unverified`: nothing confirmed can start the task on its event, so a person starts it until that is confirmed.
- `connector-early-access`: the task's connector is in an early-access programme, with Unverified points.
- `hubspot-super-admin-approval`: the HubSpot connector needs approval from a HubSpot Super Admin (or a user with App Marketplace access) as well as an Owner.
- `scheduled-task-own-environment-only`: a highly sensitive or PHI task is a Claude Code scheduled task, and ZDR and the HIPAA configuration turn cloud sessions off, so it runs in the customer's own environment on a managed device.
- `zdr-org-not-confirmed`: a task is highly sensitive and the profile's `compliance.zdr_cover` is `planned` or still open, so no signed ZDR agreement covers the work yet.
- `private-network-inside-only`: a client skill or Claude Code scheduled task reads a system on a private network with no allowlisting and no MCP tunnel, so only Claude Code on a device inside the network (a local MCP server) reaches it.
- `unmanaged-share-no-access`: a highly sensitive or PHI task's role has a mixed device fleet, and the people on unmanaged devices get no direct access.
- `confidential-standard-retention`: a task is confidential and the profile's retention is standard, where page 10 requires custom retention.
- `retention-not-covered`: the profile's retention is custom, and the task runs on Claude Tag or Managed Agents, which custom retention does not cover.
- `claude-code-not-in-role`: `role.works_in` lacks `claude-code`, but the task's runtime is `claude-code-scheduled-task` or its planned surfaces include `claude-code`; the message says which, and the runtime and surfaces are left as decided.
- `mixed-fleet-unmanaged-surfaces`: a client-skill task on internal or confidential data in a role with a mixed device fleet gets, for every user, the surfaces allowed on an unmanaged device.

### 7.3 Rules, plan fit and `levelled.json`

**`data/rules.json`**: `{"rules_version": 1, "decisions": {<decision>: {"combine": "first" | "strictest", "order": [...]}}, "rules": [...]}`.

| Part | Meaning |
|---|---|
| `decisions` | One entry per decision the engine makes: the task decisions (`runtime`, `identity`, `autonomy.start`, `autonomy.ceiling`, `data_controls.settings_baseline`, `data_controls.web_tools`, `data_controls.surfaces`, `data_controls.retention`, `memory`, `plan_fit`), the connector decisions (`connectors.identity` per task, `connectors.permission` per tool and level) and the persona decisions (`persona.distribution`, `persona.settings_baseline`). `blocker` and `warning` rules need no entry: every one that holds is raised. |
| `combine` | `first`: rules are tried in file order and the first that holds decides. `strictest`: every rule that holds is a candidate and the strictest real value wins: the lowest number, or the value earliest in `order`; ties go to the first rule. A rule that gives `"undecided"` (or an empty fact, below) loses to any real value, so a cap the page states still applies; the engine remembers the undecided rule it outranked, and on `autonomy.ceiling` with `task.cost_of_mistake.level` high and no override it raises `high-cost-ceiling-unconfirmed`, citing the undecided rule and naming the cap that applied. When only undecided rules hold, the decision is `null` with a `decision-undecided` warning. A literal `null` is not a candidate under `strictest`. |
| `when` | Data only: an object whose keys are fact names, each mapped to a value or a list of allowed values (a list-valued fact matches when any of its items does), plus `any` and `all` (lists of conditions) and `not` (one condition). Keys are checked in order and the first that fails ends the check. `{}` always holds. |
| `then` | The decision's value; `"undecided"` (the result is `null` with a `decision-undecided` warning; `null` itself is a real value, such as no settings baseline, and raises no warning); `{"fact": <name>}` to take a fact's value; or, on a blocker or warning rule, its code from 7.2. When the named fact is `null` or absent, the rule still holds but the decision is undecided: the value is `null`, the rule's id, cite and basis are kept, and a `decision-undecided` warning names the decision and the empty fact (a highly sensitive task under a pack with no settings baseline, for example). When the named fact's field is `open`, it is treated like an open field in `when`: the decision is `null` with a `field-open` warning. |
| `reason`, `fix` | The sentence shown with the result; a blocker or warning rule's `reason` is its message and `fix` says what to do. |
| Ids | Kebab-case and unique. |

Facts are flat names. Card and profile fields keep their paths (`role.device`, `plan.tier`, `devices.mdm`, `compliance.retention`, `network.can_allowlist_anthropic_ips`, `runtime_preferences.self_hosting_required`, and others). Task fields are `task.<path>` (`task.trigger`, `task.data_class`, `task.output.audience`, `task.cost_of_mistake.level`, and so on), with derived `task.write_actions`, `task.write_products`, `task.input_products`, `task.products` (the pack's product name where a pack connector default matches the system), `task.touches_private_network` (true when any system the task reads or writes has `private_network` true) and `task.shared_tool_ceiling`. Persona-wide: `systems.kinds`, `systems.products`, `pack.id`, `pack.settings_baseline`, `persona.data_classes`, `persona.products`, and `capability.<id>` (the `plan-fit.json` value for the profile's plan). Each decision already made is a fact under its own name, and a rule may read only the decisions made before its own. Blocker and warning rules run after every task decision, so they read the decided values, `data_controls.surfaces` among them. Tool rules also read `tool.use` (`read` or the write action), `tool.level` and `tool.wanted_differs`. An unset field takes its catalogue default. A field that is `open` with no value yet stops the rule that reaches it: the decision is `null` and a `field-open` warning names the field. The one exception is a `when` key whose allowed values include `null` (`{"compliance.zdr_cover": ["planned", null]}`): an open field matches it, so a rule can hold while an answer is still missing. Inside `any`, an open field that matches no listed value is pending: another branch that holds decides, and when none does the `field-open` warning is raised. A rule that names an unknown fact or decision, a duplicate id, or a code not listed in 7.2 is a load error that names the rule.

**`data/plan-fit.json`**: `{"plan_fit_version": 1, "capabilities": [{"id", "name", "team", "enterprise", "individual", "lost_on_team", "cite", "unverified"}]}`. Each plan value is `yes`, `no` or `limited`; `lost_on_team` is one sentence or `null`; `cite` and `unverified` follow the rule for rules. `unverified` is also `true` when no compendium section states the per-plan value, so the value is our reading until a page does.

**`levelled.json`**, written by `level` next to `card.json` (keys in this order, two-space indent, UTF-8, a trailing newline; the same input gives the same bytes):

```json
{"levelled_version": 1, "customer": "", "persona": "",
 "source": {"card_sha256": "", "profile_sha256": "", "rules_version": 1, "pack": ""},
 "persona_plan": {"plugin_name": {}, "distribution": {}, "settings_baseline": {}, "starting_points": []},
 "tasks": {"T1": {"runtime": {}, "identity": {}, "autonomy": {"start": {}, "ceiling": {}},
                  "data_controls": {"settings_baseline": {}, "web_tools": {}, "surfaces": {}, "retention": {}},
                  "connectors": [{"system", "access", "identity", "how", "runbook", "permission", "cite", "unverified"}],
                  "memory": {}, "plan_fit": {}}},
 "tools": [{"system", "use", "tasks", "permission", "wanted"}],
 "blockers": [{"code", "about", "cite", "unverified", "message", "fix"}], "warnings": [],
 "complete": false}
```

Every decision (`{}` above) is `{"value", "rule", "cite", "reason", "unverified", "basis", "overridden"}`; `overridden` is `null` or `{"rule_result", "reason", "approved_by"}`. When `role.plugin_name` is given, the plugin-name decision cites its provenance source as a repo-relative path to the file the validator opens for it (the persona folder first, then the customer folder, as in 4.3). A connector lists each system a task reads or writes, in the card's order, reads first; a write to a system already listed makes it `write`. Its `how`, `runbook`, `cite` and `unverified` come from the industry pack's connector default, else the general pack's (7.1); a system with no default in either has `how` saying the compendium has no entry for the product, that the first step is to check the Claude connector directory, and to add it as a custom connector if it is not listed there, and cites compendium 11 on adding a connector that is not in the directory.

Tools: a tool is one system and one use (`read`, or a write action). `tools[].wanted` is the permission each task would give the tool at its own ceiling. When the tasks that share a tool want different permissions, a `shared-tool-strictest` warning is raised about the first of them, and each task whose ceiling is higher is levelled again with `task.shared_tool_ceiling` set to the lowest ceiling among them, until nothing changes. `tools[].permission` and `connectors[].permission` are the strictest result at the tasks' starting level.

Overrides: an override replaces one task decision (`runtime`, `identity`, `autonomy.start`, `autonomy.ceiling`, `data_controls`, `memory`) as the decision is made, so later decisions follow the new value; a `data_controls` override's value is an object of the parts it replaces. The decision keeps its rule and cite, gains `overridden`, and an `override-applied` warning is raised with the decision's cite. When an Unverified warning rule then holds on an overridden decision (an override to `agent-sdk` on a ZDR task, for example), that decision becomes `unverified: true`. An override of `connectors` or `plan_fit` raises `override-not-allowed`, and one that names a task or decision levelling does not have raises `override-unknown-target`; neither is applied. `validate` refuses a value outside the 7.2 vocabulary (section 5) before levelling runs; `level` keeps a guard that reads the same `override_values`, so a bad value reaching it is not applied either and raises `override-unknown-target`, citing 7.2. Two different `override-*` messages about the same task are both kept.

`complete` is the 4.3 rule: validation passes, completeness is 100%, no open question blocks an in-pilot task, and there is no blocker.

## 8. Backlog (`backlog.py`, `data/task-library.json`)

The hierarchy is the one in `docs/playbook/04-stories.md`. The anatomy parts do not add a second hierarchy; they label the tasks. `backlog.py` reads `card.json`, `levelled.json`, the customer profile and `data/task-library.json`, and writes `backlog.json` and `backlog.md` next to the card. Both files are generated and never hand-edited. It first validates the card, then checks that `levelled.json` exists, that its `source.card_sha256` and `source.profile_sha256` match the files on disk, and that it is what `level` gives now: it levels again in memory, with the current card, profile, rules, plan fit and pack, and compares the result with the parsed `levelled.json`. Whitespace and key order alone are not a difference; any other difference (a rules or pack change since `level` ran, a hand edit) is. If any check fails it writes nothing and says exactly `levelled.json is missing or out of date. Next: run the level command.` The backlog is built from the plan `level` gives now, and `source.levelled_sha256` is the hash of that plan's `levelled.json` text.

| Level | Generated from |
|---|---|
| **Epic** | The persona card: `<role name> twin for <display name>`, id `E` |
| **Feature** | Each `features[]` entry in card order (`F-<feature id>`, kind `capability`), then one fixed feature, `F-twin-foundation` (kind `foundation`), for work that serves the whole persona |
| **Story** | Under a capability feature: one per task, id `S-<task id>`, with a statement, target and ready checks (below), with the playbook 04 story-template table in `fields` (autonomy as `start to ceiling`, `undecided` for a null; baseline as `<frequency> per week x <minutes> minutes each x <users> users`), with `delivery` (below) after `output_and_audience`, plus `constraints` (the card's list) and `wanted_change` (`Asked for, not planned: ` and the card's text) when the task has them; `backlog.md` joins a list with `; `. Stories sort in-pilot first, then by priority, then in card order. Under Twin foundation: seven stories, always in this order: `S-persona-voice`, `S-connectors-and-identity`, `S-guardrails-and-settings`, `S-distribution`, `S-governance-log`, `S-memory-policy`, `S-pilot-rollout-and-scorecard`. |
| **Task** | One per `task-library.json` template whose `when` holds for the story, in library order |

A story's `acceptance` lists one eval line per good and per bad example on the card (`Eval from good example 1 of 2 (<where>): <result>.`), or, when the card counts none yet, one line: `To write: collect at least 3 real examples from <skill owner> and write one eval case from each.`, with `the skill owner (not named yet)` when the card names none. Then one `Keeps: <rule>` line per item of the task's `constraints`, then the Plus lines that apply: `Plus: the skill triggers on the phrases its trigger evals list and stays quiet on the near-misses.` when the task's runtime is `client-skill`; `Plus: no web tools are used.` when the task's `data_controls.web_tools` is `off`; `Plus: every write carries the twin marker.` when one of the task's CRM write tools is not Blocked at the starting level, and `Plus: the twin writes nothing to the CRM at the starting level; a person files the result.` when the task has CRM write tools and all of them are Blocked; `Plus: each tool call reaches the governance log.` when the plan has one (below).

### Statement, target, ready and done

These follow the story template and the definitions of ready and done in [playbook 04](../../docs/playbook/04-stories.md#story-template). Foundation stories keep the statement `As a <role name>, I want my twin's <story title, lowered> in place so that every task story runs safely.` and carry none of the keys below.

- **Statement.** `As a <role.name, first letter lowered>, I want my twin to <story_want> so that <story_benefit>.` Each half is the card's text, trimmed, with one trailing full stop dropped and its case kept. An empty `story_want` becomes `produce the <output.what, first letter lowered>`, or `do the task "<task name>"` when `output.what` is empty too. An empty `story_benefit` becomes `I get back the <minutes_each> minutes it takes me each time` when `minutes_each` is a number, otherwise `I do not have to do it by hand`. `statement_source` is `card` when both halves came from the card and `drafted` otherwise; `backlog.md` prints `(Statement drafted by the kit: confirm the wording with the interviewee.)` under a drafted statement, and the consultant takes the wording back to the interviewee.
- **Target.** `target` is `{"text", "set"}`. With `outcome.scorecard_targets` (each with a metric and a number): `Target: <metric>: <value>; ... . Today: <frequency_per_week> per week, <minutes_each> minutes each, <users> users.` and `set` true. With none: `Target: not set. Agree the scorecard targets with the sponsor before the pilot starts.` and `set` false. The engine invents no number. `backlog.md` prints the text under the acceptance lines, and `Stories with no target: <n>.` under the status lines when n is more than 0.
- **Ready.** `ready` lists `{"check", "met", "note"}` in this order. `fields`: met when the task's data class, surface (its levelled runtime), autonomy (start and ceiling) and identity are all decided; the note names the undecided ones. `examples`: met when the card counts at least 3 good and bad examples together; the note gives the count. `connectors`: met when every system the task reads or writes has a connector entry in its levelled plan, with identity and permission decided, and no blocker about the task or the persona names the system (its id or product) in its message or fix; the note names the failing system. `compliance-sign-off`, only for a `highly-sensitive` or `phi` task: met only when the story's `compliance-sign-off` task is `done`. `backlog.md` prints `Ready to build: yes` or `Ready to build: no` with one line per unmet check, and the summary `Stories ready to build: <n> of <m>.`
- **Compliance sign-off.** A `highly-sensitive` or `phi` task story gets the `compliance-sign-off` task (`compliance`, `A7`): compliance reads the story's fields, the levelled decisions and the data controls, and records the sign-off, with a name and date, in the customer's engagement folder. Until that task is `done`, the story's `gated_by` ends with `{"kind": "sign-off", "id": "compliance", "text"}`. The check and the gate are worked out after statuses are kept, so marking the task `done` and running `backlog` again lifts both.
- **Done.** Each line of the playbook's definition of done maps to tasks the library already gives a task story:

| Definition of done | Tasks |
|---|---|
| The evals pass on the models the customer uses. | `write-evals`, `write-skill`, `trigger-evals` |
| A reviewer who isn't the author has approved it. | `second-review` |
| The skill is published to the right group, at the right version. | `publish-in-role-plugin`, `publish-in-role-plugin-team` |
| Tool calls appear in the governance log. | `governance-log-check`, and the acceptance line for the governance log where the plan has one |
| The skill owner has been shown how to update it. | `owner-handover` |

`owner-handover` (`skill-engineer`) comes on every task story that has a runtime (the same `when` as the skill-authoring tasks), with the story's part: `A2` for a client skill, `A4` for a hosted one. The engineer shows the skill owner where the skill lives, how to change an instruction and add an eval, and who reviews the change; it is done when the skill owner has made one change with the engineer watching.

### Spikes

The backlog's top-level `spikes` holds one spike per card open question, in card order: `{"id": "SP-<question id>", "kind": "spike", "title", "question", "blocks": ["S-<task id>", ...], "owner", "due", "status"}`. The title is the question cut at its first sentence end (`.`, `?` or `!` before a space or the end), at most 120 characters (a longer one is cut at a word and ends in `…`). Each `open-question` gate names its spike (`"spike": "SP-<question id>"`). A spike's status is kept the way a task's is: change it in `backlog.json` and run `backlog` again. A spike whose question has left the card is retired the way a task is. Spikes sit in no feature's stories; the dashboard lists each spike that is not done under What is blocked (section 9). `backlog.md` lists them in a `Spikes` section after the features, with the question, owner, due date and the stories each blocks; the section is left out when there are none.

### Delivery, owners and parts

A task story's `delivery` field says how its output reaches its destination, in exactly one of four forms, decided in this order from the levelled tools that list the task and are not reads (its write tools):

1. No write tools: `The output stays in the conversation or a local file.`
2. The task runs as a `claude-tag-routine` and every write tool is a Slack send: `The Claude Tag routine posts it in its own Slack channel itself, and the connector's send tool <tool> is not used.`
3. A write tool is Blocked at the starting level: `A person sends or files it: the twin produces a draft, <tools> is (are) Blocked at the starting level, and it opens (they open) at level 2.` A tool opens when every task that shares it wants it unblocked at that task's ceiling (its `wanted` values in `levelled.json`); a shared tool adds `, once every task that uses it (<tasks>) is there`. A Blocked tool that never opens ends `and it is not planned at any level.`; a mix names both. Level 2 is `OPEN_LEVEL` in `backlog.py`, the level at which `rules.json` sets a write to Needs approval.
4. Otherwise: `The twin writes it with tool <tool> (<permission>).`, one `<tool> (<permission>)` per write tool.

Form 3 adds the `deliver-draft` task (`business-owner`, `A4`) after the tool tasks: agree the draft and who sends or files it, the evidence that moves the task up where the write opens, and a last step the engine adds that names the card's `output.destination` and links the Blocked tool's connector runbook (page 11's directory section when it has none). A task's permission words agree with its tool tasks: the warning tasks for `untrusted-input-with-send` and `unmanaged-connectors-read-only` come in two variants, one for a Blocked tool (it stays Blocked at the starting level and moves to Needs approval, never Always allow, when the task moves up) and one, `-approval`, for a tool already at Needs approval (it stays there). The `slack-directory-send-unverified` warning and the untrusted-input warning name another posting route only `if the routine route is not used`, so a Claude Tag routine's story ends in one route.

The twin-marker tasks (`twin-marker-salesforce`, `twin-marker-crm`, `twin-marker-skill`, `twin-marker-report`) need `writes.crm_opens` of `now` or `later`; when the CRM write opens later, the engine adds a first step that says it is Blocked at the starting level and opens at level 2, so the marker is set up first. A CRM write that never opens gets no marker tasks. `warning-private-network-allowlist` links page 11's section on connectors outside the directory; when a private system among the task's connectors uses the Salesforce runbook, the engine adds a last step for that runbook's IP allowlist discovery (E6).

Every task has `owner_name` and `acting_owner`. The profile's `owners` names five roles: `executive-sponsor` (`sponsor`), `technical-owner` (`technical_owner`), `business-owner` (`business_owner`), `backup-owner` (`backup_owner`) and `compliance` (`compliance`); a `skill-owner` task in a task story takes the card task's `skill_owner`. A customer role with no name gets the technical owner as `acting_owner`; the partner's roles (`engagement-lead`, `solution-architect`, `skill-engineer`, `integration-engineer`, `change-and-enablement-lead`, `consultant`) get neither. The backlog's top-level `unnamed_roles` lists each customer role that has tasks but no name, as `{"role", "tasks", "acting_owner"}`, in `owner_roles` order; `backlog.md` prints it once, under the status line, as `Roles with no named person: <role>, <n> tasks, acting owner <name>; ...` (or `none`).

A `confirm-unverified-decision` task takes the part of the decision it confirms, from `DECISION_PARTS` in `backlog.py`: `runtime` A4, `identity` A5, `autonomy.*` and `data_controls.*` A7, `memory` A6, `plan_fit` A9, `connectors.<system>` A3. `warning-high-cost-ceiling-unconfirmed` is A7, a guardrail.

### The task library

`data/task-library.json` is `{"library_version": 1, "owner_roles": [...], "templates": [...]}`. Each template is `{"id", "title", "part", "applies_to", "per", "when", "how", "done_when", "owner_role"}`:

- `id`: kebab-case, unique. `part`: `A1` to `A9`.
- `applies_to`: `task-story`, or one of the seven foundation story ids.
- `per`: `null` for one task per story, or `connector`, `tool` or `unverified-decision` for one task per item of the story's task (its connectors in `levelled.json`, the levelled `tools` that list the task, or each decision marked unverified plus `connectors.<system>` for each unverified connector).
- `when`: a condition in the `rules.json` language (7.3), evaluated by `level.matches`; `{}` always applies.
- `how`: at least two steps, each `{"text", "link"}`: one imperative sentence, and a repo-relative path with an optional `#anchor`. A `per: connector` template may start a link with `{connector.runbook}`, which the engine fills in with the connector's runbook (`connect-kit-runbook` links `{connector.runbook}#before-you-start`, `#steps`, `#check-it-worked` and `#hand-over`). The tests hold every library step and every step the engine adds to a link; the constraints step the engine adds to `write-skill` links the card's enumerations ([4.2](#42-persona-card-cardjson)).
- `done_when`: at least one sentence. `owner_role`: one of `owner_roles`.

`backlog.py` checks the library when it loads it and names the template at fault: an unknown part, owner role, `applies_to` or fact, an item fact without its `per`, a foundation template that reads a task fact, fewer than two steps, a `{connector.runbook}` link anywhere but at its start or without `per: connector`, or an empty `done_when`.

Facts a `when` may read:

- Every story: `plan.tier`, `role.device`, `distribution` and `settings_baseline` (the persona plan in `levelled.json`), `governance.log` (true when `plan-fit.json` gives the plan's `governance-action-log` as anything but `no` and levelling raised no `team-no-governance-log`), `compliance.walls`, `memory.personal_memory_wanted`, `systems.kinds`, `systems.products`, `writes.kinds`, `writes.products` (the profile's systems the task, or for a foundation story any task, reads or writes) `codes` (the blocker and warning codes about the task; for a foundation story, those about `persona`), and `pack.data_providers` (true when the customer's pack lists data providers).
- Task stories also: `task.trigger`, `task.data_class`, `task.output.audience`, `task.reversible`, `task.touches_money`, `task.cost_of_mistake.level`, `task.reads_untrusted_input`, `task.in_pilot`, `task.write_actions`, `delivery.form` (`stays-local`, `runtime-posts`, `person-sends` or `twin-writes`, above), `writes.crm_opens` (`now`, `later`, `never`, or null when the task has no CRM write tool), `tools.write_permissions` and `tools.send_permissions` (the levelled permission of each write tool and each send tool), and the task's levelled decisions `runtime`, `identity`, `autonomy.start`, `autonomy.ceiling`, `data_controls.settings_baseline`, `data_controls.web_tools`, `data_controls.surfaces`, `data_controls.retention`, `memory`, `plan_fit`.
- Per item: `connector.system`, `connector.kind`, `connector.product`, `connector.access`, `connector.permission`, `connector.runbook`, `connector.unverified`; `tool.system`, `tool.use`, `tool.permission`; `decision.name`.

Coverage the tests hold the library to: every code in 7.2 has a template (`blocker-<code>` or `warning-<code>`, with the code in its title); every runtime in 7.2 has one; every runbook an industry pack names has exactly one connect template (`connect-salesforce-runbook`, `connect-microsoft-365-runbook`, or `connect-kit-runbook` for the kit's other connector runbooks), and a connector with no runbook gets one that says so plainly (`connect-no-runbook`; `connect-own-mcp-server` for a `product-data` system, which no directory connector serves); every set-up template links its runtime's runbook in `starter-kit/runbooks/`, including its `#steps` heading, and the pilot templates link `starter-kit/templates/pilot/`; on Team, `publish-in-role-plugin-team` replaces `publish-in-role-plugin` and links the runbook's one-set-for-every-member section; every template reaches a story in a fixture, an expectations variant or a test scenario. A code about `persona` lands in the foundation story its template names; if its template serves task stories, it lands in `S-guardrails-and-settings`.

Every runtime except `none` gets the same skill-authoring tasks (`collect-examples`, `write-evals`, `write-skill`, `trigger-evals`, `second-review`); `write-skill` has one step for each runtime that says where that runtime loads the skill from, with the compendium page that says so, or marked Unverified where no page does, and, when the task has `constraints`, a last step: `Make the skill keep these rules from the interviews, in the interviewee's words: <rules joined with "; ">.` Because `write-skill` comes with every runtime but `none`, it is also the task that writes a hosted or scheduled story's agent instructions; a task whose runtime is `none` has no such task and gets no start-from steps.

**Starting points.** When the card task has `starts_from`, `write-skill` keeps its id and gains, before its other steps, one step per name in card order: `Start from <name> (<where>): <first sentence of the entry's note>`, linked to the entry's `cite`. The first sentence ends at the first `.`, `!` or `?` followed by a space or the end. An entry marked `unverified` adds ` ⚠ Unverified: the pack marks this starting point unverified, so check the cited page before you build on it.` to its step. The title becomes `Write the skill from <name> until the evals pass`, or `Write the skill from <name> and <n> more until the evals pass` for several. A task with no `starts_from` is unchanged. The names are looked up as `validate` does: the customer's pack, then the general pack.

**Data providers.** When the customer's pack lists `data_providers`, `S-connectors-and-identity` gains `data_providers` (before its tasks): the pack's entries as `{name, kind, access, note, cite, unverified}`, which `backlog.md` prints under that story as a table headed `Data providers the pack knows (none is on by default)`, with a Source column linking each cite (and `⚠ Unverified` where flagged). The `data-providers-decide` task (`compliance`, `A3`, `when` `{"pack.data_providers": true}`, a fact every foundation story can read) asks for a decision on each: allowed, not allowed or later, with the approver and the reason; it is done when every listed provider has a recorded decision in the customer's engagement folder. The engine replaces its steps with one step per distinct cite of the listed providers, in pack order (`Decide for <providers>: allowed, not allowed or later, with the approver and the reason.`), at most three (the third takes every remaining provider), plus a step to record the decisions when the providers share one cite. A pack with no providers adds neither the list nor the task.

**Retention, feedback and spend.** Two foundation templates sit on `S-guardrails-and-settings` after `data-policy`: `retention-and-feedback-settings` (`technical-owner`, `A7`, always): set the org's retention period and the feedback and training-data settings to what the data policy says, and record the values; it links [compendium 15](../../docs/compendium/15-governance-and-performance.md#retention-decided), [10](../../docs/compendium/10-sensitive-data.md#questions-to-settle-with-compliance-and-legal) and [09](../../docs/compendium/09-plans-and-it-controls.md#feature-matrix). `spend-limits` (`technical-owner`, `A9`, on Team and Enterprise, the plans page 09's feature matrix gives spend controls): set the org and per-user spend limits and name who watches them. The compendium has no section of its own on spend limits, so it links the closest sourced sections, [09's feature matrix](../../docs/compendium/09-plans-and-it-controls.md#feature-matrix) and [15's who-does-what table](../../docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often). When the profile's `governance.spend_owner` names a person, the task's `owner_name` is that person.

A highly sensitive task with ZDR retention gets `zdr-retention` when its cover is in place, and `zdr-retention-agreement-first` when `zdr-org-not-confirmed` is raised about it: the same steps, after a first step that says no signed agreement covers the work yet and the task does not go live until one does, owned by `compliance`. Only the set-up and deployment tasks differ by runtime. `start-wiring` serves a `managed-agents`, `managed-agents-self-hosted` or `agent-sdk` task whose trigger is `event` or `schedule-team`: it builds what starts a session (for an event, what receives it from the input system and calls the API; for a schedule, what runs the schedule), and is done when one test event or scheduled time starts exactly one session and a repeat of the same event starts no second one.

### Ids, status and gates

- Ids: `E`, `F-<feature id>`, `S-<task id>` or the foundation story id, and `<story id>.<template id>` for a task; a per-item template adds the item: `S-T2.tool-blocked.salesforce-update`, `S-T2.confirm-unverified-decision.connectors.salesforce`. The item also goes at the end of the title, in brackets. OPS-55 changed these ids (every sample status was `todo`, so the old ids were dropped, not retired): `S-<task>.publish-in-role-plugin` became `S-<task>.publish-in-role-plugin-team` on Team; `S-<task>.connect-no-runbook.<system>` became `S-<task>.connect-kit-runbook.<system>` for a connector with a kit runbook, and `S-<task>.connect-own-mcp-server.<system>` for a `product-data` system; and it added `S-<task>.deliver-draft`, the `-approval` warning variants, and removed the twin-marker tasks of a CRM write that never opens.
- `status`: a task is `todo`, `in-progress` or `done`. To mark one, change only its `status` in `backlog.json` and run `backlog` again: the status is kept for every id the run generates again. Story, feature and epic statuses are derived: `done` when all their tasks are, `todo` when none has started, otherwise `in-progress`. Any other status is a usage error that names the task id (exit 2), and so is a `backlog.json` that is not JSON or not in its shape; `dashboard` gives the same message.
- `retired`: a task the card no longer generates, whose status was not `todo`, moves to `retired` as `{"id", "title", "status"}`, and the command prints one line for each item it retires. Retired items stay there on later runs, and return to their story with their status if the card generates them again. A `todo` task that is no longer generated is dropped.
- `gated_by`: `[{"kind", "id", "text"}]`: `blocker` items (the code and message of each blocker about the task, plus every blocker about `persona`; foundation stories get the persona blockers), then `open-question` items (each open question whose `blocks` names the task, with `"spike"` naming its spike), then, on a task story above confidential whose `compliance-sign-off` task is not done, one `sign-off` item.
- OPS-56 added `S-<task>.owner-handover` to every task story with a runtime and `S-<task>.compliance-sign-off` to each highly sensitive or PHI task story; every sample status was `todo`, so nothing was retired.
- OPS-57 added `S-connectors-and-identity.data-providers-decide` (when the pack lists providers), `S-guardrails-and-settings.retention-and-feedback-settings` and `S-guardrails-and-settings.spend-limits` (Team and Enterprise). `write-skill` kept its id when it gained start-from steps, so no status was lost.

`backlog.json` is `{"backlog_version": 1, "customer", "persona", "source": {"card_sha256", "levelled_sha256", "library_version"}, "unnamed_roles", "epic": {"id", "title", "status", "features"}, "spikes", "retired"}`, with keys in that order, two-space indent, UTF-8, a trailing newline and no dates or paths, so two runs give the same bytes. A task story is `{"id", "title", "statement", "statement_source", "part", "in_pilot", "priority", "status", "fields", "acceptance", "target", "ready", "gated_by", "tasks"}`, a foundation story the same without `statement_source`, `target` and `ready` (and `S-connectors-and-identity` adds `data_providers` before `tasks` when the pack lists them), and a task `{"id", "template", "title", "part", "how", "done_when", "owner_role", "owner_name", "acting_owner", "status"}`. A task story's `part` is `A2` for a client skill and `A4` otherwise.

`backlog.md` is the readable form: the epic as its title, a line saying it is generated from `card.json` and `levelled.json` and giving the command, the status, unnamed-roles, ready and target summary lines, then a section per feature and per story (statement and the drafted note, fields table, acceptance, target, ready, gates) with the tasks as a checklist (`[ ]` todo, `[~]` in progress, `[x]` done), each with its owner role and the owner's name (`owner: <role>, <name>`, or `owner: <role>, acting: <name>`), numbered steps (links relative to the persona folder) and done-when, then the spikes, and the retired items at the end. Every value from the card or the library goes through one helper before it is written, so text cannot change the page's structure: whitespace runs (CR and LF included) become one space and the ends are trimmed, `<` becomes `&lt;`, `|` in a table cell becomes `/`, and a value that starts a line or follows a list marker (a statement, an acceptance line, a step, a gate's kind) has a leading heading, list, quote, fence or table character backslash-escaped. `backlog.json` and `--plan-out` keep the raw values.

`--plan-out FILE` also writes the backlog in the `tree_import` plan shape, `{"version": 1, "items": [{"type", "title", "note", "children"}]}`, epic to feature to story to task, so it can be filed to a tracker. Each note starts with the item's id; a task's note adds its owner role and name, its numbered steps and `Done when:`.

Owner roles (`owner_roles`): the playbook 03 roles `executive-sponsor`, `technical-owner`, `backup-owner`, `business-owner`, `compliance`, `security`, `source-system-admin`, `skill-owner`, `pilot-user`, `engagement-lead`, `solution-architect`, `skill-engineer`, `integration-engineer` and `change-and-enablement-lead`, plus `consultant` for work the partner does that no single playbook role owns.

## What the generator does not produce

Some work stays engagement-specific: the backlog never generates it, and the consultant writes it by hand in the customer's folder under `engagements/`, beside the generated files. The [private-equity sample's backlog](../../engagements/sample-pe/backlog.md#2-supporting-items) shows each kind.

- **A house-style skill in a shared plugin** (one skill every role's skills use, in `twin-shared`): a story in the engagement's `backlog.md`, with its owner, and its design in `design.md`'s plugins and skills section.
- **The layer-or-build review of Anthropic's plugins** (OD-1): a decision row in `backlog.md` with its reviewer and sign-off. `starts_from` records the answer per task once it is agreed; the review itself is not generated.
- **Contract checks with Anthropic** (ZDR addendum, which models qualify, seat counts): a customer-action task in `backlog.md`, with the account team as owner.
- **Account migration** (personal or Pro accounts moving into the org): a task in `backlog.md`, with the steps in `design.md`'s org plan.
- **Device-trust and network work** (the identity provider's device trust, the org's IP allowlist): a task in `backlog.md` for the technical owner, with the rules in `design.md`'s devices section.
- **Keeping connectors out of chosen surfaces for a group** (for example out of chat and Cowork): a spike in `backlog.md` until the compendium confirms the setting.
- **A hosted front end for users on unmanaged devices**: a Scale-phase story in `backlog.md`.
- **A connector for a later team** (a system only a team that joins later uses): a Scale-phase task in `backlog.md`, after any spike it waits for.
- **Concrete eval cases** (the prompt, the expected result and the pass mark for each real example): the story cards in `backlog.md`, then the skill's `evals/` folder in the role plugin. The generated backlog gives one acceptance line per counted example, not the case itself.

## 9. Dashboard (`dashboard.py`)

One self-contained HTML5 page per persona, `<persona-dir>/dashboard.html`, written by `cli.py dashboard <persona-dir> [--date YYYY-MM-DD]`. It is a rendering only: every value on it comes from `card.json`, `../../customer-profile.json`, `levelled.json`, `backlog.json`, or the completeness figures `validate` computes. Before rendering, `dashboard.py` validates the card and checks the inputs are current: `levelled.json` must exist, its `source.card_sha256` and `source.profile_sha256` must match the files on disk, and it must be what `level` gives now (it levels again in memory and compares, as `backlog` does in section 8); `backlog.json` must exist, its `source.card_sha256` and `source.levelled_sha256` must match the card and that plan, and it must be what `backlog` gives now: it builds the backlog in memory, carrying `backlog.json`'s statuses over, and compares it with the parsed file. Whitespace and key order alone are not a difference. If a check fails it writes nothing and names the file and the command to run next (`levelled.json is out of date … Next: run the level command, then the backlog command`, or `backlog.json is out of date … Next: run the backlog command`). A status changed by hand in `backlog.json` therefore needs `backlog` before `dashboard` when it changes a derived story or feature status. The page is rendered from the plan and backlog built in memory, which equal the files.

`render(persona_dir, date)` returns the page and never writes; `write_dashboard(persona_dir, date)` writes it. The page:

- has one `<style>` element and no script, no event handler and no JavaScript of any kind;
- makes no external request: no link, image, font, `@import` or `url()`; the only links are the contents links to its own sections;
- shows every cite and every `how` link as text in a `<code>` element, with its full path and anchor as `levelled.json` and `backlog.json` hold it (such as `docs/compendium/06-autonomy.md#rules-for-moving-up-a-level`), never as a link and never as a bare file name; the header says once "Paths are relative to the delivery repository." Provenance sources are the exception: they are shown as the records write them, relative to the persona folder (card) or the customer folder (profile), and the "Where each answer came from" block says so;
- writes a null decision as "undecided" with its reason where the decision is shown on its own, and "none" only where the plan decided none; the settings baseline reads the same on the page as in `backlog.md`;
- HTML-escapes every value it takes from the inputs;
- uses `<details>` and `<summary>` for decision reasons, for each backlog story and for the closed provenance block at the end; nothing above the contents list is collapsed, and nothing inside a story is collapsible;
- prints every part: in print the contents list stays visible, every `<details>` is shown open, `.scroll` containers stop scrolling and wrap, and a story avoids a page break inside where it fits;
- defines its colours as custom properties on `:root`, redefined for dark mode, uses the system font stack, fits a 360px screen with a 16px gutter (tables scroll in their own container), never skips a heading level, gives every table header cells, and never shows a status by colour alone (each carries a word or symbol such as "⚠ Unverified", "✗ Blocker", "[x] done").

Its nine sections, in order, are each a `<section data-section="<Name>" id="<kebab-name>">`. The top two are for a sponsor and need nothing opened; the contents list follows them.

1. **Header** (`header`): the role and customer, with a "Fictional sample" label when the profile says so, and a sponsor line, "Tasks in the pilot: N. Blockers: N. Backlog tasks done: N of N." Then, as a list: customer and customer id; role, team and persona card id; plan tier, seats and individual accounts on the domain; the sponsor goal in full; the targets (`metric: value; …`, or "Targets not set"); completeness % with the required fields answered or default; Complete or Not complete with the reasons (required fields missing, open questions that block an in-pilot task, blockers); the counts of blockers, warnings and unverified decisions (the persona decisions, the task decision cells and the tool permissions that rest on an unverified fact); "Stories ready to build: N of M" over the task stories; the five owners (sponsor, technical owner, business owner, backup owner, compliance), each with a name or "not named"; the backlog's `unnamed_roles` line; industry pack; pilot users of headcount; role plugin, distribution and settings baseline; the paths line; and the generated date.
2. **What is blocked** (`what-is-blocked`): three lists, each with a one-line statement when it is empty. Blockers, each with what it is about and its message ("No blockers."). The backlog's spikes that are not done, each labelled "Spike" with its question, owner ("not named"), due date ("not set") and the stories it blocks ("No open spikes."). The stories with a `sign-off` gate, with the gate's text ("No story is waiting on a compliance sign-off.").
3. **Anatomy grid** (`anatomy-grid`): nine panels, one per anatomy part, from the panel table below. Each panel shows its decisions, "Required fields answered: N of N" (the required fields of both records whose `part` in `data/fields.json` is that part, counted as `validate` counts them) and "Backlog tasks done: N of N" (backlog tasks whose `part` is that part). A line under the grid counts the required fields whose part is `context`, so the panels and that line add up to the header's figure.
4. **Feature list** (`feature-list`): each card feature with its why, then each of its tasks in card order: name, in pilot or later, priority, trigger, data class, volume and cost of a mistake, then, when the task has them, "Rules it must keep:" with its `constraints` and "Wish (asked for, not planned):" with its `wanted_change` (`data-field="<task id>.constraints"` and `"<task id>.wanted_change"`), then one row per decision: runtime, identity, autonomy start, autonomy ceiling, "start to ceiling" ("undecided" for a null), data controls, memory, plan fit and connectors (system, product, access, identity and permission). Each decision's reason, rule, basis, cite and connector runbook sit inside a `<details>`. A decision resting on an unverified fact carries an "Unverified" label; an overridden one carries an "Overridden" label with the rule's result, the reason and who approved it.
5. **Blockers and warnings** (`blockers-and-warnings`): blockers, then warnings, grouped by what they are about (the persona first, then each task in card order); each shows its code, message, fix and cite, and an "Unverified" label when flagged. "No blockers." in words when there are none. A third list, "Rests on an unverified fact", names every decision, connector, tool permission, starting point and code that carries `unverified: true`.
6. **Overrides** (`overrides`): one row per card override with its task, decision, value, reason and who approved it, or "No overrides."
7. **Backlog** (`backlog`): the epic as a heading with its status and tasks done of total, a line "Stories shown open: N. Stories closed: M.", then each feature as a heading and each story as one `<details class="story">`, open when the story is in the pilot and not done. Inside a story, in order: the statement (with "(statement drafted by the kit: confirm the wording)" when the kit drafted it); the target line; "Ready to build: yes" or "no" with each unmet check and its note; the delivery sentence; the fields table, with the same labels and values as `backlog.md`; the starting points (name, kind, where, note and cite); the acceptance lines as a numbered list; the gates ("Nothing gates this story." when none); on `S-connectors-and-identity`, the data providers table; and one task table with id, title, part, owner (role and name, or the acting owner) and status, then each task's done-when and its numbered `how` steps with the links in full. A foundation story has no target, ready, delivery or starting points. Retired items come last.
8. **Open questions** (`open-questions`): id, question, the tasks it blocks, owner and due date; those that block an in-pilot task first, marked as blocking the pilot.
9. **Where each answer came from** (`where-each-answer-came-from`): a count of provenance entries by status (answered, default, assumed, open) for the card and for the profile; every assumed or open field with its record and path, owner, due date and source; the interview files the card cites; and, last on the page, a closed `<details>` "Where each answer came from: every provenance entry (N)" with one row per entry (card first, then profile, in record order): record, field, status, each source, owner and due date.

The panel table (the `PANELS` constant at the top of `dashboard.py`):

| Panel | Name | Shows |
|---|---|---|
| A1 | Persona | role plugin name with its cite; team and pilot users of headcount; voice: serves, tone, never, escalates to |
| A2 | Skills | the tasks that are client skills; each task's skill owner; the industry pack's Anthropic starting points (kind, name, where, use, cite), with an Unverified label where flagged |
| A3 | Connectors | each tool (system, product, read or write, permission decision, tasks); each profile system (product, kind, edition, access model, private network); the pack's data providers as a table (name, kind, access, note, source), headed "Data providers the pack knows (none is on by default)", or "The industry pack lists no data providers." |
| A4 | Runtime | tasks per runtime; where the role works; where the interviewees would rather work (`role.wanted_surfaces`, only when given; a surface the role does not work in is marked "a wish, not planned"); whether self-hosting is required |
| A5 | Identity | tasks per identity; connectors per identity; the identity provider, SSO and SCIM |
| A6 | Memory | whether the role wants personal memory; memory per task; the card's memory notes |
| A7 | Guardrails | settings baseline with its cite ("undecided" with the reason when null); web tools per task; autonomy start and ceiling range, naming tasks whose ceiling is undecided; tasks per data class; devices (role device, MDM, managed and unmanaged); compliance (data classes, retention, ZDR cover, walls, PHI, BAA, MNPI) |
| A8 | Evaluation | good and bad examples per task, with where they come from; scorecard targets |
| A9 | Distribution and governance | distribution with its cite; the governance log from the backlog's governance-log story; the profile's governance answers (log destination, action log, source audit, spend owner, spend limits); plan fit per task, with the reason for any limit |

Fields the page does not show. Every field in `data/fields.json` whose `feeds` names a `dashboard:` section appears on the page for both samples (a test checks it). These have no `dashboard:` feed, and why:

- `voice.jobs`, `voice.norms` and `voice.ask_before`: they shape the role plugin's voice text, not a decision or a build step; the card and the plugin show them.
- `tasks[].inputs[].access`, `tasks[].writes[].system`, `tasks[].writes[].objects` and `tasks[].writes[].action`: the levelled connectors and tools they decide are shown instead (system, access, identity and permission), and the story's fields table carries what the backlog makes of them.
- `tasks[].reversible`, `tasks[].touches_money` and `tasks[].reads_untrusted_input`: inputs to the autonomy and memory rules; the page shows the decisions and their reasons.
- `network.can_allowlist_anthropic_ips`: an input to the connector rules; it reaches the page only as the warning or task it raises.
- `tasks[].starts_from`: shown in each story's starting points, but its feed stays `backlog:task` because the starting points are read from the backlog, not the card.

Data attributes, for tests and tools that read the page: `data-section` on each section; `data-part="A1"`…`"A9"` on each panel; `data-decision="<task id>.<decision>"` on each feature-list decision cell, with decision one of `runtime`, `identity`, `autonomy.start`, `autonomy.ceiling`, `data_controls`, `memory`, `plan_fit`, `connectors` (and `persona.plugin_name`, `persona.distribution`, `persona.settings_baseline` in the header); `data-code` and `data-about` on each blocker and warning in the Blockers and warnings section only; `data-unverified="true"` on exactly the decision cells and blocker or warning entries that rest on an unverified fact (a data-controls or connectors cell is unverified when any part of it is); `data-field` on the header's `customer`, `role`, `plan`, `sponsor-goal`, `targets`, `completeness`, `complete`, `complete-reasons`, `blocker-count`, `warning-count`, `unverified-count`, `ready-count`, `unnamed-roles`, `paths-note` and `sponsor-line`, and on the backlog's `story-count`; `data-owner` on each owner; `data-blocked="blocker"`, `"spike"` or `"sign-off"` (with `data-id`) on each What is blocked entry; `data-provider` on each A3 provider row; `data-override` on each override row; `data-story` on each story, `data-story-part` on its parts (`statement`, `target`, `ready`, `delivery`, `fields`, `starting-points`, `acceptance`, `gates`, `providers`, `tasks`) and `data-task` on each task's rows; and `data-provenance="<record>:<path>"` on each provenance row.

The generated date comes from `--date YYYY-MM-DD` (default: today); the whole value must be four, two and two ASCII digits joined by hyphens, and a value that is not, or is not a real calendar date (`2026-02-30`), is a usage error (exit 2). It is the only date the renderer adds, so the same inputs and the same date give the same bytes; due dates and interview file names on the page are input data. The committed pages for the two fixtures are generated with `--date 2026-11-15`, and the acceptance tests check they match a fresh render. A page can be published as a Claude artifact by the consultant; only fictional samples are published from this repo.

## 10. Fixtures (both fictional)

- `engagements/sample-pe/personas/deal-team-associate/` on Enterprise with ZDR. Do not edit `design.md` or `backlog.md`. `discovery.md` changes only in the cells a task card names (OPS-46 changed the G1 answer and the T4 trigger).
- `engagements/sample-team-cs/`: an invented 60-person software company on a **Team** plan (Google Workspace, HubSpot, Slack, no MDM), persona `customer-success-manager`. It proves the Team path. Its discovery answers are in `discovery.md`, every row answered, and its follow-up notes with the team lead are `interviews/2026-11-10-team-lead.md`.

## 11. Rules for contributors

- Standard library only. Python 3.9+. No network in scripts or tests.
- Everything under `engagements/sample-*` is invented. No real company or person names.
- A fact about Claude goes in the compendium with a source link, or carries ⚠ Unverified. Data files cite the compendium page; they do not restate facts without a link.
- Link to existing pages; do not copy their content.
- Tests live in `tests/` and run with `python3 -m unittest discover -s tests`.
