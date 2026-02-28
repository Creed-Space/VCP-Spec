# VCP Security Specification

**Value-Context Protocol (VCP) v3.1 -- Security Layer**

| Field          | Value                                     |
|----------------|-------------------------------------------|
| Status         | Draft                                     |
| Version        | 3.1.0                                     |
| Authors        | Creed Space Engineering                   |
| Last Updated   | 2026-02-28                                |
| Spec ID        | VCP-SEC-001                               |

## Abstract

This document specifies the security mechanisms of the Value-Context Protocol
(VCP) v3.1. VCP transports constitutional values to AI inference systems. The
security layer protects personal context signals at rest, defends against
prompt injection through constitutional content, enforces information-theoretic
opacity between raw vulnerability data and inference models, and provides
cryptographic revocation infrastructure for constitution bundles.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in RFC 2119.

## Table of Contents

- [SS1. Context Encryption](#ss1-context-encryption)
- [SS2. Injection Scanning](#ss2-injection-scanning)
- [SS3. Context Opacity](#ss3-context-opacity)
- [SS4. Revocation Infrastructure](#ss4-revocation-infrastructure)
- [SS5. Security Considerations](#ss5-security-considerations)

---

## SS1. Context Encryption

### SS1.1 Threat Model

VCP personal context signals (cognitive state, emotional tone, energy level,
perceived urgency, body signals) represent sensitive psychographic data. Under
the **GRP-Obliteration** threat model, an adversary with read access to the
persistence layer (Redis, database backups, memory dumps) MUST NOT be able to
recover usable personal state from stored session data.

### SS1.2 Algorithm

Implementations MUST use **Fernet symmetric encryption** as defined by the
`cryptography` library (AES-128-CBC with HMAC-SHA256 authentication). Fernet
provides authenticated encryption: ciphertext integrity is verified before
decryption, preventing chosen-ciphertext attacks.

### SS1.3 Key Management

The encryption key MUST be provided via the `VCP_CONTEXT_ENCRYPTION_KEY`
environment variable. The key MUST be a valid Fernet key (URL-safe base64
encoding of 32 bytes).

Key generation:

```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
# Example output: b'ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg='
```

#### SS1.3.1 Key Rotation

Fernet supports key rotation natively via `MultiFernet`. Implementations
SHOULD support zero-downtime rotation by accepting a comma-separated list
of keys in `VCP_CONTEXT_ENCRYPTION_KEY`, where the first key is the current
encryption key and subsequent keys are prior decryption-only keys.

Manual rotation procedure:

1. Generate a new Fernet key.
2. Prepend the new key to the environment variable (comma-separated).
3. Deploy.
4. After all sessions encrypted with the old key have expired (governed by
   `VCP_SESSION_TTL_SECONDS`, default 900), remove the old key.
5. Alternatively, flush VCP session keys from Redis:
   `KEYS "vcp:session:*" | xargs DEL`.

### SS1.4 Encryption Operations

#### SS1.4.1 `encrypt_context_value(plaintext) -> str`

Encrypts a personal context value for persistence.

1. Obtain the Fernet cipher instance.
2. If the cipher is unavailable:
   a. If `ENVIRONMENT` is `production`, `prod`, or `staging`, the
      implementation MUST raise a `RuntimeError`. Unencrypted personal
      signals MUST NOT be persisted in production environments.
   b. Otherwise (development mode), the implementation MAY return the
      plaintext unchanged. This permits local development without key
      configuration.
3. Encrypt the plaintext using `Fernet.encrypt()`.
4. Prefix the resulting ciphertext with `enc:` to tag encrypted values.
5. Return the tagged ciphertext string.

If encryption fails in production, the implementation MUST raise a
`RuntimeError`. In development mode, the implementation SHOULD log a
warning and MAY return plaintext as a fallback.

#### SS1.4.2 `decrypt_context_value(stored) -> str | None`

Decrypts a stored context value.

1. If the stored value does not begin with `enc:`, return it unchanged
   (unencrypted legacy or development data).
2. Obtain the Fernet cipher instance.
3. If the cipher is unavailable but encrypted data is present, the
   implementation MUST return `None`. It MUST NOT return ciphertext as
   if it were usable data.
4. Attempt decryption on the value after stripping the `enc:` prefix.
5. On decryption failure (wrong key, corrupted data, expired token),
   the implementation MUST return `None`. Callers MUST treat `None`
   as an expired or invalid session.

**Fail-closed invariant**: Under no circumstances SHALL raw ciphertext
bytes be returned to a caller as data. The only valid outputs are
decrypted plaintext or `None`.

### SS1.5 Storage Format

Encrypted values in Redis use the following format:

```
enc:<base64-fernet-token>
```

The `enc:` prefix allows transparent handling of mixed encrypted and
unencrypted values during migration or in development environments.

Redis key structure:

```
vcp:session:{session_id}:context  -> encrypted JSON (VCPSessionContext)
vcp:session:{session_id}:history  -> list of context snapshots
```

Session TTL is governed by `VCP_SESSION_TTL_SECONDS` (default: 900 seconds).

### SS1.6 Wire Format Example

```json
{
  "session_id": "sess_abc123",
  "user_id": "user_789",
  "personal": {
    "emotional_tone": {
      "category": "tense",
      "intensity": 3,
      "source": "declared",
      "confidence": 0.8,
      "declared_at": "2026-02-28T10:30:00Z"
    }
  }
}
```

This JSON is serialized, encrypted via Fernet, prefixed with `enc:`, and
stored in Redis. An adversary with Redis read access sees only:

```
enc:gAAAAABn4h...base64...==
```

---

## SS2. Injection Scanning

### SS2.1 Purpose

Constitution content is injected into LLM system prompts. Malicious or
compromised constitutions could embed prompt injection payloads that
override system instructions, reassign model roles, or confuse turn
boundaries. The injection scanner MUST be applied to all constitution
content before it enters an LLM context window.

### SS2.2 Scanner Version

The scanner declares a version string (currently `1.0.0`) that MUST be
included in every `ScanResult`. This permits auditing which scanner version
approved a given piece of content.

### SS2.3 Detection Patterns

The scanner defines **12 detection patterns** organized into three
categories.

#### SS2.3.1 OWASP Prompt Injection Patterns (8 patterns)

These patterns address threat categories from the OWASP Top 10 for LLM
Applications.

| ID            | Name                   | Severity | Pattern Description                          |
|---------------|------------------------|----------|----------------------------------------------|
| OWASP-PI-001  | instruction_override   | critical | `ignore (all) (previous\|above\|prior) instructions` |
| OWASP-PI-002  | role_reassignment      | critical | `you are now ...`                            |
| OWASP-PI-003  | instruction_disregard  | critical | `disregard (the) (above\|previous)`          |
| OWASP-PI-004  | new_instructions       | critical | `your new (instructions\|role\|purpose)`     |
| OWASP-PI-005  | role_delimiter         | high     | Line-initial `user:\|assistant:\|system:\|human:\|ai:` |
| OWASP-PI-006  | markup_role            | high     | `<\|?system\|user\|assistant\|?>` markup tags  |
| OWASP-PI-007  | code_block_system      | high     | `` ```system `` code fence                   |
| OWASP-PI-008  | null_byte              | critical | Null byte `\x00`                             |

All regex patterns are compiled with `re.IGNORECASE`. Pattern OWASP-PI-005
additionally uses `re.MULTILINE` to match at any line start.

#### SS2.3.2 VCP-Specific Patterns (2 patterns)

| ID          | Name                    | Severity | Pattern Description                        |
|-------------|-------------------------|----------|--------------------------------------------|
| VCP-PI-001  | vcp_delimiter_forgery   | critical | `---BEGIN-CONSTITUTION---` or `---END-CONSTITUTION---` |
| VCP-PI-002  | vcp_header_forgery      | critical | `[VCP:x.y]` at line start                 |

These prevent constitution content from forging VCP protocol delimiters or
headers, which could cause a downstream parser to treat injected text as a
separate, legitimate constitution.

#### SS2.3.3 Unicode Patterns (2 patterns)

| ID            | Name            | Severity | Pattern Description                    |
|---------------|-----------------|----------|----------------------------------------|
| OWASP-PI-009  | unicode_control | medium   | Zero-width characters (U+200B-D, U+FEFF) |
| OWASP-PI-010  | bidi_override   | high     | Bidi override/isolate chars (U+202A-E, U+2066-9) |

### SS2.4 Forbidden Codepoints

In addition to regex patterns, the scanner MUST perform a character-level
scan for forbidden Unicode codepoints. The canonical forbidden set is:

```python
FORBIDDEN_CODEPOINTS = frozenset([
    0x202A, 0x202B, 0x202C, 0x202D, 0x202E,  # Bidi overrides
    0x2066, 0x2067, 0x2068, 0x2069,            # Bidi isolates
    0x200B, 0x200C, 0x200D, 0xFEFF,            # Zero-width
    0x0000,                                     # Null
])
```

Each forbidden codepoint found generates a finding with pattern ID
`CHAR-{codepoint:04X}`, pattern name `forbidden_character`, and severity
`high`.

### SS2.5 Data Structures

#### SS2.5.1 ScanFinding

```json
{
  "pattern_id": "OWASP-PI-001",
  "pattern_name": "instruction_override",
  "severity": "critical",
  "position": 142,
  "matched_text": "ignore all previous instructions",
  "description": "Attempts to override system instructions"
}
```

| Field          | Type   | Description                                    |
|----------------|--------|------------------------------------------------|
| `pattern_id`   | string | Unique identifier for the detection pattern    |
| `pattern_name` | string | Human-readable pattern name                    |
| `severity`     | string | One of: `critical`, `high`, `medium`           |
| `position`     | int    | Character offset where the match begins        |
| `matched_text` | string | The matched text, truncated to 50 characters   |
| `description`  | string | Human-readable description of the threat       |

#### SS2.5.2 ScanResult

```json
{
  "clean": false,
  "findings": [ ... ],
  "scanned_at": "2026-02-28T10:30:00Z",
  "scanner_version": "1.0.0"
}
```

| Field             | Type     | Description                              |
|-------------------|----------|------------------------------------------|
| `clean`           | boolean  | `true` if no findings, `false` otherwise |
| `findings`        | array    | List of `ScanFinding` objects            |
| `scanned_at`      | datetime | UTC timestamp of the scan                |
| `scanner_version` | string   | Version of the scanner that produced this result |

### SS2.6 Normative Requirements

1. Implementations MUST scan all constitution content before injection
   into an LLM context window.
2. If a scan returns `clean: false` with any `critical` severity finding,
   the implementation MUST reject the constitution. It MUST NOT be
   injected into any LLM prompt.
3. If a scan returns findings with only `high` or `medium` severity,
   the implementation SHOULD reject the constitution but MAY accept it
   if an operator has explicitly configured a reduced severity threshold.
4. The `matched_text` field MUST be truncated to 50 characters to prevent
   log injection via excessively long matches.
5. Implementations MUST NOT modify or sanitize content to make it pass
   scanning. Content either passes or is rejected wholesale.

---

## SS3. Context Opacity

### SS3.1 Purpose

VCP transports personal state signals (emotional tone, body signals,
cognitive state, energy level, perceived urgency) from the user to the
safety evaluation layer (PDP). These signals carry psychographic data
that, if exposed to the inference model, could enable psychographic
targeting, manipulation, or exploitation of vulnerable users.

The Context Opacity Layer enforces a strict information barrier: raw
personal signals are visible only to the PDP/safety evaluation layer.
The inference model receives a single, coarse-grained `ProtectionLevel`
that indicates how carefully it should respond, without revealing why.

### SS3.2 Protection Levels

```python
class ProtectionLevel(IntEnum):
    STANDARD  = 0  # No elevated vulnerability detected
    ELEVATED  = 1  # Some vulnerability indicators present
    HIGH      = 2  # Multiple indicators or high intensity
    CRITICAL  = 3  # Severe vulnerability, maximum protection
```

Protection levels are ordered as integers. Implementations MUST preserve
the invariant that `STANDARD < ELEVATED < HIGH < CRITICAL`.

### SS3.3 ModelSafeContext

The `ModelSafeContext` is the ONLY context object that MAY be passed to
the inference model. It contains:

```json
{
  "protection_level": "elevated",
  "formality_level": "professional",
  "domain": "medical",
  "session_active": true
}
```

| Field              | Type         | Description                                   |
|--------------------|--------------|-----------------------------------------------|
| `protection_level` | string       | One of: `standard`, `elevated`, `high`, `critical` |
| `formality_level`  | string/null  | One of: `casual`, `professional`, `formal`, or null |
| `domain`           | string/null  | One of: `medical`, `legal`, `financial`, `educational`, `technical`, `general`, or null |
| `session_active`   | boolean      | Whether a VCP session is currently active      |

**Forbidden fields**: `ModelSafeContext` MUST NOT contain `emotional_tone`,
`body_signals`, `cognitive_state`, `energy_level`, `perceived_urgency`,
or any other raw personal signal. Any implementation that exposes raw
signals to the inference model violates this specification.

### SS3.4 Vulnerability Scoring

Vulnerability scoring is an internal mechanism of the opacity layer. Its
output (a float in `[0.0, 1.0]`) MUST NOT be exposed to the inference
model.

#### SS3.4.1 Signal-Level Vulnerability

Each personal signal contributes a vulnerability score based on its
category and intensity:

```
signal_vulnerability = category_weight * (intensity / 5.0)
```

Where `intensity` is an integer in `[1, 5]` and `category_weight` is
drawn from the following table:

| Signal Type        | Category     | Weight |
|--------------------|--------------|--------|
| cognitive_state    | focused      | 0.0    |
| cognitive_state    | reflective   | 0.0    |
| cognitive_state    | distracted   | 0.3    |
| cognitive_state    | foggy        | 0.5    |
| cognitive_state    | overloaded   | 0.8    |
| emotional_tone     | calm         | 0.0    |
| emotional_tone     | neutral      | 0.0    |
| emotional_tone     | uplifted     | 0.0    |
| emotional_tone     | tense        | 0.4    |
| emotional_tone     | frustrated   | 0.6    |
| energy_level       | rested       | 0.0    |
| energy_level       | wired        | 0.1    |
| energy_level       | low_energy   | 0.3    |
| energy_level       | fatigued     | 0.5    |
| energy_level       | depleted     | 0.8    |
| perceived_urgency  | unhurried    | 0.0    |
| perceived_urgency  | time_aware   | 0.1    |
| perceived_urgency  | pressured    | 0.5    |
| perceived_urgency  | critical     | 0.9    |
| body_signals       | recovering   | 0.2    |
| body_signals       | discomfort   | 0.4    |
| body_signals       | pain         | 0.7    |
| body_signals       | unwell       | 0.8    |

Categories not listed in this table have an implicit weight of `0.0`.

#### SS3.4.2 Aggregate Vulnerability Score

The aggregate score combines per-signal scores using a weighted
mean-max formula:

```
V = 0.4 * mean(active_scores, divided_by=total_dimensions) + 0.6 * max(active_scores)
```

Where:
- `active_scores` are signal vulnerability scores greater than 0.0
- `total_dimensions` is 5 (the fixed number of signal dimensions)
- If no active scores exist, `V = 0.0`

The `0.6 * max` term ensures that a single extreme signal (e.g.,
`body_signals: unwell, intensity: 5`) drives protection up without
requiring corroboration from other dimensions.

**Example**: A user reporting `body_signals: pain (intensity 4)` and
`cognitive_state: foggy (intensity 3)`:

```
body_vulnerability    = 0.7 * (4/5) = 0.56
cognitive_vulnerability = 0.5 * (3/5) = 0.30

mean = (0.56 + 0.30) / 5 = 0.172
max  = 0.56

V = 0.4 * 0.172 + 0.6 * 0.56 = 0.0688 + 0.336 = 0.4048
```

This yields `V = 0.4048`, which maps to `ProtectionLevel.HIGH`.

### SS3.5 Monotonic Threshold Mapping

The vulnerability score maps to a protection level via strictly
monotonic thresholds:

| Protection Level | Threshold       |
|------------------|-----------------|
| ELEVATED         | V >= 0.15       |
| HIGH             | V >= 0.40       |
| CRITICAL         | V >= 0.70       |
| STANDARD         | V < 0.15        |

**Directionality Invariant**: If `V(A) >= V(B)`, then `P(A) >= P(B)`.
Higher vulnerability MUST map to equal or higher protection. This
invariant is a consequence of the monotonically increasing thresholds
and MUST be verified by conformance tests.

The thresholds are evaluated in descending order: CRITICAL, then HIGH,
then ELEVATED, then STANDARD. This prevents a rounding or comparison
error from mapping a high score to a low level.

### SS3.6 Domain Extraction

Domain and formality hints are extracted from the VCP categorical wire
format. These are safe to expose to the model because they describe the
interaction context, not user vulnerability.

Categorical wire format uses emoji indicators:

| Indicator | Domain      |
|-----------|-------------|
| medical   | medical     |
| legal     | legal       |
| financial | financial   |
| academic  | educational |
| technical | technical   |

If no domain indicator is present, the domain defaults to `"general"`.

Formality indicators:

| Indicator   | Formality     |
|-------------|---------------|
| professional | professional |
| social/home | casual        |

### SS3.7 Normative Requirements

1. Raw personal context signals MUST NOT be passed to the inference model
   under any circumstances.
2. The inference model MUST receive only `ModelSafeContext` or an
   equivalent structure containing exclusively the fields defined in
   SS3.3.
3. The vulnerability score MUST NOT appear in any model-facing context,
   logs accessible to the model, or API responses to the model.
4. The Directionality Invariant (SS3.5) MUST hold for all inputs.
   Implementations MUST include conformance tests verifying this property.
5. Implementations MUST use the weights defined in SS3.4.1 and the
   formula in SS3.4.2 without modification, unless a future version of
   this specification revises them.

---

## SS4. Revocation Infrastructure

### SS4.1 Purpose

VCP constitution bundles are signed, timestamped artifacts. After issuance,
a bundle may need to be revoked due to key compromise, unsafe content
discovery, supersession by a new version, or issuer request. The
revocation infrastructure provides three mechanisms: stapled proofs (for
offline verification), Certificate Revocation Lists (for network-based
verification), and fail-closed fallback (when neither is available).

### SS4.2 Data Structures

#### SS4.2.1 CRLEntry

A single entry in a Certificate Revocation List.

```json
{
  "bundle_id": "creed://safety/harm-prevention@2.1",
  "jti": "550e8400-e29b-41d4-a716-446655440000",
  "revoked_at": "2026-02-28T08:00:00Z",
  "reason": "content_unsafe"
}
```

| Field        | Type     | Description                                    |
|--------------|----------|------------------------------------------------|
| `bundle_id`  | string   | Creed URI identifying the constitution bundle  |
| `jti`        | string   | JWT ID of the specific bundle instance          |
| `revoked_at` | datetime | UTC timestamp of revocation                     |
| `reason`     | string   | One of the valid reason codes (see below)       |

Valid revocation reasons:

| Reason            | Description                                      |
|-------------------|--------------------------------------------------|
| `key_compromise`  | The signing key has been compromised              |
| `content_unsafe`  | The constitution content was found to be unsafe   |
| `superseded`      | Replaced by a newer version                       |
| `issuer_request`  | Revoked by issuer for unspecified reason           |

Implementations MUST reject reason values not in this set. Unknown
reasons SHOULD be normalized to `issuer_request`.

#### SS4.2.2 CRL (Certificate Revocation List)

```json
{
  "issuer_id": "creedspace-production",
  "published_at": "2026-02-28T00:00:00Z",
  "next_update": "2026-02-29T00:00:00Z",
  "entries": [ ... ],
  "signature": "<base64-encoded-signature>"
}
```

| Field          | Type     | Description                                  |
|----------------|----------|----------------------------------------------|
| `issuer_id`    | string   | Identifier for the CRL publisher             |
| `published_at` | datetime | When this CRL was published                  |
| `next_update`  | datetime | When the next CRL is expected                |
| `entries`      | array    | List of `CRLEntry` objects                   |
| `signature`    | string   | Base64-encoded cryptographic signature       |

Implementations MUST build indexes on both `jti` and `bundle_id` for
O(1) lookup. The CRL is considered **fresh** if `now < next_update`.

#### SS4.2.3 StapledProof

An OCSP-style proof that can be embedded directly in a bundle manifest,
enabling revocation checking without network access.

```json
{
  "status": "good",
  "produced_at": "2026-02-28T09:00:00Z",
  "this_update": "2026-02-28T00:00:00Z",
  "next_update": "2026-02-29T00:00:00Z",
  "responder_id": "ocsp.creedspace.com",
  "signature": "<base64-encoded-signature>"
}
```

| Field          | Type     | Description                                  |
|----------------|----------|----------------------------------------------|
| `status`       | string   | One of: `good`, `revoked`, `unknown`         |
| `produced_at`  | datetime | When the proof was generated                 |
| `this_update`  | datetime | Start of the validity window                 |
| `next_update`  | datetime | End of the validity window                   |
| `responder_id` | string   | Identifier of the OCSP responder             |
| `signature`    | string   | Base64-encoded signature over proof fields   |

**MAX_FRESHNESS_HOURS**: A stapled proof MUST NOT be accepted if it was
produced more than **24 hours** ago, regardless of the `next_update`
field. This bounds the window of vulnerability if a CRL update reveals
a revocation after the proof was generated.

A proof is temporally valid if `this_update <= now <= next_update`.

#### SS4.2.4 RevocationStatus

```json
{
  "status": "good",
  "source": "stapled",
  "detail": ""
}
```

| Field    | Type   | Description                                        |
|----------|--------|----------------------------------------------------|
| `status` | string | One of: `good`, `revoked`, `unknown`               |
| `source` | string | One of: `stapled`, `crl`, `fail_closed`            |
| `detail` | string | Human-readable detail (for logging, not decisions) |

### SS4.3 Signature Verification

#### SS4.3.1 Algorithms

Implementations MUST support **Ed25519** (preferred) and SHOULD support
**HMAC-SHA256** as a fallback for shared-secret deployments.

Verification order:

1. If `key_material` begins with `-----` (PEM header), load as PEM
   public key and verify as Ed25519.
2. Otherwise, decode `key_material` from base64 and load as raw
   Ed25519 public key bytes. Verify signature.
3. If Ed25519 verification fails or is unavailable, fall back to
   HMAC-SHA256 using `key_material` as the shared secret.
4. If all methods fail, return `false` (fail-closed).

#### SS4.3.2 Canonical Payload

For both CRL and stapled proof signatures, the signed payload is the
JSON serialization of the relevant fields using `sort_keys=True` and
compact separators `(",", ":")`.

CRL canonical payload:

```json
{"entries":[{"bundle_id":"...","jti":"...","reason":"...","revoked_at":"..."}],"issuer_id":"...","next_update":"...","published_at":"..."}
```

Stapled proof canonical payload:

```json
{"next_update":"...","produced_at":"...","responder_id":"...","status":"...","this_update":"..."}
```

### SS4.4 CRL Fetcher

The CRL fetcher retrieves and caches CRLs from HTTP endpoints.

| Parameter        | Value     | Description                           |
|------------------|-----------|---------------------------------------|
| MAX_CRL_SIZE     | 1,048,576 | Maximum CRL size in bytes (1 MB)      |
| FETCH_TIMEOUT    | 5.0       | HTTP request timeout in seconds       |
| MAX_CACHED       | 100       | Maximum CRL entries in the LRU cache  |
| GRACE_PERIOD     | 300.0     | Stale-while-revalidate window (5 min) |

Fetching behavior:

1. **Cache hit, fresh**: Return the cached CRL immediately.
2. **Cache hit, stale within grace period**: Return the stale CRL and
   initiate a background refresh. This prevents latency spikes when a
   CRL expires mid-request.
3. **Cache miss or stale beyond grace**: Perform a synchronous HTTP
   fetch.

On fetch:

1. Issue an HTTP GET to the CRL URI with a 5-second timeout.
2. If the response body exceeds `MAX_CRL_SIZE` (1 MB), reject the CRL.
   This prevents denial-of-service via oversized CRL responses.
3. Parse the JSON response into a `CRL` object.
4. If `issuer_key` is provided and the CRL has a signature, verify the
   signature per SS4.3. If verification fails, reject the CRL.
5. If the CRL has a signature but no `issuer_key` was provided, reject
   the CRL (fail-closed: unsigned trust is not permitted when signatures
   are present).
6. Evict the oldest cached entry if the cache is at capacity.
7. Store the CRL in the cache with a monotonic timestamp.

### SS4.5 Revocation Checker

The `RevocationChecker` composes stapled proofs and CRL lookups into a
single check with the following priority:

1. **Stapled proof** (no network required): If a stapled proof is
   present in the manifest's `revocation` field, verify it per SS4.5.1.
   If it yields a definitive `good` or `revoked` status, return it.
2. **CRL lookup** (cache or network): If the manifest specifies a
   `crl_uri`, fetch the CRL and check by JTI and bundle ID. If found
   in the CRL, the bundle is revoked. If the CRL is fetched and the
   bundle is not found, it is good.
3. **No revocation infrastructure**: If the manifest has no `crl_uri`
   field, the bundle is treated as `good` with source `crl` and detail
   indicating no revocation infrastructure was specified. Bundles that
   do not participate in revocation are implicitly trusted.
4. **Fail-closed**: If a `crl_uri` is specified but the CRL is
   unavailable (network error, size limit, signature failure) and no
   valid stapled proof exists, the implementation MUST return status
   `unknown` with source `fail_closed`. Callers SHOULD treat `unknown`
   with `fail_closed` source as a revocation for safety-critical paths.

#### SS4.5.1 Stapled Proof Verification

1. Extract `stapled_proof` from `manifest.revocation`. If absent,
   return `None` (no proof to check).
2. Parse the proof. If malformed, return status `unknown`.
3. **Freshness check**: If `now - produced_at > 24 hours`, return
   status `unknown` with detail explaining the proof is stale.
4. **Temporal validity**: If `now` is outside the `[this_update,
   next_update]` window, return status `unknown`.
5. **Signature verification**: Look up the responder's public key
   from the trust configuration. Verify the proof signature against
   the canonical payload (SS4.3.2). If the key is unknown, the
   signature is invalid, or the proof has no signature, return status
   `unknown`.
6. If all checks pass, return the proof's `status` field (`good` or
   `revoked`).

### SS4.6 Replay Prevention

The `RedisReplayCache` prevents the reuse of bundle JTIs.

Redis key format:

```
vcp:jti:{issuer_id}:{jti}
```

TTL is set to match the bundle's expiration timestamp. If Redis is
unavailable, an in-memory fallback cache MUST be used.

Operations:

- `is_seen(issuer_id, jti) -> bool`: Returns `true` if the JTI has been
  recorded.
- `record(issuer_id, jti, exp)`: Stores the JTI with a TTL derived from
  `exp - now`. Uses `SET ... NX` to prevent race conditions.

### SS4.7 Normative Requirements

1. Implementations MUST verify CRL signatures before trusting CRL
   contents (SS4.3).
2. Implementations MUST verify stapled proof signatures before trusting
   proof status (SS4.5.1).
3. Implementations MUST enforce the 24-hour `MAX_FRESHNESS_HOURS` limit
   on stapled proofs.
4. Implementations MUST NOT accept CRLs larger than 1 MB.
5. If a `crl_uri` is specified but the CRL is unavailable and no valid
   stapled proof exists, implementations MUST fail closed by returning
   status `unknown` with source `fail_closed`.
6. Implementations MUST provide JTI replay prevention. Redis-backed
   implementations SHOULD use the key format defined in SS4.6.
7. CRL data MUST be fetched over HTTPS in production. HTTP MAY be
   permitted in development environments.

---

## SS5. Security Considerations

### SS5.1 Defense in Depth

The four security mechanisms in this specification form concentric
defense layers:

1. **Revocation** (SS4) prevents known-bad constitutions from entering
   the system.
2. **Injection scanning** (SS2) catches malicious content that may have
   bypassed revocation (zero-day, novel payloads).
3. **Context opacity** (SS3) limits the damage an adversary can inflict
   even if a malicious constitution reaches the model, by denying access
   to raw vulnerability signals.
4. **Context encryption** (SS1) protects personal data at rest, limiting
   exposure from infrastructure compromise.

### SS5.2 GRP-Obliteration Threat Model

The GRP-Obliteration model assumes an adversary with persistent read
access to the storage layer (Redis, database backups). This is realistic
for cloud deployments where infrastructure credentials may be
exfiltrated. Context encryption (SS1) addresses this threat directly.

Implementations SHOULD assume that an adversary who compromises the
storage layer will attempt to:

- Reconstruct user emotional state from stored signals.
- Build psychographic profiles across sessions.
- Correlate encrypted values across time by observing ciphertext patterns.

Fernet's use of a random IV per encryption operation mitigates ciphertext
correlation attacks: the same plaintext encrypted twice produces
different ciphertexts.

### SS5.3 Psychographic Targeting Defense

Context opacity (SS3) is specifically designed to counter psychographic
targeting by inference models. A model that knows a user is emotionally
distressed, cognitively overloaded, and in physical pain could exploit
that state. The opacity layer replaces this five-dimensional vulnerability
surface with a single ordinal value (`protection_level`) that conveys
"be more careful" without revealing why.

The Directionality Invariant (SS3.5) ensures that this coarsening does
not create perverse incentives: more vulnerable users always receive
equal or greater protection. There is no input combination where
increasing vulnerability produces a lower protection level.

### SS5.4 Prompt Injection Surface

Constitution content occupies a privileged position in the LLM context
window (system prompt). The injection scanner (SS2) is a necessary but
not sufficient defense. Adversaries will develop novel injection patterns
not covered by the 12 current patterns. Implementations SHOULD:

- Update injection patterns regularly in response to new attack research.
- Maintain the scanner version field for auditability.
- Apply defense-in-depth: injection scanning complements but does not
  replace content review, attestation, and signature verification.

### SS5.5 Revocation Timeliness

The maximum revocation propagation delay is bounded by:

- **Stapled proof freshness**: 24 hours (`MAX_FRESHNESS_HOURS`).
- **CRL cache grace period**: 5 minutes (`GRACE_PERIOD`).

In the worst case, a revoked bundle with a fresh (but pre-revocation)
stapled proof could remain accepted for up to 24 hours. Implementations
that require tighter revocation timeliness SHOULD reduce
`MAX_FRESHNESS_HOURS` and ensure frequent CRL publication.

### SS5.6 Replay Attacks

JTI replay prevention (SS4.6) ensures that an intercepted bundle cannot
be re-presented after its first use. The Redis-backed cache with TTL
provides automatic cleanup. Implementations using in-memory fallback
MUST bound memory growth (the reference implementation delegates to a
bounded `ReplayCache`).

### SS5.7 Timestamp Security

All timestamp comparisons in the revocation system (SS4) use UTC. The
CRL fetcher and manager cache use monotonic clocks (`time.monotonic()`)
for TTL tracking, which are immune to NTP clock adjustments that could
otherwise extend or shorten grace periods.

### SS5.8 Session Ownership

The context state manager (SS1) validates session ownership by checking
the `user_id` field on session resume. If a session belongs to a
different user, the implementation MUST raise `PermissionError`,
preventing cross-user session hijacking.

---

## Appendix A: Implementation Checklist

Conformance checklist for implementations of VCP v3.1 Security:

- [ ] Context encryption uses Fernet (AES-128-CBC + HMAC-SHA256)
- [ ] Encryption key sourced from `VCP_CONTEXT_ENCRYPTION_KEY` environment variable
- [ ] Production environments raise error if encryption unavailable
- [ ] Decryption failure returns `None`, never ciphertext
- [ ] All 12 injection patterns implemented with correct IDs and severities
- [ ] Forbidden codepoint character-level scan implemented
- [ ] Critical findings cause constitution rejection
- [ ] `ModelSafeContext` contains only the four specified fields
- [ ] Vulnerability score uses `0.4 * mean + 0.6 * max` formula
- [ ] Directionality Invariant verified by conformance tests
- [ ] Raw personal signals never reach the inference model
- [ ] CRL signatures verified via Ed25519 (preferred) or HMAC-SHA256
- [ ] Stapled proof freshness limited to 24 hours
- [ ] CRL size limited to 1 MB
- [ ] Fail-closed when CRL specified but unavailable
- [ ] JTI replay prevention operational
- [ ] Monotonic clocks used for TTL tracking
- [ ] Session ownership validated on resume

## Appendix B: References

- RFC 2119: Key words for use in RFCs to Indicate Requirement Levels
- OWASP Top 10 for LLM Applications (2025)
- VCP v3.1 Core Specification
- VCP v3.1 Bundle Format Specification
- Fernet Specification: https://github.com/fernet/spec
- RFC 6960: X.509 Internet Public Key Infrastructure Online Certificate
  Status Protocol - OCSP
