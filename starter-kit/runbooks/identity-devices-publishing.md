# Runbook: SCIM groups, managed-settings rollout, and publishing digital-twin-kit

## What this is

Three things have to be true before a pilot starts:

1. The pilot users are in the right groups, so Claude gives them the right role and seat.
2. Managed devices carry the settings baseline for their data class.
3. The kit's marketplace and plugins reach the groups that should use them.

This runbook takes the Director of IT through all three. It is generic: replace every `<placeholder>` with the customer's value. Where a step depends on a product's own console, and Anthropic's docs do not confirm it, the step is marked **unverified**.

Roles use the names in [03-stakeholders](../../docs/playbook/03-stakeholders.md):

| Name used here | Role in 03-stakeholders |
|---|---|
| **Director of IT** | Technical owner. Claude org Owner, SSO and SCIM, devices and MDM, managed settings |
| **Backup Owner** | IT administrator. Second Owner, and runs the same steps if the Director of IT is out |
| **Source-system admins** | Source-system admins. Help with the identity provider app when a separate admin runs it; the playbook puts SSO and SCIM under the Director of IT |
| **Security** | CISO or security engineer. Reviews the device policy and the marketplace before rollout |
| **Skill owners** | Subject-matter experts. Own each plugin's content, and say which role plugin fits which role |
| **Partner integration engineer** | Integration engineer (partner role). Builds and tests the marketplace and the settings files |
| **RevOps manager** | Business owner. Names the pilot users and approves who is in the pilot group |

Sources are marked [S1] to [S6] and listed at the end. Repo files are cited by path.

## Before you start

| # | Step | Who | Source |
|---|---|---|---|
| 0.1 | Confirm the Claude org is Enterprise or Console. SCIM is not available on Team plans, which use JIT provisioning instead. | Director of IT | [S1] |
| 0.2 | Confirm SSO is set up first, including domain verification. SCIM assumes SSO is complete. | Director of IT | [S1] |
| 0.3 | Pick the managed-settings baseline for each data class. Do not choose it from this runbook. | Director of IT, with Compliance | [starter-kit/settings/README.md](../settings/README.md) |
| 0.4 | Replace the placeholders in the chosen baseline files before any device gets them: `REPLACE-WITH-ORG-UUID` (copy it from the claude.ai admin settings; a wrong value makes Claude Code exit at startup), `REPLACE-WITH-GITHUB-ORG` (the repo that holds this kit's marketplace; it appears twice in each file, under `strictKnownMarketplaces` and `extraKnownMarketplaces`), `REPLACE-WITH-GOVERNANCE-SALT` (confidential, pe-zdr and hipaa: a secret per customer), and in the pe-zdr file the two MCP host placeholders. The README lists every key and placeholder. | Partner integration engineer | [starter-kit/settings/README.md](../settings/README.md) |
| 0.5 | Make sure at least one Owner is in a group that is mapped to the Owner role (step 3.4). Otherwise the next sync can remove the Owner. Make a Backup Owner, so one person cannot lock everyone out. | Director of IT, Backup Owner | [S1]; [03-stakeholders](../../docs/playbook/03-stakeholders.md) |

## 1. Create the SCIM groups in the identity provider

**Worked example: Okta.** The same logic applies to other providers, but the clicks below are for Okta only.

**Who: Director of IT, with Source-system admins if they run the identity provider.**

Groups in the identity provider decide two things in Claude: the role each user gets, and the seat tier. Groups appear in Claude only after the first sync (step 3), so create them first.

| # | Step | Who | Source |
|---|---|---|---|
| 1.1 | In the Okta Admin console, go to **Applications > Applications** and select **Create App Integration**. Name the app `Claude`. Choose **SAML 2.0**; Anthropic recommends SAML over OIDC. | Director of IT (with Source-system admins if they run Okta) | [S3] |
| 1.2 | Configure SAML as the SSO guide describes. The name ID format is EmailAddress, and an email attribute maps to `user.email`. The guide's exact ACS URL and Entity ID come from the Claude side during SSO setup. | Director of IT (with Source-system admins) | [S3]; values **unverified** here |
| 1.3 | Add a **groups** Group Attribute Statement to the SAML configuration. The docs say it is needed for group mappings to work with JIT or SCIM. The attribute name the guide uses is not confirmed here. | Director of IT (with Source-system admins) | [S3]; attribute name **unverified** |
| 1.4 | On the **Provisioning** tab, select **Configure API Integration**. Enable **Create Users**, **Update User Attributes**, and **Deactivate Users**. Paste the SCIM base URL and token from the WorkOS setup guide that Claude's SCIM setup links to. | Director of IT (with Source-system admins) | [S3]; WorkOS values **unverified** (guide not read) |
| 1.5 | Make sure the SAML email field and the SCIM email field are the same Okta attribute. A mismatch, for example `user.login` for SCIM and `user.email` for SAML, can block logins. | Director of IT (with Source-system admins) | [S3] |
| 1.6 | Create one Okta group per role, plus one per seat type where the plan has seat tiers. Use a prefix such as `anthropic-claude-` for easy search. The docs recommend a prefix but do not require one. | Director of IT | [S1] |
| 1.7 | Create the pilot group as a separate Okta group, for example `anthropic-claude-pilot-<role>`. Add the pilot users, chosen by the RevOps manager. **Choice: see the Choices list. The docs do not describe pilot groups.** Each pilot user still needs a role group. A pilot group alone does not give a role. | Director of IT, RevOps manager | [S1]; pilot design is **unverified** |
| 1.8 | Assign the Okta groups to the Claude app on the **Assignments** tab. Users not assigned to the app when the provisioning mode is saved are removed from the organization. Check the assignment list before step 2.5. | Source-system admins | [S3]; [S1] step 2 |

## 2. Connect SCIM in Claude

**Who: Director of IT** (Owner in Claude). Only an Admin or Owner can do this.

| # | Step | Who | Source |
|---|---|---|---|
| 2.1 | In Claude, open the **User provisioning** section and click **Setup SCIM** (or **Manage SCIM**) next to SCIM directory sync. Follow the WorkOS guide and copy its values into the Okta app from step 1.4. | Director of IT | [S1] |
| 2.2 | Choose the provisioning mode: **Invite only**, **Just-in-time (JIT)**, or **SCIM directory sync**. For groups to drive roles, use SCIM directory sync. | Director of IT | [S1]; [S2] |
| 2.3 | Before saving, confirm every user who should keep access is assigned to the Claude app in Okta (step 1.8). Review the change preview, including the removal count, if it is shown. | Director of IT | [S1] |
| 2.4 | Click **Save changes** to trigger the first provisioning. | Director of IT | [S1] |
| 2.5 | Wait for the first sync to finish. Groups appear in Claude only after this sync. | Director of IT | [S1] |

## 3. Map groups to roles and seats

**Who: Director of IT.**

| # | Step | Who | Source |
|---|---|---|---|
| 3.1 | Turn on **Enable group mappings**. | Director of IT | [S1] |
| 3.2 | Click **Add** next to each role and select the matching Okta group. Every user needs a role-based group, or they are removed from the organization. | Director of IT | [S1]; [S2] |
| 3.3 | Optional: assign seat tiers under **Assign seat tiers to IdP groups**. Existing users keep their seat type. New users get the highest seat type with an unassigned seat. | Director of IT | [S1] |
| 3.4 | Make sure at least one Owner or Admin is in a mapped group. Owner and Admin accounts are not exempt from reconciliation. The Primary Owner is exempt, but the role cannot be set through group mappings. Set the Primary Owner under **Organization settings > Members** before enabling SCIM. | Director of IT | [S1] |
| 3.5 | Click **Save changes**. Changing a mapping does not update existing members on its own. After you change a mapping, run **Sync now** under **Directory sync (SCIM)**. | Director of IT | [S1]; [S2] |
| 3.6 | Custom roles (Enterprise only): save first with group mappings off, let the sync finish, attach the synced groups to custom roles under **Organization settings > Roles**, then turn group mappings back on. Users in a custom-mapped group have no permissions until their group is attached to a role. | Director of IT | [S1] |

Removal behavior: [S1] says users are removed automatically when their group access is revoked. [S2] does not describe removal from a group in detail, so confirm it on a test user. Sync is eventually consistent. It usually finishes within minutes, but it can take several hours [S2]. Expect a delay before a test user sees a change.

## 4. Deploy the managed-settings baseline to devices

**Who: Director of IT** (accountable). **Backup Owner** runs the deployment. **Partner integration engineer** confirms the file is the right baseline.

Deploy one complete file per data class. Each file is a full policy, not a diff. Do not merge two files by hand.

Where each file goes, from [S5]:

| OS | File path | MDM or OS delivery |
|---|---|---|
| macOS | `/Library/Application Support/ClaudeCode/managed-settings.json` | A configuration profile in the `com.anthropic.claudecode` managed preferences domain. Top-level keys match the JSON keys. Nested settings are dictionaries, and lists are plist arrays. |
| Windows | `C:\Program Files\ClaudeCode\managed-settings.json` | Registry value `Settings` (REG_SZ or REG_EXPAND_SZ), the whole JSON as a string, under `HKLM\SOFTWARE\Policies\ClaudeCode`. |
| Linux and WSL | `/etc/claude-code/managed-settings.json` | File only. |

Do not use the legacy path `C:\ProgramData\ClaudeCode\managed-settings.json`. Claude Code no longer reads it [S5].

Claude Code reads the first managed source that delivers a policy key, in this order: server-managed settings, then the MDM plist or HKLM value, then the managed settings file [S4]. Deliver the baseline through one source per device. Do not mix a file and an MDM profile on the same machine unless you have set `managedSourcesBehavior` on purpose.

### Intune (Windows)

Deploy the JSON file to `C:\Program Files\ClaudeCode\managed-settings.json`, or write the `Settings` registry value under `HKLM\SOFTWARE\Policies\ClaudeCode`, from a device configuration profile or a script that Intune assigns to the device group. The exact Intune blade names and the OMA-URI or script setup are **unverified** here. Anthropic's docs point to a starter template for Intune in the MDM examples repository [S5], which we did not open. Use that template, and confirm it against Intune's own current docs.

Intune delivers to devices, not to users. For how to split devices into plugin sets, see step 6.

### Jamf (macOS)

Build a configuration profile that sets the keys in the `com.anthropic.claudecode` domain, or deploy the file to `/Library/Application Support/ClaudeCode/managed-settings.json` with a policy script. The Jamf UI steps are **unverified** here. The MDM examples repository has a Jamf template [S5]; confirm it against Jamf's current docs.

### Kandji (macOS)

Anthropic's docs name Jamf, Iru and Intune as the MDM examples [S5]. They do not name Kandji. The repo's settings README mentions Kandji as a macOS profile tool [starter-kit/settings/README.md](../settings/README.md). The product name, and whether the Kandji and Iru profile steps are the same, are **unverified**. Use the same profile content as Jamf: a configuration profile in the `com.anthropic.claudecode` domain, with the file path as the fallback.

### Check the file before you deploy

- Each file must be valid JSON. A malformed file or plist makes Claude Code refuse to start, and the error names the source [S5].
- The placeholders from step 0.4 must be replaced. A wrong org UUID also makes Claude Code exit at startup [starter-kit/settings/README.md](../settings/README.md).
- A missing or unreadable file is not a failure. Claude Code runs without that source. So a pilot can appear to work while the baseline is missing. Verify step 5 on every pilot device.

## 5. Verify on a device that the settings took effect

**Who: Backup Owner** on one pilot device first, then a sample of the pilot group. The **Director of IT** reads the result.

| # | Check | Expected | Source |
|---|---|---|---|
| 5.1 | Start Claude Code on the device, run `/status`, and read the **Setting sources** line. | The line lists `Enterprise managed settings`, with the source in parentheses: `(plist)` or `(HKLM)` for MDM, `(file)` for the file path. | [S5] |
| 5.2 | Run `claude doctor` and read the **Organization policy** line. | It names where the policy loaded from. If it did not load, it says why. Needs Claude Code v2.1.261 or later. | [S5] |
| 5.3 | Check one key from the baseline. For example, in the pe-zdr file, check that WebFetch and WebSearch are denied. Run a read that the policy blocks. | The read is refused. | [starter-kit/settings/README.md](../settings/README.md); the key-level behavior is from the README and **not re-tested here** |
| 5.4 | Run `/plugin` on the device. | The marketplace `digital-twin-kit` and the plugins for the device's group are listed (step 6). | [S4] |
| 5.5 | If a device shows no policy, check that the file or profile is at the path in step 4, and that the source is not blocked by a higher-ranked source. Read `/status` again. | The `Setting sources` line names the source Claude Code used. | [S5] |

Do not roll out to the fleet until 5.1 and 5.4 pass on the pilot devices.

## 6. Publish the marketplace and its plugins to the right groups

**Who: Director of IT** (accountable). **Partner integration engineer** builds the marketplace and the plugin sets. **Security** reviews the marketplace before rollout.

### What the kit ships

- The marketplace is `digital-twin-kit`, defined in `.claude-plugin/marketplace.json` at the repo root [repo file].
- It lists three plugins: `twin-shared`, the role plugin for each role (in this kit, `twin-pe-deal-team`), and `twin-governance` [repo file].
- Every settings baseline in `starter-kit/settings/` has a `strictKnownMarketplaces` allowlist that admits only the kit's repo, and an `extraKnownMarketplaces` entry that registers it [repo files]. The repo field is the placeholder `REPLACE-WITH-GITHUB-ORG/digital-twin-kit` until step 0.4 is done.
- Every baseline also has `enabledPlugins` with `twin-shared@digital-twin-kit` set to `true`, and the confidential, pe-zdr and hipaa baselines also enable `twin-governance@digital-twin-kit` [repo files]. **No baseline enables a role plugin**, so the role plugin is an extra step per group (step 6.3).

### How to publish to groups

The managed settings do not target users. Anthropic's docs say every plugin key applies to every user who receives the settings. There is no per-user or per-group key [S4]. So "publish to a group" means one of two things:

- **Device groups.** Assign each plugin set's managed settings to a device group in Intune or Jamf. A device in the group gets its plugin set. Use this path for MDM-managed devices.
- **Server-managed settings.** On an Enterprise plan, give each group its own configuration in the claude.ai admin console, under **Organization settings > Claude Code > Managed settings**. Requires the Owner role [S4]. This path covers devices that are not under MDM, and cloud sessions, which only read server-managed settings [S4].

SCIM groups (step 1) decide the role and seat in Claude. They do not decide which plugins a device gets. Keep the two sets of groups separate, and name them so they are not confused.

### Steps

| # | Step | Who | Source |
|---|---|---|---|
| 6.1 | Confirm the placeholder repo in both marketplace keys (`strictKnownMarketplaces` and `extraKnownMarketplaces`) is replaced with the customer's repo that holds the kit (step 0.4). Confirm the kit's repo is readable by every user who will install from it. A private repo needs each user to have read access. Users without a git-host account need a seed instead. | Partner integration engineer | [S4]; [repo files] |
| 6.2 | Decide the plugin set for each group. Suggested: `twin-shared` for every role, the role plugin for its role group, and `twin-governance` for devices in the confidential, pe-zdr and hipaa baselines. | Director of IT, Skill owners, RevOps manager | [starter-kit/README.md](../../starter-kit/README.md); the mapping itself is a **choice** (see Choices) |
| 6.3 | For each group, start from the baseline for its data class (it already enables `twin-shared`, and `twin-governance` for three classes) and add the group's role plugin to `enabledPlugins`: `"<role-plugin>@digital-twin-kit": true`, for example `twin-pe-deal-team`. In the same file set `TWIN_GOVERNANCE_TWIN_ID` (and `TWIN_GOVERNANCE_LOG` if the log path is not the default) in `env`. Do not edit the other keys. Example shape from [S4]: `"enabledPlugins": {"twin-pe-deal-team@digital-twin-kit": true}`. | Partner integration engineer | [S4]; [starter-kit/settings/README.md](../settings/README.md) |
| 6.4 | Deploy each plugin set's settings to its device group (or give the group its own server-managed configuration), as described above. | Director of IT | [S4]; [S5] |
| 6.5 | Keep `twin-governance` as a managed plugin, not a user install: the confidential, pe-zdr and hipaa baselines enable it in `enabledPlugins`, and those baselines also set `allowManagedHooksOnly`, under which only hooks from plugins that managed settings force-enable still run [S6]. Confirm the hook runs on one pilot device before rollout. | Partner integration engineer | [starter-kit/plugins/twin-governance/README.md](../../starter-kit/plugins/twin-governance/README.md); the hook is shipped in [hooks/](../../starter-kit/plugins/twin-governance/hooks/) (`governance_log.py`, `hooks.json`) |
| 6.6 | Confirm the rollout on one pilot device. Start Claude Code, run `/plugin`, and check that the marketplace and the plugins for that device's group are listed. For CI, run `claude -p` with `--output-format stream-json --verbose` and read the `plugins` list in the `init` event. | Backup Owner | [S4] |
| 6.7 | Do not allow other marketplaces. The allowlist in each baseline already does this. Check that a source outside the allowlist fails with `blocked by enterprise policy`. Add `disableSideloadFlags` if users must not load plugins from a local folder or URL. | Security | [S4] |
| 6.8 | Set the claude.ai plugin toggles separately under **Organization settings > Plugins & skills**. They do not set the Claude Code keys above, and they reach Claude Code as synced plugins [S4]. | Director of IT | [S4] |

### What the governance hook does

`twin-governance` ships a working `PostToolUse` and `PostToolUseFailure` hook. It writes one metadata-only line per tool call and never blocks a call. It records; it does not enforce. Tell the Compliance role that it is a log. Walls rest on the Salesforce, HubSpot and SharePoint permissions, not on this hook. The fields, the redaction rules and the record-id allowlist are in the [twin-governance README](../../starter-kit/plugins/twin-governance/README.md).

## Sources

- [S1] Setting up JIT or SCIM provisioning. https://support.claude.com/en/articles/13133195-setting-up-jit-or-scim-provisioning
- [S2] How SCIM sync works for Enterprise organizations. https://support.claude.com/en/articles/14499648-how-scim-sync-works-for-enterprise-organizations
- [S3] SSO setup: Okta. https://support.claude.com/en/articles/13917894-sso-setup-okta
- [S4] Manage Claude Code plugins for your organization. https://code.claude.com/docs/en/plugins/org
- [S5] Deploy managed settings. https://code.claude.com/docs/en/managed-settings (its MDM examples repository is linked from this page: https://github.com/anthropics/claude-code/tree/main/examples/mdm, not opened)
- [S6] Settings reference, what runs under `allowManagedHooksOnly`. https://code.claude.com/docs/en/settings-reference#what-runs-under-allowmanagedhooksonly
