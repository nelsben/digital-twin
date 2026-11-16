# 03 — Writing skills

## What a skill is

A skill is a folder with a `SKILL.md` file (YAML frontmatter plus Markdown instructions). It can also bundle scripts, reference files and assets. Claude loads a skill in three stages:

1. **Always loaded:** the name and description, about 100 tokens per skill.
2. **When the skill fires:** the body. Keep it under about 5,000 tokens or 500 lines.
3. **Only when read:** bundled files. When a script runs, only its output enters the context.

Claude chooses a skill by matching the user's request against each description. **The description is the trigger.**

Source: [Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview.md). Skills follow the open Agent Skills standard ([agentskills.io](https://agentskills.io), announced in [Equipping agents with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)).

## Skill, connector, persona or CLAUDE.md?

| Put it in… | When it is… | Example |
|---|---|---|
| **Persona** | Always true about the role's purpose, tone and limits | "Draft, don't send." |
| **CLAUDE.md** (Claude Code) | Always-relevant facts about a workspace | Folder layout, team glossary |
| **Skill** | A procedure, template or body of knowledge needed for *some* tasks | "How we write a QBR summary" |
| **MCP connector** | Access to a live system or data | Read and update CRM records |
| **Skill + connector** | Most real tasks | A connector fetches the account; the skill says how to turn it into a brief |

Anthropic puts it this way: MCP gives Claude the tools, and skills give Claude the knowledge of how to use them. Use both. ([Features overview](https://code.claude.com/docs/en/features-overview.md))

## Frontmatter: write for every surface

Each surface accepts different frontmatter, so a skill written for one may break on another.

| Surface | Rules |
|---|---|
| Claude.ai and the Skills API | `name` and `description` are required. Only `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools` are accepted; anything else is **rejected** at upload. Inline `` !`cmd` `` commands don't run. |
| Claude Code | Every field is optional, and many extras are available (`when_to_use`, `disable-model-invocation`, `allowed-tools`, `context: fork`, `paths`, `hooks`, `model`…). Descriptions are cut off at 1,536 characters in the listing. |

The `name` field allows 64 characters at most: lowercase letters, numbers and hyphens, with no "anthropic" or "claude".

**⚠ Conflict:** the platform docs allow a 1,024-character `description`, but the claude.ai help article says 200. **Keep descriptions under 200 characters** until this is resolved.

**(Our recommendation)** Use `name` and `description` only by default. Add Claude Code–only keys in a Claude Code–specific variant, never in the shared master copy.

Sources: [Claude Code skills](https://code.claude.com/docs/en/skills.md), [Create custom skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills).

## Writing a good description

- Say **what it does and when to use it**, in the third person.
- Include the words people actually type ("QBR", "renewal", "month-end close").
- Be specific. "Helps with sales" never fires. "Builds a one-page account brief before a customer call from CRM, recent emails and news" does.

## Writing the body

From [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices.md):

- **Be concise.** Context is a shared resource, so add only what Claude doesn't already know. Keep the body under 500 lines. Link reference files directly from `SKILL.md`, one level deep. Give any reference file over 100 lines a table of contents.
- **Match freedom to fragility:**
  - **High freedom** (prose guidance) for judgment work, like a call-prep brief.
  - **Medium** (templates, scripts with parameters) for work with a standard shape, like a QBR outline.
  - **Low** (exact scripts) for fragile steps, like a reconciliation calculation.
- **Naming:** gerund form is suggested (`preparing-account-briefs`). Avoid `helper` and `utils`.
- **Avoid:** offering too many options, information that goes stale, inconsistent terms, deeply nested references, scripts that leave error handling to Claude, unexplained "magic numbers", and Windows-style paths.
- **Name MCP tools in full,** as `Server:tool`.

## Evaluate first, then iterate

Anthropic's method:

1. Run the real task **without** a skill and note where Claude falls short.
2. Write at least **three evaluation cases** from those failures, and record the baseline.
3. Write the **minimum** instructions that fix the failures.
4. Rerun and iterate. Test on Haiku, Sonnet and Opus, because a skill that works on one model may not work on another.

To iterate, use **"Claude A / Claude B"**: write the skill with one Claude, test it with a fresh one on real tasks, then bring what you observed back to the first.

**Tools that help:**

- The **`skill-creator`** plugin for Claude Code. It stores test cases in `evals/evals.json`, compares results with and without the skill, runs blind A/B tests between versions, tunes the description for triggering, and shows results in an HTML viewer.
- **`claude plugin eval`**, which runs evaluation suites from the command line or in CI.

**⚠ Conflict:** the best-practices page still says there is "not currently a built-in way" to run evaluations; that statement predates these tools. **⚠ Unverified:** whether skill-creator works inside claude.ai.

Sources: [Claude Code skills](https://code.claude.com/docs/en/skills.md), [Plugin evals](https://code.claude.com/docs/en/plugin-evals.md).

## Skeleton

```markdown
---
name: preparing-account-briefs
description: Builds a one-page account brief before a customer call from CRM data, recent emails and news. Use when asked to prep for a call or meeting.
---

# Preparing account briefs

## When this applies
<one or two lines>

## Steps
1. <step, and why it matters>
2. ...

## Output format
<template, or link: see [template.md](template.md)>

## Watch out for
- <known failure from evals>
```
