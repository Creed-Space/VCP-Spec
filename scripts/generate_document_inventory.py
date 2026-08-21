#!/usr/bin/env python3
"""Generate explicit status metadata for every specification artifact."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from validation_utils import (
    RegularFileSnapshot,
    atomic_write_text,
    read_regular_text,
    regular_file_snapshots_below,
    require_regular_file,
    sha256_regular,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "status" / "document-inventory.json"
REVIEW_DATE = "2026-08-15"
ROOTS = ("specs", "schemas", "registries", "veps", "archives")
EXTRA_ARTIFACTS = (
    "status/document-inventory.schema.json",
    "status/residual-risks.json",
    "status/residual-risks.schema.json",
)
MAX_ARTIFACT_BYTES = 50 * 1024 * 1024
MAX_ARTIFACT_FILES = 10_000
MAX_ARTIFACT_TOTAL_BYTES = 1024 * 1024 * 1024


def artifact_sha256(path: Path, snapshot: RegularFileSnapshot) -> str:
    digest, _ = sha256_regular(
        path,
        max_bytes=MAX_ARTIFACT_BYTES,
        root=ROOT,
        purpose="inventory artifact",
        expected=snapshot,
    )
    return digest


def artifact_snapshots() -> list[RegularFileSnapshot]:
    snapshots: list[RegularFileSnapshot] = []
    total_files = 0
    total_bytes = 0
    for relative in ROOTS:
        selected = regular_file_snapshots_below(
            ROOT / relative,
            max_files=MAX_ARTIFACT_FILES - total_files,
            max_file_bytes=MAX_ARTIFACT_BYTES,
            max_total_bytes=MAX_ARTIFACT_TOTAL_BYTES - total_bytes,
            purpose="document inventory source",
        )
        total_files += len(selected)
        total_bytes += sum(item.size for item in selected)
        snapshots.extend(selected)
    for relative in EXTRA_ARTIFACTS:
        path = ROOT / relative
        metadata = require_regular_file(
            path,
            max_bytes=MAX_ARTIFACT_BYTES,
            root=ROOT,
            purpose="document inventory source",
        )
        total_files += 1
        total_bytes += metadata.st_size
        if total_files > MAX_ARTIFACT_FILES:
            raise ValueError(
                f"document inventory source exceeds {MAX_ARTIFACT_FILES} files"
            )
        if total_bytes > MAX_ARTIFACT_TOTAL_BYTES:
            raise ValueError(
                "document inventory source exceeds "
                f"{MAX_ARTIFACT_TOTAL_BYTES} total bytes"
            )
        snapshots.append(RegularFileSnapshot.capture(path, metadata))
    wanted = {".md", ".json", ".yaml", ".yml"}
    unique = {
        item.path: item for item in snapshots if item.path.suffix.lower() in wanted
    }
    return [unique[path] for path in sorted(unique)]


def artifact_paths() -> list[Path]:
    """Return inventory paths while retaining the historical helper API."""
    return [item.path for item in artifact_snapshots()]


def embedded_status(path: Path, snapshot: RegularFileSnapshot) -> str | None:
    if path.suffix.lower() != ".md":
        return None
    text = read_regular_text(
        path,
        max_bytes=MAX_ARTIFACT_BYTES,
        root=ROOT,
        purpose="inventory artifact",
        expected=snapshot,
    )
    match = re.search(r"^\*\*Status\*\*:\s*([^\n]+)", text, re.MULTILINE)
    return match.group(1).strip().lower().replace(" ", "-") if match else None


def version_for(path: Path) -> str:
    match = re.search(
        r"(?:_v|@|version[-_]?)(\d+(?:\.\d+){0,2})",
        path.as_posix(),
        re.IGNORECASE,
    )
    return match.group(1) if match else "embedded-or-unversioned"


def classify(snapshot: RegularFileSnapshot) -> dict[str, object]:
    path = snapshot.path
    relative = path.relative_to(ROOT).as_posix()
    name = path.name.lower()
    status = "active-source-candidate"
    publication_class = "normative-candidate"
    authority = "Interim VCP-Spec maintainers; immutable release authority remains open"
    replacement: str | None = None
    kind = "specification" if path.suffix == ".md" else "machine-readable-artifact"

    if relative.startswith("archives/"):
        status = "historical-archived"
        publication_class = "historical"
        authority = "Historical record only"
        kind = "archive"
    elif "/examples/" in relative or relative.startswith("schemas/examples/"):
        status = "illustrative"
        publication_class = "illustrative"
        authority = "Example only; controlling specification and schema take precedence"
        kind = "example"
    elif relative.startswith("veps/"):
        publication_class = "proposal"
        authority = "VEP proposal process; acceptance requires an authorized decision"
        kind = "vep"
        status = embedded_status(path, snapshot) or "proposal-status-undeclared"
    elif "paper" in name or name.startswith("draft-watson"):
        status = "research-or-submission-draft"
        publication_class = (
            "historical" if "value_context_protocols_paper" in name else "proposal"
        )
        authority = "Non-normative research or submission draft"
        kind = "research-draft"
    elif name in {
        "vcp_specification_v1.0.md",
        "vcp_specification_v1.1_amendments.md",
        "vcp_specification_v2.0.md",
    }:
        status = "superseded-source-generation"
        publication_class = "historical"
        authority = "Historical source; VCP 3.1 source baseline supersedes it"
        replacement = "specs/VCP_SPECIFICATION_v3.1.md"
    elif name == "vcp_specification_v3.1.md":
        status = "current-source-baseline"
    elif "v3.2" in name:
        status = "candidate-amendment"
        publication_class = "proposal"
        authority = "Candidate amendment; governance acceptance remains open"
    elif relative.startswith("specs/extensions/") and path.name == "spec.md":
        status = embedded_status(path, snapshot) or status
        if status in {"draft", "experimental"}:
            publication_class = "proposal"
    elif relative.startswith("schemas/"):
        kind = "schema"
        status = "source-schema-candidate"

    return {
        "path": relative,
        "kind": kind,
        "status": status,
        "effective_version": version_for(path),
        "authority": authority,
        "dependencies": [],
        "replacement": replacement,
        "owner": "VCP-Spec maintainers",
        "review_date": REVIEW_DATE,
        "publication_class": publication_class,
        "sha256": artifact_sha256(path, snapshot),
    }


def build() -> dict[str, object]:
    return {
        "schema": "vcp-document-inventory/1",
        "generated_by": "scripts/generate_document_inventory.py",
        "claim_boundary": (
            "This inventory records source status and ownership. It does not ratify "
            "governance, rights, normative publication, accessibility, or independent review."
        ),
        "artifacts": [classify(snapshot) for snapshot in artifact_snapshots()],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        document = build()
        expected = json.dumps(document, indent=2, sort_keys=True) + "\n"
        if args.check:
            if not OUTPUT.is_file() or read_regular_text(
                OUTPUT,
                max_bytes=MAX_ARTIFACT_BYTES,
                root=ROOT,
                purpose="document inventory",
            ) != expected:
                print("Document inventory is stale: status/document-inventory.json")
                return 1
            print(
                f"Document inventory verified: {len(document['artifacts'])} artifacts"
            )
            return 0
        atomic_write_text(OUTPUT, expected)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Document inventory generated: {len(document['artifacts'])} artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
