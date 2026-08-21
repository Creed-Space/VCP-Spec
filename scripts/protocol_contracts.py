"""Cross-field protocol checks that JSON Schema cannot express directly."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

PERSONA_NAMES = {
    "N": "nanny",
    "Z": "sentinel",
    "G": "godparent",
    "A": "ambassador",
    "M": "muse",
    "D": "mediator",
    "C": "custom",
}
SCOPE_CONFLICTS = {
    frozenset(("F", "A")),
    frozenset(("V", "A")),
    frozenset(("H", "A")),
}
VERSION = (
    r"(?:(?:0|[1-9][0-9]{0,2})\.(?:0|[1-9][0-9]{0,2})"
    r"\.(?:0|[1-9][0-9]{0,2})|latest|canary)"
)
UVC_TOKEN = (
    r"[a-z][a-z0-9-]{0,31}(?:\.[a-z][a-z0-9-]{0,31}){2,9}"
    r"(?:@(?:[\^~]?(?:0|[1-9][0-9]{0,4})\.(?:0|[1-9][0-9]{0,4})"
    r"\.(?:0|[1-9][0-9]{0,4})|latest|canary))?"
    r"(?::[A-Z][A-Z0-9]{0,31})?"
)
CSM1_RE = re.compile(
    rf"^(?P<persona>[NZGAMDC])(?P<adherence>[0-5])"
    rf"(?P<scope_text>(?:\+[FWPETOVAHSR])*)"
    rf"(?::(?P<namespace>[A-Z]{{1,8}}))?"
    rf"(?:@(?P<version>{VERSION}))?$"
)
COMPACT_RE = re.compile(
    rf"^CS1\|(?P<persona_name>{'|'.join(PERSONA_NAMES.values())})"
    rf"\|(?P<adherence>[0-5])\|(?P<uvc_token>{UVC_TOKEN})"
    r"\|(?P<scope_text>[FWPETOVAHSR](?:,[FWPETOVAHSR])*)$"
)
MINOR_RE = re.compile(r"^(?:0|[1-9][0-9]{0,8})\.(?:0|[1-9][0-9]{0,8})$")
EXTENSION_RE = re.compile(r"^VCP-X-[A-Za-z][A-Za-z0-9-]*$")


def _validate_scopes(scopes: list[str]) -> None:
    if len(scopes) != len(set(scopes)):
        raise ValueError("duplicate CSM1 scope")
    active = set(scopes)
    if any(conflict <= active for conflict in SCOPE_CONFLICTS):
        raise ValueError("conflicting CSM1 scopes")


def parse_csm1(code: str) -> dict[str, object]:
    """Parse a bounded NANO/MICRO code and enforce semantic scope rules."""
    if not isinstance(code, str) or len(code) > 45:
        raise ValueError("CSM1 code must be a string of at most 45 characters")
    match = CSM1_RE.fullmatch(code)
    if match is None:
        raise ValueError("invalid CSM1 NANO/MICRO grammar")
    scopes = [part for part in match["scope_text"].split("+") if part]
    _validate_scopes(scopes)
    persona = match["persona"]
    namespace = match["namespace"]
    if persona == "C" and namespace is None:
        raise ValueError("custom CSM1 persona requires a namespace")
    return {
        "persona": persona,
        "persona_name": PERSONA_NAMES[persona],
        "adherence": int(match["adherence"]),
        "scopes": scopes,
        "namespace": namespace,
        "version": match["version"],
    }


def canonical_csm1(parsed: Mapping[str, object]) -> str:
    scopes = sorted(set(parsed.get("scopes", [])))
    result = f"{parsed['persona']}{parsed['adherence']}"
    result += "".join(f"+{scope}" for scope in scopes)
    if parsed.get("namespace"):
        result += f":{str(parsed['namespace']).upper()}"
    if parsed.get("version"):
        result += f"@{parsed['version']}"
    return result


def parse_compact_csm1(code: str) -> dict[str, object]:
    """Parse COMPACT CSM1 without accepting empty, duplicate, or conflicting scopes."""
    if not isinstance(code, str) or not 18 <= len(code) <= 294:
        raise ValueError("COMPACT CSM1 code must contain 18 to 294 characters")
    match = COMPACT_RE.fullmatch(code)
    if match is None:
        raise ValueError("invalid COMPACT CSM1 grammar")
    scopes = match["scope_text"].split(",")
    _validate_scopes(scopes)
    persona_name = match["persona_name"]
    persona = next(code for code, name in PERSONA_NAMES.items() if name == persona_name)
    return {
        "persona": persona,
        "persona_name": persona_name,
        "adherence": int(match["adherence"]),
        "scopes": scopes,
        "uvc_token": match["uvc_token"],
    }


def validate_csm1_document(document: object) -> list[str]:
    if not isinstance(document, Mapping) or not isinstance(document.get("code"), str):
        return []
    try:
        parsed = parse_csm1(document["code"])
    except ValueError as exc:
        return [str(exc)]
    errors: list[str] = []
    for field in ("persona", "persona_name", "adherence", "scopes", "namespace", "version"):
        if field in document and document[field] != parsed[field]:
            errors.append(f"{field} contradicts code")
    if "canonical" in document and document["canonical"] != canonical_csm1(parsed):
        errors.append("canonical does not match code")
    compact = document.get("compact")
    if isinstance(compact, str):
        try:
            compact_parsed = parse_compact_csm1(compact)
        except ValueError as exc:
            errors.append(str(exc))
        else:
            for field in ("persona", "persona_name", "adherence", "scopes"):
                if compact_parsed[field] != parsed[field]:
                    errors.append(f"compact {field} contradicts code")
    return errors


def parse_minor(version: object) -> tuple[int, int]:
    if not isinstance(version, str) or MINOR_RE.fullmatch(version) is None:
        raise ValueError("version must be canonical bounded major.minor")
    major, minor = version.split(".")
    return int(major), int(minor)


def valid_extension_ids(values: object) -> list[str]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        return []
    return [
        value
        for value in values
        if isinstance(value, str)
        and len(value) <= 128
        and EXTENSION_RE.fullmatch(value) is not None
    ]


def validate_handshake_message(message: object) -> list[str]:
    if not isinstance(message, Mapping) or message.get("type") != "vcp-hello":
        return []
    try:
        maximum = parse_minor(message.get("version"))
        minimum = parse_minor(message.get("min_version", "1.0"))
    except ValueError as exc:
        return [str(exc)]
    return ["min_version exceeds version"] if minimum > maximum else []


def validate_handshake_exchange(hello: object, response: object) -> list[str]:
    """Validate the cross-message invariants of a successful handshake."""
    errors = validate_handshake_message(hello)
    if not isinstance(hello, Mapping) or not isinstance(response, Mapping):
        return [*errors, "handshake exchange must contain two objects"]
    if hello.get("type") != "vcp-hello" or response.get("type") != "vcp-ack":
        return [*errors, "handshake exchange must contain vcp-hello then vcp-ack"]
    try:
        minimum = parse_minor(hello.get("min_version", "1.0"))
        maximum = parse_minor(hello.get("version"))
        negotiated = parse_minor(response.get("version"))
    except ValueError as exc:
        return [*errors, str(exc)]
    if not minimum <= negotiated <= maximum:
        errors.append("negotiated version is outside the client range")
    requested = set(valid_extension_ids(hello.get("extensions", [])))
    supported_raw = response.get("supported", [])
    unsupported_raw = response.get("unsupported", [])
    supported = set(valid_extension_ids(supported_raw))
    unsupported = set(valid_extension_ids(unsupported_raw))
    if supported & unsupported:
        errors.append("supported and unsupported overlap")
    if supported | unsupported != requested:
        errors.append("supported and unsupported do not partition valid requests")
    capabilities = response.get("capabilities", {})
    if isinstance(capabilities, Mapping) and not set(capabilities) <= supported:
        errors.append("capabilities contain an extension that is not supported")
    if "VCP-X-Torch" in supported and "VCP-X-Relational" not in supported:
        torch = capabilities.get("VCP-X-Torch") if isinstance(capabilities, Mapping) else None
        if not isinstance(torch, Mapping) or torch.get("degraded") is not True:
            errors.append(
                "Torch without Relational must advertise degraded capability"
            )
    if "VCP-X-Intent" in supported and "VCP-X-Personal" not in supported:
        intent = capabilities.get("VCP-X-Intent") if isinstance(capabilities, Mapping) else None
        if not isinstance(intent, Mapping) or intent.get("personal_signals") is not False:
            errors.append(
                "Intent without Personal must disable personal_signals capability"
            )
    return errors


def validate_manifest_document(document: object) -> list[str]:
    if not isinstance(document, Mapping):
        return []
    signature = document.get("signature")
    if not isinstance(signature, Mapping) or signature.get("algorithm") != "ed25519-multisig":
        return []
    signers = signature.get("signers")
    threshold = signature.get("threshold")
    if not isinstance(signers, list) or not isinstance(threshold, int):
        return []
    errors: list[str] = []
    if threshold > len(signers):
        errors.append("multisig threshold exceeds signer count")
    identifiers = [signer.get("id") for signer in signers if isinstance(signer, Mapping)]
    if len(identifiers) != len(set(identifiers)):
        errors.append("multisig signer identifiers are not unique")
    return errors


def validate_fixture_semantics(schema_name: str, document: object) -> list[str]:
    if schema_name == "vcp-semantics-csm1":
        return validate_csm1_document(document)
    if schema_name == "vcp-capability-handshake":
        return validate_handshake_message(document)
    if schema_name == "vcp-manifest-v1":
        return validate_manifest_document(document)
    return []
