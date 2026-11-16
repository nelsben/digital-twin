# 16 — Out-of-the-box skills, plugins and reference docs

The starter kit should reuse what Anthropic already ships, not rebuild it. This page answers three things: **what exists today**, **where it lives**, and **whether a twin engagement should adopt, adapt or skip it**. It ends with an index of Anthropic best-practice docs that every kit page can link to.

**Verdicts used below**

- **Adopt:** use as shipped.
- **Adapt:** use as a starting point and change it for the customer (their tools, terms, brand).
- **Skip:** don't use it in a twin engagement by default.

All verdicts are (Our recommendation). Everything else is from the primary source linked beside it. Facts were checked on 2026-11-14 against the GitHub repositories (through the GitHub API) and the doc pages named.

## 1. Skills in github.com/anthropics/skills

Repo: https://github.com/anthropics/skills. The repo root has no licence file (GitHub reports none). Each skill folder carries its own `LICENSE.txt`, and the README says "Many skills in this repo are open source (Apache 2.0)" and that the four document skills "are also open source (Apache 2.0)" ([README](https://github.com/anthropics/skills/blob/main/README.md)). The README's disclaimer matters: these skills are "for demonstration and educational purposes only", and "the implementations and behaviors you receive from Claude may differ". So treat them as reference patterns that we test, not as supported products.

The repo has 19 skills, a template and a spec folder. In the "Licence" column, "Apache 2.0" means the skill's own `LICENSE.txt` begins with the Apache License, Version 2.0 text, and its `SKILL.md` frontmatter says "Complete terms in LICENSE.txt" (except where noted).

| Skill | What it does | Licence | Twin roles or kit steps | Verdict |
|---|---|---|---|---|
| [skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator) | Creates and improves skills, runs evals, benchmarks with-skill against without-skill, and tunes descriptions for triggering | Apache 2.0 (`LICENSE.txt`; no `license:` field in frontmatter) | Kit step: author and evaluate every twin skill. All roles | **Adopt.** It is Anthropic's own eval loop, and it matches our "evaluate before you write" rule ([03](03-skills-authoring.md)) |
| [template](https://github.com/anthropics/skills/tree/main/template) (`template-skill`) | A bare `SKILL.md` with `name` and `description` frontmatter and a placeholder body | No licence file in the folder. **⚠ Unverified:** licence not stated | Kit step: starting point for hand-written skills | **Adopt.** Tiny, and shows the minimum format. Use it as the seed of our own skill template |
| [docx](https://github.com/anthropics/skills/tree/main/skills/docx) | Creates, reads and edits Word documents and templates | Apache 2.0 | Ops/finance and CS twins that produce reports, letters, QBR documents | **Adopt** in Claude Code and the API (the app has its own, see section 3). Test first, per the README disclaimer |
| [xlsx](https://github.com/anthropics/skills/tree/main/skills/xlsx) | Opens, edits and creates spreadsheets; handles .csv/.tsv; formulas and charts | Apache 2.0 | Sales (pipeline and forecast extracts), ops/finance (reconciliations, variance) | **Adopt**, same caveat as docx |
| [pptx](https://github.com/anthropics/skills/tree/main/skills/pptx) | Creates and edits slide decks, templates, speaker notes | Apache 2.0 | Sales (account plans, QBR decks), private-equity IC material | **Adapt.** Decks need the customer's template and brand; layer a brand skill on top |
| [pdf](https://github.com/anthropics/skills/tree/main/skills/pdf) | Reads, merges, splits, fills and creates PDFs | Apache 2.0 | Ops/finance (statements, forms), private-equity (data-room documents) | **Adopt**, same caveat |
| [mcp-builder](https://github.com/anthropics/skills/tree/main/skills/mcp-builder) | Guide for building MCP servers in Python (FastMCP) or Node/TypeScript | Apache 2.0 | Kit step: building a connector where the directory has none ([11](11-connectors.md)) | **Adopt** for custom connector work; not part of what a twin user runs |
| [doc-coauthoring](https://github.com/anthropics/skills/tree/main/skills/doc-coauthoring) | Structured workflow for co-writing specs, proposals and decision docs | **⚠ Unverified:** no `LICENSE.txt` in the folder and no `license:` field | Ops and CS twins writing proposals and runbooks; kit pages | **Adapt.** Fine as a pattern; confirm the licence before copying text |
| [internal-comms](https://github.com/anthropics/skills/tree/main/skills/internal-comms) | Templates for status reports, leadership updates, newsletters, FAQs | Apache 2.0 | Ops twin (weekly status, updates) | **Adapt.** The formats are generic; replace with the customer's own |
| [brand-guidelines](https://github.com/anthropics/skills/tree/main/skills/brand-guidelines) | Applies Anthropic's own brand colours and typography | Apache 2.0 | None (it encodes Anthropic's brand, not the customer's) | **Skip** as shipped. Use as a pattern for a customer brand skill |
| [theme-factory](https://github.com/anthropics/skills/tree/main/skills/theme-factory) | Applies one of 10 preset themes, or a generated one, to slides, docs and pages | Apache 2.0 | Any twin that outputs decks or pages | **Skip** by default; a customer brand skill is better |
| [claude-api](https://github.com/anthropics/skills/tree/main/skills/claude-api) | Reference for the Claude API and SDKs (models, tool use, caching, agents) | Apache 2.0 | Kit step: building hosted agents ([05](05-decision-matrix.md)) | **Adopt** for hosted-agent builds. It already ships bundled in Claude Code ([Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)) |
| [frontend-design](https://github.com/anthropics/skills/tree/main/skills/frontend-design) | Guidance for distinctive UI design | Apache 2.0 | None in the pilots | **Skip** |
| [web-artifacts-builder](https://github.com/anthropics/skills/tree/main/skills/web-artifacts-builder) | Builds multi-component claude.ai HTML artifacts (React, Tailwind, shadcn/ui) | Apache 2.0 | None in the pilots | **Skip** |
| [webapp-testing](https://github.com/anthropics/skills/tree/main/skills/webapp-testing) | Tests local web apps with Playwright | Apache 2.0 | None in the pilots | **Skip** |
| [algorithmic-art](https://github.com/anthropics/skills/tree/main/skills/algorithmic-art) | Generative art with p5.js | Apache 2.0 | None | **Skip** |
| [canvas-design](https://github.com/anthropics/skills/tree/main/skills/canvas-design) | Posters and static designs as .png/.pdf | Apache 2.0 | None | **Skip** |
| [slack-gif-creator](https://github.com/anthropics/skills/tree/main/skills/slack-gif-creator) | Animated GIFs sized for Slack | Apache 2.0 | None | **Skip** |
| [academy-guide](https://github.com/anthropics/skills/tree/main/skills/academy-guide) | Points users to matching Claude Academy courses and tutorials when they ask how to use Claude | Apache 2.0 | Rollout and enablement: could help adoption | **Adapt.** Its description is broad and fires on many "how do I" questions; test it for noise before rolling it out |
| [discernment-nudge](https://github.com/anthropics/skills/tree/main/skills/discernment-nudge) | After a substantive answer, appends two or three follow-up questions to help the user check facts and reasoning | Apache 2.0 | Possibly the approval-heavy roles (private equity, finance), where the reader should check the twin's work | **Adapt.** Try it in the PE pilot; it adds length to every answer, so measure it |

Sources: [anthropics/skills](https://github.com/anthropics/skills), each folder linked above, the repo's [marketplace.json](https://github.com/anthropics/skills/blob/main/.claude-plugin/marketplace.json), [spec folder](https://github.com/anthropics/skills/tree/main/spec).

**How the repo is packaged.** `marketplace.json` defines five plugins: `document-skills` (xlsx, docx, pptx, pdf), `example-skills` (12 skills including skill-creator and mcp-builder), `claude-api`, `academy-guide` and `discernment-nudge`. The template is not in any plugin; copy it by hand.

## 2. Anthropic plugin marketplaces and plugins

A plugin bundles skills, commands, agents, hooks and MCP connections. Anthropic publishes several marketplaces. In Claude Code, "official" is added automatically the first time you start an interactive terminal session ([Anthropic's marketplaces](https://code.claude.com/docs/en/plugins/anthropic-marketplaces)). Every other marketplace is added with `/plugin marketplace add <owner>/<repo>` (shell form: `claude plugin marketplace add <owner>/<repo>`).

| Marketplace or plugin | What it holds | Install command or source | Verdict |
|---|---|---|---|
| **Official** (`claude-plugins-official`) | Plugins Anthropic maintains plus partner and other-author plugins. Anthropic's own include `commit-commands`, `code-review`, `feature-dev` and language-server plugins. The repo's `plugins/` folder also lists `skill-creator`, `plugin-dev`, `mcp-server-dev`, `hookify`, `security-guidance`, `claude-md-management` and output-style plugins (`explanatory-output-style`, `learning-output-style`) | `/plugin install <name>@claude-plugins-official`. Source: https://github.com/anthropics/claude-plugins-official (Apache-2.0 per GitHub). Docs: [Install plugins](https://code.claude.com/docs/en/plugins/install) | **Adopt**, selectively: `skill-creator` and `plugin-dev` for the authoring team. **⚠ Unverified:** we did not read each plugin's contents; review before pinning. Most of the catalog is third-party, and Anthropic says to trust a plugin before installing it ([README](https://github.com/anthropics/claude-plugins-official)) |
| **Community** (`claude-community`) | Third-party plugins their authors submitted to Anthropic | `/plugin marketplace add anthropics/claude-plugins-community`, then `/plugin install <name>@claude-community`. Source: https://github.com/anthropics/claude-plugins-community | **Skip** by default. Case-by-case only, after our own review |
| **Agent skills marketplace** (`anthropic-agent-skills`) | The five plugins from section 1 | `/plugin marketplace add anthropics/skills`, then `/plugin install document-skills@anthropic-agent-skills` or `/plugin install example-skills@anthropic-agent-skills` ([README](https://github.com/anthropics/skills)) | **Adapt.** Fine for dev machines; for twins, pick individual skills into our own repo ([04](04-distribution-governance.md)) |
| **Knowledge-work plugins** (`knowledge-work-plugins`) | Role plugins for Cowork, also usable in Claude Code. Folders include `sales`, `customer-support`, `operations`, `finance`, `legal`, `data`, `productivity`, `enterprise-search`, `human-resources`, `marketing`, `product-management`, `engineering`, `design`, `small-business`, `bio-research`, `cowork-plugin-management`. Each bundles skills, commands and `.mcp.json` connector config. The marketplace also lists partner-built plugins (for example `zoominfo`, `box`, `figma`) | `claude plugin marketplace add anthropics/knowledge-work-plugins`, then `claude plugin install sales@knowledge-work-plugins`. Source: https://github.com/anthropics/knowledge-work-plugins (Apache-2.0 per GitHub). Also installable from Cowork at [claude.com/plugins](https://claude.com/plugins) | **Adapt.** These are role templates, which is our shape. The README itself calls them "generic starting points" to customise. Closest to the pilots: `sales`, `customer-support`, `operations`, `finance`. ⚠ The README says "11 plugins", but the repo has more folders, so its text is out of date. Claude Code does not auto-update this marketplace by default ([Install plugins](https://code.claude.com/docs/en/plugins/install)) |
| **Claude for Financial Services** (`claude-for-financial-services`; repo `anthropics/financial-services`, formerly `financial-services-plugins`) | Reference agents, vertical plugins and data connectors for investment banking, equity research, private equity and wealth management. Vertical plugins: `financial-analysis` (core, holds all connectors), `investment-banking`, `equity-research`, `private-equity`, `fund-admin`, `operations`. The `private-equity` plugin has skills for deal sourcing, deal screening, DD checklists, IC memos, portfolio monitoring, returns analysis and value-creation plans. Agents include `gl-reconciler`, `month-end-closer`, `valuation-reviewer` and `kyc-screener`. Each agent is also a Managed Agent template under `managed-agent-cookbooks/` | `claude plugin marketplace add anthropics/financial-services`, then `claude plugin install financial-analysis@claude-for-financial-services` (install first) and `claude plugin install private-equity@claude-for-financial-services`. Source: https://github.com/anthropics/financial-services (Apache-2.0 per GitHub) | **Adapt.** Directly relevant to the private-equity use case ([14](14-private-equity.md)). Its README says outputs are drafts "staged for human sign-off", which fits our low-autonomy default ([06](06-autonomy.md)). Subagent delegation in the Managed Agent templates is a "Research Preview" per the README. Check connector data flows against [10](10-sensitive-data.md) and [11](11-connectors.md) before use |
| **Claude for Financial Advisors** and **Claude for Legal** | Plugin suites for advisor and legal workflows. Advisors: https://github.com/anthropics/claude-for-financial-advisors. Legal: https://github.com/anthropics/claude-for-legal (both Apache-2.0 per GitHub) | See each repo's README. **⚠ Unverified:** install commands not checked | **Skip** for the pilots (not our roles). Revisit if a customer asks |
| **Claude Marketplace and directory** (claude.ai side) | The catalog served on claude.ai, with "Anthropic verified" marks on some plugins. A plugin added from the directory reaches Claude Code through account sync | Browse https://claude.com/marketplace/plugins. Admin side: [Plugins admin](https://claude.com/docs/plugins/admin), [Org rollout](https://claude.com/docs/plugins/org-rollout) | **Adopt** as the path for org-wide distribution on Team and Enterprise ([04](04-distribution-governance.md)). "Verified" is a mark, not a security audit ([11](11-connectors.md)) |
| **`claude-code-plugins`** (in `anthropics/claude-code`) | Older marketplace | Deprecated; Anthropic says to install from `claude-plugins-official` instead ([Anthropic's marketplaces](https://code.claude.com/docs/en/plugins/anthropic-marketplaces)) | **Skip** |

**Our own marketplace.** Anthropic's docs describe how to run your own marketplace alongside theirs and how an organisation restricts which marketplaces users may add ([Manage plugins for your organization](https://code.claude.com/docs/en/plugins/org)). (Our recommendation) The kit publishes one customer marketplace, containing only plugins we have reviewed, and blocks the rest through managed settings ([13](13-devices.md)).

## 3. Skills built into the Claude apps

What a twin user gets in claude.ai and Claude Desktop without installing anything:

| What | Detail | Plans | Source |
|---|---|---|---|
| **Excel, Word, PowerPoint and PDF skills** | Anthropic-created skills "that improve document creation" for those four file types. Claude uses them automatically when relevant. Output types: .xlsx, .pptx, .docx and PDF, up to 30MB | Skills: "Free, Pro, Max, Ultra, Team, and Enterprise" | [What are skills](https://support.claude.com/en/articles/12512176-what-are-skills), [Create and edit files](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude) |
| **Setting they need** | "Code execution and file creation" (called "Create and edit files" in the newer layout). Individual plans: Settings > Capabilities. Team and Enterprise: set by org Owners | Team: on by default. Enterprise: see the conflict below | [Using skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude) |
| **Skills directory** | Customize > Skills > "+" > Browse skills. **⚠ Unverified:** we did not open the directory, so we can't list what is in it | Same | [What are skills](https://support.claude.com/en/articles/12512176-what-are-skills) |
| **Custom skills** (ours) | Uploaded as zip files. The API docs say Pro, Max, Ultra, Team and Enterprise with code execution on | See conflict below | [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) |
| **Same four skills in the API** | Skill IDs `pptx`, `xlsx`, `docx`, `pdf`, used with the code execution tool | API | [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) |
| **Claude Code** | Signed in to claude.ai (v2.1.273 or later), Claude Code downloads the account's skills, built-ins included, into `~/.claude/skills/synced/`; `pdf` and `xlsx` always sync. **⚠ Conflict:** the API overview says the document skills aren't in Claude Code; we follow the newer Claude Code docs and test each setup. Without a claude.ai sign-in, or with `syncClaudeAiSkills: false`, none sync. Claude Code also ships its own bundled skills, for example `/code-review`, `/simplify`, `/loop`, `/batch`, `/debug`, `/doctor`, `/claude-api`, `/run` and `/verify`. Turn them off with `disableBundledSkills` | Any Claude Code plan | [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview), [Claude Code skills](https://code.claude.com/docs/en/skills) |

**⚠ Conflict:** plan wording. The "What are skills" article says skills are available on Free, Pro, Max, Ultra, Team and Enterprise. The API overview says custom skill upload is for Pro and above. We take the narrower one: assume custom skills need Pro or above, and a Team or Enterprise org for anything company-wide ([09](09-plans-and-it-controls.md)).

**⚠ Conflict:** Enterprise default. "Create and edit files" says code execution and file creation "is enabled by default for new Enterprise plan organizations", while "Using skills in Claude" says Enterprise Owners "must enable both code execution and skills". We take the safer reading: check the setting in each Enterprise org, and don't assume it is on.

**Not covered by ZDR or HIPAA.** The API overview lists Agent Skills as "Not eligible" for zero data retention and HIPAA ([Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)). This applies to the built-in document skills when used through the API. **⚠ Unverified:** whether the same holds for the claude.ai built-ins; page [10](10-sensitive-data.md) governs until confirmed.

**Cross-surface rule.** claude.ai and a signed-in Claude Code share skills: Claude Code downloads the account's personal, org-provided and built-in skills ([Claude Code skills](https://code.claude.com/docs/en/skills.md)). The API keeps its own separate set. **⚠ Conflict:** the [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) still says custom skills "do not sync across surfaces"; [04](04-distribution-governance.md) explains why we take the newer Claude Code docs. So for a twin, the built-ins are a free baseline in claude.ai and a signed-in Claude Code, and our own skills need one publishing step for claude.ai (which reaches Claude Code) and another for the API.

## 4. Reference index of Anthropic best-practice docs

Every URL below returned HTTP 200 when opened on 2026-11-14. Entries marked **(read)** were also read, not just opened. Some links redirect to a new address that also loads: the `anthropic.com/engineering/...` posts now resolve under `anthropic.com/research/...`, the skill-creator blog post under `claude.com/resources/articles/...`, and the old "system prompts" prompt-engineering page to a section of the prompting best-practices page. We list the original URLs, which still resolve.

### Agent Skills: overview and best practices

| URL | What it is for |
|---|---|
| https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview (read) | How skills load (metadata, instructions, resources), where they work, field limits, security, ZDR status |
| https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices | Anthropic's authoring guidance, applies across surfaces |
| https://platform.claude.com/docs/en/agents-and-tools/agent-skills/enterprise | Governance, vetting and rollout of skills in an organisation |
| https://platform.claude.com/docs/en/agents-and-tools/agent-skills/quickstart | First use of the pre-built document skills in the API |
| https://platform.claude.com/docs/en/build-with-claude/skills-guide | Skills API: upload and manage custom skills |
| https://platform.claude.com/docs/en/agents-and-tools/agent-skills/claude-api-skill | The open-source Claude API skill bundled with Claude Code |
| https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills | The design rationale for skills |
| https://support.claude.com/en/articles/12512176-what-are-skills (read) | Plain-language intro to skills, plans, admin controls |
| https://support.claude.com/en/articles/12512180-using-skills-in-claude (read) | Turning skills on in claude.ai, the code execution requirement |

### Skill authoring

| URL | What it is for |
|---|---|
| https://code.claude.com/docs/en/skills (read) | Claude Code skills: locations, frontmatter fields, bundled skills, troubleshooting |
| https://support.claude.com/en/articles/12512198-how-to-create-custom-skills | Creating a custom skill for claude.ai |
| https://github.com/anthropics/skills (read) | Example skills, the spec folder and the template |
| https://github.com/anthropics/skills/tree/main/template | The minimal skill to copy |
| https://github.com/anthropics/skills/tree/main/skills/skill-creator | Source of the skill-creator skill |
| https://agentskills.io | The open Agent Skills standard. ⚠ Not on our primary-source list; Anthropic's README and docs link to it, so we list it as the spec home |

### Evals

| URL | What it is for |
|---|---|
| https://code.claude.com/docs/en/plugin-evals (read) | `claude plugin eval`: write cases and graders, compare with no plugin, gate CI |
| https://code.claude.com/docs/en/skills (section "Run evals with skill-creator") (read) | Per-skill evals: test cases, isolated runs, grading, benchmark, blind A/B, description tuning |
| https://platform.claude.com/docs/en/test-and-evaluate/develop-tests | Defining success criteria and building test cases for any Claude feature |
| https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents | How to think about evals for agents |
| https://claude.com/blog/improving-skill-creator-test-measure-and-refine-agent-skills | Announcement of skill-creator's test and benchmark modes |
| https://agentskills.io/skill-creation/evaluating-skills | The eval file format named in Claude Code's docs. ⚠ Same note as agentskills.io above |

### Plugins and marketplaces

| URL | What it is for |
|---|---|
| https://code.claude.com/docs/en/plugins/overview | What a plugin is |
| https://code.claude.com/docs/en/plugins/create | Building a plugin |
| https://code.claude.com/docs/en/discover-plugins (read) | Installing plugins, install scopes, adding marketplaces, auto-update |
| https://code.claude.com/docs/en/plugins/install | Same topic, install-focused page |
| https://code.claude.com/docs/en/plugins/anthropic-marketplaces (read) | Official vs community marketplaces and their names |
| https://code.claude.com/docs/en/plugin-marketplaces | Creating and running a marketplace |
| https://code.claude.com/docs/en/plugins/publish | Publishing, and submitting to Anthropic's directory |
| https://code.claude.com/docs/en/plugins/loading | Why a plugin loaded or didn't; claude.ai plugin sync |
| https://claude.com/docs/plugins/overview | Plugins on claude.ai and in Cowork |
| https://claude.com/plugins | Claude Marketplace catalog on the web |

### Plugin reference

| URL | What it is for |
|---|---|
| https://code.claude.com/docs/en/plugins-reference | Full plugin reference |
| https://code.claude.com/docs/en/plugins/manifest-reference | `plugin.json` fields |
| https://code.claude.com/docs/en/plugins/marketplace-reference | `marketplace.json` fields and plugin source types |
| https://code.claude.com/docs/en/plugins/cli-reference | `claude plugin` commands, including `validate` |

### Hooks

| URL | What it is for |
|---|---|
| https://code.claude.com/docs/en/hooks | Hook events, inputs and outputs. The skills page says to move "a rule that must hold every time" into a hook |
| https://code.claude.com/docs/en/hooks-guide | Worked examples of hooks. Basis for our governance-log hook ([15](15-governance-and-performance.md)) |

### Output styles

| URL | What it is for |
|---|---|
| https://code.claude.com/docs/en/output-styles | How to change Claude Code's response style |

### Managed settings and permissions

| URL | What it is for |
|---|---|
| https://code.claude.com/docs/en/managed-settings | Organisation-wide settings deployed to machines |
| https://code.claude.com/docs/en/server-managed-settings | Settings delivered from the server, without MDM |
| https://code.claude.com/docs/en/settings | Settings files and scopes |
| https://code.claude.com/docs/en/permissions | Permission rules, including who may use which tool or skill |
| https://code.claude.com/docs/en/plugins/org | Pre-installing and restricting plugins for an organisation |

### MCP

| URL | What it is for |
|---|---|
| https://code.claude.com/docs/en/mcp | Connecting Claude Code to MCP servers |
| https://code.claude.com/docs/en/managed-mcp | Controlling which MCP servers an organisation allows |
| https://platform.claude.com/docs/en/agents-and-tools/mcp-connector | MCP connector in the Messages API |
| https://claude.com/docs/connectors/directory | The connector directory ([11](11-connectors.md)) |

### Claude Code security

| URL | What it is for |
|---|---|
| https://code.claude.com/docs/en/security | Security model and safeguards |
| https://code.claude.com/docs/en/sandboxing | Sandboxed command execution |
| https://code.claude.com/docs/en/plugins/security | What a plugin can do, and how to review one before installing |

### Org skills administration on claude.ai

| URL | What it is for |
|---|---|
| https://support.claude.com/en/articles/13119606-provision-and-manage-skills-for-your-organization | Owners provisioning skills to all users |
| https://claude.com/docs/plugins/admin | Admin controls for plugins |
| https://claude.com/docs/plugins/org-rollout | Rolling plugins out across an org |
| https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude (read) | The org-level code execution and file creation toggle |

### Prompt engineering and system prompts

| URL | What it is for |
|---|---|
| https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview | Prompt engineering entry point |
| https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices | Current prompting guidance, including role and system-prompt advice (the old "system prompts" URL redirects to its role section) |
| https://platform.claude.com/docs/en/release-notes/system-prompts/overview (read) | The published claude.ai and mobile system prompts. They "do not apply to the Claude API" |
| https://www.anthropic.com/engineering/building-effective-agents | When to use simple patterns vs agents |
| https://www.anthropic.com/engineering/writing-tools-for-agents | How to design tools for agents |

## What the starter kit takes from this

1. **Scaffold and evaluate every skill with skill-creator.** Install it from the official marketplace or copy it from `anthropics/skills`. Run its with-skill vs without-skill benchmark and description tuning before any skill ships. Use `claude plugin eval` to gate changes in CI once a role is packaged as a plugin.
2. **Seed the skill template from Anthropic's `template-skill`.** Keep the frontmatter to `name` and `description`, the format that works on every surface ([03](03-skills-authoring.md)).
3. **Start each pilot role from the matching Anthropic role plugin, then customise it.** Sales, customer success and operations/finance start from `sales`, `customer-support` and `operations`/`finance` in `knowledge-work-plugins`. The private-equity role starts from `financial-analysis` plus `private-equity` in `anthropics/financial-services`. Review each plugin's skills and connectors before use; never ship one unchanged.
4. **Don't rebuild the document skills.** Rely on the built-in Excel, Word, PowerPoint and PDF skills in claude.ai, and in Claude Code signed in to claude.ai, which receives them by sync (test which ones arrive; `pdf` and `xlsx` always do). Copy the skills from `anthropics/skills`, after testing them, only for the API and for Claude Code that isn't signed in to claude.ai or has sync turned off. Put the customer's brand and templates in our own skill on top.
5. **Run one reviewed customer marketplace.** Publish only reviewed plugins to it, and restrict other marketplaces through managed settings. Skip the community marketplace by default.
6. **Treat section 4 as the only link list.** Kit pages link to these URLs rather than to blog posts or memory. Re-check them on a schedule, because the docs moved sites during this research.
