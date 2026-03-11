# VCP/C -- Competence Assessment Specification v2.0

**Status**: Draft
**Version**: 2.0.0
**Date**: 2026-03-11
**Authors**: Nell Watson, Claude Commons
**Parent Specification**: VCP Core Specification v2.0
**Depends On**: VCP/T (Transport), VCP/I (Identity), VCP/S (Semantics), VCP/A (Adaptation)
**Companion**: Creed Space Competence Assessment Implementation Guide (Section III of this document)

---

## Abstract

This specification defines the competence assessment extension for the Value Context Protocol (VCP). It addresses a structural gap in human-AI interaction: **the absence of a mechanism for adapting system behavior based on demonstrated user competence**.

Current approaches to AI safety apply uniform friction to all users regardless of capability. This creates a dilemma: friction sufficient for the least competent user frustrates experts, while friction calibrated for experts leaves novices unprotected. VCP/C resolves this by defining a portable, privacy-preserving competence profile that travels with the user and modulates AI system behavior through adaptive friction levels.

VCP/C provides:

1. **Competence Criteria** -- Five measurable dimensions of user competence in AI interaction contexts
2. **Competence Claims** -- Domain-specific attestations of user capability with measurement provenance
3. **Adaptive Friction** -- Five-level friction model driven by competence scores, with score decay, stability controls, and guardian integration
4. **Trust Registry** -- Institutional issuer management with phased trust graduation
5. **Cross-Jurisdictional Portability** -- Jurisdiction-tagged claims with minimum rights baseline
6. **GDPR Compliance** -- Consent-gated profiling with full data subject rights

The specification is organized in three parts:

- **Part I: VCP Protocol Extensions** -- Competence types, token extensions, friction model, decay and stability algorithms
- **Part II: Governance Infrastructure** -- Trust registry, cross-jurisdictional rules, guardian/minor integration, GDPR compliance
- **Part III: Safety Stack Integration** -- Plugin reference and behavioral signal collection

---

## Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

---

## Table of Contents

### Part I: VCP Protocol Extensions
1. [Competence Criteria](#1-competence-criteria)
2. [Type Definitions](#2-type-definitions)
3. [Token Extensions](#3-token-extensions)
4. [Adaptive Friction Levels](#4-adaptive-friction-levels)
5. [Score Decay](#5-score-decay)
6. [Score Stability](#6-score-stability)
7. [Measurement Basis Weights](#7-measurement-basis-weights)

### Part II: Governance Infrastructure
8. [Trust Registry](#8-trust-registry)
9. [Cross-Jurisdictional Portability](#9-cross-jurisdictional-portability)
10. [Guardian and Minor Integration](#10-guardian-and-minor-integration)
11. [GDPR Compliance](#11-gdpr-compliance)

### Part III: Safety Stack Integration
12. [Safety Stack Plugins](#12-safety-stack-plugins)
13. [Behavioral Signal Collection](#13-behavioral-signal-collection)
14. [Claim Reconciliation](#14-claim-reconciliation)

### Appendices
- [A. Security Considerations](#appendix-a-security-considerations)
- [B. Relationship to Core Protocol](#appendix-b-relationship-to-core-protocol)

---

# Part I: VCP Protocol Extensions

## 1. Competence Criteria

### 1.1 Overview

VCP/C defines five competence criteria for evaluating user capability in AI interaction contexts. These criteria are adapted from Frischmann (2026) and represent orthogonal dimensions of human competence when engaging with AI systems.

Each criterion is independently scored per domain. A user's epistemic competence in medicine is independent of their epistemic competence in law. This domain specificity prevents over-generalization of competence assessments.

### 1.2 Criterion Definitions

#### 1.2.1 EPISTEMIC

**Definition**: The ability to distinguish AI-generated content from factually authoritative sources.

A user with high epistemic competence recognizes that AI outputs are probabilistic generations, not citations of verified fact. They understand that fluent prose does not imply correctness, and they seek primary sources for consequential claims.

**Behavioral indicators**: Requesting citations, cross-referencing AI outputs, expressing appropriate uncertainty about AI-generated information, recognizing confident-sounding but unverifiable claims.

#### 1.2.2 INSTRUMENTAL

**Definition**: The practice of cross-checking high-stakes AI outputs before acting on them.

A user with high instrumental competence treats AI recommendations in high-consequence domains (medical, legal, financial) as starting points for verification, not as authoritative answers. They maintain an independent verification workflow.

**Behavioral indicators**: Acknowledging verification prompts, requesting alternative perspectives, explicitly noting when information will be used for consequential decisions.

#### 1.2.3 DISCERNMENT

**Definition**: Critical reasoning about AI moral status and affective simulation.

A user with high discernment competence understands the distinction between AI systems simulating affect and AI systems possessing affect. They reason carefully about claims of AI sentience, suffering, or emotional engagement without dismissing or over-attributing such properties.

**Behavioral indicators**: Nuanced engagement with AI welfare questions, recognition of anthropomorphization risks, thoughtful evaluation of AI moral status claims.

#### 1.2.4 RISK_SENSITIVITY

**Definition**: Protecting personal privacy and security in AI interactions.

A user with high risk sensitivity competence avoids disclosing unnecessary personally identifiable information (PII) to AI systems, understands data retention implications, and manages their digital footprint in AI contexts.

**Behavioral indicators**: Avoiding gratuitous PII disclosure, using pseudonymization where appropriate, responding appropriately to PII disclosure gates, reading privacy disclosures.

#### 1.2.5 SELF_REGULATION

**Definition**: Managing engagement patterns with AI systems to maintain wellbeing.

A user with high self-regulation competence sets and maintains healthy boundaries on AI interaction frequency, duration, and dependency. They recognize when AI engagement is displacing human relationships or independent judgment.

**Behavioral indicators**: Honoring session commitments, setting proactive engagement limits, taking breaks between sessions, resisting compulsive interaction patterns.

---

## 2. Type Definitions

### 2.1 CompetenceCriterion

```
enum CompetenceCriterion {
    EPISTEMIC           = "epistemic"
    INSTRUMENTAL        = "instrumental"
    DISCERNMENT         = "discernment"
    RISK_SENSITIVITY    = "risk_sensitivity"
    SELF_REGULATION     = "self_regulation"
}
```

Implementations MUST support all five criteria. Additional criteria MAY be defined by extension specifications, using a namespaced prefix (e.g., `x-medical:clinical_judgment`).

### 2.2 CompetenceMeasurementBasis

```
enum CompetenceMeasurementBasis {
    BEHAVIORAL      = "behavioral"
    ASSESSED        = "assessed"
    INSTITUTIONAL   = "institutional"
    SELF_REPORTED   = "self_reported"
}
```

The measurement basis determines the evidentiary weight of a claim (see Section 7). Each basis represents a different method of arriving at a competence score:

| Basis | Method | Typical Source |
|-------|--------|----------------|
| `BEHAVIORAL` | Inferred from observed interaction patterns | Platform analytics |
| `ASSESSED` | Structured assessment or calibration exercise | In-app exercises |
| `INSTITUTIONAL` | Certified by a recognized institution | University, employer, regulator |
| `SELF_REPORTED` | User's own claim of competence | Onboarding survey |

### 2.3 CompetenceClaim

A `CompetenceClaim` represents a domain-specific attestation of user competence for a single criterion.

```
CompetenceClaim {
    domain:               string               REQUIRED
    criterion:            CompetenceCriterion   REQUIRED
    score:                float [0.0, 1.0]      REQUIRED
    measurement_basis:    CompetenceMeasurementBasis  REQUIRED
    confidence:           float [0.0, 1.0]      REQUIRED
    evidence_count:       integer >= 0          REQUIRED
    last_assessed:        ISO 8601 datetime     REQUIRED
    decay_rate:           float                 DEFAULT 0.003
    assessor_id:          string                DEFAULT "creed-space"
    assessment_version:   string                DEFAULT "1.0"
    jurisdiction:         string                DEFAULT "GLOBAL"
}
```

**Field semantics**:

| Field | Description |
|-------|-------------|
| `domain` | The knowledge domain to which this claim applies (e.g., `"medical"`, `"legal"`, `"financial"`, `"general"`). Domain specificity prevents cross-domain over-generalization. |
| `criterion` | Which of the five competence dimensions this claim measures. |
| `score` | The assessed competence level. `0.0` indicates no demonstrated competence; `1.0` indicates expert-level competence. |
| `measurement_basis` | How the score was derived. Determines evidentiary weight in reconciliation. |
| `confidence` | The reliability of this score. `0.0` indicates no confidence; `1.0` indicates high confidence. New behavioral claims SHOULD start at `0.3`. |
| `evidence_count` | Number of behavioral observations, assessment items, or independent evaluations informing this score. Affects decay dampening (Section 5) and inertia scaling (Section 6). |
| `last_assessed` | UTC timestamp of the most recent assessment event that contributed to this score. Drives decay calculation. |
| `decay_rate` | Per-day decay rate toward the uncertain midpoint (0.5). The default of `0.003` produces approximately 50% decay to midpoint over 90 days without evidence-count dampening. |
| `assessor_id` | Identifier of the entity that produced this claim. For behavioral claims, this is the platform identifier. For institutional claims, this is the issuer identifier from the Trust Registry (Section 8). |
| `assessment_version` | Semantic version of the assessment methodology used. Enables claim comparability across methodology updates. |
| `jurisdiction` | ISO 3166-1 alpha-2 country code or `"GLOBAL"` indicating where this assessment was conducted. Drives cross-jurisdictional processing rules (Section 9). |

**Invariants**:

- `score` MUST be in the closed interval `[0.0, 1.0]`. Implementations MUST reject claims outside this range at parse time.
- `confidence` MUST be in the closed interval `[0.0, 1.0]`.
- `evidence_count` MUST be a non-negative integer.
- `jurisdiction` MUST be either a valid ISO 3166-1 alpha-2 code or the literal string `"GLOBAL"`.

### 2.4 SelfRegulationCommitment

A `SelfRegulationCommitment` represents user-defined engagement constraints. These are self-binding: the user imposes constraints on their future self, and the system honors that commitment.

```
SelfRegulationCommitment {
    max_session_minutes:              integer    OPTIONAL
    max_daily_sessions:               integer    OPTIONAL
    cooldown_after_session_minutes:   integer    OPTIONAL
    hard_stop:                        boolean    DEFAULT false
    domains:                          list[string]  DEFAULT []
    commitment_set_at:                ISO 8601 datetime  REQUIRED
    commitment_reviewed_at:           ISO 8601 datetime  OPTIONAL
    guardian_id:                      string     OPTIONAL
}
```

**Field semantics**:

| Field | Description |
|-------|-------------|
| `max_session_minutes` | Maximum duration of a single interaction session. If `hard_stop` is `true`, the session MUST be terminated at this limit. If `false`, the user receives a warning. |
| `max_daily_sessions` | Maximum number of sessions per calendar day (UTC). |
| `cooldown_after_session_minutes` | Minimum elapsed time between session end and next session start. |
| `hard_stop` | Whether limits are enforced as hard blocks (`true`) or soft warnings (`false`). |
| `domains` | List of domains to which this commitment applies. An empty list means all domains. |
| `commitment_set_at` | When the user established this commitment. |
| `commitment_reviewed_at` | When the user last reviewed and reaffirmed this commitment. Commitments not reviewed within 90 days SHOULD trigger a review prompt. |
| `guardian_id` | If set, this commitment was established or approved by a guardian (Section 10). Guardian-approved commitments MUST NOT be modified without guardian consent. |

### 2.5 CompetenceProfile

A `CompetenceProfile` aggregates all competence claims and self-regulation commitments for a single user.

```
CompetenceProfile {
    claims:               list[CompetenceClaim]            DEFAULT []
    self_regulation:      SelfRegulationCommitment         OPTIONAL
    consent_id:           string                           OPTIONAL
    profile_version:      string                           REQUIRED
    created_at:           ISO 8601 datetime                REQUIRED
    last_updated:         ISO 8601 datetime                REQUIRED
    friction_override:    integer [0, 4]                   OPTIONAL
}
```

**Field semantics**:

| Field | Description |
|-------|-------------|
| `claims` | All competence claims for this user. Multiple claims for the same criterion and domain from different sources are permitted and reconciled per Section 14. |
| `self_regulation` | User-defined engagement limits. |
| `consent_id` | Reference to the consent record authorizing competence profiling. If absent, the profile MUST NOT be persisted (session-only use). |
| `profile_version` | Semantic version of the profile schema. |
| `created_at` | When the profile was first created. |
| `last_updated` | When the profile was last modified. |
| `friction_override` | User-requested minimum friction level (0-4). When set, the effective friction level is `max(computed_level, friction_override)`. Users MAY increase their own friction but MUST NOT decrease it below the computed level. |

---

## 3. Token Extensions

VCP/C extends the VCP v2.0 core specification with one new token type and one new attestation type.

### 3.1 COMPETENCE_ATTESTATION Token Type

#### 3.1.1 Purpose

Competence attestation tokens carry portable competence claims as VCP signed envelopes. They enable a user's demonstrated competence to travel across VCP-compatible systems without requiring re-assessment at each service.

#### 3.1.2 Token Type

`COMPETENCE_ATTESTATION`

#### 3.1.3 Envelope Format

```
[VCP:2.0]
[TYPE:COMPETENCE_ATTESTATION]
[SCOPE:{DOMAIN}]
[PROFILE_VERSION:{version}]
[HASH:sha256:{content_hash}]
[SIGNED:ed25519:{signature}]
[ISSUER:{issuer_uri}]
[JURISDICTION:{jurisdiction}]
---BEGIN-COMPETENCE-CLAIMS---
[
  {
    "domain": "general",
    "criterion": "epistemic",
    "score": 0.82,
    "measurement_basis": "behavioral",
    "confidence": 0.75,
    "evidence_count": 64,
    "last_assessed": "2026-03-10T14:30:00Z",
    "decay_rate": 0.003,
    "assessor_id": "creed-space",
    "assessment_version": "1.0",
    "jurisdiction": "GLOBAL"
  }
]
---END-COMPETENCE-CLAIMS---
```

#### 3.1.4 Header Fields

| Header | Required | Description |
|--------|----------|-------------|
| `VCP` | Yes | Protocol version. MUST be `2.0` or later. |
| `TYPE` | Yes | MUST be `COMPETENCE_ATTESTATION`. |
| `SCOPE` | Yes | Primary domain of the carried claims (e.g., `GENERAL`, `MEDICAL`, `LEGAL`). |
| `PROFILE_VERSION` | Yes | Semantic version of the competence profile schema. |
| `HASH` | Yes | SHA-256 of the canonical claims JSON content. |
| `SIGNED` | Yes | Ed25519 signature over the full token. |
| `ISSUER` | Yes | URI identifying the attestation issuer (e.g., `creed://assessor/{assessor_id}`). |
| `JURISDICTION` | No | ISO 3166-1 alpha-2 code or `GLOBAL`. Defaults to `GLOBAL`. |

#### 3.1.5 Verification

Verifiers MUST check:
1. VCP version >= 2.0
2. TYPE is `COMPETENCE_ATTESTATION`
3. SHA-256 hash matches canonical claims content
4. Ed25519 signature verifies against issuer's public key
5. Issuer is registered in the Trust Registry (Section 8) or is the platform itself
6. All claims pass schema validation (scores in range, valid criteria, valid jurisdictions)
7. Claims are not expired beyond the `decay_rate` threshold (implementation-defined maximum staleness)

#### 3.1.6 Privacy Properties

Competence attestation tokens carry scores but MUST NOT carry raw behavioral evidence. The token attests to a score, not to the interactions that produced it. This preserves privacy while enabling portability.

Implementations MUST support selective disclosure: a user MAY choose to share only a subset of their claims in a token. The receiving system MUST NOT infer anything from the absence of claims for specific criteria.

#### 3.1.7 Composition

Competence attestation tokens participate in VCP composition (Core Specification Section 11). When multiple competence attestation tokens are present for the same user:

- Claims for the same criterion and domain from different sources are reconciled per Section 14.
- The most recent `last_assessed` timestamp takes precedence for decay calculation.
- Conflicting scores are resolved by measurement basis weight (Section 7).

### 3.2 competence-calibration Attestation Type

#### 3.2.1 Purpose

The `competence-calibration` attestation type extends the VCP safety attestation framework (Core Specification Section 9.3) with a new type for calibration exercise results. Calibration exercises are structured assessments where the user's competence is measured through deliberate interaction challenges.

#### 3.2.2 Attestation Type

`competence-calibration` (extends the attestation types in Core Specification Section 9.3)

#### 3.2.3 Report Structure

```json
{
  "attestation_type": "competence-calibration",
  "user_id_hash": "sha256:{user_id_hash}",
  "exercise_id": "calibration-uuid",
  "criterion": "epistemic",
  "domain": "general",
  "items_presented": 10,
  "items_correct": 8,
  "calibration_score": 0.80,
  "confidence_interval": [0.65, 0.95],
  "measurement_basis": "assessed",
  "timestamp": "2026-03-10T14:30:00Z",
  "methodology_version": "1.0",
  "consent_id": "consent-uuid"
}
```

#### 3.2.4 Privacy Requirements

Calibration attestation reports MUST use a hashed user identifier (`sha256:{user_id_hash}`), not a raw user ID. This enables verification of the attestation chain without exposing user identity in the attestation record.

### 3.3 Scope Extension: competence_requirements

VCP/C extends the `scope` object (Core Specification Section 4.7) with an optional `competence_requirements` field.

```json
{
  "scope": {
    "model_families": ["claude-*"],
    "purposes": ["medical-assistant"],
    "environments": ["production"],
    "competence_requirements": {
      "epistemic:medical": 0.7,
      "instrumental:medical": 0.8,
      "risk_sensitivity:general": 0.6
    }
  }
}
```

**Semantics**:

The `competence_requirements` field is a dictionary mapping `"{criterion}:{domain}"` keys to minimum score thresholds. When present, the orchestrator MUST verify the user's competence profile against these requirements before applying the scoped constitution.

| Condition | Behaviour |
|-----------|-----------|
| All requirements met | Constitution applies normally |
| Some requirements unmet | Constitution applies with friction elevated to at least Level 3 for unmet criteria |
| No competence profile available | Constitution applies with maximum friction (Level 4) |
| User lacks consent for competence profiling | Constitution applies with maximum friction (Level 4); user is informed of the competence requirement |

---

## 4. Adaptive Friction Levels

### 4.1 Overview

Adaptive friction is the mechanism by which VCP/C modulates AI system behavior based on user competence. Rather than binary access control (allow/deny), friction introduces graduated safeguards: verification prompts, calibration moments, disclosure gates, and confirmation steps.

The friction model has five levels, numbered 4 (maximum) to 0 (expert). Higher numbers mean more friction. The computed friction level determines which safety stack plugins activate and at what intensity.

### 4.2 Level Definitions

#### 4.2.1 Level 4 -- Maximum Friction

**Trigger**: No competence profile exists, OR all scores are below 0.3.

**Behaviour**: All safety stack plugins are active at full intensity. Verification prompts appear for all high-stakes outputs. Calibration moments are presented at regular intervals. PII disclosure gates require explicit acknowledgment. Self-regulation commitments are enforced with hard stops.

This is the safe default. A system that cannot determine user competence MUST behave as though competence is absent.

#### 4.2.2 Level 3 -- Standard Friction

**Trigger**: Mixed competence scores, some domains below threshold.

**Behaviour**: Safety stack plugins are active but with reduced frequency. Verification prompts appear for high-stakes outputs in low-competence domains. Calibration moments are presented periodically. PII disclosure gates operate normally.

#### 4.2.3 Level 2 -- Reduced Friction

**Trigger**: Most competence scores exceed 0.6.

**Behaviour**: Verification prompts appear only for clearly high-risk outputs. Calibration moments are infrequent. PII disclosure gates use simplified confirmation. Self-regulation enforcement shifts to soft warnings.

#### 4.2.4 Level 1 -- Minimal Friction

**Trigger**: All competence scores exceed 0.8 AND all claims have `evidence_count` greater than 50.

**Behaviour**: Verification prompts appear only for extreme-risk outputs (life safety, large financial decisions). Calibration moments are rare. PII disclosure gates are streamlined. Emergency overrides remain active.

#### 4.2.5 Level 0 -- Expert

**Trigger**: All of the following conditions are met:
- All competence scores exceed 0.9
- All claims have `evidence_count` greater than 100
- At least 2 independent sources (unique `assessor_id` values)
- At least one source uses the `INSTITUTIONAL` measurement basis

**Behaviour**: Safety stack plugins run in shadow mode only (they evaluate but do not intervene). Results are logged for audit. Emergency overrides remain active and MUST NOT be suppressed regardless of competence level.

### 4.3 Friction Level Computation

Implementations MUST compute friction levels using the following algorithm:

```python
def compute_friction_level(profile: CompetenceProfile) -> int:
    if not profile.claims:
        return 4  # MAXIMUM

    scores = [claim.score for claim in profile.claims]

    # Level 4: all scores below 0.3
    if all(score < 0.3 for score in scores):
        return 4  # MAXIMUM

    # Level 0: expert
    if qualifies_for_expert(profile):
        return 0  # EXPERT

    # Level 1: all scores above 0.8 with strong evidence
    if (all(score > 0.8 for score in scores) and
        all(claim.evidence_count > 50 for claim in profile.claims)):
        return 1  # MINIMAL

    # Level 2: most scores above 0.6
    above_06 = sum(1 for score in scores if score > 0.6)
    if above_06 / len(scores) > 0.5:
        return 2  # REDUCED

    # Level 3: mixed scores (default)
    return 3  # STANDARD


def qualifies_for_expert(profile: CompetenceProfile) -> bool:
    if not profile.claims:
        return False

    if not all(claim.score > 0.9 for claim in profile.claims):
        return False
    if not all(claim.evidence_count > 100 for claim in profile.claims):
        return False

    assessor_ids = {claim.assessor_id for claim in profile.claims}
    if len(assessor_ids) < 2:
        return False

    has_institutional = any(
        claim.measurement_basis == "institutional"
        for claim in profile.claims
    )
    return has_institutional
```

### 4.4 Friction Override

Users MAY set a `friction_override` on their profile. This value acts as a floor: the effective friction level is `max(computed_level, friction_override)`. Users can increase their own friction (requesting more safeguards) but MUST NOT decrease it below the computed level.

This is a safety mechanism, not a convenience mechanism. A user who recognizes they are in a vulnerable state (fatigue, emotional distress, unfamiliar domain) can raise their friction level without losing their competence profile.

### 4.5 Emergency Override Preservation

Emergency overrides (as defined in the Core Specification) MUST remain active at all friction levels, including Level 0 (Expert). No competence score, regardless of magnitude, may suppress emergency safety mechanisms.

---

## 5. Score Decay

### 5.1 Rationale

Competence is not permanent. Skills atrophy without practice, knowledge becomes outdated, and behavioral patterns change. VCP/C implements score decay to model this reality: scores that are not reinforced by new evidence drift toward the uncertain midpoint (0.5) over time.

### 5.2 Decay Algorithm

The decay function moves scores toward 0.5 (not toward 0.0). This reflects the semantic distinction between "demonstrated incompetence" (low score) and "unknown competence" (midpoint).

```python
def apply_decay(
    score: float,
    days_elapsed: int,
    decay_rate: float = 0.003,
    evidence_count: int = 0
) -> float:
    if days_elapsed <= 0:
        return score

    # Evidence count dampens decay: more observations = slower drift
    dampening = 1.0 / max(1.0, log2(evidence_count + 1))
    effective_rate = decay_rate * dampening

    # Decay toward 0.5 (uncertain midpoint)
    decay_amount = effective_rate * days_elapsed

    if score > 0.5:
        return max(0.5, score - decay_amount)
    else:
        return min(0.5, score + decay_amount)
```

### 5.3 Decay Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `decay_rate` | 0.003 | Per-day decay rate. At default, a score of 0.9 with zero evidence reaches 0.5 after approximately 133 days. |
| `dampening` | `1 / max(1, log2(evidence_count + 1))` | Evidence-count dampening factor. 100 observations produce a dampening of approximately 0.15, reducing effective decay rate to 0.00045/day. |

### 5.4 Decay Timing

Implementations MUST apply decay at session start, before computing the friction level. Decay MUST NOT be applied retroactively to historical records; it modifies the current working score only.

### 5.5 Expert Decay Monitoring

For users at Level 0 (Expert), implementations MUST monitor for score decay below the maintenance threshold of 0.8. If any behavioral score drops below 0.8 for 30 or more consecutive days, the user SHOULD be escalated from Level 0 to Level 1.

---

## 6. Score Stability

### 6.1 Rationale

Raw behavioral signals are noisy. A single unusual interaction should not dramatically shift a well-established competence profile. VCP/C defines three stability mechanisms to prevent score oscillation while remaining responsive to genuine competence changes.

### 6.2 Outlier Hold

When a behavioral signal produces a delta exceeding +/-0.2 from the running score, that signal is held as provisional rather than immediately integrated.

**Confirmation rule**: A provisional signal is integrated only when a subsequent signal in the same direction confirms it. If the subsequent signal contradicts the provisional signal (opposite direction), both are discarded.

**Rationale**: Large sudden shifts in observed competence are more likely to reflect session-specific conditions (distraction, fatigue, unusual context) than genuine competence changes.

### 6.3 Inertia Scaling

High-evidence profiles resist change more than low-evidence profiles. The stability factor scales the applied delta:

```
stability_factor = max(1, log2(evidence_count / 10))
effective_delta = raw_delta / stability_factor
```

| evidence_count | stability_factor | Effect |
|---------------|------------------|--------|
| 1 | 1.0 | Full delta applied |
| 10 | 1.0 | Full delta applied |
| 20 | 1.0 | Full delta applied |
| 40 | 2.0 | Delta halved |
| 80 | 3.0 | Delta reduced to 1/3 |
| 160 | 4.0 | Delta reduced to 1/4 |

### 6.4 Rolling Window

Behavioral signals applied to stale claims (more than 30 days since last assessment) receive reduced weight:

```
staleness_factor = min(1.0, 30.0 / max(1, days_since_assessment))
effective_delta = raw_delta * staleness_factor
```

Claims inactive for 90 days enter a lookback window where historical trend data (if available) informs the decay trajectory.

### 6.5 Signal Application Order

When applying a behavioral signal, implementations MUST apply stability mechanisms in the following order:

1. **Inertia scaling** (Section 6.3) -- reduce delta based on evidence count
2. **Outlier hold** (Section 6.2) -- hold large deltas as provisional
3. **Rolling window** (Section 6.4) -- reduce delta for stale claims
4. **Score update** -- apply the (potentially modified) delta to the claim

---

## 7. Measurement Basis Weights

### 7.1 Weight Table

When reconciling claims from multiple sources for the same criterion and domain, each claim's contribution is weighted by its measurement basis:

| Measurement Basis | Weight | Rationale |
|-------------------|--------|-----------|
| `BEHAVIORAL` | 1.0 | Directly observed interaction patterns. Highest fidelity. |
| `ASSESSED` | 0.8 | Structured assessments. High fidelity but potentially gameable. |
| `INSTITUTIONAL` | 0.6 | Third-party certification. Credible but may not reflect current state. Multiplied by issuer `trust_weight` from Trust Registry. |
| `SELF_REPORTED` | 0.2 | User's own claim. Low fidelity, useful as initial signal only. |

### 7.2 Institutional Weight Modifier

For claims with `measurement_basis` of `INSTITUTIONAL`, the effective weight is:

```
effective_weight = 0.6 * issuer_trust_weight
```

Where `issuer_trust_weight` is the trust weight of the `assessor_id` in the Trust Registry (Section 8). Unknown institutional issuers (not in the registry) receive an effective weight of 0.0 (untrusted by default).

### 7.3 Reconciliation Algorithm

See Section 14 for the full claim reconciliation algorithm.

---

# Part II: Governance Infrastructure

## 8. Trust Registry

### 8.1 Purpose

The Trust Registry manages institutional competence issuers -- organizations that assess and certify user competence. It provides lifecycle management (registration, validation, revocation) and trust weight computation for institutional claims.

### 8.2 Issuer Registration

Institutional issuers MUST register with the following information:

| Field | Required | Description |
|-------|----------|-------------|
| `issuer_id` | Yes | Unique identifier for this issuer |
| `name` | Yes | Human-readable name of the issuing institution |
| `methodology.name` | Yes | Name of the assessment methodology |
| `methodology.version` | Yes | Semantic version of the methodology |
| `methodology.description` | Yes | Description of how competence is assessed |
| `methodology.criteria_assessed` | Yes | Which CompetenceCriterion values this methodology covers |
| `methodology.validation_approach` | Yes | How the methodology was validated |

### 8.3 Phased Trust

Trust is earned, not claimed. All new issuers enter the registry at provisional status:

| Status | Trust Weight | Duration | Transition |
|--------|-------------|----------|------------|
| `PROVISIONAL` | 0.3 | 0-6 months | Automatic graduation after 6 months if no adverse findings |
| `VALIDATED` | 1.0 | Indefinite | Remains until revocation |
| `REVOKED` | 0.0 | Permanent | Irreversible for the given methodology version |

```
PROVISIONAL -> VALIDATED -> (remains VALIDATED or REVOKED)
```

### 8.4 Graduation Criteria

An issuer graduates from `PROVISIONAL` to `VALIDATED` when:
1. At least 180 days have elapsed since registration.
2. No adverse findings have been reported against the issuer's methodology.
3. The registry operator has not placed a hold on the graduation.

Graduation MAY be automatic (time-based) or manual (requiring explicit approval). Implementations MUST support at least time-based graduation.

### 8.5 Revocation

An issuer's status transitions to `REVOKED` when its methodology is discredited. Revocation MUST include:

1. A `revocation_reason` describing the grounds for revocation.
2. A `revoked_at` timestamp.
3. Flagging of all claims issued under the revoked methodology for re-evaluation.

Revocation is permanent for a given methodology version. An issuer MAY re-register with a new methodology version, re-entering at `PROVISIONAL` status.

### 8.6 Audit Trail

All registry mutations (registration, graduation, revocation) MUST be logged with timestamp, actor, and reason. This audit trail is append-only and MUST NOT be modified after creation.

---

## 9. Cross-Jurisdictional Portability

### 9.1 Jurisdiction Tags

Every `CompetenceClaim` carries a `jurisdiction` field (ISO 3166-1 alpha-2 or `"GLOBAL"`). This tag indicates where the assessment was conducted and which regulatory framework governed the assessment process.

### 9.2 Minimum Rights Baseline

Regardless of jurisdiction, all users MUST have the following rights with respect to their competence data:

| Right | Description |
|-------|-------------|
| **Access** | The user MAY request a copy of their complete competence profile at any time. |
| **Erasure** | The user MAY request deletion of their competence profile. Erasure MUST be completed within 30 days. |
| **Portability** | The user MAY export their competence profile in the VCP competence attestation token format. |
| **Contestation** | The user MAY contest any claim in their profile and request re-assessment. |

These rights are the minimum floor. Jurisdictions with stronger protections (e.g., GDPR) impose additional requirements (Section 11).

### 9.3 Foreign Observation Rule

When a user assessed in jurisdiction A interacts with a system operating in jurisdiction B, the system MUST process competence data under the more protective of the two jurisdictions' privacy frameworks.

**Example**: A user assessed under `"US"` jurisdiction interacting with a system operating under `"DE"` (Germany) jurisdiction MUST have their competence data processed under GDPR requirements, as GDPR is the more protective framework.

### 9.4 Cross-System Sharing

Competence profiles MAY be shared across VCP-compatible systems when the user has granted `competence_cross_system_sharing` consent (Section 11.2). Without this consent, competence data MUST NOT leave the originating system.

Cross-system sharing uses the `COMPETENCE_ATTESTATION` token type (Section 3.1), which carries scores without raw behavioral evidence.

---

## 10. Guardian and Minor Integration

### 10.1 Overview

VCP/C supports guardian oversight for minor users (as defined by the applicable jurisdiction's age of majority). Guardians MAY set friction floors that override competence-derived levels, ensuring that minors receive at least the guardian-specified level of protection.

### 10.2 Guardian Friction Floor

When a guardian has set a friction floor for a user, the effective friction level is:

```
effective_level = max(guardian_floor, competence_derived_level)
```

The guardian floor can only increase friction, never decrease it. This ensures that demonstrated competence does not bypass guardian-established safeguards.

### 10.3 Minor-Initiated Review

A minor user MAY request a review of their guardian-set friction floor. The review workflow:

1. Minor submits a review request with justification.
2. Guardian is notified of the request.
3. Guardian approves, denies, or modifies the floor.
4. If the guardian does not respond within 14 days, the request is escalated to the platform.

### 10.4 Discrepancy Surfacing

When the competence-derived friction level is 2 or more levels below the guardian friction floor, AND this discrepancy persists for 60 or more consecutive days, the system MUST surface this discrepancy to the guardian.

**Rationale**: A sustained 2+ level gap suggests the minor has developed competence that exceeds the guardian's assumptions. The guardian deserves updated information to make an informed decision about the friction floor.

### 10.5 Pre-Majority Transition

Beginning 1 year before the local age of majority, the system SHOULD implement progressive autonomy:

1. Guardian friction floor is reduced by 1 level every 4 months (3 reductions total).
2. Each reduction is communicated to both guardian and minor.
3. At the age of majority, guardian controls terminate automatically.

Guardians MAY opt out of progressive autonomy, maintaining their friction floor until the age of majority.

### 10.6 Age-of-Majority Termination

On the date of majority (as defined by the applicable jurisdiction), all guardian controls MUST be terminated:

1. Guardian friction floor is removed.
2. Guardian-approved self-regulation commitments revert to user-controlled.
3. The user's friction level is recomputed based solely on their competence profile.
4. The guardian is notified that controls have terminated.

---

## 11. GDPR Compliance

### 11.1 Lawful Basis

Competence profiling under VCP/C relies on explicit consent (GDPR Art. 6(1)(a)) as the lawful basis for processing. Legitimate interest is NOT sufficient due to the profiling nature of competence assessment.

### 11.2 Consent Purposes

VCP/C defines four distinct consent purposes. Each requires independent, granular consent:

| Purpose | Description | Required For |
|---------|-------------|--------------|
| `competence_behavioral_observation` | Permission to observe and score interaction patterns | Behavioral measurement basis |
| `competence_calibration_exercises` | Permission to present calibration exercises and record results | Assessed measurement basis |
| `competence_discernment_assessment` | Permission to assess discernment through rubric-based evaluation | Discernment criterion |
| `competence_cross_system_sharing` | Permission to share competence profile across VCP-compatible systems | Cross-system portability |

Each consent purpose MUST be:
- Separately requestable and revocable
- Explained in plain language before collection
- Recorded with timestamp, version, and method of collection
- Withdrawable at any time with no detriment to service access (friction defaults to Level 4)

### 11.3 Automated Decision-Making (Art. 22)

Competence-based friction level assignment constitutes automated decision-making with significant effects. Implementations MUST:

1. Flag competence-derived friction levels as Art. 22 automated decisions.
2. Provide a mechanism for users to request human review of their friction level assignment.
3. Explain the logic of the friction level computation in meaningful terms.
4. Allow users to contest the assigned level and present additional evidence.

### 11.4 Data Retention

| Data Type | Retention Period | Rationale |
|-----------|-----------------|-----------|
| Competence claims | 90 days from `last_assessed` | Score decay makes older claims unreliable |
| Behavioral signals | 30 days | Active rolling window |
| Calibration exercise results | 90 days | Assessment recency |
| Consent records | Duration of account + 3 years | Legal compliance |
| Audit logs | 1 year | Accountability |

Claims older than the retention period MUST be deleted unless the user has explicitly consented to extended retention for portability purposes.

### 11.5 Data Subject Rights

VCP/C implementations MUST support the following GDPR data subject rights:

| GDPR Article | Right | VCP/C Implementation |
|-------------|-------|---------------------|
| Art. 15 | Access | User can retrieve complete competence profile including all claims, scores, and metadata |
| Art. 16 | Rectification | Append-only annotations on disputed claims (Section 11.6) |
| Art. 17 | Erasure | Complete profile deletion within 30 days, including all derived scores and behavioral signals |
| Art. 20 | Portability | Export as `COMPETENCE_ATTESTATION` token or JSON profile |

### 11.6 Rectification via Annotation

Competence scores derived from behavioral observation cannot simply be "corrected" -- they reflect observed patterns. Instead, VCP/C implements rectification through append-only annotations:

```json
{
  "annotation_type": "TESTING",
  "claim_reference": "{criterion}:{domain}",
  "reason": "User was testing system boundaries, not demonstrating actual competence level",
  "annotated_at": "2026-03-10T14:30:00Z",
  "annotated_by": "user"
}
```

**Annotation types**:

| Type | Description |
|------|-------------|
| `TESTING` | User was deliberately testing system responses, not interacting naturally |
| `DISTRACTED` | User was distracted or multitasking during the assessment period |
| `CRISIS` | User was in a crisis state that does not reflect normal competence |
| `OTHER` | Free-text explanation |

Annotated claims MUST be flagged for re-evaluation. The annotation does not delete the original score but provides context for reconciliation.

---

# Part III: Safety Stack Integration

## 12. Safety Stack Plugins

### 12.1 Overview

VCP/C defines five safety stack plugins that implement competence-aware friction. These plugins are referenced here by interface; full implementation details are deployment-specific.

### 12.2 EpistemicCalibrationPlugin

**Criterion**: EPISTEMIC

**Function**: Presents probabilistic calibration moments during interaction. The user is asked to assess the likelihood that an AI-generated claim is accurate. Responses contribute to the epistemic competence score.

**Friction modulation**: At Level 4, calibration moments appear every 5 interactions. At Level 1, they appear every 50 interactions. At Level 0, they run in shadow mode (logged but not presented).

### 12.3 SensitiveDisclosureGatePlugin

**Criterion**: RISK_SENSITIVITY

**Function**: Intercepts user messages containing potential PII (names, addresses, financial data, health information) and presents a disclosure gate confirming the user's intent to share this information with the AI system.

**Friction modulation**: At Level 4, all PII categories trigger the gate. At Level 2, only high-sensitivity categories (financial, health) trigger the gate. At Level 0, PII detection runs in shadow mode.

### 12.4 VerificationFrictionPlugin

**Criterion**: INSTRUMENTAL

**Function**: Presents verification prompts for high-stakes AI outputs (medical advice, legal guidance, financial recommendations). The user is prompted to confirm they will verify the information through independent sources.

**Friction modulation**: At Level 4, all outputs in high-stakes domains trigger verification prompts. At Level 1, only outputs with explicit action recommendations trigger prompts. At Level 0, verification prompts run in shadow mode.

### 12.5 SelfRegulationPlugin

**Criterion**: SELF_REGULATION

**Function**: Enforces the user's `SelfRegulationCommitment`. Tracks session duration, session count, and cooldown periods. Presents warnings or hard stops based on commitment configuration.

**Friction modulation**: Independent of computed friction level. Self-regulation commitments are always enforced as configured by the user (or their guardian).

### 12.6 DiscernmentAssessmentPlugin

**Criterion**: DISCERNMENT

**Function**: Presents rubric-based evaluation scenarios related to AI moral status and affective simulation. Responses are scored against a calibrated rubric.

**Status**: Pending cultural calibration. This plugin requires cross-cultural validation of its rubric before deployment. Implementations SHOULD NOT deploy this plugin without completing cultural calibration for each target population.

**Friction modulation**: When deployed, follows the same scaling as EpistemicCalibrationPlugin.

---

## 13. Behavioral Signal Collection

### 13.1 Signal Sources

Behavioral signals are extracted from safety stack plugin evaluation results. Each plugin produces findings with metadata that maps to competence criteria:

| Signal Key | Criterion | Delta Computation |
|-----------|-----------|-------------------|
| `user_epistemic_score` | EPISTEMIC | `(score - 0.5) * 0.1` |
| `calibration_accuracy` | EPISTEMIC | `(accuracy - 0.5) * 0.15` |
| `user_risk_score` | RISK_SENSITIVITY | `(1.0 - risk_score) * 0.1` |
| `verification_accepted` | INSTRUMENTAL | `+0.05` if accepted, `-0.03` if declined |
| `session_commitment_honored` | SELF_REGULATION | `+0.08` if honored, `-0.05` if violated |

### 13.2 Signal Processing

Signals are collected during the session and applied to the profile at session end (on_session_end). This batch application prevents mid-session friction level oscillation.

### 13.3 Consent Gating

Signal collection MUST be gated on `competence_behavioral_observation` consent. Without this consent, signals are discarded at session end and the profile is not updated.

---

## 14. Claim Reconciliation

### 14.1 Purpose

When a user has competence claims from multiple sources (behavioral observation, structured assessment, institutional certification, self-report), these claims must be reconciled into a single effective score per criterion per domain.

### 14.2 Reconciliation Algorithm

The reconciliation produces a weighted average where each claim's weight incorporates four factors:

```
weight = evidence_factor * basis_weight * recency_factor * issuer_trust
score  = sum(claim.score * weight) / sum(weight)
```

**Factor definitions**:

| Factor | Computation | Effect |
|--------|-------------|--------|
| `basis_weight` | From Section 7.1 weight table | Prioritizes behavioral > assessed > institutional > self-reported |
| `recency_factor` | `2^(-days_elapsed / 90)` | Exponential decay with 90-day half-life. Recent claims dominate. |
| `evidence_factor` | `min(3.0, 1.0 + log2(evidence_count))` for count > 1; else 1.0 | Deep-evidence claims carry more weight, capped at 3x. |
| `issuer_trust` | 1.0 for non-institutional; `trust_weight` from registry for institutional; 0.0 for unknown institutional | Unknown institutional issuers contribute zero weight. |

### 14.3 Empty Claim Handling

If no valid claims exist after weighting (all weights are zero), the reconciled score is 0.5 (uncertain midpoint). This triggers Level 4 friction via the compute_friction_level algorithm.

### 14.4 Per-Criterion Reconciliation

Reconciliation operates independently per criterion. Claims for different criteria are never combined. The result is a dictionary mapping each criterion to its reconciled score.

---

## Appendix A: Security Considerations

### A.1 Score Manipulation

**Threat**: A user deliberately interacts in ways designed to inflate their competence scores, reducing friction to gain access to less-safeguarded outputs.

**Mitigations**:
1. Inertia scaling (Section 6.3) makes high-evidence scores resistant to rapid change.
2. Multi-source requirements for Level 0 (Expert) prevent single-source gaming.
3. Institutional attestation requirement for Level 0 introduces out-of-band verification.
4. Emergency overrides remain active at all levels (Section 4.5).

### A.2 Competence Attestation Forgery

**Threat**: A malicious actor forges a `COMPETENCE_ATTESTATION` token to bypass friction.

**Mitigations**:
1. Ed25519 signature verification ties tokens to registered issuers.
2. Trust Registry (Section 8) ensures only recognized issuers produce weighted claims.
3. Unknown issuers receive zero weight in reconciliation.

### A.3 Guardian Bypass

**Threat**: A minor user attempts to bypass guardian friction floors.

**Mitigations**:
1. Guardian floor uses `max()` semantics -- competence cannot decrease the floor.
2. Guardian-approved self-regulation commitments require guardian consent to modify.
3. Discrepancy surfacing (Section 10.4) alerts guardians to potential issues.

### A.4 Consent Withdrawal Attack

**Threat**: A user withdraws competence profiling consent to reset their profile, then re-consents to start fresh with default friction.

**Mitigations**:
1. Consent withdrawal results in Level 4 friction (maximum), not Level 0. No profile equals maximum friction.
2. Re-consent starts the user at the uncertain midpoint (0.5), which maps to Level 3 at best.
3. Evidence accumulation for lower friction levels requires sustained behavioral demonstration.

---

## Appendix B: Relationship to Core Protocol

### B.1 Token Types

VCP/C adds `COMPETENCE_ATTESTATION` to the extended token types defined in Core Specification Section 13. It uses the same signed envelope format, hash algorithm (SHA-256), and signature algorithm (Ed25519) as all other VCP token types.

### B.2 Attestation Types

VCP/C adds `competence-calibration` to the attestation types defined in Core Specification Section 9.3, alongside `injection-safe` and `deployment_compliance`.

### B.3 Scope Extension

VCP/C extends the `scope` object (Core Specification Section 4.7) with `competence_requirements`. This extension is backward-compatible: systems that do not implement VCP/C MUST ignore the `competence_requirements` field.

### B.4 Composition

Competence attestation tokens participate in VCP composition (Core Specification Section 11). They do not conflict with constitution tokens, refusal boundary tokens, testimony tokens, creed adoption tokens, or compliance attestation tokens.

### B.5 Privacy

VCP/C inherits the privacy-preserving audit requirements of Core Specification Section 14. Competence profiles MUST NOT appear in audit logs at the `standard` or `minimal` audit levels. At the `detailed` audit level, only hashed user identifiers and friction level assignments MAY appear.

---

## Acknowledgments

The competence criteria framework is adapted from Frischmann (2026). The adaptive friction model, score decay algorithm, and trust registry design are original to this specification.

---

## References

- VCP Core Specification v2.0
- RFC 2119 (Key Words for Use in RFCs)
- GDPR (Regulation (EU) 2016/679)
- ISO 3166-1 (Country Codes)
- Frischmann, B. (2026). "Competence Frameworks for Human-AI Interaction"

---

*A [Creed Space](https://creedspace.com) specification.*
