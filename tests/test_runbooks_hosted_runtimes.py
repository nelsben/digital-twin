"""Checks for the two hosted-runtime runbooks.

starter-kit/runbooks/managed-agents.md and starter-kit/runbooks/agent-sdk-runner.md
follow the shape of the Microsoft 365 connector runbook. For both files:

- the eight level-2 headings exist, in order (managed-agents.md may add
  'Self-hosted' between 'Steps' and 'Check it worked');
- every relative link resolves to an existing file, and an #anchor matches a
  heading in that file;
- 'What this is' ends with the role table that maps names to 03-stakeholders;
- 'Read this first' carries the checked-on sentence and a 'Pages used' list;
- every numbered line under 'Steps' ends with a source-tag group such as
  ([A], [C]) or contains the unverified marker;
- every tag used is defined under 'Pages used', and every defined page is an
  https URL on an accepted domain or a relative path that exists;
- the strings 'partner-kit' and 'levelled' are absent;
- the file is between 130 and 300 lines.

Standard library only. Run with: python3 -m unittest discover -s tests
"""

import os
import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
RUNBOOKS = ROOT / "starter-kit" / "runbooks"

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

FILES = {
    "managed-agents.md": True,  # may carry the optional 'Self-hosted' section
    "agent-sdk-runner.md": False,
}

CHECKED_SENTENCE = re.compile(
    r"Checked 2026-11-16 by the author against the pages listed\. "
    r"Every claim was checked again on \d{4}-\d{2}-\d{2} by a second reader; "
    r"the results are in the \[verification log\]\(verification-log\.md\)\."
)

UNVERIFIED = "**⚠ Unverified:**"

ACCEPTED_DOMAINS = (
    "platform.claude.com",
    "code.claude.com",
    "claude.com",
    "support.claude.com",
)
ACCEPTED_GITHUB_ORGS = ("anthropics", "anthropic-ai", "modelcontextprotocol")

FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`[^`\n]*`")
LINK = re.compile(r"\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
HEADING = re.compile(r"^ {0,3}(#{1,6})\s+(.*?)\s*#*\s*$")
EXTERNAL = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//)", re.IGNORECASE)
NUMBERED = re.compile(r"^\s{0,3}\d+\.\s+\S")
TAG_GROUP_END = re.compile(r"\(\[[A-Z]\](?:,\s*\[[A-Z]\])*\)[.]?\s*$")
TAG_USE = re.compile(r"\[([A-Z])\](?!\()")
PAGE_LINE = re.compile(r"^- \[([A-Z])\]\s+(.*\S)\s*$")


def prose_lines(text):
    """Yield (line number, line) for every line outside a fenced code block."""
    fence = None
    for number, line in enumerate(text.splitlines(), start=1):
        match = FENCE.match(line)
        if match:
            marker = match.group(1)
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
            continue
        if fence is None:
            yield number, line


def slug(heading):
    """GitHub's heading-to-anchor rule."""
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", heading)
    text = text.replace("`", "").replace("*", "")
    text = text.strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def anchors_of(path):
    seen = {}
    found = set()
    for _, line in prose_lines(path.read_text(encoding="utf-8")):
        match = HEADING.match(line)
        if not match:
            continue
        base = slug(match.group(2))
        count = seen.get(base, 0)
        seen[base] = count + 1
        found.add(base if count == 0 else "%s-%d" % (base, count))
    return found


def level2_sections(text):
    """Return [(heading, [lines])] for each level-2 heading outside code fences."""
    sections = []
    for _, line in prose_lines(text):
        match = HEADING.match(line)
        if match and len(match.group(1)) == 2:
            sections.append((match.group(2).strip(), []))
        elif sections:
            sections[-1][1].append(line)
    return sections


def fenced_aware_section_lines(text, title):
    """Lines of one level-2 section, code fences included, for step checks."""
    lines = text.splitlines()
    inside = False
    fence = None
    out = []
    for line in lines:
        match = FENCE.match(line)
        if match:
            marker = match.group(1)
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
        heading = None if fence is not None or match else HEADING.match(line)
        if heading and len(heading.group(1)) == 2:
            inside = heading.group(2).strip() == title
            continue
        if inside:
            out.append((line, fence is not None or bool(match)))
    return out


def link_problem(source, target):
    file_part, _, anchor = target.partition("#")
    resolved = source if not file_part else Path(os.path.normpath(source.parent / unquote(file_part)))
    if not resolved.exists():
        return "target %s does not exist" % resolved
    if anchor and resolved.is_file() and resolved.suffix == ".md":
        if unquote(anchor).lower() not in anchors_of(resolved):
            return "no heading in %s gives the anchor #%s" % (resolved.name, anchor)
    return None


def accepted_url(url):
    parsed = urlparse(url)
    if parsed.scheme != "https":
        return False
    host = parsed.hostname or ""
    if host in ACCEPTED_DOMAINS or host.endswith(".claude.com"):
        return True
    if host in ("github.com", "www.github.com"):
        parts = [p for p in parsed.path.split("/") if p]
        return bool(parts) and parts[0] in ACCEPTED_GITHUB_ORGS
    return False


class HostedRuntimeRunbookTests(unittest.TestCase):
    def each_file(self):
        for name, may_self_host in FILES.items():
            path = RUNBOOKS / name
            self.assertTrue(path.is_file(), "missing runbook: %s" % path)
            yield path, may_self_host, path.read_text(encoding="utf-8")

    def test_headings_in_order(self):
        for path, may_self_host, text in self.each_file():
            titles = [title for title, _ in level2_sections(text)]
            expected = list(HEADINGS)
            if may_self_host and "Self-hosted" in titles:
                expected.insert(expected.index("Check it worked"), "Self-hosted")
            self.assertEqual(titles, expected, "%s: level-2 headings" % path.name)

    def test_managed_agents_has_self_hosted_section(self):
        text = (RUNBOOKS / "managed-agents.md").read_text(encoding="utf-8")
        titles = [title for title, _ in level2_sections(text)]
        self.assertIn("Self-hosted", titles)

    def test_relative_links_resolve(self):
        for path, _, text in self.each_file():
            for number, line in prose_lines(text):
                for target in LINK.findall(INLINE_CODE.sub("", line)):
                    if EXTERNAL.match(target):
                        continue
                    problem = link_problem(path, target)
                    self.assertIsNone(problem, "%s line %d: %s (%s)" % (path.name, number, problem, target))

    def test_role_table_ends_what_this_is(self):
        for path, _, text in self.each_file():
            sections = dict(level2_sections(text))
            lines = [l for l in sections.get("What this is", []) if l.strip()]
            self.assertTrue(lines, "%s: empty 'What this is'" % path.name)
            self.assertTrue(lines[-1].lstrip().startswith("|"), "%s: 'What this is' must end with the role table" % path.name)
            joined = "\n".join(lines)
            self.assertIn("| Name used here | Role in 03-stakeholders |", joined, path.name)
            self.assertIn("docs/playbook/03-stakeholders.md", joined, path.name)

    def test_checked_sentence_and_pages_used(self):
        for path, _, text in self.each_file():
            sections = dict(level2_sections(text))
            body = "\n".join(sections.get("Read this first", []))
            self.assertRegex(body, CHECKED_SENTENCE, "%s: checked sentence" % path.name)
            self.assertIn("Pages used", body, "%s: Pages used" % path.name)
            self.assertIn("How sources are marked", body, "%s: how sources are marked" % path.name)
            self.assertTrue(self.pages_used(text), "%s: no pages listed" % path.name)

    def pages_used(self, text):
        sections = dict(level2_sections(text))
        pages = {}
        for line in sections.get("Read this first", []):
            match = PAGE_LINE.match(line)
            if match:
                pages[match.group(1)] = match.group(2)
        return pages

    def test_steps_end_with_source_tags(self):
        for path, _, text in self.each_file():
            numbered = 0
            for line, in_fence in fenced_aware_section_lines(text, "Steps"):
                if in_fence or not NUMBERED.match(line):
                    continue
                numbered += 1
                ok = TAG_GROUP_END.search(line) or UNVERIFIED in line
                self.assertTrue(ok, "%s: numbered step without a source-tag group or the unverified marker: %s" % (path.name, line[:100]))
            self.assertGreaterEqual(numbered, 5, "%s: too few numbered steps" % path.name)

    def test_tags_defined_and_pages_valid(self):
        for path, _, text in self.each_file():
            pages = self.pages_used(text)
            used = set()
            for _, line in prose_lines(text):
                if PAGE_LINE.match(line):
                    continue
                stripped = INLINE_CODE.sub("", line)
                for tag in TAG_USE.findall(stripped):
                    used.add(tag)
            undefined = sorted(used - set(pages))
            self.assertFalse(undefined, "%s: tags used but not defined: %s" % (path.name, undefined))
            for tag, entry in pages.items():
                targets = LINK.findall(entry)
                self.assertTrue(targets, "%s: page [%s] has no link" % (path.name, tag))
                for target in targets:
                    if EXTERNAL.match(target):
                        self.assertTrue(accepted_url(target), "%s: page [%s] is not on an accepted domain: %s" % (path.name, tag, target))
                    else:
                        problem = link_problem(path, target)
                        self.assertIsNone(problem, "%s: page [%s]: %s" % (path.name, tag, problem))

    def test_forbidden_strings_absent(self):
        for path, _, text in self.each_file():
            lowered = text.lower()
            for word in ("partner-kit", "levelled"):
                self.assertNotIn(word, lowered, "%s contains %r" % (path.name, word))

    def test_length(self):
        for path, _, text in self.each_file():
            count = len(text.splitlines())
            self.assertTrue(130 <= count <= 300, "%s has %d lines, expected 130 to 300" % (path.name, count))


if __name__ == "__main__":
    unittest.main()
