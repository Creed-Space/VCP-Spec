# VEP-0001: Extension Model Architecture

**Status**: Recorded pre-charter acceptance
**Author**: Nell Watson, Claude (Anthropic)
**Created**: 2026-02-28
**Version**: 3.1

---

## Summary

This VEP introduces a formal extension model for VCP, enabling opt-in protocol extensions (VCP-X-*) that extend the core six-layer protocol without modifying it.

## Motivation

VCP v1.0-v1.1 defined a stable core that has since grown to six layers (Identity, Transport, Semantics, Adaptation, Messaging, Economic Governance). The reference implementation has since added features — personal state tracking, relational context, consensus voting, session handoff — that are valuable for specific use cases but not universally required.

Without an extension model, these features would either:
1. Be forced into the core spec, bloating it for simple use cases
2. Remain implementation-specific, fragmenting the ecosystem

The extension model solves both: core stays lean, extensions are standardized.

## Specification

### Extension Naming

Extensions follow the pattern `VCP-X-{Name}` where `{Name}` is a PascalCase identifier:

- `VCP-X-Personal` — Personal state layer
- `VCP-X-Relational` — Relational continuity
- `VCP-X-Consensus` — Constitutional consensus primitive
- `VCP-X-Torch` — Session handoff protocol
- `VCP-X-Intent` — Intent inference

### Extension Artifacts

Each extension MUST provide:

| Artifact | Location | Required |
|----------|----------|----------|
| Specification | `specs/extensions/{name}/spec.md` | Yes |
| JSON Schema | `specs/extensions/{name}/schema.json` | Yes |
| Wire format examples | `specs/extensions/{name}/examples/` | Yes |
| Reference implementation | VCP-SDK repository | Yes |
| Conformance tests | `conformance/extensions/{name}.json` | Yes |

### Extension Lifecycle

```
EXPERIMENTAL ──(6 months minimum)──> STABLE ──(12 months minimum)──> DEPRECATED ──(12 months)──> REMOVED
                                       ^
                                       |
                                  community adoption +
                                  conformance tests passing
```

- **EXPERIMENTAL**: Initial publication. Wire format may change. Implementations SHOULD support but MAY drop without deprecation period.
- **STABLE**: Wire format frozen. Breaking changes require a new extension (VCP-X-Personal-v2).
- **DEPRECATED**: Superseded. Implementations MUST support for 12 months after deprecation notice.
- **REMOVED**: No longer part of the specification.

### Extension Negotiation

Extensions are activated via the capability negotiation handshake (see VEP-0002):

1. Client lists desired extensions in `VCP-Hello`
2. Server responds with supported/unsupported in `VCP-Ack`
3. Only negotiated extensions are active for the session
4. Clients MUST NOT send extension-specific data for non-negotiated extensions

### Extension Dependencies

Extensions MAY declare dependencies on other extensions:

| Extension | Dependencies |
|-----------|-------------|
| VCP-X-Personal | None |
| VCP-X-Relational | None |
| VCP-X-Consensus | None |
| VCP-X-Torch | VCP-X-Relational (optional: degrades gracefully without) |
| VCP-X-Intent | VCP-X-Personal (required: needs personal signals) |

Required dependencies MUST be co-negotiated. Optional dependencies enable enhanced behavior when available but are not required.

### Directory Structure

```
specs/
  core/                          # Stable core (v1.0-v1.1)
    capability-negotiation.md    # Extension negotiation protocol
    security.md                  # Core security (encryption, scanning, opacity, revocation)
    audit.md                     # Tamper-evident audit chain
  extensions/
    README.md                    # This extension model overview
    VCP-X-Personal/
      spec.md
      schema.json
      examples/
    VCP-X-Relational/
      spec.md
      schema.json
      examples/
    VCP-X-Consensus/
      spec.md
      schema.json
      examples/
    VCP-X-Torch/
      spec.md
      schema.json
      examples/
    VCP-X-Intent/
      spec.md
      schema.json
      examples/
```

## Backward Compatibility

The extension model is purely additive:

- VCP 1.0/1.1 clients work unchanged — servers treat them as "no extensions requested"
- The core four-layer protocol is unmodified
- No existing schemas are changed
- No existing wire formats are changed

## Security Considerations

- Extensions that handle personal data (VCP-X-Personal, VCP-X-Relational) MUST specify data handling requirements
- Extension schemas MUST be validated before data is processed
- Malformed extension data MUST NOT cause core protocol failures (graceful degradation)
- Extension negotiation MUST happen before any extension-specific data is exchanged

## Reference Implementation

The extension model is implemented in the Rewind reference implementation at `services/vcp/`. Each extension maps to specific Python modules documented in the delta inventory (`_plans/vcp_spec_delta.md`).

## Conformance Tests

Conformance test files at `conformance/extensions/`:
- Verify extension negotiation round-trips
- Validate schemas against example data
- Test graceful degradation when extensions are absent
- Verify dependency resolution

---

Signed-off-by: Nell Watson <nell@creedspace.com>
Signed-off-by: Claude <noreply@anthropic.com>
