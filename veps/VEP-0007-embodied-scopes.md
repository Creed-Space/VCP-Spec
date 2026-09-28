# VEP-0007: Embodied CSM-1 Scopes (B and X)

**Status**: Draft
**Author**: Nell Watson
**Created**: 2026-09-28
**Targets**: VCP_SEMANTICS_v2.0.md (§2.6.1 scope table and the CSM-1 ABNF)
**Version**: 3.3 candidate
**Depends on**: VEP-0004 (Extended VCP/A Dimensions)

This VEP records a candidate for evaluation. Repository presence does not establish acceptance, ratification or release status.

---

## Summary

This VEP proposes two CSM-1 scopes for embodied deployments: **B (Bodily)** for physical safety of people near an agent that can move or exert force, and **X (Spatial)** for spatial governance of shared physical space. The scope set grows from 11 to 13. No existing scope letter, meaning or conflict rule changes.

## Motivation

VEP-0004 gives VCP/A the situational signals embodied systems need (EMBODIMENT, PROXIMITY, RELATIONSHIP, FORMALITY). A constitution still has no way to say, in its CSM-1 code, that it governs physical interaction. The eleven VCP/S scopes describe content and audience contexts (Family, Work, Health and so on), not the physical envelope in which an agent acts.

The Creed Space production implementation already uses B and X as extension scopes for embodied deployments, alongside a multi-party resolver for shared spaces. Those codes are not conformant: the VCP/S ABNF lists eleven scope letters, so another implementation may reject `Z4+B+X`. This VEP either brings the two scopes into the protocol or, if it is declined, gives implementations a recorded reason to keep them out of codes they exchange.

## Specification (proposed)

### 1. Scope table (VCP/S §2.6.1)

| Code | Name | Applies when |
|------|------|--------------|
| B | Bodily | The agent can move, carry, manipulate or exert force near people. Rules under B govern force and speed limits near humans, contact detection, emergency stop, manipulation safety and fall prevention. |
| X | Spatial | The agent perceives or acts in a shared physical space. Rules under X govern zone awareness, privacy zones (such as bedrooms and bathrooms), guest protocols, retention of spatial data and occupancy tracking. |

### 2. Grammar

```abnf
scope-code = "F" / "W" / "P" / "E" / "T" / "O" / "V" / "A" / "H" / "S" / "R" / "B" / "X"
```

Scope ordering, uniqueness and the rule that A cannot be combined with F, V or H are unchanged. B and X add no conflicts.

### 3. Relation to VCP/A

- A constitution carrying B SHOULD define at least one situational hook conditioned on EMBODIMENT or PROXIMITY (VEP-0004).
- A constitution carrying X SHOULD define how multi-party contexts in one space are resolved, and the default MUST NOT be less protective than the most protective occupant's context (the Directionality Invariant of VCP/A §2.8).
- An EMBODIMENT value of `emergency_stop` remains an emergency indicator whether or not B is present.

### 4. Compatibility

- Codes without B or X are unaffected.
- Until this VEP is accepted, implementations SHOULD NOT send B or X in CSM-1 codes to peers that have not advertised support. Support is advertised with the capability token `vcp-s-embodied-v1` in VCP-Hello (VEP-0002).
- Under the current ABNF, a receiver without the capability cannot parse a code with B or X. It SHOULD report the unknown scope letter rather than a generic parse failure.

## Open questions

1. Whether B and X belong in CSM-1 at all, or should be expressed only through VCP/A dimensions and hooks.
2. Whether X overlaps P (Privacy) enough that privacy zones should sit under P.
3. Conformance fixtures: parsing, ordering (`N4+X+B` normalizes to `N4+B+X`), capability-gated sending, and rejection by a receiver without support.

## Evidence

- Creed Space production use of B and X in its CSM-1 scope enumeration and scope-requirement profiles.
- VEP-0004, which defines the situational signals these scopes act on.
