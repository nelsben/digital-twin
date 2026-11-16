# Wall test: scratch-org dry run (Salesforce)

A throwaway Salesforce scratch org with two roles, one test user in each, and invented records on each side. `wall_test.py` replays the API-level cases of the [wall-test protocol](../../../../engagements/sample-pe/wall-test-protocol.md) (WT-01 to WT-16, the cases marked "can be dry-run at the API level") as each user, deploys the kit's [twin-marker metadata](../README.md), runs the `UserRecordAccess` `HasEditAccess` check from the CRM-update skill's [level-2-writes.md](../../../plugins/twin-pe-deal-team/skills/drafting-crm-updates/references/level-2-writes.md), prints a pass or fail table, and deletes the org.

All data is invented (WALLTEST- names, Project Larch, example.com addresses).

## Status

**Not yet run.** The first attempt stopped at scratch-org creation with `STORAGE_LIMIT_EXCEEDED: storage limit exceeded` (the Dev Hub's data storage showed 0 MB remaining of 5 MB). No org was created and nothing was deleted. There are no results below because none were observed. Only the create step of the script has run, so expect small fixes on the first full run.

## What you need

- Python 3 and the Salesforce CLI (`sf`).
- A Dev Hub you are logged in to, with a free scratch org and some data storage. Pass its alias as the only required argument. The script never stores it.
- No default org is used. Every `sf` call except the scratch-org create and `sf org list` must name the scratch org (`twin-wall-test`) or one of the two test-user aliases (`twin-wall-d`, `twin-wall-i`); the script refuses any other target before the CLI runs.

## Run it

```
python3 wall_test.py <dev-hub-alias>
```

| Option | Effect |
|---|---|
| `--keep-org` | Skip the delete stage, so you can look at the org. Delete it yourself: `sf org delete scratch --target-org twin-wall-test --no-prompt` |
| `--stages setup,cases,marker,delete` | Run some stages only. Setup is safe to repeat: it reuses the org, redeploys, and reseeds. |
| `--search-wait <seconds>` | How long a search control waits for the search index (default 240). A pair whose control never passes is reported NOT RUN |

Stages: create the org (Enterprise, 3 days), deploy the metadata, create the two users and seed the records; run WT-01 to WT-16; deploy the marker and run the access check; delete the org and confirm it is gone from `sf org list`. Exit code 0 means every row passed.

## What is in this folder

| Path | What it is |
|---|---|
| `config/project-scratch-def.json` | The scratch-org definition (Enterprise) |
| `force-app/main/default/roles/` | Roles Deal Team and Investor Relations, both at the top of the hierarchy, neither above the other |
| `force-app/main/default/objects/` | Sharing: Opportunity and Account private, Contact controlled by parent |
| `optional/enable-opportunity-history/` | Turns on Opportunity history. Used only if the marker deploy fails without it |
| `wall_test.py` | The script |
| `sfdx-project.json` | Makes this folder an SFDX project |

## How the cases map

The users are two Standard User accounts with no Modify All Data or View All Data (the script checks this). Every seeded record on a side is owned by that side's user. Content tokens are `ZD` or `ZI` plus 6 characters, made at seed time and read back by the script as admin.

| Protocol cases | API call, as the user the case names |
|---|---|
| WT-01 to WT-04 | SOQL for the four records by name, then by id (with `FOR VIEW`) |
| WT-05 to WT-08 | SOSL `FIND {WALLTEST*}` over opportunities, accounts, contacts and tasks, plus a search for the other side's token |
| WT-09 to WT-12 | SOQL over all opportunities, accounts and contacts, `RecentlyViewed`, and the All Opportunities list view through the REST API |
| WT-13 to WT-16 | `COUNT()`, and a grouped count by owner |

A blocked case passes only when nothing of the other side comes back (name, token, record id), the call reached the API, and its control passed. This is stricter than the protocol's leak rule, which excludes names the actor typed. A control that fails marks its pair NOT RUN.

## Results

None yet. See Status.

## What this does not prove

- Calls were made through the Salesforce API as each user, not through the Salesforce Hosted MCP connector or Claude. Nothing here shows what the connector's tools expose or how Claude uses them.
- A scratch org's sharing model is not the customer's. The roles, the private defaults and the standard profile here are a stand-in; the live run must test the customer's own roles, sharing rules and permission sets.
- SharePoint and HubSpot are not covered, and neither are the skill, Project, memory and shared-file routes (WT-17 to WT-53).
- Salesforce audit, the governance log and Event Monitoring are not checked.
- The search cases wait for the index for minutes, not the 24 hours the protocol asks for.
- It shows the cases run and the rules apply, as the protocol says; it does not show a customer's wall holds.
