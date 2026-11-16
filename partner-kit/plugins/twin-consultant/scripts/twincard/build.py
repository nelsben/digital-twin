"""Build: scaffold each task's skill and runtime wrapper under <persona-dir>/build/ (design section 8a).

build reads card.json and levelled.json, which must be current (the same test backlog uses) and
report no blocker. It never re-decides a runtime: each artifact records levelled.json's runtime with
its rule and cite, and data/build-kinds.json says what that runtime is built as. The files start
from the starter-kit templates copied into templates/build/; build fills only what the records state,
names the field each seeded line came from, and keeps every FILL IN a person must decide.

build never overwrites a person's edits: a file whose hash is not the one build recorded is kept and
listed on stderr. build.json, the manifest, has no timestamp, so the same inputs give the same bytes.

check runs deterministic checks on each built artifact and writes nothing. record moves one artifact
one status at a time, never backwards, and only from drafted to evals-passing: check must pass and
the evidence must be skill-creator's benchmark.json or `claude plugin eval`'s JSON result under
build/evidence/<task id>/, with a without-skill baseline. It appends to the artifact's history, which
build keeps. Never write or invent an eval result. Standard library only.
"""

import copy
import hashlib
import json
import re
from pathlib import Path

from twincard import backlog as _backlog
from twincard import fields as _fields
from twincard import level as _level
from twincard import validate as _validate

PLUGIN_DIR = _level.PLUGIN_DIR
KINDS_FILE = _level.DATA_DIR / "build-kinds.json"
TEMPLATE_DIR = PLUGIN_DIR / "templates" / "build"
BUILD_DIR = "build"
MANIFEST = "build.json"
BUILD_VERSION = 1
FILL_IN = "FILL IN"
STATUSES = ("scaffolded", "drafted", "evals-passing", "packaged", "deployed", "verified", "not-built")
RECORDED_ONLY = ("evals-passing", "packaged", "deployed", "verified")
KIND_KEYS = ("runtime", "kind", "what", "runbook", "skill_location", "skill_location_basis", "wrapper", "inputs",
             "scaffolds", "reason")
WRAPPERS = (None, "scheduled", "routine", "agent", "sdk")
LOCATIONS = (None, "plugin", "skills")
SKILL_FILES = ("SKILL.md", "evals/evals.json", "evals/trigger-evals.json", "references/example-reference.md")
NAME_MAX = _validate.SKILL_NAME_MAX
KINDS_NEXT = ("restore data/build-kinds.json in the twin-consultant plugin (undo the edit, or reinstall the plugin), "
              "then run the build command again")
MANIFEST_NEXT = "Next: fix build/build.json or delete it, then run the build command again."
VALIDATION_ERROR = ("card.json or customer-profile.json has validation errors. "
                    "Next: fix them, then run level and build again.")
TO_REPO = "../../../../"  # from a persona folder to the repository root
NO_FILE_ROW = "| FILL IN a file the user attaches | FILL IN | FILL IN | read |"


class BuildError(ValueError):
    """data/build-kinds.json or a template the build reads is missing or not in its shape (exit 2)."""


class UsageError(ValueError):
    """build/build.json is not JSON, not in its shape, or gives an unknown status (exit 2)."""


# --- Kit data ------------------------------------------------------------------------------------------

def load_kinds(path=None):
    """build-kinds.json, checked: one entry per runtime in the catalogue's override vocabulary."""
    path = Path(path) if path is not None else KINDS_FILE
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise BuildError("data/build-kinds.json cannot be read as JSON (%s). Next: %s" % (exc, KINDS_NEXT))
    runtimes = _fields.load_catalogue()["override_values"]["runtime"]["values"]
    if not isinstance(data, dict) or data.get("build_kinds_version") != 1 or not isinstance(data.get("kinds"), list):
        raise BuildError("data/build-kinds.json is not in its shape: it needs build_kinds_version 1 and a kinds "
                         "list. Next: %s" % KINDS_NEXT)
    seen = {}
    for entry in data["kinds"]:
        if not isinstance(entry, dict) or tuple(entry) != KIND_KEYS:
            raise BuildError("data/build-kinds.json has an entry whose keys are not %s. Next: %s"
                             % (", ".join(KIND_KEYS), KINDS_NEXT))
        if entry["runtime"] not in runtimes or entry["runtime"] in seen:
            raise BuildError("data/build-kinds.json lists the runtime %r, which is unknown or listed twice. Next: %s"
                             % (entry["runtime"], KINDS_NEXT))
        if entry["wrapper"] not in WRAPPERS or entry["skill_location"] not in LOCATIONS \
                or not isinstance(entry["inputs"], list):
            raise BuildError("data/build-kinds.json gives the runtime %s an unknown wrapper, skill location or "
                             "inputs. Next: %s" % (entry["runtime"], KINDS_NEXT))
        if (entry["skill_location"] is None) != (entry["runtime"] == "none"):
            raise BuildError("data/build-kinds.json: only the runtime none builds no skill. Next: %s" % KINDS_NEXT)
        seen[entry["runtime"]] = entry
    missing = [r for r in runtimes if r not in seen]
    if missing:
        raise BuildError("data/build-kinds.json has no entry for the runtime(s) %s. Next: %s"
                         % (", ".join(missing), KINDS_NEXT))
    return data


def _template(name):
    path = TEMPLATE_DIR / name
    try:
        return path.read_bytes()
    except OSError:
        raise BuildError("the template templates/build/%s is missing. Next: restore it from the starter kit "
                         "(it is a byte-for-byte copy), then run the build command again" % name)


# --- Skill names -----------------------------------------------------------------------------------------

def _base_name(task):
    name = re.sub(r"[^a-z0-9]+", "-", str(task.get("name") or "").lower())
    for word in _validate.SKILL_NAME_RESERVED:
        name = name.replace(word, "-")
    name = re.sub(r"-+", "-", name).strip("-")
    if not name:
        name = "task-" + re.sub(r"[^a-z0-9]+", "-", str(task.get("id") or "").lower()).strip("-")
    return name[:NAME_MAX].rstrip("-")


def derive_skill_names(tasks):
    """{task id: (skill name, derived)} for the card's tasks, in their order.

    A name the card sets is kept (validate has checked it). An empty one is derived from the task name,
    and a derived name already taken, by a card's own name first and then by an earlier task, gets -2,
    -3 and so on, cut so the whole stays within 64 characters.
    """
    taken = {t["skill_name"] for t in tasks if isinstance(t.get("skill_name"), str) and t["skill_name"]}
    names = {}
    for task in tasks:
        own = task.get("skill_name")
        if isinstance(own, str) and own:
            names[task["id"]] = (own, False)
            continue
        base = _base_name(task)
        name, number = base, 1
        while name in taken:
            number += 1
            suffix = "-%d" % number
            name = base[:NAME_MAX - len(suffix)].rstrip("-") + suffix
        taken.add(name)
        names[task["id"]] = (name, True)
    return names


# --- Reading the persona and the old manifest --------------------------------------------------------------

def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _bad_manifest(what):
    return UsageError("build/build.json %s. %s" % (what, MANIFEST_NEXT))


def read_manifest(persona_dir):
    """The earlier build.json, checked, or None when there is none; UsageError when it is unusable."""
    path = Path(persona_dir) / BUILD_DIR / MANIFEST
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_bytes().decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        raise _bad_manifest("is not JSON")
    if not isinstance(data, dict) or data.get("build_version") != BUILD_VERSION \
            or not isinstance(data.get("artifacts"), list) or not isinstance(data.get("plugin"), dict) \
            or not isinstance(data["plugin"].get("files"), list):
        raise _bad_manifest("is not in its shape (build_version 1, a plugin with files and an artifacts list)")
    for item in data["artifacts"]:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not isinstance(item.get("files"), list):
            raise _bad_manifest("has an artifact without a task id or a files list")
        status = item.get("status")
        if status not in STATUSES:
            raise _bad_manifest("gives task %s the status %s, which is not one of %s"
                                % (item["id"], json.dumps(status), ", ".join(STATUSES)))
        history = item.get("history", [])
        if not isinstance(history, list) or not all(isinstance(h, dict) for h in history):
            raise _bad_manifest("gives task %s a history that is not a list of records" % item["id"])
    for entry in data["plugin"]["files"] + [f for a in data["artifacts"] for f in a["files"]]:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str) \
                or not isinstance(entry.get("sha256"), str):
            raise _bad_manifest("has a file entry without a path and a sha256")
    return data


# --- Rendering ---------------------------------------------------------------------------------------------

def _cell(value):
    return " ".join(str(value).split()).replace("|", "/")


def _line(value):
    return " ".join(str(value).split())


def _tools_for(levelled, tid):
    return [t for t in levelled.get("tools", []) if tid in t.get("tasks", [])]


def _frontmatter(name, task):
    tid, output = task["id"], task.get("output") or {}
    what = _line(output.get("what") or "") or "FILL IN the output"
    description = ("FILL IN: check this draft. Produces: %s. Use when FILL IN the words people type "
                   "(the card's trigger is %s)." % (what.rstrip("."), task.get("trigger") or "not set"))
    return ("---\nname: %s\ndescription: %s\n---\n\n<!-- Seeded by the build command: name from card tasks.%s.%s; "
            "description from card tasks.%s.output.what and tasks.%s.trigger. -->\n"
            % (name, json.dumps(description, ensure_ascii=False), tid,
               "skill_name" if task.get("skill_name") else "name (derived)", tid, tid))


def _purpose(task):
    tid, lines = task["id"], []
    for key, label in (("story_want", "I want my twin to"), ("story_benefit", "So that")):
        value = _line(task.get(key) or "")
        if value:
            lines.append("- %s %s. (From card `tasks.%s.%s`.)" % (label, value.rstrip("."), tid, key))
        else:
            lines.append("- %s FILL IN. (Card `tasks.%s.%s` is empty.)" % (label, tid, key))
    lines.append("- FILL IN: what the skill does not cover, so Claude does not stretch it.")
    return "## Purpose\n\n" + "\n".join(lines) + "\n"


def _inputs_table(task, levelled):
    tid, data_class = task["id"], task.get("data_class") or "FILL IN"
    rows = ["| Source | What it gives | Data class | Access | Permission at the starting level | Seeded from |",
            "|---|---|---|---|---|---|"]
    for tool in _tools_for(levelled, tid):
        permission = (tool.get("permission") or {}).get("value") or "FILL IN"
        rows.append("| FILL IN `Server:tool` (system %s) | FILL IN | %s | %s | %s | levelled `tools` (%s %s); card "
                    "`tasks.%s.data_class` |" % (_cell(tool["system"]), _cell(data_class), _cell(tool["use"]),
                                                 _cell(permission), _cell(tool["system"]), _cell(tool["use"]), tid))
    rows.append("| FILL IN a file the user attaches | FILL IN | FILL IN | read | FILL IN | none |")
    return "\n".join(rows)


def _start_from(task, levelled):
    lines = []
    for point in _backlog.starting_points_of(task, levelled):
        step = _backlog.start_from_step(point)
        lines.append("%s (From card `tasks.%s.starts_from`; cite: %s.)" % (_line(step["text"]), task["id"], step["link"]))
    return lines


def _count(value):
    return str(value) if isinstance(value, int) and not isinstance(value, bool) else "not counted yet"


def render_skill_md(task, name, levelled):
    text = _template("skill/SKILL.md").decode("utf-8")
    tid = task["id"]
    head, sep, body = text.partition("\n---\n")
    if not sep:
        raise BuildError("templates/build/skill/SKILL.md has no frontmatter. Next: restore it from the starter kit")
    body = body.lstrip("\n")
    body = body.replace("# FILL IN: Skill title\n",
                        "# FILL IN: Skill title (card `tasks.%s.name`: %s)\n" % (tid, _line(task.get("name") or "")), 1)
    start = body.index("## Purpose\n")
    end = body.index("## Inputs and connectors\n")
    body = body[:start] + _purpose(task) + "\n" + body[end:]
    old_table = ("| Source | What it gives | Data class | Access |\n|---|---|---|---|\n"
                 "| FILL IN `Server:tool` | FILL IN | FILL IN | read |\n" + NO_FILE_ROW)
    if old_table not in body:
        raise BuildError("templates/build/skill/SKILL.md has no inputs table. Next: restore it from the starter kit")
    body = body.replace(old_table, _inputs_table(task, levelled), 1)
    starts = _start_from(task, levelled)
    if starts:
        anchor = "1. FILL IN: gather."
        body = body.replace(anchor, "\n\n".join(starts) + "\n\n" + anchor, 1)
    examples = task.get("examples") or {}
    body = body.rstrip("\n") + ("\n\nReal examples counted on the card: good %s, bad %s. (From card "
                                "`tasks.%s.examples.good` and `tasks.%s.examples.bad`; where they are kept is in "
                                "`tasks.%s.examples.where`.) FILL IN: one case in evals.json per good example.\n"
                                % (_count(examples.get("good")), _count(examples.get("bad")), tid, tid, tid))
    return _frontmatter(name, task) + "\n" + body


def render_evals(task, name):
    template = json.loads(_template("skill/evals/evals.json").decode("utf-8"))
    normal, missing, near_miss = template["evals"][:3]
    good = (task.get("examples") or {}).get("good")
    count = good if isinstance(good, int) and not isinstance(good, bool) and good > 0 else 1
    cases = []
    for number in range(1, count + 1):
        case = copy.deepcopy(normal)
        case["prompt"] = case["prompt"].replace("real example 1.", "real example %d." % number)
        cases.append(case)
    for case, number in ((missing, count + 1), (near_miss, count + 2)):
        case = copy.deepcopy(case)
        case["prompt"] = re.sub(r"real example \d+", "real example %d" % number, case["prompt"])
        cases.append(case)
    for position, case in enumerate(cases, 1):
        case["id"] = position
    out = {"skill_name": name, "evals": cases}
    return json.dumps(out, indent=2, ensure_ascii=False) + "\n"


def render_trigger_evals(task):
    entries = json.loads(_template("skill/evals/trigger-evals.json").decode("utf-8"))
    tid = task["id"]
    what = _line((task.get("output") or {}).get("what") or "")
    seed = ". Seeded from card tasks.%s.trigger (%s)" % (tid, task.get("trigger") or "not set")
    out = []
    for entry in entries:
        entry = dict(entry)
        if entry["should_trigger"] is True:
            entry["query"] = entry["query"].rstrip(".") + seed + (" and tasks.%s.output.what (%s)." % (tid, what) if what else ".")
        out.append(entry)
    return "[\n" + ",\n".join("  " + json.dumps(e, ensure_ascii=False) for e in out) + "\n]\n"


def render_plugin_json(plugin):
    data = json.loads(_template("role-plugin/.claude-plugin/plugin.json").decode("utf-8"))
    data["name"] = plugin
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def render_plugin_readme(plugin, card, artifacts):
    rows = ["| [%s](skills/%s/SKILL.md) | %s: %s | FILL IN |" % (a["skill_name"], a["skill_name"], a["id"], _cell(a["task"]))
            for a in artifacts if a["skill_location"] == "plugin"]
    if not rows:
        rows = ["| none yet | | |"]
    role = _line(((card.get("role") or {}).get("name")) or "")
    return "\n".join([
        "# %s" % plugin,
        "",
        "FILL IN: one line on the role this twin serves. (Card `role.name`: %s.)" % (role or "not set"),
        "",
        "Scaffolded by the build command; [build.json](../../build.json) lists each skill's task, runtime and status. "
        "Version 0.1.0.",
        "",
        "## Skills",
        "",
        "| Skill | Task | What it does |",
        "|---|---|---|",
    ] + rows + [
        "",
        "## Persona",
        "",
        "FILL IN: the three persona files, as `starter-kit/templates/role-plugin/twin-your-role/persona/README.md` "
        "describes.",
        "",
        "## Filled in by",
        "",
        "FILL IN: the task or story numbers.",
        "",
    ])


def _decision_text(decision):
    value = decision.get("value") if isinstance(decision, dict) else None
    return "undecided" if value is None else str(value)


def _hint(key, task, decisions, levelled, artifact, plugin):
    tid = task["id"]
    if key == "identity":
        return "Levelled `tasks.%s.identity`: %s." % (tid, _decision_text(decisions.get("identity")))
    if key == "autonomy":
        autonomy = decisions.get("autonomy") or {}
        return "Levelled `tasks.%s.autonomy`: start %s, ceiling %s." % (
            tid, _decision_text(autonomy.get("start")), _decision_text(autonomy.get("ceiling")))
    if key == "data_class":
        retention = _decision_text((decisions.get("data_controls") or {}).get("retention"))
        return "Card `tasks.%s.data_class`: %s; levelled `tasks.%s.data_controls.retention`: %s." % (
            tid, task.get("data_class") or "not set", tid, retention)
    if key == "connectors":
        tools = ["%s %s (%s)" % (t["system"], t["use"], (t.get("permission") or {}).get("value") or "undecided")
                 for t in _tools_for(levelled, tid)]
        return "Levelled `tools` for %s: %s." % (tid, ", ".join(tools) if tools else "none")
    if key == "trigger":
        return "Card `tasks.%s.trigger`: %s." % (tid, task.get("trigger") or "not set")
    if key == "memory":
        return "Levelled `tasks.%s.memory`: %s." % (tid, _decision_text(decisions.get("memory")))
    if key == "skill":
        where = ("the role plugin %s, at build/plugin/%s/skills/%s/" % (plugin, plugin, artifact["skill_name"])
                 if artifact["skill_location"] == "plugin" else "build/skills/%s/" % artifact["skill_name"])
        return "The build scaffolded %s in %s." % (artifact["skill_name"], where)
    return ""


LABEL_KEYS = (("runs as", "identity"), ("who it runs as", "identity"), ("autonomy", "autonomy"),
              ("data class", "data_class"), ("connectors", "connectors"), ("schedule or trigger", "trigger"),
              ("what starts a run", "trigger"), ("memory", "memory"), ("skill", "skill"),
              ("the skill that holds", "skill"))


def _label_key(label):
    low = label.lower()
    for prefix, key in LABEL_KEYS:
        if low.startswith(prefix):
            return key
    return None


def _sheet(title, intro, kind, task, decisions, levelled, artifact, plugin):
    tid = task["id"]
    runtime = artifact["runtime"]
    lines = [
        "# %s: %s, %s" % (title, tid, _line(task.get("name") or "")),
        "",
        intro,
        "",
        "Runbook: [%s](%s%s%s). Runtime: %s (levelled `tasks.%s.runtime`, rule %s; cite %s)." % (
            kind["runbook"], "../../../", TO_REPO, kind["runbook"], runtime["value"], tid, runtime["rule"] or "none",
            runtime["cite"]),
        "",
        "## Inputs you need",
        "",
        "One line per input in the runbook. Replace each FILL IN with what the engagement decided; a hint names the "
        "field it came from.",
        "",
    ]
    for label in kind["inputs"]:
        hint = _hint(_label_key(label), task, decisions, levelled, artifact, plugin)
        lines.append("- **%s** FILL IN.%s" % (label, " " + hint if hint else ""))
    lines.append("")
    return lines


def render_routine(task, decisions, levelled, artifact, plugin, kind):
    return "\n".join(_sheet("Claude Tag routine", "A fill-in sheet for setting up this task as a Claude Tag routine. "
                                                  "Fill it in, then follow the runbook's steps.",
                            kind, task, decisions, levelled, artifact, plugin))


def render_scheduled(task, decisions, levelled, artifact, plugin, kind):
    return "\n".join(_sheet("Claude Code scheduled task", "A fill-in sheet for setting up this task as a Claude Code "
                                                          "scheduled task. Fill it in, then follow the runbook's steps.",
                            kind, task, decisions, levelled, artifact, plugin))


def render_sdk(task, decisions, levelled, artifact, plugin, kind):
    lines = _sheet("Agent SDK runner", "A scaffold for the runner that runs this task with the Claude Agent SDK. Fill "
                                       "in the inputs, then build the runner by the runbook's steps.",
                   kind, task, decisions, levelled, artifact, plugin)
    lines += [
        "## Runner",
        "",
        "- Skill: copy build/skills/%s/ into the runner's working directory at `.claude/skills/%s/` (runbook step 2)."
        % (artifact["skill_name"], artifact["skill_name"]),
        "- Model: FILL IN a full model name, pinned in the options (runbook step 1).",
        "- Credentials: the runner reads `$ANTHROPIC_API_KEY` from its environment, supplied from the secrets "
        "manager (runbook step 7). Never write a key, token or URL with a key in this folder.",
        "",
    ]
    return "\n".join(lines)


def render_agent(task, decisions, levelled, artifact, plugin):
    tid = task["id"]
    systems = []
    for tool in _tools_for(levelled, tid):
        if tool["system"] not in systems:
            systems.append(tool["system"])
    tools = [{"type": "agent_toolset_20260401", "default_config": {"enabled": False}, "configs": []}]
    tools += [{"type": "mcp_toolset", "mcp_server_name": s, "default_config": {"enabled": False}, "configs": []}
              for s in systems]
    agent = {
        "name": "%s-%s" % (plugin, tid.lower()),
        "model": FILL_IN,
        "system": "FILL IN: the persona's system-prompt form, from the persona template in compendium 02.",
        "tools": tools,
        "mcp_servers": [{"name": s, "url": "FILL IN: the MCP server's URL (runbook step 5)"} for s in systems],
        "skills": [{"type": "custom",
                    "skill_id": "FILL IN: the skill_ id returned when build/skills/%s/ is uploaded (runbook step 2)"
                                % artifact["skill_name"],
                    "version": FILL_IN}],
    }
    return json.dumps(agent, indent=2, ensure_ascii=False) + "\n"


def render_environment(task, plugin, runtime):
    env_type = "cloud" if runtime == "managed-agents" else "FILL IN: the environment type the self-hosted server takes"
    env = {"name": "%s-%s-env" % (plugin, task["id"].lower()),
           "config": {"type": env_type, "networking": {"type": "limited", "allowed_hosts": []}}}
    return json.dumps(env, indent=2, ensure_ascii=False) + "\n"


# --- Planning ----------------------------------------------------------------------------------------------

def _plan_artifact(task, name, derived, levelled, kind, plugin):
    """(artifact without files and status, [(path under build/, text)])."""
    tid = task["id"]
    decisions = levelled["tasks"][tid]
    runtime = decisions["runtime"]
    item = {
        "id": tid,
        "task": _line(task.get("name") or ""),
        "kind": kind["kind"],
        "runtime": {"value": runtime["value"], "rule": runtime["rule"], "cite": runtime["cite"],
                    "unverified": runtime["unverified"]},
        "skill_name": name,
        "skill_name_derived": derived,
        "skill_location": kind["skill_location"],
        "in_pilot": task.get("in_pilot") is True,
        "runbook": kind["runbook"],
        "files": [],
        "status": None,
        "history": [],
        "reason": kind["reason"],
    }
    if kind["skill_location"] is None:
        return item, []
    folder = ("plugin/%s/skills/%s/" % (plugin, name)) if kind["skill_location"] == "plugin" else "skills/%s/" % name
    files = [
        (folder + "SKILL.md", render_skill_md(task, name, levelled)),
        (folder + "evals/evals.json", render_evals(task, name)),
        (folder + "evals/trigger-evals.json", render_trigger_evals(task)),
        (folder + "references/example-reference.md", _template("skill/references/example-reference.md").decode("utf-8")),
    ]
    wrapper = kind["wrapper"]
    if wrapper == "agent":
        files.append(("agents/%s/agent.json" % tid, render_agent(task, decisions, levelled, item, plugin)))
        files.append(("agents/%s/environment.json" % tid, render_environment(task, plugin, runtime["value"])))
    elif wrapper == "routine":
        files.append(("routines/%s/routine.md" % tid, render_routine(task, decisions, levelled, item, plugin, kind)))
    elif wrapper == "scheduled":
        files.append(("scheduled/%s/task.md" % tid, render_scheduled(task, decisions, levelled, item, plugin, kind)))
    elif wrapper == "sdk":
        files.append(("sdk/%s/README.md" % tid, render_sdk(task, decisions, levelled, item, plugin, kind)))
    return item, files


def _result(ok, error=None, validation=None, **rest):
    out = {"ok": ok, "error": error, "validation": validation, "manifest": None, "written": [], "kept": []}
    out.update(rest)
    return out


def plan(persona_dir, all_tasks=False):
    """Everything build would write, without writing; refusals come back as ok False with a Next: line."""
    validation = _validate.validate(str(persona_dir), _fields.load_catalogue())
    if not validation["ok"]:
        return _result(False, VALIDATION_ERROR, validation)
    read = _backlog._read_levelled(persona_dir)
    if read is None:
        return _result(False, _backlog.STALE, validation)
    card, _profile, levelled = read
    if levelled.get("blockers"):
        codes = ", ".join("%s (%s)" % (b["code"], b["about"]) for b in levelled["blockers"])
        return _result(False, "levelled.json reports %d blocker(s): %s. Next: resolve them (backlog.md's gated "
                              "stories say how), run level again, then build." % (len(levelled["blockers"]), codes),
                       validation)
    plugin = levelled["persona_plan"]["plugin_name"]["value"]
    if not plugin:
        return _result(False, "levelled.json names no role plugin. Next: set role.plugin_name in card.json, run "
                              "level again, then build.", validation)
    kinds_data = load_kinds()
    kinds = dict((k["runtime"], k) for k in kinds_data["kinds"])
    old = read_manifest(persona_dir)
    tasks = card["tasks"]
    names = derive_skill_names(tasks)
    selected = [t for t in tasks if all_tasks or t.get("in_pilot") is True]
    planned, files = {}, []
    for task in selected:
        name, derived = names[task["id"]]
        item, task_files = _plan_artifact(task, name, derived, levelled, kinds[levelled["tasks"][task["id"]]["runtime"]["value"]],
                                          plugin)
        planned[task["id"]] = (item, task_files)
    old_items = dict((a["id"], a) for a in (old or {}).get("artifacts", []))
    artifacts = []
    for task in tasks:
        if task["id"] in planned:
            artifacts.append(planned[task["id"]][0])
        elif task["id"] in old_items:
            artifacts.append(old_items[task["id"]])
    plugin_files = [("plugin/%s/.claude-plugin/plugin.json" % plugin, render_plugin_json(plugin)),
                    ("plugin/%s/README.md" % plugin, render_plugin_readme(plugin, card, artifacts))]
    return _result(True, None, validation, card=card, levelled=levelled, plugin=plugin, artifacts=artifacts,
                   planned=planned, plugin_files=plugin_files, old=old,
                   kinds_version=kinds_data["build_kinds_version"])


def _repo_path(persona_dir, rel):
    return "%s/%s/%s" % (_backlog.command_path(None, persona_dir), BUILD_DIR, rel)


def _place(build_dir, repo, rel, text, recorded, writes, kept):
    """The sha256 to record for one planned file; queue the write unless a person has changed the file."""
    data = text.encode("utf-8")
    new = _sha(data)
    target = build_dir / rel
    if not target.is_file():
        writes.append((target, data))
        return new
    current = _sha(target.read_bytes())
    if current == new:
        return new
    if recorded.get(repo) == current:
        writes.append((target, data))
        return new
    kept.append(repo)
    return recorded.get(repo, new)


def _status(item, build_dir, repo_prefix, recorded_status):
    if item["kind"] == "none":
        return "not-built"
    if recorded_status in RECORDED_ONLY:
        return recorded_status
    for entry in item["files"]:
        path = build_dir / entry["path"][len(repo_prefix):]
        text = path.read_bytes().decode("utf-8", "replace") if path.is_file() else FILL_IN
        if FILL_IN in text:
            return "scaffolded"
    return "drafted"


def write_build(persona_dir, all_tasks=False):
    """Plan, then write every planned file a person has not changed, and build.json; nothing on a refusal."""
    result = plan(persona_dir, all_tasks)
    if not result["ok"]:
        return result
    persona = Path(persona_dir)
    build_dir = persona / BUILD_DIR
    old = result["old"] or {}
    recorded = dict((f["path"], f["sha256"]) for f in old.get("plugin", {}).get("files", []))
    recorded.update((f["path"], f["sha256"]) for a in old.get("artifacts", []) for f in a["files"])
    old_status = dict((a["id"], a["status"]) for a in old.get("artifacts", []))
    old_history = dict((a["id"], a.get("history") or []) for a in old.get("artifacts", []))
    prefix = _repo_path(persona_dir, "")
    writes, kept = [], []
    plugin_entries = []
    for rel, text in result["plugin_files"]:
        repo = _repo_path(persona_dir, rel)
        plugin_entries.append({"path": repo, "sha256": _place(build_dir, repo, rel, text, recorded, writes, kept)})
    for tid, (item, task_files) in result["planned"].items():
        for rel, text in task_files:
            repo = _repo_path(persona_dir, rel)
            item["files"].append({"path": repo, "sha256": _place(build_dir, repo, rel, text, recorded, writes, kept)})
    for target, data in writes:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    for item in result["artifacts"]:
        if item["id"] in result["planned"]:
            item["status"] = _status(item, build_dir, prefix, old_status.get(item["id"]))
            item["history"] = old_history.get(item["id"], [])
    levelled_sha = _sha(_level.render(result["levelled"]).encode("utf-8"))
    manifest = {
        "build_version": BUILD_VERSION,
        "customer": result["levelled"]["customer"],
        "persona": result["levelled"]["persona"],
        "source": {"levelled_sha256": levelled_sha, "build_kinds_version": result["kinds_version"]},
        "plugin": {"name": result["plugin"], "files": plugin_entries},
        "artifacts": result["artifacts"],
    }
    build_dir.mkdir(parents=True, exist_ok=True)
    (build_dir / MANIFEST).write_bytes((json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    result.update(manifest=manifest, written=[str(t) for t, _ in writes], kept=kept)
    return result


# --- check: deterministic checks on each built artifact (design section 8a) --------------------------------

DESCRIPTION_MAX = 200
BODY_MAX = 500
EVALS_MIN = 3
ORDER = STATUSES[:6]
RECORDABLE = ("evals-passing",)
PACKAGE_NEXT = ("package the role with the package command (OPS-76 adds it); record sets evals-passing only, and "
                "the package command sets packaged, deployed and verified")
LINK = re.compile(r"\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
FENCE = re.compile(r"^\s*(```|~~~)")


def _needs_manifest(persona_dir):
    manifest = read_manifest(persona_dir)
    if manifest is None:
        raise UsageError("%s/build/build.json is missing. Next: run the build command first"
                         % _backlog.command_path(None, persona_dir))
    return manifest


def _find(manifest, tid):
    for item in manifest["artifacts"]:
        if item["id"] == tid:
            return item
    raise UsageError("build/build.json has no artifact %s; it has %s. Next: give one of those task ids, or run build "
                     "with --all-tasks to build every task" % (tid, ", ".join(a["id"] for a in manifest["artifacts"])
                                                               or "none"))


def skill_folder(manifest, item):
    """The artifact's skill folder under build/, or None when it builds no skill."""
    location = item.get("skill_location")
    if location == "plugin":
        return "plugin/%s/skills/%s/" % (manifest["plugin"]["name"], item["skill_name"])
    if location == "skills":
        return "skills/%s/" % item["skill_name"]
    return None


def _scalar(value, rest):
    """A frontmatter value: JSON or single-quoted strings, block scalars (| and >) and plain text."""
    value = value.strip()
    if value[:1] in ("|", ">"):
        lines = []
        for line in rest:
            if line.strip() and not line[:1].isspace():
                break
            lines.append(line.strip())
        joined = ("\n" if value[0] == "|" else " ").join(lines)
        return joined.strip()
    if value[:1] == '"':
        try:
            return json.loads(value)
        except ValueError:
            return value.strip('"')
    if value[:1] == "'" and value[-1:] == "'" and len(value) > 1:
        return value[1:-1].replace("''", "'")
    return value


def parse_frontmatter(text):
    """({key: value}, body, error): the YAML frontmatter as plain keys, as skills use it."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, text, "has no frontmatter (a --- line, name and description, then ---)"
    try:
        close = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return None, text, "has no line closing its frontmatter (---)"
    keys, block = {}, lines[1:close]
    for position, line in enumerate(block):
        match = re.match(r"^([A-Za-z0-9_-]+):(.*)$", line)
        if match:
            keys[match.group(1)] = _scalar(match.group(2), block[position + 1:])
    return keys, "\n".join(lines[close + 1:]), None


def _table_under_inputs(body):
    """The text of the first table under a heading that starts with Inputs, or None."""
    lines = body.split("\n")
    for position, line in enumerate(lines):
        if re.match(r"^#{1,6}\s+Inputs\b", line):
            table = []
            for row in lines[position + 1:]:
                if row.startswith("#"):
                    break
                if row.lstrip().startswith("|"):
                    table.append(row)
                elif table:
                    break
            return "\n".join(table) if table else None
    return None


def _norm(text):
    return re.sub(r"[^a-z0-9]+", "", str(text).lower())


def _links(body):
    """Relative link targets in a SKILL.md body, outside fenced code."""
    out, fenced = [], False
    for line in body.split("\n"):
        if FENCE.match(line):
            fenced = not fenced
            continue
        if fenced:
            continue
        for target in LINK.findall(re.sub(r"`[^`]*`", "", line)):
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
                continue
            out.append(target.split("#", 1)[0])
    return [t for t in out if t]


def _read_json(path):
    try:
        return json.loads(path.read_bytes().decode("utf-8")), None
    except OSError:
        return None, "cannot be read"
    except (UnicodeDecodeError, ValueError) as exc:
        return None, "is not JSON (%s)" % exc


def _check_skill(build_dir, folder, item, levelled, say):
    name = item["skill_name"]
    base = build_dir / folder
    skill_md = folder + "SKILL.md"
    if not (base / "SKILL.md").is_file():
        say(skill_md, "is missing", "run the build command again to scaffold it")
        return
    text = (base / "SKILL.md").read_bytes().decode("utf-8", "replace")
    keys, body, error = parse_frontmatter(text)
    if error:
        say(skill_md, error, "start the file with the frontmatter the template has")
        keys = {}
    extra = [k for k in keys if k not in ("name", "description")]
    if extra:
        say(skill_md, "has frontmatter keys other than name and description: %s" % ", ".join(extra),
            "keep only name and description, the format that works on every surface (compendium 16)")
    own = keys.get("name")
    if not error and own != name:
        say(skill_md, "gives the name %s, not the folder name %s" % (json.dumps(own), name),
            "set name to %s; a skill's name is its folder's name" % name)
    problem = _validate.skill_name_problem(name)
    if problem:
        say(skill_md, "names the skill %s, which %s (compendium 03's name rule)" % (name, problem),
            "rename it with the card's tasks.%s.skill_name, then run level and build again" % item["id"])
    description = keys.get("description")
    if not error and not (isinstance(description, str) and description.strip()):
        say(skill_md, "has no description", "write one sentence on what the skill does and when to use it")
    elif isinstance(description, str) and len(description) >= DESCRIPTION_MAX:
        say(skill_md, "description is %d characters; keep it under 200, because the platform docs allow 1,024 but the "
            "claude.ai help article says 200 (compendium 03's Conflict line)" % len(description),
            "shorten the description to under 200 characters")
    count = len(body.rstrip("\n").split("\n")) if body.strip() else 0
    if count >= BODY_MAX:
        say(skill_md, "body is %d lines; compendium 03 keeps it under %d" % (count, BODY_MAX),
            "move detail into references/ and link it from SKILL.md")
    for target in _links(body):
        parts = target.split("/")
        if target.startswith("/") or ".." in parts:
            say(skill_md, "links %s, which is outside the skill folder" % target,
                "copy what it needs into references/ and link that")
        elif len([p for p in parts if p not in ("", ".")]) > 2:
            say(skill_md, "links %s, more than one level deep" % target,
                "link reference files directly from SKILL.md, one level deep (compendium 03)")
        elif not (base / target).exists():
            say(skill_md, "links %s, which does not exist" % target, "add the file or fix the link")
    systems = []
    for tool in _tools_for(levelled, item["id"]):
        if tool["system"] not in systems:
            systems.append(tool["system"])
    table = _table_under_inputs(body)
    if systems and table is None:
        say(skill_md, "has no Inputs table, and the levelled plan gives task %s the system(s) %s"
            % (item["id"], ", ".join(systems)), "add an Inputs table with a row for each")
    elif systems:
        missing = [s for s in systems if _norm(s) not in _norm(table)]
        if missing:
            say(skill_md, "Inputs table has no row for %s, which the levelled plan gives task %s"
                % (", ".join(missing), item["id"]), "add a row naming each system")
    evals_rel = folder + "evals/evals.json"
    data, problem = _read_json(base / "evals" / "evals.json") if (base / "evals" / "evals.json").is_file() \
        else (None, "is missing")
    if problem:
        say(evals_rel, problem, "write it in skill-creator's evals.json shape")
    elif not isinstance(data, dict) or not isinstance(data.get("skill_name"), str) \
            or not isinstance(data.get("evals"), list):
        say(evals_rel, "is not in skill-creator's shape: it needs a skill_name and an evals list",
            "follow references/schemas.md in skill-creator, as starter-kit/docs/authoring-skills.md says")
    else:
        if data["skill_name"] != name:
            say(evals_rel, "gives skill_name %s, not %s" % (json.dumps(data["skill_name"]), name),
                "set skill_name to the skill's name")
        cases = data["evals"]
        if len(cases) < EVALS_MIN:
            say(evals_rel, "has %d case(s); compendium 03's method wants at least %d" % (len(cases), EVALS_MIN),
                "turn the card's good and bad examples into cases")
        for position, case in enumerate(cases, 1):
            label = case.get("id", position) if isinstance(case, dict) else position
            if not isinstance(case, dict) or not (isinstance(case.get("prompt"), str) and case["prompt"].strip()):
                say(evals_rel, "case %s has no prompt" % label, "write the request the user would type")
            expectations = case.get("expectations") if isinstance(case, dict) else None
            if not (isinstance(expectations, list) and expectations
                    and all(isinstance(e, str) and e.strip() for e in expectations)):
                say(evals_rel, "case %s has no expectation" % label, "add at least one checkable statement")
    trigger_rel = folder + "evals/trigger-evals.json"
    data, problem = _read_json(base / "evals" / "trigger-evals.json") \
        if (base / "evals" / "trigger-evals.json").is_file() else (None, "is missing")
    if problem:
        say(trigger_rel, problem, "write it as a list of {\"query\", \"should_trigger\"} entries")
    elif not isinstance(data, list) or not all(isinstance(q, dict) and isinstance(q.get("query"), str)
                                               and isinstance(q.get("should_trigger"), bool) for q in data):
        say(trigger_rel, "is not a list of {\"query\", \"should_trigger\"} entries",
            "follow starter-kit/docs/authoring-skills.md, The eval files")
    else:
        for want in (True, False):
            if not any(q["should_trigger"] is want for q in data):
                say(trigger_rel, "has no entry with should_trigger %s" % json.dumps(want),
                    "add a query that %s" % ("should start the skill, in the owner's own words" if want
                                             else "is a near miss, a task people confuse with this one"))


def _unset(value):
    return not (isinstance(value, str) and value.strip()) or FILL_IN in value


def _check_agent(build_dir, folder, item, say):
    tid = item["id"]
    agent_rel, env_rel = "agents/%s/agent.json" % tid, "agents/%s/environment.json" % tid
    agent, problem = _read_json(build_dir / agent_rel) if (build_dir / agent_rel).is_file() else (None, "is missing")
    if problem:
        say(agent_rel, problem, "fix the JSON, or delete the file and run build again")
    elif not isinstance(agent, dict):
        say(agent_rel, "is not a JSON object", "restore it from build, then fill it in")
    else:
        if _unset(agent.get("model")):
            say(agent_rel, "model is not set", "pin a full model name (runbook step 1)")
        if _unset(agent.get("system")):
            say(agent_rel, "system is not set", "write the persona's system prompt from card.json and the runbook steps")
        skills = agent.get("skills")
        if not (isinstance(skills, list) and skills and all(isinstance(s, dict) and not _unset(s.get("skill_id"))
                                                           for s in skills)):
            say(agent_rel, "names no skill (skills needs a skill_id)",
                "upload the skill and set the skill_id it returns (runbook step 2)")
        if folder is None or not (build_dir / folder / "SKILL.md").is_file():
            say(agent_rel, "names a skill whose folder build/%sSKILL.md does not exist" % (folder or ""),
                "run the build command again to scaffold it")
    env, problem = _read_json(build_dir / env_rel) if (build_dir / env_rel).is_file() else (None, "is missing")
    if problem:
        say(env_rel, problem, "fix the JSON, or delete the file and run build again")
    elif not isinstance(env, dict):
        say(env_rel, "is not a JSON object", "restore it from build, then fill it in")
    else:
        networking = (env.get("config") or {}).get("networking") if isinstance(env.get("config"), dict) else None
        if not (isinstance(networking, dict) and networking.get("type") == "limited"):
            say(env_rel, "networking is not limited", "set config.networking.type to limited and list allowed_hosts")


def check_artifact(persona_dir, manifest, item, levelled):
    """[(repo path, problem, next)] for one artifact, in a fixed order; [] when it passes."""
    persona = Path(persona_dir)
    build_dir = persona / BUILD_DIR
    prefix = _repo_path(persona_dir, "")
    problems = []

    def say(rel, message, fix):
        problems.append((prefix + rel, message, fix))

    if item["status"] == "not-built":
        return problems
    folder = skill_folder(manifest, item)
    seen = set()
    rels = [f["path"][len(prefix):] if f["path"].startswith(prefix) else f["path"] for f in item["files"]]
    if folder and (build_dir / folder).is_dir():
        rels += sorted(p.relative_to(build_dir).as_posix() for p in (build_dir / folder).rglob("*") if p.is_file())
    for rel in rels:
        if rel in seen:
            continue
        seen.add(rel)
        path = build_dir / rel
        if not path.is_file():
            say(rel, "is missing", "run the build command again to scaffold it")
        elif FILL_IN in path.read_bytes().decode("utf-8", "replace"):
            say(rel, "still has FILL IN", "replace every FILL IN with what the engagement decided")
    if folder:
        _check_skill(build_dir, folder, item, levelled, say)
    if item["kind"] == "agent-bundle":
        _check_agent(build_dir, folder, item, say)
    return problems


def check(persona_dir, tid=None):
    """{ok, error, problems: [(path, problem, next)], checked: [ids], skipped: [ids]}; UsageError on bad input."""
    manifest = _needs_manifest(persona_dir)
    items = [_find(manifest, tid)] if tid else manifest["artifacts"]
    read = _backlog._read_levelled(persona_dir)
    if read is None:
        return {"ok": False, "error": _backlog.STALE[:-1] + ", then build, then check.", "problems": [],
                "checked": [], "skipped": []}
    levelled = read[2]
    problems, checked, skipped = [], [], []
    for item in items:
        if item["status"] == "not-built":
            skipped.append(item["id"])
            continue
        checked.append(item["id"])
        problems += check_artifact(persona_dir, manifest, item, levelled)
    return {"ok": not problems, "error": None, "problems": problems, "checked": checked, "skipped": skipped}


# --- record: move an artifact one status at a time on eval evidence (design section 8a) --------------------

class Refused(ValueError):
    """record will not move the status (exit 1, nothing written)."""


def _rate(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value <= 1


def _get(data, *keys):
    for key in keys:
        if not isinstance(data, dict) or key not in data:
            return None
        data = data[key]
    return data


def read_benchmark(data, item, case_ids, shown):
    """(pass rate, baseline rate) from skill-creator's benchmark.json; Refused when it cannot count."""
    rate = _get(data, "run_summary", "with_skill", "pass_rate", "mean")
    if not _rate(rate):
        raise Refused("%s has no run_summary.with_skill.pass_rate.mean between 0 and 1. Next: give the benchmark.json "
                      "skill-creator wrote, unedited" % shown)
    if _get(data, "metadata", "skill_name") != item["skill_name"]:
        raise Refused("%s is a benchmark for metadata.skill_name %s, not %s. Next: give this skill's benchmark"
                      % (shown, json.dumps(_get(data, "metadata", "skill_name")), item["skill_name"]))
    runs = data.get("runs") if isinstance(data.get("runs"), list) else []
    without = [r for r in runs if isinstance(r, dict) and r.get("configuration") == "without_skill"]
    baseline = _get(data, "run_summary", "without_skill", "pass_rate", "mean")
    if not _rate(baseline) or not without:
        raise Refused("%s has no without_skill baseline (runs with configuration without_skill and "
                      "run_summary.without_skill.pass_rate.mean). Next: run skill-creator's benchmark with and without "
                      "the skill" % shown)
    ran = set(r.get("eval_id") for r in runs if isinstance(r, dict) and r.get("configuration") == "with_skill")
    missing = [str(c) for c in case_ids if c not in ran]
    if missing:
        raise Refused("%s has no with_skill run for case(s) %s of evals/evals.json. Next: run the benchmark on every "
                      "case" % (shown, ", ".join(missing)))
    return rate, baseline


def read_plugin_eval(data, shown):
    """(pass rate, baseline rate) from `claude plugin eval`'s JSON result; Refused when it cannot count."""
    if data.get("schemaVersion") != 1:
        raise Refused("%s has schemaVersion %s; record reads schemaVersion 1. Next: check the plugin eval page for the "
                      "new shape, then update record" % (shown, json.dumps(data.get("schemaVersion"))))
    if data.get("partial") is True:
        raise Refused("%s is partial (%s): the suite did not finish. Next: run the suite to the end"
                      % (shown, data.get("partialReason") or "no reason given"))
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        raise Refused("%s has no cases. Next: give the --json result of a suite that ran" % shown)
    scores, baselines = [], []
    for case in cases:
        name = case.get("name") if isinstance(case, dict) else None
        arms = _get(case, "arms") or {}
        for arm in ("with", "without"):
            for run in (arms.get(arm) or []) if isinstance(arms, dict) else []:
                if isinstance(run, dict) and run.get("skippedPaidGraders") is True:
                    raise Refused("%s: case %s has a run with skippedPaidGraders, so its score is not comparable. "
                                  "Next: raise the cost ceiling and run the suite again" % (shown, name))
        score, delta = _get(case, "aggregates", "score"), _get(case, "aggregates", "delta")
        if not _rate(score):
            raise Refused("%s: case %s has no cases[].aggregates.score between 0 and 1. Next: give the unedited "
                          "result" % (shown, name))
        if not isinstance(delta, (int, float)) or isinstance(delta, bool) or not _rate(score - delta):
            raise Refused("%s: case %s has no cases[].aggregates.delta, so there is no without-skill baseline. Next: "
                          "run the suite in its two-arm mode, with and without the plugin" % (shown, name))
        scores.append(score)
        baselines.append(score - delta)
    return sum(scores) / len(scores), sum(baselines) / len(baselines)


def _number(value):
    return int(value) if float(value).is_integer() else value


def _evidence_path(persona_dir, tid, evidence):
    folder = (Path(persona_dir) / BUILD_DIR / "evidence" / tid).resolve()
    shown = "%s/evidence/%s/" % (_repo_path(persona_dir, "")[:-1], tid)
    path = Path(evidence).resolve()
    try:
        rel = path.relative_to(folder)
    except ValueError:
        raise Refused("the evidence %s is not under %s. Next: save the eval output under %s, then record it"
                      % (evidence, shown, shown))
    if not path.is_file():
        raise Refused("the evidence %s is missing (no such file). Next: save the eval output under %s, then record "
                      "it" % (evidence, shown))
    return path, shown + rel.as_posix()


def record(persona_dir, tid, status, evidence, by, pass_mark=100.0, approved_by=None):
    """Move one artifact one status up, on evidence; Refused (nothing written) or UsageError otherwise."""
    manifest = _needs_manifest(persona_dir)
    item = _find(manifest, tid)
    current = item["status"]
    if not (isinstance(by, str) and by.strip()):
        raise UsageError("--by is empty. Next: give the name of the person recording the result")
    if current == "not-built" or status == "not-built":
        raise Refused("%s builds nothing (status not-built), so there is nothing to record. Next: change the task's "
                      "runtime on the card if it should be built" % tid)
    if ORDER.index(status) == ORDER.index(current):
        raise Refused("%s is already %s. Next: nothing to record; run check to see it still passes" % (tid, status))
    if ORDER.index(status) < ORDER.index(current):
        raise Refused("%s is %s; record never moves a status backwards to %s. Next: leave it, or rebuild the "
                      "artifact from a new card if it must start again" % (tid, current, status))
    if status in ORDER[3:]:
        raise Refused("record does not set %s. Next: %s" % (status, PACKAGE_NEXT))
    if ORDER.index(status) > ORDER.index(current) + 1:
        raise Refused("%s is %s; record moves one status at a time, so the next is %s, not %s. Next: %s"
                      % (tid, current, ORDER[ORDER.index(current) + 1], status,
                         "replace every FILL IN, then run build, which sets drafted" if current == "scaffolded"
                         else "record %s first" % ORDER[ORDER.index(current) + 1]))
    if status == "drafted":
        raise Refused("build sets drafted, not record. Next: replace every FILL IN in %s's files, then run build"
                      % tid)
    if pass_mark < 100 and not (isinstance(approved_by, str) and approved_by.strip()):
        raise Refused("a pass mark of %s%% is below 100%% and needs --approved-by, the person who accepted it. Next: "
                      "add --approved-by <name>, or record at 100%%" % _number(pass_mark))
    checked = check(persona_dir, tid)
    if checked["error"]:
        raise Refused(checked["error"])
    if checked["problems"]:
        raise Refused("check reports %d problem(s) for %s. Next: run check %s, fix what it lists, then record again"
                      % (len(checked["problems"]), tid, tid))
    path, shown = _evidence_path(persona_dir, tid, evidence)
    data, problem = _read_json(path)
    if problem:
        raise Refused("the evidence %s %s. Next: give the JSON file the eval tool wrote" % (shown, problem))
    folder = skill_folder(manifest, item)
    if isinstance(data, dict) and isinstance(data.get("run_summary"), dict) and isinstance(data.get("runs"), list):
        evals = json.loads((Path(persona_dir) / BUILD_DIR / folder / "evals" / "evals.json").read_text(encoding="utf-8"))
        ids = [c.get("id") for c in evals["evals"]]
        rate, baseline = read_benchmark(data, item, ids, shown)
    elif isinstance(data, dict) and "schemaVersion" in data and "cases" in data:
        rate, baseline = read_plugin_eval(data, shown)
    else:
        raise Refused("the evidence %s is neither skill-creator's benchmark.json (run_summary and runs) nor a `claude "
                      "plugin eval` JSON result (schemaVersion and cases). Next: give one of those, unedited" % shown)
    if rate * 100 < pass_mark - 1e-9:
        raise Refused("the with-skill pass rate %s%% is below the pass mark %s%%. Next: fix the skill, run the evals "
                      "again and record the new result" % (_number(round(rate * 100, 2)), _number(pass_mark)))
    entry = {"status": status, "by": by.strip(), "evidence": shown, "pass_rate": round(rate, 4),
             "baseline_rate": round(baseline, 4), "pass_mark": _number(pass_mark),
             "approved_by": approved_by.strip() if isinstance(approved_by, str) and approved_by.strip() else None}
    artifacts = []
    for old in manifest["artifacts"]:
        if old["id"] != tid:
            artifacts.append(old)
            continue
        new = {}
        for key, value in old.items():
            if key == "history":
                continue
            new[key] = value
            if key == "status":
                new["status"] = status
                new["history"] = list(old.get("history") or []) + [entry]
        artifacts.append(new)
    manifest["artifacts"] = artifacts
    target = Path(persona_dir) / BUILD_DIR / MANIFEST
    target.write_bytes((json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    return entry
