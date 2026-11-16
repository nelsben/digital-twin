# Persona template

One twin persona, kept in one source, shipped in two forms so the twin behaves the same on every surface. The fields come from
[docs/compendium/02-persona.md](../../../docs/compendium/02-persona.md).

```
persona/
  persona.md                  the single source: ten FILL IN sections
  output-style/
    your-twin-name.md         Claude Code output style, built from persona.md
  system-prompt.md            system prompt, built from persona.md
```

## Which form goes where

| Surface | Form | Where it goes |
|---|---|---|
| Claude Code | Output style | The role plugin's `output-styles/` folder |
| claude.ai (and Desktop) | System prompt | The Project's instructions |
| Hosted agents (Messages API, Managed Agents, Agent SDK) | System prompt | The `system` field or the agent's system prompt |

Claude Code facts that are always true go in CLAUDE.md, not in the persona. Hard limits are enforced by tool permissions and hooks: a persona is an instruction, not a guarantee.

## Fill it in

1. Copy the folder into the role plugin in [the customer's delivery repo](../../README.md#start-a-new-customer) as that plugin's `persona/` folder. This is the layout `starter-kit/plugins/twin-pe-deal-team` uses: `persona/persona.md`, `persona/system-prompt.md`, and the output style in the plugin's `output-styles/` folder.
2. Fill in `persona.md` first, section by section, in the second person. Give the reason for every rule. Keep it short; procedures belong in skills.
3. Build the output style: copy the sections into `output-style/your-twin-name.md`, set `name` and `description`, rename the file, and put the finished output style in that role plugin's `output-styles/` folder in the customer's delivery repo.
4. Build the system prompt: copy the same sections into the matching tags in `system-prompt.md`.
5. Delete the comment at the top of each form and every FILL IN marker.
6. Check that both forms match `persona.md` section by section. This kit's `tests/test_persona.py` makes that check for the plugins kept in this repo, and can be copied into the delivery repo to run there.

## The rule

A persona change updates `persona.md` and both forms in the same PR. Never edit one form alone: the forms drift, and the twin then behaves differently on claude.ai and in Claude Code.

## Frontmatter keys used

Output style keys (`name`, `description`, `keep-coding-instructions`, optional `force-for-plugin`) are from
[Output styles](https://code.claude.com/docs/en/output-styles). Prompt shape (role first, context before rules, reasons, XML tags) follows
[Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices).

## Worked example

The private-equity deal team example is written under issue #37, in
[twin-pe-deal-team](../../plugins/twin-pe-deal-team/README.md). It is not part of this template.
