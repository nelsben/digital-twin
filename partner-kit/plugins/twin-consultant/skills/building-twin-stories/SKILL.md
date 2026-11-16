---
name: building-twin-stories
description: Picks the next story from a twin's generated backlog and works it with the consultant one task at a time, keeping each task's status true. Use when a consultant wants to build or continue a twin.
---

# Building twin stories

## Purpose

Work the generated backlog of one role twin with the consultant: pick the
next story, do its tasks one at a time in the customer's delivery repo, and
keep each task's status true. You build; you do not plan. A plan that is out
of date goes back to `planning-a-twin`.

Words that collide: the persona card is `card.json`, the record of one role
at one customer, not the persona voice file
(`starter-kit/templates/persona/persona.md`) and not a task card in
`agents/tasks/`. The backlog is the generated `backlog.json` of one persona,
not this repo's GitHub issues or task cards.

## Inputs

| Input | Where | Required |
|---|---|---|
| Persona folder | `engagements/<customer>/personas/<persona-id>/`, with `card.json`, `levelled.json` and `backlog.json` | yes |
| The customer's delivery repo | where the twin is built; ask the consultant | yes, before build work |
| A story or task to work | from the consultant, or picked in step 2 | no |

Commands, from `${CLAUDE_PLUGIN_ROOT}/scripts/twincard/cli.py`: `backlog
<persona-dir>` checks the plan is current and rewrites `backlog.json` and
`backlog.md`, keeping every status; `dashboard <persona-dir>` rewrites
`dashboard.html` (what is blocked at the top; every open pilot story with
its tasks, owners and steps). Task templates: `${CLAUDE_PLUGIN_ROOT}/data/task-library.json`.

## Steps

1. **Check the plan is current.** Run
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/twincard/cli.py backlog <persona-dir>`.
   If it prints `levelled.json is missing or out of date. Next: run the level command.`
   or validation errors, say so and point to `planning-a-twin` to level and
   review the plan again. Do not run `level` or `all` yourself, pick no
   story and change nothing.
2. **Pick the next story.** Order: stories in the pilot that have a
   priority, lowest number first; then stories in the pilot with no priority
   (the foundation stories, in backlog order); then the rest by priority.
   Skip a story that is done, any story whose `gated_by` lists anything
   (such as blocker `connector-cannot-write`, an open question with its
   `spike`, or a compliance `sign-off`) and any story whose `ready` is not all
   met. For each in-pilot story you skip, name what gates it or the unmet
   check, and its owner (from the card's open question). Show the pick (format
   below) and ask the consultant to confirm it or name another story. Start
   nothing until they do.
3. **Work one task at a time**, the first task of the story that is not
   done, in backlog order. Set it to `in-progress` (step 5). Read its `how`
   steps and its `done_when`. Open the page each step's `link` names (paths
   are relative to the kit repo: `starter-kit/`, `docs/compendium/`) and do
   the work with the consultant in the customer's delivery repo, using that
   template, runbook or page as it stands. Do not restate it.
4. **Mark it done** only when its `done_when` holds and the consultant
   confirms. If part of `done_when` is not met, say which part, keep the
   task `in-progress`, and say who it waits on.
5. **Change a status** only in `backlog.json`, only the task's `status`
   value, and only forward: `todo` to `in-progress` to `done`. Story, feature
   and epic statuses are derived; never set them. Then run the `backlog`
   command and the `dashboard` command, so `backlog.md` and `dashboard.html`
   agree.
6. **End the session** with the summary below.

## Rules while building

- **Start level, not ceiling.** Build each task at its `autonomy.start` in
  `levelled.json` (level 1 for every pilot task), not at `autonomy.ceiling`.
  Tool settings follow the `tools` list there. Moving up a level is its own
  task, on scorecard evidence.
- **Evals before the instructions.** The kit's rule holds for the twin's
  own work: eval cases are written before its `SKILL.md`.
- **Real examples only.** A task that needs real examples from the
  `skill-owner` (such as `S-C1.collect-examples`) waits for them. Invent no
  example, input or expected result.
- **Admin-only steps are handed over.** Work in an admin console, approving
  access to a system, the identity provider or device management is done by
  the customer's admin, not by you. Hand over the step's link and the exact
  values from `levelled.json` (for a tool: its system, use, permission and
  the tasks that share it; for access: system, access and identity; the
  settings baseline; the distribution). Leave the task `in-progress` until
  the consultant says the admin has done it. Example:
  `S-C1.tool-always-allow.hubspot-read`.
- **Rules from the interviews.** A story's `constraints` field and its
  `Keeps:` acceptance lines are rules in the interviewee's words. The twin's
  instructions keep each one as said, and an eval case checks it. Its
  `wanted_change` is asked for, not planned: build nothing for it unless
  the consultant adds it to the card through `planning-a-twin`.
- **How the output is delivered.** A task story's `delivery` field says
  where its output ends up and who puts it there: it stays in the
  conversation, a routine in Slack posts it itself, a person sends or
  files the twin's draft, or the twin writes it with the tools it names.
  When a person sends or files the draft, the write tool stays Blocked
  while you build, and the story's `deliver-draft` task says who does it.
  Build the twin to end in that draft; never open the write yourself.
- **Reading a story.** What `ready`, `target`, a `drafted` statement, the
  `Start from` steps, `data_providers` and the backlog's `spikes` mean is in
  [references/reading-a-story.md](references/reading-a-story.md). Build only
  when every check is met; a drafted statement goes back to the interviewee.
- **Who it waits on.** Name the task's `owner_role` and its `owner_name`.
  When a role has no named person, `owner_name` is empty and
  `acting_owner` is the technical owner, who answers for it until the
  customer names someone. `backlog.md` lists those roles once, on its
  `Roles with no named person` line; ask the consultant to get a name.

## Output format

When picking:

```markdown
## Next story: S-C1 Account brief before a customer call
Why: in the pilot, priority 1, no gates. Skipped: <story: what gates it, owner>
Statement: <statement> (<card, or drafted: confirm with the interviewee>)
Fields: <each field: value>
Acceptance: <each line>
Target: <the target text>. Ready: <yes, or each unmet check: its note>
Delivery: <the story's delivery field>
Tasks: <id> (<owner role>, <owner name or acting owner>, <status>), ...
First task: <id>, owner <owner role>, <owner name>. Built at level <autonomy.start>, not <ceiling>.
Confirm this story, or name another.
```

At the end of each session:

```markdown
Done: <task ids marked done>
In progress: <task id>: waits on <owner role or person> for <what>
Next story: <id> <title>
Dashboard: <persona-dir>/dashboard.html (the next story is open in its Backlog section)
```

## Guardrails

- **Generated files are never edited by hand.** You change only `status`
  values in `backlog.json`; `backlog.md` and `dashboard.html` come from the
  commands. `card.json` and `levelled.json` are changed through
  `planning-a-twin`, not here.
- **Ask, do not guess.** A missing value, example, approver or repo is a
  question to the consultant, never a guess.
- **Sample folders.** Under `engagements/sample-*` everything is invented.
  Never put a real customer's names or data there.
- **No web search or fetch** when the task's data is highly sensitive or
  deal material; the `fields` of the story give its level.

## Evals

The cases in [evals/evals.json](evals/evals.json) and
[evals/trigger-evals.json](evals/trigger-evals.json) were written before
this file. They have not been run yet.
