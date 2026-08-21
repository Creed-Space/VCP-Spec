"""Bounded, race-aware filesystem primitives for repository validation tools."""

from __future__ import annotations

import hashlib
import os
import stat
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path


def _label(path: Path, root: Path | None) -> str:
    if root is None:
        return str(path)
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _fingerprint(item: os.stat_result) -> tuple[int, int, int, int, int]:
    return (
        item.st_dev,
        item.st_ino,
        item.st_size,
        item.st_mtime_ns,
        item.st_ctime_ns,
    )


@dataclass(frozen=True)
class RegularFileSnapshot:
    """Identity and mutation-sensitive metadata captured during safe traversal."""

    path: Path
    fingerprint: tuple[int, int, int, int, int]

    @classmethod
    def capture(cls, path: Path, metadata: os.stat_result) -> RegularFileSnapshot:
        return cls(path=path, fingerprint=_fingerprint(metadata))

    @property
    def size(self) -> int:
        return self.fingerprint[2]

    def matches(self, metadata: os.stat_result) -> bool:
        return self.fingerprint == _fingerprint(metadata)


def _directory_open_flags() -> int:
    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    return flags


def _open_parent_beneath(path: Path, root: Path) -> tuple[int, str]:
    """Open path's parent through no-follow directory descriptors beneath root."""
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"path escapes declared root: {path}") from exc
    parts = relative.parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"path is not a file beneath declared root: {path}")
    descriptor = os.open(root, _directory_open_flags())
    try:
        for part in parts[:-1]:
            child = os.open(
                part,
                _directory_open_flags(),
                dir_fd=descriptor,
            )
            os.close(descriptor)
            descriptor = child
        return descriptor, parts[-1]
    except BaseException:
        os.close(descriptor)
        raise


def _lstat_beneath(path: Path, root: Path) -> os.stat_result:
    parent, name = _open_parent_beneath(path, root)
    try:
        return os.stat(name, dir_fd=parent, follow_symlinks=False)
    finally:
        os.close(parent)


def require_regular_file(
    path: Path,
    *,
    max_bytes: int,
    root: Path | None = None,
    purpose: str = "input",
) -> os.stat_result:
    """Return lstat metadata after rejecting links, special files, and oversize files."""
    if max_bytes < 0:
        raise ValueError("max_bytes must be non-negative")
    metadata = _lstat_beneath(path, root) if root is not None else os.lstat(path)
    label = _label(path, root)
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise ValueError(f"{purpose} is not a regular file: {label}")
    if metadata.st_size > max_bytes:
        raise ValueError(
            f"{purpose} exceeds {max_bytes} bytes: {label} ({metadata.st_size} bytes)"
        )
    return metadata


def _open_regular_fd(
    path: Path,
    *,
    max_bytes: int,
    root: Path | None,
    purpose: str,
    expected: RegularFileSnapshot | None = None,
) -> tuple[int, os.stat_result]:
    before_open = require_regular_file(
        path, max_bytes=max_bytes, root=root, purpose=purpose
    )
    if expected is not None:
        if expected.path != path:
            raise ValueError(
                f"{purpose} snapshot does not identify {_label(path, root)}"
            )
        if not expected.matches(before_open):
            raise ValueError(
                f"{purpose} changed since inventory: {_label(path, root)}"
            )
    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    if root is None:
        descriptor = os.open(path, flags)
    else:
        parent, name = _open_parent_beneath(path, root)
        try:
            descriptor = os.open(name, flags, dir_fd=parent)
        finally:
            os.close(parent)
    actual = os.fstat(descriptor)
    if not stat.S_ISREG(actual.st_mode):
        os.close(descriptor)
        raise ValueError(f"{purpose} changed to a non-regular file: {_label(path, root)}")
    if (actual.st_dev, actual.st_ino) != (before_open.st_dev, before_open.st_ino):
        os.close(descriptor)
        raise ValueError(f"{purpose} changed before it could be read: {_label(path, root)}")
    if expected is not None and not expected.matches(actual):
        os.close(descriptor)
        raise ValueError(
            f"{purpose} changed since inventory: {_label(path, root)}"
        )
    if actual.st_size > max_bytes:
        os.close(descriptor)
        raise ValueError(
            f"{purpose} exceeds {max_bytes} bytes: {_label(path, root)} "
            f"({actual.st_size} bytes)"
        )
    return descriptor, actual


def _verify_unchanged(
    path: Path,
    descriptor: int,
    before: os.stat_result,
    *,
    root: Path | None,
    purpose: str,
) -> None:
    after = os.fstat(descriptor)
    try:
        current = _lstat_beneath(path, root) if root is not None else os.lstat(path)
    except OSError as exc:
        raise ValueError(f"{purpose} disappeared while being read: {_label(path, root)}") from exc
    if _fingerprint(after) != _fingerprint(before) or (
        current.st_dev,
        current.st_ino,
    ) != (before.st_dev, before.st_ino):
        raise ValueError(f"{purpose} changed while being read: {_label(path, root)}")


def read_regular_bytes(
    path: Path,
    *,
    max_bytes: int,
    root: Path | None = None,
    purpose: str = "input",
    expected: RegularFileSnapshot | None = None,
) -> bytes:
    descriptor, before = _open_regular_fd(
        path,
        max_bytes=max_bytes,
        root=root,
        purpose=purpose,
        expected=expected,
    )
    try:
        chunks: list[bytes] = []
        total = 0
        while chunk := os.read(descriptor, min(1024 * 1024, max_bytes + 1 - total)):
            total += len(chunk)
            if total > max_bytes:
                raise ValueError(
                    f"{purpose} grew beyond {max_bytes} bytes while being read: "
                    f"{_label(path, root)}"
                )
            chunks.append(chunk)
        _verify_unchanged(
            path, descriptor, before, root=root, purpose=purpose
        )
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def read_regular_text(
    path: Path,
    *,
    max_bytes: int,
    root: Path | None = None,
    purpose: str = "input",
    expected: RegularFileSnapshot | None = None,
) -> str:
    return read_regular_bytes(
        path,
        max_bytes=max_bytes,
        root=root,
        purpose=purpose,
        expected=expected,
    ).decode("utf-8")


def sha256_regular(
    path: Path,
    *,
    max_bytes: int,
    root: Path | None = None,
    purpose: str = "input",
    expected: RegularFileSnapshot | None = None,
) -> tuple[str, int]:
    descriptor, before = _open_regular_fd(
        path,
        max_bytes=max_bytes,
        root=root,
        purpose=purpose,
        expected=expected,
    )
    digest = hashlib.sha256()
    total = 0
    try:
        while chunk := os.read(
            descriptor, min(1024 * 1024, max_bytes + 1 - total)
        ):
            total += len(chunk)
            if total > max_bytes:
                raise ValueError(
                    f"{purpose} grew beyond {max_bytes} bytes while being read: "
                    f"{_label(path, root)}"
                )
            digest.update(chunk)
        _verify_unchanged(
            path, descriptor, before, root=root, purpose=purpose
        )
    finally:
        os.close(descriptor)
    return digest.hexdigest(), total


def portability_collision_key(relative: str) -> str:
    """Return the cross-platform comparison key used for candidate paths."""
    return unicodedata.normalize("NFC", relative).casefold()


def regular_file_snapshots_below(
    root: Path,
    *,
    max_files: int,
    max_file_bytes: int,
    max_total_bytes: int,
    purpose: str,
    max_directories: int | None = None,
    max_depth: int = 128,
) -> list[RegularFileSnapshot]:
    """Capture a bounded deterministic tree inventory without following links."""
    directory_limit = max_files if max_directories is None else max_directories
    if min(max_files, max_file_bytes, max_total_bytes, directory_limit, max_depth) < 0:
        raise ValueError("tree inventory bounds must be non-negative")
    metadata = os.lstat(root)
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        raise ValueError(f"{purpose} root is not a regular directory: {root}")
    files: list[RegularFileSnapshot] = []
    total_bytes = 0
    directory_count = 0
    discovered_files = 0
    discovered_directories = 0
    normalized: dict[str, str] = {}
    root_descriptor = os.open(root, _directory_open_flags())
    actual_root = os.fstat(root_descriptor)
    if (actual_root.st_dev, actual_root.st_ino) != (metadata.st_dev, metadata.st_ino):
        os.close(root_descriptor)
        raise ValueError(f"{purpose} root changed before traversal: {root}")

    def walk(prefix: Path, directory_descriptor: int, depth: int) -> None:
        nonlocal directory_count, discovered_directories, discovered_files, total_bytes
        if depth > max_depth:
            raise ValueError(f"{purpose} exceeds {max_depth} directory levels")
        ordered: list[tuple[str, os.stat_result]] = []
        with os.scandir(directory_descriptor) as entries:
            for entry in entries:
                entry_metadata = entry.stat(follow_symlinks=False)
                if stat.S_ISLNK(entry_metadata.st_mode):
                    raise ValueError(
                        f"{purpose} contains a symbolic link: "
                        f"{(prefix / entry.name).as_posix()}"
                    )
                if stat.S_ISDIR(entry_metadata.st_mode):
                    discovered_directories += 1
                    if discovered_directories > directory_limit:
                        raise ValueError(
                            f"{purpose} exceeds {directory_limit} directories"
                        )
                elif stat.S_ISREG(entry_metadata.st_mode):
                    discovered_files += 1
                    if discovered_files > max_files:
                        raise ValueError(f"{purpose} exceeds {max_files} files")
                else:
                    raise ValueError(
                        f"{purpose} contains a non-regular file: "
                        f"{(prefix / entry.name).as_posix()}"
                    )
                ordered.append((entry.name, entry_metadata))
        ordered.sort()
        for name, entry_metadata in ordered:
            relative_path = prefix / name
            relative = relative_path.as_posix()
            path = root / relative_path
            collision_key = portability_collision_key(relative)
            previous = normalized.get(collision_key)
            if previous is not None and previous != relative:
                raise ValueError(
                    f"{purpose} contains portability-colliding paths: "
                    f"{previous!r} and {relative!r}"
                )
            normalized[collision_key] = relative
            if stat.S_ISLNK(entry_metadata.st_mode):
                raise ValueError(f"{purpose} contains a symbolic link: {relative}")
            if stat.S_ISDIR(entry_metadata.st_mode):
                directory_count += 1
                if directory_count > directory_limit:
                    raise ValueError(
                        f"{purpose} exceeds {directory_limit} directories"
                    )
                child = os.open(
                    name,
                    _directory_open_flags(),
                    dir_fd=directory_descriptor,
                )
                try:
                    child_metadata = os.fstat(child)
                    if (
                        child_metadata.st_dev,
                        child_metadata.st_ino,
                    ) != (entry_metadata.st_dev, entry_metadata.st_ino):
                        raise ValueError(
                            f"{purpose} directory changed during traversal: {relative}"
                        )
                    walk(relative_path, child, depth + 1)
                finally:
                    os.close(child)
                continue
            if not stat.S_ISREG(entry_metadata.st_mode):
                raise ValueError(f"{purpose} contains a non-regular file: {relative}")
            if entry_metadata.st_size > max_file_bytes:
                raise ValueError(
                    f"{purpose} file exceeds {max_file_bytes} bytes: {relative}"
                )
            total_bytes += entry_metadata.st_size
            if total_bytes > max_total_bytes:
                raise ValueError(f"{purpose} exceeds {max_total_bytes} total bytes")
            files.append(RegularFileSnapshot.capture(path, entry_metadata))
            if len(files) > max_files:
                raise ValueError(f"{purpose} exceeds {max_files} files")

    try:
        walk(Path(), root_descriptor, 0)
    finally:
        os.close(root_descriptor)
    return sorted(
        files,
        key=lambda item: item.path.relative_to(root).as_posix(),
    )


def regular_files_below(
    root: Path,
    *,
    max_files: int,
    max_file_bytes: int,
    max_total_bytes: int,
    purpose: str,
    max_directories: int | None = None,
    max_depth: int = 128,
) -> list[Path]:
    """Return paths from a bounded, race-aware deterministic tree inventory."""
    return [
        item.path
        for item in regular_file_snapshots_below(
            root,
            max_files=max_files,
            max_file_bytes=max_file_bytes,
            max_total_bytes=max_total_bytes,
            purpose=purpose,
            max_directories=max_directories,
            max_depth=max_depth,
        )
    ]


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, _directory_open_flags())
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _backup_regular_file(
    path: Path,
    expected: os.stat_result,
) -> Path:
    """Create a verified, durable sibling backup without following links."""
    backup_descriptor, backup_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".bak",
    )
    backup = Path(backup_name)
    source_descriptor = -1
    try:
        flags = os.O_RDONLY
        if hasattr(os, "O_CLOEXEC"):
            flags |= os.O_CLOEXEC
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        source_descriptor = os.open(path, flags)
        actual = os.fstat(source_descriptor)
        if not stat.S_ISREG(actual.st_mode) or _fingerprint(actual) != _fingerprint(
            expected
        ):
            raise ValueError(f"output changed before backup: {path}")
        copied = 0
        while chunk := os.read(source_descriptor, 1024 * 1024):
            copied += len(chunk)
            view = memoryview(chunk)
            while view:
                written = os.write(backup_descriptor, view)
                if written <= 0:
                    raise OSError("backup write made no progress")
                view = view[written:]
        if copied != expected.st_size:
            raise ValueError(f"output changed while being backed up: {path}")
        _verify_unchanged(
            path,
            source_descriptor,
            actual,
            root=None,
            purpose="output",
        )
        os.fchmod(backup_descriptor, stat.S_IMODE(expected.st_mode))
        os.fsync(backup_descriptor)
    except BaseException:
        backup.unlink(missing_ok=True)
        raise
    finally:
        if source_descriptor >= 0:
            os.close(source_descriptor)
        os.close(backup_descriptor)
    return backup


def atomic_write_text(path: Path, text: str) -> None:
    """Replace UTF-8 text atomically, restoring prior state after late failure."""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        existing = os.lstat(path)
    except FileNotFoundError:
        existing = None
        output_mode = 0o644
    else:
        if stat.S_ISLNK(existing.st_mode) or not stat.S_ISREG(existing.st_mode):
            raise ValueError(f"output is not a regular file: {path}")
        output_mode = stat.S_IMODE(existing.st_mode)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    temporary = Path(temporary_name)
    backup: Path | None = None
    installed = False
    try:
        stream = os.fdopen(descriptor, "w", encoding="utf-8", newline="\n")
        descriptor = -1
        with stream:
            os.fchmod(stream.fileno(), output_mode)
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        if existing is not None:
            backup = _backup_regular_file(path, existing)
        os.replace(temporary, path)
        installed = True
        _fsync_directory(path.parent)
    except BaseException as primary:
        rollback_error: OSError | None = None
        if installed:
            try:
                if backup is None:
                    path.unlink(missing_ok=True)
                else:
                    os.replace(backup, path)
                    backup = None
                _fsync_directory(path.parent)
            except OSError as exc:
                rollback_error = exc
        temporary.unlink(missing_ok=True)
        if backup is not None:
            backup.unlink(missing_ok=True)
        if descriptor >= 0:
            os.close(descriptor)
        if rollback_error is not None:
            raise RuntimeError(
                f"atomic write failed and prior output could not be restored: {path}: "
                f"{rollback_error}"
            ) from primary
        raise
    else:
        temporary.unlink(missing_ok=True)
        if backup is not None:
            backup.unlink()
