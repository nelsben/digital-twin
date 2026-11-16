---
name: account-brief-before-a-customer-call
description: "FILL IN: check this draft. Produces: One-page account brief. Use when FILL IN the words people type (the card's trigger is person)."
---

<!-- Seeded by the build command: name from card tasks.C1.name (derived); description from card tasks.C1.output.what and tasks.C1.trigger. -->

# FILL IN: Skill title (card `tasks.C1.name`: Account brief before a customer call)

<!--
How to use this template: every "FILL IN" marker is yours to replace. Delete
each marker, and each comment like this one, when you are done. Keep the body
under 150 lines: move detail into references/ (see "Reference files" below).
Authoring guide: starter-kit/docs/authoring-skills.md
Anthropic's guidance: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
-->

## Purpose

- I want my twin to brief me on the account before each call. (From card `tasks.C1.story_want`.)
- So that I walk into the call already knowing the account. (From card `tasks.C1.story_benefit`.)
- FILL IN: what the skill does not cover, so Claude does not stretch it.

## Inputs and connectors

FILL IN: list everything the skill reads. Name each MCP tool in full, as
`Server:tool`. Give the data class of each source (internal, confidential,
highly sensitive or PHI; see docs/compendium/10-sensitive-data.md) and say
whether access is read or write.

| Source | What it gives | Data class | Access | Permission at the starting level | Seeded from |
|---|---|---|---|---|---|
| FILL IN `Server:tool` (system hubspot) | FILL IN | confidential | read | always-allow | levelled `tools` (hubspot read); card `tasks.C1.data_class` |
| FILL IN `Server:tool` (system google-drive) | FILL IN | confidential | read | always-allow | levelled `tools` (google-drive read); card `tasks.C1.data_class` |
| FILL IN a file the user attaches | FILL IN | FILL IN | read | FILL IN | none |

Required from the user: FILL IN the facts the skill cannot work without (for
example the account name or the date range). If one is missing, follow
"Guardrails" below.

## Steps

FILL IN: the order of work, and why each step matters. Write the steps a
capable colleague would not already know. Cut the rest.

1. FILL IN: gather. Read the sources above, and note what is missing.
2. FILL IN: analyse. State the rule or judgement that applies.
3. FILL IN: draft the output in the format below.
4. FILL IN: check the draft against the checklist in
   [references/example-reference.md](references/example-reference.md).
5. Present the draft. Do not send or publish it unless the autonomy level
   in the story allows it.

Match instruction detail to how fragile the step is: prose for judgement
work, a template for work with a standard shape, an exact script for
fragile calculations.

## Output format

FILL IN: show the shape of the output (headings, table, length, tone). If it
is longer than about 15 lines, move it to a file in `references/` and link it.

```markdown
## FILL IN: heading
- FILL IN: item, with a link to its source record
```

## Guardrails

Keep these. They hold for every twin skill. Add more below them, each
with the failure from an eval that earned it.

- **Twin marker on every write.** Any tool call that creates or changes a
  record adds the twin marker (a "Last updated by twin" field or a note
  prefix; see docs/compendium/15-governance-and-performance.md), so the
  system's own history shows what the twin did. FILL IN: the marker text for
  each connector this skill writes to. If the skill only reads, say so here.
- **No web tools for highly sensitive data.** Keep this line if any input is
  highly sensitive or may hold MNPI (material non-public information). Do
  not use web search or web fetch for these tasks, because a query can reveal
  deal intent. If the task needs outside facts, ask the user to supply them.
  FILL IN: delete the line if no input is highly sensitive.
- **Ask, do not guess.** If a required input is missing, empty or
  contradictory, say exactly what is missing and ask the user. Do not fill
  gaps with plausible values. Every figure and claim in the output links to
  its source.
- FILL IN: any further rule, such as "never quote a closed opportunity as
  open".

## Reference files

Claude reads these only when a step points to them, so they cost nothing
until then. Link each one directly from this file (one level deep, never from
another reference).

- [references/example-reference.md](references/example-reference.md): FILL IN
  one line on what it holds and when to open it. Replace this example file,
  or delete it if the skill needs no reference.
- FILL IN: add one line per further reference file.

## Evals

The cases in [evals/evals.json](evals/evals.json) and
[evals/trigger-evals.json](evals/trigger-evals.json) were written before this
skill, from real examples. Re-run them after every change.

Real examples counted on the card: good 2, bad 1. (From card `tasks.C1.examples.good` and `tasks.C1.examples.bad`; where they are kept is in `tasks.C1.examples.where`.) FILL IN: one case in evals.json per good example.
