---
name: planning-a-twin
description: Levels a valid persona card into the twin's plan, backlog and dashboard, and explains blockers, warnings, open points and overrides. Use when a consultant wants the plan made, checked or changed.
---

# Planning a twin

## Purpose

Turn a filled persona card into the plan for one role twin, and help the
consultant understand it and act on it. You run the kit's command and explain
what it found; you never decide for the customer.

Words that collide: the persona card is `card.json`, the record of one role
at one customer. It is not the persona voice file
(`starter-kit/templates/persona/persona.md`) and not a task card in
`agents/tasks/`. The backlog is the generated `backlog.json`, not this
repo's GitHub issues.

## Inputs

| Input | Where | Required |
|---|---|---|
| Persona folder | `engagements/<customer>/personas/<persona-id>/`, with `card.json` | yes |
| Customer profile | `../../customer-profile.json` from the persona folder | yes |
| An override | the value, the reason and the approver's name, from the consultant | only to record one |

The command: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/twincard/cli.py all <persona-dir>`.
It validates the card, then writes `levelled.json`, `backlog.json`,
`backlog.md` and `dashboard.html`, by the rules in
`${CLAUDE_PLUGIN_ROOT}/data/rules.json` and `${CLAUDE_PLUGIN_ROOT}/data/plan-fit.json`.

## Steps

1. **Run all** and read its output.
   - Exit 1 with validator lines (`<record>:<path>: <message>. Next: <fix>`):
     the card does not validate and nothing was written. Say so, quote the
     lines, point to `filling-persona-cards`, and stop. Do not fix the card.
   - Exit 1 with a `level: blocked` line: a blocker; all four files were
     still written. Exit 0: no blocker. Exit 2: a usage error; quote it.
2. **Read `levelled.json`** and report in this order (format below):
   1. **Blockers**, each explained as in "Explaining a blocker".
   2. **Rests on an unverified fact**: every decision, `connectors` entry,
      `tools` permission, persona starting point and blocker or warning
      entry with `"unverified": true` (the dashboard's list of the same
      name). For each: what it is, its cite, what must be confirmed (from
      its reason or message) and with whom: Anthropic, in writing, for a
      fact about its own products; the vendor for a fact about theirs; the
      customer's admin for their own system.
   3. **Undecided**: each null decision with code `decision-undecided`.
      Say what the page lacks (its reason) and that a person at the customer
      must decide it, recorded as an override with a named approver. Propose
      no value. A null with code `field-open` waits for an answer instead.
   4. **Warnings, grouped by code**: one line per code, naming every task or
      `persona` it is about, with its message and fix.
   5. **Open questions** from the card: id, question, the tasks it blocks,
      owner and due date (say so when a due date is empty).
3. **Close** with the summary below.

## Explaining a blocker

Give its code, what it is about (a task id or `persona`), what it means in
one plain sentence (from `message`), the compendium page in `cite`, and the
ways out the design allows:

- **The answer was wrong.** Correct the card or the profile with the
  consultant, from what a person said, and rerun.
- **Change the task**, as `fix` says (for example end in a draft a person
  sends, and remove the write from the card).
- **Move the customer** to the plan or org the blocker names, when it names one.
- **An override**, only where the design allows one for that decision.

Overrides are allowed for `runtime`, `identity`, `autonomy.start`,
`autonomy.ceiling`, `data_controls` and `memory` only. `connectors` and
`plan_fit` follow from the others: overriding either raises blocker `override-not-allowed`
and is not applied, so blocker `connector-cannot-write` has no override way
out. Never propose an override yourself to make a blocker disappear; offer
the ways out and let the consultant choose.

## Recording an override

Write one only when the consultant gives all three: the value, the reason,
and the named person at the customer who approved it. If any is missing, ask
for it and write nothing. Append one entry to the card's `overrides` list, in
the design's shape, and change nothing else on the card:

```json
{"task": "T4", "decision": "autonomy.ceiling", "value": 2, "reason": "<the consultant's words>", "approved_by": "<name and role at the customer>"}
```

Never set `autonomy.start` or `autonomy.ceiling` higher than the rule's
result unless the consultant asks for exactly that and names the approver.
After the rerun, state the rule's own result next to the override (in
`levelled.json` it is `overridden.rule_result`) and say the dashboard will
show the decision as Overridden, with the reason and the approver. The run
raises warning `override-applied` for it.

## After any change

Change the card or the profile only with the consultant's agreement, then
run all again. Before the change, note the decisions, the blocker and
warning codes, and the story and task ids in `levelled.json` and
`backlog.json`. After it, report what changed between the two runs:
decisions (old value, new value), blockers and warnings added or removed,
and backlog stories and tasks added, dropped or retired (the command prints
one line for each retired item).

## Output format

```markdown
## Plan for <role> at <customer>
### Blockers
- connector-cannot-write (C4): <one plain sentence>. Cite: <page#anchor>. Ways out: <each>
### Rests on an unverified fact
- C5 runtime: <what>. Confirm <what> with <whom>. Cite: <page#anchor>
### Undecided: a person decides, recorded as an override
- T4 autonomy.ceiling: <what the page lacks>
### Warnings, by code
- mail-read-only (C3, C4): <message> Next: <fix>
### Open questions
- OQ-1 (blocks C5): <question> Owner: <owner>. Due: <date or none>.

Dashboard: engagements/<customer>/personas/<persona-id>/dashboard.html
Blockers: <n>. Warnings: <n>. Open questions: <n>.
Plan complete: yes | no (<completeness below 100%, an open question blocking a pilot task, a blocker>)
Next step: build the stories with building-twin-stories (not started here).
To file the backlog in a tracker: the backlog command with --plan-out <file>. Nothing is imported from here.
```

"No blockers." when there are none. "Plan complete" is `complete` in
`levelled.json`; completeness is on the output's `validate` line.

## Guardrails

- **Generated files are never edited by hand.** Change `card.json` or the
  profile, then run the command again. `levelled.json`, `backlog.json`,
  `backlog.md` and `dashboard.html` are written only by it.
- **Ask, do not guess.** No value, reason, approver, owner or answer that the
  consultant, the card or the profile did not give you.
- **Do not start building.** Picking and doing stories is `building-twin-stories`.
- **Sample folders.** Under `engagements/sample-*` everything is invented;
  never put a real customer's names or data there.
- **No web search or fetch.** The persona folder can hold confidential or
  deal material.

## Evals

The cases in [evals/evals.json](evals/evals.json) and
[evals/trigger-evals.json](evals/trigger-evals.json) were written before
this file. They have not been run yet.
