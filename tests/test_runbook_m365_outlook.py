"""Shape checks for section 6a (Outlook mail and calendar) of the Microsoft 365 runbook.

Standard library only. Run with: python3 -m unittest tests.test_runbook_m365_outlook
"""

import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
RUNBOOK = ROOT / "starter-kit" / "runbooks" / "microsoft-365-connector.md"
README = ROOT / "starter-kit" / "README.md"

H6A = "## 6a. Outlook mail and calendar"
KEPT = [
    "## 1. Prerequisites",
    "## 2. Decide what to approve before consent",
    "## 3. Grant tenant admin consent",
    "## 4. Enable the connector for the right group (Entra side)",
    "## 5. Enable the connector for the right Claude group",
    "## 6. Keep write tools off (autonomy level 1)",
    "## 7. Plan the SharePoint wall before testing",
    "## 8. Check that deal-team libraries are not readable by walled groups",
    "## 9. Hand over",
]
HOSTS = {"learn.microsoft.com", "support.claude.com", "claude.com", "support.microsoft.com"}


def lines():
    return RUNBOOK.read_text(encoding="utf-8").splitlines()


def section():
    ls = lines()
    start = ls.index(H6A)
    end = next(i for i in range(start + 1, len(ls)) if ls[i].startswith("## "))
    return ls[start:end]


class Section6a(unittest.TestCase):
    def test_heading_order(self):
        ls = lines()
        self.assertIn(H6A, ls)
        i6 = next(i for i, l in enumerate(ls) if l.startswith("## 6. "))
        i7 = next(i for i, l in enumerate(ls) if l.startswith("## 7. "))
        self.assertTrue(i6 < ls.index(H6A) < i7)

    def test_headings_kept(self):
        ls = lines()
        for h in KEPT:
            self.assertIn(h, ls)

    def test_length(self):
        body = [l for l in section() if l.strip()]
        self.assertTrue(15 <= len(body) <= 45, len(body))
        self.assertLessEqual(len(section()), 46)

    def test_required_text(self):
        t = "\n".join(section())
        for s in ("Blocked", "Needs approval", "(Our recommendation):",
                  "docs/compendium/18-customer-success.md",
                  "was checked again on 2026-11-16 by a second reader"):
            self.assertIn(s, t)

    def test_https_hosts(self):
        t = "\n".join(section())
        for u in re.findall(r"https://[^\s)>\]]+", t):
            self.assertIn(urlparse(u).hostname, HOSTS, u)

    def test_relative_links_resolve(self):
        t = RUNBOOK.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)\s]+)\)", t):
            if re.match(r"[a-z]+:", target) or target.startswith("#"):
                continue
            path = unquote(target.split("#")[0])
            self.assertTrue((RUNBOOK.parent / path).exists(), target)

    def test_warning_signs_in_labels(self):
        t = "\n".join(section())
        t = t.replace("**⚠ Conflict:**", "").replace("**⚠ Unverified:**", "")
        self.assertNotIn("⚠", t)

    def test_readme_row(self):
        row = next(l for l in README.read_text(encoding="utf-8").splitlines()
                   if "runbooks/microsoft-365-connector.md" in l)
        self.assertIn("Outlook", row)


if __name__ == "__main__":
    unittest.main()
