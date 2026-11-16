# 04 — Writing stories

## Hierarchy

| Level | Is | Example |
|---|---|---|
| **Epic** | One role twin for one customer | "Private-equity deal-team twin" |
| **Feature** | A capability that group of users relies on | "Pre-meeting preparation" |
| **Story** | One task the twin does for a user, usually one skill plus its connectors | "Prepare a one-page company brief before a management meeting" |
| **Task** | One piece of implementation work | "Write 3 eval cases", "Configure the Salesforce External Client App" |
| **Spike** | A time-boxed question we need answered | "Confirm that Salesforce role-based access holds through the MCP server, using a test user on each side of a wall" |
| **Bug** | Something that fails an eval or a user | "The brief cites a closed opportunity as open" |

These match the `type:` labels in this repo (`type:epic`, `type:feature`, `type:story`, `type:task`, `type:spike`, `type:bug`). Customer backlogs can live in the customer's own tracker, using the same levels.

## Story template

```markdown
**As a** <role>, **I want** my twin to <task> **so that** <outcome>.

| Field | Value |
|---|---|
| Data class | internal / confidential / highly sensitive / PHI  (compendium 10) |
| Surface | client (claude.ai, Desktop, Claude Code) / hosted (which)  (compendium 05) |
| Autonomy level | 0–4  (compendium 06) |
| Connectors and identity | <system>: per-user / shared; read / write  (compendium 11) |
| Wall impact | none / soft / hard  (compendium 14) |
| Inputs | <systems, documents> |
| Output and audience | <what, who sees it> |
| Skill owner | <name> |
| Baseline | <how long it takes today, how often> |

**Acceptance criteria (evals):**
1. <eval case from a real example, with the expected result>
2. ...
3. ...
Plus: the skill triggers on <phrases>; no web tools (if MNPI); every write carries the twin marker; each tool call is logged to the governance log (metadata only, for private equity).

**Target:** edit rate below <x>%, and at least <y> minutes saved per task.
```

## Definition of ready (before building)

- The data class, surface, autonomy level and identity are filled in.
- At least 3 real examples have been collected from the skill owner.
- The connectors exist, or there is a spike or task to provide them.
- Compliance has signed off on any story above the "confidential" data class.

## Definition of done

- The evals pass on the models the customer uses.
- A reviewer who isn't the author has approved it.
- The skill is published to the right group, at the right version.
- Tool calls appear in the governance log.
- The skill owner has been shown how to update it.

## Example

**As a** deal-team associate, **I want** my twin to prepare a one-page company brief before a management meeting **so that** I spend 20 minutes on prep instead of 90.

| Field | Value |
|---|---|
| Data class | Highly sensitive (private equity) |
| Surface | Claude Code on a ZDR sign-in, on a managed device (no Desktop), in the private-equity ZDR org |
| Autonomy level | 1 (draft only) |
| Connectors and identity | Salesforce (opportunity, account), per-user, read-only. SharePoint (deal folder), per-user, read-only. |
| Wall impact | Soft: relies on Salesforce and SharePoint role-based access |
| Output and audience | A one-page brief, for internal use only |

**Acceptance criteria:**

1. For the 3 example deals, the brief contains the stage, the key contacts, open diligence items and the last three interactions, and each item links to its source record.
2. If the deal folder is empty, the brief says what's missing instead of guessing.
3. A user without access to a deal gets no data from it.
4. Web tools are off, and the governance log shows record IDs only.
