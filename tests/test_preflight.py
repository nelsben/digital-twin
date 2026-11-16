"""Tests for starter-kit/settings/preflight.py.

Standard library only. Run with: python3 -m unittest discover -s tests
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SETTINGS_DIR = ROOT / "starter-kit" / "settings"
PREFLIGHT = SETTINGS_DIR / "preflight.py"
BASELINES = sorted(SETTINGS_DIR.glob("*.managed-settings.json"))
MARKER = "REPLACE-WITH-"


def run(*paths):
    return subprocess.run(
        [sys.executable, str(PREFLIGHT), *map(str, paths)],
        capture_output=True, text=True,
    )


def placeholder_paths(node, path="$"):
    """Independent walk: the JSON paths of every string value holding the marker."""
    found = []
    if isinstance(node, dict):
        for k, v in node.items():
            found += placeholder_paths(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            found += placeholder_paths(v, f"{path}[{i}]")
    elif isinstance(node, str) and MARKER in node:
        found.append(path)
    return found


def replace_all(node):
    if isinstance(node, dict):
        return {k: replace_all(v) for k, v in node.items()}
    if isinstance(node, list):
        return [replace_all(v) for v in node]
    if isinstance(node, str):
        return node.replace(MARKER, "filled-in-")
    return node


class PreflightTest(unittest.TestCase):
    def test_baselines_found(self):
        self.assertEqual(len(BASELINES), 4)

    def test_each_baseline_fails_listing_every_placeholder(self):
        for path in BASELINES:
            with self.subTest(baseline=path.name):
                expected = placeholder_paths(json.loads(path.read_text(encoding="utf-8")))
                self.assertTrue(expected)
                result = run(path)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                lines = [ln for ln in result.stdout.splitlines() if MARKER in ln]
                self.assertEqual(len(lines), len(expected), result.stdout)
                for json_path in expected:
                    self.assertTrue(
                        any(path.name in ln and json_path in ln for ln in lines),
                        f"{json_path} not listed in:\n{result.stdout}",
                    )

    def test_filled_copy_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            for path in BASELINES:
                with self.subTest(baseline=path.name):
                    data = replace_all(json.loads(path.read_text(encoding="utf-8")))
                    copy = Path(tmp) / path.name
                    copy.write_text(json.dumps(data), encoding="utf-8")
                    result = run(copy)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertEqual(len(result.stdout.strip().splitlines()), 1)
                    self.assertIn("OK", result.stdout)

    def test_missing_file_exits_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run(Path(tmp) / "nope.json")
        self.assertEqual(result.returncode, 2)
        self.assertTrue(result.stderr.strip() or result.stdout.strip())

    def test_invalid_json_exits_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text("{not json", encoding="utf-8")
            result = run(bad)
        self.assertEqual(result.returncode, 2)
        self.assertTrue(result.stderr.strip() or result.stdout.strip())

    def test_nested_placeholder_in_list_and_object_found(self):
        data = {"a": {"b": [1, {"c": "https://REPLACE-WITH-HOST/*"}]}, "d": ["x", "REPLACE-WITH-Y"]}
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "nested.json"
            f.write_text(json.dumps(data), encoding="utf-8")
            result = run(f)
        self.assertEqual(result.returncode, 1)
        self.assertIn("a.b[1].c", result.stdout)
        self.assertIn("d[1]", result.stdout)

    def test_no_arguments_exits_2(self):
        self.assertEqual(run().returncode, 2)


if __name__ == "__main__":
    unittest.main()
