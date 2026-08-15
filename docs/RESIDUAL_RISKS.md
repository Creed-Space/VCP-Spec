# VCP residual-risk register

<!-- vcp-document-control
status: Current open-risk summary
normative-authority: Risk tracking only
protocol-version: VCP 3.1 source baseline and current candidate ecosystem
last-reviewed: 2026-08-15
owner: VCP Spec maintainers
evidence-boundary: Open risks and closure roles, not acceptance or closure authority
-->

The canonical machine-readable register is
[`status/residual-risks.json`](../status/residual-risks.json). It separates
source mitigations from the human-authority, independent-evidence, and
operational evidence required to close each risk.

| Risk | Severity | State | Closure role |
|:---|:---|:---|:---|
| Governance authority | Critical | Open authority | Authorized project principals |
| Rights and licensing | Critical | Open authority | Rights counsel and project principals |
| Independent protocol and safety review | Critical | Open independent | Independent reviewers and release authority |
| Welfare consent and harm | Critical | Open independent | Welfare review body and protocol authority |
| Package registry ownership and provenance | High | Open authority | Release authority and registry owners |
| Live-provider operations, privacy, and cost | High | Open operations | Service, privacy, and finance owners |
| Independent interoperability | High | Open independent | Independent implementer and conformance authority |
| Human accessibility and media rights | High | Open independent | Accessibility reviewer and rights authority |

Risk closure requires the exact evidence named in the JSON register. A local
test, source patch, or self-review cannot close an entry assigned to another
authority or an independent reviewer.

## Working signal

The register is working when public release decisions cite an exact register
digest, open entries remain visible in publication state, closure records name
their authority and evidence, and no source change silently converts an open
risk to accepted or closed.
