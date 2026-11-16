"""Structure checks for the twin-consultant plugin's skills (OPS-33).

Every folder under partner-kit/plugins/twin-consultant/skills/ is checked: the
frontmatter and body rules the starter kit applies to its own skills, the eval
files, the copies of fixture files the evals use, and that every question id,
field path and plugin path a skill or an expectation names really exists.

Standard library only. Runs under both
  python3 -m unittest discover -s tests
  python3 -m unittest tests.test_partner_kit_skills
"""

import json
import re
import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

# Reused, not copied: the kit's skill rules and the interview kit's banned words.
from test_kit_structure import (  # noqa: E402
    CLAUDE_CODE_ONLY_MARKER,
    eval_problems,
    parse_frontmatter,
    skill_problems,
    split_frontmatter,
)
from test_interview_kit import BANNED, parse_guide  # noqa: E402

ROOT = TESTS_DIR.parent
PLUGIN = ROOT / "partner-kit" / "plugins" / "twin-consultant"
SKILLS_DIR = PLUGIN / "skills"
FIELDS = PLUGIN / "data" / "fields.json"
ENGAGEMENTS = ROOT / "engagements"

# The skills this card adds, with the minimum number of cases in evals.json.
NAMED_SKILLS = {"preparing-role-interviews": 4, "filling-persona-cards": 5}
MIN_TRIGGER_EACH = 4  # at least this many should_trigger true, and as many false
MIN_TRIGGER_NAMED = 8
DESCRIPTION_LIMIT = 200  # strictly under
EVAL_FILES_PREFIX = "evals/files/"
PROVENANCE_ATTRS = ("status", "source", "owner", "due")

# A question id is recognised only in a fixed form: '#F2' (a provenance source) or
# 'question F2' / 'questions P1'. Bare ids are not read, because task ids (C1, T1)
# and open-question ids (E4) look the same.
QUESTION_ID_RE = re.compile(r"(?:#|\bquestions? )([A-Z]\d+)\b")
# A dotted name such as tasks.C1.minutes_each or tasks[].inputs[0].access.
PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_\-./#$])"
    r"([a-z_]+(?:\[\d*\])?(?:\.[A-Za-z0-9_\-]+(?:\[\d*\])?)+)"
)
PLUGIN_ROOT_RE = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\s`)'\"\]]+)")
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")


def skill_folders():
    if not SKILLS_DIR.is_dir():
        return []
    return sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir() and not p.name.startswith("."))


def load_catalogue():
    return json.loads(FIELDS.read_text(encoding="utf-8"))


def valid_question_ids(catalogue):
    """Question ids of the interview guide plus every id the catalogue's asked_by names."""
    _, order = parse_guide()
    ids = set(order)
    for field in catalogue["fields"]:
        ids.update(field["asked_by"])
    return ids


def catalogue_shape(catalogue):
    """Return (paths, keyed_lists, top_level_names) over both records."""
    paths = {f["path"] for f in catalogue["fields"]}
    keyed = {}
    for record_keys in catalogue["keys"].values():
        for lst, key in record_keys.items():
            keyed[lst.replace("[]", "")] = key
    tops = {re.split(r"[.\[]", p)[0] for p in paths}
    return paths, keyed, tops


def _segments(token):
    """Split a dotted token into (name, has_brackets) segments."""
    out = []
    for part in token.split("."):
        m = re.match(r"^([A-Za-z0-9_\-]+)(\[\d*\])?$", part)
        if not m:
            return None
        out.append((m.group(1), bool(m.group(2))))
    return out


def normalise_path(token, catalogue):
    """Map a provenance-style or catalogue-style path to its catalogue form.

    'provenance.tasks.C1.minutes_each.source' -> 'tasks[].minutes_each'
    'tasks.C2.writes[0].action'               -> 'tasks[].writes[].action'
    'systems.salesforce.edition'              -> 'systems[].edition'
    Returns None when the token is not a field path (its first name is no
    top-level field of either record), for example 'card.json' or 'cli.py'.
    """
    _, keyed, tops = catalogue_shape(catalogue)
    segs = _segments(token)
    if not segs:
        return None
    prov = segs[0][0] == "provenance"
    if prov:
        segs = segs[1:]
        if prov and segs and segs[-1][0] in PROVENANCE_ATTRS and not segs[-1][1]:
            segs = segs[:-1]
    if not segs or segs[0][0] not in tops:
        return None
    norm = ""
    i = 0
    while i < len(segs):
        name, brackets = segs[i]
        bare = (norm + "." + name) if norm else name
        plain = bare.replace("[]", "")
        if brackets:
            norm = bare + "[]"
        elif plain in keyed and keyed[plain] is not None and i + 1 < len(segs):
            norm = bare + "[]"
            i += 1  # the next segment is the entry's id
        else:
            norm = bare
        i += 1
    return norm


def path_exists(norm, catalogue):
    paths, keyed, _ = catalogue_shape(catalogue)
    if norm in paths or norm.replace("[]", "") in keyed:
        return True
    return any(p.startswith(norm + ".") or p.startswith(norm + "[") for p in paths)


def field_path_tokens(text, catalogue):
    """[(token, normalised)] for every dotted name in text that starts like a field path."""
    found = []
    for m in PATH_RE.finditer(text):
        norm = normalise_path(m.group(1), catalogue)
        if norm is not None:
            found.append((m.group(1), norm))
    return found


def strip_code(text):
    """Remove fenced code blocks and inline code spans, leaving the prose."""
    text = re.sub(r"(?ms)^```.*?^```[ \t]*$", "", text)
    return re.sub(r"`[^`\n]*`", "", text)


def banned_words_in(text):
    prose = strip_code(text)
    return sorted({w for w in BANNED if re.search(r"\b%s\b" % re.escape(w), prose, re.I)})


def plugin_path_refs(text, skill_dir):
    """[(reference, resolved Path)] for plugin-root paths and relative links in a SKILL.md."""
    refs = []
    for m in PLUGIN_ROOT_RE.finditer(text):
        rel = m.group(1).rstrip(".,;:")
        rel = rel.split("#")[0]
        if "<" in rel or not rel:
            continue
        refs.append((m.group(0), PLUGIN / rel))
    for m in LINK_RE.finditer(text):
        target = m.group(1).split("#")[0]
        if not target or "://" in target or target.startswith("$") or "<" in target:
            continue
        refs.append((target, (skill_dir / target).resolve()))
    return refs


def load_evals(skill_dir):
    cases = json.loads((skill_dir / "evals" / "evals.json").read_text(encoding="utf-8"))
    trigger = json.loads((skill_dir / "evals" / "trigger-evals.json").read_text(encoding="utf-8"))
    return cases, trigger


class NamedSkillsTest(unittest.TestCase):
    def test_named_skills_exist(self):
        for name in NAMED_SKILLS:
            with self.subTest(skill=name):
                folder = SKILLS_DIR / name
                self.assertTrue((folder / "SKILL.md").is_file(), f"{name}/SKILL.md is missing")
                for rel in ("evals/evals.json", "evals/trigger-evals.json"):
                    self.assertTrue((folder / rel).is_file(), f"{name}/{rel} is missing")


class SkillRulesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalogue = load_catalogue()
        cls.question_ids = valid_question_ids(cls.catalogue)

    def test_frontmatter_and_body(self):
        for folder in skill_folders():
            with self.subTest(skill=folder.name):
                text = (folder / "SKILL.md").read_text(encoding="utf-8")
                allow_any = (folder / CLAUDE_CODE_ONLY_MARKER).is_file()
                problems = skill_problems(folder.name, text, allow_any_keys=allow_any)
                self.assertEqual(problems, [], "; ".join(problems))
                fm = parse_frontmatter(split_frontmatter(text)[0] or [])
                self.assertLess(len(fm.get("description", "")), DESCRIPTION_LIMIT)

    def test_eval_files(self):
        for folder in skill_folders():
            with self.subTest(skill=folder.name):
                problems = eval_problems(folder)
                self.assertEqual(problems, [], "; ".join(problems))
                data, trigger = load_evals(folder)
                cases = data.get("evals", [])
                for case in cases:
                    for key in ("id", "prompt", "expected_output", "files", "expectations"):
                        self.assertIn(key, case, f"case {case.get('id')!r} has no {key!r}")
                    self.assertTrue(case["expectations"], f"case {case['id']!r} has no expectations")
                    for rel in case["files"]:
                        self.assertTrue(rel.startswith(EVAL_FILES_PREFIX),
                                        f"case {case['id']!r}: {rel} is not under {EVAL_FILES_PREFIX}")
                ids = [c["id"] for c in cases]
                self.assertEqual(len(ids), len(set(ids)), "case ids repeat")
                self.assertIsInstance(trigger, list)
                for q in trigger:
                    self.assertIsInstance(q.get("query"), str)
                    self.assertIsInstance(q.get("should_trigger"), bool)
                true = sum(1 for q in trigger if q["should_trigger"])
                false = len(trigger) - true
                self.assertGreaterEqual(true, MIN_TRIGGER_EACH, "too few should_trigger true")
                self.assertGreaterEqual(false, MIN_TRIGGER_EACH, "too few should_trigger false")
                if folder.name in NAMED_SKILLS:
                    self.assertGreaterEqual(len(cases), NAMED_SKILLS[folder.name])
                    self.assertGreaterEqual(len(trigger), MIN_TRIGGER_NAMED)
                    self.assertGreaterEqual(false * 2, len(trigger), "at least half must be false")

    def test_fixture_copies_match_their_source(self):
        """A file under evals/files/engagements/<customer>/ mirrors engagements/<customer>/.

        When that customer folder exists in engagements/, the file is a fixture copy and
        must equal its source byte for byte. Otherwise it is invented: the customer folder
        must be a sample-* folder (fictional by the repo rule).
        """
        copies = 0
        for folder in skill_folders():
            base = folder / "evals" / "files" / "engagements"
            if not base.is_dir():
                continue
            for path in sorted(p for p in base.rglob("*") if p.is_file()):
                rel = path.relative_to(base)
                customer = rel.parts[0]
                with self.subTest(file=str(path.relative_to(ROOT))):
                    if (ENGAGEMENTS / customer).is_dir():
                        source = ENGAGEMENTS / rel
                        self.assertTrue(source.is_file(), f"no source engagements/{rel} for this copy")
                        self.assertEqual(path.read_bytes(), source.read_bytes(),
                                         f"differs from engagements/{rel}")
                        copies += 1
                    else:
                        self.assertTrue(customer.startswith("sample-"),
                                        f"invented customer folder {customer} must be a sample-* folder")
        if all((SKILLS_DIR / n).is_dir() for n in NAMED_SKILLS):
            self.assertGreater(copies, 0, "no fixture copies found")

    def _texts(self, folder):
        """SKILL.md and every expectation of the skill, as (label, text)."""
        out = [("SKILL.md", (folder / "SKILL.md").read_text(encoding="utf-8"))]
        data, _ = load_evals(folder)
        for case in data.get("evals", []):
            for i, exp in enumerate(case.get("expectations", [])):
                out.append((f"case {case.get('id')} expectation {i + 1}", exp))
        return out

    def test_question_ids_exist(self):
        for folder in skill_folders():
            hits = 0
            for label, text in self._texts(folder):
                for qid in QUESTION_ID_RE.findall(text):
                    hits += 1
                    with self.subTest(skill=folder.name, where=label, question=qid):
                        self.assertIn(qid, self.question_ids)
            if folder.name in NAMED_SKILLS:
                self.assertGreater(hits, 0, f"{folder.name}: no question ids found")

    def test_field_paths_exist(self):
        for folder in skill_folders():
            hits = 0
            for label, text in self._texts(folder):
                for token, norm in field_path_tokens(text, self.catalogue):
                    hits += 1
                    with self.subTest(skill=folder.name, where=label, path=token):
                        self.assertTrue(path_exists(norm, self.catalogue),
                                        f"{token} ({norm}) is not in data/fields.json")
            if folder.name in NAMED_SKILLS:
                self.assertGreater(hits, 0, f"{folder.name}: no field paths found")

    def test_no_banned_words(self):
        for folder in skill_folders():
            with self.subTest(skill=folder.name):
                text = (folder / "SKILL.md").read_text(encoding="utf-8")
                self.assertEqual(banned_words_in(text), [])

    def test_plugin_paths_exist(self):
        for folder in skill_folders():
            text = (folder / "SKILL.md").read_text(encoding="utf-8")
            refs = plugin_path_refs(text, folder)
            for ref, path in refs:
                with self.subTest(skill=folder.name, path=ref):
                    self.assertTrue(path.exists(), f"{ref} does not exist")
            if folder.name in NAMED_SKILLS:
                self.assertTrue(any("CLAUDE_PLUGIN_ROOT" in r for r, _ in refs),
                                f"{folder.name}: names no plugin path")


class CheckerSelfTest(unittest.TestCase):
    """The extractors, on synthetic input, so a vacuous pass cannot hide."""

    @classmethod
    def setUpClass(cls):
        cls.catalogue = load_catalogue()

    def test_normalise(self):
        cases = {
            "provenance.tasks.C1.minutes_each.source": "tasks[].minutes_each",
            "tasks.C2.writes[0].action": "tasks[].writes[].action",
            "tasks[].inputs[].access": "tasks[].inputs[].access",
            "systems.salesforce.edition": "systems[].edition",
            "open_questions.OQ-1.owner": "open_questions[].owner",
            "outcome.sponsor_goal": "outcome.sponsor_goal",
        }
        for token, want in cases.items():
            self.assertEqual(normalise_path(token, self.catalogue), want, token)
        for token in ("card.json", "cli.py", "e.g", "profile.json"):
            self.assertIsNone(normalise_path(token, self.catalogue), token)

    def test_unknown_path_fails(self):
        self.assertFalse(path_exists(normalise_path("tasks.C1.colour", self.catalogue), self.catalogue))
        self.assertFalse(path_exists(normalise_path("voice.mood", self.catalogue), self.catalogue))
        self.assertTrue(path_exists(normalise_path("tasks.C1.output", self.catalogue), self.catalogue))

    def test_question_id_forms(self):
        text = "source interviews/x.md#F2; question P3; questions F1 to F9; task C1; OQ E4"
        self.assertEqual(QUESTION_ID_RE.findall(text), ["F2", "P3", "F1"])
        self.assertNotIn("F10", valid_question_ids(self.catalogue))

    def test_banned_words_ignore_code(self):
        self.assertEqual(banned_words_in("Write the `provenance` entry."), [])
        self.assertEqual(banned_words_in("Write the provenance entry."), ["provenance"])
        self.assertEqual(banned_words_in("```\nplugin\n```\nfine"), [])

    def test_plugin_refs(self):
        text = "Run `${CLAUDE_PLUGIN_ROOT}/scripts/twincard/cli.py validate <dir>` and " \
               "copy `${CLAUDE_PLUGIN_ROOT}/templates/<x>.md`; see [r](references/r.md)."
        refs = plugin_path_refs(text, SKILLS_DIR / "x")
        self.assertEqual(refs[0][1], PLUGIN / "scripts" / "twincard" / "cli.py")
        self.assertEqual(len(refs), 2)


if __name__ == "__main__":
    unittest.main()
