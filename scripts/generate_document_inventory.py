#!/usr/bin/env python3
"""Generate explicit status metadata for every specification artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "status" / "document-inventory.json"
REVIEW_DATE = "2026-08-15"
ROOTS = ("specs", "schemas", "registries", "veps", "archives")


def artifact_paths() -> list[Path]:
    paths = {
        path
        for root in ROOTS
        for path in (ROOT / root).rglob("*")
        if path.is_file() and path.suffix.lower() in {".md", ".json", ".yaml", ".yml"}
    }
    paths.add(ROOT / "status" / "document-inventory.schema.json")
    paths.add(ROOT / "status" / "residual-risks.json")
    paths.add(ROOT / "status" / "residual-risks.schema.json")
    return sorted(paths)


def embedded_status(path: Path) -> str | None:
    if path.suffix.lower() != ".md":
        return None
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^\*\*Status\*\*:\s*([^\n]+)", text, re.MULTILINE)
    return match.group(1).strip().lower().replace(" ", "-") if match else None


def version_for(path: Path) -> str:
    match = re.search(
        r"(?:_v|@|version[-_]?)(\d+(?:\.\d+){0,2})",
        path.as_posix(),
        re.IGNORECASE,
    )
    return match.group(1) if match else "embedded-or-unversioned"


def classify(path: Path) -> dict[str, object]:
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
        status = embedded_status(path) or "proposal-status-undeclared"
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
        status = embedded_status(path) or status
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
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def build() -> dict[str, object]:
    return {
        "schema": "vcp-document-inventory/1",
        "generated_by": "scripts/generate_document_inventory.py",
        "claim_boundary": (
            "This inventory records source status and ownership. It does not ratify "
            "governance, rights, normative publication, accessibility, or independent review."
        ),
        "artifacts": [classify(path) for path in artifact_paths()],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    document = build()
    expected = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != expected:
            print("Document inventory is stale: status/document-inventory.json")
            return 1
        print(f"Document inventory verified: {len(document['artifacts'])} artifacts")
        return 0
    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"Document inventory generated: {len(document['artifacts'])} artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
