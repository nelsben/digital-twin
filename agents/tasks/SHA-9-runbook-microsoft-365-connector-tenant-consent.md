---
id: SHA-9
title: Runbook: Microsoft 365 connector tenant consent and a SharePoint access check for deal-team libraries
domain: shared
tier: standard
status: merged
issue: 53
parent: 23
scope: [starter-kit/runbooks/microsoft-365-connector.md]
forbid: [docs/compendium/17-anthropic-pe-plugins-review.md, docs/compendium/README.md, docs/compendium/sources.md, engagements/sample-pe/design.md, starter-kit/runbooks/salesforce-hosted-mcp.md]
red_test: none
gate: test
budget: 2-attempts
spend: 10
---
## Why

The Microsoft 365 connector needs Global Admin consent, and the soft wall relies on SharePoint permissions being right before any twin reads deal folders. Issue #53.

## Done when

- Before writing, the worker reads Claude's current Microsoft 365 connector docs and Microsoft's admin consent docs; every step cites its source
- starter-kit/runbooks/microsoft-365-connector.md covers: prerequisites, tenant admin consent, which permissions are granted and whether access is per-user (delegated), enabling the connector for the right Claude group, and a check that deal-team SharePoint libraries are not readable by investor relations or other walled groups, including how to list library permissions
- Each step names who does it using the role names in docs/playbook/03-stakeholders.md
- It is generic for any customer; engagement-specific names do not appear
- Anything the docs do not confirm is marked unverified
- No other file is changed

## Review

Brain review: nine steps with owners, cited per step, no engagement names. Key finding accepted: the connector cannot be narrowed to chosen SharePoint sites, so the soft wall rests entirely on SharePoint permissions, and step 8 tests it three ways. Unverified items listed at the end. Accepted: Entra assignment as the working control, Claude-side group step marked unverified.
