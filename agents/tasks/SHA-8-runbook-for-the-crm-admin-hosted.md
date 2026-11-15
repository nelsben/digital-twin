---
id: SHA-8
title: Runbook for the CRM admin: hosted MCP connector with an External Client App and per-user OAuth
domain: shared
tier: standard
status: merged
issue: 52
parent: 23
scope: [starter-kit/runbooks/salesforce-hosted-mcp.md]
forbid: [docs/compendium/17-anthropic-pe-plugins-review.md, docs/compendium/README.md, docs/compendium/sources.md, engagements/sample-pe/design.md]
red_test: none
gate: test
budget: 2-attempts
spend: 10
---
## Why

Every deal-team skill reads the CRM through its vendor-hosted MCP server, and the auth type cannot be changed after the connector is added, so the admin needs a step-by-step runbook they can follow once and get right. Issue #52.

## Done when

- Before writing, the worker reads the vendor's current docs for its hosted MCP server and External Client Apps, and Claude's docs on adding custom connectors; every step cites the page it came from
- starter-kit/runbooks/salesforce-hosted-mcp.md covers: prerequisites, creating the External Client App, per-user OAuth (with a warning that the auth type cannot change later), adding the connector in the Claude org, read-only tool permissions for autonomy level 1, the IP allowlist (discovery E6), and a test with two users on either side of a soft wall showing each sees only their own records
- Each step names who does it (CRM admin, Claude org Owner, partner integration engineer) using the role names in docs/playbook/03-stakeholders.md
- It is generic for any customer; engagement-specific names do not appear
- Anything the docs do not confirm is marked unverified
- No other file is changed

## Review

Brain review: ten steps with owners, the auth-type warning twice, no engagement names, soft-wall test present. Salesforce's own developer pages returned 403, so Salesforce-side detail is relayed from Anthropic's Connect-to-Salesforce page and every such item is marked unverified, with a seven-item confirm list at the end. Accepted: claude.ai org connector route, own OAuth client with the Consumer Key.
