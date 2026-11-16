---
id: OPS-27
title: A consultant can run a role interview from a plain-language guide and capture the answers in a notes template that maps to the persona card
domain: ops
tier: standard
tier_reason: Two templates and one test against an existing catalogue, with the structure decided in the card
status: merged
issue: 111
scope: [partner-kit/plugins/twin-consultant/templates/interview-guide.md, partner-kit/plugins/twin-consultant/templates/interview-notes.md, tests/test_interview_kit.py, partner-kit/plugins/twin-consultant/data/fields.json, partner-kit/plugins/twin-consultant/README.md]
forbid: [partner-kit/plugins/twin-consultant/scripts/**, partner-kit/plugins/twin-consultant/templates/card.json, partner-kit/plugins/twin-consultant/templates/customer-profile.json, partner-kit/docs/**, starter-kit/**, engagements/**, docs/**, .claude-plugin/**]
red_test: python3 -m unittest tests.test_interview_kit
gate: test
budget: 2-attempts
spend: 10
---
## Why

The adversarial review found that discovery section F is five generic questions with no persona question, no memory, identity or data-class question per task, no capture format and no step from answers to a feature list. The persona card (card.json; not the persona voice file in starter-kit/templates/persona, and not a task card) can only be filled if every field has a question a role holder can answer.

## Done when

- Read partner-kit/docs/design.md sections 2, 4, 5 and 6 and partner-kit/plugins/twin-consultant/data/fields.json first. The guide is client-facing: a consultant reads it aloud to a role holder who is not technical.
- partner-kit/plugins/twin-consultant/templates/interview-guide.md exists with, in order: a short 'Before the interview' section (2 to 3 people per role, 45 to 60 minutes, ask leave to take notes, the redaction rule below); persona questions P1 to P6; task questions F1 to F9, asked once per task; a closing step that groups the tasks into a feature list in the role holder's own words (at most three numbered steps); and 'After the interview' (save the notes, fill the card, run the validate command, linking the plugin README instead of repeating it).
- F1 to F5 keep the meaning they have in docs/playbook/02-discovery.md. F6 asks who else sees or changes the output, F7 whether it can be undone and whether it touches money, F8 whether it reads things written by outsiders (customer email, tickets, web pages), F9 whether the role holder would want anything remembered between sessions. P1 to P6 cover the role, who they serve, what a good week looks like, the tone they expect, what must never be done on their behalf, and who they escalate to.
- Every question has: its id; the question as spoken, in one or two short sentences; one or two follow-up probes; 'Why we ask' in one line; 'Fills', a list of exact card field paths from fields.json; and, where the field is an enumeration, 'Listen for', which maps what people say to each allowed value. The spoken question and probes use none of these words: Claude, MCP, connector, plugin, skill, runtime, autonomy, ZDR, MNPI, PHI, data class, provenance.
- Every card field in parts A1 to A8 that is required and is not a key field appears under at least one question's Fills, or has a default with a source in the catalogue. For each path under a question's Fills, that field's asked_by in fields.json includes the question id, and the reverse. Where the two disagree, change only the asked_by lists in fields.json and list each change in the report; change no other property of the catalogue.
- partner-kit/plugins/twin-consultant/templates/interview-notes.md exists with: a header (customer id, persona id, date, the interviewee's role, the interviewer); one slot per P question; a task block with a task id and one slot per F question, marked as repeated per task; the closing feature table (feature name, why it matters, task ids); and an open-questions table (question, owner, due date). It states where the file is saved (the interviews folder path from design.md section 3) and how a card's provenance source points at an answer, in the form design.md section 4.3 gives. It states the redaction rule: before the file is committed, real company names, people's names and amounts in examples are replaced, and for anything under engagements/sample-* everything is invented.
- tests/test_interview_kit.py (standard library only) checks: ids P1 to P6 and F1 to F9 each appear exactly once as a question in the guide; every path under Fills exists in fields.json for the card record; the two-way agreement between Fills and asked_by; every interview question id used in any asked_by is in the guide and every discovery id (A to G) used in any asked_by exists in docs/playbook/02-discovery.md; the required-field coverage rule above; the notes template has a slot for every question id; no spoken question or probe contains a banned word.
- partner-kit/plugins/twin-consultant/README.md lists the two templates and no longer lists the interview guide as not built. python3 -m unittest discover -s tests passes. The report lists every asked_by change and any required field no question could reasonably fill, as 'gap: <field path> needs <what>'.

## Review

Brain read the whole diff at 84d51ff. The guide has P1 to P6 and F1 to F9, each with Ask, Probes, Why we ask and Fills, and a Listen for list wherever a filled field is an enumeration. The test checks both directions between Fills and the catalogue's asked_by, that every required anatomy field is asked or has a sourced default, and that the spoken lines carry no product jargon. Two asked_by changes in fields.json (role.device gains P1, outcome.sponsor_goal gains P3); no other catalogue change. Carried forward to the docs story (#154): a sponsor goal heard in P3 is `assumed` until the sponsor confirms it in A1.
