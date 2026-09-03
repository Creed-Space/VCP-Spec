# Version and Compatibility Policy

<!-- vcp-document-control
status: Current candidate compatibility policy
normative-authority: Cross-repository release policy
protocol-version: VCP 3.1 baseline with v3.2 amendments pre-release
last-reviewed: 2026-08-14 active authority and evidence boundary
owner: VCP Spec maintainers
evidence-boundary: Declared compatibility and required evidence, not hosted or registry proof
-->

VCP uses separate version domains. A package release number does not declare a
new protocol release.

| Surface | Current repository status | Compatibility meaning |
|:---|:---|:---|
| Core specification | v3.1 source baseline | Mutable source reference; immutable normative release remains open |
| v3.2 amendments | Pre-release | Candidate behavior requiring governance approval |
| VEP-0004 | Experimental | Extended VCP/A dimensions, not promoted by SDK support |
| Python SDK | 4.2.0, `value-context-protocol` | SDK semver, implements v3.2 candidate features |
| Rust SDK | 4.2.0 workspace, `vcp-core` | SDK semver, implements v3.2 candidate features |
| WebMCP SDK | 4.2.0, `@creedspace/vcp-sdk` | Browser integration, not a full TypeScript protocol implementation |
| Demo | 0.1.0 application | Demonstration release, not conformance evidence |

## Compatibility rules

1. Normative protocol changes require the VEP process and an explicit protocol
   release decision.
2. SDK patch and minor releases may repair implementation defects without
   changing the wire protocol. Fail-closed security changes still require a
   documented migration impact.
3. Experimental extensions and amendments must be capability-negotiated and
   identified as experimental in user-facing output.
4. Conformance is established by shared vectors against an exact Spec and SDK
   commit pair. A green build in one repository is insufficient.
5. Release notes must state both the package version and supported protocol
   baseline.

The cross-repository release owner should update this table whenever any package
or protocol version changes.
