# VCP-Spec Wiki Log

## [2026-05-23] lint-fix | Remove stale UNVERIFIED markers for VCP-X-Welfare
Files fixed: domain/extension-model.md, systems/itsame-architecture.md
Issues resolved:
- Both pages carried [UNVERIFIED] for VCP-X-Welfare from the bootstrap pass. The expand pass read specs/extensions/VCP-X-Welfare/spec.md (logged in expand entry) and documented findings in itsame-layers-detail.md, but failed to update extension-model.md and itsame-architecture.md. Now corrected with citation to spec.md v1.0.0: EXPERIMENTAL status, embodied welfare instrumentation scope.
- Extension count in itsame-architecture.md updated from "Five" to "Six" to match actual directory.
- Provenance sections of both files updated to include specs/extensions/VCP-X-Welfare/spec.md.

## [2026-05-23] bootstrap | Initial wiki creation
Pages created: systems/itsame-architecture, systems/csm1-semantics, domain/extension-model
Sources ingested: VCP-Spec/README.md, VCP-SDK/CLAUDE.md (for SDK-side perspective on CSM-1)
Note: VCP-Spec is a Spec repo — no dedicated page-type taxonomy in SCHEMA.md. Product taxonomy (systems, domain) adopted as closest fit; this choice is provisional and should be reviewed if the schema gains a Spec category.
Note: VCP-X-Welfare extension directory exists (specs/extensions/VCP-X-Welfare/) but spec was not read — marked [UNVERIFIED] in extension-model.md.

## [2026-05-23] expand | 4 additional pages covering VEPs, capability negotiation, security, layer detail
Pages created: systems/vep-specs, systems/capability-negotiation, systems/security-model, systems/itsame-layers-detail
Sources ingested: veps/VEP-0001-extension-model.md, veps/VEP-0002-capability-negotiation.md, veps/VEP-0003-mcp-bridge.md, veps/VEP-0004-extended-vcpa-dimensions.md, specs/core/capability-negotiation.md, specs/core/security.md, specs/VCP_SPECIFICATION_v3.1.md, specs/extensions/VCP-X-Personal/spec.md, specs/extensions/VCP-X-Relational/spec.md, specs/extensions/VCP-X-Torch/spec.md, specs/extensions/VCP-X-Consensus/spec.md, specs/extensions/VCP-X-Welfare/spec.md, specs/extensions/README.md
Key findings: VCP-X-Welfare now read (EXPERIMENTAL, embodied welfare for robotics); VEP-0004 Experimental adds 4 VCP/A dimensions; torch gestalt_token format documented; AI self-model uncertainty requirement (? is load-bearing); Fernet encryption fail-closed in production; 12 injection scan patterns; 5 extension status states documented
