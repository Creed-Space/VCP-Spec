# CSM-1 Semantics Layer

<!-- wiki:type = system -->
<!-- wiki:scope = vcp-spec -->
<!-- wiki:created = 2026-05-23 -->
<!-- wiki:updated = 2026-05-23 -->
<!-- wiki:status = active -->

## Summary

VCP/S (Semantics, Layer 3) defines how values are encoded as machine-readable tokens. The primary encoding format is CSM-1 (Creed Structured Model 1), a compact grammar for expressing constitutional personas, behavioral dimensions, and value constraints. (VCP-SDK/CLAUDE.md, "Quick Reference")

## CSM-1 Token Format

A CSM-1 token encodes a persona and its value dimensions in compact form.

Example: `N5+F+E`
- `N` — persona code (NANNY)
- `5` — adherence level
- `+F+E` — domain flags (Family, Education)

(VCP-SDK/CLAUDE.md, "Quick Reference" table)

Additional examples from the VCP-Spec README (README.md, "Quick Start"):
```python
token.csm1  # e.g. csm1:supportive_companion:EH-TH-...
```

## Key Concepts

**UVC Token** (Universal Value Code): addresses a specific constitution by URI. Example: `family.safe.guide@1.2.0` — namespaced, versioned reference. (VCP-SDK/CLAUDE.md, "Quick Reference")

**Bundle**: signed envelope containing `{manifest, content, signature}`. The unit of transport in VCP/T. (VCP-SDK/CLAUDE.md, "Quick Reference")

**Context encoding**: situational context encoded compactly, e.g. `⏰🌅|📍🏡|👥👶` (time/morning, location/home, people/children). (VCP-SDK/CLAUDE.md, "Quick Reference")

## Spec Documents for This Layer

From VCP-Spec (README.md, "By Layer — VCP/S"):
- `docs/content/CSM1_GRAMMAR_SPECIFICATION.md` — grammar rules
- `docs/semantics/VCP_SEMANTICS_COMPOSITION.md` — persona composition

Full layer spec: `specs/VCP_SEMANTICS_v2.0.md`

## Implementation

In VCP-SDK: `python/src/vcp/semantics/` directory. (VCP-SDK directory listing)

Also referenced in Rewind codebase: `services/vcp/semantics/csm1.py` (Rewind git status, modified file). ([[rewind:systems/safety-stack]] for context on how Rewind uses CSM-1)

## Provenance

- Sources consulted: VCP-Spec/README.md, VCP-SDK/CLAUDE.md
- Last verified against sources: 2026-05-23

## See Also

- [[vcp-spec:systems/itsame-architecture]] — full layer stack context
- [[vcp-spec:domain/extension-model]] — extensions that add to semantics (VCP-X-Personal, VCP-X-Relational)
- [[shared:vcp]] — cross-project VCP concept page
