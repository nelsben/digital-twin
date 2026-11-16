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
"""

import datetime
import json
import re
from pathlib import Path

from . import fields as _fields
from . import packs as _packs

CARD_FILE = "card.json"
PROFILE_FILE = "customer-profile.json"
RECORD_FILES = {"card": CARD_FILE, "profile": PROFILE_FILE}

_MISSING = object()
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


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
    if data.get(version_key) != expected:
        report.error(record, version_key, "is %r, not %r" % (data.get(version_key, None), expected),
                     "Set %s to %d" % (version_key, expected))
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


def _check_record(data, record, catalogue, report):
    """Check one record. Return (required_paths, provenance, values_by_catalogue_path)."""
    provenance = _check_envelope(data, record, catalogue, report)
    rules = catalogue["provenance"]
    keys = catalogue["keys"].get(record, {})
    duplicates = catalogue.get("duplicates_warn", {}).get(record, {})
    required = []
    values = {}
    known_paths = set()
    for entry in _fields.fields_for(record, catalogue):
        for path, value in _instances(data, entry, keys, duplicates, report, record):
            known_paths.add(path)
            values.setdefault(entry["path"], []).append((path, value))
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
            if entry["required"]:
                required.append(path)
                if prov is None:
                    report.error(record, path, "has no provenance entry",
                                 "Add provenance.%s with a status (answered, default, assumed or open) and a source" % path)
            if _is_unset(value):
                if entry["required"] and prov_status not in rules["may_be_empty"]:
                    report.error(record, path, "is required and has no value",
                                 "Fill it in from %s, or mark it open with an owner and a due date"
                                 % (", ".join(entry["asked_by"]) or "its default"))
                continue
            if not _type_ok(entry, value):
                report.error(record, path, "should be %s; got %r" % (_expected(entry), value),
                             "Change it to %s" % _expected(entry))
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
    for record, data in (("profile", profile), ("card", card)):
        if data is None:
            continue
        paths, provenance, values = _check_record(data, record, catalogue, report)
        values_by_record[record] = values
        for path in paths:
            prov = provenance.get(path)
            done = isinstance(prov, dict) and prov.get("status") in rules["counts_as_complete"]
            required.append((record, path, done))

    if card is not None:
        _check_references(catalogue, values_by_record, report)
    _check_cross_record(card, profile, profile_path, report)
    _check_industry(profile, report)

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
