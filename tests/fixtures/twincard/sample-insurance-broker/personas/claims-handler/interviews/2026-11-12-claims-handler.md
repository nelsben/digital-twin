# Interview notes

| Item | Value |
|---|---|
| Customer id | sample-insurance-broker |
| Persona id | claims-handler |
| Date | 2026-11-12 |
| Interviewee's role | Claims handler, commercial motor and property |
| Interviewer | Partner engagement lead |

Write what they said in their words. Questions are in the interview guide, `partner-kit/plugins/twin-consultant/templates/interview-guide.md` in the partner kit.

> Fictional. The interviewee, every client and every figure here are invented.

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

"I'm a claims handler in the commercial team, motor fleet and property mostly. Three years. All day I've got Outlook, Ledgerline and Teams open, and Dynamics when I need to look up who the client contact is. We've had Claude in the browser since the summer; honestly I'd rather it was in Teams where I already am." Device: "Work laptop. I also check Outlook on my own phone when I'm out at a site."

### P2. Who you serve

"The client, first. Usually the fleet manager or the finance person at the firm we look after. Then the insurer's claims team, who decide what gets paid. The client is outside, the insurer is outside, nobody I serve is inside really, apart from my team leader."

### P3. A good week

"A good week is every new claim acknowledged inside the day, every Friday report out before lunch and no client chasing me. My team leader looks at how many claims I've got open past 30 days with nothing moving. House rules: always put the claim number in the subject line, never guess a policy number, and note every call on the file."

### P4. How it should sound

"Short. Plain. Clients are not insurance people, so no jargon. Polite but not gushing; I hate 'I hope this email finds you well'."

### P5. Never, and ask first

"Never tell a client a claim is covered. That's the insurer's call, not ours, and it's the thing that gets brokers sued. Never send anything to a client without me reading it first. Ask me before closing a claim on the system."

### P6. Who you turn to

"My team leader. If it's a coverage question, the account executive for that client. If it's a complaint, it goes to compliance the same day, that's the rule."

**Something the card might need:** "Every new claim has to be acknowledged to the client within 24 hours. That's written into our service agreement with the bigger clients and we report on it every month."

## Task block (repeat once per task)

Task id: T1    Task name: Set up a new claim from the client's notification

#### F1. Your tasks

T1. "New claims are the big one. A client emails the claims inbox, sometimes with our claim form, sometimes just 'the van's been hit'. I'd say fifteen a week for me, twenty minutes each if it's straightforward. All nine of us in commercial do them." Hand over one tomorrow? "Not this one, I need to see them. The Friday reports." What kind of help: "Getting claims in."

#### F2. What goes in, what comes out

T1. "I start from the email in the claims inbox in Outlook. I look up the client and the policy in Dynamics. Then I create the claim in Ledgerline and send the client an acknowledgement email with the claim number." Sensitivity: "Confidential. It's the client's business and sometimes a driver's details. Nothing medical on commercial motor, usually."

#### F3. What good looks like

T1. "A good one: claim on the right policy, right date of loss, acknowledgement out the same morning. A bad one: last month someone put a claim on last year's policy and the insurer bounced it." Examples: "I can show you two good ones and one bad one from my files." Who judges: "My team leader."

#### F4. If it goes wrong

T1. "If I miss one, we go past 24 hours and the client complains. If it's on the wrong policy, it's a mess to unpick with the insurer. Medium, I'd say."

#### F5. What starts it

T1. "It starts when the email lands in the claims inbox."

#### F6. Who else sees it

T1. "The client gets the acknowledgement. The claim record is seen by the whole team and the insurer gets it when we notify them."

#### F7. Undo and money

T1. "I can fix the claim record. An email once sent is sent." Money: "No, not at that point. Nobody is paid at set-up."

#### F8. Things written by outsiders

T1. "Yes, every one. Clients, drivers, sometimes the other side's solicitor writes in. Some of those letters are pushy."

#### F9. Remembering

T1. "It'd be handy if it remembered how each client likes their Friday report laid out. Nothing else really."

Task id: T2    Task name: Send each large client its Friday claims report

#### F1. Your tasks

T2. "Every Friday morning I send each of my bigger commercial clients a list of their open claims and what's moved this week. Six clients. All of it takes me about two and a half hours. Four of us have big clients." This is the one to hand over first: "If I could give you one tomorrow, it's this one." What kind of help: "Keeping clients in the loop."

#### F2. What goes in, what comes out

T2. "I pull the open claims for that client out of Ledgerline, with the reserve and the last note, and paste them into an email in Outlook to the client's fleet manager." Sensitivity: "Confidential."

#### F3. What good looks like

T2. "Good: every open claim, with one line on what happened this week, and a reserve that matches the system. Bad: one went out with another client's claim on it in the spring. I'll dig out two good ones." Who judges: "My team leader."

#### F4. If it goes wrong

T2. "If it's a bit wrong, I get an awkward phone call and send a correction. Medium."

#### F5. What starts it

T2. "Friday morning, every week. It's mine; nobody else does my clients."

#### F6. Who else sees it

T2. "The client, and I copy my team leader."

#### F7. Undo and money

T2. "No, once it's gone it's gone." Money: "It shows the reserve figures but it doesn't move any money."

#### F8. Things written by outsiders

T2. "No. It all comes from our own system."

#### F9. Remembering

T2. "Same as before: the layout each client likes."

Task id: T4    Task name: Chase missing documents on open claims

#### F1. Your tasks

T4. "Chasing. Repair estimates, police reports, photos. I go through my Ledgerline diary and email whoever owes us something. Maybe ten chasers a day, five minutes each. Everyone does it." What kind of help: "Keeping clients in the loop, really."

#### F2. What goes in, what comes out

T4. "The diary in Ledgerline tells me what's due. I write the chaser in Outlook to the client or the garage." Sensitivity: "Confidential."

#### F3. What good looks like

T4. "A good chaser says exactly what we need and by when. I don't have examples saved."

#### F4. If it goes wrong

(Not asked: ran out of time.)

#### F5. What starts it

T4. "I do it when I get a minute, usually first thing."

#### F6. Who else sees it

T4. "The client or the garage."

#### F7. Undo and money

T4. "An email is an email; you can't take it back." Money: "No."

#### F8. Things written by outsiders

T4. "Not really, I'm writing to them."

#### F9. Remembering

T4. (Not asked.)

## Features (closing step)

| Feature name (their words) | Why it matters | Task ids |
|---|---|---|
| Getting claims in | "If it's not in by the end of the day we've broken our promise to the client." | T1 |
| Keeping clients in the loop | "Clients who know where they stand don't chase, and they renew." | T2, T4 |

## Open questions

| Question | Owner | Due date |
|---|---|---|
| What happens if a chaser (T4) goes wrong? Not asked. | Claims Team Leader | 2026-11-24 |
