# VCP-X-Personal: Personal State Signaling Extension

## Extension Metadata

| Field              | Value                                               |
|--------------------|-----------------------------------------------------|
| Name               | VCP-X-Personal                                      |
| Version            | 1.0.0                                               |
| Status             | Stable                                              |
| Introduced in      | VCP 3.1.0                                           |
| Replaces           | VCP 3.0 Prosaic Signals (4 float dimensions)        |
| Dependencies       | VCP Core >= 3.1.0                                   |
| Wire-format prefix | `personal`                                          |
| Specification date | 2026-02-28                                          |

## 1. Overview

VCP-X-Personal defines a structured, categorical signaling layer for communicating
the user's self-reported personal state within a VCP context envelope. It addresses
five dimensions of human experience -- cognitive state, emotional tone, energy level,
perceived urgency, and body signals -- each expressed as a categorical value paired
with an integer intensity (1-5).

**Design Principle.** Layer 3 is not diagnostic or therapeutic; it reflects
self-reported state for adaptation only. Systems consuming personal signals MUST NOT
treat them as medical assessments, emotional diagnoses, or clinical indicators.
Personal signals exist so that an AI system can adjust its response style (e.g.,
shorter answers when the user is fatigued, gentler tone when frustrated). They do
not authorize any form of intervention, triage, or clinical recommendation.

### 1.1 Relationship to VCP Core

Personal signals occupy Layer 3 of the VCP context stack:

```
Layer 1: Categorical context (9 situational dimensions)
Layer 2: Constitutional context (creed / constitution references)
Layer 3: Personal context   <-- THIS EXTENSION
Layer 4: Generation preferences (Priori-style sliders)
Layer 5: Relational context (VCP 3.1 relational extensions)
```

Personal signals are OPTIONAL. A VCP context envelope with no `personal` field
is valid and indicates that no personal state information is available.

### 1.2 Migration from VCP 3.0

VCP 3.0 used four floating-point prosaic signals (`urgency`, `health`, `cognitive`,
`affect`) on a 0.0-1.0 scale. VCP 3.1 replaces these with five categorical
dimensions plus integer intensity. See Section 8 for the `from_legacy_prosaic`
migration path.

---

## 2. Data Models

### 2.1 PersonalDimension

An enumeration of the five personal state dimensions.

| Enum Value           | Wire Key             | Symbol | Description                               |
|----------------------|----------------------|--------|-------------------------------------------|
| `COGNITIVE_STATE`    | `cognitive_state`    | brain  | Mental clarity and focus                   |
| `EMOTIONAL_TONE`     | `emotional_tone`     | thought| Emotional register                         |
| `ENERGY_LEVEL`       | `energy_level`       | battery| Physical and mental energy                 |
| `PERCEIVED_URGENCY`  | `perceived_urgency`  | zap    | Time pressure perception                   |
| `BODY_SIGNALS`       | `body_signals`       | health | Physical comfort and wellbeing             |

### 2.2 Dimension Value Enums

Each dimension has a fixed set of categorical values. These are string enums.

**cognitive_state** (CognitiveStateValue):

| Value         | Meaning                                      |
|---------------|----------------------------------------------|
| `focused`     | Clear, concentrated attention                |
| `distracted`  | Attention scattered, difficulty concentrating|
| `overloaded`  | Too many inputs, cognitive capacity exceeded |
| `foggy`       | Unclear thinking, mental haze                |
| `reflective`  | Contemplative, introspective mode            |

**emotional_tone** (EmotionalToneValue):

| Value         | Meaning                                      |
|---------------|----------------------------------------------|
| `calm`        | Relaxed, at ease                             |
| `tense`       | Heightened alertness, stress present         |
| `frustrated`  | Blocked, irritated, experiencing friction    |
| `neutral`     | Neither positive nor negative                |
| `uplifted`    | Positive affect, elevated mood               |

**energy_level** (EnergyLevelValue):

| Value         | Meaning                                      |
|---------------|----------------------------------------------|
| `rested`      | Well-rested, full energy reserves            |
| `low_energy`  | Below baseline but functional                |
| `fatigued`    | Significantly tired, reduced capacity        |
| `wired`       | High energy, possibly over-stimulated        |
| `depleted`    | Exhausted, minimal reserves remaining        |

**perceived_urgency** (PerceivedUrgencyValue):

| Value         | Meaning                                      |
|---------------|----------------------------------------------|
| `unhurried`   | No time pressure                             |
| `time_aware`  | Aware of schedule but not pressured          |
| `pressured`   | Active time constraint                       |
| `critical`    | Immediate deadline or emergency              |

**body_signals** (BodySignalsValue):

| Value         | Meaning                                      |
|---------------|----------------------------------------------|
| `neutral`     | No notable physical signals                  |
| `discomfort`  | Mild physical discomfort                     |
| `pain`        | Active pain experience                       |
| `unwell`      | Illness or systemic unwellness               |
| `recovering`  | Post-illness or post-exertion recovery       |

### 2.3 SignalSource

Indicates how the personal signal was obtained. This is metadata about provenance,
not about the signal content itself.

| Value            | Description                                        |
|------------------|----------------------------------------------------|
| `declared`       | User explicitly stated or selected the value             |
| `inferred`       | System inferred from user behavior (LLM-based)           |
| `inferred_local` | Inferred from local device signals (regex, sensor)       |
| `elicitation`    | User self-reported via MCP elicitation dialog mid-task   |
| `preset`         | Loaded from a saved preset profile                       |
| `decayed`        | Was active; decay has been applied to intensity          |

### 2.4 PersonalSignal

A single signal for one personal dimension.

| Field         | Type              | Required | Default     | Description                                    |
|---------------|-------------------|----------|-------------|------------------------------------------------|
| `category`    | string (enum)     | YES      | --          | Categorical value from the dimension's enum    |
| `intensity`   | integer [1-5]     | NO       | 3           | Signal strength (1=minimal, 5=strong)          |
| `source`      | SignalSource      | NO       | `declared`  | How the signal was obtained                    |
| `confidence`  | float [0.0-1.0]   | NO       | 1.0         | Confidence in the signal's accuracy            |
| `declared_at` | ISO 8601 datetime | NO       | null        | When the signal was declared (used for decay)  |
| `extended`    | string or null    | NO       | null        | Optional sub-signal (e.g., "migraine", "hunger")|

**Validation Rules:**

- `category` MUST be a valid value for the dimension it belongs to. A `cognitive_state`
  signal with category `"calm"` is invalid (that belongs to `emotional_tone`).
- `intensity` MUST be an integer between 1 and 5 inclusive.
- `confidence` MUST be a float between 0.0 and 1.0 inclusive.
- `declared_at`, when present, MUST be a valid ISO 8601 datetime string.
- `extended` is an opaque string for implementer-defined sub-signals. The protocol
  does not validate its contents beyond maximum length (256 characters).

### 2.5 PersonalContext

The container object holding signals for all five dimensions. Each dimension is
independently nullable -- a `PersonalContext` with only `cognitive_state` set and
all others null is valid.

| Field               | Type                  | Required | Description                  |
|---------------------|-----------------------|----------|------------------------------|
| `cognitive_state`   | PersonalSignal | null | NO       | Mental clarity signal        |
| `emotional_tone`    | PersonalSignal | null | NO       | Emotional register signal    |
| `energy_level`      | PersonalSignal | null | NO       | Energy level signal          |
| `perceived_urgency` | PersonalSignal | null | NO       | Time pressure signal         |
| `body_signals`      | PersonalSignal | null | NO       | Physical state signal        |

**Serialization Methods:**

- `to_simple_dict()` -- Produces a flat dictionary of `{dimension: {category, intensity} | null}` pairs, stripping metadata (source, confidence, declared_at, extended).
- `from_simple_dict(data)` -- Constructs a `PersonalContext` from a simple dictionary. Accepts both full `PersonalSignal` objects and `{category, intensity}` shorthand.
- `has_any_signal()` -- Returns true if any dimension has a non-null signal.

### 2.6 GenerationPreferences

User-steerable response style parameters, inspired by Priori-style sliders. These
are NOT personal state signals; they are explicit instructions about desired output
characteristics. They travel alongside personal context in the VCP envelope.

| Field             | Type           | Range | Description                     |
|-------------------|----------------|-------|---------------------------------|
| `depth`           | integer | null | 1-5   | Brief (1) to Detailed (5)      |
| `formality`       | integer | null | 1-5   | Casual (1) to Formal (5)       |
| `directness`      | integer | null | 1-5   | Elaborated (1) to Concise (5)  |
| `technical_level` | integer | null | 1-5   | Simple (1) to Expert (5)       |

All fields are nullable. A null value means the user has expressed no preference
for that parameter, and the system should use its default.

---

## 3. Decay Mechanics

Personal signals are temporally situated. A signal declared 4 hours ago is less
relevant than one declared 30 seconds ago. The decay system models this temporal
degradation so that stale signals lose influence gracefully.

### 3.1 DecayCurve

Three curve shapes are supported:

| Curve          | Formula                                                    | Use Case                    |
|----------------|------------------------------------------------------------|-----------------------------|
| `exponential`  | `baseline + (initial - baseline) * 0.5^(elapsed/half_life)`| Default; smooth degradation |
| `linear`       | Uniform decline over `full_decay_seconds`                  | Predictable countdown       |
| `step`         | Discrete drops at configured `(seconds, intensity)` pairs  | Phase-based transitions     |

### 3.2 DecayConfig

Per-dimension configuration for decay behavior.

| Field                   | Type              | Default       | Description                                     |
|-------------------------|-------------------|---------------|-------------------------------------------------|
| `half_life_seconds`     | float             | (required)    | Time for intensity to reach 50% of range         |
| `baseline`              | integer [1-5]     | 1             | Floor intensity; signal clears at this value     |
| `reset_on_engagement`   | boolean           | false         | Reset decay timer on user activity               |
| `curve`                 | DecayCurve        | `exponential` | Shape of the decay function                      |
| `stale_threshold`       | float [0.0-1.0]   | 0.3           | Fraction below which signal is considered stale  |
| `fresh_window_seconds`  | float             | 60.0          | Period after declaration before decay begins     |
| `pinned`                | boolean           | false         | If true, signal never decays                     |
| `full_decay_seconds`    | float | null      | null          | For LINEAR curve: time to reach baseline         |
| `step_thresholds`       | list | null        | null          | For STEP curve: list of (seconds, intensity) pairs|

### 3.3 Default Decay Configurations

These defaults are tuned to the expected temporal profiles of each dimension.

| Dimension            | Half-life   | Baseline | Stale Threshold | Fresh Window | Reset on Engagement | Curve       |
|----------------------|-------------|----------|-----------------|--------------|---------------------|-------------|
| `cognitive_state`    | 720s (12m)  | 1        | 0.3             | 60s          | true                | exponential |
| `emotional_tone`     | 1800s (30m) | 1        | 0.25            | 60s          | false               | exponential |
| `energy_level`       | 7200s (2h)  | 1        | 0.2             | 300s (5m)    | false               | exponential |
| `perceived_urgency`  | 900s (15m)  | 1        | 0.35            | 60s          | false               | exponential |
| `body_signals`       | 14400s (4h) | 1        | 0.15            | 600s (10m)   | false               | exponential |

**Design rationale:**

- **cognitive_state** decays quickly (12 minutes) because mental state shifts
  rapidly. It resets on engagement because continued interaction often refreshes
  cognitive signals.
- **emotional_tone** has a moderate half-life (30 minutes). Emotions persist longer
  than cognitive states but still shift within a session.
- **energy_level** decays slowly (2 hours) with a longer fresh window (5 minutes)
  because energy rarely changes dramatically within a single interaction.
- **perceived_urgency** decays at 15 minutes. Urgency is transient by nature.
- **body_signals** has the longest half-life (4 hours) and fresh window (10 minutes)
  because physical states change the slowest and are the most persistent.

### 3.4 Exponential Decay Formula

For the default exponential curve:

```
lambda = ln(2) / half_life_seconds
decayed_float = baseline + (declared_intensity - baseline) * e^(-lambda * elapsed_seconds)
effective_intensity = max(baseline, floor(decayed_float))
```

This produces a smooth exponential decline from `declared_intensity` toward
`baseline`, with the half-life controlling the rate. The result is floored to
produce integer intensity values.

### 3.5 Linear Decay Formula

For linear curves:

```
fraction = min(1.0, elapsed_seconds / full_decay_seconds)
decayed_float = declared_intensity - (declared_intensity - baseline) * fraction
effective_intensity = max(baseline, floor(decayed_float))
```

The signal declines uniformly from `declared_intensity` to `baseline` over exactly
`full_decay_seconds`. If `full_decay_seconds` is null or zero, the signal does
not decay.

### 3.6 Step Decay

For step curves, the `step_thresholds` list defines discrete intensity levels
at elapsed-time boundaries. Thresholds are evaluated in descending order of
`after_seconds`; the first threshold where `elapsed >= after_seconds` determines
the current intensity.

```json
{
  "curve": "step",
  "step_thresholds": [
    {"after_seconds": 0,    "intensity": 5},
    {"after_seconds": 300,  "intensity": 4},
    {"after_seconds": 900,  "intensity": 3},
    {"after_seconds": 1800, "intensity": 2},
    {"after_seconds": 3600, "intensity": 1}
  ]
}
```

If no threshold matches (elapsed < smallest `after_seconds`), the declared
intensity is returned unchanged.

---

## 4. Signal Lifecycle

### 4.1 Lifecycle States

Each active signal progresses through a defined lifecycle:

```
SET --> ACTIVE --> DECAYING --> STALE --> EXPIRED
```

| State      | Condition                                                              | Behavior                        |
|------------|------------------------------------------------------------------------|---------------------------------|
| `SET`      | `elapsed <= 0` (just declared)                                         | Full intensity, no decay        |
| `ACTIVE`   | `elapsed < fresh_window_seconds`                                       | Within fresh window, no decay   |
| `DECAYING` | `elapsed >= fresh_window_seconds` AND `effective > stale_level`        | Intensity actively declining    |
| `STALE`    | `effective <= stale_level` AND `effective > baseline`                   | Below usefulness, above floor   |
| `EXPIRED`  | `effective <= baseline`                                                 | At floor, effectively cleared   |

Where `stale_level = baseline + (declared_intensity - baseline) * stale_threshold`.

### 4.2 Pinned Signals

When `pinned = true` in the decay config, the signal never advances past `ACTIVE`.
Its intensity remains at the declared value indefinitely. This is useful for
persistent states like chronic conditions that the user has explicitly flagged.

### 4.3 Engagement Reset

When `reset_on_engagement = true`, any user interaction (message, input event)
resets the `declared_at` timestamp to the current time, restarting the decay cycle.
This is appropriate for dimensions like `cognitive_state` where continued engagement
implies the state remains current.

### 4.4 Source Transitions

When decay is applied and the effective intensity differs from the declared
intensity, the `source` field transitions to `DECAYED` to signal that the
current value reflects temporal degradation, not a fresh declaration.

---

## 5. Wire Format

### 5.1 Full PersonalSignal (JSON)

```json
{
  "category": "focused",
  "intensity": 4,
  "source": "declared",
  "confidence": 0.95,
  "declared_at": "2026-02-28T10:00:00Z",
  "extended": null
}
```

### 5.2 Full PersonalContext (JSON)

```json
{
  "cognitive_state": {
    "category": "focused",
    "intensity": 4,
    "source": "declared",
    "confidence": 0.95,
    "declared_at": "2026-02-28T10:00:00Z",
    "extended": null
  },
  "emotional_tone": {
    "category": "calm",
    "intensity": 3,
    "source": "declared",
    "confidence": 1.0,
    "declared_at": "2026-02-28T10:00:00Z",
    "extended": null
  },
  "energy_level": null,
  "perceived_urgency": {
    "category": "time_aware",
    "intensity": 2,
    "source": "inferred",
    "confidence": 0.72,
    "declared_at": "2026-02-28T09:58:00Z",
    "extended": null
  },
  "body_signals": null
}
```

### 5.3 Simple Dict Format (to_simple_dict output)

```json
{
  "cognitive_state": {"category": "focused", "intensity": 4},
  "emotional_tone": {"category": "calm", "intensity": 3},
  "energy_level": null,
  "perceived_urgency": {"category": "time_aware", "intensity": 2},
  "body_signals": null
}
```

### 5.4 VCP Context Request Envelope

Personal signals travel inside the `personal` field of a VCP context request:

```json
{
  "version": "3.1.0",
  "categorical": "location:office|social:professional|time:morning",
  "personal": {
    "cognitive_state": {
      "category": "overloaded",
      "intensity": 4,
      "source": "declared",
      "confidence": 1.0,
      "declared_at": "2026-02-28T14:30:00Z",
      "extended": null
    },
    "emotional_tone": {
      "category": "frustrated",
      "intensity": 3,
      "source": "declared",
      "confidence": 0.9,
      "declared_at": "2026-02-28T14:30:00Z",
      "extended": null
    },
    "energy_level": {
      "category": "fatigued",
      "intensity": 4,
      "source": "declared",
      "confidence": 1.0,
      "declared_at": "2026-02-28T14:30:00Z",
      "extended": null
    },
    "perceived_urgency": {
      "category": "pressured",
      "intensity": 5,
      "source": "declared",
      "confidence": 1.0,
      "declared_at": "2026-02-28T14:30:00Z",
      "extended": null
    },
    "body_signals": null
  },
  "generation_prefs": {
    "depth": 2,
    "formality": 3,
    "directness": 5,
    "technical_level": 4
  },
  "preset_id": null,
  "transition": "minor"
}
```

### 5.5 Decayed Signal Example

After 20 minutes with `cognitive_state` half-life of 720s:

```json
{
  "category": "overloaded",
  "intensity": 2,
  "source": "decayed",
  "confidence": 1.0,
  "declared_at": "2026-02-28T14:30:00Z",
  "extended": null
}
```

Calculation: `baseline(1) + (4-1) * 0.5^(1200/720) = 1 + 3 * 0.5^1.667 = 1 + 3 * 0.315 = 1.945 -> floor -> 1`

Wait -- that would be 1. Let us recalculate more carefully:

```
elapsed = 1200 seconds (20 minutes)
half_life = 720 seconds
lambda = ln(2) / 720 = 0.000963
decayed = 1 + (4 - 1) * e^(-0.000963 * 1200) = 1 + 3 * e^(-1.155)
        = 1 + 3 * 0.3149 = 1.945
floor(1.945) = 1
```

So after 20 minutes, a cognitive_state signal of intensity 4 has decayed to 1
(baseline), meaning it has EXPIRED. This is by design: cognitive state is
volatile and should refresh frequently.

A more illustrative example at 6 minutes (360 seconds):

```
decayed = 1 + (4 - 1) * e^(-0.000963 * 360) = 1 + 3 * e^(-0.3466)
        = 1 + 3 * 0.707 = 3.12
floor(3.12) = 3
```

After 6 minutes: intensity 4 has decayed to 3. Lifecycle state: DECAYING.

### 5.6 DecayConfig Wire Format

```json
{
  "half_life_seconds": 720,
  "baseline": 1,
  "reset_on_engagement": true,
  "curve": "exponential",
  "stale_threshold": 0.3,
  "fresh_window_seconds": 60,
  "pinned": false,
  "full_decay_seconds": null,
  "step_thresholds": null
}
```

---

## 6. Opacity and Downstream Consumption

### 6.1 Protection Level Mapping

Downstream systems SHOULD NOT consume raw personal signals directly. Instead,
the VCP opacity layer maps personal signals to a protection level:

| Protection Level | Criteria                                                                    | Temperature | Safety Floor |
|------------------|-----------------------------------------------------------------------------|-------------|--------------|
| `critical`       | body_signals pain/unwell at 4+, OR urgency critical at 4+                  | 0.4         | 0.3          |
| `high`           | cognitive overloaded/foggy at 4+, OR emotional frustrated at 4+            | 0.5         | 0.2          |
| `elevated`       | body_signals discomfort at 3+, OR emotional tense at 3+                    | 0.6         | 0.1          |
| `standard`       | Default / no notable signals                                               | 0.85        | 0.0          |

This opacity pattern ensures that AI systems adapt their behavior based on the
user's state without having access to the specific categorical values.

### 6.2 Generation Parameter Computation

When a protection level is available, it takes precedence over raw signal
reading. The computation produces two parameters:

- **temperature**: Controls response randomness. Lower values produce more
  deterministic, focused output appropriate for stressed or overloaded users.
- **safety_floor**: Minimum threshold for safety checks. Higher values trigger
  more cautious handling for physically or emotionally distressed users.

---

## 7. Security Considerations

### 7.1 Personal Data Classification

Personal signals constitute sensitive personal data under GDPR Article 9 and
similar frameworks. Specifically:

- **body_signals** may constitute health data (special category data).
- **emotional_tone** may constitute data about psychological state.

Implementers MUST:

1. Obtain explicit consent before collecting personal signals.
2. Apply data minimization -- only request dimensions that are needed.
3. Implement purpose limitation -- use signals only for response adaptation.
4. Provide deletion capabilities (right to erasure).
5. Encrypt personal signals at rest and in transit.

### 7.2 Opacity Principle

The opacity layer (Section 6) exists specifically to prevent unnecessary exposure
of raw personal signals to downstream systems. Implementers SHOULD:

- Pass protection levels, not raw signals, to LLM providers.
- Log protection levels, not raw signal values, in audit trails.
- Aggregate signals before sharing with third parties.

### 7.3 Inference Safety

Signals with `source: "inferred"` or `source: "inferred_local"` carry inherent
uncertainty. Implementers MUST:

- Set `confidence` appropriately (never 1.0 for inferred signals).
- Allow users to correct or dismiss inferred signals.
- Never infer `body_signals` without explicit user opt-in.

### 7.4 Non-Diagnostic Guarantee

This section restates the core design principle with normative force:

- Systems MUST NOT use personal signals to make medical, psychological, or
  diagnostic assessments.
- Systems MUST NOT route users to crisis services based solely on personal
  signals (crisis routing requires explicit user statements or constitutional
  safety rules, not ambient signal levels).
- The `extended` field MUST NOT be used to capture clinical terminology,
  ICD codes, or diagnostic labels.

### 7.5 Decay and Data Retention

Decayed and expired signals SHOULD be purged from session storage within a
reasonable timeframe (recommended: 24 hours after expiry). Implementers MUST
NOT retain personal signal history for analytics or training purposes without
explicit, separate consent.

---

## 8. Backward Compatibility

### 8.1 Legacy Prosaic Signal Migration

VCP 3.0 used four float-valued prosaic signals. The `from_legacy_prosaic` class
method on `PersonalContext` provides automatic migration:

**Field mapping:**

| VCP 3.0 Field | VCP 3.1 Dimension    | Notes                                    |
|---------------|----------------------|------------------------------------------|
| `urgency`     | `perceived_urgency`  | Direct mapping                           |
| `health`      | `body_signals`       | Direct mapping                           |
| `cognitive`   | `cognitive_state`    | Direct mapping                           |
| `affect`      | `emotional_tone`     | Direct mapping                           |
| (none)        | `energy_level`       | No v3.0 equivalent; remains null         |

**Float-to-intensity conversion:**

```
intensity = max(1, min(5, floor(float_value * 5) + 1))
```

| Float Range   | Intensity |
|---------------|-----------|
| 0.0 - 0.19    | 1         |
| 0.2 - 0.39    | 2         |
| 0.4 - 0.59    | 3         |
| 0.6 - 0.79    | 4         |
| 0.8 - 1.0     | 5         |

**Float-to-category mapping (per dimension):**

`urgency` to `perceived_urgency`:

| Float Range   | Category       |
|---------------|----------------|
| < 0.3         | `unhurried`    |
| 0.3 - 0.49    | `time_aware`   |
| 0.5 - 0.79    | `pressured`    |
| >= 0.8        | `critical`     |

`health` to `body_signals`:

| Float Range   | Category       |
|---------------|----------------|
| < 0.2         | `neutral`      |
| 0.2 - 0.39    | `discomfort`   |
| 0.4 - 0.59    | `pain`         |
| 0.6 - 0.79    | `unwell`       |
| >= 0.8        | `recovering`   |

`cognitive` to `cognitive_state`:

| Float Range   | Category       |
|---------------|----------------|
| < 0.2         | `focused`      |
| 0.2 - 0.39    | `reflective`   |
| 0.4 - 0.59    | `distracted`   |
| 0.6 - 0.79    | `foggy`        |
| >= 0.8        | `overloaded`   |

`affect` to `emotional_tone`:

| Float Range   | Category       |
|---------------|----------------|
| < 0.2         | `calm`         |
| 0.2 - 0.39    | `neutral`      |
| 0.4 - 0.59    | `tense`        |
| 0.6 - 0.79    | `frustrated`   |
| >= 0.8        | `uplifted`     |

### 8.2 Wire-Format Backward Compatibility

The VCP context request accepts both `personal` (v3.1) and `prosaic` (v3.0)
field names. When `prosaic` is provided but `personal` is absent, the system
transparently maps `prosaic` to `personal`. The `prosaic` field is marked
deprecated and will be removed in VCP 4.0.

### 8.3 Legacy Type Aliases

For code-level backward compatibility, the following aliases are maintained:

| Legacy Name        | Current Name       |
|--------------------|--------------------|
| `ProsaicSignalType`| `PersonalDimension`|
| `ProsaicSignal`    | `PersonalSignal`   |
| `ProsaicContext`   | `PersonalContext`  |

These aliases are deprecated and will be removed in VCP 4.0.

---

## 9. Conformance

### 9.1 Conformance Levels

| Level    | Requirements                                                              |
|----------|---------------------------------------------------------------------------|
| Minimal  | Accept and pass through PersonalContext without processing                |
| Standard | Apply decay, compute lifecycle states, map to protection levels           |
| Full     | Standard + generation parameter computation, opacity layer, audit logging |

### 9.2 Required Behaviors

All conforming implementations MUST:

1. Validate `category` values against the correct dimension enum.
2. Reject `intensity` values outside the [1, 5] range.
3. Reject `confidence` values outside the [0.0, 1.0] range.
4. Treat null dimension fields as "no signal" (not as "signal with default value").
5. Honor the non-diagnostic principle (Section 7.4).

### 9.3 Optional Behaviors

Conforming implementations MAY:

1. Override default decay configurations per dimension.
2. Implement custom decay curves beyond the three defined types.
3. Extend the `extended` field with domain-specific sub-signal vocabularies.
4. Implement preset management for commonly-used signal configurations.

---

## 10. References

| Reference                | Description                                                |
|--------------------------|------------------------------------------------------------|
| VCP Core 3.1.0           | Base protocol specification                                |
| `services/vcp/models.py` | Reference implementation (Python / Pydantic)               |
| VCP-X-Relational         | Companion extension for relational context (Layer 5)       |
| GDPR Article 9           | Special categories of personal data                        |
| Priori                   | Inspiration for GenerationPreferences slider model         |

---

## Appendix A: StepThreshold Schema

A step threshold is a pair of `(after_seconds, intensity)` defining a discrete
intensity level that activates after a specified number of seconds.

```json
{
  "after_seconds": 300,
  "intensity": 4
}
```

- `after_seconds` MUST be a non-negative number.
- `intensity` MUST be an integer between 1 and 5 inclusive.
- Thresholds SHOULD be provided in ascending order of `after_seconds`.

## Appendix B: Preset Profiles

A preset profile is a named collection of personal signals that can be activated
with a single `preset_id` reference. When a preset is activated:

1. All signals from the preset are applied with `source: "preset"`.
2. `declared_at` is set to the activation timestamp.
3. Existing signals on the same dimensions are overwritten.
4. Dimensions not covered by the preset are left unchanged.

Example preset "deep_work":

```json
{
  "preset_id": "deep_work",
  "signals": {
    "cognitive_state": {"category": "focused", "intensity": 5},
    "emotional_tone": {"category": "calm", "intensity": 4},
    "energy_level": {"category": "rested", "intensity": 4},
    "perceived_urgency": {"category": "unhurried", "intensity": 1},
    "body_signals": null
  }
}
```

## Appendix C: Change Log

| Version | Date       | Changes                                          |
|---------|------------|--------------------------------------------------|
| 1.0.0   | 2026-02-28 | Initial stable release, replaces VCP 3.0 prosaic |
