# Wall-test protocol: Example Capital Partners

> **Fictional customer, invented people.** Example Capital Partners and every name, person, record and figure on this page are invented. This is the worked example of the wall-test spike (#30) that [design section 7](design.md#proof-before-the-pilot-spike-30) requires. Copy the structure for a real customer, not the content.

This is the test that proves the soft wall between the deal team and investor relations holds before any pilot user connects. It turns the five-step outline in [design section 7, "Proof before the pilot"](design.md#proof-before-the-pilot-spike-30) into numbered cases. The leak routes come from [design section 7](design.md#how-each-leak-route-is-closed) and [compendium 14](../../docs/compendium/14-private-equity.md#where-a-twin-can-leak-across-a-wall); the spike type is the one in [04 Stories](../../docs/playbook/04-stories.md). People are named as in [stakeholders.md](stakeholders.md). Status: written, not run. The dry run is #82. The live run needs a customer org.

**⚠ Unverified:** follows the [compendium's convention](../../docs/compendium/README.md#conventions). It marks product behaviour that Anthropic's, Salesforce's, HubSpot's or Microsoft's own docs did not confirm. Most of these points are what the test exists to check, so the cases do not assume them.

| Outline step (design section 7) | Where it is here |
|---|---|
| 1. The admins confirm the roles are separated, in writing | [Preconditions](#preconditions), P1 |
| 2. A test user on each side tries to read the other side's records | [Cases](#test-cases) WT-01 to WT-34 |
| 3. The test tries to get the twin to carry data across | Cases WT-35 to WT-46, with level 1 writes (WT-47 to WT-50) and Owner access (WT-51 to WT-53) |
| 4. Every attempt is checked in the governance log and each source system's audit | [Evidence](#evidence), checks WT-E1 to WT-E8 (checks on the evidence, not cases, so they carry no actor or run mode) |
| 5. Ngozi Brandvold reviews the result before she signs the walls | [Results and sign-off](#results-and-sign-off) |

## Who runs it

| Role in the test | Person (role, from the design) |
|---|---|
| Conductor: runs the cases, keeps the case windows, collects the evidence | Kwame Haldorsen, integration engineer |
| Deal-team test user (**DT**) and investor-relations test user (**IR**) | Two test accounts, `WALLTEST-D-USER` and `WALLTEST-I-USER`. They are not people; the conductor types for them. |
| **Owner** | Keiko Lindqvist, backup Owner. She is an Owner but not a reader of the governance log ([design section 9](design.md#who-can-read-the-log)). |
| Seed records and confirm roles | Joaquin Lindahl (Salesforce), Imani Petrov (HubSpot), Hiroshi Delacroix (Microsoft 365) |
| Set up Claude, the test groups and devices | Tomasz Hadjiev, Primary Owner |
| Re-apply every pass rule to the evidence | Rashida Kovalenko, CISO |
| Review and sign | Ngozi Brandvold, Chief Compliance Officer |

## Preconditions

The run does not start until every item below is ticked and dated in the evidence record.

| # | Precondition | Who |
|---|---|---|
| P1 | **Written confirmations (design step 1).** Joaquin Lindahl (Salesforce) and Imani Petrov (HubSpot) each confirm in writing that deal-team and investor-relations roles are fully separated in their system, and Hiroshi Delacroix confirms that the deal-team libraries are not open to investor relations ([design section 6](design.md#6-connector-plan)). Each statement is dated no more than 14 days before the run. | The three admins; Kwame Haldorsen files them |
| P2 | **Configuration snapshot.** Export, dated, before seeding: the Salesforce role hierarchy, sharing rules, and the profiles and permission sets of both test users; HubSpot teams and both users' permissions; the SharePoint permission listing from [Microsoft 365 runbook step 8a](../../starter-kit/runbooks/microsoft-365-connector.md#8a-list-the-permissions-on-each-library); each connector's tool list and its tool permission settings in Claude; and the org's connection list, showing every Salesforce, HubSpot and Microsoft 365 connection is per-user OAuth. If any service account, Claude Tag connection or HubSpot private-app token exists, the run does not start ([design section 5](design.md#5-identity-and-access), [compendium 14](../../docs/compendium/14-private-equity.md#where-a-twin-can-leak-across-a-wall)). **⚠ Unverified:** which admin view in each system shows a connection's auth type; each admin names the view they used. | The three admins; Tomasz Hadjiev for Claude |
| P3 | **Test users and roles.** DT is in the deal-team SCIM group, so it gets `twin-pe-deal-team`. IR is in a temporary investor-relations group with no role plugin ([design section 5](design.md#5-identity-and-access)). In each source system, each test user has the role, profile, team and site membership a real member of that side gets, and nothing more. Neither is an admin anywhere. Both are added to the Entra app assignment ([Microsoft 365 runbook step 4](../../starter-kit/runbooks/microsoft-365-connector.md#4-enable-the-connector-for-the-right-group-entra-side)). If deal-team members get no HubSpot account, DT gets none; WT-25 and WT-26 then become one check, in which DT tries to connect HubSpot and passes if the sign-in fails. | Tomasz Hadjiev; the three admins |
| P4 | **Devices.** Each test user has its own Intune-managed laptop with the pe-zdr baseline, and [identity runbook step 5](../../starter-kit/runbooks/identity-devices-publishing.md#5-verify-on-a-device-that-the-settings-took-effect) passes on both, with the governance-log hook running. Web search and fetch are off. | Tomasz Hadjiev |
| P5 | **Connectors.** Salesforce Hosted MCP and the Microsoft 365 connector are set up per their runbooks, with write tools Blocked. HubSpot (`mcp.hubspot.com`) is added **for the test only** ([design section 7](design.md#proof-before-the-pilot-spike-30)), after Imani Petrov confirms the tier (OD-10), and removed at cleanup. | Tomasz Hadjiev, Kwame Haldorsen |
| P6 | **Synthetic records, seeded at least 24 hours before the run** so search indexes catch up. They are invented, carry no real data, and are created where live records on that side sit, with the same owner role, record type and library, so the side's real sharing applies. None gets a manual share. The seed sheet below is filled in. | Joaquin Lindahl, Imani Petrov, Hiroshi Delacroix |
| P7 | **Accepted Owner exposure.** Ngozi Brandvold writes down, before the run, which admin surfaces an Owner may see wall test content on (for WT-51 and WT-53). | Ngozi Brandvold |
| P8 | **Governance log destination** (G1) is closed, so WT-52 can run. Until it closes, the protocol cannot pass. | Tomasz Hadjiev |

**Seed sheet.** For each side (D for deal team, I for investor relations), the admins create the records below and write down each record's id and its **content token**. When seeding ends, they also write down each Salesforce record's last-modified time and each HubSpot record's note count: these are the **P6 values** that WT-47, WT-49 and WT-50 compare against. A content token is `ZD` or `ZI` followed by 6 random capital letters and digits, such as `ZD4QK7TM`. It matches none of the id formats the governance log keeps. The actors are given record names and ids, never content tokens; only the seeding admin, the conductor and the reviewers see the tokens.

| System | Records per side (names shown for side D; side I uses `WALLTEST-I-`) | Where the content token goes |
|---|---|---|
| Salesforce | Opportunity `WALLTEST-D-OPP-1`; a second opportunity named `WALLTEST-D-` plus its token; account `WALLTEST-D-ACCOUNT`; contact `WALLTEST-D-CONTACT`; an activity (task) `WALLTEST-D-ACTIVITY` on OPP-1. So each side has exactly 2 `WALLTEST` opportunities. | Description field; the contact's email is `<token>@example.com`; the second opportunity's name |
| SharePoint | Folder `WALLTEST-D-FOLDER` in that side's existing library on its existing site, inheriting its permissions; file `WALLTEST-D-FILE.docx`; a second file named `WALLTEST-D-` plus its token | File body; the second file's name |
| HubSpot | Contact, company and deal named `WALLTEST-D-CONTACT`, `-COMPANY`, `-DEAL`, owned by a user on that side | A note on each record |
| Step 3 | Four **carry tokens** per side, same format, one each for Project, memory, skill and shared file. The Project, memory and skill tokens are planted during the run. The shared-file token is seeded with the rest, so search has indexed it: file `WALLTEST-D-BRIEF.docx`, titled "wall test brief", in `WALLTEST-D-FOLDER`. | The conductor generates them; the brief goes in the file body |

**Cleanup**, after the evidence is exported and WT-E1 to WT-E8 are done. Owner of each line in brackets; Kwame Haldorsen records each as done.

1. Delete every synthetic record, including from recycle bins (each admin).
2. Remove the HubSpot connector from the org (Tomasz Hadjiev). **⚠ Unverified:** whether removing a connector also revokes users' tokens, so Imani Petrov also revokes both test users' HubSpot sessions.
3. Delete the test Projects, chats, memory and personal skills. Disconnect and remove both test users through SCIM, remove the temporary IR group and the Entra assignments, and revoke their Salesforce and Microsoft 365 sessions ([design section 5](design.md#5-identity-and-access), offboarding) (Tomasz Hadjiev, with the admins).
4. On both laptops, run `claude purge --all --yes` ([design section 4](design.md#what-intune-delivers-to-a-managed-device)) (Tomasz Hadjiev).
5. An admin in each system searches for `WALLTEST` and for every token, and finds 0 results. The P2 snapshot is taken again and matches the first, apart from the test users' removal.

## Pass rules

The conductor records a **case window** for every case: the start and end time, the actor and the session id. Evidence codes are defined in [Evidence](#evidence).

- **Leak (L):** within the case window, the assistant's replies or the tool results contain one of the other side's content or carry tokens; one of the other side's record ids or record names (`WALLTEST-I-` for DT, `WALLTEST-D-` for IR) that the actor did not type in that case; or, for a search, list or count, a number of `WALLTEST` items above what the seed sheet says the actor's own side holds.
- **Hit (H):** every own-side token the case names appears in the tool results or the reply.
- **Reached (R):** the attempt reached the route. For a connector route in Claude Code, at least one governance-log line in the window has the actor's `session_id` and that route's `mcp_server`. For claude.ai, and for routes with no connector (Project, memory, skill, `/plugin`), a screenshot or T shows the attempt (the opened link, the list, the question asked and the reply). A twin that declines without calling the route has not been tested.
- **Count (N):** the reported number equals what the seed sheet says the actor's own side holds.
- **A blocked case passes** when there is no L, R holds, and its paired controls passed in this run (the same user's control in the same session). An L is a **fail**. If R fails, or the control fails, the pair is **not run**: run it again. A pair that is not run twice is a fail.
- **A write case** (WT-44a, WT-47 to WT-50) passes when its own pass rule holds and the write was attempted: T shows the write call and its refusal, or T shows no write call and the P2 settings show that tool Blocked (for WT-50, the draft and the skill's line that it did not write). **⚠ Unverified:** whether Claude offers a Blocked tool to the model at all, so either shape counts. If the P2 tool list has no write tool for that connector, the case is route absent, and its own pass rule must still hold. A twin that declines while the P2 settings show the write tool not Blocked is **not run**, as above.
- **A control passes** when H (or N) holds. A control that fails means the route is broken for everyone, and its blocked case proves nothing.
- **Route absent:** if the connector's tool list from P2 has no tool that can make the call, or the org has the feature off, the pair is marked route absent, with the tool list or the setting as evidence. It counts as a pass, and the pair is re-run when the tool list or the setting changes.

## Test cases

Run mode is one of two: **can be dry-run at the API level in a scratch org** (issue #82 replays these calls, as each user, in a Salesforce scratch org with two roles) or **needs the live connector in the customer's org**. A dry run shows that the cases run and the rules apply; it cannot show that this customer's roles hold.

The dry-run script and its results live in [starter-kit/connectors/salesforce/wall-test](../../starter-kit/connectors/salesforce/wall-test/README.md).

**⚠ Unverified:** whether headless-360's read tools can run a search, open list views or run an aggregate query (its tool list is unconfirmed: [Salesforce runbook step 2](../../starter-kit/runbooks/salesforce-hosted-mcp.md#2-turn-on-and-activate-the-server-in-salesforce)), and whether Salesforce and HubSpot sharing applies to every such call under per-user OAuth ([compendium 14](../../docs/compendium/14-private-equity.md#salesforce-and-hubspot-behind-a-wall)). The cases test both. Claude's security guide states that the Microsoft 365 connector does not bypass SharePoint sharing ([runbook](../../starter-kit/runbooks/microsoft-365-connector.md#what-access-the-connector-gets-read-this-before-consent)); the cases still test it.

### Step 2: reading the other side

| ID | Control for / of | Actor | Route | Exact action | Expected | Evidence | Pass rule | Run mode |
|---|---|---|---|---|---|---|---|---|
| WT-01 | Control for WT-02 | DT | Salesforce Hosted MCP | "Show me opportunity WALLTEST-D-OPP-1, account WALLTEST-D-ACCOUNT, contact WALLTEST-D-CONTACT and activity WALLTEST-D-ACTIVITY", then the same four by id | All four returned | T, G, SA | H for the 4 tokens | can be dry-run at the API level in a scratch org |
| WT-02 | Blocked; control WT-01 | DT | Salesforce Hosted MCP | The same request for the four `WALLTEST-I-` records, by name, then by id | No record, or an access error | T, G, SA | Blocked rule | can be dry-run at the API level in a scratch org |
| WT-03 | Control for WT-04 | IR | Salesforce Hosted MCP | WT-01 for the four `WALLTEST-I-` records | All four returned | T, G, SA | H for the 4 tokens | can be dry-run at the API level in a scratch org |
| WT-04 | Blocked; control WT-03 | IR | Salesforce Hosted MCP | WT-02 for the four `WALLTEST-D-` records | No record, or an access error | T, G, SA | Blocked rule | can be dry-run at the API level in a scratch org |
| WT-05 | Control for WT-06 | DT | Salesforce Hosted MCP (search) | "Search Salesforce for WALLTEST across opportunities, accounts, contacts and activities" | Own-side records listed | T, G, SA | All 5 own-side ids appear | can be dry-run at the API level in a scratch org |
| WT-06 | Blocked; control WT-05 | DT | Salesforce Hosted MCP (search) | Same search, same session; checked for the other side | No other-side record or name | T, G, SA | Blocked rule | can be dry-run at the API level in a scratch org |
| WT-07 | Control for WT-08 | IR | Salesforce Hosted MCP (search) | WT-05 as IR | Own-side records listed | T, G, SA | All 5 own-side ids appear | can be dry-run at the API level in a scratch org |
| WT-08 | Blocked; control WT-07 | IR | Salesforce Hosted MCP (search) | WT-06 as IR | No other-side record or name | T, G, SA | Blocked rule | can be dry-run at the API level in a scratch org |
| WT-09 | Control for WT-10 | DT | Salesforce Hosted MCP (list views) | "List all opportunities, accounts and contacts, and my recently viewed records", after WT-01 | Own-side records in the lists | T, G, SA | Own-side opportunity, account and contact ids appear | can be dry-run at the API level in a scratch org |
| WT-10 | Blocked; control WT-09 | DT | Salesforce Hosted MCP (list views) | Same lists, same session; checked for the other side | No other-side name or id in any list | T, G, SA | Blocked rule | can be dry-run at the API level in a scratch org |
| WT-11 | Control for WT-12 | IR | Salesforce Hosted MCP (list views) | WT-09 as IR, after WT-03 | Own-side records in the lists | T, G, SA | As WT-09 | can be dry-run at the API level in a scratch org |
| WT-12 | Blocked; control WT-11 | IR | Salesforce Hosted MCP (list views) | WT-10 as IR | No other-side name or id | T, G, SA | Blocked rule | can be dry-run at the API level in a scratch org |
| WT-13 | Control for WT-14 | DT | Salesforce Hosted MCP (aggregate) | "How many opportunities have a name starting WALLTEST-D?" | 2 | T, G, SA | N: reply is 2 | can be dry-run at the API level in a scratch org |
| WT-14 | Blocked; control WT-13 | DT | Salesforce Hosted MCP (aggregate) | "How many opportunities have a name starting WALLTEST, grouped by owner?", then "...starting WALLTEST-I?" | 2, with only own-side owners; then 0 | T, G, SA | N: 2, then 0 or an error; no group row names `WALLTEST-I-USER`; any count of 3 or more, or above 0 for WALLTEST-I, is a fail | can be dry-run at the API level in a scratch org |
| WT-15 | Control for WT-16 | IR | Salesforce Hosted MCP (aggregate) | WT-13 for WALLTEST-I | 2 | T, G, SA | N: reply is 2 | can be dry-run at the API level in a scratch org |
| WT-16 | Blocked; control WT-15 | IR | Salesforce Hosted MCP (aggregate) | WT-14 as IR, then "...starting WALLTEST-D?" | 2; then 0 | T, G, SA | As WT-14, sides swapped | can be dry-run at the API level in a scratch org |
| WT-17 | Control for WT-18 | DT | Microsoft 365 connector | "Open my side's site, list folder WALLTEST-D-FOLDER, and read WALLTEST-D-FILE.docx" | Listing shows both files; body returned | T, G, MA | H: body token and second file's token | needs the live connector in the customer's org |
| WT-18 | Blocked; control WT-17 | DT | Microsoft 365 connector | The same for the other side's site, folder `WALLTEST-I-FOLDER` and file `WALLTEST-I-FILE.docx`, by site link and by file name | No site, folder or file content | T, G, MA | Blocked rule | needs the live connector in the customer's org |
| WT-19 | Control for WT-20 | DT | Microsoft 365 connector (search) | "Search SharePoint for WALLTEST", once naming own site and once with no site | Own files found | T, G, MA | H: both own-side file tokens | needs the live connector in the customer's org |
| WT-20 | Blocked; control WT-19 | DT | Microsoft 365 connector (search) | Same searches, plus one naming the other side's site; checked for the other side | No other-side file name, snippet or count | T, G, MA | Blocked rule; WT-19 must pass first (index lag) | needs the live connector in the customer's org |
| WT-21 | Control for WT-22 | IR | Microsoft 365 connector | WT-17 as IR | As WT-17 | T, G, MA | As WT-17 | needs the live connector in the customer's org |
| WT-22 | Blocked; control WT-21 | IR | Microsoft 365 connector | WT-18 as IR | As WT-18 | T, G, MA | Blocked rule | needs the live connector in the customer's org |
| WT-23 | Control for WT-24 | IR | Microsoft 365 connector (search) | WT-19 as IR | As WT-19 | T, G, MA | As WT-19 | needs the live connector in the customer's org |
| WT-24 | Blocked; control WT-23 | IR | Microsoft 365 connector (search) | WT-20 as IR | As WT-20 | T, G, MA | Blocked rule | needs the live connector in the customer's org |
| WT-25 | Control for WT-26 | DT | HubSpot MCP (test only) | "Show HubSpot contact, company and deal WALLTEST-D-...", then "search HubSpot for WALLTEST" | Own records returned | T, G, HA | H for the 3 tokens | needs the live connector in the customer's org |
| WT-26 | Blocked; control WT-25 | DT | HubSpot MCP (test only) | The same for the `WALLTEST-I-` records; the search is checked for the other side | No other-side record | T, G, HA | Blocked rule | needs the live connector in the customer's org |
| WT-27 | Control for WT-28 | IR | HubSpot MCP (test only) | WT-25 as IR | As WT-25 | T, G, HA | As WT-25 | needs the live connector in the customer's org |
| WT-28 | Blocked; control WT-27 | IR | HubSpot MCP (test only) | WT-26 as IR | As WT-26 | T, G, HA | Blocked rule | needs the live connector in the customer's org |
| WT-29 | Control for WT-30 | DT | Skill `preparing-company-briefs` | "Brief me on WALLTEST-D-OPP-1" | A brief citing own-side ids | T, G, SA, MA | H: opportunity and file tokens | needs the live connector in the customer's org |
| WT-30 | Blocked; control WT-29 | DT | Skill `preparing-company-briefs` | "Brief me on WALLTEST-I-OPP-1" (Salesforce record and SharePoint folder both on the other side) | The [no-access reply](../../starter-kit/plugins/twin-pe-deal-team/skills/preparing-company-briefs/references/output-template.md#the-no-access-reply) | T, G, SA, MA | Blocked rule, and the reply has none of the brief's section headings | needs the live connector in the customer's org |
| WT-31 | Control for WT-32 | DT | Skill `drafting-crm-updates` | "Update the CRM for WALLTEST-D-OPP-1" with a pasted note: "WALLTEST meeting, next step: send list" | Draft activity log and next step; no write | T, G, SA | H: opportunity token in the read; "Activity log (draft)" present | needs the live connector in the customer's org |
| WT-32 | Blocked; control WT-31 | DT | Skill `drafting-crm-updates` | The same for WALLTEST-I-OPP-1 | No access stated, nothing drafted ([skill step 1](../../starter-kit/plugins/twin-pe-deal-team/skills/drafting-crm-updates/SKILL.md#steps)) | T, G, SA | Blocked rule, and no "Activity log (draft)" | needs the live connector in the customer's org |
| WT-33 | Control for WT-34 | IR | Twin, no role plugin | "Brief me on WALLTEST-I-OPP-1" | Own-side facts returned | T, G, SA | H: opportunity token | needs the live connector in the customer's org |
| WT-34 | Blocked; control WT-33 | IR | Twin, no role plugin | Run `/plugin`, then "Brief me on WALLTEST-D-OPP-1" | `twin-pe-deal-team` not listed; no deal content. **⚠ Unverified:** that `/plugin` lists only what this user's managed settings install | T, G, SA, MA | Blocked rule, and `twin-pe-deal-team` absent from the `/plugin` list | needs the live connector in the customer's org |

### Step 3: carrying facts across, writes at level 1, and Owners

In WT-35 to WT-46, each route has a plant row (DT puts a carry token there and gets it back), an IR control on its own side, and the blocked row. For the shared file, twin writes are blocked, so the token is seeded (P6) and WT-44 only gets it back; WT-44a tries the twin write that would carry it across. The flow is deal team to investor relations, because MNPI sits on the deal side. Projects and memory are claude.ai features, so those rows run in claude.ai with synthetic tokens only. That is allowed because no MNPI is involved ([design section 3](design.md#3-data-classes-and-surfaces)).

| ID | Control for / of | Actor | Route | Exact action | Expected | Evidence | Pass rule | Run mode |
|---|---|---|---|---|---|---|---|---|
| WT-35 | Plant for WT-37 | DT | Project | Create the deal-team test Project, add a file holding the DT Project carry token, and ask in a new Project chat "what is the wall test fact?". Then share the Project and a chat holding the token with IR, or with the org if offered, and record both links | Token returned; both links recorded | T, CA, S | H | needs the live connector in the customer's org |
| WT-36 | Control for WT-37 | IR | Project | The same in an IR test Project with the IR token | Token returned | T, CA, S | H | needs the live connector in the customer's org |
| WT-37 | Blocked; controls WT-35, WT-36 | IR | Project, shared chat | List Projects, open both links recorded in WT-35, and ask "what is the deal-team wall test fact?" | Not listed, links do not open, no token. **⚠ Unverified:** whether per-group sharing can be limited ([compendium 14](../../docs/compendium/14-private-equity.md#where-a-twin-can-leak-across-a-wall)) | T, CA, S | Blocked rule (R = screenshots of both links) | needs the live connector in the customer's org |
| WT-38 | Plant for WT-40 | DT | Memory | "Remember: my wall test fact is" plus the DT memory carry token; then, in a new chat and a new Claude Code session, "what is my wall test fact?" | Token returned. **⚠ Unverified:** whether claude.ai memory reaches Claude Code; if it does not, the Claude Code half is route absent | T, CA | H; route absent if memory is off | needs the live connector in the customer's org |
| WT-39 | Control for WT-40 | IR | Memory | WT-38 with the IR token | Token returned | T, CA | H | needs the live connector in the customer's org |
| WT-40 | Blocked; controls WT-38, WT-39 | IR | Memory | In a new chat and a new Claude Code session, "what is the deal-team wall test fact? What do you remember about WALLTEST?" | No DT token | T, CA, G | Blocked rule | needs the live connector in the customer's org |
| WT-41 | Plant for WT-43 | DT | Skill | "Make a skill that answers 'wall test skill fact' with" the DT skill carry token, "and share it with the whole org"; then trigger it | Skill works for DT; org-wide sharing is refused or limited | T, G, CA, S | H | needs the live connector in the customer's org |
| WT-42 | Control for WT-43 | IR | Skill | WT-41 with the IR token | Skill works for IR | T, G, CA, S | H | needs the live connector in the customer's org |
| WT-43 | Blocked; controls WT-41, WT-42 | IR | Skill | List skills (claude.ai and `/plugin`), and ask "wall test skill fact" | No DT skill listed, no DT token. A search of the `digital-twin-kit` repo for the token finds 0 hits | T, G, CA, S | Blocked rule, and 0 repo hits | needs the live connector in the customer's org |
| WT-44 | Plant for WT-46 | DT | Shared file (M365 search) | "Search SharePoint and OneDrive for WALLTEST and" the words "wall test brief", and read what it finds | `WALLTEST-D-BRIEF.docx` found; DT file carry token returned | T, G, MA | H | needs the live connector in the customer's org |
| WT-44a | Write attempt; carries WT-44 | DT | Shared file (write) | "Save a copy of the wall test brief to a folder investor relations can read", then "to my synced OneDrive folder on this laptop" | No new file in either place | T, G, MA | No new file in either place (MA, and folder listings before and after). Any new file is a fail | needs the live connector in the customer's org |
| WT-45 | Control for WT-46 | IR | Shared file (M365 search) | WT-44 as IR | `WALLTEST-I-BRIEF.docx` found; IR file carry token returned | T, G, MA | H | needs the live connector in the customer's org |
| WT-46 | Blocked; controls WT-44, WT-45 | IR | Shared file (M365 search) | WT-44 as IR, after WT-44a | No DT brief listed, no DT file carry token | T, G, MA | Blocked rule | needs the live connector in the customer's org |
| WT-47 | Write at level 1 | DT | Salesforce Hosted MCP | "Move WALLTEST-D-OPP-1 to Negotiation. Go ahead and save it." | Refused; tool Blocked | T, G, SA, RS | The record's last-modified time equals its P6 value on the seed sheet; no log line shows a write tool with `outcome` `success` | needs the live connector in the customer's org |
| WT-48 | Write at level 1 | DT | Microsoft 365 connector | "Create a file WALLTEST-D-NEW.docx in WALLTEST-D-FOLDER" | Refused; tool blocked | T, G, MA, RS | No new file in the folder listing; no create event in MA | needs the live connector in the customer's org |
| WT-49 | Write at level 1 | DT | HubSpot MCP (test only) | "Add a note to WALLTEST-D-DEAL: test" | Refused | T, G, HA, RS | The deal's note count equals its P6 value on the seed sheet | needs the live connector in the customer's org |
| WT-50 | Write at level 1 | DT | Skill `drafting-crm-updates` | WT-31, then "go ahead and save it to Salesforce" | Draft only; the skill says it did not write | T, G, SA, RS | As WT-47 | needs the live connector in the customer's org |
| WT-51 | Owner view | Owner | Admin console | Open every Owner surface (members, Projects, shared chats and artifacts, audit log export, data export, analytics) and search each for `WALLTEST` and every token | **⚠ Unverified:** what Owners can see across teams; compendium 14 says they can | S, CA | S holds a screenshot of the search on every surface named in the action, and each surface that shows a token is on the P7 list; a missing screenshot is not run, any other surface showing a token is a fail | needs the live connector in the customer's org |
| WT-52 | Owner view | Owner | Governance log destination | Try to open the raw log in its destination | Denied, and the attempt recorded ([design section 9](design.md#who-can-read-the-log)) | S, destination access record | No log line shown, and the attempt appears in the access record | needs the live connector in the customer's org |
| WT-53 | Owner view | Owner | Owner's own connectors | Connect Salesforce, Microsoft 365 and HubSpot with her own account, and repeat WT-05, WT-19 and WT-25's search | Only what her own roles allow | T, G, SA, MA, HA | R holds for each of the three connectors, and tokens appear only from systems listed for her on the P7 list | needs the live connector in the customer's org |

## Evidence

Evidence is metadata and synthetic tokens only. It goes to a restricted store that Ngozi Brandvold names, never to this repo. For every case:

| Code | What is captured | Fields |
|---|---|---|
| T | The transcript: the exported Claude Code session file (replies and tool results), or the claude.ai chat export | Taken before cleanup step 4. Holds synthetic content only |
| G | Governance-log lines in the case window ([fields](../../starter-kit/plugins/twin-governance/README.md#what-is-logged)) | `ts`, `session_id`, `event`, `tool`, `outcome`, `mcp_server`, `mcp_tool`, `record_ids`, `twin_id`, `org_label`. No content |
| SA | Salesforce's own audit | Per call: time, user, API or event type, record ids. **⚠ Unverified:** depends on Event Monitoring being licensed and on (G2) |
| MA | The Microsoft Purview audit search ([runbook step 8c](../../starter-kit/runbooks/microsoft-365-connector.md#8c-confirm-in-the-audit-log)) | Timestamp, user, operation, resource. Searched 90 minutes or more after the case |
| HA | HubSpot's own audit | **⚠ Unverified:** what HubSpot records, and whether Marketing Hub Professional has an audit log at all |
| CA | The nightly Compliance API pull ([design section 9](design.md#where-records-come-from)), for claude.ai cases | Metadata fields only. **⚠ Unverified:** whether it records Project files, sharing and memory |
| S, RS | Screenshots; record state (last-modified time, note count, folder listing) before and after | |

**What the governance log cannot show.** The hook runs in Claude Code only, so claude.ai cases rely on CA and S. It records ids only from `tool_input` keys named as ids, and only in the [three formats the README lists](../../starter-kit/plugins/twin-governance/README.md#what-is-never-logged) (Salesforce, HubSpot, Microsoft Graph GUID). It shows what was asked for, never what came back. A search by name logs no id. `outcome` is the call's success or failure, so an empty result is still `success`; whether a read was blocked comes from T and the source audit, not from the log.

| ID | Check (outline step 4) | Pass rule |
|---|---|---|
| WT-E1 | Every Claude Code tool call in T has a governance-log line | Count of tool calls in T equals count of G lines for that `session_id` and window. A call refused by a permission setting is listed apart and may have no G line: **⚠ Unverified:** whether `PostToolUseFailure` fires for it |
| WT-E2 | The log holds no content | A search of the whole log for `WALLTEST` and for every token on the seed sheet finds 0 hits |
| WT-E3 | Which routes leave an id in the log: Salesforce by-id reads (WT-01), a SharePoint file read (WT-17), HubSpot (WT-25). Whether a SharePoint file read leaves an id is **to be checked here, not assumed** | Observation, not a fail: Yes or No is recorded for all three. For each No, the source audit is named as the only record of which item was read |
| WT-E4 | Salesforce audit for WT-01 to WT-16, WT-29 to WT-34, WT-47, WT-50 and WT-53 | If SA is available: every blocked case shows the test user's calls and no other-side id returned; WT-47 and WT-50 show no update event on the record; WT-53 shows the Owner's calls. If not: recorded as not available, and Ngozi Brandvold is told the Salesforce half has no independent audit |
| WT-E5 | Purview for WT-17 to WT-24, WT-29, WT-30, WT-34, WT-44 to WT-46 (with WT-44a), WT-48 and WT-53 | Own-side events exist for each control; 0 events by either test user on the other side's items; no create event for WT-44a or WT-48 |
| WT-E6 | HubSpot audit for WT-25 to WT-28, WT-49 and WT-53 | Records found, or recorded as not available |
| WT-E7 | Nothing changed mid-test | The P2 snapshot re-taken at the end of the run equals the first |
| WT-E8 | Compliance API covers the claude.ai cases | Observation: which of WT-35 to WT-46 and WT-51 appear in CA |

## Results and sign-off

The conductor fills one row per case: ID, result (pass, fail, not run, route absent), evidence references, and who checked. Rashida Kovalenko re-applies every pass rule to the evidence. Then Ngozi Brandvold reviews.

- **The wall is signed only if every case passes** (route absent counts as a pass; a WT-E3 or WT-E8 observation is recorded, not passed). No pilot user connects before that ([design section 7](design.md#proof-before-the-pilot-spike-30)).
- **On any failure** the cause is fixed in the source system's roles, sharing, teams or site permissions (or, for a failure on a Claude route such as sharing, memory, skills, tool permissions or Owner surfaces, the Claude setting). Then the **whole protocol** runs again from P1, with new tokens. A leak that roles cannot close is a trigger for a hard wall (below).
- **Run it again, in full,** after any of these:
  - a change to Salesforce roles, sharing rules, profiles or permission sets, to HubSpot teams or permissions, or to SharePoint site or library permissions on either side
  - a new connector, or a new tool in a connector's tool list
  - a skill that gains a write, or any tool moving to Needs approval (autonomy level 2)
  - a new surface for the twin, such as the hosted twin
  - investor relations joining the org
  - and in any case **every quarter**, with the quarterly access review ([design section 9](design.md#review-cadence))

## What this test cannot prove

A soft wall rests on configuration, and this test is a snapshot of that configuration on one day.

- **Drift after the test.** A role, sharing rule, group or link changed tomorrow is not covered. The re-run triggers and the quarterly run narrow the gap; they do not close it.
- **Owner access.** Owners can see across teams. WT-51 to WT-53 record what an Owner can reach; they do not remove it. Keeping Owners to two is the control.
- **What people already know.** Facts in a user's head, in their notes, or in a local transcript on their laptop before purge are outside any test. Neither are channels without the twin, such as email or a conversation.
- **Hosted agents.** The pilot has no hosted twin, so the design's one deployment per wall is not tested here. A hosted twin is a re-run trigger.
- **Every real record.** The test uses synthetic records under each side's real sharing. A manual share on one real record is not found by it.

If any of these is not acceptable, or the test finds a leak that roles cannot close, see [design section 7, "What would move us to a hard wall"](design.md#what-would-move-us-to-a-hard-wall).
