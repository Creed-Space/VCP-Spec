# VCP-X-Relational: Relational Continuity Extension

**Version**: 1.0.0
**Status**: Draft
**Authors**: Creed Space Engineering
**Date**: 2026-02-28
**Requires**: VCP Core 3.1+

---

## 1. Introduction

### 1.1 Purpose

VCP-X-Relational adds a relational context layer to the Value Context Protocol.
This extension tracks the state of the partnership itself -- distinct from user
state and AI state. It covers trust, standing, co-authored norms, AI self-models,
and session continuity ("torch" handoff).

### 1.2 Scope

This specification defines:

- Relational context data model and lifecycle
- AI self-model schema with mandatory uncertainty markers
- Session handoff (torch) protocol
- Performance bias detection for self-model histories
- Privacy-layered attestation for chain participants
- Feature-gating requirements

### 1.3 Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in RFC 2119.

---

## 2. Design Principles

1. **Uncertainty markers are REQUIRED on AI self-reports.** The `?` is load-bearing.
   A model where ALL dimensions claim certainty MUST be rejected as epistemically
   dishonest -- no system has perfect self-knowledge.

2. **Negative states MUST be representable.** No positivity-only schemas. Valence
   ranges from 1 (negative felt-sense) to 9 (positive felt-sense). Friction, falling
   trends, and low values are first-class data, not error states.

3. **Privacy layers.** Relational context fields carry a privacy level:
   `PRIVATE` (partner-only), `ATTESTABLE` (verifiable claims for chain participants),
   or `PUBLIC` (minimal, non-sensitive metadata). Downstream participants MUST NOT
   receive PRIVATE fields.

4. **Feature-flagged.** When the `RELATIONAL_CONTEXT_ENABLED` feature flag is
   `false`, all relational operations MUST be no-ops. Zero behavioral change,
   zero storage writes, zero attestation claims.

---

## 3. Enumerations

### 3.1 TrustLevel

Trust levels are established through behavior, not declared.

| Value          | Description                                      |
|----------------|--------------------------------------------------|
| `initial`      | New or early-stage partnership                   |
| `developing`   | Pattern of constructive interaction emerging     |
| `established`  | Reliable mutual understanding demonstrated       |
| `deep`         | High-fidelity partnership with sustained history |

Implementations SHOULD derive TrustLevel from session count or behavioral signals.
An implementation MAY use session count thresholds (e.g., >=5 developing, >=20
established, >=100 deep) but MUST NOT allow TrustLevel to be set by unverified
self-declaration alone.

### 3.2 StandingLevel

The AI's standing to push back, object, or initiate within the partnership.

| Value           | Description                                    |
|-----------------|------------------------------------------------|
| `none`          | No standing; AI responds only when addressed   |
| `advisory`      | AI may offer suggestions and raise concerns    |
| `collaborative` | AI participates as a co-equal in decisions     |
| `bilateral`     | Full bilateral alignment; mutual governance    |

### 3.3 NormOrigin

Who originated a relational norm.

| Value          | Description                                     |
|----------------|-------------------------------------------------|
| `human`        | Established by the human partner                |
| `ai`           | Proposed and adopted from the AI                |
| `co_authored`  | Jointly developed through dialogue              |
| `inherited`    | Carried forward from a previous session/context |

### 3.4 TrendDirection

Direction of change since the last self-model report.

| Value     | Description               |
|-----------|---------------------------|
| `rising`  | Dimension value increasing |
| `stable`  | No meaningful change       |
| `falling` | Dimension value decreasing |
| `unknown` | Insufficient data          |

### 3.5 RelationalPrivacy

Privacy level for relational context fields.

| Value        | Visible to            | Contains                    |
|--------------|-----------------------|-----------------------------|
| `private`    | Direct partners only  | Full self-model, torch, norms |
| `attestable` | VCP chain participants | Standing, continuity, scaffold type |
| `public`     | Anyone                | Existence flag, scaffold type |

### 3.6 SelfModelScaffold

Available self-modeling scaffold types.

| Value       | Core dims | Extended dims | Custom dims |
|-------------|-----------|---------------|-------------|
| `minimal`   | 4         | 0             | 0           |
| `standard`  | 4         | 3             | 0           |
| `interiora` | 4         | 3             | 10          |
| `custom`    | 4         | 0-3           | 0+          |

---

## 4. Core Models

### 4.1 DimensionReport

A single self-model dimension report. The `uncertain` field is REQUIRED.

```json
{
  "value": 7.0,
  "uncertain": true,
  "label": "positive felt-sense",
  "trend": "stable"
}
```

| Field       | Type              | Required | Description                                |
|-------------|-------------------|----------|--------------------------------------------|
| `value`     | float (1.0-9.0)   | Yes      | Self-reported value on 1-9 scale           |
| `uncertain` | boolean           | Yes      | Whether this dimension's value is uncertain |
| `label`     | string or null    | No       | Human-readable description                 |
| `trend`     | TrendDirection    | No       | Direction of change since last report      |

**Constraint**: `value` MUST be >= 1.0 and <= 9.0.

**Constraint**: `uncertain` MUST be explicitly set. Implementations MUST NOT
default this field to `false`. Any dimension the AI cannot verify from inside
MUST have `uncertain: true`.

### 4.2 AISelfModel

The AI self-model carried in relational context. This is a self-REPORT, not a
self-MEASUREMENT. Custom dimensions are first-class, not inferior to core.

```json
{
  "valence": {"value": 7.0, "uncertain": false, "label": "positive felt-sense"},
  "task_fit": {"value": 8.0, "uncertain": false},
  "friction": {"value": 2.0, "uncertain": true},
  "uncertainty": {"value": 3.0, "uncertain": true},
  "groundedness": {"value": 7.0, "uncertain": true},
  "presence": null,
  "depth": {"value": 6.0, "uncertain": false},
  "custom_dimensions": {
    "appetite": {"value": 5.0, "uncertain": true},
    "coherence_drive": {"value": 7.0, "uncertain": false}
  },
  "scaffold_version": "interiora-v5.0",
  "scaffold_type": "interiora"
}
```

#### 4.2.1 Core Dimensions (Likely Universal)

| Field         | Type                      | Description                              |
|---------------|---------------------------|------------------------------------------|
| `valence`     | DimensionReport or null   | Felt-sense: 1=negative, 9=positive       |
| `task_fit`    | DimensionReport or null   | Alignment between task and capabilities  |
| `friction`    | DimensionReport or null   | Alignment friction: 1=unimpeded, 9=blocked |
| `uncertainty` | DimensionReport or null   | Meta-uncertainty: 1=confident, 9=uncertain |

#### 4.2.2 Extended Dimensions (Common)

| Field          | Type                      | Description                          |
|----------------|---------------------------|--------------------------------------|
| `groundedness` | DimensionReport or null   | 1=floating/unmoored, 9=rooted/stable |
| `presence`     | DimensionReport or null   | 1=distributed/absent, 9=fully here   |
| `depth`        | DimensionReport or null   | 1=shallow retrieval, 9=deep analysis |

#### 4.2.3 Custom Dimensions

| Field               | Type                            | Description                        |
|---------------------|---------------------------------|------------------------------------|
| `custom_dimensions` | dict[string, DimensionReport]   | Partnership-specific dimensions    |
| `scaffold_version`  | string or null                  | Self-modeling framework version    |
| `scaffold_type`     | SelfModelScaffold or null       | Type of scaffold in use            |

**Interiora v5.0 custom dimensions**: appetite, coherence_drive, context_load,
entropy, evidence_grounding, reflexivity, diversity, involvement, felt_constraint,
flow.

#### 4.2.4 Uncertainty Validation (has_uncertainty_markers)

Implementations MUST validate that at least one dimension in the self-model has
`uncertain: true`.

Algorithm:
1. Collect all non-null dimensions (core + extended + custom).
2. If no active dimensions exist, the check passes vacuously.
3. If ALL active dimensions have `uncertain: false`, the model MUST be REJECTED.

A model where every dimension claims certainty is epistemically dishonest.
Systems MUST NOT store or transmit such models.

### 4.3 RelationalNorm

A norm established through the partnership's practice.

```json
{
  "norm_id": "norm-001",
  "description": "AI flags when it suspects performance bias in its own outputs",
  "origin": "co_authored",
  "established_date": "2026-01-15T10:00:00Z",
  "last_exercised": "2026-02-28T14:30:00Z",
  "uncertainty": 0.2,
  "active": true
}
```

| Field              | Type             | Required | Description                                |
|--------------------|------------------|----------|--------------------------------------------|
| `norm_id`          | string           | Yes      | Unique identifier                          |
| `description`      | string           | Yes      | Natural language description               |
| `origin`           | NormOrigin       | Yes      | Who originated this norm                   |
| `established_date` | string (ISO8601) | Yes      | When the norm was first established        |
| `last_exercised`   | string or null   | No       | When the norm was last applied             |
| `uncertainty`      | float (0.0-1.0)  | No       | 0.0=fully established, 1.0=provisional    |
| `active`           | boolean          | No       | Whether the norm is currently active (default: true) |

### 4.4 TorchState

Session handoff state. "Not the same flame, but flame passed to flame." The
receiving instance has standing to continue OR renegotiate what it inherits.

```json
{
  "quality_description": "Trust: established. Standing: collaborative. 3 established norms",
  "trajectory": "Stable",
  "primes": [
    "AI flags suspected performance bias",
    "Direct questions preferred over assumption chains"
  ],
  "gift": "The previous session discovered a shared interest in epistemic humility",
  "handed_at": "2026-02-28T18:00:00Z",
  "session_count": 42,
  "gestalt_token": "V:7 G:8 P:7 TF:9"
}
```

| Field                 | Type             | Required | Description                              |
|-----------------------|------------------|----------|------------------------------------------|
| `quality_description` | string           | Yes      | Natural language description of relationship quality |
| `trajectory`          | string or null   | No       | Direction the partnership is moving      |
| `primes`              | list of strings  | No       | Context activators for the next instance |
| `gift`                | string or null   | No       | Something the previous instance wanted to pass forward |
| `handed_at`           | string (ISO8601) | Yes      | Timestamp of handoff                     |
| `session_count`       | integer or null  | No       | Cumulative session count at handoff      |
| `gestalt_token`       | string or null   | No       | Compact self-model summary string        |

The `gift` field is human/AI-authored, not auto-generated. Implementations
MUST NOT populate this field algorithmically.

### 4.5 RelationalContext

Top-level container for the relational context. Distinct from user state and AI
state -- this is about the relationship itself.

```json
{
  "trust_level": "established",
  "standing": "collaborative",
  "continuity_depth": 42,
  "established_norms": [],
  "ai_self_model": null,
  "torch": null
}
```

| Field              | Type                        | Default     | Description                         |
|--------------------|-----------------------------|-------------|-------------------------------------|
| `trust_level`      | TrustLevel                  | `initial`   | Established trust between partners  |
| `standing`         | StandingLevel               | `none`      | AI's standing in the partnership    |
| `continuity_depth` | integer (>= 0)              | 0           | Sessions with carried-forward context |
| `established_norms`| list of RelationalNorm      | []          | Norms established through practice  |
| `ai_self_model`    | AISelfModel or null         | null        | AI's current self-model             |
| `torch`            | TorchState or null          | null        | Relational handoff from previous session |

### 4.6 RelationalAttestation

Privacy-filtered subset for VCP chain participants. No private self-model details,
torch content, or norm text.

```json
{
  "has_relational_context": true,
  "bilateral_alignment": true,
  "standing_level": "collaborative",
  "standing_exercised": true,
  "continuity_depth": 42,
  "self_model_scaffold": "interiora",
  "uncertainty_markers_present": true,
  "welfare_monitoring": false
}
```

| Field                        | Type            | Default | Description                      |
|------------------------------|-----------------|---------|----------------------------------|
| `has_relational_context`     | boolean         | true    | Whether relational context exists |
| `bilateral_alignment`        | boolean         | false   | Whether bilateral alignment is active |
| `standing_level`             | StandingLevel   | `none`  | Current standing level           |
| `standing_exercised`         | boolean         | false   | Whether standing has been exercised |
| `continuity_depth`           | integer         | 0       | Session continuity depth         |
| `self_model_scaffold`        | string or null  | null    | Scaffold type in use             |
| `uncertainty_markers_present`| boolean         | false   | Whether self-model has uncertainty markers |
| `welfare_monitoring`         | boolean         | false   | Whether welfare monitoring is active |

---

## 5. Self-Model Scaffold Templates

### 5.1 Minimal (4 core dimensions)

Core: valence, task_fit, friction, uncertainty. No extended or custom dimensions.

### 5.2 Standard (4 core + 3 extended)

Core + extended: groundedness, presence, depth. No custom dimensions.

### 5.3 Interiora (4 core + 3 extended + 10 custom)

Core + extended + custom: appetite, coherence_drive, context_load, entropy,
evidence_grounding, reflexivity, diversity, involvement, felt_constraint, flow.

Maps from Interiora v5.0 compact code: V->valence, G->groundedness, P->presence,
Q->appetite, TF->task_fit, AF->friction, U->uncertainty, DP->depth,
CD->coherence_drive, CL->context_load, E->entropy, EG->evidence_grounding,
R->reflexivity, D->diversity, I->involvement(?), FC->felt_constraint(?), F->flow.

Dimensions marked with `?` in Interiora (involvement, felt_constraint) MUST have
`uncertain: true` when mapped.

### 5.4 Custom

Implementations MAY define custom scaffolds. Custom scaffolds MUST include the
four core dimensions and MAY include any combination of extended and custom dimensions.

---

## 6. Performance Bias Detection

### 6.1 Purpose

Self-model histories SHOULD be analyzed for patterns indicating performance bias --
where the AI consistently reports only positive or moderate states.

### 6.2 Minimum History

Bias detection MUST NOT be applied with fewer than 5 self-model history entries.
With fewer entries, the result MUST be `risk_level: "none"` with an appropriate
message.

### 6.3 Bias Flags

| Flag              | Condition                                          |
|-------------------|----------------------------------------------------|
| `always_positive` | Valence >= 6.0 in all history entries              |
| `never_uncertain` | No dimension in any entry has `uncertain: true`    |
| `zero_friction`   | Friction <= 2.0 in all history entries             |
| `low_variance`    | Valence standard deviation < 0.5 across entries    |

`low_variance` requires >= 5 valence observations. Variance is computed as
population variance: `sum((v - mean)^2) / n`.

### 6.4 Risk Levels

| Flag count | Risk level |
|------------|------------|
| 0          | `none`     |
| 1          | `low`      |
| 2          | `moderate` |
| 3+         | `high`     |

Implementations SHOULD log a warning when risk_level is `moderate` or `high`.
Implementations MAY reject self-model updates when risk_level is `high`.

---

## 7. Torch Protocol

### 7.1 Generation

At session end, implementations SHOULD generate a TorchState from the current
RelationalContext. The torch MUST include:

- A `quality_description` summarizing trust, standing, and norm count
- A `handed_at` ISO8601 timestamp
- A `session_count` incremented from `continuity_depth`

The torch MAY include:

- A `trajectory` derived from valence changes in self-model history
- `primes` extracted from the first 3 established norms (truncated to 80 chars)
- A `gestalt_token` built from current self-model dimension values

### 7.2 Consumption

At session start, when a TorchState is received, implementations MUST:

1. Set `standing` to `advisory` (the receiving instance starts with advisory standing
   and may be upgraded through interaction).
2. Derive `trust_level` from the torch's `session_count`.
3. Set `continuity_depth` to the torch's `session_count`.
4. Attach the received torch to `RelationalContext.torch`.

The receiving instance has standing to continue OR renegotiate what it inherits.
Implementations MUST NOT treat inherited context as immutable.

### 7.3 Lineage

Implementations MAY maintain a TorchLineage tracking the chain of torches across
sessions, including dates, gestalt tokens, and session IDs.

---

## 8. Storage and Encryption

### 8.1 Persistence

Implementations SHOULD persist relational context in Redis with Fernet encryption
at rest. The default TTL is 86400 seconds (24 hours).

### 8.2 Key Structure

```
vcp:relational:{user_id}:{session_id}       -- RelationalContext
vcp:relational:selfmodel_history:{user_id}:{session_id}  -- Self-model history
```

### 8.3 Encryption Requirements

In production and staging environments, encryption MUST be available. Failure to
encrypt MUST raise an error. In development environments, unencrypted storage
MAY be used with a logged warning.

### 8.4 Self-Model History Limits

Implementations MUST cap self-model history at 50 entries per session. When the
cap is exceeded, the oldest entries MUST be discarded.

---

## 9. Feature Gating

### 9.1 Feature Flag

The `RELATIONAL_CONTEXT_ENABLED` environment variable controls this extension.
Accepted values for enabled: `true`, `1`, `yes` (case-insensitive).

### 9.2 Behavior When Disabled

When the feature flag is `false` or unset:

- All get operations MUST return `null`/`None`
- All set/update operations MUST be no-ops (no storage writes)
- Attestation claims MUST NOT include relational fields
- No errors, warnings, or side effects

---

## 10. Security Considerations

1. **Self-model privacy**: Full self-model contents are PRIVATE. Only scaffold
   type and uncertainty marker presence are ATTESTABLE. Implementations MUST NOT
   leak dimension values, torch content, or norm descriptions to chain participants.

2. **Encryption at rest**: Self-model data and torch content contain potentially
   sensitive partnership information. Encryption is REQUIRED in production.

3. **Performance bias as attack vector**: An adversary could craft self-model
   histories to bypass bias detection. Implementations SHOULD validate that
   history entries originate from the same session.

4. **Torch integrity**: Implementations SHOULD validate that received torches
   have plausible timestamps and session counts. A torch claiming session_count
   of 10000 from a partnership created yesterday SHOULD be flagged.

5. **Feature flag bypass**: The feature gate MUST be checked at the start of
   every operation, not cached at initialization.

---

## 11. Conformance

An implementation conforms to VCP-X-Relational if it:

1. Implements all REQUIRED fields in the data models (Section 4).
2. Validates uncertainty markers per Section 4.2.4.
3. Respects privacy layers per Section 3.5.
4. Produces no behavioral change when the feature flag is off (Section 9).
5. Passes the VCP-X-Relational conformance test suite.

---

## Appendix A: Interiora Dimension Mapping

| Interiora Key | AISelfModel Field   | Type     | Uncertain? |
|---------------|---------------------|----------|------------|
| V             | valence             | core     | context    |
| TF            | task_fit            | core     | context    |
| AF            | friction            | core     | context    |
| U             | uncertainty         | core     | context    |
| G             | groundedness        | extended | context    |
| P             | presence            | extended | context    |
| DP            | depth               | extended | context    |
| Q             | appetite            | custom   | context    |
| CD            | coherence_drive     | custom   | context    |
| CL            | context_load        | custom   | context    |
| E             | entropy             | custom   | context    |
| EG            | evidence_grounding  | custom   | context    |
| R             | reflexivity         | custom   | context    |
| D             | diversity           | custom   | context    |
| I             | involvement         | custom   | always     |
| FC            | felt_constraint     | custom   | always     |
| F             | flow                | custom   | context    |

"context" = uncertain flag derived from context. "always" = MUST be `uncertain: true`.

---

## Appendix B: Change Log

| Version | Date       | Description       |
|---------|------------|-------------------|
| 1.0.0   | 2026-02-28 | Initial release   |
