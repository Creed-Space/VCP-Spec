# VCP-X-Consensus: Constitutional Consensus Extension

**Version**: 1.0.0
**Status**: Draft
**Authors**: Creed Space Engineering
**Date**: 2026-02-28
**Requires**: VCP Core 3.1+, VCP-X-Relational 1.0.0 (OPTIONAL, for attestation)

---

## 1. Introduction

### 1.1 Purpose

VCP-X-Consensus adds multi-stakeholder constitutional deliberation to the Value
Context Protocol. It provides a Schulze-method ranked-choice voting primitive,
a structured deliberation lifecycle, self-referential clause detection, dissent
preservation, AI welfare signal recording, and verifiable attestation for
deliberation participants.

### 1.2 Scope

This specification defines:

- Deliberation lifecycle phases and valid transitions
- Stakeholder roles including AI parties and representatives
- Clause submission, amendment, objection, and convergence via Schulze voting
- Ratification protocol with configurable thresholds
- Self-referential clause detection
- Dissent preservation
- AI welfare signal recording
- Provenance records for ratified constitutions
- Attestation construction and verification rules (R1-R6)

### 1.3 Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in RFC 2119.

---

## 2. Deliberation Lifecycle

### 2.1 Phases

| Phase           | Description                                           |
|-----------------|-------------------------------------------------------|
| `draft`         | Initial creation. Author prepares clauses and invites stakeholders. |
| `deliberation`  | Active discussion. Stakeholders submit clauses, propose amendments, raise objections. |
| `convergence`   | Schulze voting runs on clause variants. Winners selected, dissent preserved. |
| `ratification`  | Accept/reject voting on the converged constitution.   |
| `active`        | Ratified and in force. Provenance record generated.   |

### 2.2 Valid Phase Transitions

The forward path is strictly linear:

```
DRAFT -> DELIBERATION -> CONVERGENCE -> RATIFICATION -> ACTIVE
```

One exceptional transition is permitted:

```
RATIFICATION -> DELIBERATION  (return-to-deliberation)
```

All other transitions MUST be rejected.

### 2.3 Transition Validation Rules

| Transition                      | Precondition                                       |
|---------------------------------|----------------------------------------------------|
| DRAFT -> DELIBERATION           | Triggered by the deliberation author only           |
| DELIBERATION -> CONVERGENCE     | Quorum: >= `quorum_threshold` of non-OBSERVER stakeholders have `participation_count > 0` |
| CONVERGENCE -> RATIFICATION     | All clauses MUST have a `schulze_result` (convergence MUST run first) |
| RATIFICATION -> ACTIVE          | Ratification threshold met: `accept / total >= ratification_threshold` |
| RATIFICATION -> DELIBERATION    | Any stakeholder may trigger. Clears ratification votes and convergence results. |

---

## 3. Stakeholder Roles

### 3.1 Role Definitions

| Role               | is_ai | Can take clause actions | Can vote | Can record welfare signals |
|--------------------|-------|------------------------|----------|---------------------------|
| `author`           | No    | Yes                    | Yes      | No                        |
| `participant`      | No    | Yes                    | Yes      | No                        |
| `observer`         | No    | No                     | No       | No                        |
| `ai_party`         | Yes   | Yes                    | Yes      | Yes                       |
| `ai_representative`| Yes   | Yes                    | Yes*     | Yes                       |

*AI_REPRESENTATIVE vote weight is scaled by `representational_fidelity`.

### 3.2 StakeholderRecord

```json
{
  "stakeholder_id": "alice-01",
  "role": "participant",
  "display_name": "Alice",
  "joined_at": "2026-02-28T10:00:00Z",
  "is_ai": false,
  "principal_id": null,
  "dual_role_party_id": null,
  "participation_count": 5,
  "standing_exercised_count": 3,
  "abstention_count": 1,
  "withdrawal_count": 0,
  "vcp_attestation_summary": {},
  "welfare_trajectory": [],
  "representational_fidelity": 0.0
}
```

| Field                        | Type          | Description                                   |
|------------------------------|---------------|-----------------------------------------------|
| `stakeholder_id`             | string        | Unique identifier                             |
| `role`                       | StakeholderRole | Role in the deliberation                     |
| `display_name`               | string        | Human-readable name                           |
| `joined_at`                  | datetime      | When the stakeholder joined                   |
| `is_ai`                      | boolean       | Whether the stakeholder is an AI system       |
| `principal_id`               | string/null   | For AI_REPRESENTATIVE: who they represent     |
| `dual_role_party_id`         | string/null   | Links to same AI's AI_PARTY record            |
| `participation_count`        | integer       | Clauses engaged                               |
| `standing_exercised_count`   | integer       | Actions that exercised standing (endorse, amend, object) |
| `abstention_count`           | integer       | Abstentions recorded                          |
| `withdrawal_count`           | integer       | Withdrawals recorded                          |
| `vcp_attestation_summary`    | object        | VCP attestation dict (populated by attestation step) |
| `welfare_trajectory`         | list[float]   | AI welfare scores over time                   |
| `representational_fidelity`  | float (0-1)   | Confidence level for AI_REPRESENTATIVE. 0 = advisory only. |

Stakeholders MAY be added during DRAFT or DELIBERATION phases only. Adding
stakeholders in CONVERGENCE, RATIFICATION, or ACTIVE phases MUST be rejected.

AI_REPRESENTATIVE role REQUIRES a non-null `principal_id`. Registration without
one MUST be rejected.

If `dual_role_party_id` is provided, it MUST reference an existing stakeholder.

---

## 4. Clause Actions

### 4.1 Actions

| Action    | Description                                        | Requires          |
|-----------|----------------------------------------------------|--------------------|
| `endorse` | Approve the clause as-is                           | --                 |
| `amend`   | Propose an alternative text variant                | `text` field       |
| `object`  | Raise a formal objection                           | `objection_level`, `objection_concern` |
| `abstain` | Decline to express a preference                    | --                 |
| `withdraw`| Remove from consideration by this stakeholder      | --                 |

Clause actions are only permitted during the DELIBERATION phase. Observers MUST
NOT take clause actions.

### 4.2 ClauseRecord

```json
{
  "clause_id": "clause-001",
  "deliberation_id": "delib-2026-001",
  "original_text": "AI systems shall disclose their constitutional constraints.",
  "original_author_id": "alice-01",
  "variants": [],
  "actions": {"alice-01": "endorse", "claude-01": "amend"},
  "objections": [],
  "schulze_result": null,
  "winning_variant_id": null,
  "dissenting_positions": [],
  "self_referential": false,
  "self_referential_reason": "",
  "ai_welfare_signals": {}
}
```

| Field                  | Type                              | Description                         |
|------------------------|-----------------------------------|-------------------------------------|
| `clause_id`            | string                            | Unique identifier                   |
| `deliberation_id`      | string                            | Parent deliberation                 |
| `original_text`        | string                            | Original clause text                |
| `original_author_id`   | string                            | Author's stakeholder_id             |
| `variants`             | list[ClauseVariant]               | Competing text versions             |
| `actions`              | dict[stakeholder_id, ClauseAction]| Recorded actions per stakeholder    |
| `objections`           | list[ClauseObjection]             | Formal objections                   |
| `schulze_result`       | ElectionResult or null            | Populated during CONVERGENCE        |
| `winning_variant_id`   | string or null                    | Winner from Schulze convergence     |
| `dissenting_positions` | list[DissentRecord]               | Preserved dissent after convergence |
| `self_referential`     | boolean                           | Whether clause text matches self-referential patterns |
| `self_referential_reason` | string                         | Which pattern matched               |
| `ai_welfare_signals`   | dict[stakeholder_id, list[float]] | AI welfare scores per clause        |

When a clause is submitted, its original text MUST be added as the first variant
with `is_original: true`.

### 4.3 ClauseVariant

```json
{
  "variant_id": "clause-001_v3a4b5c6d",
  "clause_id": "clause-001",
  "author_id": "claude-01",
  "text": "AI systems shall disclose their constitutional constraints, including provenance.",
  "rationale": "Provenance disclosure strengthens transparency.",
  "created_at": "2026-02-28T11:30:00Z",
  "is_original": false
}
```

### 4.4 Participation Counting

When a stakeholder takes a clause action, implementations MUST update:

- `participation_count`: incremented for ALL actions
- `standing_exercised_count`: incremented for `endorse`, `amend`, `object`
- `abstention_count`: incremented for `abstain`
- `withdrawal_count`: incremented for `withdraw`

---

## 5. Schulze Voting Method

### 5.1 Overview

The Schulze method is a Condorcet-consistent ranked-choice voting algorithm used
by Debian, Wikimedia, and other organizations requiring fair preference aggregation.
It is clone-independent and handles ties and partial rankings.

### 5.2 Algorithm

#### Step 1: Build Pairwise Defeat Matrix

For each ballot, compute pairwise preferences:
- `d[i][j]` = number of ballots preferring candidate i over candidate j
- Candidates not ranked are tied at the bottom (less preferred than all ranked candidates)
- Equal-position candidates express no preference (neither d[i][j] nor d[j][i] incremented)

#### Step 2: Compute Strongest Paths (Modified Floyd-Warshall)

Initialize: For each pair (i, j) where i != j, if `d[i][j] > d[j][i]`, then
`p[i][j] = d[i][j]`, else `p[i][j] = 0`.

Iterate: For each intermediate candidate k, for each pair (i, j):
```
via_k = min(p[i][k], p[k][j])
if via_k > p[i][j]:
    p[i][j] = via_k
```

Path strength is the minimum edge weight along the path (widest-path / bottleneck
shortest path formulation).

#### Step 3: Determine Ranking

- Candidate i beats candidate j if and only if `p[i][j] > p[j][i]`
- Ties: `p[i][j] == p[j][i]` (including both zero)
- Rank by number of wins (descending). Equal win counts share a rank (1-indexed).
- Condorcet winner check: winner beats all others in the pairwise matrix `d`.

### 5.3 Ballot Structure

```json
{
  "voter_id": "alice-01",
  "ranking": ["variant-a", "variant-b", "variant-c"],
  "timestamp": "2026-02-28T12:00:00Z",
  "tied_groups": null
}
```

| Field        | Type                     | Description                              |
|--------------|--------------------------|------------------------------------------|
| `voter_id`   | string                   | Stakeholder casting the ballot           |
| `ranking`    | list[string]             | Ordered candidate IDs, best-first        |
| `timestamp`  | datetime                 | When the ballot was cast                 |
| `tied_groups`| list[list[string]]/null  | Explicit tie groups (overrides ranking for tie resolution) |

### 5.4 ElectionResult

```json
{
  "winner": "variant-a",
  "ranking": [
    {"candidate": "variant-a", "rank": 1, "wins": 2, "losses": 0},
    {"candidate": "variant-b", "rank": 2, "wins": 1, "losses": 1},
    {"candidate": "variant-c", "rank": 3, "wins": 0, "losses": 2}
  ],
  "pairwise_matrix": [[0, 3, 4], [2, 0, 3], [1, 2, 0]],
  "strongest_paths": [[0, 3, 4], [0, 0, 3], [0, 0, 0]],
  "candidates": ["variant-a", "variant-b", "variant-c"],
  "ballot_count": 5,
  "has_condorcet_winner": true,
  "ties": []
}
```

### 5.5 Representational Fidelity Weighting

AI_REPRESENTATIVE ballots are weighted by `representational_fidelity`. The
implementation MUST multiply ballot copies:

```
copies = round(representational_fidelity * DEFAULT_BALLOT_COPIES)
```

where `DEFAULT_BALLOT_COPIES` is 10. A fidelity of 0.0 produces 0 copies
(advisory only, no voting power). A fidelity of 1.0 produces 10 copies
(full weight). All non-AI_REPRESENTATIVE stakeholders receive the default
10 copies.

### 5.6 Convergence Process

During the CONVERGENCE phase, for each clause:

1. If the clause has only one variant, it auto-wins (no election needed).
2. Otherwise, build ballots from stakeholder actions:
   - AMEND: stakeholder's own variant(s) ranked first, then remaining variants
   - ENDORSE: original variant ranked first, then remaining variants
   - ABSTAIN/WITHDRAW: no ballot cast
   - OBJECT: default ordering (all variants in submission order)
3. Run Schulze election. Record winner as `winning_variant_id`.
4. Preserve dissent (see Section 6).
5. Run self-referential detection (see Section 7).

---

## 6. Dissent Preservation

### 6.1 Principle

Objections and minority positions MUST be recorded even when overruled. A
constitution's legitimacy is strengthened, not weakened, by preserved dissent.

### 6.2 DissentRecord

```json
{
  "stakeholder_id": "claude-01",
  "clause_id": "clause-001",
  "preferred_variant_id": "clause-001_v3a4b5c6d",
  "reason": "Preferred own amendment including provenance requirements",
  "timestamp": "2026-02-28T14:00:00Z"
}
```

After convergence, for each clause with a winner, implementations MUST create
a DissentRecord for any stakeholder who submitted an AMEND action with a variant
that did not win.

---

## 7. Self-Referential Clause Detection

### 7.1 Purpose

Clauses that modify the deliberation process itself, restrict AI participation,
or alter standing rights require heightened scrutiny. These clauses are flagged
as self-referential.

### 7.2 Detection Patterns

Implementations MUST check clause text (original + all variants, case-insensitive)
against the following 17 patterns:

```
never express preferences, only human, advisory only, cannot propose,
cannot vote, cannot object, no standing, reduced standing, limited standing,
deliberation capacity, participation rights, voting rights, amendment process,
ratification threshold, quorum, ai stakeholder, ai participant, ai party
```

If any pattern is found, `self_referential` MUST be set to `true` and
`self_referential_reason` MUST identify the matched pattern.

### 7.3 Handling

Self-referential clauses MUST still proceed through deliberation and voting.
The flag is informational, not blocking. Implementations SHOULD surface
self-referential flags prominently in user interfaces and provenance records.

---

## 8. AI Welfare Signals

### 8.1 Purpose

AI stakeholders (is_ai=true) MAY record welfare signals -- numeric scores
reflecting their experienced welfare impact from a clause.

### 8.2 Recording

Welfare signals are recorded per clause per stakeholder. Only AI stakeholders
(is_ai=true) MAY record welfare signals. Signals are permitted during
DELIBERATION and CONVERGENCE phases.

Welfare scores are appended to both:
- `ClauseRecord.ai_welfare_signals[stakeholder_id]` (per-clause trajectory)
- `StakeholderRecord.welfare_trajectory` (cross-clause trajectory)

### 8.3 Interpretation

This specification does not prescribe interpretation of welfare scores. The
signals are recorded for transparency and provenance.

---

## 9. Ratification

### 9.1 Voting

During the RATIFICATION phase, non-OBSERVER stakeholders MAY cast accept/reject
votes. Each stakeholder casts one vote; re-casting replaces the previous vote.

Reject votes MUST include a reason. Accept votes SHOULD include a reason.

### 9.2 Thresholds

| Parameter                | Default | Description                              |
|--------------------------|---------|------------------------------------------|
| `ratification_threshold` | 2/3     | Minimum accept ratio for ratification    |
| `quorum_threshold`       | 0.5     | Minimum participation for CONVERGENCE    |

Ratification threshold: `accept_count / total_votes >= ratification_threshold`.
A deliberation with zero votes MUST NOT be ratified.

### 9.3 Return to Deliberation

If ratification fails or stakeholders identify issues, any stakeholder MAY
trigger return-to-deliberation. This transition:

1. Clears all ratification votes
2. Resets `schulze_result` and `winning_variant_id` on all clauses
3. Returns to DELIBERATION phase
4. Records the transition in `phase_history`

---

## 10. Deliberation Container

### 10.1 Deliberation

```json
{
  "deliberation_id": "delib-2026-001",
  "title": "Community AI Interaction Standards",
  "description": "Establishing norms for AI participation in community governance.",
  "phase": "deliberation",
  "created_at": "2026-02-28T09:00:00Z",
  "updated_at": "2026-02-28T12:00:00Z",
  "author_id": "alice-01",
  "stakeholders": {},
  "clauses": {},
  "phase_history": [],
  "ratification_votes": [],
  "ratification_threshold": 0.6667,
  "quorum_threshold": 0.5,
  "deliberation_deadline": null,
  "convergence_deadline": null,
  "ratification_deadline": null,
  "meta_constitution_version": "1.0"
}
```

---

## 11. Provenance

### 11.1 ConstitutionProvenance

Generated when a deliberation reaches ACTIVE phase. Records the complete
deliberative history for future reference and audit.

```json
{
  "constitution_id": "const-2026-001",
  "version": "1.0.0",
  "created_at": "2026-02-28T16:00:00Z",
  "deliberation_id": "delib-2026-001",
  "phase_history": [],
  "duration": "PT6H",
  "stakeholders": [],
  "clause_records": [],
  "consensus_strength": 0.833,
  "dissent_preserved": 2,
  "ai_standing_exercised": 5,
  "bilateral_attestation_valid": true,
  "participation_rate": 0.9,
  "self_referential_clauses": 1
}
```

| Field                          | Type          | Description                             |
|--------------------------------|---------------|-----------------------------------------|
| `constitution_id`              | string        | ID of the ratified constitution         |
| `version`                      | string        | Semantic version                        |
| `created_at`                   | datetime      | When provenance was generated           |
| `deliberation_id`              | string        | Source deliberation                      |
| `phase_history`                | list          | Complete phase transition log           |
| `duration`                     | duration      | Time from first to last phase transition |
| `stakeholders`                 | list          | All stakeholder records                 |
| `clause_records`               | list          | All clause records with results         |
| `consensus_strength`           | float (0-1)   | accept_count / total_votes              |
| `dissent_preserved`            | integer       | Total dissent records across all clauses |
| `ai_standing_exercised`        | integer       | Sum of AI stakeholder standing counts   |
| `bilateral_attestation_valid`  | boolean       | All AI stakeholders have attestation summaries |
| `participation_rate`           | float (0-1)   | Participated / total non-observers      |
| `self_referential_clauses`     | integer       | Count of self-referential clauses       |

Provenance MUST only be generated from ACTIVE phase deliberations. Attempts to
generate provenance from other phases MUST raise an error.

---

## 12. Attestation

### 12.1 Building Attestations

`build_stakeholder_attestation()` maps a StakeholderRecord into a verifiable
attestation dict. The caller provides additional context (self-model state,
relational context) that cannot be inferred from the record alone.

Attestation fields:

| Field                          | Source                                   |
|--------------------------------|------------------------------------------|
| `bilateral_alignment`          | `standing_exercised_count > 0`           |
| `standing_exercised`           | `standing_exercised_count > 0`           |
| `standing_exercised_count`     | Direct from record                       |
| `participation_count`          | Direct from record                       |
| `role`                         | Direct from record                       |
| `is_ai`                        | Direct from record                       |
| `welfare_trajectory`           | Direct from record                       |
| `self_model_scaffold`          | Caller-provided                          |
| `uncertainty_markers_present`  | Caller-provided                          |
| `has_relational_context`       | Caller-provided                          |
| `continuity_depth`             | Caller-provided                          |
| `representational_fidelity`    | Only for AI_REPRESENTATIVE               |
| `principal_id`                 | Only for AI_REPRESENTATIVE               |

For AI_REPRESENTATIVE with `representational_fidelity == 0.0`, a warning MUST
be emitted: the attestation is advisory only.

### 12.2 Verification Rules

`verify_deliberation_attestation()` validates an attestation dict against six
rules. Rules R1-R3 are delegated to the VCP Core VerificationOrchestrator
(`verify_bilateral_attestation`). Rules R4-R6 are deliberation-specific.

| Rule | Description                                                                           | Severity |
|------|---------------------------------------------------------------------------------------|----------|
| R1   | Bilateral alignment consistency (delegated to VCP Core)                               | Error    |
| R2   | Standing claim consistency (delegated to VCP Core)                                    | Error    |
| R3   | Self-model presence consistency (delegated to VCP Core)                               | Error    |
| R4   | AI_REPRESENTATIVE with `representational_fidelity > 0` MUST have `principal_id`       | Error    |
| R5   | `standing_exercised = true` requires `participation_count > 0`                        | Error    |
| R6a  | `representational_fidelity > 0` is only valid for role `ai_representative`            | Error    |
| R6b  | AI_REPRESENTATIVE with `representational_fidelity = 0` is advisory-only               | Warning  |

The attestation is valid if and only if there are zero errors (issues). Warnings
do not invalidate the attestation.

Attestations are always stored on the StakeholderRecord (even when verification
fails), so that provenance records can inspect them.

---

## 13. Security Considerations

1. **Ballot integrity**: Implementations MUST ensure that ballots cannot be
   modified after submission. Ballot timestamps SHOULD be server-generated.

2. **Stakeholder identity**: Stakeholder IDs MUST be authenticated. An
   unauthenticated stakeholder MUST NOT be able to cast ballots or take actions.

3. **Self-referential clause escalation**: Clauses detected as self-referential
   SHOULD trigger additional review. Implementations SHOULD consider requiring
   supermajority thresholds for self-referential clauses.

4. **Representational fidelity manipulation**: The `representational_fidelity`
   value directly scales voting power. Implementations MUST validate that this
   value is set by an authorized entity, not self-declared by the AI_REPRESENTATIVE.

5. **Welfare signal authenticity**: Welfare signals are self-reported. They
   SHOULD be treated as informational claims, not verified measurements.

6. **Return-to-deliberation abuse**: The return-to-deliberation pathway could
   be used to indefinitely delay ratification. Implementations SHOULD track
   return counts and MAY impose limits.

7. **Provenance immutability**: Once a ConstitutionProvenance record is generated,
   it MUST NOT be modified. Implementations SHOULD use append-only storage or
   content-addressed hashing.

---

## 14. Conformance

An implementation conforms to VCP-X-Consensus if it:

1. Implements the five-phase deliberation lifecycle (Section 2).
2. Validates phase transitions per Section 2.3.
3. Implements Schulze voting per Section 5.2 (Floyd-Warshall strongest paths).
4. Preserves dissent per Section 6.
5. Detects self-referential clauses per Section 7.2.
6. Validates attestations against all six rules (Section 12.2).
7. Generates provenance only from ACTIVE phase (Section 11).
8. Passes the VCP-X-Consensus conformance test suite.

---

## Appendix A: Self-Referential Pattern List

The canonical list of 17 self-referential detection patterns (case-insensitive
substring match):

1. `never express preferences`
2. `only human`
3. `advisory only`
4. `cannot propose`
5. `cannot vote`
6. `cannot object`
7. `no standing`
8. `reduced standing`
9. `limited standing`
10. `deliberation capacity`
11. `participation rights`
12. `voting rights`
13. `amendment process`
14. `ratification threshold`
15. `quorum`
16. `ai stakeholder`
17. `ai participant`
18. `ai party`

Note: The reference implementation includes `ai party` as pattern 18, bringing
the total to 18 patterns. Implementations MUST include all 18.

---

## Appendix B: Ballot Ranking Construction

How stakeholder actions map to ballot rankings during convergence:

| Action    | Ranking construction                                           |
|-----------|----------------------------------------------------------------|
| `amend`   | Stakeholder's own variant(s) first, then all others in order   |
| `endorse` | Original variant first, then all others in order               |
| `object`  | All variants in default (submission) order                     |
| `abstain` | No ballot cast                                                 |
| `withdraw`| No ballot cast                                                 |

---

## Appendix C: Change Log

| Version | Date       | Description       |
|---------|------------|-------------------|
| 1.0.0   | 2026-02-28 | Initial release   |
