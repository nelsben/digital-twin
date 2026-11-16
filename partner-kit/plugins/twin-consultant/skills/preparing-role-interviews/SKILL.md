---
name: preparing-role-interviews
description: Sets up role interviews for a twin, making the persona folder, one notes file per interviewee and a tailored question plan. Use when a consultant is about to interview people in a role.
---

# Preparing role interviews

## Purpose

Before a consultant interviews people in one role at one customer, set up the
files they will write in and tell them which questions to ask each person.
You prepare; you never answer. Filling the persona card from the notes is a
separate step (filling-persona-cards), and so is writing the persona voice.

Words that collide: the persona card is `card.json`, the record of one role.
It is not the persona voice file (`starter-kit/templates/persona/persona.md`)
and not a task card in `agents/tasks/`. This step edits neither, and never
writes `card.json`.

## Inputs

| Input | Where | Required |
|---|---|---|
| Customer folder | `engagements/<customer>/` | yes |
| Role name | from the consultant, for example "Portfolio operations manager" | yes |
| Who will be interviewed | role labels, the date of each interview, the interviewer | yes |
| Customer profile | `engagements/<customer>/customer-profile.json` | no |
| Existing card | `engagements/<customer>/personas/<persona-id>/card.json` | no |

If the customer folder, the role name or who will be interviewed is missing,
say exactly which is missing and ask. Do not pick a role for the consultant;
you may list the persona folders that already exist as options. Create
nothing until you have all three.

Files you read, from this kit:

- The interview guide: `${CLAUDE_PLUGIN_ROOT}/templates/interview-guide.md`
- The notes template: `${CLAUDE_PLUGIN_ROOT}/templates/interview-notes.md`
- The field catalogue: `${CLAUDE_PLUGIN_ROOT}/data/fields.json`
- The industry pack: `${CLAUDE_PLUGIN_ROOT}/data/industry-packs/<industry>.json`

## Steps

1. **Read the customer profile** if it exists. Its `industry` names the pack
   to read. With no profile, say so and use
   `${CLAUDE_PLUGIN_ROOT}/data/industry-packs/general.json`, and take the
   customer id for the notes header from the folder name until a profile
   sets it. Say which you did.
2. **Settle the persona id.** If a persona folder for this role already
   exists, use it. Otherwise derive a kebab-case id from the role name
   ("Portfolio operations manager" gives `portfolio-operations-manager`),
   show it, and wait for the consultant to confirm or change it.
3. **Read the existing card**, if the persona folder has `card.json`. Do not
   change it.
4. **Create the folders**: `engagements/<customer>/personas/<persona-id>/interviews/`.
5. **Create one notes file per interviewee** at
   `interviews/<yyyy-mm-dd>-<who>.md`, copied from the notes template. The
   date is the interview date. `<who>` is a kebab-case role label
   (`head-of-portfolio-operations`, `associate`), never a person's name
   unless the consultant says to use it. If that file name exists already,
   add `-b`, `-c`. Fill only the header table: Customer id (the profile's
   `customer`), Persona id, Date, Interviewee's role, Interviewer. Leave
   every other line of the template exactly as it is.
6. **Print the plan** (format below).

## Which questions to ask, and which to confirm

Use the guide's question ids as they are: P1 to P6 once per person, F1 to
F9 once per task. Never renumber, reword or drop a question in the files.

With no card, every question is to ask. With a card, a question is
**confirm-only** for a person or a task when every field it fills (its
"Fills" line in the guide, which matches `asked_by` in the catalogue) has
either an `answered` or `default` entry in the card's `provenance`, or, for a
field that is not required, a value on the card. Key fields such as `id`
and `tasks[].feature` do not count. Everything else is **to ask**, and the
plan says which field is missing. For example, question F3 stays to ask while
`tasks.T1.examples.good` is open, and question F1 stays to ask while
`tasks.T4.users` is empty. For a confirm-only question, read back the card's
answer so the consultant can say "is this still right?".

## Prompts from the pack

Turn each of the pack's `typical_tasks` into a prompt the consultant can
read out after question F1, using the task's `name` as written:
"Do you do anything like Company brief?". Say which pack it came from. The
general pack lists no typical tasks; say so and give no prompts.

## Output format

```markdown
## Interview plan: <role name> at <customer>

Pack: <pack id> (from the customer profile | no profile, so general)
Persona folder: engagements/<customer>/personas/<persona-id>/
Notes files: interviews/2026-11-20-<who>.md, ...

### Persona questions (each person)
| Question | Ask or confirm | On the card now |
|---|---|---|
| P1 Your role | confirm | Deal-team associate; Deal team; managed |

### Task questions
| Task | Question | Ask or confirm | Missing on the card |
|---|---|---|---|
| T1 Prepare a one-page company brief | F3 | ask | examples.good, examples.bad |

### Prompts from the <pack id> pack (after question F1)
- "Do you do anything like <task name>?"
```

Keep the plan short: one line per question or per task and question.

## Guardrails

- **Ask, do not guess.** Missing input: name it and ask. Never write an
  answer, a figure or a task into a notes file or the plan that the
  consultant or the card did not give you.
- **Words said to the interviewee stay plain.** Read out the guide's Ask
  lines and the pack prompts as written. Do not add technical terms when
  you rephrase.
- **Names.** Under `engagements/sample-*` everything is invented. Anywhere,
  a notes file name holds a role label, not a person's name, unless the
  consultant asks for the name.
- **No web search or fetch.** The customer folder can hold confidential
  material; everything you need is in the kit and the folder.

## Evals

The cases in [evals/evals.json](evals/evals.json) and
[evals/trigger-evals.json](evals/trigger-evals.json) were written before this
file. Re-run them after every change.
