#!/usr/bin/env python3
"""Generate the honest candidate requirement and legacy-gap registry."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from validation_utils import atomic_write_text, read_regular_bytes

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "specs/core/protocol-operations-profile.md"
OUTPUT = ROOT / "registries/candidate-requirements.json"
REVIEW_DATE = "2026-08-15"
MAX_SOURCE_BYTES = 5 * 1024 * 1024
FENCE = re.compile(r"^\s{0,3}(?P<fence>`{3,}|~{3,})")
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


def read_source(path: Path) -> str:
    return read_regular_bytes(
        path,
        max_bytes=MAX_SOURCE_BYTES,
        root=ROOT,
        purpose="requirement source",
    ).decode("utf-8")


def _fence_after_line(active: str | None, line: str) -> str | None:
    match = FENCE.match(line)
    if match is None:
        return active
    marker = match.group("fence")
    if active is None:
        return marker
    suffix = line[match.end() :]
    if marker[0] == active[0] and len(marker) >= len(active) and not suffix.strip():
        return None
    return active


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
        if FENCE.match(line):
            break
        collected.append(stripped)
    return " ".join(collected)


def requirements(source_text: str | None = None) -> list[dict[str, object]]:
    lines = (read_source(SOURCE) if source_text is None else source_text).splitlines()
    records: list[dict[str, object]] = []
    identifiers: set[str] = set()
    active_fence: str | None = None
    for index, line in enumerate(lines):
        previous_fence = active_fence
        active_fence = _fence_after_line(active_fence, line)
        if previous_fence is not None or FENCE.match(line):
            continue
        match = HEADING.match(line)
        if match is None:
            continue
        identifier, area_code, title = match.groups()
        if identifier in identifiers:
            raise ValueError(
                f"duplicate candidate requirement identifier: {identifier}"
            )
        identifiers.add(identifier)
        if area_code not in AREA:
            raise ValueError(
                f"candidate requirement {identifier} has unsupported area {area_code}"
            )
        area, actor, failure = AREA[area_code]
        requirement_text = first_paragraph(lines, index + 1)
        if not requirement_text:
            raise ValueError(
                f"candidate requirement {identifier} has no requirement text"
            )
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
                "requirement_text": requirement_text,
                "failure_semantics": failure,
                "source": {
                    "path": SOURCE.relative_to(ROOT).as_posix(),
                    "line": index + 1,
                    "anchor": identifier.lower(),
                },
                "evidence": [],
            }
        )
    if active_fence is not None:
        raise ValueError(
            f"unclosed Markdown fence in requirement source: {SOURCE.relative_to(ROOT)}"
        )
    if not records:
        raise ValueError("candidate requirement source contains no stable requirement IDs")
    return records


def legacy_gaps(source_texts: dict[Path, str] | None = None) -> list[dict[str, object]]:
    gaps: list[dict[str, object]] = []
    for path in LEGACY_SOURCES:
        active_fence: str | None = None
        text = read_source(path) if source_texts is None else source_texts[path]
        for number, line in enumerate(text.splitlines(), 1):
            previous_fence = active_fence
            active_fence = _fence_after_line(active_fence, line)
            if previous_fence is not None or FENCE.match(line):
                continue
            if active_fence is not None:
                continue
            if "VCP-OP-" in line:
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
        if active_fence is not None:
            raise ValueError(
                f"unclosed Markdown fence in requirement source: {path.relative_to(ROOT)}"
            )
    return gaps


def build() -> dict[str, object]:
    sources = [SOURCE, *LEGACY_SOURCES]
    source_bytes = {
        path: read_regular_bytes(
            path,
            max_bytes=MAX_SOURCE_BYTES,
            root=ROOT,
            purpose="requirement source",
        )
        for path in sources
    }
    source_texts = {path: data.decode("utf-8") for path, data in source_bytes.items()}
    identified = requirements(source_texts[SOURCE])
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
                "sha256": sha256(source_bytes[path]),
            }
            for path in sources
        ],
        "requirements": identified,
        "coverage": {
            "identified_requirement_count": len(identified),
            "mapped_evidence_count": sum(bool(item["evidence"]) for item in identified),
            "legacy_normative_statements_without_stable_id": legacy_gaps(
                source_texts
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    except (OSError, UnicodeError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    try:
        if args.check:
            if not OUTPUT.is_file() or read_regular_bytes(
                OUTPUT,
                max_bytes=MAX_SOURCE_BYTES,
                root=ROOT,
                purpose="requirement registry",
            ).decode("utf-8") != rendered:
                print(
                    "Requirement registry is stale: registries/candidate-requirements.json"
                )
                return 1
            print("Candidate requirement registry verified")
            return 0
        atomic_write_text(OUTPUT, rendered)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("Candidate requirement registry generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
