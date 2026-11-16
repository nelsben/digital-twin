# Discovery: Example Regional Insurance Brokers

> **Fictional customer.** Example Regional Insurance Brokers and every name, person, product and figure on this page are invented for a review walk. Ledgerline Claims is an invented product.

Scope: the **claims handler**, the first role. Section order and numbering follow the [questionnaire](../../../../../docs/playbook/02-discovery.md) (A1 to G4). Status is **answered** or **open**; every open item has an owner and a due date.

Discovery date: 2026-11-10. One call with the Head of Claims (sponsor, section A only), the IT Infrastructure Manager and the Head of Compliance.

## A. Sponsor and scope

| # | Question (short) | Answer | Status | Owner | Due |
|---|---|---|---|---|---|
| A1 | Sponsor and 6-month outcome | The Head of Claims sponsors. In her words: "In six months I want my handlers spending half the time they do now on the Friday client reports, and I never want to miss a 24-hour acknowledgement on a new claim again." | answered | | |
| A2 | First roles; is private equity in scope? | Claims handlers first. No private equity. The firm is a regional insurance broker (commercial and personal lines). | answered | | |
| A3 | Headcount per role; pilot size | 180 staff. Claims handlers: 22 (9 commercial motor and property, 4 injury, 9 personal lines). Pilot: 6, chosen by the Claims Team Leader. | answered | | |

## B. Claude plans and licensing

| # | Question (short) | Answer | Status | Owner | Due |
|---|---|---|---|---|---|
| B1 | Plans in use, and how many | Claude Enterprise, 120 seats, bought in the summer. No zero-data-retention addendum. No API use. | answered | | |
| B2 | Individual licenses on the company domain? | Yes, 3 people in marketing on Pro. | answered | | |
| B3 | Who holds Owner and Primary Owner? | IT Infrastructure Manager is Primary Owner; the IT Service Desk Lead is the second Owner. | answered | | |

## C. Data classes and compliance

| # | Question (short) | Answer | Status | Owner | Due |
|---|---|---|---|---|---|
| C1 | Data classes per role | Claims handlers: internal and confidential (policyholder and claimant personal data, claim values). Injury claims carry medical reports from claimants' doctors and medical experts. "Highly sensitive" is a class the firm uses for medical reports. | answered | | |
| C2 | Any PHI? Is there a BAA? | No BAA. Whether the medical reports on injury claims count as PHI: the Head of Compliance said "I genuinely don't know whether that applies to us as a broker; I'll take advice." | open | Head of Compliance | 2026-11-27 |
| C3 | Required retention; accept the ZDR exceptions? | Standard Claude retention is accepted for now; no ZDR was bought. Claim files are kept seven years in Ledgerline, which is the record. | answered | | |
| C4 | Information barriers? | None. | answered | | |
| C5 | Is there MNPI? | No. | answered | | |

## D. Identity and devices

| # | Question (short) | Answer | Status | Owner | Due |
|---|---|---|---|---|---|
| D1 | Identity provider; SSO and SCIM? | Okta, with SSO and SCIM to Claude already set up. | answered | | |
| D2 | MDM, and managed versus unmanaged share | Microsoft Intune manages every Windows laptop. About ten claims staff read Outlook and Teams on their own phones, which are not enrolled. | answered | | |
| D3 | Contractors or external users? | Two loss adjusters on contract use Teams guest access only; no Claude seats. | answered | | |

## E. Systems and connectors

| # | Question (short) | Answer | Status | Owner | Due |
|---|---|---|---|---|---|
| E1 | Which CRM? | Microsoft Dynamics 365 Sales, Enterprise edition, for client and policy contacts. | answered | | |
| E2 | Where do documents live? | SharePoint Online: one site per client team; medical reports sit in a restricted "Injury - medical" library. | answered | | |
| E3 | Which messaging tools? | Microsoft Teams. Outlook for all email and calendars. Microsoft 365 E3. | answered | | |
| E4 | How is access controlled in each system? | Dynamics: security roles by business unit. SharePoint: site permissions per client team; the medical library is limited to the injury team. Ledgerline: roles handler, senior handler, team leader. | answered | | |
| E5 | Any systems on a private network only? | Ledgerline Claims 9.2 runs on-premises on the private network, with no internet exposure. | answered | | |
| E6 | Can they allowlist Anthropic's IP range? | No. "We will not open Ledgerline to the internet, allowlist or not." | answered | | |

## G. Governance, logging and spend

| # | Question (short) | Answer | Status | Owner | Due |
|---|---|---|---|---|---|
| G1 | Log system; a log of every action? | Microsoft Sentinel. Compliance wants a record of every action the twin takes on a claim. | answered | | |
| G2 | Existing source audit? | Ledgerline keeps an audit trail of every claim change. No Salesforce. | answered | | |
| G3 | Who owns tooling and spend; limits? | IT Infrastructure Manager owns spend. A per-user monthly limit is wanted; the amount is not set. | answered | | |
| G4 | Technical, business and backup owners | Technical owner: IT Infrastructure Manager. Business owner: Claims Team Leader. Backup Owner: IT Service Desk Lead. | answered | | |
