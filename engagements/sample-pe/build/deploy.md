# Deploy checklist: Example Capital Partners

Written by `cli.py package` from each persona's backlog.json; do not edit it by hand. Change the backlog, then run package again.

The customer's admin works through it in the customer's Claude org, in order. Each step names the backlog task or tasks it comes from, the owner, the runbook section, and the package path it uses under this folder. A ticked box means every task in the step is done in backlog.json. A gated step waits on the open question, spike or sign-off it names.

Credentials live in the customer's secret store. This checklist and every note recorded from it name an environment variable or a placeholder at most, never a key, token, password, org id or instance URL.

When an artifact is live, the consultant records it with `cli.py record <persona-dir> <task-id> --status deployed --by <admin> --evidence <note>`, then `--status verified` with the runbook's check-it-worked result.

## 1. Org settings and data policy

Settings and decisions in the customer's Claude org, before anyone uses a twin.

### deal-team-associate

- [ ] `S-guardrails-and-settings.data-policy`: Agree the data policy for each of the role's data classes with compliance
  - Owner: compliance, Chief Compliance Officer
  - Guide: [docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above](../../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-guardrails-and-settings.retention-and-feedback-settings`: Set the org's retention period and its feedback and training-data settings to the data policy
  - Owner: technical-owner, Director of IT
  - Guide: [docs/compendium/15-governance-and-performance.md#retention-decided](../../../docs/compendium/15-governance-and-performance.md#retention-decided)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-guardrails-and-settings.spend-limits`: Set the org's spend limits and name who watches them
  - Owner: technical-owner, IT
  - Guide: [docs/compendium/09-plans-and-it-controls.md#spend-and-usage-limits](../../../docs/compendium/09-plans-and-it-controls.md#spend-and-usage-limits)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-T1.zdr-retention-agreement-first`, `S-T5.zdr-retention-agreement-first`, `S-T2.zdr-retention-agreement-first`, `S-T3.zdr-retention-agreement-first`, `S-T4.zdr-retention-agreement-first`, `S-T6.zdr-retention-agreement-first`: Get the zero-data-retention agreement signed, then confirm the task runs only in that org
  - Owner: compliance, Chief Compliance Officer
  - Guide: [docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt](../../../docs/compendium/10-sensitive-data.md#what-zdr-is-and-isnt)
  - Package: none, a setting, a record or an account in the customer's systems
  - Gated (S-T1, S-T2) by: open-question E4 (spike SP-E4), open-question E6 (spike SP-E6), open-question F3 (spike SP-F3), open-question G1 (spike SP-G1), open-question OD-9 (spike SP-OD-9), open-question OD-11 (spike SP-OD-11), open-question OD-13 (spike SP-OD-13), sign-off compliance
  - Gated (S-T5) by: open-question F3 (spike SP-F3), sign-off compliance
  - Gated (S-T3) by: open-question E6 (spike SP-E6), open-question F3 (spike SP-F3), open-question OD-8 (spike SP-OD-8), open-question OD-9 (spike SP-OD-9), sign-off compliance
  - Gated (S-T4, S-T6) by: open-question F3 (spike SP-F3), open-question OD-1 (spike SP-OD-1), sign-off compliance
- [ ] `S-guardrails-and-settings.settings-deploy`: Deploy the managed-settings baseline levelled.json names to the role's devices
  - Owner: technical-owner, Director of IT
  - Runbook: [starter-kit/runbooks/identity-devices-publishing.md#4-deploy-the-managed-settings-baseline-to-devices](../../../starter-kit/runbooks/identity-devices-publishing.md#4-deploy-the-managed-settings-baseline-to-devices)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-T1.web-tools-off`, `S-T5.web-tools-off`, `S-T2.web-tools-off`, `S-T3.web-tools-off`, `S-T4.web-tools-off`, `S-T6.web-tools-off`: Check web search and web fetch are off wherever this task runs
  - Owner: technical-owner, Director of IT
  - Guide: [starter-kit/settings/README.md#keys](../../../starter-kit/settings/README.md#keys)
  - Package: none, a setting, a record or an account in the customer's systems
  - Gated (S-T1, S-T2) by: open-question E4 (spike SP-E4), open-question E6 (spike SP-E6), open-question F3 (spike SP-F3), open-question G1 (spike SP-G1), open-question OD-9 (spike SP-OD-9), open-question OD-11 (spike SP-OD-11), open-question OD-13 (spike SP-OD-13), sign-off compliance
  - Gated (S-T5) by: open-question F3 (spike SP-F3), sign-off compliance
  - Gated (S-T3) by: open-question E6 (spike SP-E6), open-question F3 (spike SP-F3), open-question OD-8 (spike SP-OD-8), open-question OD-9 (spike SP-OD-9), sign-off compliance
  - Gated (S-T4, S-T6) by: open-question F3 (spike SP-F3), open-question OD-1 (spike SP-OD-1), sign-off compliance
- [ ] `S-memory-policy.memory-off`: Keep personal memory off for the role and tell the pilot users why
  - Owner: technical-owner, Director of IT
  - Guide: [starter-kit/templates/pilot/memory-policy.md#what-pilot-users-are-told](../../../starter-kit/templates/pilot/memory-policy.md#what-pilot-users-are-told)
  - Package: none, a setting, a record or an account in the customer's systems

## 2. Identity and groups

Who the twin's users are, and the accounts its hosted runs use. A credential is created in the customer's secret store; this checklist names it, never its value.

### deal-team-associate

- [ ] `S-connectors-and-identity.identity-scim-groups`: Create the role's SCIM groups and connect SCIM in Claude
  - Owner: technical-owner, Director of IT
  - Runbook: [starter-kit/runbooks/identity-devices-publishing.md#1-create-the-scim-groups-in-the-identity-provider](../../../starter-kit/runbooks/identity-devices-publishing.md#1-create-the-scim-groups-in-the-identity-provider)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-T3.credentials-api-key-vault`: Store the runtime's credentials in the customer's vault, read-only to the runtime
  - Owner: technical-owner, Director of IT
  - Guide: [docs/compendium/11-connectors.md#what-exists-for-our-systems](../../../docs/compendium/11-connectors.md#what-exists-for-our-systems)
  - Package: `build/bundles/deal-team-associate/T3/`
  - Gated (S-T3) by: open-question E6 (spike SP-E6), open-question F3 (spike SP-F3), open-question OD-8 (spike SP-OD-8), open-question OD-9 (spike SP-OD-9), sign-off compliance

## 3. Connectors and tool permissions

Each connector the tasks use, and each tool's permission as the levelled plan sets it.

### deal-team-associate

- [ ] `S-connectors-and-identity.connector-review`: Review each connector before it is enabled
  - Owner: security, acting: Director of IT
  - Guide: [docs/compendium/11-connectors.md#buying-a-connector-and-reviewing-it](../../../docs/compendium/11-connectors.md#buying-a-connector-and-reviewing-it)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-T1.connect-salesforce-runbook.salesforce`, `S-T5.connect-salesforce-runbook.salesforce`, `S-T2.connect-salesforce-runbook.salesforce`, `S-T3.connect-salesforce-runbook.salesforce`, `S-T4.connect-salesforce-runbook.salesforce`: Connect it by following the kit's Salesforce hosted MCP runbook (salesforce)
  - Owner: source-system-admin, acting: Director of IT
  - Runbook: [starter-kit/runbooks/salesforce-hosted-mcp.md#4-choose-per-user-oauth-the-decision-you-cannot-undo](../../../starter-kit/runbooks/salesforce-hosted-mcp.md#4-choose-per-user-oauth-the-decision-you-cannot-undo)
  - Package: none, a setting, a record or an account in the customer's systems
  - Gated (S-T1, S-T2) by: open-question E4 (spike SP-E4), open-question E6 (spike SP-E6), open-question F3 (spike SP-F3), open-question G1 (spike SP-G1), open-question OD-9 (spike SP-OD-9), open-question OD-11 (spike SP-OD-11), open-question OD-13 (spike SP-OD-13), sign-off compliance
  - Gated (S-T5) by: open-question F3 (spike SP-F3), sign-off compliance
  - Gated (S-T3) by: open-question E6 (spike SP-E6), open-question F3 (spike SP-F3), open-question OD-8 (spike SP-OD-8), open-question OD-9 (spike SP-OD-9), sign-off compliance
  - Gated (S-T4) by: open-question F3 (spike SP-F3), open-question OD-1 (spike SP-OD-1), sign-off compliance
- [ ] `S-T1.connect-microsoft-365-runbook.sharepoint`, `S-T5.connect-microsoft-365-runbook.sharepoint`, `S-T4.connect-microsoft-365-runbook.sharepoint`, `S-T6.connect-microsoft-365-runbook.sharepoint`: Connect it by following the kit's Microsoft 365 connector runbook (sharepoint)
  - Owner: source-system-admin, acting: Director of IT
  - Runbook: [starter-kit/runbooks/microsoft-365-connector.md#2-decide-what-to-approve-before-consent](../../../starter-kit/runbooks/microsoft-365-connector.md#2-decide-what-to-approve-before-consent)
  - Package: none, a setting, a record or an account in the customer's systems
  - Gated (S-T1) by: open-question E4 (spike SP-E4), open-question E6 (spike SP-E6), open-question F3 (spike SP-F3), open-question G1 (spike SP-G1), open-question OD-9 (spike SP-OD-9), open-question OD-11 (spike SP-OD-11), open-question OD-13 (spike SP-OD-13), sign-off compliance
  - Gated (S-T5) by: open-question F3 (spike SP-F3), sign-off compliance
  - Gated (S-T4, S-T6) by: open-question F3 (spike SP-F3), open-question OD-1 (spike SP-OD-1), sign-off compliance
- [ ] `S-T2.connect-microsoft-365-runbook.teams`, `S-T3.connect-microsoft-365-runbook.teams`: Connect it by following the kit's Microsoft 365 connector runbook (teams)
  - Owner: source-system-admin, acting: Director of IT
  - Runbook: [starter-kit/runbooks/microsoft-365-connector.md#2-decide-what-to-approve-before-consent](../../../starter-kit/runbooks/microsoft-365-connector.md#2-decide-what-to-approve-before-consent)
  - Package: none, a setting, a record or an account in the customer's systems
  - Gated (S-T2) by: open-question E4 (spike SP-E4), open-question E6 (spike SP-E6), open-question F3 (spike SP-F3), open-question G1 (spike SP-G1), open-question OD-9 (spike SP-OD-9), open-question OD-11 (spike SP-OD-11), open-question OD-13 (spike SP-OD-13), sign-off compliance
  - Gated (S-T3) by: open-question E6 (spike SP-E6), open-question F3 (spike SP-F3), open-question OD-8 (spike SP-OD-8), open-question OD-9 (spike SP-OD-9), sign-off compliance
- [ ] `S-T2.twin-marker-salesforce.salesforce`: Deploy the Salesforce twin marker field (Last updated by twin) (salesforce)
  - Owner: source-system-admin, acting: Director of IT
  - Guide: [starter-kit/connectors/salesforce/README.md#deploy-it-the-salesforce-admin-does-this](../../../starter-kit/connectors/salesforce/README.md#deploy-it-the-salesforce-admin-does-this)
  - Package: none, a setting, a record or an account in the customer's systems
  - Gated (S-T2) by: open-question E4 (spike SP-E4), open-question E6 (spike SP-E6), open-question F3 (spike SP-F3), open-question G1 (spike SP-G1), open-question OD-9 (spike SP-OD-9), open-question OD-11 (spike SP-OD-11), open-question OD-13 (spike SP-OD-13), sign-off compliance
- [ ] `S-T1.tool-always-allow.salesforce-read`, `S-T5.tool-always-allow.salesforce-read`, `S-T2.tool-always-allow.salesforce-read`, `S-T3.tool-always-allow.salesforce-read`, `S-T4.tool-always-allow.salesforce-read`: Set the connector tool to Always allow, as the levelled tools list says (salesforce-read)
  - Owner: technical-owner, Director of IT
  - Guide: [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced)
  - Package: none, a setting, a record or an account in the customer's systems
  - Gated (S-T1, S-T2) by: open-question E4 (spike SP-E4), open-question E6 (spike SP-E6), open-question F3 (spike SP-F3), open-question G1 (spike SP-G1), open-question OD-9 (spike SP-OD-9), open-question OD-11 (spike SP-OD-11), open-question OD-13 (spike SP-OD-13), sign-off compliance
  - Gated (S-T5) by: open-question F3 (spike SP-F3), sign-off compliance
  - Gated (S-T3) by: open-question E6 (spike SP-E6), open-question F3 (spike SP-F3), open-question OD-8 (spike SP-OD-8), open-question OD-9 (spike SP-OD-9), sign-off compliance
  - Gated (S-T4) by: open-question F3 (spike SP-F3), open-question OD-1 (spike SP-OD-1), sign-off compliance
- [ ] `S-T1.tool-always-allow.sharepoint-read`, `S-T5.tool-always-allow.sharepoint-read`, `S-T4.tool-always-allow.sharepoint-read`, `S-T6.tool-always-allow.sharepoint-read`: Set the connector tool to Always allow, as the levelled tools list says (sharepoint-read)
  - Owner: technical-owner, Director of IT
  - Guide: [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced)
  - Package: none, a setting, a record or an account in the customer's systems
  - Gated (S-T1) by: open-question E4 (spike SP-E4), open-question E6 (spike SP-E6), open-question F3 (spike SP-F3), open-question G1 (spike SP-G1), open-question OD-9 (spike SP-OD-9), open-question OD-11 (spike SP-OD-11), open-question OD-13 (spike SP-OD-13), sign-off compliance
  - Gated (S-T5) by: open-question F3 (spike SP-F3), sign-off compliance
  - Gated (S-T4, S-T6) by: open-question F3 (spike SP-F3), open-question OD-1 (spike SP-OD-1), sign-off compliance
- [ ] `S-T2.tool-always-allow.teams-read`: Set the connector tool to Always allow, as the levelled tools list says (teams-read)
  - Owner: technical-owner, Director of IT
  - Guide: [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced)
  - Package: none, a setting, a record or an account in the customer's systems
  - Gated (S-T2) by: open-question E4 (spike SP-E4), open-question E6 (spike SP-E6), open-question F3 (spike SP-F3), open-question G1 (spike SP-G1), open-question OD-9 (spike SP-OD-9), open-question OD-11 (spike SP-OD-11), open-question OD-13 (spike SP-OD-13), sign-off compliance
- [ ] `S-T2.tool-blocked.salesforce-update`: Set the connector tool to Blocked, as the levelled tools list says (salesforce-update)
  - Owner: technical-owner, Director of IT
  - Guide: [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced)
  - Package: none, a setting, a record or an account in the customer's systems
  - Gated (S-T2) by: open-question E4 (spike SP-E4), open-question E6 (spike SP-E6), open-question F3 (spike SP-F3), open-question G1 (spike SP-G1), open-question OD-9 (spike SP-OD-9), open-question OD-11 (spike SP-OD-11), open-question OD-13 (spike SP-OD-13), sign-off compliance
- [ ] `S-T3.tool-blocked.teams-send`: Set the connector tool to Blocked, as the levelled tools list says (teams-send)
  - Owner: technical-owner, Director of IT
  - Guide: [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced)
  - Package: none, a setting, a record or an account in the customer's systems
  - Gated (S-T3) by: open-question E6 (spike SP-E6), open-question F3 (spike SP-F3), open-question OD-8 (spike SP-OD-8), open-question OD-9 (spike SP-OD-9), sign-off compliance

## 4. Publish the marketplace

Publish the customer marketplace and the role plugin to the people the plan names.

### deal-team-associate

Distribution: group-targeted (Enterprise). Publish the marketplace to the role's group only.

- [ ] `S-distribution.distribute-group`: Publish the marketplace and the role plugin to the role's group
  - Owner: technical-owner, Director of IT
  - Runbook: [starter-kit/runbooks/identity-devices-publishing.md#6-publish-the-marketplace-and-its-plugins-to-the-right-groups](../../../starter-kit/runbooks/identity-devices-publishing.md#6-publish-the-marketplace-and-its-plugins-to-the-right-groups)
  - Package: `build/marketplace/`
- [ ] `S-T1.publish-in-role-plugin`: Publish the skill in the role plugin
  - Owner: skill-engineer, not named yet
  - Runbook: [starter-kit/runbooks/identity-devices-publishing.md#6-publish-the-marketplace-and-its-plugins-to-the-right-groups](../../../starter-kit/runbooks/identity-devices-publishing.md#6-publish-the-marketplace-and-its-plugins-to-the-right-groups)
  - Package: `build/marketplace/plugins/twin-pe-deal-team/skills/preparing-company-briefs/`
  - Gated (S-T1) by: open-question E4 (spike SP-E4), open-question E6 (spike SP-E6), open-question F3 (spike SP-F3), open-question G1 (spike SP-G1), open-question OD-9 (spike SP-OD-9), open-question OD-11 (spike SP-OD-11), open-question OD-13 (spike SP-OD-13), sign-off compliance
- [ ] `S-T5.publish-in-role-plugin`: Publish the skill in the role plugin
  - Owner: skill-engineer, not named yet
  - Runbook: [starter-kit/runbooks/identity-devices-publishing.md#6-publish-the-marketplace-and-its-plugins-to-the-right-groups](../../../starter-kit/runbooks/identity-devices-publishing.md#6-publish-the-marketplace-and-its-plugins-to-the-right-groups)
  - Package: `build/marketplace/plugins/twin-pe-deal-team/skills/prepare-for-a-management-or-expert-call/`
  - Gated (S-T5) by: open-question F3 (spike SP-F3), sign-off compliance
- [ ] `S-T2.publish-in-role-plugin`: Publish the skill in the role plugin
  - Owner: skill-engineer, not named yet
  - Runbook: [starter-kit/runbooks/identity-devices-publishing.md#6-publish-the-marketplace-and-its-plugins-to-the-right-groups](../../../starter-kit/runbooks/identity-devices-publishing.md#6-publish-the-marketplace-and-its-plugins-to-the-right-groups)
  - Package: `build/marketplace/plugins/twin-pe-deal-team/skills/drafting-crm-updates/`
  - Gated (S-T2) by: open-question E4 (spike SP-E4), open-question E6 (spike SP-E6), open-question F3 (spike SP-F3), open-question G1 (spike SP-G1), open-question OD-9 (spike SP-OD-9), open-question OD-11 (spike SP-OD-11), open-question OD-13 (spike SP-OD-13), sign-off compliance
- [ ] `S-T4.publish-in-role-plugin`: Publish the skill in the role plugin
  - Owner: skill-engineer, not named yet
  - Runbook: [starter-kit/runbooks/identity-devices-publishing.md#6-publish-the-marketplace-and-its-plugins-to-the-right-groups](../../../starter-kit/runbooks/identity-devices-publishing.md#6-publish-the-marketplace-and-its-plugins-to-the-right-groups)
  - Package: `build/marketplace/plugins/twin-pe-deal-team/skills/screen-an-inbound-cim-or-teaser/`
  - Gated (S-T4) by: open-question F3 (spike SP-F3), open-question OD-1 (spike SP-OD-1), sign-off compliance
- [ ] `S-T6.publish-in-role-plugin`: Publish the skill in the role plugin
  - Owner: skill-engineer, not named yet
  - Runbook: [starter-kit/runbooks/identity-devices-publishing.md#6-publish-the-marketplace-and-its-plugins-to-the-right-groups](../../../starter-kit/runbooks/identity-devices-publishing.md#6-publish-the-marketplace-and-its-plugins-to-the-right-groups)
  - Package: `build/marketplace/plugins/twin-pe-deal-team/skills/draft-a-section-of-an-investment-committee-memo-from-diligence-n/`
  - Gated (S-T6) by: open-question F3 (spike SP-F3), open-question OD-1 (spike SP-OD-1), sign-off compliance

## 5. Hosted agents, routines and scheduled tasks

Each runtime outside the chat, created from its bundle.

### deal-team-associate

- [ ] `S-T3.setup-managed-agents-self-hosted`: Set up self-hosted Managed Agents in the customer's environment and its schedule or trigger
  - Owner: integration-engineer, not named yet
  - Runbook: [starter-kit/runbooks/managed-agents.md#before-you-start](../../../starter-kit/runbooks/managed-agents.md#before-you-start)
  - Package: `build/bundles/deal-team-associate/T3/`
  - Gated (S-T3) by: open-question E6 (spike SP-E6), open-question F3 (spike SP-F3), open-question OD-8 (spike SP-OD-8), open-question OD-9 (spike SP-OD-9), sign-off compliance
- [ ] `S-T3.start-wiring`: Build what starts each session from the task's event or schedule
  - Owner: integration-engineer, not named yet
  - Guide: [docs/compendium/05-decision-matrix.md#the-options](../../../docs/compendium/05-decision-matrix.md#the-options)
  - Package: `build/bundles/deal-team-associate/T3/`
  - Gated (S-T3) by: open-question E6 (spike SP-E6), open-question F3 (spike SP-F3), open-question OD-8 (spike SP-OD-8), open-question OD-9 (spike SP-OD-9), sign-off compliance

## 6. Governance hook

Where the governance log goes, and the hook that writes it.

### deal-team-associate

- [ ] `S-governance-log.governance-log-destination`: Agree the governance log's destination and who can read it
  - Owner: technical-owner, Director of IT
  - Guide: [docs/compendium/15-governance-and-performance.md#where-the-log-lives-settle-it-with-each-customer](../../../docs/compendium/15-governance-and-performance.md#where-the-log-lives-settle-it-with-each-customer)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-governance-log.governance-hook-deploy`: Deploy the governance hook through managed settings
  - Owner: integration-engineer, not named yet
  - Guide: [starter-kit/plugins/twin-governance/README.md#configuration](../../../starter-kit/plugins/twin-governance/README.md#configuration)
  - Package: none, a setting, a record or an account in the customer's systems

## 7. Check it worked and hand over

Each runbook's check-it-worked and hand-over step, then each skill's hand-over to its owner.

### deal-team-associate

- [ ] `S-guardrails-and-settings.settings-verify`: Verify on a device that the managed settings took effect
  - Owner: technical-owner, Director of IT
  - Runbook: [starter-kit/runbooks/identity-devices-publishing.md#5-verify-on-a-device-that-the-settings-took-effect](../../../starter-kit/runbooks/identity-devices-publishing.md#5-verify-on-a-device-that-the-settings-took-effect)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-governance-log.governance-log-check`: Check that a tool call reaches the governance log
  - Owner: security, acting: Director of IT
  - Guide: [starter-kit/plugins/twin-governance/README.md#the-governance-log-hook](../../../starter-kit/plugins/twin-governance/README.md#the-governance-log-hook)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-governance-log.source-audit`: Turn on the source systems' own audit for the twin's writes
  - Owner: source-system-admin, acting: Director of IT
  - Guide: [docs/compendium/15-governance-and-performance.md#what-each-source-records](../../../docs/compendium/15-governance-and-performance.md#what-each-source-records)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-T1.wall-test`, `S-T5.wall-test`, `S-T2.wall-test`, `S-T3.wall-test`, `S-T4.wall-test`, `S-T6.wall-test`: Test the information wall with two users on either side before the pilot
  - Owner: compliance, Chief Compliance Officer
  - Runbook: [starter-kit/runbooks/salesforce-hosted-mcp.md#9-test-two-users-on-either-side-of-a-soft-wall](../../../starter-kit/runbooks/salesforce-hosted-mcp.md#9-test-two-users-on-either-side-of-a-soft-wall)
  - Package: none, a setting, a record or an account in the customer's systems
  - Gated (S-T1, S-T2) by: open-question E4 (spike SP-E4), open-question E6 (spike SP-E6), open-question F3 (spike SP-F3), open-question G1 (spike SP-G1), open-question OD-9 (spike SP-OD-9), open-question OD-11 (spike SP-OD-11), open-question OD-13 (spike SP-OD-13), sign-off compliance
  - Gated (S-T5) by: open-question F3 (spike SP-F3), sign-off compliance
  - Gated (S-T3) by: open-question E6 (spike SP-E6), open-question F3 (spike SP-F3), open-question OD-8 (spike SP-OD-8), open-question OD-9 (spike SP-OD-9), sign-off compliance
  - Gated (S-T4, S-T6) by: open-question F3 (spike SP-F3), open-question OD-1 (spike SP-OD-1), sign-off compliance
- [ ] `S-T3.setup-managed-agents-self-hosted`: Run it once inside the customer's environment, check it, and hand it over.
  - Owner: integration-engineer, not named yet
  - Runbook: [starter-kit/runbooks/managed-agents.md#check-it-worked](../../../starter-kit/runbooks/managed-agents.md#check-it-worked)
  - Package: `build/bundles/deal-team-associate/T3/`
  - Gated (S-T3) by: open-question E6 (spike SP-E6), open-question F3 (spike SP-F3), open-question OD-8 (spike SP-OD-8), open-question OD-9 (spike SP-OD-9), sign-off compliance
- [ ] `S-T1.owner-handover`: Hand the skill over to its owner
  - Owner: skill-engineer, not named yet
  - Guide: [starter-kit/templates/skill/README.md#copy-it](../../../starter-kit/templates/skill/README.md#copy-it)
  - Package: `build/marketplace/plugins/twin-pe-deal-team/skills/preparing-company-briefs/`
  - Gated (S-T1) by: open-question E4 (spike SP-E4), open-question E6 (spike SP-E6), open-question F3 (spike SP-F3), open-question G1 (spike SP-G1), open-question OD-9 (spike SP-OD-9), open-question OD-11 (spike SP-OD-11), open-question OD-13 (spike SP-OD-13), sign-off compliance
- [ ] `S-T5.owner-handover`: Hand the skill over to its owner
  - Owner: skill-engineer, not named yet
  - Guide: [starter-kit/templates/skill/README.md#copy-it](../../../starter-kit/templates/skill/README.md#copy-it)
  - Package: `build/marketplace/plugins/twin-pe-deal-team/skills/prepare-for-a-management-or-expert-call/`
  - Gated (S-T5) by: open-question F3 (spike SP-F3), sign-off compliance
- [ ] `S-T2.owner-handover`: Hand the skill over to its owner
  - Owner: skill-engineer, not named yet
  - Guide: [starter-kit/templates/skill/README.md#copy-it](../../../starter-kit/templates/skill/README.md#copy-it)
  - Package: `build/marketplace/plugins/twin-pe-deal-team/skills/drafting-crm-updates/`
  - Gated (S-T2) by: open-question E4 (spike SP-E4), open-question E6 (spike SP-E6), open-question F3 (spike SP-F3), open-question G1 (spike SP-G1), open-question OD-9 (spike SP-OD-9), open-question OD-11 (spike SP-OD-11), open-question OD-13 (spike SP-OD-13), sign-off compliance
- [ ] `S-T3.owner-handover`: Hand the skill over to its owner
  - Owner: skill-engineer, not named yet
  - Guide: [starter-kit/templates/skill/README.md#copy-it](../../../starter-kit/templates/skill/README.md#copy-it)
  - Package: `build/bundles/deal-team-associate/T3/`
  - Gated (S-T3) by: open-question E6 (spike SP-E6), open-question F3 (spike SP-F3), open-question OD-8 (spike SP-OD-8), open-question OD-9 (spike SP-OD-9), sign-off compliance
- [ ] `S-T4.owner-handover`: Hand the skill over to its owner
  - Owner: skill-engineer, not named yet
  - Guide: [starter-kit/templates/skill/README.md#copy-it](../../../starter-kit/templates/skill/README.md#copy-it)
  - Package: `build/marketplace/plugins/twin-pe-deal-team/skills/screen-an-inbound-cim-or-teaser/`
  - Gated (S-T4) by: open-question F3 (spike SP-F3), open-question OD-1 (spike SP-OD-1), sign-off compliance
- [ ] `S-T6.owner-handover`: Hand the skill over to its owner
  - Owner: skill-engineer, not named yet
  - Guide: [starter-kit/templates/skill/README.md#copy-it](../../../starter-kit/templates/skill/README.md#copy-it)
  - Package: `build/marketplace/plugins/twin-pe-deal-team/skills/draft-a-section-of-an-investment-committee-memo-from-diligence-n/`
  - Gated (S-T6) by: open-question F3 (spike SP-F3), open-question OD-1 (spike SP-OD-1), sign-off compliance
