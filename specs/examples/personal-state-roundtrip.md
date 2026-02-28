# Wire Format Example: Personal State Roundtrip

**VCP Version**: 3.1
**Extension**: VCP-X-Personal
**Purpose**: Demonstrates encoding personal state, transmitting it, decoding it, and applying decay over time.

---

## Scenario

A user starts a work session feeling focused and pressured. Over 30 minutes, urgency decays while cognitive state remains fresh due to engagement resets.

---

## Step 1: User Declares Personal State

The user sets their state via the client interface at T=0 (10:00 AM):

```json
{
  "signals": {
    "cognitive_state": {
      "category": "cognitive_state",
      "value": "focused",
      "intensity": 4,
      "source": "declared",
      "confidence": 0.95,
      "declared_at": "2026-02-28T10:00:00Z"
    },
    "perceived_urgency": {
      "category": "perceived_urgency",
      "value": "pressured",
      "intensity": 4,
      "source": "declared",
      "confidence": 0.9,
      "declared_at": "2026-02-28T10:00:00Z"
    },
    "energy_level": {
      "category": "energy_level",
      "value": "rested",
      "intensity": 3,
      "source": "declared",
      "confidence": 0.8,
      "declared_at": "2026-02-28T10:00:00Z"
    }
  },
  "preset_id": null
}
```

**Annotations**:
- Only declared dimensions are sent; undeclared dimensions have no signal (not "neutral")
- `intensity` is 1-5 integer scale: 1=barely present, 5=dominant
- `source: "declared"` means the user explicitly set this value
- `confidence` reflects the source's reliability (declared = high confidence)

---

## Step 2: Encoding for Transport

The personal state is encrypted at rest in the VCP context state manager:

```
# Plaintext (before encryption):
{"cognitive_state": {"value": "focused", "intensity": 4, "source": "declared", ...}}

# Encrypted (in Redis):
enc:gAAAAABnwV...  (Fernet ciphertext with enc: prefix)
```

The VCP bundle transmits only the protection level to the inference model:

```json
{
  "model_safe_context": {
    "protection_level": "STANDARD",
    "formality_level": 3,
    "domain": "professional",
    "session_active": true
  }
}
```

**Key principle**: Raw personal signals (focused, pressured, rested) NEVER reach the inference model. Only the computed `protection_level` is exposed. The context opacity layer ensures this separation.

---

## Step 3: Decay at T+15 Minutes (10:15 AM)

No user engagement has occurred. Both signals are decaying.

### Cognitive State Decay

Default config: `half_life=720s (12min), curve=exponential, fresh_window=60s, baseline=1`

```
elapsed = 900s (15 minutes)
fresh_window = 60s → decay has been active for 840s
effective_elapsed = 840s

decayed_intensity = baseline + (initial - baseline) × 0.5^(elapsed / half_life)
                  = 1 + (4 - 1) × 0.5^(840 / 720)
                  = 1 + 3 × 0.5^1.167
                  = 1 + 3 × 0.446
                  = 1 + 1.338
                  = 2.338

lifecycle_state = DECAYING (above stale_threshold of 0.3 × (4-1) + 1 = 1.9)
```

### Perceived Urgency Decay

Default config: `half_life=900s (15min), curve=exponential, fresh_window=60s, baseline=1`

```
elapsed = 900s
effective_elapsed = 840s

decayed_intensity = 1 + (4 - 1) × 0.5^(840 / 900)
                  = 1 + 3 × 0.5^0.933
                  = 1 + 3 × 0.524
                  = 1 + 1.572
                  = 2.572

lifecycle_state = DECAYING
```

### Current State at T+15min

```json
{
  "signals": {
    "cognitive_state": {
      "category": "cognitive_state",
      "value": "focused",
      "intensity": 2.338,
      "source": "decayed",
      "lifecycle_state": "DECAYING",
      "original_intensity": 4,
      "declared_at": "2026-02-28T10:00:00Z"
    },
    "perceived_urgency": {
      "category": "perceived_urgency",
      "value": "pressured",
      "intensity": 2.572,
      "source": "decayed",
      "lifecycle_state": "DECAYING",
      "original_intensity": 4,
      "declared_at": "2026-02-28T10:00:00Z"
    },
    "energy_level": {
      "category": "energy_level",
      "value": "rested",
      "intensity": 2.190,
      "source": "decayed",
      "lifecycle_state": "DECAYING",
      "original_intensity": 3,
      "declared_at": "2026-02-28T10:00:00Z"
    }
  }
}
```

---

## Step 4: Engagement Reset at T+16 Minutes

The user sends a message, triggering an engagement event. Cognitive state resets because `reset_on_engagement: true`:

```json
{
  "cognitive_state": {
    "category": "cognitive_state",
    "value": "focused",
    "intensity": 4,
    "source": "declared",
    "lifecycle_state": "ACTIVE",
    "declared_at": "2026-02-28T10:16:00Z"
  }
}
```

Perceived urgency does NOT reset — it continues decaying. The `reset_on_engagement` flag is per-dimension.

---

## Step 5: Staleness at T+45 Minutes (10:45 AM)

After 45 minutes with no further updates, perceived urgency has gone stale:

```
elapsed = 2700s (45 minutes)
effective_elapsed = 2640s

urgency_decayed = 1 + (4 - 1) × 0.5^(2640 / 900)
               = 1 + 3 × 0.5^2.933
               = 1 + 3 × 0.131
               = 1 + 0.393
               = 1.393

stale_threshold_value = baseline + stale_threshold × (initial - baseline)
                      = 1 + 0.35 × (4 - 1)
                      = 1 + 1.05
                      = 2.05

1.393 < 2.05 → lifecycle_state = STALE
```

```json
{
  "perceived_urgency": {
    "category": "perceived_urgency",
    "value": "pressured",
    "intensity": 1.393,
    "source": "decayed",
    "lifecycle_state": "STALE",
    "original_intensity": 4,
    "declared_at": "2026-02-28T10:00:00Z"
  }
}
```

Stale signals are still available but clients SHOULD treat them with reduced confidence.

---

## Lifecycle State Diagram

```
 ┌─────────┐   fresh_window   ┌────────┐   decay starts   ┌──────────┐
 │   SET   │ ───────────────> │ ACTIVE │ ───────────────> │ DECAYING │
 └─────────┘    elapsed       └────────┘                  └──────────┘
                                  ^                            │
                                  │     engagement reset       │
                                  └────────────────────────────┤
                                                               │
                                             below threshold   │
                                                               v
                                                          ┌─────────┐
                                                          │  STALE  │
                                                          └─────────┘
                                                               │
                                              at baseline      │
                                                               v
                                                          ┌─────────┐
                                                          │ EXPIRED │
                                                          └─────────┘
```

---

## Decay Curve Comparison

For an initial intensity of 4 (baseline=1), 12-minute half-life:

| Minutes | Exponential | Linear (full_decay=60min) | Step (thresholds: 5m→3, 15m→2, 30m→1) |
|---------|-------------|---------------------------|----------------------------------------|
| 0       | 4.000       | 4.000                     | 4                                      |
| 5       | 3.117       | 3.750                     | 3                                      |
| 10      | 2.459       | 3.500                     | 3                                      |
| 15      | 1.968       | 3.250                     | 2                                      |
| 20      | 1.608       | 3.000                     | 2                                      |
| 30      | 1.152       | 2.500                     | 1                                      |
| 60      | 1.003       | 1.000                     | 1                                      |

---

## Key Invariants

1. Decayed intensity NEVER drops below `baseline` (floor of 1)
2. `source` changes from `"declared"` to `"decayed"` once decay starts
3. Categorical `value` does NOT change during decay — only intensity changes
4. Engagement resets only apply to dimensions with `reset_on_engagement: true`
5. Pinned signals (`pinned: true`) never decay regardless of elapsed time
6. The decay formula is pure: given (initial, elapsed, config), the result is deterministic
