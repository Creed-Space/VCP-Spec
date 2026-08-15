# VCP Extensions

## Extension Model

The Value-Context Protocol core specification (v1.0 through v1.1) defines a
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
| `examples/`      | Recommended annotated wire-format examples |

The `spec.md` is the normative document. The schema and examples are informative
but MUST be consistent with the prose specification at all times.


## Capability Negotiation

Extensions are negotiated during session establishment using the mechanism defined
in `specs/core/capability-negotiation.md`. The negotiation follows a three-step
handshake:

1. **Advertise** -- The initiator lists supported extensions and their versions
   in the `capabilities.extensions` array of the session-init message.
2. **Accept** -- The responder echoes back the subset of extensions it supports,
   along with the negotiated version for each.
3. **Confirm** -- Both parties activate only the intersection of advertised
   capabilities. Unrecognized extensions are silently ignored.

Once negotiated, extension payloads appear in the `extensions` map of VCP context
requests and responses, keyed by their canonical identifier (e.g.,
`"VCP-X-Torch"`).


## Extension Lifecycle

Every extension progresses through a defined lifecycle:

| Status         | Meaning                                                         |
|----------------|-----------------------------------------------------------------|
| EXPERIMENTAL   | Under active development. Wire format may change without notice. Implementations SHOULD flag experimental extensions to users. |
| DRAFT          | A documented candidate under review. Implementations MUST negotiate it and MUST NOT advertise accepted or stable status. |
| STABLE         | Wire format is frozen. Breaking changes require a new extension identifier (e.g., `VCP-X-Torch` to `VCP-X-Torch2`). Implementations MAY rely on stable extensions in production. |
| DEPRECATED     | Superseded by a newer extension or folded into the core. Implementations SHOULD emit warnings. Deprecated extensions are removed after two major VCP versions. |

Transition from EXPERIMENTAL to STABLE requires:

- A project-maintained implementation with passing tests.
- At least one independent consumer of the extension.
- A formal review by the VCP working group.

Transition from STABLE to DEPRECATED requires:

- A documented migration path to the replacement.
- A minimum deprecation window of two major VCP versions (e.g., deprecated in
  v3.1, removed no earlier than v5.0).


## Current Extensions (v3.2)

| Extension        | Status       | Description                                                       |
|------------------|--------------|-------------------------------------------------------------------|
| VCP-X-Personal   | Stable       | Personal state modeling: 5 categorical dimensions with intensity (1-5) and configurable decay. Dimensions: cognitive_state, emotional_tone, energy_level, perceived_urgency, body_signals. |
| VCP-X-Relational | Draft        | Relational continuity layer: trust levels (initial/developing/established/deep), standing (observer/advisory/collaborative/autonomous), established norms, AI self-model, and session continuity depth. |
| VCP-X-Consensus  | Draft        | Constitutional consensus primitive: Schulze-method voting over constitution sets with structured deliberation rounds, quorum requirements, and amendment proposals. |
| VCP-X-Torch      | Stable       | Session handoff between agents: captures relationship quality, trajectory, primes (key norms), and gestalt tokens. Enables continuity across instance boundaries. |
| VCP-X-Intent     | Experimental | Heuristic intent inference from VCP context signals. Rule-based classification into 10 intent categories with confidence scores and transparent reasoning. Correctable by users. |
| VCP-X-Welfare    | Experimental | Welfare instrumentation: core (WC/AS/bidirectional Q), embodied dimensions (robotics), temporal patterns (trajectory, checkpoints), multi-agent aggregation (swarm welfare), and attestation chains. Builds on VCP/S v2.1 welfare lines. |


## Adding a New Extension

To propose a new extension:

1. Create a directory under `specs/extensions/VCP-X-{Name}/`.
2. Write `spec.md` following the structure of existing extensions.
3. Provide a JSON Schema in `schema.json`.
4. Include at least two annotated examples in `examples/`.
5. Set the status to EXPERIMENTAL.
6. Submit the extension for review via the standard VCP RFC process.

New extensions MUST NOT conflict with existing extension identifiers or with core
protocol field names. The `extensions` map in VCP payloads is the only namespace
available to extensions; top-level fields are reserved for the core protocol.


## Versioning

Extensions are versioned independently of the core protocol. An extension version
is a semver string (e.g., `"1.0.0"`, `"2.1.0"`). The negotiated version appears
in the capability negotiation response alongside the extension identifier.

When an extension makes a breaking change that cannot be negotiated via versioning,
it MUST be published under a new identifier. The old identifier transitions to
DEPRECATED.


## Interoperability Requirements

- Implementations MUST ignore unrecognized extensions without error.
- Implementations MUST NOT require any extension for core VCP operations
  (verification, attestation, revocation).
- Extensions MAY depend on other extensions. Such dependencies MUST be declared
  in the `spec.md` under a "Dependencies" section.
- Extensions MUST NOT modify the semantics of core protocol fields.
