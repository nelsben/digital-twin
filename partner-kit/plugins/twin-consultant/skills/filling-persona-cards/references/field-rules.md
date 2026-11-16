# Field rules for the persona card

Step 4 of `SKILL.md` points here. The catalogue (`data/fields.json` in this
plugin) is the authority: for each field it gives the type, the allowed
values, whether it is required, whether it is a key, and `asked_by`, the
question ids whose answers may fill it. Design of record:
`partner-kit/docs/design.md`, sections 4 and 5.

## Contents

- Where a value may come from
- Keys and paths
- Values and conversions
- Pack defaults
- Worked examples

## Where a value may come from

- Only from the answer under a question id in the field's `asked_by`. An
  interview-guide id (P1 to P6, F1 to F9) is read from the notes file's
  heading of that id; a task question from the task block whose "Task id:"
  line names the task. A discovery id (A1 to G4) is read from the
  engagement's discovery answers (`../../discovery.md`), cited as
  `discovery.md#<id>`.
- `role.headcount` and `role.pilot_users` are asked by discovery A3. A head
  count heard in P1 is not their source; leave them for A3 or the
  consultant.
- `tasks[].data_class` is asked by discovery C1 and F2. Use C1 only when it
  names a single class for the role. Otherwise F2 of the task, then a pack
  default, then `open`.
- A field the notes leave out entirely is empty. If it is required it is
  `open`; if not, leave it empty with no entry.
- When several notes answer the same field without contradicting each
  other, cite the one the value is taken from. For a list (`voice.never`),
  you may combine items from several notes; cite the file that gave most.

## Keys and paths

- Key fields (`id`, `customer`, `tasks[].id`, `features[].id`,
  `tasks[].feature`, `tasks[].inputs[].system`, `tasks[].writes[].system`,
  `open_questions[].id`, `open_questions[].blocks`) carry no `provenance`
  entry. They must still be present and must point at something that
  exists: a system id must be in the profile's `systems`.
- `provenance` paths use ids, not positions, except in `inputs`, `writes`
  and `overrides`: `tasks.T1.minutes_each`, `voice.tone`,
  `tasks.T2.writes[0].action`.
- Open question ids: `OQ-1`, `OQ-2`, ... unless the notes give an id.

## Values and conversions

- Enumerations: map the interviewee's words with the guide's "Listen for"
  lines. "I start it when I need it" is `person`; "the team does it on a
  schedule" is `schedule-team`.
- `frequency_per_week`: a number per week. "About eight a month" is
  8 x 12 / 52 = 1.85; "about two a month" is 0.46; round to two decimals.
  "Every morning, five days a week" is 5.
- `minutes_each`: minutes. "Half an hour" is 30; "an hour and a half" is
  90; "four hours" is 240.
- `in_pilot`: true only when the interviewee says to pilot it.
- Booleans (`reversible`, `touches_money`, `reads_untrusted_input`,
  `memory.personal_memory_wanted`) need a yes or no in the answer.
- Lists that the template gives one placeholder entry (`features`,
  `overrides`, `open_questions`, `outcome.scorecard_targets`) become `[]`
  when nothing fills them.

## Pack defaults

A pack's `typical_tasks` entry gives a default `trigger` and `data_class`
for a card task that is the same task (match on what the task is, not on
its id). Use it only when the notes are silent on that field. The entry is
`{"status": "default", "source": "data/industry-packs/<id>.json"}`. A pack
gives no default for any other card field.

## Worked examples

From the Team sample (`engagements/sample-team-cs`):

```json
"tasks.C1.minutes_each": {"status": "answered", "source": "interviews/2026-11-06-csm.md#F1"},
"tasks.C2.trigger": {"status": "answered", "source": "interviews/2026-11-07-senior-csm.md#F5"},
"tasks.C5.data_class": {"status": "default", "source": "data/industry-packs/b2b-software.json"}
```

A missing answer (F4 was not asked for task D1):

```json
"tasks": [{"id": "D1", "cost_of_mistake": {"level": null, "what_happens": ""}}],
"open_questions": [{"id": "OQ-1", "question": "What happens if D1 goes wrong? (F4 was not asked)",
  "blocks": ["D1"], "owner": "<from the notes or the consultant>", "due": "<yyyy-mm-dd>"}],
"provenance": {"tasks.D1.cost_of_mistake.level": {"status": "open", "source": "interviews/<file>#F4",
  "owner": "<same>", "due": "<same>"}}
```

A disagreement (two planners on what starts L1): value `null`, status
`open`, and the open question quotes both: "Planner (2026-11-04): 'I start
it myself on Thursday afternoon'. Senior planner (2026-11-05): 'It runs on
a schedule every Thursday'. Which is it?"
