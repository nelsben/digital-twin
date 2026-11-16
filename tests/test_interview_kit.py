"""Interview guide and notes template agree with the field catalogue (OPS-27)."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "partner-kit" / "plugins" / "twin-consultant"
GUIDE = PLUGIN / "templates" / "interview-guide.md"
NOTES = PLUGIN / "templates" / "interview-notes.md"
FIELDS = PLUGIN / "data" / "fields.json"
DISCOVERY = ROOT / "docs" / "playbook" / "02-discovery.md"

QUESTION_IDS = ["P%d" % i for i in range(1, 7)] + ["F%d" % i for i in range(1, 10)]
BANNED = ["claude", "mcp", "connector", "plugin", "skill", "runtime", "autonomy",
          "zdr", "mnpi", "phi", "data class", "provenance"]


def parse_guide():
    """Return {id: {"ask": str, "probes": [str], "fills": [str], "listen": str, "why": str}}."""
    text = GUIDE.read_text(encoding="utf-8")
    parts = re.split(r"(?m)^### ((?:P|F)\d+)\b.*$", text)
    out, order = {}, []
    for i in range(1, len(parts), 2):
        qid, body = parts[i], parts[i + 1]
        # stop at the next level-2 heading
        body = re.split(r"(?m)^## ", body)[0]
        order.append(qid)
        ask = re.search(r"(?m)^\*\*Ask:\*\*\s*(.+)$", body)
        why = re.search(r"(?m)^\*\*Why we ask:\*\*\s*(.+)$", body)
        fills = re.search(r"(?m)^\*\*Fills:\*\*\s*(.+)$", body)
        probes = re.search(r"\*\*Probes:\*\*\n((?:- .+\n?)+)", body)
        listen = re.search(r"\*\*Listen for:\*\*\n((?:- .+\n?)+)", body)
        out[qid] = {
            "ask": ask.group(1) if ask else "",
            "why": why.group(1) if why else "",
            "fills": re.findall(r"`([^`]+)`", fills.group(1)) if fills else [],
            "probes": [p[2:] for p in probes.group(1).strip().split("\n")] if probes else [],
            "listen": listen.group(1) if listen else "",
        }
    return out, order


class InterviewKitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cat = json.loads(FIELDS.read_text(encoding="utf-8"))
        cls.card = {f["path"]: f for f in cls.cat["fields"] if f["record"] == "card"}
        cls.guide, cls.order = parse_guide()

    def test_each_question_once(self):
        self.assertEqual(sorted(self.order), sorted(QUESTION_IDS))
        self.assertEqual(len(self.order), len(set(self.order)))

    def test_question_parts_present(self):
        for qid, q in self.guide.items():
            self.assertTrue(q["ask"], qid + ": Ask")
            self.assertTrue(q["why"], qid + ": Why we ask")
            self.assertTrue(q["fills"], qid + ": Fills")
            self.assertIn(len(q["probes"]), (1, 2), qid + ": probes")

    def test_guide_section_order(self):
        text = GUIDE.read_text(encoding="utf-8")
        heads = re.findall(r"(?m)^## (.+)$", text)
        low = [h.lower() for h in heads]
        want = ["before the interview", "persona", "task", "closing", "after the interview"]
        pos = [next(i for i, h in enumerate(low) if w in h) for w in want]
        self.assertEqual(pos, sorted(pos))
        closing = re.split(r"(?m)^## ", text.split("## ")[[i for i, h in enumerate(low) if "closing" in h][0] + 1])[0]
        self.assertLessEqual(len(re.findall(r"(?m)^\d+\. ", closing)), 3)

    def test_fills_paths_exist_for_card(self):
        for qid, q in self.guide.items():
            for p in q["fills"]:
                self.assertIn(p, self.card, "%s fills unknown card path %s" % (qid, p))

    def test_fills_and_asked_by_agree(self):
        for qid, q in self.guide.items():
            for p in q["fills"]:
                self.assertIn(qid, self.card[p]["asked_by"], "%s fills %s but asked_by lacks it" % (qid, p))
        for path, f in self.card.items():
            for qid in f["asked_by"]:
                if qid in QUESTION_IDS:
                    self.assertIn(path, self.guide[qid]["fills"], "%s asked_by %s but not in its Fills" % (path, qid))

    def test_asked_by_ids_exist(self):
        disc = set(re.findall(r"(?m)^\| ([A-G]\d+) \|", DISCOVERY.read_text(encoding="utf-8")))
        for f in self.cat["fields"]:
            for qid in f["asked_by"]:
                if qid in QUESTION_IDS:
                    self.assertIn(qid, self.guide)
                else:
                    self.assertIn(qid, disc, "%s: %s not in discovery" % (f["path"], qid))

    def test_required_fields_covered(self):
        filled = {p for q in self.guide.values() for p in q["fills"]}
        for path, f in self.card.items():
            if f["part"] in ["A%d" % i for i in range(1, 9)] and f["required"] and not f["key"]:
                d = f["default"]
                has_default = bool(d and d.get("source"))
                self.assertTrue(path in filled or has_default, "uncovered: " + path)

    def test_listen_for_covers_enum_values(self):
        for qid, q in self.guide.items():
            for p in q["fills"]:
                f = self.card[p]
                if f["type"] in ("enum", "enum-list"):
                    self.assertTrue(q["listen"], "%s: Listen for needed for %s" % (qid, p))
                    for v in f["values"]:
                        self.assertIn("`%s`" % v, q["listen"], "%s: Listen for lacks %s" % (qid, v))

    def test_notes_has_slot_per_question(self):
        text = NOTES.read_text(encoding="utf-8")
        heads = "\n".join(re.findall(r"(?m)^#{2,5} .*$", text))
        for qid in QUESTION_IDS:
            self.assertRegex(heads, r"\b%s\b" % qid)
        for word in ["customer", "persona", "date", "role", "interviewer", "feature", "open question",
                     "interviews/", "redact", "sample-"]:
            self.assertIn(word, text.lower())
        self.assertRegex(text, r"interviews/\d{4}-\d{2}-\d{2}-[a-z-]+\.md#F1")

    def test_no_banned_words_in_spoken_text(self):
        for qid, q in self.guide.items():
            for s in [q["ask"]] + q["probes"]:
                for w in BANNED:
                    self.assertIsNone(re.search(r"\b%s\b" % re.escape(w), s, re.I), "%s uses '%s': %s" % (qid, w, s))

    def test_readme_lists_templates(self):
        r = (PLUGIN / "README.md").read_text(encoding="utf-8")
        self.assertIn("templates/interview-guide.md", r)
        self.assertIn("templates/interview-notes.md", r)
        self.assertNotRegex(r, r"(?i)interview guide and notes templates")


if __name__ == "__main__":
    unittest.main()
