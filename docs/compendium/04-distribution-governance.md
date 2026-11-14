# 04 — Distributing and governing skills

## How each surface gets skills

| Surface | How skills get there | Who controls it | Shares skills with |
|---|---|---|---|
| **Claude.ai, Desktop, Cowork** | An Owner uploads a zip or creates the skill under Organization settings > Plugins & skills. Plugin marketplaces can sync from GitHub or GitLab, by manual re-sync or a webhook on push. | Owners and Primary Owners (**not** the Admin role); on Enterprise, also custom roles with the "Libraries" permission | Claude Code, when signed in with the same account |
| **Claude Code** | Personal `~/.claude/skills/`, project `.claude/skills/` (committed to Git), plugins from marketplaces, enterprise managed settings | Managed settings control which marketplaces and plugins are allowed or required | Receives claude.ai skills in `~/.claude/skills/synced/` (v2.1.273 or later; can be turned off) |
| **Claude API (Skills API)** | `POST /v1/skills` with a zip or files: up to 30 MB per upload, up to 20 skills per request | Anyone holding an API key with access to the workspace | **Nothing.** The API keeps its own separate set |
| **Managed Agents** (beta) | Listed in the agent's `skills` array (up to 500 per session), or loaded automatically from a mounted GitHub repo's `.claude/skills` | Whoever can edit the agent, or commit to that repo | Uses API skills |
| **Agent SDK** | Files on disk only, loaded through `settingSources`. There is no API to register a skill | Your engineers | Nothing |

⚠ **Conflict:** the platform overview and the enterprise pages say custom skills "do not sync across surfaces". The newer Claude Code docs and the provisioning article describe claude.ai → Claude Code sync, so the overview is out of date on that point. The API is still separate.

Sources: [Plugins admin](https://claude.com/docs/plugins/admin), [Org rollout](https://claude.com/docs/plugins/org-rollout), [Provisioning skills](https://support.claude.com/en/articles/13119606-provision-and-manage-skills-for-your-organization), [Claude Code skills](https://code.claude.com/docs/en/skills.md), [Claude Code org plugins](https://code.claude.com/docs/en/plugins/org.md), [Skills API guide](https://platform.claude.com/docs/en/build-with-claude/skills-guide.md), [Managed Agents skills](https://platform.claude.com/docs/en/managed-agents/skills.md), [Agent SDK skills](https://code.claude.com/docs/en/agent-sdk/skills.md).

## Recommended pipeline (our recommendation)

```
Git repo (source of truth: skills, personas, evals, registry)
   │  pull request → review by someone other than the author → evals pass → merge
   ├──► claude.ai org marketplace (synced from GitHub) ──► claude.ai / Desktop / Cowork ──► synced to Claude Code
   ├──► Claude Code marketplace via managed settings (for Claude Code–only variants)
   └──► Skills API: upload, then pin a version (only if a hosted agent needs it)
```

This repository can become that source-of-truth repo once we start building.

## Admin controls on claude.ai

- **Requirements:** turn on both "Cloud code execution and file creation" and "Skills".
- **Default state:** an org skill is turned on for every member by default, though members can turn it off for themselves.
- **Availability levels:** Not available, Available to install, Installed by default, Required.
- **Targeting groups:** bundle the skills into a plugin and set access per group (**Enterprise only**).
- **Version history,** with "Compare with current" and "Revert", for items an Owner uploaded. Items synced from a repo don't get this.
- **Policy switches:**
  - User-created skills, on or off.
  - Peer skill sharing, which is view-only.
  - Sharing with groups.
  - Publishing: Requires review, Open, or Off. Defaults depend on the plan.
- **When people leave:** skills a former member shared stay active until an Owner removes them.

## Governance

From Anthropic's [enterprise skills guidance](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/enterprise.md):

- **Treat installing a skill like installing software.** Use only skills you trust.
  - Higher risk: skills with scripts, MCP references, network calls, hard-coded credentials, or instructions that try to steer Claude.
  - Use the 8-step review checklist on that page.
- **Separate duties.** Authors don't review their own skills.
- **Gate releases on evals:** 3 to 5 queries each for triggering, for the skill working on its own, and for the skill working alongside other skills.
- **Keep a registry:** purpose, owner, version, dependencies and eval status for every skill.
- **Pin versions in production.** On the API, "latest" means anyone in the workspace can change what production runs. Keep checksums, signed commits and a rollback plan.
- **Keep the skill count low.** The more skills are loaded, the less reliably the right one fires. Claude Code's skill list gets about 1% of the context window.

**Security scanning** (Enterprise-only toggle) checks claude.ai and Cowork uploads, and blocks a skill that fails or hasn't finished scanning. It does **not** cover:

- uploads through the API or Console
- skills that existed before scanning was turned on
- orgs with customer-managed encryption keys (CMEK), ZDR or HIPAA.

**Claude Code specifics:**

- Skills in a repo are trusted on sight.
- Plugins can run hooks, MCP servers and programs outside the sandbox.
- Managed settings such as `allowManagedPermissionRulesOnly` and `disableSkillShellExecution` reduce the risk.

Sources: [Plugin security](https://code.claude.com/docs/en/plugins/security.md), [Claude Code skills](https://code.claude.com/docs/en/skills.md).

**Managed Agents repo skills:** anyone who can commit to the mounted repo can change what the agent does, with no review step. Protect that branch.

## Compliance limits

- **Skills aren't eligible for ZDR** and aren't covered by a HIPAA BAA. HIPAA mode turns skills off in local Claude Code and Cowork.
- **The audit log records sharing events, not skill contents.** API skill creates and deletes are logged only if the Compliance API is on.

## Measuring use

| Source | What it gives | Limits |
|---|---|---|
| Claude.ai Inventory | Users and activity over the last 30 days, per skill or plugin | No export |
| `GET /v1/organizations/analytics/skills` | Usage by user, group or product, across chat, Claude Code, Cowork and the Office agent | Enterprise only; one-day lag; data from 2026-01-01 on |
| Claude Code OpenTelemetry | Plugin events | Third-party plugin names are hidden unless `OTEL_LOG_TOOL_DETAILS=1` is set |
| Skills API | None | No usage analytics for API-workspace skills |

Source: [Skills analytics API](https://platform.claude.com/docs/en/api/organization/analytics/skills.md).
