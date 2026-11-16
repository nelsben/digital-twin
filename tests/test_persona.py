"""Checks for every role plugin's persona: one source, two forms, no drift.

Every folder under starter-kit/plugins that holds persona/persona.md is a role
plugin. For each, persona.md is the single source. The output style (Claude
Code; the single .md file in the plugin's output-styles/ folder) and the system
prompt (claude.ai Projects, hosted agents) are built from it and must carry
each section in the same words. The shape follows
starter-kit/templates/persona/README.md.

Standard library only. Run with: python3 -m unittest tests.test_persona
(or: python3 -m unittest discover -s tests)

Output style frontmatter keys: https://code.claude.com/docs/en/output-styles
(Frontmatter reference). A plugin ships output styles from its output-styles/
folder: https://code.claude.com/docs/en/plugins-reference (Standard layout).
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = ROOT / "starter-kit" / "plugins"
PE_PLUGIN = "twin-pe-deal-team"
STAKEHOLDERS = ROOT / "engagements" / "sample-pe" / "stakeholders.md"

# From the Output styles frontmatter reference.
OUTPUT_STYLE_KEYS = frozenset({"name", "description", "keep-coding-instructions", "force-for-plugin"})
OUTPUT_STYLE_MAX_WORDS = 600

# The tag for each persona.md section, in order, as in the template's
# system-prompt.md. Sections 4 to 6 sit inside <rules>.
SECTION_TAGS = (
    "role",
    "context",
    "voice",
    "do",
    "never",
    "ask_first",
    "uncertainty",
    "escalation",
    "twin_marker",
    "data_classes",
)

PERSONA_HEADING = re.compile(r"^## (\d+)\. (.+?)\s*$")
STYLE_HEADING = re.compile(r"^## (.+?)\s*$")
PERSON_NAME = re.compile(r"^[A-Z][A-Za-z'-]+(?: [A-Z][A-Za-z'-]+){1,3}$")


def normalise(text):
    return " ".join(text.split())


def split_frontmatter(text):
    """Return (frontmatter dict, body text). The file must open with '---'."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            fm = {}
            for line in lines[1:i]:
                if ":" in line and line[0] not in " \t":
                    key, _, value = line.partition(":")
                    fm[key.strip()] = value.strip().strip("\"'")
            return fm, "\n".join(lines[i + 1:])
    return None, text


def sections(text, heading):
    """Return [(heading text, normalised body)] for each '## ' section."""
    found = []
    current, body = None, []
    for line in text.splitlines():
        match = heading.match(line)
        if match:
            if current is not None:
                found.append((current, normalise("\n".join(body))))
            current, body = match.groups()[-1], []
        elif current is not None:
            body.append(line)
    if current is not None:
        found.append((current, normalise("\n".join(body))))
    return found


def persona_sections(text):
    numbers = [int(m.group(1)) for m in map(PERSONA_HEADING.match, text.splitlines()) if m]
    return numbers, sections(text, PERSONA_HEADING)


def tag_content(text, tag):
    """Return the normalised content of the only <tag>...</tag>, or None."""
    matches = re.findall(rf"<{tag}>(.*?)</{tag}>", text, flags=re.DOTALL)
    if len(matches) != 1:
        return None
    return normalise(matches[0])


def stakeholder_names(text):
    """Every person's name in the 'Name (invented)' column of stakeholders.md."""
    names = set()
    column = None
    for line in text.splitlines():
        if not line.startswith("|"):
            column = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if "Name (invented)" in cells:
            column = cells.index("Name (invented)")
            continue
        if column is None or column >= len(cells):
            continue
        cell = cells[column]
        if PERSON_NAME.match(cell):
            names.add(cell)
    return names


def drift(persona_text, style_text, prompt_text):
    """Return a list of differences between persona.md and the two forms."""
    problems = []
    _, persona = persona_sections(persona_text)
    _, style_body = split_frontmatter(style_text)
    style = sections(style_body, STYLE_HEADING)
    if [h for h, _ in style] != [h for h, _ in persona]:
        problems.append(
            f"output style headings {[h for h, _ in style]} do not match persona.md "
            f"headings {[h for h, _ in persona]}"
        )
    else:
        for (heading, body), (_, style_section) in zip(persona, style):
            if body != style_section:
                problems.append(f"output style section {heading!r} differs from persona.md")
    for (heading, body), tag in zip(persona, SECTION_TAGS):
        content = tag_content(prompt_text, tag)
        if content is None:
            problems.append(f"system prompt needs exactly one <{tag}> for section {heading!r}")
        elif content != body:
            problems.append(f"system prompt <{tag}> differs from persona.md section {heading!r}")
    return problems


class RolePlugin:
    """The three persona files of one role plugin folder."""

    def __init__(self, folder):
        self.folder = folder
        self.name = folder.name
        self.persona = folder / "persona" / "persona.md"
        self.system_prompt = folder / "persona" / "system-prompt.md"
        styles = sorted((folder / "output-styles").glob("*.md"))
        # The single .md file in output-styles/; None when there is not exactly one.
        self.output_style = styles[0] if len(styles) == 1 else None
        self.style_files = styles

    def forms(self):
        return [self.persona, self.system_prompt, self.output_style]


def role_plugins():
    """Every plugin folder that holds persona/persona.md, in name order."""
    if not PLUGINS_DIR.is_dir():
        return []
    return [
        RolePlugin(folder)
        for folder in sorted(PLUGINS_DIR.iterdir())
        if (folder / "persona" / "persona.md").is_file()
    ]


def read(test, path):
    if path is None or not path.is_file():
        test.fail(f"{path.relative_to(ROOT) if path else 'the output style'} is missing")
    return path.read_text(encoding="utf-8")


def plugins_or_fail(test):
    """Return every role plugin, failing the test when there is none."""
    plugins = role_plugins()
    test.assertTrue(
        plugins,
        f"no role plugin found: no folder under {PLUGINS_DIR.relative_to(ROOT)} holds persona/persona.md",
    )
    return plugins


class PersonaFilesTest(unittest.TestCase):
    def test_there_is_at_least_one_role_plugin(self):
        self.assertTrue(role_plugins(), "no folder under starter-kit/plugins holds persona/persona.md")
        self.assertIn(PE_PLUGIN, [p.name for p in role_plugins()])

    def test_the_three_files_exist(self):
        for plugin in plugins_or_fail(self):
            with self.subTest(plugin=plugin.name):
                self.assertEqual(
                    len(plugin.style_files),
                    1,
                    f"{plugin.name}/output-styles/ must hold exactly one .md file, found {len(plugin.style_files)}",
                )
                for path in plugin.forms():
                    self.assertTrue(path is not None and path.is_file(), f"{plugin.name}: a persona file is missing")

    def test_no_template_markers_left(self):
        for plugin in plugins_or_fail(self):
            with self.subTest(plugin=plugin.name):
                for path in plugin.forms():
                    text = read(self, path)
                    rel = path.relative_to(ROOT)
                    self.assertNotIn("FILL IN", text, f"{rel} still has a FILL IN marker")
                    self.assertNotIn("<!--", text, f"{rel} still has a template comment")

    def test_placeholders_removed(self):
        for plugin in plugins_or_fail(self):
            with self.subTest(plugin=plugin.name):
                for folder in ("output-styles", "skills"):
                    gitkeep = plugin.folder / folder / ".gitkeep"
                    self.assertFalse(gitkeep.exists(), f"{gitkeep.relative_to(ROOT)} should be removed")


class PersonaSectionsTest(unittest.TestCase):
    def test_persona_has_the_ten_template_sections(self):
        for plugin in plugins_or_fail(self):
            with self.subTest(plugin=plugin.name):
                numbers, found = persona_sections(read(self, plugin.persona))
                self.assertEqual(numbers, list(range(1, len(SECTION_TAGS) + 1)))
                for heading, body in found:
                    self.assertTrue(body, f"persona.md section {heading!r} is empty")

    def test_both_forms_match_persona(self):
        for plugin in plugins_or_fail(self):
            with self.subTest(plugin=plugin.name):
                problems = drift(
                    read(self, plugin.persona), read(self, plugin.output_style), read(self, plugin.system_prompt)
                )
                self.assertEqual(problems, [], "\n".join(problems))

    def test_drift_is_caught(self):
        persona = "# P\n\n## 1. Role\n\nYou are   the twin.\n"
        style = "---\nname: x\n---\n# P\n\n## Role\n\nYou are the\ntwin.\n"
        prompt = "<role>\nYou are the twin.\n</role>"
        self.assertEqual(drift(persona, style, prompt), [])
        self.assertTrue(drift(persona, style.replace("the\ntwin", "a twin"), prompt))
        self.assertTrue(drift(persona, style, prompt.replace("the twin", "a twin")))


class PrivateEquityRulesTest(unittest.TestCase):
    """The deal rules live in the PE plugin's persona, not in twin-shared."""

    def test_pe_persona_states_the_code_name_and_web_rules(self):
        plugin = RolePlugin(PLUGINS_DIR / PE_PLUGIN)
        for path in plugin.forms():
            text = normalise(read(self, path)).lower()
            rel = path.relative_to(ROOT)
            self.assertIn("code name", text, f"{rel} has no rule on deal code names")
            self.assertRegex(text, r"never (expand|guess)", f"{rel} does not say never to expand or guess a code name")
            self.assertIn("web search or web fetch", text, f"{rel} has no rule against web search or web fetch")


class OutputStyleTest(unittest.TestCase):
    def test_frontmatter_keys(self):
        for plugin in plugins_or_fail(self):
            with self.subTest(plugin=plugin.name):
                fm, _ = split_frontmatter(read(self, plugin.output_style))
                self.assertIsNotNone(fm, "the output style must open with a frontmatter block")
                extra = sorted(set(fm) - OUTPUT_STYLE_KEYS)
                self.assertEqual(extra, [], f"keys not in the output style reference: {extra}")
                self.assertTrue(fm.get("name"), "the output style needs a name")
                self.assertTrue(fm.get("description"), "the output style needs a description")
                self.assertEqual(fm.get("keep-coding-instructions"), "false")

    def test_body_word_limit(self):
        for plugin in plugins_or_fail(self):
            with self.subTest(plugin=plugin.name):
                _, body = split_frontmatter(read(self, plugin.output_style))
                words = len(body.split())
                self.assertLessEqual(words, OUTPUT_STYLE_MAX_WORDS, f"output style body is {words} words")


class NoCustomerNamesTest(unittest.TestCase):
    def test_stakeholder_names_are_found(self):
        names = stakeholder_names(read(self, STAKEHOLDERS))
        self.assertIn("Ngozi Brandvold", names)
        self.assertGreaterEqual(len(names), 10)

    def test_no_sample_customer_or_people(self):
        # The sample-pe names are checked against the PE plugin only: that
        # is the plugin built from the sample engagement's role.
        names = stakeholder_names(read(self, STAKEHOLDERS))
        parts = {p for name in names for p in name.split() if len(p) >= 4}
        plugin = RolePlugin(PLUGINS_DIR / PE_PLUGIN)
        for path in plugin.forms():
            text = read(self, path)
            rel = path.relative_to(ROOT)
            self.assertNotIn("Example Capital", text, f"{rel} names the sample customer")
            for name in sorted(names | parts):
                self.assertIsNone(
                    re.search(rf"\b{re.escape(name)}\b", text),
                    f"{rel} contains {name!r} from engagements/sample-pe/stakeholders.md",
                )


if __name__ == "__main__":
    unittest.main()
