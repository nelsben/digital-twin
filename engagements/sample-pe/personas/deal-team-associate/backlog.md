# Deal-team associate twin for Example Capital Partners

Generated from card.json and levelled.json by `python3 partner-kit/plugins/twin-consultant/scripts/twincard/cli.py backlog engagements/sample-pe/personas/deal-team-associate`; never edit it by hand. To mark a task, change only its status in backlog.json, then run the command again.

Status: todo. 5 features, 13 stories, 149 tasks. Task marks: `[ ]` todo, `[~]` in progress, `[x]` done.

Roles with no named person: security, 2 tasks, acting owner Director of IT; source-system-admin, 13 tasks, acting owner Director of IT; skill-owner, 2 tasks, acting owner Director of IT.

Stories ready to build: 0 of 6.

Stories with no target: 6. Agree the scorecard targets with the sponsor.

## F-pre-meeting-preparation: Pre-meeting preparation

Kind: capability. Status: todo. 2 stories.

### S-T1: Prepare a one-page company brief

As a deal-team associate, I want my twin to draft the one-page company brief from Salesforce and SharePoint so that I spend my time on the model and the diligence calls instead.

Part A2. In pilot: yes. Priority: 1. Status: todo.

| Field | Value |
|---|---|
| Data class | highly-sensitive |
| Surface | client-skill; surfaces: claude-code |
| Autonomy | 1 to 3 |
| Connectors and identity | salesforce: user identity, read, always-allow; sharepoint: user identity, read, always-allow |
| Wall impact | soft |
| Inputs | salesforce (deal record (opportunity, account)); sharepoint (prior memos and data-room files) |
| Output and audience | One-page company brief, internal; to none (the conversation) |
| Delivery | The output stays in the conversation or a local file. |
| Skill owner | Callum Nwosu |
| Baseline | 4 per week x 90 minutes each x 3 users |
| Constraints | A reviewer checks every brief before it goes further. |

**Acceptance criteria:**

1. To write: collect at least 3 real examples from Callum Nwosu and write one eval case from each.
2. Keeps: A reviewer checks every brief before it goes further.
3. Plus: the skill triggers on the phrases its trigger evals list and stays quiet on the near-misses.
4. Plus: no web tools are used.
5. Plus: each tool call reaches the governance log.

Target: not set. Agree the scorecard targets with the sponsor before the pilot starts.

Ready to build: no
- examples: 0 counted examples (0 good, 0 bad); at least 3 needed.
- compliance-sign-off: Waiting for S-T1.compliance-sign-off: compliance signs the story off before it is built.

**Gated by:**

- open-question E4: Do the Salesforce and HubSpot admins confirm in writing that deal-team and investor-relations roles are fully separated? (spike SP-E4)
- open-question E6: Can Anthropic's range 160.79.104.0/21 be allowlisted? (spike SP-E6)
- open-question F3: Two to three real good and bad examples per skill, redacted. (spike SP-F3)
- open-question G1: Where does the governance log go (Splunk is the candidate), how is it hosted and who may read it? (spike SP-G1)
- open-question OD-9: ZDR addendum on the existing Enterprise org, which models qualify for ZDR, and the seat count. (spike SP-OD-9)
- open-question OD-11: Numeric scorecard targets for hours saved and edit rate on T1 and T2. (spike SP-OD-11)
- open-question OD-13: Keep the Salesforce and Microsoft 365 connectors out of chat and Cowork for the deal-team group. Due: before any pilot user connects. (spike SP-OD-13)
- sign-off compliance: Compliance has not signed the story off yet (S-T1.compliance-sign-off).

**Tasks:**

- [ ] **S-T1.compliance-sign-off** Get compliance's sign-off on the story before it is built (owner: compliance, Chief Compliance Officer, part A7)
  1. Check the story meets the definition of ready before compliance reads it. See [docs/playbook/04-stories.md#definition-of-ready-before-building](../../../../docs/playbook/04-stories.md#definition-of-ready-before-building).
  2. Compliance reads the story's fields, the levelled decisions for the task and its data controls. See [partner-kit/docs/design.md#73-rules-plan-fit-and-levelledjson](../../../../partner-kit/docs/design.md#73-rules-plan-fit-and-levelledjson).
  3. Record the sign-off, with the signer's name and the date, in the customer's engagement folder. See [engagements/README.md](../../../../engagements/README.md).
  - Done when: The sign-off is recorded in the customer's engagement folder with a name and a date.
- [ ] **S-T1.collect-examples** Collect 3 examples of the task from real work, each with the result a person expects (owner: skill-owner, Callum Nwosu, part A8)
  1. Ask the people who do the task today for three recent, real examples of it. See [starter-kit/docs/authoring-skills.md#step-order](../../../../starter-kit/docs/authoring-skills.md#step-order).
  2. Record each example's inputs and the output a person would accept as done. See [starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals](../../../../starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals).
  3. Remove any data the examples must not carry into the repository, keeping their shape. See [docs/compendium/10-sensitive-data.md#design-patterns-that-keep-data-out-of-the-conversation](../../../../docs/compendium/10-sensitive-data.md#design-patterns-that-keep-data-out-of-the-conversation).
  - Done when: Three real examples, each with its inputs and its expected result, are stored where the evals can read them.
- [ ] **S-T1.write-evals** Write the evals from the examples and the story's acceptance criteria (owner: skill-engineer, part A8)
  1. Turn each example and each acceptance criterion into an eval case with its expected result. See [starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals](../../../../starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals).
  2. Put the eval cases in the files the kit expects, next to the skill. See [starter-kit/docs/authoring-skills.md#the-eval-files](../../../../starter-kit/docs/authoring-skills.md#the-eval-files).
  3. Run the evals once before any skill exists and keep the failing baseline. See [docs/compendium/03-skills-authoring.md#evaluate-first-then-iterate](../../../../docs/compendium/03-skills-authoring.md#evaluate-first-then-iterate).
  - Done when: Every acceptance criterion has at least one eval, and the evals run and fail without the skill.
- [ ] **S-T1.write-skill** Write the skill from the kit template until the evals pass (owner: skill-engineer, part A2)
  1. Copy the kit's skill template into the role plugin's skills folder, the one source of the skill for every runtime. See [starter-kit/templates/skill/README.md#copy-it](../../../../starter-kit/templates/skill/README.md#copy-it).
  2. Rename the copy to the skill's name. See [starter-kit/templates/skill/README.md#rename-it](../../../../starter-kit/templates/skill/README.md#rename-it).
  3. Fill in the description and the body, then rerun the evals until they pass. See [starter-kit/templates/skill/README.md#fill-it-in](../../../../starter-kit/templates/skill/README.md#fill-it-in).
  4. On client-skill, the skill loads from the role plugin, which an Owner publishes to claude.ai, Desktop and Cowork and which reaches a signed-in Claude Code. See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  5. On managed-agents, the skill loads from the agent's skills array (skills uploaded through the Skills API), or from a mounted GitHub repo's .claude/skills folder. See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  6. On managed-agents-self-hosted, load the skill the same two ways as hosted Managed Agents (Unverified: no compendium page says where a self-hosted deployment loads skills from). See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  7. On agent-sdk, the skill is files on disk in the runner's container, loaded through settingSources; there is no API to register a skill. See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  8. On claude-code-scheduled-task, put the skill where Claude Code loads skills: the project's .claude/skills folder or a plugin (Unverified: no compendium page says which of these a scheduled task loads). See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  9. On claude-tag-routine, give the routine the skill as its instructions (Unverified: no compendium page says whether a Claude Tag routine loads org skills). See [docs/compendium/05-decision-matrix.md#the-options](../../../../docs/compendium/05-decision-matrix.md#the-options).
  10. Make the skill keep these rules from the interviews, in the interviewee's words: A reviewer checks every brief before it goes further.. See [partner-kit/docs/design.md#42-persona-card-cardjson](../../../../partner-kit/docs/design.md#42-persona-card-cardjson).
  - Done when: The skill sits in the role plugin, it is where the task's runtime loads it from, and every eval for the story passes.
- [ ] **S-T1.trigger-evals** Write and run the trigger evals for the skill (owner: skill-engineer, part A8)
  1. Install skill-creator where the evals run. See [starter-kit/docs/authoring-skills.md#install-skill-creator](../../../../starter-kit/docs/authoring-skills.md#install-skill-creator).
  2. Write prompts that should and should not start the skill, as trigger evals. See [starter-kit/docs/authoring-skills.md#the-eval-files](../../../../starter-kit/docs/authoring-skills.md#the-eval-files).
  3. Run the trigger evals and tighten the description until they pass. See [docs/compendium/03-skills-authoring.md#writing-a-good-description](../../../../docs/compendium/03-skills-authoring.md#writing-a-good-description).
  - Done when: The skill starts on every should-trigger prompt and on none of the should-not prompts.
- [ ] **S-T1.second-review** Have a second person review the skill and its evals (owner: skill-owner, Callum Nwosu, part A8)
  1. Open a pull request with the skill and its evals. See [docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often](../../../../docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often).
  2. Have someone other than the author review it against the definition of done. See [docs/playbook/04-stories.md#definition-of-done](../../../../docs/playbook/04-stories.md#definition-of-done).
  - Done when: A reviewer who did not write the skill has approved the pull request and the evals pass.
- [ ] **S-T1.publish-in-role-plugin** Publish the skill in the role plugin (owner: skill-engineer, part A9)
  1. Add the skill to the role plugin and bump the plugin's version. See [starter-kit/templates/role-plugin/README.md#steps](../../../../starter-kit/templates/role-plugin/README.md#steps).
  2. Publish the marketplace so the role's users get the new version. See [starter-kit/runbooks/identity-devices-publishing.md#6-publish-the-marketplace-and-its-plugins-to-the-right-groups](../../../../starter-kit/runbooks/identity-devices-publishing.md#6-publish-the-marketplace-and-its-plugins-to-the-right-groups).
  - Done when: A pilot user in the role sees the skill after the plugin updates.
- [ ] **S-T1.owner-handover** Hand the skill over to its owner (owner: skill-engineer, part A2)
  1. Show the skill owner where the skill lives: its folder in the role plugin, the one source for every runtime. See [starter-kit/templates/skill/README.md#copy-it](../../../../starter-kit/templates/skill/README.md#copy-it).
  2. Show them how to change an instruction in the skill and add an eval case for the change. See [starter-kit/templates/skill/README.md#fill-it-in](../../../../starter-kit/templates/skill/README.md#fill-it-in).
  3. Name who reviews a change before it is published: someone other than its author. See [docs/playbook/04-stories.md#definition-of-done](../../../../docs/playbook/04-stories.md#definition-of-done).
  4. Have the skill owner make one change while the engineer watches. See [docs/playbook/04-stories.md#definition-of-done](../../../../docs/playbook/04-stories.md#definition-of-done).
  - Done when: The skill owner has made one change to the skill with the engineer watching.
- [ ] **S-T1.connect-salesforce-runbook.salesforce** Connect it by following the kit's Salesforce hosted MCP runbook (salesforce) (owner: source-system-admin, acting: Director of IT, part A3)
  1. Choose per-user OAuth as the runbook explains before anything is created. See [starter-kit/runbooks/salesforce-hosted-mcp.md#4-choose-per-user-oauth-the-decision-you-cannot-undo](../../../../starter-kit/runbooks/salesforce-hosted-mcp.md#4-choose-per-user-oauth-the-decision-you-cannot-undo).
  2. Add the connector in the Claude org. See [starter-kit/runbooks/salesforce-hosted-mcp.md#6-add-the-connector-in-the-claude-org](../../../../starter-kit/runbooks/salesforce-hosted-mcp.md#6-add-the-connector-in-the-claude-org).
  3. Set the tool permissions first, then connect. See [starter-kit/runbooks/salesforce-hosted-mcp.md#7-set-tool-permissions-then-connect](../../../../starter-kit/runbooks/salesforce-hosted-mcp.md#7-set-tool-permissions-then-connect).
  - Done when: Each pilot user has connected with their own login and only the planned tools are enabled.
- [ ] **S-T1.connect-microsoft-365-runbook.sharepoint** Connect it by following the kit's Microsoft 365 connector runbook (sharepoint) (owner: source-system-admin, acting: Director of IT, part A3)
  1. Decide what to approve before granting consent. See [starter-kit/runbooks/microsoft-365-connector.md#2-decide-what-to-approve-before-consent](../../../../starter-kit/runbooks/microsoft-365-connector.md#2-decide-what-to-approve-before-consent).
  2. Grant tenant admin consent. See [starter-kit/runbooks/microsoft-365-connector.md#3-grant-tenant-admin-consent](../../../../starter-kit/runbooks/microsoft-365-connector.md#3-grant-tenant-admin-consent).
  3. Enable the connector for the right Claude group. See [starter-kit/runbooks/microsoft-365-connector.md#5-enable-the-connector-for-the-right-claude-group](../../../../starter-kit/runbooks/microsoft-365-connector.md#5-enable-the-connector-for-the-right-claude-group).
  - Done when: Consent is granted, the connector is enabled for the role's group only, and its write tools are set as the story's tool tasks say.
- [ ] **S-T1.tool-always-allow.salesforce-read** Set the connector tool to Always allow, as the levelled tools list says (salesforce-read) (owner: technical-owner, Director of IT, part A7)
  1. Open the connector's page in the Claude org and find the tool. See [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced).
  2. Set the tool to Always allow and record the change. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  - Done when: The tool is set to Always allow in the Claude org, as levelled.json says.
- [ ] **S-T1.tool-always-allow.sharepoint-read** Set the connector tool to Always allow, as the levelled tools list says (sharepoint-read) (owner: technical-owner, Director of IT, part A7)
  1. Open the connector's page in the Claude org and find the tool. See [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced).
  2. Set the tool to Always allow and record the change. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  - Done when: The tool is set to Always allow in the Claude org, as levelled.json says.
- [ ] **S-T1.evidence-level-2** Gather the evidence to move the task up to level 2, act with approval (owner: business-owner, RevOps manager, part A8)
  1. Show the evals pass reliably at the current level. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Bring a month of scorecard results, with the edit rate, to the business owner. See [docs/compendium/15-governance-and-performance.md#measuring-performance](../../../../docs/compendium/15-governance-and-performance.md#measuring-performance).
  - Done when: The business owner has approved the move to level 2 on scorecard evidence, and every write or send tool the task uses at level 2 is at Needs approval; a task whose output a routine posts itself changes no tool setting.
- [ ] **S-T1.evidence-level-3** Gather the evidence to move the task up to level 3, act within an allowlist (owner: business-owner, RevOps manager, part A8)
  1. Confirm every allowlisted action can be undone or stays internal. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Show a stable eval pass rate, a low edit rate and few rejections at level 2. See [docs/compendium/15-governance-and-performance.md#measuring-performance](../../../../docs/compendium/15-governance-and-performance.md#measuring-performance).
  3. List the tools to set to Always allow and keep every other tool on Needs approval. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  - Done when: The business owner has approved the allowlist on scorecard evidence, and only those tools are Always allow.
- [ ] **S-T1.wall-test** Test the information wall with two users on either side before the pilot (owner: compliance, Chief Compliance Officer, part A7)
  1. List what the wall must keep apart in each system the task reads. See [docs/compendium/14-private-equity.md#what-a-wall-has-to-guarantee](../../../../docs/compendium/14-private-equity.md#what-a-wall-has-to-guarantee).
  2. Run the task as a user on each side of the wall and check neither sees the other side's records. See [docs/compendium/14-private-equity.md#where-a-twin-can-leak-across-a-wall](../../../../docs/compendium/14-private-equity.md#where-a-twin-can-leak-across-a-wall).
  3. Use the two-user test in the system's runbook where the kit has one. See [starter-kit/runbooks/salesforce-hosted-mcp.md#9-test-two-users-on-either-side-of-a-soft-wall](../../../../starter-kit/runbooks/salesforce-hosted-mcp.md#9-test-two-users-on-either-side-of-a-soft-wall).
  - Done when: Compliance has seen the two-user test pass for every walled system the task reads.
- [ ] **S-T1.web-tools-off** Check web search and web fetch are off wherever this task runs (owner: technical-owner, Director of IT, part A7)
  1. Check the settings baseline or the org setting turns web tools off on the task's surfaces. See [starter-kit/settings/README.md#keys](../../../../starter-kit/settings/README.md#keys).
  2. Try a web search in the task and confirm it is refused. See [docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above](../../../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above).
  - Done when: A web search or fetch attempted during the task is refused.
- [ ] **S-T1.confirm-unverified-decision.connectors.salesforce** Confirm the unverified fact behind this decision with Anthropic or the vendor before build (connectors.salesforce) (owner: solution-architect, part A3)
  1. Find the Unverified mark on the page the decision cites in levelled.json. See [partner-kit/docs/design.md#72-decision-values](../../../../partner-kit/docs/design.md#72-decision-values).
  2. Ask Anthropic or the vendor in writing, using the partner questions list. See [docs/compendium/12-orgs-and-ownership.md#questions-to-bring-to-anthropic-as-a-partner](../../../../docs/compendium/12-orgs-and-ownership.md#questions-to-bring-to-anthropic-as-a-partner).
  3. Record the answer with its source and level the card again. See [docs/compendium/08-open-questions.md#questions-most-first-time-builders-miss](../../../../docs/compendium/08-open-questions.md#questions-most-first-time-builders-miss).
  - Done when: The fact is confirmed in writing with a source, or the decision is changed so it no longer rests on it.
- [ ] **S-T1.warning-zdr-org-not-confirmed** Resolve warning zdr-org-not-confirmed: confirm the separate Enterprise org with ZDR (owner: compliance, Chief Compliance Officer, part A7)
  1. Explain that highly sensitive data needs a separate Enterprise org with ZDR. See [docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above](../../../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above).
  2. Confirm with the customer whether a zero-data-retention agreement covers the org this work runs in, record the answer as compliance.zdr_cover in the profile, then level again. See [docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt](../../../../docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt).
  - Done when: The profile's compliance.zdr_cover is in-place for this work, or the task's data class is lowered with the compliance owner.
- [ ] **S-T1.zdr-retention-agreement-first** Get the zero-data-retention agreement signed, then confirm the task runs only in that org (owner: compliance, Chief Compliance Officer, part A7)
  1. The profile's compliance.zdr_cover is planned or still open: no signed zero-data-retention agreement covers this work yet. Do not let the task go live until the agreement is signed and covers the org it runs in. See [docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt](../../../../docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt).
  2. Check the task's surfaces and connectors are all in the ZDR org. See [docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt](../../../../docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt).
  3. Record which features the ZDR org lacks that the task might expect. See [docs/compendium/12-orgs-and-ownership.md#recommended-starting-point](../../../../docs/compendium/12-orgs-and-ownership.md#recommended-starting-point).
  - Done when: The zero-data-retention agreement is signed and covers the org, compliance.zdr_cover is in-place, and compliance has confirmed the task runs only in the ZDR org.

### S-T5: Prepare for a management or expert call

As a deal-team associate, I want my twin to pull together a briefing note for whoever is on the call so that the caller walks in knowing what we already know.

Part A2. In pilot: no. Priority: 4. Status: todo.

| Field | Value |
|---|---|
| Data class | highly-sensitive |
| Surface | client-skill; surfaces: claude-code |
| Autonomy | 1 to 3 |
| Connectors and identity | salesforce: user identity, read, always-allow; sharepoint: user identity, read, always-allow |
| Wall impact | soft |
| Inputs | salesforce (account and opportunity); sharepoint (prior call notes) |
| Output and audience | Briefing note for the caller, internal; to none (the conversation) |
| Delivery | The output stays in the conversation or a local file. |
| Skill owner | Callum Nwosu |
| Baseline | 1.85 per week x 45 minutes each x unknown users |

**Acceptance criteria:**

1. To write: collect at least 3 real examples from Callum Nwosu and write one eval case from each.
2. Plus: the skill triggers on the phrases its trigger evals list and stays quiet on the near-misses.
3. Plus: no web tools are used.
4. Plus: each tool call reaches the governance log.

Target: not set. Agree the scorecard targets with the sponsor before the pilot starts.

Ready to build: no
- examples: 0 counted examples (0 good, 0 bad); at least 3 needed.
- compliance-sign-off: Waiting for S-T5.compliance-sign-off: compliance signs the story off before it is built.

**Gated by:**

- open-question F3: Two to three real good and bad examples per skill, redacted. (spike SP-F3)
- sign-off compliance: Compliance has not signed the story off yet (S-T5.compliance-sign-off).

**Tasks:**

- [ ] **S-T5.compliance-sign-off** Get compliance's sign-off on the story before it is built (owner: compliance, Chief Compliance Officer, part A7)
  1. Check the story meets the definition of ready before compliance reads it. See [docs/playbook/04-stories.md#definition-of-ready-before-building](../../../../docs/playbook/04-stories.md#definition-of-ready-before-building).
  2. Compliance reads the story's fields, the levelled decisions for the task and its data controls. See [partner-kit/docs/design.md#73-rules-plan-fit-and-levelledjson](../../../../partner-kit/docs/design.md#73-rules-plan-fit-and-levelledjson).
  3. Record the sign-off, with the signer's name and the date, in the customer's engagement folder. See [engagements/README.md](../../../../engagements/README.md).
  - Done when: The sign-off is recorded in the customer's engagement folder with a name and a date.
- [ ] **S-T5.collect-examples** Collect 3 examples of the task from real work, each with the result a person expects (owner: skill-owner, Callum Nwosu, part A8)
  1. Ask the people who do the task today for three recent, real examples of it. See [starter-kit/docs/authoring-skills.md#step-order](../../../../starter-kit/docs/authoring-skills.md#step-order).
  2. Record each example's inputs and the output a person would accept as done. See [starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals](../../../../starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals).
  3. Remove any data the examples must not carry into the repository, keeping their shape. See [docs/compendium/10-sensitive-data.md#design-patterns-that-keep-data-out-of-the-conversation](../../../../docs/compendium/10-sensitive-data.md#design-patterns-that-keep-data-out-of-the-conversation).
  - Done when: Three real examples, each with its inputs and its expected result, are stored where the evals can read them.
- [ ] **S-T5.write-evals** Write the evals from the examples and the story's acceptance criteria (owner: skill-engineer, part A8)
  1. Turn each example and each acceptance criterion into an eval case with its expected result. See [starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals](../../../../starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals).
  2. Put the eval cases in the files the kit expects, next to the skill. See [starter-kit/docs/authoring-skills.md#the-eval-files](../../../../starter-kit/docs/authoring-skills.md#the-eval-files).
  3. Run the evals once before any skill exists and keep the failing baseline. See [docs/compendium/03-skills-authoring.md#evaluate-first-then-iterate](../../../../docs/compendium/03-skills-authoring.md#evaluate-first-then-iterate).
  - Done when: Every acceptance criterion has at least one eval, and the evals run and fail without the skill.
- [ ] **S-T5.write-skill** Write the skill from dd-meeting-prep until the evals pass (owner: skill-engineer, part A2)
  1. Start from dd-meeting-prep (claude-for-financial-services: private-equity): Adapt, for T5. See [docs/compendium/17-anthropic-pe-plugins-review.md#1-whats-in-private-equity](../../../../docs/compendium/17-anthropic-pe-plugins-review.md#1-whats-in-private-equity).
  2. Copy the kit's skill template into the role plugin's skills folder, the one source of the skill for every runtime. See [starter-kit/templates/skill/README.md#copy-it](../../../../starter-kit/templates/skill/README.md#copy-it).
  3. Rename the copy to the skill's name. See [starter-kit/templates/skill/README.md#rename-it](../../../../starter-kit/templates/skill/README.md#rename-it).
  4. Fill in the description and the body, then rerun the evals until they pass. See [starter-kit/templates/skill/README.md#fill-it-in](../../../../starter-kit/templates/skill/README.md#fill-it-in).
  5. On client-skill, the skill loads from the role plugin, which an Owner publishes to claude.ai, Desktop and Cowork and which reaches a signed-in Claude Code. See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  6. On managed-agents, the skill loads from the agent's skills array (skills uploaded through the Skills API), or from a mounted GitHub repo's .claude/skills folder. See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  7. On managed-agents-self-hosted, load the skill the same two ways as hosted Managed Agents (Unverified: no compendium page says where a self-hosted deployment loads skills from). See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  8. On agent-sdk, the skill is files on disk in the runner's container, loaded through settingSources; there is no API to register a skill. See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  9. On claude-code-scheduled-task, put the skill where Claude Code loads skills: the project's .claude/skills folder or a plugin (Unverified: no compendium page says which of these a scheduled task loads). See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  10. On claude-tag-routine, give the routine the skill as its instructions (Unverified: no compendium page says whether a Claude Tag routine loads org skills). See [docs/compendium/05-decision-matrix.md#the-options](../../../../docs/compendium/05-decision-matrix.md#the-options).
  - Done when: The skill sits in the role plugin, it is where the task's runtime loads it from, and every eval for the story passes.
- [ ] **S-T5.trigger-evals** Write and run the trigger evals for the skill (owner: skill-engineer, part A8)
  1. Install skill-creator where the evals run. See [starter-kit/docs/authoring-skills.md#install-skill-creator](../../../../starter-kit/docs/authoring-skills.md#install-skill-creator).
  2. Write prompts that should and should not start the skill, as trigger evals. See [starter-kit/docs/authoring-skills.md#the-eval-files](../../../../starter-kit/docs/authoring-skills.md#the-eval-files).
  3. Run the trigger evals and tighten the description until they pass. See [docs/compendium/03-skills-authoring.md#writing-a-good-description](../../../../docs/compendium/03-skills-authoring.md#writing-a-good-description).
  - Done when: The skill starts on every should-trigger prompt and on none of the should-not prompts.
- [ ] **S-T5.second-review** Have a second person review the skill and its evals (owner: skill-owner, Callum Nwosu, part A8)
  1. Open a pull request with the skill and its evals. See [docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often](../../../../docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often).
  2. Have someone other than the author review it against the definition of done. See [docs/playbook/04-stories.md#definition-of-done](../../../../docs/playbook/04-stories.md#definition-of-done).
  - Done when: A reviewer who did not write the skill has approved the pull request and the evals pass.
- [ ] **S-T5.publish-in-role-plugin** Publish the skill in the role plugin (owner: skill-engineer, part A9)
  1. Add the skill to the role plugin and bump the plugin's version. See [starter-kit/templates/role-plugin/README.md#steps](../../../../starter-kit/templates/role-plugin/README.md#steps).
  2. Publish the marketplace so the role's users get the new version. See [starter-kit/runbooks/identity-devices-publishing.md#6-publish-the-marketplace-and-its-plugins-to-the-right-groups](../../../../starter-kit/runbooks/identity-devices-publishing.md#6-publish-the-marketplace-and-its-plugins-to-the-right-groups).
  - Done when: A pilot user in the role sees the skill after the plugin updates.
- [ ] **S-T5.owner-handover** Hand the skill over to its owner (owner: skill-engineer, part A2)
  1. Show the skill owner where the skill lives: its folder in the role plugin, the one source for every runtime. See [starter-kit/templates/skill/README.md#copy-it](../../../../starter-kit/templates/skill/README.md#copy-it).
  2. Show them how to change an instruction in the skill and add an eval case for the change. See [starter-kit/templates/skill/README.md#fill-it-in](../../../../starter-kit/templates/skill/README.md#fill-it-in).
  3. Name who reviews a change before it is published: someone other than its author. See [docs/playbook/04-stories.md#definition-of-done](../../../../docs/playbook/04-stories.md#definition-of-done).
  4. Have the skill owner make one change while the engineer watches. See [docs/playbook/04-stories.md#definition-of-done](../../../../docs/playbook/04-stories.md#definition-of-done).
  - Done when: The skill owner has made one change to the skill with the engineer watching.
- [ ] **S-T5.connect-salesforce-runbook.salesforce** Connect it by following the kit's Salesforce hosted MCP runbook (salesforce) (owner: source-system-admin, acting: Director of IT, part A3)
  1. Choose per-user OAuth as the runbook explains before anything is created. See [starter-kit/runbooks/salesforce-hosted-mcp.md#4-choose-per-user-oauth-the-decision-you-cannot-undo](../../../../starter-kit/runbooks/salesforce-hosted-mcp.md#4-choose-per-user-oauth-the-decision-you-cannot-undo).
  2. Add the connector in the Claude org. See [starter-kit/runbooks/salesforce-hosted-mcp.md#6-add-the-connector-in-the-claude-org](../../../../starter-kit/runbooks/salesforce-hosted-mcp.md#6-add-the-connector-in-the-claude-org).
  3. Set the tool permissions first, then connect. See [starter-kit/runbooks/salesforce-hosted-mcp.md#7-set-tool-permissions-then-connect](../../../../starter-kit/runbooks/salesforce-hosted-mcp.md#7-set-tool-permissions-then-connect).
  - Done when: Each pilot user has connected with their own login and only the planned tools are enabled.
- [ ] **S-T5.connect-microsoft-365-runbook.sharepoint** Connect it by following the kit's Microsoft 365 connector runbook (sharepoint) (owner: source-system-admin, acting: Director of IT, part A3)
  1. Decide what to approve before granting consent. See [starter-kit/runbooks/microsoft-365-connector.md#2-decide-what-to-approve-before-consent](../../../../starter-kit/runbooks/microsoft-365-connector.md#2-decide-what-to-approve-before-consent).
  2. Grant tenant admin consent. See [starter-kit/runbooks/microsoft-365-connector.md#3-grant-tenant-admin-consent](../../../../starter-kit/runbooks/microsoft-365-connector.md#3-grant-tenant-admin-consent).
  3. Enable the connector for the right Claude group. See [starter-kit/runbooks/microsoft-365-connector.md#5-enable-the-connector-for-the-right-claude-group](../../../../starter-kit/runbooks/microsoft-365-connector.md#5-enable-the-connector-for-the-right-claude-group).
  - Done when: Consent is granted, the connector is enabled for the role's group only, and its write tools are set as the story's tool tasks say.
- [ ] **S-T5.tool-always-allow.salesforce-read** Set the connector tool to Always allow, as the levelled tools list says (salesforce-read) (owner: technical-owner, Director of IT, part A7)
  1. Open the connector's page in the Claude org and find the tool. See [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced).
  2. Set the tool to Always allow and record the change. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  - Done when: The tool is set to Always allow in the Claude org, as levelled.json says.
- [ ] **S-T5.tool-always-allow.sharepoint-read** Set the connector tool to Always allow, as the levelled tools list says (sharepoint-read) (owner: technical-owner, Director of IT, part A7)
  1. Open the connector's page in the Claude org and find the tool. See [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced).
  2. Set the tool to Always allow and record the change. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  - Done when: The tool is set to Always allow in the Claude org, as levelled.json says.
- [ ] **S-T5.evidence-level-2** Gather the evidence to move the task up to level 2, act with approval (owner: business-owner, RevOps manager, part A8)
  1. Show the evals pass reliably at the current level. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Bring a month of scorecard results, with the edit rate, to the business owner. See [docs/compendium/15-governance-and-performance.md#measuring-performance](../../../../docs/compendium/15-governance-and-performance.md#measuring-performance).
  - Done when: The business owner has approved the move to level 2 on scorecard evidence, and every write or send tool the task uses at level 2 is at Needs approval; a task whose output a routine posts itself changes no tool setting.
- [ ] **S-T5.evidence-level-3** Gather the evidence to move the task up to level 3, act within an allowlist (owner: business-owner, RevOps manager, part A8)
  1. Confirm every allowlisted action can be undone or stays internal. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Show a stable eval pass rate, a low edit rate and few rejections at level 2. See [docs/compendium/15-governance-and-performance.md#measuring-performance](../../../../docs/compendium/15-governance-and-performance.md#measuring-performance).
  3. List the tools to set to Always allow and keep every other tool on Needs approval. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  - Done when: The business owner has approved the allowlist on scorecard evidence, and only those tools are Always allow.
- [ ] **S-T5.wall-test** Test the information wall with two users on either side before the pilot (owner: compliance, Chief Compliance Officer, part A7)
  1. List what the wall must keep apart in each system the task reads. See [docs/compendium/14-private-equity.md#what-a-wall-has-to-guarantee](../../../../docs/compendium/14-private-equity.md#what-a-wall-has-to-guarantee).
  2. Run the task as a user on each side of the wall and check neither sees the other side's records. See [docs/compendium/14-private-equity.md#where-a-twin-can-leak-across-a-wall](../../../../docs/compendium/14-private-equity.md#where-a-twin-can-leak-across-a-wall).
  3. Use the two-user test in the system's runbook where the kit has one. See [starter-kit/runbooks/salesforce-hosted-mcp.md#9-test-two-users-on-either-side-of-a-soft-wall](../../../../starter-kit/runbooks/salesforce-hosted-mcp.md#9-test-two-users-on-either-side-of-a-soft-wall).
  - Done when: Compliance has seen the two-user test pass for every walled system the task reads.
- [ ] **S-T5.web-tools-off** Check web search and web fetch are off wherever this task runs (owner: technical-owner, Director of IT, part A7)
  1. Check the settings baseline or the org setting turns web tools off on the task's surfaces. See [starter-kit/settings/README.md#keys](../../../../starter-kit/settings/README.md#keys).
  2. Try a web search in the task and confirm it is refused. See [docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above](../../../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above).
  - Done when: A web search or fetch attempted during the task is refused.
- [ ] **S-T5.confirm-unverified-decision.connectors.salesforce** Confirm the unverified fact behind this decision with Anthropic or the vendor before build (connectors.salesforce) (owner: solution-architect, part A3)
  1. Find the Unverified mark on the page the decision cites in levelled.json. See [partner-kit/docs/design.md#72-decision-values](../../../../partner-kit/docs/design.md#72-decision-values).
  2. Ask Anthropic or the vendor in writing, using the partner questions list. See [docs/compendium/12-orgs-and-ownership.md#questions-to-bring-to-anthropic-as-a-partner](../../../../docs/compendium/12-orgs-and-ownership.md#questions-to-bring-to-anthropic-as-a-partner).
  3. Record the answer with its source and level the card again. See [docs/compendium/08-open-questions.md#questions-most-first-time-builders-miss](../../../../docs/compendium/08-open-questions.md#questions-most-first-time-builders-miss).
  - Done when: The fact is confirmed in writing with a source, or the decision is changed so it no longer rests on it.
- [ ] **S-T5.warning-zdr-org-not-confirmed** Resolve warning zdr-org-not-confirmed: confirm the separate Enterprise org with ZDR (owner: compliance, Chief Compliance Officer, part A7)
  1. Explain that highly sensitive data needs a separate Enterprise org with ZDR. See [docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above](../../../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above).
  2. Confirm with the customer whether a zero-data-retention agreement covers the org this work runs in, record the answer as compliance.zdr_cover in the profile, then level again. See [docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt](../../../../docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt).
  - Done when: The profile's compliance.zdr_cover is in-place for this work, or the task's data class is lowered with the compliance owner.
- [ ] **S-T5.zdr-retention-agreement-first** Get the zero-data-retention agreement signed, then confirm the task runs only in that org (owner: compliance, Chief Compliance Officer, part A7)
  1. The profile's compliance.zdr_cover is planned or still open: no signed zero-data-retention agreement covers this work yet. Do not let the task go live until the agreement is signed and covers the org it runs in. See [docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt](../../../../docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt).
  2. Check the task's surfaces and connectors are all in the ZDR org. See [docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt](../../../../docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt).
  3. Record which features the ZDR org lacks that the task might expect. See [docs/compendium/12-orgs-and-ownership.md#recommended-starting-point](../../../../docs/compendium/12-orgs-and-ownership.md#recommended-starting-point).
  - Done when: The zero-data-retention agreement is signed and covers the org, compliance.zdr_cover is in-place, and compliance has confirmed the task runs only in the ZDR org.

## F-pipeline-upkeep-and-reporting: Pipeline upkeep and reporting

Kind: capability. Status: todo. 2 stories.

### S-T2: Update the CRM after a meeting

As a deal-team associate, I want my twin to draft the activity log and next-step fields on the Salesforce opportunity for me to approve so that Salesforce is up to date after every meeting.

Part A2. In pilot: yes. Priority: 2. Status: todo.

| Field | Value |
|---|---|
| Data class | highly-sensitive |
| Surface | client-skill; surfaces: claude-code |
| Autonomy | 1 to 3 |
| Connectors and identity | teams: user identity, read, always-allow; salesforce: user identity, write, blocked |
| Wall impact | soft |
| Inputs | teams (meeting notes or transcript); salesforce (opportunity) |
| Output and audience | Activity log and next-step fields, internal; to Salesforce opportunity |
| Delivery | A person sends or files it: the twin produces a draft, salesforce-update is Blocked at the starting level, and it opens at level 2. |
| Skill owner | Beatriz Halloran |
| Baseline | 10 per week x 15 minutes each x 18 users |
| Constraints | I want to approve each change before it's written. |
| Wanted change | Asked for, not planned: Later it could start when the meeting ends. |

**Acceptance criteria:**

1. To write: collect at least 3 real examples from Beatriz Halloran and write one eval case from each.
2. Keeps: I want to approve each change before it's written.
3. Plus: the skill triggers on the phrases its trigger evals list and stays quiet on the near-misses.
4. Plus: no web tools are used.
5. Plus: the twin writes nothing to the CRM at the starting level; a person files the result.
6. Plus: each tool call reaches the governance log.

Target: not set. Agree the scorecard targets with the sponsor before the pilot starts.

Ready to build: no
- examples: 0 counted examples (0 good, 0 bad); at least 3 needed.
- compliance-sign-off: Waiting for S-T2.compliance-sign-off: compliance signs the story off before it is built.

**Gated by:**

- open-question E4: Do the Salesforce and HubSpot admins confirm in writing that deal-team and investor-relations roles are fully separated? (spike SP-E4)
- open-question E6: Can Anthropic's range 160.79.104.0/21 be allowlisted? (spike SP-E6)
- open-question F3: Two to three real good and bad examples per skill, redacted. (spike SP-F3)
- open-question G1: Where does the governance log go (Splunk is the candidate), how is it hosted and who may read it? (spike SP-G1)
- open-question OD-9: ZDR addendum on the existing Enterprise org, which models qualify for ZDR, and the seat count. (spike SP-OD-9)
- open-question OD-11: Numeric scorecard targets for hours saved and edit rate on T1 and T2. (spike SP-OD-11)
- open-question OD-13: Keep the Salesforce and Microsoft 365 connectors out of chat and Cowork for the deal-team group. Due: before any pilot user connects. (spike SP-OD-13)
- sign-off compliance: Compliance has not signed the story off yet (S-T2.compliance-sign-off).

**Tasks:**

- [ ] **S-T2.compliance-sign-off** Get compliance's sign-off on the story before it is built (owner: compliance, Chief Compliance Officer, part A7)
  1. Check the story meets the definition of ready before compliance reads it. See [docs/playbook/04-stories.md#definition-of-ready-before-building](../../../../docs/playbook/04-stories.md#definition-of-ready-before-building).
  2. Compliance reads the story's fields, the levelled decisions for the task and its data controls. See [partner-kit/docs/design.md#73-rules-plan-fit-and-levelledjson](../../../../partner-kit/docs/design.md#73-rules-plan-fit-and-levelledjson).
  3. Record the sign-off, with the signer's name and the date, in the customer's engagement folder. See [engagements/README.md](../../../../engagements/README.md).
  - Done when: The sign-off is recorded in the customer's engagement folder with a name and a date.
- [ ] **S-T2.collect-examples** Collect 3 examples of the task from real work, each with the result a person expects (owner: skill-owner, Beatriz Halloran, part A8)
  1. Ask the people who do the task today for three recent, real examples of it. See [starter-kit/docs/authoring-skills.md#step-order](../../../../starter-kit/docs/authoring-skills.md#step-order).
  2. Record each example's inputs and the output a person would accept as done. See [starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals](../../../../starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals).
  3. Remove any data the examples must not carry into the repository, keeping their shape. See [docs/compendium/10-sensitive-data.md#design-patterns-that-keep-data-out-of-the-conversation](../../../../docs/compendium/10-sensitive-data.md#design-patterns-that-keep-data-out-of-the-conversation).
  - Done when: Three real examples, each with its inputs and its expected result, are stored where the evals can read them.
- [ ] **S-T2.write-evals** Write the evals from the examples and the story's acceptance criteria (owner: skill-engineer, part A8)
  1. Turn each example and each acceptance criterion into an eval case with its expected result. See [starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals](../../../../starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals).
  2. Put the eval cases in the files the kit expects, next to the skill. See [starter-kit/docs/authoring-skills.md#the-eval-files](../../../../starter-kit/docs/authoring-skills.md#the-eval-files).
  3. Run the evals once before any skill exists and keep the failing baseline. See [docs/compendium/03-skills-authoring.md#evaluate-first-then-iterate](../../../../docs/compendium/03-skills-authoring.md#evaluate-first-then-iterate).
  - Done when: Every acceptance criterion has at least one eval, and the evals run and fail without the skill.
- [ ] **S-T2.write-skill** Write the skill from the kit template until the evals pass (owner: skill-engineer, part A2)
  1. Copy the kit's skill template into the role plugin's skills folder, the one source of the skill for every runtime. See [starter-kit/templates/skill/README.md#copy-it](../../../../starter-kit/templates/skill/README.md#copy-it).
  2. Rename the copy to the skill's name. See [starter-kit/templates/skill/README.md#rename-it](../../../../starter-kit/templates/skill/README.md#rename-it).
  3. Fill in the description and the body, then rerun the evals until they pass. See [starter-kit/templates/skill/README.md#fill-it-in](../../../../starter-kit/templates/skill/README.md#fill-it-in).
  4. On client-skill, the skill loads from the role plugin, which an Owner publishes to claude.ai, Desktop and Cowork and which reaches a signed-in Claude Code. See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  5. On managed-agents, the skill loads from the agent's skills array (skills uploaded through the Skills API), or from a mounted GitHub repo's .claude/skills folder. See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  6. On managed-agents-self-hosted, load the skill the same two ways as hosted Managed Agents (Unverified: no compendium page says where a self-hosted deployment loads skills from). See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  7. On agent-sdk, the skill is files on disk in the runner's container, loaded through settingSources; there is no API to register a skill. See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  8. On claude-code-scheduled-task, put the skill where Claude Code loads skills: the project's .claude/skills folder or a plugin (Unverified: no compendium page says which of these a scheduled task loads). See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  9. On claude-tag-routine, give the routine the skill as its instructions (Unverified: no compendium page says whether a Claude Tag routine loads org skills). See [docs/compendium/05-decision-matrix.md#the-options](../../../../docs/compendium/05-decision-matrix.md#the-options).
  10. Make the skill keep these rules from the interviews, in the interviewee's words: I want to approve each change before it's written.. See [partner-kit/docs/design.md#42-persona-card-cardjson](../../../../partner-kit/docs/design.md#42-persona-card-cardjson).
  - Done when: The skill sits in the role plugin, it is where the task's runtime loads it from, and every eval for the story passes.
- [ ] **S-T2.trigger-evals** Write and run the trigger evals for the skill (owner: skill-engineer, part A8)
  1. Install skill-creator where the evals run. See [starter-kit/docs/authoring-skills.md#install-skill-creator](../../../../starter-kit/docs/authoring-skills.md#install-skill-creator).
  2. Write prompts that should and should not start the skill, as trigger evals. See [starter-kit/docs/authoring-skills.md#the-eval-files](../../../../starter-kit/docs/authoring-skills.md#the-eval-files).
  3. Run the trigger evals and tighten the description until they pass. See [docs/compendium/03-skills-authoring.md#writing-a-good-description](../../../../docs/compendium/03-skills-authoring.md#writing-a-good-description).
  - Done when: The skill starts on every should-trigger prompt and on none of the should-not prompts.
- [ ] **S-T2.second-review** Have a second person review the skill and its evals (owner: skill-owner, Beatriz Halloran, part A8)
  1. Open a pull request with the skill and its evals. See [docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often](../../../../docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often).
  2. Have someone other than the author review it against the definition of done. See [docs/playbook/04-stories.md#definition-of-done](../../../../docs/playbook/04-stories.md#definition-of-done).
  - Done when: A reviewer who did not write the skill has approved the pull request and the evals pass.
- [ ] **S-T2.publish-in-role-plugin** Publish the skill in the role plugin (owner: skill-engineer, part A9)
  1. Add the skill to the role plugin and bump the plugin's version. See [starter-kit/templates/role-plugin/README.md#steps](../../../../starter-kit/templates/role-plugin/README.md#steps).
  2. Publish the marketplace so the role's users get the new version. See [starter-kit/runbooks/identity-devices-publishing.md#6-publish-the-marketplace-and-its-plugins-to-the-right-groups](../../../../starter-kit/runbooks/identity-devices-publishing.md#6-publish-the-marketplace-and-its-plugins-to-the-right-groups).
  - Done when: A pilot user in the role sees the skill after the plugin updates.
- [ ] **S-T2.owner-handover** Hand the skill over to its owner (owner: skill-engineer, part A2)
  1. Show the skill owner where the skill lives: its folder in the role plugin, the one source for every runtime. See [starter-kit/templates/skill/README.md#copy-it](../../../../starter-kit/templates/skill/README.md#copy-it).
  2. Show them how to change an instruction in the skill and add an eval case for the change. See [starter-kit/templates/skill/README.md#fill-it-in](../../../../starter-kit/templates/skill/README.md#fill-it-in).
  3. Name who reviews a change before it is published: someone other than its author. See [docs/playbook/04-stories.md#definition-of-done](../../../../docs/playbook/04-stories.md#definition-of-done).
  4. Have the skill owner make one change while the engineer watches. See [docs/playbook/04-stories.md#definition-of-done](../../../../docs/playbook/04-stories.md#definition-of-done).
  - Done when: The skill owner has made one change to the skill with the engineer watching.
- [ ] **S-T2.connect-salesforce-runbook.salesforce** Connect it by following the kit's Salesforce hosted MCP runbook (salesforce) (owner: source-system-admin, acting: Director of IT, part A3)
  1. Choose per-user OAuth as the runbook explains before anything is created. See [starter-kit/runbooks/salesforce-hosted-mcp.md#4-choose-per-user-oauth-the-decision-you-cannot-undo](../../../../starter-kit/runbooks/salesforce-hosted-mcp.md#4-choose-per-user-oauth-the-decision-you-cannot-undo).
  2. Add the connector in the Claude org. See [starter-kit/runbooks/salesforce-hosted-mcp.md#6-add-the-connector-in-the-claude-org](../../../../starter-kit/runbooks/salesforce-hosted-mcp.md#6-add-the-connector-in-the-claude-org).
  3. Set the tool permissions first, then connect. See [starter-kit/runbooks/salesforce-hosted-mcp.md#7-set-tool-permissions-then-connect](../../../../starter-kit/runbooks/salesforce-hosted-mcp.md#7-set-tool-permissions-then-connect).
  - Done when: Each pilot user has connected with their own login and only the planned tools are enabled.
- [ ] **S-T2.connect-microsoft-365-runbook.teams** Connect it by following the kit's Microsoft 365 connector runbook (teams) (owner: source-system-admin, acting: Director of IT, part A3)
  1. Decide what to approve before granting consent. See [starter-kit/runbooks/microsoft-365-connector.md#2-decide-what-to-approve-before-consent](../../../../starter-kit/runbooks/microsoft-365-connector.md#2-decide-what-to-approve-before-consent).
  2. Grant tenant admin consent. See [starter-kit/runbooks/microsoft-365-connector.md#3-grant-tenant-admin-consent](../../../../starter-kit/runbooks/microsoft-365-connector.md#3-grant-tenant-admin-consent).
  3. Enable the connector for the right Claude group. See [starter-kit/runbooks/microsoft-365-connector.md#5-enable-the-connector-for-the-right-claude-group](../../../../starter-kit/runbooks/microsoft-365-connector.md#5-enable-the-connector-for-the-right-claude-group).
  - Done when: Consent is granted, the connector is enabled for the role's group only, and its write tools are set as the story's tool tasks say.
- [ ] **S-T2.tool-always-allow.salesforce-read** Set the connector tool to Always allow, as the levelled tools list says (salesforce-read) (owner: technical-owner, Director of IT, part A7)
  1. Open the connector's page in the Claude org and find the tool. See [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced).
  2. Set the tool to Always allow and record the change. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  - Done when: The tool is set to Always allow in the Claude org, as levelled.json says.
- [ ] **S-T2.tool-always-allow.teams-read** Set the connector tool to Always allow, as the levelled tools list says (teams-read) (owner: technical-owner, Director of IT, part A7)
  1. Open the connector's page in the Claude org and find the tool. See [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced).
  2. Set the tool to Always allow and record the change. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  - Done when: The tool is set to Always allow in the Claude org, as levelled.json says.
- [ ] **S-T2.tool-blocked.salesforce-update** Set the connector tool to Blocked, as the levelled tools list says (salesforce-update) (owner: technical-owner, Director of IT, part A7)
  1. Open the connector's page in the Claude org and find the tool. See [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced).
  2. Set the tool to Blocked, or leave it out of the role plugin, and record the change. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  - Done when: The tool is Blocked in the Claude org, as levelled.json says, and the twin cannot call it.
- [ ] **S-T2.deliver-draft** Agree where the twin's draft lands and who sends or files it while the twin cannot write it (owner: business-owner, RevOps manager, part A4)
  1. Agree with the pilot users that the twin ends in a draft, and that a person sends or files it while the twin cannot write it itself. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  2. Where the story's delivery says the write opens, agree the evidence that moves the task up to the level where the twin writes it itself. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  3. Name who puts the draft in its destination (Salesforce opportunity) and write down how, from the connector's runbook. See [starter-kit/runbooks/salesforce-hosted-mcp.md](../../../../starter-kit/runbooks/salesforce-hosted-mcp.md).
  - Done when: The business owner has agreed where each draft lands and who sends or files it, and the pilot users know.
- [ ] **S-T2.evidence-level-2** Gather the evidence to move the task up to level 2, act with approval (owner: business-owner, RevOps manager, part A8)
  1. Show the evals pass reliably at the current level. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Bring a month of scorecard results, with the edit rate, to the business owner. See [docs/compendium/15-governance-and-performance.md#measuring-performance](../../../../docs/compendium/15-governance-and-performance.md#measuring-performance).
  - Done when: The business owner has approved the move to level 2 on scorecard evidence, and every write or send tool the task uses at level 2 is at Needs approval; a task whose output a routine posts itself changes no tool setting.
- [ ] **S-T2.evidence-level-3** Gather the evidence to move the task up to level 3, act within an allowlist (owner: business-owner, RevOps manager, part A8)
  1. Confirm every allowlisted action can be undone or stays internal. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Show a stable eval pass rate, a low edit rate and few rejections at level 2. See [docs/compendium/15-governance-and-performance.md#measuring-performance](../../../../docs/compendium/15-governance-and-performance.md#measuring-performance).
  3. List the tools to set to Always allow and keep every other tool on Needs approval. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  - Done when: The business owner has approved the allowlist on scorecard evidence, and only those tools are Always allow.
- [ ] **S-T2.twin-marker-salesforce.salesforce** Deploy the Salesforce twin marker field (Last updated by twin) (salesforce) (owner: source-system-admin, acting: Director of IT, part A3)
  1. The CRM write tool salesforce-update is Blocked at the starting level and opens at level 2; set the marker up before it opens. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Deploy the marker field and its permission sets. See [starter-kit/connectors/salesforce/README.md#deploy-it-the-salesforce-admin-does-this](../../../../starter-kit/connectors/salesforce/README.md#deploy-it-the-salesforce-admin-does-this).
  3. Give edit access to the marker only to the users the twin acts for. See [starter-kit/connectors/salesforce/README.md#who-can-edit-the-field](../../../../starter-kit/connectors/salesforce/README.md#who-can-edit-the-field).
  - Done when: The marker field is deployed and only the role's users can set it.
- [ ] **S-T2.twin-marker-skill** Make the skill set the twin marker on every CRM write (owner: skill-engineer, part A2)
  1. The CRM write tool salesforce-update is Blocked at the starting level and opens at level 2; set the marker up before it opens. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Add a step to the skill that sets the twin marker with every write. See [docs/compendium/15-governance-and-performance.md#what-each-source-records](../../../../docs/compendium/15-governance-and-performance.md#what-each-source-records).
  3. Add an eval that fails when a write leaves the twin marker unset. See [starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals](../../../../starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals).
  - Done when: The evals show every CRM write the twin makes carries the twin marker.
- [ ] **S-T2.twin-marker-report** Report on the twin marker in the CRM's own history (owner: business-owner, RevOps manager, part A8)
  1. The CRM write tool salesforce-update is Blocked at the starting level and opens at level 2; set the marker up before it opens. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Build a CRM report of the records the twin marker shows the twin changed. See [docs/compendium/15-governance-and-performance.md#what-each-source-records](../../../../docs/compendium/15-governance-and-performance.md#what-each-source-records).
  3. Add the count of twin-written changes to the monthly scorecard. See [docs/compendium/15-governance-and-performance.md#measuring-performance](../../../../docs/compendium/15-governance-and-performance.md#measuring-performance).
  - Done when: The business owner can see in the CRM which changes the twin made.
- [ ] **S-T2.wall-test** Test the information wall with two users on either side before the pilot (owner: compliance, Chief Compliance Officer, part A7)
  1. List what the wall must keep apart in each system the task reads. See [docs/compendium/14-private-equity.md#what-a-wall-has-to-guarantee](../../../../docs/compendium/14-private-equity.md#what-a-wall-has-to-guarantee).
  2. Run the task as a user on each side of the wall and check neither sees the other side's records. See [docs/compendium/14-private-equity.md#where-a-twin-can-leak-across-a-wall](../../../../docs/compendium/14-private-equity.md#where-a-twin-can-leak-across-a-wall).
  3. Use the two-user test in the system's runbook where the kit has one. See [starter-kit/runbooks/salesforce-hosted-mcp.md#9-test-two-users-on-either-side-of-a-soft-wall](../../../../starter-kit/runbooks/salesforce-hosted-mcp.md#9-test-two-users-on-either-side-of-a-soft-wall).
  - Done when: Compliance has seen the two-user test pass for every walled system the task reads.
- [ ] **S-T2.web-tools-off** Check web search and web fetch are off wherever this task runs (owner: technical-owner, Director of IT, part A7)
  1. Check the settings baseline or the org setting turns web tools off on the task's surfaces. See [starter-kit/settings/README.md#keys](../../../../starter-kit/settings/README.md#keys).
  2. Try a web search in the task and confirm it is refused. See [docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above](../../../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above).
  - Done when: A web search or fetch attempted during the task is refused.
- [ ] **S-T2.confirm-unverified-decision.connectors.salesforce** Confirm the unverified fact behind this decision with Anthropic or the vendor before build (connectors.salesforce) (owner: solution-architect, part A3)
  1. Find the Unverified mark on the page the decision cites in levelled.json. See [partner-kit/docs/design.md#72-decision-values](../../../../partner-kit/docs/design.md#72-decision-values).
  2. Ask Anthropic or the vendor in writing, using the partner questions list. See [docs/compendium/12-orgs-and-ownership.md#questions-to-bring-to-anthropic-as-a-partner](../../../../docs/compendium/12-orgs-and-ownership.md#questions-to-bring-to-anthropic-as-a-partner).
  3. Record the answer with its source and level the card again. See [docs/compendium/08-open-questions.md#questions-most-first-time-builders-miss](../../../../docs/compendium/08-open-questions.md#questions-most-first-time-builders-miss).
  - Done when: The fact is confirmed in writing with a source, or the decision is changed so it no longer rests on it.
- [ ] **S-T2.warning-zdr-org-not-confirmed** Resolve warning zdr-org-not-confirmed: confirm the separate Enterprise org with ZDR (owner: compliance, Chief Compliance Officer, part A7)
  1. Explain that highly sensitive data needs a separate Enterprise org with ZDR. See [docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above](../../../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above).
  2. Confirm with the customer whether a zero-data-retention agreement covers the org this work runs in, record the answer as compliance.zdr_cover in the profile, then level again. See [docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt](../../../../docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt).
  - Done when: The profile's compliance.zdr_cover is in-place for this work, or the task's data class is lowered with the compliance owner.
- [ ] **S-T2.zdr-retention-agreement-first** Get the zero-data-retention agreement signed, then confirm the task runs only in that org (owner: compliance, Chief Compliance Officer, part A7)
  1. The profile's compliance.zdr_cover is planned or still open: no signed zero-data-retention agreement covers this work yet. Do not let the task go live until the agreement is signed and covers the org it runs in. See [docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt](../../../../docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt).
  2. Check the task's surfaces and connectors are all in the ZDR org. See [docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt](../../../../docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt).
  3. Record which features the ZDR org lacks that the task might expect. See [docs/compendium/12-orgs-and-ownership.md#recommended-starting-point](../../../../docs/compendium/12-orgs-and-ownership.md#recommended-starting-point).
  - Done when: The zero-data-retention agreement is signed and covers the org, compliance.zdr_cover is in-place, and compliance has confirmed the task runs only in the ZDR org.

### S-T3: Weekly pipeline summary for the Monday deal meeting

As a deal-team associate, I want my twin to write the Monday pipeline summary from the Salesforce pipeline report so that the pipeline view is right without anyone spending an hour on it.

Part A4. In pilot: no. Priority: 6. Status: todo.

| Field | Value |
|---|---|
| Data class | highly-sensitive |
| Surface | managed-agents-self-hosted; surfaces: none |
| Autonomy | 1 to 4 |
| Connectors and identity | salesforce: api-key-vault identity, read, always-allow; teams: api-key-vault identity, write, blocked |
| Wall impact | soft |
| Inputs | salesforce (pipeline report) |
| Output and audience | Pipeline summary, internal; to The deal team's channel in Microsoft Teams |
| Delivery | A person sends or files it: the twin produces a draft, teams-send is Blocked at the starting level, and it opens at level 2. |
| Skill owner | not named yet |
| Baseline | 1 per week x 60 minutes each x 18 users |

**Acceptance criteria:**

1. To write: collect at least 3 real examples from the skill owner (not named yet) and write one eval case from each.
2. Plus: no web tools are used.
3. Plus: each tool call reaches the governance log.

Target: not set. Agree the scorecard targets with the sponsor before the pilot starts.

Ready to build: no
- examples: 0 counted examples (0 good, 0 bad); at least 3 needed.
- compliance-sign-off: Waiting for S-T3.compliance-sign-off: compliance signs the story off before it is built.

**Gated by:**

- open-question E6: Can Anthropic's range 160.79.104.0/21 be allowlisted? (spike SP-E6)
- open-question F3: Two to three real good and bad examples per skill, redacted. (spike SP-F3)
- open-question OD-8: Identity for the hosted Monday summary, whether it may post to Teams, and whether a wrapper server is needed. Due: before T3 is built (after the pilot). (spike SP-OD-8)
- open-question OD-9: ZDR addendum on the existing Enterprise org, which models qualify for ZDR, and the seat count. (spike SP-OD-9)
- sign-off compliance: Compliance has not signed the story off yet (S-T3.compliance-sign-off).

**Tasks:**

- [ ] **S-T3.compliance-sign-off** Get compliance's sign-off on the story before it is built (owner: compliance, Chief Compliance Officer, part A7)
  1. Check the story meets the definition of ready before compliance reads it. See [docs/playbook/04-stories.md#definition-of-ready-before-building](../../../../docs/playbook/04-stories.md#definition-of-ready-before-building).
  2. Compliance reads the story's fields, the levelled decisions for the task and its data controls. See [partner-kit/docs/design.md#73-rules-plan-fit-and-levelledjson](../../../../partner-kit/docs/design.md#73-rules-plan-fit-and-levelledjson).
  3. Record the sign-off, with the signer's name and the date, in the customer's engagement folder. See [engagements/README.md](../../../../engagements/README.md).
  - Done when: The sign-off is recorded in the customer's engagement folder with a name and a date.
- [ ] **S-T3.collect-examples** Collect 3 examples of the task from real work, each with the result a person expects (owner: skill-owner, acting: Director of IT, part A8)
  1. Ask the people who do the task today for three recent, real examples of it. See [starter-kit/docs/authoring-skills.md#step-order](../../../../starter-kit/docs/authoring-skills.md#step-order).
  2. Record each example's inputs and the output a person would accept as done. See [starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals](../../../../starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals).
  3. Remove any data the examples must not carry into the repository, keeping their shape. See [docs/compendium/10-sensitive-data.md#design-patterns-that-keep-data-out-of-the-conversation](../../../../docs/compendium/10-sensitive-data.md#design-patterns-that-keep-data-out-of-the-conversation).
  - Done when: Three real examples, each with its inputs and its expected result, are stored where the evals can read them.
- [ ] **S-T3.write-evals** Write the evals from the examples and the story's acceptance criteria (owner: skill-engineer, part A8)
  1. Turn each example and each acceptance criterion into an eval case with its expected result. See [starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals](../../../../starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals).
  2. Put the eval cases in the files the kit expects, next to the skill. See [starter-kit/docs/authoring-skills.md#the-eval-files](../../../../starter-kit/docs/authoring-skills.md#the-eval-files).
  3. Run the evals once before any skill exists and keep the failing baseline. See [docs/compendium/03-skills-authoring.md#evaluate-first-then-iterate](../../../../docs/compendium/03-skills-authoring.md#evaluate-first-then-iterate).
  - Done when: Every acceptance criterion has at least one eval, and the evals run and fail without the skill.
- [ ] **S-T3.write-skill** Write the skill from the kit template until the evals pass (owner: skill-engineer, part A2)
  1. Copy the kit's skill template into the role plugin's skills folder, the one source of the skill for every runtime. See [starter-kit/templates/skill/README.md#copy-it](../../../../starter-kit/templates/skill/README.md#copy-it).
  2. Rename the copy to the skill's name. See [starter-kit/templates/skill/README.md#rename-it](../../../../starter-kit/templates/skill/README.md#rename-it).
  3. Fill in the description and the body, then rerun the evals until they pass. See [starter-kit/templates/skill/README.md#fill-it-in](../../../../starter-kit/templates/skill/README.md#fill-it-in).
  4. On client-skill, the skill loads from the role plugin, which an Owner publishes to claude.ai, Desktop and Cowork and which reaches a signed-in Claude Code. See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  5. On managed-agents, the skill loads from the agent's skills array (skills uploaded through the Skills API), or from a mounted GitHub repo's .claude/skills folder. See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  6. On managed-agents-self-hosted, load the skill the same two ways as hosted Managed Agents (Unverified: no compendium page says where a self-hosted deployment loads skills from). See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  7. On agent-sdk, the skill is files on disk in the runner's container, loaded through settingSources; there is no API to register a skill. See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  8. On claude-code-scheduled-task, put the skill where Claude Code loads skills: the project's .claude/skills folder or a plugin (Unverified: no compendium page says which of these a scheduled task loads). See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  9. On claude-tag-routine, give the routine the skill as its instructions (Unverified: no compendium page says whether a Claude Tag routine loads org skills). See [docs/compendium/05-decision-matrix.md#the-options](../../../../docs/compendium/05-decision-matrix.md#the-options).
  - Done when: The skill sits in the role plugin, it is where the task's runtime loads it from, and every eval for the story passes.
- [ ] **S-T3.trigger-evals** Write and run the trigger evals for the skill (owner: skill-engineer, part A8)
  1. Install skill-creator where the evals run. See [starter-kit/docs/authoring-skills.md#install-skill-creator](../../../../starter-kit/docs/authoring-skills.md#install-skill-creator).
  2. Write prompts that should and should not start the skill, as trigger evals. See [starter-kit/docs/authoring-skills.md#the-eval-files](../../../../starter-kit/docs/authoring-skills.md#the-eval-files).
  3. Run the trigger evals and tighten the description until they pass. See [docs/compendium/03-skills-authoring.md#writing-a-good-description](../../../../docs/compendium/03-skills-authoring.md#writing-a-good-description).
  - Done when: The skill starts on every should-trigger prompt and on none of the should-not prompts.
- [ ] **S-T3.second-review** Have a second person review the skill and its evals (owner: skill-owner, acting: Director of IT, part A8)
  1. Open a pull request with the skill and its evals. See [docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often](../../../../docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often).
  2. Have someone other than the author review it against the definition of done. See [docs/playbook/04-stories.md#definition-of-done](../../../../docs/playbook/04-stories.md#definition-of-done).
  - Done when: A reviewer who did not write the skill has approved the pull request and the evals pass.
- [ ] **S-T3.owner-handover** Hand the skill over to its owner (owner: skill-engineer, part A4)
  1. Show the skill owner where the skill lives: its folder in the role plugin, the one source for every runtime. See [starter-kit/templates/skill/README.md#copy-it](../../../../starter-kit/templates/skill/README.md#copy-it).
  2. Show them how to change an instruction in the skill and add an eval case for the change. See [starter-kit/templates/skill/README.md#fill-it-in](../../../../starter-kit/templates/skill/README.md#fill-it-in).
  3. Name who reviews a change before it is published: someone other than its author. See [docs/playbook/04-stories.md#definition-of-done](../../../../docs/playbook/04-stories.md#definition-of-done).
  4. Have the skill owner make one change while the engineer watches. See [docs/playbook/04-stories.md#definition-of-done](../../../../docs/playbook/04-stories.md#definition-of-done).
  - Done when: The skill owner has made one change to the skill with the engineer watching.
- [ ] **S-T3.setup-managed-agents-self-hosted** Set up self-hosted Managed Agents in the customer's environment and its schedule or trigger (owner: integration-engineer, part A4)
  1. Check the runbook's prerequisites and the environment the customer names. See [starter-kit/runbooks/managed-agents.md#before-you-start](../../../../starter-kit/runbooks/managed-agents.md#before-you-start).
  2. Stand up the self-hosted harness and sandbox in that environment. See [starter-kit/runbooks/managed-agents.md#self-hosted](../../../../starter-kit/runbooks/managed-agents.md#self-hosted).
  3. Define the agent with the skill, its tools and the tool permissions the plan names. See [starter-kit/runbooks/managed-agents.md#steps](../../../../starter-kit/runbooks/managed-agents.md#steps).
  4. Create the schedule or the trigger that starts each run, and pin the versions. See [starter-kit/runbooks/managed-agents.md#start-a-run](../../../../starter-kit/runbooks/managed-agents.md#start-a-run).
  5. Confirm the route keeps the retention the task needs. See [docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt](../../../../docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt).
  6. Run it once inside the customer's environment, check it, and hand it over. See [starter-kit/runbooks/managed-agents.md#check-it-worked](../../../../starter-kit/runbooks/managed-agents.md#check-it-worked).
  - Done when: The self-hosted agent has run once from its schedule or trigger inside the customer's environment.
- [ ] **S-T3.start-wiring** Build what starts each session from the task's event or schedule (owner: integration-engineer, part A4)
  1. For an event, build what receives it from the input system and calls the API to start one session for it (Unverified: page 05 says a session starts from an API call, not what turns the input system's event into that call). See [docs/compendium/05-decision-matrix.md#the-options](../../../../docs/compendium/05-decision-matrix.md#the-options).
  2. For a schedule, set up what runs it: a Managed Agents scheduled deployment, or for the Agent SDK a scheduler we host (Unverified: page 05 does not say whether a self-hosted deployment has scheduled deployments). See [docs/compendium/05-decision-matrix.md#the-options](../../../../docs/compendium/05-decision-matrix.md#the-options).
  3. Key each start by the event's id or the scheduled time, so a repeat of the same event starts no second session (our recommendation; no compendium page covers repeats). See [docs/compendium/05-decision-matrix.md](../../../../docs/compendium/05-decision-matrix.md).
  - Done when: One test event, or one scheduled time, starts exactly one session, and a repeat of the same event does not start a second.
- [ ] **S-T3.credentials-api-key-vault** Store the runtime's credentials in the customer's vault, read-only to the runtime (owner: technical-owner, Director of IT, part A5)
  1. Create a credential for each system the task uses, limited to the task's objects and actions. See [docs/compendium/11-connectors.md#what-exists-for-our-systems](../../../../docs/compendium/11-connectors.md#what-exists-for-our-systems).
  2. Store the credentials in the customer's vault and give the runtime read access only. See [docs/compendium/05-decision-matrix.md#decision-flow-our-recommendation](../../../../docs/compendium/05-decision-matrix.md#decision-flow-our-recommendation).
  3. Record who rotates each credential and how often. See [docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often](../../../../docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often).
  - Done when: The runtime reads every credential it needs from the vault and none is stored in code or configuration.
- [ ] **S-T3.success-check** Add an explicit success check to every run (owner: skill-engineer, part A8)
  1. Define what a successful run produces, beyond the session ending cleanly. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Make each run check that result and report a failure when it is missing. See [docs/compendium/15-governance-and-performance.md#what-each-source-records](../../../../docs/compendium/15-governance-and-performance.md#what-each-source-records).
  - Done when: A run that ends without its result is reported as failed, not as succeeded.
- [ ] **S-T3.missed-run-plan** Plan for missed runs and reconcile them (owner: integration-engineer, part A4)
  1. List how a run can be missed: a skipped schedule, a failed trigger or a webhook that gave up. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Add a reconciliation step that finds missed runs and reruns or reports them. See [docs/compendium/15-governance-and-performance.md#what-each-source-records](../../../../docs/compendium/15-governance-and-performance.md#what-each-source-records).
  3. Name the person who handles a run that still fails. See [docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often](../../../../docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often).
  - Done when: A missed run is found and handled within one cycle, by a named person.
- [ ] **S-T3.connect-salesforce-runbook.salesforce** Connect it by following the kit's Salesforce hosted MCP runbook (salesforce) (owner: source-system-admin, acting: Director of IT, part A3)
  1. Choose per-user OAuth as the runbook explains before anything is created. See [starter-kit/runbooks/salesforce-hosted-mcp.md#4-choose-per-user-oauth-the-decision-you-cannot-undo](../../../../starter-kit/runbooks/salesforce-hosted-mcp.md#4-choose-per-user-oauth-the-decision-you-cannot-undo).
  2. Add the connector in the Claude org. See [starter-kit/runbooks/salesforce-hosted-mcp.md#6-add-the-connector-in-the-claude-org](../../../../starter-kit/runbooks/salesforce-hosted-mcp.md#6-add-the-connector-in-the-claude-org).
  3. Set the tool permissions first, then connect. See [starter-kit/runbooks/salesforce-hosted-mcp.md#7-set-tool-permissions-then-connect](../../../../starter-kit/runbooks/salesforce-hosted-mcp.md#7-set-tool-permissions-then-connect).
  - Done when: Each pilot user has connected with their own login and only the planned tools are enabled.
- [ ] **S-T3.connect-microsoft-365-runbook.teams** Connect it by following the kit's Microsoft 365 connector runbook (teams) (owner: source-system-admin, acting: Director of IT, part A3)
  1. Decide what to approve before granting consent. See [starter-kit/runbooks/microsoft-365-connector.md#2-decide-what-to-approve-before-consent](../../../../starter-kit/runbooks/microsoft-365-connector.md#2-decide-what-to-approve-before-consent).
  2. Grant tenant admin consent. See [starter-kit/runbooks/microsoft-365-connector.md#3-grant-tenant-admin-consent](../../../../starter-kit/runbooks/microsoft-365-connector.md#3-grant-tenant-admin-consent).
  3. Enable the connector for the right Claude group. See [starter-kit/runbooks/microsoft-365-connector.md#5-enable-the-connector-for-the-right-claude-group](../../../../starter-kit/runbooks/microsoft-365-connector.md#5-enable-the-connector-for-the-right-claude-group).
  - Done when: Consent is granted, the connector is enabled for the role's group only, and its write tools are set as the story's tool tasks say.
- [ ] **S-T3.tool-always-allow.salesforce-read** Set the connector tool to Always allow, as the levelled tools list says (salesforce-read) (owner: technical-owner, Director of IT, part A7)
  1. Open the connector's page in the Claude org and find the tool. See [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced).
  2. Set the tool to Always allow and record the change. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  - Done when: The tool is set to Always allow in the Claude org, as levelled.json says.
- [ ] **S-T3.tool-blocked.teams-send** Set the connector tool to Blocked, as the levelled tools list says (teams-send) (owner: technical-owner, Director of IT, part A7)
  1. Open the connector's page in the Claude org and find the tool. See [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced).
  2. Set the tool to Blocked, or leave it out of the role plugin, and record the change. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  - Done when: The tool is Blocked in the Claude org, as levelled.json says, and the twin cannot call it.
- [ ] **S-T3.deliver-draft** Agree where the twin's draft lands and who sends or files it while the twin cannot write it (owner: business-owner, RevOps manager, part A4)
  1. Agree with the pilot users that the twin ends in a draft, and that a person sends or files it while the twin cannot write it itself. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  2. Where the story's delivery says the write opens, agree the evidence that moves the task up to the level where the twin writes it itself. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  3. Name who puts the draft in its destination (The deal team's channel in Microsoft Teams) and write down how, from the connector's runbook. See [starter-kit/runbooks/microsoft-365-connector.md](../../../../starter-kit/runbooks/microsoft-365-connector.md).
  - Done when: The business owner has agreed where each draft lands and who sends or files it, and the pilot users know.
- [ ] **S-T3.evidence-level-2** Gather the evidence to move the task up to level 2, act with approval (owner: business-owner, RevOps manager, part A8)
  1. Show the evals pass reliably at the current level. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Bring a month of scorecard results, with the edit rate, to the business owner. See [docs/compendium/15-governance-and-performance.md#measuring-performance](../../../../docs/compendium/15-governance-and-performance.md#measuring-performance).
  - Done when: The business owner has approved the move to level 2 on scorecard evidence, and every write or send tool the task uses at level 2 is at Needs approval; a task whose output a routine posts itself changes no tool setting.
- [ ] **S-T3.evidence-level-3** Gather the evidence to move the task up to level 3, act within an allowlist (owner: business-owner, RevOps manager, part A8)
  1. Confirm every allowlisted action can be undone or stays internal. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Show a stable eval pass rate, a low edit rate and few rejections at level 2. See [docs/compendium/15-governance-and-performance.md#measuring-performance](../../../../docs/compendium/15-governance-and-performance.md#measuring-performance).
  3. List the tools to set to Always allow and keep every other tool on Needs approval. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  - Done when: The business owner has approved the allowlist on scorecard evidence, and only those tools are Always allow.
- [ ] **S-T3.evidence-level-4** Decide every approval in advance before the task runs unattended at level 4 (owner: business-owner, RevOps manager, part A8)
  1. Write down each approval the task could need and decide it in policy, since an unattended run cannot ask. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Show the success check and the missed-run plan have worked for a month. See [docs/compendium/15-governance-and-performance.md#measuring-performance](../../../../docs/compendium/15-governance-and-performance.md#measuring-performance).
  - Done when: The business owner has approved unattended runs with every approval decided in policy.
- [ ] **S-T3.wall-test** Test the information wall with two users on either side before the pilot (owner: compliance, Chief Compliance Officer, part A7)
  1. List what the wall must keep apart in each system the task reads. See [docs/compendium/14-private-equity.md#what-a-wall-has-to-guarantee](../../../../docs/compendium/14-private-equity.md#what-a-wall-has-to-guarantee).
  2. Run the task as a user on each side of the wall and check neither sees the other side's records. See [docs/compendium/14-private-equity.md#where-a-twin-can-leak-across-a-wall](../../../../docs/compendium/14-private-equity.md#where-a-twin-can-leak-across-a-wall).
  3. Use the two-user test in the system's runbook where the kit has one. See [starter-kit/runbooks/salesforce-hosted-mcp.md#9-test-two-users-on-either-side-of-a-soft-wall](../../../../starter-kit/runbooks/salesforce-hosted-mcp.md#9-test-two-users-on-either-side-of-a-soft-wall).
  - Done when: Compliance has seen the two-user test pass for every walled system the task reads.
- [ ] **S-T3.web-tools-off** Check web search and web fetch are off wherever this task runs (owner: technical-owner, Director of IT, part A7)
  1. Check the settings baseline or the org setting turns web tools off on the task's surfaces. See [starter-kit/settings/README.md#keys](../../../../starter-kit/settings/README.md#keys).
  2. Try a web search in the task and confirm it is refused. See [docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above](../../../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above).
  - Done when: A web search or fetch attempted during the task is refused.
- [ ] **S-T3.confirm-unverified-decision.connectors.salesforce** Confirm the unverified fact behind this decision with Anthropic or the vendor before build (connectors.salesforce) (owner: solution-architect, part A3)
  1. Find the Unverified mark on the page the decision cites in levelled.json. See [partner-kit/docs/design.md#72-decision-values](../../../../partner-kit/docs/design.md#72-decision-values).
  2. Ask Anthropic or the vendor in writing, using the partner questions list. See [docs/compendium/12-orgs-and-ownership.md#questions-to-bring-to-anthropic-as-a-partner](../../../../docs/compendium/12-orgs-and-ownership.md#questions-to-bring-to-anthropic-as-a-partner).
  3. Record the answer with its source and level the card again. See [docs/compendium/08-open-questions.md#questions-most-first-time-builders-miss](../../../../docs/compendium/08-open-questions.md#questions-most-first-time-builders-miss).
  - Done when: The fact is confirmed in writing with a source, or the decision is changed so it no longer rests on it.
- [ ] **S-T3.warning-agent-sdk-cover-unverified** Resolve warning agent-sdk-cover-unverified: keep the Agent SDK out of the task until its cover is confirmed (owner: solution-architect, part A4)
  1. Check which retention or HIPAA cover the task needs. See [docs/compendium/05-decision-matrix.md#decision-flow-our-recommendation](../../../../docs/compendium/05-decision-matrix.md#decision-flow-our-recommendation).
  2. Ask Anthropic to confirm the Agent SDK's cover in writing, and use the confirmed route until then. See [docs/compendium/12-orgs-and-ownership.md#questions-to-bring-to-anthropic-as-a-partner](../../../../docs/compendium/12-orgs-and-ownership.md#questions-to-bring-to-anthropic-as-a-partner).
  - Done when: The task uses a route the pages confirm, or Anthropic's written confirmation is recorded with its source.
- [ ] **S-T3.warning-zdr-org-not-confirmed** Resolve warning zdr-org-not-confirmed: confirm the separate Enterprise org with ZDR (owner: compliance, Chief Compliance Officer, part A7)
  1. Explain that highly sensitive data needs a separate Enterprise org with ZDR. See [docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above](../../../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above).
  2. Confirm with the customer whether a zero-data-retention agreement covers the org this work runs in, record the answer as compliance.zdr_cover in the profile, then level again. See [docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt](../../../../docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt).
  - Done when: The profile's compliance.zdr_cover is in-place for this work, or the task's data class is lowered with the compliance owner.
- [ ] **S-T3.zdr-retention-agreement-first** Get the zero-data-retention agreement signed, then confirm the task runs only in that org (owner: compliance, Chief Compliance Officer, part A7)
  1. The profile's compliance.zdr_cover is planned or still open: no signed zero-data-retention agreement covers this work yet. Do not let the task go live until the agreement is signed and covers the org it runs in. See [docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt](../../../../docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt).
  2. Check the task's surfaces and connectors are all in the ZDR org. See [docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt](../../../../docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt).
  3. Record which features the ZDR org lacks that the task might expect. See [docs/compendium/12-orgs-and-ownership.md#recommended-starting-point](../../../../docs/compendium/12-orgs-and-ownership.md#recommended-starting-point).
  - Done when: The zero-data-retention agreement is signed and covers the org, compliance.zdr_cover is in-place, and compliance has confirmed the task runs only in the ZDR org.

## F-deal-screening: Deal screening

Kind: capability. Status: todo. 1 stories.

### S-T4: Screen an inbound CIM or teaser

As a deal-team associate, I want my twin to screen the CIM or teaser and suggest pursue or pass so that the screening notes are done by Wednesday.

Part A2. In pilot: no. Priority: 3. Status: todo.

| Field | Value |
|---|---|
| Data class | highly-sensitive |
| Surface | client-skill; surfaces: claude-code |
| Autonomy | 1 to 3 |
| Connectors and identity | sharepoint: user identity, read, always-allow; salesforce: user identity, read, always-allow |
| Wall impact | soft |
| Inputs | sharepoint (the CIM or teaser (an emailed document is saved to SharePoint first)); salesforce (prior contact with the company) |
| Output and audience | Screening summary with a pursue-or-pass suggestion, internal; to none (the conversation), for a principal |
| Delivery | The output stays in the conversation or a local file. |
| Skill owner | Beatriz Halloran |
| Baseline | 5 per week x 40 minutes each x unknown users |

**Acceptance criteria:**

1. To write: collect at least 3 real examples from Beatriz Halloran and write one eval case from each.
2. Plus: the skill triggers on the phrases its trigger evals list and stays quiet on the near-misses.
3. Plus: no web tools are used.
4. Plus: each tool call reaches the governance log.

Target: not set. Agree the scorecard targets with the sponsor before the pilot starts.

Ready to build: no
- examples: 0 counted examples (0 good, 0 bad); at least 3 needed.
- compliance-sign-off: Waiting for S-T4.compliance-sign-off: compliance signs the story off before it is built.

**Gated by:**

- open-question F3: Two to three real good and bad examples per skill, redacted. (spike SP-F3)
- open-question OD-1: Layer on Anthropic's private-equity and financial-analysis plugins, or build? (spike SP-OD-1)
- sign-off compliance: Compliance has not signed the story off yet (S-T4.compliance-sign-off).

**Tasks:**

- [ ] **S-T4.compliance-sign-off** Get compliance's sign-off on the story before it is built (owner: compliance, Chief Compliance Officer, part A7)
  1. Check the story meets the definition of ready before compliance reads it. See [docs/playbook/04-stories.md#definition-of-ready-before-building](../../../../docs/playbook/04-stories.md#definition-of-ready-before-building).
  2. Compliance reads the story's fields, the levelled decisions for the task and its data controls. See [partner-kit/docs/design.md#73-rules-plan-fit-and-levelledjson](../../../../partner-kit/docs/design.md#73-rules-plan-fit-and-levelledjson).
  3. Record the sign-off, with the signer's name and the date, in the customer's engagement folder. See [engagements/README.md](../../../../engagements/README.md).
  - Done when: The sign-off is recorded in the customer's engagement folder with a name and a date.
- [ ] **S-T4.collect-examples** Collect 3 examples of the task from real work, each with the result a person expects (owner: skill-owner, Beatriz Halloran, part A8)
  1. Ask the people who do the task today for three recent, real examples of it. See [starter-kit/docs/authoring-skills.md#step-order](../../../../starter-kit/docs/authoring-skills.md#step-order).
  2. Record each example's inputs and the output a person would accept as done. See [starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals](../../../../starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals).
  3. Remove any data the examples must not carry into the repository, keeping their shape. See [docs/compendium/10-sensitive-data.md#design-patterns-that-keep-data-out-of-the-conversation](../../../../docs/compendium/10-sensitive-data.md#design-patterns-that-keep-data-out-of-the-conversation).
  - Done when: Three real examples, each with its inputs and its expected result, are stored where the evals can read them.
- [ ] **S-T4.write-evals** Write the evals from the examples and the story's acceptance criteria (owner: skill-engineer, part A8)
  1. Turn each example and each acceptance criterion into an eval case with its expected result. See [starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals](../../../../starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals).
  2. Put the eval cases in the files the kit expects, next to the skill. See [starter-kit/docs/authoring-skills.md#the-eval-files](../../../../starter-kit/docs/authoring-skills.md#the-eval-files).
  3. Run the evals once before any skill exists and keep the failing baseline. See [docs/compendium/03-skills-authoring.md#evaluate-first-then-iterate](../../../../docs/compendium/03-skills-authoring.md#evaluate-first-then-iterate).
  - Done when: Every acceptance criterion has at least one eval, and the evals run and fail without the skill.
- [ ] **S-T4.write-skill** Write the skill from deal-screening until the evals pass (owner: skill-engineer, part A2)
  1. Start from deal-screening (claude-for-financial-services: private-equity): Adapt, for T4. See [docs/compendium/17-anthropic-pe-plugins-review.md#1-whats-in-private-equity](../../../../docs/compendium/17-anthropic-pe-plugins-review.md#1-whats-in-private-equity).
  2. Copy the kit's skill template into the role plugin's skills folder, the one source of the skill for every runtime. See [starter-kit/templates/skill/README.md#copy-it](../../../../starter-kit/templates/skill/README.md#copy-it).
  3. Rename the copy to the skill's name. See [starter-kit/templates/skill/README.md#rename-it](../../../../starter-kit/templates/skill/README.md#rename-it).
  4. Fill in the description and the body, then rerun the evals until they pass. See [starter-kit/templates/skill/README.md#fill-it-in](../../../../starter-kit/templates/skill/README.md#fill-it-in).
  5. On client-skill, the skill loads from the role plugin, which an Owner publishes to claude.ai, Desktop and Cowork and which reaches a signed-in Claude Code. See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  6. On managed-agents, the skill loads from the agent's skills array (skills uploaded through the Skills API), or from a mounted GitHub repo's .claude/skills folder. See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  7. On managed-agents-self-hosted, load the skill the same two ways as hosted Managed Agents (Unverified: no compendium page says where a self-hosted deployment loads skills from). See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  8. On agent-sdk, the skill is files on disk in the runner's container, loaded through settingSources; there is no API to register a skill. See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  9. On claude-code-scheduled-task, put the skill where Claude Code loads skills: the project's .claude/skills folder or a plugin (Unverified: no compendium page says which of these a scheduled task loads). See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  10. On claude-tag-routine, give the routine the skill as its instructions (Unverified: no compendium page says whether a Claude Tag routine loads org skills). See [docs/compendium/05-decision-matrix.md#the-options](../../../../docs/compendium/05-decision-matrix.md#the-options).
  - Done when: The skill sits in the role plugin, it is where the task's runtime loads it from, and every eval for the story passes.
- [ ] **S-T4.trigger-evals** Write and run the trigger evals for the skill (owner: skill-engineer, part A8)
  1. Install skill-creator where the evals run. See [starter-kit/docs/authoring-skills.md#install-skill-creator](../../../../starter-kit/docs/authoring-skills.md#install-skill-creator).
  2. Write prompts that should and should not start the skill, as trigger evals. See [starter-kit/docs/authoring-skills.md#the-eval-files](../../../../starter-kit/docs/authoring-skills.md#the-eval-files).
  3. Run the trigger evals and tighten the description until they pass. See [docs/compendium/03-skills-authoring.md#writing-a-good-description](../../../../docs/compendium/03-skills-authoring.md#writing-a-good-description).
  - Done when: The skill starts on every should-trigger prompt and on none of the should-not prompts.
- [ ] **S-T4.second-review** Have a second person review the skill and its evals (owner: skill-owner, Beatriz Halloran, part A8)
  1. Open a pull request with the skill and its evals. See [docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often](../../../../docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often).
  2. Have someone other than the author review it against the definition of done. See [docs/playbook/04-stories.md#definition-of-done](../../../../docs/playbook/04-stories.md#definition-of-done).
  - Done when: A reviewer who did not write the skill has approved the pull request and the evals pass.
- [ ] **S-T4.publish-in-role-plugin** Publish the skill in the role plugin (owner: skill-engineer, part A9)
  1. Add the skill to the role plugin and bump the plugin's version. See [starter-kit/templates/role-plugin/README.md#steps](../../../../starter-kit/templates/role-plugin/README.md#steps).
  2. Publish the marketplace so the role's users get the new version. See [starter-kit/runbooks/identity-devices-publishing.md#6-publish-the-marketplace-and-its-plugins-to-the-right-groups](../../../../starter-kit/runbooks/identity-devices-publishing.md#6-publish-the-marketplace-and-its-plugins-to-the-right-groups).
  - Done when: A pilot user in the role sees the skill after the plugin updates.
- [ ] **S-T4.owner-handover** Hand the skill over to its owner (owner: skill-engineer, part A2)
  1. Show the skill owner where the skill lives: its folder in the role plugin, the one source for every runtime. See [starter-kit/templates/skill/README.md#copy-it](../../../../starter-kit/templates/skill/README.md#copy-it).
  2. Show them how to change an instruction in the skill and add an eval case for the change. See [starter-kit/templates/skill/README.md#fill-it-in](../../../../starter-kit/templates/skill/README.md#fill-it-in).
  3. Name who reviews a change before it is published: someone other than its author. See [docs/playbook/04-stories.md#definition-of-done](../../../../docs/playbook/04-stories.md#definition-of-done).
  4. Have the skill owner make one change while the engineer watches. See [docs/playbook/04-stories.md#definition-of-done](../../../../docs/playbook/04-stories.md#definition-of-done).
  - Done when: The skill owner has made one change to the skill with the engineer watching.
- [ ] **S-T4.connect-salesforce-runbook.salesforce** Connect it by following the kit's Salesforce hosted MCP runbook (salesforce) (owner: source-system-admin, acting: Director of IT, part A3)
  1. Choose per-user OAuth as the runbook explains before anything is created. See [starter-kit/runbooks/salesforce-hosted-mcp.md#4-choose-per-user-oauth-the-decision-you-cannot-undo](../../../../starter-kit/runbooks/salesforce-hosted-mcp.md#4-choose-per-user-oauth-the-decision-you-cannot-undo).
  2. Add the connector in the Claude org. See [starter-kit/runbooks/salesforce-hosted-mcp.md#6-add-the-connector-in-the-claude-org](../../../../starter-kit/runbooks/salesforce-hosted-mcp.md#6-add-the-connector-in-the-claude-org).
  3. Set the tool permissions first, then connect. See [starter-kit/runbooks/salesforce-hosted-mcp.md#7-set-tool-permissions-then-connect](../../../../starter-kit/runbooks/salesforce-hosted-mcp.md#7-set-tool-permissions-then-connect).
  - Done when: Each pilot user has connected with their own login and only the planned tools are enabled.
- [ ] **S-T4.connect-microsoft-365-runbook.sharepoint** Connect it by following the kit's Microsoft 365 connector runbook (sharepoint) (owner: source-system-admin, acting: Director of IT, part A3)
  1. Decide what to approve before granting consent. See [starter-kit/runbooks/microsoft-365-connector.md#2-decide-what-to-approve-before-consent](../../../../starter-kit/runbooks/microsoft-365-connector.md#2-decide-what-to-approve-before-consent).
  2. Grant tenant admin consent. See [starter-kit/runbooks/microsoft-365-connector.md#3-grant-tenant-admin-consent](../../../../starter-kit/runbooks/microsoft-365-connector.md#3-grant-tenant-admin-consent).
  3. Enable the connector for the right Claude group. See [starter-kit/runbooks/microsoft-365-connector.md#5-enable-the-connector-for-the-right-claude-group](../../../../starter-kit/runbooks/microsoft-365-connector.md#5-enable-the-connector-for-the-right-claude-group).
  - Done when: Consent is granted, the connector is enabled for the role's group only, and its write tools are set as the story's tool tasks say.
- [ ] **S-T4.tool-always-allow.salesforce-read** Set the connector tool to Always allow, as the levelled tools list says (salesforce-read) (owner: technical-owner, Director of IT, part A7)
  1. Open the connector's page in the Claude org and find the tool. See [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced).
  2. Set the tool to Always allow and record the change. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  - Done when: The tool is set to Always allow in the Claude org, as levelled.json says.
- [ ] **S-T4.tool-always-allow.sharepoint-read** Set the connector tool to Always allow, as the levelled tools list says (sharepoint-read) (owner: technical-owner, Director of IT, part A7)
  1. Open the connector's page in the Claude org and find the tool. See [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced).
  2. Set the tool to Always allow and record the change. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  - Done when: The tool is set to Always allow in the Claude org, as levelled.json says.
- [ ] **S-T4.evidence-level-2** Gather the evidence to move the task up to level 2, act with approval (owner: business-owner, RevOps manager, part A8)
  1. Show the evals pass reliably at the current level. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Bring a month of scorecard results, with the edit rate, to the business owner. See [docs/compendium/15-governance-and-performance.md#measuring-performance](../../../../docs/compendium/15-governance-and-performance.md#measuring-performance).
  - Done when: The business owner has approved the move to level 2 on scorecard evidence, and every write or send tool the task uses at level 2 is at Needs approval; a task whose output a routine posts itself changes no tool setting.
- [ ] **S-T4.evidence-level-3** Gather the evidence to move the task up to level 3, act within an allowlist (owner: business-owner, RevOps manager, part A8)
  1. Confirm every allowlisted action can be undone or stays internal. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Show a stable eval pass rate, a low edit rate and few rejections at level 2. See [docs/compendium/15-governance-and-performance.md#measuring-performance](../../../../docs/compendium/15-governance-and-performance.md#measuring-performance).
  3. List the tools to set to Always allow and keep every other tool on Needs approval. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  - Done when: The business owner has approved the allowlist on scorecard evidence, and only those tools are Always allow.
- [ ] **S-T4.wall-test** Test the information wall with two users on either side before the pilot (owner: compliance, Chief Compliance Officer, part A7)
  1. List what the wall must keep apart in each system the task reads. See [docs/compendium/14-private-equity.md#what-a-wall-has-to-guarantee](../../../../docs/compendium/14-private-equity.md#what-a-wall-has-to-guarantee).
  2. Run the task as a user on each side of the wall and check neither sees the other side's records. See [docs/compendium/14-private-equity.md#where-a-twin-can-leak-across-a-wall](../../../../docs/compendium/14-private-equity.md#where-a-twin-can-leak-across-a-wall).
  3. Use the two-user test in the system's runbook where the kit has one. See [starter-kit/runbooks/salesforce-hosted-mcp.md#9-test-two-users-on-either-side-of-a-soft-wall](../../../../starter-kit/runbooks/salesforce-hosted-mcp.md#9-test-two-users-on-either-side-of-a-soft-wall).
  - Done when: Compliance has seen the two-user test pass for every walled system the task reads.
- [ ] **S-T4.web-tools-off** Check web search and web fetch are off wherever this task runs (owner: technical-owner, Director of IT, part A7)
  1. Check the settings baseline or the org setting turns web tools off on the task's surfaces. See [starter-kit/settings/README.md#keys](../../../../starter-kit/settings/README.md#keys).
  2. Try a web search in the task and confirm it is refused. See [docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above](../../../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above).
  - Done when: A web search or fetch attempted during the task is refused.
- [ ] **S-T4.confirm-unverified-decision.connectors.salesforce** Confirm the unverified fact behind this decision with Anthropic or the vendor before build (connectors.salesforce) (owner: solution-architect, part A3)
  1. Find the Unverified mark on the page the decision cites in levelled.json. See [partner-kit/docs/design.md#72-decision-values](../../../../partner-kit/docs/design.md#72-decision-values).
  2. Ask Anthropic or the vendor in writing, using the partner questions list. See [docs/compendium/12-orgs-and-ownership.md#questions-to-bring-to-anthropic-as-a-partner](../../../../docs/compendium/12-orgs-and-ownership.md#questions-to-bring-to-anthropic-as-a-partner).
  3. Record the answer with its source and level the card again. See [docs/compendium/08-open-questions.md#questions-most-first-time-builders-miss](../../../../docs/compendium/08-open-questions.md#questions-most-first-time-builders-miss).
  - Done when: The fact is confirmed in writing with a source, or the decision is changed so it no longer rests on it.
- [ ] **S-T4.warning-high-cost-ceiling-unconfirmed** Resolve warning high-cost-ceiling-unconfirmed: confirm the ceiling of a task whose mistakes cost a lot (owner: business-owner, RevOps manager, part A7)
  1. Read which cap applied and why in levelled.json, and note that page 06 has no rule for the cost of a mistake. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Confirm the cap with the customer, or record a lower ceiling as an override on the card, then level again. See [partner-kit/docs/design.md#73-rules-plan-fit-and-levelledjson](../../../../partner-kit/docs/design.md#73-rules-plan-fit-and-levelledjson).
  - Done when: The customer has confirmed the ceiling, or a lower ceiling is on the card as an override with a reason and an approver.
- [ ] **S-T4.warning-zdr-org-not-confirmed** Resolve warning zdr-org-not-confirmed: confirm the separate Enterprise org with ZDR (owner: compliance, Chief Compliance Officer, part A7)
  1. Explain that highly sensitive data needs a separate Enterprise org with ZDR. See [docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above](../../../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above).
  2. Confirm with the customer whether a zero-data-retention agreement covers the org this work runs in, record the answer as compliance.zdr_cover in the profile, then level again. See [docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt](../../../../docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt).
  - Done when: The profile's compliance.zdr_cover is in-place for this work, or the task's data class is lowered with the compliance owner.
- [ ] **S-T4.zdr-retention-agreement-first** Get the zero-data-retention agreement signed, then confirm the task runs only in that org (owner: compliance, Chief Compliance Officer, part A7)
  1. The profile's compliance.zdr_cover is planned or still open: no signed zero-data-retention agreement covers this work yet. Do not let the task go live until the agreement is signed and covers the org it runs in. See [docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt](../../../../docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt).
  2. Check the task's surfaces and connectors are all in the ZDR org. See [docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt](../../../../docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt).
  3. Record which features the ZDR org lacks that the task might expect. See [docs/compendium/12-orgs-and-ownership.md#recommended-starting-point](../../../../docs/compendium/12-orgs-and-ownership.md#recommended-starting-point).
  - Done when: The zero-data-retention agreement is signed and covers the org, compliance.zdr_cover is in-place, and compliance has confirmed the task runs only in the ZDR org.

## F-investment-committee-drafting: Investment committee drafting

Kind: capability. Status: todo. 1 stories.

### S-T6: Draft a section of an investment committee memo from diligence notes

As a deal-team associate, I want my twin to produce the draft memo section so that I get back the 240 minutes it takes me each time.

(Statement drafted by the kit: confirm the wording with the interviewee.)

Part A2. In pilot: no. Priority: 5. Status: todo.

| Field | Value |
|---|---|
| Data class | highly-sensitive |
| Surface | client-skill; surfaces: claude-code |
| Autonomy | 1 to 3 |
| Connectors and identity | sharepoint: user identity, read, always-allow |
| Wall impact | soft |
| Inputs | sharepoint (diligence notes and data-room files) |
| Output and audience | Draft memo section, internal; to none (the conversation), for the partners |
| Delivery | The output stays in the conversation or a local file. |
| Skill owner | Ravindra Sorensen |
| Baseline | 0.46 per week x 240 minutes each x unknown users |
| Constraints | It's always a draft and always reviewed. |

**Acceptance criteria:**

1. To write: collect at least 3 real examples from Ravindra Sorensen and write one eval case from each.
2. Keeps: It's always a draft and always reviewed.
3. Plus: the skill triggers on the phrases its trigger evals list and stays quiet on the near-misses.
4. Plus: no web tools are used.
5. Plus: each tool call reaches the governance log.

Target: not set. Agree the scorecard targets with the sponsor before the pilot starts.

Ready to build: no
- examples: 0 counted examples (0 good, 0 bad); at least 3 needed.
- compliance-sign-off: Waiting for S-T6.compliance-sign-off: compliance signs the story off before it is built.

**Gated by:**

- open-question F3: Two to three real good and bad examples per skill, redacted. (spike SP-F3)
- open-question OD-1: Layer on Anthropic's private-equity and financial-analysis plugins, or build? (spike SP-OD-1)
- sign-off compliance: Compliance has not signed the story off yet (S-T6.compliance-sign-off).

**Tasks:**

- [ ] **S-T6.compliance-sign-off** Get compliance's sign-off on the story before it is built (owner: compliance, Chief Compliance Officer, part A7)
  1. Check the story meets the definition of ready before compliance reads it. See [docs/playbook/04-stories.md#definition-of-ready-before-building](../../../../docs/playbook/04-stories.md#definition-of-ready-before-building).
  2. Compliance reads the story's fields, the levelled decisions for the task and its data controls. See [partner-kit/docs/design.md#73-rules-plan-fit-and-levelledjson](../../../../partner-kit/docs/design.md#73-rules-plan-fit-and-levelledjson).
  3. Record the sign-off, with the signer's name and the date, in the customer's engagement folder. See [engagements/README.md](../../../../engagements/README.md).
  - Done when: The sign-off is recorded in the customer's engagement folder with a name and a date.
- [ ] **S-T6.collect-examples** Collect 3 examples of the task from real work, each with the result a person expects (owner: skill-owner, Ravindra Sorensen, part A8)
  1. Ask the people who do the task today for three recent, real examples of it. See [starter-kit/docs/authoring-skills.md#step-order](../../../../starter-kit/docs/authoring-skills.md#step-order).
  2. Record each example's inputs and the output a person would accept as done. See [starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals](../../../../starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals).
  3. Remove any data the examples must not carry into the repository, keeping their shape. See [docs/compendium/10-sensitive-data.md#design-patterns-that-keep-data-out-of-the-conversation](../../../../docs/compendium/10-sensitive-data.md#design-patterns-that-keep-data-out-of-the-conversation).
  - Done when: Three real examples, each with its inputs and its expected result, are stored where the evals can read them.
- [ ] **S-T6.write-evals** Write the evals from the examples and the story's acceptance criteria (owner: skill-engineer, part A8)
  1. Turn each example and each acceptance criterion into an eval case with its expected result. See [starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals](../../../../starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals).
  2. Put the eval cases in the files the kit expects, next to the skill. See [starter-kit/docs/authoring-skills.md#the-eval-files](../../../../starter-kit/docs/authoring-skills.md#the-eval-files).
  3. Run the evals once before any skill exists and keep the failing baseline. See [docs/compendium/03-skills-authoring.md#evaluate-first-then-iterate](../../../../docs/compendium/03-skills-authoring.md#evaluate-first-then-iterate).
  - Done when: Every acceptance criterion has at least one eval, and the evals run and fail without the skill.
- [ ] **S-T6.write-skill** Write the skill from ic-memo until the evals pass (owner: skill-engineer, part A2)
  1. Start from ic-memo (claude-for-financial-services: private-equity): Adapt, for T6. See [docs/compendium/17-anthropic-pe-plugins-review.md#1-whats-in-private-equity](../../../../docs/compendium/17-anthropic-pe-plugins-review.md#1-whats-in-private-equity).
  2. Copy the kit's skill template into the role plugin's skills folder, the one source of the skill for every runtime. See [starter-kit/templates/skill/README.md#copy-it](../../../../starter-kit/templates/skill/README.md#copy-it).
  3. Rename the copy to the skill's name. See [starter-kit/templates/skill/README.md#rename-it](../../../../starter-kit/templates/skill/README.md#rename-it).
  4. Fill in the description and the body, then rerun the evals until they pass. See [starter-kit/templates/skill/README.md#fill-it-in](../../../../starter-kit/templates/skill/README.md#fill-it-in).
  5. On client-skill, the skill loads from the role plugin, which an Owner publishes to claude.ai, Desktop and Cowork and which reaches a signed-in Claude Code. See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  6. On managed-agents, the skill loads from the agent's skills array (skills uploaded through the Skills API), or from a mounted GitHub repo's .claude/skills folder. See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  7. On managed-agents-self-hosted, load the skill the same two ways as hosted Managed Agents (Unverified: no compendium page says where a self-hosted deployment loads skills from). See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  8. On agent-sdk, the skill is files on disk in the runner's container, loaded through settingSources; there is no API to register a skill. See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  9. On claude-code-scheduled-task, put the skill where Claude Code loads skills: the project's .claude/skills folder or a plugin (Unverified: no compendium page says which of these a scheduled task loads). See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  10. On claude-tag-routine, give the routine the skill as its instructions (Unverified: no compendium page says whether a Claude Tag routine loads org skills). See [docs/compendium/05-decision-matrix.md#the-options](../../../../docs/compendium/05-decision-matrix.md#the-options).
  11. Make the skill keep these rules from the interviews, in the interviewee's words: It's always a draft and always reviewed.. See [partner-kit/docs/design.md#42-persona-card-cardjson](../../../../partner-kit/docs/design.md#42-persona-card-cardjson).
  - Done when: The skill sits in the role plugin, it is where the task's runtime loads it from, and every eval for the story passes.
- [ ] **S-T6.trigger-evals** Write and run the trigger evals for the skill (owner: skill-engineer, part A8)
  1. Install skill-creator where the evals run. See [starter-kit/docs/authoring-skills.md#install-skill-creator](../../../../starter-kit/docs/authoring-skills.md#install-skill-creator).
  2. Write prompts that should and should not start the skill, as trigger evals. See [starter-kit/docs/authoring-skills.md#the-eval-files](../../../../starter-kit/docs/authoring-skills.md#the-eval-files).
  3. Run the trigger evals and tighten the description until they pass. See [docs/compendium/03-skills-authoring.md#writing-a-good-description](../../../../docs/compendium/03-skills-authoring.md#writing-a-good-description).
  - Done when: The skill starts on every should-trigger prompt and on none of the should-not prompts.
- [ ] **S-T6.second-review** Have a second person review the skill and its evals (owner: skill-owner, Ravindra Sorensen, part A8)
  1. Open a pull request with the skill and its evals. See [docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often](../../../../docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often).
  2. Have someone other than the author review it against the definition of done. See [docs/playbook/04-stories.md#definition-of-done](../../../../docs/playbook/04-stories.md#definition-of-done).
  - Done when: A reviewer who did not write the skill has approved the pull request and the evals pass.
- [ ] **S-T6.publish-in-role-plugin** Publish the skill in the role plugin (owner: skill-engineer, part A9)
  1. Add the skill to the role plugin and bump the plugin's version. See [starter-kit/templates/role-plugin/README.md#steps](../../../../starter-kit/templates/role-plugin/README.md#steps).
  2. Publish the marketplace so the role's users get the new version. See [starter-kit/runbooks/identity-devices-publishing.md#6-publish-the-marketplace-and-its-plugins-to-the-right-groups](../../../../starter-kit/runbooks/identity-devices-publishing.md#6-publish-the-marketplace-and-its-plugins-to-the-right-groups).
  - Done when: A pilot user in the role sees the skill after the plugin updates.
- [ ] **S-T6.owner-handover** Hand the skill over to its owner (owner: skill-engineer, part A2)
  1. Show the skill owner where the skill lives: its folder in the role plugin, the one source for every runtime. See [starter-kit/templates/skill/README.md#copy-it](../../../../starter-kit/templates/skill/README.md#copy-it).
  2. Show them how to change an instruction in the skill and add an eval case for the change. See [starter-kit/templates/skill/README.md#fill-it-in](../../../../starter-kit/templates/skill/README.md#fill-it-in).
  3. Name who reviews a change before it is published: someone other than its author. See [docs/playbook/04-stories.md#definition-of-done](../../../../docs/playbook/04-stories.md#definition-of-done).
  4. Have the skill owner make one change while the engineer watches. See [docs/playbook/04-stories.md#definition-of-done](../../../../docs/playbook/04-stories.md#definition-of-done).
  - Done when: The skill owner has made one change to the skill with the engineer watching.
- [ ] **S-T6.connect-microsoft-365-runbook.sharepoint** Connect it by following the kit's Microsoft 365 connector runbook (sharepoint) (owner: source-system-admin, acting: Director of IT, part A3)
  1. Decide what to approve before granting consent. See [starter-kit/runbooks/microsoft-365-connector.md#2-decide-what-to-approve-before-consent](../../../../starter-kit/runbooks/microsoft-365-connector.md#2-decide-what-to-approve-before-consent).
  2. Grant tenant admin consent. See [starter-kit/runbooks/microsoft-365-connector.md#3-grant-tenant-admin-consent](../../../../starter-kit/runbooks/microsoft-365-connector.md#3-grant-tenant-admin-consent).
  3. Enable the connector for the right Claude group. See [starter-kit/runbooks/microsoft-365-connector.md#5-enable-the-connector-for-the-right-claude-group](../../../../starter-kit/runbooks/microsoft-365-connector.md#5-enable-the-connector-for-the-right-claude-group).
  - Done when: Consent is granted, the connector is enabled for the role's group only, and its write tools are set as the story's tool tasks say.
- [ ] **S-T6.tool-always-allow.sharepoint-read** Set the connector tool to Always allow, as the levelled tools list says (sharepoint-read) (owner: technical-owner, Director of IT, part A7)
  1. Open the connector's page in the Claude org and find the tool. See [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced).
  2. Set the tool to Always allow and record the change. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  - Done when: The tool is set to Always allow in the Claude org, as levelled.json says.
- [ ] **S-T6.evidence-level-2** Gather the evidence to move the task up to level 2, act with approval (owner: business-owner, RevOps manager, part A8)
  1. Show the evals pass reliably at the current level. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Bring a month of scorecard results, with the edit rate, to the business owner. See [docs/compendium/15-governance-and-performance.md#measuring-performance](../../../../docs/compendium/15-governance-and-performance.md#measuring-performance).
  - Done when: The business owner has approved the move to level 2 on scorecard evidence, and every write or send tool the task uses at level 2 is at Needs approval; a task whose output a routine posts itself changes no tool setting.
- [ ] **S-T6.evidence-level-3** Gather the evidence to move the task up to level 3, act within an allowlist (owner: business-owner, RevOps manager, part A8)
  1. Confirm every allowlisted action can be undone or stays internal. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Show a stable eval pass rate, a low edit rate and few rejections at level 2. See [docs/compendium/15-governance-and-performance.md#measuring-performance](../../../../docs/compendium/15-governance-and-performance.md#measuring-performance).
  3. List the tools to set to Always allow and keep every other tool on Needs approval. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  - Done when: The business owner has approved the allowlist on scorecard evidence, and only those tools are Always allow.
- [ ] **S-T6.wall-test** Test the information wall with two users on either side before the pilot (owner: compliance, Chief Compliance Officer, part A7)
  1. List what the wall must keep apart in each system the task reads. See [docs/compendium/14-private-equity.md#what-a-wall-has-to-guarantee](../../../../docs/compendium/14-private-equity.md#what-a-wall-has-to-guarantee).
  2. Run the task as a user on each side of the wall and check neither sees the other side's records. See [docs/compendium/14-private-equity.md#where-a-twin-can-leak-across-a-wall](../../../../docs/compendium/14-private-equity.md#where-a-twin-can-leak-across-a-wall).
  3. Use the two-user test in the system's runbook where the kit has one. See [starter-kit/runbooks/salesforce-hosted-mcp.md#9-test-two-users-on-either-side-of-a-soft-wall](../../../../starter-kit/runbooks/salesforce-hosted-mcp.md#9-test-two-users-on-either-side-of-a-soft-wall).
  - Done when: Compliance has seen the two-user test pass for every walled system the task reads.
- [ ] **S-T6.web-tools-off** Check web search and web fetch are off wherever this task runs (owner: technical-owner, Director of IT, part A7)
  1. Check the settings baseline or the org setting turns web tools off on the task's surfaces. See [starter-kit/settings/README.md#keys](../../../../starter-kit/settings/README.md#keys).
  2. Try a web search in the task and confirm it is refused. See [docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above](../../../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above).
  - Done when: A web search or fetch attempted during the task is refused.
- [ ] **S-T6.warning-high-cost-ceiling-unconfirmed** Resolve warning high-cost-ceiling-unconfirmed: confirm the ceiling of a task whose mistakes cost a lot (owner: business-owner, RevOps manager, part A7)
  1. Read which cap applied and why in levelled.json, and note that page 06 has no rule for the cost of a mistake. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Confirm the cap with the customer, or record a lower ceiling as an override on the card, then level again. See [partner-kit/docs/design.md#73-rules-plan-fit-and-levelledjson](../../../../partner-kit/docs/design.md#73-rules-plan-fit-and-levelledjson).
  - Done when: The customer has confirmed the ceiling, or a lower ceiling is on the card as an override with a reason and an approver.
- [ ] **S-T6.warning-zdr-org-not-confirmed** Resolve warning zdr-org-not-confirmed: confirm the separate Enterprise org with ZDR (owner: compliance, Chief Compliance Officer, part A7)
  1. Explain that highly sensitive data needs a separate Enterprise org with ZDR. See [docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above](../../../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above).
  2. Confirm with the customer whether a zero-data-retention agreement covers the org this work runs in, record the answer as compliance.zdr_cover in the profile, then level again. See [docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt](../../../../docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt).
  - Done when: The profile's compliance.zdr_cover is in-place for this work, or the task's data class is lowered with the compliance owner.
- [ ] **S-T6.zdr-retention-agreement-first** Get the zero-data-retention agreement signed, then confirm the task runs only in that org (owner: compliance, Chief Compliance Officer, part A7)
  1. The profile's compliance.zdr_cover is planned or still open: no signed zero-data-retention agreement covers this work yet. Do not let the task go live until the agreement is signed and covers the org it runs in. See [docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt](../../../../docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt).
  2. Check the task's surfaces and connectors are all in the ZDR org. See [docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt](../../../../docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt).
  3. Record which features the ZDR org lacks that the task might expect. See [docs/compendium/12-orgs-and-ownership.md#recommended-starting-point](../../../../docs/compendium/12-orgs-and-ownership.md#recommended-starting-point).
  - Done when: The zero-data-retention agreement is signed and covers the org, compliance.zdr_cover is in-place, and compliance has confirmed the task runs only in the ZDR org.

## F-twin-foundation: Twin foundation

Kind: foundation. Status: todo. 7 stories.

### S-persona-voice: Persona voice

As a Deal-team associate, I want my twin's persona voice in place so that every task story runs safely.

Part A1. In pilot: yes. Priority: none. Status: todo.

| Field | Value |
|---|---|
| Plan | enterprise |
| Device | managed |
| Plugin name | twin-pe-deal-team |
| Distribution | group-targeted |
| Settings baseline | pe-zdr |
| Governance log | yes |

**Acceptance criteria:**

1. persona.md is filled in from the card's voice section, with a reason for every rule.
2. The output style and the system prompt match persona.md.
3. The business owner has approved the voice.

**Gated by:**

- Nothing.

**Tasks:**

- [ ] **S-persona-voice.persona-fill** Fill in the persona from the kit template, from the card's voice section (owner: skill-engineer, part A1)
  1. Copy the kit's persona template. See [starter-kit/templates/persona/README.md#fill-it-in](../../../../starter-kit/templates/persona/README.md#fill-it-in).
  2. Fill in persona.md section by section from the card's voice, giving the reason for every rule. See [docs/compendium/02-persona.md#a-persona-template-our-recommendation](../../../../docs/compendium/02-persona.md#a-persona-template-our-recommendation).
  - Done when: persona.md is filled in with no FILL IN marker left.
- [ ] **S-persona-voice.persona-forms** Build the output style and the system prompt from the persona (owner: skill-engineer, part A1)
  1. Build each form the role's surfaces need from persona.md. See [starter-kit/templates/persona/README.md#which-form-goes-where](../../../../starter-kit/templates/persona/README.md#which-form-goes-where).
  2. Change persona.md and both forms in the same pull request, never one alone. See [starter-kit/templates/persona/README.md#the-rule](../../../../starter-kit/templates/persona/README.md#the-rule).
  - Done when: Both forms match persona.md and sit where each surface reads them.
- [ ] **S-persona-voice.persona-review** Have the business owner and a pilot user review the persona voice (owner: business-owner, RevOps manager, part A1)
  1. Show the reviewers drafts from the twin with the persona in place. See [docs/compendium/02-persona.md#where-the-persona-lives-on-each-surface](../../../../docs/compendium/02-persona.md#where-the-persona-lives-on-each-surface).
  2. Record what they change and update persona.md and both forms. See [starter-kit/templates/persona/README.md#the-rule](../../../../starter-kit/templates/persona/README.md#the-rule).
  - Done when: The business owner has approved the persona voice.

### S-connectors-and-identity: Connectors and identity

As a Deal-team associate, I want my twin's connectors and identity in place so that every task story runs safely.

Part A3. In pilot: yes. Priority: none. Status: todo.

| Field | Value |
|---|---|
| Plan | enterprise |
| Device | managed |
| Plugin name | twin-pe-deal-team |
| Distribution | group-targeted |
| Settings baseline | pe-zdr |
| Governance log | yes |

**Acceptance criteria:**

1. Every connector the role uses is listed with its identity and approver.
2. The role's users are in the organisation with the right role.

**Gated by:**

- Nothing.

**Data providers the pack knows (none is on by default):**

| Provider | Kind | Access | Note | Source |
|---|---|---|---|---|
| Daloopa | financial-data | mcp | Remote MCP server https://mcp.daloopa.com/server/mcp, shipped in the financial-analysis plugin. Not allowed in the private-equity ZDR org for the pilot: a query shows the vendor what the firm is looking at. Per vendor later, after the vendor test. Its retention and identity model are unconfirmed. | [docs/compendium/17-anthropic-pe-plugins-review.md#3-where-the-data-goes-connectors-and-external-tools](../../../../docs/compendium/17-anthropic-pe-plugins-review.md#3-where-the-data-goes-connectors-and-external-tools) ⚠ Unverified |
| Morningstar | market-data | mcp | Remote MCP server https://mcp.morningstar.com/mcp, shipped in the financial-analysis plugin. Not allowed in the private-equity ZDR org for the pilot: a query shows the vendor what the firm is looking at. Its retention and identity model are unconfirmed. | [docs/compendium/17-anthropic-pe-plugins-review.md#3-where-the-data-goes-connectors-and-external-tools](../../../../docs/compendium/17-anthropic-pe-plugins-review.md#3-where-the-data-goes-connectors-and-external-tools) ⚠ Unverified |
| S&P Global (Kensho) | market-data | mcp | Remote MCP server https://kfinance.kensho.com/integrations/mcp, shipped in the financial-analysis plugin. Not allowed in the private-equity ZDR org for the pilot: a query shows the vendor what the firm is looking at. Capital IQ data. Its retention and identity model are unconfirmed. | [docs/compendium/17-anthropic-pe-plugins-review.md#3-where-the-data-goes-connectors-and-external-tools](../../../../docs/compendium/17-anthropic-pe-plugins-review.md#3-where-the-data-goes-connectors-and-external-tools) ⚠ Unverified |
| FactSet | market-data | mcp | Remote MCP server https://mcp.factset.com/mcp, shipped in the financial-analysis plugin. Not allowed in the private-equity ZDR org for the pilot: a query shows the vendor what the firm is looking at. Its retention and identity model are unconfirmed. | [docs/compendium/17-anthropic-pe-plugins-review.md#3-where-the-data-goes-connectors-and-external-tools](../../../../docs/compendium/17-anthropic-pe-plugins-review.md#3-where-the-data-goes-connectors-and-external-tools) ⚠ Unverified |
| Moody's | credit-data | mcp | Remote MCP server https://api.moodys.com/genai-ready-data/m1/mcp, shipped in the financial-analysis plugin. Not allowed in the private-equity ZDR org for the pilot: a query shows the vendor what the firm is looking at. Its retention and identity model are unconfirmed. | [docs/compendium/17-anthropic-pe-plugins-review.md#3-where-the-data-goes-connectors-and-external-tools](../../../../docs/compendium/17-anthropic-pe-plugins-review.md#3-where-the-data-goes-connectors-and-external-tools) ⚠ Unverified |
| MT Newswires | news | mcp | Remote MCP server https://vast-mcp.blueskyapi.com/mtnewswires, shipped in the financial-analysis plugin. Not allowed in the private-equity ZDR org for the pilot: a query shows the vendor what the firm is looking at. The host is not the news vendor's own domain, so there is an extra party in the path. Its retention and identity model are unconfirmed. | [docs/compendium/17-anthropic-pe-plugins-review.md#3-where-the-data-goes-connectors-and-external-tools](../../../../docs/compendium/17-anthropic-pe-plugins-review.md#3-where-the-data-goes-connectors-and-external-tools) ⚠ Unverified |
| Aiera | earnings-data | mcp | Remote MCP server https://mcp-pub.aiera.com, shipped in the financial-analysis plugin. Not allowed in the private-equity ZDR org for the pilot: a query shows the vendor what the firm is looking at. Its retention and identity model are unconfirmed. | [docs/compendium/17-anthropic-pe-plugins-review.md#3-where-the-data-goes-connectors-and-external-tools](../../../../docs/compendium/17-anthropic-pe-plugins-review.md#3-where-the-data-goes-connectors-and-external-tools) ⚠ Unverified |
| LSEG | market-data | mcp | Remote MCP server https://api.analytics.lseg.com/lfa/mcp, shipped in the financial-analysis plugin. Not allowed in the private-equity ZDR org for the pilot: a query shows the vendor what the firm is looking at. Its retention and identity model are unconfirmed. | [docs/compendium/17-anthropic-pe-plugins-review.md#3-where-the-data-goes-connectors-and-external-tools](../../../../docs/compendium/17-anthropic-pe-plugins-review.md#3-where-the-data-goes-connectors-and-external-tools) ⚠ Unverified |
| PitchBook | private-company-data | mcp | Remote MCP server https://premium.mcp.pitchbook.com/mcp, shipped in the financial-analysis plugin. Not allowed in the private-equity ZDR org for the pilot: a query shows the vendor what the firm is looking at. Highest exposure: searching for private targets shows the vendor the firm's pipeline. Its retention and identity model are unconfirmed. | [docs/compendium/17-anthropic-pe-plugins-review.md#3-where-the-data-goes-connectors-and-external-tools](../../../../docs/compendium/17-anthropic-pe-plugins-review.md#3-where-the-data-goes-connectors-and-external-tools) ⚠ Unverified |
| Chronograph | portfolio-monitoring | mcp | Remote MCP server https://ai.chronograph.pe/mcp, shipped in the financial-analysis plugin. Not allowed for the pilot. A later candidate for portfolio-monitoring if the firm already uses it, after the compendium 11 review. Its retention and identity model are unconfirmed. | [docs/compendium/17-anthropic-pe-plugins-review.md#3-where-the-data-goes-connectors-and-external-tools](../../../../docs/compendium/17-anthropic-pe-plugins-review.md#3-where-the-data-goes-connectors-and-external-tools) ⚠ Unverified |
| Egnyte | document-storage | mcp | Remote MCP server https://mcp-server.egnyte.com/mcp, shipped in the financial-analysis plugin. Not for a firm that uses SharePoint. For a firm that keeps deal files there it is acceptable after the compendium 11 review, per user and read-only. Its retention and identity model are unconfirmed. | [docs/compendium/17-anthropic-pe-plugins-review.md#3-where-the-data-goes-connectors-and-external-tools](../../../../docs/compendium/17-anthropic-pe-plugins-review.md#3-where-the-data-goes-connectors-and-external-tools) ⚠ Unverified |
| Box | document-storage | mcp | Remote MCP server https://mcp.box.com, shipped in the financial-analysis plugin. Same as Egnyte. Its retention and identity model are unconfirmed. | [docs/compendium/17-anthropic-pe-plugins-review.md#3-where-the-data-goes-connectors-and-external-tools](../../../../docs/compendium/17-anthropic-pe-plugins-review.md#3-where-the-data-goes-connectors-and-external-tools) ⚠ Unverified |

**Tasks:**

- [ ] **S-connectors-and-identity.identity-scim-groups** Create the role's SCIM groups and connect SCIM in Claude (owner: technical-owner, Director of IT, part A5)
  1. Create the role's groups in the identity provider. See [starter-kit/runbooks/identity-devices-publishing.md#1-create-the-scim-groups-in-the-identity-provider](../../../../starter-kit/runbooks/identity-devices-publishing.md#1-create-the-scim-groups-in-the-identity-provider).
  2. Connect SCIM in Claude. See [starter-kit/runbooks/identity-devices-publishing.md#2-connect-scim-in-claude](../../../../starter-kit/runbooks/identity-devices-publishing.md#2-connect-scim-in-claude).
  3. Map the groups to roles and seats. See [starter-kit/runbooks/identity-devices-publishing.md#3-map-groups-to-roles-and-seats](../../../../starter-kit/runbooks/identity-devices-publishing.md#3-map-groups-to-roles-and-seats).
  - Done when: The role's users arrive in Claude through SCIM in the right group.
- [ ] **S-connectors-and-identity.connector-inventory** List every connector the role uses, its identity and who approves it (owner: solution-architect, part A3)
  1. List the systems each task reads or writes and the connector for each. See [docs/compendium/11-connectors.md#what-exists-for-our-systems](../../../../docs/compendium/11-connectors.md#what-exists-for-our-systems).
  2. Record each connector's identity and the person who approves it. See [docs/playbook/01-engagement-model.md](../../../../docs/playbook/01-engagement-model.md).
  - Done when: Every connector the role uses is listed with its identity and approver.
- [ ] **S-connectors-and-identity.connector-review** Review each connector before it is enabled (owner: security, acting: Director of IT, part A3)
  1. Review each connector against the kit's review questions. See [docs/compendium/11-connectors.md#buying-a-connector-and-reviewing-it](../../../../docs/compendium/11-connectors.md#buying-a-connector-and-reviewing-it).
  2. Record the review and any limits it sets. See [docs/compendium/11-connectors.md#adding-a-connector-that-isnt-in-the-directory](../../../../docs/compendium/11-connectors.md#adding-a-connector-that-isnt-in-the-directory).
  - Done when: A security reviewer has checked every connector before it is enabled.
- [ ] **S-connectors-and-identity.data-providers-decide** Decide for each data provider the pack knows: allowed, not allowed or later (owner: compliance, Chief Compliance Officer, part A3)
  1. Decide for Daloopa, Morningstar, S&P Global (Kensho), FactSet, Moody's, MT Newswires, Aiera, LSEG, PitchBook, Chronograph, Egnyte and Box: allowed, not allowed or later, with the approver and the reason. See [docs/compendium/17-anthropic-pe-plugins-review.md#3-where-the-data-goes-connectors-and-external-tools](../../../../docs/compendium/17-anthropic-pe-plugins-review.md#3-where-the-data-goes-connectors-and-external-tools).
  2. Record each provider's decision, its approver and its reason in the customer's engagement folder. See [docs/compendium/17-anthropic-pe-plugins-review.md#3-where-the-data-goes-connectors-and-external-tools](../../../../docs/compendium/17-anthropic-pe-plugins-review.md#3-where-the-data-goes-connectors-and-external-tools).
  - Done when: Every data provider the story lists has a recorded decision (allowed, not allowed or later), with its approver and reason, in the customer's engagement folder.

### S-guardrails-and-settings: Guardrails and settings

As a Deal-team associate, I want my twin's guardrails and settings in place so that every task story runs safely.

Part A7. In pilot: yes. Priority: none. Status: todo.

| Field | Value |
|---|---|
| Plan | enterprise |
| Device | managed |
| Plugin name | twin-pe-deal-team |
| Distribution | group-targeted |
| Settings baseline | pe-zdr |
| Governance log | yes |

**Acceptance criteria:**

1. The settings, or what replaces them, are in force for the role.
2. Compliance has signed off the data policy for each data class.

**Gated by:**

- Nothing.

**Tasks:**

- [ ] **S-guardrails-and-settings.settings-deploy** Deploy the managed-settings baseline levelled.json names to the role's devices (owner: technical-owner, Director of IT, part A7)
  1. Check the baseline file before deploying it. See [starter-kit/settings/README.md#check-the-file-before-you-deploy](../../../../starter-kit/settings/README.md#check-the-file-before-you-deploy).
  2. Deploy it to the role's devices through device management. See [starter-kit/runbooks/identity-devices-publishing.md#4-deploy-the-managed-settings-baseline-to-devices](../../../../starter-kit/runbooks/identity-devices-publishing.md#4-deploy-the-managed-settings-baseline-to-devices).
  - Done when: The baseline is on every device of the role.
- [ ] **S-guardrails-and-settings.settings-verify** Verify on a device that the managed settings took effect (owner: technical-owner, Director of IT, part A7)
  1. Open Claude Code on a pilot device and check the settings in force. See [starter-kit/runbooks/identity-devices-publishing.md#5-verify-on-a-device-that-the-settings-took-effect](../../../../starter-kit/runbooks/identity-devices-publishing.md#5-verify-on-a-device-that-the-settings-took-effect).
  2. Check each key the baseline sets. See [starter-kit/settings/README.md#keys](../../../../starter-kit/settings/README.md#keys).
  - Done when: A pilot device shows every key of the baseline in force.
- [ ] **S-guardrails-and-settings.data-policy** Agree the data policy for each of the role's data classes with compliance (owner: compliance, Chief Compliance Officer, part A7)
  1. Take each data class the role's tasks hold through the decision matrix. See [docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above](../../../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above).
  2. Agree the device policy for each class. See [docs/compendium/13-devices.md#policy-by-data-class-and-device-our-recommendation](../../../../docs/compendium/13-devices.md#policy-by-data-class-and-device-our-recommendation).
  - Done when: Compliance has signed off the data policy for every data class the role holds.
- [ ] **S-guardrails-and-settings.retention-and-feedback-settings** Set the org's retention period and its feedback and training-data settings to the data policy (owner: technical-owner, Director of IT, part A7)
  1. Read the retention the data policy sets for chat, Claude Code and the governance log. See [docs/compendium/15-governance-and-performance.md#retention-decided](../../../../docs/compendium/15-governance-and-performance.md#retention-decided).
  2. Settle with compliance whether /feedback transcripts may be kept 5 years and, with the Compliance API on, local Claude Code and Cowork sessions 6 years; if not, turn feedback off with DISABLE_FEEDBACK_COMMAND=1 in managed settings and set a custom retention period. See [docs/compendium/10-sensitive-data.md#questions-to-settle-with-compliance-and-legal](../../../../docs/compendium/10-sensitive-data.md#questions-to-settle-with-compliance-and-legal).
  3. Set the retention period (custom retention is Enterprise only, at least 30 days) and the feedback and training-data settings in the org, and record each value in the customer's engagement folder. See [docs/compendium/09-plans-and-it-controls.md#feature-matrix](../../../../docs/compendium/09-plans-and-it-controls.md#feature-matrix).
  - Done when: The org's retention period and its feedback and training-data settings match the data policy, and each value is recorded in the customer's engagement folder.
- [ ] **S-guardrails-and-settings.spend-limits** Set the org's spend limits and name who watches them (owner: technical-owner, IT, part A9)
  1. Set the org's spend limit, and on Enterprise a per-user limit for the role's users. See [docs/compendium/09-plans-and-it-controls.md#spend-and-usage-limits](../../../../docs/compendium/09-plans-and-it-controls.md#spend-and-usage-limits).
  2. Name who watches spend and the usage alerts, and record the limits and that person in the customer's engagement folder. See [docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often](../../../../docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often).
  - Done when: The org's spend limit, and on Enterprise the per-user limits, are set and recorded, and a named person watches them.

### S-distribution: Distribution

As a Deal-team associate, I want my twin's distribution in place so that every task story runs safely.

Part A9. In pilot: yes. Priority: none. Status: todo.

| Field | Value |
|---|---|
| Plan | enterprise |
| Device | managed |
| Plugin name | twin-pe-deal-team |
| Distribution | group-targeted |
| Settings baseline | pe-zdr |
| Governance log | yes |

**Acceptance criteria:**

1. The role plugin reaches the role's users at the current version, and no one else it must not reach.

**Gated by:**

- Nothing.

**Tasks:**

- [ ] **S-distribution.role-plugin-build** Create the role plugin from the kit template (owner: skill-engineer, part A9)
  1. Copy and rename the role-plugin template. See [starter-kit/templates/role-plugin/README.md#steps](../../../../starter-kit/templates/role-plugin/README.md#steps).
  2. Add the persona and the skills, and the marketplace entry. See [docs/compendium/04-distribution-governance.md#recommended-pipeline-our-recommendation](../../../../docs/compendium/04-distribution-governance.md#recommended-pipeline-our-recommendation).
  - Done when: The role plugin is in the marketplace and its tests pass.
- [ ] **S-distribution.distribute-group** Publish the marketplace and the role plugin to the role's group (owner: technical-owner, Director of IT, part A9)
  1. Publish the marketplace to the role's group. See [starter-kit/runbooks/identity-devices-publishing.md#6-publish-the-marketplace-and-its-plugins-to-the-right-groups](../../../../starter-kit/runbooks/identity-devices-publishing.md#6-publish-the-marketplace-and-its-plugins-to-the-right-groups).
  2. Check a user outside the group does not get the role plugin. See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  - Done when: Only the role's group gets the role plugin.

### S-governance-log: Governance log

As a Deal-team associate, I want my twin's governance log in place so that every task story runs safely.

Part A9. In pilot: yes. Priority: none. Status: todo.

| Field | Value |
|---|---|
| Plan | enterprise |
| Device | managed |
| Plugin name | twin-pe-deal-team |
| Distribution | group-targeted |
| Settings baseline | pe-zdr |
| Governance log | yes |

**Acceptance criteria:**

1. What is logged for the twin, and where, is agreed and checked.

**Gated by:**

- Nothing.

**Tasks:**

- [ ] **S-governance-log.governance-log-destination** Agree the governance log's destination and who can read it (owner: technical-owner, Director of IT, part A9)
  1. Settle where the log lives with the customer. See [docs/compendium/15-governance-and-performance.md#where-the-log-lives-settle-it-with-each-customer](../../../../docs/compendium/15-governance-and-performance.md#where-the-log-lives-settle-it-with-each-customer).
  2. Agree who can read the log and how long it is kept. See [docs/compendium/15-governance-and-performance.md#one-governance-log-for-all-twins-our-recommendation](../../../../docs/compendium/15-governance-and-performance.md#one-governance-log-for-all-twins-our-recommendation).
  - Done when: The log's destination, readers and retention are agreed in writing.
- [ ] **S-governance-log.governance-hook-deploy** Deploy the governance hook through managed settings (owner: integration-engineer, part A9)
  1. Configure the governance hook for the customer's log destination. See [starter-kit/plugins/twin-governance/README.md#configuration](../../../../starter-kit/plugins/twin-governance/README.md#configuration).
  2. Deploy it as a managed hook with the settings baseline. See [starter-kit/plugins/twin-governance/README.md#deploying-it-managed-hooks](../../../../starter-kit/plugins/twin-governance/README.md#deploying-it-managed-hooks).
  3. Send the log to the customer's monitoring system. See [starter-kit/plugins/twin-governance/README.md#getting-the-log-to-your-siem](../../../../starter-kit/plugins/twin-governance/README.md#getting-the-log-to-your-siem).
  - Done when: The governance hook runs on every device of the role.
- [ ] **S-governance-log.governance-log-check** Check that a tool call reaches the governance log (owner: security, acting: Director of IT, part A9)
  1. Make a tool call through the twin on a pilot device. See [starter-kit/plugins/twin-governance/README.md#the-governance-log-hook](../../../../starter-kit/plugins/twin-governance/README.md#the-governance-log-hook).
  2. Find the call's entry in the log destination. See [starter-kit/settings/README.md#governance-hook](../../../../starter-kit/settings/README.md#governance-hook).
  - Done when: A test tool call appears in the governance log with its metadata.
- [ ] **S-governance-log.source-audit** Turn on the source systems' own audit for the twin's writes (owner: source-system-admin, acting: Director of IT, part A9)
  1. Check each system the twin writes keeps an audit of changes. See [docs/compendium/15-governance-and-performance.md#what-each-source-records](../../../../docs/compendium/15-governance-and-performance.md#what-each-source-records).
  2. Turn it on where it is off and record how long it is kept. See [docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often](../../../../docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often).
  - Done when: Every system the twin writes keeps an audit of its changes.

### S-memory-policy: Memory policy

As a Deal-team associate, I want my twin's memory policy in place so that every task story runs safely.

Part A6. In pilot: yes. Priority: none. Status: todo.

| Field | Value |
|---|---|
| Plan | enterprise |
| Device | managed |
| Plugin name | twin-pe-deal-team |
| Distribution | group-targeted |
| Settings baseline | pe-zdr |
| Governance log | yes |

**Acceptance criteria:**

1. The memory policy is written down and in force.

**Gated by:**

- Nothing.

**Tasks:**

- [ ] **S-memory-policy.memory-policy** Write down the role's memory policy (owner: solution-architect, part A6)
  1. Copy the kit's memory-policy template and decide what the twin may remember for the role and what it must not. See [starter-kit/templates/pilot/memory-policy.md#what-the-twin-may-remember-and-what-it-must-not](../../../../starter-kit/templates/pilot/memory-policy.md#what-the-twin-may-remember-and-what-it-must-not).
  2. Name who can switch memory on or off for the org. See [starter-kit/templates/pilot/memory-policy.md#who-can-switch-memory-on-or-off-for-the-org](../../../../starter-kit/templates/pilot/memory-policy.md#who-can-switch-memory-on-or-off-for-the-org).
  3. Write the policy into the design and the persona. See [starter-kit/templates/persona/README.md#fill-it-in](../../../../starter-kit/templates/persona/README.md#fill-it-in).
  - Done when: The memory policy is written down and the business owner has approved it.
- [ ] **S-memory-policy.memory-off** Keep personal memory off for the role and tell the pilot users why (owner: technical-owner, Director of IT, part A6)
  1. Turn personal memory off where the role's users work. See [docs/compendium/02-persona.md#memory](../../../../docs/compendium/02-persona.md#memory).
  2. Tell the pilot users why memory is off. See [starter-kit/templates/pilot/memory-policy.md#what-pilot-users-are-told](../../../../starter-kit/templates/pilot/memory-policy.md#what-pilot-users-are-told).
  - Done when: Personal memory is off for the role's users and they know why.

### S-pilot-rollout-and-scorecard: Pilot rollout and scorecard

As a Deal-team associate, I want my twin's pilot rollout and scorecard in place so that every task story runs safely.

Part A8. In pilot: yes. Priority: none. Status: todo.

| Field | Value |
|---|---|
| Plan | enterprise |
| Device | managed |
| Plugin name | twin-pe-deal-team |
| Distribution | group-targeted |
| Settings baseline | pe-zdr |
| Governance log | yes |

**Acceptance criteria:**

1. The pilot users are trained, the baseline is recorded, and the first scorecard is reviewed.

**Gated by:**

- Nothing.

**Tasks:**

- [ ] **S-pilot-rollout-and-scorecard.pilot-users** Name the pilot users and agree the pilot dates (owner: business-owner, RevOps manager, part A8)
  1. Choose five to ten pilot users in the role. See [docs/playbook/01-engagement-model.md](../../../../docs/playbook/01-engagement-model.md).
  2. Agree the start and review dates with the business owner. See [docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often](../../../../docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often).
  - Done when: The pilot users and dates are agreed and recorded.
- [ ] **S-pilot-rollout-and-scorecard.pilot-baseline** Record the baseline time for each pilot task before the pilot starts (owner: consultant, part A8)
  1. Take each pilot story's baseline from its fields table. See [docs/playbook/04-stories.md#story-template](../../../../docs/playbook/04-stories.md#story-template).
  2. Confirm it with the pilot users before they start. See [docs/compendium/15-governance-and-performance.md#measuring-performance](../../../../docs/compendium/15-governance-and-performance.md#measuring-performance).
  - Done when: Every pilot task has a baseline agreed with its users.
- [ ] **S-pilot-rollout-and-scorecard.pilot-scorecard** Set up the monthly scorecard for the twin (owner: business-owner, RevOps manager, part A8)
  1. Copy the kit's scorecard template and choose the adoption, quality, value and safety measures for each task. See [starter-kit/templates/pilot/scorecard.md#per-task](../../../../starter-kit/templates/pilot/scorecard.md#per-task).
  2. Take each measure as the compendium describes. See [docs/compendium/15-governance-and-performance.md#measuring-performance](../../../../docs/compendium/15-governance-and-performance.md#measuring-performance).
  3. Book the monthly review with the business owner, and record its decision on the scorecard. See [starter-kit/templates/pilot/scorecard.md#decision-this-month](../../../../starter-kit/templates/pilot/scorecard.md#decision-this-month).
  - Done when: The first monthly scorecard has been reviewed with the business owner.
- [ ] **S-pilot-rollout-and-scorecard.pilot-training** Train the pilot users and tell them how to report a failure (owner: change-and-enablement-lead, part A8)
  1. Run a short session on what the twin does, at what level, and what it never does, from the kit's session outline. See [starter-kit/templates/pilot/pilot-training.md#part-1-session-outline](../../../../starter-kit/templates/pilot/pilot-training.md#part-1-session-outline).
  2. Give the pilot users one place to report a failure or a wrong draft, with the kit's report form. See [starter-kit/templates/pilot/pilot-training.md#where-reports-go](../../../../starter-kit/templates/pilot/pilot-training.md#where-reports-go).
  - Done when: Every pilot user has been trained and knows where to report a failure.

## Spikes

Open questions on the card. A spike is time-boxed research that answers one; it holds no build work. Mark a spike by changing its status in backlog.json.

- [ ] **SP-E4** Do the Salesforce and HubSpot admins confirm in writing that deal-team and investor-relations roles are fully separated? (owner: Source-system admins (Salesforce admin and HubSpot admin); due: 2026-11-27; blocks: S-T1, S-T2)
- [ ] **SP-E6** Can Anthropic's range 160.79.104.0/21 be allowlisted? (owner: Security; due: 2026-11-27; blocks: S-T1, S-T2, S-T3)
- [ ] **SP-F3** Two to three real good and bad examples per skill, redacted. (owner: Skill owners; due: 2026-12-04; blocks: S-T1, S-T2, S-T3, S-T4, S-T5, S-T6)
- [ ] **SP-G1** Where does the governance log go (Splunk is the candidate), how is it hosted and who may read it? (owner: Technical owner (Director of IT); due: 2026-12-04; blocks: S-T1, S-T2)
- [ ] **SP-OD-1** Layer on Anthropic's private-equity and financial-analysis plugins, or build? (owner: Review: Rashida Kovalenko. Sign-off: Eleanor Osei-Whitcombe; due: 2026-12-04; blocks: S-T4, S-T6)
- [ ] **SP-OD-8** Identity for the hosted Monday summary, whether it may post to Teams, and whether a wrapper server is needed. Due: before T3 is built (after the pilot). (owner: Ngozi Brandvold and Tomasz Hadjiev; Joaquin Lindahl for the Salesforce role; due: not set; blocks: S-T3)
- [ ] **SP-OD-9** ZDR addendum on the existing Enterprise org, which models qualify for ZDR, and the seat count. (owner: Tomasz Hadjiev, with the Anthropic account team; due: 2026-12-04; blocks: S-T1, S-T2, S-T3)
- [ ] **SP-OD-11** Numeric scorecard targets for hours saved and edit rate on T1 and T2. (owner: Samir Castellanos, with Marguerite Oyelaran; due: 2026-12-04; blocks: S-T1, S-T2)
- [ ] **SP-OD-13** Keep the Salesforce and Microsoft 365 connectors out of chat and Cowork for the deal-team group. Due: before any pilot user connects. (owner: Tomasz Hadjiev; due: not set; blocks: S-T1, S-T2)

## Retired

Nothing retired.
