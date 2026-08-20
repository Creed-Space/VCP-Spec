from __future__ import annotations

import contextlib
import io
import json
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import compare_release_candidates
import package_release_candidate
import validation_utils
from package_release_candidate import (
    build_archive,
    copy_regular_candidate,
    create_candidate,
    selected_paths,
    selected_snapshots,
)


class ReleasePackagingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "docs").mkdir()
        (self.root / "docs" / "b.md").write_text("bravo\n", encoding="utf-8")
        (self.root / "a.md").write_text("alpha\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_archive_is_reproducible_regular_and_metadata_normalized(self) -> None:
        paths = [self.root / "a.md", self.root / "docs" / "b.md"]
        first = self.root / "first.tar.gz"
        second = self.root / "second.tar.gz"
        with mock.patch.object(package_release_candidate, "ROOT", self.root):
            build_archive(first, paths, 123456789)
            build_archive(second, paths, 123456789)
        self.assertEqual(first.read_bytes(), second.read_bytes())

        with tarfile.open(first, "r:gz") as archive:
            members = archive.getmembers()
            self.assertEqual([member.name for member in members], ["a.md", "docs/b.md"])
            self.assertTrue(all(member.isfile() for member in members))
            self.assertTrue(all(member.uid == member.gid == 0 for member in members))
            self.assertTrue(all(member.mode == 0o644 for member in members))
            self.assertTrue(all(member.mtime == 123456789 for member in members))
            self.assertEqual(archive.extractfile("a.md").read(), b"alpha\n")

    def test_archive_failure_leaves_no_partial_destination_or_temporary(self) -> None:
        cases = {
            "archive write": (
                "add_file",
                mock.patch.object(
                    package_release_candidate,
                    "add_file",
                    side_effect=ValueError("archive write failed"),
                ),
            ),
            "durability sync": (
                "fsync",
                mock.patch.object(
                    package_release_candidate.os,
                    "fsync",
                    side_effect=OSError("archive sync failed"),
                ),
            ),
        }
        for name, (_, failure) in cases.items():
            with self.subTest(name=name):
                output = self.root / "candidate.tar.gz"
                with (
                    mock.patch.object(package_release_candidate, "ROOT", self.root),
                    failure,
                    self.assertRaisesRegex(Exception, "failed"),
                ):
                    build_archive(output, [self.root / "a.md"], 0)
                self.assertFalse(output.exists())
                self.assertEqual(list(self.root.glob(".candidate.tar.gz.*.tmp")), [])

    def test_rendered_copy_is_exclusive_and_cleans_partial_write(self) -> None:
        source = self.root / "a.md"
        destination = self.root / "copy.md"
        with mock.patch.object(package_release_candidate, "ROOT", self.root):
            copy_regular_candidate(source, destination)
            self.assertEqual(destination.read_bytes(), source.read_bytes())
            with self.assertRaises(FileExistsError):
                copy_regular_candidate(source, destination)
            self.assertEqual(destination.read_bytes(), source.read_bytes())

        destination.unlink()
        with (
            mock.patch.object(package_release_candidate, "ROOT", self.root),
            mock.patch.object(
                package_release_candidate.os, "fsync", side_effect=OSError("disk full")
            ),
            self.assertRaisesRegex(OSError, "disk full"),
        ):
            copy_regular_candidate(source, destination)
        self.assertFalse(destination.exists())

    def test_late_failure_never_exposes_partial_final_candidate(self) -> None:
        destination = self.root / "final-candidate"
        destination.mkdir()

        def fail_late(staging: Path) -> None:
            (staging / "vcp-spec-source-candidate.tar.gz").write_bytes(b"partial")
            (staging / "rendered-candidates").mkdir()
            raise OSError("late checksum failure")

        with (
            mock.patch.object(
                sys,
                "argv",
                ["package_release_candidate.py", "--output-dir", str(destination)],
            ),
            mock.patch.object(
                package_release_candidate, "create_candidate", side_effect=fail_late
            ),
        ):
            diagnostics = io.StringIO()
            with contextlib.redirect_stderr(diagnostics):
                self.assertEqual(package_release_candidate.main(), 1)
        self.assertIn("late checksum failure", diagnostics.getvalue())
        self.assertTrue(destination.is_dir())
        self.assertEqual(list(destination.iterdir()), [])
        self.assertEqual(list(self.root.glob(".final-candidate.*.tmp")), [])

        def build_complete(staging: Path) -> None:
            (staging / "release-manifest.json").write_text("{}\n", encoding="utf-8")

        with (
            mock.patch.object(
                sys,
                "argv",
                ["package_release_candidate.py", "--output-dir", str(destination)],
            ),
            mock.patch.object(
                package_release_candidate,
                "create_candidate",
                side_effect=build_complete,
            ),
            mock.patch.object(
                package_release_candidate.os,
                "fsync",
                side_effect=OSError("directory sync failure"),
            ),
        ):
            diagnostics = io.StringIO()
            with contextlib.redirect_stderr(diagnostics):
                self.assertEqual(package_release_candidate.main(), 1)
        self.assertIn("directory sync failure", diagnostics.getvalue())
        self.assertFalse(destination.exists())
        self.assertEqual(list(self.root.glob(".final-candidate.*.tmp")), [])

    def test_source_budget_is_aggregate_across_roots(self) -> None:
        source_root = self.root / "source"
        source_root.mkdir()
        (source_root / "root.txt").write_bytes(b"r")
        for name in ("one", "two"):
            directory = source_root / name
            directory.mkdir()
            (directory / "item.txt").write_bytes(b"xx")

        with (
            mock.patch.object(package_release_candidate, "ROOT", source_root),
            mock.patch.object(
                package_release_candidate, "INCLUDE_FILES", ("root.txt",)
            ),
            mock.patch.object(
                package_release_candidate, "INCLUDE_ROOTS", ("one", "two")
            ),
            mock.patch.object(package_release_candidate, "MAX_FILE_BYTES", 10),
            mock.patch.object(package_release_candidate, "MAX_CANDIDATE_FILES", 2),
            mock.patch.object(package_release_candidate, "MAX_CANDIDATE_BYTES", 100),
            self.assertRaisesRegex(ValueError, "exceeds 0 files"),
        ):
            selected_paths()
        with (
            mock.patch.object(package_release_candidate, "ROOT", source_root),
            mock.patch.object(
                package_release_candidate, "INCLUDE_FILES", ("root.txt",)
            ),
            mock.patch.object(
                package_release_candidate, "INCLUDE_ROOTS", ("one", "two")
            ),
            mock.patch.object(package_release_candidate, "MAX_FILE_BYTES", 10),
            mock.patch.object(package_release_candidate, "MAX_CANDIDATE_FILES", 10),
            mock.patch.object(package_release_candidate, "MAX_CANDIDATE_BYTES", 4),
            self.assertRaisesRegex(ValueError, "exceeds 1 total bytes"),
        ):
            selected_paths()

    def test_inventoried_source_replacement_fails_closed(self) -> None:
        source_root = self.root / "source-snapshot"
        docs = source_root / "docs"
        docs.mkdir(parents=True)
        source = docs / "item.txt"
        source.write_bytes(b"old!")

        with (
            mock.patch.object(package_release_candidate, "ROOT", source_root),
            mock.patch.object(package_release_candidate, "INCLUDE_FILES", ()),
            mock.patch.object(package_release_candidate, "INCLUDE_ROOTS", ("docs",)),
        ):
            snapshots = selected_snapshots()
            docs.rename(source_root / "old-docs")
            docs.mkdir()
            source.write_bytes(b"new!")
            output = self.root / "replaced-source.tar.gz"
            with self.assertRaisesRegex(ValueError, "changed since inventory"):
                build_archive(output, snapshots, 0)

        self.assertFalse(output.exists())
        self.assertEqual(list(self.root.glob(".replaced-source.tar.gz.*.tmp")), [])

    def test_reproducibility_inventory_rejects_post_inventory_replacement(self) -> None:
        candidate = self.root / "candidate"
        candidate.mkdir()
        source = candidate / "item.txt"
        source.write_bytes(b"old!")
        real_inventory = validation_utils.regular_file_snapshots_below

        def inventory_then_replace(*args, **kwargs):
            snapshots = real_inventory(*args, **kwargs)
            source.unlink()
            source.write_bytes(b"new!")
            return snapshots

        with (
            mock.patch.object(
                compare_release_candidates,
                "regular_file_snapshots_below",
                side_effect=inventory_then_replace,
            ),
            self.assertRaisesRegex(ValueError, "changed since inventory"),
        ):
            compare_release_candidates.inventory(candidate)

    def test_complete_candidate_contains_consistent_manifest_and_checksums(self) -> None:
        source_root = self.root / "source"
        source_root.mkdir()
        (source_root / "README.md").write_text("source\n", encoding="utf-8")
        docs = source_root / "docs"
        docs.mkdir()
        (docs / "spec.md").write_text("specification\n", encoding="utf-8")
        rendered = source_root / "artifacts" / "rendered-candidates"
        rendered.mkdir(parents=True)
        (rendered / "README.md").write_text("excluded\n", encoding="utf-8")
        (rendered / "spec.pdf").write_bytes(b"rendered")
        output = self.root / "staging"
        output.mkdir()

        def fake_git(*arguments: str) -> str:
            if arguments == ("rev-parse", "HEAD"):
                return "a" * 40
            if "--format=%ct" in arguments:
                return "123456789"
            if "--format=%cI" in arguments:
                return "1973-11-29T21:33:09+00:00"
            raise AssertionError(arguments)

        with (
            mock.patch.object(package_release_candidate, "ROOT", source_root),
            mock.patch.object(
                package_release_candidate, "INCLUDE_FILES", ("README.md",)
            ),
            mock.patch.object(package_release_candidate, "INCLUDE_ROOTS", ("docs",)),
            mock.patch.object(package_release_candidate, "git", side_effect=fake_git),
        ):
            create_candidate(output)

        manifest = json.loads(
            (output / "release-manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["source_commit"], "a" * 40)
        self.assertFalse(manifest["publication_authorized"])
        paths = [entry["path"] for entry in manifest["files"]]
        self.assertEqual(
            paths,
            [
                "vcp-spec-source-candidate.tar.gz",
                "rendered-candidates/spec.pdf",
                "SHA256SUMS",
            ],
        )
        checksums = (output / "SHA256SUMS").read_text(encoding="utf-8")
        self.assertIn("vcp-spec-source-candidate.tar.gz", checksums)
        self.assertIn("rendered-candidates/spec.pdf", checksums)

    def test_successful_main_atomically_replaces_empty_destination(self) -> None:
        destination = self.root / "published-candidate"
        destination.mkdir()

        def build_minimal(staging: Path) -> None:
            (staging / "release-manifest.json").write_text("{}\n", encoding="utf-8")

        with (
            mock.patch.object(
                sys,
                "argv",
                ["package_release_candidate.py", "--output-dir", str(destination)],
            ),
            mock.patch.object(
                package_release_candidate, "create_candidate", side_effect=build_minimal
            ),
        ):
            diagnostics = io.StringIO()
            with contextlib.redirect_stdout(diagnostics):
                self.assertEqual(package_release_candidate.main(), 0)
        self.assertIn("Packaged non-publication", diagnostics.getvalue())
        self.assertEqual(
            (destination / "release-manifest.json").read_text(encoding="utf-8"),
            "{}\n",
        )
        self.assertEqual(list(self.root.glob(".published-candidate.*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
