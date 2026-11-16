# Deploy checklist: Example Software Co

Written by `cli.py package` from each persona's backlog.json; do not edit it by hand. Change the backlog, then run package again.

The customer's admin works through it in the customer's Claude org, in order. Each step names the backlog task or tasks it comes from, the owner, the runbook section, and the package path it uses under this folder. A ticked box means every task in the step is done in backlog.json. A gated step waits on the open question, spike or sign-off it names.

Credentials live in the customer's secret store. This checklist and every note recorded from it name an environment variable or a placeholder at most, never a key, token, password, org id or instance URL.

When an artifact is live, the consultant records it with `cli.py record <persona-dir> <task-id> --status deployed --by <admin> --evidence <note>`, then `--status verified` with the runbook's check-it-worked result.

## 1. Org settings and data policy

Settings and decisions in the customer's Claude org, before anyone uses a twin.

### customer-success-manager

- [ ] `S-guardrails-and-settings.data-policy`: Agree the data policy for each of the role's data classes with compliance
  - Owner: compliance, Pieter Achterberg (Finance and legal lead)
  - Guide: [docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above](../../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-guardrails-and-settings.retention-and-feedback-settings`: Set the org's retention period and its feedback and training-data settings to the data policy
  - Owner: technical-owner, Teodor Amsel (IT and operations lead)
  - Guide: [docs/compendium/15-governance-and-performance.md#retention-decided](../../../docs/compendium/15-governance-and-performance.md#retention-decided)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-guardrails-and-settings.spend-limits`: Set the org's spend limits and name who watches them
  - Owner: technical-owner, IT and operations lead
  - Guide: [docs/compendium/09-plans-and-it-controls.md#spend-and-usage-limits](../../../docs/compendium/09-plans-and-it-controls.md#spend-and-usage-limits)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-guardrails-and-settings.settings-none`: Record what the twin relies on in place of a managed-settings baseline
  - Owner: solution-architect, not named yet
  - Runbook: [starter-kit/runbooks/identity-devices-publishing.md#what-a-team-twin-does-not-get](../../../starter-kit/runbooks/identity-devices-publishing.md#what-a-team-twin-does-not-get)
  - Package: none, a setting, a record or an account in the customer's systems

## 2. Identity and groups

Who the twin's users are, and the accounts its hosted runs use. A credential is created in the customer's secret store; this checklist names it, never its value.

### customer-success-manager

- [ ] `S-connectors-and-identity.identity-team-members`: Invite the role's users and set their roles by hand
  - Owner: technical-owner, Teodor Amsel (IT and operations lead)
  - Runbook: [starter-kit/runbooks/identity-devices-publishing.md#getting-people-in-and-setting-roles](../../../starter-kit/runbooks/identity-devices-publishing.md#getting-people-in-and-setting-roles)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-C2.credentials-service-account`: Create the service account the plan names, with only the access the task needs
  - Owner: technical-owner, Teodor Amsel (IT and operations lead)
  - Guide: [docs/compendium/11-connectors.md#what-exists-for-our-systems](../../../docs/compendium/11-connectors.md#what-exists-for-our-systems)
  - Package: `build/bundles/customer-success-manager/C2/`

## 3. Connectors and tool permissions

Each connector the tasks use, and each tool's permission as the levelled plan sets it.

### customer-success-manager

- [ ] `S-connectors-and-identity.connector-review`: Review each connector before it is enabled
  - Owner: security, acting: Teodor Amsel (IT and operations lead)
  - Guide: [docs/compendium/11-connectors.md#buying-a-connector-and-reviewing-it](../../../docs/compendium/11-connectors.md#buying-a-connector-and-reviewing-it)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-C1.connect-kit-runbook.hubspot`, `S-C4.connect-kit-runbook.hubspot`, `S-C2.connect-kit-runbook.hubspot`, `S-C3.connect-kit-runbook.hubspot`: Connect it by following the kit's runbook for this connector (hubspot)
  - Owner: integration-engineer, not named yet
  - Runbook: [starter-kit/runbooks/hubspot-connector.md#before-you-start](../../../starter-kit/runbooks/hubspot-connector.md#before-you-start)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-C1.connect-kit-runbook.google-drive`, `S-C4.connect-kit-runbook.google-drive`: Connect it by following the kit's runbook for this connector (google-drive)
  - Owner: integration-engineer, not named yet
  - Runbook: [starter-kit/runbooks/google-workspace-connectors.md#before-you-start](../../../starter-kit/runbooks/google-workspace-connectors.md#before-you-start)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-C2.connect-kit-runbook.slack`: Connect it by following the kit's runbook for this connector (slack)
  - Owner: integration-engineer, not named yet
  - Runbook: [starter-kit/runbooks/slack-connector.md#before-you-start](../../../starter-kit/runbooks/slack-connector.md#before-you-start)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-C5.connect-kit-runbook.zendesk`: Connect it by following the kit's runbook for this connector (zendesk)
  - Owner: integration-engineer, not named yet
  - Runbook: [starter-kit/runbooks/zendesk-connector.md#before-you-start](../../../starter-kit/runbooks/zendesk-connector.md#before-you-start)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-C2.connect-own-mcp-server.usage-db`: Connect it through our own MCP server: the directory has no connector for this system (usage-db)
  - Owner: integration-engineer, not named yet
  - Guide: [docs/compendium/11-connectors.md#building-our-own-mcp-server](../../../docs/compendium/11-connectors.md#building-our-own-mcp-server)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-C4.twin-marker-hubspot.hubspot`: Create the HubSpot twin marker (Last updated by twin) (hubspot)
  - Owner: source-system-admin, acting: Teodor Amsel (IT and operations lead)
  - Guide: [starter-kit/connectors/hubspot/README.md#create-it-the-hubspot-admin-does-this](../../../starter-kit/connectors/hubspot/README.md#create-it-the-hubspot-admin-does-this)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-C1.tool-always-allow.hubspot-read`, `S-C2.tool-always-allow.hubspot-read`, `S-C3.tool-always-allow.hubspot-read`: Set the connector tool to Always allow, as the levelled tools list says (hubspot-read)
  - Owner: technical-owner, Teodor Amsel (IT and operations lead)
  - Guide: [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-C1.tool-always-allow.google-drive-read`, `S-C4.tool-always-allow.google-drive-read`: Set the connector tool to Always allow, as the levelled tools list says (google-drive-read)
  - Owner: technical-owner, Teodor Amsel (IT and operations lead)
  - Guide: [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-C2.tool-always-allow.usage-db-read`: Set the connector tool to Always allow, as the levelled tools list says (usage-db-read)
  - Owner: technical-owner, Teodor Amsel (IT and operations lead)
  - Guide: [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-C5.tool-always-allow.zendesk-read`: Set the connector tool to Always allow, as the levelled tools list says (zendesk-read)
  - Owner: technical-owner, Teodor Amsel (IT and operations lead)
  - Guide: [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-C4.tool-blocked.hubspot-create`: Set the connector tool to Blocked, as the levelled tools list says (hubspot-create)
  - Owner: technical-owner, Teodor Amsel (IT and operations lead)
  - Guide: [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-C2.tool-blocked.slack-send`: Set the connector tool to Blocked, as the levelled tools list says (slack-send)
  - Owner: technical-owner, Teodor Amsel (IT and operations lead)
  - Guide: [docs/compendium/06-autonomy.md#how-a-level-is-enforced](../../../docs/compendium/06-autonomy.md#how-a-level-is-enforced)
  - Package: none, a setting, a record or an account in the customer's systems

## 4. Publish the marketplace

Publish the customer marketplace and the role plugin to the people the plan names.

### customer-success-manager

Distribution: everyone (Team). The plan has no group targeting, so every member gets the role plugin.

- [ ] `S-distribution.distribute-everyone`: Publish the role plugin to the whole organisation
  - Owner: technical-owner, Teodor Amsel (IT and operations lead)
  - Runbook: [starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member](../../../starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member)
  - Package: `build/marketplace/`
- [ ] `S-C1.publish-in-role-plugin-team`: Publish the skill in the role plugin, which every member of the Team org gets
  - Owner: skill-engineer, not named yet
  - Runbook: [starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member](../../../starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member)
  - Package: `build/marketplace/plugins/twin-customer-success-manager/skills/account-brief-before-a-customer-call/`
- [ ] `S-C4.publish-in-role-plugin-team`: Publish the skill in the role plugin, which every member of the Team org gets
  - Owner: skill-engineer, not named yet
  - Runbook: [starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member](../../../starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member)
  - Package: `build/marketplace/plugins/twin-customer-success-manager/skills/follow-up-email-after-a-customer-call-and-a-call-note-in-hubspot/`
- [ ] `S-C3.publish-in-role-plugin-team`: Publish the skill in the role plugin, which every member of the Team org gets
  - Owner: skill-engineer, not named yet
  - Runbook: [starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member](../../../starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member)
  - Package: `build/marketplace/plugins/twin-customer-success-manager/skills/renewal-quote-email-to-the-customer/`
- [ ] `S-C5.publish-in-role-plugin-team`: Publish the skill in the role plugin, which every member of the Team org gets
  - Owner: skill-engineer, not named yet
  - Runbook: [starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member](../../../starter-kit/runbooks/identity-devices-publishing.md#plugins-one-set-for-every-member)
  - Package: `build/marketplace/plugins/twin-customer-success-manager/skills/open-ticket-summary-when-a-ticket-is-escalated/`

## 5. Hosted agents, routines and scheduled tasks

Each runtime outside the chat, created from its bundle.

### customer-success-manager

- [ ] `S-C2.setup-tag-routine`: Set up the Claude Tag routine in the team's Slack channel
  - Owner: integration-engineer, not named yet
  - Runbook: [starter-kit/runbooks/claude-tag-routine.md#before-you-start](../../../starter-kit/runbooks/claude-tag-routine.md#before-you-start)
  - Package: `build/bundles/customer-success-manager/C2/`

## 6. Governance hook

Where the governance log goes, and the hook that writes it.

### customer-success-manager

- [ ] `S-governance-log.governance-without-hook`: Record what is logged for this twin without the governance hook
  - Owner: solution-architect, not named yet
  - Guide: [docs/compendium/15-governance-and-performance.md#team-plan-with-no-device-management](../../../docs/compendium/15-governance-and-performance.md#team-plan-with-no-device-management)
  - Package: none, a setting, a record or an account in the customer's systems

## 7. Check it worked and hand over

Each runbook's check-it-worked and hand-over step, then each skill's hand-over to its owner.

### customer-success-manager

- [ ] `S-governance-log.source-audit`: Turn on the source systems' own audit for the twin's writes
  - Owner: source-system-admin, acting: Teodor Amsel (IT and operations lead)
  - Guide: [docs/compendium/15-governance-and-performance.md#what-each-source-records](../../../docs/compendium/15-governance-and-performance.md#what-each-source-records)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-C1.connect-kit-runbook.hubspot`, `S-C4.connect-kit-runbook.hubspot`, `S-C2.connect-kit-runbook.hubspot`, `S-C3.connect-kit-runbook.hubspot`: Run the runbook's checks with a pilot user before the task is built.
  - Owner: integration-engineer, not named yet
  - Runbook: [starter-kit/runbooks/hubspot-connector.md#check-it-worked](../../../starter-kit/runbooks/hubspot-connector.md#check-it-worked)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-C1.connect-kit-runbook.hubspot`, `S-C4.connect-kit-runbook.hubspot`, `S-C2.connect-kit-runbook.hubspot`, `S-C3.connect-kit-runbook.hubspot`: Record the hand-over the runbook asks for in the customer's folder.
  - Owner: integration-engineer, not named yet
  - Runbook: [starter-kit/runbooks/hubspot-connector.md#hand-over](../../../starter-kit/runbooks/hubspot-connector.md#hand-over)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-C1.connect-kit-runbook.google-drive`, `S-C4.connect-kit-runbook.google-drive`: Run the runbook's checks with a pilot user before the task is built.
  - Owner: integration-engineer, not named yet
  - Runbook: [starter-kit/runbooks/google-workspace-connectors.md#check-it-worked](../../../starter-kit/runbooks/google-workspace-connectors.md#check-it-worked)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-C1.connect-kit-runbook.google-drive`, `S-C4.connect-kit-runbook.google-drive`: Record the hand-over the runbook asks for in the customer's folder.
  - Owner: integration-engineer, not named yet
  - Runbook: [starter-kit/runbooks/google-workspace-connectors.md#hand-over](../../../starter-kit/runbooks/google-workspace-connectors.md#hand-over)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-C2.connect-kit-runbook.slack`: Run the runbook's checks with a pilot user before the task is built.
  - Owner: integration-engineer, not named yet
  - Runbook: [starter-kit/runbooks/slack-connector.md#check-it-worked](../../../starter-kit/runbooks/slack-connector.md#check-it-worked)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-C2.connect-kit-runbook.slack`: Record the hand-over the runbook asks for in the customer's folder.
  - Owner: integration-engineer, not named yet
  - Runbook: [starter-kit/runbooks/slack-connector.md#hand-over](../../../starter-kit/runbooks/slack-connector.md#hand-over)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-C5.connect-kit-runbook.zendesk`: Run the runbook's checks with a pilot user before the task is built.
  - Owner: integration-engineer, not named yet
  - Runbook: [starter-kit/runbooks/zendesk-connector.md#check-it-worked](../../../starter-kit/runbooks/zendesk-connector.md#check-it-worked)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-C5.connect-kit-runbook.zendesk`: Record the hand-over the runbook asks for in the customer's folder.
  - Owner: integration-engineer, not named yet
  - Runbook: [starter-kit/runbooks/zendesk-connector.md#hand-over](../../../starter-kit/runbooks/zendesk-connector.md#hand-over)
  - Package: none, a setting, a record or an account in the customer's systems
- [ ] `S-C2.setup-tag-routine`: Run it once by hand and check that it posted in the channel.
  - Owner: integration-engineer, not named yet
  - Runbook: [starter-kit/runbooks/claude-tag-routine.md#check-it-worked](../../../starter-kit/runbooks/claude-tag-routine.md#check-it-worked)
  - Package: `build/bundles/customer-success-manager/C2/`
- [ ] `S-C2.setup-tag-routine`: Hand the routine over to the person who answers for it in the channel.
  - Owner: integration-engineer, not named yet
  - Runbook: [starter-kit/runbooks/claude-tag-routine.md#hand-over](../../../starter-kit/runbooks/claude-tag-routine.md#hand-over)
  - Package: `build/bundles/customer-success-manager/C2/`
- [ ] `S-C1.owner-handover`: Hand the skill over to its owner
  - Owner: skill-engineer, not named yet
  - Guide: [starter-kit/templates/skill/README.md#copy-it](../../../starter-kit/templates/skill/README.md#copy-it)
  - Package: `build/marketplace/plugins/twin-customer-success-manager/skills/account-brief-before-a-customer-call/`
- [ ] `S-C4.owner-handover`: Hand the skill over to its owner
  - Owner: skill-engineer, not named yet
  - Guide: [starter-kit/templates/skill/README.md#copy-it](../../../starter-kit/templates/skill/README.md#copy-it)
  - Package: `build/marketplace/plugins/twin-customer-success-manager/skills/follow-up-email-after-a-customer-call-and-a-call-note-in-hubspot/`
- [ ] `S-C2.owner-handover`: Hand the skill over to its owner
  - Owner: skill-engineer, not named yet
  - Guide: [starter-kit/templates/skill/README.md#copy-it](../../../starter-kit/templates/skill/README.md#copy-it)
  - Package: `build/bundles/customer-success-manager/C2/`
- [ ] `S-C3.owner-handover`: Hand the skill over to its owner
  - Owner: skill-engineer, not named yet
  - Guide: [starter-kit/templates/skill/README.md#copy-it](../../../starter-kit/templates/skill/README.md#copy-it)
  - Package: `build/marketplace/plugins/twin-customer-success-manager/skills/renewal-quote-email-to-the-customer/`
- [ ] `S-C5.owner-handover`: Hand the skill over to its owner
  - Owner: skill-engineer, not named yet
  - Guide: [starter-kit/templates/skill/README.md#copy-it](../../../starter-kit/templates/skill/README.md#copy-it)
  - Package: `build/marketplace/plugins/twin-customer-success-manager/skills/open-ticket-summary-when-a-ticket-is-escalated/`
