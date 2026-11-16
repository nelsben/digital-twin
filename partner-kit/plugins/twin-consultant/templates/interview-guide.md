# Role interview guide

You read this aloud to someone who does the job every day and is not technical. Say the **Ask** line as written, use a probe if the answer is thin, and write what they say in their words in the notes file ([interview-notes.md](interview-notes.md)). The other lines are for you: **Why we ask**, **Fills** (the card fields the answer feeds) and **Listen for** (what people say, and which allowed value it means).

Design of record: [partner-kit/docs/design.md](../../../docs/design.md), section 6.

## Before the interview

- Interview 2 to 3 people in each role, one at a time. One person gives you their habits; three show you what is common.
- Plan 45 to 60 minutes. Do the persona questions (P1 to P6) once, then the task questions (F1 to F9) for each task, starting with the one that takes most of their week. Stop after about three tasks and book a second session rather than rush.
- Ask leave to take notes before you start: "I'd like to take notes so I get your words right. Is that all right?" If they say no, write from memory straight after.
- Redaction rule: before the notes file is committed, replace real company names, people's names and amounts in examples with invented ones. Under `engagements/sample-*` everything is invented from the start.

## Persona questions

Ask each once per person.

### P1. Your role

**Ask:** "Tell me about your job: what is your title, which team are you in, and which tools or apps do you have open most of the day?"

**Probes:**
- "Do you mostly work on a laptop the company looks after, on your own device, or both?"
- "What do people call your team?"

**Why we ask:** It names the role and team, the places the role holder works, and whether their device is company-managed.

**Fills:** `id`, `role.name`, `role.team`, `role.works_in`, `role.device`

**Listen for:**
- `claude-ai` for the Claude website or app in a browser; `desktop` for the Claude desktop app.
- `claude-code` for working in a terminal or code editor; `cowork` for Claude working on files in a shared folder.
- `slack` for asking Claude from Slack; `teams` for asking Claude from Microsoft Teams.
- `managed` for "IT set it up and controls it"; `unmanaged` for "my own device"; `mixed` for "some of each".

### P2. Who you serve

**Ask:** "Who do you do this work for? Who is waiting on what you produce?"

**Probes:**
- "Who would notice first if you stopped for a week?"
- "Are they inside the company, outside, or both?"

**Why we ask:** It tells the assistant who it is helping and shapes how it speaks to them.

**Fills:** `voice.serves`

### P3. A good week

**Ask:** "Think of a really good week at work. What did you get done, and what did your manager point to as the result?"

**Probes:**
- "What are the two or three jobs you are judged on?"
- "What habits or house rules do good people in your team follow?"

**Why we ask:** It gives the jobs, the working habits and the result the sponsor cares about, in the role holder's words.

**Fills:** `voice.jobs`, `voice.norms`, `outcome.sponsor_goal`

### P4. How it should sound

**Ask:** "When a helper writes or talks to you, how should it sound? Think of someone you would enjoy working with."

**Probes:**
- "Short and direct, or full and careful?"
- "Is there a word or style that puts you off?"

**Why we ask:** It sets the tone the assistant uses.

**Fills:** `voice.tone`

### P5. Never, and ask first

**Ask:** "What should a helper never do on your behalf, even if you asked it to in a hurry?"

**Probes:**
- "What would you want to check first before it went ahead?"
- "Has anyone ever done something for you that you had to undo?"

**Why we ask:** It sets the hard stops and the points where the assistant must pause and ask.

**Fills:** `voice.never`, `voice.ask_before`

### P6. Who you turn to

**Ask:** "When you are unsure or something looks wrong, who do you go to?"

**Probes:**
- "Is it a person, a team or a channel?"
- "Who decides when you disagree?"

**Why we ask:** It tells the assistant who to send problems to.

**Fills:** `voice.escalate_to`

## Task questions

Ask F1 to F9 once for each task. Start with F1 for all the tasks, then go task by task through F2 to F9.

### F1. Your tasks

**Ask:** "Which tasks take most of your week? For each one, how often do you do it, how long does it take, and how many people in your team do it?"

**Probes:**
- "If you could hand over only one of these tomorrow, which would it be?"
- "What would you call the kind of help this task belongs to?"

**Why we ask:** It chooses the tasks, sets the time baseline and picks what to try first.

**Fills:** `features[].id`, `features[].name`, `features[].why`, `tasks[].id`, `tasks[].feature`, `tasks[].name`, `tasks[].frequency_per_week`, `tasks[].minutes_each`, `tasks[].users`, `tasks[].priority`, `tasks[].in_pilot`

### F2. What goes in, what comes out

**Ask:** "Take this task. What do you start from, where do you find it, and what do you hand over at the end?"

**Probes:**
- "Do you only look at things, or do you also change, add or send things in those systems?"
- "How sensitive is the material: everyday internal, confidential, very sensitive, or personal health information?"

**Why we ask:** It names the systems the task reads and changes, and the sensitivity of what is involved.

**Fills:** `tasks[].inputs[].system`, `tasks[].inputs[].objects`, `tasks[].inputs[].access`, `tasks[].output.what`, `tasks[].output.audience`, `tasks[].output.destination`, `tasks[].writes[].system`, `tasks[].writes[].objects`, `tasks[].writes[].action`, `tasks[].data_class`

**Listen for:**
- `read` for "I look it up"; `write` for "I fill it in or change it".
- `self` for "just for me"; `internal` for "my own company"; `other-team` for "another team or department"; `external` for "a customer, investor or anyone outside".
- `create` for "add a new one"; `update` for "change an existing one"; `delete` for "remove"; `send` for "email, post or send out".
- `internal` for ordinary company material; `confidential` for "not for sharing outside the team"; `highly-sensitive` for "would cause real harm if it leaked"; `phi` for health information about individuals.

### F3. What good looks like

**Ask:** "What does a good result look like? Can you show me two or three real examples, some good and some not?"

**Probes:**
- "Where do those examples live, and can we look at them together?"
- "Who is the best person to say whether a result is right?"

**Why we ask:** The examples become the checks we run on the assistant, and the judge becomes its owner.

**Fills:** `tasks[].examples.good`, `tasks[].examples.bad`, `tasks[].examples.where`, `tasks[].skill_owner`

### F4. If it goes wrong

**Ask:** "If this task goes wrong, what happens?"

**Probes:**
- "Who would find out, and how quickly?"
- "Has it gone wrong before? What did it cost?"

**Why we ask:** It sets how much freedom the assistant gets on this task.

**Fills:** `tasks[].cost_of_mistake.level`, `tasks[].cost_of_mistake.what_happens`

**Listen for:**
- `low` for "I'd fix it in a minute, nobody would know".
- `medium` for "some rework, an awkward conversation or a lost afternoon".
- `high` for "money lost, a customer upset, a rule broken or a headline".

### F5. What starts it

**Ask:** "What starts this task? Do you start it yourself, does it happen on a schedule, or does something happen that sets it off?"

**Probes:**
- "Is it only you, or does a team share it?"
- "If it runs on a schedule, when, and who needs the result?"

**Why we ask:** It decides whether the assistant waits for you or works on its own.

**Fills:** `tasks[].trigger`

**Listen for:**
- `person` for "I start it when I need it".
- `schedule-own` for "every Monday I do my own".
- `schedule-team` for "the team does it on a schedule and shares it in a channel".
- `event` for "when a form arrives, a deal changes or an alert fires".

### F6. Who else sees it

**Ask:** "Who else sees or changes what this task produces?"

**Probes:**
- "Does it go anywhere outside your own files, such as a shared folder, a system or an email?"
- "Does anyone check it before it goes further?"

**Why we ask:** Output that other people see needs more care than output only you see.

**Fills:** `tasks[].output.audience`, `tasks[].output.destination`, `tasks[].writes[].system`

**Listen for:**
- `self`, `internal`, `other-team` and `external` as in F2: "just me", "my company", "another team", "someone outside".

### F7. Undo and money

**Ask:** "Can this be undone if it is wrong? Does it touch money in any way?"

**Probes:**
- "What would you want a person to approve before it happened?"
- "Is anything sent out, deleted or paid that cannot be taken back?"

**Why we ask:** Things that cannot be undone, or that move money, need a person to approve them.

**Fills:** `tasks[].writes[].action`, `tasks[].reversible`, `tasks[].touches_money`, `voice.ask_before`

**Listen for:**
- `create` for "add a new one"; `update` for "change an existing one"; `delete` for "remove"; `send` for "send out".

### F8. Things written by outsiders

**Ask:** "Does this task read anything written by people outside the company, such as customer emails, tickets or web pages?"

**Probes:**
- "Who could write something into that material?"
- "Do you ever see odd or pushy instructions in it?"

**Why we ask:** Text from outsiders can try to steer the assistant, so we treat it with more care.

**Fills:** `tasks[].reads_untrusted_input`

### F9. Remembering

**Ask:** "Would you want your helper to remember anything between one conversation and the next, such as your preferences or how you like things done?"

**Probes:**
- "What would you be uncomfortable with it keeping?"
- "Who else should be able to see what it remembers?"

**Why we ask:** Remembered items persist and can be read later, so we decide on purpose what is kept.

**Fills:** `memory.personal_memory_wanted`, `memory.notes`

## Closing: from tasks to features

Do this after the last task, with the role holder, in their words. Not a question to ask once per task.

1. Read back the list of tasks you heard, using their names for them.
2. Ask: "Which of these belong together? What would you call each group?" Use their name for each group.
3. For each group ask: "Why does it matter to you?" Write the group name, the reason and its task ids in the closing table of the notes. These become the card's features.

## After the interview

1. Save the notes at the path given in [interview-notes.md](interview-notes.md), then apply the redaction rule above.
2. Fill the card from the notes: one answer per field, each with its provenance entry pointing at the answer.
3. Run the validate command from the [plugin README](../README.md#validate) and fix what it reports. Put anything unanswered on the card as an open question with an owner and a date.
