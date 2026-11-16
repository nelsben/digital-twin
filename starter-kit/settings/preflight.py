#!/usr/bin/env python3
"""Reject managed-settings files that still hold REPLACE-WITH- placeholders.

Usage: python3 starter-kit/settings/preflight.py <file>...

Prints one line per string value that still contains REPLACE-WITH-, giving the
file and the JSON path of the value, and exits 1. Exits 0 with one OK line when
none is left. Exits 2 with a message for a missing file or invalid JSON.
Python 3.9+, standard library only.
"""

import json
import sys

MARKER = "REPLACE-WITH-"


def find_placeholders(node, path="$"):
    """Yield (json_path, value) for every string value containing the marker."""
    if isinstance(node, dict):
        for key, value in node.items():
            yield from find_placeholders(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from find_placeholders(value, f"{path}[{index}]")
    elif isinstance(node, str) and MARKER in node:
        yield path, node


def main(argv):
    files = argv[1:]
    if not files:
        print("usage: preflight.py <file>...", file=sys.stderr)
        return 2
    loaded = []
    for name in files:
        try:
            with open(name, encoding="utf-8") as handle:
                loaded.append((name, json.load(handle)))
        except FileNotFoundError:
            print(f"{name}: file not found", file=sys.stderr)
            return 2
        except (OSError, UnicodeDecodeError) as exc:
            print(f"{name}: cannot read file: {exc}", file=sys.stderr)
            return 2
        except json.JSONDecodeError as exc:
            print(f"{name}: invalid JSON: {exc}", file=sys.stderr)
            return 2

    count = 0
    for name, data in loaded:
        for path, value in find_placeholders(data):
            print(f"{name}: {path} still holds a placeholder: {value}")
            count += 1
    if count:
        return 1
    print(f"OK: no {MARKER} placeholders left in {len(files)} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
