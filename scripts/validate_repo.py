#!/usr/bin/env python3
"""Deterministic validation for the VCP specification repository."""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import subprocess
import sys
import unicodedata
import zipfile
from collections.abc import Mapping
from datetime import UTC, date, datetime
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml
from jsonschema.validators import validator_for
from jsonschema_formats import strict_format_checker
from protocol_contracts import validate_fixture_semantics
from validation_utils import read_regular_bytes, read_regular_text

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOTS = (
    ROOT / "schemas",
    ROOT / "specs" / "extensions",
    ROOT / "governance",
    ROOT / "status",
)
PUBLIC_MARKDOWN = {
    ROOT / "README.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "GOVERNANCE.md",
    ROOT / "LICENSING_STATUS.md",
    ROOT / "SECURITY.md",
    ROOT / "COMPATIBILITY.md",
    ROOT / "ARTIFACTS.md",
    ROOT / "ROADMAP.md",
    ROOT / "docs" / "README.md",
    ROOT / "veps" / "README.md",
}
CONTROLLED_POLICY_MARKDOWN = PUBLIC_MARKDOWN | {
    ROOT / "DEPENDENCY_POLICY.md",
    ROOT / "RELEASE_CHECKLIST.md",
    ROOT / "REPOSITORY_CONTROLS.md",
}
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
FENCE_RE = re.compile(r"^\s{0,3}(?P<fence>`{3,}|~{3,})")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(?P<title>.*?)\s*#*\s*$")
EXPLICIT_ANCHOR_RE = re.compile(
    r"<(?:a|[A-Za-z][A-Za-z0-9-]*)\s+[^>]*(?:id|name)=[\"']([^\"']+)[\"'][^>]*>",
    re.IGNORECASE,
)
INVALID_PERCENT_ESCAPE_RE = re.compile(r"%(?![0-9A-Fa-f]{2})")
DOCUMENT_CONTROL_RE = re.compile(
    r"<!--\s*vcp-document-control\s*\n(?P<body>.*?)\n-->", re.DOTALL
)
DOCUMENT_CONTROL_FIELDS = {
    "status",
    "normative-authority",
    "protocol-version",
    "last-reviewed",
    "owner",
    "evidence-boundary",
}
MAX_DOCUMENT_REVIEW_AGE_DAYS = 366
MAX_JSON_BYTES = 10 * 1024 * 1024
MAX_YAML_BYTES = 2 * 1024 * 1024
MAX_MARKDOWN_BYTES = 5 * 1024 * 1024
MAX_REPOSITORY_FILES = 100_000
MAX_DOCX_MEMBERS = 10_000
MAX_DOCX_MEMBER_BYTES = 50 * 1024 * 1024
MAX_DOCX_UNCOMPRESSED_BYTES = 250 * 1024 * 1024
MAX_DOCX_COMPRESSION_RATIO = 1_000
MAX_SCHEMA_NODES = 200_000
MAX_DATA_NODES = 200_000
MAX_DATA_DEPTH = 128
MAX_YAML_ALIASES = 1_000
EXTENSION_ROW_RE = re.compile(
    r"^\|\s*(?:\[(VCP-X-[A-Za-z]+)\]\([^)]+\)|(VCP-X-[A-Za-z]+))"
    r"\s*\|\s*([A-Za-z]+)\s*\|",
    re.MULTILINE,
)
EXTENSION_STATUSES = {"draft", "stable", "experimental", "deprecated"}
CSM1_PROSE_FILES = (
    "specs/VCP_SEMANTICS_v2.0.md",
    "docs/semantics/VCP_SEMANTICS_CSM1.md",
    "docs/content/CSM1_GRAMMAR_SPECIFICATION.md",
    "specs/VCP_ECONOMIC_GOVERNANCE_v2.0.md",
)
NAMESPACE_BEFORE_SCOPE_RE = re.compile(
    r"\b[NZGAMDC][0-5]:[A-Z]{1,8}(?=\+(?:\$?[A-Z]))"
)
REQUIRED_RELEASE_FILES = (
    ".github/workflows/release-candidate.yml",
    ".github/workflows/codeql.yml",
    ".github/workflows/dependency-review.yml",
    ".github/repository-policy.json",
    "RELEASE_CHECKLIST.md",
    "REPOSITORY_CONTROLS.md",
    "governance/authority.json",
    "governance/authority.schema.json",
    "governance/PROPOSED_TSC_CHARTER.md",
    "governance/PROPOSED_IP_AND_MARKS_POLICY.md",
    "governance/decisions/DECISION_TEMPLATE.md",
    "governance/meetings/MINUTES_TEMPLATE.md",
    "governance/security/SECURITY_DECISION_TEMPLATE.md",
    "LICENSING_STATUS.md",
    "DEPENDENCY_POLICY.md",
    "reviews/GOVERNANCE_EDITORIAL_INDEPENDENT_REVIEW.md",
    "ROADMAP.md",
    "docs/ERRATA_AND_DEPRECATION.md",
    "docs/EXAMPLE_CLASSIFICATION.md",
    "docs/TERMINOLOGY.md",
    "docs/RESIDUAL_RISKS.md",
    "docs/THREAT_MODEL.md",
    "docs/SECURITY_RESPONSE.md",
    "docs/SUPPORT_AND_SUNSET.md",
    "docs/ISSUE_AND_DECISION_ROUTING.md",
    "docs/REQUIREMENT_TRACEABILITY.md",
    "status/residual-risks.json",
    "status/residual-risks.schema.json",
    "registries/verification-status-codes.json",
    "registries/errata.json",
    "registries/provisional-identifiers.json",
    "registries/candidate-requirements.json",
    "schemas/vcp-verification-status-registry.schema.json",
    "schemas/vcp-errata-registry.schema.json",
    "schemas/vcp-provisional-identifiers.schema.json",
    "schemas/vcp-requirement-registry.schema.json",
    "specs/core/status-code-registry.md",
    "scripts/generate_document_inventory.py",
    "scripts/generate_requirement_registry.py",
    "status/document-inventory.json",
    "status/document-inventory.schema.json",
)


class Problems:
    def __init__(self) -> None:
        self.items: list[str] = []

    def add(self, message: str) -> None:
        self.items.append(message)

    def finish(self) -> int:
        if self.items:
            for item in sorted(self.items):
                print(f"ERROR: {item}", file=sys.stderr)
            print(
                f"Validation failed with {len(self.items)} problem(s).", file=sys.stderr
            )
            return 1
        print("VCP-Spec validation passed.")
        return 0


class DuplicateKeyError(ValueError):
    """Raised when an object contains an ambiguous duplicate JSON key."""


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader with duplicate-key and construction-work bounds."""

    def __init__(self, stream: object) -> None:
        super().__init__(stream)
        self._vcp_nodes = 0
        self._vcp_aliases = 0
        self._vcp_depth = 0

    def compose_node(self, parent: object, index: object) -> yaml.Node:
        self._vcp_nodes += 1
        if self._vcp_nodes > MAX_DATA_NODES:
            raise yaml.YAMLError(
                f"document exceeds the {MAX_DATA_NODES}-node construction limit"
            )
        if self.check_event(yaml.AliasEvent):
            self._vcp_aliases += 1
            if self._vcp_aliases > MAX_YAML_ALIASES:
                raise yaml.YAMLError(
                    f"document exceeds the {MAX_YAML_ALIASES}-alias limit"
                )
        self._vcp_depth += 1
        if self._vcp_depth > MAX_DATA_DEPTH:
            self._vcp_depth -= 1
            raise yaml.YAMLError(
                f"document exceeds the {MAX_DATA_DEPTH}-level construction limit"
            )
        try:
            return super().compose_node(parent, index)
        finally:
            self._vcp_depth -= 1


# GitHub Actions uses YAML 1.2 semantics, where `on` is a string rather than
# the YAML 1.1 boolean accepted by PyYAML's default resolver. Retain true/false
# booleans while preventing valid workflow keys from changing type.
UniqueKeyLoader.yaml_implicit_resolvers = {
    initial: [
        (tag, pattern)
        for tag, pattern in resolvers
        if tag != "tag:yaml.org,2002:bool"
    ]
    for initial, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}
UniqueKeyLoader.add_implicit_resolver(
    "tag:yaml.org,2002:bool",
    re.compile(r"^(?:true|false)$", re.IGNORECASE),
    list("tTfF"),
)


def _construct_unique_mapping(
    loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[object, object]:
    loader.flatten_mapping(node)
    mapping: dict[object, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "found an unhashable mapping key",
                key_node.start_mark,
            ) from exc
        if duplicate:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def repository_source_files(*suffixes: str) -> list[Path]:
    """Discover source files without descending into generated dependency trees."""
    wanted = set(suffixes)
    files: list[Path] = []
    entries = 0
    ignored = {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "__pycache__",
        "node_modules",
        "target",
    }

    def fail(error: OSError) -> None:
        raise error

    for directory, dirnames, filenames in os.walk(
        ROOT, topdown=True, onerror=fail, followlinks=False
    ):
        dirnames[:] = sorted(
            name
            for name in dirnames
            if name not in ignored and (not name.startswith(".") or name == ".github")
        )
        entries += len(dirnames) + len(filenames)
        if entries > MAX_REPOSITORY_FILES:
            raise ValueError(
                f"repository source inventory exceeds {MAX_REPOSITORY_FILES} entries"
            )
        base = Path(directory)
        files.extend(
            base / name
            for name in filenames
            if not wanted or Path(name).suffix.lower() in wanted
        )
    return sorted(files)


def json_files() -> list[Path]:
    return [
        path
        for path in repository_source_files(".json")
        if any(path.is_relative_to(root) for root in SCHEMA_ROOTS)
    ]


def schema_files() -> list[Path]:
    return [
        path
        for path in json_files()
        if "examples" not in path.parts
        and (path.name.endswith(".schema.json") or path.name == "schema.json")
    ]


def _unique_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def _reject_non_finite_json(value: str) -> object:
    raise ValueError(f"non-finite JSON number {value!r} is not permitted")


def validate_structure_bounds(value: object) -> None:
    """Reject pathological nesting, node counts, cycles, and non-string map keys."""
    stack: list[tuple[object, int, bool]] = [(value, 1, False)]
    active_containers: set[int] = set()
    visited_containers: set[int] = set()
    node_count = 0
    while stack:
        current, depth, exiting = stack.pop()
        if exiting:
            active_containers.remove(id(current))
            continue
        node_count += 1
        if node_count > MAX_DATA_NODES:
            raise ValueError(f"document exceeds the {MAX_DATA_NODES}-node limit")
        if depth > MAX_DATA_DEPTH:
            raise ValueError(f"document exceeds the {MAX_DATA_DEPTH}-level depth limit")
        if not isinstance(current, (dict, list)):
            continue
        identity = id(current)
        if identity in active_containers:
            raise ValueError("document contains an alias cycle")
        if identity in visited_containers:
            continue
        active_containers.add(identity)
        visited_containers.add(identity)
        stack.append((current, depth, True))
        if isinstance(current, dict):
            if any(not isinstance(key, str) for key in current):
                raise ValueError("document object keys must be strings")
            stack.extend(
                (nested, depth + 1, False) for nested in current.values()
            )
        else:
            stack.extend((nested, depth + 1, False) for nested in current)


def load_json(path: Path, problems: Problems) -> object | None:
    try:
        loaded = json.loads(
            read_regular_text(
                path,
                max_bytes=MAX_JSON_BYTES,
                root=ROOT,
                purpose="JSON input",
            ),
            object_pairs_hook=_unique_json_object,
            parse_constant=_reject_non_finite_json,
        )
        validate_structure_bounds(loaded)
        return loaded
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        DuplicateKeyError,
        RecursionError,
        ValueError,
    ) as exc:
        problems.add(f"{relative(path)} is not valid bounded UTF-8 JSON: {exc}")
        return None


def schema_name(path: Path) -> str:
    """Return a stable fixture name without collapsing extension schema.json files."""
    if path.name == "schema.json" and path.parent.name.startswith("VCP-X-"):
        return path.parent.name
    return path.stem.removesuffix(".schema")


def _walk_schema_references(value: object) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    stack: list[tuple[str, object]] = [("$", value)]
    visited = 0
    while stack:
        location, current = stack.pop()
        visited += 1
        if visited > MAX_SCHEMA_NODES:
            raise ValueError(
                f"schema exceeds the {MAX_SCHEMA_NODES}-node traversal limit"
            )
        if isinstance(current, dict):
            for keyword in ("$ref", "$dynamicRef"):
                reference = current.get(keyword)
                if isinstance(reference, str):
                    found.append((f"{location}/{keyword}", reference))
            stack.extend(
                (f"{location}/{key}", nested)
                for key, nested in reversed(list(current.items()))
            )
        elif isinstance(current, list):
            stack.extend(
                (f"{location}/{index}", nested)
                for index, nested in reversed(list(enumerate(current)))
            )
    return found


def _resolve_local_schema_reference(schema: dict[str, object], reference: str) -> bool:
    if not reference.startswith("#"):
        return False
    fragment = unquote(reference[1:])
    if not fragment:
        return True
    if not fragment.startswith("/"):
        anchors: set[str] = set()
        stack: list[object] = [schema]
        visited = 0
        while stack:
            current = stack.pop()
            visited += 1
            if visited > MAX_SCHEMA_NODES:
                raise ValueError(
                    f"schema exceeds the {MAX_SCHEMA_NODES}-node traversal limit"
                )
            if isinstance(current, dict):
                anchors.update(
                    anchor
                    for keyword in ("$anchor", "$dynamicAnchor")
                    if isinstance((anchor := current.get(keyword)), str)
                )
                stack.extend(current.values())
            elif isinstance(current, list):
                stack.extend(current)
        return fragment in anchors
    current: object = schema
    for raw_token in fragment[1:].split("/"):
        if re.search(r"~(?![01])", raw_token):
            return False
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict) and token in current:
            current = current[token]
        elif isinstance(current, list) and token.isdecimal():
            index = int(token)
            if index >= len(current):
                return False
            current = current[index]
        else:
            return False
    return True


def validate_schema_references(
    path: Path, schema: dict[str, object], problems: Problems
) -> None:
    try:
        references = _walk_schema_references(schema)
    except ValueError as exc:
        problems.add(f"{relative(path)} cannot be traversed safely: {exc}")
        return
    for location, reference in references:
        if not reference.startswith("#"):
            problems.add(
                f"{relative(path)} {location} uses non-local reference {reference!r}; "
                "candidate validation must be deterministic and offline"
            )
        else:
            try:
                resolved = _resolve_local_schema_reference(schema, reference)
            except ValueError as exc:
                problems.add(f"{relative(path)} cannot resolve {reference!r}: {exc}")
                continue
            if not resolved:
                problems.add(
                    f"{relative(path)} {location} does not resolve local reference {reference!r}"
                )


def _schema_nodes(value: object) -> list[tuple[str, dict[str, object]]]:
    nodes: list[tuple[str, dict[str, object]]] = []
    stack: list[tuple[str, object]] = [("$", value)]
    visited = 0
    while stack:
        location, current = stack.pop()
        visited += 1
        if visited > MAX_SCHEMA_NODES:
            raise ValueError(
                f"schema exceeds the {MAX_SCHEMA_NODES}-node traversal limit"
            )
        if isinstance(current, dict):
            nodes.append((location, current))
            stack.extend(
                (f"{location}/{key}", nested)
                for key, nested in reversed(list(current.items()))
                if key != "examples"
            )
        elif isinstance(current, list):
            stack.extend(
                (f"{location}/{index}", nested)
                for index, nested in reversed(list(enumerate(current)))
            )
    return nodes


def validate_embedded_schema_examples(
    path: Path, schema: dict[str, object], problems: Problems
) -> None:
    """Validate every annotation example against the subschema that contains it."""
    try:
        nodes = _schema_nodes(schema)
    except ValueError as exc:
        problems.add(f"{relative(path)} examples cannot be traversed safely: {exc}")
        return
    for location, node in nodes:
        examples = node.get("examples")
        if not isinstance(examples, list):
            continue
        wrapper: dict[str, object] = {
            "$schema": schema.get(
                "$schema", "https://json-schema.org/draft/2020-12/schema"
            ),
            "allOf": [node],
        }
        for definitions_keyword in ("$defs", "definitions"):
            if definitions_keyword in schema:
                wrapper[definitions_keyword] = schema[definitions_keyword]
        validator_class = validator_for(wrapper)
        validator = validator_class(wrapper, format_checker=strict_format_checker())
        for index, example in enumerate(examples, 1):
            try:
                errors = list(validator.iter_errors(example))
            except Exception as exc:  # noqa: BLE001
                problems.add(
                    f"{relative(path)} {location}/examples/{index - 1} "
                    f"could not be validated: {exc}"
                )
                continue
            if errors:
                problems.add(
                    f"{relative(path)} {location}/examples/{index - 1} is invalid: "
                    f"{errors[0].message}"
                )


def validate_schemas(problems: Problems) -> dict[str, tuple[dict[str, object], object]]:
    schemas: dict[str, tuple[dict[str, object], object]] = {}
    ids: dict[str, Path] = {}
    names: dict[str, Path] = {}
    try:
        paths = schema_files()
    except (OSError, ValueError) as exc:
        problems.add(f"JSON schema source inventory failed: {exc}")
        return schemas
    for path in paths:
        loaded = load_json(path, problems)
        if not isinstance(loaded, dict):
            if loaded is not None:
                problems.add(f"{relative(path)} must contain a JSON object")
            continue
        try:
            validator_class = validator_for(loaded)
            validator_class.check_schema(loaded)
            validator = validator_class(loaded, format_checker=strict_format_checker())
        except Exception as exc:  # noqa: BLE001  # validator classes expose distinct errors
            problems.add(f"{relative(path)} is not a valid declared schema: {exc}")
            continue
        validate_schema_references(path, loaded, problems)
        schema_id = loaded.get("$id")
        if isinstance(schema_id, str):
            if schema_id in ids:
                problems.add(
                    f"duplicate schema $id {schema_id!r}: {relative(ids[schema_id])} and {relative(path)}"
                )
            ids[schema_id] = path
        name = schema_name(path)
        if name in names:
            problems.add(
                f"duplicate schema fixture name {name!r}: "
                f"{relative(names[name])} and {relative(path)}"
            )
        names[name] = path
        schemas[name] = (loaded, validator)
        validate_embedded_schema_examples(path, loaded, problems)
    return schemas


def validate_fixtures(
    schemas: dict[str, tuple[dict[str, object], object]], problems: Problems
) -> None:
    examples = ROOT / "schemas" / "examples"
    if not examples.is_dir():
        problems.add("schemas/examples is missing")
        return
    try:
        fixtures = [path for path in json_files() if path.is_relative_to(examples)]
    except (OSError, ValueError) as exc:
        problems.add(f"JSON fixture source inventory failed: {exc}")
        return
    if not fixtures:
        problems.add("schemas/examples contains no JSON fixtures")
        return
    seen: dict[str, set[str]] = {}
    for path in fixtures:
        fixture = load_json(path, problems)
        if fixture is None:
            continue
        name = path.name
        match = re.match(r"(.+?)\.(valid|invalid)(?:[-.].*)?\.json$", name)
        if not match:
            problems.add(
                f"{relative(path)} must use <schema>.valid*.json or <schema>.invalid*.json"
            )
            continue
        schema_name, expectation = match.groups()
        if schema_name not in schemas:
            problems.add(f"{relative(path)} names unknown schema {schema_name!r}")
            continue
        seen.setdefault(schema_name, set()).add(expectation)
        validator = schemas[schema_name][1]
        try:
            errors = list(validator.iter_errors(fixture))
        except Exception as exc:  # noqa: BLE001
            problems.add(
                f"{relative(path)} could not be validated deterministically: {exc}"
            )
            continue
        semantic_errors = validate_fixture_semantics(schema_name, fixture)
        if expectation == "valid" and errors:
            problems.add(f"{relative(path)} should be valid: {errors[0].message}")
        if expectation == "valid" and semantic_errors:
            problems.add(
                f"{relative(path)} is semantically inconsistent: {semantic_errors[0]}"
            )
        if expectation == "invalid" and not errors and not semantic_errors:
            problems.add(f"{relative(path)} should be rejected but was accepted")
    for required in (
        "vcp-adaptation-context",
        "vcp-capability-handshake",
        "vcp-manifest-v1",
        "vcp-messaging-v1.2",
        "vcp-semantics-csm1",
    ):
        if seen.get(required) != {"valid", "invalid"}:
            problems.add(
                f"{required} requires at least one valid and one invalid fixture"
            )


HANDSHAKE_MESSAGE_TYPES = frozenset({"vcp-hello", "vcp-ack", "vcp-error"})
JSON_FENCE_RE = re.compile(r"^\s{0,3}```json\s*$")


def _fenced_json_blocks(text: str) -> list[tuple[int, str]]:
    """Return (line_number, body) for every ```json fenced block in Markdown text."""
    blocks: list[tuple[int, str]] = []
    body: list[str] = []
    start: int | None = None
    for number, line in enumerate(text.splitlines(), 1):
        if start is None:
            if JSON_FENCE_RE.match(line):
                start = number
                body = []
        elif FENCE_RE.match(line) and not line[FENCE_RE.match(line).end() :].strip():
            blocks.append((start, "\n".join(body)))
            start = None
        else:
            body.append(line)
    return blocks


def _handshake_messages(value: object) -> list[object]:
    """Return every nested object whose `type` is a capability-handshake message type."""
    found: list[object] = []
    if isinstance(value, dict):
        if value.get("type") in HANDSHAKE_MESSAGE_TYPES:
            found.append(value)
        else:
            for child in value.values():
                found.extend(_handshake_messages(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(_handshake_messages(child))
    return found


def validate_spec_json_examples(
    schemas: dict[str, tuple[dict[str, object], object]], problems: Problems
) -> None:
    """Validate handshake and personal-state examples embedded in specs/**/*.md."""
    targets = {
        "handshake": schemas.get("vcp-capability-handshake"),
        "personal": schemas.get("VCP-X-Personal"),
    }
    if any(entry is None for entry in targets.values()):
        problems.add("spec example validation requires the handshake and Personal schemas")
        return
    try:
        paths = [
            path
            for path in repository_source_files(".md")
            if path.is_relative_to(ROOT / "specs")
        ]
    except (OSError, ValueError) as exc:
        problems.add(f"spec example source inventory failed: {exc}")
        return
    for path in paths:
        text = _read_bounded_markdown(path, problems)
        if text is None:
            continue
        for line, body in _fenced_json_blocks(text):
            try:
                value = json.loads(body, object_pairs_hook=_unique_json_object)
            except ValueError:
                continue  # annotated or elided examples are not machine-checked
            checks: list[tuple[str, object]] = [
                ("handshake", message) for message in _handshake_messages(value)
            ]
            if isinstance(value, dict) and isinstance(value.get("personal"), dict):
                checks.append(("personal", value))
            for kind, instance in checks:
                validator = targets[kind][1]
                errors = list(validator.iter_errors(instance))
                if errors:
                    location = "/".join(str(part) for part in errors[0].absolute_path)
                    problems.add(
                        f"{relative(path)}:{line} {kind} example is invalid"
                        f"{' at ' + location if location else ''}: {errors[0].message}"
                    )


def validate_status_registry(
    schemas: dict[str, tuple[dict[str, object], object]], problems: Problems
) -> None:
    path = ROOT / "registries" / "verification-status-codes.json"
    registry = load_json(path, problems)
    schema_entry = schemas.get("vcp-verification-status-registry")
    if registry is None or schema_entry is None:
        return
    errors = list(schema_entry[1].iter_errors(registry))
    if errors:
        problems.add(
            f"{relative(path)} does not satisfy its schema: {errors[0].message}"
        )
        return
    assert isinstance(registry, dict)
    codes = registry.get("codes", [])
    assert isinstance(codes, list)
    if not codes:
        problems.add(f"{relative(path)} must define at least one status code")
        return
    for field in ("code", "symbol", "wire_label"):
        values = [entry[field] for entry in codes if isinstance(entry, dict)]
        if len(values) != len(set(values)):
            problems.add(f"{relative(path)} repeats {field} values")
    numeric_codes = sorted(entry["code"] for entry in codes if isinstance(entry, dict))
    if numeric_codes != list(range(numeric_codes[-1] + 1)):
        problems.add(f"{relative(path)} numeric codes must be contiguous from zero")


def strip_fenced_code(text: str) -> str:
    output: list[str] = []
    active_fence: str | None = None
    for line in text.splitlines():
        match = FENCE_RE.match(line)
        if match:
            marker = match.group("fence")
            if active_fence is None:
                active_fence = marker
                continue
            suffix = line[match.end() :]
            if (
                marker[0] == active_fence[0]
                and len(marker) >= len(active_fence)
                and not suffix.strip()
            ):
                active_fence = None
                continue
        if active_fence is None:
            output.append(line)
    return "\n".join(output)


def has_unclosed_fence(text: str) -> bool:
    active_fence: str | None = None
    for line in text.splitlines():
        match = FENCE_RE.match(line)
        if match is None:
            continue
        marker = match.group("fence")
        if active_fence is None:
            active_fence = marker
        elif (
            marker[0] == active_fence[0]
            and len(marker) >= len(active_fence)
            and not line[match.end() :].strip()
        ):
            active_fence = None
    return active_fence is not None


def link_target(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("<") and ">" in raw:
        return raw[1 : raw.index(">")]
    return raw.split(maxsplit=1)[0]


def github_heading_slug(title: str) -> str:
    """Approximate GitHub's stable heading slug rules for local link validation."""
    title = re.sub(r"<[^>]+>", "", title)
    title = re.sub(r"!?\[([^\]]*)\]\([^)]+\)", r"\1", title)
    title = title.replace("`", "").strip().casefold()
    cleaned = "".join(
        character
        for character in title
        if character in {" ", "-", "_"}
        or unicodedata.category(character)[0] in {"L", "M", "N"}
    )
    return re.sub(r"\s+", "-", cleaned)


def markdown_anchors(text: str) -> set[str]:
    anchors = set(EXPLICIT_ANCHOR_RE.findall(text))
    counts: dict[str, int] = {}
    for line in strip_fenced_code(text).splitlines():
        match = HEADING_RE.match(line)
        if match is None:
            continue
        base = github_heading_slug(match.group("title"))
        count = counts.get(base, 0)
        counts[base] = count + 1
        anchors.add(base if count == 0 else f"{base}-{count}")
    return anchors


def _read_bounded_markdown(path: Path, problems: Problems) -> str | None:
    try:
        text = read_regular_text(
            path,
            max_bytes=MAX_MARKDOWN_BYTES,
            root=ROOT,
            purpose="Markdown input",
        )
        invalid = next(
            (
                (index, character)
                for index, character in enumerate(text)
                if unicodedata.category(character) == "Cc"
                and character not in "\n\r\t"
            ),
            None,
        )
        if invalid is not None:
            index, character = invalid
            problems.add(
                f"{relative(path)} contains prohibited control character "
                f"U+{ord(character):04X} at offset {index}"
            )
            return None
        return text
    except (OSError, UnicodeError, ValueError) as exc:
        problems.add(f"{relative(path)} is not readable UTF-8: {exc}")
        return None


def validate_markdown(problems: Problems) -> None:
    anchor_cache: dict[Path, set[str]] = {}
    try:
        paths = repository_source_files(".md")
    except (OSError, ValueError) as exc:
        problems.add(f"Markdown source inventory failed: {exc}")
        return
    for path in paths:
        text = _read_bounded_markdown(path, problems)
        if text is None:
            continue
        if has_unclosed_fence(text):
            problems.add(f"{relative(path)} has an unclosed fenced code block")
        if path in PUBLIC_MARKDOWN:
            lines = text.splitlines()
            if not any(line.startswith("# ") for line in lines[:20]):
                problems.add(f"{relative(path)} needs one H1 in its first 20 lines")
            if any(line.endswith((" ", "\t")) for line in lines):
                problems.add(f"{relative(path)} contains trailing whitespace")
        searchable = strip_fenced_code(text)
        for raw in LINK_RE.findall(searchable):
            target = link_target(raw)
            if INVALID_PERCENT_ESCAPE_RE.search(target):
                problems.add(f"{relative(path)} has malformed percent escape: {target}")
                continue
            try:
                parts = urlsplit(target)
            except ValueError as exc:
                problems.add(f"{relative(path)} has malformed link {target!r}: {exc}")
                continue
            if parts.scheme or target.startswith("//"):
                continue
            clean = unquote(parts.path)
            destination = (
                ROOT / clean.lstrip("/")
                if clean.startswith("/")
                else path.parent / clean
                if clean
                else path
            )
            try:
                destination = destination.resolve(strict=False)
            except (OSError, RuntimeError, ValueError) as exc:
                problems.add(
                    f"{relative(path)} cannot resolve local link {target!r}: {exc}"
                )
                continue
            try:
                destination.relative_to(ROOT)
            except ValueError:
                problems.add(f"{relative(path)} link escapes repository: {target}")
                continue
            if not destination.exists():
                problems.add(f"{relative(path)} has broken local link: {target}")
                continue
            fragment = unquote(parts.fragment)
            if not fragment:
                continue
            anchor_document = destination
            if anchor_document.is_dir():
                anchor_document = anchor_document / "README.md"
            if anchor_document.suffix.lower() != ".md" or not anchor_document.is_file():
                continue
            anchors = anchor_cache.get(anchor_document)
            if anchors is None:
                target_text = _read_bounded_markdown(anchor_document, problems)
                if target_text is None:
                    continue
                anchors = markdown_anchors(target_text)
                anchor_cache[anchor_document] = anchors
            if fragment not in anchors:
                problems.add(f"{relative(path)} has broken local anchor: {target}")


def validate_yaml(problems: Problems) -> None:
    try:
        paths = repository_source_files(".yml", ".yaml")
    except (OSError, ValueError) as exc:
        problems.add(f"YAML source inventory failed: {exc}")
        return
    for path in paths:
        try:
            loaded = yaml.load(
                read_regular_text(
                    path,
                    max_bytes=MAX_YAML_BYTES,
                    root=ROOT,
                    purpose="YAML input",
                ),
                Loader=UniqueKeyLoader,
            )
            validate_structure_bounds(loaded)
        except (OSError, UnicodeError, ValueError, RecursionError, yaml.YAMLError) as exc:
            problems.add(f"{relative(path)} is not valid YAML: {exc}")


def validate_docx(problems: Problems) -> None:
    try:
        paths = repository_source_files(".docx")
    except (OSError, ValueError) as exc:
        problems.add(f"DOCX source inventory failed: {exc}")
        return
    for path in paths:
        try:
            package = read_regular_bytes(
                path,
                max_bytes=MAX_DOCX_UNCOMPRESSED_BYTES,
                root=ROOT,
                purpose="DOCX package",
            )
            with zipfile.ZipFile(io.BytesIO(package)) as archive:
                members = archive.infolist()
                if len(members) > MAX_DOCX_MEMBERS:
                    problems.add(
                        f"{relative(path)} has {len(members)} members; "
                        f"maximum is {MAX_DOCX_MEMBERS}"
                    )
                    continue
                names = [member.filename for member in members]
                if len(names) != len(set(names)):
                    problems.add(f"{relative(path)} contains duplicate ZIP member names")
                    continue
                total_size = sum(member.file_size for member in members)
                if total_size > MAX_DOCX_UNCOMPRESSED_BYTES:
                    problems.add(
                        f"{relative(path)} expands to {total_size} bytes; "
                        f"maximum is {MAX_DOCX_UNCOMPRESSED_BYTES}"
                    )
                    continue
                unsafe_member = next(
                    (
                        member
                        for member in members
                        if member.file_size > MAX_DOCX_MEMBER_BYTES
                        or (
                            member.file_size > 0
                            and member.file_size
                            > max(member.compress_size, 1) * MAX_DOCX_COMPRESSION_RATIO
                        )
                    ),
                    None,
                )
                if unsafe_member is not None:
                    problems.add(
                        f"{relative(path)} has unsafe member size or compression ratio: "
                        f"{unsafe_member.filename}"
                    )
                    continue
                bad_member = archive.testzip()
                if bad_member:
                    problems.add(f"{relative(path)} has corrupt member {bad_member}")
                if "word/document.xml" not in archive.namelist():
                    problems.add(f"{relative(path)} is missing word/document.xml")
        except (OSError, RuntimeError, ValueError, zipfile.BadZipFile) as exc:
            problems.add(f"{relative(path)} is not a valid DOCX package: {exc}")


def validate_document_control(problems: Problems) -> None:
    """Require complete, current control metadata on every active docs page."""
    today = datetime.now(UTC).date()
    try:
        markdown = repository_source_files(".md")
    except (OSError, ValueError) as exc:
        problems.add(f"document-control source inventory failed: {exc}")
        return
    controlled_paths = {
        path for path in markdown if path.is_relative_to(ROOT / "docs")
    } | CONTROLLED_POLICY_MARKDOWN
    for path in sorted(controlled_paths):
        text = _read_bounded_markdown(path, problems)
        if text is None:
            continue
        matches = list(DOCUMENT_CONTROL_RE.finditer(text))
        if not matches:
            problems.add(f"{relative(path)} has no vcp-document-control header")
            continue
        if len(matches) > 1:
            problems.add(f"{relative(path)} has multiple vcp-document-control headers")
            continue
        match = matches[0]
        fields: dict[str, str] = {}
        for raw_line in match.group("body").splitlines():
            if not raw_line.strip():
                continue
            key, separator, value = raw_line.partition(":")
            key = key.strip()
            value = value.strip()
            if not separator or not key or not value:
                problems.add(
                    f"{relative(path)} has malformed document-control line: "
                    f"{raw_line.strip()!r}"
                )
                continue
            if key in fields:
                problems.add(f"{relative(path)} repeats document-control field {key!r}")
            fields[key] = value
        missing = sorted(DOCUMENT_CONTROL_FIELDS - fields.keys())
        unexpected = sorted(fields.keys() - DOCUMENT_CONTROL_FIELDS)
        if missing:
            problems.add(
                f"{relative(path)} is missing document-control fields: {missing}"
            )
        if unexpected:
            problems.add(
                f"{relative(path)} has unknown document-control fields: {unexpected}"
            )
        reviewed_value = fields.get("last-reviewed")
        if reviewed_value is None:
            continue
        reviewed_match = re.fullmatch(
            r"(?P<date>\d{4}-\d{2}-\d{2})(?:\s+\S.*)?", reviewed_value
        )
        if reviewed_match is None:
            problems.add(
                f"{relative(path)} has invalid last-reviewed date: {reviewed_value!r}"
            )
            continue
        try:
            reviewed = date.fromisoformat(reviewed_match.group("date"))
        except ValueError:
            problems.add(
                f"{relative(path)} has invalid last-reviewed date: {reviewed_value!r}"
            )
            continue
        age = (today - reviewed).days
        if age < 0:
            problems.add(
                f"{relative(path)} last-reviewed date is in the future: {reviewed}"
            )
        elif age > MAX_DOCUMENT_REVIEW_AGE_DAYS:
            problems.add(
                f"{relative(path)} review is stale at {age} days; "
                f"maximum is {MAX_DOCUMENT_REVIEW_AGE_DAYS}"
            )


def declared_extension_status(path: Path, problems: Problems) -> str | None:
    text = _read_bounded_markdown(path, problems)
    if text is None:
        return None
    match = re.search(r"^\*\*Status\*\*:\s*([A-Za-z]+)", text, re.MULTILINE)
    if match is None:
        match = re.search(r"^\|\s*Status\s*\|\s*([A-Za-z]+)\s*\|", text, re.MULTILINE)
    if match is None:
        problems.add(f"{relative(path)} has no machine-readable extension status")
        return None
    status = match.group(1).lower()
    if status not in EXTENSION_STATUSES:
        problems.add(f"{relative(path)} declares unsupported status {status!r}")
        return None
    return status


def validate_extension_registries(
    extension_dirs: list[Path], problems: Problems
) -> None:
    declared: dict[str, str] = {}
    for directory in extension_dirs:
        spec = directory / "spec.md"
        if spec.is_file():
            status = declared_extension_status(spec, problems)
            if status is not None:
                declared[directory.name] = status

    registry_expectations = {
        ROOT / "README.md": set(declared),
        ROOT / "specs" / "extensions" / "README.md": set(declared),
        ROOT / "specs" / "VCP_SPECIFICATION_v3.1.md": set(declared) - {"VCP-X-Welfare"},
    }
    for path, expected_names in registry_expectations.items():
        text = _read_bounded_markdown(path, problems)
        if text is None:
            continue
        rows: dict[str, str] = {}
        for match in EXTENSION_ROW_RE.finditer(text):
            name = match.group(1) or match.group(2)
            status = match.group(3).lower()
            if name in rows:
                problems.add(f"{relative(path)} repeats extension registry row {name}")
            rows[name] = status
        actual_names = set(rows)
        if actual_names != expected_names:
            missing = sorted(expected_names - actual_names)
            unexpected = sorted(actual_names - expected_names)
            problems.add(
                f"{relative(path)} extension registry mismatch: "
                f"missing={missing}, unexpected={unexpected}"
            )
        for name in sorted(actual_names & set(declared)):
            if rows[name] != declared[name]:
                problems.add(
                    f"{relative(path)} labels {name} {rows[name]!r}; "
                    f"canonical spec declares {declared[name]!r}"
                )


def validate_csm1_prose(problems: Problems) -> None:
    """Reject known executable-prose drift from the normative CSM1 grammar."""
    for name in CSM1_PROSE_FILES:
        path = ROOT / name
        text = _read_bounded_markdown(path, problems)
        if text is None:
            continue
        if NAMESPACE_BEFORE_SCOPE_RE.search(text):
            problems.add(
                f"{relative(path)} places a CSM1 namespace before its scope list"
            )
        if "(?::([A-Z]{1,8}))?((?:\\+[FWPETOVAHSR])*)" in text:
            problems.add(
                f"{relative(path)} contains the obsolete namespace-first MICRO parser"
            )
        if "\\|([A-Z,]*)$" in text:
            problems.add(
                f"{relative(path)} contains an unconstrained or empty COMPACT scope-list parser"
            )
        if "\\|([^|]+)\\|" in text:
            problems.add(
                f"{relative(path)} contains an unconstrained COMPACT uvc-token parser"
            )


PROTOCOL_PROSE_RULES = {
    "specs/VCP_IDENTITY_v2.0.md": {
        "required": (
            'token-path = segment 2*9("." segment)',
            "Canonical VCP/I URI serialization MUST preserve the dots",
            "Serializers MUST emit only the dotted canonical form.",
            "VCP/I URIs cannot carry a namespace suffix",
        ),
        "forbidden": (
            'path    = segment *("/" segment)',
            "base.replace('.', '/')",
            "token.replace('.', '/')",
            "Path separators are deterministically replaced (`'.'` to `'/'`)",
        ),
    },
    "docs/identity/VCP_IDENTITY_ENCODING.md": {
        "required": (
            'token-path = segment 2*9("." segment)',
            "Canonical serializers MUST preserve the dots",
            "Canonical output remains dotted.",
        ),
        "forbidden": (
            'path    = segment *("/" segment)',
            "base.replace('.', '/')",
            "token.replace('.', '/')",
        ),
    },
    "docs/uvc/UVC_ENCODING_FORMATS.md": {
        "required": (
            'token-path = segment 2*9("." segment)',
            "Canonical serializers MUST preserve the dots",
            "Canonical output remains dotted.",
        ),
        "forbidden": (
            'path    = segment *("/" segment)',
            "base.replace('.', '/')",
            "token.replace('.', '/')",
        ),
    },
    "specs/VCP_SEMANTICS_v2.0.md": {
        "required": (
            'token-path = segment 2*9("." segment)',
            "Canonical URI serializers MUST preserve the dotted UVC token path",
        ),
        "forbidden": ('path    = segment *("/" segment)',),
    },
    "specs/VCP_ADAPTATION_v2.0.md": {
        "required": (
            "A timed-out hook MUST abort the current chain and its pipeline operation",
            "The runtime MUST give each hook a staged snapshot of chain state",
            "Hook execution failures are fail-closed.",
        ),
        "forbidden": (
            "A timed-out hook SHALL be treated as if it returned",
            "A failed hook SHALL be treated as if it returned",
            "The default behavior for hook failures is fail-open",
            'result = HookResult(status="continue")',
            "hook.cascade_failure",
        ),
    },
    "docs/adaptation/VCP_HOOKS.md": {
        "required": (
            "A timed-out hook MUST abort the current chain and its pipeline operation",
            "Each hook MUST receive a staged snapshot of chain state.",
            "### 7.1 Fail-Closed Execution Failures",
        ),
        "forbidden": (
            "A timed-out hook SHALL be treated as if it returned",
            "A failed hook SHALL be treated as if it returned",
            "The default behavior for hook failures is fail-open",
            'result = HookResult(status="continue")',
            "hook.cascade_failure",
        ),
    },
    "specs/VCP_MESSAGING_v2.0.md": {
        "required": (
            "Ed25519 signature of the canonical message envelope excluding `signature`",
            "64-byte Ed25519 signature encoded as 88 characters of standard base64",
            "Receivers MUST reject an encoded message larger than 64 KiB",
            "rfc8785_canonicalize(to_sign)",
            "[AQgw]==",
            "The VCP-SDK repository maintains the v2.0 implementation-candidate schema",
        ),
        "forbidden": (
            "schemas/vcp-messaging-v2.0.schema.json",
            "signature of the canonical payload",
            "json.dumps(\n        to_sign",
        ),
    },
    "specs/VCP_INTER_AGENT_MESSAGING_v1.2.md": {
        "required": (
            "Ed25519 signature of the canonical envelope excluding `signature`",
            "Receivers MUST reject an encoded message larger than 64 KiB",
            "rfc8785_canonicalize(to_sign)",
            "[AQgw]==",
        ),
        "forbidden": (
            "signature of the canonical payload",
            "json.dumps(\n        to_sign",
            "base64:<base64-encoded-bytes>",
        ),
    },
    "specs/VCP_SPECIFICATION_v1.0.md": {
        "required": (
            "Ed25519 signatures MUST decode to exactly 64 bytes",
            "A multisignature object MUST omit the single-signature `value` field.",
            "[AQgw]==",
        ),
        "forbidden": (
            "signature = base64.b64decode(manifest['signature']['value'])",
        ),
    },
    "specs/VCP_SPECIFICATION_v2.0.md": {
        "required": (
            "Ed25519 signatures MUST decode to exactly 64 bytes",
            "A multisignature object MUST omit the single-signature `value` field.",
            "[AQgw]==",
        ),
        "forbidden": (
            "signature = base64.b64decode(manifest['signature']['value'])",
        ),
    },
    "specs/core/capability-negotiation.md": {
        "required": (
            '`type` | string | REQUIRED | MUST be `"vcp-hello"`.',
            '`supported` UNION `unsupported` MUST equal the valid identifiers',
            "The two lists MUST be disjoint.",
        ),
        "forbidden": (
            "VCP-Hello\"",
            "MAY omit the `unsupported` field",
        ),
    },
}


def protocol_prose_errors(documents: Mapping[str, str]) -> list[str]:
    """Return targeted errors for previously observed cross-document drift."""
    errors: list[str] = []
    for name, rules in PROTOCOL_PROSE_RULES.items():
        text = documents.get(name)
        if text is None:
            errors.append(f"protocol drift source is missing: {name}")
            continue
        for required in rules["required"]:
            if required not in text:
                errors.append(f"{name} is missing required contract text: {required!r}")
        for forbidden in rules["forbidden"]:
            if forbidden in text:
                errors.append(f"{name} contains obsolete contract text: {forbidden!r}")
    return errors


def validate_protocol_prose(problems: Problems) -> None:
    documents: dict[str, str] = {}
    for name in PROTOCOL_PROSE_RULES:
        text = _read_bounded_markdown(ROOT / name, problems)
        if text is not None:
            documents[name] = text
    for error in protocol_prose_errors(documents):
        problems.add(error)


def _duplicate_values(entries: object, field: str) -> bool:
    if not isinstance(entries, list):
        return False
    values = [entry.get(field) for entry in entries if isinstance(entry, dict)]
    serialized = [json.dumps(value, sort_keys=True) for value in values]
    return len(serialized) != len(set(serialized))


def validate_repository_invariants(problems: Problems) -> None:
    for relative_path in REQUIRED_RELEASE_FILES:
        if not (ROOT / relative_path).is_file():
            problems.add(f"required release file is missing: {relative_path}")
    try:
        inventory_check = subprocess.run(
            [sys.executable, "scripts/generate_document_inventory.py", "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        problems.add(f"document inventory check could not complete: {exc}")
        inventory_check = None
    if inventory_check is not None and inventory_check.returncode:
        problems.add(inventory_check.stdout.strip() or inventory_check.stderr.strip())
    try:
        requirement_check = subprocess.run(
            [sys.executable, "scripts/generate_requirement_registry.py", "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        problems.add(f"requirement registry check could not complete: {exc}")
        requirement_check = None
    if requirement_check is not None and requirement_check.returncode:
        problems.add(
            requirement_check.stdout.strip() or requirement_check.stderr.strip()
        )
    inventory_schema = load_json(
        ROOT / "status/document-inventory.schema.json", problems
    )
    inventory = load_json(ROOT / "status/document-inventory.json", problems)
    if isinstance(inventory_schema, dict) and isinstance(inventory, dict):
        try:
            validator_class = validator_for(inventory_schema)
            validator_class.check_schema(inventory_schema)
            validator = validator_class(
                inventory_schema, format_checker=strict_format_checker()
            )
            for error in validator.iter_errors(inventory):
                location = ".".join(str(part) for part in error.absolute_path) or "root"
                problems.add(f"document inventory {location}: {error.message}")
        except Exception as exc:  # noqa: BLE001
            problems.add(f"document inventory schema is invalid: {exc}")
        if _duplicate_values(inventory.get("artifacts"), "path"):
            problems.add("document inventory repeats artifact paths")
    risk_schema = load_json(ROOT / "status/residual-risks.schema.json", problems)
    risks = load_json(ROOT / "status/residual-risks.json", problems)
    if isinstance(risk_schema, dict) and isinstance(risks, dict):
        try:
            validator_class = validator_for(risk_schema)
            validator_class.check_schema(risk_schema)
            validator = validator_class(
                risk_schema, format_checker=strict_format_checker()
            )
            for error in validator.iter_errors(risks):
                location = ".".join(str(part) for part in error.absolute_path) or "root"
                problems.add(f"residual-risk register {location}: {error.message}")
            entries = risks.get("risks", [])
            identifiers = [
                entry.get("id") for entry in entries if isinstance(entry, dict)
            ]
            if len(identifiers) != len(set(identifiers)):
                problems.add("residual-risk register repeats risk identifiers")
        except Exception as exc:  # noqa: BLE001
            problems.add(f"residual-risk schema is invalid: {exc}")
    for label, schema_name, registry_name in (
        (
            "errata registry",
            "schemas/vcp-errata-registry.schema.json",
            "registries/errata.json",
        ),
        (
            "provisional identifier registry",
            "schemas/vcp-provisional-identifiers.schema.json",
            "registries/provisional-identifiers.json",
        ),
        (
            "requirement registry",
            "schemas/vcp-requirement-registry.schema.json",
            "registries/candidate-requirements.json",
        ),
    ):
        registry_schema = load_json(ROOT / schema_name, problems)
        registry = load_json(ROOT / registry_name, problems)
        if not isinstance(registry_schema, dict) or not isinstance(registry, dict):
            continue
        try:
            validator_class = validator_for(registry_schema)
            validator_class.check_schema(registry_schema)
            validator = validator_class(
                registry_schema, format_checker=strict_format_checker()
            )
            for error in validator.iter_errors(registry):
                location = ".".join(str(part) for part in error.absolute_path) or "root"
                problems.add(f"{label} {location}: {error.message}")
        except Exception as exc:  # noqa: BLE001
            problems.add(f"{label} schema is invalid: {exc}")
    identifiers = load_json(ROOT / "registries/provisional-identifiers.json", problems)
    if isinstance(identifiers, dict):
        entries = identifiers.get("identifiers", [])
        for field in ("id", "canonical_value", "collision_key"):
            if _duplicate_values(entries, field):
                problems.add(f"provisional identifier registry repeats {field}")
    requirements = load_json(ROOT / "registries/candidate-requirements.json", problems)
    if isinstance(requirements, dict):
        entries = requirements.get("requirements", [])
        if _duplicate_values(entries, "id"):
            problems.add("candidate requirement registry repeats requirement IDs")
        sources = requirements.get("sources", [])
        if _duplicate_values(sources, "path"):
            problems.add("candidate requirement registry repeats source paths")
        coverage = requirements.get("coverage")
        if isinstance(coverage, dict) and isinstance(entries, list):
            if coverage.get("identified_requirement_count") != len(entries):
                problems.add(
                    "candidate requirement registry identified count does not match entries"
                )
            mapped = sum(
                bool(entry.get("evidence"))
                for entry in entries
                if isinstance(entry, dict)
            )
            if coverage.get("mapped_evidence_count") != mapped:
                problems.add(
                    "candidate requirement registry mapped count does not match evidence"
                )
    policy = load_json(ROOT / ".github/repository-policy.json", problems)
    if isinstance(policy, dict):
        if policy.get("schema") != "vcp-repository-policy/1":
            problems.add("repository policy has an unknown schema")
        if policy.get("repository") != "Creed-Space/VCP-Spec":
            problems.add("repository policy names the wrong repository")
        if policy.get("external_state_applied") is not False:
            problems.add("repository policy must not claim unverified external state")
        desired = policy.get("desired")
        if not isinstance(desired, dict):
            problems.add("repository policy desired settings must be an object")
            checks: object = []
        else:
            checks = desired.get("required_checks", [])
        if (
            not isinstance(checks, list)
            or any(not isinstance(check, str) for check in checks)
            or len(checks) != len(set(checks))
        ):
            problems.add("repository policy required checks must be a unique list")
    try:
        dangerous = repository_source_files(".bak")
    except (OSError, ValueError) as exc:
        problems.add(f"dangerous-artifact inventory failed: {exc}")
        dangerous = []
    dangerous += sorted(ROOT.glob("commit-*-sweep.sh"))
    for path in dangerous:
        problems.add(f"unsafe or ambiguous tracked artifact remains: {relative(path)}")
    extension_dirs = sorted((ROOT / "specs" / "extensions").glob("VCP-X-*"))
    for directory in extension_dirs:
        for required in ("spec.md", "schema.json"):
            if not (directory / required).is_file():
                problems.add(f"{relative(directory)} is missing {required}")
    validate_extension_registries(extension_dirs, problems)
    validate_csm1_prose(problems)
    validate_protocol_prose(problems)
    veps = sorted((ROOT / "veps").glob("VEP-[0-9][0-9][0-9][0-9]-*.md"))
    numbers = [int(path.name[4:8]) for path in veps]
    if numbers != list(range(1, len(numbers) + 1)):
        problems.add(f"VEP numbering is not contiguous from 0001: {numbers}")
    for path in veps:
        text = _read_bounded_markdown(path, problems)
        if text is None:
            continue
        if not re.search(r"^\*\*Status\*\*:\s+\S+", text, re.MULTILINE):
            problems.add(f"{relative(path)} has no machine-readable Status field")

    authority_schema = load_json(ROOT / "governance/authority.schema.json", problems)
    authority = load_json(ROOT / "governance/authority.json", problems)
    if isinstance(authority_schema, dict) and isinstance(authority, dict):
        try:
            validator_class = validator_for(authority_schema)
            validator_class.check_schema(authority_schema)
            validator = validator_class(
                authority_schema, format_checker=strict_format_checker()
            )
            for error in validator.iter_errors(authority):
                location = ".".join(str(part) for part in error.absolute_path) or "root"
                problems.add(f"governance authority {location}: {error.message}")
        except Exception as exc:  # noqa: BLE001
            problems.add(f"governance authority schema is invalid: {exc}")
        if authority.get("status") == "interim-unratified":
            active_parts = [
                _read_bounded_markdown(ROOT / name, problems)
                for name in ("README.md", "GOVERNANCE.md")
            ]
            active_copy = "\n".join(part for part in active_parts if part is not None)
            for forbidden in (
                "VCP is governed by a Technical Steering Committee",
                "VCP is developed in the open under neutral governance",
                "No single organization controls the protocol's direction",
            ):
                if forbidden in active_copy:
                    problems.add(
                        f"active public copy contradicts interim authority: {forbidden}"
                    )

    tracker = _read_bounded_markdown(ROOT / "veps/README.md", problems)
    if tracker is None:
        tracker = ""
    for path in veps:
        number = path.name[4:8]
        text = _read_bounded_markdown(path, problems)
        if text is None:
            continue
        status_match = re.search(r"^\*\*Status\*\*:\s+(.+)$", text, re.MULTILINE)
        row_match = re.search(
            rf"^\|\s*\[{number}\]\([^)]+\)\s*\|[^|]+\|\s*([^|]+?)\s*\|",
            tracker,
            re.MULTILINE,
        )
        if status_match and row_match:
            declared = status_match.group(1).strip().casefold()
            tracked = row_match.group(1).strip().casefold()
            if declared != tracked:
                problems.add(
                    f"{relative(path)} status {declared!r} differs from tracker {tracked!r}"
                )

    try:
        candidate = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        problems.add(f"git ls-files could not complete: {exc}")
        candidate = None
    if candidate is None:
        pass
    elif candidate.returncode:
        problems.add("git ls-files failed while checking candidate files")
    else:
        for raw in candidate.stdout.split(b"\0"):
            if not raw:
                continue
            try:
                path = ROOT / raw.decode("utf-8")
            except UnicodeDecodeError:
                problems.add("candidate contains a path that is not valid UTF-8")
                continue
            try:
                if not path.exists():
                    continue
                if path.is_symlink():
                    problems.add(
                        f"candidate source symlink requires review: {relative(path)}"
                    )
                elif path.is_file() and path.stat().st_size > 50 * 1024 * 1024:
                    problems.add(f"candidate file exceeds 50 MiB: {relative(path)}")
            except OSError as exc:
                problems.add(
                    f"candidate file changed during validation: {relative(path)}: {exc}"
                )

    uses_re = re.compile(r"^\s*uses:\s*([^#\s]+)", re.MULTILINE)
    immutable_action = re.compile(r"^[^@]+@[0-9a-f]{40}$")
    for workflow in sorted((ROOT / ".github/workflows").glob("*.yml")):
        try:
            workflow_text = read_regular_text(
                workflow,
                max_bytes=MAX_YAML_BYTES,
                root=ROOT,
                purpose="workflow",
            )
        except (OSError, UnicodeError, ValueError) as exc:
            problems.add(f"{relative(workflow)} is not readable: {exc}")
            continue
        for use in uses_re.findall(workflow_text):
            if not immutable_action.fullmatch(use):
                problems.add(f"{relative(workflow)} has unpinned action: {use}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--only",
        choices=("schemas", "links", "documents", "all"),
        default="all",
    )
    args = parser.parse_args()
    problems = Problems()
    schemas: dict[str, tuple[dict[str, object], object]] = {}
    if args.only in {"schemas", "all"}:
        schemas = validate_schemas(problems)
        validate_fixtures(schemas, problems)
        validate_spec_json_examples(schemas, problems)
        validate_status_registry(schemas, problems)
    if args.only in {"links", "all"}:
        validate_markdown(problems)
    if args.only in {"documents", "all"}:
        validate_yaml(problems)
        validate_docx(problems)
        validate_document_control(problems)
    if args.only == "all":
        validate_repository_invariants(problems)
    return problems.finish()


if __name__ == "__main__":
    raise SystemExit(main())
