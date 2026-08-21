from __future__ import annotations

import hashlib
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validation_utils
from validation_utils import (
    atomic_write_text,
    portability_collision_key,
    read_regular_bytes,
    read_regular_text,
    regular_files_below,
    require_regular_file,
    sha256_regular,
)


class RegularFilePrimitiveTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_exact_size_bound_and_digest(self) -> None:
        path = self.root / "data.bin"
        path.write_bytes(b"abcd")
        self.assertEqual(read_regular_bytes(path, max_bytes=4), b"abcd")
        digest, size = sha256_regular(path, max_bytes=4)
        self.assertEqual(digest, hashlib.sha256(b"abcd").hexdigest())
        self.assertEqual(size, 4)
        with self.assertRaisesRegex(ValueError, "exceeds 3 bytes"):
            read_regular_bytes(path, max_bytes=3)
        with self.assertRaisesRegex(ValueError, "non-negative"):
            require_regular_file(path, max_bytes=-1)

    def test_text_decoding_and_file_type_rejection(self) -> None:
        invalid = self.root / "invalid.txt"
        invalid.write_bytes(b"\xff")
        with self.assertRaises(UnicodeDecodeError):
            read_regular_text(invalid, max_bytes=1)

        target = self.root / "target"
        target.write_text("content", encoding="utf-8")
        link = self.root / "link"
        link.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "not a regular file"):
            read_regular_bytes(link, max_bytes=100)

        fifo = self.root / "fifo"
        os.mkfifo(fifo)
        with self.assertRaisesRegex(ValueError, "not a regular file"):
            require_regular_file(fifo, max_bytes=100)

    def test_replacement_between_stat_and_open_is_detected(self) -> None:
        path = self.root / "race.txt"
        path.write_text("first", encoding="utf-8")
        real_require = validation_utils.require_regular_file

        def replace_after_stat(*args, **kwargs):
            metadata = real_require(*args, **kwargs)
            replacement = self.root / "replacement"
            replacement.write_text("other", encoding="utf-8")
            os.replace(replacement, path)
            return metadata

        with (
            mock.patch.object(
                validation_utils, "require_regular_file", side_effect=replace_after_stat
            ),
            self.assertRaisesRegex(ValueError, "changed before it could be read"),
        ):
            read_regular_bytes(path, max_bytes=100)

    def test_in_place_mutation_during_read_is_detected(self) -> None:
        path = self.root / "race.txt"
        path.write_bytes(b"original")
        real_read = os.read
        mutated = False

        def mutate_after_read(descriptor: int, amount: int) -> bytes:
            nonlocal mutated
            chunk = real_read(descriptor, amount)
            if chunk and not mutated:
                mutated = True
                path.write_bytes(b"changed!")
            return chunk

        with (
            mock.patch.object(validation_utils.os, "read", side_effect=mutate_after_read),
            self.assertRaisesRegex(ValueError, "changed while being read"),
        ):
            read_regular_bytes(path, max_bytes=100)


class TreeAndAtomicWriteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def inventory(self, **overrides) -> list[Path]:
        bounds = {
            "max_files": 10,
            "max_file_bytes": 10,
            "max_total_bytes": 20,
            "purpose": "test tree",
        }
        bounds.update(overrides)
        return regular_files_below(self.root, **bounds)

    def test_tree_inventory_is_sorted_and_each_resource_bound_is_enforced(self) -> None:
        (self.root / "b.txt").write_bytes(b"bb")
        nested = self.root / "nested"
        nested.mkdir()
        (nested / "a.txt").write_bytes(b"aaa")
        self.assertEqual(
            [path.relative_to(self.root).as_posix() for path in self.inventory()],
            ["b.txt", "nested/a.txt"],
        )
        with self.assertRaisesRegex(ValueError, "exceeds 1 files"):
            self.inventory(max_files=1)
        with self.assertRaisesRegex(ValueError, "file exceeds 2 bytes"):
            self.inventory(max_file_bytes=2)
        with self.assertRaisesRegex(ValueError, "exceeds 4 total bytes"):
            self.inventory(max_total_bytes=4)
        with self.assertRaisesRegex(ValueError, "exceeds 0 directories"):
            self.inventory(max_directories=0)
        with self.assertRaisesRegex(ValueError, "exceeds 0 directory levels"):
            self.inventory(max_depth=0)
        with self.assertRaisesRegex(ValueError, "non-negative"):
            self.inventory(max_files=-1)

    def test_tree_inventory_rejects_links_and_portability_collisions(self) -> None:
        target = self.root / "target"
        target.write_text("x", encoding="utf-8")
        link = self.root / "link"
        link.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "symbolic link"):
            self.inventory()
        self.assertEqual(
            portability_collision_key("Folder/É.txt"),
            portability_collision_key("folder/E\u0301.TXT"),
        )
        link.unlink()
        (self.root / "another").write_text("x", encoding="utf-8")
        with (
            mock.patch.object(
                validation_utils,
                "portability_collision_key",
                return_value="same-portable-path",
            ),
            self.assertRaisesRegex(ValueError, "portability-colliding"),
        ):
            self.inventory()

    def test_directory_replacement_race_and_intermediate_symlink_are_rejected(self) -> None:
        walk_root = self.root / "walk"
        child = walk_root / "child"
        child.mkdir(parents=True)
        (child / "inside.txt").write_text("inside", encoding="utf-8")
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "secret.txt").write_text("secret", encoding="utf-8")
        backup = walk_root / "original-child"
        real_open = os.open
        replaced = False

        def replace_before_descent(path, flags, *args, **kwargs):
            nonlocal replaced
            if path == "child" and kwargs.get("dir_fd") is not None and not replaced:
                replaced = True
                child.rename(backup)
                child.symlink_to(outside, target_is_directory=True)
            return real_open(path, flags, *args, **kwargs)

        with (
            mock.patch.object(
                validation_utils.os, "open", side_effect=replace_before_descent
            ),
            self.assertRaises(OSError),
        ):
            regular_files_below(
                walk_root,
                max_files=10,
                max_file_bytes=100,
                max_total_bytes=100,
                purpose="raced tree",
            )

        with self.assertRaises(OSError):
            read_regular_bytes(
                child / "secret.txt",
                max_bytes=100,
                root=walk_root,
            )

    def test_atomic_write_preserves_mode_and_rejects_unsafe_destination(self) -> None:
        output = self.root / "output.txt"
        output.write_text("old", encoding="utf-8")
        output.chmod(0o600)
        atomic_write_text(output, "new\n")
        self.assertEqual(output.read_text(encoding="utf-8"), "new\n")
        self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)

        link = self.root / "output-link"
        link.symlink_to(output)
        with self.assertRaisesRegex(ValueError, "not a regular file"):
            atomic_write_text(link, "unsafe")
        self.assertEqual(output.read_text(encoding="utf-8"), "new\n")

    def test_atomic_write_cleans_temporary_file_after_replace_failure(self) -> None:
        output = self.root / "output.txt"
        with (
            mock.patch.object(validation_utils.os, "replace", side_effect=OSError("boom")),
            self.assertRaisesRegex(OSError, "boom"),
        ):
            atomic_write_text(output, "new")
        self.assertFalse(output.exists())
        self.assertEqual(list(self.root.glob(".output.txt.*.tmp")), [])

    def test_atomic_write_rolls_back_after_post_replace_durability_failure(self) -> None:
        cases = {"existing": b"old", "absent": None}
        for name, prior in cases.items():
            with self.subTest(name=name):
                output = self.root / f"{name}.txt"
                if prior is not None:
                    output.write_bytes(prior)
                    output.chmod(0o600)
                with (
                    mock.patch.object(
                        validation_utils,
                        "_fsync_directory",
                        side_effect=[OSError("directory sync failed"), None],
                    ),
                    self.assertRaisesRegex(OSError, "directory sync failed"),
                ):
                    atomic_write_text(output, "new")
                if prior is None:
                    self.assertFalse(output.exists())
                else:
                    self.assertEqual(output.read_bytes(), prior)
                    self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)
                self.assertEqual(list(self.root.glob(f".{name}.txt.*.tmp")), [])
                self.assertEqual(list(self.root.glob(f".{name}.txt.*.bak")), [])


if __name__ == "__main__":
    unittest.main()
