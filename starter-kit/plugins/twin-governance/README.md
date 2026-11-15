# twin-governance

The guardrails plugin: hooks that enforce governance and performance rules across role twins.

Status: version 0.3.0. It ships one hook, the governance log hook. Other folders are still placeholders; no skills or output styles are written yet.

## Compendium pages

- [04-distribution-governance.md](../../../docs/compendium/04-distribution-governance.md)
- [15-governance-and-performance.md](../../../docs/compendium/15-governance-and-performance.md)

## The governance log hook

`hooks/hooks.json` registers `hooks/governance_log.py` on `PostToolUse` and `PostToolUseFailure` for all tools (matcher `*`), with a 5 second timeout. After every tool call the script appends exactly one JSON line to a local log file. This is the local source for the long-term audit record described in compendium 15: private-equity chat retention is 30 days and ZDR sessions are not in the Compliance API, so we keep our own log, and for private-equity data it holds metadata only.

The script is Python 3 standard library only (the hook runs `python3`, so IT needs Python 3 on the PATH of managed devices). It never blocks or changes a tool call: it always exits 0, prints nothing to stdout, and reports problems (bad input, an unwritable log) on stderr only.

### What is logged

One line per call, with these fields:

| Field | Value |
|---|---|
| `schema_version` | `2` |
| `ts` | UTC timestamp, ISO 8601, ending in `Z` |
| `session_id` | Claude Code session id |
| `event` | `PostToolUse` or `PostToolUseFailure` |
| `tool` | Tool name, such as `Bash` or `mcp__salesforce__query` |
| `outcome` | `success` for `PostToolUse`, `failure` for `PostToolUseFailure` |
| `cwd_hash` | First 12 hex characters of sha256 over `TWIN_GOVERNANCE_SALT` plus the full working directory; left out when no salt is set (see below) |
| `os_user` | OS user name |
| `twin_id`, `org_label` | From `TWIN_GOVERNANCE_TWIN_ID` and `TWIN_GOVERNANCE_ORG_LABEL`; `null` if unset |
| `mcp_server`, `mcp_tool` | For MCP tools, parsed from `mcp__<server>__<tool>`; `null` otherwise |
| `record_ids` | Record ids from `tool_input` that match a known system id format (see below); `[]` if none |

Example:

```json
{"schema_version":2,"ts":"2026-11-14T09:30:12.345Z","session_id":"abc123","event":"PostToolUse","tool":"mcp__salesforce__update_record","outcome":"success","os_user":"jsmith","twin_id":"twin-pe-deal-team","org_label":"pe-org","mcp_server":"salesforce","mcp_tool":"update_record","record_ids":["0065e00000AbCdEfGH"],"cwd_hash":"3b1f0c9a47de"}
```

### What is never logged

Metadata-only is the only mode. These are dropped and never written:

- `tool_input` values, except record ids
- `tool_response` and the `error` text of a failed call
- prompts, file contents, and transcript paths
- full paths and folder names (the working directory is logged only as a salted hash, `cwd_hash`)

The only thing taken from `tool_input` is a list of record ids: the values of keys named `id`, `Id`, `recordId`, `record_id`, or ending in `_id`, found at any depth, at most 20 per line. A value is kept only if the whole value matches one of these known system id formats:

| System | Accepted form |
|---|---|
| Salesforce | 15 or 18 alphanumeric characters (letters and digits, no other characters) |
| HubSpot | Digits only, 1 to 20 of them |
| Microsoft Graph | GUID: 8-4-4-4-12 hex digits with dashes, either case |

Every other value is dropped, not truncated or hashed. This matters on deal teams: a key such as `deal_id` can hold a code name like `Falcon_target`, and an id-shaped free-text value must not reach the log. Such values never match the allowlist, so they are not logged. `tests/test_governance_hook.py` proves this: it feeds a fake secret, a prompt and a file body through `tool_input`, `tool_response` and `error`, and checks that none of them appear in the log line, and it checks that a code name under an id key logs no record id.

### Why folder names are not logged

Earlier versions (schema 1) logged the working directory's last folder name as `cwd_basename`. On a deal team the working folder is often the deal's code name, so the folder name itself can leak it. Version 0.3.0 removes `cwd_basename`. The log still needs a way to tell whether two lines came from the same working directory, so it holds `cwd_hash` instead: the first 12 hex characters of sha256 over the salt plus the full working directory path. The same folder and salt always give the same hash, so lines can be grouped, but the hash cannot be turned back into a name without the salt and a guess at the path. If `TWIN_GOVERNANCE_SALT` is not set, the field is left out rather than written unsalted, because an unsalted hash of a guessable path is easy to reverse. The salt itself is never logged.

### Configuration

Set these environment variables for the Claude Code process (for example through managed settings `env`, or the device's login environment):

| Variable | Default | Meaning |
|---|---|---|
| `TWIN_GOVERNANCE_LOG` | `~/.claude/twin-governance/log.jsonl` | Log file path. Missing directories are created. The file is created with mode 0600 and new directories with 0700. |
| `TWIN_GOVERNANCE_TWIN_ID` | unset | Twin id written to every line, such as `twin-pe-deal-team` |
| `TWIN_GOVERNANCE_ORG_LABEL` | unset | Org label written to every line, such as `pe-org` |
| `TWIN_GOVERNANCE_SALT` | unset | Salt for `cwd_hash`. Set it to a secret value per customer or per deployment, and keep it out of the log destination. With no salt (or an empty one), `cwd_hash` is left out of every line. |
| `TWIN_GOVERNANCE_MODE` | `metadata` | The only mode. There is no content mode; any other value logs metadata only and prints a warning on stderr. |

### Getting the log to your SIEM

The log destination is a decision for each customer, and IT owns the tooling choice (compendium 15, "Where the log lives"). The plugin only writes a local file. IT picks the way it reaches the customer's SIEM, data warehouse or observability tool, for example a log forwarder or agent that tails `TWIN_GOVERNANCE_LOG` (one JSON object per line, UTF-8), or a scheduled job that ships and rotates the file. Points to settle with the customer:

- Where the forwarder reads: set `TWIN_GOVERNANCE_LOG` to a path the forwarder already watches.
- Who can read the log and how long it is kept. For private-equity data, restrict access as tightly as the deal data, and keep a reviewed record of who reads it.
- Rotation of the local file. The hook only appends; it never truncates or rotates.

### Deploying it: managed hooks

The `pe-zdr` and `hipaa` settings baselines (and `confidential`) set `allowManagedHooksOnly`, so only hooks that IT deploys run. A plugin installed by a user does not run its hooks under that setting. For the governance hook to run there, deploy `twin-governance` through the managed marketplace (see [settings README](../../settings/README.md)), not as a user install. If the hook is not running on a managed device, check this first.

## Filled in by

#21
