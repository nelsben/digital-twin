# Interview notes

| Item | Value |
|---|---|
| Customer id | sample-insurance-broker |
| Persona id | claims-handler |
| Date | 2026-11-13 |
| Interviewee's role | Senior claims handler, injury claims |
| Interviewer | Partner engagement lead |

Write what they said in their words. Questions are in [interview-guide.md](interview-guide.md).

> Fictional. The interviewee, every claimant and every figure here are invented.

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

"Senior claims handler on the injury team: employer's liability and public liability. Eight years here. Ledgerline, Outlook, the medical library on SharePoint, and Teams for the team chat." Device: "My laptop. I don't do work on my phone, I don't want claimants' details on it." Claude: "I use the Claude app on the laptop now and then for wording."

### P2. Who you serve

"The insured client, and through them the insurer. And the claimant, in a way, though they're on the other side. Everyone waiting on me is outside the firm."

### P3. A good week

"Every medical report summarised the day it lands, so the insurer can reserve properly. No complaints. My manager points at reserve accuracy on my files. House rule: a summary never gives an opinion on liability; that's the insurer's."

### P4. How it should sound

"Careful. Full sentences. These are people who've been hurt. Never flippant."

### P5. Never, and ask first

"Never send a medical report, or anything quoting one, outside the firm without a person reading it. Never contact a claimant directly; they usually have a solicitor. Ask before changing a reserve."

### P6. Who you turn to

"The Claims Team Leader. For anything about a claimant's health or capacity, the injury technical lead."

**Something the card might need:** "If a claimant sounds vulnerable, bereaved or confused, we flag them as a vulnerable customer on the file and a senior handles every contact from then on. Whatever helps us has to respect that flag."

## Task block (repeat once per task)

Task id: T3    Task name: Summarise a medical report for the insurer

#### F1. Your tasks

T3. "Medical reports. When one comes in on an injury claim I read it, they're 20 to 40 pages, and write a one-page summary for the insurer's handler: injuries, prognosis, what it means for the reserve. Three or four a week, an hour and a half each. The four of us on injury do them." Hand over first? "This one, if it can be trusted." What kind of help: "Injury files."

#### F2. What goes in, what comes out

T3. "The report is in the medical library on SharePoint. I read the claim in Ledgerline for the background. The summary gets attached to the claim in Ledgerline and I email it to the insurer." Sensitivity: "Very sensitive. It's someone's medical records; it would do real harm if it leaked. Whether it's 'health information' in the legal sense, you'd have to ask compliance. Nobody's told us."

#### F3. What good looks like

T3. "Good: the insurer can set the reserve from the summary without opening the report. Bad: one last year missed that the claimant couldn't go back to work, and the reserve was half what it should have been." Examples: "I can find three good and two bad, but they'd have to be anonymised." Who judges: "The injury technical lead."

#### F4. If it goes wrong

T3. "High. Wrong prognosis, wrong reserve, and if we've misread someone's injuries that's a complaint and possibly the ombudsman."

#### F5. What starts it

T3. "I start it when I see a report has come in."

#### F6. Who else sees it

T3. "The insurer's handler. It sits on the claim file for the team."

#### F7. Undo and money

T3. "The summary can be corrected if it's caught before the insurer acts on it. Once they've reserved on it, mostly no." Money: "Yes, it drives the reserve, and that is money."

#### F8. Things written by outsiders

T3. "No, but the reports themselves are written by the claimant's doctor or a medical expert the solicitor picked, so they are outside documents. I can't see anyone hiding instructions in a medical report, though."

#### F9. Remembering

T3. "Preferences are fine. I wouldn't want it remembering anything about a claimant's injuries from one file to the next."

Task id: T2    Task name: Send each large client its Friday claims report

#### F1. Your tasks

T2. "We do the Friday report too, for our two council clients. About an hour for both."

#### F2. What goes in, what comes out

T2. "Open claims out of Ledgerline into an email."

#### F3. What good looks like

T2. (Covered by the commercial team.)

#### F4. If it goes wrong

T2. "If it goes to the wrong client, that's a data breach and we report it. High, not medium."

#### F5. What starts it

T2. "Friday, every week."

#### F6. Who else sees it

T2. "The council's risk manager."

#### F7. Undo and money

T2. "Can't be undone once sent."

#### F8. Things written by outsiders

T2. "No."

#### F9. Remembering

T2. (Not asked.)

Task id: T4    Task name: Chase missing documents on open claims

#### F1. Your tasks

T4. "Chasing solicitors and doctors for reports. Every day."

#### F2. What goes in, what comes out

T4. "My Ledgerline diary, then an email."

#### F3. What good looks like

T4. (Not asked.)

#### F4. If it goes wrong

T4. "I'd have to think about that. Ask the team leader."

#### F5. What starts it

T4. "Today I go through my diary when I can. What I'd love is for it to notice by itself when something is fourteen days overdue and send the chaser."

#### F6. Who else sees it

T4. "The solicitor or the doctor's office."

#### F7. Undo and money

T4. "No undo. No money."

#### F8. Things written by outsiders

T4. "No."

#### F9. Remembering

T4. (Not asked.)

## Features (closing step)

| Feature name (their words) | Why it matters | Task ids |
|---|---|---|
| Injury files | "The reserve is only as good as the summary." | T3 |
| Chasing paperwork | "Half of claims work is waiting for someone else's paper." | T4 |

## Open questions

| Question | Owner | Due date |
|---|---|---|
| Do medical reports count as PHI for the firm? | Head of Compliance | 2026-11-27 |
