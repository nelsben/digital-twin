---
id: OPS-10
title: pe-zdr managed settings restrict MCP servers to an allowlist of the firm's reviewed connectors
domain: ops
tier: standard
status: merged
issue: 67
parent: 23
scope: [starter-kit/settings/pe-zdr.managed-settings.json, starter-kit/settings/README.md, tests/test_settings.py]
forbid: [starter-kit/runbooks/identity-devices-publishing.md, docs/compendium/17-anthropic-pe-plugins-review.md, docs/compendium/README.md, docs/compendium/sources.md, engagements/sample-pe/design.md, starter-kit/runbooks/salesforce-hosted-mcp.md, starter-kit/runbooks/microsoft-365-connector.md]
red_test: python3 -m unittest tests.test_settings
gate: test
budget: 2-attempts
spend: 10
---
## Why

Anthropic's financial-analysis plugin registers 12 third-party MCP servers, and the kit's private-equity settings baseline has no MCP allowlist, so installing a plugin would make those connectors reachable from the ZDR org. Issue #67.

## Done when

- Before editing, the worker reads https://code.claude.com/docs/en/settings and the MCP docs and uses the exact managed-settings keys they give for restricting MCP servers; if page 17's names (allowManagedMcpServersOnly, allowedMcpServers) differ from the docs, the docs win and the report says so
- starter-kit/settings/pe-zdr.managed-settings.json allows only the firm's reviewed servers, with placeholder entries for the Salesforce Hosted MCP and Microsoft 365 connectors in whatever form the docs require, and blocks all others
- If the docs show these keys cover only Claude Code (not claude.ai or Desktop connectors), starter-kit/settings/README.md says so in one or two lines and names where the org-level connector allowlist is set instead
- starter-kit/settings/README.md documents the new keys in the pe-zdr row or section
- tests/test_settings.py checks that pe-zdr has the allowlist keys and that no entry names any of the 12 upstream financial-analysis vendors (daloopa, morningstar, kensho, factset, moodys, blueskyapi, aiera, lseg, pitchbook, chronograph, egnyte, box)
- The gate passes: python3 -m unittest discover -s tests

## Review

Brain review: keys and entry shape checked against code.claude.com/docs/en/managed-mcp (allowedMcpServers + allowManagedMcpServersOnly together make the allowlist authoritative; serverUrl with * wildcards). Two placeholder entries, no vendor names, 70 tests pass. Ran on haiku as a tier experiment at $0.03 and held up.
