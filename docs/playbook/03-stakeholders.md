# 03 — Stakeholders

## Customer roles (name a person for each in discovery)

| Role | Typical title | Responsible for |
|---|---|---|
| **Executive sponsor** | COO, CRO, managing partner | The outcome, the budget and removing blockers |
| **Technical owner** | **Director of IT** | Claude orgs (Owner role), SSO and SCIM, devices and MDM, managed settings, connectors, tooling and **spend**, the log pipeline, offboarding |
| **Backup Owner** | IT administrator | Second Owner in each org, so no one person can lock everyone out |
| **Business owner** | **RevOps manager** (or the role's own leader) | Which tasks to automate, story priority, autonomy promotions, the monthly scorecard |
| **Compliance / legal** | CCO, general counsel | Data classes, retention, walls, BAA and ZDR terms; signs off for the private-equity and HIPAA orgs |
| **Security** | CISO, security engineer | Reviewing connectors and skills, the device policy, IP allowlisting, the log's access controls |
| **Source-system admins** | Salesforce admin, HubSpot admin, M365 or Google admin | External Client App and OAuth setup, role-based access, tenant consent, field markers for twin edits |
| **Skill owners** | Subject-matter experts in each role | Each skill's content, examples and evals; reviewing changes |
| **Pilot users** | 5–10 per role | Using the twin, giving feedback, reporting failures |

## Partner roles (us)

| Role | Responsible for |
|---|---|
| **Engagement lead** | Scope, plan, stakeholder management, sign-offs |
| **Solution architect** | Org plan, data and device policy, connector and wall design, the governance-log design |
| **Skill engineer** | Evals, skills, persona, plugins |
| **Integration engineer** | Connectors (configuring, wrapping or building), hosted agents, the logging hook |
| **Change and enablement lead** | Training, pilot support, adoption |

## RACI

R = responsible, A = accountable, C = consulted, I = informed.

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
