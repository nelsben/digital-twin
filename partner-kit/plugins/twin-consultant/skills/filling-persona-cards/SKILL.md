---
name: filling-persona-cards
description: Turns role interview notes into a valid persona card (card.json), tracing every field to its answer. Use when a consultant has interview notes for a role and wants the card created or updated.
---

# Filling persona cards

## Purpose

Read the interview notes in one persona folder and write `card.json`: every
field from what the notes say, each with a `provenance` entry naming where
it came from, then validate. You never invent an answer, a figure or a name.

Words that collide: the persona card is `card.json`, the record of one role
at one customer. It is not the persona voice file
(`starter-kit/templates/persona/persona.md`) and not a task card in
`agents/tasks/`. Do not edit either of those here. Levelling the card is a
separate step; do not run it.

## Inputs

| Input | Where | Required |
|---|---|---|
| Persona folder | `engagements/<customer>/personas/<persona-id>/` | yes |
| Interview notes | `interviews/*.md` in that folder, one or more | yes |
| Customer profile | `../../customer-profile.json` from the persona folder | yes (see step 1) |
| Discovery answers | `discovery.md` in the customer folder, if there is one | no |
| Existing card | `card.json` in the persona folder | no |

From this kit: the card template `${CLAUDE_PLUGIN_ROOT}/templates/card.json`,
the field catalogue `${CLAUDE_PLUGIN_ROOT}/data/fields.json`, the interview
guide `${CLAUDE_PLUGIN_ROOT}/templates/interview-guide.md` (its "Listen for"
lines map words to allowed values), and the pack the profile's `industry`
names, under `${CLAUDE_PLUGIN_ROOT}/data/industry-packs/`.

No notes files, or no persona folder: say which is missing and ask.

## Steps

1. **Check the customer profile.** If `../../customer-profile.json` is
   missing, say so and offer to create it from
   `${CLAUDE_PLUGIN_ROOT}/templates/customer-profile.json` and the
   engagement's discovery answers. If `discovery.md` is missing and the
   consultant gives discovery answers, offer to create it from
   `${CLAUDE_PLUGIN_ROOT}/templates/discovery.md` and write the answers in
   its rows first. Follow
   [references/customer-profile.md](references/customer-profile.md). Do not
   guess plan, identity, device or compliance answers.
2. **Start the card.** No `card.json`: copy the template and set `id` (the
   folder name) and `customer` (the profile's `customer`). A `card.json`
   exists: load it and keep every field whose `provenance` status is
   `answered`, with its value and source, even if your reading differs. If new
   notes contradict a kept answer, add an open question; do not overwrite it.
3. **Build the lists.** Task ids come from each notes file's "Task id:" line.
   Features come from the closing table of the notes: the name in their
   words, the id in kebab-case (`call-preparation-and-follow-up`). Each
   system a task reads or writes is a system id from the profile; `inputs`
   and `writes` are positional (`tasks.C2.writes[0].action`). Delete
   template placeholder entries that stay empty, so an unused list is `[]`.
4. **Fill each field.** For every card field in the catalogue, look only at
   the answers under the question ids its `asked_by` lists (for example
   `tasks[].trigger` only under question F5). Set the value and write one
   `provenance` entry per the table below. Detail, worked examples and the
   number rules are in [references/field-rules.md](references/field-rules.md).
5. **Write `card.json`**, then run the validate command (step 6).
6. **Validate and fix.** Run
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/twincard/cli.py validate <persona-dir>`.
   Each error reads `<record>:<path>: <message>. Next: <fix>`. Fix what the
   notes can answer, run it again, and stop when it prints `Valid.` or what
   is left needs a person (an owner, a due date, a missing answer).
7. **Report** (format below).

## Status of each field

| Status | When | Entry |
|---|---|---|
| `answered` | The notes say it, under a question id that `asked_by` lists, or a discovery row does | `{"status": "answered", "source": "interviews/<file>#F2"}` or `"source": "discovery.md#A1"` |
| `default` | The notes are silent and a pack typical task with the same task, or a catalogue default, gives the value | `"source"`: the pack file, such as `data/industry-packs/b2b-software.json`, or the compendium page |
| `assumed` | A working guess: the consultant's own, or one a rule below calls for | the value, and `"owner"`: who must confirm it |
| `open` | The notes do not say, or two people disagree | the field is empty (`null`, `""` or `[]`; `false` is a value), adds `"owner"` and `"due"`, plus an `open_questions` entry |

Every `open` field gets an `open_questions` entry: the question in plain
words, `blocks` naming every task id it holds up, `owner`, `due`. Take
owner and due from the notes' open-questions table or from the consultant;
if neither gives them, ask. Never make them up.

## Rules that are easy to get wrong

- **Sponsor goal.** `outcome.sponsor_goal` heard only from an interviewee
  (question P3) is `assumed`, with `owner` the sponsor named in the profile's
  `owners.sponsor`, until the sponsor confirms it. It is `answered` when the
  sponsor's own words are in a discovery answer (question A1) or the
  consultant says the sponsor confirmed it.
- **Disagreement.** When two interviewees give answers that cannot both be
  true (a different number, allowed value or yes/no), do not pick one or
  average them. The field is `open` and empty, and the open question quotes
  both answers with their file names. Two tones add to each other: combine
  them, citing both files with `; `. A task two people put under different
  features keeps the first file's, plus an open question (field rules).
- **Several sources.** An answer from more than one person cites each, with
  `; `: `"interviews/a.md#P2; interviews/b.md#P2"`.
- **Said in conversation.** An answer the consultant gives in the chat is
  written first, to its row in `discovery.md` (questions A1 to G4) or to a
  dated notes file `interviews/<yyyy-mm-dd>-<who>.md` under the question's
  heading, then cited there.
- **Open is empty.** A working guess is `assumed`, with an owner, not `open`.
- **Today, not the wish.** `tasks[].trigger` is how the task starts now;
  "ideally" or "later" goes in an open question. The rules for question F8,
  question F7, per-something rates, rules, wished changes and surfaces are in
  [references/field-rules.md](references/field-rules.md). A story want or
  benefit is the interviewee's words, first person, or empty: invent none.
- **Only what was said.** No figure, name or system that is not in the
  notes, the profile, the discovery answers or the consultant's message. A
  field the notes do not touch stays empty; if it is required it is `open`.
- **The interviewee's own pick wins.** "Low to medium. Say medium." gives
  `medium`.

## Output format

End the response with:

```markdown
Completeness: <n>% (from the validate output)
Still open or assumed:
- <field path>: <open|assumed>, owner <owner>, due <date or none>
Next step: level the card (a separate step; not run here).
```

## Guardrails

- **Ask, do not guess.** Missing or contradictory input becomes an open
  field with an owner, or a question to the consultant, never a value.
- **Sample folders.** Under `engagements/sample-*` everything is invented:
  `fictional` is true in the profile and any name you write is invented or
  from the notes.
- **No web search or fetch.** Notes can hold confidential or deal material.
- **Write only** `card.json`; the profile and `discovery.md` when the
  consultant agrees in step 1; a discovery row or a new dated notes file for
  an answer given in conversation. Never change what existing notes say,
  the persona voice file or a task card.

## Reference files

- [references/field-rules.md](references/field-rules.md): field-by-field
  rules, number conversions and worked examples. Open it at step 4.
- [references/customer-profile.md](references/customer-profile.md): creating
  a missing customer profile. Open it at step 1.

## Evals

The cases in [evals/evals.json](evals/evals.json) and
[evals/trigger-evals.json](evals/trigger-evals.json) were written before this
file. Re-run them after every change.
