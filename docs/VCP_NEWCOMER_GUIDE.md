# VCP Newcomer Guide

<!-- vcp-document-control
status: Current companion
normative-authority: Accepted specifications and schemas
protocol-version: VCP 3.1
last-reviewed: 2026-08-13 status and authority classification
owner: VCP Spec maintainers
evidence-boundary: Orientation only
-->

| Field | Value |
|:---|:---|
| Status | Current non-normative guide |
| Normative authority | VCP 3.1 and accepted VEPs |
| Protocol baseline | VCP 3.1 |
| Last reviewed | 2026-08-13 |
| Owner | VCP Spec maintainers |
| Evidence boundary | Orientation only |

## The problem VCP addresses

AI applications often carry values and situational context as informal prompt
text. That makes provenance, versioning, minimization, compatibility, and audit
difficult. VCP defines structured forms for declared values and context so a
cooperating host can verify and apply them through an explicit policy path.

VCP is useful when the same declared context must cross a component, process,
vendor, language, or agent boundary while preserving meaning and provenance.

## What VCP provides

- identity tokens and namespaces;
- signed bundle and manifest structures;
- CSM-1 compact semantic expressions;
- adaptation and personal-state structures;
- capability negotiation and version boundaries;
- optional extensions with their own lifecycle;
- audit-oriented failure codes and conformance fixtures.

## What VCP leaves to the host

The host chooses trust anchors, obtains consent, enforces authorization,
minimizes private context, resolves conflicts, controls model and tool access,
redacts logs, manages retention, and handles incident response. A syntactically
valid VCP object is still untrusted input until the required checks succeed.

## Maturity at a glance

| Surface | Current state |
|:---|:---|
| VCP 3.1 | Repository baseline |
| VCP 3.2 amendments | Pre-release candidate |
| Extensions | Mixed stable, draft, and experimental statuses |
| SDKs | Source-only release candidates |
| Demo | Demonstration application |
| Conformance | Machine-reported suite coverage, with unsupported areas explicit |
| Certification | No certification programme is authorized |
| IETF draft | Expired working copy requiring rights and technical review |

## A safe first exercise

1. Read the [overview](./VCP_OVERVIEW.md) and the normative
   [VCP 3.1 specification](../specs/VCP_SPECIFICATION_v3.1.md).
2. Select an exact sibling VCP-SDK commit.
3. Install the Python source candidate with `python -m pip install ./python`.
4. Parse a CSM-1 expression using the tested example in the SDK.
5. Run the applicable conformance runner and inspect its machine-readable report.
6. Treat unsupported suites as unsupported.

The full [integration guide](./VCP_INTEGRATION_GUIDE.md) describes the trust and
deployment boundaries. The [ecosystem status](./ECOSYSTEM_STATUS.md) shows which
claims are currently available.

## Vocabulary

**Compatible** means a named implementation accepts a declared version or
surface under a documented matrix. **Conformant** means an exact implementation
and exact protocol revision pass every mandatory suite for a defined profile.
**Certified** is reserved for a future authorized programme with independent
criteria, appeals, expiry, and revocation. Repository badges cannot create that
authority.

## Contributing

Protocol changes start in the canonical VCP-Spec VEP intake. SDK-only changes
may be proposed in VCP-SDK when they do not alter the wire contract. Review the
[interim governance](../GOVERNANCE.md), [contribution guide](../CONTRIBUTING.md),
and [document control](./DOCUMENT_CONTROL.md) before editing normative material.
