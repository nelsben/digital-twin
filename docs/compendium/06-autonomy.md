# 06 — How much the twin may do on its own

Autonomy isn't a yes-or-no setting. **Plan** it per task (our recommendation), but know where it is **enforced**: in chat and Cowork, per connector tool. A task can only be as free as the settings on the tools it uses, so the same twin can act on one task and only draft on another only when those tasks use different tools. See [How a level is enforced](#how-a-level-is-enforced).

## The ladder (our recommendation)

| Level | The twin… | A person… | Fits | Controls |
|---|---|---|---|---|
| **0 Advise** | Answers questions, explains, finds things | Does all the work | Policy questions, "where is…" | Read-only connectors |
| **1 Draft** | Prepares the work (emails, briefs, CRM updates, reports) | Reviews it and acts | **All pilots to start** | Write tools Blocked, or left out of the role plugin |
| **2 Act with approval** | Carries out the action after the person approves each step | Approves each action | CRM field updates, sending internal messages | Connector tools set to **Needs approval**; `always_ask` in Managed Agents |
| **3 Act within an allowlist** | Acts without asking on a short list of reversible, internal tasks, and logs each one | Reviews the log afterwards | Tagging tickets, filing notes, updating its own task list | Allowlisted tools set to **Always allow**, everything else Needs approval; hooks enforce the limits; audit log |
| **4 Run unattended** | Runs on a schedule or event with nobody present | Gets a report and handles exceptions | A nightly health scan posted to a channel | Hosted runtime with pinned versions, limited credentials, budgets, success checks and reconciliation |

Sources: [Connectors](https://claude.com/docs/connectors/getting-started.md) (Always allow, Needs approval and Blocked settings), [Managed Agents MCP](https://platform.claude.com/docs/en/managed-agents/mcp-connector.md) (`always_ask` is the default), [Output styles](https://code.claude.com/docs/en/output-styles.md) (put guardrails in hooks).

## How a level is enforced

- **In chat and Cowork, per connector tool.** On a connector's page, each group of tools or single tool is set to Always allow, Needs approval or Blocked ([Connectors](https://claude.com/docs/connectors/getting-started.md)). The page describes no setting per skill, plugin or task.
- **So a task's level is the strictest setting any of its tools needs.** Two tasks that share a tool share that tool's setting. If a level-1 task and a level-3 task both use the same CRM write tool, that tool can't be both Blocked and Always allow: either split the tools or run both tasks at the stricter level. (Our reading of the connector settings.)
- **In Claude Code, a skill can narrow tools for its own turn.** `disallowed-tools` in a skill's frontmatter removes tools "from Claude's available pool while this skill is active", and the restriction clears when the user sends the next message. `allowed-tools` only pre-approves tools for that turn; it "does not restrict which tools are available". `disallowed-tools` is rejected in claude.ai and Skills API uploads, so this works in Claude Code only ([Claude Code skills](https://code.claude.com/docs/en/skills.md)).
- **Skill hooks are session-wide, not per skill.** Hooks in a skill's frontmatter are registered when the skill is invoked and keep running "for the rest of the session" ([Claude Code skills](https://code.claude.com/docs/en/skills.md)). A PreToolUse hook can block a tool call ([Hooks](https://code.claude.com/docs/en/hooks)). ⚠ **Unverified:** whether a PreToolUse hook can tell which skill is active, which it would need to enforce a level per skill.

## Rules for moving up a level

1. **The action can be undone, or it is internal,** before it goes above level 2. Anything a customer sees, anything financial, and anything that deletes stays at level 1 or 2.
2. **Evals show the task is reliable** at the current level before you move up ([03](03-skills-authoring.md)).
3. **Define what success means.** A scheduled task that "Succeeded" only means the session ended cleanly, not that the work got done. Add an explicit check. ([Scheduled tasks](https://code.claude.com/docs/en/routines.md))
4. **Plan for missed runs.** Managed Agents doesn't re-run a schedule it missed, and its webhooks give up after 3 delivery attempts and "aren't a durable log". Something has to reconcile. ([Scheduled deployments](https://platform.claude.com/docs/en/managed-agents/scheduled-deployments.md), [Webhooks](https://platform.claude.com/docs/en/managed-agents/webhooks.md))
5. **An unattended run can't ask anyone.** At level 4, `always_ask` blocks the run. Every approval has to be decided in advance, in policy.

## The trade-off in one line

Each level up saves people time, but makes mistakes costlier and harder to see. The risk compounds, as Anthropic's "building effective agents" warns. Start at level 1, and earn each level with evidence from evals.
