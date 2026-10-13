"""Tests break what the guard claims to catch, and pin what it deliberately ignores."""

import contextlib
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Callable
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import worktree_guard as guard


class WorktreeGuardTest(unittest.TestCase):
    def setUp(self) -> None:
        # A pre-push hook runs these tests with GIT_DIR and its siblings set. Inherited,
        # they point every git call, here and in the guard, at the real repository
        # instead of the temporary one, so they are cleared for each test.
        saved = {name: value for name, value in os.environ.items() if name.startswith("GIT_")}
        for name in saved:
            del os.environ[name]
        self.addCleanup(os.environ.update, saved)
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        (self.root / "tracked.txt").write_text("one\n")
        self.git("add", "tracked.txt")
        self.git("commit", "-q", "-m", "init")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def git(self, *args: str) -> None:
        subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)

    def changes(self, mutate: Callable[[], object]) -> list[str]:
        before = guard.snapshot(self.root)
        mutate()
        return guard.differences(before, guard.snapshot(self.root))

    def test_unchanged_tree_passes(self) -> None:
        (self.root / "untracked.txt").write_text("x\n")
        self.assertEqual(self.changes(lambda: None), [])

    def test_untracked_contents_rewritten(self) -> None:
        path = self.root / "untracked.txt"
        path.write_text("before\n")
        self.assertTrue(self.changes(lambda: path.write_text("after!\n")))

    def test_file_named_dash_rewritten(self) -> None:
        path = self.root / "-"
        path.write_text("before\n")
        self.assertTrue(self.changes(lambda: path.write_text("after!\n")))

    def test_execute_bit_dropped(self) -> None:
        path = self.root / "tool.sh"
        path.write_text("echo hi\n")
        path.chmod(0o755)
        self.assertTrue(self.changes(lambda: path.chmod(0o644)))

    def test_symlink_retargeted_to_same_bytes(self) -> None:
        (self.root / "a.txt").write_text("same\n")
        (self.root / "b.txt").write_text("same\n")
        link = self.root / "link"
        link.symlink_to("a.txt")

        def retarget() -> None:
            link.unlink()
            link.symlink_to("b.txt")

        self.assertTrue(self.changes(retarget))

    def test_symlink_target_gains_trailing_newline(self) -> None:
        link = self.root / "link"
        link.symlink_to("target")

        def retarget() -> None:
            link.unlink()
            os.symlink("target\n", link)

        self.assertTrue(self.changes(retarget))

    def test_staged_blob_replaced_while_status_stays_mm(self) -> None:
        path = self.root / "tracked.txt"
        path.write_text("staged one\n")
        self.git("add", "tracked.txt")
        path.write_text("worktree\n")

        def restage() -> None:
            path.write_text("staged two\n")
            self.git("add", "tracked.txt")
            path.write_text("worktree\n")

        self.assertTrue(self.changes(restage))

    def test_new_file_created(self) -> None:
        self.assertTrue(self.changes(lambda: (self.root / "new.txt").write_text("x\n")))

    def test_tracked_file_deleted(self) -> None:
        self.assertTrue(self.changes(lambda: (self.root / "tracked.txt").unlink()))

    def test_ignored_paths_are_outside_the_guard(self) -> None:
        (self.root / ".gitignore").write_text("cache/\n")
        self.git("add", ".gitignore")
        self.git("commit", "-q", "-m", "ignore")

        def write_ignored() -> None:
            (self.root / "cache").mkdir()
            (self.root / "cache" / "x.pyc").write_text("bytecode\n")
            (self.root / "empty").mkdir()

        self.assertEqual(self.changes(write_ignored), [])

    @unittest.skipIf(os.geteuid() == 0, "root can read a mode-000 file")
    def test_unreadable_file_aborts(self) -> None:
        path = self.root / "secret.txt"
        path.write_text("x\n")
        path.chmod(0)
        try:
            with self.assertRaises(PermissionError):
                guard.snapshot(self.root)
        finally:
            path.chmod(0o644)

    def test_main_reports_command_failure(self) -> None:
        cwd = os.getcwd()
        os.chdir(self.root)
        try:
            self.assertEqual(guard.main(["--", sys.executable, "-c", "raise SystemExit(3)"]), 3)
            write = "open('made.txt', 'w').write('x')"
            report = io.StringIO()
            with contextlib.redirect_stderr(report):
                self.assertEqual(guard.main(["--", sys.executable, "-c", write]), 1)
            self.assertIn("changed entry: made.txt", report.getvalue())
        finally:
            os.chdir(cwd)


class HookEnvironmentTest(unittest.TestCase):
    def test_tests_leave_the_repository_named_by_git_dir_alone(self) -> None:
        # The way a pre-push hook in a worktree runs this file: GIT_DIR names a real repository
        clean = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        with tempfile.TemporaryDirectory() as decoy:
            subprocess.run(["git", "init", "-q", decoy], env=clean, check=True, capture_output=True)
            hook = clean | {"GIT_DIR": str(Path(decoy) / ".git"), "GIT_WORK_TREE": decoy}
            subprocess.run([sys.executable, __file__, "WorktreeGuardTest"], env=hook, capture_output=True)
            log = subprocess.run(["git", "-C", decoy, "rev-list", "--all"], env=clean, capture_output=True, text=True)
            self.assertEqual(log.stdout, "", "a test committed into the repository GIT_DIR named")


if __name__ == "__main__":
    unittest.main()
