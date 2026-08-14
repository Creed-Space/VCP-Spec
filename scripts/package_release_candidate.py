#!/usr/bin/env python3
"""Create a deterministic, non-publication VCP specification candidate bundle."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import stat
import subprocess
import sys
import tarfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_FILE_BYTES = 50 * 1024 * 1024
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
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def selected_paths() -> list[Path]:
    paths = [ROOT / relative for relative in INCLUDE_FILES]
    for relative in INCLUDE_ROOTS:
        paths.extend(path for path in (ROOT / relative).rglob("*") if path.is_file())
    return sorted({path for path in paths if path.is_file()})


def add_file(archive: tarfile.TarFile, path: Path, epoch: int) -> None:
    metadata = os.lstat(path)
    relative = path.relative_to(ROOT).as_posix()
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise ValueError(f"candidate input is not a regular file: {relative}")
    if metadata.st_size > MAX_FILE_BYTES:
        raise ValueError(f"candidate input exceeds 50 MiB: {relative}")
    info = archive.gettarinfo(str(path), arcname=relative)
    info.uid = 0
    info.gid = 0
    info.uname = "root"
    info.gname = "root"
    info.mode = 0o644
    info.mtime = epoch
    with path.open("rb") as stream:
        archive.addfile(info, stream)


def build_archive(output: Path, paths: list[Path], epoch: int) -> None:
    with (
        output.open("wb") as raw,
        gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=epoch) as zipped,
        tarfile.open(fileobj=zipped, mode="w", format=tarfile.PAX_FORMAT) as archive,
    ):
        for path in paths:
            add_file(archive, path, epoch)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--require-clean", action="store_true")
    args = parser.parse_args()
    try:
        if args.require_clean and git("status", "--porcelain"):
            raise ValueError(
                "--require-clean was requested but the source tree is dirty"
            )
        output = args.output_dir.resolve()
        if output.exists() and any(output.iterdir()):
            raise ValueError(f"output directory must be empty: {output}")
        output.mkdir(parents=True, exist_ok=True)
        paths = selected_paths()
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
        build_archive(archive, paths, epoch)
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
        for source in sorted((ROOT / "artifacts" / "rendered-candidates").iterdir()):
            if not source.is_file() or source.name in {"README.md", "manifest.json"}:
                continue
            destination = rendered_output / source.name
            destination.write_bytes(source.read_bytes())
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
        checksums.write_text(
            "".join(f"{item['sha256']}  {item['path']}\n" for item in files),
            encoding="utf-8",
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
        manifest_path = output / "release-manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Packaged non-publication specification candidate: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
