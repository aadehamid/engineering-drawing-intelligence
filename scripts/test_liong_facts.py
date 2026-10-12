"""Pin today's figures, and break the documents on purpose to see the check catch it."""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import liong_facts as facts
import worktree_guard as guard

EXPECTED = {
    "r0.nodes": 17, "r0.engineering_objects": 15, "r0.drawings": 2,
    "r0.flow_edges": 14, "r0.other_edges": 17, "r0.edges": 31, "r0.e1_e2_paths": 2,
    "r2.nodes": 15, "r2.edges": 26, "r2.on_sheet_removed": 2, "r2.e1_e2_paths": 1,
    "scn010.nodes": 17, "scn010.edges": 29,
    "scn011.contextual_nodes": 5, "scn011.contextual_edges": 4,
    "scn011.nodes": 22, "scn011.edges": 35,
    "scaled.worlds": 100, "scaled.sheets": 200, "scaled.engineering_objects": 1500,
    "scaled.nodes": 1700, "scaled.edges": 3100, "scaled.r2_nodes": 1500, "scaled.r2_edges": 2600,
    "documents.substantive": 11,
}


class FiguresTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        shutil.copyfile(facts.ROOT / "README.md", self.root / "README.md")
        shutil.copytree(facts.ROOT / "docs", self.root / "docs")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def edit(self, path: Path, old: str, new: str) -> None:
        file = self.root / path
        text = file.read_text(encoding="utf-8")
        self.assertIn(old, text)
        file.write_text(text.replace(old, new, 1), encoding="utf-8")

    def test_figures_match_today(self) -> None:
        self.assertEqual(facts.compute(facts.ROOT), EXPECTED)

    def test_documents_agree(self) -> None:
        self.assertEqual(facts.check(facts.ROOT), [])

    def test_wrong_figure_fails(self) -> None:
        self.edit(facts.FIXTURES, "baseline therefore contains 31 edges", "baseline therefore contains 32 edges")
        self.assertIn(
            f"{facts.FIXTURES}: states 32 for r0.edges; the fixture gives 31", facts.check(self.root)
        )

    def test_wrong_word_figure_fails(self) -> None:
        self.edit(Path("README.md"), "eleven draft documents", "twelve draft documents")
        self.assertTrue(any("documents.substantive" in e for e in facts.check(self.root)))

    def test_reworded_claim_fails(self) -> None:
        self.edit(facts.FIXTURES, "These 14 edges express", "This set of 14 edges expresses")
        self.assertTrue(any("claim not found" in e for e in facts.check(self.root)))

    def test_unknown_pair_fails(self) -> None:
        self.edit(facts.FIXTURES, "Published R0 stays at 17/31", "Published R0 stays at 18/31")
        self.assertIn(f"{facts.FIXTURES}: 18/31 matches no known graph state", facts.check(self.root))

    def test_fixture_change_moves_the_figures(self) -> None:
        self.edit(facts.FIXTURES, "J1 -> P6    P6 -> VB    VB -> J2", "J1 -> P6    P6 -> VB    VB -> J2    V1 -> J2")
        self.assertEqual(facts.compute(self.root)["r0.edges"], 32)
        self.assertTrue(facts.check(self.root))

    def test_reformatted_fixture_gives_same_figures(self) -> None:
        self.edit(facts.FIXTURES, "  E1,V1,VB,J1,J2,X1,P1,P2,P3,P4,P6 -> S1",
                  "  E1, V1, VB, J1, J2, X1, P1, P2, P3, P4, P6   ->   S1")
        self.edit(facts.FIXTURES, "E1 -> P1    P1 -> J1", "E1->P1\nP1  ->  J1")
        self.assertEqual(facts.compute(self.root), EXPECTED)

    def test_claim_wrapped_across_lines_still_checked(self) -> None:
        self.edit(facts.FIXTURES, "baseline therefore contains 31 edges", "baseline therefore\ncontains 31 edges")
        self.assertEqual(facts.check(self.root), [])

    def test_find_matches_across_line_breaks(self) -> None:
        self.edit(facts.FIXTURES, "baseline therefore contains 31 edges", "baseline therefore\ncontains 31 edges")
        self.assertTrue(any(r.endswith(": therefore contains 31") for r in facts.find(self.root, "therefore contains 31")))

    def test_tool_never_writes_to_the_repository(self) -> None:
        before = guard.snapshot(facts.ROOT)
        script = str(facts.ROOT / "scripts" / "liong_facts.py")
        for args in (["figures"], ["figures", "--json"], ["check"], ["find", "R0"]):
            subprocess.run([sys.executable, script, *args], check=True, capture_output=True)
        self.assertEqual(guard.differences(before, guard.snapshot(facts.ROOT)), [])


if __name__ == "__main__":
    unittest.main()
