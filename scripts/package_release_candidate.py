#!/usr/bin/env python3
"""Create a deterministic, non-publication VCP specification candidate bundle."""

from __future__ import annotations

import argparse
import gzip
import io
import json
import os
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path

from validation_utils import (
    RegularFileSnapshot,
    atomic_write_text,
    read_regular_bytes,
    regular_file_snapshots_below,
    require_regular_file,
    sha256_regular,
)

ROOT = Path(__file__).resolve().parents[1]
MAX_FILE_BYTES = 50 * 1024 * 1024
MAX_CANDIDATE_FILES = 10_000
MAX_CANDIDATE_BYTES = 1024 * 1024 * 1024
INCLUDE_ROOTS = (
    "docs",
    "governance",
    "schemas",
    "specs",
    "status",
    "veps",
    "reviews",
)
INCLUDE_FILES = (
    "README.md",
    "GOVERNANCE.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "LICENSING_STATUS.md",
    "ARTIFACTS.md",
    "CHANGELOG.md",
    "CITATION.cff",
    "COMPATIBILITY.md",
    "DEPENDENCY_POLICY.md",
    "RELEASE_CHECKLIST.md",
    "REPOSITORY_CONTROLS.md",
    "LICENSE",
)


def git(*arguments: str) -> str:
    return subprocess.run(
        ("git", *arguments),
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def sha256(path: Path) -> str:
    digest, _ = sha256_regular(
        path,
        max_bytes=MAX_CANDIDATE_BYTES,
        purpose="candidate output",
    )
    return digest


def selected_snapshots() -> list[RegularFileSnapshot]:
    snapshots: list[RegularFileSnapshot] = []
    total_bytes = 0
    for relative in INCLUDE_FILES:
        path = ROOT / relative
        if not path.exists():
            continue
        metadata = require_regular_file(
            path,
            max_bytes=MAX_FILE_BYTES,
            root=ROOT,
            purpose="candidate source",
        )
        snapshots.append(RegularFileSnapshot.capture(path, metadata))
        total_bytes += metadata.st_size
        if len(snapshots) > MAX_CANDIDATE_FILES:
            raise ValueError(
                f"candidate source exceeds {MAX_CANDIDATE_FILES} files"
            )
        if total_bytes > MAX_CANDIDATE_BYTES:
            raise ValueError(
                f"candidate source exceeds {MAX_CANDIDATE_BYTES} total bytes"
            )
    for relative in INCLUDE_ROOTS:
        remaining_files = MAX_CANDIDATE_FILES - len(snapshots)
        remaining_bytes = MAX_CANDIDATE_BYTES - total_bytes
        selected = regular_file_snapshots_below(
            ROOT / relative,
            max_files=remaining_files,
            max_file_bytes=MAX_FILE_BYTES,
            max_total_bytes=remaining_bytes,
            purpose=f"candidate source {relative}",
        )
        snapshots.extend(selected)
        total_bytes += sum(item.size for item in selected)
        if total_bytes > MAX_CANDIDATE_BYTES:
            raise ValueError(
                f"candidate source exceeds {MAX_CANDIDATE_BYTES} total bytes"
            )
    unique = {item.path: item for item in snapshots}
    return [unique[path] for path in sorted(unique)]


def selected_paths() -> list[Path]:
    """Return the selected source paths while retaining the legacy helper API."""
    return [item.path for item in selected_snapshots()]


def add_file(
    archive: tarfile.TarFile,
    source: Path | RegularFileSnapshot,
    epoch: int,
) -> int:
    snapshot = source if isinstance(source, RegularFileSnapshot) else None
    path = snapshot.path if snapshot is not None else source
    relative = path.relative_to(ROOT).as_posix()
    content = read_regular_bytes(
        path,
        max_bytes=MAX_FILE_BYTES,
        root=ROOT,
        purpose="candidate input",
        expected=snapshot,
    )
    info = tarfile.TarInfo(relative)
    info.size = len(content)
    info.uid = 0
    info.gid = 0
    info.uname = "root"
    info.gname = "root"
    info.mode = 0o644
    info.mtime = epoch
    archive.addfile(info, io.BytesIO(content))
    return len(content)


def build_archive(
    output: Path,
    sources: list[Path | RegularFileSnapshot],
    epoch: int,
) -> None:
    if len(sources) > MAX_CANDIDATE_FILES:
        raise ValueError(f"candidate source exceeds {MAX_CANDIDATE_FILES} files")
    descriptor, temporary_name = tempfile.mkstemp(
        dir=output.parent, prefix=f".{output.name}.", suffix=".tmp"
    )
    temporary = Path(temporary_name)
    try:
        with (
            os.fdopen(descriptor, "wb") as raw,
            gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=epoch) as zipped,
            tarfile.open(
                fileobj=zipped, mode="w", format=tarfile.PAX_FORMAT
            ) as archive,
        ):
            total_bytes = 0
            for source in sources:
                total_bytes += add_file(archive, source, epoch)
                if total_bytes > MAX_CANDIDATE_BYTES:
                    raise ValueError(
                        f"candidate source exceeds {MAX_CANDIDATE_BYTES} total bytes"
                    )
        with temporary.open("rb") as stream:
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o600)
        os.replace(temporary, output)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def copy_regular_candidate(
    source: Path | RegularFileSnapshot,
    destination: Path,
) -> None:
    snapshot = source if isinstance(source, RegularFileSnapshot) else None
    path = snapshot.path if snapshot is not None else source
    content = read_regular_bytes(
        path,
        max_bytes=MAX_FILE_BYTES,
        root=ROOT,
        purpose="rendered candidate input",
        expected=snapshot,
    )
    created = False
    try:
        writer = destination.open("xb")
        created = True
        with writer:
            writer.write(content)
            writer.flush()
            os.fsync(writer.fileno())
    except BaseException:
        if created:
            destination.unlink(missing_ok=True)
        raise


def create_candidate(output: Path) -> None:
    """Build a complete candidate inside an unpublished staging directory."""
    snapshots = selected_snapshots()
    missing = [
        relative for relative in INCLUDE_FILES if not (ROOT / relative).is_file()
    ]
    if missing:
        raise ValueError(f"required candidate files are missing: {missing}")
    git_head = git("rev-parse", "HEAD")
    epoch = int(git("show", "-s", "--format=%ct", "HEAD"))
    timestamp = (
        datetime.fromisoformat(git("show", "-s", "--format=%cI", "HEAD"))
        .isoformat()
        .replace("+00:00", "Z")
    )
    archive = output / "vcp-spec-source-candidate.tar.gz"
    build_archive(archive, snapshots, epoch)
    files: list[dict[str, object]] = [
        {
            "path": archive.name,
            "kind": "source-candidate",
            "canonical": False,
            "size_bytes": archive.stat().st_size,
            "sha256": sha256(archive),
        }
    ]
    rendered_output = output / "rendered-candidates"
    rendered_output.mkdir()
    rendered_root = ROOT / "artifacts" / "rendered-candidates"
    rendered_metadata = os.lstat(rendered_root)
    if stat.S_ISLNK(rendered_metadata.st_mode) or not stat.S_ISDIR(
        rendered_metadata.st_mode
    ):
        raise ValueError("rendered candidate source must be a regular directory")
    rendered_sources = regular_file_snapshots_below(
        rendered_root,
        max_files=MAX_CANDIDATE_FILES,
        max_file_bytes=MAX_FILE_BYTES,
        max_total_bytes=MAX_CANDIDATE_BYTES,
        purpose="rendered candidate source",
    )
    for source in rendered_sources:
        if source.path.parent != rendered_root or source.path.name in {
            "README.md",
            "manifest.json",
        }:
            continue
        destination = rendered_output / source.path.name
        copy_regular_candidate(source, destination)
        files.append(
            {
                "path": destination.relative_to(output).as_posix(),
                "kind": "rendered-document-candidate",
                "canonical": False,
                "size_bytes": destination.stat().st_size,
                "sha256": sha256(destination),
            }
        )
    checksums = output / "SHA256SUMS"
    atomic_write_text(
        checksums,
        "".join(f"{item['sha256']}  {item['path']}\n" for item in files),
    )
    files.append(
        {
            "path": checksums.name,
            "kind": "checksum-list",
            "canonical": False,
            "size_bytes": checksums.stat().st_size,
            "sha256": sha256(checksums),
        }
    )
    manifest = {
        "schema": "vcp-spec-release-candidate-manifest/1",
        "source_commit": git_head,
        "source_commit_time": timestamp,
        "publication_authorized": False,
        "canonical_render_selected": False,
        "rights_review_complete": False,
        "manifest_scope": "all candidate files except this self-referential manifest",
        "files": files,
    }
    atomic_write_text(
        output / "release-manifest.json",
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--require-clean", action="store_true")
    args = parser.parse_args()
    staging: Path | None = None
    committed: Path | None = None
    try:
        if args.require_clean and git("status", "--porcelain"):
            raise ValueError(
                "--require-clean was requested but the source tree is dirty"
            )
        output = args.output_dir.resolve()
        try:
            output.relative_to(ROOT)
        except ValueError:
            pass
        else:
            raise ValueError("output directory must be outside the source repository")
        if output.exists():
            metadata = os.lstat(output)
            if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
                raise ValueError(f"output path must be a regular directory: {output}")
            if any(output.iterdir()):
                raise ValueError(f"output directory must be empty: {output}")
        output.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(
            tempfile.mkdtemp(
                dir=output.parent,
                prefix=f".{output.name}.",
                suffix=".tmp",
            )
        )
        create_candidate(staging)
        os.replace(staging, output)
        staging = None
        committed = output
        directory_flags = os.O_RDONLY
        if hasattr(os, "O_DIRECTORY"):
            directory_flags |= os.O_DIRECTORY
        directory = os.open(output.parent, directory_flags)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
        committed = None
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    finally:
        if staging is not None:
            try:
                shutil.rmtree(staging)
            except OSError as exc:
                print(f"ERROR: could not remove candidate staging directory: {exc}", file=sys.stderr)
        if committed is not None:
            try:
                shutil.rmtree(committed)
            except OSError as exc:
                print(f"ERROR: could not roll back candidate output: {exc}", file=sys.stderr)
    print(
        "Packaged non-publication specification candidate: "
        f"{output / 'release-manifest.json'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
