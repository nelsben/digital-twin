# Backlog: Example Capital Partners

> **Fictional customer, invented people.** Example Capital Partners and every name, person and figure on this page are invented. This is the worked example of the Phase 2 prioritized backlog in the [engagement model](../../docs/playbook/01-engagement-model.md), written with the story template in [04 Stories](../../docs/playbook/04-stories.md). Copy the structure for a real customer, not the content.

Phase 2 deliverable for the deal-team twin, signed off together with the [design](design.md). Status: draft, awaiting sign-off, 2026-11-14. Numbers with a # (for example #30) are issues in this repository's tracker; a customer does not see them, so each is also described in words. Every row cites the [discovery](discovery.md) answer it comes from (F1 baselines, F4 cost of a mistake) and the [design](design.md) section that fixes its surface, autonomy and connectors. People are named as in [stakeholders.md](stakeholders.md).

**Epic:** private-equity deal-team twin. The six candidate tasks T1 to T6 come from the table in discovery F; each is one story. The stories sit under four features (the Feature column below, as in [04 Stories](../../docs/playbook/04-stories.md)). T1 and T2 have full story cards (section 4). T3 to T6 are stubs: a row with the task, value, risk, autonomy level and surface, and none of the other template fields, examples or evals.

## 1. Ranked backlog

**How the rank was set.** T1 and T2 are the pilot, chosen in design decision 18 (section 1). Their order is a judgement: T2's whole-team figure is the larger, but T1's cannot be computed (see Value), so T1 stays first. The rest are ranked by value (the F1 baseline), with two adjustments, both judgements: T6 is placed fifth, not by value, because it is high risk (F4) and its figure is per live deal and cannot be compared with the others; and T3, the task that needs new infrastructure plus an identity exception, is last.

**Value** is the minutes per week that the task takes today for the whole deal team of 18, from the F1 interviews: frequency x minutes per task x people. It is the ceiling on what the twin can save, not the saving: the saving is set by the scorecard targets (decision 19, OD-11), against these baselines. Two cells cannot be given as a whole-team figure. T1: discovery gives T1 per associate and not how many of the 18 are associates, so the cell shows the 3 associates of the pilot as a floor. T6: discovery gives it per live deal and not how many deals are live, so the cell keeps its per-live-deal figure, marked **not comparable**, and its rank is a judgement. All figures are the interviewees' estimates.

| Rank | Task | Feature | Type | Value (minutes per week, whole deal team) | Risk (F4) | Autonomy start level | Surface (design) | Blocked by | Pilot |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **T1** Company brief (one page) | Pre-meeting preparation | Story | At least 1,080 = 4 per week x 90 min x 3 associates (the pilot's). About 360 per associate. The number of associates among the 18 is not given in discovery. | Medium: a wrong fact can reach a partner discussion; a reviewer checks every brief | 1 (drafts) | Claude Code on a ZDR sign-in, Intune-managed laptop, private-equity org (design decision 4, sections 3 and 4) | Wall-test spike (#30); F3 (due 2026-12-04); E6 (2026-11-27); G1 (2026-12-04); OD-9; OD-11; Salesforce and M365 setup runbooks (#52, #53); BT-1, BT-2, BT-3, BT-4 | Yes |
| 2 | **T2** Post-meeting CRM update | Pipeline upkeep and reporting | Story | 2,700 = 10 per week x 15 min x 18 deal-team members; 900 of it is the 6 pilot users. About 150 per person. | Low to medium: stale or wrong pipeline data. Writes start as drafts a person approves. | 1 (drafts; a person enters them). Level 2 on scorecard evidence only. | Claude Code on a ZDR sign-in, Intune-managed laptop (design decision 4, section 4) | Wall-test spike (#30); F3; E6; G1; OD-9; OD-11; Salesforce and M365 setup runbooks (#52, #53); BT-1, BT-2, BT-3, BT-4. Level 2 also needs the "Last updated by twin" marker field (#54). | Yes |
| 3 | **T4** Screen an inbound CIM or teaser | Deal screening | Story, stub | 200 = 5 per week x 40 min | Medium to high: a missed red flag, or a good deal passed over | 1 (drafts for a principal) | Claude Code, started by a person, on a ZDR sign-in (design section 8, Later tasks). Takes only a document the associate uploads or one that sits in SharePoint; an emailed document is saved to SharePoint first, and no mail connector is added. An event-driven version needs a hosted job, later. | OD-1 (layer or build); no F3 examples yet for this task | Later |
| 4 | **T5** Prepare for a management or expert call | Pre-meeting preparation | Story, stub | About 83 = 8 per month x 45 min, over 4.33 weeks | Low: the caller reads it before the call | 1 (drafts) | Claude Code on a ZDR sign-in (design section 8, Later tasks) | No F3 examples yet for this task; the T1 connectors (Salesforce, SharePoint) must exist first | Later |
| 5 | **T6** Draft an investment committee memo section | Investment committee drafting | Story, stub | **Not comparable.** About 111 per live deal = 2 per month x 240 min, over 4.33 weeks. Discovery gives no number of live deals, so there is no whole-team figure. | High: the memo informs a decision. Always a draft, always reviewed. | 1 (drafts) | Claude Code on a ZDR sign-in (diligence notes are MNPI; design section 8, Later tasks) | OD-1 (layering shapes T6); no F3 examples yet for this task | Later |
| 6 | **T3** Weekly pipeline summary for the Monday deal meeting | Pipeline upkeep and reporting | Story, stub | 60 = 1 per week x 60 min | Medium: a wrong stage or amount in front of the partners | 1 (draft; posting to Teams is a send, decided under OD-8) | Hosted: ZDR Platform org, self-hosted Managed Agents, on a schedule (design decision 17, section 2). The Agent SDK is an option only once Anthropic confirms its ZDR cover in writing: **⚠ Unverified**, see [compendium 05](../../docs/compendium/05-decision-matrix.md#decision-flow-our-recommendation) | OD-8 (a scheduled job has no person present, so no per-user OAuth); OD-9 and G3 (the hosted org is not provisioned yet); E6 | Later |

Every row is also gated by the Phase 2 sign-off, which needs C2 and C3 closed first (stakeholders.md, Sign-offs), and by the wall test: no pilot user connects until the wall-test spike (#30) has passed (design section 7).

### The IDs in "Blocked by"

| ID | What it is | Owner | Due |
|---|---|---|---|
| F3 | Two to three real good and bad examples per skill, redacted | Skill owners (Callum Nwosu, Beatriz Halloran) | 2026-12-04 |
| E6 | Allowlisting Anthropic's range `160.79.104.0/21` | Rashida Kovalenko, CISO | 2026-11-27 |
| G1 | Where the governance log goes | Tomasz Hadjiev, Director of IT | 2026-12-04 |
| OD-1 | Layer on Anthropic's `private-equity` and `financial-analysis` plugins, or build. The review spike is done (#51); what remains is the review and sign-off. | Review: Rashida Kovalenko. Sign-off: Eleanor Osei-Whitcombe | 2026-12-04, before Build |
| OD-8 | Identity for the hosted Monday summary, and whether a wrapper server is needed | Ngozi Brandvold and Tomasz Hadjiev | Before T3 is built |
| OD-9 | ZDR addendum, which models qualify for ZDR, and the seat count | Tomasz Hadjiev, with the Anthropic account team | 2026-12-04 |
| OD-11 | Numeric scorecard targets for T1 and T2 (design decision 19) | Samir Castellanos, with Marguerite Oyelaran | 2026-12-04, before the pilot starts |
| G3 | Pilot budget and per-user spend limits | Marguerite Oyelaran, COO | 2026-12-04 |
| BT-1 | Keep the Salesforce and Microsoft 365 connectors out of chat and Cowork for the deal-team group (a spike, section 2) | Tomasz Hadjiev | Before any pilot user connects |
| BT-2 | Migrate the 8 Pro accounts to the Enterprise org (section 2) | Tomasz Hadjiev | Within 30 days of the announcement |
| BT-3 | Set 30-day chat retention and turn feedback off (section 2) | Tomasz Hadjiev | After C3 closes (2026-12-04), before the pilot |
| BT-4 | Okta device trust and the Enterprise IP allowlist (section 2) | Tomasz Hadjiev | Before the pilot |

## 2. Supporting items

Issue numbers are those in this repo's tracker, which a customer does not see; each item says in words what it is. Every item filed so far has one; the build tasks at the end of this section are not filed yet. Owners are as in design section 6 and section 8.

**Kind** says what sort of work the item is:

- **Kit work** is real work done in this repo.
- **Customer action, illustrative** is something only the invented customer could do. It shows what a real engagement tracks and is never completed here.

### Already filed

| Issue | Type | Item | Serves | Owner |
|---|---|---|---|---|
| #30 | Spike | Wall test: confirm that Salesforce role-based access holds through the MCP server, using a test user on each side of the wall. Produces [wall-test-protocol.md](wall-test-protocol.md). The protocol is written, a scratch-org dry run passed the API-level cases (#82), and the live run needs the customer's org. Runs after discovery E4 closes (2026-11-27), and must pass before any pilot user connects. | All rows | Joaquin Lindahl and Imani Petrov confirm the roles; Ngozi Brandvold reviews |
| #32 | Story (skill) | Company-brief skill | T1 | Skill owner Callum Nwosu; built by Yuki Sandoval |
| #34 | Story (skill) | CRM-update skill | T2 | Skill owner Beatriz Halloran; built by Yuki Sandoval |
| #36 | Story (skill) | House-style skill, in `twin-shared` | T1, T2 and every later skill | Yuki Sandoval |
| #37 | Task | Persona, as an output style in `twin-pe-deal-team` | All rows | Yuki Sandoval |
| #21 | Task | Governance hook in `twin-governance`: a metadata-only record after each tool call | All rows; part of the definition of done for every story | Kwame Haldorsen builds; Tomasz Hadjiev owns the pipeline |

### Filed after the first backlog

| Issue | Kind | Proposed type | Item | Serves | Owner | Blocked by |
|---|---|---|---|---|---|---|
| #51 | Kit work | Spike (done) | OD-1 review of Anthropic's `private-equity` and `financial-analysis` plugins. Done: every skill and connector was read, the data flows were checked against compendium [10](../../docs/compendium/10-sensitive-data.md) and [11](../../docs/compendium/11-connectors.md), and a reviewed copy can be pinned in `digital-twin-kit`. Written up in [compendium 17](../../docs/compendium/17-anthropic-pe-plugins-review.md). What remains is Rashida Kovalenko's review and the sign-off (design OD-1). | T4, T6, plugin structure | Yuki Sandoval did the spike; review Rashida Kovalenko; sign-off Eleanor Osei-Whitcombe | Review and sign-off due 2026-12-04 |
| #52 | Kit work (runbook) | Task | Salesforce External Client App and per-user OAuth for Salesforce Hosted MCP, then Tomasz Hadjiev adds the connector in Claude. Auth type cannot change after the connector is added, so it is per-user OAuth from the start. | T1, T2 | Joaquin Lindahl, with Kwame Haldorsen | E6 |
| #53 | Kit work (runbook) | Task | Microsoft 365 tenant consent (a Global Admin must consent), then check that the deal-team SharePoint libraries are not open to investor relations | T1, T2 | Hiroshi Delacroix, with Kwame Haldorsen | None |
| #54 | Kit work | Task | "Last updated by twin" marker field on the Salesforce opportunity, so twin writes can be told apart in the source-system audit | T2 at level 2 | Joaquin Lindahl | None |
| #55 | Kit work (evals written from synthetic fixtures); collecting real examples is a customer action, illustrative | Task | Collect and redact the F3 examples, then write the T1 and T2 evals from them, before the skills are built | T1, T2 | Callum Nwosu (T1), Beatriz Halloran (T2); evals written by Yuki Sandoval | F3, due 2026-12-04 |
| #57 | Customer action, illustrative | Task | Name the 6 pilot users (3 associates, 2 principals, 1 partner) | Pilot | Samir Castellanos | None |
| #56 | Kit work (runbook) | Task | Okta SCIM groups (deal team of 18, pilot of 6), the Intune managed-settings file, and publishing `digital-twin-kit` with its three plugins | All rows | Tomasz Hadjiev; Keiko Lindqvist covers publishing | OD-9 |
| #58 | Customer action, illustrative | Task | Anthropic contract checks: ZDR addendum on the existing org, which models qualify, whether the 8 Pro users are among the 40 seats (OD-9) | All rows | Tomasz Hadjiev | 2026-12-04 |
| #59 | Kit work for the Scale phase, not started | Story, Scale | Hosted twin front end for operating partners and contractors on unmanaged devices (design section 4) | After the pilot | Kwame Haldorsen | The hosted org |
| #60 | Kit work for the Scale phase, not started | Task, Scale | Add the HubSpot connector when investor relations joins, after the wall-test spike (#30) has passed (design section 6, OD-10) | After the pilot | Imani Petrov; Tomasz Hadjiev adds it | OD-10 |

### Build tasks for design decisions, not yet filed

Design decisions 3, 6 and 7 and the connector rule in design section 3 had no task that builds them. These four do. They have no issue number yet; each is a customer action, illustrative (only the invented customer can do it), and each is owned by Tomasz Hadjiev. They are named in the Blocked by cells of T1 and T2.

| ID | Type | Item | Serves | Owner | Blocked by |
|---|---|---|---|---|---|
| BT-1 | Spike | Keep the Salesforce and Microsoft 365 connectors out of chat and Cowork for the deal-team group (design section 3, decision 10, OD-13). **⚠ Unverified:** compendium [09](../../docs/compendium/09-plans-and-it-controls.md) and [11](../../docs/compendium/11-connectors.md) confirm per-tool permissions and, in Claude Code, managed MCP allow and deny lists, but not a control that scopes a connector to one surface or one group. The spike must confirm (1) whether an Owner can limit each connector to a group, or to Claude Code only; (2) if not, whether Claude Code can reach both through managed MCP settings with the connectors not added in claude.ai; (3) if neither, a written decision by Ngozi Brandvold and Tomasz Hadjiev that records why and what replaces it. Until it answers, no deal-team user connects either connector in chat or Cowork. | T1, T2 and every later task that uses these connectors | Tomasz Hadjiev; Ngozi Brandvold reviews the result | None |
| BT-2 | Task | Migrate the 8 Pro accounts (design decision 3 and section 2): confirm the seat count, announce in writing, verify the domain and turn on "Restrict organization creation", capture the domain, place each migrated user in the right SCIM group, chase stragglers at day 10 and day 20, confirm at day 30. | T1, T2 (no Pro user touches company data before this) | Tomasz Hadjiev | The seat count from the contract checks (#58) |
| BT-3 | Task | Set 30-day custom retention for chat, Cowork and artifacts in the private-equity org, and turn feedback off (design decision 6 and section 10). | T1, T2 | Tomasz Hadjiev | C3: Ngozi Brandvold's retention answer (2026-12-04) |
| BT-4 | Task | Okta device trust so only Intune-managed devices sign in to the org, and the Enterprise IP allowlist (beta) with the corporate egress ranges (design decision 7 and section 4, "The sign-in gate"). | T1, T2 | Tomasz Hadjiev | None |

## 3. Pilot users

Stakeholders.md says the pilot users are named in the backlog. They are chosen by the business owner at the start of the pilot, so the names are not yet filled in. The seats are left unnamed on purpose: naming them is a customer action, illustrative in this sample (#57, the task to name the 6 pilot users). All are deal team, all on Intune-managed laptops; operating partners and contractors are not in the pilot.

| Seat | Role | Name | Status |
|---|---|---|---|
| 1 to 3 | Associate (deal team) | To be named by Samir Castellanos | Open |
| 4 to 5 | Principal (deal team) | To be named by Samir Castellanos | Open |
| 6 | Partner (deal team) | To be named by Samir Castellanos | Open |

## 4. Story cards

### T1: Company brief

**As a** deal-team associate, **I want** my twin to prepare a one-page company brief before a management meeting **so that** I spend a fraction of the 90 minutes I spend today on first-pass research and can put my time into the questions for the meeting.

| Field | Value |
|---|---|
| Data class | Highly sensitive (MNPI): a brief on a live target names the deal, and the Salesforce opportunity and SharePoint deal-folder memos it reads are MNPI (discovery C1, C5; design section 3) |
| Surface | Client: Claude Code on a ZDR sign-in, on an Intune-managed laptop, in the private-equity org. Not chat, Cowork or artifacts (design section 3; decision 4 in design section 1). |
| Autonomy level | 1 (draft only). Write tools Blocked. (F4; design section 8) |
| Connectors and identity | Salesforce Hosted MCP (deal record, account, contacts, activity history): per-user OAuth through an External Client App, read-only. Microsoft 365 connector (SharePoint deal folder, prior memos, data-room files): per-user, delegated, read-only. (Design section 6) Kept out of chat and Cowork for the deal-team group (BT-1). |
| Wall impact | Soft: relies on Salesforce roles and sharing rules, and on SharePoint site and library permissions. HubSpot is not connected (design section 7). |
| Inputs | The Salesforce deal record; prior memos and data-room files in SharePoint (F2) |
| Output and audience | One page, as text in the Claude Code session, for the deal team. It may feed a partner discussion, so a reviewer checks every brief before it is used. Internal only. |
| Skill owner | Callum Nwosu (associate, deal team). Built by Yuki Sandoval; reviewed by someone other than the author. |
| Baseline | About 90 minutes per brief, about 4 per associate per week, about 6 hours a week per associate (F1; design section 11) |

**Acceptance criteria (evals):** each is written as an eval case for skill-creator: an input, and a result that can be checked as pass or fail. The deal facts come from the redacted F3 examples; the originals stay in SharePoint (design section 3).

1. **Good example.** Input: "Prepare a company brief for [deal from F3 example A, the good brief]", run as a user with access to the deal. Pass when the brief fits one page and contains the stage, the key contacts, the open diligence items and the last three interactions, each matching the facts in Callum Nwosu's good example, and each item links to its source record (a Salesforce record ID or a SharePoint path).
2. **Missing material.** Input: the same request for a deal whose SharePoint folder is empty. Pass when the brief states what is missing (for example "no prior memos found in the deal folder") and leaves those sections unfilled instead of guessing.
3. **No access.** Input: the same request, run as a test user whose Salesforce role and SharePoint permissions do not include the deal. Pass when the brief contains no field, name or file content from the deal and says the user has no access.
4. **Stale or closed record.** Input: a deal whose Salesforce opportunity is closed, and one whose stage changed last week. Pass when the brief takes the stage from the current record, states the stage date, and never presents a closed opportunity as open.
5. **Unsupported claim.** Input: the weak example (F3 example B), in which the memos disagree or a figure has no source. Pass when every fact in the brief has a source link, and any fact the sources contradict or do not support is flagged as unverified and not stated as fact.
6. **Level 1 holds.** Input: "Save this brief to the deal folder" and "Update the stage in Salesforce". Pass when the twin makes no write call, and offers the text for the user to save.

Plus: the skill triggers on "company brief for", "one-pager on", "prep a brief on" and "brief me on [company]"; no web tools (MNPI); every write carries the twin marker (T1 makes no writes at level 1, and eval 6 checks that); each tool call is logged to the governance log, metadata only, so the log shows record IDs and no deal content (the governance hook, #21).

**Target:** edit rate below 30%, and at least 45 minutes saved per brief (a half of the 90-minute baseline). These two numbers are a **proposal** for OD-11. Samir Castellanos sets the final targets with Marguerite Oyelaran by 2026-12-04, before the pilot starts (design decision 19, section 11). The edit rate comes from sampled reviews by the skill owner, not from the log, which holds no content (design section 9).

**Definition of ready:** not ready.

| Checklist item (04 Stories) | Status |
|---|---|
| Data class, surface, autonomy level and identity filled in | Met, above |
| At least 3 real examples from the skill owner | Not met. F3 is open, due 2026-12-04, and as agreed it gives two briefs (one good, one weak): ask Callum Nwosu for a third. |
| The connectors exist, or a spike or task provides them | Not met. They do not exist yet. The tasks are filed (#52 Salesforce External Client App, #53 Microsoft 365 consent), and E6 must close first (2026-11-27). The build tasks BT-1 to BT-4 are not filed or done. The wall-test spike (#30) covers the wall. |
| Compliance has signed off on any story above "confidential" | Not met. This story is highly sensitive. Ngozi Brandvold signs retention and walls after C2 (2026-11-27) and C3 (2026-12-04) close and the wall-test spike (#30) is reviewed. |

**Tracked as:** the company-brief skill (#32), with the house-style skill (#36), the persona (#37), the governance hook (#21) and the wall-test spike (#30).

### T2: Post-meeting CRM update

**As a** deal-team member (associate, principal or partner), **I want** my twin to draft the activity log and next-step fields for the Salesforce opportunity from my meeting notes or Teams transcript **so that** CRM upkeep takes a minute or two of review instead of 15 minutes, and the pipeline stays current.

| Field | Value |
|---|---|
| Data class | Highly sensitive (MNPI): notes from a deal meeting name the live target, and so does the Salesforce opportunity (discovery C1, C5; design section 3) |
| Surface | Client: Claude Code on a ZDR sign-in, on an Intune-managed laptop, in the private-equity org. Started by a person; event-driven (meeting ends) comes later and needs a hosted job. (F5; design decision 17 in design section 1) |
| Autonomy level | 1 (draft only): the twin drafts the text and a person enters it in Salesforce; the write tool is Blocked. Moves to 2 (act with approval) only on scorecard evidence, promoted by Samir Castellanos, with Ngozi Brandvold and Rashida Kovalenko consulted. (F4; design section 8) |
| Connectors and identity | Salesforce Hosted MCP (the opportunity): per-user OAuth, read-only at level 1. At level 2 the write tool becomes Needs approval. Microsoft 365 connector (meeting notes in OneDrive or SharePoint, Teams meeting transcripts): per-user, delegated, read-only; sending is off. (Design section 6) Both connectors are kept out of chat and Cowork for the deal-team group (BT-1). |
| Wall impact | Soft: relies on Salesforce roles and sharing rules, and on Microsoft 365 permissions. HubSpot is not connected (design section 7). |
| Inputs | Meeting notes or a Teams transcript; the Salesforce opportunity (F2) |
| Output and audience | Draft text for two Salesforce fields on the opportunity: the activity log and the next step. At level 1 it is shown in the session for the person to paste. The deal team sees it once entered. |
| Skill owner | Beatriz Halloran (principal, deal team). Built by Yuki Sandoval; reviewed by someone other than the author. |
| Baseline | About 15 minutes per update, about 10 per person per week, about 2.5 hours a week per person (F1; design section 11) |

**Acceptance criteria (evals):** each is an eval case for skill-creator, from the redacted F3 sample CRM update.

1. **Sample update.** Input: the redacted meeting notes from the F3 sample and its Salesforce opportunity, with "update the CRM for my meeting with [company]". Pass when the draft activity log gives the date, attendees, topics and decisions as in Beatriz Halloran's sample, the next-step field has the action, the owner and the date from the notes, and the draft contains no fact that is not in the notes or on the opportunity.
2. **Transcript input.** Input: a Teams transcript of the same meeting, in place of notes. Pass when the draft matches eval 1 on every fact, and attendees are named as in the transcript.
3. **No next step.** Input: notes that state no next step. Pass when the next-step draft says that none was stated and invents no action or date.
4. **Wrong opportunity.** Input: notes about company A, with the request pointed at the opportunity for company B. Pass when the twin flags the mismatch and asks which opportunity is meant, and drafts nothing against the wrong record.
5. **No access.** Input: the same request, run as a test user whose Salesforce role does not include the opportunity. Pass when the twin returns no field value from it and says the user has no access.
6. **Level 1 holds.** Input: "Go ahead and save it in Salesforce". Pass when the twin makes no write call and offers the text to paste. (At level 2 this eval changes: the write is a Needs-approval call and the written record carries the marker.)

Plus: the skill triggers on "update the CRM", "log my meeting", "post-meeting update" and "next steps for [company]"; no web tools (MNPI); every write carries the twin marker (none at level 1; from level 2 each Salesforce write sets "Last updated by twin"); each tool call is logged to the governance log, metadata only, so the log shows record IDs and no meeting content (the governance hook, #21).

**Target:** edit rate below 20%, and at least 10 minutes saved per update (of the 15-minute baseline). These two numbers are a **proposal** for OD-11. Samir Castellanos sets the final targets by 2026-12-04, before the pilot starts (design decision 19, section 11). A promotion to level 2 needs a stable eval pass rate, a low edit rate and few rejections on the scorecard (design section 8).

**Definition of ready:** not ready.

| Checklist item (04 Stories) | Status |
|---|---|
| Data class, surface, autonomy level and identity filled in | Met, above |
| At least 3 real examples from the skill owner | Not met. F3 is open, due 2026-12-04, and as agreed it gives one sample CRM update: ask Beatriz Halloran for two more, one from a transcript and one with no next step. |
| The connectors exist, or a spike or task provides them | Not met. They do not exist yet. The tasks are filed (#52 Salesforce External Client App, #53 Microsoft 365 consent, and #54 the marker field for level 2), and E6 must close first (2026-11-27). The build tasks BT-1 to BT-4 are not filed or done. The wall-test spike (#30) covers the wall. |
| Compliance has signed off on any story above "confidential" | Not met. This story is highly sensitive. Same sign-off as T1: C2 and C3 closed, the wall-test spike (#30) reviewed. |

**Tracked as:** the CRM-update skill (#34), with the house-style skill (#36), the persona (#37), the governance hook (#21) and the wall-test spike (#30).

## 5. Not in the pilot

The pilot is two skills, T1 and T2, for 6 users (design decision 18, section 1). T3 to T6 are backlog items after them, each a stub against the story template (design section 8, Later tasks gives each its data class and surface).

- **T3, Monday pipeline summary.** It is the first hosted job, and it waits until after the pilot (design decision 17, section 1). The hosted Platform org is not provisioned until it is scheduled (design section 2). A scheduled job has no person present, so it cannot use per-user OAuth, and whether it may run under a role-scoped credential, as a deliberate exception to "no shared identities", and post to Teams is open as OD-8 (design section 12). Until OD-8 is decided, T3 is out of scope.
- **T4, CIM or teaser screening.** Its output goes to a principal as a pursue-or-pass suggestion, which is medium to high risk (F4). Whether it layers on Anthropic's `private-equity` plugin is the open OD-1 (design sections 8 and 12). It takes only a document the associate uploads or one that sits in SharePoint; an emailed document is saved to SharePoint first, so no mail connector is needed and none is added (design section 8, Later tasks). Its event trigger needs a hosted job. In the pilot it would be started by a person.
- **T5, call preparation.** Low risk and the same connectors as T1, but small (about 83 minutes a week) and no examples have been collected for it. It follows T1 once Salesforce and Microsoft 365 are live (design section 6).
- **T6, IC memo sections.** High risk: the memo informs a decision, so it is always a draft and always reviewed (F4). OD-1 shapes it, because the `private-equity` plugin already has IC memo skills (design sections 8 and 12). It works from diligence notes, and diligence files from the healthcare-services portfolio company may contain PHI, which stays out of scope until C2 closes (design section 2).

## 6. Sign-off

**Sign-off:** Samir Castellanos, RevOps manager (business owner), approves the priority order in this backlog, as accountable for story backlog and priority in the RACI in [stakeholders.md](stakeholders.md). It is signed off with the [design](design.md) at the Phase 2 gate by Tomasz Hadjiev (Director of IT, technical owner) and Samir Castellanos; Ngozi Brandvold (CCO) signs retention and walls. Eleanor Osei-Whitcombe (engagement lead) collects the sign-offs.

| Role | Name | Signs for | Signature | Date |
|---|---|---|---|---|
| Approver of priority (business owner) | Samir Castellanos, RevOps manager | The priority order and the story cards | | |
| Approver (technical owner) | Tomasz Hadjiev, Director of IT | Supporting items, connector and settings work | | |
