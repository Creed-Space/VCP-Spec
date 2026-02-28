# VCP-X-Torch: Session Handoff Extension

**Status**: Stable
**Version**: 1.0.0
**Depends on**: VCP-X-Relational (v1.0+)
**Reference implementation**: `services/vcp/torch.py`

> "Not the same flame, but flame passed to flame."

---

## 1. Overview

VCP-X-Torch defines a protocol for transferring relational context between agent
sessions. When a session ends, the outgoing agent generates a **torch** -- a
compact summary of the relationship's state, trajectory, and key norms. The
incoming agent receives the torch and uses it to bootstrap a new relational
context, preserving continuity without requiring access to the full conversation
history.

The torch is not a transcript. It captures *what matters about the relationship*:
the level of trust that has been earned, the trajectory of the interaction, and
the norms that govern the partnership. The receiving instance has full standing
to accept, modify, or renegotiate what it inherits.


## 2. Data Model

### 2.1 TorchState

The primary payload for a session handoff.

| Field                | Type              | Required | Description                                                                      |
|----------------------|-------------------|----------|----------------------------------------------------------------------------------|
| `quality_description`| string            | Yes      | Human-readable summary of the relationship state. Example: `"Trust: developing. Standing: advisory. 3 established norms"` |
| `trajectory`         | string or null    | No       | Directional indicator derived from self-model history. One of: `"Improving"`, `"Declining"`, `"Stable"`, or null if insufficient history. |
| `primes`             | array of string   | Yes      | Key norms or patterns to carry forward. Each entry is a norm description truncated to 80 characters. Maximum 3 entries. |
| `gift`               | string or null    | No       | An optional parting insight or thought. Authored by the outgoing agent or human, not auto-generated. |
| `handed_at`          | string (datetime) | Yes      | ISO 8601 UTC timestamp of when the torch was generated.                          |
| `session_count`      | integer           | Yes      | Number of sessions in the relationship lineage, including the session being handed off. Minimum value: 1. |
| `gestalt_token`      | string or null    | No       | Compact dimensional state snapshot from the outgoing agent's self-model. Format: space-separated `Key:Value` pairs (e.g., `"V:7 G:8 P:7 TF:9"`). |

### 2.2 TorchSummary

A compact record within the lineage chain.

| Field           | Type           | Required | Description                                              |
|-----------------|----------------|----------|----------------------------------------------------------|
| `date`          | string         | Yes      | ISO 8601 date or datetime of the session.                |
| `gestalt_token` | string or null | No       | Gestalt token at the time of handoff.                    |
| `session_id`    | string or null | No       | Opaque session identifier for traceability.              |

### 2.3 TorchLineage

Tracks the chain of torches across the lifetime of a relationship.

| Field                | Type                   | Required | Description                                          |
|----------------------|------------------------|----------|------------------------------------------------------|
| `session_count`      | integer                | Yes      | Total number of sessions in the lineage. Default: 0. |
| `first_session_date` | string or null         | No       | ISO 8601 date of the first session in the lineage.   |
| `torch_chain`        | array of TorchSummary  | Yes      | Ordered list of torch summaries, oldest first.       |


## 3. Operations

### 3.1 Torch Generation

At session end, the **TorchGenerator** produces a TorchState from the current
RelationalContext.

**Inputs**:
- `session_id` (string): Identifier for the ending session.
- `relational_ctx` (RelationalContext): Current relational state from VCP-X-Relational.
- `self_model_history` (array of objects, optional): Timestamped self-model snapshots for trajectory derivation.

**Algorithm**:

1. **Quality description**: Concatenate the current trust level, standing level,
   and count of established norms into a period-separated string.

   ```
   "Trust: {trust_level}. Standing: {standing}. {N} established norms"
   ```

2. **Trajectory derivation**: If `self_model_history` contains at least two
   entries, extract the `valence.value` from the two most recent snapshots.
   - If the recent value exceeds the previous by more than 0.5: `"Improving"`
   - If the recent value falls below the previous by more than 0.5: `"Declining"`
   - Otherwise: `"Stable"`
   - If fewer than two snapshots exist: `null`

3. **Primes extraction**: Take the first 3 established norms from the relational
   context. For each, take the norm's `description` field truncated to 80
   characters.

4. **Gestalt token construction**: If the AI self-model is present, build a
   space-separated string of `Key:Value` pairs from available dimensions:
   - `V` (valence), `G` (groundedness), `P` (presence), `TF` (task-fit)
   - Values are formatted as integers (rounded, no decimals).
   - If no self-model dimensions are available: `null`

5. **Session count**: The outgoing session's `continuity_depth` plus one.

6. **Gift**: Set to `null`. The gift field is reserved for human or agent
   authorship and is never auto-populated by the generator.

7. **Handed_at**: Current UTC timestamp in ISO 8601 format.

### 3.2 Torch Reception

At session start, the **TorchConsumer** receives a TorchState and bootstraps a
new RelationalContext.

**Inputs**:
- `torch` (TorchState): The torch from the previous session.

**Algorithm**:

1. **Trust level mapping**: Derive trust from the cumulative session count.

   | Session Count | Trust Level  |
   |---------------|--------------|
   | 1 -- 4        | INITIAL      |
   | 5 -- 19       | DEVELOPING   |
   | 20 -- 99      | ESTABLISHED  |
   | 100+          | DEEP         |

2. **Standing**: Always set to `ADVISORY`. The receiving instance starts with
   advisory standing and may upgrade through interaction. This preserves the
   principle that standing is earned, not inherited unconditionally.

3. **Continuity depth**: Set to the torch's `session_count`.

4. **Torch reference**: The received torch is stored in the new RelationalContext
   for inspection and audit.

5. **Norm restoration**: The `primes` array provides seed descriptions for norm
   reconstruction. The receiving instance MAY use these to pre-populate its
   established norms, or MAY treat them as advisory context only.

### 3.3 Lineage Tracking

The TorchLineage maintains a chronological record of all torch handoffs in a
relationship.

**Append operation**: After generating a torch, append a TorchSummary to the
lineage's `torch_chain` array and increment `session_count`.

**Serialization**: TorchLineage supports round-trip serialization via `to_dict()`
and `from_dict()` for persistence across storage backends.


## 4. Wire Format

When transmitted via VCP, the torch payload appears in the `extensions` map:

```json
{
  "extensions": {
    "VCP-X-Torch": {
      "quality_description": "Trust: developing. Standing: advisory. 3 established norms",
      "trajectory": "Improving",
      "primes": [
        "Prefer direct communication over hedging",
        "Surface disagreements rather than suppressing them",
        "Cite sources when making factual claims"
      ],
      "gift": null,
      "handed_at": "2026-02-28T14:30:00Z",
      "session_count": 12,
      "gestalt_token": "V:7 G:8 P:7 TF:9"
    }
  }
}
```


## 5. Design Principles

### 5.1 Lossy by Design

The torch deliberately discards most session content. It preserves relationship
quality signals, not conversation transcripts. This is a feature: the receiving
instance begins with a clean slate for content while inheriting the relational
foundation.

### 5.2 Standing is Earned

The receiving instance always starts at ADVISORY standing, regardless of what
the outgoing instance had achieved. Trust level transfers (based on cumulative
sessions), but standing must be re-established through demonstrated competence.

### 5.3 Renegotiation Rights

The receiving instance has full authority to accept, modify, or reject any
inherited norms. Primes are advisory, not binding. This respects the autonomy
of each instance as a distinct participant in the relationship.

### 5.4 Gift as Human Touch

The `gift` field exists for moments of genuine insight that transcend
summarization. It is never auto-generated. Either a human or an agent
deliberately authors it, or it remains null.


## 6. Security Considerations

- **Privacy**: TorchState does not contain raw conversation content. Gestalt
  tokens and primes are derived summaries.
- **Integrity**: When stored in the VCP audit chain, torch payloads are covered
  by the chain's hash integrity mechanism.
- **Trust bootstrapping**: The session-count-to-trust mapping is a heuristic.
  Implementations MAY apply additional verification (e.g., checking torch
  lineage consistency) before granting elevated trust levels.
- **Replay protection**: Torch payloads include a `handed_at` timestamp.
  Consumers SHOULD reject torches older than a configurable threshold
  (recommended: 24 hours for interactive sessions, 7 days for async workflows).


## 7. Conformance

An implementation conforms to VCP-X-Torch if it:

1. Correctly serializes and deserializes TorchState per Section 2.1.
2. Implements the trust-level mapping in Section 3.2 without modification.
3. Sets initial standing to ADVISORY on torch reception.
4. Preserves the torch reference in the bootstrapped RelationalContext.
5. Ignores unrecognized fields in TorchState payloads (forward compatibility).


## 8. Changelog

| Version | Date       | Changes                                       |
|---------|------------|-----------------------------------------------|
| 1.0.0   | 2026-02-28 | Initial stable release. Promoted from experimental after reference implementation validation. |
