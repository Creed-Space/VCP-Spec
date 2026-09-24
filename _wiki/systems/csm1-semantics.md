# CSM-1 Semantics Layer

<!-- wiki:type = system -->
<!-- wiki:scope = vcp-spec -->
<!-- wiki:created = 2026-05-23 -->
<!-- wiki:updated = 2026-09-24 -->
<!-- wiki:status = active -->

## Summary

VCP/S (Semantics, Layer 3) defines how values are encoded in machine-readable form. It encodes constitutional configurations as CSM-1 (Constitutional Safety Minicode). A CSM-1 code packs persona, adherence level, scopes, namespace and version into one line, and CSM-1 v1.1 adds a multi-line token that carries constitutional and personal state. (specs/VCP_SEMANTICS_v2.0.md §2.1, §2.4)

## CSM-1 code and token

A CSM-1 code is one line: persona, adherence level, then optional scopes, namespace and version.

Example: `N5+F+E`
- `N` — persona code (Nanny)
- `5` — adherence level (0-5)
- `+F+E` — scopes (Family, Education)

(VCP-SDK/CLAUDE.md, "Quick Reference" table.) The canonical form sorts scopes, so this code serializes as `N5+E+F`. (specs/VCP_SEMANTICS_v2.0.md §2.10.1)

A CSM-1 token is the multi-line v1.1 form: seven required lines (`VCP:`, `C:`, `P:`, `G:`, `X:`, `F:`, `S:`), then an optional `R:` personal-state line and optional extension lines. (specs/VCP_SEMANTICS_v2.0.md §2.4)

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

- Sources consulted: VCP-Spec/README.md, VCP-SDK/CLAUDE.md, specs/VCP_SEMANTICS_v2.0.md
- Last verified against sources: 2026-05-23; the CSM-1 summary and the code and token section rechecked against specs/VCP_SEMANTICS_v2.0.md on 2026-09-24

## See Also

- [[vcp-spec:systems/itsame-architecture]] — full layer stack context
- [[vcp-spec:domain/extension-model]] — extensions that add to semantics (VCP-X-Personal, VCP-X-Relational)
- [[shared:vcp]] — cross-project VCP concept page
