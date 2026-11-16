# Discovery: Example Capital Partners

> **Fictional customer.** Example Capital Partners and every name, person and figure on this page are invented. This is the worked example for the [discovery questionnaire](../../docs/playbook/02-discovery.md). Copy the structure for a real customer, not the content.

Scope: the **deal team**, the first role. Section order and numbering follow the questionnaire (A1 to G4). Status is **answered** or **open**; every open item has an owner (a role from [03 Stakeholders](../../docs/playbook/03-stakeholders.md)) and a due date. Where our playbook has a default stance, the answer says whether the customer confirms or changes it.

Discovery date: 2026-11-14. Roles are used instead of names here; the named people go in [stakeholders.md](stakeholders.md) (#26).

## A. Sponsor and scope

| # | Question (short) | Answer | Design impact | Status |
|---|---|---|---|---|
| A1 | Sponsor and 6-month outcome | The COO sponsors. In 6 months the deal team should spend visibly less time on first-pass company briefs and CRM upkeep, with a low edit rate on what the twin drafts. Numeric targets are set in design. | Sets the scorecard: hours saved and edit rate on the two named tasks. See [15](../../docs/compendium/15-governance-and-performance.md). | answered |
| A2 | First roles; is private equity in scope? | The deal team is first. Private equity is in scope; it is the whole engagement. | First epic is the deal-team twin. MNPI is present, so deal material stays on ZDR surfaces. See [14](../../docs/compendium/14-private-equity.md). | answered |
| A3 | Headcount per role; pilot size | 65 staff in total. Deal team: 18 (partners, principals, associates). Pilot: 6, chosen by the business owner. | Pilot of 6 fits the 5 to 10 guidance. The other 12 deal-team members and other roles join at Scale. See [12](../../docs/compendium/12-orgs-and-ownership.md). | answered |

## B. Claude plans and licensing

| # | Question (short) | Answer | Design impact | Status |
|---|---|---|---|---|
| B1 | Plans in use, and how many | Claude Enterprise with 40 seats, plus 8 people on individual Pro plans. No Team plan. No API use was reported. | Enterprise gives group targeting through SCIM, audit and custom retention. The 8 Pro accounts are outside IT's control and on consumer terms. See [09](../../docs/compendium/09-plans-and-it-controls.md). | answered |
| B2 | Individual licenses on the company domain? | Yes: 8 people bought Pro plans on the company domain. | Plan the migration to the Enterprise org. Domain capture is one-way and unmigrated accounts are deleted after 30 days, so announce it first. See [09](../../docs/compendium/09-plans-and-it-controls.md). | answered |
| B3 | Who holds Owner and Primary Owner? | The Director of IT is Primary Owner. An IT administrator is the second Owner. | Only Owners can manage skills and plugins, so IT drives publishing. Two Owners means no lock-out. See [04](../../docs/compendium/04-distribution-governance.md). | answered |

## C. Data classes and compliance

| # | Question (short) | Answer | Design impact | Status | Owner | Due |
|---|---|---|---|---|---|---|
| C1 | Data classes per role | Deal team: internal, confidential and highly sensitive (MNPI). Investor relations: confidential (investor and fundraising contacts). No PHI today. | Highly sensitive work goes to ZDR surfaces, on managed devices. See [10](../../docs/compendium/10-sensitive-data.md). | answered | | |
| C2 | Any PHI? Is there a BAA? | No PHI today and no BAA. One portfolio company is a healthcare services business, so diligence or portfolio-monitoring files might contain PHI. Compliance has not yet ruled on it. | HIPAA is permanent per org and many features are excluded, so this decides whether a separate org is ever needed. Until answered: treat PHI as out of scope and keep portfolio-company health files away from the twin. See [10](../../docs/compendium/10-sensitive-data.md). | open | Compliance / legal | 2026-11-27 |
| C3 | Required retention; accept the ZDR exceptions? | Compliance has not stated its retention requirement and has not yet seen the ZDR exceptions (flagged content kept up to 2 years, feedback 5 years). **Provisionally confirms the default:** 30-day retention for private-equity chat. | Decides the retention setting and whether feedback is turned off. Our governance log is the long-term audit record. See [10](../../docs/compendium/10-sensitive-data.md) and [14](../../docs/compendium/14-private-equity.md). | open | Compliance / legal | 2026-12-04 |
| C4 | Information barriers: soft or hard? | Soft walls between the deal team and investor relations, enforced through role-based access in Salesforce and HubSpot. **Confirms the default** (soft walls, option B). | One private-equity org. Per-user OAuth, no shared identities, so source-system roles do the enforcing. Build so soft walls can later become hard walls. See [14](../../docs/compendium/14-private-equity.md). | answered | | |
| C5 | Is there MNPI? | Yes, in deal work. | Web search and fetch off. Deal material and MNPI only on ZDR surfaces. See [14](../../docs/compendium/14-private-equity.md). | answered | | |

## D. Identity and devices

| # | Question (short) | Answer | Design impact | Status |
|---|---|---|---|---|
| D1 | Identity provider; SSO and SCIM? | Okta, with SCIM. | SCIM groups target plugins and skills per group. Okta device trust can gate sign-in. See [09](../../docs/compendium/09-plans-and-it-controls.md). | answered |
| D2 | MDM, and managed versus unmanaged share | Microsoft Intune manages all staff laptops. 5 operating partners use unmanaged personal devices. | Deal-team staff are on managed laptops, so the strongest controls apply to the pilot. Operating partners get no direct access to highly sensitive data; they would need a hosted twin. See [13](../../docs/compendium/13-devices.md). | answered |
| D3 | Contractors or other external users? | Yes, some contractors, also on unmanaged personal devices. None are in the pilot. | Same rule as unmanaged devices: no Claude Code, no direct access to highly sensitive data, connectors read-only. See [13](../../docs/compendium/13-devices.md). | answered |

## E. Systems and connectors

| # | Question (short) | Answer | Design impact | Status | Owner | Due |
|---|---|---|---|---|---|---|
| E1 | Which CRM, and which edition? | Salesforce Enterprise Edition holds the deal pipeline. HubSpot Marketing Hub Professional holds investor relations and fundraising contacts. | Salesforce Hosted MCP needs Enterprise Edition and an External Client App, which this meets. HubSpot reaches the twin through its own MCP server; the compendium does not state the tier it needs, so confirm in design. See [11](../../docs/compendium/11-connectors.md). | answered | | |
| E2 | Where do documents live? | SharePoint and OneDrive. | The Microsoft 365 connector (work accounts). A Global Admin must consent for the tenant. Reads by default. See [11](../../docs/compendium/11-connectors.md). | answered | | |
| E3 | Which messaging tools? | Microsoft Teams internally. Slack Connect with some portfolio companies. | Teams is covered by the Microsoft 365 connector. Slack Connect channels carry outside content, so no twin may both read them and post without a person approving each send. Claude Tag is unavailable under ZDR. See [11](../../docs/compendium/11-connectors.md). | answered | | |
| E4 | How is access controlled in each system? | Salesforce: roles and sharing rules. HubSpot: user permissions and teams. SharePoint: site and library permissions. The Salesforce and HubSpot admins have not yet confirmed that deal-team and investor-relations roles are fully separated. | Soft walls depend on this. Design includes a wall check: confirm each role boundary before the pilot. See [14](../../docs/compendium/14-private-equity.md). | answered | | |
| E5 | Any systems on a private network only? | No. Salesforce, HubSpot, Microsoft 365 and Slack are all cloud services. (Splunk hosting is covered in G1.) | No MCP tunnel needed for the pilot. See [11](../../docs/compendium/11-connectors.md). | answered | | |
| E6 | Can they allowlist Anthropic's IP range (`160.79.104.0/21`)? | Not yet asked of the security team. | Needed for remote connectors that sit behind an IP allowlist, and for any wrapper server we host. See [11](../../docs/compendium/11-connectors.md). | open | Security | 2026-11-27 |

## F. Roles and tasks (deal team)

Run from three interviews with deal-team members (a partner, a principal, an associate). The candidate tasks follow the table. All figures are the interviewees' estimates.

| # | Question (short) | Answer | Design impact | Status | Owner | Due |
|---|---|---|---|---|---|---|
| F1 | Which tasks take most of the week; how often and how long? | Six candidate tasks, with frequency and minutes per task, in the table below. | Task choice and the value baseline. See [07](../../docs/compendium/07-pilot-roles.md). | answered | | |
| F2 | Inputs, systems, output and audience | In the table below, per task. All inputs sit in Salesforce, SharePoint or Teams. | Connectors: Salesforce, Microsoft 365. No HubSpot input, which keeps the wall intact. See [11](../../docs/compendium/11-connectors.md). | answered | | |
| F3 | What does good look like? 2 to 3 real examples | Not collected yet. The deal team has agreed to share two past company briefs, one good and one weak, and a sample CRM update. | These become the evals, and they are written before the skill. See [03](../../docs/compendium/03-skills-authoring.md). | open | Skill owners | 2026-12-04 |
| F4 | What if it goes wrong? | Per task, in the table below. The costliest are wrong facts in a brief and a wrong screening summary reaching a principal. | Sets the autonomy ceiling: drafts at level 1; CRM writes at level 2 only after scorecard evidence. See [06](../../docs/compendium/06-autonomy.md). | answered | | |
| F5 | Scheduled, event-driven or person-started? | Five tasks are started by a person. One (the Monday pipeline summary) runs on a schedule. | The five run in the client. The scheduled one is a hosted job in the ZDR Platform org, with a front end we build. See [05](../../docs/compendium/05-decision-matrix.md). | answered | | |

### Candidate tasks for the deal team

| # | Task | Frequency | Minutes per task | Inputs and systems | Output and audience | Cost of a mistake | Trigger |
|---|---|---|---|---|---|---|---|
| T1 | Prepare a one-page company brief | About 4 per associate per week | 90 | Salesforce deal record; prior memos and data-room files in SharePoint | One page for the deal team; may feed a partner discussion | Medium: a wrong fact can reach a partner discussion. A reviewer checks every brief. | Person |
| T2 | Update the CRM after a meeting | About 10 per person per week | 15 | Meeting notes or Teams transcript; the Salesforce opportunity | Activity log and next-step fields in Salesforce; the deal team | Low to medium: stale or wrong pipeline data. Writes start as drafts a person approves. | Person (event-driven later: meeting ends) |
| T3 | Weekly pipeline summary for the Monday deal meeting | Weekly | 60 | Salesforce pipeline report | Summary posted to the deal team in Teams | Medium: a wrong stage or amount in front of the partners. | Schedule (Monday morning) |
| T4 | Screen an inbound CIM or teaser | About 5 per week | 40 | The document, from email or SharePoint; Salesforce for prior contact with the company | Screening summary with a pursue-or-pass suggestion, for a principal | Medium to high: a missed red flag, or a good deal passed over | Event (a new document arrives); person in the pilot |
| T5 | Prepare for a management or expert call | About 8 per month | 45 | Salesforce, SharePoint, prior call notes | Briefing note for the caller | Low: the caller reads it before the call | Person |
| T6 | Draft a section of an investment committee memo from diligence notes | About 2 per month per deal | 240 | Diligence notes and data-room files in SharePoint | Draft section for the partners | High: the memo informs a decision. Always a draft, always reviewed. | Person |

## G. Governance, logging and spend

| # | Question (short) | Answer | Design impact | Status | Owner | Due |
|---|---|---|---|---|---|---|
| G1 | Which security log system or warehouse? | Splunk is the security log system. Whether the governance log goes there is not decided. Hosting (cloud or self-managed) and who may read the log are not yet known. **Confirms the default:** the destination is a customer discussion. | The design (what is recorded, metadata only for private equity, one log for all twins) is fixed. Only the destination changes. See [15](../../docs/compendium/15-governance-and-performance.md). | open | Technical owner (Director of IT) | 2026-12-04 |
| G2 | Salesforce logging; any Salesforce-Anthropic integration? | No Salesforce-Anthropic integration exists today. What they log in Salesforce (Event Monitoring, Field Audit Trail, Setup Audit Trail) is unknown; the Salesforce admin has not checked which are licensed and on. | If Event Monitoring is on, it may cover the Salesforce part of the audit trail. See [15](../../docs/compendium/15-governance-and-performance.md). | open | Source-system admins (Salesforce admin) | 2026-11-27 |
| G3 | Who owns tooling and spend; budget and limits? | IT owns tooling and spend. **Confirms the default.** The pilot budget and the per-user spend limits are not yet set. | Spend controls, per-user limits and alerts follow the budget. See [15](../../docs/compendium/15-governance-and-performance.md). | open | Executive sponsor | 2026-12-04 |
| G4 | Technical owner, business owner, backup Owner? | Technical owner: the Director of IT. Business owner: the RevOps manager. Backup Owner: an IT administrator. **Confirms the defaults.** | One Owner pair for the org; compliance signs off on retention and walls. Names go in [stakeholders.md](stakeholders.md) (#26). See [12](../../docs/compendium/12-orgs-and-ownership.md) and [03](../../docs/playbook/03-stakeholders.md). | answered | | |

## Discovery summary

The findings that drive design, and where the options are explained:

1. **MNPI means deal material stays on ZDR surfaces, with web tools off.** Chat follows 30-day retention (default, provisionally confirmed; C3 is open), so our own governance log is the long-term record. See [14 Private equity](../../docs/compendium/14-private-equity.md) and [10 Sensitive data](../../docs/compendium/10-sensitive-data.md).
2. **Soft walls, enforced by Salesforce and HubSpot roles, are the wall design.** One private-equity org with per-user identity and no shared accounts. Confirm the role boundaries before the pilot (E4). See [14 Private equity](../../docs/compendium/14-private-equity.md).
3. **The PHI question is open and could force a separate HIPAA org.** A healthcare services portfolio company is the trigger (C2). HIPAA is permanent once on. See [10 Sensitive data](../../docs/compendium/10-sensitive-data.md) and [12 Orgs and ownership](../../docs/compendium/12-orgs-and-ownership.md).
4. **Eight Pro accounts on the company domain need a migration plan.** Domain capture is one-way and deletes unmigrated accounts after 30 days. See [09 Plans and IT controls](../../docs/compendium/09-plans-and-it-controls.md).
5. **Operating partners and contractors on unmanaged devices cannot touch highly sensitive data directly.** Pilot users are all on managed laptops; a hosted twin or an Okta device check covers the rest. See [13 Devices](../../docs/compendium/13-devices.md).
6. **Connectors: Salesforce Hosted MCP and the Microsoft 365 connector cover the pilot.** Slack Connect brings outside content, so no read-and-send twin. IP allowlisting (E6) is open. See [11 Connectors](../../docs/compendium/11-connectors.md).
7. **The governance log's destination is open: Splunk is the candidate, and Salesforce Event Monitoring may cover the source-system half.** G1 and G2 are open. See [15 Governance and performance](../../docs/compendium/15-governance-and-performance.md).
8. **First tasks are the company brief (T1) and the post-meeting CRM update (T2).** Both start at level 1; CRM writes move to level 2 on scorecard evidence; the Monday pipeline summary (T3) is the first hosted job. See [06 Autonomy](../../docs/compendium/06-autonomy.md), [05 Hosted or client](../../docs/compendium/05-decision-matrix.md) and [07 Pilot roles](../../docs/compendium/07-pilot-roles.md).

### Open items

| # | Item | Owner | Due |
|---|---|---|---|
| C2 | PHI exposure and BAA | Compliance / legal | 2026-11-27 |
| E6 | IP allowlisting | Security | 2026-11-27 |
| G2 | Salesforce Event Monitoring and related logs | Source-system admins | 2026-11-27 |
| C3 | Retention and the ZDR exceptions | Compliance / legal | 2026-12-04 |
| F3 | Real good and bad examples | Skill owners | 2026-12-04 |
| G1 | Where the governance log goes | Technical owner (Director of IT) | 2026-12-04 |
| G3 | Budget and spend limits | Executive sponsor | 2026-12-04 |
