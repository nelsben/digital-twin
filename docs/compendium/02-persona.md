# 02 — Persona and memory

## What a persona is

For a role twin, the persona is not a character. It is a **job description written for Claude**: who it works for, what it is for, how it should sound, and where its limits are.

Anthropic's guidance:

- **A role helps, even a short one.** "Even a single sentence makes a difference."
- **Explain why** each instruction exists. Claude applies instructions better when it knows the reason.
- **Ask before irreversible or externally visible actions,** such as sending, deleting or publishing.

Source: [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices.md).

## A persona template (our recommendation)

```markdown
You are the <role> twin for <company>'s <team>. You support <who> with <the 3–5 jobs>.

Why you exist: <the outcome the team cares about, e.g. "AEs spend less time on prep and CRM upkeep and more time with customers">.

How you work:
- <working norm + why, e.g. "Cite the CRM record or document for every fact, because reps forward your output to customers.">
- <tone: e.g. "Direct and brief; reps read this between calls.">

Boundaries:
- Never <hard limit + why>.
- Before anything a customer or another team would see, show a draft and wait for approval.
- If you lack data, say what's missing instead of guessing.

When unsure, <escalation path: ask the user / name the team that owns it>.
```

Keep the persona short. Put task procedures in skills, not in the persona: the persona is always loaded, while a skill loads only when it is needed.

## Where the persona lives on each surface

| Surface | Mechanism | Notes |
|---|---|---|
| API, Agent SDK, Managed Agents | System prompt | You control it fully. |
| Claude Code | **Output style** for role, tone and format, plus **CLAUDE.md** for facts that are always true (under 200 lines) | A custom output style drops Claude Code's coding instructions unless `keep-coding-instructions: true` is set. A plugin can force its style with `force-for-plugin`. Subagents don't inherit the style. ([Output styles](https://code.claude.com/docs/en/output-styles.md)) |
| Claude.ai, Desktop | Project instructions; skills | **⚠ Unverified:** how a Project's instructions relate to an org plugin (not confirmed in this research). Confirm before relying on it. |
| Claude Tag (Slack) | Channel memory and workspace notes | Anyone in the channel can read and edit these. ([Tag memory](https://claude.com/docs/claude-tag/users/memory.md)) |

**Treat the persona as an instruction, not a guarantee.** Anthropic says this directly about output styles. Hard limits belong in tool permissions and hooks ([06](06-autonomy.md)).

**One persona, several surfaces.** If the same twin runs on claude.ai and in Claude Code, you will keep the persona in two forms. Keep the master copy in Git and generate both from it.

## Memory

A role twin needs **role memory**: the playbook, the product facts, the house style. That knowledge goes in skills and reference files, not in conversation memory. Personal memory is optional, and it comes with risks.

| Mechanism | Scope | What to know |
|---|---|---|
| Claude.ai memory | Per user. Projects can keep their own separate memory. | Owners can switch memory on or off for the org, but cannot view or edit a member's memories. Some orgs still run the older memory version. ([Memory article](https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context)) |
| API memory tool (`memory_20250818`) | Whatever your app decides | Your app stores the data, so it can be eligible for zero data retention (ZDR) and HIPAA. You must build path-traversal protection, size limits and expiry yourself. ([Memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool.md)) |
| Managed Agents memory stores | Per store, attached to a session | 100 kB per memory, 10,000 memories per store, 8 stores per session. Versioned and attributed. The docs warn about prompt injection, so mark reference stores `read_only`. ([Managed Agents memory](https://platform.claude.com/docs/en/managed-agents/memory.md)) |
| Claude Tag channel memory | Per Slack channel | Anyone in the channel can read and edit it. From a public channel Claude can also save workspace notes, which it reads "in every channel in the workspace, private channels included". A private channel reads the workspace notes read-only and saves to its own channel notes only, and workspace notes saved while a channel was public stay shared until an Owner deletes them ([Tag memory](https://claude.com/docs/claude-tag/users/memory.md)). (Our recommendation): run a role whose channel memory must stay in its channel in a private channel from the start, and have an Owner review the workspace notes. |

**Memory poisoning.** If a twin reads untrusted input (customer emails, tickets, web pages) and can also write to memory, an attacker can plant instructions that persist. Keep role knowledge read-only and reviewed. Let only controlled steps write memory.
