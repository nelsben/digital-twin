"""Industry packs: list them, load one, and check one against the format.

A pack is a JSON file at data/industry-packs/<id>.json inside the plugin,
found from this file's location (never from a repo path, because the plugin
is copied to a cache when installed). The format is in
partner-kit/docs/design.md, section 7.1.

    list_packs()            -> ["general", "private-equity"]
    load_pack(id)           -> the pack, or PackError naming the ids that exist
    pack_problems(pack)     -> [{"path", "message", "fix"}], empty when the pack is well formed

Enumerations (task triggers and data classes, system kinds) and the type of
each compliance default come from the field catalogue, data/fields.json.
"""

import json
import re
from pathlib import Path

from . import fields as _fields

PLUGIN_DIR = Path(__file__).resolve().parent.parent.parent
PACKS_DIR = PLUGIN_DIR / "data" / "industry-packs"

PACK_VERSION = 1
ID_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
CITE_PATTERN = re.compile(r"^(docs/compendium/[0-9]{2}-[a-z0-9-]+\.md)(#[a-z0-9_-]+)?$")
RUNBOOK_PATTERN = re.compile(r"^starter-kit/runbooks/[A-Za-z0-9._-]+\.md$")
SETTINGS_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

TOP_LEVEL = ("pack_version", "id", "name", "summary", "sources", "settings_baseline")
LISTS = ("anthropic_starting_points", "data_providers", "connector_defaults",
         "compliance_defaults", "typical_tasks")
KINDS = ("plugin", "skill", "agent-template", "reference")
USES = ("start-from", "reuse", "reference")
ACCESS = ("connector", "mcp", "api", "none")

# The fields of each list entry, in order. Every entry also carries cite and unverified.
ENTRY_FIELDS = {
    "anthropic_starting_points": ("kind", "name", "where", "use", "note"),
    "data_providers": ("name", "kind", "access", "note"),
    "connector_defaults": ("system_kind", "product", "how", "identity", "runbook"),
    "compliance_defaults": ("field", "value", "reason"),
    "typical_tasks": ("id", "name", "feature", "trigger", "data_class", "inputs"),
}
COMMON_FIELDS = ("cite", "unverified")

# Entry fields that are free text: a non-empty string. runbook is a path or null.
TEXT_FIELDS = {
    "anthropic_starting_points": ("name", "where", "note"),
    "data_providers": ("name", "kind", "note"),
    "connector_defaults": ("product", "how", "identity"),
    "compliance_defaults": ("reason",),
    "typical_tasks": ("name", "feature"),
}


class PackError(Exception):
    """A pack could not be found or read. The message says what to do."""


def list_packs():
    """Return the ids of the packs that exist, sorted."""
    if not PACKS_DIR.is_dir():
        return []
    return sorted(path.stem for path in PACKS_DIR.glob("*.json"))


def load_pack(pack_id):
    """Return the pack with this id, or raise PackError naming the ids that exist.

    A pack file that is not JSON, or not a pack object (pack_version 1, its own id, and lists of
    objects where the pack has lists), raises PackError naming the file.
    """
    known = list_packs()
    if not isinstance(pack_id, str) or pack_id not in known:
        raise PackError("There is no industry pack %r (data/industry-packs/%s.json). Packs that exist: %s. Use one "
                        "of them, or 'general' for a customer with no pack."
                        % (pack_id, pack_id, ", ".join(known) or "(none)"))
    path = PACKS_DIR / (pack_id + ".json")
    try:
        pack = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        raise PackError("Pack %r (%s) does not parse as JSON (%s). Fix the syntax in %s." % (pack_id, path, exc, path))
    problem = _shape_problem(pack, pack_id)
    if problem:
        raise PackError("Pack %r (%s) is not an industry pack: %s. Start from a pack that loads, such as "
                        "general.json." % (pack_id, path, problem))
    return pack


def _shape_problem(pack, pack_id):
    """Why a parsed pack file is not in the pack shape, or None. pack_problems() checks the content."""
    if not isinstance(pack, dict):
        return "it is not a JSON object"
    if pack.get("pack_version") != PACK_VERSION or isinstance(pack.get("pack_version"), bool):
        return "pack_version is not %d" % PACK_VERSION
    if pack.get("id") != pack_id:
        return "its id is %s, not %r" % (json.dumps(pack.get("id")), pack_id)
    for name in LISTS:
        value = pack.get(name, [])
        if not isinstance(value, list) or not all(isinstance(entry, dict) for entry in value):
            return "%s is not a list of objects" % name
    return None


def _is_text(value):
    return isinstance(value, str) and value.strip() != ""


def _enumeration(catalogue, record, path):
    entry = _fields.entry_for(record, path, catalogue)
    return list(entry["values"]) if entry else []


def _one_of(values):
    return "one of: " + ", ".join(values)


class _Problems:
    def __init__(self):
        self.items = []

    def add(self, path, message, fix):
        self.items.append({"path": path, "message": message, "fix": fix})


def _check_cite(entry, path, sources, problems):
    cite = entry.get("cite")
    where = path + ".cite"
    if not isinstance(cite, str):
        problems.add(where, "is missing or not a string",
                     "Set cite to the compendium page that says this, as docs/compendium/<page>.md or "
                     "docs/compendium/<page>.md#<heading anchor>")
        return
    match = CITE_PATTERN.match(cite)
    if not match:
        problems.add(where, "%r is not a path to a compendium page" % cite,
                     "Use docs/compendium/<page>.md, optionally followed by #<heading anchor>")
    elif match.group(1) not in sources:
        problems.add(where, "cites %s, which is not listed in sources" % match.group(1),
                     "Add %s to the pack's sources, or cite a page that is listed" % match.group(1))
    unverified = entry.get("unverified", None)
    if not isinstance(unverified, bool):
        problems.add(path + ".unverified", "is missing or not true or false",
                     "Set unverified to true when the cited page marks the fact Unverified, else false")


def _check_text(entry, names, path, problems):
    for name in names:
        if not _is_text(entry.get(name)):
            problems.add("%s.%s" % (path, name), "is missing or not a non-empty string",
                         "Write %s as a short sentence or phrase" % name)


def _check_keys(entry, kind, path, problems):
    allowed = ENTRY_FIELDS[kind] + COMMON_FIELDS
    for name in ENTRY_FIELDS[kind]:
        if name not in entry:
            problems.add("%s.%s" % (path, name), "is missing", "Add %s to this entry" % name)
    for name in entry:
        if name not in allowed:
            problems.add("%s.%s" % (path, name), "is not a field of this entry",
                         "Delete it. The fields are: %s" % ", ".join(allowed))


def _check_enum(entry, name, values, path, problems):
    if name in entry and entry[name] not in values:
        problems.add("%s.%s" % (path, name), "is %r, which is not allowed" % (entry[name],),
                     "Change it to %s" % _one_of(values))


def _check_entry(kind, entry, path, catalogue, sources, problems):
    _check_keys(entry, kind, path, problems)
    _check_text(entry, TEXT_FIELDS[kind], path, problems)
    _check_cite(entry, path, sources, problems)
    if kind == "anthropic_starting_points":
        _check_enum(entry, "kind", KINDS, path, problems)
        _check_enum(entry, "use", USES, path, problems)
    elif kind == "data_providers":
        _check_enum(entry, "access", ACCESS, path, problems)
    elif kind == "connector_defaults":
        _check_enum(entry, "system_kind", _enumeration(catalogue, "profile", "systems[].kind"), path, problems)
        runbook = entry.get("runbook", None)
        if "runbook" in entry and runbook is not None and not (isinstance(runbook, str) and RUNBOOK_PATTERN.match(runbook)):
            problems.add(path + ".runbook", "%r is not a runbook path" % (runbook,),
                         "Use starter-kit/runbooks/<name>.md, or null when there is no runbook")
    elif kind == "compliance_defaults":
        _check_compliance(entry, path, catalogue, problems)
    elif kind == "typical_tasks":
        _check_task(entry, path, catalogue, problems)


def _check_compliance(entry, path, catalogue, problems):
    # Imported here: validate.py imports this module to check a profile's industry.
    from . import validate as _validate

    field = entry.get("field")
    if "field" not in entry:
        return
    spec = _fields.entry_for("profile", field, catalogue) if isinstance(field, str) else None
    if spec is None or spec.get("key"):
        problems.add(path + ".field", "%r is not a customer-profile field in the catalogue" % (field,),
                     "Use a profile path from data/fields.json, for example compliance.retention")
        return
    if "value" in entry and not _validate._type_ok(spec, entry["value"]):
        problems.add(path + ".value", "%r should be %s" % (entry["value"], _validate._expected(spec)),
                     "Change the value to %s, the type the catalogue gives %s"
                     % (_validate._expected(spec), field))


def _check_task(entry, path, catalogue, problems):
    _check_enum(entry, "trigger", _enumeration(catalogue, "card", "tasks[].trigger"), path, problems)
    _check_enum(entry, "data_class", _enumeration(catalogue, "card", "tasks[].data_class"), path, problems)
    if "id" in entry and not _is_text(entry["id"]):
        problems.add(path + ".id", "is not a non-empty string", "Give the task an id such as T1")
    inputs = entry.get("inputs")
    if "inputs" in entry:
        kinds = _enumeration(catalogue, "profile", "systems[].kind")
        if not isinstance(inputs, list):
            problems.add(path + ".inputs", "is not a list", "Write inputs as a list of system kinds, or an empty list")
        else:
            for index, kind in enumerate(inputs):
                if kind not in kinds:
                    problems.add("%s.inputs[%d]" % (path, index), "%r is not a system kind" % (kind,),
                                 "Change it to %s" % _one_of(kinds))


def pack_problems(pack, catalogue=None):
    """Return a list of {path, message, fix}, one per fault in the pack. Empty when it is well formed."""
    catalogue = catalogue if catalogue is not None else _fields.load_catalogue()
    problems = _Problems()
    if not isinstance(pack, dict):
        problems.add("pack", "is not a JSON object", "Start from data/industry-packs/general.json")
        return problems.items

    if pack.get("pack_version") != PACK_VERSION:
        problems.add("pack_version", "is %r, not %d" % (pack.get("pack_version"), PACK_VERSION),
                     "Set pack_version to %d" % PACK_VERSION)
    if not (isinstance(pack.get("id"), str) and ID_PATTERN.match(pack["id"])):
        problems.add("id", "is missing or %r is not a pack id" % (pack.get("id"),),
                     "Use lower-case words joined by hyphens, the same as the file name without .json")
    for name in ("name", "summary"):
        if not _is_text(pack.get(name)):
            problems.add(name, "is missing or not a non-empty string",
                         "Write %s%s" % (name, " as one sentence" if name == "summary" else ""))
    if _is_text(pack.get("summary")) and "\n" in pack["summary"]:
        problems.add("summary", "runs over more than one line", "Write the summary as one sentence on one line")

    sources = pack.get("sources")
    source_set = set()
    if not isinstance(sources, list) or not sources:
        problems.add("sources", "is missing or not a list of pages",
                     "List the compendium pages the pack draws on, as docs/compendium/<page>.md")
    else:
        for index, source in enumerate(sources):
            if not (isinstance(source, str) and CITE_PATTERN.match(source) and "#" not in source):
                problems.add("sources[%d]" % index, "%r is not a path to a compendium page" % (source,),
                             "Use docs/compendium/<page>.md, with no anchor")
            else:
                source_set.add(source)

    baseline = pack.get("settings_baseline", "")
    if "settings_baseline" not in pack or not (baseline is None or
                                               (isinstance(baseline, str) and SETTINGS_PATTERN.match(baseline))):
        problems.add("settings_baseline", "is missing or %r is not a settings file name" % (baseline,),
                     "Use the name of a file in starter-kit/settings without .managed-settings.json "
                     "(for example pe-zdr), or null")

    for name in pack:
        if name not in TOP_LEVEL and name not in LISTS:
            problems.add(name, "is not a field of a pack",
                         "Delete it. The fields are: %s" % ", ".join(TOP_LEVEL + LISTS))

    for kind in LISTS:
        items = pack.get(kind)
        if not isinstance(items, list):
            problems.add(kind, "is missing or not a list", "Add %s as a list, or an empty list" % kind)
            continue
        seen = set()
        for index, entry in enumerate(items):
            path = "%s[%d]" % (kind, index)
            if not isinstance(entry, dict):
                problems.add(path, "is not an object", "Write each entry as an object")
                continue
            _check_entry(kind, entry, path, catalogue, source_set, problems)
            if kind == "typical_tasks" and _is_text(entry.get("id")):
                if entry["id"] in seen:
                    problems.add(path + ".id", "%r is used twice in typical_tasks" % entry["id"],
                                 "Give each typical task its own id")
                seen.add(entry["id"])
    return problems.items
