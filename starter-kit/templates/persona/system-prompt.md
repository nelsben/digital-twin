<!--
The system prompt for the twin, for the Messages API (the system parameter),
Managed Agents (the agent's system prompt) or claude.ai project instructions
(paste into the Project's instructions).

Built from persona.md: each tag below holds persona.md sections 1 to 10, in the
same order and in the same words. Change persona.md first, then both forms, in
the same PR. Delete this comment before you use the prompt.

Why this shape, from Anthropic's prompting best practices
(https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices):
a role in the first line; context (who and why) before the rules; a reason
with every rule; one XML tag per kind of content, with the same tag names
every time. If you add reference material of any length (a playbook, product
facts), put it above these tags, in its own <document> tags, not inside a rule.
Keep it short: procedures go in skills, and facts that are always true go in a
reference file or project knowledge.
-->

<role>
FILL IN: copy persona.md section 1.
</role>

<context>
FILL IN: copy persona.md section 2.
</context>

<voice>
FILL IN: copy persona.md section 3.
</voice>

<rules>
<do>
FILL IN: copy persona.md section 4.
</do>
<never>
FILL IN: copy persona.md section 5.
</never>
<ask_first>
FILL IN: copy persona.md section 6.
</ask_first>
</rules>

<uncertainty>
FILL IN: copy persona.md section 7.
</uncertainty>

<escalation>
FILL IN: copy persona.md section 8.
</escalation>

<twin_marker>
FILL IN: copy persona.md section 9.
</twin_marker>

<data_classes>
FILL IN: copy persona.md section 10.
</data_classes>
