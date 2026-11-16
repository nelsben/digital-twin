"""Link checks for the playbook and the READMEs a consultant starts from.

Every relative markdown link in docs/playbook/*.md, README.md, CLAUDE.md,
starter-kit/README.md, partner-kit/README.md, engagements/README.md and
engagements/sample-pe/README.md must resolve to an existing file or folder.
When it carries an #anchor and the target is a markdown file, the anchor must
match a heading in that file, by GitHub's rule: lower case, spaces to hyphens,
punctuation dropped. The playbook README must list every numbered page.

Standard library only. Run with: python3 -m unittest discover -s tests
"""

import os
import re
import unittest
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
PLAYBOOK = ROOT / "docs" / "playbook"

CHECKED = sorted(PLAYBOOK.glob("*.md")) + [
    ROOT / "README.md",
    ROOT / "CLAUDE.md",
    ROOT / "starter-kit" / "README.md",
    ROOT / "partner-kit" / "README.md",
    ROOT / "engagements" / "README.md",
    ROOT / "engagements" / "sample-pe" / "README.md",
]

FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`[^`\n]*`")
LINK = re.compile(r"\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
HEADING = re.compile(r"^ {0,3}(#{1,6})\s+(.*?)\s*#*\s*$")
EXTERNAL = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//)", re.IGNORECASE)


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
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", heading)  # links keep their text
    text = text.replace("`", "").replace("*", "")
    text = text.strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)  # punctuation dropped
    return text.replace(" ", "-")


_anchor_cache = {}


def anchors_of(path):
    """The set of anchors a markdown file offers, repeated headings numbered."""
    if path not in _anchor_cache:
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
        _anchor_cache[path] = found
    return _anchor_cache[path]


def relative_links(path):
    """Yield (line number, target) for each relative link in a markdown file."""
    for number, line in prose_lines(path.read_text(encoding="utf-8")):
        for target in LINK.findall(INLINE_CODE.sub("", line)):
            if not EXTERNAL.match(target):
                yield number, target


def shown(path):
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def problem_with(source, target):
    """Return a sentence naming what is wrong with a link, or None."""
    file_part, _, anchor = target.partition("#")
    resolved = source if not file_part else Path(os.path.normpath(source.parent / unquote(file_part)))
    if not resolved.exists():
        return "target %s does not exist" % shown(resolved)
    if anchor and resolved.is_file() and resolved.suffix == ".md":
        if unquote(anchor).lower() not in anchors_of(resolved):
            return "no heading in %s gives the anchor #%s" % (shown(resolved), anchor)
    return None


class PlaybookLinkTests(unittest.TestCase):
    def test_checked_files_exist(self):
        for path in CHECKED:
            with self.subTest(file=str(path.relative_to(ROOT))):
                self.assertTrue(path.is_file(), "%s is missing" % path.relative_to(ROOT))

    def test_every_relative_link_resolves(self):
        for path in CHECKED:
            if not path.is_file():
                continue
            with self.subTest(file=str(path.relative_to(ROOT))):
                broken = []
                for number, target in relative_links(path):
                    problem = problem_with(path, target)
                    if problem:
                        broken.append("line %d: (%s) %s" % (number, target, problem))
                self.assertEqual(broken, [], "\n" + "\n".join(broken))

    def test_playbook_readme_lists_every_numbered_page(self):
        readme = PLAYBOOK / "README.md"
        listed = {
            Path(unquote(target.partition("#")[0])).name
            for _, target in relative_links(readme)
            if target.partition("#")[0].endswith(".md")
        }
        pages = sorted(p.name for p in PLAYBOOK.glob("[0-9][0-9]-*.md"))
        self.assertTrue(pages, "no numbered pages found in docs/playbook")
        missing = [name for name in pages if name not in listed]
        self.assertEqual(missing, [], "docs/playbook/README.md does not list: %s" % ", ".join(missing))


class SlugTests(unittest.TestCase):
    def test_github_rule(self):
        self.assertEqual(slug("Decision flow (our recommendation)"), "decision-flow-our-recommendation")
        self.assertEqual(slug("How to publish to groups"), "how-to-publish-to-groups")
        self.assertEqual(slug("8a. List the `permissions` on each library"), "8a-list-the-permissions-on-each-library")
        self.assertEqual(slug("Team plan: no SCIM, no group targeting"), "team-plan-no-scim-no-group-targeting")

    def test_headings_with_a_letter_prefix(self):
        path = ROOT / "docs" / "playbook" / "02-discovery.md"
        self.assertIn("a-sponsor-and-scope", anchors_of(path))


if __name__ == "__main__":
    unittest.main()
