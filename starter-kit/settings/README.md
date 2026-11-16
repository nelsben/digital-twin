# Managed-settings baselines

Claude Code settings that IT deploys to every device, one file per data class ([compendium 10](../../docs/compendium/10-sensitive-data.md), [13](../../docs/compendium/13-devices.md), [14](../../docs/compendium/14-private-equity.md)). Each file is complete, not a diff. `tests/test_settings.py` checks them.

| File | Org (compendium 12) | Data class | Plan |
|---|---|---|---|
| `general.managed-settings.json` | 1 General | Internal | Team or Enterprise ([server-managed settings](https://code.claude.com/docs/en/server-managed-settings) are on both; [compendium 09](../../docs/compendium/09-plans-and-it-controls.md)) |
| `confidential.managed-settings.json` | 1 General (confidential roles) | Confidential | Enterprise for per-group delivery ([compendium 09](../../docs/compendium/09-plans-and-it-controls.md)), or a device-management file per device on any plan. On Team one organisation-wide configuration means every member gets the same file ([server-managed settings](https://code.claude.com/docs/en/server-managed-settings#current-limitations)) |
| `pe-zdr.managed-settings.json` | 2 Private equity (ZDR) | Highly sensitive: deal data, MNPI | Enterprise only (ZDR; [compendium 09](../../docs/compendium/09-plans-and-it-controls.md)) |
| `hipaa.managed-settings.json` | 4 HIPAA, when a PHI role is in scope | PHI | Enterprise only (HIPAA; [compendium 09](../../docs/compendium/09-plans-and-it-controls.md), [10](../../docs/compendium/10-sensitive-data.md)) |

A Team customer instead pastes one baseline, `general` (or `confidential` if every member handles confidential data), as the organisation's single server-managed configuration, or deploys a device file where it has device management. Steps are in the runbook's [Team plan section](../runbooks/identity-devices-publishing.md#team-plan-no-scim-no-group-targeting).

Before deploying, replace `REPLACE-WITH-ORG-UUID` (copy the org ID from claude.ai admin settings; a wrong value makes Claude Code exit at startup), `REPLACE-WITH-GITHUB-ORG` (the repo holding this kit's marketplace, in both marketplace keys), `REPLACE-WITH-GOVERNANCE-SALT` (a secret per customer; confidential, pe-zdr and hipaa), and in pe-zdr the `REPLACE-WITH-SALESFORCE-HOSTED-MCP-HOST` and `REPLACE-WITH-MICROSOFT-365-MCP-HOST` URL placeholders.

## Keys

| Key | Does | Docs |
|---|---|---|
| `strictKnownMarketplaces` | Allowlist: only the kit's one reviewed marketplace may be added | [plugins/org](https://code.claude.com/docs/en/plugins/org) |
| `extraKnownMarketplaces` | Registers the `digital-twin-kit` marketplace on every device. The allowlist above only permits a source; it registers nothing | [plugins/org](https://code.claude.com/docs/en/plugins/org) |
| `enabledPlugins` | Force-enables `twin-shared` on every device, and `twin-governance` in confidential, pe-zdr and hipaa. No role plugin is enabled here: add it per group | [plugins/org](https://code.claude.com/docs/en/plugins/org) |
| `env` | confidential, pe-zdr, hipaa: sets `TWIN_GOVERNANCE_ORG_LABEL` and `TWIN_GOVERNANCE_SALT`. Values are plain text on the device, so the salt only keeps `cwd_hash` from being reversed by outsiders | [settings-reference](https://code.claude.com/docs/en/settings-reference) |
| `forceLoginOrgUUID` | Claude Code exits if the sign-in belongs to another org | [hipaa-setup](https://code.claude.com/docs/en/hipaa-setup) |
| `permissions.disableBypassPermissionsMode` | `"disable"` stops bypassPermissions mode | [managed-settings](https://code.claude.com/docs/en/server-managed-settings) |
| `allowManagedHooksOnly` | Only hooks IT deploys run (not in general) | [settings-reference](https://code.claude.com/docs/en/settings-reference) |
| `permissions.deny` | Blocks reads of `.env`, credential, key and cloud-config files; WebFetch and WebSearch off in pe-zdr and hipaa | [permissions](https://code.claude.com/docs/en/permissions) |
| `allowManagedMcpServersOnly` + `allowedMcpServers` | pe-zdr only: Claude Code loads just the listed MCP servers (matched by `serverUrl`, with `*` wildcards); plugin-provided servers are checked too, so the 12 financial-analysis connectors stay blocked. Entries are the Salesforce Hosted MCP and Microsoft 365 placeholders until replaced | [managed-mcp](https://code.claude.com/docs/en/managed-mcp) |
| `forceLoginMethod` | pe-zdr and hipaa: claude.ai sign-in (`claudeai`) | [settings-reference](https://code.claude.com/docs/en/settings-reference) |
| `allowedProviders`, `cleanupPeriodDays` | hipaa only: Anthropic API only, transcripts kept 30 days. The HIPAA configuration needs Claude Code v2.1.285 or later ([compendium 10](../../docs/compendium/10-sensitive-data.md)): run `claude --version` on each device before you deploy | [hipaa-setup](https://code.claude.com/docs/en/hipaa-setup) |

The MCP allowlist covers servers Claude Code loads itself, including claude.ai connectors it fetches. Connectors that Claude Desktop delivers to its local and SSH sessions are not covered; control them in the claude.ai organization settings (Connectors).

Key reference: [settings-reference](https://code.claude.com/docs/en/settings-reference), [settings](https://code.claude.com/docs/en/settings).

## Check the file before you deploy

From the repo root, run `python3 starter-kit/settings/preflight.py <file>` on the exact file you are about to deploy (several files may follow). It exits 0 and prints `OK` when no `REPLACE-WITH-` value is left. A failure means do not deploy: exit 1 prints the file, the JSON path and the value of each placeholder still in it, and exit 2 means the file is missing, unreadable or not valid JSON. Fix the file and run it again.

## How IT deploys

Delivery options: [managed-settings](https://code.claude.com/docs/en/managed-settings).

Which path enforces what: device-management files enforce every key in these baselines, and the OS can protect the file from user changes. The server-managed path (the paste in claude.ai) is a client-side control that a user on an unmanaged device can bypass ([server-managed-settings](https://code.claude.com/docs/en/server-managed-settings#security-considerations)). The sign-in lock (`forceLoginOrgUUID`) needs device management, because a user receives server-managed settings only after signing in to your organisation ([authentication](https://code.claude.com/docs/en/authentication#restrict-login-to-your-organization)). On a machine that receives both, Claude Code by default uses the first source that delivers a policy key, server-managed settings first, and skips the other source's policy keys without a warning; setting `managedSourcesBehavior` to `"merge"` in the highest-ranked source applies every source (v2.1.242 or later) ([how Claude Code combines managed sources](https://code.claude.com/docs/en/managed-settings#how-claude-code-combines-managed-sources); [plugins/org](https://code.claude.com/docs/en/plugins/org#which-managed-source-applies-on-a-machine)). `/status` names the source it used and the ones it skipped.

- macOS file: `/Library/Application Support/ClaudeCode/managed-settings.json`; or a configuration profile in the `com.anthropic.claudecode` domain (Jamf, Kandji).
- Windows file: `C:\Program Files\ClaudeCode\managed-settings.json`; or registry value `Settings` (the JSON as a string) under `HKLM\SOFTWARE\Policies\ClaudeCode` (Intune, Group Policy).
- Linux and WSL: `/etc/claude-code/managed-settings.json`.
- Alternative: paste the JSON in claude.ai under Organization settings > Claude Code > Managed settings (Team and Enterprise; [server-managed-settings](https://code.claude.com/docs/en/server-managed-settings)).

Copy the file for the data class to the path, saved as `managed-settings.json`. Check with `/status`.

## Warnings

- Server-managed settings "operate as a client-side control, not a security boundary". On unmanaged devices a user can bypass them (compendium 13). Use MDM files on managed devices; keep sensitive classes off unmanaged ones.
- These settings do not replace ZDR, the HIPAA configuration or org-level controls on claude.ai (retention, SSO, connectors, Compliance API). They cover Claude Code on the device only.
- Claude Desktop needs its own policy for sign-in lock (`forceLoginOrgUUID` in the Desktop MDM policy).

## Governance hook

The hook reaches a device through the `twin-governance@digital-twin-kit` entry in `enabledPlugins` in the confidential, pe-zdr and hipaa baselines; see the [twin-governance README](../plugins/twin-governance/README.md) for what it logs. With `allowManagedHooksOnly` on, hooks from plugins that managed settings force-enable through `enabledPlugins` still run ([settings-reference](https://code.claude.com/docs/en/settings-reference#what-runs-under-allowmanagedhooksonly), [hooks](https://code.claude.com/docs/en/hooks)). Check it once on a managed device: `/plugin` lists it, and a log line appears after a tool call.

Pilot-device check, on every pilot device before the pilot starts there: run `python3 --version`, make one tool call in Claude Code, and confirm a new line appears in the log file (`~/.claude/twin-governance/log.jsonl` unless `TWIN_GOVERNANCE_LOG` is set). The hook command is `python3 "${CLAUDE_PLUGIN_ROOT}"/hooks/governance_log.py`. If `python3` is not found, the hook does not run, so nothing is logged, and the pilot does not start on that device until IT fixes the PATH. **⚠ Unverified:** what Claude Code shows the user when the hook command is missing.

Not set here, because they vary per role and per customer: `TWIN_GOVERNANCE_TWIN_ID` and `TWIN_GOVERNANCE_LOG`. Set them in the managed settings `env` block of that group's own file (see the identity runbook, step 6.3), or in the device environment.
