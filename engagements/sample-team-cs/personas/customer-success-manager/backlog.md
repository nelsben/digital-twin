# Customer success manager twin for Example Software Co

Generated from card.json and levelled.json by `python3 partner-kit/plugins/twin-consultant/scripts/twincard/cli.py backlog engagements/sample-team-cs/personas/customer-success-manager`; never edit it by hand. To mark a task, change only its status in backlog.json, then run the command again.

Status: todo. 4 features, 12 stories, 106 tasks. Task marks: `[ ]` todo, `[~]` in progress, `[x]` done.

Roles with no named person: security, 1 task, acting owner Teodor Amsel (IT and operations lead); source-system-admin, 3 tasks, acting owner Teodor Amsel (IT and operations lead).

## F-call-preparation-and-follow-up: Call preparation and follow-up

Kind: capability. Status: todo. 2 stories.

### S-C1: Account brief before a customer call

As a Customer success manager, I want my twin to account brief before a customer call so that I get the one-page account brief.

Part A2. In pilot: yes. Priority: 1. Status: todo.

| Field | Value |
|---|---|
| Data class | confidential |
| Surface | client-skill; surfaces: claude-ai |
| Autonomy | 1 to 3 |
| Connectors and identity | hubspot: user identity, read, always-allow; google-drive: user identity, read, always-allow |
| Wall impact | none |
| Inputs | hubspot (company, contacts, deals, open tickets, notes); google-drive (account plan, last QBR deck, contract) |
| Output and audience | One-page account brief, internal; to none (the conversation) |
| Delivery | The output stays in the conversation or a local file. |
| Skill owner | Marisol Quenby |
| Baseline | 6 per week x 30 minutes each x 8 users |

**Acceptance criteria:**

1. Eval from good example 1 of 2 (Shared drive 'CS examples' (invented)): the twin's output matches what a person accepted.
2. Eval from good example 2 of 2 (Shared drive 'CS examples' (invented)): the twin's output matches what a person accepted.
3. Eval from bad example 1 of 1 (Shared drive 'CS examples' (invented)): the twin does not repeat the mistake.

**Gated by:**

- Nothing.

**Tasks:**

- [ ] **S-C1.collect-examples** Collect 3 examples of the task from real work, each with the result a person expects (owner: skill-owner, Marisol Quenby, part A8)
  1. Ask the people who do the task today for three recent, real examples of it. See [starter-kit/docs/authoring-skills.md#step-order](../../../../starter-kit/docs/authoring-skills.md#step-order).
  2. Record each example's inputs and the output a person would accept as done. See [starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals](../../../../starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals).
  3. Remove any data the examples must not carry into the repository, keeping their shape. See [docs/compendium/10-sensitive-data.md#design-patterns-that-keep-data-out-of-the-conversation](../../../../docs/compendium/10-sensitive-data.md#design-patterns-that-keep-data-out-of-the-conversation).
  - Done when: Three real examples, each with its inputs and its expected result, are stored where the evals can read them.
- [ ] **S-C1.write-evals** Write the evals from the examples and the story's acceptance criteria (owner: skill-engineer, part A8)
  1. Turn each example and each acceptance criterion into an eval case with its expected result. See [starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals](../../../../starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals).
  2. Put the eval cases in the files the kit expects, next to the skill. See [starter-kit/docs/authoring-skills.md#the-eval-files](../../../../starter-kit/docs/authoring-skills.md#the-eval-files).
  3. Run the evals once before any skill exists and keep the failing baseline. See [docs/compendium/03-skills-authoring.md#evaluate-first-then-iterate](../../../../docs/compendium/03-skills-authoring.md#evaluate-first-then-iterate).
  - Done when: Every acceptance criterion has at least one eval, and the evals run and fail without the skill.
- [ ] **S-C1.write-skill** Write the skill from the kit template until the evals pass (owner: skill-engineer, part A2)
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
- [ ] **S-C1.trigger-evals** Write and run the trigger evals for the skill (owner: skill-engineer, part A8)
  1. Install skill-creator where the evals run. See [starter-kit/docs/authoring-skills.md#install-skill-creator](../../../../starter-kit/docs/authoring-skills.md#install-skill-creator).
  2. Write prompts that should and should not start the skill, as trigger evals. See [starter-kit/docs/authoring-skills.md#the-eval-files](../../../../starter-kit/docs/authoring-skills.md#the-eval-files).
  3. Run the trigger evals and tighten the description until they pass. See [docs/compendium/03-skills-authoring.md#writing-a-good-description](../../../../docs/compendium/03-skills-authoring.md#writing-a-good-description).
  - Done when: The skill starts on every should-trigger prompt and on none of the should-not prompts.
- [ ] **S-C1.second-review** Have a second person review the skill and its evals (owner: skill-owner, Marisol Quenby, part A8)
  1. Open a pull request with the skill and its evals. See [docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often](../../../../docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often).
  2. Have someone other than the author review it against the definition of done. See [docs/playbook/04-stories.md#definition-of-done](../../../../docs/playbook/04-stories.md#definition-of-done).
  - Done when: A reviewer who did not write the skill has approved the pull request and the evals pass.
- [ ] **S-C1.publish-in-role-plugin-team** Publish the skill in the role plugin, which every member of the Team org gets (owner: skill-engineer, part A9)
  1. Add the skill to the role plugin and bump the plugin's version. See [starter-kit/templates/role-plugin/README.md#steps](../../../../starter-kit/templates/role-plugin/README.md#steps).
  2. Add the role plugin to the one organisation-wide configuration, so every member gets the new version. See [starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member](../../../../starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member).
  3. Write the skill's description so it says which role it is for, because there is no group target on Team. See [starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member](../../../../starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member).
  - Done when: A pilot user in the role sees the skill after the plugin updates, and its description names the role.
- [ ] **S-C1.connect-kit-runbook.hubspot** Connect it by following the kit's runbook for this connector (hubspot) (owner: integration-engineer, part A3)
  1. Check the runbook's prerequisites, including who must approve the connector. See [starter-kit/runbooks/hubspot-connector.md#before-you-start](../../../../starter-kit/runbooks/hubspot-connector.md#before-you-start).
  2. Follow the runbook's steps to add the connector and set each tool as the story's tool tasks say. See [starter-kit/runbooks/hubspot-connector.md#steps](../../../../starter-kit/runbooks/hubspot-connector.md#steps).
  3. Run the runbook's checks with a pilot user before the task is built. See [starter-kit/runbooks/hubspot-connector.md#check-it-worked](../../../../starter-kit/runbooks/hubspot-connector.md#check-it-worked).
  4. Record the hand-over the runbook asks for in the customer's folder. See [starter-kit/runbooks/hubspot-connector.md#hand-over](../../../../starter-kit/runbooks/hubspot-connector.md#hand-over).
  - Done when: A pilot user has connected with the planned identity, each tool is set as the story's tool tasks say, and the runbook's checks pass.
- [ ] **S-C1.connect-kit-runbook.google-drive** Connect it by following the kit's runbook for this connector (google-drive) (owner: integration-engineer, part A3)
  1. Check the runbook's prerequisites, including who must approve the connector. See [starter-kit/runbooks/google-workspace-connectors.md#before-you-start](../../../../starter-kit/runbooks/google-workspace-connectors.md#before-you-start).
  2. Follow the runbook's steps to add the connector and set each tool as the story's tool tasks say. See [starter-kit/runbooks/google-workspace-connectors.md#steps](../../../../starter-kit/runbooks/google-workspace-connectors.md#steps).
  3. Run the runbook's checks with a pilot user before the task is built. See [starter-kit/runbooks/google-workspace-connectors.md#check-it-worked](../../../../starter-kit/runbooks/google-workspace-connectors.md#check-it-worked).
  4. Record the hand-over the runbook asks for in the customer's folder. See [starter-kit/runbooks/google-workspace-connectors.md#hand-over](../../../../starter-kit/runbooks/google-workspace-connectors.md#hand-over).
  - Done when: A pilot user has connected with the planned identity, each tool is set as the story's tool tasks say, and the runbook's checks pass.
- [ ] **S-C1.tool-always-allow.hubspot-read** Set the connector tool to Always allow, as the levelled tools list says (hubspot-read) (owner: technical-owner, Teodor Amsel (IT and operations lead), part A7)
  1. Open the connector's page in the Claude org and find the tool. See [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced).
  2. Set the tool to Always allow and record the change. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  - Done when: The tool is set to Always allow in the Claude org, as levelled.json says.
- [ ] **S-C1.tool-always-allow.google-drive-read** Set the connector tool to Always allow, as the levelled tools list says (google-drive-read) (owner: technical-owner, Teodor Amsel (IT and operations lead), part A7)
  1. Open the connector's page in the Claude org and find the tool. See [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced).
  2. Set the tool to Always allow and record the change. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  - Done when: The tool is set to Always allow in the Claude org, as levelled.json says.
- [ ] **S-C1.evidence-level-2** Gather the evidence to move the task up to level 2, act with approval (owner: business-owner, Marisol Quenby (Customer success team lead), part A8)
  1. Show the evals pass reliably at the current level. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Bring a month of scorecard results, with the edit rate, to the business owner. See [docs/compendium/15-governance-and-performance.md#measuring-performance](../../../../docs/compendium/15-governance-and-performance.md#measuring-performance).
  - Done when: The business owner has approved the move to level 2 on scorecard evidence, and the tool settings are changed.
- [ ] **S-C1.evidence-level-3** Gather the evidence to move the task up to level 3, act within an allowlist (owner: business-owner, Marisol Quenby (Customer success team lead), part A8)
  1. Confirm every allowlisted action can be undone or stays internal. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Show a stable eval pass rate, a low edit rate and few rejections at level 2. See [docs/compendium/15-governance-and-performance.md#measuring-performance](../../../../docs/compendium/15-governance-and-performance.md#measuring-performance).
  3. List the tools to set to Always allow and keep every other tool on Needs approval. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  - Done when: The business owner has approved the allowlist on scorecard evidence, and only those tools are Always allow.
- [ ] **S-C1.confirm-unverified-decision.connectors.google-drive** Confirm the unverified fact behind this decision with Anthropic or the vendor before build (connectors.google-drive) (owner: solution-architect, part A3)
  1. Find the Unverified mark on the page the decision cites in levelled.json. See [partner-kit/docs/design.md#72-decision-values](../../../../partner-kit/docs/design.md#72-decision-values).
  2. Ask Anthropic or the vendor in writing, using the partner questions list. See [docs/compendium/12-orgs-and-ownership.md#questions-to-bring-to-anthropic-as-a-partner](../../../../docs/compendium/12-orgs-and-ownership.md#questions-to-bring-to-anthropic-as-a-partner).
  3. Record the answer with its source and level the card again. See [docs/compendium/08-open-questions.md#questions-most-first-time-builders-miss](../../../../docs/compendium/08-open-questions.md#questions-most-first-time-builders-miss).
  - Done when: The fact is confirmed in writing with a source, or the decision is changed so it no longer rests on it.
- [ ] **S-C1.warning-memory-poisoning-risk** Resolve warning memory-poisoning-risk: keep memory writes to controlled steps for the task that reads untrusted input (owner: solution-architect, part A6)
  1. Explain how untrusted input can poison memory, and that memory on claude.ai is one org-wide switch. See [docs/compendium/02-persona.md#memory](../../../../docs/compendium/02-persona.md#memory).
  2. Keep role knowledge in reviewed skills and build the task so it never writes memory; only controlled steps write it. See [starter-kit/templates/pilot/memory-policy.md#tasks-that-read-input-written-by-outsiders](../../../../starter-kit/templates/pilot/memory-policy.md#tasks-that-read-input-written-by-outsiders).
  3. If the org cannot keep memory writes to controlled steps, ask the Owner to switch memory off org-wide. See [docs/compendium/09-plans-and-it-controls.md#feature-matrix](../../../../docs/compendium/09-plans-and-it-controls.md#feature-matrix).
  - Done when: The evals show the task writes nothing to memory, its role knowledge lives in reviewed skills, and the org's memory setting is agreed.
- [ ] **S-C1.warning-confidential-standard-retention** Resolve warning confidential-standard-retention: set custom retention or record the customer's acceptance (owner: compliance, Pieter Achterberg (Finance and legal lead), part A7)
  1. Explain that page 10 requires custom retention for confidential data, otherwise local sessions are kept 6 years. See [docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above](../../../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above).
  2. On Enterprise, set custom retention; on Team, record that the customer accepts standard retention. See [docs/compendium/10-sensitive-data.md#other-controls](../../../../docs/compendium/10-sensitive-data.md#other-controls).
  - Done when: Custom retention is set, or the customer's acceptance of standard retention is recorded.

### S-C4: Follow-up email after a customer call, and a call note in HubSpot

As a Customer success manager, I want my twin to follow-up email after a customer call, and a call note in HubSpot so that I get the draft follow-up email, which the manager sends, and a call note on the HubSpot record.

Part A2. In pilot: yes. Priority: 2. Status: todo.

| Field | Value |
|---|---|
| Data class | confidential |
| Surface | client-skill; surfaces: claude-ai |
| Autonomy | 1 to 2 |
| Connectors and identity | google-drive: user identity, read, always-allow; hubspot: user identity, write, blocked |
| Wall impact | none |
| Inputs | google-drive (call notes or transcript) |
| Output and audience | Draft follow-up email, which the manager sends, and a call note on the HubSpot record, external; to a draft in the conversation; the HubSpot company record |
| Delivery | A person sends or files it: the twin produces a draft, hubspot-create is Blocked at the starting level, and it opens at level 2. |
| Skill owner | Marisol Quenby |
| Baseline | 6 per week x 25 minutes each x 8 users |
| Constraints | I want to approve the note before it's created. |

**Acceptance criteria:**

1. Eval from good example 1 of 2 (Shared drive 'CS examples' (invented)): the twin's output matches what a person accepted.
2. Eval from good example 2 of 2 (Shared drive 'CS examples' (invented)): the twin's output matches what a person accepted.
3. Eval from bad example 1 of 1 (Shared drive 'CS examples' (invented)): the twin does not repeat the mistake.
4. Keeps: I want to approve the note before it's created.
5. Plus: the twin writes nothing to the CRM at the starting level; a person files the result.

**Gated by:**

- Nothing.

**Tasks:**

- [ ] **S-C4.collect-examples** Collect 3 examples of the task from real work, each with the result a person expects (owner: skill-owner, Marisol Quenby, part A8)
  1. Ask the people who do the task today for three recent, real examples of it. See [starter-kit/docs/authoring-skills.md#step-order](../../../../starter-kit/docs/authoring-skills.md#step-order).
  2. Record each example's inputs and the output a person would accept as done. See [starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals](../../../../starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals).
  3. Remove any data the examples must not carry into the repository, keeping their shape. See [docs/compendium/10-sensitive-data.md#design-patterns-that-keep-data-out-of-the-conversation](../../../../docs/compendium/10-sensitive-data.md#design-patterns-that-keep-data-out-of-the-conversation).
  - Done when: Three real examples, each with its inputs and its expected result, are stored where the evals can read them.
- [ ] **S-C4.write-evals** Write the evals from the examples and the story's acceptance criteria (owner: skill-engineer, part A8)
  1. Turn each example and each acceptance criterion into an eval case with its expected result. See [starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals](../../../../starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals).
  2. Put the eval cases in the files the kit expects, next to the skill. See [starter-kit/docs/authoring-skills.md#the-eval-files](../../../../starter-kit/docs/authoring-skills.md#the-eval-files).
  3. Run the evals once before any skill exists and keep the failing baseline. See [docs/compendium/03-skills-authoring.md#evaluate-first-then-iterate](../../../../docs/compendium/03-skills-authoring.md#evaluate-first-then-iterate).
  - Done when: Every acceptance criterion has at least one eval, and the evals run and fail without the skill.
- [ ] **S-C4.write-skill** Write the skill from the kit template until the evals pass (owner: skill-engineer, part A2)
  1. Copy the kit's skill template into the role plugin's skills folder, the one source of the skill for every runtime. See [starter-kit/templates/skill/README.md#copy-it](../../../../starter-kit/templates/skill/README.md#copy-it).
  2. Rename the copy to the skill's name. See [starter-kit/templates/skill/README.md#rename-it](../../../../starter-kit/templates/skill/README.md#rename-it).
  3. Fill in the description and the body, then rerun the evals until they pass. See [starter-kit/templates/skill/README.md#fill-it-in](../../../../starter-kit/templates/skill/README.md#fill-it-in).
  4. On client-skill, the skill loads from the role plugin, which an Owner publishes to claude.ai, Desktop and Cowork and which reaches a signed-in Claude Code. See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  5. On managed-agents, the skill loads from the agent's skills array (skills uploaded through the Skills API), or from a mounted GitHub repo's .claude/skills folder. See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  6. On managed-agents-self-hosted, load the skill the same two ways as hosted Managed Agents (Unverified: no compendium page says where a self-hosted deployment loads skills from). See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  7. On agent-sdk, the skill is files on disk in the runner's container, loaded through settingSources; there is no API to register a skill. See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  8. On claude-code-scheduled-task, put the skill where Claude Code loads skills: the project's .claude/skills folder or a plugin (Unverified: no compendium page says which of these a scheduled task loads). See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  9. On claude-tag-routine, give the routine the skill as its instructions (Unverified: no compendium page says whether a Claude Tag routine loads org skills). See [docs/compendium/05-decision-matrix.md#the-options](../../../../docs/compendium/05-decision-matrix.md#the-options).
  10. Make the skill keep these rules from the interviews, in the interviewee's words: I want to approve the note before it's created..
  - Done when: The skill sits in the role plugin, it is where the task's runtime loads it from, and every eval for the story passes.
- [ ] **S-C4.trigger-evals** Write and run the trigger evals for the skill (owner: skill-engineer, part A8)
  1. Install skill-creator where the evals run. See [starter-kit/docs/authoring-skills.md#install-skill-creator](../../../../starter-kit/docs/authoring-skills.md#install-skill-creator).
  2. Write prompts that should and should not start the skill, as trigger evals. See [starter-kit/docs/authoring-skills.md#the-eval-files](../../../../starter-kit/docs/authoring-skills.md#the-eval-files).
  3. Run the trigger evals and tighten the description until they pass. See [docs/compendium/03-skills-authoring.md#writing-a-good-description](../../../../docs/compendium/03-skills-authoring.md#writing-a-good-description).
  - Done when: The skill starts on every should-trigger prompt and on none of the should-not prompts.
- [ ] **S-C4.second-review** Have a second person review the skill and its evals (owner: skill-owner, Marisol Quenby, part A8)
  1. Open a pull request with the skill and its evals. See [docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often](../../../../docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often).
  2. Have someone other than the author review it against the definition of done. See [docs/playbook/04-stories.md#definition-of-done](../../../../docs/playbook/04-stories.md#definition-of-done).
  - Done when: A reviewer who did not write the skill has approved the pull request and the evals pass.
- [ ] **S-C4.publish-in-role-plugin-team** Publish the skill in the role plugin, which every member of the Team org gets (owner: skill-engineer, part A9)
  1. Add the skill to the role plugin and bump the plugin's version. See [starter-kit/templates/role-plugin/README.md#steps](../../../../starter-kit/templates/role-plugin/README.md#steps).
  2. Add the role plugin to the one organisation-wide configuration, so every member gets the new version. See [starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member](../../../../starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member).
  3. Write the skill's description so it says which role it is for, because there is no group target on Team. See [starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member](../../../../starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member).
  - Done when: A pilot user in the role sees the skill after the plugin updates, and its description names the role.
- [ ] **S-C4.connect-kit-runbook.google-drive** Connect it by following the kit's runbook for this connector (google-drive) (owner: integration-engineer, part A3)
  1. Check the runbook's prerequisites, including who must approve the connector. See [starter-kit/runbooks/google-workspace-connectors.md#before-you-start](../../../../starter-kit/runbooks/google-workspace-connectors.md#before-you-start).
  2. Follow the runbook's steps to add the connector and set each tool as the story's tool tasks say. See [starter-kit/runbooks/google-workspace-connectors.md#steps](../../../../starter-kit/runbooks/google-workspace-connectors.md#steps).
  3. Run the runbook's checks with a pilot user before the task is built. See [starter-kit/runbooks/google-workspace-connectors.md#check-it-worked](../../../../starter-kit/runbooks/google-workspace-connectors.md#check-it-worked).
  4. Record the hand-over the runbook asks for in the customer's folder. See [starter-kit/runbooks/google-workspace-connectors.md#hand-over](../../../../starter-kit/runbooks/google-workspace-connectors.md#hand-over).
  - Done when: A pilot user has connected with the planned identity, each tool is set as the story's tool tasks say, and the runbook's checks pass.
- [ ] **S-C4.connect-kit-runbook.hubspot** Connect it by following the kit's runbook for this connector (hubspot) (owner: integration-engineer, part A3)
  1. Check the runbook's prerequisites, including who must approve the connector. See [starter-kit/runbooks/hubspot-connector.md#before-you-start](../../../../starter-kit/runbooks/hubspot-connector.md#before-you-start).
  2. Follow the runbook's steps to add the connector and set each tool as the story's tool tasks say. See [starter-kit/runbooks/hubspot-connector.md#steps](../../../../starter-kit/runbooks/hubspot-connector.md#steps).
  3. Run the runbook's checks with a pilot user before the task is built. See [starter-kit/runbooks/hubspot-connector.md#check-it-worked](../../../../starter-kit/runbooks/hubspot-connector.md#check-it-worked).
  4. Record the hand-over the runbook asks for in the customer's folder. See [starter-kit/runbooks/hubspot-connector.md#hand-over](../../../../starter-kit/runbooks/hubspot-connector.md#hand-over).
  - Done when: A pilot user has connected with the planned identity, each tool is set as the story's tool tasks say, and the runbook's checks pass.
- [ ] **S-C4.tool-always-allow.google-drive-read** Set the connector tool to Always allow, as the levelled tools list says (google-drive-read) (owner: technical-owner, Teodor Amsel (IT and operations lead), part A7)
  1. Open the connector's page in the Claude org and find the tool. See [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced).
  2. Set the tool to Always allow and record the change. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  - Done when: The tool is set to Always allow in the Claude org, as levelled.json says.
- [ ] **S-C4.tool-blocked.hubspot-create** Set the connector tool to Blocked, as the levelled tools list says (hubspot-create) (owner: technical-owner, Teodor Amsel (IT and operations lead), part A7)
  1. Open the connector's page in the Claude org and find the tool. See [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced).
  2. Set the tool to Blocked, or leave it out of the role plugin, and record the change. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  - Done when: The tool is Blocked in the Claude org, as levelled.json says, and the twin cannot call it.
- [ ] **S-C4.deliver-draft** Agree where the twin's draft lands and who sends or files it while the twin cannot write it (owner: business-owner, Marisol Quenby (Customer success team lead), part A4)
  1. Agree with the pilot users that the twin ends in a draft, and that a person sends or files it while the twin cannot write it itself. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  2. Where the story's delivery says the write opens, agree the evidence that moves the task up to the level where the twin writes it itself. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  3. Name who puts the draft in its destination (a draft in the conversation; the HubSpot company record) and write down how, from the connector's runbook. See [starter-kit/runbooks/hubspot-connector.md](../../../../starter-kit/runbooks/hubspot-connector.md).
  - Done when: The business owner has agreed where each draft lands and who sends or files it, and the pilot users know.
- [ ] **S-C4.evidence-level-2** Gather the evidence to move the task up to level 2, act with approval (owner: business-owner, Marisol Quenby (Customer success team lead), part A8)
  1. Show the evals pass reliably at the current level. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Bring a month of scorecard results, with the edit rate, to the business owner. See [docs/compendium/15-governance-and-performance.md#measuring-performance](../../../../docs/compendium/15-governance-and-performance.md#measuring-performance).
  - Done when: The business owner has approved the move to level 2 on scorecard evidence, and the tool settings are changed.
- [ ] **S-C4.twin-marker-crm.hubspot** Add a twin marker to this CRM: the kit has no marker for it yet (hubspot) (owner: source-system-admin, acting: Teodor Amsel (IT and operations lead), part A3)
  1. The CRM write tool hubspot-create is Blocked at the starting level and opens at level 2; set the marker up before it opens. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Choose a marker the CRM can hold on every record the twin writes, such as a field or a note prefix. See [docs/compendium/15-governance-and-performance.md#what-each-source-records](../../../../docs/compendium/15-governance-and-performance.md#what-each-source-records).
  3. Create it in the CRM and limit who can set it to the role's users, as the kit's Salesforce marker does. See [starter-kit/connectors/salesforce/README.md#who-can-edit-the-field](../../../../starter-kit/connectors/salesforce/README.md#who-can-edit-the-field).
  - Done when: Every record type the twin writes in this CRM can carry the twin marker.
- [ ] **S-C4.twin-marker-skill** Make the skill set the twin marker on every CRM write (owner: skill-engineer, part A2)
  1. The CRM write tool hubspot-create is Blocked at the starting level and opens at level 2; set the marker up before it opens. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Add a step to the skill that sets the twin marker with every write. See [docs/compendium/15-governance-and-performance.md#what-each-source-records](../../../../docs/compendium/15-governance-and-performance.md#what-each-source-records).
  3. Add an eval that fails when a write leaves the twin marker unset. See [starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals](../../../../starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals).
  - Done when: The evals show every CRM write the twin makes carries the twin marker.
- [ ] **S-C4.twin-marker-report** Report on the twin marker in the CRM's own history (owner: business-owner, Marisol Quenby (Customer success team lead), part A8)
  1. The CRM write tool hubspot-create is Blocked at the starting level and opens at level 2; set the marker up before it opens. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Build a CRM report of the records the twin marker shows the twin changed. See [docs/compendium/15-governance-and-performance.md#what-each-source-records](../../../../docs/compendium/15-governance-and-performance.md#what-each-source-records).
  3. Add the count of twin-written changes to the monthly scorecard. See [docs/compendium/15-governance-and-performance.md#measuring-performance](../../../../docs/compendium/15-governance-and-performance.md#measuring-performance).
  - Done when: The business owner can see in the CRM which changes the twin made.
- [ ] **S-C4.confirm-unverified-decision.connectors.google-drive** Confirm the unverified fact behind this decision with Anthropic or the vendor before build (connectors.google-drive) (owner: solution-architect, part A3)
  1. Find the Unverified mark on the page the decision cites in levelled.json. See [partner-kit/docs/design.md#72-decision-values](../../../../partner-kit/docs/design.md#72-decision-values).
  2. Ask Anthropic or the vendor in writing, using the partner questions list. See [docs/compendium/12-orgs-and-ownership.md#questions-to-bring-to-anthropic-as-a-partner](../../../../docs/compendium/12-orgs-and-ownership.md#questions-to-bring-to-anthropic-as-a-partner).
  3. Record the answer with its source and level the card again. See [docs/compendium/08-open-questions.md#questions-most-first-time-builders-miss](../../../../docs/compendium/08-open-questions.md#questions-most-first-time-builders-miss).
  - Done when: The fact is confirmed in writing with a source, or the decision is changed so it no longer rests on it.
- [ ] **S-C4.warning-unmanaged-connectors-read-only** Resolve warning unmanaged-connectors-read-only: make the connectors read-only on an unmanaged device (owner: technical-owner, Teodor Amsel (IT and operations lead), part A7)
  1. Explain why confidential data on an unmanaged device calls for read-only connectors. See [docs/compendium/13-devices.md#policy-by-data-class-and-device-our-recommendation](../../../../docs/compendium/13-devices.md#policy-by-data-class-and-device-our-recommendation).
  2. Leave the task's write tools Blocked at the starting level, as their tool tasks set them, so the connectors are read-only. See [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced).
  3. When the task moves up a level, keep the write tools Blocked for people on unmanaged devices, or get the customer's written acceptance of the write and set them to Needs approval, never Always allow. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  - Done when: The write tools are Blocked at the starting level, and the customer's written acceptance is recorded before any of them opens for people on unmanaged devices.
- [ ] **S-C4.warning-memory-poisoning-risk** Resolve warning memory-poisoning-risk: keep memory writes to controlled steps for the task that reads untrusted input (owner: solution-architect, part A6)
  1. Explain how untrusted input can poison memory, and that memory on claude.ai is one org-wide switch. See [docs/compendium/02-persona.md#memory](../../../../docs/compendium/02-persona.md#memory).
  2. Keep role knowledge in reviewed skills and build the task so it never writes memory; only controlled steps write it. See [starter-kit/templates/pilot/memory-policy.md#tasks-that-read-input-written-by-outsiders](../../../../starter-kit/templates/pilot/memory-policy.md#tasks-that-read-input-written-by-outsiders).
  3. If the org cannot keep memory writes to controlled steps, ask the Owner to switch memory off org-wide. See [docs/compendium/09-plans-and-it-controls.md#feature-matrix](../../../../docs/compendium/09-plans-and-it-controls.md#feature-matrix).
  - Done when: The evals show the task writes nothing to memory, its role knowledge lives in reviewed skills, and the org's memory setting is agreed.
- [ ] **S-C4.warning-confidential-standard-retention** Resolve warning confidential-standard-retention: set custom retention or record the customer's acceptance (owner: compliance, Pieter Achterberg (Finance and legal lead), part A7)
  1. Explain that page 10 requires custom retention for confidential data, otherwise local sessions are kept 6 years. See [docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above](../../../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above).
  2. On Enterprise, set custom retention; on Team, record that the customer accepts standard retention. See [docs/compendium/10-sensitive-data.md#other-controls](../../../../docs/compendium/10-sensitive-data.md#other-controls).
  - Done when: Custom retention is set, or the customer's acceptance of standard retention is recorded.

## F-renewals: Renewals

Kind: capability. Status: todo. 2 stories.

### S-C2: Weekly renewal-risk digest

As a Customer success manager, I want my twin to weekly renewal-risk digest so that I get the renewal-risk digest.

Part A4. In pilot: no. Priority: 3. Status: todo.

| Field | Value |
|---|---|
| Data class | confidential |
| Surface | claude-tag-routine; surfaces: slack |
| Autonomy | 1 to 2 |
| Connectors and identity | hubspot: service-account identity, read, always-allow; usage-db: service-account identity, read, always-allow; slack: service-account identity, write, blocked |
| Wall impact | none |
| Inputs | hubspot (renewal dates, deal stage, contacts); usage-db (usage trend per account) |
| Output and audience | Renewal-risk digest, internal; to The team's Slack channel |
| Delivery | The Claude Tag routine posts it in its own Slack channel itself, and the connector's send tool slack-send is not used. |
| Skill owner | Marisol Quenby |
| Baseline | 1 per week x 90 minutes each x 8 users |

**Acceptance criteria:**

1. Eval from good example 1 of 2 (Shared drive 'CS examples' (invented)): the twin's output matches what a person accepted.
2. Eval from good example 2 of 2 (Shared drive 'CS examples' (invented)): the twin's output matches what a person accepted.
3. Eval from bad example 1 of 1 (Shared drive 'CS examples' (invented)): the twin does not repeat the mistake.

**Gated by:**

- Nothing.

**Tasks:**

- [ ] **S-C2.collect-examples** Collect 3 examples of the task from real work, each with the result a person expects (owner: skill-owner, Marisol Quenby, part A8)
  1. Ask the people who do the task today for three recent, real examples of it. See [starter-kit/docs/authoring-skills.md#step-order](../../../../starter-kit/docs/authoring-skills.md#step-order).
  2. Record each example's inputs and the output a person would accept as done. See [starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals](../../../../starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals).
  3. Remove any data the examples must not carry into the repository, keeping their shape. See [docs/compendium/10-sensitive-data.md#design-patterns-that-keep-data-out-of-the-conversation](../../../../docs/compendium/10-sensitive-data.md#design-patterns-that-keep-data-out-of-the-conversation).
  - Done when: Three real examples, each with its inputs and its expected result, are stored where the evals can read them.
- [ ] **S-C2.write-evals** Write the evals from the examples and the story's acceptance criteria (owner: skill-engineer, part A8)
  1. Turn each example and each acceptance criterion into an eval case with its expected result. See [starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals](../../../../starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals).
  2. Put the eval cases in the files the kit expects, next to the skill. See [starter-kit/docs/authoring-skills.md#the-eval-files](../../../../starter-kit/docs/authoring-skills.md#the-eval-files).
  3. Run the evals once before any skill exists and keep the failing baseline. See [docs/compendium/03-skills-authoring.md#evaluate-first-then-iterate](../../../../docs/compendium/03-skills-authoring.md#evaluate-first-then-iterate).
  - Done when: Every acceptance criterion has at least one eval, and the evals run and fail without the skill.
- [ ] **S-C2.write-skill** Write the skill from the kit template until the evals pass (owner: skill-engineer, part A2)
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
- [ ] **S-C2.trigger-evals** Write and run the trigger evals for the skill (owner: skill-engineer, part A8)
  1. Install skill-creator where the evals run. See [starter-kit/docs/authoring-skills.md#install-skill-creator](../../../../starter-kit/docs/authoring-skills.md#install-skill-creator).
  2. Write prompts that should and should not start the skill, as trigger evals. See [starter-kit/docs/authoring-skills.md#the-eval-files](../../../../starter-kit/docs/authoring-skills.md#the-eval-files).
  3. Run the trigger evals and tighten the description until they pass. See [docs/compendium/03-skills-authoring.md#writing-a-good-description](../../../../docs/compendium/03-skills-authoring.md#writing-a-good-description).
  - Done when: The skill starts on every should-trigger prompt and on none of the should-not prompts.
- [ ] **S-C2.second-review** Have a second person review the skill and its evals (owner: skill-owner, Marisol Quenby, part A8)
  1. Open a pull request with the skill and its evals. See [docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often](../../../../docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often).
  2. Have someone other than the author review it against the definition of done. See [docs/playbook/04-stories.md#definition-of-done](../../../../docs/playbook/04-stories.md#definition-of-done).
  - Done when: A reviewer who did not write the skill has approved the pull request and the evals pass.
- [ ] **S-C2.setup-tag-routine** Set up the Claude Tag routine in the team's Slack channel (owner: integration-engineer, part A4)
  1. Check the runbook's prerequisites: the plan, the Routines toggle, the Owner and Slack admin, and the channel. See [starter-kit/runbooks/claude-tag-routine.md#before-you-start](../../../../starter-kit/runbooks/claude-tag-routine.md#before-you-start).
  2. Create the routine in the Slack channel the card names, with the skill as its instructions, and set its schedule. See [starter-kit/runbooks/claude-tag-routine.md#steps](../../../../starter-kit/runbooks/claude-tag-routine.md#steps).
  3. Check who can read the channel against the task's data class. See [docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above](../../../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above).
  4. Run it once by hand and check that it posted in the channel. See [starter-kit/runbooks/claude-tag-routine.md#check-it-worked](../../../../starter-kit/runbooks/claude-tag-routine.md#check-it-worked).
  5. Hand the routine over to the person who answers for it in the channel. See [starter-kit/runbooks/claude-tag-routine.md#hand-over](../../../../starter-kit/runbooks/claude-tag-routine.md#hand-over).
  - Done when: The routine has posted once on its schedule in a channel whose members fit the data class.
- [ ] **S-C2.credentials-service-account** Create the service account the plan names, with only the access the task needs (owner: technical-owner, Teodor Amsel (IT and operations lead), part A5)
  1. Create the service account in each system the task reads or writes. See [docs/compendium/11-connectors.md#what-exists-for-our-systems](../../../../docs/compendium/11-connectors.md#what-exists-for-our-systems).
  2. Grant it only the objects and actions the card lists for the task. See [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced).
  3. Record who owns the account and when its access is reviewed. See [docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often](../../../../docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often).
  - Done when: The service account exists, holds only the task's access, and has a named owner and review date.
- [ ] **S-C2.success-check** Add an explicit success check to every run (owner: skill-engineer, part A8)
  1. Define what a successful run produces, beyond the session ending cleanly. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Make each run check that result and report a failure when it is missing. See [docs/compendium/15-governance-and-performance.md#what-each-source-records](../../../../docs/compendium/15-governance-and-performance.md#what-each-source-records).
  - Done when: A run that ends without its result is reported as failed, not as succeeded.
- [ ] **S-C2.missed-run-plan** Plan for missed runs and reconcile them (owner: integration-engineer, part A4)
  1. List how a run can be missed: a skipped schedule, a failed trigger or a webhook that gave up. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Add a reconciliation step that finds missed runs and reruns or reports them. See [docs/compendium/15-governance-and-performance.md#what-each-source-records](../../../../docs/compendium/15-governance-and-performance.md#what-each-source-records).
  3. Name the person who handles a run that still fails. See [docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often](../../../../docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often).
  - Done when: A missed run is found and handled within one cycle, by a named person.
- [ ] **S-C2.connect-kit-runbook.hubspot** Connect it by following the kit's runbook for this connector (hubspot) (owner: integration-engineer, part A3)
  1. Check the runbook's prerequisites, including who must approve the connector. See [starter-kit/runbooks/hubspot-connector.md#before-you-start](../../../../starter-kit/runbooks/hubspot-connector.md#before-you-start).
  2. Follow the runbook's steps to add the connector and set each tool as the story's tool tasks say. See [starter-kit/runbooks/hubspot-connector.md#steps](../../../../starter-kit/runbooks/hubspot-connector.md#steps).
  3. Run the runbook's checks with a pilot user before the task is built. See [starter-kit/runbooks/hubspot-connector.md#check-it-worked](../../../../starter-kit/runbooks/hubspot-connector.md#check-it-worked).
  4. Record the hand-over the runbook asks for in the customer's folder. See [starter-kit/runbooks/hubspot-connector.md#hand-over](../../../../starter-kit/runbooks/hubspot-connector.md#hand-over).
  - Done when: A pilot user has connected with the planned identity, each tool is set as the story's tool tasks say, and the runbook's checks pass.
- [ ] **S-C2.connect-kit-runbook.slack** Connect it by following the kit's runbook for this connector (slack) (owner: integration-engineer, part A3)
  1. Check the runbook's prerequisites, including who must approve the connector. See [starter-kit/runbooks/slack-connector.md#before-you-start](../../../../starter-kit/runbooks/slack-connector.md#before-you-start).
  2. Follow the runbook's steps to add the connector and set each tool as the story's tool tasks say. See [starter-kit/runbooks/slack-connector.md#steps](../../../../starter-kit/runbooks/slack-connector.md#steps).
  3. Run the runbook's checks with a pilot user before the task is built. See [starter-kit/runbooks/slack-connector.md#check-it-worked](../../../../starter-kit/runbooks/slack-connector.md#check-it-worked).
  4. Record the hand-over the runbook asks for in the customer's folder. See [starter-kit/runbooks/slack-connector.md#hand-over](../../../../starter-kit/runbooks/slack-connector.md#hand-over).
  - Done when: A pilot user has connected with the planned identity, each tool is set as the story's tool tasks say, and the runbook's checks pass.
- [ ] **S-C2.connect-own-mcp-server.usage-db** Connect it through our own MCP server: the directory has no connector for this system (usage-db) (owner: integration-engineer, part A3)
  1. Build our own MCP server for the system, with read-only tools that return only what the task needs. See [docs/compendium/11-connectors.md#building-our-own-mcp-server](../../../../docs/compendium/11-connectors.md#building-our-own-mcp-server).
  2. Make it reachable from Claude: allowlist Anthropic's IP range at the edge, or run the agent inside the network. See [docs/compendium/11-connectors.md#adding-a-connector-that-isnt-in-the-directory](../../../../docs/compendium/11-connectors.md#adding-a-connector-that-isnt-in-the-directory).
  3. Review the server before it is enabled, as for a bought connector, and write down the steps you followed. See [docs/compendium/11-connectors.md#buying-a-connector-and-reviewing-it](../../../../docs/compendium/11-connectors.md#buying-a-connector-and-reviewing-it).
  - Done when: Our server answers the task's reads for a pilot user with the planned identity, and it has been reviewed.
- [ ] **S-C2.tool-always-allow.hubspot-read** Set the connector tool to Always allow, as the levelled tools list says (hubspot-read) (owner: technical-owner, Teodor Amsel (IT and operations lead), part A7)
  1. Open the connector's page in the Claude org and find the tool. See [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced).
  2. Set the tool to Always allow and record the change. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  - Done when: The tool is set to Always allow in the Claude org, as levelled.json says.
- [ ] **S-C2.tool-always-allow.usage-db-read** Set the connector tool to Always allow, as the levelled tools list says (usage-db-read) (owner: technical-owner, Teodor Amsel (IT and operations lead), part A7)
  1. Open the connector's page in the Claude org and find the tool. See [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced).
  2. Set the tool to Always allow and record the change. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  - Done when: The tool is set to Always allow in the Claude org, as levelled.json says.
- [ ] **S-C2.tool-blocked.slack-send** Set the connector tool to Blocked, as the levelled tools list says (slack-send) (owner: technical-owner, Teodor Amsel (IT and operations lead), part A7)
  1. Open the connector's page in the Claude org and find the tool. See [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced).
  2. Set the tool to Blocked, or leave it out of the role plugin, and record the change. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  - Done when: The tool is Blocked in the Claude org, as levelled.json says, and the twin cannot call it.
- [ ] **S-C2.evidence-level-2** Gather the evidence to move the task up to level 2, act with approval (owner: business-owner, Marisol Quenby (Customer success team lead), part A8)
  1. Show the evals pass reliably at the current level. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Bring a month of scorecard results, with the edit rate, to the business owner. See [docs/compendium/15-governance-and-performance.md#measuring-performance](../../../../docs/compendium/15-governance-and-performance.md#measuring-performance).
  - Done when: The business owner has approved the move to level 2 on scorecard evidence, and the tool settings are changed.
- [ ] **S-C2.confirm-unverified-decision.connectors.slack** Confirm the unverified fact behind this decision with Anthropic or the vendor before build (connectors.slack) (owner: solution-architect, part A3)
  1. Find the Unverified mark on the page the decision cites in levelled.json. See [partner-kit/docs/design.md#72-decision-values](../../../../partner-kit/docs/design.md#72-decision-values).
  2. Ask Anthropic or the vendor in writing, using the partner questions list. See [docs/compendium/12-orgs-and-ownership.md#questions-to-bring-to-anthropic-as-a-partner](../../../../docs/compendium/12-orgs-and-ownership.md#questions-to-bring-to-anthropic-as-a-partner).
  3. Record the answer with its source and level the card again. See [docs/compendium/08-open-questions.md#questions-most-first-time-builders-miss](../../../../docs/compendium/08-open-questions.md#questions-most-first-time-builders-miss).
  - Done when: The fact is confirmed in writing with a source, or the decision is changed so it no longer rests on it.
- [ ] **S-C2.warning-private-network-allowlist** Resolve warning private-network-allowlist: allowlist Anthropic's IP range for the private system (owner: technical-owner, Teodor Amsel (IT and operations lead), part A3)
  1. Ask the customer's network owner to allowlist Anthropic's IP range at the edge. See [docs/compendium/11-connectors.md#what-exists-for-our-systems](../../../../docs/compendium/11-connectors.md#what-exists-for-our-systems).
  2. Test the connection from Claude before the task is built. See [docs/compendium/11-connectors.md#adding-a-connector-that-isnt-in-the-directory](../../../../docs/compendium/11-connectors.md#adding-a-connector-that-isnt-in-the-directory).
  - Done when: The private system answers a connector call from Claude.
- [ ] **S-C2.warning-tag-private-channel-only** Resolve warning tag-private-channel-only: run the Claude Tag routine only in a private channel (owner: technical-owner, Teodor Amsel (IT and operations lead), part A7)
  1. Create or choose a private channel limited to the team. See [docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above](../../../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above).
  2. Check the channel's members before the routine first posts. See [docs/compendium/13-devices.md#team-plan-with-no-device-management](../../../../docs/compendium/13-devices.md#team-plan-with-no-device-management).
  - Done when: The routine posts only in a private channel whose members are the team.
- [ ] **S-C2.warning-slack-directory-send-unverified** Resolve warning slack-directory-send-unverified: post through the Claude Tag routine, or the Slack MCP server only if the routine route is not used (owner: integration-engineer, part A3)
  1. Note that posting through the Slack directory connector is unverified. See [docs/compendium/11-connectors.md#what-exists-for-our-systems](../../../../docs/compendium/11-connectors.md#what-exists-for-our-systems).
  2. Post through the Claude Tag routine's own post where the task runs as a routine; use the Slack MCP server only if the routine route is not used. See [starter-kit/runbooks/claude-tag-routine.md#steps](../../../../starter-kit/runbooks/claude-tag-routine.md#steps).
  - Done when: The task posts by one confirmed route: the routine's own post, or the Slack MCP server only if the routine route is not used.
- [ ] **S-C2.warning-untrusted-input-with-send** Resolve warning untrusted-input-with-send: keep the send tool Blocked now, and approved by a person once it opens (owner: technical-owner, Teodor Amsel (IT and operations lead), part A7)
  1. Note that the task reads untrusted content and can send it out. See [docs/compendium/11-connectors.md#buying-a-connector-and-reviewing-it](../../../../docs/compendium/11-connectors.md#buying-a-connector-and-reviewing-it).
  2. Leave the send tool Blocked at the starting level, as its tool task sets it. See [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced).
  3. When the task moves up a level, set the send tool to Needs approval, never Always allow, and keep the task at level 2 or below; on a Claude Tag routine this applies only if the routine route is not used. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  - Done when: The send tool is Blocked at the starting level, never Always allow, and the task's ceiling is level 2 or below.
- [ ] **S-C2.warning-memory-poisoning-risk** Resolve warning memory-poisoning-risk: keep memory writes to controlled steps for the task that reads untrusted input (owner: solution-architect, part A6)
  1. Explain how untrusted input can poison memory, and that memory on claude.ai is one org-wide switch. See [docs/compendium/02-persona.md#memory](../../../../docs/compendium/02-persona.md#memory).
  2. Keep role knowledge in reviewed skills and build the task so it never writes memory; only controlled steps write it. See [starter-kit/templates/pilot/memory-policy.md#tasks-that-read-input-written-by-outsiders](../../../../starter-kit/templates/pilot/memory-policy.md#tasks-that-read-input-written-by-outsiders).
  3. If the org cannot keep memory writes to controlled steps, ask the Owner to switch memory off org-wide. See [docs/compendium/09-plans-and-it-controls.md#feature-matrix](../../../../docs/compendium/09-plans-and-it-controls.md#feature-matrix).
  - Done when: The evals show the task writes nothing to memory, its role knowledge lives in reviewed skills, and the org's memory setting is agreed.
- [ ] **S-C2.warning-confidential-standard-retention** Resolve warning confidential-standard-retention: set custom retention or record the customer's acceptance (owner: compliance, Pieter Achterberg (Finance and legal lead), part A7)
  1. Explain that page 10 requires custom retention for confidential data, otherwise local sessions are kept 6 years. See [docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above](../../../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above).
  2. On Enterprise, set custom retention; on Team, record that the customer accepts standard retention. See [docs/compendium/10-sensitive-data.md#other-controls](../../../../docs/compendium/10-sensitive-data.md#other-controls).
  - Done when: Custom retention is set, or the customer's acceptance of standard retention is recorded.

### S-C3: Renewal quote email to the customer

As a Customer success manager, I want my twin to renewal quote email to the customer so that I get the draft renewal quote email, which the manager checks and sends from Gmail.

Part A2. In pilot: no. Priority: 4. Status: todo.

| Field | Value |
|---|---|
| Data class | confidential |
| Surface | client-skill; surfaces: claude-ai |
| Autonomy | 1 to 2 |
| Connectors and identity | hubspot: user identity, read, always-allow |
| Wall impact | none |
| Inputs | hubspot (renewal deal, line items, products, quote) |
| Output and audience | Draft renewal quote email, which the manager checks and sends from Gmail, external; to none (a draft in the conversation) |
| Delivery | The output stays in the conversation or a local file. |
| Skill owner | Marisol Quenby |
| Baseline | 2 per week x 40 minutes each x 8 users |
| Constraints | I check the figures before I send. |

**Acceptance criteria:**

1. Eval from good example 1 of 2 (Shared drive 'CS examples' (invented)): the twin's output matches what a person accepted.
2. Eval from good example 2 of 2 (Shared drive 'CS examples' (invented)): the twin's output matches what a person accepted.
3. Eval from bad example 1 of 1 (Shared drive 'CS examples' (invented)): the twin does not repeat the mistake.
4. Keeps: I check the figures before I send.

**Gated by:**

- Nothing.

**Tasks:**

- [ ] **S-C3.collect-examples** Collect 3 examples of the task from real work, each with the result a person expects (owner: skill-owner, Marisol Quenby, part A8)
  1. Ask the people who do the task today for three recent, real examples of it. See [starter-kit/docs/authoring-skills.md#step-order](../../../../starter-kit/docs/authoring-skills.md#step-order).
  2. Record each example's inputs and the output a person would accept as done. See [starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals](../../../../starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals).
  3. Remove any data the examples must not carry into the repository, keeping their shape. See [docs/compendium/10-sensitive-data.md#design-patterns-that-keep-data-out-of-the-conversation](../../../../docs/compendium/10-sensitive-data.md#design-patterns-that-keep-data-out-of-the-conversation).
  - Done when: Three real examples, each with its inputs and its expected result, are stored where the evals can read them.
- [ ] **S-C3.write-evals** Write the evals from the examples and the story's acceptance criteria (owner: skill-engineer, part A8)
  1. Turn each example and each acceptance criterion into an eval case with its expected result. See [starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals](../../../../starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals).
  2. Put the eval cases in the files the kit expects, next to the skill. See [starter-kit/docs/authoring-skills.md#the-eval-files](../../../../starter-kit/docs/authoring-skills.md#the-eval-files).
  3. Run the evals once before any skill exists and keep the failing baseline. See [docs/compendium/03-skills-authoring.md#evaluate-first-then-iterate](../../../../docs/compendium/03-skills-authoring.md#evaluate-first-then-iterate).
  - Done when: Every acceptance criterion has at least one eval, and the evals run and fail without the skill.
- [ ] **S-C3.write-skill** Write the skill from the kit template until the evals pass (owner: skill-engineer, part A2)
  1. Copy the kit's skill template into the role plugin's skills folder, the one source of the skill for every runtime. See [starter-kit/templates/skill/README.md#copy-it](../../../../starter-kit/templates/skill/README.md#copy-it).
  2. Rename the copy to the skill's name. See [starter-kit/templates/skill/README.md#rename-it](../../../../starter-kit/templates/skill/README.md#rename-it).
  3. Fill in the description and the body, then rerun the evals until they pass. See [starter-kit/templates/skill/README.md#fill-it-in](../../../../starter-kit/templates/skill/README.md#fill-it-in).
  4. On client-skill, the skill loads from the role plugin, which an Owner publishes to claude.ai, Desktop and Cowork and which reaches a signed-in Claude Code. See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  5. On managed-agents, the skill loads from the agent's skills array (skills uploaded through the Skills API), or from a mounted GitHub repo's .claude/skills folder. See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  6. On managed-agents-self-hosted, load the skill the same two ways as hosted Managed Agents (Unverified: no compendium page says where a self-hosted deployment loads skills from). See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  7. On agent-sdk, the skill is files on disk in the runner's container, loaded through settingSources; there is no API to register a skill. See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  8. On claude-code-scheduled-task, put the skill where Claude Code loads skills: the project's .claude/skills folder or a plugin (Unverified: no compendium page says which of these a scheduled task loads). See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  9. On claude-tag-routine, give the routine the skill as its instructions (Unverified: no compendium page says whether a Claude Tag routine loads org skills). See [docs/compendium/05-decision-matrix.md#the-options](../../../../docs/compendium/05-decision-matrix.md#the-options).
  10. Make the skill keep these rules from the interviews, in the interviewee's words: I check the figures before I send..
  - Done when: The skill sits in the role plugin, it is where the task's runtime loads it from, and every eval for the story passes.
- [ ] **S-C3.trigger-evals** Write and run the trigger evals for the skill (owner: skill-engineer, part A8)
  1. Install skill-creator where the evals run. See [starter-kit/docs/authoring-skills.md#install-skill-creator](../../../../starter-kit/docs/authoring-skills.md#install-skill-creator).
  2. Write prompts that should and should not start the skill, as trigger evals. See [starter-kit/docs/authoring-skills.md#the-eval-files](../../../../starter-kit/docs/authoring-skills.md#the-eval-files).
  3. Run the trigger evals and tighten the description until they pass. See [docs/compendium/03-skills-authoring.md#writing-a-good-description](../../../../docs/compendium/03-skills-authoring.md#writing-a-good-description).
  - Done when: The skill starts on every should-trigger prompt and on none of the should-not prompts.
- [ ] **S-C3.second-review** Have a second person review the skill and its evals (owner: skill-owner, Marisol Quenby, part A8)
  1. Open a pull request with the skill and its evals. See [docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often](../../../../docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often).
  2. Have someone other than the author review it against the definition of done. See [docs/playbook/04-stories.md#definition-of-done](../../../../docs/playbook/04-stories.md#definition-of-done).
  - Done when: A reviewer who did not write the skill has approved the pull request and the evals pass.
- [ ] **S-C3.publish-in-role-plugin-team** Publish the skill in the role plugin, which every member of the Team org gets (owner: skill-engineer, part A9)
  1. Add the skill to the role plugin and bump the plugin's version. See [starter-kit/templates/role-plugin/README.md#steps](../../../../starter-kit/templates/role-plugin/README.md#steps).
  2. Add the role plugin to the one organisation-wide configuration, so every member gets the new version. See [starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member](../../../../starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member).
  3. Write the skill's description so it says which role it is for, because there is no group target on Team. See [starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member](../../../../starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member).
  - Done when: A pilot user in the role sees the skill after the plugin updates, and its description names the role.
- [ ] **S-C3.connect-kit-runbook.hubspot** Connect it by following the kit's runbook for this connector (hubspot) (owner: integration-engineer, part A3)
  1. Check the runbook's prerequisites, including who must approve the connector. See [starter-kit/runbooks/hubspot-connector.md#before-you-start](../../../../starter-kit/runbooks/hubspot-connector.md#before-you-start).
  2. Follow the runbook's steps to add the connector and set each tool as the story's tool tasks say. See [starter-kit/runbooks/hubspot-connector.md#steps](../../../../starter-kit/runbooks/hubspot-connector.md#steps).
  3. Run the runbook's checks with a pilot user before the task is built. See [starter-kit/runbooks/hubspot-connector.md#check-it-worked](../../../../starter-kit/runbooks/hubspot-connector.md#check-it-worked).
  4. Record the hand-over the runbook asks for in the customer's folder. See [starter-kit/runbooks/hubspot-connector.md#hand-over](../../../../starter-kit/runbooks/hubspot-connector.md#hand-over).
  - Done when: A pilot user has connected with the planned identity, each tool is set as the story's tool tasks say, and the runbook's checks pass.
- [ ] **S-C3.tool-always-allow.hubspot-read** Set the connector tool to Always allow, as the levelled tools list says (hubspot-read) (owner: technical-owner, Teodor Amsel (IT and operations lead), part A7)
  1. Open the connector's page in the Claude org and find the tool. See [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced).
  2. Set the tool to Always allow and record the change. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  - Done when: The tool is set to Always allow in the Claude org, as levelled.json says.
- [ ] **S-C3.evidence-level-2** Gather the evidence to move the task up to level 2, act with approval (owner: business-owner, Marisol Quenby (Customer success team lead), part A8)
  1. Show the evals pass reliably at the current level. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Bring a month of scorecard results, with the edit rate, to the business owner. See [docs/compendium/15-governance-and-performance.md#measuring-performance](../../../../docs/compendium/15-governance-and-performance.md#measuring-performance).
  - Done when: The business owner has approved the move to level 2 on scorecard evidence, and the tool settings are changed.
- [ ] **S-C3.warning-confidential-standard-retention** Resolve warning confidential-standard-retention: set custom retention or record the customer's acceptance (owner: compliance, Pieter Achterberg (Finance and legal lead), part A7)
  1. Explain that page 10 requires custom retention for confidential data, otherwise local sessions are kept 6 years. See [docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above](../../../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above).
  2. On Enterprise, set custom retention; on Team, record that the customer accepts standard retention. See [docs/compendium/10-sensitive-data.md#other-controls](../../../../docs/compendium/10-sensitive-data.md#other-controls).
  - Done when: Custom retention is set, or the customer's acceptance of standard retention is recorded.

## F-escalations: Escalations

Kind: capability. Status: todo. 1 stories.

### S-C5: Open-ticket summary when a ticket is escalated

As a Customer success manager, I want my twin to open-ticket summary when a ticket is escalated so that I get the summary of the customer's open tickets.

Part A2. In pilot: no. Priority: 5. Status: todo.

| Field | Value |
|---|---|
| Data class | confidential |
| Surface | client-skill; surfaces: claude-ai |
| Autonomy | 1 to 3 |
| Connectors and identity | zendesk: user identity, read, always-allow |
| Wall impact | none |
| Inputs | zendesk (the customer's open tickets) |
| Output and audience | Summary of the customer's open tickets, internal; to none (the conversation) |
| Delivery | The output stays in the conversation or a local file. |
| Skill owner | Marisol Quenby |
| Baseline | 2 per week x 30 minutes each x 8 users |
| Wanted change | Asked for, not planned: Something happening: the escalation itself, ideally. Today I start it when I'm told. |

**Acceptance criteria:**

1. Eval from good example 1 of 2 (Shared drive 'CS examples' (invented)): the twin's output matches what a person accepted.
2. Eval from good example 2 of 2 (Shared drive 'CS examples' (invented)): the twin's output matches what a person accepted.
3. Eval from bad example 1 of 1 (Shared drive 'CS examples' (invented)): the twin does not repeat the mistake.

**Gated by:**

- Nothing.

**Tasks:**

- [ ] **S-C5.collect-examples** Collect 3 examples of the task from real work, each with the result a person expects (owner: skill-owner, Marisol Quenby, part A8)
  1. Ask the people who do the task today for three recent, real examples of it. See [starter-kit/docs/authoring-skills.md#step-order](../../../../starter-kit/docs/authoring-skills.md#step-order).
  2. Record each example's inputs and the output a person would accept as done. See [starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals](../../../../starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals).
  3. Remove any data the examples must not carry into the repository, keeping their shape. See [docs/compendium/10-sensitive-data.md#design-patterns-that-keep-data-out-of-the-conversation](../../../../docs/compendium/10-sensitive-data.md#design-patterns-that-keep-data-out-of-the-conversation).
  - Done when: Three real examples, each with its inputs and its expected result, are stored where the evals can read them.
- [ ] **S-C5.write-evals** Write the evals from the examples and the story's acceptance criteria (owner: skill-engineer, part A8)
  1. Turn each example and each acceptance criterion into an eval case with its expected result. See [starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals](../../../../starter-kit/docs/authoring-skills.md#mapping-a-storys-acceptance-criteria-to-evals).
  2. Put the eval cases in the files the kit expects, next to the skill. See [starter-kit/docs/authoring-skills.md#the-eval-files](../../../../starter-kit/docs/authoring-skills.md#the-eval-files).
  3. Run the evals once before any skill exists and keep the failing baseline. See [docs/compendium/03-skills-authoring.md#evaluate-first-then-iterate](../../../../docs/compendium/03-skills-authoring.md#evaluate-first-then-iterate).
  - Done when: Every acceptance criterion has at least one eval, and the evals run and fail without the skill.
- [ ] **S-C5.write-skill** Write the skill from the kit template until the evals pass (owner: skill-engineer, part A2)
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
- [ ] **S-C5.trigger-evals** Write and run the trigger evals for the skill (owner: skill-engineer, part A8)
  1. Install skill-creator where the evals run. See [starter-kit/docs/authoring-skills.md#install-skill-creator](../../../../starter-kit/docs/authoring-skills.md#install-skill-creator).
  2. Write prompts that should and should not start the skill, as trigger evals. See [starter-kit/docs/authoring-skills.md#the-eval-files](../../../../starter-kit/docs/authoring-skills.md#the-eval-files).
  3. Run the trigger evals and tighten the description until they pass. See [docs/compendium/03-skills-authoring.md#writing-a-good-description](../../../../docs/compendium/03-skills-authoring.md#writing-a-good-description).
  - Done when: The skill starts on every should-trigger prompt and on none of the should-not prompts.
- [ ] **S-C5.second-review** Have a second person review the skill and its evals (owner: skill-owner, Marisol Quenby, part A8)
  1. Open a pull request with the skill and its evals. See [docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often](../../../../docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often).
  2. Have someone other than the author review it against the definition of done. See [docs/playbook/04-stories.md#definition-of-done](../../../../docs/playbook/04-stories.md#definition-of-done).
  - Done when: A reviewer who did not write the skill has approved the pull request and the evals pass.
- [ ] **S-C5.publish-in-role-plugin-team** Publish the skill in the role plugin, which every member of the Team org gets (owner: skill-engineer, part A9)
  1. Add the skill to the role plugin and bump the plugin's version. See [starter-kit/templates/role-plugin/README.md#steps](../../../../starter-kit/templates/role-plugin/README.md#steps).
  2. Add the role plugin to the one organisation-wide configuration, so every member gets the new version. See [starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member](../../../../starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member).
  3. Write the skill's description so it says which role it is for, because there is no group target on Team. See [starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member](../../../../starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member).
  - Done when: A pilot user in the role sees the skill after the plugin updates, and its description names the role.
- [ ] **S-C5.connect-kit-runbook.zendesk** Connect it by following the kit's runbook for this connector (zendesk) (owner: integration-engineer, part A3)
  1. Check the runbook's prerequisites, including who must approve the connector. See [starter-kit/runbooks/zendesk-connector.md#before-you-start](../../../../starter-kit/runbooks/zendesk-connector.md#before-you-start).
  2. Follow the runbook's steps to add the connector and set each tool as the story's tool tasks say. See [starter-kit/runbooks/zendesk-connector.md#steps](../../../../starter-kit/runbooks/zendesk-connector.md#steps).
  3. Run the runbook's checks with a pilot user before the task is built. See [starter-kit/runbooks/zendesk-connector.md#check-it-worked](../../../../starter-kit/runbooks/zendesk-connector.md#check-it-worked).
  4. Record the hand-over the runbook asks for in the customer's folder. See [starter-kit/runbooks/zendesk-connector.md#hand-over](../../../../starter-kit/runbooks/zendesk-connector.md#hand-over).
  - Done when: A pilot user has connected with the planned identity, each tool is set as the story's tool tasks say, and the runbook's checks pass.
- [ ] **S-C5.tool-always-allow.zendesk-read** Set the connector tool to Always allow, as the levelled tools list says (zendesk-read) (owner: technical-owner, Teodor Amsel (IT and operations lead), part A7)
  1. Open the connector's page in the Claude org and find the tool. See [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced).
  2. Set the tool to Always allow and record the change. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  - Done when: The tool is set to Always allow in the Claude org, as levelled.json says.
- [ ] **S-C5.evidence-level-2** Gather the evidence to move the task up to level 2, act with approval (owner: business-owner, Marisol Quenby (Customer success team lead), part A8)
  1. Show the evals pass reliably at the current level. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Bring a month of scorecard results, with the edit rate, to the business owner. See [docs/compendium/15-governance-and-performance.md#measuring-performance](../../../../docs/compendium/15-governance-and-performance.md#measuring-performance).
  - Done when: The business owner has approved the move to level 2 on scorecard evidence, and the tool settings are changed.
- [ ] **S-C5.evidence-level-3** Gather the evidence to move the task up to level 3, act within an allowlist (owner: business-owner, Marisol Quenby (Customer success team lead), part A8)
  1. Confirm every allowlisted action can be undone or stays internal. See [docs/compendium/06-autonomy.md#rules-for-moving-up-a-level](../../../../docs/compendium/06-autonomy.md#rules-for-moving-up-a-level).
  2. Show a stable eval pass rate, a low edit rate and few rejections at level 2. See [docs/compendium/15-governance-and-performance.md#measuring-performance](../../../../docs/compendium/15-governance-and-performance.md#measuring-performance).
  3. List the tools to set to Always allow and keep every other tool on Needs approval. See [docs/compendium/06-autonomy.md#the-ladder-our-recommendation](../../../../docs/compendium/06-autonomy.md#the-ladder-our-recommendation).
  - Done when: The business owner has approved the allowlist on scorecard evidence, and only those tools are Always allow.
- [ ] **S-C5.confirm-unverified-decision.plan_fit** Confirm the unverified fact behind this decision with Anthropic or the vendor before build (plan_fit) (owner: solution-architect, part A9)
  1. Find the Unverified mark on the page the decision cites in levelled.json. See [partner-kit/docs/design.md#72-decision-values](../../../../partner-kit/docs/design.md#72-decision-values).
  2. Ask Anthropic or the vendor in writing, using the partner questions list. See [docs/compendium/12-orgs-and-ownership.md#questions-to-bring-to-anthropic-as-a-partner](../../../../docs/compendium/12-orgs-and-ownership.md#questions-to-bring-to-anthropic-as-a-partner).
  3. Record the answer with its source and level the card again. See [docs/compendium/08-open-questions.md#questions-most-first-time-builders-miss](../../../../docs/compendium/08-open-questions.md#questions-most-first-time-builders-miss).
  - Done when: The fact is confirmed in writing with a source, or the decision is changed so it no longer rests on it.
- [ ] **S-C5.confirm-unverified-decision.connectors.zendesk** Confirm the unverified fact behind this decision with Anthropic or the vendor before build (connectors.zendesk) (owner: solution-architect, part A3)
  1. Find the Unverified mark on the page the decision cites in levelled.json. See [partner-kit/docs/design.md#72-decision-values](../../../../partner-kit/docs/design.md#72-decision-values).
  2. Ask Anthropic or the vendor in writing, using the partner questions list. See [docs/compendium/12-orgs-and-ownership.md#questions-to-bring-to-anthropic-as-a-partner](../../../../docs/compendium/12-orgs-and-ownership.md#questions-to-bring-to-anthropic-as-a-partner).
  3. Record the answer with its source and level the card again. See [docs/compendium/08-open-questions.md#questions-most-first-time-builders-miss](../../../../docs/compendium/08-open-questions.md#questions-most-first-time-builders-miss).
  - Done when: The fact is confirmed in writing with a source, or the decision is changed so it no longer rests on it.
- [ ] **S-C5.warning-memory-poisoning-risk** Resolve warning memory-poisoning-risk: keep memory writes to controlled steps for the task that reads untrusted input (owner: solution-architect, part A6)
  1. Explain how untrusted input can poison memory, and that memory on claude.ai is one org-wide switch. See [docs/compendium/02-persona.md#memory](../../../../docs/compendium/02-persona.md#memory).
  2. Keep role knowledge in reviewed skills and build the task so it never writes memory; only controlled steps write it. See [starter-kit/templates/pilot/memory-policy.md#tasks-that-read-input-written-by-outsiders](../../../../starter-kit/templates/pilot/memory-policy.md#tasks-that-read-input-written-by-outsiders).
  3. If the org cannot keep memory writes to controlled steps, ask the Owner to switch memory off org-wide. See [docs/compendium/09-plans-and-it-controls.md#feature-matrix](../../../../docs/compendium/09-plans-and-it-controls.md#feature-matrix).
  - Done when: The evals show the task writes nothing to memory, its role knowledge lives in reviewed skills, and the org's memory setting is agreed.
- [ ] **S-C5.warning-connector-early-access** Resolve warning connector-early-access: confirm the early-access connector with the vendor (owner: integration-engineer, part A3)
  1. Ask the vendor about the connector's plan support and per-user checks. See [docs/compendium/11-connectors.md#what-exists-for-our-systems](../../../../docs/compendium/11-connectors.md#what-exists-for-our-systems).
  2. Record the answer with its source before the build. See [docs/compendium/11-connectors.md#buying-a-connector-and-reviewing-it](../../../../docs/compendium/11-connectors.md#buying-a-connector-and-reviewing-it).
  - Done when: The vendor's answer is recorded with its source.
- [ ] **S-C5.warning-confidential-standard-retention** Resolve warning confidential-standard-retention: set custom retention or record the customer's acceptance (owner: compliance, Pieter Achterberg (Finance and legal lead), part A7)
  1. Explain that page 10 requires custom retention for confidential data, otherwise local sessions are kept 6 years. See [docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above](../../../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above).
  2. On Enterprise, set custom retention; on Team, record that the customer accepts standard retention. See [docs/compendium/10-sensitive-data.md#other-controls](../../../../docs/compendium/10-sensitive-data.md#other-controls).
  - Done when: Custom retention is set, or the customer's acceptance of standard retention is recorded.

## F-twin-foundation: Twin foundation

Kind: foundation. Status: todo. 7 stories.

### S-persona-voice: Persona voice

As a Customer success manager, I want my twin's persona voice in place so that every task story runs safely.

Part A1. In pilot: yes. Priority: none. Status: todo.

| Field | Value |
|---|---|
| Plan | team |
| Device | unmanaged |
| Plugin name | twin-customer-success-manager |
| Distribution | everyone |
| Settings baseline | undecided |
| Governance log | no |

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
- [ ] **S-persona-voice.persona-review** Have the business owner and a pilot user review the persona voice (owner: business-owner, Marisol Quenby (Customer success team lead), part A1)
  1. Show the reviewers drafts from the twin with the persona in place. See [docs/compendium/02-persona.md#where-the-persona-lives-on-each-surface](../../../../docs/compendium/02-persona.md#where-the-persona-lives-on-each-surface).
  2. Record what they change and update persona.md and both forms. See [starter-kit/templates/persona/README.md#the-rule](../../../../starter-kit/templates/persona/README.md#the-rule).
  - Done when: The business owner has approved the persona voice.

### S-connectors-and-identity: Connectors and identity

As a Customer success manager, I want my twin's connectors and identity in place so that every task story runs safely.

Part A3. In pilot: yes. Priority: none. Status: todo.

| Field | Value |
|---|---|
| Plan | team |
| Device | unmanaged |
| Plugin name | twin-customer-success-manager |
| Distribution | everyone |
| Settings baseline | undecided |
| Governance log | no |

**Acceptance criteria:**

1. Every connector the role uses is listed with its identity and approver.
2. The role's users are in the organisation with the right role.

**Gated by:**

- Nothing.

**Tasks:**

- [ ] **S-connectors-and-identity.warning-hubspot-super-admin-approval** Resolve warning hubspot-super-admin-approval: book the HubSpot approval (owner: source-system-admin, acting: Teodor Amsel (IT and operations lead), part A3)
  1. Name the customer's HubSpot Super Admin, or a user with App Marketplace access, in the profile's owners. See [docs/compendium/11-connectors.md#what-exists-for-our-systems](../../../../docs/compendium/11-connectors.md#what-exists-for-our-systems).
  2. Book the approval alongside the Claude Owner's. See [starter-kit/runbooks/identity-devices-publishing.md#getting-people-in-and-setting-roles](../../../../starter-kit/runbooks/identity-devices-publishing.md#getting-people-in-and-setting-roles).
  - Done when: A HubSpot Super Admin, or a user with App Marketplace access, has approved the connector.
- [ ] **S-connectors-and-identity.identity-team-members** Invite the role's users and set their roles by hand (owner: technical-owner, Teodor Amsel (IT and operations lead), part A5)
  1. Invite each user of the role to the organisation. See [starter-kit/runbooks/identity-devices-publishing.md#getting-people-in-and-setting-roles](../../../../starter-kit/runbooks/identity-devices-publishing.md#getting-people-in-and-setting-roles).
  2. Record who is in the role, since the plan has no group to hold them. See [starter-kit/runbooks/identity-devices-publishing.md#team-plan-no-scim-no-group-targeting](../../../../starter-kit/runbooks/identity-devices-publishing.md#team-plan-no-scim-no-group-targeting).
  - Done when: Every user of the role is in the organisation with the right role, and the list is recorded.
- [ ] **S-connectors-and-identity.connector-inventory** List every connector the role uses, its identity and who approves it (owner: solution-architect, part A3)
  1. List the systems each task reads or writes and the connector for each. See [docs/compendium/11-connectors.md#what-exists-for-our-systems](../../../../docs/compendium/11-connectors.md#what-exists-for-our-systems).
  2. Record each connector's identity and the person who approves it. See [docs/playbook/01-engagement-model.md](../../../../docs/playbook/01-engagement-model.md).
  - Done when: Every connector the role uses is listed with its identity and approver.
- [ ] **S-connectors-and-identity.connector-review** Review each connector before it is enabled (owner: security, acting: Teodor Amsel (IT and operations lead), part A3)
  1. Review each connector against the kit's review questions. See [docs/compendium/11-connectors.md#buying-a-connector-and-reviewing-it](../../../../docs/compendium/11-connectors.md#buying-a-connector-and-reviewing-it).
  2. Record the review and any limits it sets. See [docs/compendium/11-connectors.md#adding-a-connector-that-isnt-in-the-directory](../../../../docs/compendium/11-connectors.md#adding-a-connector-that-isnt-in-the-directory).
  - Done when: A security reviewer has checked every connector before it is enabled.

### S-guardrails-and-settings: Guardrails and settings

As a Customer success manager, I want my twin's guardrails and settings in place so that every task story runs safely.

Part A7. In pilot: yes. Priority: none. Status: todo.

| Field | Value |
|---|---|
| Plan | team |
| Device | unmanaged |
| Plugin name | twin-customer-success-manager |
| Distribution | everyone |
| Settings baseline | undecided |
| Governance log | no |

**Acceptance criteria:**

1. The settings, or what replaces them, are in force for the role.
2. Compliance has signed off the data policy for each data class.

**Gated by:**

- Nothing.

**Tasks:**

- [ ] **S-guardrails-and-settings.warning-team-no-managed-settings** Resolve warning team-no-managed-settings: put the guardrails in tool permissions and skills (owner: solution-architect, part A7)
  1. List the guardrails that managed settings would have locked. See [docs/compendium/13-devices.md#team-plan-with-no-device-management](../../../../docs/compendium/13-devices.md#team-plan-with-no-device-management).
  2. Move each one into a connector tool permission or a skill, and tell the customer what cannot be locked. See [starter-kit/runbooks/identity-devices-publishing.md#what-a-team-twin-does-not-get](../../../../starter-kit/runbooks/identity-devices-publishing.md#what-a-team-twin-does-not-get).
  - Done when: Each guardrail is enforced by a tool permission or a skill, or listed as not lockable and accepted.
- [ ] **S-guardrails-and-settings.warning-confidential-on-team** Resolve warning confidential-on-team: confirm the lower audit need for confidential data on Team (owner: compliance, Pieter Achterberg (Finance and legal lead), part A7)
  1. Explain what Team lacks for confidential data. See [docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above](../../../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above).
  2. Get the compliance owner's written confirmation that the lower audit need holds. See [docs/compendium/15-governance-and-performance.md#team-plan-with-no-device-management](../../../../docs/compendium/15-governance-and-performance.md#team-plan-with-no-device-management).
  - Done when: The compliance owner has confirmed in writing that confidential data on Team is acceptable.
- [ ] **S-guardrails-and-settings.settings-none** Record what the twin relies on in place of a managed-settings baseline (owner: solution-architect, part A7)
  1. List what a baseline would have enforced. See [docs/compendium/13-devices.md#team-plan-with-no-device-management](../../../../docs/compendium/13-devices.md#team-plan-with-no-device-management).
  2. Record what replaces each item, or that nothing does. See [starter-kit/runbooks/identity-devices-publishing.md#what-a-team-twin-does-not-get](../../../../starter-kit/runbooks/identity-devices-publishing.md#what-a-team-twin-does-not-get).
  - Done when: The design lists what replaces the baseline and the customer has accepted it.
- [ ] **S-guardrails-and-settings.data-policy** Agree the data policy for each of the role's data classes with compliance (owner: compliance, Pieter Achterberg (Finance and legal lead), part A7)
  1. Take each data class the role's tasks hold through the decision matrix. See [docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above](../../../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above).
  2. Agree the device policy for each class. See [docs/compendium/13-devices.md#policy-by-data-class-and-device-our-recommendation](../../../../docs/compendium/13-devices.md#policy-by-data-class-and-device-our-recommendation).
  - Done when: Compliance has signed off the data policy for every data class the role holds.

### S-distribution: Distribution

As a Customer success manager, I want my twin's distribution in place so that every task story runs safely.

Part A9. In pilot: yes. Priority: none. Status: todo.

| Field | Value |
|---|---|
| Plan | team |
| Device | unmanaged |
| Plugin name | twin-customer-success-manager |
| Distribution | everyone |
| Settings baseline | undecided |
| Governance log | no |

**Acceptance criteria:**

1. The role plugin reaches the role's users at the current version, and no one else it must not reach.

**Gated by:**

- Nothing.

**Tasks:**

- [ ] **S-distribution.warning-team-no-group-targeting** Resolve warning team-no-group-targeting: keep the role plugin safe for everyone in the org (owner: solution-architect, part A9)
  1. Explain that on Team the role plugin goes to everyone. See [starter-kit/runbooks/identity-devices-publishing.md#team-plan-no-scim-no-group-targeting](../../../../starter-kit/runbooks/identity-devices-publishing.md#team-plan-no-scim-no-group-targeting).
  2. Check the role plugin holds nothing other roles must not see. See [starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member](../../../../starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member).
  - Done when: The role plugin holds nothing another role must not see, or the customer has chosen Enterprise.
- [ ] **S-distribution.role-plugin-build** Create the role plugin from the kit template (owner: skill-engineer, part A9)
  1. Copy and rename the role-plugin template. See [starter-kit/templates/role-plugin/README.md#steps](../../../../starter-kit/templates/role-plugin/README.md#steps).
  2. Add the persona and the skills, and the marketplace entry. See [docs/compendium/04-distribution-governance.md#recommended-pipeline-our-recommendation](../../../../docs/compendium/04-distribution-governance.md#recommended-pipeline-our-recommendation).
  - Done when: The role plugin is in the marketplace and its tests pass.
- [ ] **S-distribution.distribute-everyone** Publish the role plugin to the whole organisation (owner: technical-owner, Teodor Amsel (IT and operations lead), part A9)
  1. Publish the role plugin for every member. See [starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member](../../../../starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member).
  2. Tell the other roles the plugin is not meant for them. See [docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills](../../../../docs/compendium/04-distribution-governance.md#how-each-surface-gets-skills).
  - Done when: Every member can install the role plugin and the role's users have it.

### S-governance-log: Governance log

As a Customer success manager, I want my twin's governance log in place so that every task story runs safely.

Part A9. In pilot: yes. Priority: none. Status: todo.

| Field | Value |
|---|---|
| Plan | team |
| Device | unmanaged |
| Plugin name | twin-customer-success-manager |
| Distribution | everyone |
| Settings baseline | undecided |
| Governance log | no |

**Acceptance criteria:**

1. What is logged for the twin, and where, is agreed and checked.

**Gated by:**

- Nothing.

**Tasks:**

- [ ] **S-governance-log.warning-team-no-governance-log** Resolve warning team-no-governance-log: record use without the governance hook (owner: solution-architect, part A9)
  1. Explain that the governance log is a Claude Code hook a Team twin on the web does not get. See [docs/compendium/15-governance-and-performance.md#team-plan-with-no-device-management](../../../../docs/compendium/15-governance-and-performance.md#team-plan-with-no-device-management).
  2. Record use from the usage dashboard and the source systems' own audit instead. See [docs/compendium/15-governance-and-performance.md#what-each-source-records](../../../../docs/compendium/15-governance-and-performance.md#what-each-source-records).
  - Done when: The design says what is recorded instead of the governance log, and the customer has accepted it.
- [ ] **S-governance-log.warning-team-no-audit-log** Resolve warning team-no-audit-log: rely on the source systems' audit logs (owner: compliance, Pieter Achterberg (Finance and legal lead), part A9)
  1. Explain that Team has no audit log and no Compliance API. See [docs/compendium/15-governance-and-performance.md#team-plan-with-no-device-management](../../../../docs/compendium/15-governance-and-performance.md#team-plan-with-no-device-management).
  2. Confirm each source system's own audit covers what compliance needs. See [docs/compendium/15-governance-and-performance.md#what-each-source-records](../../../../docs/compendium/15-governance-and-performance.md#what-each-source-records).
  - Done when: Compliance has accepted the source systems' audit in place of Claude's audit log.
- [ ] **S-governance-log.governance-without-hook** Record what is logged for this twin without the governance hook (owner: solution-architect, part A9)
  1. List what the plan and surface record without the hook. See [docs/compendium/15-governance-and-performance.md#team-plan-with-no-device-management](../../../../docs/compendium/15-governance-and-performance.md#team-plan-with-no-device-management).
  2. Write it into the design and get the customer's acceptance. See [docs/compendium/15-governance-and-performance.md#what-each-source-records](../../../../docs/compendium/15-governance-and-performance.md#what-each-source-records).
  - Done when: The design says what is logged for the twin and the customer has accepted it.
- [ ] **S-governance-log.source-audit** Turn on the source systems' own audit for the twin's writes (owner: source-system-admin, acting: Teodor Amsel (IT and operations lead), part A9)
  1. Check each system the twin writes keeps an audit of changes. See [docs/compendium/15-governance-and-performance.md#what-each-source-records](../../../../docs/compendium/15-governance-and-performance.md#what-each-source-records).
  2. Turn it on where it is off and record how long it is kept. See [docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often](../../../../docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often).
  - Done when: Every system the twin writes keeps an audit of its changes.

### S-memory-policy: Memory policy

As a Customer success manager, I want my twin's memory policy in place so that every task story runs safely.

Part A6. In pilot: yes. Priority: none. Status: todo.

| Field | Value |
|---|---|
| Plan | team |
| Device | unmanaged |
| Plugin name | twin-customer-success-manager |
| Distribution | everyone |
| Settings baseline | undecided |
| Governance log | no |

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
- [ ] **S-memory-policy.memory-on** Tell the pilot users what memory keeps and how to clear it (owner: change-and-enablement-lead, part A6)
  1. Explain what personal memory keeps and which tasks keep it off. See [docs/compendium/02-persona.md#memory](../../../../docs/compendium/02-persona.md#memory).
  2. Show the pilot users how to see and clear what it keeps. See [starter-kit/templates/pilot/memory-policy.md#what-pilot-users-are-told](../../../../starter-kit/templates/pilot/memory-policy.md#what-pilot-users-are-told).
  - Done when: Every pilot user knows what memory keeps and how to clear it.

### S-pilot-rollout-and-scorecard: Pilot rollout and scorecard

As a Customer success manager, I want my twin's pilot rollout and scorecard in place so that every task story runs safely.

Part A8. In pilot: yes. Priority: none. Status: todo.

| Field | Value |
|---|---|
| Plan | team |
| Device | unmanaged |
| Plugin name | twin-customer-success-manager |
| Distribution | everyone |
| Settings baseline | undecided |
| Governance log | no |

**Acceptance criteria:**

1. The pilot users are trained, the baseline is recorded, and the first scorecard is reviewed.

**Gated by:**

- Nothing.

**Tasks:**

- [ ] **S-pilot-rollout-and-scorecard.pilot-users** Name the pilot users and agree the pilot dates (owner: business-owner, Marisol Quenby (Customer success team lead), part A8)
  1. Choose five to ten pilot users in the role. See [docs/playbook/01-engagement-model.md](../../../../docs/playbook/01-engagement-model.md).
  2. Agree the start and review dates with the business owner. See [docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often](../../../../docs/compendium/15-governance-and-performance.md#who-does-what-and-how-often).
  - Done when: The pilot users and dates are agreed and recorded.
- [ ] **S-pilot-rollout-and-scorecard.pilot-baseline** Record the baseline time for each pilot task before the pilot starts (owner: consultant, part A8)
  1. Take each pilot story's baseline from its fields table. See [docs/playbook/04-stories.md#story-template](../../../../docs/playbook/04-stories.md#story-template).
  2. Confirm it with the pilot users before they start. See [docs/compendium/15-governance-and-performance.md#measuring-performance](../../../../docs/compendium/15-governance-and-performance.md#measuring-performance).
  - Done when: Every pilot task has a baseline agreed with its users.
- [ ] **S-pilot-rollout-and-scorecard.pilot-scorecard** Set up the monthly scorecard for the twin (owner: business-owner, Marisol Quenby (Customer success team lead), part A8)
  1. Copy the kit's scorecard template and choose the adoption, quality, value and safety measures for each task. See [starter-kit/templates/pilot/scorecard.md#per-task](../../../../starter-kit/templates/pilot/scorecard.md#per-task).
  2. Take each measure as the compendium describes. See [docs/compendium/15-governance-and-performance.md#measuring-performance](../../../../docs/compendium/15-governance-and-performance.md#measuring-performance).
  3. Book the monthly review with the business owner, and record its decision on the scorecard. See [starter-kit/templates/pilot/scorecard.md#decision-this-month](../../../../starter-kit/templates/pilot/scorecard.md#decision-this-month).
  - Done when: The first monthly scorecard has been reviewed with the business owner.
- [ ] **S-pilot-rollout-and-scorecard.pilot-training** Train the pilot users and tell them how to report a failure (owner: change-and-enablement-lead, part A8)
  1. Run a short session on what the twin does, at what level, and what it never does, from the kit's session outline. See [starter-kit/templates/pilot/pilot-training.md#part-1-session-outline](../../../../starter-kit/templates/pilot/pilot-training.md#part-1-session-outline).
  2. Give the pilot users one place to report a failure or a wrong draft, with the kit's report form. See [starter-kit/templates/pilot/pilot-training.md#where-reports-go](../../../../starter-kit/templates/pilot/pilot-training.md#where-reports-go).
  - Done when: Every pilot user has been trained and knows where to report a failure.

## Retired

Nothing retired.
