# 05 — The persona-card workflow

This page takes a consultant from a qualified customer to a persona card, a levelled plan, a backlog and a dashboard. Each step is tied to a phase of the [engagement model](01-engagement-model.md). The tools are in the [partner kit](../../partner-kit/README.md), which is partner-only. The design of record is [partner-kit/docs/design.md](../../partner-kit/docs/design.md).

The **persona card** is `card.json`, the record of one role at one customer. It is not the persona voice file in `starter-kit/templates/persona`, and it is not a task card in `agents/tasks`.

```
interview notes ──► persona card ──► levelled plan ──► backlog ──► dashboard
                     card.json       levelled.json     backlog.json   dashboard.html
```

There are four skills, one per step, and five commands: `validate`, `level`, `backlog`, `dashboard` and `all`. The [plugin README](../../partner-kit/plugins/twin-consultant/README.md) has the usage, the exit codes and the table of skills. This page does not repeat them.

## Phase 0: Qualify

Start `customer-profile.json` from the [template](../../partner-kit/plugins/twin-consultant/templates/customer-profile.json), in `engagements/<customer>/` ([starting a real customer folder](../../engagements/README.md#starting-a-real-customer-folder)). It is the fit note from the phase table: the plan, the data classes, the systems and the sponsor. Fill what you know. Leave the rest open, with an owner.

- Skill: none. `filling-persona-cards` offers to create a missing profile in Phase 1.
- Command: none. `validate` checks the profile together with the first card.
- Done when: a sponsor is named in the profile and the first role is chosen.

## Phase 1: Discovery

1. **Prepare the interviews.** Skill: `preparing-role-interviews`. It makes the persona folder, one notes file per interviewee and a question plan. No command. Interview 2 to 3 people per role.
2. **Run them** with the [interview guide](../../partner-kit/plugins/twin-consultant/templates/interview-guide.md). Write what people say, in their words, in the notes files. The questions in [section F of the discovery questionnaire](02-discovery.md#f-roles-and-tasks-run-per-role-in-interviews) are the summary of the guide.
3. **Fill the card from the notes.** Skill: `filling-persona-cards`. Every field gets a source, and every answer still missing becomes an open question with an owner and a due date. The skill invents nothing.
4. **Validate.** Command: `validate`. Fix what the notes can answer. What is left needs a person at the customer.

Done when: the card validates and every open field has an owner and a date, as the phase table asks of every discovery question.

## Phase 2: Design

1. **Level the card and generate the plan.** Skill: `planning-a-twin`. Command: `all`. It writes `levelled.json`, `backlog.json`, `backlog.md` and `dashboard.html`.
2. **Read the result,** in this order:
   - blockers: a task that cannot be built as asked on this plan or data class;
   - decisions that rest on an unverified fact;
   - undecided decisions, which a person at the customer must make;
   - warnings, grouped by code;
   - open questions.
3. **Record overrides.** An override changes a rule's result. Write one only when you have the value, the reason and the name of the person at the customer who approved it. The dashboard shows it as Overridden, with all three.
4. **Run `all` again** after every change to the card, the profile or an override, and read what moved.
5. **Take the dashboard and the design to the sponsor.** The technical and business owners approve, as the phase table says.

## Phase 3: Build

Skill: `building-twin-stories`. It picks the next story from the backlog, works its tasks one at a time and keeps each task's status true. Evals come first ([engagement model, principle 2](01-engagement-model.md#principles-for-every-engagement)) and every task starts at autonomy level 1. After each status change, run `backlog` and then `dashboard`, so `backlog.md` and `dashboard.html` agree. See [04 Writing stories](04-stories.md#from-the-persona-card) for how the generated backlog relates to a hand-written one.

## Phases 4 and 5: Pilot and Scale

A change is made on the card or the profile, and the plan is made again with `all` (skill: `planning-a-twin`). Examples: a new answer from the pilot, a promotion in autonomy, a new role.

- A promotion in autonomy is an override on the card. Its reason is the scorecard evidence ([compendium 06](../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level)) and its approver is named.
- A new role is a new persona folder under the same customer. The profile is shared.
- **Never edit a generated file.** `levelled.json`, `backlog.md` and `dashboard.html` come only from the commands. In `backlog.json` a person changes only a task's `status`.

## The files in a persona folder

The two samples under [engagements/](../../engagements/README.md#the-samples) show every file below.

| File | What it is | Who writes it |
|---|---|---|
| `../../customer-profile.json` | The customer profile, shared by all that customer's personas | A person, from discovery |
| `interviews/<date>-<who>.md` | Interview notes, one file per interviewee | A person |
| `card.json` | The persona card, with its overrides and open questions | A person, or Claude with the consultant from the notes. Overrides only by the consultant. |
| `levelled.json` | The levelled plan: each task's decisions with rule, source page and reason, plus blockers and warnings | A command (`level`) |
| `backlog.json` | The backlog: epic, features, stories, tasks and their status | A command (`backlog`). A person changes only a task's `status`. |
| `backlog.md` | The same backlog, readable | A command (`backlog`) |
| `dashboard.html` | One status page for the persona | A command (`dashboard`) |

## What a rule decides, and what a person decides

- **By rule:** per task, the runtime, the identity, the autonomy start and ceiling, the data controls, the connectors, memory and plan fit; per persona, the distribution and the settings baseline; and the blockers and warnings. Each result names the rule and the compendium page behind it. The same card gives the same files.
- **By a person:** every answer in an interview. Every override. Every decision the dashboard shows as undecided. Whether a blocker is met by changing the task, correcting an answer or moving the customer to another plan. Every sign-off, and every promotion in autonomy.

Nobody proposes an override only to make a blocker go away. Offer the ways out and let the consultant and the customer choose.

## Limits

- The partner kit is partner-only. It is never installed in a customer org and never listed in the customer marketplace.
- A decision the dashboard marks as resting on an unverified fact must be confirmed with Anthropic before the customer relies on it. The marker is defined in the [compendium conventions](../../docs/compendium/README.md#conventions).
- The skills' evals are written and have not been run.
