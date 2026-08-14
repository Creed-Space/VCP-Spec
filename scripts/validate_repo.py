#!/usr/bin/env python3
"""Deterministic validation for the VCP specification repository."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import zipfile
from datetime import date
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml
from jsonschema import FormatChecker
from jsonschema.validators import validator_for

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOTS = (ROOT / "schemas", ROOT / "specs" / "extensions")
PUBLIC_MARKDOWN = {
    ROOT / "README.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "GOVERNANCE.md",
    ROOT / "LICENSING_STATUS.md",
    ROOT / "SECURITY.md",
    ROOT / "COMPATIBILITY.md",
    ROOT / "ARTIFACTS.md",
    ROOT / "docs" / "README.md",
    ROOT / "veps" / "README.md",
}
CONTROLLED_POLICY_MARKDOWN = PUBLIC_MARKDOWN | {
    ROOT / "DEPENDENCY_POLICY.md",
    ROOT / "RELEASE_CHECKLIST.md",
    ROOT / "REPOSITORY_CONTROLS.md",
}
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
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
EXTENSION_ROW_RE = re.compile(
    r"^\|\s*(?:\[(VCP-X-[A-Za-z]+)\]\([^)]+\)|(VCP-X-[A-Za-z]+))"
    r"\s*\|\s*([A-Za-z]+)\s*\|",
    re.MULTILINE,
)
EXTENSION_STATUSES = {"draft", "stable", "experimental", "deprecated"}
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


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def json_files() -> list[Path]:
    files: set[Path] = set()
    for root in SCHEMA_ROOTS:
        files.update(root.rglob("*.json"))
    return sorted(files)


def schema_files() -> list[Path]:
    return [
        path
        for path in json_files()
        if "examples" not in path.parts
        and (path.name.endswith(".schema.json") or path.name == "schema.json")
    ]


def load_json(path: Path, problems: Problems) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        problems.add(f"{relative(path)} is not valid UTF-8 JSON: {exc}")
        return None


def validate_schemas(problems: Problems) -> dict[str, tuple[dict[str, object], object]]:
    schemas: dict[str, tuple[dict[str, object], object]] = {}
    ids: dict[str, Path] = {}
    for path in schema_files():
        loaded = load_json(path, problems)
        if not isinstance(loaded, dict):
            if loaded is not None:
                problems.add(f"{relative(path)} must contain a JSON object")
            continue
        try:
            validator_class = validator_for(loaded)
            validator_class.check_schema(loaded)
            validator = validator_class(loaded, format_checker=FormatChecker())
        except Exception as exc:  # noqa: BLE001  # validator classes expose distinct errors
            problems.add(f"{relative(path)} is not a valid declared schema: {exc}")
            continue
        schema_id = loaded.get("$id")
        if isinstance(schema_id, str):
            if schema_id in ids:
                problems.add(
                    f"duplicate schema $id {schema_id!r}: {relative(ids[schema_id])} and {relative(path)}"
                )
            ids[schema_id] = path
        schemas[path.stem.removesuffix(".schema")] = (loaded, validator)
        for index, example in enumerate(loaded.get("examples", [])):
            errors = list(validator.iter_errors(example))
            if errors:
                problems.add(
                    f"{relative(path)} top-level example {index + 1} is invalid: {errors[0].message}"
                )
    return schemas


def validate_fixtures(
    schemas: dict[str, tuple[dict[str, object], object]], problems: Problems
) -> None:
    examples = ROOT / "schemas" / "examples"
    if not examples.is_dir():
        problems.add("schemas/examples is missing")
        return
    fixtures = sorted(examples.rglob("*.json"))
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
        errors = list(validator.iter_errors(fixture))
        if expectation == "valid" and errors:
            problems.add(f"{relative(path)} should be valid: {errors[0].message}")
        if expectation == "invalid" and not errors:
            problems.add(f"{relative(path)} should be rejected but was accepted")
    for required in ("vcp-manifest-v1", "vcp-semantics-csm1"):
        if seen.get(required) != {"valid", "invalid"}:
            problems.add(
                f"{required} requires at least one valid and one invalid fixture"
            )


def strip_fenced_code(text: str) -> str:
    output: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            output.append(line)
    return "\n".join(output)


def link_target(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("<") and ">" in raw:
        return raw[1 : raw.index(">")]
    return raw.split(maxsplit=1)[0]


def validate_markdown(problems: Problems) -> None:
    for path in sorted(ROOT.rglob("*.md")):
        if any(
            part.startswith(".") or part in {"node_modules", "target"}
            for part in path.parts
        ):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            problems.add(f"{relative(path)} is not readable UTF-8: {exc}")
            continue
        if path in PUBLIC_MARKDOWN:
            lines = text.splitlines()
            if not any(line.startswith("# ") for line in lines[:20]):
                problems.add(f"{relative(path)} needs one H1 in its first 20 lines")
            if any(line.endswith((" ", "\t")) for line in lines):
                problems.add(f"{relative(path)} contains trailing whitespace")
        searchable = strip_fenced_code(text)
        for raw in LINK_RE.findall(searchable):
            target = unquote(link_target(raw))
            parts = urlsplit(target)
            if parts.scheme or target.startswith(("#", "//")):
                continue
            clean = parts.path
            if not clean:
                continue
            destination = (
                ROOT / clean.lstrip("/")
                if clean.startswith("/")
                else path.parent / clean
            )
            destination = destination.resolve(strict=False)
            try:
                destination.relative_to(ROOT)
            except ValueError:
                problems.add(f"{relative(path)} link escapes repository: {target}")
                continue
            if not destination.exists():
                problems.add(f"{relative(path)} has broken local link: {target}")


def validate_yaml(problems: Problems) -> None:
    paths = sorted(ROOT.rglob("*.yml")) + sorted(ROOT.rglob("*.yaml"))
    for path in paths:
        if any(part.startswith(".") and part != ".github" for part in path.parts):
            continue
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            problems.add(f"{relative(path)} is not valid YAML: {exc}")


def validate_docx(problems: Problems) -> None:
    for path in sorted(ROOT.glob("*.docx")):
        try:
            with zipfile.ZipFile(path) as archive:
                bad_member = archive.testzip()
                if bad_member:
                    problems.add(f"{relative(path)} has corrupt member {bad_member}")
                if "word/document.xml" not in archive.namelist():
                    problems.add(f"{relative(path)} is missing word/document.xml")
        except (OSError, zipfile.BadZipFile) as exc:
            problems.add(f"{relative(path)} is not a valid DOCX package: {exc}")


def validate_document_control(problems: Problems) -> None:
    """Require complete, current control metadata on every active docs page."""
    today = date.today()
    controlled_paths = set((ROOT / "docs").rglob("*.md")) | CONTROLLED_POLICY_MARKDOWN
    for path in sorted(controlled_paths):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            problems.add(f"{relative(path)} is not readable UTF-8: {exc}")
            continue
        match = DOCUMENT_CONTROL_RE.search(text)
        if match is None:
            problems.add(f"{relative(path)} has no vcp-document-control header")
            continue
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
        try:
            reviewed = date.fromisoformat(reviewed_value[:10])
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
    text = path.read_text(encoding="utf-8")
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
        text = path.read_text(encoding="utf-8")
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


def validate_repository_invariants(problems: Problems) -> None:
    for relative_path in REQUIRED_RELEASE_FILES:
        if not (ROOT / relative_path).is_file():
            problems.add(f"required release file is missing: {relative_path}")
    policy = load_json(ROOT / ".github/repository-policy.json", problems)
    if isinstance(policy, dict):
        if policy.get("schema") != "vcp-repository-policy/1":
            problems.add("repository policy has an unknown schema")
        if policy.get("repository") != "Creed-Space/VCP-Spec":
            problems.add("repository policy names the wrong repository")
        if policy.get("external_state_applied") is not False:
            problems.add("repository policy must not claim unverified external state")
        checks = policy.get("desired", {}).get("required_checks", [])
        if not isinstance(checks, list) or len(checks) != len(set(checks)):
            problems.add("repository policy required checks must be a unique list")
    dangerous = sorted(ROOT.rglob("*.bak")) + sorted(ROOT.glob("commit-*-sweep.sh"))
    for path in dangerous:
        problems.add(f"unsafe or ambiguous tracked artifact remains: {relative(path)}")
    extension_dirs = sorted((ROOT / "specs" / "extensions").glob("VCP-X-*"))
    for directory in extension_dirs:
        for required in ("spec.md", "schema.json"):
            if not (directory / required).is_file():
                problems.add(f"{relative(directory)} is missing {required}")
    validate_extension_registries(extension_dirs, problems)
    veps = sorted((ROOT / "veps").glob("VEP-[0-9][0-9][0-9][0-9]-*.md"))
    numbers = [int(path.name[4:8]) for path in veps]
    if numbers != list(range(1, len(numbers) + 1)):
        problems.add(f"VEP numbering is not contiguous from 0001: {numbers}")
    for path in veps:
        text = path.read_text(encoding="utf-8")
        if not re.search(r"^\*\*Status\*\*:\s+\S+", text, re.MULTILINE):
            problems.add(f"{relative(path)} has no machine-readable Status field")

    authority_schema = load_json(ROOT / "governance/authority.schema.json", problems)
    authority = load_json(ROOT / "governance/authority.json", problems)
    if isinstance(authority_schema, dict) and isinstance(authority, dict):
        try:
            validator_class = validator_for(authority_schema)
            validator_class.check_schema(authority_schema)
            validator = validator_class(
                authority_schema, format_checker=FormatChecker()
            )
            for error in validator.iter_errors(authority):
                location = ".".join(str(part) for part in error.absolute_path) or "root"
                problems.add(f"governance authority {location}: {error.message}")
        except Exception as exc:  # noqa: BLE001
            problems.add(f"governance authority schema is invalid: {exc}")
        if authority.get("status") == "interim-unratified":
            active_copy = "\n".join(
                (ROOT / name).read_text(encoding="utf-8")
                for name in ("README.md", "GOVERNANCE.md")
            )
            for forbidden in (
                "VCP is governed by a Technical Steering Committee",
                "VCP is developed in the open under neutral governance",
                "No single organization controls the protocol's direction",
            ):
                if forbidden in active_copy:
                    problems.add(
                        f"active public copy contradicts interim authority: {forbidden}"
                    )

    tracker = (ROOT / "veps/README.md").read_text(encoding="utf-8")
    for path in veps:
        number = path.name[4:8]
        text = path.read_text(encoding="utf-8")
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

    candidate = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if candidate.returncode:
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
            if not path.exists():
                continue
            if path.is_symlink():
                problems.add(
                    f"candidate source symlink requires review: {relative(path)}"
                )
            elif path.is_file() and path.stat().st_size > 50 * 1024 * 1024:
                problems.add(f"candidate file exceeds 50 MiB: {relative(path)}")

    uses_re = re.compile(r"^\s*uses:\s*([^#\s]+)", re.MULTILINE)
    immutable_action = re.compile(r"^[^@]+@[0-9a-f]{40}$")
    for workflow in sorted((ROOT / ".github/workflows").glob("*.yml")):
        for use in uses_re.findall(workflow.read_text(encoding="utf-8")):
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
