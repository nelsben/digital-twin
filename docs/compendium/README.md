# Digital twin compendium

**Status:** the facts here are grounded in Anthropic's docs as fetched on 2026-11-14. The [starter kit](../../starter-kit/README.md) and the [sample engagement](../../engagements/sample-pe/README.md) are built on top of this compendium. Every page links its sources; [sources.md](sources.md) has the full list.

**How to use it:** we deliver twins to customers as Anthropic partners. This compendium is our knowledge base. Engagement method (discovery, stakeholders, stories) is in the [partner playbook](../playbook/README.md). Anything marked "Decided" is our **default stance**, to be confirmed with each customer in discovery.

## What we mean by a digital twin

A digital twin is a companion agent for a role. It knows how that role works, has the access the role needs, and takes on the role's repetitive work. We are building **role templates**: one twin per role (for example, every account executive gets the same sales twin), not one twin per person.

In Claude terms, a twin is not one thing. It is a package of parts: a persona, skills, connectors, a runtime, an identity, memory and guardrails. Each part has its own Anthropic mechanism and its own decision. [01-anatomy.md](01-anatomy.md) breaks this down, and the rest of the compendium takes the parts one at a time.

## Reading order

| Page | What it answers |
|---|---|
| [01-anatomy.md](01-anatomy.md) | What a twin is made of, and the engineering principles behind it |
| [02-persona.md](02-persona.md) | How to define the role, tone and boundaries, and where memory fits |
| [03-skills-authoring.md](03-skills-authoring.md) | How to write a skill that triggers reliably and works |
| [04-distribution-governance.md](04-distribution-governance.md) | How skills reach people on each Claude surface, and how to control them |
| [05-decision-matrix.md](05-decision-matrix.md) | Hosted agent or client skill: the criteria, and a decision flow |
| [06-autonomy.md](06-autonomy.md) | How much a twin may do on its own: a graded ladder with controls |
| [07-pilot-roles.md](07-pilot-roles.md) | What this looks like for sales, customer success and operations/finance |
| [08-open-questions.md](08-open-questions.md) | Decisions we still need to make, and questions you might not know to ask |
| [09-plans-and-it-controls.md](09-plans-and-it-controls.md) | Features on every plan (individual, Team, Enterprise), and what IT can control on each |
| [10-sensitive-data.md](10-sensitive-data.md) | What leaves the machine; ZDR and HIPAA; a decision matrix by data class |
| [11-connectors.md](11-connectors.md) | Connectors for our systems; whether to use, buy, build or host |
| [12-orgs-and-ownership.md](12-orgs-and-ownership.md) | How many Claude orgs to ask for, who owns each, and questions for Anthropic |
| [13-devices.md](13-devices.md) | Managed (MDM) and unmanaged devices: what can be enforced, and the policy for each |
| [14-private-equity.md](14-private-equity.md) | The primary use case: designing for information barriers and for none |
| [15-governance-and-performance.md](15-governance-and-performance.md) | Audit sources, our own governance log, scorecards, and who reviews what, how often |
| [16-oob-skills-and-references.md](16-oob-skills-and-references.md) | Anthropic's ready-made skills and plugins, adopt/adapt/skip for each, and an index of best-practice docs |
| [17-anthropic-pe-plugins-review.md](17-anthropic-pe-plugins-review.md) | Every skill and connector in Anthropic's `private-equity` and `financial-analysis` plugins: where the data goes, adopt/adapt/skip for each, and how to pin a reviewed copy (OD-1) |
| [sources.md](sources.md) | Every source, with its URL |

## The ten things to know first

1. **Identity matters more than infrastructure.** Each way of running Claude acts as a different principal: the employee, a shared service account, or your API key. That choice decides permissions, the audit trail, and what happens when someone leaves. ([05](05-decision-matrix.md))
2. **Skills are know-how; connectors are access.** A skill teaches Claude *how* to do a task. An MCP connector gives it the *tools and data* to do it. A twin usually needs both. ([03](03-skills-authoring.md))
3. **Skills don't sync across every surface.** Claude.ai and a signed-in Claude Code share skills. The API keeps its own separate set. One Git repo should be the source of truth, with a publishing step for each surface. ([04](04-distribution-governance.md))
4. **Write skills to the smallest common format.** Claude.ai and the API reject frontmatter keys that only Claude Code understands. Keep descriptions under 200 characters until a conflict in the docs is resolved. ([03](03-skills-authoring.md))
5. **The skill's description decides whether it ever runs.** Claude chooses skills by matching the request to each description. A vague description means a skill that never fires. ([03](03-skills-authoring.md))
6. **Evaluate before you write, not after.** Anthropic's method: run the task without a skill, write down where it fails, build at least three test cases, then write the minimum that fixes the failures. ([03](03-skills-authoring.md))
7. **Start client-side, at low autonomy.** Anthropic's guidance is to use the simplest thing that works. For the pilots, that means a role plugin that people use inside Claude, which drafts and recommends while a person acts. Add hosted jobs only where a trigger or schedule really needs one. ([05](05-decision-matrix.md), [06](06-autonomy.md))
8. **A persona is an instruction, not a guarantee.** Put real limits in permissions and approval settings, not in the prompt. ([02](02-persona.md), [06](06-autonomy.md))
9. **Compliance limits rule out some options.** Skills and Managed Agents aren't eligible for zero data retention (ZDR) or HIPAA coverage. Regulated data pushes you toward running agents on your own infrastructure. ([04](04-distribution-governance.md), [05](05-decision-matrix.md))
10. **Many controls depend on plan and role.** Group targeting, security scanning and usage analytics are Enterprise-only. Only an Owner (not an Admin) can manage org skills. ([04](04-distribution-governance.md))

### Added after the second round of research

11. **Running locally doesn't keep data local.** The model runs at Anthropic, so anything the agent reads is sent. Data is protected by the contract (ZDR, a BAA) and by minimization, not by where the program runs. ([10](10-sensitive-data.md))
12. **Individual plans are outside IT's reach,** and their terms allow training on your data by default. Team should be the minimum for company data. ([09](09-plans-and-it-controls.md))
13. **Each data class gets its own org.** HIPAA is permanent once turned on, and ZDR, CMEK and Claude Tag constrain each other. ([10](10-sensitive-data.md))
14. **Connectors aren't covered for PHI,** and "Verified" in the directory isn't a security audit. ([11](11-connectors.md))

## Conventions

- **⚠ Conflict:** Anthropic's own pages disagree. We note both values and take the safer one.
- **⚠ Unverified:** the research didn't confirm this, or it depends on plan or beta status.
- **(Our recommendation):** our judgment, not Anthropic's wording.
