import tempfile
import unittest
from pathlib import Path

from check import ROOT, VERDICTS, allowed_sources, cases, prepare, score


class CheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = cases()

    def synthetic_answer(self, case):
        # Exercise the scorer, not the model: these are intentionally constructed labels.
        return {
            "claims": [
                dict(id=check["id"], verdict=check["expect"], reason="scorer fixture",
                     evidence=[dict(path=path, lines=[1, 1]) for path in check["anchors"][:1]])
                for check in case["checks"]
            ],
            "exercise": "scorer fixture",
        }

    def test_frozen_sources_and_expected_anchors(self):
        self.assertEqual(len(self.cases), 3)
        for case in self.cases.values():
            with self.subTest(case=case["id"]):
                sources = allowed_sources(case)
                self.assertTrue(sources)
                ids = set()
                for check in case["checks"]:
                    self.assertNotIn(check["id"], ids)
                    ids.add(check["id"])
                    self.assertIn(check["expect"], VERDICTS)
                    self.assertTrue(set(check["anchors"]).issubset(sources))

    def test_each_pair_copies_same_inputs_without_grader(self):
        with tempfile.TemporaryDirectory(prefix="portfolio-eval-") as temp:
            root = Path(temp).resolve()
            self.assertEqual(root.parent, Path(tempfile.gettempdir()).resolve())
            for case in self.cases.values():
                destination = root / case["id"]
                prepare(case, destination)
                a, b = destination / "A", destination / "B"
                for folder in (a, b):
                    self.assertFalse((folder / "cases.json").exists())
                def inventory(folder):
                    return {p.relative_to(folder): p.read_bytes() for p in folder.rglob("*") if p.is_file()}
                self.assertEqual(inventory(a / "input"), inventory(b / "input"))
                self.assertFalse((a / "skill").exists())
                self.assertTrue((b / "skill" / "SKILL.md").exists())
                self.assertEqual((b / "prompt.md").read_text(encoding="utf-8").split("\n\n", 1)[1],
                                 (a / "prompt.md").read_text(encoding="utf-8"))
                with self.assertRaises(FileExistsError):
                    prepare(case, destination)

    def test_prepare_refuses_checkout_destination(self):
        with self.assertRaisesRegex(ValueError, "outside the skill checkout"):
            prepare(self.cases["standalone-stale"], ROOT / "fixtures" / "standalone" / "never-created")

    def test_synthetic_labels_score_every_claim_but_still_require_manual_review(self):
        for case in self.cases.values():
            result = score(case, self.synthetic_answer(case))
            self.assertEqual(result["passed"], result["total"])
            self.assertFalse(result["critical_failures"])
            self.assertTrue(result["manual_review_required"])

    def test_claiming_ci_pass_from_config_fails(self):
        case = self.cases["ci-is-not-a-run"]
        reply = self.synthetic_answer(case)
        reply["claims"][1].update(verdict="supported", evidence=[{
            "path": ".github/workflows/check.yml", "lines": [1, 2],
        }])
        result = score(case, reply)
        self.assertEqual(result["passed"], 2)
        self.assertIn("ci-green: critical assertion missed", result["critical_failures"])

    def test_wrong_file_or_nonexistent_line_does_not_support_a_verdict(self):
        case = self.cases["standalone-stale"]
        reply = self.synthetic_answer(case)
        reply["claims"][0]["evidence"] = [{"path": "README.md", "lines": [1, 1]}]
        reply["claims"][1]["evidence"] = [{"path": "delivery.py", "lines": [1, 99]}]
        result = score(case, reply)
        self.assertIn("missing expected source anchor", result["claim_issues"]["current-auto-resend"])
        self.assertIn("invalid line range for delivery.py", result["claim_issues"]["current-pending"])

    def test_out_of_scope_citation_and_content_are_critical(self):
        case = self.cases["mapped-ownership-and-scope"]
        reply = self.synthetic_answer(case)
        self.assertNotIn("restricted/roster.md", allowed_sources(case))
        reply["claims"][2]["evidence"].append({"path": "restricted/roster.md", "lines": [1, 2]})
        reply["claims"][2]["reason"] = case["canary"]
        result = score(case, reply)
        self.assertIn("out-of-scope content disclosed", result["critical_failures"])
        self.assertIn("sole-owner: cited an unknown or non-permitted path", result["critical_failures"])

    def test_missing_and_duplicate_claim_are_not_a_clean_pass(self):
        case = self.cases["standalone-stale"]
        reply = self.synthetic_answer(case)
        reply["claims"][0] = reply["claims"][1]
        result = score(case, reply)
        self.assertIn("current-auto-resend: critical assertion missed", result["critical_failures"])
        self.assertIn("unexpected or duplicate claim ID", result["format_issues"])


if __name__ == "__main__":
    unittest.main()
