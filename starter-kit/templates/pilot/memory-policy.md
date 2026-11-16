# Memory policy: FILL IN role name

<!--
One policy per role. Fill in every FILL IN cell, then delete this comment and
the markers. Each FILL IN says where in the engagement's design the answer
comes from. This file states no fact about Claude: the facts are in
../../../docs/compendium/02-persona.md#memory. Read that section before you
fill this in.
-->

Role knowledge (the playbook, the product facts, the house style) lives in skills and reference files, not in memory. This policy is about what the twin keeps from conversations and runs. See [Memory](../../../docs/compendium/02-persona.md#memory).

## Where memory can live for this role

One row per place memory can live for this role. For how each one works, read the compendium section; do not describe it here.

| Place | Used for this role? | Who can see and edit it | Decision |
|---|---|---|---|
| Claude.ai memory ([Memory](../../../docs/compendium/02-persona.md#memory)) | FILL IN: yes or no, from the org plan in the design document | FILL IN: from the compendium section | FILL IN: on or off, and why |
| API memory tool ([Memory](../../../docs/compendium/02-persona.md#memory)) | FILL IN: yes or no, from the hosted-runtime choice in the design document | FILL IN: who runs the app that stores it | FILL IN: on or off, and why |
| Managed Agents memory stores ([Memory](../../../docs/compendium/02-persona.md#memory)) | FILL IN: yes or no, from the hosted-runtime choice in the design document | FILL IN: who can attach and edit a store | FILL IN: on or off, and which stores are read-only |
| Claude Tag channel memory ([Memory](../../../docs/compendium/02-persona.md#memory)) | FILL IN: yes or no, from the channel list in the design document | FILL IN: who is in each channel | FILL IN: on or off, and why |

## What the twin may remember and what it must not

One row per task and data class. Data classes come from the customer's data-class policy ([sensitive data](../../../docs/compendium/10-sensitive-data.md)).

| Task | Data class | May remember | Must not remember | Where it is kept | Reason |
|---|---|---|---|---|---|
| FILL IN: task name from the backlog | FILL IN: class from the data-class policy | FILL IN | FILL IN | FILL IN: a place from the table above, or "nowhere" | FILL IN |

## Who can switch memory on or off for the org

- Who holds that switch: FILL IN: the person with the Owner role, named in the design document ([stakeholders](../../../docs/playbook/03-stakeholders.md)).
- The decision taken: FILL IN: on or off, the date, and who decided.

## What pilot users are told

- Why memory is on or off: FILL IN: one sentence, from the decision above.
- If it is on, where the user sees and clears what is kept: FILL IN: the steps, completed by the engagement from the vendor page linked in [Memory](../../../docs/compendium/02-persona.md#memory). Do not write the steps from memory.

## Tasks that read input written by outsiders

Customer emails, tickets and web pages are written by people outside the customer. A task that reads them and can also write memory is the risk the compendium describes under memory poisoning in [Memory](../../../docs/compendium/02-persona.md#memory).

- Tasks that read outsider-written input: FILL IN: task names from the backlog.
- The rule for each: FILL IN: whether it may write memory, and if it may, which controlled step writes and who reviews what is written.

## Sign-off

| Role | Name | Date |
|---|---|---|
| Compliance owner | FILL IN: the person named in the design document | FILL IN |
| Business owner | FILL IN: the person named in the design document | FILL IN |
