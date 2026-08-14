# Value-Context Protocol Overview

<!-- vcp-document-control
status: Current companion
normative-authority: Accepted specifications and schemas
protocol-version: VCP 3.1
last-reviewed: 2026-08-13 status and authority classification
owner: VCP Spec maintainers
evidence-boundary: Architecture summary only
-->

| Field | Value |
|:---|:---|
| Status | Current non-normative overview |
| Normative authority | [VCP 3.1](../specs/VCP_SPECIFICATION_v3.1.md), accepted VEPs, and versioned schemas |
| Protocol baseline | VCP 3.1, with VCP 3.2 material remaining pre-release |
| Last reviewed | 2026-08-13 |
| Owner | VCP Spec maintainers |
| Evidence boundary | Architecture summary. It does not prove implementation, deployment, or conformance. |

## Purpose

The Value-Context Protocol, VCP, defines portable representations for declared
values, constitutional profiles, adaptation context, and related provenance.
An application can carry these representations between cooperating components,
verify integrity relative to configured trust anchors, and record the decision
path by which context was accepted or rejected.

VCP does not cause a model to honor a constraint by itself. The host application
owns verification, authorization, policy enforcement, privacy controls, prompt
or tool integration, output handling, and audit. A complete deployment proves
that the verified decision reaches every relevant execution path.

## Protocol shape

The repository describes six named layers:

| Layer | Concern | Present maturity boundary |
|:---|:---|:---|
| VCP/I, Identity | Stable identifiers, namespaces, and tokens | Core baseline material |
| VCP/T, Transport | Manifests, integrity, signatures, trust, revocation, and audit | Core baseline material |
| VCP/S, Semantics | Compact constitutional meaning and composition | Core baseline material |
| VCP/A, Adaptation | Situational context, state, and hook behavior | Core baseline plus candidate extensions |
| VCP/M, Messaging | Governed messages and escalation | Summary in the baseline, detailed layer material separately versioned |
| VCP/E, Economic governance | Authorization and fiduciary constraints | Summary in the baseline, detailed layer material separately versioned |

The four core layers, I, T, S, and A, have the most complete specification and
implementation evidence. A six-layer architecture claim therefore describes
the intended stack. It does not imply equal maturity across every layer.

## Authority and status

The repository baseline is VCP 3.1. VCP 3.2 amendments and VEP-0004 remain
pre-release or experimental until the interim governance process records an
authorized decision. VEP-0005 is a draft adaptation to MCP 2026-07-28 and does
not change VCP 3.1.

The current SDK candidate is source-only. Python, Rust, WASM, CLI, and WebMCP
metadata names are candidate identifiers. No registry availability follows from
those identifiers. See the machine-readable
[publication state](../status/publication-state.json).

## Trust and enforcement boundary

A safe VCP processing path has distinct stages:

```text
untrusted bytes
  -> bounded parse and schema selection
  -> canonicalization and content hash
  -> trust anchor and signature decision
  -> temporal, audience, scope, region, and revocation checks
  -> privacy projection and application policy
  -> explicitly authorized injection or tool behavior
  -> redacted audit event
```

Parsing success is not verification. Signature success is not authorization.
Context minimization is not consent. A conformance runner proves only the suites
and implementation surfaces named in its report.

## Implementations

The sibling VCP-SDK repository contains:

- a Python reference implementation and MCP server entry point;
- a Rust core library, CLI, and WASM package;
- a WebMCP browser subset for registering VCP-oriented tools;
- language-neutral fixtures and checked conformance runners.

The sibling VCP-Demo-Site repository demonstrates selected user experiences.
It is an application and never serves as normative or conformance authority.

## Next reading

- [Newcomer guide](./VCP_NEWCOMER_GUIDE.md)
- [Integration guide](./VCP_INTEGRATION_GUIDE.md)
- [Context data flow](./VCP_CONTEXT_DATA_FLOW.md)
- [Compatibility policy](../COMPATIBILITY.md)
- [Ecosystem status](./ECOSYSTEM_STATUS.md)
