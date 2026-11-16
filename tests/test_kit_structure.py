"""Structure checks for the starter kit: marketplace, plugin manifests and skills.

Standard library only. Run with: python3 -m unittest discover -s tests
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KIT_DIR = ROOT / "starter-kit"
PLUGINS_DIR = KIT_DIR / "plugins"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"

# Limits for SKILL.md frontmatter. The name limits come from the Agent Skills overview:
# https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview
# The platform allows 1024 characters of description; the kit's own, stricter limit is 200
# (starter-kit/docs/authoring-skills.md).
SKILL_NAME_MAX_CHARS = 64
SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9-]+$")
SKILL_NAME_RESERVED_WORDS = ("anthropic", "claude")
SKILL_DESCRIPTION_MAX_CHARS = 200

# Body size: the platform guidance is under 500 lines
# (https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices);
# the kit's own, stricter limit is under 150 lines (starter-kit/docs/authoring-skills.md).
# A body must have fewer lines than this.
SKILL_BODY_MAX_LINES = 150

# Cross-surface frontmatter keys: the portability rule in
# docs/compendium/03-skills-authoring.md. A skill folder holding a file with the
# opt-out name below may use any keys (Claude Code only).
CROSS_SURFACE_KEYS = frozenset({"name", "description"})
CLAUDE_CODE_ONLY_MARKER = "CLAUDE_CODE_ONLY"

# Semantic version, from https://semver.org (the official regex).
SEMVER_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)

BLOCK_SCALAR_INDICATORS = {">", ">-", ">+", "|", "|-", "|+"}


def split_frontmatter(text):
    """Return (frontmatter_lines, body_lines); frontmatter_lines is None if absent.

    The frontmatter is the block between the first two '---' lines, and the
    first line of the file must be the opening '---'.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, lines
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i], lines[i + 1:]
    return None, lines


def _unquote(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def parse_frontmatter(lines):
    """Parse simple 'key: value' pairs into a dict.

    Quoted values are unquoted. Folded or literal block scalars ('>' or '|')
    are joined from their indented continuation lines. Not a YAML parser.
    """
    result = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        i += 1
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[0] in " \t" or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if value in BLOCK_SCALAR_INDICATORS:
            parts = []
            while i < len(lines) and (not lines[i].strip() or lines[i][0] in " \t"):
                parts.append(lines[i].strip())
                i += 1
            sep = "\n" if value.startswith("|") else " "
            value = sep.join(p for p in parts if p)
        else:
            value = _unquote(value)
        result[key] = value
    return result


def skill_problems(folder_name, text, allow_any_keys=False):
    """Return a list of human-readable problems with one SKILL.md."""
    fm_lines, body_lines = split_frontmatter(text)
    if fm_lines is None:
        return ["no frontmatter block (the file must start with '---' and close it with '---')"]
    fm = parse_frontmatter(fm_lines)
    problems = []

    name = fm.get("name", "")
    if not name:
        problems.append("frontmatter is missing 'name'")
    else:
        if len(name) > SKILL_NAME_MAX_CHARS:
            problems.append(f"name is {len(name)} characters; the limit is {SKILL_NAME_MAX_CHARS}")
        if not SKILL_NAME_PATTERN.match(name):
            problems.append(f"name {name!r} must use only lowercase letters, digits and hyphens")
        for word in SKILL_NAME_RESERVED_WORDS:
            if word in name.lower():
                problems.append(f"name {name!r} must not contain the reserved word {word!r}")
        if name != folder_name:
            problems.append(f"name {name!r} must match its folder name {folder_name!r}")

    description = fm.get("description", "")
    if not description.strip():
        problems.append("frontmatter is missing a non-empty 'description'")
    elif len(description) > SKILL_DESCRIPTION_MAX_CHARS:
        problems.append(
            f"description is {len(description)} characters; the limit is {SKILL_DESCRIPTION_MAX_CHARS}"
        )

    if not allow_any_keys:
        extra = sorted(set(fm) - CROSS_SURFACE_KEYS)
        if extra:
            problems.append(
                f"frontmatter keys {extra} are not cross-surface; use only "
                f"{sorted(CROSS_SURFACE_KEYS)}, or add a file named "
                f"{CLAUDE_CODE_ONLY_MARKER} to the skill folder if it is Claude Code only"
            )

    if len(body_lines) >= SKILL_BODY_MAX_LINES:
        problems.append(
            f"body is {len(body_lines)} lines; it must be under {SKILL_BODY_MAX_LINES}"
        )
    return problems


def load_json(test, path):
    """Load a JSON file, failing the test with a clear message if missing or invalid."""
    rel = path.relative_to(ROOT)
    if not path.is_file():
        test.fail(f"{rel} is missing; the starter kit needs it (see card OPS-1)")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        test.fail(f"{rel} is not valid JSON: {exc}")
    if not isinstance(data, dict):
        test.fail(f"{rel} must hold a JSON object at the top level")
    return data


def plugin_dirs():
    if not PLUGINS_DIR.is_dir():
        return []
    return sorted(p for p in PLUGINS_DIR.iterdir() if p.is_dir() and not p.name.startswith("."))


def skill_files():
    if not KIT_DIR.is_dir():
        return []
    return sorted(KIT_DIR.rglob("SKILL.md"))


class MarketplaceTest(unittest.TestCase):
    def test_marketplace_has_required_fields(self):
        data = load_json(self, MARKETPLACE)
        for key in ("name", "owner"):
            self.assertTrue(data.get(key), f"marketplace.json is missing '{key}'")
        plugins = data.get("plugins")
        self.assertIsInstance(plugins, list, "marketplace.json 'plugins' must be a list")
        self.assertTrue(plugins, "marketplace.json 'plugins' must not be empty")

    def test_every_entry_source_is_a_plugin(self):
        data = load_json(self, MARKETPLACE)
        for entry in data.get("plugins", []):
            label = entry.get("name", "<unnamed>") if isinstance(entry, dict) else repr(entry)
            with self.subTest(plugin=label):
                self.assertIsInstance(entry, dict, "plugin entry must be an object")
                self.assertTrue(entry.get("name"), "plugin entry is missing 'name'")
                source = entry.get("source")
                self.assertIsInstance(source, str, f"{label}: 'source' must be a path string")
                path = (ROOT / source).resolve()
                self.assertTrue(path.is_dir(), f"{label}: source path {source} does not exist")
                self.assertTrue(
                    (path / ".claude-plugin" / "plugin.json").is_file(),
                    f"{label}: {source} has no .claude-plugin/plugin.json",
                )

    def test_no_orphan_plugins(self):
        data = load_json(self, MARKETPLACE)
        listed = set()
        for entry in data.get("plugins", []):
            if isinstance(entry, dict) and isinstance(entry.get("source"), str):
                listed.add((ROOT / entry["source"]).resolve())
        for folder in plugin_dirs():
            with self.subTest(plugin=folder.name):
                self.assertIn(
                    folder.resolve(),
                    listed,
                    f"{folder.relative_to(ROOT)} is not listed in .claude-plugin/marketplace.json",
                )


class PluginManifestTest(unittest.TestCase):
    def test_plugins_exist(self):
        self.assertTrue(plugin_dirs(), f"no plugin folders found under {PLUGINS_DIR.relative_to(ROOT)}")

    def test_every_plugin_manifest_is_valid(self):
        for folder in plugin_dirs():
            with self.subTest(plugin=folder.name):
                data = load_json(self, folder / ".claude-plugin" / "plugin.json")
                self.assertEqual(
                    data.get("name"), folder.name, "plugin.json 'name' must equal the folder name"
                )
                version = data.get("version")
                self.assertIsInstance(version, str, "plugin.json is missing a 'version' string")
                self.assertRegex(version, SEMVER_PATTERN, f"version {version!r} is not semver")
                description = data.get("description")
                self.assertTrue(
                    isinstance(description, str) and description.strip(),
                    "plugin.json is missing a non-empty 'description'",
                )


class SkillStructureTest(unittest.TestCase):
    """Zero SKILL.md files is allowed today; each one found is checked."""

    def test_every_skill_is_valid(self):
        for path in skill_files():
            rel = path.relative_to(ROOT)
            with self.subTest(skill=str(rel)):
                allow_any = (path.parent / CLAUDE_CODE_ONLY_MARKER).is_file()
                text = path.read_text(encoding="utf-8")
                problems = skill_problems(path.parent.name, text, allow_any_keys=allow_any)
                self.assertEqual(problems, [], f"{rel}: " + "; ".join(problems))


TEMPLATE_SKILL_DIR = KIT_DIR / "templates" / "skill" / "your-skill-name"


def skill_dirs():
    """Every skill folder under the plugins, plus the skill template."""
    dirs = [p.parent for p in sorted(PLUGINS_DIR.rglob("SKILL.md"))] if PLUGINS_DIR.is_dir() else []
    if TEMPLATE_SKILL_DIR.is_dir():
        dirs.append(TEMPLATE_SKILL_DIR)
    return dirs


def eval_problems(skill_dir):
    """Return problems with a skill folder's evals/evals.json and evals/trigger-evals.json.

    The template's placeholder values meet every check (its skill_name equals its
    folder name and its files lists are empty), so it needs no exception.
    """
    problems = []
    loaded = {}
    for name in ("evals.json", "trigger-evals.json"):
        path = skill_dir / "evals" / name
        if not path.is_file():
            problems.append(f"evals/{name} is missing")
            continue
        try:
            loaded[name] = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            problems.append(f"evals/{name} is not valid JSON: {exc}")

    data = loaded.get("evals.json")
    if data is not None:
        if not isinstance(data, dict):
            problems.append("evals/evals.json must hold a JSON object at the top level")
        else:
            if "skill_name" in data and data["skill_name"] != skill_dir.name:
                problems.append(
                    f"evals/evals.json skill_name {data['skill_name']!r} must equal "
                    f"the folder name {skill_dir.name!r}"
                )
            cases = data.get("evals", [])
            if not isinstance(cases, list):
                problems.append("evals/evals.json 'evals' must be a list")
                cases = []
            for case in cases:
                files = case.get("files", []) if isinstance(case, dict) else []
                if not isinstance(files, list):
                    problems.append(f"case {case.get('id')!r}: 'files' must be a list")
                    continue
                for rel in files:
                    if not isinstance(rel, str) or not (skill_dir / rel).is_file():
                        problems.append(f"case {case.get('id')!r}: file {rel!r} does not exist")

    trigger = loaded.get("trigger-evals.json")
    if trigger is not None and not isinstance(trigger, list):
        problems.append("evals/trigger-evals.json must hold a JSON list")
    return problems


class SkillEvalFilesTest(unittest.TestCase):
    def test_skill_dirs_found(self):
        self.assertTrue(skill_dirs(), "no skill folders found")

    def test_every_skill_has_valid_eval_files(self):
        for folder in skill_dirs():
            rel = folder.relative_to(ROOT)
            with self.subTest(skill=str(rel)):
                problems = eval_problems(folder)
                self.assertEqual(problems, [], f"{rel}: " + "; ".join(problems))

    def test_eval_checker_catches_problems(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "my-skill"
            (skill / "evals").mkdir(parents=True)
            self.assertEqual(len(eval_problems(skill)), 2)  # both files missing
            (skill / "evals" / "trigger-evals.json").write_text("[", encoding="utf-8")
            (skill / "evals" / "evals.json").write_text(
                json.dumps({"skill_name": "other", "evals": [{"id": 1, "files": ["evals/files/x.md"]}]}),
                encoding="utf-8",
            )
            text = "; ".join(eval_problems(skill))
            self.assertIn("not valid JSON", text)
            self.assertIn("must equal", text)
            self.assertIn("does not exist", text)
            (skill / "evals" / "files").mkdir()
            (skill / "evals" / "files" / "x.md").write_text("x", encoding="utf-8")
            (skill / "evals" / "trigger-evals.json").write_text("[]", encoding="utf-8")
            (skill / "evals" / "evals.json").write_text(
                json.dumps({"skill_name": "my-skill", "evals": [{"id": 1, "files": ["evals/files/x.md"]}]}),
                encoding="utf-8",
            )
            self.assertEqual(eval_problems(skill), [])


class SkillCheckerSelfTest(unittest.TestCase):
    """The checker itself, on synthetic input, since the kit may hold no skills yet."""

    GOOD = "---\nname: house-style\ndescription: Applies house style. Use when drafting.\n---\n# Body\n"

    def test_good_skill_passes(self):
        self.assertEqual(skill_problems("house-style", self.GOOD), [])

    def test_parser_handles_quotes_and_folded_values(self):
        fm = parse_frontmatter(['name: "a-b"', "description: >", "  one", "  two", "other: 'x'"])
        self.assertEqual(fm, {"name": "a-b", "description": "one two", "other": "x"})

    def test_missing_frontmatter_fails(self):
        self.assertTrue(skill_problems("x", "# no frontmatter\n"))

    def test_bad_names_fail(self):
        for name in ("Bad_Name", "claude-helper", "my-anthropic-skill", "a" * 65):
            text = f"---\nname: {name}\ndescription: d\n---\nbody\n"
            self.assertTrue(skill_problems(name, text), name)

    def test_name_must_match_folder(self):
        self.assertTrue(skill_problems("other-folder", self.GOOD))

    def test_description_limits(self):
        text = "---\nname: x\ndescription: " + "d" * (SKILL_DESCRIPTION_MAX_CHARS + 1) + "\n---\nbody\n"
        self.assertTrue(skill_problems("x", text))
        ok = "---\nname: x\ndescription: " + "d" * SKILL_DESCRIPTION_MAX_CHARS + "\n---\nbody\n"
        self.assertEqual(skill_problems("x", ok), [])
        self.assertTrue(skill_problems("x", "---\nname: x\ndescription:\n---\nbody\n"))

    def test_extra_keys_need_marker(self):
        text = "---\nname: x\ndescription: d\nallowed-tools: Read\n---\nbody\n"
        self.assertTrue(skill_problems("x", text))
        self.assertEqual(skill_problems("x", text, allow_any_keys=True), [])

    def test_long_body_fails(self):
        text = "---\nname: x\ndescription: d\n---\n" + "line\n" * SKILL_BODY_MAX_LINES
        self.assertTrue(skill_problems("x", text))
        text = "---\nname: x\ndescription: d\n---\n" + "line\n" * (SKILL_BODY_MAX_LINES - 1)
        self.assertEqual(skill_problems("x", text), [])


if __name__ == "__main__":
    unittest.main()
