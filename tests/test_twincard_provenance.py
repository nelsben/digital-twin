"""Every answered field on the two fixture persona cards is supported by the answer it cites.

The persona card's promise is that each field traces to a source (partner-kit/docs/design.md,
section 4.3). This test keeps that true for the two fictional fixtures. For every provenance
entry whose status is answered:

* a source under interviews/ must name a file that exists, a question id that the field
  catalogue (partner-kit/plugins/twin-consultant/data/fields.json) lists in asked_by for the
  field, a heading for that question (in the section for the task, for a task field), and an
  answer under it that is not empty and not a 'not asked' placeholder. For a task field whose
  catalogue type is enum, the answer must also contain the card's value (case-insensitive,
  hyphens read as spaces) or one of the words the interview guide's 'Listen for' lines map to
  that value (ENUM_WORDS below).
* a source that names a discovery answer (discovery#A1, or ../../discovery.md#A1 for a file
  above the persona folder) must name a question id in asked_by; when the discovery file is
  there, the question must have a non-empty answer in it, and an integer field's number must
  appear in that answer.
* any other source on an answered entry fails: an answered field cites an interview or a
  discovery answer.

Standard library only. Run with: python3 -m unittest discover -s tests
"""

import copy
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN_DIR = ROOT / "partner-kit" / "plugins" / "twin-consultant"
CATALOGUE = PLUGIN_DIR / "data" / "fields.json"
GUIDE = PLUGIN_DIR / "templates" / "interview-guide.md"

FIXTURES = {
    "pe": ROOT / "engagements" / "sample-pe" / "personas" / "deal-team-associate",
    "team": ROOT / "engagements" / "sample-team-cs" / "personas" / "customer-success-manager",
}

# Words the interview guide's 'Listen for' lines map to each allowed value of an enum task
# field, as regular expressions over lower-cased text in which hyphens read as spaces. The
# value itself (for example 'highly sensitive') always counts and is not repeated here.
ENUM_WORDS = {
    "tasks[].trigger": {
        "person": [r"\bperson\b", r"\bi start", r"\bstart(?:s|ed)? it\b", r"\bmyself\b", r"\bi do\b", r"\bme\b"],
        "schedule-own": [r"\bschedule\b", r"\bevery\b", r"\bmy own\b"],
        "schedule-team": [r"\bteam\b", r"\bchannel\b", r"\bshared?\b"],
        "event": [r"\bevent\b", r"\barriv", r"\balert", r"\bfires?\b", r"\bhappen", r"\bsets? it off\b", r"\bwebhook"],
    },
    "tasks[].inputs[].access": {
        "read": [r"\bread", r"\blook", r"\bview"],
        "write": [r"\bwrit", r"\bfill(?:s|ed)? (?:it )?in\b", r"\bchange", r"\bupdate", r"\bedit"],
    },
    "tasks[].output.audience": {
        "self": [r"\bjust for me\b", r"\bonly me\b"],
        "internal": [r"\binternal", r"\bcompany\b", r"\bfirm\b", r"\binside\b", r"\bin house\b"],
        "other-team": [r"\bother team\b", r"\banother team\b", r"\bdepartment\b"],
        "external": [r"\bexternal", r"\bcustomers?\b", r"\binvestors?\b", r"\boutside\b", r"\bclients?\b"],
    },
    "tasks[].writes[].action": {
        "create": [r"\bcreate", r"\badd(?:s|ed)?\b", r"\bnew one\b"],
        "update": [r"\bupdate", r"\bchange", r"\bedit"],
        "delete": [r"\bdelete", r"\bremove"],
        "send": [r"\bsend", r"\bsent\b", r"\bpost", r"\bemail"],
    },
    "tasks[].data_class": {
        "internal": [r"\binternal", r"\beveryday\b", r"\bordinary\b"],
        "confidential": [r"\bconfidential", r"\bnot for sharing\b"],
        "highly-sensitive": [r"\bvery sensitive\b", r"\breal harm\b", r"\bleak"],
        "phi": [r"\bphi\b", r"\bhealth information\b"],
    },
    "tasks[].cost_of_mistake.level": {
        "low": [r"\bfix it in a minute\b"],
        "medium": [r"\brework\b", r"\bawkward conversation\b", r"\blost afternoon\b"],
        "high": [r"\bmoney lost\b", r"\bcustomer upset\b", r"\brule broken\b", r"\bheadline\b"],
    },
}

PLACEHOLDER = re.compile(r"^\W*(?:not asked|not applicable|n/?a|skipped|tbd|todo)\b", re.IGNORECASE)
INTERVIEW_HEADING = re.compile(r"^#{3,4}\s+([PF]\d+)\b")
DISCOVERY_SOURCE = re.compile(r"^(?:(?:\.\./)+discovery\.md|discovery(?:\.md)?)#([A-G]\d+)$")
TOKEN = re.compile(r"[^.\[\]]+|\[\d+\]")


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def list_paths(catalogue, record="card"):
    """Catalogue list prefixes such as 'tasks[]' and 'tasks[].inputs[]'."""
    out = set()
    for entry in catalogue["fields"]:
        if entry["record"] != record:
            continue
        pieces = entry["path"].split(".")
        for i, piece in enumerate(pieces):
            if piece.endswith("[]"):
                out.add(".".join(pieces[: i + 1]))
    return out


def catalogue_path(concrete, lists):
    """Map a provenance path such as tasks.C3.inputs[0].access to tasks[].inputs[].access."""
    tokens = TOKEN.findall(concrete)
    out, i = [], 0
    while i < len(tokens):
        token = tokens[i]
        out.append(token)
        i += 1
        if ".".join(out) + "[]" in lists:
            out[-1] += "[]"
            if i < len(tokens):
                i += 1  # the id (keyed list) or the [n] position (positional list)
    return ".".join(out)


def card_value(card, concrete):
    node = card
    for token in TOKEN.findall(concrete):
        if token.startswith("["):
            node = node[int(token[1:-1])]
        elif isinstance(node, list):
            node = next(item for item in node if item.get("id") == token or item.get("metric") == token)
        else:
            node = node[token]
    return node


def interview_sections(text):
    """Return {(task id or None, question id): answer text} for one notes file.

    A question under a 'Task id: X' line belongs to task X; a persona question has task None.
    """
    sections, task, key, lines = {}, None, None, []

    def close():
        if key is not None:
            sections[key] = " ".join(line.strip() for line in lines if line.strip())

    for line in text.splitlines():
        found = re.match(r"^\s*Task id:\s*(\S+)", line)
        if found:
            task = found.group(1)
            continue
        if re.match(r"^##\s", line):
            close()
            key, lines = None, []
            if not re.match(r"^##\s+Task block", line):
                task = None
            continue
        heading = INTERVIEW_HEADING.match(line)
        if heading:
            close()
            qid = heading.group(1)
            key, lines = (task if qid.startswith("F") else None, qid), []
            continue
        if key is not None:
            lines.append(line)
    close()
    return sections


def normal(text):
    return re.sub(r"\s+", " ", text.lower().replace("-", " "))


def states_enum_value(catalogue_field, value, text):
    """True when the answer holds the value itself or a word the guide maps to it."""
    text = normal(text)
    literal = re.escape(normal(str(value)))
    if re.search(r"\b" + literal + r"(?:s|d|ed|ing)?\b", text):
        return True
    return any(re.search(pattern, text) for pattern in ENUM_WORDS[catalogue_field][value])


def discovery_answer(text, qid):
    """The answer cell of discovery.md's table row for a question id, or None."""
    for line in text.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and cells[0] == qid:
            return cells[2]
    return None


def check_card(persona_dir, card=None, catalogue=None):
    """Return a list of problems for the answered provenance entries of one persona card."""
    persona_dir = Path(persona_dir)
    catalogue = catalogue or load_json(CATALOGUE)
    card = card if card is not None else load_json(persona_dir / "card.json")
    fields = {entry["path"]: entry for entry in catalogue["fields"] if entry["record"] == "card"}
    lists = list_paths(catalogue)
    problems, cache = [], {}

    for path, prov in sorted(card["provenance"].items()):
        if prov.get("status") != "answered":
            continue
        source = prov.get("source", "")
        where = "%s (%s)" % (path, source)
        cpath = catalogue_path(path, lists)
        entry = fields.get(cpath)
        if entry is None:
            problems.append("%s: no catalogue field %s" % (where, cpath))
            continue
        if "#" not in source:
            problems.append("%s: an answered entry must cite a question id after #" % where)
            continue
        target, qid = source.rsplit("#", 1)
        if qid not in entry["asked_by"]:
            problems.append("%s: question %s is not in asked_by %s for %s" % (where, qid, entry["asked_by"], cpath))
            continue

        discovery = DISCOVERY_SOURCE.match(source)
        if source.startswith("interviews/"):
            notes = persona_dir / target
            if not notes.is_file():
                problems.append("%s: file does not exist" % where)
                continue
            if notes not in cache:
                cache[notes] = interview_sections(notes.read_text(encoding="utf-8"))
            sections = cache[notes]
            if cpath.startswith("tasks[]"):
                task = path.split(".")[1]
                answers = [sections.get((task, qid))]
                missing = "no heading %s under task %s" % (qid, task)
            elif qid.startswith("F"):
                answers = [text for (task, q), text in sections.items() if q == qid and task is not None]
                answers = [text for text in answers if text.strip()] or [None]
                missing = "no heading %s in any task block" % qid
            else:
                answers = [sections.get((None, qid))]
                missing = "no heading %s" % qid
            if answers == [None]:
                problems.append("%s: %s" % (where, missing))
                continue
            text = " ".join(answer for answer in answers if answer)
            if not text.strip() or PLACEHOLDER.match(text):
                problems.append("%s: the answer under %s is empty or a 'not asked' placeholder" % (where, qid))
                continue
            if entry["type"] == "enum" and cpath.startswith("tasks[]"):
                value = card_value(card, path)
                if not states_enum_value(cpath, value, text):
                    problems.append("%s: the answer under %s does not state %r: %s" % (where, qid, value, text))
        elif discovery:
            file_part = target
            if file_part.endswith(".md"):
                discovery_file = (persona_dir / file_part).resolve()
                if not discovery_file.is_file():
                    problems.append("%s: discovery file does not exist" % where)
                    continue
                answer = discovery_answer(discovery_file.read_text(encoding="utf-8"), qid)
                if not answer or PLACEHOLDER.match(answer):
                    problems.append("%s: discovery has no answer for %s" % (where, qid))
                    continue
                if entry["type"] == "integer":
                    value = card_value(card, path)
                    if not re.search(r"(?<!\d)%d(?!\d)" % value, answer):
                        problems.append("%s: the discovery answer does not state %r: %s" % (where, value, answer))
        else:
            problems.append("%s: an answered entry cites an interview or a discovery answer" % where)
    return problems


class ProvenanceTests(unittest.TestCase):
    def test_word_lists_cover_the_enum_task_fields(self):
        """Every enum task field of the catalogue has a word list for each of its values."""
        catalogue = load_json(CATALOGUE)
        guide = GUIDE.read_text(encoding="utf-8")
        enum_fields = {e["path"]: e["values"] for e in catalogue["fields"]
                       if e["record"] == "card" and e["type"] == "enum" and e["path"].startswith("tasks[]")}
        self.assertEqual(sorted(enum_fields), sorted(ENUM_WORDS))
        for path, values in enum_fields.items():
            with self.subTest(path=path):
                self.assertEqual(sorted(ENUM_WORDS[path]), sorted(values))
                for value in values:
                    self.assertIn("`%s`" % value, guide, "%s is not a value in the interview guide" % value)

    def _check(self, name):
        persona_dir = FIXTURES[name]
        card = load_json(persona_dir / "card.json")
        answered = [p for p, v in card["provenance"].items() if v.get("status") == "answered"]
        self.assertGreater(len(answered), 50, "too few answered entries to be the fixture")
        problems = check_card(persona_dir)
        self.assertEqual(problems, [], "\n" + "\n".join(problems))

    def test_private_equity_card_answers_are_supported(self):
        self._check("pe")

    def test_team_card_answers_are_supported(self):
        self._check("team")

    def test_checker_fails_on_an_entry_that_cites_the_wrong_question(self):
        """The checker must catch a source whose question the catalogue does not list."""
        persona_dir = FIXTURES["team"]
        card = load_json(persona_dir / "card.json")
        # tasks.C1.data_class is asked by C1 and F2; the notes' answer to F4 is about mistakes.
        wrong = copy.deepcopy(card)
        wrong["provenance"]["tasks.C1.data_class"]["source"] = "interviews/2026-11-06-csm.md#F4"
        problems = check_card(persona_dir, card=wrong)
        self.assertTrue(any("tasks.C1.data_class" in p and "not in asked_by" in p for p in problems), problems)
        # The unchanged card has no such problem for that entry.
        self.assertFalse(any("tasks.C1.data_class" in p for p in check_card(persona_dir, card=card)))


if __name__ == "__main__":
    unittest.main()
