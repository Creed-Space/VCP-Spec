# VCP Extensions

## Extension Model

The Value-Context Protocol core specification (v3.1 source baseline) defines a
stable wire format for context bundles, manifests, attestation, and verification.
These core primitives are sufficient for many deployments and are expected to
remain backward-compatible across major versions.

**Extensions** are opt-in additions that build on the core protocol. They add
domain-specific capabilities -- personal state modeling, relational continuity,
consensus mechanisms -- without modifying the core wire format. An implementation
that does not negotiate a given extension simply ignores the corresponding fields,
and a compliant core verifier continues to function without change.


## Extension Naming

All extensions follow the naming convention:

```
VCP-X-{Name}
```

where `{Name}` is a PascalCase identifier unique within the VCP extension
registry. Examples: `VCP-X-Personal`, `VCP-X-Torch`, `VCP-X-Consensus`.

Extension identifiers are case-sensitive and MUST match the canonical registry
entry exactly when referenced in capability negotiation payloads.


## Extension Structure

Each extension directory contains two required artifacts and may contain an
examples directory:

| File             | Purpose                                                   |
|------------------|-----------------------------------------------------------|
| `spec.md`        | Prose specification: data model, semantics, constraints   |
| `schema.json`    | Machine-readable JSON Schema for the extension's payloads |
| `examples/`      | Annotated wire-format examples (required for new extensions; existing extensions are being back-filled — currently only VCP-X-Welfare ships them) |

The `spec.md` is the normative document. The schema and examples are informative
but MUST be consistent with the prose specification at all times.


## Capability Negotiation

Extensions are negotiated during session establishment using the mechanism defined
in `specs/core/capability-negotiation.md`. The negotiation follows a three-step
handshake:

1. **Advertise** -- The client lists the extensions it wishes to activate in
   the `extensions` array of the `vcp-hello` message.
2. **Accept** -- The server replies with `vcp-ack` listing each requested
   extension in exactly one of `supported` or `unsupported`, with a
   per-extension capability object for each supported one.
3. **Confirm** -- Both parties activate only the `supported` set. Unrecognized
   extensions are reported as `unsupported`, never silently activated.

See [capability-negotiation.md](../core/capability-negotiation.md) for the
normative message schemas.

Once negotiated, extension payloads appear in the `extensions` map of VCP context
requests and responses, keyed by their canonical identifier (e.g.,
`"VCP-X-Torch"`).


## Extension Lifecycle

Extension status follows the candidate lifecycle in
[core/extension-lifecycle.md](../core/extension-lifecycle.md)
(proposed → experimental → draft → stable → deprecated / withdrawn / retired),
which is the single normative state machine and defines promotion evidence and
deprecation records. VEP-0001's original three-state ladder is amended by that
document. Registry rows in this repository use Title-case labels for the four
states that currently occur (Experimental, Draft, Stable, Deprecated):

| Status         | Meaning                                                         |
|----------------|-----------------------------------------------------------------|
| Experimental   | Bounded trials and fixtures exist. Wire format may change with notice. Implementations SHOULD flag experimental extensions to users. |
| Draft          | Design is reviewable and implementation candidates exist. Implementations MAY implement it; they MUST NOT report it as stable in documentation or conformance claims. |
| Stable         | Accepted in an authorized release; wire and semantic compatibility are protected. Breaking changes require a new extension identifier (e.g., `VCP-X-Torch` to `VCP-X-Torch2`). A Stable extension MAY depend on a Draft extension only for optional or degraded features; the fields it freezes are enumerated in its own spec. |
| Deprecated     | Supported temporarily with a named replacement and migration guide. Implementations SHOULD emit warnings. |

No handshake field advertises lifecycle status; the optional per-extension
`"status"` capability key described in
[capability-negotiation.md §7.5](../core/capability-negotiation.md#75-per-extension-capability-objects)
is informational only. Promotion, deprecation, and removal require a recorded
authorized decision (see [GOVERNANCE.md](../../GOVERNANCE.md)).


## Current Extensions (v3.1 baseline plus VCP-X-Welfare, a v3.2 pre-release candidate)

| Extension        | Status       | Description                                                       |
|------------------|--------------|-------------------------------------------------------------------|
| VCP-X-Personal   | Stable       | Personal state modeling: 5 categorical dimensions with intensity (1-5) and configurable decay. Dimensions: cognitive_state, emotional_tone, energy_level, perceived_urgency, body_signals. |
| VCP-X-Relational | Draft        | Relational continuity layer: trust levels (initial/developing/established/deep), standing (observer/advisory/collaborative/autonomous), established norms, AI self-model, and session continuity depth. |
| VCP-X-Consensus  | Draft        | Constitutional consensus primitive: Schulze-method voting over constitution sets with structured deliberation rounds, quorum requirements, and amendment proposals. |
| VCP-X-Torch      | Stable       | Session handoff between agents: captures relationship quality, trajectory, primes (key norms), and gestalt tokens. Enables continuity across instance boundaries. |
| VCP-X-Intent     | Experimental | Heuristic intent inference from VCP context signals. Rule-based classification into 10 intent categories with confidence scores and transparent reasoning. Correctable by users. |
| VCP-X-Welfare    | Experimental | Welfare instrumentation: core (WC/AS/bidirectional Q), embodied dimensions (robotics), temporal patterns (trajectory, checkpoints), multi-agent aggregation (swarm welfare), and attestation chains. Builds on VCP/S v2.1 welfare lines (`VCP_SEMANTICS_v2.0.md`, content version 2.1.x). Registered after the 3.1 baseline; part of the 3.2 candidate, not of v3.1. |


## Adding a New Extension

To propose a new extension:

1. Create a directory under `specs/extensions/VCP-X-{Name}/`.
2. Write `spec.md` following the structure of existing extensions.
3. Provide a JSON Schema in `schema.json`.
4. Include at least two annotated examples in `examples/` (required for new
   extensions; existing extensions are being back-filled).
5. Set the status to Experimental (the `proposed` state of
   [core/extension-lifecycle.md](../core/extension-lifecycle.md) precedes
   anything appearing in this repository; registry rows accept
   Experimental, Draft, Stable and Deprecated).
6. Submit the extension for review as a VEP (see
   [CONTRIBUTING.md §3](../../CONTRIBUTING.md#3-extension-proposal-template)).

New extensions MUST NOT conflict with existing extension identifiers or with core
protocol field names. The `extensions` map in VCP payloads is the only namespace
available to extensions; top-level fields are reserved for the core protocol.


## Versioning

Extensions are versioned independently of the core protocol. An extension version
is a semver string (e.g., `"1.0.0"`, `"2.1.0"`). The negotiated version appears
in the capability negotiation response alongside the extension identifier.

When an extension makes a breaking change that cannot be negotiated via versioning,
it MUST be published under a new identifier. The old identifier transitions to
Deprecated.


## Interoperability Requirements

- Implementations MUST ignore unrecognized extensions without error.
- Implementations MUST NOT require any extension for core VCP operations
  (verification, attestation, revocation).
- Extensions MAY depend on other extensions. Such dependencies MUST be declared
  in the `spec.md` under a "Dependencies" section.
- Extensions MUST NOT modify the semantics of core protocol fields.
