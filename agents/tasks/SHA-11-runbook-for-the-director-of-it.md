---
id: SHA-11
title: Runbook for the Director of IT: SCIM groups, MDM rollout of managed settings, and publishing digital-twin-kit
domain: shared
tier: standard
status: merged
issue: 56
parent: 23
scope: [starter-kit/runbooks/identity-devices-publishing.md]
forbid: [starter-kit/plugins/twin-pe-deal-team/skills/preparing-company-briefs/evals/**, starter-kit/plugins/twin-pe-deal-team/skills/drafting-crm-updates/evals/**, docs/compendium/17-anthropic-pe-plugins-review.md, docs/compendium/README.md, docs/compendium/sources.md, engagements/sample-pe/design.md, starter-kit/runbooks/salesforce-hosted-mcp.md, starter-kit/runbooks/microsoft-365-connector.md]
red_test: none
gate: test
budget: 2-attempts
spend: 10
---
## Why

The pilot cannot start until users are in the right groups, managed devices carry the settings baseline, and the kit's plugins are published to those groups. One runbook takes the Director of IT through all three. Issue #56.

## Done when

- Before writing, the worker reads Claude's current docs on SCIM provisioning, managed settings file locations per OS, and plugin marketplaces for organizations; every step cites its source
- starter-kit/runbooks/identity-devices-publishing.md covers: creating SCIM groups (all users of a role, pilot subset) in the identity provider with Okta as the worked example, deploying one of the starter-kit/settings files through Intune with Jamf and Kandji notes, verifying on a device that the settings took effect, and publishing the digital-twin-kit marketplace and its plugins to the right groups
- It links to starter-kit/settings/README.md instead of repeating which baseline to pick
- Each step names who does it using the role names in docs/playbook/03-stakeholders.md
- It is generic for any customer; engagement-specific names do not appear
- Anything the docs do not confirm is marked unverified
- No other file is changed

## Review

Brain review: runbook covers SCIM groups, managed-settings delivery and kit publishing for the Director of IT. Valid findings: baselines carry no enabledPlugins, no per-group plugin key (plugin sets go via device groups or server-managed config), a pilot group alone grants no role, Kandji marked unverified. Attempt 1 wrongly claimed the governance hook was an unwired placeholder; attempt 2 corrected it to the shipped metadata-only PostToolUse/PostToolUseFailure log that records and never blocks, with walls resting on source-system permissions. 70 tests pass.
