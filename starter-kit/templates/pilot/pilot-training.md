# Pilot training: FILL IN twin name

<!--
Two parts: the session you run with pilot users, and the form they use to
report a failure. Fill in every FILL IN cell, then delete this comment and the
markers. Each FILL IN has one line saying where in the engagement's design the
answer comes from. Give the pilot users the finished Part 2 as a page they can
copy.
-->

## Part 1. Session outline

About 45 minutes. Run it before the first pilot user starts. Autonomy levels are in [How much the twin may do on its own](../../../docs/compendium/06-autonomy.md); do not teach them from this file.

### For each task

Repeat this block once per task in the pilot.

- Task: FILL IN: task name, from the backlog.
- What the twin does: FILL IN: one line, from the story's description in the backlog.
- The autonomy level it runs at, and what that means for you: FILL IN: the level from the scorecard's "Per task" row, and the one thing the user does at that level (review, approve each step, or read the log).
- What it never does: FILL IN: the hard limits, from the persona's "What you never do" section.

### Recognise the twin's output

- In each system, the marker that shows the twin wrote or changed something: FILL IN: one line per system, from the source-system design (the field marker or label agreed with each system admin).

### Data that must not be pasted in

- FILL IN: the data classes the twin must not receive, from the customer's data-class policy ([sensitive data](../../../docs/compendium/10-sensitive-data.md)).

### Stop or undo

- How to stop the twin mid-task: FILL IN: from the design document.
- How to undo what it did, per system: FILL IN: from the design document.
- Who to call if it will not stop: FILL IN: a person or channel, from the stakeholder map.

## Part 2. Report a failure or a wrong draft

### Where reports go

FILL IN: the one place, for example a named channel or inbox, chosen in the design document. Use only this place, so nothing is lost.

### The report form

Copy this into the place above and fill it in. Short answers are fine.

```
Date:
Task:
What I asked:
What came back:
What I expected:
System and record (for example the CRM record or the document):
Data class involved:
How bad (choose one):
  - wrong but harmless
  - wrong and sent
  - data exposed
```

### Who triages and how fast

Roles are those in [Stakeholders](../../../docs/playbook/03-stakeholders.md).

| How bad | Who triages | Within |
|---|---|---|
| Wrong but harmless | FILL IN: a role from the stakeholder map, for example the skill owner | FILL IN: a time |
| Wrong and sent | FILL IN: a role from the stakeholder map | FILL IN: a time |
| Data exposed | Security and compliance | The same day |

A "data exposed" report goes to security and compliance the same day, whoever receives it first. Do not wait for the next review.
