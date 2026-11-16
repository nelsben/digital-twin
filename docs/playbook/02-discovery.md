# 02 — Discovery questionnaire

Run this with every customer. Each answer feeds a design decision, and the link shows where the options are explained. Mark anything unanswered as **open**, with an owner and a date.

## A. Sponsor and scope
| # | Question | Why it matters | See |
|---|---|---|---|
| A1 | Who sponsors this, and what outcome do they want in 6 months? | It sets the scorecard targets | [15](../compendium/15-governance-and-performance.md) |
| A2 | Which roles are first? Is private equity in scope? | It decides the first epic, and whether we need ZDR | [14](../compendium/14-private-equity.md) |
| A3 | How many people are in each role, and how many will pilot? | Seat counts and pilot size | [12](../compendium/12-orgs-and-ownership.md) |

## B. Claude plans and licensing
| # | Question | Why it matters | See |
|---|---|---|---|
| B1 | Which Claude plans exist today: individual, Team, Enterprise, API? How many of each? | Individual plans are outside IT's control and use consumer terms | [09](../compendium/09-plans-and-it-controls.md) |
| B2 | Are people buying individual licenses on the company domain? | Plan a migration; domain capture is a one-way step | [09](../compendium/09-plans-and-it-controls.md) |
| B3 | Who holds the Owner and Primary Owner roles today? | Only Owners can manage skills and plugins | [04](../compendium/04-distribution-governance.md) |

## C. Data classes and compliance
| # | Question | Why it matters | See |
|---|---|---|---|
| C1 | Which data classes will each role touch: internal, confidential, highly sensitive, PHI? | It decides the orgs, surfaces and controls | [10](../compendium/10-sensitive-data.md) |
| C2 | Does any role handle PHI? Is there a BAA? | HIPAA is permanent per org, and many features are excluded | [10](../compendium/10-sensitive-data.md) |
| C3 | What retention does compliance require? Will they accept the ZDR exceptions (flagged content kept up to 2 years, feedback 5 years)? | The retention settings, and whether feedback is turned off | [10](../compendium/10-sensitive-data.md) |
| C4 | Are information barriers required? Soft (enforced by source-system permissions) or hard (provable separation)? | It decides the wall design and the org count | [14](../compendium/14-private-equity.md) |
| C5 | Is there MNPI? | Web tools off; ZDR surfaces only | [14](../compendium/14-private-equity.md) |

## D. Identity and devices
| # | Question | Why it matters | See |
|---|---|---|---|
| D1 | Which identity provider is used (Okta, Entra, Google Workspace)? Are SSO and SCIM available? | Group targeting, provisioning, device checks. SCIM and group targeting depend on the plan | [09](../compendium/09-plans-and-it-controls.md) |
| D2 | Do they use MDM? What share of users are on managed devices, and what share on unmanaged? | The strongest controls need MDM; unmanaged devices need a hosted twin for sensitive data | [13](../compendium/13-devices.md) |
| D3 | Are there contractors or other external users? | Device and identity policy | [13](../compendium/13-devices.md) |

## E. Systems and connectors
| # | Question | Why it matters | See |
|---|---|---|---|
| E1 | Which CRM: Salesforce (which edition?) or HubSpot (which tier?)? | Salesforce Hosted MCP may need Enterprise Edition and an External Client App | [11](../compendium/11-connectors.md) |
| E2 | Where do documents live: SharePoint, OneDrive, Google Drive (shared drives?)? | Which connector, and whether shared drives are supported | [11](../compendium/11-connectors.md) |
| E3 | Which messaging tools: Slack, Teams? | Connectors; whether Claude Tag is possible | [11](../compendium/11-connectors.md) |
| E4 | How is access controlled in each system (roles, sharing rules, teams)? | Soft walls depend on it | [14](../compendium/14-private-equity.md) |
| E5 | Are any systems on a private network only? | MCP tunnels, or running inside the network | [11](../compendium/11-connectors.md) |
| E6 | Can the customer allowlist Anthropic's IP range (`160.79.104.0/21`)? | Needed for remote connectors | [11](../compendium/11-connectors.md) |

## F. Roles and tasks (run per role, in interviews)

The per-role questions are run with the [interview guide](../../partner-kit/plugins/twin-consultant/templates/interview-guide.md). Its question ids are the ones the persona card cites, and F1 to F5 here are the summary.

| # | Question | Why it matters |
|---|---|---|
| F1 | Which tasks take most of your week? How often, and how long each? | Choosing tasks; the value baseline |
| F2 | For each task: which inputs and systems, what output, and who sees it? | Connectors, data class, autonomy |
| F3 | What does good look like? Please share 2–3 real examples, good and bad. | These become the evals |
| F4 | What happens if it goes wrong? | Autonomy ceiling ([06](../compendium/06-autonomy.md)) |
| F5 | Does the task run on a schedule or when something happens, or does a person start it? | Hosted or client ([05](../compendium/05-decision-matrix.md)) |

## G. Governance, logging and spend
| # | Question | Why it matters | See |
|---|---|---|---|
| G1 | Which security log system, data warehouse or observability tool do they run? Does security or compliance require a log of every action the twin takes? | Where the governance log goes. The answer decides whether a plan without audit logs fits | [15](../compendium/15-governance-and-performance.md), [09](../compendium/09-plans-and-it-controls.md) |
| G2 | What do they already log in Salesforce (Event Monitoring, Field Audit Trail)? Do they use Claude through any Salesforce integration? | Source-system audit; existing Salesforce–Anthropic logging | [15](../compendium/15-governance-and-performance.md) |
| G3 | Who owns tooling and spend? What is the budget, and what spend limits are wanted? | Spend controls, per-user limits, alerts | [15](../compendium/15-governance-and-performance.md) |
| G4 | Who is the technical owner, the business owner and the backup Owner? | Ownership of each org | [03](03-stakeholders.md) |
