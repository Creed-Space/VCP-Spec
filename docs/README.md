# VCP Documentation Index

<!-- vcp-document-control
status: Current index
normative-authority: Index only
protocol-version: VCP 3.1
last-reviewed: 2026-08-13 status and authority classification
owner: VCP Spec maintainers
evidence-boundary: Navigation and classification only
-->

| Field | Value |
|:---|:---|
| Status | Current index |
| Normative authority | Index only. Normative requirements live in accepted specifications and schemas. |
| Protocol baseline | VCP 3.1 |
| Last reviewed | 2026-08-13 |
| Owner | VCP Spec maintainers |
| Evidence boundary | Navigation and document classification, not implementation conformance |

## Start here

1. [Current overview](./VCP_OVERVIEW.md)
2. [Newcomer guide](./VCP_NEWCOMER_GUIDE.md)
3. [Source integration guide](./VCP_INTEGRATION_GUIDE.md)
4. [Ecosystem status](./ECOSYSTEM_STATUS.md)
5. [Document control](./DOCUMENT_CONTROL.md)
6. [Conformance claim vocabulary](./CONFORMANCE_CLAIMS.md)

These pages describe the current source candidate. The root
[publication-state record](../status/publication-state.json) is the machine
authority for artifact availability. It currently permits source installs only.

## Normative protocol material

| Surface | Current authority | Status |
|:---|:---|:---|
| Protocol baseline | [VCP 3.1](../specs/VCP_SPECIFICATION_v3.1.md) | Published repository baseline |
| Candidate amendments | [VEP-0004 extended VCP/A dimensions](../veps/VEP-0004-extended-vcpa-dimensions.md) | Experimental, pre-release candidate |
| Enhancement proposals | [VEP index](../veps/README.md) | Per-VEP status |
| Machine contracts | [JSON Schemas](../schemas/) | Versioned beside specifications |
| Internet-Draft source | [Expired working copy](../specs/draft-watson-vcp-00.md) | Withdrawn from publication readiness |

Repository labels such as published baseline describe document maturity inside
this repository. They do not establish IETF status, independent review,
certification, or registry publication.

## Protocol companions

- [Identity](./identity/VCP_IDENTITY_NAMING.md)
- [Transport and source integration](./VCP_INTEGRATION_GUIDE.md)
- [Semantics and CSM-1](./semantics/VCP_SEMANTICS_CSM1.md)
- [Adaptation](./adaptation/VCP_ADAPTATION.md)
- [Context](./context/VCP_CONTEXT_SPECIFICATION.md)
- [OpenAPI actions](./openapi/vcp_actions.yaml)

Companion documents explain or elaborate the normative material. If a
companion conflicts with an accepted specification or schema, the accepted
specification and schema control.

## Project and release records

- [Current work register](./VCP_NEAR_TERM_TODOS.md)
- [Adoption gates](./VCP_ADOPTION_STRATEGY.md)
- [Unratified package identifiers](./VCP_PACKAGE_NAMING.md)
- [Rendered artifact status](./RENDERED_ARTIFACT_STATUS.md)
- [Compatibility policy](../COMPATIBILITY.md)
- [Release checklist](../RELEASE_CHECKLIST.md)
- [Governance](../GOVERNANCE.md), currently interim and unratified

Historical host integration and audit evidence lives under
[`archives/`](../archives/). Archived material preserves provenance and has no
current normative or operational authority.
