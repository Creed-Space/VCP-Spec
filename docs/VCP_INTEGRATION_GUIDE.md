# VCP Integration Guide

<!-- vcp-document-control
status: Current companion
normative-authority: Accepted specifications and schemas
protocol-version: VCP 3.1
last-reviewed: 2026-08-13 status and authority classification
owner: VCP Spec maintainers
evidence-boundary: Source integration checks only
-->

| Field | Value |
|---|---|
| Status | Current, non-normative integration guide |
| Normative authority | `specs/VCP_SPECIFICATION_v3.1.md` and accepted VEPs |
| Protocol boundary | v3.1 baseline; v3.2 work is candidate or experimental |
| SDK boundary | 4.2.0 source candidate |
| Last reviewed | 2026-08-13 |
| Owner | VCP-Spec maintainers |
| Evidence boundary | Commands and imports are checked against the coordinated VCP-SDK source candidate. Registry publication and production behavior require separate evidence. |

## 1. Publication State

The VCP-SDK artifacts are **source-only candidates**. No PyPI, npm, or
crates.io release is currently claimed. Candidate package names describe local
metadata and do not establish registry availability.

Use an immutable VCP-SDK checkout at the `source_commit` recorded in
[`status/publication-state.json`](../status/publication-state.json)
(currently `null`, meaning no commit has been pinned yet). From its
repository root:

```bash
# Python source package
python -m pip install ./python

# WebMCP source package
npm --prefix webmcp ci
npm --prefix webmcp test
npm --prefix webmcp run build
npm install ./webmcp

# Rust workspace
cargo build --manifest-path ./rust/Cargo.toml -p vcp-core
```

The machine-readable publication gate is
`VCP-SDK/release/publication-state.json`, mirrored in this repository as
[`status/publication-state.json`](../status/publication-state.json)
(as_of 2026-08-15). Public registry commands become valid
only after that record contains a ratified name, an immutable source commit, an
artifact digest or attestation, a registry receipt, and a successful installed
artifact smoke test.

## 2. Integration Boundary

VCP supplies data formats, parsers, cryptographic verification primitives,
policy components, and context projection helpers. The host application owns:

1. Trust-anchor configuration and key rotation.
2. Network retrieval policy and revocation availability.
3. User consent, purpose limitation, minimisation, retention, and deletion.
4. Enforcement between verification and model-context construction.
5. Provider credentials, provider calls, budgets, logging, and incident response.
6. Human review for legal, privacy, accessibility, safety, and deployment claims.

A parser success is not a verification success. A verification success is not a
policy authorization. A formatted prompt is not proof that the host enforces the
result.

## 3. Recommended Data Flow

```text
receive reference or bundle
  -> apply size and syntax limits
  -> resolve through an allowlisted transport
  -> verify hash, signature, issuer, audience, scope, time, and revocation
  -> fail closed on invalid or unavailable required evidence
  -> evaluate host policy and consent
  -> project only purpose-required context
  -> format the verified content for the selected model boundary
  -> record a privacy-safe decision event
```

Keep the untrusted bundle separate from trusted configuration. Never let bundle
content select trust anchors, network destinations, log fields, or executable
hooks.

## 4. Python Quick Start

The checked source example below is
`VCP-SDK/examples/python/01_parse_token.py`:

```python
from vcp.identity import Token

identity = Token.parse("family.safe.guide@1.2.0")
assert identity.canonical == "family.safe.guide"
assert identity.role == "guide"
```

Run all public Python examples against the installed source package:

```bash
python -m pip install ./python
for example in examples/python/*.py; do python "$example"; done
```

For cryptographic verification, use
`examples/python/02_verify_bundle.py`. For the complete verified path, use
`examples/python/05_full_pipeline.py`. Both generate test keys locally, create a
bundle, configure trust anchors, require `VerificationResult.VALID`, and only
then prepare downstream content.

A production integration must replace generated keys and in-memory trust with an
authorized trust configuration. It must retain the same fail-closed decision
boundary.

## 5. Rust Quick Start

Build and run checked examples from the VCP-SDK root:

```bash
cargo run --manifest-path ./rust/Cargo.toml -p vcp-core --example parse_token
cargo run --manifest-path ./rust/Cargo.toml -p vcp-core --example sign_and_verify
cargo run --manifest-path ./rust/Cargo.toml -p vcp-core --example verify_bundle
```

The candidate crate name is `vcp-core`, imported as `vcp_core`. Do not add a
crates.io dependency until a registry receipt exists. During local coordinated
development, use the workspace path or a Git dependency pinned to an immutable,
reviewed commit.

## 6. WebMCP Quick Start

The browser package is a WebMCP integration subset. It does not export the
Python and Rust protocol classes. In particular, it does not export `Bundle`,
`CSM1Code`, `ContextEncoder`, or `Token`.

After building and installing the local `webmcp` directory:

```typescript
import { registerVCPTools } from '@creedspace/vcp-sdk';

const registration = await registerVCPTools({
  enableChat: false,
  tokenParser: (token) => parseWithApplicationOwnedCode(token),
});

console.log(registration.api);        // document, navigator, or unavailable
console.log(registration.registered); // accepted tool names
console.log(registration.failed);     // browser-rejected registrations
registration.cleanup();               // AbortSignal-owned and idempotent
```

The current imperative API is `document.modelContext`. The SDK keeps an isolated
`navigator.modelContext` fallback for earlier preview builds. Registration is
asynchronous, and cleanup uses AbortSignal. WebMCP remains experimental. Confirm
origin-trial, browser, and API requirements against current browser documentation
rather than relying on a browser version alone.

Generic site behavior and native WebMCP support are separate compatibility
claims. A site may work in Firefox or WebKit while native tool registration is
available only in an experimental Chromium lane.

## 7. Layer Integration Matrix

| Layer | Minimum host responsibility | Primary candidate surface |
|---|---|---|
| VCP/I Identity | Parse, canonicalize, apply namespace policy, reject invalid boundaries | Python `vcp.identity`, Rust `vcp_core::identity` |
| VCP/T Transport | Verify content, signature, trust, scope, audience, time, and revocation before use | Python orchestrator and trust modules, Rust transport and orchestrator modules |
| VCP/S Semantics | Parse CSM-1 and apply only supported semantics | Python semantics modules, Rust CSM-1 modules |
| VCP/A Adaptation | Treat personal and situational context as potentially sensitive; negotiate candidate features | Python adaptation modules, Rust context modules |
| VCP/M Messaging | Select one declared messaging version and enforce negotiation | Versioned schemas and SDK messaging modules |
| VCP/E Economic governance | Require explicit authority for consequential actions | Candidate schema and host policy |
| VCP-X extensions | Negotiate each extension and fail safely when unsupported | Extension-specific SDK modules and conformance cases |

## 8. Fail-Closed Requirements

A security-sensitive integration should reject or stop before model use when:

1. Required signatures, hashes, keys, trust anchors, or attestations are absent.
2. Content, identity, issuer, audience, scope, or temporal claims do not match.
3. Required revocation or status evidence is unavailable.
4. Canonicalization is ambiguous or differs between producer and consumer.
5. A peer does not negotiate the extension or version being sent.
6. Consent, purpose, or field-level disclosure authorization is absent or expired.
7. A budget, size, recursion, redirect, decompression, or network boundary is exceeded.
8. A hook or policy decision fails, times out, or returns an unknown state.

Log a bounded decision identifier and result. Do not log plaintext CSM-1 tokens,
personal-state payloads, prompts, keys, upstream bodies, or full bundles unless a
separately reviewed retention policy explicitly requires them.

## 9. Conformance Claims

Fixture presence and a small example table do not establish conformance. A claim
must identify:

1. The exact protocol and extension versions.
2. The exact conformance manifest and runner version.
3. The implementation and artifact digest tested.
4. Passed, failed, unsupported, and not-applicable cases.
5. The operating system, runtime, browser, and relevant feature configuration.
6. Whether the evidence is same-project parity or independent interoperability.

Use the [conformance claim vocabulary](./CONFORMANCE_CLAIMS.md). Until the complete
matrix and an independent implementation exist, describe results as scoped test
suite passes rather than ecosystem-wide VCP compliance or certification.

## 10. Predeployment Checklist

1. Pin the Spec, SDK, schemas, examples, and host integration to immutable commits.
2. Run the full repository suites and the generated conformance matrix.
3. Build packages once, inspect contents, and test the installed artifacts.
4. Complete independent security, privacy, legal, accessibility, and editorial review.
5. Configure trust roots, revocation, quotas, logging, retention, rollback, and alerts.
6. Exercise invalid, revoked, unavailable, timeout, partial, and rollback paths.
7. Record the exact release manifest, SBOMs, attestations, and approvals.
8. Publish only through an authorized workflow, then perform registry and production smoke tests.

## 11. Current Sources

1. Normative baseline: `specs/VCP_SPECIFICATION_v3.1.md`.
2. Compatibility policy: `COMPATIBILITY.md`.
3. SDK source: `https://github.com/Creed-Space/VCP-SDK`.
4. Checked examples: `VCP-SDK/examples/`.
5. Conformance corpus and runners: `VCP-SDK/conformance/`.
6. Current WebMCP API: `https://developer.chrome.com/docs/ai/webmcp/imperative-api`.
7. Publication state: `VCP-SDK/release/publication-state.json`, mirrored as [`status/publication-state.json`](../status/publication-state.json).
