# VCP-X-Intent: Heuristic Intent Inference Extension

**Status**: EXPERIMENTAL
**Version**: 0.1.0
**Depends on**: VCP-X-Personal (v1.0+)
**Project-maintained implementation**: `services/vcp/intent_inference.py`

> Wire format and inference rules may change without notice while this extension
> remains EXPERIMENTAL. Implementations SHOULD flag intent classifications as
> heuristic and correctable.

---

## 1. Overview

VCP-X-Intent infers user intent from VCP context signals using rule-based
heuristics. It requires no LLM call -- intent is derived entirely from the
categorical and personal state dimensions already present in the VCP context
request. The result is an InterpretiveFrame: a primary intent classification
with confidence score, up to three ranked alternatives, and a mechanism for
user correction.

This extension is inspired by Priori.chat's visible intent classification. The
core design principle is **transparency**: the system's interpretation of intent
is always visible to the user, the reasoning is always stated, and the user can
always override it.


## 2. Data Model

### 2.1 IntentCategory

An enumeration of 10 intent categories. These are mutually exclusive at the
primary classification level; alternatives provide ranked fallbacks.

| Value                    | Description                                             |
|--------------------------|---------------------------------------------------------|
| `professional_inquiry`   | Work-related question or task in a professional context |
| `urgent_task`            | Time-sensitive task requiring efficient completion      |
| `personal_exploration`   | Open-ended personal reflection or inquiry               |
| `emotional_processing`   | Emotional support or processing needed                  |
| `health_check`           | Health-related concern or symptom discussion             |
| `casual_conversation`    | Low-stakes social interaction                           |
| `crisis_support`         | Acute crisis requiring immediate, careful response      |
| `creative_work`          | Creative ideation, writing, or artistic collaboration   |
| `learning`               | Knowledge acquisition or skill development              |
| `routine_check`          | Habitual check-in with no strong directional signal     |

### 2.2 IntentInterpretation

A single intent reading with confidence and reasoning.

| Field                      | Type                | Required | Description                                                     |
|----------------------------|---------------------|----------|-----------------------------------------------------------------|
| `category`                 | IntentCategory      | Yes      | The inferred intent category.                                   |
| `confidence`               | number (0.0 -- 1.0) | Yes      | Confidence in this classification. Higher is more confident.    |
| `reasoning`                | string              | Yes      | Human-readable explanation of why this intent was inferred. Maximum 200 characters. |
| `contributing_dimensions`  | array of string     | Yes      | List of PersonalDimension names or VCP/A situational dimension names (e.g., `location`, `activity`) that contributed to this inference. May be empty for default/fallback classifications. |

### 2.3 InterpretiveFrame

The complete intent inference result.

| Field             | Type                            | Required | Description                                                     |
|-------------------|---------------------------------|----------|-----------------------------------------------------------------|
| `primary`         | IntentInterpretation            | Yes      | The highest-confidence intent classification.                   |
| `alternatives`    | array of IntentInterpretation   | Yes      | Up to 3 additional ranked classifications. May be empty.        |
| `user_correction` | IntentCategory or null          | No       | If the user overrode the primary classification, the corrected category. Default: null. |


## 3. Inference Rules

Intent is inferred by evaluating the personal state dimensions from VCP-X-Personal
and any categorical signals from the VCP context request. Rules are evaluated in
priority order. All matching rules produce candidate IntentInterpretations; the
candidate with the highest confidence becomes the primary classification.

### 3.1 Rule Evaluation Order

Rules are listed in priority order. When multiple rules match, all candidates
are collected, deduplicated by category (keeping the highest-confidence entry
for each category), and sorted by confidence descending.

| Priority | Condition                                                                     | Category               | Confidence | Reasoning                                                        |
|----------|-------------------------------------------------------------------------------|------------------------|------------|------------------------------------------------------------------|
| 1        | `perceived_urgency.category == "critical"` AND `intensity >= 4`               | CRISIS_SUPPORT         | 0.9        | Critical urgency signal detected -- prioritizing crisis support  |
| 2        | `perceived_urgency.category == "pressured"` AND workplace signals present     | URGENT_TASK            | 0.75       | Time pressure detected -- likely needs efficient task completion |
| 2b       | `perceived_urgency.category == "pressured"` (no workplace signals)            | URGENT_TASK            | 0.6        | Time pressure detected -- likely needs efficient task completion |
| 3        | `body_signals.category in {"pain", "unwell"}` AND `intensity >= 3`            | HEALTH_CHECK           | 0.75       | Pain or unwellness signals suggest health-related intent         |
| 4        | `emotional_tone.category in {"frustrated", "tense"}` AND `intensity >= 4`     | EMOTIONAL_PROCESSING   | 0.7        | High emotional intensity suggests processing or support needed   |
| 5        | Workplace or colleagues signals AND `cognitive_state.category == "focused"`   | PROFESSIONAL_INQUIRY   | 0.85       | Workplace context suggests professional interaction              |
| 5b       | Workplace or colleagues signals (without focused cognition)                   | PROFESSIONAL_INQUIRY   | 0.7        | Workplace context suggests professional interaction              |
| 6        | Home or evening signals AND `emotional_tone.category == "calm"` AND `cognitive_state.category == "reflective"` | PERSONAL_EXPLORATION | 0.75 | Relaxed personal context suggests exploratory interaction |
| 6b       | Home or evening signals AND `emotional_tone.category == "calm"`               | PERSONAL_EXPLORATION   | 0.7        | Relaxed personal context suggests exploratory interaction        |
| 6c       | Home or evening signals (alone)                                               | PERSONAL_EXPLORATION   | 0.55       | Relaxed personal context suggests exploratory interaction        |
| 7        | `emotional_tone.category == "uplifted"`                                       | CREATIVE_WORK          | 0.55       | Positive emotional state may indicate creative intent            |
| 8        | `cognitive_state.category == "focused"` AND no candidate has confidence >= 0.7 | LEARNING              | 0.5        | Focused cognitive state with no stronger signals suggests learning|
| 9        | No urgency OR `perceived_urgency.category == "unhurried"`, no workplace, AND no candidate has confidence >= 0.6 | CASUAL_CONVERSATION | 0.4 | No strong contextual signals -- defaulting to casual interaction |
| 10       | No candidates matched                                                         | ROUTINE_CHECK          | 0.3        | Insufficient context for specific intent classification          |

### 3.2 Categorical Signal Extraction

Categorical signals are extracted from two sources in the VCP context request:

1. **JSON format** (`categorical_json`): A map of signal categories to value
   arrays. All values are lowercased for matching. Both keys and values are
   added to the signal set.

2. **Wire format** (`categorical`): A compact string with emoji-encoded
   keywords. The following mappings are recognized:

   | Signal     | Wire indicators          |
   |------------|--------------------------|
   | workplace  | `office`, emoji `U+1F3E2` |
   | home       | `home`, emoji `U+1F3E0`   |
   | colleagues | `colleagues`, emoji `U+1F454` |
   | evening    | `evening`, emoji `U+1F305` |
   | morning    | `morning`, emoji `U+1F304` |

### 3.3 Deduplication

After all rules have been evaluated, candidates are deduplicated by category.
If two rules produce candidates with the same IntentCategory, the one with the
higher confidence is retained and the other is discarded.


## 4. User Correction

The InterpretiveFrame includes a `user_correction` field. When the user
explicitly states their intent or selects a different category:

1. Set `user_correction` to the user-specified IntentCategory.
2. The corrected category becomes the effective primary intent for all
   downstream processing.
3. The original `primary` and `alternatives` are preserved for audit and
   calibration purposes.

Implementations SHOULD present the inferred intent to the user in a
non-intrusive, correctable format (e.g., a label with a dropdown override).


## 5. Wire Format

When transmitted via VCP, the intent payload appears in the `extensions` map:

```json
{
  "extensions": {
    "VCP-X-Intent": {
      "primary": {
        "category": "professional_inquiry",
        "confidence": 0.85,
        "reasoning": "Workplace context suggests professional interaction",
        "contributing_dimensions": ["location", "activity", "cognitive_state"]
      },
      "alternatives": [
        {
          "category": "urgent_task",
          "confidence": 0.6,
          "reasoning": "Time pressure detected -- likely needs efficient task completion",
          "contributing_dimensions": ["perceived_urgency"]
        },
        {
          "category": "learning",
          "confidence": 0.5,
          "reasoning": "Focused cognitive state with no stronger signals suggests learning",
          "contributing_dimensions": ["cognitive_state"]
        }
      ],
      "user_correction": null
    }
  }
}
```


## 6. Design Principles

### 6.1 Transparency Over Accuracy

Intent inference is inherently uncertain. VCP-X-Intent prioritizes making the
system's interpretation visible and correctable over achieving high accuracy.
A wrong inference that the user can see and fix is strictly preferable to a
hidden inference that silently shapes the response.

### 6.2 No LLM Required

All inference is rule-based. This makes intent classification deterministic,
auditable, and free of latency or cost from additional model calls. The
confidence scores are calibrated heuristics, not model-derived probabilities.

### 6.3 Graceful Degradation

When personal state dimensions are absent or sparse, the system falls back to
lower-confidence classifications. The CASUAL_CONVERSATION and ROUTINE_CHECK
categories serve as default fallbacks, ensuring every context request receives
a classification.

### 6.4 Dimensional Provenance

Each IntentInterpretation lists the dimensions that contributed to the
classification. This provides a traceable chain from input signals to output
intent, supporting both user understanding and system debugging.


## 7. Security Considerations

- **Intent manipulation**: Adversarial users could craft VCP context signals to
  trigger specific intent classifications. Since intent is transparent and
  correctable, this has limited impact -- the user sees the result.
- **Privacy**: Intent categories are derived from context dimensions already
  present in the VCP payload. VCP-X-Intent does not introduce new data
  collection.
- **Crisis detection**: The CRISIS_SUPPORT category triggers at high confidence
  (0.9) for critical urgency. Implementations SHOULD treat this as a safety
  signal and adjust response handling accordingly (e.g., routing to appropriate
  support resources).


## 8. Conformance

An implementation conforms to VCP-X-Intent if it:

1. Implements all 14 rules (10 categories) in the Section 3.1 table.
2. Correctly deduplicates candidates per Section 3.3.
3. Returns at most 3 alternatives in addition to the primary.
4. Preserves user corrections without discarding original classifications.
5. Advertises `"status": "experimental"` in its VCP-X-Intent capability object (the optional per-extension `status` key of `specs/core/capability-negotiation.md` §7.5).
6. Ignores unrecognized fields in InterpretiveFrame payloads.


## 9. Changelog

| Version | Date       | Changes                                             |
|---------|------------|-----------------------------------------------------|
| 0.1.0   | 2026-02-28 | Initial experimental release with 10 inference rules. |
