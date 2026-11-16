# Discovery: Example Software Co

> **Fictional customer.** Example Software Co and every name, person and figure on this page are invented. This is the Team-plan worked example for the [discovery questionnaire](../../docs/playbook/02-discovery.md). Copy the structure for a real customer, not the content.

Scope: the **customer success team**, the first role. Section order and numbering follow the questionnaire (A1 to G4). Status is **answered** or **open**; every open item has an owner and a due date. Every answer below is answered.

Discovery date: 2026-11-04. One call with Teodor Amsel, the IT and operations lead. Odalys Fenwick, the VP Customer Success and the sponsor, joined for section A. The answers are written as they gave them.

## A. Sponsor and scope

| # | Question (short) | Answer | Status |
|---|---|---|---|
| A1 | Sponsor and 6-month outcome | Odalys Fenwick, VP Customer Success at Example Software Co, sponsors it. In her words: "In 6 months each customer success manager spends less time preparing for calls and writing follow-ups, and no renewal is missed for lack of warning." | answered |
| A2 | First roles; is private equity in scope? | Customer success first. We are a B2B software company; private equity is not in scope. | answered |
| A3 | Headcount per role; pilot size | 60 people in the company. The customer success team is 8 managers, and 4 of them will pilot. | answered |

## B. Claude plans and licensing

| # | Question (short) | Answer | Status |
|---|---|---|---|
| B1 | Plans in use, and how many | Claude Team, 60 seats: one for everyone. No Enterprise and no API use. | answered |
| B2 | Individual licenses on the company domain? | None. We checked: 0 individual accounts on our domain. | answered |
| B3 | Who holds Owner and Primary Owner? | Teodor Amsel is Primary Owner. Nadia Rusu, the operations analyst, is the second Owner. | answered |

## C. Data classes and compliance

| # | Question (short) | Answer | Status |
|---|---|---|---|
| C1 | Data classes per role | Internal and confidential only. Contracts, CRM data and customer calls are confidential; nothing is more sensitive than that. | answered |
| C2 | Any PHI? Is there a BAA? | No PHI, so no BAA. | answered |
| C3 | Required retention; accept the ZDR exceptions? | No special requirement: standard retention is fine for us. Compliance is Pieter Achterberg, our finance and legal lead. | answered |
| C4 | Information barriers: soft or hard? | None. We have no walls; the whole team sees every account. | answered |
| C5 | Is there MNPI? | No MNPI. | answered |

## D. Identity and devices

| # | Question (short) | Answer | Status |
|---|---|---|---|
| D1 | Identity provider; SSO and SCIM? | Everyone signs in with Google Workspace. No SSO and no SCIM for Claude. | answered |
| D2 | MDM, and managed versus unmanaged share | No device management at all (none). None of our laptops are managed: staff use their own laptops, all 60 staff. | answered |
| D3 | Contractors or other external users? | No contractors or outside users. | answered |

## E. Systems and connectors

| # | Question (short) | Answer | Status |
|---|---|---|---|
| E1 | Which CRM, and which edition? | HubSpot is our CRM, on Sales Hub Professional. | answered |
| E2 | Where do documents live? | Google Drive for documents, Gmail for mail and Google Calendar for meetings, all on Google Workspace Business Standard. | answered |
| E3 | Which messaging tools? | Slack, on Slack Pro. Support tickets are in Zendesk, on Suite Team. | answered |
| E4 | How is access controlled in each system? | HubSpot: teams and record permissions. Google Drive: shared drives per team. Gmail: each user's own mailbox. Google Calendar: each user's own calendar. Slack: public and private channels. Zendesk: agent groups. The usage database: database roles; analysts only. | answered |
| E5 | Any systems on a private network only? | One: our internal product-usage database, in-house (PostgreSQL), on our private network. HubSpot, Google Drive, Gmail, Google Calendar, Slack and Zendesk are cloud services, not on a private network. | answered |
| E6 | Can they allowlist Anthropic's IP range (`160.79.104.0/21`)? | Yes, we can allowlist it. | answered |

## F. Roles and tasks (customer success)

| # | Question (short) | Answer | Status |
|---|---|---|---|
| F1 | Which tasks take most of the week; how often and how long? | Asked in the role interviews; the answers are in the notes under [personas/customer-success-manager/interviews/](personas/customer-success-manager/interviews/). | answered |
| F2 | Inputs, systems, output and audience | Asked in the role interviews, per task (same notes). | answered |
| F3 | What does good look like? 2 to 3 real examples | Asked in the role interviews, per task (same notes). | answered |
| F4 | What if it goes wrong? | Asked in the role interviews, per task (same notes). | answered |
| F5 | Scheduled, event-driven or person-started? | Asked in the role interviews, per task (same notes). | answered |

## G. Governance, logging and spend

| # | Question (short) | Answer | Status |
|---|---|---|---|
| G1 | Which security log system or warehouse? | None: we run no security log system. Nobody here requires a log of every action the twin takes. | answered |
| G2 | Salesforce logging; any Salesforce-Anthropic integration? | We don't use Salesforce. What we have is HubSpot's own audit log and Zendesk ticket history. | answered |
| G3 | Who owns tooling and spend; budget and limits? | The IT and operations lead owns tooling and spend. The limit is a monthly cap set by the IT and operations lead. | answered |
| G4 | Technical owner, business owner, backup Owner? | Technical owner: Teodor Amsel, IT and operations lead. Business owner: Marisol Quenby, customer success team lead. Backup Owner: Nadia Rusu, operations analyst. | answered |
