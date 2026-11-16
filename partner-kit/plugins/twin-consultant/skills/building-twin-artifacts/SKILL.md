---
name: building-twin-artifacts
description: Takes a twin's built artifacts from scaffolded to evals-passing with the consultant, evals from real examples first, then the instructions, the checks and a recorded result. Use after build.
---

# Building twin artifacts

## Purpose

Work with the consultant to turn each artifact the `build` command
scaffolded under `<persona-dir>/build/` into one that passes its evals, and
record that result. You write eval cases and instructions; you never write
or invent an eval result. A plan that is out of date goes back to
`planning-a-twin`; picking the next story is `building-twin-stories`.

Words that collide: an artifact is one task's entry in `build/build.json`
(a `SKILL.md` folder, and for some tasks a wrapper such as `agent.json`),
not a backlog story. `check` and `record` are commands of
`${CLAUDE_PLUGIN_ROOT}/scripts/twincard/cli.py`, not the repo's tests.

## Where real material lives

Real customer examples, eval prompts built from them, and every eval run
and its output stay in the customer's environment or the engagement's
private store. Never copy them into this repo. Only the fictional samples
(`engagements/sample-*`) live here, and they stay at drafted: no evidence
file is ever added to a sample.

## Inputs

| Input | Where | Required |
|---|---|---|
| Persona folder | `engagements/<customer>/personas/<persona-id>/`, with `card.json`, `levelled.json` and `build/build.json` | yes |
| Real examples | counted on the card as `tasks[].examples.good` and `tasks[].examples.bad`, kept where `tasks[].examples.where` says | yes, before step 3 |
| The task's owner | `tasks[].skill_owner` on the card | yes, for steps 3 and 7 |
| A starting point | `tasks[].starts_from`, seeded as a "Start from" line in the scaffold | no |

## Steps

Do one artifact at a time, in pilot order: artifacts with `in_pilot` true
in `build.json`, by the card's `tasks[].priority`, lowest first.

1. **Run build.** `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/twincard/cli.py build <persona-dir>`
   (add `--all-tasks` past the pilot). It never overwrites a file a person
   changed. If it refuses, say why and stop; a stale plan goes back to
   `planning-a-twin`.
2. **Run the task without the new instructions first.** With the
   consultant, in the customer's environment, run the real task on a real
   example with nothing from `build/` loaded. Note each failure in plain
   words. These failures are what the evals must catch.
3. **Turn the counted examples into eval cases**, with the task's owner.
   One case in `evals/evals.json` per good example, one for each bad
   example's failure, a missing-data case and a should-not-trigger case from
   a task people confuse with this one. Fill `evals/trigger-evals.json` with
   the owner's own words and near misses. Follow the mapping table in
   `starter-kit/docs/authoring-skills.md` and the method in
   `docs/compendium/03-skills-authoring.md`. If the examples are not in
   hand, stop: story task `S-C1.collect-examples` is the pattern, and it
   waits for them.
4. **Write the minimum `SKILL.md`** that fixes the failures from step 2.
   Start from the "Start from" line when there is one. Keep the three
   guardrails, keep the frontmatter to `name` and `description`, and move
   detail into `references/`. Replace every FILL IN marker.
5. **For a hosted agent** (kind agent-bundle), fill `agent.json`'s
   `system` from the persona (`voice.serves`, `voice.tone`, `voice.norms`,
   `voice.never`, `voice.ask_before`, `voice.escalate_to`) and from the
   runbook's steps that `build.json` names, then `model`, the server URLs
   and the `skill_id` the upload returns. Keep `environment.json`'s
   networking limited.
6. **Run the evals with the consultant.** Use `skill-creator`'s benchmark,
   which runs every case with and without the new instructions, then its
   description tuning against `trigger-evals.json`. Once the role is
   packaged, use `claude plugin eval` in its two-arm mode instead. Run on
   Haiku, Sonnet and Opus, or on each model the customer has enabled, and
   note the pass rate per model in the story.
7. **Run check, then record.** Run
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/twincard/cli.py check <persona-dir> <task-id>`
   and fix every line it prints until it exits 0. Then run build again: it
   sets drafted once no FILL IN is left. Save the tool's own output file,
   unedited, under `build/evidence/<task-id>/` in the customer's copy, and
   run `record <persona-dir> <task-id> --status evals-passing --evidence <file> --by <name>`.
   A pass mark below 100 needs `--pass-mark` and `--approved-by` with the
   owner's name.
8. **End the session** with the summary below.

What `check` tests, the evidence fields `record` reads, and every refusal
are in [references/check-and-record.md](references/check-and-record.md).

## Packaging and deployment

Once artifacts are evals-passing, the consultant runs
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/twincard/cli.py package <customer-dir>`.
It writes the customer's marketplace, the hosted bundles and `build/deploy.md`,
the deploy checklist, and sets packaged. With `--include-drafts` it writes a
draft to look at with the customer, never to publish, and records nothing.

- **The customer's admin runs `deploy.md`** in the customer's org, in order.
  Neither you nor the consultant does it for them.
- **The consultant records.** When the admin reports a step done, save
  their note under `build/evidence/<task-id>/` in the customer's copy and run
  `record <persona-dir> <task-id> --status deployed --by <admin> --evidence <note>`;
  then `--status verified` with the runbook's check-it-worked result.
- **Credentials live in the customer's secret store**, never in the
  engagement folder. A note or a checklist names an environment variable or
  a placeholder such as `<agent-id>`, never a key, token, password, id or
  address.
- **A step `deploy.md` lacks is a gap in the backlog.** Tell the
  consultant; never add it to `deploy.md` by hand.

## Rules

- **Never write or invent an eval result.** `record` reads only the file
  the eval tool wrote. Do not type a pass rate, edit a result file, or build
  one by hand. If a run did not happen, the status stays drafted.
- **Evals before the instructions.** Steps 2 and 3 come before step 4,
  always.
- **One status at a time, never backwards.** Only the package command
  sets packaged. `record` sets evals-passing on the eval tool's file, and
  deployed and verified on the notes from the customer's deployment, never
  on your say-so.
- **A refusal is an answer.** When `check` or `record` refuses, show its
  line and its "Next:" step to the consultant. Do not work around it.
- **Real examples only.** Invent no example, input or expected result for
  a real customer.

## Summary

```markdown
## <persona>: <task-id>, <status before> -> <status after>
- Failures without the new instructions: <list>
- Eval cases: <count> (good <n>, bad <n>, missing data, near miss)
- check: <0 problems, or the lines still open>
- Pass rate per model: Haiku <x>, Sonnet <x>, Opus <x>; baseline <x>
- Evidence: build/evidence/<task-id>/<file> (customer's copy), recorded by <name>
- Next: <the next artifact in pilot order, or what blocks this one>
```
