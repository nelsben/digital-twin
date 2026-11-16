# 01 — Engagement model

Six phases. Each one ends with a customer sign-off, so nothing moves forward on assumptions.

| Phase | Goal | We deliver | Customer signs off | Exit when |
|---|---|---|---|---|
| **0. Qualify** | Confirm fit and a sponsor | Fit notes: plan tier, data classes, systems, sponsor, recorded as the start of the [customer profile](../../partner-kit/plugins/twin-consultant/templates/customer-profile.json) | Sponsor agrees to discovery | A sponsor is named and the first role is chosen |
| **1. Discovery** | Understand the roles, data, systems and constraints | Completed [discovery questionnaire](02-discovery.md); role interviews (2–3 people per role); [stakeholder map](03-stakeholders.md); candidate tasks, with time spent and cost of a mistake; one [persona card](05-persona-card-workflow.md) per role, filled from the interview notes | Discovery summary | Every question in the questionnaire is answered or marked open, with an owner |
| **2. Design** | Decide the architecture and the backlog | Org plan ([compendium 12](../compendium/12-orgs-and-ownership.md)); data-class and device policy ([10](../compendium/10-sensitive-data.md), [13](../compendium/13-devices.md)); connector plan ([11](../compendium/11-connectors.md)); wall design ([14](../compendium/14-private-equity.md)); governance-log design ([15](../compendium/15-governance-and-performance.md)); **story backlog** ([04](04-stories.md)); per persona, the levelled plan, the generated backlog and the dashboard | Design document and the prioritized backlog | Technical and business owners approve |
| **3. Build** | Make the first role twin | Evals first, then skills; role and shared plugins; connectors; managed settings; the governance-log hook; persona | Each story's acceptance criteria (its evals) | Stories for the pilot scope are done, with evals passing |
| **4. Pilot** | Prove it with real users | 5–10 users per role at autonomy level 1 ([06](../compendium/06-autonomy.md)); training; a monthly scorecard ([15](../compendium/15-governance-and-performance.md)) | Pilot scorecard | Scorecard targets met, or the backlog is reworked |
| **5. Scale** | Roll out wider and raise autonomy | Rollout to groups; autonomy promotions backed by evidence; the next roles; hosted jobs where a schedule or event really helps | Each promotion and each new role | Agreed by the business owner |
| **6. Run / hand over** | The customer operates it | Runbooks; the review schedule ([15](../compendium/15-governance-and-performance.md)); skill-owner training; optionally, an ongoing support arrangement with us | Handover acceptance | Customer owners run the cadence without us |

The [persona-card workflow](05-persona-card-workflow.md) ties its steps to these phases.

## Principles for every engagement

1. **Start with one role,** private equity first where it applies, then grow. A shared plugin for common skills keeps each later role small.
2. **Write the evals before the skill.** A story's acceptance criteria are its evals ([compendium 03](../compendium/03-skills-authoring.md)).
3. **Start at autonomy level 1, the draft stage.** Every promotion needs scorecard evidence.
4. **The customer owns its data and its log.** We design what the log records. The customer chooses where it goes.
5. **Write everything down in a way that works across orgs.** Use one repo for skills, persona, evals and settings, so a new org or a new wall is a copy, not a rebuild ([compendium 14](../compendium/14-private-equity.md)).
