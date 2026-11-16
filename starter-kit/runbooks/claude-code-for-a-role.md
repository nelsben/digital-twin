# Runbook: get Claude Code installed, signed in and checked for a role that does not use it yet

## What this is

Some twin tasks run in Claude Code, and some roles (a deal team, customer success, RevOps) have never used it. This runbook takes one such role from "no Claude Code" to "each pilot user has a seat that includes it, a working install, a sign-in that belongs to the customer's organization, the managed settings in force, and the kit's role plugin running one task". It does not deploy the managed settings or publish the marketplace: [identity-devices-publishing.md](identity-devices-publishing.md) does that, and this runbook links its sections instead of copying them. It is generic: replace every `<placeholder>` with the customer's value.

Roles use the names in [03-stakeholders](../../docs/playbook/03-stakeholders.md):

| Name used here | Role in 03-stakeholders |
|---|---|
| **Director of IT** | Technical owner. Claude org Owner, seats, devices and MDM, managed settings |
| **Backup Owner** | IT administrator. Runs device steps for the Director of IT |
| **Pilot user** | Pilot users (5 to 10 per role). Install, sign in and run the first task |
| **RevOps manager** | Business owner. Names the pilot users |
| **Skill owners** | Subject-matter experts. Pick the first-run task from the role plugin |
| **Security** | CISO or security engineer. Reads the device result |

## Read this first

Each step and product fact ends with the pages it came from, as tags like ([A]) that "Pages used" defines. **⚠ Unverified:** (the compendium's marker) means no page we downloaded states it; the item says what to confirm. Commands, menu paths and phrases are copied from the pages as downloaded on 2026-11-16.

Checked 2026-11-16 by the author against the pages listed. Every claim was checked again on 2026-11-16 by a second reader; the results are in the [verification log](verification-log.md).

Pages used:

- [A] [Use Claude Code with your Team or Enterprise plan (help center)](https://support.claude.com/en/articles/11845131)
- [B] [Advanced setup: install, verify, update](https://code.claude.com/docs/en/setup.md)
- [C] [Authentication](https://code.claude.com/docs/en/authentication.md)
- [D] [Deploy managed settings](https://code.claude.com/docs/en/managed-settings.md)
- [E] [Server-managed settings](https://code.claude.com/docs/en/server-managed-settings.md)
- [F] [Discover and install plugins](https://code.claude.com/docs/en/discover-plugins.md)
- [G] [Commands](https://code.claude.com/docs/en/commands.md)
- [H] [CLI reference](https://code.claude.com/docs/en/cli-reference.md)
- [I] [Skills](https://code.claude.com/docs/en/skills.md)
- [J] [Troubleshoot installation and login](https://code.claude.com/docs/en/troubleshoot-install.md)

## Inputs you need

- **The plan:** Team, Enterprise, or an older Enterprise plan with seat types. Compendium [09](../../docs/compendium/09-plans-and-it-controls.md) lists Claude Code as available on both.
- **The pilot users and the role's group:** named by the RevOps manager, with the group-to-role mapping from [identity runbook section 3](identity-devices-publishing.md#3-map-groups-to-roles-and-seats). On Team there is no group mapping: see [Team plan](identity-devices-publishing.md#team-plan-no-scim-no-group-targeting).
- **The device list:** each pilot user's device, its operating system (macOS or Windows) and whether it is managed.
- **The settings baseline** for the role's data class, already chosen and its placeholders replaced (identity runbook step 0.3 and 0.4).
- **The role plugin:** its name, for example `twin-pe-deal-team`, and the one skill to run first, picked by the Skill owners.
- **The organization's sign-in:** the claude.ai account each person was invited with ([C]).

## Before you start

- The pilot users are in the Claude organization and in the role's group (identity runbook section 3, or the invites on Team). The free claude.ai plan does not include Claude Code ([B]).
- The managed-settings file for the baseline is on the device **before** the first sign-in ([identity runbook section 4](identity-devices-publishing.md#4-deploy-the-managed-settings-baseline-to-devices)). Anthropic says to deploy the sign-in lock `forceLoginOrgUUID` through device management tooling, because a person receives server-managed settings "only after authenticating into your organization", so those settings cannot redirect a first sign-in ([C]).
- The device meets the requirements: macOS 13.0+, or Windows 10 1809+ or Windows Server 2019+, 4 GB+ RAM, an internet connection ([B]).
- On a HIPAA-ready Enterprise plan, Claude Code is included in the seat but "available but not covered under your BAA" without the HIPAA configuration or ZDR; do not use it with PHI until that is applied ([A]).

## Steps

1. **Who: Director of IT.** Give each pilot user a seat that includes Claude Code. "Claude Code is included with every Team plan seat"; on new and self-serve Enterprise plans it is included with the single Enterprise seat; on older Enterprise plans the user needs a Chat + Claude Code or Premium seat, which Owners buy or reassign in **Organization settings > Organization** ([A]). Put each person in the role's group by [identity runbook section 3](identity-devices-publishing.md#3-map-groups-to-roles-and-seats). On Team, invite the person and set roles by hand (identity runbook T1 to T4). ([A])
2. **Who: Backup Owner, with the Pilot user.** Install Claude Code on the managed device. **macOS:** in Terminal run `curl -fsSL https://claude.ai/install.sh | bash`, or `brew install --cask claude-code` for Homebrew. **Windows:** in PowerShell run `irm https://claude.ai/install.ps1 | iex`, or `winget install Anthropic.ClaudeCode` for WinGet; "You do not need to run as Administrator." Homebrew and WinGet installs do not auto-update, so the owner of the device must run the upgrade command; the native installer updates itself. ([B])
3. **Who: Backup Owner.** Open a new terminal and run `claude --version`; a working install prints a version number. Run `claude doctor` for install and settings diagnostics. If `claude` is "not found", the install directory is not on the PATH: follow the PATH fix in the troubleshooting page. ([B], [J])
4. **Who: Pilot user.** Sign in with the organization account. Run `claude`; a browser window opens. Choose **Claude account with subscription**, select the Team or Enterprise plan and click **Authorize**; the terminal shows `Login successful`. Do not use an API key or a Console login. If the person is already signed in to another account, run `/login`. ([A], [C])
5. **Who: Backup Owner, with the Pilot user.** Confirm the session belongs to the organization. Run `/status`, which shows "version, model, account, and connectivity" ([G]), and check that the account is the invited work address and the **Login method** is the subscription, not an API key ([C]). With `forceLoginOrgUUID` deployed, "Claude Code reports an error for a claude.ai login to any other organization" ([C]), so a session that starts is a first signal. **⚠ Unverified:** no page we downloaded says which rows `/status` shows for a claude.ai subscription login; the one page that names an `Organization` row describes a profile credential. Confirm at setup what the rows read, and compare the email with the member list in **Organization settings > Members**. `claude auth status --text` prints sign-in status ([H]); **⚠ Unverified:** whether it names the organization.
6. **Who: Backup Owner.** Confirm the managed settings from [identity runbook section 4](identity-devices-publishing.md#4-deploy-the-managed-settings-baseline-to-devices) are in force, with the check in [identity runbook section 5](identity-devices-publishing.md#5-verify-on-a-device-that-the-settings-took-effect): in `/status` the `Setting sources` line lists `Enterprise managed settings`, with `(plist)` or `(HKLM)` for MDM, `(file)` for a file, `(remote)` for server-managed settings ([D]). If the line is missing, Claude Code found no managed source that delivers a policy key: check that the file sits at the path for the OS and that it holds a policy key, not only control keys ([D]). For server-managed settings, `claude doctor` shows the `Managed settings (remote)` line ([E]).
7. **Who: Backup Owner.** Add the kit's marketplace and install the role plugin, as [identity runbook section 6](identity-devices-publishing.md#6-publish-the-marketplace-and-its-plugins-to-the-right-groups) sets out. Where the managed settings register `digital-twin-kit` and enable the role plugin, run `/plugin` and read the **Installed** tab. Otherwise, in a session run `/plugin marketplace add <github-org>/digital-twin-kit`, then `/plugin install <role-plugin>@digital-twin-kit`, which opens the plugin's details so you can choose a scope before it installs. ([F])
8. **Who: Pilot user, with a Skill owner.** Run one task from the role plugin. A plugin skill is invoked as `/plugin-name:skill-name`, for example `/twin-pe-deal-team:preparing-company-briefs` ([I]). Use a fictional or public input the Skill owners agreed.

**(Our recommendation):** do steps 2 to 8 for one person first, fix what they hit, then repeat for the rest of the pilot group.

**Unmanaged devices:** if the role's devices are not managed, there is no device-management route to deploy the sign-in lock or the managed settings file, and a user can bypass server-managed settings; follow the policy by data class in compendium [13](../../docs/compendium/13-devices.md) ([C], [E]).

## Check it worked

**Who: Backup Owner, with the Pilot user. About fifteen minutes per person.**

| # | Do this | Pass if |
|---|---|---|
| 1 | `claude --version` in a new terminal | A version number prints. ([B]) |
| 2 | `/status` | The account is the invited work address; `Setting sources` lists `Enterprise managed settings`. ([D], [G]) |
| 3 | `claude doctor` | No dropped managed-settings entry and no install warning. ([B], [D]) |
| 4 | `/plugin` | `digital-twin-kit` and the role plugin are listed. ([F]) |
| 5 | The first task from step 8 | The skill runs and the output is what the Skill owner expects. ([I]) |

Do not roll out to the rest of the group until checks 2 and 4 pass on the first person's device.

## Hand over

**Who: Backup Owner to the Director of IT, the RevOps manager and the Skill owners.** In the customer's folder under `engagements/<customer>/`, record per pilot user: the seat type; the operating system and the install method; the version `claude --version` printed; the date and result of each check above; the managed source `/status` named; and each unverified item still open. The Director of IT owns seats and devices; the Skill owners own the role plugin.

## What can go wrong

- **No Claude Code option on sign-in, or the wrong account.** Run `/logout`, then `claude update`, restart the terminal and run `claude` again ([A]). `/login` switches an account ([A]).
- **`claude` not found after install.** The PATH lacks the install directory ([B], [J]).
- **The session exits at start with an organization error.** The sign-in belongs to another organization, or `forceLoginOrgUUID` holds a wrong value, and then no organization may log in ([C], [D]).
- **An API key is set.** Under `forceLoginOrgUUID`, `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN` and `apiKeyHelper` are blocked at startup; run `unset ANTHROPIC_API_KEY` and check `/status` ([C]).
- **`Setting sources` line missing.** Check the file path and the placeholders ([D]); see identity runbook section 5.
- **A non-default `ANTHROPIC_BASE_URL` or a `CLAUDE_CODE_USE_*` variable.** Claude Code skips the server-managed settings fetch ([E]).
- **Homebrew or WinGet install out of date.** Run the upgrade command ([B]).
- **The plugin skill does not run.** Check the plugin is listed in `/plugin` and use the namespaced command ([F], [I]).
- **Install on a managed device by MDM.** **⚠ Unverified:** no page we downloaded gives an MDM package or script for installing Claude Code; step 2 uses Anthropic's own installers. Confirm with Security and the device team.
- **Desktop instead of the terminal.** **⚠ Conflict:** [A] says "Recommended" is Claude Desktop with its Code tab, and [B] marks the native install "(Recommended)". We take the terminal install, because the managed-settings checks above are written for it. **⚠ Unverified:** whether the Desktop Code tab reads the managed settings file.
