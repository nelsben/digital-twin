# 13 — Managed and unmanaged devices

## What MDM is

**MDM (mobile device management)** is how IT controls company laptops and phones. Common tools are Microsoft Intune, Jamf and Kandji. IT uses MDM to install apps, push settings that users can't change, require disk encryption, and wipe a device when someone leaves.

- A **managed device** is enrolled in MDM.
- An **unmanaged device** isn't: a personal laptop, or a contractor's machine.

This matters because **Claude's strongest controls are delivered by MDM.**

- **Claude Desktop** reads MDM policies. Examples:
  - force sign-in to our org (`forceLoginOrgUUID`)
  - turn off desktop extensions and local MCP
  - limit which folders Claude can use.
- **Claude Code** reads a managed settings file. IT can enforce the sandbox, deny rules, the allowed marketplaces, and HIPAA settings.

Anthropic's server-managed settings, which aren't delivered by MDM, are "client-side control, not a security boundary". A user can step around them.

Sources: [Desktop policies](https://support.claude.com/en/articles/12622667), [Server-managed settings](https://code.claude.com/docs/en/server-managed-settings.md), [Authentication](https://code.claude.com/docs/en/authentication.md).

## What you can enforce on each

| Control | Managed device | Unmanaged device |
|---|---|---|
| Force sign-in to *our* org only | ✓ MDM | ✗ |
| Lock Claude Code (sandbox, deny rules, allowed plugins, HIPAA settings) | ✓ managed settings file | ✗ server-managed settings only, which can be bypassed |
| Turn off desktop extensions and local MCP servers | ✓ | ✗ |
| Disk encryption, remote wipe, purging local transcripts | ✓ | ✗ |
| Block other Claude orgs (tenant restrictions) | ✓ on the corporate network | Only on the corporate network or VPN |
| SSO, SCIM, connector permissions, plugin policy | ✓ | ✓ (these are server-side) |
| Restrict which networks can reach the org (Enterprise IP allowlist, beta) | ✓ | ✓, and it can shut unmanaged devices out |

**(Our recommendation) Keep unmanaged devices out of sensitive orgs.** Combine two things:

- the Enterprise IP allowlist, limited to the corporate network or VPN
- a **device check in your identity provider** (Okta device trust, Entra conditional access), so only managed devices can sign in to org 2 or org 4.

These are standard identity-provider features, not Anthropic's.

## Policy by data class and device (our recommendation)

| Data class | Managed device | Unmanaged device |
|---|---|---|
| **Internal** | Every surface | claude.ai web and Desktop through SSO |
| **Confidential** | Every surface, with managed settings | **claude.ai web only.** No Claude Code or desktop extensions, because the sandbox and deny rules can't be enforced. Connectors read-only. |
| **Highly sensitive (private equity)** | Claude Code or Desktop on a ZDR sign-in, locked by MDM | **No direct access.** Use a **hosted twin we run** instead (see below). |
| **PHI** | Claude Code under the HIPAA configuration, locked by MDM | **Blocked.** The HIPAA settings depend on managed settings. |

## A hosted twin for unmanaged devices (our recommendation)

For private-equity users on unmanaged devices:

- Run the twin **on our infrastructure**: the Agent SDK, or self-hosted Managed Agents, in the ZDR Platform org (org 3 in [12](12-orgs-and-ownership.md)).
- Give it a **simple front end**: a web page behind SSO, or a Teams or Slack bot.
- The device only displays results. Tools, files and credentials stay on our servers.

Claude Tag can't fill this role, because it's unavailable under ZDR. So the Slack or Teams front end would be ours to build.

This adds engineering work. It's the price of letting unmanaged devices near deal data.
