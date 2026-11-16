# Interview notes

| Item | Value |
|---|---|
| Customer id | |
| Persona id | |
| Date | yyyy-mm-dd |
| Interviewee's role | |
| Interviewer | |

Write what they said in their words. Questions are in [interview-guide.md](interview-guide.md).

## Where this file is saved

`engagements/<customer>/personas/<persona-id>/interviews/<yyyy-mm-dd>-<who>.md`, for example `interviews/2026-11-14-associate-a.md`.

## How the card points at an answer

A card's provenance entry for a field gives this file and the question id as its source, with status `answered`:

```
"tasks.T1.frequency_per_week": {"status": "answered", "source": "interviews/2026-11-14-associate-a.md#F1"}
```

Answers from persona questions use their own id, for example `#P3`. Where a task block answers a question, name the task in the answer text.

## Redaction rule

Before this file is committed, replace real company names, people's names and amounts in examples with invented ones. For anything under `engagements/sample-*` everything is invented from the start.

## Persona answers

### P1. Your role

### P2. Who you serve

### P3. A good week

### P4. How it should sound

### P5. Never, and ask first

### P6. Who you turn to

## Task block (repeat once per task)

Task id: T__    Task name:

#### F1. Your tasks

#### F2. What goes in, what comes out

#### F3. What good looks like

#### F4. If it goes wrong

#### F5. What starts it

#### F6. Who else sees it

#### F7. Undo and money

#### F8. Things written by outsiders

#### F9. Remembering

## Features (closing step)

| Feature name (their words) | Why it matters | Task ids |
|---|---|---|
| | | |

## Open questions

| Question | Owner | Due date |
|---|---|---|
| | | |
