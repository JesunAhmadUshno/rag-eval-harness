"""Portfolio standard checks: the required files exist and no public file carries a grade.

No lock test yet: PROPOSAL.md is a draft. When it is locked by tag proposal-v1, add a test that pins
its SHA-256 as committed at the lock commit.
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQUIRED = ["README.md", "PROPOSAL.md", "REPORT.md", "CHANGELOG.md", "CITATION.cff", "SECURITY.md", "LICENSE",
            "reproduce.sh", "docs/decisions", "level-1-learn/README.md", "level-2-build/README.md",
            "level-3-deep/README.md", "level-3-deep/results_deep.json", "real-data/results_real.json",
            "real-data/results_paired_stats.json", "model-metrics/calibration.json"]
# Grades are internal. These are the forms they took in this repo before the standard v2 migration.
GRADE = re.compile(r"\d[\d,]* of 10,000|10,000 scale|house scale|\d+\s*/\s*10000\b|[Gg]rade(?: at v[\d.]+)?:\s*\d"
                   r"|\bGrade,? v\d|[Pp]ublicity grade|\d of 1,000\b|Grade [A-D][+-]?\b")
SKIP_DIRS = {".git", "node_modules", "dist", "samples", "generated", "data"}
TEXT = (".md", ".jsx", ".js", ".mjs", ".html", ".cff", ".yml", ".py")


def public_text_files():
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if name.endswith(TEXT) and name != "test_layout.py":
                yield os.path.join(base, name)


class LayoutTest(unittest.TestCase):
    def test_required_files_exist(self):
        missing = [p for p in REQUIRED if not os.path.exists(os.path.join(ROOT, p))]
        self.assertEqual(missing, [], "missing: " + ", ".join(missing))

    def test_readme_opens_with_the_abstract(self):
        with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as f:
            text = f.read()
        for field in ("**Question.**", "**Headline.**", "**Field.**", "**Job family.**", "**Verdict.**",
                      "## Reproduce", "## Lifecycle", "## Layout"):
            self.assertIn(field, text)

    def test_no_public_grade(self):
        hits = []
        for path in public_text_files():
            with open(path, encoding="utf-8", errors="replace") as f:
                for n, line in enumerate(f, 1):
                    if GRADE.search(line):
                        hits.append(f"{os.path.relpath(path, ROOT)}:{n}: {line.strip()[:80]}")
        self.assertEqual(hits, [], "grades are internal:\n" + "\n".join(hits))

    def test_grade_pattern_catches_the_old_forms(self):
        for old in ("Project grade at v1.2: 9,050 of 10,000", "Grade, v1.1: 8,000", "Grades on the house 10,000 scale",
                    "Publicity grade (of 1,000)", "Grade B+ after this change", "score 9050/10000"):
            self.assertRegex(old, GRADE)


if __name__ == "__main__":
    unittest.main()
