"""Checks for the compendium follow-ups (OPS-61): the marker conventions, the
connector rows that the runbook checks found stale, and that nothing other files
link to was renamed or removed.

Standard library only. Run with: python3 -m unittest tests.test_compendium_followups
(or: python3 -m unittest discover -s tests)
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPENDIUM = ROOT / "docs" / "compendium"
README = COMPENDIUM / "README.md"
CONNECTORS = COMPENDIUM / "11-connectors.md"
SOURCES = COMPENDIUM / "sources.md"
DATA = ROOT / "partner-kit" / "plugins" / "twin-consultant" / "data"
RUNBOOKS = ROOT / "starter-kit" / "runbooks"

# The marker forms docs/compendium/README.md defines under Conventions.
DEFINED_WARNINGS = ("**⚠ Conflict:**", "**⚠ Unverified:**")
DEFINED_OURS = ("Our recommendation", "Our reading")

# A bold warning label: **⚠ Label...** or ⚠ **Label...**
BOLD_WARNING = re.compile(r"\*\*⚠[^*]*\*\*|⚠ \*\*[^*]*\*\*")
# A plain, unbolded spelling of a defined warning label.
PLAIN_WARNING = re.compile(r"(?<!\*\*)⚠ (?:Unverified|Conflict):")
# A bracketed "Our ..." label, and lowercase spellings of the same labels.
OUR_LABEL = re.compile(r"\((?:\*\*)?(Our [^)*]*?)(?:\*\*)?\)|\((our (?:recommendation|reading|conclusion)[^)]*)\)")
# A bracketed lowercase spelling of a defined label, in any form.
LOWER_OUR = re.compile(r"\(our (?:recommend\w*|reading|conclusion)[^)]*\)?")
ANCHOR_LINK = re.compile(r"docs/compendium/([0-9A-Za-z_-]+\.md)#([A-Za-z0-9_-]+)")

PINNED_HEADINGS = {
    '01-anatomy.md': [
        '## One role, one package (our recommendation)',
        '## The engineering principles behind every decision',
    ],
    '02-persona.md': [
        '## What a persona is',
        '## A persona template (our recommendation)',
        '## Where the persona lives on each surface',
        '## Memory',
    ],
    '03-skills-authoring.md': [
        '## What a skill is',
        '## Skill, connector, persona or CLAUDE.md?',
        '## Frontmatter: write for every surface',
        '## Writing a good description',
        '## Writing the body',
        '## Evaluate first, then iterate',
        '## Skeleton',
    ],
    '04-distribution-governance.md': [
        '## How each surface gets skills',
        '## Recommended pipeline (our recommendation)',
        '## Admin controls on claude.ai',
        '## Governance',
        '## Compliance limits',
        '## Measuring use',
    ],
    '05-decision-matrix.md': [
        '## The options',
        '## Decision criteria',
        '## Decision flow (our recommendation)',
        '## What this means for the pilots (our recommendation)',
    ],
    '06-autonomy.md': [
        '## The ladder (our recommendation)',
        '## How a level is enforced',
        '## Rules for moving up a level',
        '## The trade-off in one line',
    ],
    '07-pilot-roles.md': [
        '## Shared skills (one common plugin for every role)',
        '## By role',
        '## What to capture in role interviews',
    ],
    '08-open-questions.md': [
        '## Decisions needed before building',
        '### Status after the second round (2026-11-14)',
        '### Status after the third round (2026-11-14)',
        '### Status after the fourth round (2026-11-14)',
        '## Questions most first-time builders miss',
        '## Things to research next',
    ],
    '09-plans-and-it-controls.md': [
        '## Feature matrix',
        '## What IT can do on each plan',
        '## What this means for the rollout (our recommendation)',
        "## Traps IT directors don't know to ask about",
    ],
    '10-sensitive-data.md': [
        '## First: "running locally" doesn\'t keep data local',
        "## What ZDR is, and isn't",
        '## What HIPAA covers',
        '## Other controls',
        '## Decision matrix by data class (our recommendation, built from the sources above)',
        '## Design patterns that keep data out of the conversation',
        '## Questions to settle with compliance and legal',
    ],
    '11-connectors.md': [
        '## What exists for our systems',
        "## Adding a connector that isn't in the directory",
        '## Building our own MCP server',
        '## Buying a connector, and reviewing it',
        '## Connectors and sensitive data',
        '## Decision matrix: use, buy, build or host',
    ],
    '12-orgs-and-ownership.md': [
        '## What "ownership" means',
        '## Why more than one org',
        '## Recommended starting point',
        '### Team-plan variant: a non-regulated role (our recommendation)',
        '## The ask, quantified (fill in)',
        '## Questions to bring to Anthropic (as a partner)',
    ],
    '13-devices.md': [
        '## What MDM is',
        '## What you can enforce on each',
        '## Policy by data class and device (our recommendation)',
        '## A hosted twin for unmanaged devices (our recommendation)',
        '## Team plan with no device management',
    ],
    '14-private-equity.md': [
        '## Three facts that shape everything',
        '## What a wall has to guarantee',
        '## Where a twin can leak across a wall',
        '## Salesforce and HubSpot behind a wall',
        '## Three designs',
        '## Designing for both',
        '## The private-equity twin at a glance (our recommendation)',
    ],
    '15-governance-and-performance.md': [
        '## What each source records',
        '## One governance log for all twins (our recommendation)',
        '### Where the log lives: settle it with each customer',
        '## Retention, decided',
        '## Team plan with no device management',
        '## Measuring performance',
        '## Who does what, and how often',
    ],
    '16-oob-skills-and-references.md': [
        '## 1. Skills in github.com/anthropics/skills',
        '## 2. Anthropic plugin marketplaces and plugins',
        '## 3. Skills built into the Claude apps',
        '## 4. Reference index of Anthropic best-practice docs',
        '### Agent Skills: overview and best practices',
        '### Skill authoring',
        '### Evals',
        '### Plugins and marketplaces',
        '### Plugin reference',
        '### Hooks',
        '### Output styles',
        '### Managed settings and permissions',
        '### MCP',
        '### Claude Code security',
        '### Org skills administration on claude.ai',
        '### Prompt engineering and system prompts',
        '## What the starter kit takes from this',
    ],
    '17-anthropic-pe-plugins-review.md': [
        '## The short answer',
        "## 1. What's in `private-equity`",
        "## 2. What's in `financial-analysis`",
        '## 3. Where the data goes: connectors and external tools',
        '## 4. What the deal-team stories layer on',
        '## 5. How to pin a reviewed copy',
        '## 6. Outcome for OD-1',
    ],
    '18-customer-success.md': [
        '## The short answer',
        "## What's in `customer-support`",
        '## Where the data goes: connectors and external tools',
        '## The connectors a customer-success role needs',
        '## Typical customer-success tasks (our recommendation)',
        '## What changes on a Team plan',
    ],
    'README.md': [
        '## What we mean by a digital twin',
        '## Reading order',
        '## The ten things to know first',
        '### Added after the second round of research',
        '## Conventions',
    ],
    'sources.md': [
        '## Agent Skills',
        '## Plugins and administration',
        '## Runtimes',
        '## Connectors, persona and memory',
        '## Engineering principles',
        '## Plans and IT controls (second round)',
        '## Sensitive data (second round)',
        '## Connectors (second round)',
        '## Out-of-the-box skills, plugins and reference docs (page 16)',
        "## Anthropic's private-equity and financial-analysis plugins (page 17)",
        '## Consistency pass (OPS-23, fetched 2026-11-15)',
        '## Customer success (page 18)',
        '## Connectors (OPS-31, fetched 2026-11-15)',
    ],
}


def body_lines(text):
    """Lines outside code fences that are not headings."""
    fence = False
    for line in text.splitlines():
        if line.startswith("```"):
            fence = not fence
            continue
        if fence or re.match(r"^#{1,6} ", line):
            continue
        yield line


def headings(text, levels=(2, 3)):
    found = []
    fence = False
    for line in text.splitlines():
        if line.startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        m = re.match(r"^(#{1,6}) (.+?)\s*$", line)
        if m and len(m.group(1)) in levels:
            found.append("%s %s" % (m.group(1), m.group(2)))
    return found


def slug(heading):
    text = re.sub(r"[^a-z0-9 -]", "", heading.lower())
    return text.strip().replace(" ", "-")


def anchors(page):
    text = (COMPENDIUM / page).read_text(encoding="utf-8")
    return {slug(h.split(" ", 1)[1]) for h in headings(text, levels=(1, 2, 3, 4, 5, 6))}


def table_row(text, label):
    for line in text.splitlines():
        if line.startswith("| **%s**" % label):
            return line
    return None


class MarkerConventionsTest(unittest.TestCase):
    def setUp(self):
        self.readme = README.read_text(encoding="utf-8")

    def test_readme_defines_every_form(self):
        for form in DEFINED_WARNINGS + ("**(Our recommendation):**", "**(Our reading):**"):
            self.assertTrue(("- %s" % form) in self.readme, form)

    def test_conflict_covers_two_sources(self):
        line = next(l for l in self.readme.splitlines() if l.startswith("- **⚠ Conflict:**"))
        self.assertTrue("vendor" in line, line)
        self.assertTrue("We note both values and take the safer one" in line, line)

    def test_every_marker_on_a_page_is_defined(self):
        bad = []
        for page in sorted(COMPENDIUM.glob("*.md")):
            for line in body_lines(page.read_text(encoding="utf-8")):
                if line.startswith("- **(Our") and page == README:
                    continue
                for form in BOLD_WARNING.findall(line):
                    if form not in DEFINED_WARNINGS:
                        bad.append("%s: %s" % (page.name, form))
                for form in PLAIN_WARNING.findall(line):
                    bad.append("%s: plain %s" % (page.name, form))
                rest = line
                for form in DEFINED_WARNINGS:
                    rest = rest.replace(form, "")
                if "⚠" in rest:
                    bad.append("%s: stray ⚠ in %r" % (page.name, line[:80]))
                for form in LOWER_OUR.findall(line):
                    bad.append("%s: lowercase %s" % (page.name, form[:40]))
                for cap, low in OUR_LABEL.findall(line):
                    label = cap or low
                    if label not in DEFINED_OURS:
                        bad.append("%s: (%s)" % (page.name, label))
        self.assertEqual(bad, [])


class ConnectorRowsTest(unittest.TestCase):
    def setUp(self):
        self.text = CONNECTORS.read_text(encoding="utf-8")

    def test_outlook_row(self):
        rows = [l for l in self.text.splitlines() if l.startswith("| **") and "Outlook" in l.split("|")[1]]
        self.assertTrue(rows)

    def test_gmail_and_calendar_carry_the_conflict(self):
        for label in ("Gmail", "Google Calendar"):
            row = table_row(self.text, label)
            self.assertIsNotNone(row, label)
            self.assertFalse("**No.**" in row, label)
            self.assertTrue("⚠ Conflict" in row, label)

    def test_slack_send_tools_are_settled(self):
        row = table_row(self.text, "Slack")
        self.assertIsNotNone(row)
        self.assertFalse("whether the directory connector exposes the send tools" in row)

    def test_help_center_article_in_sources(self):
        self.assertIn("10166901", SOURCES.read_text(encoding="utf-8"))


class NothingBreaksTest(unittest.TestCase):
    def test_cited_anchors_resolve(self):
        files = list(DATA.glob("*.json")) + list((DATA / "industry-packs").glob("*.json")) + list(RUNBOOKS.glob("*.md"))
        checked, bad = 0, []
        cache = {}
        for path in files:
            for page, anchor in ANCHOR_LINK.findall(path.read_text(encoding="utf-8")):
                if page not in cache:
                    cache[page] = anchors(page) if (COMPENDIUM / page).is_file() else set()
                checked += 1
                if anchor not in cache[page]:
                    bad.append("%s -> %s#%s" % (path.relative_to(ROOT), page, anchor))
        self.assertGreater(checked, 100)
        self.assertEqual(bad, [])

    def test_pinned_headings_still_present(self):
        missing = []
        for page, pinned in PINNED_HEADINGS.items():
            found = headings((COMPENDIUM / page).read_text(encoding="utf-8"))
            for heading in pinned:
                if heading not in found:
                    missing.append("%s: %s" % (page, heading))
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
