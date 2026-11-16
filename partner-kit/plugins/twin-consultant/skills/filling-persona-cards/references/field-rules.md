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
- When the notes differ
- Rules, wished changes and wished surfaces
- Pack defaults
- Worked examples

## Where a value may come from

- Only from the answer under a question id in the field's `asked_by`. An
  interview-guide id (P1 to P6, F1 to F9) is read from the notes file's
  heading of that id; a task question from the task block whose "Task id:"
  line names the task. A discovery id (A1 to G4) is read from the row of
  that id in `discovery.md` in the customer folder, cited as
  `discovery.md#<id>` (never `../../discovery.md#<id>`: the validator looks
  in the customer folder itself).
- An answer the consultant gives in conversation is written first: a
  discovery answer to its row in `discovery.md` (create the file from
  `templates/discovery.md` if there is none), an interview answer to a new
  dated notes file `interviews/<yyyy-mm-dd>-<who>.md` under the question's
  heading (inside the task block for a task question). Then cite that line.
- `role.headcount` and `role.pilot_users` are asked by discovery A3. A head
  count heard in P1 is not their source; leave them for A3 or the
  consultant.
- `tasks[].data_class` is asked by discovery C1 and F2. Use C1 only when it
  names a single class for the role. Otherwise F2 of the task, then a pack
  default, then `open`.
- A field the notes leave out entirely is empty. If it is required it is
  `open`; if not, leave it empty with no entry.
- When several notes answer the same field without contradicting each
  other, combine what they say and cite every file the value draws on,
  separated by `; `. For a list (`voice.never`), cite each file that gave an
  item, and a discovery row too when one item comes from it.

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
- `tasks[].trigger` records how the task starts today. "Something
  happening, ideally. Today I start it when I'm told" is `person`, answered;
  the wish ("ideally", "later", "really it is") becomes an open question
  that blocks nothing until it is decided.
- `frequency_per_week`: a number per week. "About eight a month" is
  8 x 12 / 52 = 1.85; "about two a month" is 0.46; round to two decimals.
  "Every morning, five days a week" is 5.
- A rate per something else ("twice per deal", "once per account") is the
  rate for one deal or account, `assumed` with an owner until the count per
  week is known. Say so in the report.
- `minutes_each`: minutes. "Half an hour" is 30; "an hour and a half" is
  90; "four hours" is 240.
- `in_pilot`: true only when the interviewee says to pilot it.
- Booleans (`reversible`, `touches_money`, `reads_untrusted_input`,
  `memory.personal_memory_wanted`) need a yes or no in the answer. `false`
  is a value, so an `open` boolean is `null`.
- `tasks[].reads_untrusted_input`: when question F8 is answered "No" but
  the notes show the task reading what outsiders wrote (tickets customers
  write, a call transcript with the customer's words, an inbound document),
  the value is `true`, `assumed`, with an owner the consultant names. Ask
  the consultant who; do not pick one. The same holds when the "No" comes
  with a caveat that names documents written outside the company ("No,
  apart from the target's data-room files"): `true`, `assumed`, and the
  caveat is quoted, in the interviewee's words, in the follow-up to that
  owner (the report's "Still open or assumed" line for the field) or in an
  open question for them (`blocks` `[]`), so they confirm it.
- `tasks[].reversible`: a split answer under question F7 ("the draft can be
  thrown away, the sent email cannot") is `open` unless the notes say which
  part the twin does. When they say the twin only drafts, it is `true`.
- Lists that the template gives one placeholder entry (`features`,
  `overrides`, `open_questions`, `outcome.scorecard_targets`) become `[]`
  when nothing fills them.

## When the notes differ

- **A task under two features.** When two notes files put the same task
  under different features in their closing tables, `tasks[].feature` is
  the feature in the first file (files in name order, which is date
  order). Add an `open_questions` entry that quotes both closing-table rows
  with their file names and names who decides (the owner from the notes'
  open-questions table or from the consultant; ask if neither gives one).
  `blocks` is `[]`: the feature only groups tasks.
- **Two tones.** Two interviewees' answers to question P4 are never a
  disagreement. `voice.tone` combines them, and its source names both files
  with `; `. Do not keep only one of them.

## Rules, wished changes, story wants and wished surfaces

Five card fields hold only what an interviewee said, in their words.
Nothing is inferred: not from a process, a regulation you know of, a pack
or another task. None is required; with nothing said, the value stays empty
(`[]` or `""`) and has no `provenance` entry.

- `tasks[].constraints`: a rule or deadline the task must always keep,
  from questions F4 and F7 in that task's block. One item per rule, quoted
  as the interviewee said it ("I check the figures before I send."). Cite
  every file that gave an item, with `; `. A rule said outside the task
  block (under question P6, say) cannot be cited as answered, because the
  validator looks for the heading inside the task block: record it
  `assumed`, citing where it was said, with an owner to confirm it.
- `tasks[].wanted_change`: what the interviewee would change about how the
  task is done today, from questions F3 and F5, quoted. The wish half of an
  F5 trigger answer ("the escalation itself, ideally") goes here as well;
  the open question about the trigger stays.
- `tasks[].story_want` and `tasks[].story_benefit`: the two halves of the
  task story's statement, "I want <want>, so that <benefit>." Write them
  from the interviewee's own words under question F1 (and F3 for the
  benefit), in the first person of the role: `story_want` is what the twin
  does ("draft the renewal quote email from the HubSpot deal"),
  `story_benefit` what that gives back ("I only check the figures and send
  it"). Leave both empty when the notes do not say why the task should be
  handed over; never invent a benefit. The backlog then drafts the
  statement from the output and the minutes, marked for the consultant to
  confirm with the interviewee.
- `role.wanted_surfaces`: where the interviewees say they would rather
  work, from question P1, as `role.works_in` values. Where they work today
  is `role.works_in`, not this. It is a wish: levelling does not read it.

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
"tasks.C5.trigger": {"status": "answered", "source": "interviews/2026-11-07-senior-csm.md#F5"},
"tasks.C1.reads_untrusted_input": {"status": "answered", "source": "interviews/2026-11-10-team-lead.md#F8"},
"voice.tone": {"status": "answered",
  "source": "interviews/2026-11-06-csm.md#P4; interviews/2026-11-07-senior-csm.md#P4"},
"role.headcount": {"status": "answered", "source": "discovery.md#A3"},
"tasks.C3.constraints": {"status": "answered", "source": "interviews/2026-11-07-senior-csm.md#F4"},
"tasks.C5.wanted_change": {"status": "answered", "source": "interviews/2026-11-07-senior-csm.md#F5"}
```

C3's constraint is the senior CSM's "I check the figures before I send.",
one item, as said.

C5's notes say "the escalation itself, ideally. Today I start it when I'm
told", so the trigger is `person` and the wish is open question OQ-1 with
`blocks` `[]`. C1's first answer under question F8 was "No"; the follow-up
notes file `2026-11-10-team-lead.md` records the team lead's "Yes", so the
value is `true` and answered from that file.

A working guess, from the private-equity sample: the associate answers "No"
under question F8 for T1, but the same answer says the data-room files are
the target's documents, which outsiders wrote. So the value is `true`,
assumed, with the owner the consultant named:

```json
"tasks.T1.reads_untrusted_input": {"status": "assumed",
  "source": "interviews/2026-11-12-associate.md#F8", "owner": "Eleanor Osei-Whitcombe"}
```

The report's line for it quotes the associate's caveat about the data-room
files, so the owner sees what to confirm.

A pack default, as a general example (task D1 stands for any card task). It
applies only when the notes are silent on the data class:

```json
"tasks.D1.data_class": {"status": "default", "source": "data/industry-packs/<id>.json"}
```

A missing answer (F4 was not asked for task D1):

```json
"tasks": [{"id": "D1", "cost_of_mistake": {"level": null, "what_happens": ""}}],
"open_questions": [{"id": "OQ-1", "question": "What happens if D1 goes wrong? (F4 was not asked)",
  "blocks": ["D1"], "owner": "<from the notes or the consultant>", "due": "<yyyy-mm-dd>"}],
"provenance": {"tasks.D1.cost_of_mistake.level": {"status": "open", "source": "interviews/<file>#F4",
  "owner": "<same>", "due": "<same>"}}
```

A disagreement (two planners on what starts L1): value `null` (an open
field is empty), status `open`, and the open question quotes both: "Planner (2026-11-04): 'I start
it myself on Thursday afternoon'. Senior planner (2026-11-05): 'It runs on
a schedule every Thursday'. Which is it?"
