"""Validate a persona card (card.json) and its customer profile.

validate(persona_dir) reads <persona_dir>/card.json and the profile at
<persona_dir>/../../customer-profile.json, and returns:

    {"persona_dir": str,
     "ok": bool,                      # True when there are no errors
     "errors":   [{"record", "path", "message", "fix"}],
     "warnings": [{"record", "path", "message", "fix"}],
     "completeness": {"percent", "required", "satisfied", "missing"}}

Types, enumerations, required flags, list keys, provenance statuses and
cross-record references all come from data/fields.json. Paths use ids, not
positions (tasks.T1.minutes_each); an entry without its id is named by
position (tasks[0].id). Design of record: partner-kit/docs/design.md,
sections 4 and 5.

Beyond the catalogue's types: a card needs at least one task; a top-level key
neither record has is an error naming the closest known key; record versions
are the exact integer; numbers are finite and not negative; and each override
names a value from design 7.2's vocabulary (override_values in fields.json,
read here and by level's guard), with a reason and an approver, once per task
and decision. A field with required_when {"in_pilot": true} counts as required
for each task in the pilot; and each name in a task's starts_from is a
start-from or reuse entry of the customer's industry pack or the general pack.
"""

import datetime
import difflib
import json
import math
import re
from pathlib import Path

from . import fields as _fields
from . import packs as _packs

CARD_FILE = "card.json"
PROFILE_FILE = "customer-profile.json"
RECORD_FILES = {"card": CARD_FILE, "profile": PROFILE_FILE}

_MISSING = object()
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# The task an instance path such as tasks.T1.skill_owner or tasks[0].skill_owner belongs to.
_TASK_PATH = re.compile(r"^tasks(?:\.([^.\[]+)|\[(\d+)\])\.")


def _is_unset(value):
    return value is _MISSING or value is None or value == "" or value == []


def _is_date(value):
    if not isinstance(value, str) or not _DATE.match(value):
        return False
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _type_ok(entry, value):
    kind = entry["type"]
    values = entry["values"]
    if kind == "string":
        return isinstance(value, str)
    if kind == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if kind == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if kind == "boolean":
        return isinstance(value, bool)
    if kind == "enum":
        return isinstance(value, str) and value in values
    if kind == "enum-list":
        return isinstance(value, list) and all(isinstance(v, str) and v in values for v in value)
    if kind == "string-list":
        return isinstance(value, list) and all(isinstance(v, str) for v in value)
    if kind == "date":
        return _is_date(value)
    if kind == "any":
        return True
    raise ValueError("fields.json: unknown type %r for %s" % (kind, entry["path"]))


def _expected(entry):
    kind = entry["type"]
    if kind == "enum":
        return "one of: " + ", ".join(entry["values"])
    if kind == "enum-list":
        return "a list drawn from: " + ", ".join(entry["values"])
    if kind == "date":
        return "a date in YYYY-MM-DD form"
    return {"string": "a string", "integer": "a whole number", "number": "a number",
            "boolean": "true or false", "string-list": "a list of strings"}.get(kind, kind)


class _Report:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self._seen = set()

    def _add(self, bucket, record, path, message, fix):
        key = (id(bucket), record, path, message)
        if key in self._seen:
            return
        self._seen.add(key)
        bucket.append({"record": record, "path": path, "message": message, "fix": fix})

    def error(self, record, path, message, fix):
        self._add(self.errors, record, path, message, fix)

    def warning(self, record, path, message, fix):
        self._add(self.warnings, record, path, message, fix)

    def has_error(self, record, path):
        return any(e["record"] == record and e["path"] == path for e in self.errors)


def _join(prefix, name):
    return prefix + "." + name if prefix else name


def _instances(data, entry, keys, duplicates, report, record):
    """Return [(instance_path, value)] for one catalogue entry.

    Checks the containers on the way: objects must be objects, lists must be
    lists of objects, and keyed list entries must carry a unique key. Lists
    whose key is null are positional; an exact duplicate entry in one of the
    lists named in duplicates_warn is a warning. A missing key is reported by
    the key-field check in _check_record.
    """
    out = []
    segments = entry["path"].split(".")

    def walk(node, index, cat_prefix, inst_prefix):
        segment = segments[index]
        is_list = segment.endswith("[]")
        name = segment[:-2] if is_list else segment
        cat_path = _join(cat_prefix, name)
        inst_path = _join(inst_prefix, name)
        child = node.get(name, _MISSING)
        if index == len(segments) - 1:
            out.append((inst_path, child))
            return
        if child is _MISSING or child is None:
            if is_list:
                return
            child = {}
        if is_list:
            if not isinstance(child, list):
                if not report.has_error(record, inst_path):
                    report.error(record, inst_path, "is not a list",
                                 "Make %s a list of objects, or an empty list" % inst_path)
                return
            key = keys.get(cat_path)
            compare = duplicates.get(cat_path)
            seen = set()
            seen_entries = set()
            for position, element in enumerate(child):
                if not isinstance(element, dict):
                    report.error(record, "%s[%d]" % (inst_path, position), "is not an object",
                                 "Make each entry of %s an object, as in the template" % inst_path)
                    continue
                label = element.get(key) if key else None
                if key and not (isinstance(label, str) and label):
                    label = None
                elif key and label in seen:
                    report.error(record, "%s.%s.%s" % (inst_path, label, key),
                                 "%s %r is used twice in %s" % (key, label, inst_path),
                                 "Give each entry of %s a unique %s, or merge the entries" % (inst_path, key))
                    continue
                if label is not None:
                    seen.add(label)
                    element_path = "%s.%s" % (inst_path, label)
                else:
                    element_path = "%s[%d]" % (inst_path, position)
                if compare:
                    signature = json.dumps([element.get(name) for name in compare], sort_keys=True)
                    if signature in seen_entries:
                        report.warning(record, element_path,
                                       "repeats an earlier entry of %s (same %s)" % (inst_path, ", ".join(compare)),
                                       "Delete the duplicate entry, or change what it reads or writes")
                    seen_entries.add(signature)
                walk(element, index + 1, cat_path + "[]", element_path)
        else:
            if not isinstance(child, dict):
                report.error(record, inst_path, "is not an object",
                             "Make %s an object, as in the template" % inst_path)
                return
            walk(child, index + 1, cat_path, inst_path)

    if isinstance(data, dict):
        walk(data, 0, "", "")
    return out


def _load(path, record, report):
    name = RECORD_FILES[record]
    if not path.is_file():
        where = "in the persona folder" if record == "card" else "at ../../%s from the persona folder" % name
        report.error(record, name, "not found %s (%s)" % (where, path),
                     "Copy templates/%s from the twin-consultant plugin to %s" % (name, path))
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        report.error(record, name, "does not parse as JSON: %s" % exc,
                     "Fix the JSON syntax in %s" % path)
        return None
    if not isinstance(data, dict):
        report.error(record, name, "is not a JSON object",
                     "Start from templates/%s in the twin-consultant plugin" % name)
        return None
    return data


def _check_envelope(data, record, catalogue, report):
    version_key, provenance_key = catalogue["envelope"][record]
    expected = catalogue["record_versions"][record]
    version = data.get(version_key)
    if not (type(version) is int and version == expected):
        report.error(record, version_key, "is %s, not the integer %d" % (json.dumps(version), expected),
                     "Set %s to %d, written as a whole number" % (version_key, expected))
    provenance = data.get(provenance_key, _MISSING)
    if not isinstance(provenance, dict):
        report.error(record, provenance_key, "is missing or not an object",
                     "Add a provenance object mapping field paths to {status, source}")
        return {}
    return provenance


def _check_provenance_entry(record, path, entry, rules, report):
    """Return the entry's status when it is well formed, else None."""
    if not isinstance(entry, dict):
        report.error(record, path, "provenance entry is not an object",
                     'Write it as {"status": "answered", "source": "<interview file>#<question id>"}')
        return None
    status = entry.get("status")
    if status not in rules["statuses"]:
        report.error(record, path, "provenance status %r is not one of: %s" % (status, ", ".join(rules["statuses"])),
                     "Set the status to answered, default, assumed or open")
        return None
    ok = True
    if status in rules["needs_owner"] and not (isinstance(entry.get("owner"), str) and entry["owner"].strip()):
        report.error(record, path, "provenance status %s needs an owner" % status,
                     "Name the person who will confirm this answer in the provenance entry's owner")
        ok = False
    if status in rules["needs_due"] and not _is_date(entry.get("due")):
        report.error(record, path, "provenance status %s needs a due date in YYYY-MM-DD form" % status,
                     "Add a due date, for example \"due\": \"2026-12-04\"")
        ok = False
    return status if ok else None


# --- Sources -------------------------------------------------------------------------------------------
#
# A provenance source is one source or several separated by SOURCE_SEPARATOR. Each is '<file>' or
# '<file>#<anchor>'. The file is looked up in the record's own folder (the persona folder for a card,
# the customer folder for a profile), then in the customer folder, and never outside the customer
# folder. Only entries whose status is answered are opened (OPENED_STATUSES).

SOURCE_SEPARATOR = "; "
OPENED_STATUSES = ("answered",)
INTERVIEWS_DIR = "interviews"
DISCOVERY_FILE = "discovery.md"
SOURCE_FIX = ("Point the source at the notes or discovery line that holds the answer, "
              "or set the status to assumed with an owner")
OPEN_VALUE_FIX = "Empty the value, or set the status to assumed with an owner if the value is your working guess"

_QUESTION_ID = re.compile(r"^[A-Z]\d+$")
_TASK_LINE = re.compile(r"^\s*Task id:\s*(\S+)")
_LEVEL_TWO = re.compile(r"^##\s")
_HEADING = re.compile(r"^ {0,3}(#{1,6})\s+(.*?)\s*#*\s*$")
_FENCE = re.compile(r"^\s*(```|~~~)")


def split_sources(source):
    """The sources of one provenance source string, in order: 'a.md#P2; b.md#P2' -> ['a.md#P2', 'b.md#P2']."""
    if not isinstance(source, str):
        return []
    return [part.strip() for part in source.split(SOURCE_SEPARATOR) if part.strip()]


def github_slug(heading):
    """GitHub's heading-to-anchor rule: lower case, spaces to hyphens, punctuation dropped."""
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", heading)
    text = text.replace("`", "").replace("*", "").strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


class _Sources:
    """Opens source files for one validation run; each file is read once."""

    def __init__(self, persona_dir, customer_dir):
        self.folders = {"card": persona_dir.resolve(), "profile": customer_dir.resolve()}
        self.customer = customer_dir.resolve()
        self._text = {}

    def find(self, record, name):
        """Return (Path or None, problem or None) for a source's file part."""
        parts = Path(name).parts
        if not name or Path(name).is_absolute() or ".." in parts:
            return None, ("names its file with '..' or an absolute path; name a file in the record's folder or "
                          "the customer folder instead (discovery.md#A1, not ../../discovery.md#A1)")
        for folder in (self.folders[record], self.customer):
            candidate = folder / name
            if candidate.is_file():
                return candidate, None
        return None, "names a file that is not in the %s folder or the customer folder" % (
            "persona" if record == "card" else "customer")

    def text(self, path):
        if path not in self._text:
            try:
                self._text[path] = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                self._text[path] = ""
        return self._text[path]

    def anchors(self, path):
        key = ("anchors", path)
        if key not in self._text:
            seen, found, fence = {}, set(), None
            for line in self.text(path).splitlines():
                match = _FENCE.match(line)
                if match:
                    fence = match.group(1) if fence is None else (None if fence == match.group(1) else fence)
                    continue
                heading = _HEADING.match(line) if fence is None else None
                if heading:
                    base = github_slug(heading.group(2))
                    count = seen.get(base, 0)
                    seen[base] = count + 1
                    found.add(base if count == 0 else "%s-%d" % (base, count))
            self._text[key] = found
        return self._text[key]


def _question_heading(qid):
    return re.compile(r"^#{2,6}\s+%s\." % re.escape(qid))


def _task_block(text, task_id):
    """The lines of the block whose 'Task id:' line names task_id, or None when there is none.

    A block runs from its 'Task id:' line to the next 'Task id:' line or the next level-2 heading.
    """
    lines, inside, found = [], False, False
    for line in text.splitlines():
        task = _TASK_LINE.match(line)
        if task:
            inside = task.group(1) == task_id
            found = found or inside
            continue
        if _LEVEL_TWO.match(line):
            inside = False
            continue
        if inside:
            lines.append(line)
    return lines if found else None


def _source_problem(record, path, one, sources):
    """Return why one source of an answered entry does not open, or None when it opens."""
    name, hash_mark, anchor = one.partition("#")
    found, problem = sources.find(record, name)
    if found is None:
        return problem
    under_interviews = Path(name).parts[:1] == (INTERVIEWS_DIR,)
    if under_interviews:
        if not hash_mark or not _QUESTION_ID.match(anchor):
            return "names an interview file with no question id after # (write it as %s#F2)" % name
        heading = _question_heading(anchor)
        lines = sources.text(found).splitlines()
        task = re.match(r"^tasks\.([^.\[]+)\.", path)
        if task:
            lines = _task_block(sources.text(found), task.group(1))
            if lines is None:
                return "names a file with no 'Task id: %s' block" % task.group(1)
            if not any(heading.match(line) for line in lines):
                return "has no heading %s. inside the task block for %s" % (anchor, task.group(1))
        elif not any(heading.match(line) for line in lines):
            return "has no heading %s." % anchor
        return None
    if Path(name).name == DISCOVERY_FILE:
        if not hash_mark or not anchor:
            return "names discovery.md with no question id after # (write it as discovery.md#A1)"
        for line in sources.text(found).splitlines():
            if line.lstrip().startswith("|"):
                cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
                if cells and cells[0] == anchor:
                    return None
        return "has no table row for %s" % anchor
    if hash_mark and anchor not in sources.anchors(found):
        return "has no heading whose anchor is #%s" % anchor
    return None


def _check_sources(record, provenance, values, sources, report):
    """Open every source of each answered entry; an open entry's field must be empty."""
    by_path = {path: value for pairs in values.values() for path, value in pairs}
    for path, entry in provenance.items():
        if not isinstance(entry, dict):
            continue
        status = entry.get("status")
        if status == "open" and path in by_path and not _is_unset(by_path[path]):
            report.error(record, path, "is open but holds the value %r; an open field is empty" % (by_path[path],),
                         OPEN_VALUE_FIX)
        if status not in OPENED_STATUSES:
            continue
        for one in split_sources(entry.get("source")):
            problem = _source_problem(record, path, one, sources)
            if problem:
                report.error(record, path, "source %s does not open: it %s" % (one, problem), SOURCE_FIX)


def _lower_bound(record, entry, catalogue):
    return catalogue.get("lower_bounds", {}).get("%s:%s" % (record, entry["path"]), 0)


def _check_number(record, path, entry, value, catalogue, report):
    """A number or integer field is finite and at least its lower bound (0 unless lower_bounds says)."""
    if entry["type"] not in ("integer", "number"):
        return
    low = _lower_bound(record, entry, catalogue)
    if not math.isfinite(value):
        report.error(record, path, "is %s, which is not a finite number" % value,
                     "Set it to a number of at least %s" % low)
    elif value < low:
        report.error(record, path, "is %s, which is below %s" % (value, low),
                     "Set it to a number of at least %s" % low)


def _task_of(data, path):
    """The card task an instance path belongs to, or None."""
    match = _TASK_PATH.match(path)
    tasks = data.get("tasks") if isinstance(data, dict) else None
    if not match or not isinstance(tasks, list):
        return None
    if match.group(2) is not None:
        index = int(match.group(2))
        return tasks[index] if index < len(tasks) and isinstance(tasks[index], dict) else None
    return next((t for t in tasks if isinstance(t, dict) and t.get("id") == match.group(1)), None)


def is_required(entry, data, path):
    """True when the field at this instance path counts as required: required, or required_when holds.

    The one condition is {"in_pilot": true}: the field is required for a task whose in_pilot is true.
    """
    if entry["required"]:
        return True
    if entry.get("required_when") != {"in_pilot": True}:
        return False
    task = _task_of(data, path)
    return isinstance(task, dict) and task.get("in_pilot") is True


def _check_record(data, record, catalogue, report):
    """Check one record. Return (required_paths, provenance, values_by_catalogue_path)."""
    provenance = _check_envelope(data, record, catalogue, report)
    rules = catalogue["provenance"]
    keys = catalogue["keys"].get(record, {})
    duplicates = catalogue.get("duplicates_warn", {}).get(record, {})
    required = []
    values = {}
    known_paths = set()
    no_provenance = set(catalogue.get("no_provenance", {}).get(record, []))
    for entry in _fields.fields_for(record, catalogue):
        for path, value in _instances(data, entry, keys, duplicates, report, record):
            known_paths.add(path)
            values.setdefault(entry["path"], []).append((path, value))
            if entry["path"] in no_provenance:
                # Recorded with the entry it belongs to (an override's reason and approver): no provenance,
                # not counted in completeness; a required one is a non-empty string.
                if entry["required"] and not (isinstance(value, str) and value.strip()):
                    report.error(record, path, "is required and is %s" % (
                        "missing" if value is _MISSING else "empty" if isinstance(value, str) else json.dumps(value)),
                        "Write it as a non-empty string")
                elif not _is_unset(value) and not _type_ok(entry, value):
                    report.error(record, path, "should be %s; got %r" % (_expected(entry), value),
                                 "Change it to %s" % _expected(entry))
                continue
            if entry["key"]:
                # A key field names or links an entry: always required, no provenance,
                # not counted in completeness. A key list may be empty.
                if value is _MISSING or value is None or value == "":
                    report.error(record, path, "is a key and has no value",
                                 "Set %s; ids and links between entries depend on it" % path)
                elif not _type_ok(entry, value):
                    report.error(record, path, "should be %s; got %r" % (_expected(entry), value),
                                 "Change it to %s" % _expected(entry))
                continue
            prov = provenance.get(path)
            prov_status = prov.get("status") if isinstance(prov, dict) else None
            needed = is_required(entry, data, path)
            if needed:
                required.append(path)
                if prov is None:
                    report.error(record, path, "has no provenance entry",
                                 "Add provenance.%s with a status (answered, default, assumed or open) and a source" % path)
            if _is_unset(value):
                if needed and prov_status not in rules["may_be_empty"]:
                    report.error(record, path, "is required and has no value",
                                 "Fill it in from %s, or mark it open with an owner and a due date"
                                 % (", ".join(entry["asked_by"]) or "its default"))
                continue
            if not _type_ok(entry, value):
                report.error(record, path, "should be %s; got %r" % (_expected(entry), value),
                             "Change it to %s" % _expected(entry))
            else:
                _check_number(record, path, entry, value, catalogue, report)
    for path, prov in provenance.items():
        _check_provenance_entry(record, path, prov, rules, report)
        if path not in known_paths:
            report.warning(record, path, "provenance names a field this %s does not have" % record,
                           "Check the path: paths use ids, as in tasks.T1.minutes_each")
    return required, provenance, values


def _resolve_targets(target, values_by_record):
    record, path = target.split(":", 1) if ":" in target else (None, target)
    return {v for _, v in values_by_record.get(record or "card", {}).get(path, []) if isinstance(v, str) and v}


def _check_references(catalogue, values_by_record, report):
    key_paths = {entry["path"] for entry in _fields.fields_for("card", catalogue) if entry["key"]}
    for ref in catalogue["references"]["card"]:
        target_record = ref["must_be"].split(":", 1)[0] if ":" in ref["must_be"] else "card"
        if target_record not in values_by_record:
            continue
        targets = _resolve_targets(ref["must_be"], values_by_record)
        target_name = ref["must_be"].split(":")[-1]
        where = "the customer profile's" if target_record == "profile" else "the card's"
        for path, value in values_by_record["card"].get(ref["path"], []):
            if _is_unset(value):
                if ref["path"] in key_paths or isinstance(value, list):
                    continue
                report.error("card", path, "is empty; it must name one of %s %s" % (where, target_name),
                             "Set it to one of: %s" % (", ".join(sorted(targets)) or "(none defined yet)"))
                continue
            items = value if isinstance(value, list) else [value]
            unknown = [v for v in items if v not in targets]
            if unknown:
                report.error("card", path, "names %s, which is not in %s %s"
                             % (", ".join(repr(v) for v in unknown), where, target_name),
                             "Use one of: %s, or add the missing entry"
                             % (", ".join(sorted(targets)) or "(none defined yet)"))


def _check_cross_record(card, profile, profile_path, report):
    if card is not None and profile is not None and not _is_unset(card.get("customer", _MISSING)) \
            and not _is_unset(profile.get("customer", _MISSING)) and card.get("customer") != profile.get("customer"):
        report.error("card", "customer", "is %r but the customer profile's customer is %r"
                     % (card.get("customer"), profile.get("customer")),
                     "Set card.customer to the profile's customer id")
    if profile is not None:
        folder = profile_path.parent
        if folder.name.startswith("sample-") and folder.parent.name == "engagements" \
                and profile.get("fictional") is not True:
            report.error("profile", "fictional", "must be true for a profile under engagements/%s" % folder.name,
                         "Set fictional to true; everything under engagements/sample-* is invented")
        tier = profile.get("plan", {}).get("tier") if isinstance(profile.get("plan"), dict) else None
        if tier == "individual":
            report.warning("profile", "plan.tier",
                           "individual plans always fail plan fit: Team is the minimum for company data"
                           " (docs/compendium/09-plans-and-it-controls.md)",
                           "Plan the move to Team or Enterprise before the twin is built")


def _check_retention_cover(profile, report):
    """compliance.retention 'zdr' against compliance.zdr_cover (design 4.1); silent unless both hold catalogue values."""
    compliance = profile.get("compliance") if isinstance(profile, dict) else None
    if not isinstance(compliance, dict):
        return  # a missing or malformed section is the required-field check's to report
    retention, cover = compliance.get("retention"), compliance.get("zdr_cover")
    if retention != "zdr" or not isinstance(cover, str):
        return
    if cover == "none":
        report.error("profile", "compliance.retention",
                     "is 'zdr' but compliance.zdr_cover is 'none': the customer has no zero-data-retention agreement"
                     " and plans none, so the twin cannot be set up with ZDR",
                     "Set compliance.retention to the retention the org really has (standard or custom-30-day), or"
                     " correct compliance.zdr_cover to planned or in-place if the customer does have or plan an"
                     " agreement")
    elif cover == "planned":
        report.warning("profile", "compliance.retention",
                       "is 'zdr' but compliance.zdr_cover is 'planned': ZDR is not in force until the agreement"
                       " is signed",
                       "Keep zdr only if the twin will not start before the agreement is signed; otherwise record"
                       " the retention in force today (standard or custom-30-day)")


def _check_industry(profile, report):
    """The profile's industry must be general or the id of an industry pack."""
    industry = profile.get("industry") if isinstance(profile, dict) else None
    if not isinstance(industry, str) or industry == "":
        return  # a missing or empty value is the required-field check's to report
    known = ["general"] + [pack_id for pack_id in _packs.list_packs() if pack_id != "general"]
    if industry not in known:
        report.error("profile", "industry", "%r is neither general nor the id of an industry pack" % industry,
                     "Set industry to one of: %s. If this customer's industry has no pack, use general"
                     % ", ".join(known))


# --- Override values (design 7.2), read by validate and by level's guard -----------------------------

def _check_starts_from(card, profile, report):
    """Each name in a task's starts_from is a start-from or reuse entry of the customer's pack or general."""
    tasks = card.get("tasks") if isinstance(card, dict) else None
    if not isinstance(tasks, list):
        return
    industry = profile.get("industry") if isinstance(profile, dict) else None
    # A pack that does not load is reported once, by the industry check; starts_from is not checked then.
    try:
        general = _packs.load_pack(_packs.GENERAL)
        pack = None
        if isinstance(industry, str) and industry != _packs.GENERAL and industry in _packs.list_packs():
            pack = _packs.load_pack(industry)
    except _packs.PackError:
        return
    if pack is None:
        pack, general = general, None
    for position, task in enumerate(tasks):
        if not isinstance(task, dict) or not isinstance(task.get("starts_from"), list):
            continue
        tid = task.get("id")
        label = tid if isinstance(tid, str) and tid else "[%d]" % position
        path = ("tasks.%s" % label if not label.startswith("[") else "tasks" + label) + ".starts_from"
        for name in task["starts_from"]:
            if not isinstance(name, str):
                continue
            problem = _packs.starts_from_problem(name, pack, general)
            if problem:
                report.error("card", path, "task %s starts from %s" % (label, problem), _packs.STARTS_FROM_FIX)


def _closed_values(spec, catalogue):
    """The allowed strings of one vocabulary entry: its values, or the values of the field it names."""
    if "values_from" in spec:
        record, path = spec["values_from"].split(":", 1)
        entry = _fields.entry_for(record, path, catalogue) or {}
        return list(entry.get("values") or [])
    return list(spec.get("values") or [])


def _one_value_problem(spec, value, catalogue):
    """None when value fits spec, else (message, fix) listing what is allowed."""
    kind = spec["type"]
    if kind == "integer":
        low, high = spec["min"], spec["max"]
        if isinstance(value, int) and not isinstance(value, bool) and low <= value <= high:
            return None
        return ("is %s, which is not a whole number from %d to %d" % (json.dumps(value), low, high),
                "Set it to a whole number from %d to %d (true and false are not numbers)" % (low, high))
    allowed = _closed_values(spec, catalogue)
    shown = ", ".join(allowed) + (", or null" if spec.get("null") else "")
    if kind == "enum":
        if (value is None and spec.get("null")) or (isinstance(value, str) and value in allowed):
            return None
        return ("is %s, which is not one of: %s" % (json.dumps(value, ensure_ascii=False), shown),
                "Use one of: %s, written exactly so" % shown)
    if kind == "enum-list":
        if isinstance(value, list) and all(isinstance(v, str) and v in allowed for v in value):
            return None
        return ("is %s, which is not a list drawn from: %s" % (json.dumps(value, ensure_ascii=False), shown),
                "Make it a list drawn from: %s" % shown)
    if kind == "string":
        if isinstance(value, str):
            return None
        return ("is %s, which is not a string" % json.dumps(value, ensure_ascii=False), "Make it a string")
    raise ValueError("fields.json override_values: unknown type %r" % kind)


def override_value_problems(decision, value, catalogue=None):
    """[(path suffix, message, fix)] for an override value outside design 7.2's vocabulary; [] when it fits.

    Only the overridable decisions have a vocabulary; any other decision gives [] here (validate's enum
    check and level's target check deal with it).
    """
    catalogue = catalogue if catalogue is not None else _fields.load_catalogue()
    spec = (catalogue.get("override_values") or {}).get(decision)
    if not isinstance(spec, dict):
        return []
    if spec["type"] != "object":
        problem = _one_value_problem(spec, value, catalogue)
        return [] if problem is None else [("",) + problem]
    parts = spec["parts"]
    names = ", ".join(parts)
    if not isinstance(value, dict) or not value:
        return [("", "is %s, which is not an object with at least one of: %s"
                 % (json.dumps(value, ensure_ascii=False), names),
                 'Write the parts it replaces as an object, for example {"web_tools": "off"}')]
    out = []
    for key, part in value.items():
        if key not in parts:
            close = difflib.get_close_matches(str(key), list(parts), n=1)
            out.append(("." + str(key), "names part %r, which is not one of: %s%s"
                        % (key, names, "; did you mean %s?" % close[0] if close else ""),
                        "Rename it to %s, or remove it" % (close[0] if close else "one of: " + names)))
            continue
        problem = _one_value_problem(parts[key], part, catalogue)
        if problem is not None:
            out.append(("." + key,) + problem)
    return out

def _check_overrides(card, catalogue, report):
    """Each override's value fits its decision's vocabulary, and no task and decision is overridden twice."""
    overrides = card.get("overrides")
    if not isinstance(overrides, list):
        return
    seen = {}
    for index, item in enumerate(overrides):
        if not isinstance(item, dict):
            continue
        decision = item.get("decision")
        if "value" in item or isinstance(decision, str):
            for suffix, message, fix in override_value_problems(decision, item.get("value"), catalogue):
                report.error("card", "overrides[%d].value%s" % (index, suffix), message, fix)
        key = (item.get("task"), decision)
        if not all(isinstance(part, str) for part in key):
            continue
        if key in seen:
            report.error("card", "overrides[%d]" % index,
                         "overrides[%d] and overrides[%d] both override %s on task %s"
                         % (seen[key], index, decision, key[0]),
                         "Keep one of the two entries, the one the customer approved, and delete the other")
        else:
            seen[key] = index


SKILL_NAME_MAX = 64
SKILL_NAME_CHARS = re.compile(r"^[a-z0-9-]+$")
SKILL_NAME_RESERVED = ("anthropic", "claude")
SKILL_NAME_RULE = "docs/compendium/03-skills-authoring.md#frontmatter-write-for-every-surface"


def skill_name_problem(name):
    """What breaks compendium 03's rule for a skill name, or None: 64 characters at most, lowercase letters,
    numbers and hyphens, with no "anthropic" or "claude"."""
    if len(name) > SKILL_NAME_MAX:
        return "is %d characters long; a skill name has %d at most" % (len(name), SKILL_NAME_MAX)
    if not SKILL_NAME_CHARS.match(name):
        return "has characters other than lowercase letters, numbers and hyphens"
    for word in SKILL_NAME_RESERVED:
        if word in name:
            return "contains the reserved word %s" % word
    return None


def _check_skill_names(card, report):
    """A task's skill_name, when set, follows compendium 03's name rule and is not another task's."""
    tasks = card.get("tasks") if isinstance(card, dict) else None
    if not isinstance(tasks, list):
        return
    seen = {}
    for position, task in enumerate(tasks):
        if not isinstance(task, dict) or not isinstance(task.get("skill_name"), str) or task["skill_name"] == "":
            continue
        tid = task.get("id")
        label = tid if isinstance(tid, str) and tid else "[%d]" % position
        path = ("tasks.%s" % label if not label.startswith("[") else "tasks" + label) + ".skill_name"
        name = task["skill_name"]
        problem = skill_name_problem(name)
        if problem:
            report.error("card", path, "task %s's skill_name %r %s (%s)" % (label, name, problem, SKILL_NAME_RULE),
                         "Write it in lowercase letters, numbers and hyphens, at most %d characters, without "
                         "\"anthropic\" or \"claude\", or leave it empty for build to derive it" % SKILL_NAME_MAX)
        elif name in seen:
            report.error("card", path, "task %s's skill_name %r is task %s's skill_name too" % (label, name, seen[name]),
                         "Give each task its own skill name, or leave one empty for build to derive it")
        else:
            seen[name] = label


def _check_tasks(card, report):
    """A card needs a tasks list with at least one task."""
    tasks = card.get("tasks", _MISSING)
    if isinstance(tasks, list) and tasks:
        return
    got = "missing" if tasks is _MISSING else ("an empty list" if tasks == [] else "%s, not a list"
                                                % json.dumps(tasks, ensure_ascii=False))
    report.error("card", "tasks", "a card needs at least one task; tasks is %s" % got,
                 "Add the role's tasks from the interview notes as a list of task objects, as in "
                 "templates/card.json")


def _known_top_level(record, catalogue):
    names = list(catalogue["envelope"][record])
    for entry in _fields.fields_for(record, catalogue):
        name = re.split(r"[.\[]", entry["path"])[0]
        if name not in names:
            names.append(name)
    return names


def _check_unknown_keys(data, record, catalogue, report):
    """A top-level key the catalogue does not know is an error naming the closest known key."""
    known = _known_top_level(record, catalogue)
    for key in data:
        if key in known:
            continue
        close = difflib.get_close_matches(key, known, n=1, cutoff=0.5)
        if close:
            report.error(record, key, "is not a field of %s; the closest known key is %s"
                         % (RECORD_FILES[record], close[0]),
                         "Rename %s to %s, or remove it" % (key, close[0]))
        else:
            report.error(record, key, "is not a field of %s" % RECORD_FILES[record],
                         "Remove it; the known keys are %s" % ", ".join(known))


def qualified(record, path):
    """The record-qualified path used in reports: card:voice.tone, profile:plan.tier."""
    return "%s:%s" % (record, path)


def validate(persona_dir, catalogue=None):
    """Validate the persona card in persona_dir and its customer profile."""
    catalogue = catalogue if catalogue is not None else _fields.load_catalogue()
    persona = Path(persona_dir)
    card_path = persona / CARD_FILE
    profile_path = (persona / ".." / ".." / PROFILE_FILE).resolve()
    report = _Report()

    card = _load(card_path, "card", report)
    profile = _load(profile_path, "profile", report)

    rules = catalogue["provenance"]
    required = []
    values_by_record = {}
    sources = _Sources(persona, profile_path.parent)
    for record, data in (("profile", profile), ("card", card)):
        if data is None:
            continue
        _check_unknown_keys(data, record, catalogue, report)
        if record == "card":
            _check_tasks(data, report)
            _check_overrides(data, catalogue, report)
        paths, provenance, values = _check_record(data, record, catalogue, report)
        _check_sources(record, provenance, values, sources, report)
        values_by_record[record] = values
        for path in paths:
            prov = provenance.get(path)
            done = isinstance(prov, dict) and prov.get("status") in rules["counts_as_complete"]
            required.append((record, path, done))

    if card is not None:
        _check_references(catalogue, values_by_record, report)
    _check_cross_record(card, profile, profile_path, report)
    _check_retention_cover(profile, report)
    _check_industry(profile, report)
    _check_starts_from(card, profile, report)
    _check_skill_names(card, report)

    satisfied = sum(1 for _, _, done in required if done)
    total = len(required)
    loaded = card is not None and profile is not None
    percent = (satisfied * 100 // total if total else 100) if loaded else 0
    return {
        "persona_dir": str(persona),
        "ok": not report.errors,
        "errors": report.errors,
        "warnings": report.warnings,
        "completeness": {
            "percent": percent,
            "required": total,
            "satisfied": satisfied,
            "missing": [qualified(r, p) for r, p, done in required if not done],
        },
    }
