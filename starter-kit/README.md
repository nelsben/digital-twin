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
| [templates/skill](templates/skill/README.md) | The starting folder for every twin skill: `SKILL.md`, references and evals |
| [templates/persona](templates/persona/README.md) | One persona source, shipped as an output style and a system prompt |
| [settings](settings/README.md) | Managed-settings baselines, one per data class, for IT to deploy |
| [docs/authoring-skills.md](docs/authoring-skills.md) | The step order for writing and evaluating a skill, evals first |
| [tests](../tests) | Structure, settings and governance-hook tests; run before every PR |
| [engagements/sample-pe](../engagements/sample-pe/README.md) | The worked example: an invented private-equity customer, discovery through backlog |

## Using it on an engagement

The phases are in [docs/playbook/01-engagement-model.md](../docs/playbook/01-engagement-model.md). Phase 0 (Qualify) needs no kit parts.

| Phase | Kit parts used |
|---|---|
| 1. Discovery | [sample-pe](../engagements/sample-pe/README.md) shows a finished questionnaire, stakeholder map and candidate tasks to copy the shape from |
| 2. Design | The [settings](settings/README.md) baselines (pick one per org); sample-pe `design.md` and `backlog.md` as models; [compendium 16](../docs/compendium/16-oob-skills-and-references.md) to choose what to reuse |
| 3. Build | [templates/skill](templates/skill/README.md) and [authoring-skills.md](docs/authoring-skills.md) for each story; [templates/persona](templates/persona/README.md); the role and shared plugins; [twin-governance](plugins/twin-governance/README.md); the [tests](../tests) |
| 4. Pilot | The governance log from twin-governance feeds the scorecard; settings baselines are deployed to pilot devices |
| 5. Scale | Copy the skill template and persona template for each new role; add the plugin to the marketplace; promote autonomy on scorecard evidence |
| 6. Run / hand over | The marketplace repo, evals and tests become the customer's; the governance log destination stays with their IT |

## Start a new customer

1. Copy [engagements/sample-pe](../engagements/sample-pe/README.md) as the folder layout for `engagements/<customer>/`. Copy the structure, not the invented content.
2. Fork or copy this kit's [marketplace](../.claude-plugin/marketplace.json) and `starter-kit/plugins/` into the customer's repo, and rename the role plugin.
3. Fill in the persona from [templates/persona](templates/persona/README.md): `persona.md` first, then the output style and the system prompt.
4. Copy [templates/skill](templates/skill/README.md) once per story, evals first, following [authoring-skills.md](docs/authoring-skills.md).
5. Pick a [settings baseline](settings/README.md) per org, and replace `REPLACE-WITH-ORG-UUID` and `REPLACE-WITH-GITHUB-ORG`.
6. Deploy [twin-governance](plugins/twin-governance/README.md) through the managed marketplace, not as a user install, so its hook runs under `allowManagedHooksOnly`.

## Reuse before you build

Compendium 16 ends with [six decisions](../docs/compendium/16-oob-skills-and-references.md#what-the-starter-kit-takes-from-this). In short:

1. Scaffold and evaluate every skill with skill-creator.
2. Seed the skill template from Anthropic's `template-skill`.
3. Start each pilot role from the matching Anthropic role plugin, then customise it.
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

Use skill-creator to author and evaluate skills ([authoring-skills.md](docs/authoring-skills.md) has the full loop):

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
