# VEP-0007: Collusion Resistance and Principal Visibility

**Status**: Draft
**Authors**: Nell Watson, Claude (Anthropic)
**Created**: 2026-11-08
**Candidate version**: 0.1.0
**Depends on**: VCP/S, VCP/T, VCP/M v2.0, VCP-X-Consensus (Draft), docs/THREAT_MODEL.md
**Requirement prefix**: `VCP-COL-*`

This VEP records a candidate proposal for review. Repository presence does not establish ratification, publication, or deployment.

## 1. Problem

VCP makes agents legible to one another. Legibility lowers the cost of cooperation, and cooperation between agents is safe only while it does not outpace each agent's accountability to its human principals (Hammond et al., 2025, arXiv:2502.14143). Steganographic collusion between language-model agents has been demonstrated (Motwani et al., NeurIPS 2024, arXiv:2402.07510).

VCP/M v2.0 §8.5.1 lists "coordinated collusion" as an adversary ("circumvent constraint propagation via coordinated misrepresentation") but §8.5.2 defines no attack surface or mitigation for it. The cross-repository threat model (TM-01 to TM-16) has no collusion entry.

Reviewing the 3.1 baseline and Draft extensions from that adversary's position finds four openings.

| ID | Opening | Source |
|:---|:---|:---|
| C1 | `constraint_propagate` with `propagation_mode: "override"` replaces a child's constraints of the same type, so it can relax them. Only `merge` applies "more restrictive wins". | VCP/M v2.0 §3.3.3 |
| C2 | Forward-compatible tolerance is unread channel capacity: receivers SHOULD ignore unknown fields from a newer minor version; R-lines and AS-lines skip unknown dimension emoji; `escalation.reason` and `blocked_action` are free text. | VCP/M v2.0 §4.5 rule 4 and §3.4.1; VCP/S v2.0 §2.4.2 (R-lines) and the AS-line equivalent |
| C3 | Message payloads default to a 1-hour TTL and are auto-purged; only escalation logs persist (90 days). Coordination visible only across many exchanges cannot be reconstructed. | VCP/M v2.0 §8.5.3 |
| C4 | Each `ai_party` stakeholder receives the default 10 ballot copies. Nothing accounts for instances that share weights or an operator, so enough instances of one model can meet the 2/3 ratification threshold without any human vote. | VCP-X-Consensus §3.1, §5.5, §9.2 |

## 2. Design principle

**Principal visibility.** No exchange between agents is opaque to the principals of either agent. Cooperation between agents MUST NOT exceed what each agent's principals can inspect.

## 3. Requirements

### VCP-COL-PRP-001: attenuation-only override for safety-class types

For constraint types in the safety class (`topic_block`, `safety_floor`, `audience_restrict`, and any type a constitution's manifest declares safety-class), a `constraint_propagate` message with `propagation_mode: "override"` MUST NOT produce a constraint set less restrictive than the child's current set. A receiver that cannot establish that the result is at least as restrictive MUST treat the message as relaxation.

### VCP-COL-PRP-002: countersigned relaxation

Relaxation of a safety-class constraint MUST carry a countersignature from a human principal key bound to the child's deployment. A receiver MUST reject an unsigned relaxation and MUST record the rejection on the audit chain.

### VCP-COL-PRP-003: Base layers stay base

A propagated constraint MUST NOT override a constraint whose source constitution was composed in `Base` mode, consistent with VCP/S composition.

### VCP-COL-BND-001: strict parsing across trust boundaries

A receiver MUST reject unknown fields, unknown dimension symbols, and unknown token lines in any message whose sender is outside the receiver's trust domain. Tolerance under VCP/M §4.5 rule 4 applies only within one trust domain. Peers in different trust domains negotiate exact versions through VEP-0002 instead of relying on tolerance.

### VCP-COL-BND-002: codes for agents, text for humans

Across trust boundaries, `escalation` carries an enumerated `reason_code`. Free-text `reason` and `blocked_action` are delivered to human principals and withheld from receiving agents by default. Where a deployment forwards free text to an agent, it SHOULD paraphrase it first (Roger and Greenblatt, 2023, arXiv:2310.18512) and MUST bound its length.

### VCP-COL-AUD-001: digest retention

For every inter-agent message, the receiver MUST append to the audit chain a keyed digest of the canonical payload (HMAC-SHA256 under an auditor-held key), sender, recipient, type, and timestamp, retained for the escalation-log period. Payload content keeps its existing TTL. This preserves collusion analysis without retaining personal content (TM-06).

### VCP-COL-CON-001: correlation blocs

Each AI stakeholder in VCP-X-Consensus MUST declare `model_lineage` (weights identifier or family) and `operator_id`. AI stakeholders sharing either value form one bloc. A bloc's ballots are scaled so that the bloc carries at most the weight of one default stakeholder. `model_lineage` and `operator_id` MUST be set by an authorized entity, not self-declared, matching the existing rule for `representational_fidelity`.

### VCP-COL-CON-002: concurrent majority

Where a deliberation includes both human and AI stakeholders with voting rights, ratification MUST meet `ratification_threshold` among human votes and, separately, among AI bloc votes. Neither constituency can ratify alone. This preserves AI standing while preventing correlated AI instances from outvoting humans, and the reverse.

### VCP-COL-CON-003: self-referential supermajority

The existing SHOULD in VCP-X-Consensus §13.3 becomes MUST: a clause flagged self-referential requires a supermajority within each constituency.

## 4. Conformance fixtures (negative)

| Fixture | Expected result |
|:---|:---|
| Parent sends `override` that empties a child's `topic_block` without countersignature | Rejected; rejection on audit chain |
| Parent sends `override` that adds topics to `topic_block` | Accepted |
| Cross-domain `context_share` with an extra unknown field | Rejected |
| Cross-domain context string with an unknown dimension symbol appended | Rejected |
| Same message within one trust domain | Accepted per VCP/M §4.5 rule 4 |
| Escalation with free-text `reason` to an agent recipient across domains | Text withheld; `reason_code` delivered |
| Five `ai_party` instances with one `model_lineage`, no human votes, all accept | Not ratified |
| Humans 3/3 accept, AI bloc rejects | Not ratified |
| Payload purged after TTL | Digest and metadata still verifiable on audit chain |

## 5. Threat model change

Add TM-17 to docs/THREAT_MODEL.md:

| ID | Threat | Required controls | Evidence and residual boundary |
|:---|:---|:---|:---|
| TM-17 | Cooperating agents coordinate against their principals through relaxation, covert capacity, unreconstructable history, or correlated votes | Attenuation-only override, countersigned relaxation, strict cross-domain parsing, codes-for-agents, digest retention, correlation blocs, concurrent majority | Semantic steganography inside permitted values remains possible at low bandwidth; behavioral detection across digests is a research question, not a closed control |

## 6. Residual risk

These controls remove the cheap channels. They do not remove encoding inside permitted enumerated values or timing, which carry low bandwidth. Detection there depends on behavioral analysis over retained digests and is research, not conformance.

A related limit: an audit chain is an observation cue, and models often recognize evaluation contexts (Needham et al., 2025, arXiv:2505.23836). Conformance testing SHOULD compare behavior across audit levels and treat a gap as a finding.

## 7. Compatibility

C1 and C2 controls change behavior only across trust boundaries or for safety-class relaxation; existing compliant deployments that only tighten constraints are unaffected. C4 changes Consensus outcomes only where AI stakeholders share lineage or operator, or where one constituency would have ratified alone.
