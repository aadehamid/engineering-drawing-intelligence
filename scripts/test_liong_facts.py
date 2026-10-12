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
    "r0.on_sheet_edges": 15, "r0.instrument_parent_edges": 1, "r0.cross_sheet_edges": 1,
    "r2.nodes": 15, "r2.edges": 26, "r2.on_sheet_removed": 2, "r2.e1_e2_paths": 1,
    "scn012.export_nodes": 14, "scn012.export_flow_edges": 14,
    "scn010.nodes": 17, "scn010.edges": 29,
    "scn011.contextual_nodes": 5, "scn011.contextual_edges": 4,
    "scn011.nodes": 22, "scn011.edges": 35,
    "scaled.worlds": 100, "scaled.sheets": 200, "scaled.engineering_objects": 1500,
    "scaled.nodes": 1700, "scaled.edges": 3100, "scaled.r2_nodes": 1500, "scaled.r2_edges": 2600,
    "documents.substantive": 11,
}


class CopiedDocsTestCase(unittest.TestCase):
    """Each test edits its own copy of README.md and docs/."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        shutil.copyfile(facts.ROOT / "README.md", self.root / "README.md")
        shutil.copytree(facts.ROOT / "docs", self.root / "docs")
        self.addCleanup(self.temp.cleanup)

    def edit(self, path: Path, old: str, new: str) -> None:
        file = self.root / path
        text = file.read_text(encoding="utf-8")
        self.assertIn(old, text)
        file.write_text(text.replace(old, new, 1), encoding="utf-8")


class FiguresTest(CopiedDocsTestCase):


    def test_figures_match_today(self) -> None:
        self.assertEqual(facts.compute(facts.ROOT), EXPECTED)

    def test_every_claim_names_a_figure(self) -> None:
        figures = facts.compute(facts.ROOT)
        for _, _, keys in facts.CLAIMS:
            for key in keys:
                self.assertIn(key, figures)

    def test_missing_table_row_names_the_row(self) -> None:
        self.edit(facts.FIXTURES, "| R2 |", "| R2b |")
        with self.assertRaisesRegex(ValueError, "no table row labelled R2"):
            facts.compute(self.root)

    def test_documents_agree(self) -> None:
        self.assertEqual(facts.check(facts.ROOT), [])

    def test_wrong_figure_fails(self) -> None:
        self.edit(facts.FIXTURES, "baseline therefore contains 31 edges", "baseline therefore contains 32 edges")
        self.assertIn(
            f"{facts.FIXTURES}: states 32 for r0.edges; the fixture gives 31", facts.check(self.root)
        )

    def test_wrong_word_figure_fails(self) -> None:
        self.edit(facts.README, "eleven draft documents", "twelve draft documents")
        self.assertTrue(any("documents.substantive" in e for e in facts.check(self.root)))

    def test_reworded_claim_fails(self) -> None:
        self.edit(facts.FIXTURES, "These 14 edges express", "This set of 14 edges expresses")
        self.assertTrue(any("claim not found" in e for e in facts.check(self.root)))

    def test_unknown_pair_fails(self) -> None:
        self.edit(facts.FIXTURES, "Published R0 stays at 17/31", "Published R0 stays at 18/31")
        self.assertIn(f"{facts.FIXTURES}: 18/31 matches no known graph state", facts.check(self.root))

    def test_wrong_denominator_fails(self) -> None:
        self.edit(facts.EVALUATION, "FLOW recall with denominator 14", "FLOW recall with denominator 99")
        errors = facts.check(self.root)
        self.assertIn(f"{facts.EVALUATION}: states 99 for r0.flow_edges; the fixture gives 14", errors)

    def test_unregistered_contradictory_sentence_fails(self) -> None:
        self.edit(facts.FIXTURES, "## Revision and time rules", "The R0 view has 99 edges.\n\n## Revision and time rules")
        self.assertTrue(any("unregistered figure: 99 in" in e for e in facts.check(self.root)))

    def test_wrong_count_equal_to_another_figure_fails(self) -> None:
        self.edit(facts.FIXTURES, "## Revision and time rules", "The R0 view has 15 nodes.\n\n## Revision and time rules")
        self.assertTrue(any("unregistered figure: 15 in" in e for e in facts.check(self.root)))

    def test_number_word_count_fails(self) -> None:
        self.edit(facts.FIXTURES, "## Revision and time rules", "The R0 view has twelve nodes.\n\n## Revision and time rules")
        self.assertTrue(any("unregistered figure: twelve in" in e for e in facts.check(self.root)))

    def test_any_spelling_of_an_unregistered_figure_fails(self) -> None:
        for sentence, number in (
            ("The R0 view has seventeen nodes.", "seventeen"),
            ("The R0 view has `99` nodes.", "99"),
            ("The R0 view has 99 total validated engineering comparison nodes.", "99"),
            ("The R0 view has thirty-one edges.", "thirty-one"),
        ):
            with self.subTest(sentence=sentence):
                self.setUp()
                self.edit(facts.FIXTURES, "## Revision and time rules", f"{sentence}\n\n## Revision and time rules")
                self.assertTrue(any(f"unregistered figure: {number} in" in e for e in facts.check(self.root)))

    def test_hyphenated_figure_is_checked(self) -> None:
        self.edit(facts.FIXTURES, "equals the 17-node/31-edge R0 set", "equals the 16-node/30-edge R0 set")
        errors = facts.check(self.root)
        self.assertIn(f"{facts.FIXTURES}: states 16 for r0.nodes; the fixture gives 17", errors)
        self.assertIn(f"{facts.FIXTURES}: states 30 for r0.edges; the fixture gives 31", errors)

    def test_unregistered_hyphenated_figure_fails(self) -> None:
        self.edit(facts.FIXTURES, "## Revision and time rules", "The view is a 16-node graph.\n\n## Revision and time rules")
        self.assertTrue(any("unregistered figure: 16 in" in e for e in facts.check(self.root)))

    def test_leading_zero_pair_fails(self) -> None:
        self.edit(facts.FIXTURES, "Published R0 stays at 17/31", "Published R0 stays at 018/031")
        self.assertIn(f"{facts.FIXTURES}: 018/031 matches no known graph state", facts.check(self.root))

    def test_id_ranges_are_not_pairs(self) -> None:
        self.edit(facts.FIXTURES, "## Revision and time rules", "See SCN-002/009 and LIONG-007/009.\n\n## Revision and time rules")
        self.assertEqual(facts.check(self.root), [])

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


class DecisionRecordsTest(CopiedDocsTestCase):
    RECORD = Path("docs/decisions/DEC-014-skipped-question-convention.md")
    INDEX = Path("docs/decisions/README.md")


    def errors(self) -> list[str]:
        return facts.check_decisions(self.root)

    def test_records_match_today(self) -> None:
        self.assertEqual(facts.check_decisions(facts.ROOT), [])

    def test_status_differs_from_index(self) -> None:
        self.edit(self.RECORD, "Status: Decided", "Status: Proposed")
        self.assertIn(f"{self.INDEX}: DEC-014 status Decided; the record says Proposed", self.errors())

    def test_date_differs_from_index(self) -> None:
        self.edit(self.RECORD, "Date: 2026-10-11", "Date: 2026-10-12")
        self.assertTrue(any("DEC-014 date 2026-10-11" in e for e in self.errors()))

    def test_title_differs_from_index(self) -> None:
        self.edit(self.RECORD, "# DEC-014: A skipped question", "# DEC-014: An unanswered question")
        self.assertIn(f"{self.INDEX}: DEC-014 title differs from its record", self.errors())

    def test_record_without_index_row(self) -> None:
        (self.root / "docs/decisions/DEC-099-orphan.md").write_text(
            (self.root / self.RECORD).read_text().replace("DEC-014", "DEC-099"), encoding="utf-8"
        )
        self.assertIn("docs/decisions/DEC-099-orphan.md: DEC-099 has no index row", self.errors())

    def test_index_row_without_record(self) -> None:
        (self.root / self.RECORD).unlink()
        self.assertTrue(any("links to missing file" in e for e in self.errors()))

    def test_duplicate_index_row(self) -> None:
        row = "| [DEC-014](DEC-014-skipped-question-convention.md) | A skipped question in a decision round counts as agreement | Decided | 2026-10-11 |\n"
        self.edit(self.INDEX, row, row + row)
        self.assertIn(f"{self.INDEX}: DEC-014 is indexed twice", self.errors())

    def test_decided_needs_owner_quote(self) -> None:
        self.edit(self.RECORD, "> Q12: yes", "Q12: yes")
        self.assertTrue(any("quotes the owner" in e for e in self.errors()))

    def test_missing_section_fails(self) -> None:
        self.edit(self.RECORD, "## Alternatives considered", "## Other options")
        self.assertTrue(any("needs sections" in e for e in self.errors()))

    def test_unknown_status_fails(self) -> None:
        self.edit(self.RECORD, "Status: Decided", "Status: Approved")
        self.assertTrue(any("needs exactly one Status line" in e for e in self.errors()))

    def supersede(self, line: str) -> None:
        self.edit(self.RECORD, "Status: Decided", "Status: Superseded")
        self.edit(self.INDEX, "| Decided | 2026-10-11 |", "| Superseded | 2026-10-11 |")
        self.edit(self.RECORD, "## Context", f"{line}\n\n## Context")

    def add_successor(self, amends_line: str) -> None:
        text = (self.root / self.RECORD).read_text().replace("DEC-014", "DEC-020")
        text = text.replace("Status: Superseded", "Status: Decided").replace("Superseded by DEC-020 on 2026-11-01.\n\n", "")
        text = text.replace("Date: 2026-10-11", "Date: 2026-11-01").replace("## Context", f"{amends_line}\n\n## Context", 1)
        (self.root / "docs/decisions/DEC-020-successor.md").write_text(text, encoding="utf-8")
        title = "A skipped question in a decision round counts as agreement"
        row = f"| [DEC-020](DEC-020-successor.md) | {title} | Decided | 2026-11-01 |\n"
        self.edit(self.INDEX, "\n\n## Record format", f"\n{row}\n## Record format")

    def test_superseded_needs_dated_successor_line(self) -> None:
        self.supersede("Superseded by DEC-020")
        self.assertTrue(any("Superseded by DEC-NNN on YYYY-MM-DD" in e for e in self.errors()))

    def test_successor_must_exist(self) -> None:
        self.supersede("Superseded by DEC-020 on 2026-11-01.")
        self.assertTrue(any("successor DEC-020 has no record" in e for e in self.errors()))

    def test_successor_must_say_it_amends(self) -> None:
        self.supersede("Superseded by DEC-020 on 2026-11-01.")
        self.add_successor("Follows DEC-014")
        self.assertTrue(any("does not say 'Amends DEC-014'" in e for e in self.errors()))

    def test_valid_supersession_passes(self) -> None:
        self.supersede("Superseded by DEC-020 on 2026-11-01.")
        self.add_successor("Amends DEC-014")
        self.assertEqual(self.errors(), [])

    def test_empty_section_fails(self) -> None:
        text = (self.root / self.RECORD).read_text()
        start = text.index("## Evidence\n") + len("## Evidence\n")
        (self.root / self.RECORD).write_text(text[:start], encoding="utf-8")
        self.assertIn(f"{self.RECORD}: section ## Evidence is empty", self.errors())

    def test_question_without_owner_answer_fails(self) -> None:
        self.edit(self.RECORD, "The owner answered:\n\n> Q12: yes\n", "")
        self.assertTrue(any("after 'The owner answered:'" in e for e in self.errors()))

    def test_malformed_index_row_fails(self) -> None:
        self.edit(self.INDEX, "\n\n## Record format", "\n| DEC-099 | Ghost | Decided | 2026-10-11 |\n\n## Record format")
        self.assertTrue(any("malformed index row: | DEC-099 | Ghost" in e for e in self.errors()))


    def test_amends_requires_superseded_predecessor(self) -> None:
        self.add_successor("Amends DEC-014")
        self.assertTrue(any("amends DEC-014, which is not marked" in e for e in self.errors()))

    def test_header_like_row_fails(self) -> None:
        self.edit(self.INDEX, "\n\n## Record format", "\n| ID | Ghost | Decided | 2026-10-11 |\n\n## Record format")
        self.assertTrue(any("malformed index row: | ID | Ghost" in e for e in self.errors()))

    def test_comment_only_section_is_empty(self) -> None:
        text = (self.root / self.RECORD).read_text()
        start = text.index("## Evidence\n") + len("## Evidence\n")
        (self.root / self.RECORD).write_text(text[:start] + "\n<!-- empty -->\n", encoding="utf-8")
        self.assertIn(f"{self.RECORD}: section ## Evidence is empty", self.errors())

    def test_indented_index_row_fails(self) -> None:
        self.edit(self.INDEX, "\n\n## Record format", "\n | DEC-099 | Ghost | Decided | 2026-10-11 |\n\n## Record format")
        self.assertTrue(any("malformed index row: | DEC-099 | Ghost" in e for e in self.errors()))

    def test_comment_spanning_sections_hides_them(self) -> None:
        self.edit(self.RECORD, "## Context", "<!--\n## Context")
        (self.root / self.RECORD).write_text((self.root / self.RECORD).read_text() + "-->\n", encoding="utf-8")
        self.assertTrue(any("needs sections" in e for e in self.errors()))

    def test_hidden_metadata_is_ignored(self) -> None:
        self.edit(self.RECORD, "Status: Decided\nDate: 2026-10-11",
                  "<!--\nStatus: Decided\nDate: 2026-10-11\n-->\nStatus: Proposed\nDate: 2026-10-12")
        errors = self.errors()
        self.assertIn(f"{self.INDEX}: DEC-014 status Decided; the record says Proposed", errors)
        self.assertIn(f"{self.INDEX}: DEC-014 date 2026-10-11; the record says 2026-10-12", errors)

    def test_heading_only_section_is_empty(self) -> None:
        text = (self.root / self.RECORD).read_text()
        start = text.index("## Evidence\n") + len("## Evidence\n")
        (self.root / self.RECORD).write_text(text[:start] + "\n### Pending evidence\n", encoding="utf-8")
        self.assertIn(f"{self.RECORD}: section ## Evidence is empty", self.errors())

    def test_row_aliasing_another_record_fails(self) -> None:
        self.edit(self.INDEX, "\n\n## Record format",
                  "\n| [DEC-099](DEC-014-skipped-question-convention.md) | Ghost | Proposed | 2026-10-12 |\n\n## Record format")
        self.assertTrue(any("DEC-099 links to DEC-014-skipped-question-convention.md, which is not the DEC-099 record" in e
                            for e in self.errors()))

    def test_unclosed_fence_hides_what_follows(self) -> None:
        self.edit(self.RECORD, "## Owner's words", "```markdown\n## Owner's words")
        self.assertTrue(any("needs sections" in e for e in self.errors()))

    def test_longer_fence_hides_inner_fences(self) -> None:
        self.edit(self.RECORD, "## Context", "````markdown\n```\n## Context")
        (self.root / self.RECORD).write_text((self.root / self.RECORD).read_text() + "```\n````\n", encoding="utf-8")
        self.assertTrue(any("needs sections" in e for e in self.errors()))

    def test_repeated_section_fails(self) -> None:
        (self.root / self.RECORD).write_text((self.root / self.RECORD).read_text() + "\n## Decision\n\n", encoding="utf-8")
        self.assertTrue(any("each once, in that order" in e for e in self.errors()))

    def test_duplicate_record_id_fails(self) -> None:
        (self.root / "docs/decisions/DEC-014-aaa-duplicate.md").write_text(
            "# DEC-014: A different decision\n\nStatus: Proposed\nDate: 2026-10-12\n", encoding="utf-8"
        )
        self.assertTrue(any("DEC-014 is already used by DEC-014-aaa-duplicate.md" in e for e in self.errors()))

    def test_issue_reference_prose_is_content(self) -> None:
        text = (self.root / self.RECORD).read_text()
        start = text.index("## Evidence\n") + len("## Evidence\n")
        (self.root / self.RECORD).write_text(
            text[:start] + "\n#6 requested that this repository record the convention.\n", encoding="utf-8"
        )
        self.assertEqual(self.errors(), [])

    def test_unclosed_comment_hides_what_follows(self) -> None:
        self.edit(self.RECORD, "## Owner's words", "<!--\n## Owner's words")
        self.assertTrue(any("needs sections" in e for e in self.errors()))

    def test_comment_opener_inside_code_is_code(self) -> None:
        self.edit(self.RECORD, "## Owner's words", "```html\n<!--\n```\n\n## Owner's words")
        self.assertEqual(self.errors(), [])

    def replace_evidence(self, body: str) -> None:
        text = (self.root / self.RECORD).read_text()
        start = text.index("## Evidence\n") + len("## Evidence\n")
        (self.root / self.RECORD).write_text(text[:start] + body, encoding="utf-8")

    def test_reference_definition_alone_is_empty(self) -> None:
        self.replace_evidence("\n[register]: ../LIONG-REG-001-decisions.md\n")
        self.assertIn(f"{self.RECORD}: section ## Evidence is empty", self.errors())

    def test_html_tags_alone_are_empty(self) -> None:
        self.replace_evidence("\n<br>\n<div></div>\n")
        self.assertIn(f"{self.RECORD}: section ## Evidence is empty", self.errors())

    def test_visible_reference_is_content(self) -> None:
        self.replace_evidence("\nSee [register].\n\n[register]: ../LIONG-REG-001-decisions.md\n")
        self.assertEqual(self.errors(), [])

    def test_markup_only_owner_answer_fails(self) -> None:
        for answer in ("> <br>", "> [approval]: ../LIONG-REG-001-decisions.md", "> >", "> -", "> 1.",
                       "> ```\n> ```", "> > ---", "> **  **", "> [](../LIONG-REG-001-decisions.md)",
                       "> &nbsp;", "> &#32;", "> ![](logo.png)"):
            with self.subTest(answer=answer):
                self.setUp()
                self.edit(self.RECORD, "> Q12: yes", answer)
                self.assertTrue(any("quotes the owner" in e for e in self.errors()))


    def test_autolink_is_content(self) -> None:
        self.replace_evidence("\n<https://github.com/aadehamid/Engineering_Drawing_to_Graph/pull/6>\n")
        self.assertEqual(self.errors(), [])

    def test_markup_in_owner_answer_fails_even_with_words(self) -> None:
        for answer in ("> - Q12: yes", "> > Q12: yes", "> [Q12: yes](../LIONG-REG-001-decisions.md)",
                       "> Q12&#58; yes", "> `<approved>`", "> [](https://example.com/Approval_(signed).pdf)"):
            with self.subTest(answer=answer):
                self.setUp()
                self.edit(self.RECORD, "> Q12: yes", answer)
                self.assertTrue(any("plain-text" in e for e in self.errors()))

    def test_plain_owner_answers_pass(self) -> None:
        for answer in ("> Q12: yes", "> Yes, agreed. Use SQL Server on Azure.", "> I'm not married to Neon."):
            with self.subTest(answer=answer):
                self.setUp()
                self.edit(self.RECORD, "> Q12: yes", answer)
                self.assertEqual(self.errors(), [])

    def test_empty_list_or_rule_section_is_empty(self) -> None:
        for body in ("\n-\n", "\n---\n", "\n> \n", "\n```\n```\n"):
            with self.subTest(body=body):
                self.setUp()
                self.replace_evidence(body)
                self.assertIn(f"{self.RECORD}: section ## Evidence is empty", self.errors())

    def test_owner_words_inside_raw_html_block_fail(self) -> None:
        for tag in ("script", "style"):
            with self.subTest(tag=tag):
                self.setUp()
                self.edit(self.RECORD, "The owner answered:\n\n> Q12: yes\n",
                          f"<{tag}>\nThe owner answered:\n\n> Q12: yes\n</{tag}>\n")
                self.assertTrue(any("plain text only" in e for e in self.errors()))

if __name__ == "__main__":
    unittest.main()
