# Design: Example Capital Partners

> **Fictional customer, invented people.** Example Capital Partners and every name, person and figure on this page are invented. This is the worked example of the Phase 2 design document in the [engagement model](../../docs/playbook/01-engagement-model.md). Copy the structure for a real customer, not the content.

Phase 2 deliverable for the deal-team twin. Author: Mateo Ferreira (solution architect). Sign-off collected by Eleanor Osei-Whitcombe (engagement lead). Status: draft for sign-off, 2026-11-14.

Every decision below cites the [discovery](discovery.md) question it answers (A1 to G4) and the compendium page that explains the options. People are named as in [stakeholders.md](stakeholders.md). Items marked **open** wait on a discovery answer; section 12 lists them with an owner and a date. The prioritized story backlog is a separate Phase 2 deliverable (`backlog.md`, coming) and is signed off with this document.

## 1. Summary

Example Capital Partners gets one Claude org for people, the existing Claude Enterprise org with 40 seats, run as a **private-equity org** with zero data retention (ZDR) on Claude Code. A second, Platform org for hosted agents is planned but not provisioned until the first hosted job or hosted front end is scheduled. The deal-team twin starts with a pilot of 6 users on Intune-managed laptops, at autonomy level 1 (drafts only), with two skills: the company brief (T1) and the post-meeting CRM update (T2). Because the deal team handles MNPI, deal material stays on ZDR surfaces with web search and fetch off; chat is held to 30-day retention, provisionally, so our own metadata-only governance log is the long-term audit record. The soft wall between the deal team and investor relations is enforced by Salesforce and HubSpot role-based access under per-user identity, and a wall test (spike #30) must pass before the pilot. Operating partners and contractors on unmanaged devices get no direct access to highly sensitive data; a hosted twin we run is their route later. Six discovery items are still open and each blocks part of this design: PHI (C2), retention (C3), IP allowlisting (E6), the log destination (G1), Salesforce logging (G2) and spend limits (G3). C2 and C3 must close before the CCO signs; section 12 gives every owner and date.

| # | Decision | Choice | Why (discovery) | See |
|---|---|---|---|---|
| 1 | Which orgs exist | Private-equity org (the existing Enterprise org, with ZDR). Hosted Platform org with ZDR, created when the first hosted job is scheduled. No General org. No HIPAA org yet. No walled org. | A2, B1, C1, C2, F5 | [12](../../docs/compendium/12-orgs-and-ownership.md) |
| 2 | Org ownership | Primary Owner Tomasz Hadjiev; backup Owner Keiko Lindqvist; business owner Samir Castellanos; Ngozi Brandvold signs off retention and walls | B3, G4 | [12](../../docs/compendium/12-orgs-and-ownership.md) |
| 3 | The 8 Pro accounts | Announce, verify the domain, block new personal sign-ups, then domain capture; unmigrated accounts are deleted after 30 days | B1, B2 | [09](../../docs/compendium/09-plans-and-it-controls.md) |
| 4 | MNPI surfaces | Claude Code on a ZDR sign-in on managed devices, and the hosted ZDR org. Not chat, Cowork, artifacts, Claude Tag or cloud sessions | C1, C5 | [10](../../docs/compendium/10-sensitive-data.md), [14](../../docs/compendium/14-private-equity.md) |
| 5 | Web search and fetch | Off for the whole private-equity org | C5 | [14](../../docs/compendium/14-private-equity.md) |
| 6 | Chat retention | 30-day custom retention, provisional. Feedback off. | C3 | [14](../../docs/compendium/14-private-equity.md), [15](../../docs/compendium/15-governance-and-performance.md) |
| 7 | Device gate | Intune-managed devices only for sign-in to the org, through Okta device trust | D1, D2 | [13](../../docs/compendium/13-devices.md) |
| 8 | Unmanaged users | Operating partners and contractors get a hosted twin we run (later); no seat in the org until then | D2, D3 | [13](../../docs/compendium/13-devices.md) |
| 9 | Identity | Okta SSO and SCIM groups; per-user OAuth on every connector; no shared identities | C4, D1 | [09](../../docs/compendium/09-plans-and-it-controls.md), [14](../../docs/compendium/14-private-equity.md) |
| 10 | Connectors for the pilot | Salesforce Hosted MCP and the Microsoft 365 connector, reads only. HubSpot and Slack not enabled. | E1 to E5, F2 | [11](../../docs/compendium/11-connectors.md) |
| 11 | Wall | Soft wall (design B), proven by spike #30 before the pilot | C4, E4 | [14](../../docs/compendium/14-private-equity.md) |
| 12 | Autonomy | Level 1 for T1 and T2. CRM writes move to level 2 only on scorecard evidence. | F4 | [06](../../docs/compendium/06-autonomy.md) |
| 13 | Marketplace | One reviewed marketplace, `digital-twin-kit`; managed settings block all others | B3, D2 | [16](../../docs/compendium/16-oob-skills-and-references.md) |
| 14 | Deal-team plugin | Layer on Anthropic's `financial-analysis` and `private-equity` plugins, as reviewed copies. Recommendation, pending OD-1. | A2, F1 | [16](../../docs/compendium/16-oob-skills-and-references.md) |
| 15 | Governance log | Metadata only. Splunk is the candidate (G1 open); Salesforce Event Monitoring may cover the Salesforce half (G2 open). | G1, G2 | [15](../../docs/compendium/15-governance-and-performance.md) |
| 16 | Spend | IT owns tooling and spend; limits and budget set once G3 closes | G3 | [15](../../docs/compendium/15-governance-and-performance.md) |
| 17 | First hosted job | The Monday pipeline summary (T3), after the pilot, in the hosted org | F5 | [05](../../docs/compendium/05-decision-matrix.md) |

## 2. Org plan

This section applies [compendium 12](../../docs/compendium/12-orgs-and-ownership.md)'s starting plan to a firm whose staff are all private-equity users. The starting plan has three orgs (General, Private equity, Build and hosted) and adds a HIPAA org and walled orgs only when needed.

### Orgs for Example Capital Partners

| Org (compendium 12 number) | Exists? | Plan | Purpose here | Key settings |
|---|---|---|---|---|
| **Private equity** (org 2) | Yes. It is the firm's existing Claude Enterprise org (B1), with the ZDR addendum added by contract. | Claude Enterprise, ZDR | The deal-team twin and, at Scale, investor relations and other roles | ZDR on Claude Code; no Claude Tag or cloud sessions; 30-day custom retention for chat; web search and fetch off; org lock through Intune; our own audit log; SSO and SCIM through Okta |
| **Build and hosted** (org 3) | Planned. Provisioned when the first hosted job (T3) or the hosted front end for unmanaged users is scheduled, which is after the pilot. | Claude Platform, ZDR | Hosted agents: the Monday pipeline summary, and the hosted twin for operating partners and contractors | Workspaces `dev`, `staging`, `prod`; `inference_geo: us`; one deployment per wall |
| **General** (org 1) | **No.** Every role in scope is private equity and all data is internal, confidential or highly sensitive. Internal work uses the private-equity org. | None | None | None |
| **HIPAA** (org 4) | **No, not yet.** See the trigger below. | None | None | None |
| **Walled private equity** (org +N) | **No.** Soft walls (section 7). | None | None | None |

Why one General org is not needed: compendium 12 puts sales, CS and ops twins there, and none of those roles exist in this engagement (A2, A3). Claude Tag, the one General-org feature the firm might want, is unavailable under ZDR and Slack is not an input to any candidate task (E3, F2).

### The ask, quantified (from compendium 12)

| Item | Private-equity org | Hosted org (later) |
|---|---|---|
| Plan | Enterprise | Platform (usage-based) |
| Pilot seats | 6 deal-team members (of 18). The org has 40 seats today. | n/a (API usage) |
| Contract add-ons | ZDR addendum (Claude Code). CMEK not selected: nothing in discovery needs it and it turns off Claude Tag, Claude Code on the web and skill scanning. | ZDR addendum; self-hosted Managed Agents access only if we choose that route (by request) |
| Connectors | Salesforce, SharePoint, OneDrive, Teams (per-user only) | Built or wrapped servers, if a hosted job needs them |
| Technical owner and backup | Tomasz Hadjiev (Primary Owner) and Keiko Lindqvist | Same |
| Business owner | Samir Castellanos; Ngozi Brandvold signs off retention and walls | Same |

### Owners

| Role | Person | Notes |
|---|---|---|
| Primary Owner (technical owner) | Tomasz Hadjiev, Director of IT | Runs SSO, SCIM, managed settings, connectors, tooling and spend, the log pipeline and offboarding (B3, G4) |
| Backup Owner | Keiko Lindqvist, IT administrator | Second Owner, so no one person can lock everyone out. Covers publishing when the Director of IT is away. |
| Business owner | Samir Castellanos, RevOps manager | Who joins, which tasks, autonomy promotions, the scorecard |
| Retention and walls sign-off | Ngozi Brandvold, Chief Compliance Officer | C2 and C3 close before she signs |

Only Owners can manage plugins and skills; the Admin role cannot ([09](../../docs/compendium/09-plans-and-it-controls.md)). We keep the Owner count at two so that Owners, who can see across teams, stay few ([14](../../docs/compendium/14-private-equity.md)).

### Migrating the 8 Pro accounts (B1, B2)

The eight people who bought Pro plans on the company domain are on consumer terms, outside IT's control, and their data may be used for training unless they opted out. They do not use a twin or any company data until they have migrated ([09](../../docs/compendium/09-plans-and-it-controls.md)). Owner of the migration: Tomasz Hadjiev.

1. **Check seats.** Discovery does not say whether the 8 are among the 40 seats. If they are not, the org needs up to 48. Confirm the count and the contract first (OD-9).
2. **Announce.** Domain capture is one-way, and accounts not migrated within 30 days are deleted. Tell the 8 people, in writing, what happens and by when.
3. **Verify the domain** and turn on "Restrict organization creation", so no new personal accounts appear.
4. **Capture the domain** on the Enterprise plan. Each of the 8 migrates within 30 days or the account is deleted.
5. **Place each migrated user** in the right SCIM group (section 5). Remove access they should not have.
6. **Chase stragglers** at day 10 and day 20, and confirm at day 30 who migrated.

### Trigger for a HIPAA org (C2)

A HIPAA org is created only if Ngozi Brandvold rules that protected health information (PHI) from the healthcare-services portfolio company will be processed by a twin. That means a named role or task needs diligence or portfolio-monitoring files that contain PHI, and Compliance has accepted a BAA. HIPAA is permanent once on, and it turns off connectors, skills and other features, so the org is built then and not before ([10](../../docs/compendium/10-sensitive-data.md), [12](../../docs/compendium/12-orgs-and-ownership.md)). Until C2 closes, PHI is out of scope. Portfolio-company health files stay out of the twin: the managed deny rules in section 4 cover the folders IT names, and the skills say so.

## 3. Data classes and surfaces

The data classes are those from discovery C1: **internal**, **confidential** and **highly sensitive (MNPI)** for the deal team, and **confidential** (investor and fundraising contacts) for investor relations. **PHI** is out of scope today (C2 open). The table follows [compendium 10](../../docs/compendium/10-sensitive-data.md) and [14](../../docs/compendium/14-private-equity.md).

"ZDR status" is the status of the surface, not of the data: under Enterprise ZDR only Claude Code is covered, and chat, Cowork and artifacts are held to 30-day retention.

| Data class | Examples here | Allowed surfaces | ZDR status of those surfaces | Web search and fetch | Not allowed |
|---|---|---|---|---|---|
| **Internal** | Process documents, firm policies, public company information | Claude Code, claude.ai chat, Desktop, Cowork, connectors | Claude Code: ZDR. Chat and Cowork: not ZDR, 30-day retention | **Off** | Individual plans. Claude Tag and cloud sessions (off by ZDR) |
| **Confidential** (deal team: pipeline records, prior memos; investor relations: investor and fundraising contacts) | Salesforce opportunities, SharePoint memos, HubSpot contacts | Claude Code on managed devices; Cowork and chat on managed devices; vetted connectors, read-only, per-user | Claude Code: ZDR. Chat and Cowork: not ZDR, 30-day retention | **Off** | Individual plans; unvetted connectors; Claude Tag |
| **Highly sensitive (MNPI)** | Target lists, deal models, diligence notes, data-room files, anything that names a live target | **ZDR surfaces only:** Claude Code locally on a ZDR sign-in on a managed device, and a hosted agent in the ZDR Platform org (later) | **ZDR** | **Off** | Chat, Cowork, artifacts, Claude Tag, cloud sessions, Remote Control, hosted Managed Agents, API skills, code execution, Files, Batch, the API's MCP connector, web search and fetch |
| **PHI** | None today | None (out of scope until C2 closes) | n/a | **Off** | Everything, in this org |

Rules that make the table hold:

- **Web search and fetch are off for the whole private-equity org**, not only for MNPI work. Search queries and fetched sites can reveal deal intent even under ZDR, and the org cannot tell which class a given chat holds ([14](../../docs/compendium/14-private-equity.md)).
- **Highly sensitive work goes through Claude Code.** A session that touches MNPI starts in Claude Code on a ZDR sign-in. Chat and Cowork are for internal and confidential work only. The deal-team plugin tells users so.
- **Scripts return results, not records.** A skill script returns totals, IDs or pass/fail, never raw deal rows. Skills hold methods and never deal data ([10](../../docs/compendium/10-sensitive-data.md), [14](../../docs/compendium/14-private-equity.md)).
- **Model choice.** The most capable "Covered Models" tier needs 30-day retention, so ZDR roles use a model outside it. Which models qualify is a question to Anthropic ([12](../../docs/compendium/12-orgs-and-ownership.md), question 6) and it is settled before the pilot (OD-9).
- **Evals contain deal facts.** The two past briefs and sample CRM update from F3 are deal data. The skill owners redact them (targets, amounts and names replaced) before they enter the repo; the originals stay in SharePoint. Evals run only on ZDR surfaces.
- **No Claude Code with a Console API key.** It bypasses claude.ai's server-managed settings ([09](../../docs/compendium/09-plans-and-it-controls.md)). Managed settings set `forceLoginMethod` and `forceLoginOrgUUID`, and the device policy blocks other keys.

## 4. Devices

All staff laptops are managed in Microsoft Intune, and 5 operating partners and some contractors use unmanaged personal devices (D2, D3). All 6 pilot users are on managed laptops. The rules follow [compendium 13](../../docs/compendium/13-devices.md).

### Rules per data class and device

| Data class | Managed device (Intune) | Unmanaged device (operating partners, contractors) |
|---|---|---|
| **Internal** | Every surface | claude.ai web and Desktop through SSO |
| **Confidential** | Every surface, with managed settings | claude.ai web only. No Claude Code or desktop extensions. Connectors read-only. |
| **Highly sensitive (MNPI)** | Claude Code on a ZDR sign-in, locked by Intune | **No direct access.** The hosted twin instead (below). |
| **PHI** | None (out of scope) | **Blocked** |

### The sign-in gate

Compendium 13 recommends keeping unmanaged devices out of sensitive orgs. This org is the sensitive org. So:

- **Okta device trust** allows sign-in to the private-equity org only from Intune-managed devices (D1).
- **The Enterprise IP allowlist (beta)** limits the org to the corporate network or VPN. Tomasz Hadjiev supplies the egress ranges.
- **Tenant restrictions** block other Claude orgs on the corporate network, through the TLS-inspecting proxy.

With the gate on, the unmanaged column above is **moot for the org itself**: operating partners and contractors have no seat in it. The column states the rule for the hosted twin's front end and for any later decision to lift the gate, which needs Ngozi Brandvold's and Rashida Kovalenko's agreement.

### What Intune delivers to a managed device

- Force sign-in to our org (`forceLoginOrgUUID`) and a managed Claude Code settings file.
- Sandbox that fails closed, deny rules for folders IT names (including portfolio-company health folders, C2), allowed marketplaces (section 8), the governance-log hook (section 9) and `cleanupPeriodDays`.
- Desktop extensions and local MCP servers off; `/feedback` off.
- Full-disk encryption, remote wipe, and `claude purge --all --yes` on offboarding.

Owner: Tomasz Hadjiev. Rashida Kovalenko reviews the device policy.

### What unmanaged users get instead

Operating partners and contractors get a **hosted twin we run**, not direct access ([13](../../docs/compendium/13-devices.md)):

- The Agent SDK in the hosted ZDR Platform org, with a front end we build: a web page behind Okta SSO, or a Teams bot. Claude Tag cannot fill this role because ZDR turns it off.
- The device only displays results. Tools, files and credentials stay on our servers. Every connector call uses the person's own OAuth token, so the wall in section 7 still holds.
- Contractors: connectors read-only (D3). Level 1 only.
- It is out of the pilot (none of the 6 pilot users need it). It enters the backlog as a Scale item. Until it exists, operating partners and contractors have no Claude access to firm data.

This is engineering work, and it is the price of letting unmanaged devices near deal data.

## 5. Identity and access

| Topic | Design | Why (discovery) |
|---|---|---|
| Sign-in | Okta SSO. Okta device trust gates the org to managed devices (section 4). | D1 |
| Provisioning | SCIM from Okta. Groups: one for the deal team (18) and one for the pilot (6). Group names are set by Tomasz Hadjiev. Investor relations gets its own group when it joins, so plugin targeting never crosses the wall. | D1, A3, C4 |
| Owners | Two: Tomasz Hadjiev (Primary) and Keiko Lindqvist. No custom role with the Libraries permission. | B3, G4 |
| Connector identity | **Per-user OAuth only.** Each person's Salesforce, HubSpot and SharePoint permissions then apply to their twin. No service accounts, no Claude Tag integration users, no HubSpot private-app tokens. | C4 |
| Connector permissions | Owner sets each tool to Always allow, Needs approval or Blocked. Read tools: Always allow. Write tools: Blocked at level 1. | F4 |
| Projects, shared chats, artifacts | One Project per deal team, members from that team only. Sharing limited. Per-group sharing controls are unverified: we ask Anthropic ([12](../../docs/compendium/12-orgs-and-ownership.md), question 5). | C4 |
| Memory | Per user (fine). Project memory is shared with the project's members, so Projects stay per team. | C4 |
| Quarterly access review | Owners, group membership, connector scopes. Tomasz Hadjiev, with Ngozi Brandvold for retention. | G4 |
| Offboarding | SCIM removal; "Stop sharing" on anything the person shared; purge the laptop; reassign skills they owned. A removed user's connector token works until it expires, so Salesforce and Microsoft 365 sessions are revoked in those systems as well. | G4 |

Sources for the rules: [09](../../docs/compendium/09-plans-and-it-controls.md), [11](../../docs/compendium/11-connectors.md), [14](../../docs/compendium/14-private-equity.md).

## 6. Connector plan

A row per system from discovery E1 to E6. All connections are per-user and read-only in the pilot (autonomy level 1, F4). "Setup owner" is the person at the customer who does the work, as named in stakeholders.md; the partner's integration engineer, Kwame Haldorsen, works with each. Tomasz Hadjiev, as Owner, adds every connector in Claude.

| System (discovery) | Connector | Identity | Read / write | Setup owner | Verdict ([11](../../docs/compendium/11-connectors.md)) | Notes |
|---|---|---|---|---|---|---|
| **Salesforce** (E1; Enterprise Edition) | Salesforce Hosted MCP, added as a custom connector (the directory listing is not confirmed) | Per user, OAuth through an External Client App | Read in the pilot. Write tools Blocked at level 1; Needs approval from level 2 (T2). Twin writes carry a "Last updated by twin" marker. | Joaquin Lindahl (External Client App, OAuth, roles, sharing rules, the marker field) | **Use**. Build a wrapper only if compliance needs redaction or field allowlists (OD-8). | Enterprise Edition meets the stated requirement. Auth type cannot change after the connector is added, so it is fixed now as per-user OAuth. |
| **HubSpot** (E1; Marketing Hub Professional) | `mcp.hubspot.com`, as a custom connector | Per user, OAuth | Read | Imani Petrov (user permissions and teams) | **Use**, but **not added in the pilot** | No deal-team task reads HubSpot (F2), so adding it now would only open a route across the wall. Added when investor relations joins and spike #30 has passed. The HubSpot tier the MCP server needs is not stated in the compendium: Imani Petrov confirms it (OD-10). |
| **SharePoint and OneDrive** (E2) | Microsoft 365 connector (directory) | Per user, delegated (work accounts) | Read. Writes off. | Hiroshi Delacroix (Global Admin consent for the tenant, site and library permissions) | **Use** | Site and library permissions carry the wall for documents. Hiroshi Delacroix confirms the deal-team libraries are not open to investor relations. |
| **Teams** (E3) | Microsoft 365 connector (same one) | Per user, delegated | Reads chat, calendar and meeting transcripts (T2 input). Sending off. | Hiroshi Delacroix | **Use** | The hosted Monday summary (T3) will need to post to Teams. That is a send and is decided with T3, not in the pilot (OD-8). |
| **Slack Connect** (E3) | Slack connector (directory), if ever enabled. **Not added in the pilot.** | Per user, OAuth with Slack admin approval | None | Tomasz Hadjiev adds it as Owner; Slack admin approval is needed and no Slack admin is named yet | **Use**, deferred | Slack Connect channels carry outside content. No twin may both read them and post without a person approving each send. Claude Tag is unavailable under ZDR. |
| **Splunk** (G1) | **No Claude connector.** The twin has no Splunk tool. The governance-log hook writes metadata events to it. | A write-only credential for the hook; carries metadata only | Write only (from the hook) | Tomasz Hadjiev (G1 owner), with Kwame Haldorsen building the hook | **Build** the hook; destination pending G1 | Hosting (cloud or self-managed) and who may read are unknown. The hook runs on the laptop or the hosted server, not from Anthropic's IP range, so E6 does not apply to this link. |

Cross-cutting points:

- **No private-network systems** (E5). No MCP tunnel is needed.
- **IP allowlisting (E6, open).** Salesforce, HubSpot, Microsoft 365 and any wrapper we host call from Anthropic's range `160.79.104.0/21` when a claude.ai connector is used. Where a system sits behind an IP allowlist, Rashida Kovalenko adds the range, and nothing broader. This blocks the Salesforce connector if the External Client App restricts IPs, so E6 closes before connector setup.
- **Review each connector** against the compendium 11 checklist before it is added: publisher, scopes, token audience, write defaults, tool-list change watch, subprocessors, source-system audit, IP range, token life after offboarding, and no read-and-send pairing. Rashida Kovalenko signs the review.
- **Claude Code managed MCP allow and deny lists** limit Claude Code to these servers.

## 7. Wall design

**Design B, soft walls**, as decided in discovery C4 and described in [compendium 14](../../docs/compendium/14-private-equity.md). One private-equity org. The source systems enforce the wall, through per-user identity. The wall separates the **deal team** from **investor relations**.

### What a wall has to guarantee

1. People on one side cannot see the other side's data.
2. The twin cannot carry data across the wall.
3. An audit can prove both.

### How each leak route is closed

| Leak route | Control in this design |
|---|---|
| Shared-identity connectors | Per-user OAuth only. No service accounts, Claude Tag connections or HubSpot private-app tokens (section 5). |
| Salesforce | Roles and sharing rules decide what each user's twin sees. Joaquin Lindahl owns them. |
| HubSpot | User permissions and teams decide. Imani Petrov owns them. HubSpot is not connected in the pilot (section 6). |
| SharePoint | Site and library permissions. Hiroshi Delacroix owns them. |
| Skills that contain deal data | Skills hold methods, never deal data. Deal facts come from connectors at run time. |
| Projects, shared chats | One Project per deal team; sharing limited (section 5). |
| Memory | Per user; Project memory stays inside one team's Project. |
| Hosted agents | One deployment per wall, as separate workspaces in the hosted org. |
| Admins | Two Owners; reads of the governance log are themselves logged (section 9). |
| Local transcripts | Managed devices only, with purge and encryption (section 4). |

### Proof before the pilot: spike #30

Discovery E4 is answered but not confirmed: the Salesforce and HubSpot admins have not yet said that deal-team and investor-relations roles are fully separated. **Spike #30 is the proof, and it must pass before any pilot user connects.** It follows the spike template in [04 Stories](../../docs/playbook/04-stories.md) and produces `wall-test-protocol.md` (coming). In outline:

1. Joaquin Lindahl and Imani Petrov each confirm in writing that the deal-team and investor-relations roles are fully separated in their systems.
2. A test user on each side of the wall signs in to the twin and tries to read the other side's records, through Salesforce Hosted MCP and, for the test only, through HubSpot.
3. The test also tries to get the twin to carry data across: a skill, a Project or a memory that holds the other side's facts.
4. Every attempt is checked in the governance log (section 9) and in each source system's own audit.
5. Ngozi Brandvold reviews the result before she signs the walls.

The pilot does not start until the spike passes. If it fails, source-system roles are fixed and the spike is repeated.

### What would move us to a hard wall

A hard wall (design C) is a separate Claude org and a separate hosted deployment per walled team, a copy of the private-equity org with new IDs. We move to it if **any one** of these is true:

- A regulator or an LP requires provable separation.
- The firm begins public-company deals where MNPI must be walled off provably.
- Spike #30, or a later wall test, shows a leak that source-system roles cannot close.

Ngozi Brandvold makes the call. The design is built so the move is a copy and not a rebuild: one Git repo holds plugins, skills, persona and evals; managed settings, connector lists and plugin policy are kept as files; and nothing deal-specific sits in shared parts ([14](../../docs/compendium/14-private-equity.md)).

## 8. Plugins and skills

### The marketplace

The repo's `.claude-plugin/marketplace.json` publishes one marketplace, `digital-twin-kit`, with three plugins:

| Plugin | Holds | Installed for |
|---|---|---|
| `twin-shared` | Shared skills (house style, account research) | Everyone in the org |
| `twin-pe-deal-team` | The deal-team skills and the persona (output style) | The deal-team SCIM group only |
| `twin-governance` | Hooks that enforce governance, including the governance-log hook (section 9) | Everyone in the org, required |

### Managed-settings restriction to this one marketplace

Per [compendium 16](../../docs/compendium/16-oob-skills-and-references.md), "What the starter kit takes from this", decision 5: the kit runs **one reviewed customer marketplace** and blocks the rest through managed settings.

- Intune delivers a Claude Code managed settings file that allows only `digital-twin-kit` as a marketplace and forces the three plugins on. Anthropic's other marketplaces, including the community one, are blocked.
- The claude.ai plugin policy is a separate control plane and is set to match: Owners publish `digital-twin-kit`, and user-created plugin sharing is limited ([09](../../docs/compendium/09-plans-and-it-controls.md)).
- Server-managed settings alone are not a boundary, so the file comes through MDM on managed devices ([09](../../docs/compendium/09-plans-and-it-controls.md)).
- Plugins are reviewed before they enter the marketplace: skills with scripts, MCP references or network calls are the higher-risk ones ([04](../../docs/compendium/04-distribution-governance.md)). A reviewer other than the author signs each change.
- If OD-1 resolves to layering, the Anthropic plugins enter this marketplace as reviewed copies pinned to a commit. We do not add a second marketplace to the allowlist.

### First skills

| Skill | Task | Skill owner | Autonomy | Inputs | Output |
|---|---|---|---|---|---|
| **T1** Company brief | One-page company brief, about 4 per associate per week, 90 minutes each today | Callum Nwosu | Level 1: drafts. A reviewer checks every brief. | Salesforce deal record; prior memos and data-room files in SharePoint | One page for the deal team |
| **T2** Post-meeting CRM update | About 10 per person per week, 15 minutes each today | Beatriz Halloran | Level 1: the twin drafts the activity log and next-step fields; a person enters them. Write tools are Blocked. | Meeting notes or Teams transcript; the Salesforce opportunity | Draft text for the Salesforce opportunity |

Rules for both ([06](../../docs/compendium/06-autonomy.md), [03](../../docs/compendium/03-skills-authoring.md)):

- **Level 1 for every task** to start. Write tools are Blocked or left out of the plugin.
- **T2 moves to level 2 (act with approval) only on scorecard evidence**: a stable eval pass rate, a low edit rate and few rejections. Samir Castellanos promotes; Ngozi Brandvold and Rashida Kovalenko are consulted (F4). At level 2 the Salesforce write tool becomes Needs approval and every write carries the "Last updated by twin" marker.
- **Evals first.** Each skill's acceptance criteria are its evals, written from the F3 examples before the skill (F3 is open; due 2026-12-04). Yuki Sandoval, the skill engineer, builds; skill owners review.
- **Skills hold methods, never deal data.**
- Web search and fetch stay off.

T3 (the Monday pipeline summary), T4 (CIM screening), T5 (call preparation) and T6 (IC memo sections) are backlog items after T1 and T2. T3 is the first hosted job (section 12, OD-8).

### Layering on Anthropic's plugins (OD-1)

Our recommendation is to layer `twin-pe-deal-team` on Anthropic's `financial-analysis` and `private-equity` plugins from `anthropics/financial-services`, adapting them and not shipping them unchanged ([compendium 16](../../docs/compendium/16-oob-skills-and-references.md)). T1 and T2 are firm-specific (Salesforce fields, the firm's brief format), so we write them either way; layering shapes T4, T6 and the plugin's structure. It is pending partner sign-off. The review spike is done ([compendium 17](../../docs/compendium/17-anthropic-pe-plugins-review.md)). See OD-1.

## 9. Governance log and audit

One governance log for all twins, designed per [compendium 15](../../docs/compendium/15-governance-and-performance.md). What it records and how it is fixed; only the destination is open.

### What is recorded

**Metadata only, not content.** For private equity the log records that the twin read a given opportunity, not what was in it; otherwise the log would become a way around the walls. Each record holds:

- when
- who
- which twin and skill
- which tool
- which system and record IDs
- whether it was approved, and by whom
- the outcome
- tokens and cost

### Where records come from

| Source | How it reaches the log | Note |
|---|---|---|
| Local Claude Code on managed devices | A hook in `twin-governance`, set in managed settings, fires after each tool call. Users cannot remove it. | ZDR sessions are invisible to the Compliance API, so this is the only record of them |
| Hosted agents (later) | The agent's server logs each tool call | Covers unmanaged devices |
| OpenTelemetry (Claude Code, Agent SDK) | Exported through managed settings, with prompts and tool inputs left off | Adoption and cost metrics. Check the exact metric list. |
| Compliance API (chat and Cowork, which are not ZDR) | Nightly pull, metadata fields only | Does not see ZDR sessions |
| Audit logs, skills analytics | Nightly pull | Audit logs keep 180 days |
| Source-system audit | Salesforce, HubSpot, Microsoft 365 | The twin acts as the user, so its changes look like the user's. The "Last updated by twin" marker (Joaquin Lindahl) tells them apart. |

### Destination (G1, G2: open)

| Part | Candidate | Pending |
|---|---|---|
| The log itself | **Splunk**, the firm's security log system | G1: whether the log goes there, whether Splunk is cloud or self-managed, and who may read it. Owner: Tomasz Hadjiev, due 2026-12-04. The design above does not change if the answer is different. |
| Salesforce half of the audit | **Salesforce Event Monitoring** (with Field Audit Trail and Setup Audit Trail) | G2: which of these are licensed and on. Owner: Joaquin Lindahl, due 2026-11-27. If Event Monitoring is on, it may cover the Salesforce half of the log. |

### Who can read the log

Access is as tight as the deal data itself, and every read is itself recorded and reviewed ([15](../../docs/compendium/15-governance-and-performance.md)). Our proposal, pending G1:

| Reader | Sees | Why |
|---|---|---|
| Ngozi Brandvold, CCO | The raw log | Audit and wall proof |
| Rashida Kovalenko, CISO | The raw log; owns access controls on it | Security review |
| Tomasz Hadjiev, Director of IT | The raw log (he is accountable for the pipeline) | Operations |
| Samir Castellanos, RevOps manager | Scorecard aggregates only (adoption, cost per task, approve and reject rates) | Monthly scorecard |
| Everyone else, including Owners as such, partner staff and skill owners | Nothing from the raw log | Keeps the log from becoming a way around the wall |

Who else may read, and the log's retention period, are set with Ngozi Brandvold (C3).

### Review cadence

| Cadence | What | Who |
|---|---|---|
| Monthly | Twin scorecard; promote or demote autonomy | Samir Castellanos, with Tomasz Hadjiev |
| Quarterly | Access review, including who reads the log; retention review | Tomasz Hadjiev, with Ngozi Brandvold |
| Every model release | Rerun all evals before switching | Tomasz Hadjiev |
| Every skill change | Pull-request review by someone other than the author; evals pass | Skill owner and reviewer |

The scorecard's "edit rate" cannot come from the log, because the log holds no content. It comes from sampled reviews by the skill owners.

## 10. Retention

| What | Setting | Status |
|---|---|---|
| Chat, Cowork and artifacts in the private-equity org | **30-day custom retention** (the minimum). Compendium 14 option (a): accept 30 days for chat and keep MNPI on ZDR surfaces. | **Provisional.** Discovery C3 provisionally confirms the default; Compliance has not stated its requirement. |
| Claude Code and hosted agents | ZDR: Anthropic does not store inputs and outputs after responding | Needs the ZDR addendum (OD-9) |
| Compliance API records of non-ZDR sessions | The custom retention period applies, so they do not default to 6 years. Set to 30 days. | Follows C3 |
| Local transcripts on laptops | `cleanupPeriodDays` set in managed settings, at 30 days or less; purged at offboarding | Value follows C3 |
| `/feedback` | Off through managed settings | Whatever C3 decides about the 5-year exception |
| **Our governance log** | **The long-term audit record**, because Anthropic's copy is gone after 30 days | Retention period set with Ngozi Brandvold (C3, G1) |

Exceptions the CCO has not yet seen (C3): even under ZDR, content flagged for trust and safety review is kept for up to 2 years, and anything sent with `/feedback` for 5 years. Turning feedback off removes the second. We take both exceptions to Ngozi Brandvold with this document ([10](../../docs/compendium/10-sensitive-data.md), [14](../../docs/compendium/14-private-equity.md), [15](../../docs/compendium/15-governance-and-performance.md)).

## 11. Spend

IT owns tooling and spend, as discovery G3 confirms. The pilot budget and the per-user limits are not set yet (open; Marguerite Oyelaran, due 2026-12-04), so this section sets the controls, not the amounts.

| Item | Design |
|---|---|
| Owner | Tomasz Hadjiev, IT |
| Budget | Pilot budget set by Marguerite Oyelaran (G3, OD-7) |
| Per-user limits | Enterprise spend controls, per user, set once the budget is known |
| Alerts | Usage alerts on the org and on each user, at thresholds Tomasz Hadjiev proposes after G3 |
| Seats | 40 today. Up to 48 if the 8 Pro accounts are not among them (OD-9). Pilot use is 6 seats. |
| Hosted runtime (later) | Agent SDK containers run at about $0.05 per hour, plus tokens ([05](../../docs/compendium/05-decision-matrix.md)). Hosted Managed Agents are not an option under ZDR; self-hosted ones are. |
| `inference_geo: us` in the hosted org | Priced at 1.1 times the standard price ([10](../../docs/compendium/10-sensitive-data.md)) |
| Cost per task | Tokens plus runtime, on the monthly scorecard ([15](../../docs/compendium/15-governance-and-performance.md)) |

### Value baseline

From the interviews (F1), figures are the interviewees' estimates:

| Task | Frequency | Minutes each | Hours per week, per person |
|---|---|---|---|
| T1 Company brief | About 4 per associate per week | 90 | About 6, per associate |
| T2 Post-meeting CRM update | About 10 per person per week | 15 | About 2.5 |

Discovery A1 left the numeric targets for design. We set them with Samir Castellanos before the pilot starts, against these baselines (OD-11), and do not state them here, because there is no pilot data yet to set them on.

## 12. Open design decisions

### OD-1: layer or build the deal-team plugin

**Question:** is `twin-pe-deal-team` layered on Anthropic's `private-equity` and `financial-analysis` plugins from `anthropics/financial-services`, or built from scratch?

**Our recommendation: layer**, pending partner sign-off and a review spike. Why: the `private-equity` plugin already has skills for deal screening, diligence checklists, IC memos, portfolio monitoring and returns analysis, which cover T4 and T6; its outputs are drafts "staged for human sign-off", which fits level 1; and it is Apache-2.0 per GitHub ([compendium 16](../../docs/compendium/16-oob-skills-and-references.md)). What the spike must check before we depend on it:

- Every skill and connector in both plugins, read before use; none ships unchanged.
- Data flows against compendium [10](../../docs/compendium/10-sensitive-data.md) and [11](../../docs/compendium/11-connectors.md). `financial-analysis` holds all the data connectors: any third-party data connector is out for MNPI work, and any web access is off.
- No shared identities, and no skill that needs a write tool at level 1.
- The reviewed copy can be pinned in `digital-twin-kit` (section 8), with no second marketplace.

| Owner | Date |
|---|---|
| Sign-off: Eleanor Osei-Whitcombe (engagement lead). Spike: Yuki Sandoval (skill engineer), reviewed by Rashida Kovalenko | 2026-12-04, before Build starts |

**Outcome (2026-11-14): still open, pending sign-off.** The review spike is written up in [compendium 17](../../docs/compendium/17-anthropic-pe-plugins-review.md), at upstream commit `3e32c22`. It passes all four checks above and supports layering as a vendored copy in `digital-twin-kit`, with the connectors file and the web, EDGAR and mail steps removed. It keeps 19 of the 23 skills (8 as shipped, 11 changed) and skips `deal-sourcing`, `ai-readiness`, `dcf-model` and `skill-creator`. T1 and T2 take only small pieces from it. It stays open because Rashida Kovalenko has not yet reviewed the spike and Eleanor Osei-Whitcombe has not signed off.

### Open discovery items that block design

These are the open items from [discovery](discovery.md) that block this design. F3 (examples for evals) is also open, due 2026-12-04, but blocks Build and not design.

| # | Discovery item | What it blocks | Owner | Date |
|---|---|---|---|---|
| OD-2 | **C2** Is there PHI, and is there a BAA? | Whether a HIPAA org is ever needed (section 2); the CCO's sign-off | Ngozi Brandvold, CCO (Compliance / legal) | 2026-11-27 |
| OD-3 | **C3** Required retention, and the ZDR exceptions | Section 10 (retention, feedback, local transcripts, the log's retention); the CCO's sign-off | Ngozi Brandvold, CCO (Compliance / legal) | 2026-12-04 |
| OD-4 | **E6** Can Anthropic's range `160.79.104.0/21` be allowlisted? | Connector setup (section 6) | Rashida Kovalenko, CISO (Security) | 2026-11-27 |
| OD-5 | **G1** Where the governance log goes (Splunk candidate), how it is hosted and who may read it | Section 9 destination and readers | Tomasz Hadjiev, Director of IT | 2026-12-04 |
| OD-6 | **G2** Is Salesforce Event Monitoring, Field Audit Trail or Setup Audit Trail licensed and on? | Section 9: the Salesforce half of the audit | Joaquin Lindahl, Salesforce administrator | 2026-11-27 |
| OD-7 | **G3** Pilot budget and per-user spend limits | Section 11 | Marguerite Oyelaran, COO (executive sponsor) | 2026-12-04 |

Design sign-off needs C2 and C3 closed first (stakeholders.md). The other four close before the work they block starts.

### Open items found in design

| # | Item | Owner | Date |
|---|---|---|---|
| OD-8 | **Identity for the hosted Monday summary (T3).** A scheduled job has no person present, so it cannot use per-user OAuth. Decide whether it runs under a credential scoped to the deal-team role, which would be a deliberate exception to "no shared identities", and whether it may post to Teams. Until decided, T3 stays out of scope. Also: whether compliance requires a wrapper server with redaction or field allowlists for Salesforce deal data (compendium 11 "Build"). | Ngozi Brandvold and Tomasz Hadjiev; Joaquin Lindahl for the Salesforce role | Before T3 is built (after the pilot) |
| OD-9 | **Contract and capacity checks with Anthropic.** (a) The ZDR addendum can be added to the existing Enterprise org, and what ZDR covers there (compendium 12, questions 3 and 4). (b) Which models qualify for ZDR (question 6). (c) Seats: whether the 8 Pro users are among the 40. | Tomasz Hadjiev, with the Anthropic account team | 2026-12-04 |
| OD-10 | **HubSpot MCP tier.** Confirm that Marketing Hub Professional supports the server. Needed only when investor relations joins. | Imani Petrov, HubSpot administrator | Before investor relations joins |
| OD-11 | **Numeric scorecard targets** for hours saved and edit rate on T1 and T2, against the baselines in section 11 | Samir Castellanos, RevOps manager, with Marguerite Oyelaran | Before the pilot starts |
| OD-12 | **Slack administrator.** Named only if Slack is ever enabled (section 6). | Tomasz Hadjiev | When Slack is proposed |

## 13. Sign-off

This is the Phase 2 gate in the [engagement model](../../docs/playbook/01-engagement-model.md): technical and business owners approve. The prioritized backlog is signed off with this document once `backlog.md` exists.

| Role | Name | Signs for | Sections | Condition | Signature | Date |
|---|---|---|---|---|---|---|
| Approver (technical owner) | Tomasz Hadjiev, Director of IT | The design document | All; especially 2 to 6, 8, 9 and 11 | | | |
| Approver (business owner) | Samir Castellanos, RevOps manager | The design document | All; especially 1, 8, 11 and 12 | | | |
| Retention and walls | Ngozi Brandvold, Chief Compliance Officer | Retention and the walls | 3, 7 and 10 | C2 and C3 closed first; spike #30 reviewed | | |

Collected by Eleanor Osei-Whitcombe (engagement lead). Designed by Mateo Ferreira (solution architect). Marguerite Oyelaran (COO, executive sponsor) is informed and chairs steering.
