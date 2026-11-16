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
| **Highly sensitive (private equity)** | Claude Code on a ZDR sign-in, locked by MDM. Not Desktop: ZDR doesn't cover chat or Cowork | **No direct access.** Use a **hosted twin we run** instead (see below). |
| **PHI** | Claude Code under the HIPAA configuration, locked by MDM | **Blocked.** The HIPAA settings depend on managed settings. |

Sources: [Claude Code ZDR](https://code.claude.com/docs/en/zero-data-retention) (ZDR covers Claude Code inference on Enterprise, not chat or Cowork), [HIPAA setup](https://code.claude.com/docs/en/hipaa-setup), [Server-managed settings](https://code.claude.com/docs/en/server-managed-settings.md).

## A hosted twin for unmanaged devices (our recommendation)

For private-equity users on unmanaged devices:

- Run the twin **on our infrastructure**: self-hosted Managed Agents, in the ZDR Platform org (org 3 in [12](12-orgs-and-ownership.md)). Self-hosted Managed Agents is the one Managed Agents setup that ZDR covers.
- On the Agent SDK: it signs in with an API key, and the [HIPAA setup page](https://code.claude.com/docs/en/hipaa-setup.md) says a session on "A Claude Console API key or federation credentials" is not eligible for the HIPAA configuration ([10](10-sensitive-data.md#what-hipaa-covers)). **⚠ Unverified:** whether the Agent SDK is covered under ZDR. Don't build this twin on it until Anthropic confirms in writing.
- Give it a **simple front end**: a web page behind SSO, or a Teams or Slack bot.
- The device only displays results. Tools, files and credentials stay on our servers.

Claude Tag can't fill this role, because it's unavailable under ZDR. So the Slack or Teams front end would be ours to build.

This adds engineering work. It's the price of letting unmanaged devices near deal data.

Sources: [API data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention) (self-hosted Managed Agents under ZDR; the Agent SDK isn't listed), [Claude Code ZDR](https://code.claude.com/docs/en/zero-data-retention) (Claude Tag is off under ZDR).

## Team plan with no device management

Some customers are on Team, have no MDM, and want a twin for a non-regulated role such as customer success. That twin lives in **claude.ai on the web**.

**What it gets:**

- **Org-level connector control.** An Owner adds the connectors, and each connector's tools can be set to Always allow, Needs approval or Blocked ([Connectors](https://claude.com/docs/connectors/getting-started.md), [Pricing](https://claude.com/pricing)).
- **Org-provisioned skills and plugins,** shared by an Owner to everyone. Group targeting needs Enterprise ([Provisioning skills](https://support.claude.com/en/articles/13119606-provision-and-manage-skills-for-your-organization), [Plugin admin](https://claude.com/docs/plugins/admin)).
- **A usage dashboard:** usage analytics, and the Users (30d) and Activity (30d) counts per plugin and skill ([Pricing](https://claude.com/pricing), [Plugin admin](https://claude.com/docs/plugins/admin)).

**What it doesn't get:**

- **Managed settings and hooks.** Both belong to Claude Code. The [hooks page](https://code.claude.com/docs/en/hooks) says "Claude Code fires the same hook events wherever it runs": sessions in the terminal, IDE extensions, the "Desktop app" and cloud sessions. Its "Desktop app" link goes to Claude Code's [Desktop quickstart](https://code.claude.com/docs/en/desktop-quickstart.md), which puts Claude Code "in the **Code** tab" of the desktop app: the Code tab, not a chat in Claude Desktop. In a self-hosted environment Claude Code also runs the hooks the operator seeded. (Our reading): no hook covers claude.ai chat, Cowork, Claude in Slack or Claude Tag, or Teams, because the hooks page names none of them ([15](15-governance-and-performance.md#one-governance-log-for-all-twins-our-recommendation)). Server-managed settings are on Team, but they configure Claude Code, and they are "a client-side control, not a security boundary" ([Server-managed settings](https://code.claude.com/docs/en/server-managed-settings.md), [Hooks](https://code.claude.com/docs/en/hooks)). Without MDM there is no managed settings file either (see the table above).
- **The governance log** in [15](15-governance-and-performance.md), because it is a hook.
- **An audit log or the Compliance API.** Both are Enterprise only ([Audit logs](https://support.claude.com/en/articles/9970975), [Pricing](https://claude.com/pricing)).

**So such a twin cannot meet a requirement to log every action.** (Our reading) of the sources above. If the customer has that requirement, the twin needs Claude Code on MDM-managed devices with the governance hook locked in managed settings ([15](15-governance-and-performance.md)). Enterprise adds the audit log and the Compliance API, but neither is a log of each tool call. (Our recommendation)
