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
AGENT_RUNTIME_SOURCE = ROOT / "veps/VEP-0006-agent-runtime-profile.md"
OUTPUT = ROOT / "registries/candidate-requirements.json"
REVIEW_DATE = "2026-08-31"
MAX_SOURCE_BYTES = 5 * 1024 * 1024
FENCE = re.compile(r"^\s{0,3}(?P<fence>`{3,}|~{3,})")
HEADING = re.compile(r"^### (VCP-OP-([A-Z]{3})-[0-9]{3}): (.+)$")
AGENT_RUNTIME_HEADING = re.compile(
    r"^### (VCP-ARP-([A-Z]{3})-[0-9]{3}): (.+)$"
)
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
AGENT_RUNTIME_AREA = {
    "STS": ("status", "profile implementation", "Preserve the exact portable state."),
    "NEG": ("negotiation", "negotiating peer", "Reject or revise the profile offer."),
    "RES": ("result", "profile operation", "Return a structured expected state."),
    "SIT": ("situation", "context compiler", "Withhold an incomplete or misleading projection."),
    "EVD": ("evidence", "evidence service", "Preserve provenance, conflict, and uncertainty."),
    "NRM": ("normative-context", "normative compiler", "Preserve source, hardness, and scope."),
    "CAP": ("capability", "capability adapter", "Mark the capability unavailable."),
    "AFF": ("affordance", "affordance service", "Invalidate or withhold the contextual option."),
    "RUN": ("run", "run service", "Reject the invalid run transition."),
    "PRF": ("proof", "proof service", "Keep completion unproven."),
    "ACT": ("action", "host authority service", "Deny execution authority or require reconciliation."),
    "CTL": ("control", "control service", "Reject the command or retain the safer stopped state."),
    "EVT": ("event", "event service", "Expose the gap and rebuild from durable authority."),
    "ACC": ("accretion", "memory authority", "Quarantine or reject the candidate or promotion."),
    "BUD": ("resource", "resource governor", "Stop before consuming recovery reserve."),
    "SEC": ("security", "profile implementation", "Fail closed without widening authority."),
}
AGENT_RUNTIME_EVIDENCE: dict[str, list[dict[str, str]]] = {
    "VCP-ARP-NEG-001": [
        {
            "kind": "positive",
            "reference": "VCP-SDK/conformance/agent-runtime/observe_contracts.json#VCP-ARP-NEG-001",
            "status": "mapped",
        }
    ],
    "VCP-ARP-NEG-002": [
        {
            "kind": "negative",
            "reference": "VCP-SDK/python/tests/agent/test_agent_runtime.py::test_missing_required_profile_blocks_without_implicit_downgrade",
            "status": "mapped",
        }
    ],
    "VCP-ARP-NEG-006": [
        {
            "kind": "positive",
            "reference": "VCP-SDK/conformance/agent-runtime/observe_contracts.json#VCP-ARP-NEG-006",
            "status": "mapped",
        }
    ],
    "VCP-ARP-RES-001": [
        {
            "kind": "positive",
            "reference": "VCP-SDK/python/tests/agent/test_agent_runtime.py::test_bootstrap_is_bounded_deterministic_and_no_network",
            "status": "mapped",
        }
    ],
    "VCP-ARP-RES-002": [
        {
            "kind": "negative",
            "reference": "VCP-SDK/python/tests/agent/test_agent_runtime.py::test_expected_absence_is_a_result_value_until_caller_chooses_exception",
            "status": "mapped",
        }
    ],
    "VCP-ARP-SIT-001": [
        {
            "kind": "positive",
            "reference": "VCP-SDK/python/tests/agent/test_agent_runtime.py::test_bootstrap_exposes_orientation_in_one_result",
            "status": "mapped",
        }
    ],
    "VCP-ARP-SIT-004": [
        {
            "kind": "positive",
            "reference": "VCP-SDK/python/tests/agent/test_agent_runtime.py::test_bootstrap_is_bounded_deterministic_and_no_network",
            "status": "mapped",
        }
    ],
    "VCP-ARP-CAP-001": [
        {
            "kind": "positive",
            "reference": "VCP-SDK/python/tests/agent/test_agent_runtime.py::test_affordance_joins_descriptor_situation_authority_and_cost",
            "status": "mapped",
        }
    ],
    "VCP-ARP-CAP-004": [
        {
            "kind": "negative",
            "reference": "VCP-SDK/python/tests/agent/test_agent_runtime.py::test_generic_support_and_contextual_unavailability_remain_distinct",
            "status": "mapped",
        }
    ],
    "VCP-ARP-AFF-001": [
        {
            "kind": "positive",
            "reference": "VCP-SDK/python/tests/agent/test_agent_runtime.py::test_affordance_joins_descriptor_situation_authority_and_cost",
            "status": "mapped",
        }
    ],
    "VCP-ARP-AFF-002": [
        {
            "kind": "negative",
            "reference": "VCP-SDK/python/tests/agent/test_agent_runtime.py::test_generic_support_and_contextual_unavailability_remain_distinct",
            "status": "mapped",
        }
    ],
    "VCP-ARP-AFF-003": [
        {
            "kind": "positive",
            "reference": "VCP-SDK/python/tests/agent/test_agent_runtime.py::test_effect_ceiling_is_applied_to_contextual_options",
            "status": "mapped",
        }
    ],
    "VCP-ARP-BUD-001": [
        {
            "kind": "positive",
            "reference": "VCP-SDK/python/tests/agent/test_agent_runtime.py::test_bootstrap_is_bounded_deterministic_and_no_network",
            "status": "mapped",
        }
    ],
    "VCP-ARP-BUD-003": [
        {
            "kind": "positive",
            "reference": "VCP-SDK/python/tests/agent/test_agent_runtime.py::test_affordance_joins_descriptor_situation_authority_and_cost",
            "status": "mapped",
        }
    ],
    "VCP-ARP-SEC-001": [
        {
            "kind": "negative",
            "reference": "VCP-SDK/conformance/agent-runtime/observe_contracts.json#VCP-ARP-CONTRACT-002",
            "status": "mapped",
        }
    ],
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


def agent_runtime_requirements(
    source_text: str | None = None,
) -> list[dict[str, object]]:
    """Extract stable Agent Runtime candidate requirements and mapped evidence."""

    text = read_source(AGENT_RUNTIME_SOURCE) if source_text is None else source_text
    lines = text.splitlines()
    records: list[dict[str, object]] = []
    identifiers: set[str] = set()
    active_fence: str | None = None
    for index, line in enumerate(lines):
        previous_fence = active_fence
        active_fence = _fence_after_line(active_fence, line)
        if previous_fence is not None or FENCE.match(line):
            continue
        match = AGENT_RUNTIME_HEADING.match(line)
        if match is None:
            continue
        identifier, area_code, title = match.groups()
        if identifier in identifiers:
            raise ValueError(f"duplicate candidate requirement identifier: {identifier}")
        identifiers.add(identifier)
        if area_code not in AGENT_RUNTIME_AREA:
            raise ValueError(
                f"candidate requirement {identifier} has unsupported area {area_code}"
            )
        area, actor, failure = AGENT_RUNTIME_AREA[area_code]
        requirement_text = first_paragraph(lines, index + 1)
        if not requirement_text:
            raise ValueError(f"candidate requirement {identifier} has no requirement text")
        evidence = AGENT_RUNTIME_EVIDENCE.get(identifier, [])
        records.append(
            {
                "id": identifier,
                "title": title,
                "area": area,
                "actor": actor,
                "testability": "machine" if evidence else "not-yet-mapped",
                "preconditions": [
                    "The selected Agent Runtime candidate profile requires this behavior."
                ],
                "requirement_text": requirement_text,
                "failure_semantics": failure,
                "source": {
                    "path": AGENT_RUNTIME_SOURCE.relative_to(ROOT).as_posix(),
                    "line": index + 1,
                    "anchor": identifier.lower(),
                },
                "evidence": evidence,
            }
        )
    if active_fence is not None:
        raise ValueError(
            "unclosed Markdown fence in requirement source: "
            f"{AGENT_RUNTIME_SOURCE.relative_to(ROOT)}"
        )
    if not records:
        raise ValueError("Agent Runtime candidate contains no stable requirement IDs")
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
    sources = [SOURCE, AGENT_RUNTIME_SOURCE, *LEGACY_SOURCES]
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
    identified = requirements(source_texts[SOURCE]) + agent_runtime_requirements(
        source_texts[AGENT_RUNTIME_SOURCE]
    )
    return {
        "schema": "vcp-requirement-registry/1",
        "generated_by": "scripts/generate_requirement_registry.py",
        "as_of": REVIEW_DATE,
        "claim_boundary": (
            "Stable IDs cover the candidate operations and Agent Runtime profiles. "
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
