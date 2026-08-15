#!/usr/bin/env python3
"""Generate the honest candidate requirement and legacy-gap registry."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "specs/core/protocol-operations-profile.md"
OUTPUT = ROOT / "registries/candidate-requirements.json"
REVIEW_DATE = "2026-08-15"
HEADING = re.compile(r"^### (VCP-OP-([A-Z]{3})-[0-9]{3}): (.+)$")
NORMATIVE = re.compile(
    r"\b(MUST NOT|SHALL NOT|SHOULD NOT|MUST|SHALL|SHOULD|MAY|REQUIRED|RECOMMENDED)\b"
)
AREA = {
    "NEG": (
        "negotiation",
        "negotiating peer",
        "Reject or restart negotiation without silently selecting a weaker profile.",
    ),
    "REV": (
        "revocation",
        "verifier",
        "Return a non-success verification status and grant no authority.",
    ),
    "SCP": (
        "scope",
        "authorizer",
        "Deny authority that cannot be proven within the complete constrained chain.",
    ),
    "STM": (
        "state-machine",
        "protocol implementation",
        "Reject the transition or return no partial authority.",
    ),
    "REG": (
        "registry",
        "registry consumer or maintainer",
        "Reject an ambiguous identifier or retain its explicitly local status.",
    ),
}
LEGACY_SOURCES = [ROOT / "specs/VCP_SPECIFICATION_v3.1.md"] + sorted(
    path for path in (ROOT / "specs/core").glob("*.md") if path != SOURCE
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def first_paragraph(lines: list[str], start: int) -> str:
    collected: list[str] = []
    for line in lines[start:]:
        stripped = line.strip()
        if not stripped:
            if collected:
                break
            continue
        if stripped.startswith("#"):
            break
        collected.append(stripped)
    return " ".join(collected)


def requirements() -> list[dict[str, object]]:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    records: list[dict[str, object]] = []
    for index, line in enumerate(lines):
        match = HEADING.match(line)
        if match is None:
            continue
        identifier, area_code, title = match.groups()
        area, actor, failure = AREA[area_code]
        records.append(
            {
                "id": identifier,
                "title": title,
                "area": area,
                "actor": actor,
                "testability": "machine",
                "preconditions": [
                    "The selected candidate profile requires this behavior."
                ],
                "requirement_text": first_paragraph(lines, index + 1),
                "failure_semantics": failure,
                "source": {
                    "path": SOURCE.relative_to(ROOT).as_posix(),
                    "line": index + 1,
                    "anchor": identifier.lower(),
                },
                "evidence": [],
            }
        )
    return records


def legacy_gaps() -> list[dict[str, object]]:
    gaps: list[dict[str, object]] = []
    for path in LEGACY_SOURCES:
        in_fence = False
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.lstrip().startswith(("```", "~~~")):
                in_fence = not in_fence
                continue
            if in_fence or "VCP-OP-" in line:
                continue
            keywords = sorted(set(NORMATIVE.findall(line)))
            if keywords:
                gaps.append(
                    {
                        "path": path.relative_to(ROOT).as_posix(),
                        "line": number,
                        "keywords": keywords,
                        "line_sha256": sha256(line.strip().encode("utf-8")),
                    }
                )
    return gaps


def build() -> dict[str, object]:
    identified = requirements()
    sources = [SOURCE, *LEGACY_SOURCES]
    return {
        "schema": "vcp-requirement-registry/1",
        "generated_by": "scripts/generate_requirement_registry.py",
        "as_of": REVIEW_DATE,
        "claim_boundary": (
            "Stable IDs currently cover only the candidate operations profile. "
            "Legacy normative statements are enumerated as open gaps and no empty evidence list is a pass."
        ),
        "sources": [
            {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": sha256(path.read_bytes()),
            }
            for path in sources
        ],
        "requirements": identified,
        "coverage": {
            "identified_requirement_count": len(identified),
            "mapped_evidence_count": sum(bool(item["evidence"]) for item in identified),
            "legacy_normative_statements_without_stable_id": legacy_gaps(),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != rendered:
            print(
                "Requirement registry is stale: registries/candidate-requirements.json"
            )
            return 1
        print("Candidate requirement registry verified")
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8")
    print("Candidate requirement registry generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
