"""Load the field catalogue, data/fields.json, relative to this file.

The plugin is copied to a cache when installed, so the catalogue is found
from this file's location, never from a repo path (design section 3).
A catalogue that is missing, is not JSON or is not in the catalogue's shape
raises CatalogueError naming the file. An entry may carry required_when, only
{"in_pilot": true} and only on a card tasks[] field (design section 4.3).
"""

import json
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parent.parent.parent
CATALOGUE_PATH = PLUGIN_DIR / "data" / "fields.json"
TOP_LEVEL = {"envelope": dict, "record_versions": dict, "keys": dict, "provenance": dict, "references": dict,
             "fields": list}
ENTRY_KEYS = ("path", "record", "type", "values", "required", "key")
# The one condition required_when supports, on a tasks[] field: required for a task in the pilot.
REQUIRED_WHEN = ({"in_pilot": True},)
TASK_PREFIX = "tasks[]."

_CACHE = {}


class CatalogueError(ValueError):
    """fields.json cannot be read or is not a field catalogue. The message names the file."""


def _shape_problem(data):
    if not isinstance(data, dict):
        return "it is not a JSON object"
    for name, kind in TOP_LEVEL.items():
        if not isinstance(data.get(name), kind):
            return "%s is missing or not a JSON %s" % (name, "list" if kind is list else "object")
    for index, entry in enumerate(data["fields"]):
        if not isinstance(entry, dict) or any(key not in entry for key in ENTRY_KEYS):
            return "fields[%d] is not an entry with %s" % (index, ", ".join(ENTRY_KEYS))
        if "required_when" in entry:
            if entry["required_when"] not in REQUIRED_WHEN:
                return "fields[%d] (%s) has required_when %s; the only condition is {\"in_pilot\": true}" % (
                    index, entry.get("path"), json.dumps(entry["required_when"]))
            if not str(entry.get("path")).startswith(TASK_PREFIX) or entry.get("record") != "card":
                return "fields[%d] (%s) has required_when, which only a card tasks[] field may carry" % (
                    index, entry.get("path"))
    return None


def load_catalogue(path=None):
    """Return the parsed catalogue. Reads data/fields.json once per path; CatalogueError when unusable."""
    target = Path(path) if path is not None else CATALOGUE_PATH
    key = str(target)
    if key not in _CACHE:
        try:
            with target.open(encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, ValueError) as exc:
            raise CatalogueError("fields.json (%s) cannot be read as JSON: %s" % (target, exc))
        problem = _shape_problem(data)
        if problem:
            raise CatalogueError("fields.json (%s) is not a field catalogue: %s" % (target, problem))
        _CACHE[key] = data
    return _CACHE[key]


def fields_for(record, catalogue=None):
    """Return the catalogue entries for one record: 'profile' or 'card'."""
    catalogue = catalogue if catalogue is not None else load_catalogue()
    return [entry for entry in catalogue["fields"] if entry["record"] == record]


def entry_for(record, path, catalogue=None):
    """Return the catalogue entry for a record and catalogue path, or None."""
    for entry in fields_for(record, catalogue):
        if entry["path"] == path:
            return entry
    return None
