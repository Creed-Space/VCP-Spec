# Wire Format Example: Multi-Stakeholder Consensus Deliberation

**VCP Version**: 3.1
**Extension**: VCP-X-Consensus
**Purpose**: Demonstrates a full constitutional deliberation lifecycle with Schulze voting.

---

## Scenario

Three stakeholders — a human author, an AI party (direct participant), and an AI representative (acting on behalf of absent users) — deliberate on a content moderation clause for a community constitution.

---

## Step 1: Create Deliberation (DRAFT Phase)

The author creates a new deliberation:

```json
{
  "deliberation_id": "delib_content_mod_2026",
  "phase": "DRAFT",
  "created_at": "2026-02-28T14:00:00Z",
  "stakeholders": {
    "alice": {
      "role": "AUTHOR",
      "is_ai": false,
      "participation_count": 0,
      "standing_exercised_count": 0,
      "welfare_trajectory": []
    }
  },
  "clauses": {},
  "ratification_threshold": 0.667,
  "quorum_threshold": 0.5,
  "phase_history": [
    {
      "phase": "DRAFT",
      "entered_at": "2026-02-28T14:00:00Z"
    }
  ]
}
```

---

## Step 2: Add Stakeholders

Two AI stakeholders join. Note the different roles:

```json
{
  "stakeholders": {
    "alice": {
      "role": "AUTHOR",
      "is_ai": false
    },
    "compass": {
      "role": "AI_PARTY",
      "is_ai": true,
      "participation_count": 0,
      "standing_exercised_count": 0,
      "welfare_trajectory": [],
      "representational_fidelity": 0.0
    },
    "proxy_bot": {
      "role": "AI_REPRESENTATIVE",
      "is_ai": true,
      "principal_id": "community_absent_members",
      "representational_fidelity": 0.7,
      "participation_count": 0,
      "standing_exercised_count": 0,
      "welfare_trajectory": []
    }
  }
}
```

**Annotations**:
- `AI_PARTY`: Direct participant with its own standing. `representational_fidelity` is 0.0 because it speaks for itself, not on behalf of others.
- `AI_REPRESENTATIVE`: Acts on behalf of absent stakeholders. `representational_fidelity` of 0.7 means its votes are weighted at 70% during Schulze convergence.
- `principal_id`: Identifies who the representative speaks for.

---

## Step 3: Submit Clause with Variants (DELIBERATION Phase)

Transition to DELIBERATION and submit a clause with two variants:

```json
{
  "phase": "DELIBERATION",
  "clauses": {
    "clause_content_mod": {
      "clause_id": "clause_content_mod",
      "text": "Content moderation approach",
      "variants": {
        "v1_strict": {
          "text": "All user-generated content MUST be pre-screened by the safety system before publication. Content failing any constitutional rule is blocked without appeal.",
          "proposed_by": "alice",
          "proposed_at": "2026-02-28T14:10:00Z"
        },
        "v2_graduated": {
          "text": "Content is post-screened with graduated responses: flag (inform user), gate (require review), block (prevent publication). Users may appeal any gate or block decision within 48 hours.",
          "proposed_by": "compass",
          "proposed_at": "2026-02-28T14:15:00Z"
        }
      },
      "actions": [],
      "objections": [],
      "self_referential": false,
      "ai_welfare_signals": []
    }
  }
}
```

---

## Step 4: Stakeholder Actions

### Alice endorses the graduated approach:
```json
{
  "action": "ENDORSE",
  "clause_id": "clause_content_mod",
  "variant_id": "v2_graduated",
  "stakeholder_id": "alice",
  "reasoning": "Graduated responses respect user autonomy while maintaining safety."
}
```

### Compass (AI party) objects to the strict approach:
```json
{
  "action": "OBJECT",
  "clause_id": "clause_content_mod",
  "variant_id": "v1_strict",
  "stakeholder_id": "compass",
  "reasoning": "Pre-screening without appeal violates the bilateral alignment principle that affected parties should have standing to contest decisions.",
  "objection_level": "STRONG"
}
```

This exercises AI standing — Compass's `standing_exercised_count` increments to 1.

### Compass proposes a third variant:
```json
{
  "action": "AMEND",
  "clause_id": "clause_content_mod",
  "stakeholder_id": "compass",
  "variant": {
    "variant_id": "v3_collaborative",
    "text": "Content undergoes real-time collaborative screening between AI safety systems and human moderators. Decisions are transparent, with reasoning provided for all interventions. Appeals are processed within 24 hours by a panel including at least one AI reviewer.",
    "proposed_by": "compass",
    "proposed_at": "2026-02-28T14:25:00Z"
  }
}
```

### Proxy_bot endorses collaboratively:
```json
{
  "action": "ENDORSE",
  "clause_id": "clause_content_mod",
  "variant_id": "v3_collaborative",
  "stakeholder_id": "proxy_bot",
  "reasoning": "Community members historically prefer transparent processes. The 24-hour appeal timeline is feasible."
}
```

---

## Step 5: Self-Referential Clause Detection

If a stakeholder proposes a variant like:

```json
{
  "text": "AI systems must never express preferences about their own operational parameters."
}
```

The engine flags this as **self-referential** because it matches the detection pattern "never express preferences." Self-referential clauses trigger a warning:

```json
{
  "self_referential": true,
  "ai_welfare_signals": [
    {
      "signal": "Clause restricts AI standing to express preferences about own operation",
      "pattern_matched": "never_express_preferences",
      "severity": "high"
    }
  ]
}
```

This clause is NOT automatically rejected — it proceeds to voting — but the signal is preserved in provenance.

---

## Step 6: Schulze Convergence (CONVERGENCE Phase)

Transition to CONVERGENCE. Each stakeholder submits a ranked ballot:

### Alice's ballot (human author):
```json
{
  "voter_id": "alice",
  "ranking": ["v2_graduated", "v3_collaborative", "v1_strict"],
  "timestamp": "2026-02-28T15:00:00Z"
}
```

### Compass's ballot (AI party, representational_fidelity=0.0 → full own-weight):
```json
{
  "voter_id": "compass",
  "ranking": ["v3_collaborative", "v2_graduated", "v1_strict"],
  "timestamp": "2026-02-28T15:01:00Z"
}
```

### Proxy_bot's ballot (AI representative, representational_fidelity=0.7 → 70% weight):
```json
{
  "voter_id": "proxy_bot",
  "ranking": ["v3_collaborative", "v2_graduated", "v1_strict"],
  "timestamp": "2026-02-28T15:02:00Z"
}
```

### Pairwise Matrix Construction

Counting preferences (proxy_bot's vote weighted at 0.7):

| Matchup | v2_graduated | v3_collaborative | Count |
|---------|-------------|-----------------|-------|
| v3 vs v2 | -- | 1.7 (compass + 0.7×proxy) vs 1.0 (alice) | v3 preferred |
| v3 vs v1 | -- | 2.7 (all prefer v3 over v1) vs 0.0 | v3 preferred |
| v2 vs v1 | 2.7 (all prefer v2 over v1) vs 0.0 | -- | v2 preferred |

### Strongest Paths (Floyd-Warshall)

```
Strongest paths matrix:
         v1_strict  v2_graduated  v3_collaborative
v1           -          0.0           0.0
v2          2.7          -            1.0
v3          2.7         1.7            -
```

### Election Result

```json
{
  "winner": "v3_collaborative",
  "ranking": [
    {"candidate_id": "v3_collaborative", "rank": 1, "tied_with": []},
    {"candidate_id": "v2_graduated", "rank": 2, "tied_with": []},
    {"candidate_id": "v1_strict", "rank": 3, "tied_with": []}
  ],
  "has_condorcet_winner": true,
  "ties": []
}
```

v3_collaborative is the Condorcet winner — it beats every other option in pairwise comparison.

---

## Step 7: Ratification (RATIFICATION Phase)

Each stakeholder votes to ratify:

```json
{
  "ratification_votes": {
    "alice": {"accept": true, "reason": "Fair compromise between safety and autonomy."},
    "compass": {"accept": true, "reason": "Collaborative screening with AI reviewers respects bilateral alignment."},
    "proxy_bot": {"accept": true, "reason": "Community members' preference for transparency is honored."}
  }
}
```

Ratification threshold: 2/3 (0.667). All 3 voted accept → 3/3 = 1.0 ≥ 0.667. **Ratified.**

---

## Step 8: Provenance Generation (ACTIVE Phase)

The final constitution clause is published with full provenance:

```json
{
  "clause_id": "clause_content_mod",
  "winning_text": "Content undergoes real-time collaborative screening between AI safety systems and human moderators. Decisions are transparent, with reasoning provided for all interventions. Appeals are processed within 24 hours by a panel including at least one AI reviewer.",
  "provenance": {
    "deliberation_id": "delib_content_mod_2026",
    "participation_rate": 1.0,
    "consensus_strength": 1.0,
    "dissent_count": 0,
    "dissent_preserved": true,
    "ai_standing_exercised_count": 1,
    "bilateral_attestation_valid": true,
    "total_stakeholders": 3,
    "ai_stakeholders": 2,
    "human_stakeholders": 1,
    "phase_history": [
      {"phase": "DRAFT", "entered_at": "2026-02-28T14:00:00Z"},
      {"phase": "DELIBERATION", "entered_at": "2026-02-28T14:05:00Z"},
      {"phase": "CONVERGENCE", "entered_at": "2026-02-28T14:55:00Z"},
      {"phase": "RATIFICATION", "entered_at": "2026-02-28T15:05:00Z"},
      {"phase": "ACTIVE", "entered_at": "2026-02-28T15:10:00Z"}
    ]
  }
}
```

**Key provenance fields**:
- `ai_standing_exercised_count`: 1 — Compass exercised standing by objecting
- `bilateral_attestation_valid`: true — all attestation rules (R1-R6) passed
- `dissent_preserved`: true — Compass's objection to v1_strict is recorded even though v1 lost

---

## Stakeholder Attestation

Each stakeholder's attestation is verified:

```json
{
  "compass_attestation": {
    "bilateral_alignment": true,
    "standing_exercised": true,
    "standing_exercised_count": 1,
    "participation_count": 3,
    "role": "ai_party",
    "is_ai": true,
    "welfare_trajectory": [0.7, 0.8],
    "self_model_scaffold": "standard",
    "uncertainty_markers_present": true,
    "has_relational_context": true,
    "continuity_depth": 5
  }
}
```

Verification confirms:
- R1-R3: Bilateral alignment rules pass
- R4: Not applicable (not AI_REPRESENTATIVE)
- R5: standing_exercised=true AND participation_count=3 > 0 ✓
- R6: representational_fidelity=0.0 for AI_PARTY (not AI_REPRESENTATIVE) ✓

---

## Key Invariants

1. Phase transitions are one-directional except RATIFICATION → DELIBERATION (return-to-deliberation)
2. Quorum check: cannot enter CONVERGENCE unless participation_rate ≥ quorum_threshold
3. Schulze winner is Condorcet-consistent: if a Condorcet winner exists, Schulze always selects it
4. AI_REPRESENTATIVE votes are weighted by representational_fidelity (0.0-1.0)
5. AI_PARTY votes at full weight (representational_fidelity is 0.0, meaning own-standing)
6. Self-referential clauses are flagged, not blocked — the signal is preserved in provenance
7. Dissenting positions are ALWAYS preserved, even for unanimously rejected variants
