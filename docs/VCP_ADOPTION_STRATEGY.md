# VCP Adoption and Standards Gates

<!-- vcp-document-control
status: Current strategy
normative-authority: None
protocol-version: VCP 3.1
last-reviewed: 2026-08-13 status and authority classification
owner: VCP project leadership
evidence-boundary: Adoption gates only
-->

| Field | Value |
|:---|:---|
| Status | Current non-normative strategy |
| Normative authority | None |
| Protocol baseline | VCP 3.1 |
| Last reviewed | 2026-08-13 |
| Owner | VCP project leadership |
| Evidence boundary | Entry criteria for outreach, publication, and standards work |

## Principle

Adoption claims follow evidence. Outreach starts with a clearly versioned,
source-installable candidate and expands only as independent evidence appears.
Named organizations, frameworks, researchers, or standards bodies are never
described as participants until they have agreed publicly or in an authorized
record.

## Milestones

| Milestone | Entry evidence | Public claim allowed |
|:---|:---|:---|
| A. Reviewable source | Current docs, exact source commits, passing local checks, explicit human gates | Experimental source candidate |
| B. Immutable candidate | Hosted CI, inspected package artifacts, SBOMs, manifest, security review ledger | Release candidate for named profiles |
| C. First public release | Ratified names, rights approval, trusted publisher, registry receipts, production smoke | Published packages at exact versions |
| D. Independent interop | Separately maintained implementation passes mandatory profile suites | Independent interoperability for that profile |
| E. Governance maturity | Constituted membership, quorum, decisions, conflicts, minutes, appeals | Community-governed project within the recorded scope |
| F. Standards submission | Current draft, submission rights, acknowledgements, technical and security review | Submitted Internet-Draft or other precise standards status |

## IETF path

An Internet-Draft is a temporary working document. Submission does not make it
an RFC or an IETF standard. RFC 2026 states that Proposed Standard normally does
not require implementation or operational experience. Advancement to Internet
Standard requires significant implementation and successful operational
experience. The project therefore values independent implementations as strong
engineering evidence while avoiding the false claim that two are a universal
precondition for Proposed Standard.

Before resubmission, the expired draft requires:

1. reconciliation with VCP 3.1, candidate amendments, and accepted VEPs;
2. a clear four-core-layer scope or complete treatment of all claimed layers;
3. validated security, privacy, registry, and IANA considerations;
4. IETF Trust and BCP 78 rights review;
5. complete contributor acknowledgements and submission authority;
6. current `idnits` or Datatracker validation;
7. an explicit intended status and standards venue strategy.

## Ecosystem outreach

Outreach materials include a one-page architecture summary, executable source
quick start, machine-readable compatibility and conformance reports, threat
model, privacy boundary, and migration story. Integrations begin as small,
reversible experiments against one named version. Their maintainers decide
whether and how VCP fits their architecture.

High-cost commitments such as a new foundation, certification programme, or
trademark licensing scheme wait for governance and legal authority. Repository
text cannot create acceptance by an external foundation or standards body.

## Evidence review cadence

The status page is regenerated for every candidate. Time-sensitive external
claims are checked against primary sources before publication. A scheduled
compatibility watcher reports upstream MCP and WebMCP changes, but human review
decides whether any change alters VCP.
