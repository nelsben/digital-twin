"""Checks for the two client-runtime runbooks (OPS-50).

Covers starter-kit/runbooks/claude-code-scheduled-task.md and
starter-kit/runbooks/claude-tag-routine.md. Standard library only.
"""
import re
import unittest
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
RUNBOOKS = [
    ROOT / "starter-kit" / "runbooks" / "claude-code-scheduled-task.md",
    ROOT / "starter-kit" / "runbooks" / "claude-tag-routine.md",
]

HEADINGS = [
    "What this is",
    "Read this first",
    "Inputs you need",
    "Before you start",
    "Steps",
    "Check it worked",
    "Hand over",
    "What can go wrong",
]

CHECKED_SENTENCE = (
    "Checked 2026-11-16 by the author against the pages listed. "
    "Not yet independently verified: verification-log.md has no rows for this runbook."
)

UNVERIFIED = "**⚠ Unverified:**"
FORBIDDEN = ["partner-kit", "levelled"]

ACCEPTED_HOSTS = {
    "code.claude.com",
    "platform.claude.com",
    "support.claude.com",
    "slack.com",
    "docs.slack.dev",
}

TAG_GROUP_AT_END = re.compile(r"\(\[[A-Z]\](?:, \[[A-Z]\])*\)\.?\s*$")
TAG_USE = re.compile(r"\[([A-Z])\](?!\()")
PAGE_DEF = re.compile(r"^- \[([A-Z])\] \[[^\]]+\]\(([^)]+)\)\s*$")
LINK = re.compile(r"\]\(([^)\s]+)\)")


def read(path):
    return path.read_text(encoding="utf-8")


def sections(text):
    """Map level-2 heading to its body lines."""
    out, current = {}, None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            out[current] = []
        elif current is not None:
            out[current].append(line)
    return out


def accepted_url(url):
    p = urlparse(url)
    if p.scheme != "https":
        return False
    if p.netloc == "claude.com":
        return p.path.startswith("/docs/")
    if p.netloc == "slack.com":
        return p.path.startswith("/help")
    return p.netloc in ACCEPTED_HOSTS


class RunbookChecks(unittest.TestCase):
    def each(self):
        for path in RUNBOOKS:
            with self.subTest(runbook=path.name):
                self.assertTrue(path.is_file(), f"missing file: {path}")
                yield path, read(path)

    def test_files_exist_and_length(self):
        for path, text in self.each():
            n = len(text.splitlines())
            self.assertTrue(110 <= n <= 260, f"{path.name} has {n} lines, want 110 to 260")

    def test_eight_headings_in_order(self):
        for path, text in self.each():
            found = [l[3:].strip() for l in text.splitlines() if l.startswith("## ")]
            self.assertEqual(found, HEADINGS)

    def test_relative_links_resolve(self):
        for path, text in self.each():
            for target in LINK.findall(text):
                if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                    continue
                file_part = target.split("#", 1)[0]
                self.assertTrue(
                    (path.parent / file_part).exists(),
                    f"{path.name}: link does not resolve: {target}",
                )

    def test_numbered_steps_end_with_source_tags_or_unverified(self):
        for path, text in self.each():
            steps = sections(text).get("Steps", [])
            numbered = [l for l in steps if re.match(r"^\d+\.\s", l)]
            self.assertGreaterEqual(len(numbered), 5, f"{path.name}: too few numbered steps")
            for line in numbered:
                self.assertTrue(
                    TAG_GROUP_AT_END.search(line) or UNVERIFIED in line,
                    f"{path.name}: step without source tags or unverified marker: {line[:90]}",
                )

    def test_tags_defined_and_pages_valid(self):
        for path, text in self.each():
            body = sections(text).get("Read this first", [])
            defined = {}
            for line in body:
                m = PAGE_DEF.match(line)
                if m:
                    defined[m.group(1)] = m.group(2)
            self.assertGreaterEqual(len(defined), 3, f"{path.name}: Pages used list is missing")
            for tag, target in defined.items():
                if target.startswith("http"):
                    self.assertTrue(accepted_url(target), f"{path.name}: [{tag}] domain not accepted: {target}")
                else:
                    self.assertTrue(
                        (path.parent / target.split("#", 1)[0]).exists(),
                        f"{path.name}: [{tag}] relative path missing: {target}",
                    )
            used = set(TAG_USE.findall(text)) - set(defined)
            # a definition line itself uses the tag; only undefined tags remain here
            self.assertEqual(used, set(), f"{path.name}: tags used but not defined: {sorted(used)}")
            used_all = set(TAG_USE.findall("\n".join(l for l in text.splitlines() if not PAGE_DEF.match(l))))
            self.assertEqual(
                set(defined) - used_all, set(), f"{path.name}: pages defined but never cited"
            )

    def test_forbidden_strings_absent(self):
        for path, text in self.each():
            for word in FORBIDDEN:
                self.assertNotIn(word, text, f"{path.name} contains {word!r}")

    def test_checked_sentence_present(self):
        for path, text in self.each():
            body = " ".join(sections(text).get("Read this first", []))
            self.assertIn(CHECKED_SENTENCE, " ".join(body.split()))

    def test_role_table_ends_what_this_is(self):
        for path, text in self.each():
            body = [l for l in sections(text).get("What this is", []) if l.strip()]
            self.assertTrue(body and body[-1].startswith("|"), f"{path.name}: role table must end the section")
            self.assertIn("03-stakeholders.md", "\n".join(body))

    def test_inputs_cover_the_decisions(self):
        needles = ["runs as", "autonomy", "06-autonomy.md", "data class", "retention", "connector", "memory", "skill"]
        for path, text in self.each():
            body = "\n".join(sections(text).get("Inputs you need", [])).lower()
            for needle in needles:
                self.assertIn(needle.lower(), body, f"{path.name}: Inputs you need lacks {needle!r}")

    def test_hand_over_and_check_sections_not_empty(self):
        for path, text in self.each():
            secs = sections(text)
            self.assertIn("engagements/", "\n".join(secs["Hand over"]))
            self.assertIn("ten minutes", "\n".join(secs["Check it worked"]))


if __name__ == "__main__":
    unittest.main()
