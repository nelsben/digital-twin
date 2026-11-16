# Stakeholders: Example Capital Partners

> **Fictional customer, invented people.** Example Capital Partners and every name, title and person on this page are invented. Any resemblance to a real person is a coincidence. This is the worked example for [03 Stakeholders](../../docs/playbook/03-stakeholders.md). Copy the structure for a real customer, not the content.

[Discovery](discovery.md) used roles instead of names and promised the named people here. This page names one person for every customer and partner role in the playbook, gives the engagement RACI, and says who signs each phase gate and how we keep in touch. Nothing here changes a discovery answer: the sponsor is the COO, the Director of IT is technical owner and Primary Owner, an IT administrator is the backup Owner, the RevOps manager is business owner, Compliance / legal owns C2 and C3, Security owns E6, and the source-system admins own E4 and G2.

Later documents (design, backlog, sign-offs) should refer to people by role and name as written in the tables below.

## Customer roles

Roles and responsibilities are those in [03 Stakeholders](../../docs/playbook/03-stakeholders.md). "Open items owned" are the open items in [discovery](discovery.md), with their due dates. A dash means the person owns no open item today.

| Role | Name (invented) | Title | Responsible for in this engagement | Open items owned (from discovery.md) |
|---|---|---|---|---|
| **Executive sponsor** | Marguerite Oyelaran | COO | The 6-month outcome (less time on company briefs and CRM upkeep, low edit rate), the budget, and removing blockers. Chooses which roles come after the deal team. | G3: pilot budget and per-user spend limits (due 2026-12-04) |
| **Technical owner** | Tomasz Hadjiev | Director of IT | Primary Owner of the Claude Enterprise org. SSO and SCIM (Okta), Intune-managed devices, managed settings, connectors, tooling and spend, the governance-log pipeline, the migration of the 8 Pro accounts, offboarding. | G1: where the governance log goes (due 2026-12-04) |
| **Backup Owner** | Keiko Lindqvist | IT administrator | Second Owner of the org, so no one person can lock everyone out. Covers publishing of skills and plugins when the Director of IT is away. | - |
| **Business owner** | Samir Castellanos | RevOps manager | Which deal-team tasks to automate, story priority, choosing the 6 pilot users, autonomy promotions (CRM writes to level 2 only on scorecard evidence), the monthly scorecard. | - |
| **Compliance / legal** | Ngozi Brandvold | Chief Compliance Officer | Data classes, retention, information walls and the PHI question. Signs off on retention and walls. | C2: PHI exposure and BAA (due 2026-11-27); C3: retention and the ZDR exceptions (due 2026-12-04) |
| **Security** | Rashida Kovalenko | CISO | Reviewing connectors and skills, the device policy, IP allowlisting, access controls on the governance log. | E6: allowlisting `160.79.104.0/21` (due 2026-11-27) |
| **Source-system admins** (Salesforce) | Joaquin Lindahl | Salesforce administrator | External Client App and OAuth setup for Salesforce Hosted MCP, roles and sharing rules, field markers for twin edits. Confirms before the pilot that deal-team and investor-relations roles are fully separated (E4). | E4: written confirmation that deal-team and investor-relations roles are fully separated in Salesforce (due 2026-11-27); G2: Salesforce Event Monitoring and related logs (due 2026-11-27) |
| **Source-system admins** (HubSpot) | Imani Petrov | HubSpot administrator | User permissions and teams on the investor-relations side of the wall. Confirms the same role boundary as the Salesforce admin (E4). | E4: written confirmation that the roles are fully separated in HubSpot (due 2026-11-27) |
| **Source-system admins** (M365) | Hiroshi Delacroix | Microsoft 365 administrator | Tenant consent for the Microsoft 365 connector (a Global Admin must consent), SharePoint site and library permissions. | - |
| **Skill owner** (company briefs, T1; call prep, T5) | Callum Nwosu | Associate, deal team | Content, examples and evals for the company-brief and call-prep skills; reviews changes. | F3: good and weak example briefs and a sample CRM update (due 2026-12-04, shared across skill owners) |
| **Skill owner** (CRM update T2; CIM screening T4) | Beatriz Halloran | Principal, deal team | Content, examples and evals for the post-meeting CRM update and CIM-screening skills; reviews changes. | F3 (shared, as above) |
| **Skill owner** (IC memo sections, T6) | Ravindra Sorensen | Partner, deal team | Content, examples and evals for the investment committee memo skill; reviews changes. | F3 (shared, as above) |
| **Pilot users** (6) | Chosen by the business owner at the start of the pilot; named in the backlog | 3 associates, 2 principals, 1 partner (all deal team, all on Intune-managed laptops) | Using the twin, giving feedback, reporting failures. Operating partners and contractors (unmanaged devices) are not in the pilot. | - |

## Partner roles

Roles and responsibilities are those in [03 Stakeholders](../../docs/playbook/03-stakeholders.md).

| Role | Name (invented) | Responsible for in this engagement | Main customer counterpart |
|---|---|---|---|
| **Engagement lead** | Eleanor Osei-Whitcombe | Scope, plan, the sign-offs below, and the relationship with the COO. Chairs the steering meeting. | Marguerite Oyelaran (COO) |
| **Solution architect** | Mateo Ferreira | The single private-equity org plan, data and device policy, connector and soft-wall design, the governance-log design. | Tomasz Hadjiev (Director of IT), Ngozi Brandvold (CCO) |
| **Skill engineer** | Yuki Sandoval | Evals first, then the deal-team skills, persona and plugins, built from the skill owners' examples. | Callum Nwosu, Beatriz Halloran and Ravindra Sorensen (skill owners) |
| **Integration engineer** | Kwame Haldorsen | Salesforce Hosted MCP and Microsoft 365 connector setup, the hosted Monday pipeline job (T3), the logging hook. | Joaquin Lindahl, Hiroshi Delacroix (source-system admins), Keiko Lindqvist |
| **Change and enablement lead** | Sunita Papadakis | Training, pilot support and adoption for the 6 pilot users. | Samir Castellanos (RevOps manager) |

## RACI

R = responsible, A = accountable, C = consulted, I = informed. Rows and columns are those of the playbook RACI in [03 Stakeholders](../../docs/playbook/03-stakeholders.md). The column roles map to people above: Sponsor is Marguerite Oyelaran, Director of IT is Tomasz Hadjiev, RevOps manager is Samir Castellanos, Compliance is Ngozi Brandvold, Security is Rashida Kovalenko, System admins are Joaquin Lindahl, Imani Petrov and Hiroshi Delacroix, Skill owners are Callum Nwosu, Beatriz Halloran and Ravindra Sorensen, and Partner is the team above.

| Activity | Sponsor | Director of IT | RevOps manager | Compliance | Security | System admins | Skill owners | Partner |
|---|---|---|---|---|---|---|---|---|
| Discovery | A | C | C | C | C | C | C | R |
| Choosing roles and tasks | A | I | R | C | I | I | C | C |
| Org plan and data policy | I | A | C | R (data policy) | C | I | I | R (design) |
| Story backlog and priority | I | C | A | C | C | I | C | R |
| Writing evals and skills | I | I | C | I | I | I | R (content) | R (build), A |
| Connectors and managed settings | I | A | I | C | C | R | I | R |
| Governance log | I | A | C | C | C | C | I | R |
| Pilot | I | C | A | I | I | I | C | R |
| Autonomy promotions | I | C | A | C | C | I | C | R (evidence) |
| Running after handover | I | A (technical) | A (business) | C | C | R | R | I |

**Cells changed from the playbook:** none. This customer's discovery answers (IT owns tooling and spend, soft walls, one private-equity org) match the playbook defaults, so no cell differs.

## Sign-offs

One row per phase gate in [01 Engagement model](../../docs/playbook/01-engagement-model.md). Phase 0 (Qualify) ended when the COO agreed to discovery and is not repeated here. "Signs" means the named person gives the customer's sign-off; the engagement lead, Eleanor Osei-Whitcombe, collects it.

| Phase | Gate (what is signed off) | Signs for the customer (name, role) | Also required |
|---|---|---|---|
| **1. Discovery** | Discovery summary | Marguerite Oyelaran, COO (executive sponsor) | Every question answered or open with an owner; the 8 open items carry due dates (the last on 2026-12-04) |
| **2. Design** | Design document and the prioritized backlog | Tomasz Hadjiev, Director of IT (technical owner), and Samir Castellanos, RevOps manager (business owner) | Ngozi Brandvold, CCO, signs off on retention and the walls (C2, C3 closed first) |
| **3. Build** | Each story's acceptance criteria (its evals passing) | Samir Castellanos, RevOps manager (business owner) | The skill owner for that story confirms the evals reflect good work; Tomasz Hadjiev confirms connector and settings stories |
| **4. Pilot** | Pilot scorecard | Samir Castellanos, RevOps manager (business owner) | Marguerite Oyelaran, COO, reviews the scorecard at steering |
| **5. Scale** | Each autonomy promotion and each new role | Autonomy promotions: Samir Castellanos, RevOps manager. New roles: Marguerite Oyelaran, COO | Ngozi Brandvold and Rashida Kovalenko consulted on each promotion, with the scorecard evidence |
| **6. Run / hand over** | Handover acceptance | Tomasz Hadjiev, Director of IT (technical), and Samir Castellanos, RevOps manager (business) | The customer runs the review cadence without us; Keiko Lindqvist as backup Owner is trained |

## Communication

Two standing meetings. Dates and times are set by the engagement lead in week 1; open items from [discovery](discovery.md) are reviewed in both until they close.

| Meeting | Cadence | Purpose | Customer attendees | Partner attendees |
|---|---|---|---|---|
| **Working session** | Weekly, 45 minutes | Progress on the current phase, open items and due dates, blockers, decisions needed from owners this week | Samir Castellanos (business owner), Tomasz Hadjiev (technical owner), Keiko Lindqvist (backup Owner). Skill owners join when the agenda has skills or evals. Compliance, Security and the source-system admins join for their open items only. | Eleanor Osei-Whitcombe (chair), Mateo Ferreira, Yuki Sandoval, Kwame Haldorsen. Sunita Papadakis joins from Phase 3. |
| **Steering** | Fortnightly, 30 minutes | Status against the 6-month outcome, risks, budget and spend, sign-offs due, and in the pilot the monthly scorecard | Marguerite Oyelaran (sponsor, chair for the customer), Tomasz Hadjiev, Samir Castellanos. Ngozi Brandvold when walls, retention or PHI are on the agenda. | Eleanor Osei-Whitcombe, Mateo Ferreira |

Between meetings, anything blocking goes to the engagement lead, who raises it with the sponsor if it cannot wait for steering.
