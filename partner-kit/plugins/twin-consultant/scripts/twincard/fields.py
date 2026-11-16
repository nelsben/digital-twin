"""Load the field catalogue, data/fields.json, relative to this file.

The plugin is copied to a cache when installed, so the catalogue is found
from this file's location, never from a repo path (design section 3).
"""

import json
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parent.parent.parent
CATALOGUE_PATH = PLUGIN_DIR / "data" / "fields.json"

_CACHE = {}


def load_catalogue(path=None):
    """Return the parsed catalogue. Reads data/fields.json once per path."""
    target = Path(path) if path is not None else CATALOGUE_PATH
    key = str(target)
    if key not in _CACHE:
        with target.open(encoding="utf-8") as handle:
            _CACHE[key] = json.load(handle)
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
