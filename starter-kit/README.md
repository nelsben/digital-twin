# Digital twin starter kit

## What this is

The starter kit is the set of parts we copy into a customer's repo to build a role-based Claude twin: a plugin marketplace, plugins, skill and persona templates, managed-settings baselines, a governance hook, tests and a worked sample engagement. The [partner playbook](../docs/playbook/README.md) says how we run an engagement; the [compendium](../docs/compendium/README.md) says what is true about Claude; this kit is what we build with. Read this page first, then follow the links.

## What's inside

| Part | What it is for |
|---|---|
| [Marketplace](../.claude-plugin/marketplace.json) | The one reviewed customer marketplace, `digital-twin-kit`, listing the three plugins below |
| [twin-shared](plugins/twin-shared/README.md) | The common plugin every role twin installs, for skills that are not role-specific |
| [twin-pe-deal-team](plugins/twin-pe-deal-team/README.md) | The role twin for a private equity deal team: skills and output style |
| [twin-governance](plugins/twin-governance/README.md) | Governance guardrails as hooks, including the metadata-only governance log |
| [templates/role-plugin](templates/role-plugin/README.md) | The starting folder for one role plugin (one per role, never per person): manifest, README, empty skills and output styles, persona pointer, and the steps to add it to the marketplace |
| [templates/skill](templates/skill/README.md) | The starting folder for every twin skill: `SKILL.md`, references and evals |
| [templates/persona](templates/persona/README.md) | One persona source, shipped as an output style and a system prompt |
| [templates/pilot](templates/pilot/README.md) | The pilot's fill-in files, one per pilot task in the backlog |
| [templates/pilot/scorecard.md](templates/pilot/scorecard.md) | The monthly scorecard for one twin and its decision to stay, move up or move down a level |
| [templates/pilot/memory-policy.md](templates/pilot/memory-policy.md) | What the twin may remember for one role and what it must not, with the sign-off |
| [templates/pilot/pilot-training.md](templates/pilot/pilot-training.md) | The pilot users' training session and where they report a failure |
| [runbooks/identity-devices-publishing.md](runbooks/identity-devices-publishing.md) | SCIM groups, the managed-settings rollout, and publishing the marketplace to the right groups |
| [runbooks/salesforce-hosted-mcp.md](runbooks/salesforce-hosted-mcp.md) | Connect Salesforce through its hosted MCP server with per-user OAuth |
| [runbooks/microsoft-365-connector.md](runbooks/microsoft-365-connector.md) | Connect Microsoft 365: tenant consent, a SharePoint access check, and Outlook mail and calendar |
| [runbooks/hubspot-connector.md](runbooks/hubspot-connector.md) | Connect HubSpot to a role's twin |
| [runbooks/google-workspace-connectors.md](runbooks/google-workspace-connectors.md) | Connect Google Drive, Gmail and Google Calendar to a role's twin |
| [runbooks/slack-connector.md](runbooks/slack-connector.md) | Connect Slack to a role's twin, for reading and searching Slack |
| [runbooks/zendesk-connector.md](runbooks/zendesk-connector.md) | Connect Zendesk to a role's twin |
| [runbooks/claude-code-scheduled-task.md](runbooks/claude-code-scheduled-task.md) | Set up a Claude Code scheduled task for a twin's task |
| [runbooks/claude-tag-routine.md](runbooks/claude-tag-routine.md) | Set up a Claude Tag routine in a Slack channel for a twin's task |
| [runbooks/managed-agents.md](runbooks/managed-agents.md) | Set up a task on Managed Agents, hosted or self-hosted |
| [runbooks/agent-sdk-runner.md](runbooks/agent-sdk-runner.md) | Build and host an Agent SDK runner for a task |
| [runbooks/verification-log.md](runbooks/verification-log.md) | When each runbook was last checked against its sources, and by whom |
| [settings](settings/README.md) | Managed-settings baselines, one per data class, for IT to deploy |
| [docs/authoring-skills.md](docs/authoring-skills.md) | The step order for writing and evaluating a skill, evals first |
| [tests](../tests) | Structure, settings and governance-hook tests; run before every PR |
| [engagements/sample-pe](../engagements/sample-pe/README.md) | The worked example: an invented private-equity customer, discovery through backlog |
| [engagements/sample-team-cs](../engagements/sample-team-cs/README.md) | The second worked example: an invented software company on the Team plan, interview notes through dashboard |

## Using it on an engagement

The phases are in [docs/playbook/01-engagement-model.md](../docs/playbook/01-engagement-model.md). Phase 0 (Qualify) starts the customer profile from the [partner kit's template](../partner-kit/plugins/twin-consultant/templates/customer-profile.json) as the fit note.

| Phase | Kit parts used |
|---|---|
| 1. Discovery | [sample-pe](../engagements/sample-pe/README.md) shows a finished questionnaire, stakeholder map and candidate tasks to copy the shape from. The persona-card workflow turns the interviews into a card: [playbook 05](../docs/playbook/05-persona-card-workflow.md) |
| 2. Design | The [settings](settings/README.md) baselines (pick one per org); sample-pe `design.md` and `backlog.md` as models; [compendium 16](../docs/compendium/16-oob-skills-and-references.md) to choose what to reuse. The levelled plan, backlog and dashboard come from the card: [playbook 05](../docs/playbook/05-persona-card-workflow.md) |
| 3. Build | [templates/skill](templates/skill/README.md) and [authoring-skills.md](docs/authoring-skills.md) for each story; the runbooks above for each connector and runtime the backlog names; [templates/persona](templates/persona/README.md); the role and shared plugins; [twin-governance](plugins/twin-governance/README.md); the [tests](../tests) |
| 4. Pilot | The [pilot templates](templates/pilot/README.md) (scorecard, memory policy, training); the governance log from twin-governance feeds the scorecard; settings baselines are deployed to pilot devices |
| 5. Scale | Copy the skill template and persona template for each new role; add the plugin to the marketplace; promote autonomy on scorecard evidence |
| 6. Run / hand over | The marketplace repo, evals and tests become the customer's; the governance log destination stays with their IT |

## Start a new customer

1. Copy [engagements/sample-pe](../engagements/sample-pe/README.md) as the folder layout for `engagements/<customer>/`. Copy the structure, not the invented content.
2. Fork or copy this kit's [marketplace](../.claude-plugin/marketplace.json) and `starter-kit/plugins/` into the customer's repo. Make one role plugin per role from [templates/role-plugin](templates/role-plugin/README.md).
3. Fill in the persona from [templates/persona](templates/persona/README.md): `persona.md` first, then the output style and the system prompt.
4. Copy [templates/skill](templates/skill/README.md) once per story, evals first, following [authoring-skills.md](docs/authoring-skills.md).
5. Pick a [settings baseline](settings/README.md) per org, and replace `REPLACE-WITH-ORG-UUID` and `REPLACE-WITH-GITHUB-ORG`.
6. Deploy [twin-governance](plugins/twin-governance/README.md) through the managed marketplace, not as a user install, so its hook runs under `allowManagedHooksOnly`.

## Reuse before you build

Compendium 16 ends with [six decisions](../docs/compendium/16-oob-skills-and-references.md#what-the-starter-kit-takes-from-this). In short:

1. Scaffold and evaluate every skill with skill-creator.
2. Seed the skill template from Anthropic's `template-skill`.
3. Start each pilot role from the matching Anthropic role plugin, then customise it. Install Anthropic's plugins on your own unmanaged machine, not on a customer's managed device; see [Install skill-creator](docs/authoring-skills.md#install-skill-creator).
4. Don't rebuild the document skills.
5. Run one reviewed customer marketplace, and restrict other marketplaces through managed settings.
6. Treat section 4 of compendium 16 as the only link list.

## Working with Claude on this repo

Claude (or a consultant pointing Claude at this repo) should read this README and the [compendium](../docs/compendium/README.md) first, so its answers use our defaults and our sources.

Install the marketplace locally. From the repo root, in Claude Code:

```
/plugin marketplace add ./
/plugin install twin-shared@digital-twin-kit
```

Shell form: `claude plugin marketplace add ./` and `claude plugin install twin-shared@digital-twin-kit`. Use `claude plugin validate .` to check the manifests ([CLI reference](https://code.claude.com/docs/en/plugins/cli-reference)).

Run the tests from the repo root:

```
python3 -m unittest discover -s tests
```

Use skill-creator to author and evaluate skills ([authoring-skills.md](docs/authoring-skills.md) has the full loop). Install it on your own unmanaged machine, not on a customer's managed device; why is in [Install skill-creator](docs/authoring-skills.md#install-skill-creator):

```
/plugin install skill-creator@claude-plugins-official
```

## Anthropic references

Every link is from section 4 of [compendium 16](../docs/compendium/16-oob-skills-and-references.md#4-reference-index-of-anthropic-best-practice-docs), which holds the full list.

| Link | What it is for |
|---|---|
| [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) | How skills load, where they work, field limits, ZDR status |
| [Skill best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) | Anthropic's skill authoring guidance |
| [Claude Code skills](https://code.claude.com/docs/en/skills) | Frontmatter fields, bundled skills, "Run evals with skill-creator" |
| [anthropics/skills](https://github.com/anthropics/skills) | Example skills, the spec folder and the template |
| [Plugin evals](https://code.claude.com/docs/en/plugin-evals) | `claude plugin eval`: cases, graders, CI gating |
| [Discover plugins](https://code.claude.com/docs/en/discover-plugins) | Installing plugins, scopes, adding marketplaces |
| [Creating a marketplace](https://code.claude.com/docs/en/plugin-marketplaces) | Creating and running a marketplace |
| [Org plugin management](https://code.claude.com/docs/en/plugins/org) | Pre-installing and restricting plugins for an organisation |
| [Managed settings](https://code.claude.com/docs/en/managed-settings) | Organisation-wide settings deployed to machines |
| [Hooks](https://code.claude.com/docs/en/hooks) | Hook events, inputs and outputs |
| [Output styles](https://code.claude.com/docs/en/output-styles) | Changing Claude Code's response style |
| [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) | Role and system-prompt advice |
