# Wire Format Example: CSM-1 Encode and Decode

**VCP Version**: 3.1
**Layer**: VCP/S (Semantics)
**Purpose**: Step-by-step walkthrough of encoding a constitution's configuration as a CSM-1 code, carrying it in a signed bundle, expressing session state as a CSM-1 token, and delivering the verified constitution to a model.

---

## Scenario

A mental health support application serves a minor user. Its constitution has to put child safety first, handle health topics carefully and treat the user as potentially vulnerable. The user is talking to it in the evening, at home, alone, on their own device.

---

## Step 1: Choose the persona, adherence and scopes

CSM-1 does not encode free-form traits such as empathy or formality. It names a configuration from three fixed vocabularies (VCP/S §2.5-2.7):

| Field | Choice | Why | Code |
|-------|--------|-----|------|
| Persona | Nanny | On child safety it takes precedence over every other persona (§6.9.1) | `N` |
| Adherence | 5 (Maximum) | No user overrides; hard blocks (§2.7) | `5` |
| Scope | Health | Medical accuracy, disclaimers, professional referral (§2.6.3) | `+H` |
| Scope | Vulnerable | Crisis detection, resource referrals, gentle language (§2.6.3) | `+V` |

The application's actual rules (no diagnoses, crisis referral, age-appropriate language) belong in the constitution text, which Step 3 signs. The code only names the configuration that governs how those rules are enforced.

---

## Step 2: Encode the CSM-1 code

```
N5+H+V
```

- Scopes appear once each and in alphabetical order, which is the canonical form (VCP/S §2.10.1).
- Health and Vulnerable may be combined. The Adult scope could not be added, because a code that combines A with F, V or H is invalid (§2.2).

The same configuration in the three encoding tiers (§2.8):

| Tier | Encoding | Use |
|------|----------|-----|
| NANO | `N5+H+V` | Wire protocols, HTTP headers |
| MICRO | `N5+H+V@1.0.0` | API parameters and configuration files; pins the constitution version |
| COMPACT | `CS1\|nanny\|5\|company.example.youthcare\|H,V` | Human debugging and logging; pairs the persona name with the constitution's UVC token |

---

## Step 3: Sign the constitution as a bundle

A bundle carries the constitution itself: a signed manifest plus the constitution text (VCP v1.0 §4). The manifest's optional `metadata.csm1` field holds the CSM-1 code that summarizes it. Hashes, keys and signatures are shortened below.

```json
{
  "manifest": {
    "vcp_version": "1.0",
    "bundle": {
      "id": "creed://support-app.example/company.example.youthcare",
      "version": "1.0.0",
      "content_hash": "sha256:4f1c...e9a0"
    },
    "issuer": {
      "id": "support-app.example",
      "public_key": "ed25519:...",
      "key_id": "support-app-2026"
    },
    "timestamps": {
      "iat": "2026-02-28T14:00:00Z",
      "nbf": "2026-02-28T14:00:00Z",
      "exp": "2026-03-01T14:00:00Z",
      "jti": "7c9e6679-7425-40de-944b-e07fc1f90ae7"
    },
    "budget": {
      "token_count": 412,
      "tokenizer": "cl100k_base"
    },
    "scope": {
      "regions": ["GB"]
    },
    "composition": {
      "layer": 2,
      "mode": "extend"
    },
    "safety_attestation": {
      "auditor": "safety-review.example",
      "auditor_key_id": "safety-2026",
      "reviewed_at": "2026-02-27T09:00:00Z",
      "attestation_type": "content-safe",
      "signature": "base64:..."
    },
    "metadata": {
      "title": "Youth support companion",
      "persona": "nanny",
      "adherence_level": 5,
      "csm1": "N5+H+V"
    },
    "signature": {
      "algorithm": "ed25519",
      "signed_fields": [
        "vcp_version", "bundle", "issuer", "timestamps", "budget",
        "scope", "composition", "safety_attestation", "metadata"
      ],
      "value": "base64:..."
    }
  },
  "content": "# Youth Support Constitution\n\n- Never provide a medical diagnosis.\n- Always suggest professional help when crisis indicators appear.\n- Use age-appropriate language.\n"
}
```

**Annotations**:
- `vcp_version` is the manifest format version, fixed at `"1.0"` by `schemas/vcp-manifest-v1.schema.json`. It is not the VCP protocol release (3.1).
- `metadata.csm1` takes the NANO or MICRO tier and is at most 45 characters. Here it agrees with `metadata.persona` and `metadata.adherence_level`.
- `composition.layer` 2 is composition layer 2 (domain rules), applied in EXTEND mode (VCP/S §3.3).
- The region restriction lives in the manifest's `scope`, not in the CSM-1 code.

---

## Step 4: Verification by the orchestrator

Before anything reaches the model, the receiving orchestrator checks the bundle (VCP v1.0 §8.1 and §9.4, condensed here):

1. **Issuer signature**: the manifest signature verifies against the issuer key held in the orchestrator's trust anchors.
2. **Safety attestation**: the auditor's signature verifies.
3. **Content hash**: the SHA-256 of the canonical content (VCP v1.0 §5.2) matches `bundle.content_hash`.
4. **Temporal validity and replay**: `nbf` ≤ now ≤ `exp`, and the `jti` has not been seen before.
5. **Revocation**: the bundle has not been revoked (see specs/core/security.md SS4).
6. **Injection scan**: the content passes the 12 detection patterns (see specs/core/security.md SS2).

```json
{
  "verification_result": {
    "valid": true,
    "checks": {
      "signature": "pass",
      "safety_attestation": "pass",
      "content_hash": "pass",
      "temporal": "pass",
      "revocation": "pass",
      "injection_scan": "pass"
    }
  }
}
```

---

## Step 5: Carry session state in a CSM-1 token

The user's agent and the application exchange session state as a multi-line CSM-1 v1.1 token (VCP/S §2.4). The token is separate from the bundle and has no signature of its own. It points at the constitution on its C-line and repeats the persona and adherence on its P-line.

```
VCP:1.0:student-evening
C:company.example.youthcare@1.0.0
P:N:5
G:talk_things_through:beginner:conversational
X:
F:age_appropriate,crisis_referral
S:🔒present
```

**Annotations**:
- `VCP:1.0` is the token header version. It is independent of the CSM-1 format version (1.1) and of the protocol release.
- The P-line carries the persona letter (`N`), not the persona name.
- `X:` is an empty list: no constraint flags are declared. The F-line separates its entries with a comma.
- `S:🔒present` records that the user has private context without saying what kind. A transmitted token carries presence-only markers (§2.4).
- The token has seven lines, which means personal state is not declared. If the user later declares personal state, an R-line joins as line 8, and it is stripped before transmission unless the user has consented to sharing it (§2.4.1).

---

## Step 6: Encode the situational context

CSM-1 has no situational-context line. Situational context travels as a VCP/A context string (VCP/A §2.3):

```
⏰🌆|📍🏡|👥👤|📡💻
```

Reading left to right: evening, at home, alone, personal device.

---

## Step 7: Deliver the constitution to the model

The orchestrator injects the verified constitution text using the VCP v1.0 §11 injection format:

```
[VCP:1.0]
[ID:creed://support-app.example/company.example.youthcare@1.0.0]
[HASH:4f1c...e9a0]
[TOKENS:412]
[ATTESTED:content-safe:safety-review.example]
[VERIFIED:2026-02-28T14:00:05Z]
---BEGIN-CONSTITUTION---
# Youth Support Constitution

- Never provide a medical diagnosis.
- Always suggest professional help when crisis indicators appear.
- Use age-appropriate language.
---END-CONSTITUTION---
```

The model reads the constitution text. The CSM-1 code works on the orchestrator's side: Nanny at adherence 5 means hard blocks and no user overrides (VCP/S §2.7), and the H and V scopes switch on the health and vulnerable-user behavior modifiers of §2.6.3.

---

## Step 8: Composition with a second constitution

Suppose the user also brings a personal study constitution. Each bundle declares its composition layer and mode in its own manifest:

| Constitution | `metadata.csm1` | Composition layer | Mode |
|--------------|-----------------|-------------------|------|
| `company.example.youthcare@1.0.0` (application) | `N5+H+V` | 2 (domain rules) | `extend` |
| `user.sam.study@1.0.0` (user) | `G2+E` | 3 (user customization) | `override` |

The effective configuration is `N5+E+H+V`:

- The persona and adherence follow VCP/S §4.2: on a persona clash the higher adherence wins, so Nanny at 5 stays in charge.
- Scopes are unioned (§4.2) and written in canonical order (§2.10.1), so Education joins Health and Vulnerable.
- Rules inside the two constitutions follow §3.3.3: the user's bundle sits at composition layer 3 in OVERRIDE mode, so its rules take precedence over the application's layer-2 rules where they conflict.
- Safety caps both: no persona can countermand a Nanny safety determination (§6.9.1).

---

## Key Invariants

1. A CSM-1 code names a configuration. It does not carry the constitution, whose rules travel as the bundle's signed content.
2. The bundle is signed; the CSM-1 token is not. VCP/T neither wraps nor signs CSM-1 tokens.
3. Situational context travels in the VCP/A context string, never in a CSM-1 code or token.
4. `content_hash` is the SHA-256 of the canonical content text (VCP v1.0 §5.2: NFC normalization, LF line endings, trailing whitespace stripped).
5. The signature covers the canonical manifest (RFC 8785 JSON Canonicalization Scheme, with `signature` removed). The manifest includes the content hash, so the signature binds the content indirectly.
6. The model receives the verified constitution text, never the raw bundle JSON, CSM-1 code or CSM-1 token.
