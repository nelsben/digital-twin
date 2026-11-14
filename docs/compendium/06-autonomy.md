# 06 — How much the twin may do on its own

Autonomy isn't a yes-or-no setting. Give it **per task, not per twin**: the same twin can act freely on one task and only draft on another.

## The ladder (our recommendation)

| Level | The twin… | A person… | Fits | Controls |
|---|---|---|---|---|
| **0 Advise** | Answers questions, explains, finds things | Does all the work | Policy questions, "where is…" | Read-only connectors |
| **1 Draft** | Prepares the work (emails, briefs, CRM updates, reports) | Reviews it and acts | **All pilots to start** | Write tools Blocked, or left out of the role plugin |
| **2 Act with approval** | Carries out the action after the person approves each step | Approves each action | CRM field updates, sending internal messages | Connector tools set to **Needs approval**; `always_ask` in Managed Agents |
| **3 Act within an allowlist** | Acts without asking on a short list of reversible, internal tasks, and logs each one | Reviews the log afterwards | Tagging tickets, filing notes, updating its own task list | Allowlisted tools set to **Always allow**, everything else Needs approval; hooks enforce the limits; audit log |
| **4 Run unattended** | Runs on a schedule or event with nobody present | Gets a report and handles exceptions | A nightly health scan posted to a channel | Hosted runtime with pinned versions, limited credentials, budgets, success checks and reconciliation |

Sources: [Connectors](https://claude.com/docs/connectors/getting-started.md) (Always allow, Needs approval and Blocked settings), [Managed Agents MCP](https://platform.claude.com/docs/en/managed-agents/mcp-connector.md) (`always_ask` is the default), [Output styles](https://code.claude.com/docs/en/output-styles.md) (put guardrails in hooks).

## Rules for moving up a level

1. **The action can be undone, or it is internal,** before it goes above level 2. Anything a customer sees, anything financial, and anything that deletes stays at level 1 or 2.
2. **Evals show the task is reliable** at the current level before you move up ([03](03-skills-authoring.md)).
3. **Define what success means.** A scheduled task that "Succeeded" only means the session ended cleanly, not that the work got done. Add an explicit check. ([Scheduled tasks](https://code.claude.com/docs/en/routines.md))
4. **Plan for missed runs.** Managed Agents doesn't re-run a schedule it missed, and its webhooks give up after 3 delivery attempts and "aren't a durable log". Something has to reconcile. ([Scheduled deployments](https://platform.claude.com/docs/en/managed-agents/scheduled-deployments.md), [Webhooks](https://platform.claude.com/docs/en/managed-agents/webhooks.md))
5. **An unattended run can't ask anyone.** At level 4, `always_ask` blocks the run. Every approval has to be decided in advance, in policy.

## The trade-off in one line

Each level up saves people time, but makes mistakes costlier and harder to see. The risk compounds, as Anthropic's "building effective agents" warns. Start at level 1, and earn each level with evidence from evals.
