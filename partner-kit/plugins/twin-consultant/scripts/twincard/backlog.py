"""Build a persona's backlog: turn card.json and levelled.json into backlog.json and backlog.md.

build(persona_dir) validates the card, checks levelled.json is present, was made from the current
card and profile, and is what level gives now (it levels again in memory and compares the parsed
plans; whitespace and key order are not a difference), then builds the backlog from
data/task-library.json; it never writes.
write_backlog(persona_dir) does the same and writes <persona_dir>/backlog.json and backlog.md.

    {"ok": bool,                  # False on validation errors or a missing or stale levelled.json
     "validation": {...},         # the validate() result
     "error": str or None,        # why nothing was built
     "backlog": {...} or None,    # the backlog.json content
     "retired_now": [...]}        # items this run retired: [{"id", "title", "status"}]

The epic is the role twin; one feature per card feature, then F-twin-foundation; one story per
card task, then the seven foundation stories; tasks come from the library's templates, whose
'when' conditions use the levelling engine's condition language (level.matches). Statuses are
kept across runs. Every value written to backlog.md goes through one helper (_md) so card and library
text cannot change the page's structure; backlog.json and the --plan-out tree keep the raw values.
Design of record: partner-kit/docs/design.md, section 8.
"""

import hashlib
import json
import re
from pathlib import Path

from . import fields as _fields
from . import level as _level
from . import validate as _validate

PLUGIN_DIR = _level.PLUGIN_DIR
REPO_ROOT = PLUGIN_DIR.parent.parent.parent
LIBRARY_PATH = _level.DATA_DIR / "task-library.json"
BACKLOG_JSON = "backlog.json"
BACKLOG_MD = "backlog.md"
CLI_PATH = "partner-kit/plugins/twin-consultant/scripts/twincard/cli.py"
# backlog.md sits in engagements/<engagement>/personas/<persona>/, four folders below the repository root.
MD_LINK_PREFIX = "../../../../"

BACKLOG_VERSION = 1
LIBRARY_VERSION = 1
STALE = "levelled.json is missing or out of date. Next: run the level command."
STATUSES = ("todo", "in-progress", "done")
MARKS = {"todo": "[ ]", "in-progress": "[~]", "done": "[x]"}
PARTS = tuple("A%d" % n for n in range(1, 10))
TASK_STORY = "task-story"
TEMPLATE_KEYS = ("id", "title", "part", "applies_to", "per", "when", "how", "done_when", "owner_role")
STEP_KEYS = ("text", "link")
ID_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

FOUNDATION_FEATURE = ("F-twin-foundation", "Twin foundation")
# (story id, title, part): the work every twin needs whatever its tasks are.
FOUNDATION = (
    ("S-persona-voice", "Persona voice", "A1"),
    ("S-connectors-and-identity", "Connectors and identity", "A3"),
    ("S-guardrails-and-settings", "Guardrails and settings", "A7"),
    ("S-distribution", "Distribution", "A9"),
    ("S-governance-log", "Governance log", "A9"),
    ("S-memory-policy", "Memory policy", "A6"),
    ("S-pilot-rollout-and-scorecard", "Pilot rollout and scorecard", "A8"),
)
FOUNDATION_IDS = tuple(sid for sid, _, _ in FOUNDATION)
# A persona-level code whose template serves task stories lands in this foundation story.
PERSONA_CODE_STORY = "S-guardrails-and-settings"

FOUNDATION_ACCEPTANCE = {
    "S-persona-voice": ["persona.md is filled in from the card's voice section, with a reason for every rule.",
                        "The output style and the system prompt match persona.md.",
                        "The business owner has approved the voice."],
    "S-connectors-and-identity": ["Every connector the role uses is listed with its identity and approver.",
                                  "The role's users are in the organisation with the right role."],
    "S-guardrails-and-settings": ["The settings, or what replaces them, are in force for the role.",
                                  "Compliance has signed off the data policy for each data class."],
    "S-distribution": ["The role plugin reaches the role's users at the current version, and no one else it must "
                       "not reach."],
    "S-governance-log": ["What is logged for the twin, and where, is agreed and checked."],
    "S-memory-policy": ["The memory policy is written down and in force."],
    "S-pilot-rollout-and-scorecard": ["The pilot users are trained, the baseline is recorded, and the first "
                                      "scorecard is reviewed."],
}

# --- Facts a template's 'when' may read -----------------------------------------------------------

PERSONA_FACTS = ("plan.tier", "role.device", "distribution", "settings_baseline", "governance.log",
                 "compliance.walls", "memory.personal_memory_wanted", "systems.kinds", "systems.products",
                 "writes.kinds", "writes.products", "codes")
TASK_FACTS = ("task.trigger", "task.data_class", "task.output.audience", "task.reversible", "task.touches_money",
              "task.cost_of_mistake.level", "task.reads_untrusted_input", "task.in_pilot", "task.write_actions",
              "delivery.form", "writes.crm_opens", "tools.write_permissions", "tools.send_permissions")
DECISION_FACTS = ("runtime", "identity", "autonomy.start", "autonomy.ceiling", "data_controls.settings_baseline",
                  "data_controls.web_tools", "data_controls.surfaces", "data_controls.retention", "memory",
                  "plan_fit")
ITEM_FACTS = {
    "connector": ("connector.system", "connector.kind", "connector.product", "connector.access",
                  "connector.permission", "connector.runbook", "connector.unverified"),
    "tool": ("tool.system", "tool.use", "tool.permission"),
    "unverified-decision": ("decision.name",),
}
ALL_ITEM_FACTS = tuple(name for names in ITEM_FACTS.values() for name in names)
GOVERNANCE_CAPABILITY = "governance-action-log"
# Fields from the interviews that a task story carries when the card holds them (design section 8).
WRITE_SKILL = "write-skill"
CONSTRAINTS_STEP = "Make the skill keep these rules from the interviews, in the interviewee's words: %s."
WANTED_CHANGE_LABEL = "Asked for, not planned: "
CONSTRAINTS_LINK = "partner-kit/docs/design.md#42-persona-card-cardjson"

# --- The story template (design section 8; docs/playbook/04-stories.md) ------------------------------

STATEMENT = "As a %s, I want my twin to %s so that %s."
DRAFTED_NOTE = "(Statement drafted by the kit: confirm the wording with the interviewee.)"
TARGET_NOT_SET = "Target: not set. Agree the scorecard targets with the sponsor before the pilot starts."
TO_WRITE = "To write: collect at least 3 real examples from %s and write one eval case from each."
UNNAMED_SKILL_OWNER = "the skill owner (not named yet)"
ACCEPT_TRIGGER = ("Plus: the skill triggers on the phrases its trigger evals list and stays quiet on the "
                  "near-misses.")
EXAMPLES_NEEDED = 3
# Data classes above confidential: their stories wait for compliance's sign-off before building.
SIGN_OFF_CLASSES = ("highly-sensitive", "phi")
SIGN_OFF_TEMPLATE = "compliance-sign-off"
SIGN_OFF_CHECK = "compliance-sign-off"
OWNER_HANDOVER = "owner-handover"
SPIKE_TITLE_MAX = 120

# --- Delivery, owners and parts (design section 8) ---------------------------------------------------

# The level at which a Blocked write tool becomes Needs approval (rules.json: a write at level 2 needs approval).
OPEN_LEVEL = 2
PERMISSION_NAMES = {"always-allow": "Always allow", "needs-approval": "Needs approval", "blocked": "Blocked"}
STAYS_LOCAL = "The output stays in the conversation or a local file."
ROUTINE_POSTS = ("The Claude Tag routine posts it in its own Slack channel itself, and the connector's send tool %s "
                 "is not used.")
AUTONOMY_PAGE = "docs/compendium/06-autonomy.md"
MOVING_UP = AUTONOMY_PAGE + "#rules-for-moving-up-a-level"
CONNECTORS_PAGE = "docs/compendium/11-connectors.md#what-exists-for-our-systems"
DELIVER_DRAFT = "deliver-draft"
DELIVER_STEP = ("Name who puts the draft in its destination (%s) and write down how, from the connector's "
                "runbook.")
MARKER_STEP = "The CRM write %s Blocked at the starting level and %s at level %d; set the marker up before it opens."
ACCEPT_MARKER = "Plus: every write carries the twin marker."
ACCEPT_NO_CRM_WRITE = "Plus: the twin writes nothing to the CRM at the starting level; a person files the result."
SALESFORCE_RUNBOOK = "starter-kit/runbooks/salesforce-hosted-mcp.md"
SALESFORCE_E6 = SALESFORCE_RUNBOOK + "#8-ip-allowlist-discovery-e6"
SALESFORCE_E6_STEP = "For Salesforce, run the runbook's IP allowlist discovery (E6) before the connection test."
PRIVATE_NETWORK_TEMPLATE = "warning-private-network-allowlist"
RUNBOOK_PLACEHOLDER = "{connector.runbook}"
# The anatomy part of each decision a confirm-unverified-decision task confirms: (name or prefix, part).
CONFIRM_TEMPLATE = "confirm-unverified-decision"
DECISION_PARTS = (("runtime", "A4"), ("identity", "A5"), ("autonomy.", "A7"), ("data_controls.", "A7"),
                  ("memory", "A6"), ("plan_fit", "A9"), ("connectors.", "A3"))
# Library owner roles the profile names, by its owners key; the partner's roles are never listed as unnamed.
PROFILE_OWNERS = {"executive-sponsor": "sponsor", "technical-owner": "technical_owner",
                  "business-owner": "business_owner", "backup-owner": "backup_owner", "compliance": "compliance"}
SKILL_OWNER = "skill-owner"
PARTNER_ROLES = ("engagement-lead", "solution-architect", "skill-engineer", "integration-engineer",
                 "change-and-enablement-lead", "consultant")


class BacklogError(ValueError):
    """A fault in task-library.json."""


class UsageError(ValueError):
    """A fault the person running the command can fix, such as an unknown status in backlog.json."""


# --- The task library ------------------------------------------------------------------------------

def allowed_facts(applies_to, per):
    """The fact names a template's 'when' may read."""
    names = set(PERSONA_FACTS)
    if applies_to == TASK_STORY:
        names |= set(TASK_FACTS) | set(DECISION_FACTS)
        if per:
            names |= set(ITEM_FACTS[per])
    return names


def _check_template(template, owner_roles, seen):
    tid = template.get("id") if isinstance(template, dict) else None
    where = "task-library.json template %r" % (tid,)

    def fail(message):
        raise BacklogError("%s: %s" % (where, message))

    if not isinstance(template, dict) or sorted(template) != sorted(TEMPLATE_KEYS):
        fail("must have exactly the keys %s" % ", ".join(TEMPLATE_KEYS))
    if not isinstance(tid, str) or not ID_PATTERN.match(tid):
        fail("the id must be kebab-case")
    if tid in seen:
        fail("duplicate id")
    seen.add(tid)
    if not isinstance(template["title"], str) or not template["title"].strip():
        fail("title must be a sentence")
    if template["part"] not in PARTS:
        fail("part %r is not one of A1 to A9" % (template["part"],))
    applies_to = template["applies_to"]
    if applies_to != TASK_STORY and applies_to not in FOUNDATION_IDS:
        fail("applies_to %r is not %s or a foundation story (%s)"
             % (applies_to, TASK_STORY, ", ".join(FOUNDATION_IDS)))
    per = template["per"]
    if per is not None and per not in ITEM_FACTS:
        fail("per %r is not null or one of %s" % (per, ", ".join(sorted(ITEM_FACTS))))
    if per is not None and applies_to != TASK_STORY:
        fail("per needs applies_to %s" % TASK_STORY)
    try:
        names = _level.fact_names(template["when"])
    except _level.LevelError as exc:
        fail("when: %s" % exc)
    allowed = allowed_facts(applies_to, per)
    for name in names:
        if name in allowed:
            continue
        if name in ALL_ITEM_FACTS:
            fail("when reads %s, an item fact, without the matching per" % name)
        if applies_to != TASK_STORY and (name in TASK_FACTS or name in DECISION_FACTS):
            fail("when reads %s, a task fact, but a foundation story has no task" % name)
        fail("when reads unknown fact %s" % name)
    how = template["how"]
    if not isinstance(how, list) or len(how) < 2:
        fail("how must list at least 2 steps")
    for index, step in enumerate(how):
        if not isinstance(step, dict) or sorted(step) != sorted(STEP_KEYS):
            fail("how[%d] must have exactly the keys text and link" % index)
        if not isinstance(step["text"], str) or not step["text"].strip().endswith("."):
            fail("how[%d] text must be one sentence ending in a full stop" % index)
        link = step["link"]
        if link is not None and (not isinstance(link, str) or not link or link.startswith("/") or "://" in link):
            fail("how[%d] link must be null or a repo-relative path" % index)
        if isinstance(link, str) and "{" in link:
            rest = link[len(RUNBOOK_PLACEHOLDER):] if link.startswith(RUNBOOK_PLACEHOLDER) else None
            if rest is None or "{" in rest or (rest and not rest.startswith("#")):
                fail("how[%d] link may hold %s only at its start, before an optional #anchor"
                     % (index, RUNBOOK_PLACEHOLDER))
            if per != "connector":
                fail("how[%d] link uses %s, which needs per connector" % (index, RUNBOOK_PLACEHOLDER))
    if not isinstance(template["done_when"], str) or not template["done_when"].strip():
        fail("done_when must be at least one sentence")
    if template["owner_role"] not in owner_roles:
        fail("owner_role %r is not in owner_roles" % (template["owner_role"],))


def load_library(path=None):
    """Return task-library.json, checked; raise BacklogError naming the template at fault."""
    target = Path(path) if path is not None else LIBRARY_PATH
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise BacklogError("task-library.json (%s) cannot be read as JSON: %s" % (target, exc))
    if not isinstance(data, dict) or sorted(data) != ["library_version", "owner_roles", "templates"]:
        raise BacklogError("task-library.json holds library_version, owner_roles and templates, nothing else")
    if data["library_version"] != LIBRARY_VERSION:
        raise BacklogError("task-library.json must have library_version %d" % LIBRARY_VERSION)
    roles = data["owner_roles"]
    if not isinstance(roles, list) or not all(isinstance(r, str) and ID_PATTERN.match(r) for r in roles):
        raise BacklogError("task-library.json owner_roles must be a list of kebab-case role ids")
    if not isinstance(data["templates"], list) or not data["templates"]:
        raise BacklogError("task-library.json templates must be a non-empty list")
    seen = set()
    for template in data["templates"]:
        _check_template(template, set(roles), seen)
    return data


# --- Reading the persona -----------------------------------------------------------------------------

def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _paths(persona_dir):
    persona = Path(persona_dir)
    return (persona / _validate.CARD_FILE, (persona / ".." / ".." / _validate.PROFILE_FILE).resolve(),
            persona / _level.LEVELLED_FILE)


def _read_levelled(persona_dir):
    """(card, profile, levelled) when levelled.json is what level gives now, else None.

    levelled.json must name the current card and profile by hash, and level, run again in memory on
    the current card, profile and kit data, must give the same plan once both are parsed. The plan
    returned is the one level gives now, so the backlog's levelled_sha256 is the hash of its text.
    """
    card_path, profile_path, levelled_path = _paths(persona_dir)
    if not levelled_path.is_file():
        return None
    card_bytes, profile_bytes = card_path.read_bytes(), profile_path.read_bytes()
    try:
        levelled = json.loads(levelled_path.read_bytes().decode("utf-8"))
        source = levelled["source"]
        stale = source.get("card_sha256") != _sha(card_bytes) or source.get("profile_sha256") != _sha(profile_bytes)
    except (ValueError, KeyError, TypeError, AttributeError):
        return None
    if stale:
        return None
    fresh = _level.level(str(persona_dir))
    if not fresh["ok"] or _level.canonical(fresh["levelled"]) != _level.canonical(levelled):
        return None
    return (json.loads(card_bytes.decode("utf-8")), json.loads(profile_bytes.decode("utf-8")), fresh["levelled"])


BACKLOG_FIX = "Next: fix backlog.json or delete it, then run the backlog command again."


def _unusable(what):
    return UsageError("backlog.json %s. %s" % (what, BACKLOG_FIX))


def read_statuses(persona_dir):
    """({task or spike id: (title, status)}, [retired entries]) from an existing backlog.json; UsageError if unusable.

    A file that is not JSON or not in backlog.json's shape, or a status outside todo, in-progress and done,
    is a usage error naming the file and what to do next.
    """
    path = Path(persona_dir) / BACKLOG_JSON
    if not path.is_file():
        return {}, []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise _unusable("cannot be read as JSON (%s)" % exc)
    if not isinstance(data, dict):
        raise _unusable("is not a JSON object")
    epic = data.get("epic")
    features = epic.get("features") if isinstance(epic, dict) else None
    if not isinstance(features, list):
        raise _unusable("has no list at epic.features")
    tasks = {}
    for f_index, feature in enumerate(features):
        stories = feature.get("stories") if isinstance(feature, dict) else None
        if not isinstance(stories, list):
            raise _unusable("epic.features[%d] has no list of stories" % f_index)
        for s_index, story in enumerate(stories):
            items = story.get("tasks") if isinstance(story, dict) else None
            if not isinstance(items, list):
                raise _unusable("epic.features[%d].stories[%d] has no list of tasks" % (f_index, s_index))
            for t_index, item in enumerate(items):
                where = "epic.features[%d].stories[%d].tasks[%d]" % (f_index, s_index, t_index)
                if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                    raise _unusable("%s is not a task with an id" % where)
                tid, status = item["id"], item.get("status")
                if status not in STATUSES:
                    raise UsageError("backlog.json: task %s has status %r, which is not one of %s. Next: set it "
                                     "to one of them, then run the backlog command again."
                                     % (tid, status, ", ".join(STATUSES)))
                tasks[tid] = (item.get("title"), status)
    spikes = data.get("spikes", [])
    if spikes is None:
        spikes = []
    if not isinstance(spikes, list):
        raise _unusable("has spikes that is not a list")
    for index, spike in enumerate(spikes):
        if not isinstance(spike, dict) or not isinstance(spike.get("id"), str):
            raise _unusable("spikes[%d] is not a spike with an id" % index)
        if spike.get("status") not in STATUSES:
            raise UsageError("backlog.json: spike %s has status %r, which is not one of %s. Next: set it to one of "
                             "them, then run the backlog command again."
                             % (spike["id"], spike.get("status"), ", ".join(STATUSES)))
        tasks[spike["id"]] = (spike.get("title"), spike["status"])
    retired = data.get("retired", [])
    if retired is None:
        retired = []
    if not isinstance(retired, list):
        raise _unusable("has retired that is not a list")
    out = []
    for entry in retired:
        if not isinstance(entry, dict) or entry.get("status") not in STATUSES:
            rid = entry.get("id") if isinstance(entry, dict) else entry
            raise UsageError("backlog.json: retired item %s has an unknown status, not one of %s. Next: set it "
                             "to one of them, then run the backlog command again." % (rid, ", ".join(STATUSES)))
        out.append({"id": entry.get("id"), "title": entry.get("title"), "status": entry["status"]})
    return tasks, out


# --- Facts --------------------------------------------------------------------------------------------

def _value(decision):
    return decision.get("value") if isinstance(decision, dict) else None


def _systems(profile):
    return dict((s.get("id"), s) for s in profile.get("systems") or [] if isinstance(s, dict))


def _kinds_and_products(system_ids, systems):
    kinds, products = [], []
    for sid in system_ids:
        system = systems.get(sid) or {}
        for out, value in ((kinds, system.get("kind")), (products, system.get("product"))):
            if value is not None and value not in out:
                out.append(value)
    return kinds, products


def _system_ids(items):
    out = []
    for item in items:
        if item.get("system") and item["system"] not in out:
            out.append(item["system"])
    return out


def governance_log(profile, persona_codes):
    """True when the plan has a governance log and levelling raised no team-no-governance-log."""
    tier = (profile.get("plan") or {}).get("tier")
    value = "no"
    for cap in _level.load_plan_fit()["capabilities"]:
        if cap["id"] == GOVERNANCE_CAPABILITY:
            value = cap.get(tier, "no")
    return value != "no" and "team-no-governance-log" not in persona_codes


def _codes(levelled, about):
    out = []
    for item in levelled.get("blockers", []) + levelled.get("warnings", []):
        if item["about"] == about and item["code"] not in out:
            out.append(item["code"])
    return out


def persona_facts(card, profile, levelled, systems):
    plan = levelled.get("persona_plan") or {}
    codes = _codes(levelled, "persona")
    tasks = card.get("tasks") or []
    used = _system_ids([i for t in tasks for i in (t.get("inputs") or []) + (t.get("writes") or [])])
    written = _system_ids([w for t in tasks for w in t.get("writes") or []])
    kinds, products = _kinds_and_products(used, systems)
    wkinds, wproducts = _kinds_and_products(written, systems)
    facts = {
        "plan.tier": (profile.get("plan") or {}).get("tier"),
        "role.device": (card.get("role") or {}).get("device"),
        "distribution": _value(plan.get("distribution")),
        "settings_baseline": _value(plan.get("settings_baseline")),
        "governance.log": governance_log(profile, codes),
        "compliance.walls": (profile.get("compliance") or {}).get("walls"),
        "memory.personal_memory_wanted": (card.get("memory") or {}).get("personal_memory_wanted"),
        "systems.kinds": kinds, "systems.products": products,
        "writes.kinds": wkinds, "writes.products": wproducts,
        "codes": codes,
    }
    for name in TASK_FACTS + DECISION_FACTS + ALL_ITEM_FACTS:
        facts[name] = None
    return facts


def task_facts(base, task, decisions, levelled, systems):
    facts = dict(base)
    kinds, products = _kinds_and_products(_system_ids((task.get("inputs") or []) + (task.get("writes") or [])),
                                          systems)
    wkinds, wproducts = _kinds_and_products(_system_ids(task.get("writes") or []), systems)
    autonomy = decisions.get("autonomy") or {}
    controls = decisions.get("data_controls") or {}
    facts.update({
        "systems.kinds": kinds, "systems.products": products,
        "writes.kinds": wkinds, "writes.products": wproducts,
        "codes": _codes(levelled, task.get("id")),
        "task.trigger": task.get("trigger"),
        "task.data_class": task.get("data_class"),
        "task.output.audience": (task.get("output") or {}).get("audience"),
        "task.reversible": task.get("reversible"),
        "task.touches_money": task.get("touches_money"),
        "task.cost_of_mistake.level": (task.get("cost_of_mistake") or {}).get("level"),
        "task.reads_untrusted_input": task.get("reads_untrusted_input"),
        "task.in_pilot": task.get("in_pilot"),
        "task.write_actions": [w.get("action") for w in task.get("writes") or []],
        "runtime": _value(decisions.get("runtime")),
        "identity": _value(decisions.get("identity")),
        "autonomy.start": _value(autonomy.get("start")),
        "autonomy.ceiling": _value(autonomy.get("ceiling")),
        "data_controls.settings_baseline": _value(controls.get("settings_baseline")),
        "data_controls.web_tools": _value(controls.get("web_tools")),
        "data_controls.surfaces": _value(controls.get("surfaces")),
        "data_controls.retention": _value(controls.get("retention")),
        "memory": _value(decisions.get("memory")),
        "plan_fit": _value(decisions.get("plan_fit")),
    })
    writes = _write_tools(levelled, task.get("id"))
    facts.update({
        "delivery.form": _delivery(task, decisions, writes)[0],
        "writes.crm_opens": _crm_opens(writes, systems),
        "tools.write_permissions": [_value(t.get("permission")) for t in writes],
        "tools.send_permissions": [_value(t.get("permission")) for t in writes if t.get("use") == "send"],
    })
    return facts


def _tool_id(tool):
    return "%s-%s" % (tool["system"], tool["use"])


def _write_tools(levelled, tid):
    """The levelled tools other than reads that list the task, in levelled order."""
    return [t for t in levelled.get("tools") or [] if tid in (t.get("tasks") or []) and t.get("use") != "read"]


def _blocked(tool):
    return _value(tool.get("permission")) == "blocked"


def _opens(tool):
    """True when the tool is not Blocked once every task that uses it is at its ceiling."""
    wanted = tool.get("wanted") or {}
    return bool(wanted) and all(value != "blocked" for value in wanted.values())


def _join(items):
    items = list(items)
    if len(items) < 2:
        return "".join(items)
    return "%s and %s" % (", ".join(items[:-1]), items[-1])


def _crm_opens(writes, systems):
    """now, later or never for the task's CRM write tools; None when it has none."""
    crm = [t for t in writes if (systems.get(t["system"]) or {}).get("kind") == "crm"]
    if not crm:
        return None
    if any(not _blocked(t) for t in crm):
        return "now"
    return "later" if any(_opens(t) for t in crm) else "never"


def _opening(tools, tid):
    """When Blocked tools open: 'it opens at level 2', with the other tasks a shared tool waits for."""
    shared = []
    for tool in tools:
        for other in sorted(tool.get("wanted") or {}):
            if other != tid and other not in shared:
                shared.append(other)
    text = "%s at level %d" % ("it opens" if len(tools) == 1 else "they open", OPEN_LEVEL)
    if shared:
        text += ", once every task that uses %s (%s) is there" % (
            "it" if len(tools) == 1 else "them", _join([tid] + shared))
    return text


def _delivery(task, decisions, writes):
    """(form, sentence): how the task's output reaches its destination (design section 8)."""
    tid = task.get("id")
    if not writes:
        return "stays-local", STAYS_LOCAL
    if _value(decisions.get("runtime")) == "claude-tag-routine" and all(
            t["system"] == "slack" and t["use"] == "send" for t in writes):
        return "runtime-posts", ROUTINE_POSTS % _join(_tool_id(t) for t in writes)
    blocked = [t for t in writes if _blocked(t)]
    if blocked:
        opening = [t for t in blocked if _opens(t)]
        closed = [t for t in blocked if not _opens(t)]
        names = _join(_tool_id(t) for t in blocked)
        verb = "is" if len(blocked) == 1 else "are"
        lead = "A person sends or files it: the twin produces a draft, %s %s Blocked at the starting level" % (
            names, verb)
        if not closed:
            return "person-sends", "%s, and %s." % (lead, _opening(opening, tid))
        if not opening:
            return "person-sends", "%s, and %s not planned at any level." % (
                lead, "it is" if len(blocked) == 1 else "they are")
        return "person-sends", "%s; %s at level %d and %s not planned at any level." % (
            lead, _join(_tool_id(t) for t in opening), "opens" if len(opening) == 1 else "open", OPEN_LEVEL,
            "%s is" % _join(_tool_id(t) for t in closed) if len(closed) == 1 else
            "%s are" % _join(_tool_id(t) for t in closed))
    return "twin-writes", "The twin writes it with %s %s." % (
        "tool" if len(writes) == 1 else "tools",
        _join("%s (%s)" % (_tool_id(t), PERMISSION_NAMES.get(_value(t.get("permission")), "undecided"))
              for t in writes))


def _decision(decisions, name):
    if name.startswith("autonomy."):
        return (decisions.get("autonomy") or {}).get(name.split(".", 1)[1])
    if name.startswith("data_controls."):
        return (decisions.get("data_controls") or {}).get(name.split(".", 1)[1])
    return decisions.get(name)


def _items(per, tid, decisions, levelled, systems):
    """[(item key, item facts)] for a per-item template on one task."""
    out = []
    if per == "connector":
        for entry in decisions.get("connectors") or []:
            system = systems.get(entry.get("system")) or {}
            out.append((entry.get("system"), {
                "connector.system": entry.get("system"), "connector.kind": system.get("kind"),
                "connector.product": system.get("product"), "connector.access": entry.get("access"),
                "connector.permission": entry.get("permission"), "connector.runbook": entry.get("runbook"),
                "connector.unverified": bool(entry.get("unverified"))}))
    elif per == "tool":
        for tool in levelled.get("tools") or []:
            if tid in (tool.get("tasks") or []):
                out.append(("%s-%s" % (tool["system"], tool["use"]), {
                    "tool.system": tool["system"], "tool.use": tool["use"],
                    "tool.permission": _value(tool.get("permission"))}))
    elif per == "unverified-decision":
        for name in _level.DECISION_FACTS:
            decision = _decision(decisions, name)
            if isinstance(decision, dict) and decision.get("unverified"):
                out.append((name, {"decision.name": name}))
        for entry in decisions.get("connectors") or []:
            if entry.get("unverified"):
                name = "connectors.%s" % entry.get("system")
                out.append((name, {"decision.name": name}))
    return out


# --- Stories -------------------------------------------------------------------------------------------

def _num(value):
    if value is None:
        return "unknown"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _show(value):
    if value is None:
        return "undecided"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, list):
        return ", ".join(_show(v) for v in value) or "none"
    return str(value)


def _lower_first(text):
    return text[:1].lower() + text[1:] if text else text


def _story_fields(task, decisions, profile, delivery):
    autonomy = decisions.get("autonomy") or {}
    controls = decisions.get("data_controls") or {}
    output = task.get("output") or {}
    connectors = "; ".join("%s: %s identity, %s, %s" % (c.get("system"), _show(c.get("identity")), c.get("access"),
                                                        _show(c.get("permission")))
                           for c in decisions.get("connectors") or []) or "none"
    inputs = "; ".join("%s (%s)" % (i.get("system"), i.get("objects")) for i in task.get("inputs") or []) or "none"
    fields = {
        "data_class": task.get("data_class"),
        "surface": "%s; surfaces: %s" % (_show(_value(decisions.get("runtime"))),
                                         _show(_value(controls.get("surfaces")))),
        "autonomy": "%s to %s" % (_show(_value(autonomy.get("start"))), _show(_value(autonomy.get("ceiling")))),
        "connectors_and_identity": connectors,
        "wall_impact": _show((profile.get("compliance") or {}).get("walls")),
        "inputs": inputs,
        "output_and_audience": "%s, %s; to %s" % (output.get("what"), output.get("audience"),
                                                  output.get("destination")),
        "delivery": delivery,
        "skill_owner": task.get("skill_owner") or "not named yet",
        "baseline": "%s per week x %s minutes each x %s users" % (
            _num(task.get("frequency_per_week")), _num(task.get("minutes_each")), _num(task.get("users"))),
    }
    # From the interviews, only when the card holds them; neither changes levelling (design section 8).
    constraints = _constraints(task)
    if constraints:
        fields["constraints"] = constraints
    if _text(task.get("wanted_change")):
        fields["wanted_change"] = WANTED_CHANGE_LABEL + _text(task.get("wanted_change"))
    return fields


def _text(value):
    return value.strip() if isinstance(value, str) else ""


def _constraints(task):
    """The task's business rules and deadlines from the interviews, as the card holds them, empty ones dropped."""
    items = task.get("constraints")
    return [item for item in items if _text(item)] if isinstance(items, list) else []


def _acceptance(task, facts):
    examples = task.get("examples") or {}
    good, bad = examples.get("good"), examples.get("bad")
    where = " (%s)" % examples["where"] if examples.get("where") else ""
    lines = []
    for count, kind, result in ((good, "good", "the twin's output matches what a person accepted"),
                                (bad, "bad", "the twin does not repeat the mistake")):
        if isinstance(count, int) and not isinstance(count, bool) and count > 0:
            lines += ["Eval from %s example %d of %d%s: %s." % (kind, i, count, where, result)
                      for i in range(1, count + 1)]
    if not lines:
        lines = [TO_WRITE % (_text(task.get("skill_owner")) or UNNAMED_SKILL_OWNER)]
    lines += ["Keeps: %s" % item for item in _constraints(task)]
    if facts["runtime"] == "client-skill":
        lines.append(ACCEPT_TRIGGER)
    if facts["data_controls.web_tools"] == "off":
        lines.append("Plus: no web tools are used.")
    if facts["writes.crm_opens"] == "now":
        lines.append(ACCEPT_MARKER)
    elif facts["writes.crm_opens"] in ("later", "never"):
        lines.append(ACCEPT_NO_CRM_WRITE)
    if facts["governance.log"]:
        lines.append("Plus: each tool call reaches the governance log.")
    return lines


def _gates(blockers, questions):
    out = [{"kind": "blocker", "id": b["code"], "text": b["message"]} for b in blockers]
    out += [{"kind": "open-question", "id": q.get("id"), "text": q.get("question"), "spike": _spike_id(q)}
            for q in questions]
    return out


def _clause(value):
    """A card sentence part as the statement uses it: trimmed, one trailing full stop dropped, case kept."""
    text = " ".join(_text(value).split())
    return text[:-1].rstrip() if text.endswith(".") else text


def _statement(task, role):
    """(statement, statement_source): the card's story_want and story_benefit, or the kit's fallbacks."""
    want, benefit = _clause(task.get("story_want")), _clause(task.get("story_benefit"))
    source = "card" if want and benefit else "drafted"
    if not want:
        what = _clause((task.get("output") or {}).get("what"))
        want = "produce the %s" % _lower_first(what) if what else 'do the task "%s"' % _clause(task.get("name"))
    if not benefit:
        minutes = task.get("minutes_each")
        if isinstance(minutes, (int, float)) and not isinstance(minutes, bool):
            benefit = "I get back the %s minutes it takes me each time" % _num(minutes)
        else:
            benefit = "I do not have to do it by hand"
    return STATEMENT % (_lower_first(role), want, benefit), source


def _target(task, card):
    """The story's target line from outcome.scorecard_targets; it invents no number."""
    targets = [t for t in (card.get("outcome") or {}).get("scorecard_targets") or []
               if isinstance(t, dict) and _text(t.get("metric")) and isinstance(t.get("value"), (int, float))
               and not isinstance(t.get("value"), bool)]
    if not targets:
        return {"text": TARGET_NOT_SET, "set": False}
    return {"text": "Target: %s. Today: %s per week, %s minutes each, %s users." % (
        "; ".join("%s: %s" % (_text(t["metric"]), _num(t["value"])) for t in targets),
        _num(task.get("frequency_per_week")), _num(task.get("minutes_each")), _num(task.get("users"))),
        "set": True}


def _undecided(value):
    return value is None or value == _level.UNDECIDED


def _count(value):
    return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else 0


def _ready(task, decisions, blockers, systems):
    """The definition-of-ready checks the card and the plan can answer; the sign-off check is added later."""
    autonomy = decisions.get("autonomy") or {}
    undecided = [name for name, missing in (
        ("data class", not _text(task.get("data_class"))),
        ("surface", _undecided(_value(decisions.get("runtime")))),
        ("autonomy", _undecided(_value(autonomy.get("start"))) or _undecided(_value(autonomy.get("ceiling")))),
        ("identity", _undecided(_value(decisions.get("identity"))))) if missing]
    examples = task.get("examples") or {}
    good, bad = _count(examples.get("good")), _count(examples.get("bad"))
    used = _system_ids((task.get("inputs") or []) + (task.get("writes") or []))
    entries = dict((c.get("system"), c) for c in decisions.get("connectors") or [])
    failing = []
    for sid in used:
        entry = entries.get(sid)
        names = [n.lower() for n in (sid, (systems.get(sid) or {}).get("product")) if n]
        named_by = [b["code"] for b in blockers
                    if any(n in ("%s %s" % (b.get("message") or "", b.get("fix") or "")).lower() for n in names)]
        if entry is None:
            failing.append("%s has no connector decided" % sid)
        elif _undecided(entry.get("identity")) or _undecided(entry.get("permission")):
            failing.append("%s has its identity or permission undecided" % sid)
        elif named_by:
            failing.append("%s is named by blocker %s" % (sid, _join(named_by)))
    return [
        {"check": "fields", "met": not undecided,
         "note": "Not decided yet: %s." % _join(undecided) if undecided else
                 "Data class, surface, autonomy and identity are decided."},
        {"check": "examples", "met": good + bad >= EXAMPLES_NEEDED,
         "note": "%d counted example%s (%d good, %d bad); at least %d needed." % (
             good + bad, "" if good + bad == 1 else "s", good, bad, EXAMPLES_NEEDED)},
        {"check": "connectors", "met": not failing,
         "note": "; ".join(failing) + "." if failing else
                 ("Every system the task uses has a decided connector: %s." % _join(used) if used else
                  "The task reads and writes no system.")},
    ]


def _sign_offs(features, card):
    """After statuses are kept: the compliance sign-off check and gate on stories above confidential."""
    classes = dict((t.get("id"), t.get("data_class")) for t in card.get("tasks") or [])
    for feature in features:
        for story in feature["stories"]:
            if "ready" not in story or classes.get(story["id"][2:]) not in SIGN_OFF_CLASSES:
                continue
            tid = "%s.%s" % (story["id"], SIGN_OFF_TEMPLATE)
            item = next((t for t in story["tasks"] if t["id"] == tid), None)
            done = item is not None and item["status"] == "done"
            story["ready"].append({"check": SIGN_OFF_CHECK, "met": done,
                                   "note": "%s is done." % tid if done else
                                           "Waiting for %s: compliance signs the story off before it is built."
                                           % tid})
            if not done:
                story["gated_by"].append({"kind": "sign-off", "id": "compliance",
                                          "text": "Compliance has not signed the story off yet (%s)." % tid})


def _spike_id(question):
    return "SP-%s" % question.get("id")


def _spike_title(question):
    """The question cut at its first sentence end, at most 120 characters."""
    text = " ".join(str(question or "").split())
    end = re.search(r"[.?!](?=\s|$)", text)
    if end:
        text = text[:end.end()]
    if len(text) > SPIKE_TITLE_MAX:
        cut = text[:SPIKE_TITLE_MAX - 1]
        if " " in cut:
            cut = cut[:cut.rfind(" ")]
        text = cut.rstrip(" ,;:") + "\u2026"
    return text


def _spikes(questions):
    """One spike per open question on the card, in card order."""
    return [{"id": _spike_id(q), "kind": "spike", "title": _spike_title(q.get("question")),
             "question": q.get("question"), "blocks": ["S-%s" % t for t in q.get("blocks") or []],
             "owner": q.get("owner"), "due": q.get("due"), "status": "todo"} for q in questions]


def _link(link, item):
    """A library link with the connector-runbook placeholder filled in from the item's facts."""
    if link and link.startswith(RUNBOOK_PLACEHOLDER):
        return (item or {}).get("connector.runbook") + link[len(RUNBOOK_PLACEHOLDER):]
    return link


def _confirm_part(name):
    for prefix, part in DECISION_PARTS:
        if name == prefix or (prefix.endswith(".") and name.startswith(prefix)):
            return part
    return None


def _task(story_id, template, key, item=None):
    part = template["part"]
    if template["id"] == CONFIRM_TEMPLATE and key:
        part = _confirm_part(key) or part
    return {"id": "%s.%s" % (story_id, template["id"]) + (".%s" % key if key else ""),
            "template": template["id"],
            "title": template["title"] + (" (%s)" % key if key else ""),
            "part": part,
            "how": [{"text": step["text"], "link": _link(step["link"], item)} for step in template["how"]],
            "done_when": template["done_when"],
            "owner_role": template["owner_role"],
            "owner_name": None,
            "acting_owner": None,
            "status": "todo"}


def _applies(template, story_id):
    applies = template["applies_to"]
    if story_id is None:
        return applies == TASK_STORY
    if applies == story_id:
        return True
    # A persona-level code whose template serves task stories lands in one foundation story.
    return (story_id == PERSONA_CODE_STORY and applies == TASK_STORY and template["per"] is None
            and _level.fact_names(template["when"]) == ["codes"])


def _tasks_for(story_id, facts, library, foundation, tid=None, decisions=None, levelled=None, systems=None):
    """The tasks the library's templates give one story, in library order."""
    known = set(facts)
    out = []
    for template in library["templates"]:
        if not _applies(template, story_id if foundation else None):
            continue
        if template["per"] is None:
            if _level.matches(template["when"], facts, known):
                out.append(_task(story_id, template, None))
            continue
        for key, item in _items(template["per"], tid, decisions, levelled, systems):
            merged = dict(facts)
            merged.update(item)
            if _level.matches(template["when"], merged, known):
                out.append(_task(story_id, template, key, item))
    return out


def derive_status(statuses):
    """done when every status is done, todo when every one is todo, otherwise in-progress."""
    statuses = list(statuses)
    if statuses and all(s == "done" for s in statuses):
        return "done"
    if all(s == "todo" for s in statuses):
        return "todo"
    return "in-progress"


# --- Building ------------------------------------------------------------------------------------------

def _result(ok, validation, error=None, backlog=None, retired_now=None):
    return {"ok": ok, "validation": validation, "error": error, "backlog": backlog, "retired_now": retired_now or []}


def _task_story(task, role, base, card, profile, levelled, systems, questions, persona_blockers, library):
    tid = task.get("id")
    decisions = (levelled.get("tasks") or {}).get(tid) or {}
    facts = task_facts(base, task, decisions, levelled, systems)
    story_id = "S-" + tid
    writes = _write_tools(levelled, tid)
    blockers = persona_blockers + [b for b in levelled.get("blockers", []) if b["about"] == tid]
    statement, source = _statement(task, role)
    part = "A2" if facts["runtime"] == "client-skill" else "A4"
    tasks = _with_engine_steps(
        _with_constraints(_tasks_for(story_id, facts, library, False, tid, decisions, levelled, systems),
                          _constraints(task)),
        task, facts, decisions, writes, systems)
    for item in tasks:
        if item["template"] == OWNER_HANDOVER:
            item["part"] = part
    return {
        "id": story_id,
        "title": task.get("name"),
        "statement": statement,
        "statement_source": source,
        "part": part,
        "in_pilot": bool(task.get("in_pilot")),
        "priority": task.get("priority"),
        "status": "todo",
        "fields": _story_fields(task, decisions, profile, _delivery(task, decisions, writes)[1]),
        "acceptance": _acceptance(task, facts),
        "target": _target(task, card),
        "ready": _ready(task, decisions, blockers, systems),
        "gated_by": _gates(blockers, [q for q in questions if tid in (q.get("blocks") or [])]),
        "tasks": tasks,
    }


def _with_engine_steps(tasks, task, facts, decisions, writes, systems):
    """Steps the engine adds from the card and the plan (design section 8): the twin marker before a CRM
    write opens, who files a draft and how, and Salesforce's allowlist discovery for a private Salesforce."""
    runbooks = dict((c.get("system"), c.get("runbook")) for c in decisions.get("connectors") or [])
    for item in tasks:
        if item["template"].startswith("twin-marker-") and facts["writes.crm_opens"] == "later":
            crm = [t for t in writes if (systems.get(t["system"]) or {}).get("kind") == "crm" and _opens(t)]
            names = _join(_tool_id(t) for t in crm)
            item["how"].insert(0, {"text": MARKER_STEP % (
                ("tool %s is" if len(crm) == 1 else "tools %s are") % names,
                "opens" if len(crm) == 1 else "open", OPEN_LEVEL), "link": MOVING_UP})
        elif item["template"] == DELIVER_DRAFT:
            blocked = [t for t in writes if _blocked(t)]
            link = next((runbooks[t["system"]] for t in blocked if runbooks.get(t["system"])), None)
            item["how"].append({"text": DELIVER_STEP % ((task.get("output") or {}).get("destination") or
                                                        "the card's destination"),
                                "link": link or CONNECTORS_PAGE})
        elif item["template"] == PRIVATE_NETWORK_TEMPLATE:
            if any(runbooks.get(sid) == SALESFORCE_RUNBOOK and (systems.get(sid) or {}).get("private_network")
                   for sid in runbooks):
                item["how"].append({"text": SALESFORCE_E6_STEP, "link": SALESFORCE_E6})
    return tasks


def _with_constraints(tasks, constraints):
    """The write-skill task gains one step that lists the task's constraints as rules the skill must keep."""
    if constraints:
        for item in tasks:
            if item["template"] == WRITE_SKILL:
                item["how"].append({"text": CONSTRAINTS_STEP % "; ".join(constraints), "link": CONSTRAINTS_LINK})
    return tasks


def _foundation_stories(role, base, levelled, persona_blockers, library):
    plan = levelled.get("persona_plan") or {}
    fields = {
        "plan": _show(base["plan.tier"]),
        "device": _show(base["role.device"]),
        "plugin_name": _show(_value(plan.get("plugin_name"))),
        "distribution": _show(base["distribution"]),
        "settings_baseline": _show(base["settings_baseline"]),
        "governance_log": _show(base["governance.log"]),
    }
    out = []
    for story_id, title, part in FOUNDATION:
        out.append({
            "id": story_id, "title": title,
            "statement": "As a %s, I want my twin's %s in place so that every task story runs safely." % (
                role, title.lower()),
            "part": part, "in_pilot": True, "priority": None, "status": "todo",
            "fields": dict(fields),
            "acceptance": list(FOUNDATION_ACCEPTANCE[story_id]),
            "gated_by": _gates(persona_blockers, []),
            "tasks": _tasks_for(story_id, base, library, True),
        })
    return out


def _apply_statuses(features, old_tasks, old_retired, spikes=()):
    """Keep each task's and spike's status from the last run, derive the parents', and retire started items
    no longer made."""
    retired_by_id = dict((r["id"], r) for r in old_retired)
    generated = set()
    for spike in spikes:
        generated.add(spike["id"])
        if spike["id"] in old_tasks:
            spike["status"] = old_tasks[spike["id"]][1]
        elif spike["id"] in retired_by_id:
            spike["status"] = retired_by_id[spike["id"]]["status"]
    for feature in features:
        for story in feature["stories"]:
            for item in story["tasks"]:
                generated.add(item["id"])
                if item["id"] in old_tasks:
                    item["status"] = old_tasks[item["id"]][1]
                elif item["id"] in retired_by_id:
                    item["status"] = retired_by_id[item["id"]]["status"]
            story["status"] = derive_status(t["status"] for t in story["tasks"])
        feature["status"] = derive_status(s["status"] for s in feature["stories"])
    retired = [r for r in old_retired if r["id"] not in generated]
    kept = set(r["id"] for r in retired)
    retired_now = []
    for tid, (title, status) in old_tasks.items():
        if tid not in generated and tid not in kept and status != "todo":
            entry = {"id": tid, "title": title, "status": status}
            retired.append(entry)
            retired_now.append(entry)
    return retired, retired_now


def build(persona_dir, library=None):
    """Build the backlog for the persona in persona_dir. Never writes. See the module docstring."""
    validation = _validate.validate(str(persona_dir), _fields.load_catalogue())
    if not validation["ok"]:
        return _result(False, validation, "card.json or customer-profile.json has validation errors. "
                                          "Next: fix them, then run level and backlog again.")
    read = _read_levelled(persona_dir)
    if read is None:
        return _result(False, validation, STALE)
    card, profile, levelled = read
    return assemble(persona_dir, validation, card, profile, levelled, library)


def assemble(persona_dir, validation, card, profile, levelled, library=None):
    """Build the backlog from parsed records known to be current; statuses come from backlog.json."""
    library = library if library is not None else load_library()
    old_tasks, old_retired = read_statuses(persona_dir)
    systems = _systems(profile)
    base = persona_facts(card, profile, levelled, systems)
    persona_blockers = [b for b in levelled.get("blockers", []) if b["about"] == "persona"]
    questions = card.get("open_questions") or []
    tasks = card.get("tasks") or []
    order = dict((t.get("id"), i) for i, t in enumerate(tasks))
    role = (card.get("role") or {}).get("name") or card.get("id")

    features = []
    for feature in card.get("features") or []:
        stories = [_task_story(task, role, base, card, profile, levelled, systems, questions, persona_blockers,
                               library) for task in tasks if task.get("feature") == feature.get("id")]
        stories.sort(key=lambda s: (not s["in_pilot"],
                                    s["priority"] if isinstance(s["priority"], (int, float)) else float("inf"),
                                    order.get(s["id"][2:], 0)))
        features.append({"id": "F-" + feature.get("id"), "title": feature.get("name"), "kind": "capability",
                         "status": "todo", "stories": stories})
    features.append({"id": FOUNDATION_FEATURE[0], "title": FOUNDATION_FEATURE[1], "kind": "foundation",
                     "status": "todo", "stories": _foundation_stories(role, base, levelled, persona_blockers,
                                                                      library)})
    spikes = _spikes(questions)
    retired, retired_now = _apply_statuses(features, old_tasks, old_retired, spikes)
    _sign_offs(features, card)
    unnamed = _name_owners(features, card, profile, library)

    display = profile.get("display_name") or card.get("customer")
    backlog = {
        "backlog_version": BACKLOG_VERSION,
        "customer": card.get("customer"),
        "persona": card.get("id"),
        "source": {"card_sha256": levelled["source"]["card_sha256"], "levelled_sha256": _sha(_level.render(levelled).encode("utf-8")),
                   "library_version": library["library_version"]},
        "unnamed_roles": unnamed,
        "epic": {"id": "E", "title": "%s twin for %s" % (role, display),
                 "status": derive_status(f["status"] for f in features), "features": features},
        "spikes": spikes,
        "retired": retired,
    }
    return _result(True, validation, None, backlog, retired_now)


def _name_owners(features, card, profile, library):
    """Set each task's owner_name and acting_owner; return the customer roles with no named person.

    A role the profile names (or, for skill-owner, the card task's skill_owner) gets that name. A customer
    role with no name gets the technical owner as its acting owner; the partner's roles get neither.
    """
    owners = profile.get("owners") or {}
    technical = _text(owners.get("technical_owner")) or None
    skill_owners = dict((t.get("id"), _text(t.get("skill_owner"))) for t in card.get("tasks") or [])
    counts_by_role = {}
    for feature in features:
        for story in feature["stories"]:
            tid = story["id"][2:]
            for item in story["tasks"]:
                role = item["owner_role"]
                if role in PROFILE_OWNERS:
                    name = _text(owners.get(PROFILE_OWNERS[role])) or None
                elif role == SKILL_OWNER:
                    name = skill_owners.get(tid) or None
                else:
                    name = None
                item["owner_name"] = name
                item["acting_owner"] = technical if name is None and role not in PARTNER_ROLES else None
                if name is None and role not in PARTNER_ROLES:
                    counts_by_role[role] = counts_by_role.get(role, 0) + 1
    return [{"role": role, "tasks": counts_by_role[role], "acting_owner": technical}
            for role in library["owner_roles"] if role in counts_by_role]


def has_blocker(persona_dir):
    """True when levelled.json reports a blocker."""
    path = Path(persona_dir) / _level.LEVELLED_FILE
    return bool(json.loads(path.read_text(encoding="utf-8")).get("blockers"))


# --- Rendering -----------------------------------------------------------------------------------------

def render_json(backlog):
    """backlog.json's text: keys in a fixed order, two-space indent, UTF-8, a trailing newline."""
    return json.dumps(backlog, indent=2, ensure_ascii=False) + "\n"


def command_path(backlog, persona_dir=None):
    """The persona folder as the command takes it: engagements/<engagement>/personas/<persona>."""
    if persona_dir is not None:
        persona = Path(persona_dir).resolve()
        return "engagements/%s/personas/%s" % (persona.parent.parent.name, persona.name)
    for profile in sorted((REPO_ROOT / "engagements").glob("*/customer-profile.json")):
        try:
            customer = json.loads(profile.read_text(encoding="utf-8")).get("customer")
        except ValueError:
            continue
        if customer == backlog["customer"] and (profile.parent / "personas" / backlog["persona"]).is_dir():
            return "engagements/%s/personas/%s" % (profile.parent.name, backlog["persona"])
    return "engagements/%s/personas/%s" % (backlog["customer"], backlog["persona"])


def counts(backlog):
    """(features, stories, tasks) in the backlog."""
    stories = [s for f in backlog["epic"]["features"] for s in f["stories"]]
    return len(backlog["epic"]["features"]), len(stories), sum(len(s["tasks"]) for s in stories)


_MD_LEAD = re.compile(r"^(?:[#>+\-*=_`~|]|\d+[.)])")


def _md(text, lead=False):
    """A value as backlog.md writes it: one line, '<' as &lt;, and (lead) no block marker at its start.

    Whitespace runs (CR and LF included) become one space and the ends are trimmed. With lead, the
    value starts a line or follows a list marker, so a leading heading, list, quote, fence or table
    character is backslash-escaped. backlog.json and the plan tree keep the raw values.
    """
    out = " ".join(str(text).split()).replace("<", "&lt;")
    if lead:
        match = _MD_LEAD.match(out)
        if match:
            mark = match.group(0)
            out = mark[:-1] + "\\" + mark[-1] + out[len(mark):]
    return out


def _cell(text):
    """A table cell: _md, with '|' as '/'."""
    return _md(text).replace("|", "/")


def _owner(item):
    """The task's owner as backlog.md and the plan tree print it: the role, then the name or the acting owner."""
    if item.get("owner_name"):
        return "%s, %s" % (item["owner_role"], item["owner_name"])
    if item.get("acting_owner"):
        return "%s, acting: %s" % (item["owner_role"], item["acting_owner"])
    return item["owner_role"]


def _unnamed_line(backlog):
    roles = backlog.get("unnamed_roles") or []
    if not roles:
        return "Roles with no named person: none."
    return "Roles with no named person: %s." % "; ".join(
        "%s, %d task%s, %s" % (r["role"], r["tasks"], "" if r["tasks"] == 1 else "s",
                              "acting owner %s" % r["acting_owner"] if r["acting_owner"] else "no acting owner")
        for r in roles)


def _is_ready(story):
    return all(c["met"] for c in story["ready"])


def _task_stories(backlog):
    return [s for f in backlog["epic"]["features"] for s in f["stories"] if "ready" in s]


def _md_spikes(spikes):
    if not spikes:
        return []
    lines = ["", "## Spikes", "", "Open questions on the card. A spike is time-boxed research that answers one; "
             "it holds no build work. Mark a spike by changing its status in backlog.json.", ""]
    for spike in spikes:
        lines.append("- %s **%s** %s (owner: %s; due: %s; blocks: %s)" % (
            MARKS[spike["status"]], _md(spike["id"]), _md(spike["question"]),
            _md(spike["owner"]) if _text(spike.get("owner")) else "not named yet",
            _md(spike["due"]) if _text(spike.get("due")) else "not set",
            _md(", ".join(spike["blocks"])) if spike["blocks"] else "no story"))
    return lines


def _md_story(story):
    lines = ["", "### %s: %s" % (_md(story["id"]), _md(story["title"])), "", _md(story["statement"], lead=True), ""]
    if story.get("statement_source") == "drafted":
        lines += [DRAFTED_NOTE, ""]
    lines += ["Part %s. In pilot: %s. Priority: %s. Status: %s." % (
                 _md(story["part"]), "yes" if story["in_pilot"] else "no",
                 _md(story["priority"]) if story["priority"] is not None else "none", _md(story["status"])),
             "", "| Field | Value |", "|---|---|"]
    for key, value in story["fields"].items():
        value = "; ".join(value) if isinstance(value, list) else value
        lines.append("| %s | %s |" % (key.replace("_", " ").capitalize(), _cell(value)))
    lines += ["", "**Acceptance criteria:**", ""]
    lines += ["%d. %s" % (i, _md(text, lead=True)) for i, text in enumerate(story["acceptance"], 1)]
    if "target" in story:
        lines += ["", _md(story["target"]["text"], lead=True)]
    if "ready" in story:
        lines += ["", "Ready to build: %s" % ("yes" if _is_ready(story) else "no")]
        lines += ["- %s: %s" % (_md(c["check"], lead=True), _md(c["note"])) for c in story["ready"] if not c["met"]]
    lines += ["", "**Gated by:**", ""]
    lines += ["- %s %s: %s%s" % (_md(g["kind"], lead=True), _md(g["id"]), _md(g["text"]),
                                 " (spike %s)" % _md(g["spike"]) if g.get("spike") else "")
              for g in story["gated_by"]] or ["- Nothing."]
    lines += ["", "**Tasks:**", ""]
    for item in story["tasks"]:
        lines.append("- %s **%s** %s (owner: %s, part %s)" % (
            MARKS[item["status"]], _md(item["id"]), _md(item["title"]), _md(_owner(item)), _md(item["part"])))
        for i, step in enumerate(item["how"], 1):
            text = _md(step["text"], lead=True)
            if step["link"]:
                text += " See [%s](%s%s)." % (_md(step["link"]), MD_LINK_PREFIX, _md(step["link"]))
            lines.append("  %d. %s" % (i, text))
        lines.append("  - Done when: %s" % _md(item["done_when"]))
    return lines


def render_md(backlog, persona_dir=None):
    """backlog.md's text, generated from the backlog; links are relative to the persona folder."""
    epic = backlog["epic"]
    n_features, n_stories, n_tasks = counts(backlog)
    lines = [
        "# " + _md(epic["title"]),
        "",
        "Generated from card.json and levelled.json by `python3 %s backlog %s`; never edit it by hand. To mark a "
        "task, change only its status in backlog.json, then run the command again." % (
            CLI_PATH, _md(command_path(backlog, persona_dir))),
        "",
        "Status: %s. %d features, %d stories, %d tasks. Task marks: `[ ]` todo, `[~]` in progress, `[x]` done."
        % (_md(epic["status"]), n_features, n_stories, n_tasks),
        "",
        _md(_unnamed_line(backlog), lead=True),
    ]
    told = _task_stories(backlog)
    lines += ["", "Stories ready to build: %d of %d." % (sum(1 for s in told if _is_ready(s)), len(told))]
    no_target = sum(1 for s in told if not s["target"]["set"])
    if no_target:
        lines += ["", "Stories with no target: %d. Agree the scorecard targets with the sponsor." % no_target]
    for feature in epic["features"]:
        lines += ["", "## %s: %s" % (_md(feature["id"]), _md(feature["title"])), "",
                  "Kind: %s. Status: %s. %d stories." % (_md(feature["kind"]), _md(feature["status"]),
                                                         len(feature["stories"]))]
        for story in feature["stories"]:
            lines += _md_story(story)
    lines += _md_spikes(backlog.get("spikes") or [])
    lines += ["", "## Retired", ""]
    if backlog["retired"]:
        lines += ["Items no longer generated from the card that had been started or finished:", ""]
        lines += ["- %s **%s** %s (%s)" % (MARKS[r["status"]], _md(r["id"]), _md(r["title"]), _md(r["status"]))
                  for r in backlog["retired"]]
    else:
        lines.append("Nothing retired.")
    return "\n".join(lines) + "\n"


def plan_tree(backlog):
    """The tree_import shape {"version": 1, "items": [epic]}; notes hold the ids, and for a task its steps."""
    def node(kind, title, note, children):
        return {"type": kind, "title": title, "note": note, "children": children}

    def task_note(item):
        steps = ["%d. %s%s" % (i, s["text"], " (%s)" % s["link"] if s["link"] else "")
                 for i, s in enumerate(item["how"], 1)]
        return "\n".join([item["id"], "Owner: %s. Part %s. Status: %s." % (
            _owner(item), item["part"], item["status"])] + steps + ["Done when: " + item["done_when"]])

    epic = backlog["epic"]
    features = []
    for feature in epic["features"]:
        stories = []
        for story in feature["stories"]:
            gates = ["Gated by %s %s." % (g["kind"], g["id"]) for g in story["gated_by"]]
            stories.append(node("story", story["title"], "\n".join([story["id"], story["statement"]] + gates),
                                [node("task", item["title"], task_note(item), []) for item in story["tasks"]]))
        features.append(node("feature", feature["title"], feature["id"], stories))
    return {"version": 1, "items": [node("epic", epic["title"], "E\nStatus: %s." % epic["status"], features)]}


def write_backlog(persona_dir, library=None):
    """Build and write backlog.json and backlog.md; nothing is written when the build fails."""
    result = build(persona_dir, library)
    if result["ok"]:
        persona = Path(persona_dir)
        (persona / BACKLOG_JSON).write_bytes(render_json(result["backlog"]).encode("utf-8"))
        (persona / BACKLOG_MD).write_bytes(render_md(result["backlog"], persona_dir).encode("utf-8"))
    return result
