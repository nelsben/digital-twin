# 01 — What a twin is made of

A digital twin is a bundle of seven parts. Each part has its own Anthropic mechanism and its own decision.

| Part | What it is | Claude mechanisms | Covered in |
|---|---|---|---|
| **Persona** | The role, purpose, audience, tone and boundaries | API: system prompt. Claude Code: output style plus CLAUDE.md. Claude.ai: Project instructions (**⚠ Unverified:** see [02](02-persona.md)) | [02](02-persona.md) |
| **Skills** | Know-how: procedures, templates, domain knowledge, scripts | Agent Skills (`SKILL.md` folders) | [03](03-skills-authoring.md), [04](04-distribution-governance.md) |
| **Connectors** | Access to systems: CRM, ticketing, email, files | MCP servers (claude.ai org connectors, Claude Code MCP, Managed Agents MCP) | [05](05-decision-matrix.md) |
| **Runtime** | Where the twin runs and what starts it | Client (claude.ai, Desktop, Claude Code) or hosted (Agent SDK, Messages API, Managed Agents, Claude Tag in Slack, scheduled tasks) | [05](05-decision-matrix.md) |
| **Identity** | Whose name and permissions its actions carry | The user's own account, a service account, or an API key plus a credential vault | [05](05-decision-matrix.md) |
| **Memory** | What carries over between sessions | Claude.ai memory, Project memory, the API memory tool, Managed Agents memory stores, Claude Tag channel memory | [02](02-persona.md) |
| **Guardrails** | What it may do without asking, and what it may never do | Tool permissions set per connector tool (Always allow, Needs approval, Blocked), so autonomy is enforced per tool, not per task; in Claude Code, a skill's `disallowed-tools` and hooks; Managed Agents `always_ask` | [06](06-autonomy.md) |

A sixth discipline sits across all of these: **evaluation.** It tells you whether the twin actually does the job, and whether it still does after a model update.

## One role, one package (our recommendation)

Package each role twin as **one plugin per role**: for example `sales-twin`, `cs-twin` and `ops-twin`. A plugin bundles skills and can reference connectors, and it is the unit an admin distributes.

- **On claude.ai,** Owners publish plugins to the org, set each one to Available, Installed by default or Required, and (on Enterprise) target groups. ([Plugins admin](https://claude.com/docs/plugins/admin))
- **In Claude Code,** a Claude Code plugin can also carry an output style (the persona), hooks (guardrails) and MCP servers. ([Features overview](https://code.claude.com/docs/en/features-overview.md))
- **Shared skills,** such as "write in house style" or "account research brief", go in a common plugin that every role installs. Each role plugin then stays small.

**The catch:** making a plugin available doesn't connect its connectors. An Owner still has to add each connector, and each member has to sign in to it. ([Plugins admin](https://claude.com/docs/plugins/admin))

## The engineering principles behind every decision

These come from Anthropic's engineering writing. They are why the later pages recommend what they do.

1. **Start with the simplest thing that works.** Prefer workflows (fixed, predictable steps) until you truly need open-ended autonomy. Autonomy brings "higher costs, and the potential for compounding errors". ([Building effective agents](https://www.anthropic.com/engineering/building-effective-agents))
2. **Context is a finite budget.** Load information just in time instead of all at once. Skills follow this by design: about 100 tokens of description are always loaded, and the body loads only when the skill fires. ([Context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), [Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview.md))
3. **Fewer, better tools.** "More tools don't always lead to better outcomes." Give each tool a clear purpose, high-signal results and errors that say what to do next. ([Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents))
4. **Multi-agent setups cost a lot.** They use about 15 times the tokens of a chat. They suit broad, parallel research, not tightly linked steps. ([Multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system))
5. **Long-running work needs state outside the conversation.** Use progress files, task lists and git. Watch for the agent "declaring victory early". ([Long-running harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents))
6. **Explain the why.** Claude follows instructions better when it knows why they matter. ([Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices.md))
