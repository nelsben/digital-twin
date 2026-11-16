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
      card.json  customer-profile.json  interview-guide.md  interview-notes.md
```

A plugin is copied to a cache when installed, so **everything the scripts read sits inside the plugin folder**. Scripts find data relative to their own file, never by repo path.

Per customer, in the engagement folder:

```
engagements/<customer>/
  customer-profile.json
  personas/<persona-id>/
    interviews/<yyyy-mm-dd>-<who>.md       # notes or transcript
    card.json
    levelled.json   backlog.json   backlog.md   dashboard.html     # generated; never hand-edited
```

CLI (one entry point, run from anywhere):

```
python3 partner-kit/plugins/twin-consultant/scripts/twincard/cli.py validate  <persona-dir>
python3 .../cli.py level     <persona-dir>     # writes levelled.json
python3 .../cli.py backlog   <persona-dir>     # writes backlog.json, backlog.md
python3 .../cli.py dashboard <persona-dir>     # writes dashboard.html
python3 .../cli.py all       <persona-dir>     # the four in order; stops at the first failure
```

`<persona-dir>` holds `card.json`; the customer profile is found at `../../customer-profile.json`. Exit code 0 on success, 1 on a validation or levelling blocker, 2 on a usage error. Errors name the field path and say what to do next.

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
    "retention": "zdr", "walls": "soft"
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

- `status`: `answered` (a person said it; `source` points at the interview file and question id, or a discovery question id), `default` (taken from a named default; `source` is the compendium page or pack that sets it), `assumed` (the consultant's guess; needs an `owner` to confirm), `open` (no answer yet; needs `owner` and `due`; the value may be null).
- Paths use ids, not array positions: `tasks.T1.minutes_each`, `voice.tone`, `systems.salesforce.edition`. Lists with no key (`inputs[]`, `writes[]`, `overrides[]`) use the position: `tasks.T1.writes[0].action`.
- A required field with no provenance entry is a validation error. This is what makes "every field traces to a source" checkable.
- **Completeness** = required fields whose status is `answered` or `default`, over all required fields, as a percentage. `assumed` and `open` count against it.
- A card is **complete** when: validation passes, completeness is 100%, no open question blocks an in-pilot task, and levelling reports no blocker.

## 5. Field catalogue (`data/fields.json`)

One entry per field of both records:

```json
{"path": "tasks[].trigger", "record": "card", "type": "enum", "values": ["person","schedule-own","schedule-team","event"],
 "required": true, "key": false, "asked_by": ["F5"], "default": null,
 "feeds": ["rule:runtime", "backlog:story.surface"], "part": "A4"}
```

- `required`: true when a levelling decision (section 7) or the persona voice needs the field. A required field needs a provenance entry and counts in completeness.
- `key`: true for a field that names or links an entry rather than answering a question: the record ids (`id` and `customer` on the card, `customer` on the profile), the list keys (`systems[].id`, `features[].id`, `tasks[].id`, `open_questions[].id`, `outcome.scorecard_targets[].metric`) and the references (`tasks[].feature`, `tasks[].inputs[].system`, `tasks[].writes[].system`, `overrides[].task`, `open_questions[].blocks`). **A key field is always structurally required, carries no provenance and is left out of completeness**, so its `required` flag is false. A missing key is a validation error.
- `default`: `null`, or `{"value": ..., "source": "<compendium or playbook page>"}`.
- `asked_by`: discovery question ids (A1 to G4 in `docs/playbook/02-discovery.md`) or interview-guide question ids (section 6). Every field has at least one, or a `default` with a source link.
- `feeds`: the levelling rules, backlog generators or dashboard panels that read it. **Every field has at least one.** A field nothing reads is deleted.
- `feeds` vocabulary: `rule:<decision>` with decision one of `runtime`, `identity`, `autonomy`, `data_controls`, `connectors`, `memory`, `plan_fit`; `backlog:<level>` with level one of `epic`, `feature`, `story`, `task`; `dashboard:<section>` with section one of `header`, `anatomy`, `features`, `blockers`, `backlog`, `open_questions`, `provenance`; and `voice` (the persona voice file).
- `part`: the anatomy part it belongs to (A1 persona, A2 skills, A3 connectors, A4 runtime, A5 identity, A6 memory, A7 guardrails, A8 evaluation, A9 distribution and governance) or `context`.
- Tests enforce both rules and that the templates, the validator and the catalogue agree.

## 6. Interview guide

Client-facing: a consultant reads it to a role holder. Plain language, no Claude jargon. Question ids continue the discovery questionnaire's section F (F1 to F5 exist) with a `P` section for the persona itself:

- `P1`–`P6`: the role, who they serve, what a good week looks like, tone they expect, things the twin must never do, who they escalate to.
- `F1`–`F5` as in discovery, asked per task, extended with `F6` (who else sees or changes the output), `F7` (can it be undone; does it touch money), `F8` (does it read things written by outsiders: customer email, tickets, web pages), `F9` (would you want it to remember anything between sessions).
- A closing section turns tasks into a feature list: group tasks under a capability the role holder names.

Every question lists the card field paths it fills. Every required card field in parts A1–A8 is reachable from a question or a default.

## 7. Levelling (`data/rules.json`, `level.py`)

Rules are data, not if-statements buried in code: `{"id", "decides", "when", "then", "cite", "unverified"}`. `cite` is a compendium page path (and anchor where one exists). `unverified: true` when the compendium marks the underlying fact ⚠ Unverified; it is carried into `levelled.json`, the backlog and the dashboard so nobody builds on an unconfirmed fact unknowingly.

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

Per persona: the plugin name (`twin-<persona-id>`), how it is distributed on this plan (group-targeted on Enterprise; to everyone on Team), the settings baseline, the Anthropic plugins to start from (industry pack), and a list of **blockers** (a task that cannot be built as asked on this plan or data class) and **warnings**.

Overrides on the card replace a rule's result and are shown as overridden, with the reason, everywhere.

### 7.1 Industry packs (`data/industry-packs/<id>.json`, `packs.py`)

A pack is the machine-readable form of what the compendium says about one industry. Levelling and the backlog read it; it links to compendium pages for its facts and never states an unconfirmed fact as settled. The profile's `industry` is `general` or the id of a pack, and the validator reports anything else. `general.json` is for a customer with no pack: starting points that apply to any role, and empty lists where nothing general applies.

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
- `typical_tasks[]`: `{id, name, feature, trigger, data_class, inputs}`. `trigger` and `data_class` use the catalogue's values for `tasks[].trigger` and `tasks[].data_class`; `inputs` is a list of system kinds.
- Every entry in every list also carries `cite` and `unverified`. `cite` is a repo-relative path to a page under `docs/compendium/`, with an optional `#anchor` that matches a heading on that page, and the page is listed in `sources`. `unverified` is `true` when the cited page marks the fact Unverified or Not confirmed. A pack states nothing the cited page does not say; a value a task needs that the page does not give (for example its trigger) is the pack author's choice, listed in the pull request, not the page's.

`packs.py` has `list_packs()`, `load_pack(id)` (an unknown id raises an error that names the ids that exist) and `pack_problems(pack)`, which returns `{path, message, fix}` for each fault and reads enumerations and profile field types from the catalogue. `tests/test_twincard_packs.py` checks each shipped pack against the repo: cites, anchors, runbooks, the settings baseline and the unverified rule.

### 7.2 Decision values

The vocabulary that `tests/fixtures/twincard/expectations.json` and the levelling engine share. A decision the compendium does not settle is `null`, with a reason that says it is undecided and what the page lacks; it is never filled in by judgment.

| Decision | Values |
|---|---|
| `runtime` | `client-skill`, `claude-code-scheduled-task`, `claude-tag-routine`, `managed-agents` (the Anthropic-hosted form), `managed-agents-self-hosted` (Managed Agents with the harness and sandbox self-hosted; the only Managed Agents form the ZDR branch of the compendium 05 decision flow allows), `agent-sdk`, `none` (no runtime is allowed for this task) |
| `identity` | `user`, `service-account`, `api-key-vault` |
| `autonomy.start`, `autonomy.ceiling` | an integer from 0 to 4 (the ladder in compendium 06) |
| `data_controls` | `{settings_baseline, web_tools, surfaces, retention}`: `settings_baseline` is a file stem in `starter-kit/settings/` (`general`, `confidential`, `pe-zdr`, `hipaa`) or `null`; `web_tools` is `on` or `off`; `surfaces` is a list of `role.works_in` values (empty for a hosted runtime); `retention` is a value of `compliance.retention` |
| `connectors` | a list of `{system, access, identity}`: `system` is a profile system id, `access` is `read` or `write`, `identity` is an `identity` value |
| `memory` | `on` or `off` |
| `plan_fit` | `ok`, `ok-with-limits`, `needs-enterprise`, `not-supported` |

Each decision in the expectations file is `{expected, cite, reason, unverified}`. A blocker or a warning is `{code, about, cite, unverified}`: `about` is a task id or `persona`, `cite` is a compendium page with an anchor, and `unverified` is true when the cited page marks the fact Unverified. An overridden decision also carries `overridden: true`, the rule's own result and the override's reason.

Blocker codes (the task cannot be built as asked on this plan or data class):

- `plan-below-team`: the plan is an individual plan; Team is the minimum for company data.
- `private-network-unreachable`: a task reads a system on a private network that its runtime cannot reach on this plan (no MCP tunnel, no allowlisting, not run inside the network).
- `log-every-action-not-met`: the customer requires a log of every action, and the twin runs where no governance hook can run (claude.ai on the web, no device management).
- `highly-sensitive-needs-zdr-org`: a task is highly sensitive, and the customer has no Enterprise org with ZDR.
- `unmanaged-device-no-access`: a highly sensitive or PHI task would run on an unmanaged device, which gets no direct access.
- `phi-needs-hipaa-org`: PHI is in scope, and there is no dedicated HIPAA org with a signed BAA.
- `phi-no-hosted-runtime`: a PHI task needs a hosted runtime, and none is covered for PHI.
- `connector-cannot-write`: a task writes to a system whose connector cannot do that action.

Warning codes (the task can be built, with a limit someone must see):

- `agent-sdk-cover-unverified`: a task wired into systems needs ZDR or HIPAA cover, and the Agent SDK cannot be used for it until Anthropic confirms that cover in writing (Unverified, compendium 05 decision flow), so the plan uses the route the page does confirm; when the page confirms no route (PHI), `phi-no-hosted-runtime` is raised instead of this warning.
- `decision-undecided`: the compendium does not decide one of the task's decisions, so a person must.
- `shared-tool-strictest`: two tasks share a connector tool, so both run at the stricter task's setting.
- `override-applied`: a card override replaced a rule's result; the result is shown as overridden, with the reason.
- `team-no-group-targeting`: on Team the role plugin is shared to everyone; group targeting needs Enterprise.
- `team-no-managed-settings`: claude.ai on the web with no device management gets no managed settings and no hooks.
- `team-no-governance-log`: the governance log is a Claude Code hook, so a Team twin on the web has none.
- `team-no-audit-log`: Team has no audit log and no Compliance API.
- `confidential-on-team`: confidential data on Team is acceptable only where the audit need is lower.
- `unmanaged-connectors-read-only`: confidential data on an unmanaged device calls for read-only connectors, and the task writes.
- `mail-read-only`: the mail and calendar connectors read only, so an email task ends in a draft a person sends.
- `private-network-allowlist`: a system on a private network must be reachable from Anthropic's IP range, allowlisted at the edge.
- `tag-private-channel-only`: Claude Tag on confidential data belongs only in scoped private channels.
- `slack-directory-send-unverified`: whether the Slack directory connector can post is Unverified; post through Claude Tag or the Slack MCP server.
- `untrusted-input-with-send`: a task reads untrusted content and can send it out, so a person approves each send.
- `memory-poisoning-risk`: a task reads untrusted input while personal memory is wanted, so memory stays off for it.
- `event-source-unverified`: nothing confirmed can start the task on its event, so a person starts it until that is confirmed.
- `connector-early-access`: the task's connector is in an early-access programme, with Unverified points.
- `hubspot-super-admin-approval`: the HubSpot connector needs a HubSpot Super Admin's approval as well as an Owner.

## 8. Backlog (`backlog.py`, `data/task-library.json`)

The hierarchy is the one in `docs/playbook/04-stories.md`. The anatomy parts do not add a second hierarchy; they label the tasks.

| Level | Generated from |
|---|---|
| **Epic** | The persona card: "<role name> twin for <customer>" |
| **Feature** | Each `features[]` entry, plus one fixed feature, **Twin foundation**, for work that serves the whole persona |
| **Story** | Under a capability feature: one per task (`As a <role>, I want my twin to <task> so that <outcome>`), with the story-template table from playbook 04 filled from the card and `levelled.json`. Under Twin foundation: one per persona-wide part (persona voice; connectors and identity; guardrails and settings; distribution; governance log; memory policy; pilot rollout and scorecard). |
| **Task** | From `task-library.json`: templates keyed by anatomy part and by levelling result, each with `title`, `part`, `how` (the steps, linking the kit template, runbook or compendium page to use), `done_when`, `owner_role`. For example a client-skill story always gets "collect 3 examples", "write the evals", "write the skill from the template", "trigger evals", "review by a second person", "publish". A story with a Salesforce write gets the twin-marker tasks. |

Every generated item has a stable id (`E`, `F-<feature>`, `S-<task id>`, `S-<task id>.T3`), a `part`, a `status` (`todo` at generation; kept across regeneration if `backlog.json` already has the id), and the open questions and blockers that gate it. `backlog.md` is the readable form. `backlog.json` also exports in the `tree_import` plan shape (`{"version":1,"items":[{"type","title","note","children"}]}`) so it can be filed to a tracker.

## 9. Dashboard (`dashboard.py`)

One self-contained HTML file per persona (inline CSS, no external requests, light and dark, readable on a phone). It is a rendering of `card.json`, `levelled.json` and `backlog.json`:

1. Header: persona, customer, plan tier, completeness %, complete or not, generated date.
2. Anatomy grid: nine panels (A1–A9), each with the decisions made, their status, and counts of tasks done.
3. Feature list: features and their tasks, with runtime, autonomy start → ceiling, data class and plan fit per task; overrides marked.
4. Blockers and warnings, including anything resting on an unverified fact.
5. Backlog: epic → features → stories → tasks with status.
6. Open questions with owner and due date.
7. Where each answer came from (provenance summary).

The generated date comes from `--date YYYY-MM-DD` (default: today), so a run with a fixed date gives the same bytes every time. It can be published as a Claude artifact by the consultant. Only fictional samples are published from this repo.

## 10. Fixtures (both fictional)

- `engagements/sample-pe/personas/deal-team-associate/` on Enterprise with ZDR. New files only: do not edit `discovery.md`, `design.md`, `backlog.md`.
- `engagements/sample-team-cs/`: an invented 60-person software company on a **Team** plan (Google Workspace, HubSpot, Slack, no MDM), persona `customer-success-manager`. It proves the Team path.

## 11. Rules for contributors

- Standard library only. Python 3.9+. No network in scripts or tests.
- Everything under `engagements/sample-*` is invented. No real company or person names.
- A fact about Claude goes in the compendium with a source link, or carries ⚠ Unverified. Data files cite the compendium page; they do not restate facts without a link.
- Link to existing pages; do not copy their content.
- Tests live in `tests/` and run with `python3 -m unittest discover -s tests`.
