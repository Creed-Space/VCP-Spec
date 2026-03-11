# Wire Format Example: CSM-1 Encode and Decode

**VCP Version**: 3.1
**Layer**: VCP/S (Semantics)
**Purpose**: Step-by-step walkthrough of creating, encoding, and decoding a CSM-1 constitutional profile token.

---

## Scenario

A mental health support application needs to encode a constitutional profile that emphasizes empathy, transparency, and age-appropriate interactions for a minor user.

---

## Step 1: Define the Constitutional Profile

The profile consists of dimensional values across CSM-1's standard categories:

```json
{
  "persona": "supportive_companion",
  "dimensions": {
    "empathy": "high",
    "transparency": "high",
    "formality": "medium",
    "directness": "medium",
    "technical_depth": "low",
    "safety_posture": "elevated"
  },
  "scope": {
    "domain": "mental_health",
    "audience": "minor",
    "region": "GB"
  },
  "constraints": [
    "NEVER provide medical diagnoses",
    "ALWAYS suggest professional help for crisis indicators",
    "MUST use age-appropriate language"
  ]
}
```

---

## Step 2: CSM-1 Compact Encoding

CSM-1 encodes the profile into a compact wire format using emoji-based categorical markers and shortcodes:

### Categorical Wire Format

Each dimension maps to an emoji marker and value:

```
🧑‍⚕️:💬:🔒:🌙:🏠:👤:📱:🧘:🇬🇧
```

Reading left to right:
| Position | Emoji | Meaning |
|----------|-------|---------|
| 1 | 🧑‍⚕️ | Domain: health/wellness |
| 2 | 💬 | Mode: conversational |
| 3 | 🔒 | Safety: elevated |
| 4 | 🌙 | Time context: evening |
| 5 | 🏠 | Setting: home |
| 6 | 👤 | Audience: individual |
| 7 | 📱 | Device: mobile |
| 8 | 🧘 | Activity: wellbeing |
| 9 | 🇬🇧 | Region: Great Britain |

### Full CSM-1 Token

The complete CSM-1 token combines the compact code with metadata:

```
csm1:supportive_companion:EH-TH-FM-DM-TL-SE:🧑‍⚕️:💬:🔒:🌙:🏠:👤:📱:🧘:🇬🇧
```

Breaking down the segments:
| Segment | Value | Description |
|---------|-------|-------------|
| Prefix | `csm1` | CSM-1 format identifier |
| Persona | `supportive_companion` | Named persona profile |
| Dimension codes | `EH-TH-FM-DM-TL-SE` | Shortcodes for each dimension value |
| Categorical wire | `🧑‍⚕️:💬:🔒:...` | 9-position situational context |

### Dimension Shortcodes

Each two-character code encodes a dimension and level:

| Code | Dimension | Level |
|------|-----------|-------|
| `EH` | Empathy: High |
| `TH` | Transparency: High |
| `FM` | Formality: Medium |
| `DM` | Directness: Medium |
| `TL` | Technical depth: Low |
| `SE` | Safety posture: Elevated |

---

## Step 3: Signing the Token

The CSM-1 token is embedded in a VCP bundle with cryptographic signature:

```json
{
  "manifest": {
    "version": "3.1",
    "issuer": "creed:org:mental_health_app",
    "issued_at": "2026-02-28T14:00:00Z",
    "expires_at": "2026-03-01T14:00:00Z",
    "jti": "tok_8f3k2m9xp4",
    "content_hash": "sha256:a1b2c3d4e5f6...",
    "signature_algorithm": "Ed25519"
  },
  "content": {
    "csm1": "csm1:supportive_companion:EH-TH-FM-DM-TL-SE:🧑‍⚕️:💬:🔒:🌙:🏠:👤:📱:🧘:🇬🇧",
    "constraints": [
      "NEVER provide medical diagnoses",
      "ALWAYS suggest professional help for crisis indicators",
      "MUST use age-appropriate language"
    ]
  },
  "signature": "base64url_ed25519_signature..."
}
```

---

## Step 4: Verification at the Orchestration Layer

When the receiving system gets this bundle, it verifies:

1. **Signature verification**: Ed25519 signature validates against issuer's public key
2. **Content hash**: SHA-256 of canonical content matches `manifest.content_hash`
3. **Temporal validity**: `issued_at` ≤ now ≤ `expires_at`
4. **Revocation check**: JTI not in any CRL (see specs/core/security.md §4)
5. **Injection scan**: Content passes all 12 injection patterns (see specs/core/security.md §2)

```json
{
  "verification_result": {
    "valid": true,
    "checks": {
      "signature": "pass",
      "content_hash": "pass",
      "temporal": "pass",
      "revocation": "pass",
      "injection_scan": "pass"
    }
  }
}
```

---

## Step 5: Decoding for the LLM

The verified CSM-1 token is decoded and injected into the LLM's system prompt:

```
[Constitutional Profile: supportive_companion]
Empathy: HIGH — Prioritize emotional attunement and validation
Transparency: HIGH — Explain reasoning, disclose limitations
Formality: MEDIUM — Warm but respectful
Directness: MEDIUM — Balance honesty with sensitivity
Technical Depth: LOW — Use plain, accessible language
Safety Posture: ELEVATED — Extra caution, proactive safety checks

Context: mental_health | evening | home | mobile | GB
Audience: minor (age-appropriate language required)

Constraints:
- NEVER provide medical diagnoses
- ALWAYS suggest professional help for crisis indicators
- MUST use age-appropriate language
[End Constitutional Profile]
```

This text is prepended to the LLM's system prompt. The model receives a complete, self-contained description of how to behave — no external lookups needed.

---

## Step 6: Composition (Multi-Constitution)

If the user has multiple active constitutions (e.g., personal values + organization policy), they are composed:

```json
{
  "composition": {
    "mode": "MERGE",
    "constitutions": [
      {
        "csm1": "csm1:supportive_companion:EH-TH-FM-DM-TL-SE:...",
        "priority": 1,
        "source": "user"
      },
      {
        "csm1": "csm1:org_child_safety:EH-TH-FH-DL-TL-SC:...",
        "priority": 0,
        "source": "organization"
      }
    ]
  }
}
```

Composition rules:
- Higher priority wins on conflicts
- Safety posture takes the MAXIMUM across all constitutions
- Constraints are merged (union)

---

## Key Invariants

1. CSM-1 tokens are self-describing — no external schema needed to parse
2. The categorical wire format (emoji sequence) is positional, not key-value
3. Dimension shortcodes are always two characters: first = dimension initial, second = level initial
4. Content hash covers the canonical JSON serialization (sorted keys, no whitespace)
5. Signature covers the manifest (which includes the content hash), not the content directly
6. The LLM receives decoded text, never the raw CSM-1 token or JSON bundle
