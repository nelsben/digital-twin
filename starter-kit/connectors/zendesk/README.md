Written 2026-11-16 by the author from the pages listed; not yet checked by a second reader.

# Zendesk marker field: Last updated by twin

## What this is

One custom ticket field, "Last updated by twin", of type text. The twin's ticket-update skill writes the current UTC time into it on every ticket change, so Zendesk's own ticket history can tell a twin change from a human one. The reason is in [compendium 15](../../../docs/compendium/15-governance-and-performance.md): with per-user sign-in a write by the twin appears under the agent's name. This is the Zendesk copy of the pattern in the [Salesforce marker README](../salesforce/README.md); read that first for the thinking. How the connection is made is in the [Zendesk connector runbook](../../runbooks/zendesk-connector.md). There is no file to deploy: a Zendesk admin adds the field in Admin Center.

Each step ends with the pages it came from, as tags like ([A]) that "Pages used" defines. **⚠ Unverified:** means no page we downloaded states it, and the item says what to confirm.

## Why this marker

We first meant a ticket tag "twin" added with every change: a tag is in every plan, and "Agents can add or remove tags in tickets" ([F]). Two things moved us to a field.

- **A tag is added once.** "Each audit represents a single update to the ticket", and its examples include "Tags were added or removed" ([D]). A second twin change to a ticket that already carries the tag adds no tag, so no event says the twin acted again. **⚠ Unverified:** that re-adding a tag already on the ticket records nothing; no page says either way. Safer reading: assume it records nothing.
- **An agent can remove a tag.** Agents "can delete tags on one ticket at a time" ([F]), and admins can remove a tag from all open tickets ([F]). A removed tag leaves the report short and the twin's change unmarked. The same holds for any ticket field an agent can edit (below), but a field value is rewritten by the next twin write.

A text field holding the time changes on every write, and "The value of a ticket field was changed" is an audit example ([D]), so each twin write leaves a Change event. Each audit has "author_id" ("The user who created the audit") and "created_at" ([D]). This is the reason the Salesforce field is a DateTime. Text fields can be used as a view condition, with "Present" ([G]).

## Create it (the Zendesk admin does this)

1. In Admin Center, click **Objects and rules**, then **Tickets > Fields**, then **Add field** ([C]). "You must be an administrator to create custom ticket fields." ([C])
2. Select the **Text** type and the display name "Last updated by twin". "You can't alter a field type after the custom ticket field is created." ([C])
3. Under Permissions choose **Agents can edit**, so customers never see it ([C]). Add a description for admins saying the twin sets it. Leave "Required to solve a ticket" off.
4. If you use several ticket forms, add the field to each form the twin writes to ([C]). Do this in a sandbox or on a test form first.

## Limit who can set it

The goal is edit for the twin only. Zendesk's field permissions have three options: "Agents can edit", "Customers can edit" and "Customers can view" ([C]). None is "twin only". With the connector, "external AI agents enforce the acting user's role, group access, and permissions" ([A]), so the twin can write the field only when the signed-in agent can, and that agent can also write it by hand.

- Treat the field as a marker, not a security control. It makes the twin's writes visible and reportable. It does not stop an agent editing it on purpose.
- Cross-check against the governance log in [twin-governance](../../plugins/twin-governance/README.md), and against Zendesk's own log: "Transaction logs include records of which external AI agent performed each action and on whose behalf that action was taken." ([A])
- Zendesk's FAQ says a tool call can be blocked by "the acting user’s Zendesk permissions" ([B]); it names no setting that allows one field for the twin only. Record with Security that anyone who can edit tickets can edit the marker.

## Make the skill set it

The ticket-update skill writes at autonomy level 2 and above. The pages say the connection can do "creating and updating tickets" ([A]) but do not list a tool that sets a custom field. **⚠ Unverified:** that an update-ticket tool can set a custom ticket field value; the write test below is how to find out. The skill must:

1. Put the marker in the same ticket update as the change.
2. Use the current time in UTC, ISO 8601, for example `2026-11-16T09:30:00Z`. Set it on every write, never on a read; never a past or future time; never clear it.
3. Fail closed. If the tool rejects the field, do not retry the update without it. Stop and tell the user.
4. Never overwrite tags on the way. The API says that unless told otherwise "the set tag behavior is used, which overwrites and replaces existing tags" ([E]). **⚠ Unverified:** whether the connector's tool does the same; test it on a ticket with two tags.

**(Our recommendation):** the marker is set on every write, and an eval fails when a write leaves it unset. Put the rules in `SKILL.md` and write the eval first ([authoring-skills.md](../../docs/authoring-skills.md)).

## Check it worked

In a sandbox or on one test ticket, with one pilot user:

1. Set the update tool to **Needs approval** and ask the twin to change the priority of the named test ticket. Approve once.
2. Open the ticket's events. Expect a Change event on "Last updated by twin" with the new time, in an audit that shows who made it ([D]). **⚠ Unverified:** that the audit author is the signed-in person; the connection has "its own identity through OAuth 2.1" ([A]), so the author might be shown as the agent.
3. If step 2 shows no person, read the Zendesk Bridge transaction log for the same time. It records "on whose behalf" ([A]).
4. Make a second change. Expect a second Change event with a later time.
5. Change the same ticket by hand in the ticket view without the marker. Expect an audit with no marker event. This is what the report tells apart.

Keep the results, the date and the two users in the engagement folder, not here.

## Report on it

- **A view, any plan.** A view with the condition "Present" on the field lists every ticket the twin has changed ([G]). Views can be shared by admins ([F]). Add the ticket id, requester, assignee and the field as columns.
- **Explore.** "On Suite Professional and above, you can report on custom ticket fields in Explore." ([C]) Report on the field's presence by week. **⚠ Unverified:** whether Explore shows the field's value history or only its latest value; if only the latest, the audit events above are the history.
- The marker records that the twin wrote, not that a person approved it. Approval is the autonomy level and the confirmation step.

## What can go wrong

| Problem | What to do |
|---|---|
| The tool cannot set the field | The write test shows it. Do not go live at level 2; ask Zendesk. |
| Tags on the ticket disappear after a twin update | The tool replaced the tag list ([E]). Block the tool and fix the skill. |
| The field is blank on a twin-changed ticket | The eval should have failed. Fix the skill; the transaction log shows which changes had no marker. |
| An agent cleared or changed the marker | Expected; it is a marker, not a control. Cross-check the governance log. |
| The field is missing on a ticket form | Add it to that form ([C]). |

## Pages used

- [A] [Understanding Zendesk Bridge and allowing external AI agents to perform actions in Zendesk (EAP)](https://support.zendesk.com/hc/en-us/articles/11398710406554)
- [B] [Zendesk Bridge FAQ (EAP)](https://support.zendesk.com/hc/en-us/articles/11458059060250)
- [C] [Adding custom ticket fields to your tickets and forms](https://support.zendesk.com/hc/en-us/articles/4408883152794-Adding-custom-ticket-fields-to-your-tickets-and-forms)
- [D] [Ticket audits (Zendesk API reference)](https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_audits/)
- [E] [Tickets (Zendesk API reference)](https://developer.zendesk.com/api-reference/ticketing/tickets/tickets/)
- [F] [Working with ticket tags](https://support.zendesk.com/hc/en-us/articles/4408835059482-Working-with-ticket-tags)
- [G] [Using custom ticket fields in business rules and views](https://support.zendesk.com/hc/en-us/articles/4408887162394-Using-custom-ticket-fields-in-business-rules-and-views)
