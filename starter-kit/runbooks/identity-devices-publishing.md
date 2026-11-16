# Runbook: SCIM groups, managed-settings rollout, and publishing digital-twin-kit

## What this is

Three things have to be true before a pilot starts:

1. The pilot users are in the right groups, so Claude gives them the right role and seat.
2. Managed devices carry the settings baseline for their data class.
3. The kit's marketplace and plugins reach the groups that should use them.

This runbook takes the Director of IT through all three. It is generic: replace every `<placeholder>` with the customer's value. Where a step depends on a product's own console, and that vendor's docs do not confirm it, the step is marked **⚠ Unverified:** (the compendium's marker) and says what to confirm at setup. Every claim was checked against the vendor's pages on 2026-11-15; the results are in the [verification log](verification-log.md).

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

Sources are marked [S1] to [S19] and listed at the end. Repo files are cited by path.

## Before you start

| # | Step | Who | Source |
|---|---|---|---|
| 0.1 | Find out which plan the Claude org is on, then pick a path. **Enterprise** (or a Console organization) with SCIM: follow steps 1 to 6. **Team**: follow [Team plan: no SCIM, no group targeting](#team-plan-no-scim-no-group-targeting), which points back to steps 4 to 6 where they apply. SCIM is not available on Team plans, which use JIT provisioning instead, or on Console organizations joined to a Team plan's parent organization. | Director of IT | [S1]; [S3] |
| 0.2 | Confirm SSO is set up first, including domain verification. SCIM assumes SSO is complete. (On Team, SSO is optional: see step T2.) | Director of IT | [S1] |
| 0.3 | Pick the managed-settings baseline for each data class. Do not choose it from this runbook. | Director of IT, with Compliance | [starter-kit/settings/README.md](../settings/README.md) |
| 0.4 | Replace the placeholders in the chosen baseline files before any device gets them: `REPLACE-WITH-ORG-UUID` (copy it from the claude.ai admin settings; a wrong value makes Claude Code exit at startup [S11]), `REPLACE-WITH-GITHUB-ORG` (the repo that holds this kit's marketplace; it appears twice in each file, under `strictKnownMarketplaces` and `extraKnownMarketplaces`), `REPLACE-WITH-GOVERNANCE-SALT` (confidential, pe-zdr and hipaa: a secret per customer), and in the pe-zdr file the two MCP host placeholders. The value for each is in the connector runbooks: Salesforce, [the line that says to paste `api.salesforce.com`](salesforce-hosted-mcp.md#L87); Microsoft 365, [the line that says which host to paste and that it is still **⚠ Unverified:**](microsoft-365-connector.md#L80) (until it is confirmed, the pe-zdr allowlist matches no Microsoft 365 server). The README lists every key and placeholder. | Partner integration engineer | [starter-kit/settings/README.md](../settings/README.md) |
| 0.5 | Make sure at least one Owner is in a group that is mapped to the Owner role (step 3.4). Otherwise the next sync can remove the Owner. Make a Backup Owner, so one person cannot lock everyone out. (On Team there is no group mapping: make the Backup Owner by hand, step T4.) | Director of IT, Backup Owner | [S1]; [03-stakeholders](../../docs/playbook/03-stakeholders.md) |

## Team plan: no SCIM, no group targeting

Use this section when step 0.1 finds a **Team** plan. Team has no SCIM and no per-group configuration, so steps 1 to 3 do not apply and step 6 shrinks to one organisation-wide rollout. What a Team customer gets is a working deployment with honest limits. The facts behind it are in compendium [09](../../docs/compendium/09-plans-and-it-controls.md), [12](../../docs/compendium/12-orgs-and-ownership.md#team-plan-variant-a-non-regulated-role-our-recommendation) and [13](../../docs/compendium/13-devices.md#team-plan-with-no-device-management).

**Who: Director of IT** (Owner in Claude), with the roles in the table at the top.

### Getting people in and setting roles

| # | Step | Who | Source |
|---|---|---|---|
| T1 | Choose how people join. **Invite only** is the default: an Owner or Admin adds and removes members directly in Claude, and members sign in with the claude.ai account the admin invited. **Just-in-time (JIT)** provisions a user the first time they sign in through the identity provider app. JIT is listed for Team plans in the article's introduction, but the same article says the JIT mode is available to all plans: confirm with Anthropic before relying on either. | Director of IT | [S1]; [S19] |
| T2 | SSO is optional on Team. If the console offers it, set it up: **Organization settings > Organization and access**, **Authentication** section, **Setup SSO**. For Okta, follow steps 1.1, 1.2 and 1.5 (SAML only) and assign the people who should have access on the app's **Assignments** tab (step 1.8, first sentence). Skip 1.3, 1.4 and 1.6 to 1.8: they are SCIM and group steps. **⚠ Conflict:** [S15] and [S19] say SSO is available for Team plans; [S16] lists "Manage SSO / auth" under Enterprise-only security controls (compendium 09 records the same conflict). If **Setup SSO** is not shown, use invites (T1) and raise it with the Anthropic account team. | Director of IT (with Source-system admins) | [S15]; [S3]; [S16] |
| T3 | Set the provisioning mode under **Organization settings > Organization and access > User provisioning**: **Invite only** or **Just-in-time (JIT)**. Do not choose SCIM directory sync: it is not available on Team. A JIT user is provisioned at login with the **User** role. | Director of IT | [S1]; [S3] |
| T4 | Set roles by hand in the admin console, because there is no group mapping on Team. The roles are User, Admin, Owner and Primary Owner [S16]. Give the Owner role to the Director of IT and to a Backup Owner (step 0.5), and to nobody else: only Owners can edit managed settings [S17], and the Admin role cannot manage Plugins & skills ([compendium 09](../../docs/compendium/09-plans-and-it-controls.md)). Change a role under **Organization settings > Members**. **⚠ Unverified:** [S16] does not describe how a role is changed, so confirm the menu path at setup. | Director of IT, Backup Owner | [S16]; [S17]; **⚠ Unverified:** menu path |

### Managed settings: one configuration for the whole organisation

| # | Step | Who | Source |
|---|---|---|---|
| T5 | Pick the one baseline for the whole organisation, because Team gets one configuration and every member receives it. Use `general` for internal data. Use `confidential` only if every member may handle confidential data. `pe-zdr` and `hipaa` are Enterprise only (ZDR and HIPAA need Enterprise), so a Team customer with those roles needs Enterprise, not this section. Replace the placeholders (step 0.4) and run `python3 starter-kit/settings/preflight.py <file>` on the file ([settings README](../settings/README.md)). | Director of IT, with Compliance; Partner integration engineer | [compendium 09](../../docs/compendium/09-plans-and-it-controls.md); [starter-kit/settings/README.md](../settings/README.md) |
| T6 | Paste the file as JSON in claude.ai under **Organization settings > Claude Code > Managed settings**. It needs the Owner or Primary Owner role, and server-managed settings are available on Team and Enterprise. Members' Claude Code clients fetch it when they sign in to the organization. | Director of IT (Owner) | [S17] |
| T7 | Tell the business owner what this is: a **client-side control, not a security boundary**. On a device the organisation does not manage, a user needs no admin rights to bypass it, for example by signing in to a personal or other organisation, using a Console API key or a third-party provider or a non-default `ANTHROPIC_BASE_URL`, running an older version, or running a modified binary. Keep confidential data off unmanaged devices (compendium 13). | Director of IT | [S17]; [compendium 13](../../docs/compendium/13-devices.md) |
| T8 | The sign-in lock (`forceLoginOrgUUID`) is enforced only by a device-management file. Anthropic says to deploy it with device management tooling, because a user receives server-managed settings only after signing in to your organisation, so those settings cannot redirect a first sign-in. Pasting the key in the console does not give a lock on its own. Without device management there is no sign-in lock. | Director of IT | [S11] |
| T9 | If the customer does have device management (Intune, Jamf, Kandji) on some or all devices, use step 4 on those devices unchanged. Do not also paste a configuration for them unless you have read the [settings README](../settings/README.md) paragraph on two sources: by default Claude Code uses the first managed source that delivers a policy key, server-managed settings first, and skips the device file's policy keys. | Director of IT, Backup Owner | [S18]; [starter-kit/settings/README.md](../settings/README.md) |

### Plugins: one set for every member

| # | Step | Who | Source |
|---|---|---|---|
| T10 | Know that Team has no per-group configuration: the one configuration, with its `extraKnownMarketplaces` and `enabledPlugins`, reaches every member, and every plugin key applies to every user who receives the settings. Add the role plugin to the `enabledPlugins` of the file from T5 (step 6.3), and set `TWIN_GOVERNANCE_TWIN_ID` there. The `general` baseline enables only `twin-shared@digital-twin-kit`, not `twin-governance`; `confidential` enables both. A governance hook that arrives this way is the client-side control in T7: a user can bypass it, it does not run in claude.ai on the web, and it is not a log to rely on (see the closing paragraph). | Partner integration engineer | [S17]; [S4] |
| T11 | **(Our recommendation)** Because there is no group target: ship one role plugin, for the pilot role, and write each skill's description so it says which role it is for, so a member outside the role is not offered it by mistake. Where there is device management, split plugin sets with device groups (step 6, device groups). Do not add a second role plugin to the one file until the customer is on Enterprise or has device groups. | Director of IT, Skill owners | Our recommendation; [S4] for the device-group path |
| T12 | Set the claude.ai plugin toggles under **Organization settings > Plugins & skills** (step 6.8). On Team an Owner shares an org plugin to everyone; there is no group target there either. | Director of IT | [S4]; [compendium 13](../../docs/compendium/13-devices.md#team-plan-with-no-device-management) |

### Which steps apply on Team

| Runbook step | Applies on Team? | What to do instead | Source |
|---|---|---|---|
| 1 | No | Create no SCIM groups. SCIM is not available on Team; use T1 to T3. | [S1]; [S3] |
| 2 | No | Do not connect SCIM. Set the provisioning mode in T3. | [S1] |
| 3 | No | No group mapping, no seat-tier mapping and no custom roles: set roles by hand (T4). | [S1]; [compendium 09](../../docs/compendium/09-plans-and-it-controls.md) |
| 4 | Only with device management | Deploy the file to devices under Intune, Jamf or Kandji. Without device management, paste the file in claude.ai (T6) and accept the limits in T7 and T8. | [S5]; [S17] |
| 5 | Wherever settings were delivered | Run it on each pilot device. For settings delivered by server-managed settings, the **Setting sources** line shows `(remote)`. | [S5] |
| 6 | Organisation-wide only | Steps 6.1, 6.3 to 6.8 apply with one role plugin in the one file (T10). No per-group configuration and no per-group device targeting unless there are device groups. | [S4]; [S17] |

### What a Team twin does not get

A Team twin does not get group targeting, SCIM, audit logs, the Compliance API, custom retention, ZDR or HIPAA ([compendium 13](../../docs/compendium/13-devices.md#team-plan-with-no-device-management) and [15](../../docs/compendium/15-governance-and-performance.md#team-plan-with-no-device-management) list what it does get and what it cannot record). Without device management there is no device settings file and no sign-in lock. The governance hook can reach Claude Code through the server-managed configuration (T10), but only as the client-side control T7 describes, which a user can bypass, and it does not run at all in claude.ai on the web, which is where compendium 13 puts a Team twin with no device management. So it is not a log the customer can rely on. [S17] lists hooks among the settings it supports ("This includes hooks") and says that "Because hooks execute shell commands, users in interactive sessions see a security approval dialog before Claude Code applies them"; it does not say whether the hooks of a plugin that a server-managed `enabledPlugins` entry enables run, or whether that triggers the dialog. **⚠ Unverified:** whether the governance plugin's hook runs on a Team device that gets the plugin only from a server-managed configuration; test it on one pilot device (step 6.5). A customer who needs every action logged needs Enterprise and managed devices: the managed hook on each device, and the Enterprise audit log and Compliance API beside it, neither of which is a log of each tool call.

## 1. Create the SCIM groups in the identity provider

**Worked example: Okta.** The same logic applies to other providers, but the clicks below are for Okta only.

**Who: Director of IT, with Source-system admins if they run the identity provider.**

Groups in the identity provider decide two things in Claude: the role each user gets, and the seat tier. Groups appear in Claude only after the first sync (step 3), so create them first.

| # | Step | Who | Source |
|---|---|---|---|
| 1.1 | In the Okta Admin Console, go to **Applications and Resources > Applications**, select **Create App Integration**, then **Classic experience**, and choose **SAML 2.0** as the sign-in method. Anthropic recommends SAML over OIDC. Name the app `Claude`. Anthropic's guide shows the older menu name **Applications > Applications**. | Director of IT (with Source-system admins if they run Okta) | [S7]; [S3] |
| 1.2 | Configure SAML as the SSO guide describes. Set the Name ID format to EmailAddress and Application username to Email, and add an attribute statement named `email` with the value `user.email`. The ACS URL and Audience URI (Entity ID) are per organization: copy them from the WorkOS setup flow in the Claude **Identity and access** settings (`claude.ai/admin-settings/identity`; [S3] gives this URL for Team and Enterprise). **⚠ Conflict:** [S1] and [S15] name `claude.ai/admin-settings/organization` (**Organization and access**) for the same settings. Use whichever your console shows. | Director of IT (with Source-system admins) | [S3]; [S15] |
| 1.3 | Add a group attribute statement named `groups`, with a filter that covers every Okta group mapped to a Claude role or seat type. Without it, users cannot receive mapped roles. In Okta it is on the **Sign On** tab, under **Attribute Statements** > **Show legacy configuration**; Okta's newer alternative is custom claims. | Director of IT (with Source-system admins) | [S3]; [S9] |
| 1.4 | Turn on SCIM for the app. For an app built with **Create App Integration**, Okta's steps are: on the **General** tab, edit **App Settings** and set **Provisioning** to **SCIM**; then on the **Provisioning** tab, under **Settings > Integration**, click **Edit** and enter the SCIM connector base URL and the API token (HTTP Header) from the WorkOS setup flow. Anthropic's guide calls this step **Configure API Integration** > **Enable API integration**, Okta's label for catalog apps. Then under **To App**, click **Edit** and enable **Create Users**, **Update User Attributes**, and **Deactivate Users**. | Director of IT (with Source-system admins) | [S8]; [S10]; [S3] |
| 1.5 | Make sure the SAML email field and the SCIM email field are the same Okta attribute. A mismatch, for example `user.login` for SCIM and `user.email` for SAML, can block logins. | Director of IT (with Source-system admins) | [S3] |
| 1.6 | Create one Okta group per role, plus one per seat type where the plan has seat tiers. Use a prefix such as `anthropic-claude-` for easy search. The docs recommend a prefix but do not require one. | Director of IT | [S1] |
| 1.7 | Create the pilot group as a separate Okta group, for example `anthropic-claude-pilot-<role>`. Add the pilot users, chosen by the RevOps manager. **(Our recommendation): the docs do not describe pilot groups.** Each pilot user still needs a role group. A pilot group alone does not give a role. | Director of IT, RevOps manager | [S1]; **⚠ Unverified:** confirm the pilot design at setup |
| 1.8 | Assign the Okta groups to the Claude app on the **Assignments** tab ([S3] step 4: "In the **Assignments** tab, assign the people or Okta groups that should access Claude"). Users not assigned to the app when the provisioning mode is saved are removed from the organization. Check the assignment list before step 2.4, which saves it. | Source-system admins | [S3]; [S1] step 2 |

## 2. Connect SCIM in Claude

**Who: Director of IT** (Owner in Claude). The docs require the Owner role in a Claude organization, or Admin in a Console organization.

| # | Step | Who | Source |
|---|---|---|---|
| 2.1 | In Claude, open **Organization settings > Organization and access**, go to the **User provisioning** section and click **Setup SCIM** (or **Manage SCIM**) next to SCIM directory sync. Follow the WorkOS guide and copy its values into the Okta app from step 1.4. | Director of IT | [S1] |
| 2.2 | Choose the provisioning mode: **Invite only**, **Just-in-time (JIT)**, or **SCIM directory sync**. For groups to drive roles, use SCIM directory sync. | Director of IT | [S1]; [S2] |
| 2.3 | Before saving, confirm every user who should keep access is assigned to the Claude app in Okta (step 1.8). Review the change preview, including the removal count, if it is shown, and cancel if more users would be removed than you expect. | Director of IT | [S1] |
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
| 3.5 | Click **Save changes**. After you change a seat-tier or role mapping, existing members are not resynced on their own [S2]. Run a manual sync. ⚠ Conflict: [S1] names a **Sync** button under **User provisioning** and a **Sync now** button next to **Directory sync (SCIM)** on the Organization and access page; [S2] names **Sync** under **User provisioning** and **Check for updates** under **SCIM sync** in **Organization settings > Groups**. Use whichever your console shows. | Director of IT | [S1]; [S2] |
| 3.6 | Custom roles (Enterprise only): save first with group mappings off, let the sync finish, attach the synced groups to custom roles under **Organization settings > Roles**, then turn group mappings back on. If the synced groups are not listed, click **Check for updates** in **Organization settings > Groups**. Users in a custom-mapped group have no permissions until their group is attached to a role. | Director of IT | [S1]; [S2] |

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

Deploy the JSON file to `C:\Program Files\ClaudeCode\managed-settings.json`, or write the `Settings` registry value under `HKLM\SOFTWARE\Policies\ClaudeCode`, from a device configuration profile or a script that Intune assigns to the device group. **⚠ Unverified:** confirm the exact Intune blade names and the OMA-URI or script setup at setup. Anthropic's docs point to a starter template for Intune in the MDM examples repository [S5], which we did not open. Use that template, and confirm it against Intune's own current docs.

Intune can assign scripts and apps to user groups or device groups [S14]. The file and the HKLM value are machine-wide, so assign them to device groups **(Our recommendation)**. For how to split devices into plugin sets, see step 6.

### Jamf (macOS)

Build a configuration profile that sets the keys in the `com.anthropic.claudecode` domain, or deploy the file to `/Library/Application Support/ClaudeCode/managed-settings.json` with a policy script. **⚠ Unverified:** confirm the Jamf UI steps at setup. The MDM examples repository has a Jamf template [S5]; confirm it against Jamf's current docs.

### Kandji (macOS)

Anthropic's docs name Jamf, Iru, Intune and Group Policy as the MDM starter templates [S5]. They do not name Kandji. The repo's settings README mentions Kandji as a macOS profile tool [starter-kit/settings/README.md](../settings/README.md). **⚠ Unverified:** confirm at setup the product name, and whether the Kandji and Iru profile steps are the same. Use the same profile content as Jamf: a configuration profile in the `com.anthropic.claudecode` domain, with the file path as the fallback.

### Check the file before you deploy

- Each file must be valid JSON. A malformed file or plist makes Claude Code refuse to start, and the error names the source [S5].
- The placeholders from step 0.4 must be replaced. A wrong org UUID also makes Claude Code exit at startup [starter-kit/settings/README.md](../settings/README.md); [S11].
- A missing file is not a failure: Claude Code runs without that source. A file the operating system will not let Claude Code read (for example a root-only file) is the same: sessions start without its policies, and `/status` and `claude doctor` record the failure. So a pilot can appear to work while the baseline is missing. Verify step 5 on every pilot device. Other read errors, such as an I/O error, make Claude Code exit at startup [S5].

## 5. Verify on a device that the settings took effect

**Who: Backup Owner** on one pilot device first, then a sample of the pilot group. The **Director of IT** reads the result.

| # | Check | Expected | Source |
|---|---|---|---|
| 5.1 | Start Claude Code on the device, run `/status`, and read the **Setting sources** line. | The line lists `Enterprise managed settings`, with the source in parentheses: `(plist)` or `(HKLM)` for MDM, `(file)` for the file path, `(remote)` for server-managed settings. | [S5] |
| 5.2 | Run `claude doctor`. | It lists each managed-settings entry Claude Code dropped, with its source and field. Its **Organization policy** line says where the claude.ai organization policy (Remote Control and cloud sessions) loaded from, or why it did not; that line needs Claude Code v2.1.261 or later. | [S5] |
| 5.3 | Check one key from the baseline. For example, in the pe-zdr file, `WebFetch` and `WebSearch` are denied by bare tool name, so ask Claude to fetch a web page. Then ask Claude to read a `.env` file inside the project folder. | Claude has no web fetch or web search tool: a bare tool name in `deny` removes the tool from Claude's context. The `.env` read is refused. `Read(**/.env)` matches files at or under the current directory only. | [starter-kit/settings/README.md](../settings/README.md); [S13]; **not re-tested here** |
| 5.4 | Run `/plugin` on the device. | The marketplace `digital-twin-kit` and the plugins for the device's group are listed (step 6). | [S4] |
| 5.5 | If a device shows no policy, check that the file or profile is at the path in step 4, and that the source is not blocked by a higher-ranked source. Read `/status` again. | The `Setting sources` line names the source Claude Code used. On v2.1.242 or later, a `Skipped sources` line names any source it found and did not use. | [S5] |

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
- **Server-managed settings.** On an Enterprise plan, give each group its own configuration in the claude.ai admin console, under **Organization settings > Claude Code > Managed settings**, with **Add configuration**. Requires the Owner or Primary Owner role [S4]; [S12]. Each group must already exist in Claude, synced through SCIM or created as a custom group. Group configurations do not merge with each other or with the organization-wide one, so each must hold the whole baseline. They are not yet available to organizations with HIPAA enabled [S12]. This path covers devices that are not under MDM, and cloud sessions, which only read server-managed settings [S4].

Per-group server-managed configurations need Enterprise: on a Team plan one configuration applies to every user [S17]. A Team reader follows [Team plan: no SCIM, no group targeting](#team-plan-no-scim-no-group-targeting) instead.

On the device-group path, SCIM groups (step 1) decide the role and seat in Claude, not which plugins a device gets: keep the device groups separate from the SCIM groups, and name them so they are not confused. On the server-managed path, the configuration is chosen by Claude group, so a SCIM-synced group can carry a plugin set [S12]. Use a group your identity provider syncs, so no one can add themselves to it in the admin console [S12].

### Steps

| # | Step | Who | Source |
|---|---|---|---|
| 6.1 | Confirm the placeholder repo in both marketplace keys (`strictKnownMarketplaces` and `extraKnownMarketplaces`) is replaced with the customer's repo that holds the kit (step 0.4). Confirm the kit's repo is readable by every user who will install from it. A private repo needs each user to have read access. Users without a git-host account need a seed instead. | Partner integration engineer | [S4]; [repo files] |
| 6.2 | Decide the plugin set for each group. Suggested: `twin-shared` for every role, the role plugin for its role group, and `twin-governance` for devices in the confidential, pe-zdr and hipaa baselines. | Director of IT, Skill owners, RevOps manager | [starter-kit/README.md](../../starter-kit/README.md); the mapping itself is **(Our recommendation)** |
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
- [S7] Okta, Create SAML app integrations. https://help.okta.com/en-us/content/topics/apps/apps_app_integration_wizard_saml.htm
- [S8] Okta, Add SCIM provisioning to app integrations. https://help.okta.com/en-us/content/topics/apps/apps_app_integration_wizard_scim.htm
- [S9] Okta, Define group attribute statements. https://help.okta.com/en-us/content/topics/apps/define-group-attribute-statements.htm
- [S10] Okta, Configure provisioning for an app integration. https://help.okta.com/en-us/content/topics/provisioning/lcm/lcm-provision-application.htm
- [S11] Claude Code authentication, restrict login to your organization. https://code.claude.com/docs/en/authentication#restrict-login-to-your-organization
- [S12] Configure server-managed settings, give groups different settings. https://code.claude.com/docs/en/server-managed-settings#give-groups-different-settings
- [S13] Claude Code permissions, deny rules and Read path patterns. https://code.claude.com/docs/en/permissions
- [S14] Microsoft Intune Management Extension (scripts and Win32 apps assigned to a user or device). https://learn.microsoft.com/en-us/intune/device-management/tools/management-extension-windows
- [S15] Setting up single sign-on (SSO), plans and admin location. https://support.claude.com/en/articles/13132885-setting-up-single-sign-on-sso
- [S16] Roles in Team and Enterprise plans. https://support.claude.com/en/articles/9267276
- [S17] Configure server-managed settings (requirements, current limitations, security considerations). https://code.claude.com/docs/en/server-managed-settings
- [S18] Deploy managed settings, how Claude Code combines managed sources. https://code.claude.com/docs/en/managed-settings#how-claude-code-combines-managed-sources
- [S19] Claude Code authentication, Claude for Teams or Enterprise (invite members). https://code.claude.com/docs/en/authentication#claude-for-teams-or-enterprise
