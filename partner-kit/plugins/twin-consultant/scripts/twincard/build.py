"""Build: scaffold each task's skill and runtime wrapper under <persona-dir>/build/ (design section 8a).

build reads card.json and levelled.json, which must be current (the same test backlog uses) and
report no blocker. It never re-decides a runtime: each artifact records levelled.json's runtime with
its rule and cite, and data/build-kinds.json says what that runtime is built as. The files start
from the starter-kit templates copied into templates/build/; build fills only what the records state,
names the field each seeded line came from, and keeps every FILL IN a person must decide.

build never overwrites a person's edits: a file whose hash is not the one build recorded is kept and
listed on stderr. build.json, the manifest, has no timestamp, so the same inputs give the same bytes.
Standard library only.
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
