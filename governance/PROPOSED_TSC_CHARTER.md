# Proposed Technical Steering Committee charter

**Status:** proposal only. Unratified. No current operational or legal effect.

This preserved charter describes a possible future governance model for the
Value-Context Protocol. The Technical Steering Committee described below has
not been constituted, no neutral-governance or foundation transfer is claimed,
and the intellectual-property and trademark provisions require authorized legal
review. Current authority is recorded in [`../GOVERNANCE.md`](../GOVERNANCE.md)
and [`authority.json`](./authority.json).

---

## 1. Technical Steering Committee (TSC)

### 1.1 Purpose

The Technical Steering Committee is the primary decision-making body for the VCP
specification. The TSC is responsible for:

- Approving specification changes via the VEP process
- Setting the technical direction and roadmap
- Managing extension lifecycle (EXPERIMENTAL, STABLE, DEPRECATED)
- Resolving disputes between contributors
- Maintaining the integrity and coherence of the protocol

### 1.2 Composition

The TSC consists of 3 to 7 members drawn from protocol stakeholders:

| Seat type       | Count   | Selection method                     |
|-----------------|---------|--------------------------------------|
| Founding        | 1       | Nell Watson (founding chair)         |
| Creed Space     | 1-2     | Appointed by Creed Space             |
| Community       | 1-4     | Nominated and elected (see 1.5)      |

The proposed initial TSC would be:

| Name             | Role      | Affiliation   | Term expires   |
|------------------|-----------|---------------|----------------|
| Nell Watson      | Chair     | Creed Space   | Founding       |
| (TBD)            | Secretary | Creed Space   | Year 1         |
| (TBD)            | Member    | Community     | Year 2         |

Community seats are filled as the contributor base grows. The TSC SHOULD reach
5 members within 12 months of the first published specification version.

### 1.3 Roles

**Chair.** Sets meeting agendas. Facilitates discussion. Casts the tie-breaking
vote when consensus cannot be reached. The founding chair serves without term
limit; successor chairs are elected by the TSC for 2-year terms.

**Secretary.** Records meeting minutes. Publishes minutes to the repository
within 7 days. Tracks VEP status and numbering. Maintains the governance
calendar.

**Members.** Participate in discussion and voting. Review VEPs. Represent the
interests of the stakeholder community they were drawn from.

### 1.4 Terms

- Founding chair: no term limit (may step down voluntarily)
- All other seats: 2-year terms, staggered so no more than half expire in any
  calendar year
- Members MAY serve consecutive terms
- Members MAY resign at any time by written notice to the TSC

### 1.5 Community seat elections

Community seats are filled by the following process:

1. The TSC opens a nomination period of at least 14 days
2. Any person who has authored a merged PR or filed a VEP in the preceding
   12 months is eligible for nomination (self-nomination permitted)
3. Nominees submit a brief statement (500 words max) describing their
   interest and relevant experience
4. The TSC votes by simple majority to fill the seat
5. In case of a tie, the chair casts the deciding vote

### 1.6 Removal

A TSC member may be removed by a supermajority (2/3) vote of the remaining
members for:

- Sustained inactivity (missing 3 consecutive meetings without notice)
- Conduct violations as defined in CODE_OF_CONDUCT.md
- Actions that materially harm the protocol or its community

The member in question is given an opportunity to respond before the vote.

---

## 2. Decision process

### 2.1 Consensus model

The TSC operates by **lazy consensus**: a proposal is considered approved if no
TSC member objects within the defined review period. Silence is assent.

When a member objects, the TSC moves to a formal vote:

| Decision type             | Threshold                    | Minimum discussion |
|---------------------------|------------------------------|--------------------|
| Specification change      | Supermajority (2/3 of TSC)   | 14 days            |
| Breaking change           | Supermajority (2/3 of TSC)   | 21 days            |
| Process / governance      | Simple majority              | 7 days             |
| Extension status change   | Simple majority              | 7 days             |
| Typo / editorial fix      | 1 TSC member approval        | None               |

### 2.2 Meetings

- The TSC meets monthly via video call
- Meeting times rotate to accommodate global time zones
- Minutes are published to `docs/tsc-minutes/` within 7 days
- Meetings are open to observers; speaking rights reserved for TSC members
  and invited presenters
- Quorum requires a simple majority of seated members

### 2.3 Asynchronous decisions

Decisions MAY be made asynchronously on GitHub issues labeled `tsc-vote`.
The same thresholds and discussion periods apply. A decision is recorded when
the required number of TSC members have voted and the discussion period has
elapsed.

---

## 3. VCP Enhancement Proposals (VEPs)

Significant specification changes follow the VEP process. This ensures that
changes are well-motivated, thoroughly discussed, and properly documented.

### 3.1 What requires a VEP

- Any change to the normative specification text
- Addition, modification, or removal of a protocol layer
- New or modified JSON Schema definitions
- New VCP-X extensions
- Breaking changes to the wire format
- Changes to the conformance test requirements

The following do NOT require a VEP:

- Typo and editorial fixes
- Non-normative clarifications
- SDK-only enhancements that do not change the protocol
- Documentation improvements

### 3.2 Lifecycle

```
DRAFT --> PROPOSED --> ACCEPTED --> IMPLEMENTED --> RELEASED
                  \-> REVISED --/       |
                  \-> DECLINED          |
                                   WITHDRAWN
```

**DRAFT.** The author opens a GitHub issue using the VEP template. The issue
describes the proposed change, its motivation, backward-compatibility impact,
and security considerations. The author MAY include a draft PR.

**PROPOSED.** A TSC member reviews the draft for completeness and assigns a VEP
number (VEP-0001, VEP-0002, etc.). The issue is labeled `vep` and
`status:proposed`. A minimum 14-day discussion period begins. Breaking changes
require 21 days.

**ACCEPTED.** After the discussion period, the TSC votes. If accepted, the
issue is labeled `status:accepted`. The author (or another contributor) proceeds
to implementation.

**REVISED.** The TSC requests changes before acceptance. The author updates the
proposal and discussion resumes. A REVISED proposal returns to PROPOSED status
for a new discussion period (minimum 7 days for revisions).

**DECLINED.** The TSC declines the proposal with a recorded rationale. Declined
VEPs MAY be reopened if circumstances change.

**IMPLEMENTED.** A pull request is submitted and merged that includes:

- Updated specification text in `specs/`
- Updated JSON Schema in `schemas/`
- Reference implementation demonstrating the feature
- Conformance tests validating the feature
- Migration notes if the change affects existing implementations

**RELEASED.** The implemented VEP is included in a published specification
version. The issue is closed and labeled `status:released`.

**WITHDRAWN.** The author may withdraw a VEP at any stage before RELEASED.

### 3.3 VEP numbering

VEPs are numbered sequentially starting from VEP-0001. Numbers are never reused,
even if a VEP is declined or withdrawn.

---

## 4. Extension governance

VCP-X extensions allow the protocol to grow without bloating the core
specification.

### 4.1 Extension lifecycle

```
EXPERIMENTAL --> STABLE --> DEPRECATED --> REMOVED
```

**EXPERIMENTAL.** The extension has been accepted via VEP and merged, but is
subject to breaking changes. Implementations SHOULD support it but MUST NOT
depend on its stability. Minimum 6 months before promotion.

**STABLE.** The extension has proven its value and the TSC has voted to stabilize
it. Breaking changes now require a VEP with the "breaking change" threshold.
Minimum 12 months before deprecation.

**DEPRECATED.** The TSC has decided to phase out the extension. Implementations
SHOULD continue to support it for at least 12 months. A deprecation notice and
migration path MUST be published.

**REMOVED.** The extension is no longer part of the specification. Removed
extensions remain in the repository's `archive/` directory for reference.

### 4.2 Extension requirements

Every VCP-X extension MUST include:

| Artifact                | Location                        | Required |
|-------------------------|---------------------------------|----------|
| Specification           | `specs/extensions/<name>.md`    | Yes      |
| JSON Schema             | `schemas/extensions/<name>.json`| Yes      |
| Reference implementation| Linked from spec                | Yes      |
| Conformance tests       | `tests/extensions/<name>/`      | Yes      |
| Security considerations | Section in spec                 | Yes      |

### 4.3 Extension maintainers

Each extension has a designated maintainer responsible for:

- Responding to issues within 14 days
- Reviewing PRs related to the extension
- Proposing lifecycle transitions to the TSC

If a maintainer becomes inactive for 90 days, the TSC MAY appoint a replacement.

---

## 5. Contributor license

### 5.1 Developer Certificate of Origin (DCO)

VCP uses the [Developer Certificate of Origin](https://developercertificate.org/)
(DCO), the same mechanism used by the Linux kernel and many other open source
projects.

Every commit MUST include a `Signed-off-by` line:

```
Signed-off-by: Jane Smith <jane@example.com>
```

By adding this line, you certify that:

1. The contribution was created in whole or in part by you, and you have the
   right to submit it under the project's open source license; or
2. The contribution is based upon previous work that, to the best of your
   knowledge, is covered under an appropriate open source license and you have
   the right to submit that work with modifications; or
3. The contribution was provided directly to you by some other person who
   certified (1) or (2) and you have not modified it.

VCP does NOT require a Contributor License Agreement (CLA). The DCO provides
equivalent legal clarity with less friction.

### 5.2 License

All specification text, schemas, and reference implementations are licensed
under the MIT License. See [LICENSE](../LICENSE).

---

## 6. Intellectual property and foundation transfer

### 6.1 Grant to the Agentic AI Foundation

Creed Space grants the Agentic AI Foundation a perpetual, irrevocable,
worldwide, royalty-free, non-exclusive license to use, reproduce, modify, and
distribute the VCP specification, schemas, and reference implementations,
including the right to sublicense, under the terms of the MIT License.

This grant covers all contributions made prior to and after the foundation
transfer date. It is effective upon the Foundation's formal acceptance of
stewardship.

### 6.2 Contributor IP

All contributions made under the DCO are licensed under the same MIT License.
Contributors retain copyright to their individual contributions.

---

## 7. Trademark policy

### 7.1 Ownership

"Value-Context Protocol" and "VCP" are trademarks of Creed Space.

### 7.2 Permitted use without approval

Conformant implementations MAY use the following without prior permission:

- "VCP-compatible"
- "Supports VCP"
- "Built on VCP"

These terms indicate that the implementation follows the published specification
but do not imply endorsement by Creed Space or the TSC.

### 7.3 Use requiring approval

The following require passing the official conformance test suite AND TSC
approval:

- "VCP Certified"
- The VCP logo or certification mark
- Any representation of official endorsement

### 7.4 Foundation trademark license

Upon formal transfer of stewardship to the Agentic AI Foundation, Creed Space
grants the Foundation a perpetual, royalty-free license to use, manage, and
sublicense the VCP trademarks in connection with the protocol and its ecosystem.

### 7.5 Prohibited use

The VCP name and trademarks MUST NOT be used:

- To imply endorsement of unrelated products or services
- In a manner that is misleading or deceptive
- In connection with products that violate the Code of Conduct

---

## 8. Neutrality

The Value-Context Protocol is developed in the open under neutral governance.
No single organization controls the protocol's direction. The TSC represents
diverse stakeholder interests including protocol implementors, AI providers,
and end users.

Decisions are made on technical merit, ecosystem benefit, and alignment with
the protocol's mission of transparent, ethical value communication in AI
systems. Commercial interests are welcome but do not receive preferential
treatment in the specification process.

---

## 9. Amendments

This governance document may be amended through the VEP process. Amendments
require a TSC supermajority (2/3) vote and a minimum 14-day discussion period.

The following provisions require unanimous TSC consent to amend:

- Section 5 (Contributor license -- DCO requirement)
- Section 6 (IP and foundation transfer)
- Section 8 (Neutrality statement)

---

## 10. Definitions

| Term            | Meaning                                                    |
|-----------------|------------------------------------------------------------|
| TSC             | Technical Steering Committee                               |
| VEP             | VCP Enhancement Proposal                                   |
| DCO             | Developer Certificate of Origin                            |
| Lazy consensus  | Approved unless a member objects within the review period   |
| Simple majority | More than half of seated TSC members                       |
| Supermajority   | At least two-thirds of seated TSC members                  |
| Quorum          | Simple majority of seated TSC members present              |
| Normative       | Text that defines required behavior (uses RFC 2119 terms)  |

---

*This proposal would become effective only through a recorded ratification by
authorized participants. Repository presence and merge history do not ratify it.*
