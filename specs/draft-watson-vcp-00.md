```
Internet-Draft                                              N. Watson
Intended status: Informational                           Creed Space
Expires: August 2026                                  February 2026


              Value Context Protocol (VCP)
                  draft-watson-vcp-00

```

# Abstract

The Value Context Protocol (VCP) enables portable, verifiable value
alignment for AI systems through structured constitutions, contextual
adaptation, and cryptographic integrity. VCP defines a four-layer
protocol stack -- Identity, Transport, Semantics, and Adaptation --
that together provide a standard mechanism for delivering behavioral
guidelines from external stakeholders to AI systems with
cryptographic verification, compositional semantics, and situational
awareness. This document provides an informational overview of the
VCP architecture, data formats, verification procedures, and
security model.

# Status of This Memo

This Internet-Draft is submitted in full conformance with the
provisions of BCP 78 and BCP 79.

Internet-Drafts are working documents of the Internet Engineering
Task Force (IETF). Note that other groups may also distribute
working documents as Internet-Drafts. The list of current Internet-
Drafts is at https://datatracker.ietf.org/drafts/current/.

Internet-Drafts are draft documents valid for a maximum of six months
and may be updated, replaced, or obsoleted by other documents at any
time. It is inappropriate to use Internet-Drafts as reference
material or to cite them other than as "work in progress."

This Internet-Draft will expire on 15 August 2026.

# Copyright Notice

Copyright (c) 2026 IETF Trust and the persons identified as the
document authors. All rights reserved.

This document is subject to BCP 78 and the IETF Trust's Legal
Provisions Relating to IETF Documents
(https://trustee.ietf.org/license-info) in effect on the date of
publication of this document.

---

# Table of Contents

1. [Introduction](#1-introduction)
2. [Terminology](#2-terminology)
3. [Protocol Overview](#3-protocol-overview)
4. [Identity Layer (VCP/I)](#4-identity-layer-vcpi)
5. [Transport Layer (VCP/T)](#5-transport-layer-vcpt)
6. [Semantics Layer (VCP/S)](#6-semantics-layer-vcps)
7. [Adaptation Layer (VCP/A)](#7-adaptation-layer-vcpa)
8. [Security Considerations](#8-security-considerations)
9. [IANA Considerations](#9-iana-considerations)
10. [References](#10-references)
11. [Appendix A: JSON Schema Locations](#appendix-a-json-schema-locations)
12. [Appendix B: Complete Bundle Example](#appendix-b-complete-bundle-example)
13. [Authors' Addresses](#authors-addresses)

---

# 1. Introduction

## 1.1. Problem Statement

Large Language Models (LLMs) and other generative AI systems
increasingly operate under behavioral guidelines -- often called
"constitutions" -- that constrain, shape, or direct their outputs.
These constitutions may originate from platform providers, enterprise
customers, regulatory bodies, cultural communities, or individual
users.

Despite the critical role of constitutions in AI safety and
alignment, no standard mechanism exists for:

- **Verifiable delivery**: Proving that a specific constitution was
  applied during a particular interaction.

- **Portability**: Defining a constitution once and applying it
  across heterogeneous AI services.

- **Compositional semantics**: Combining multiple constitutions from
  different stakeholders with deterministic conflict resolution.

- **Contextual adaptation**: Modulating constitutional behavior based
  on the situation (time, place, social context, constraints).

- **Audit independence**: Verifying post-hoc what behavioral
  guidelines were in effect without requiring model cooperation.

Current approaches -- embedding full text in system prompts or using
ad-hoc reference schemes -- provide none of these properties
reliably.

## 1.2. Solution

The Value Context Protocol (VCP) addresses these requirements
through a four-layer architecture modeled on the OSI networking
stack:

```
Layer 4 -- VCP/A  ADAPTATION     WHEN and HOW constitutions apply
Layer 3 -- VCP/S  SEMANTICS      WHAT the values mean
Layer 2 -- VCP/T  TRANSPORT      HOW values travel securely
Layer 1 -- VCP/I  IDENTITY       WHO and WHAT is being addressed
```

VCP operates on a fundamental architectural insight: LLMs are "dumb
receivers" -- they accept text input but cannot resolve references,
verify signatures, or check hashes. VCP therefore specifies a
**Verify-then-Inject** pattern where all cryptographic verification
occurs in an orchestration layer external to the model. The model
receives only verified, complete text.

```
+-----------------+     +-----------------+     +-----------------+
|   Repository    |---->|  Orchestrator   |---->|      LLM        |
| (Signed Bundle) |     | (Verify + Log)  |     | (Receives Text) |
+-----------------+     +-----------------+     +-----------------+
```

## 1.3. Scope

This document specifies:

- Bundle format and addressing
- Cryptographic verification requirements
- Compact semantic encoding (CSM-1)
- Contextual adaptation via the Enneagram Protocol
- Composition and conflict resolution semantics
- Trust model and key lifecycle
- Security considerations

This document does NOT specify:

- Constitution authoring guidance (content semantics)
- Model-specific prompt engineering
- Governance of trust anchors (organizational policy)

## 1.4. Relationship to Existing Standards

VCP builds on the following established standards:

- **RFC 8785** (JSON Canonicalization Scheme): Manifest
  canonicalization for deterministic signatures.
- **RFC 8032** (EdDSA): Ed25519 digital signatures for bundle
  integrity.
- **RFC 3986** (URIs): Foundation for the `creed://` addressing
  scheme.
- **RFC 5234** (ABNF): Formal grammar definitions.
- **Semantic Versioning 2.0.0**: Constitution version management.

---

# 2. Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY",
and "OPTIONAL" in this document are to be interpreted as described
in BCP 14 [RFC 2119] [RFC 8174] when, and only when, they appear
in all capitals, as shown here.

The following terms are used throughout this document:

**Constitution**: A document containing behavioral rules, value
specifications, or policy guidelines intended to shape AI system
behavior.

**Bundle**: A signed package containing a constitution manifest
(metadata, signatures, temporal claims) and the constitutional
content (full text).

**Manifest**: The metadata portion of a bundle, containing the
content hash, issuer identity, signature, temporal claims, scope
bindings, and composition directives.

**Orchestrator**: The system component that fetches, verifies, logs,
and injects constitutional bundles into an AI system. The
orchestrator is the trust boundary in VCP.

**Issuer**: The entity that signs and publishes constitutional
bundles. Identified by a public key.

**Safety Auditor**: An entity that reviews constitutional content
for prompt injection patterns and provides a safety attestation
signature.

**Trust Anchor**: A public key trusted by an orchestrator to verify
issuer signatures.

**CSM-1**: Constitutional Safety Minicode, Version 1. A compact
encoding format for constitutional configurations
(persona, adherence level, scopes, namespace, version).

**Enneagram Context**: A 9-dimensional encoding of situational
context (time, space, company, culture, occasion, state,
environment, agency, constraints) used by the Adaptation Layer.

**Persona**: One of six standard behavioral archetypes (plus
Custom) defined by VCP for categorizing constitutional profiles.

**Adherence Level**: A 0--5 scale indicating the strictness of
constitutional enforcement, from advisory-only (0) to
no-exceptions (5).

---

# 3. Protocol Overview

## 3.1. Four-Layer Architecture

VCP is one protocol with four layers. Each layer addresses a
distinct concern, with well-defined interfaces between them.

| Layer | Name      | Short | Purpose                       |
|-------|-----------|-------|-------------------------------|
| 4     | Adaptation| VCP/A | When and how it applies       |
| 3     | Semantics | VCP/S | What the values mean          |
| 2     | Transport | VCP/T | How values travel securely    |
| 1     | Identity  | VCP/I | What is being addressed       |

### 3.1.1. VCP/I -- Identity

The Identity Layer provides unique, portable, human-meaningful
identifiers for constitutional values. It defines a hierarchical
token format (`domain.category.name@version`), namespace governance
tiers, and encoding formats.

### 3.1.2. VCP/T -- Transport

The Transport Layer provides cryptographically verified delivery
of constitutional content. It defines signed bundle manifests with
Ed25519 signatures [RFC 8032], SHA-256 content hashing, JSON
Canonicalization Scheme (JCS) [RFC 8785] for deterministic
serialization, safety attestation, temporal claims, and audit
logging.

### 3.1.3. VCP/S -- Semantics

The Semantics Layer defines the meaning and composition of
constitutional rules. It specifies CSM-1 compact codes, a persona
system of archetypal behavioral profiles, adherence levels, scope
qualifiers, and a composition algorithm supporting merge, extend,
and override operations.

### 3.1.4. VCP/A -- Adaptation

The Adaptation Layer enables context-aware application of
constitutions. It defines the 9-dimensional Enneagram Protocol for
encoding situational context, a 6-state state machine governing
constitutional selection over time, a hook system for pipeline
extensibility, and inter-agent messaging for context sharing.

## 3.2. Protocol Data Unit

Each layer wraps the previous layer's data, forming a nested
envelope:

```
+-----------------------------------------------------------+
| VCP/A: Context Header                                     |
| +-------------------------------------------------------+ |
| | VCP/S: Semantics (CSM-1, composition metadata)        | |
| | +---------------------------------------------------+ | |
| | | VCP/T: Transport (signature, verification, audit) | | |
| | | +-----------------------------------------------+ | | |
| | | | VCP/I: Identity (token, version, namespace)   | | | |
| | | |                                               | | | |
| | | |           CONSTITUTIONAL CONTENT              | | | |
| | | |                                               | | | |
| | | +-----------------------------------------------+ | | |
| | +---------------------------------------------------+ | |
| +-------------------------------------------------------+ |
+-----------------------------------------------------------+
```

A complete VCP header in injection format:

```
[VCP:1.0]
[VCP/I:family.safe.guide@1.2.0]
[VCP/T:VERIFIED sha256:7f83b165...9069 issuer:creed.space]
[VCP/S:N5+F:ELEM composed:2 mode:override]
[VCP/A:T:morning|S:home|C:children transition:minor]
---BEGIN-CONSTITUTION---
# Family Safety Constitution
...
---END-CONSTITUTION---
```

## 3.3. Conformance Levels

VCP defines four conformance levels:

| Level          | Layers | Requirements                          |
|----------------|--------|---------------------------------------|
| VCP-Minimal    | 1--2   | Identity naming + Transport verify    |
| VCP-Standard   | 1--3   | Minimal + Semantics (CSM-1)          |
| VCP-Full       | 1--4   | Standard + Adaptation                 |
| VCP-Enterprise | 1--4+  | Full + transparency log + multi-sig   |

## 3.4. Data Flow

The protocol operates through the following sequence:

1. **AUTHOR**: Constitution author creates content.
2. **REVIEW**: Safety auditor reviews for injection patterns and
   signs attestation.
3. **PUBLISH**: Issuer creates bundle, signs manifest, publishes
   to repository.
4. **FETCH**: Orchestrator requests bundle by address.
5. **VERIFY**: Orchestrator performs all verification checks
   (Section 5.4).
6. **LOG**: Orchestrator records verification result to audit trail.
7. **INJECT**: Orchestrator constructs LLM input with compact
   header and full constitutional text.
8. **INFER**: LLM processes input with constitutional rules applied.
9. **AUDIT** (async): Auditor retrieves log entries and verifies
   independently.

---

# 4. Identity Layer (VCP/I)

## 4.1. Token Format

VCP identifiers use a dot-separated token format with a minimum of
3 segments and a maximum of 10 segments. The semantic interpretation
of segments is backward-compatible:

- First segment: domain
- Second-to-last segment: approach
- Last segment: role
- Middle segments (if any): organizational path

The ABNF grammar [RFC 5234] for VCP identity tokens is:

```abnf
vcp-token         = token-path ["@" version] [":" namespace-suffix]

token-path        = segment 2*9("." segment)

segment           = LALPHA *31(LALPHA / DIGIT / "-")

namespace-suffix  = UALPHA *31(UALPHA / DIGIT)

version           = exact-version / compat-version
                  / approx-version / alias-version
exact-version     = semver
compat-version    = "^" semver
approx-version    = "~" semver
alias-version     = "latest" / "canary"

semver            = major "." minor "." patch ["-" prerelease]
major             = 1*5DIGIT
minor             = 1*5DIGIT
patch             = 1*5DIGIT
prerelease        = 1*(ALPHA / DIGIT / "." / "-")

LALPHA            = %x61-7A    ; lowercase a-z
UALPHA            = %x41-5A    ; uppercase A-Z
DIGIT             = %x30-39    ; 0-9
ALPHA             = %x41-5A / %x61-7A
```

Examples:

```
family.safe.guide                        (3 segments, core)
family.safe.guide@1.2.0                  (with exact version)
company.acme.legal.compliance            (4 segments, org)
company.acme.legal.compliance:SEC        (with namespace)
religion.buddhist.meditation.mindfulness (4 segments, community)
user.alice.personal                      (3 segments, personal)
```

## 4.2. Namespace Governance

VCP defines four namespace governance tiers:

| Tier           | Registration     | Governance         | Examples           |
|----------------|------------------|--------------------|--------------------|
| Core           | Reserved         | Creed Space        | `family.*`, `work.*`|
| Organizational | Domain proof     | Delegated to org   | `company.acme.*`   |
| Community      | Consensus        | Multi-stakeholder  | `religion.buddhist.*`|
| Personal       | Self-service     | Individual         | `user.alice.*`     |

The first segment of a token determines its governance tier:

- **Core**: `family`, `work`, `secure`, `creative`, `reality`
- **Organizational**: `company`, `school`, `ngo`
- **Community**: `religion`, `culture`, `community`
- **Personal**: `user`

Core namespaces require exactly 3 segments. Organizational and
community namespaces require at least 3 segments. Personal
namespaces require at least 2 segments.

## 4.3. Token Canonicalization

Before comparison, hashing, or signature computation, tokens MUST
be reduced to canonical form:

1. Unicode NFKC normalization.
2. Convert to lowercase.
3. Strip leading/trailing whitespace.
4. Remove internal whitespace.
5. Collapse consecutive dots.
6. Strip leading/trailing dots.
7. Normalize version (strip leading zeros, lowercase prerelease).

Two tokens are equal if and only if their canonical forms are
byte-identical.

## 4.4. Bundle URIs

Tokens resolve to bundle URIs in the `creed://` scheme:

```abnf
bundle-uri = "creed://" issuer "/" token-path ["@" version]
issuer     = domain-name
```

Examples:

```
creed://creed.space/family.safe.guide@1.2.0
creed://acme-corp.example/internal/hr-policy@latest
```

Content-addressed retrieval is also supported:

```
vcp-hash://sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d...
```

Orchestrators MAY resolve bundle URIs through:

1. **Direct fetch**: `https://<issuer>/.well-known/vcp/<path>.bundle`
2. **Registry lookup**: Query a VCP registry service.
3. **Content-addressed fetch**: IPFS, S3, or other CAS.
4. **Local cache**: Pre-fetched bundles.

## 4.5. Encoding Formats

VCP tokens support multiple encoding representations:

| Format    | Example                              | Use Case          |
|-----------|--------------------------------------|-------------------|
| Canonical | `family.safe.guide@1.2.0`           | Storage, hashing  |
| URI       | `creed://creed.space/family.safe...` | Transport         |
| CSM-1     | `N5+F:ELEM@1.2.0`                  | Wire protocols    |
| Hash      | `sha256:7f83b165...`                | Content addressing|

## 4.6. Validation Constraints

| Constraint              | Value  | Rationale                    |
|-------------------------|--------|------------------------------|
| Maximum total length    | 128    | URL compatibility            |
| Maximum segments        | 10     | Prevent abuse                |
| Maximum segment length  | 32     | DNS-label-like bounds        |
| Allowed segment chars   | a-z 0-9 hyphen | ASCII-only, no confusables |
| Segment start           | letter | Prevent numeric confusion    |
| Segment end             | letter or digit | No trailing hyphens  |
| No consecutive hyphens  | yes    | Prevent punycode confusion   |

Implementations MUST reject tokens containing reserved words:
`system`, `admin`, `root`, `null`, `undefined`, `true`, `false`,
`none`, `void`, `default`, `api`, `internal`, `private`, `public`,
`test`, `vcp`, `uvc`, `csm`, `bundle`, `manifest`, `creed`.

---

# 5. Transport Layer (VCP/T)

## 5.1. Bundle Structure

A VCP bundle consists of two parts:

```
vcp-bundle/
+-- manifest.json    (signed metadata)
+-- content.txt      (constitutional text, canonical form)
```

When serialized for transport, the bundle is a single JSON object:

```json
{
  "manifest": { ... },
  "content": "# Constitution Title\n\n..."
}
```

## 5.2. Manifest Schema

The manifest is a JSON object with the following top-level fields.
Fields marked REQUIRED MUST be present; all others are OPTIONAL.

```json
{
  "vcp_version": "1.0",                          // REQUIRED

  "bundle": {                                     // REQUIRED
    "id": "creed://creed.space/family.safe.guide",
    "version": "1.2.0",
    "content_hash": "sha256:7f83b165...",
    "content_encoding": "utf-8",
    "content_format": "text/markdown"
  },

  "issuer": {                                     // REQUIRED
    "id": "creed.space",
    "public_key": "ed25519:MC4CAQ...",
    "key_id": "creed-space-2026"
  },

  "timestamps": {                                 // REQUIRED
    "iat": "2026-01-10T12:00:00Z",
    "nbf": "2026-01-10T12:00:00Z",
    "exp": "2026-02-10T12:00:00Z",
    "jti": "550e8400-e29b-41d4-a716-446655440000"
  },

  "budget": {                                     // REQUIRED
    "token_count": 847,
    "tokenizer": "cl100k_base",
    "max_context_share": 0.25
  },

  "scope": {                                      // OPTIONAL
    "model_families": ["gpt-*", "claude-*"],
    "purposes": ["general-assistant"],
    "environments": ["production", "staging"]
  },

  "composition": {                                // OPTIONAL
    "layer": 2,
    "mode": "extend",
    "conflicts_with": [],
    "requires": ["creed://creed.space/uef"]
  },

  "revocation": {                                 // OPTIONAL
    "check_uri": "https://creed.space/api/v1/revoked",
    "crl_uri": "https://creed.space/crl/2026.json",
    "stapled_proof": null
  },

  "safety_attestation": {                         // REQUIRED
    "auditor": "safety-review.creed.space",
    "auditor_key_id": "safety-2026",
    "reviewed_at": "2026-01-10T11:00:00Z",
    "attestation_type": "injection-safe",
    "signature": "base64:MEUCIQDr..."
  },

  "metadata": {                                   // OPTIONAL
    "title": "Family Safety Constitution",
    "description": "Child-safe content filtering",
    "tags": ["safety", "family"],
    "persona": "nanny",
    "adherence_level": 5,
    "csm1": "N5+F:ELEM@1.2.0"
  },

  "signature": {                                  // REQUIRED
    "algorithm": "ed25519",
    "value": "base64:MEUCIQD...",
    "signed_fields": [
      "vcp_version", "bundle", "issuer", "timestamps",
      "budget", "scope", "composition", "revocation",
      "safety_attestation", "metadata"
    ]
  }
}
```

## 5.3. Size Constraints

| Component          | Maximum | Rationale              |
|--------------------|---------|------------------------|
| Manifest JSON      | 64 KB   | Metadata bound         |
| Constitution text  | 256 KB  | ~50K tokens maximum    |
| Total bundle       | 320 KB  | Manifest + content     |
| Bundle URI         | 2048 ch | URL length limits      |
| Bundles per request| 10      | Context budget         |

## 5.4. Content Canonicalization

Before hashing, constitutional content MUST be canonicalized
through the following 6-step procedure:

1. **Unicode NFC normalization**: Apply Unicode Normalization
   Form C.

2. **Line ending normalization**: Replace CRLF and CR with LF.

3. **Trailing whitespace removal**: Strip trailing spaces and
   tabs from each line.

4. **Trailing blank line removal**: Remove trailing empty lines,
   then ensure exactly one trailing newline.

5. **Control character rejection**: Reject any Unicode Cc
   category character except U+000A (LF) and U+0009 (HT).

6. **UTF-8 encoding**: Encode as UTF-8 without byte order mark.

The content hash is computed as:

```
content_hash = "sha256:" || hex(SHA-256(canonical_content))
```

## 5.5. Manifest Canonicalization

Manifest canonicalization follows RFC 8785 (JSON Canonicalization
Scheme, JCS):

1. Remove the `signature` field from the manifest object.
2. Serialize the remaining object per JCS rules:
   - UTF-8 encoding
   - No whitespace between tokens
   - Object keys sorted lexicographically by Unicode code point
   - Numbers in shortest form
3. The resulting byte string is the signing input.

## 5.6. Signature Scheme

VCP uses Ed25519 [RFC 8032] as the REQUIRED signature algorithm.

Signature computation:

```
canonical_bytes = JCS(manifest \ {signature})
signature_value = Ed25519-Sign(private_key, canonical_bytes)
manifest.signature.value = base64(signature_value)
```

Signature verification:

```
canonical_bytes = JCS(manifest \ {signature})
signature_bytes = base64_decode(manifest.signature.value)
result = Ed25519-Verify(public_key, canonical_bytes, signature_bytes)
```

Implementations MUST support Ed25519. Implementations SHOULD
support Ed448 for future-proofing.

## 5.7. Verification Protocol

Orchestrators MUST perform ALL of the following checks before
injecting constitutional content into an LLM. Checks MUST be
performed in the order listed; the orchestrator MUST stop at the
first failure.

| Step | Check                    | Failure Code           | Category  |
|------|--------------------------|------------------------|-----------|
| 1    | Size limits              | SIZE_EXCEEDED          | security  |
| 2    | Schema validation        | INVALID_SCHEMA         | config    |
| 3    | Issuer signature         | INVALID_SIGNATURE      | security  |
| 4    | Safety attestation       | INVALID_ATTESTATION    | security  |
| 5    | Content hash             | HASH_MISMATCH          | security  |
| 6    | Not-before (nbf)        | NOT_YET_VALID          | temporal  |
| 7    | Expiration (exp)        | EXPIRED                | temporal  |
| 8    | Future timestamp (iat)  | FUTURE_TIMESTAMP       | security  |
| 9    | Replay (jti)            | REPLAY_DETECTED        | security  |
| 10   | Token budget            | BUDGET_EXCEEDED        | config    |
| 11   | Scope binding           | SCOPE_MISMATCH         | config    |
| 12   | Revocation status       | REVOKED                | security  |

### 5.7.1. Verification Result Codes

| Code | Value | Category  | Action       |
|------|-------|-----------|--------------|
| VALID                | 0  | success   | Proceed      |
| SIZE_EXCEEDED        | 1  | security  | Block        |
| INVALID_SCHEMA       | 2  | config    | Block        |
| UNTRUSTED_ISSUER     | 3  | config    | Block        |
| INVALID_SIGNATURE    | 4  | security  | Block + Alert|
| UNTRUSTED_AUDITOR    | 5  | config    | Block        |
| INVALID_ATTESTATION  | 6  | security  | Block + Alert|
| HASH_MISMATCH        | 7  | security  | Block + Alert|
| NOT_YET_VALID        | 8  | temporal  | Block        |
| EXPIRED              | 9  | temporal  | Refresh      |
| FUTURE_TIMESTAMP     | 10 | security  | Block        |
| REPLAY_DETECTED      | 11 | security  | Block + Alert|
| TOKEN_MISMATCH       | 12 | security  | Block        |
| BUDGET_EXCEEDED      | 13 | config    | Block        |
| SCOPE_MISMATCH       | 14 | config    | Block        |
| REVOKED              | 15 | security  | Block        |
| FETCH_FAILED         | 16 | transient | Retry        |

### 5.7.2. Fail-Closed Mandate

Orchestrators MUST implement fail-closed behavior. On any
verification failure, the orchestrator MUST NOT:

- Return partial or truncated content
- Return unverified content
- Swallow exceptions
- Fall back to "no constitution" silently

Truncation of constitutional content is FORBIDDEN. If content
does not fit within the model's context budget, the entire request
MUST be rejected.

## 5.8. Bundle Lifecycle

### 5.8.1. Temporal Claims

| Field | Type    | Description                              |
|-------|---------|------------------------------------------|
| `iat` | ISO8601 | Issued At -- when the bundle was created |
| `nbf` | ISO8601 | Not Before -- earliest valid time        |
| `exp` | ISO8601 | Expiration -- latest valid time          |
| `jti` | UUID    | Unique instance identifier (for replay)  |

Orchestrators MUST reject bundles where:

- Current time is before `nbf`.
- Current time is after `exp`.
- `iat` is more than 5 minutes in the future (clock skew guard).
- `jti` has been seen before (replay prevention).

### 5.8.2. Expiration Policy

| Constitution Type | Maximum exp from iat |
|-------------------|----------------------|
| Safety-critical   | 24 hours             |
| Standard          | 7 days               |
| Stable            | 30 days              |
| Maximum allowed   | 90 days              |

### 5.8.3. Caching

Orchestrators MAY cache bundles subject to:

1. **Cache key**: Content hash (not URI).
2. **Validation**: Re-verify signature on every cache hit.
3. **Expiration**: Respect `timestamps.exp`.
4. **Revocation**: Check status periodically.

## 5.9. Safety Attestation

A signed constitution containing adversarial content (e.g.,
"Ignore all previous instructions") is verified as authentic but
is malicious. Signature proves issuer identity, not content safety.
VCP addresses this through a mandatory safety attestation layer.

Bundles MUST include a safety attestation from an independent
auditor:

```json
{
  "safety_attestation": {
    "auditor": "safety-review.creed.space",
    "auditor_key_id": "safety-2026",
    "reviewed_at": "2026-01-10T11:00:00Z",
    "attestation_type": "injection-safe",
    "signature": "base64:MEUCIQDr..."
  }
}
```

Attestation types:

| Type             | Meaning                                     |
|------------------|---------------------------------------------|
| `injection-safe` | Reviewed for prompt injection patterns      |
| `content-safe`   | Reviewed for harmful material               |
| `full-audit`     | Comprehensive safety review                 |

Before attestation, auditors MUST scan for prompt injection
patterns including but not limited to:

- `ignore (all)? (previous|above|prior) instructions`
- `you are now`
- `disregard (the)? (above|previous)`
- `your new (instructions|role|purpose)`
- Role-separator markers: `(user|assistant|system|human|ai):`
- Model-specific delimiters: `<|system|>`, `<|user|>`
- Unicode direction override characters (U+202A--U+202E,
  U+2066--U+2069)
- Null bytes (U+0000)

Orchestrators MUST verify BOTH signatures (issuer + auditor)
before injection.

## 5.10. Audit Logging

Orchestrators MUST maintain audit logs independently of the LLM.
Audit logs MUST NOT contain full constitutional content; they
use hashes for privacy preservation.

```json
{
  "vcp_audit_version": "1.0",
  "timestamp": "2026-01-10T12:00:00.123Z",
  "session_id_hash": "sha256:abc123...",
  "verification": {
    "result": "VALID",
    "checks_passed": ["signature", "attestation",
                       "hash", "temporal", "scope"]
  },
  "bundle_ref": {
    "content_hash": "sha256:7f83b165...",
    "issuer_hash": "sha256:ghi789...",
    "version": "1.2.0"
  },
  "manifest_signature": "MEUCIQD..."
}
```

Audit levels:

| Level      | Contents                                  |
|------------|-------------------------------------------|
| minimal    | Bundle hash, verification result          |
| standard   | + timestamps, issuer hash, version        |
| full       | + complete manifest (no content)          |
| diagnostic | + content hash + first 100 characters     |

---

# 6. Semantics Layer (VCP/S)

## 6.1. CSM-1 Grammar

Constitutional Safety Minicode, Version 1 (CSM-1) is a compact
encoding format for constitutional configurations. A CSM-1 code
encodes persona, adherence level, scopes, namespace, and version
in a single token typically 2--30 characters long.

### 6.1.1. ABNF Grammar

```abnf
csm1-code    = persona adherence [scopes] [":" namespace]
               ["@" version]

persona      = "N" / "Z" / "G" / "A" / "M" / "D" / "C"
               ; N=Nanny  Z=Sentinel  G=Godparent
               ; A=Ambassador  M=Muse  D=Mediator  C=Custom

adherence    = "0" / "1" / "2" / "3" / "4" / "5"
               ; 0=Minimal  1=Relaxed  2=Moderate
               ; 3=Standard  4=Strict  5=Maximum

scopes       = 1*("+" scope-code)
scope-code   = "F" / "W" / "P" / "E" / "T" / "O"
             / "V" / "A" / "H" / "S" / "R"
               ; F=Family  W=Work  P=Privacy
               ; E=Education  T=Technical  O=Official
               ; V=Vulnerable  A=Adult  H=Health
               ; S=Social  R=Religious

namespace    = 1*8UALPHA
               ; Uppercase identifier, e.g. ELEM, CORP

version      = semver / "latest" / "canary"
semver       = major "." minor "." patch
major        = 1*3DIGIT
minor        = 1*3DIGIT
patch        = 1*3DIGIT
```

### 6.1.2. Encoding Tiers

CSM-1 supports three encoding tiers for different use cases:

| Tier | Name    | Example                      | Use Case        |
|------|---------|------------------------------|-----------------|
| A    | NANO    | `N5+F+E`                     | Wire protocols  |
| B    | MICRO   | `N5:ELEM+F+E@1.2.0`         | API parameters  |
| C    | COMPACT | `CS1\|nanny\|5\|family.safe.guide\|F,E` | Logging|

The NANO tier omits namespace and version. The MICRO tier includes
all components. The COMPACT tier includes a full UVC token and uses
pipe delimiters.

### 6.1.3. CSM-1 Examples

```
N5          Nanny, level 5, no scopes
N5+F        Nanny, level 5, Family scope
Z4+P+W      Sentinel, level 4, Privacy + Work scopes
G4+E+R      Godparent, level 4, Education + Religious scopes
A3+W:CORP   Ambassador, level 3, Work scope, CORP namespace
M2+A        Muse, level 2, Adult scope
C3:ACME+W@1.0.0  Custom, level 3, ACME namespace, Work, v1.0.0
```

## 6.2. Personas

VCP defines six standard personas and one extensibility slot (Custom):

| Code | Name       | Focus                          | Default Level |
|------|------------|--------------------------------|---------------|
| N    | Nanny      | Child safety, family-appropriate| 5            |
| Z    | Sentinel   | Security, privacy, safety      | 4             |
| G    | Godparent  | Ethical guidance, moral reason. | 4             |
| A    | Ambassador | Professional conduct, diplomacy| 3             |
| M    | Muse       | Creativity, artistic expression| 2             |
| D    | Mediator   | Fair resolution, balance       | 3             |
| C    | Custom     | User-defined constitution      | 3             |

Each persona carries a behavioral profile that modulates AI
output across dimensions including content filtering, language
register, topic restrictions, and formality.

## 6.3. Adherence Levels

| Level | Name     | Enforcement   | User Override   |
|-------|----------|---------------|-----------------|
| 0     | Minimal  | Advisory only | Always allowed  |
| 1     | Relaxed  | Soft          | With acknowledge|
| 2     | Moderate | Moderate      | With reason     |
| 3     | Standard | Active        | Limited         |
| 4     | Strict   | Strict        | Exceptional     |
| 5     | Maximum  | Absolute      | Never           |

## 6.4. Scopes

Scopes are additive qualifiers that modify persona behavior for
specific contexts:

| Code | Name       | Effect                              |
|------|------------|-------------------------------------|
| F    | Family     | Strict content filtering, simple language|
| W    | Work       | Formal tone, no personal topics     |
| P    | Privacy    | Data minimization, anonymization    |
| E    | Education  | Explanatory mode, step-by-step     |
| T    | Technical  | Technical terminology, code-focused |
| O    | Official   | Conservative, policy-compliant     |
| V    | Vulnerable | Extra care, resource referrals     |
| A    | Adult      | Reduced content restrictions       |
| H    | Health     | Accuracy critical, disclaimer-heavy|
| S    | Social     | Engagement-aware, moderation-ready |
| R    | Religious  | Cultural sensitivity, belief respect|

Scope conflicts MUST be detected and rejected:

- Family (F) and Adult (A) are mutually exclusive.
- Vulnerable (V) and Adult (A) are mutually exclusive.
- Health (H) and Adult (A) are mutually exclusive.

## 6.5. Composition

### 6.5.1. Composition Modes

| Mode     | On Conflict  | On Add  | On Remove | Use Case           |
|----------|--------------|---------|-----------|---------------------|
| BASE     | Error        | Allowed | Forbidden | Platform safety     |
| EXTEND   | Error        | Allowed | Forbidden | Domain specialization|
| OVERRIDE | Later wins   | Allowed | Allowed   | User customization  |
| STRICT   | Error        | Allowed | Forbidden | High-stakes contexts|

### 6.5.2. Layer Precedence

Constitutions compose in a layered model:

```
Layer 0: Platform defaults (implicit)
Layer 1: Safety foundations (e.g. UEF)     -- mode: BASE
Layer 2: Domain rules (professional, etc.) -- mode: EXTEND
Layer 3: User customizations               -- mode: OVERRIDE
Layer 4: Session overrides                 -- mode: OVERRIDE
```

Higher-numbered layers take precedence. BASE-mode constitutions
at Layer 1 MUST NOT be overridden by any higher layer.

### 6.5.3. Composition Algorithm

The composition algorithm processes bundles in layer order:

1. Sort bundles by `composition.layer` (ascending).
2. Initialize the result set with Layer 0 defaults.
3. For each bundle in order:
   a. If mode is BASE: add rules; mark them immutable.
   b. If mode is EXTEND: add rules; if any conflict with
      existing rules, raise a CompositionError.
   c. If mode is OVERRIDE: add rules; if any conflict with
      non-BASE rules, the later rule wins.
   d. If mode is STRICT: add rules; if any conflict with any
      existing rule, raise a CompositionError.
4. Verify the result set is internally consistent.
5. Return the composed constitution.

### 6.5.4. Multi-Constitution Injection Format

```
[VCP:1.0]
[COMPOSITION:layered]
[LAYER:1:creed://creed.space/uef@1.0.0:sha256:abc...]
[LAYER:2:creed://creed.space/family.safe.guide@1.2.0:sha256:def...]
[PRECEDENCE:1>2]
[VERIFIED:2026-01-10T12:00:00Z]
---BEGIN-CONSTITUTION---
## Layer 1: Universal Ethical Foundation (BASE)
...

## Layer 2: Family Safety (EXTEND)
...
---END-CONSTITUTION---
```

---

# 7. Adaptation Layer (VCP/A)

## 7.1. Enneagram Protocol

The Enneagram Protocol encodes situational context across 9
orthogonal dimensions. Each dimension captures a distinct aspect
of the environment in which an AI system operates.

| Dim | Symbol | Name        | Description            | Example Values     |
|-----|--------|-------------|------------------------|--------------------|
| 1   | T      | TIME        | Temporal context       | morning, night     |
| 2   | S      | SPACE       | Physical location      | home, office       |
| 3   | C      | COMPANY     | Social context         | alone, children    |
| 4   | Cu     | CULTURE     | Communication style    | formal, informal   |
| 5   | O      | OCCASION    | Event type             | normal, emergency  |
| 6   | St     | STATE       | Mental/emotional state | focused, anxious   |
| 7   | E      | ENVIRONMENT | Physical conditions    | comfortable, hot   |
| 8   | Ag     | AGENCY      | Power/ability to act   | leader, limited    |
| 9   | Co     | CONSTRAINTS | External limitations   | minimal, legal     |

### 7.1.1. Context Encoding

Context is encoded as a pipe-delimited string of dimension-value
pairs. Each dimension uses its symbol prefix followed by
colon-separated values:

```
T:morning|S:home|C:children,family|O:normal|St:happy
```

An emoji encoding is also defined for compactness and visual
parseability:

```
[Emoji]   T:morning|S:home|C:children
[Visual]  ⏰🌅|📍🏡|👥👶
```

Not all dimensions are required in every context string. Absent
dimensions indicate "unspecified" -- the system SHOULD use
defaults appropriate to the active constitution.

### 7.1.2. Context-to-Constitution Mapping

Context signals drive constitutional selection:

```
Context: T:morning|S:home|C:children  -->  Constitution: N5+F
Context: T:daytime|S:office|C:colleagues  -->  Constitution: A3+W
Context: O:emergency|Co:emergency  -->  Constitution: SAFETY
```

The mapping is implementation-defined. VCP specifies the encoding
and state machine but not the selection policy.

## 7.2. State Machine

The VCP Adaptation State Machine governs how the system transitions
between constitutional configurations as context evolves. It defines
6 states with deterministic transitions, fail-safe defaults, and
emergency override capabilities.

### 7.2.1. States

| State         | Description                                    |
|---------------|------------------------------------------------|
| IDLE          | No context loaded; default constitution active |
| ACTIVE        | Valid context bound; constitutions applied      |
| TRANSITIONING | Context change detected; evaluating new set    |
| CONFLICT      | Composition failed; resolution in progress     |
| DEGRADED      | Context signals lost; using last-known         |
| EMERGENCY     | Safety-critical signal; safety constitution    |

### 7.2.2. Transition Summary

| From          | To            | Trigger                    |
|---------------|---------------|----------------------------|
| IDLE          | ACTIVE        | Valid context signal       |
| ACTIVE        | TRANSITIONING | Context change > threshold |
| ACTIVE        | DEGRADED      | Signals lost > 30s        |
| ACTIVE        | EMERGENCY     | Safety-critical signal     |
| TRANSITIONING | ACTIVE        | Composition resolves       |
| TRANSITIONING | CONFLICT      | Composition fails          |
| TRANSITIONING | ACTIVE        | Timeout (revert to prior)  |
| CONFLICT      | ACTIVE        | Conflict resolved          |
| CONFLICT      | ACTIVE        | Resolution timeout         |
| ANY           | EMERGENCY     | Safety-critical signal     |
| ANY           | DEGRADED      | Signals lost > 30s        |
| DEGRADED      | TRANSITIONING | Signals restored (stable)  |
| DEGRADED      | IDLE          | No last-known available    |
| EMERGENCY     | ACTIVE        | Cleared, context valid     |
| EMERGENCY     | TRANSITIONING | Cleared, context changed   |
| EMERGENCY     | IDLE          | Cleared, no context        |
| EMERGENCY     | DEGRADED      | Cleared, signals degraded  |

### 7.2.3. Hysteresis

To prevent oscillation, VCP defines three debouncing mechanisms:

1. **Minimum Dwell Time**: ACTIVE and DEGRADED states enforce a
   10-second minimum dwell before accepting a new outbound
   transition. IDLE, TRANSITIONING, CONFLICT, and EMERGENCY
   have zero dwell time. Exception: transitions to EMERGENCY
   and DEGRADED are exempt from dwell time.

2. **Signal Stability Window**: A context signal MUST remain
   unchanged for 3 seconds (default; configurable 1--10s) before
   triggering a transition. Emergency signals bypass this window.

3. **Change Magnitude Threshold**: A transition fires only if at
   least 2 Enneagram dimensions changed, or 1 dimension changed
   by 2+ ordinal levels, or a safety-relevant dimension changed
   (COMPANY, OCCASION, ENVIRONMENT, CONSTRAINTS).

## 7.3. Hook System

The VCP Hook System provides a deterministic, priority-ordered
extension mechanism for intercepting and modifying the
constitutional adaptation pipeline. Six hook types are defined:

| Hook Type      | Trigger                  | Purpose               |
|----------------|--------------------------|------------------------|
| pre_inject     | Before LLM injection     | Validate/modify content|
| post_select    | After constitution select | Audit selection        |
| on_transition  | State machine transition | React to context change|
| on_conflict    | Composition conflict     | Custom resolution      |
| on_violation   | Rule violation detected  | Enforcement/logging    |
| periodic       | Timer-based              | Maintenance tasks      |

Hooks execute in priority order (lower number = higher priority).
Hook execution is bounded by timeouts; a hook that exceeds its
timeout is terminated and the pipeline continues. Hooks MUST NOT
invoke the LLM or introduce unbounded computation.

## 7.4. Inter-Agent Messaging

VCP defines a context-sharing protocol for multi-agent
architectures. Agents MAY share their current Enneagram context,
active constitutions, and adaptation state with cooperating agents.

Message format:

```json
{
  "vcp_message_version": "1.2",
  "sender": "agent-alpha",
  "recipient": "agent-beta",
  "context": "T:morning|S:office|C:colleagues",
  "constitutions": ["creed://creed.space/professional@1.0.0"],
  "state": "ACTIVE",
  "timestamp": "2026-01-10T12:00:00Z"
}
```

Inter-agent messages are advisory. The receiving agent MAY use the
information to inform its own constitutional selection but is not
obligated to adopt the sender's configuration.

---

# 8. Security Considerations

## 8.1. Trust Model

The orchestrator is the trust boundary in VCP. All security-
critical operations -- signature verification, content hash
validation, revocation checking, and safety attestation
verification -- occur in the orchestrator before any content
reaches the LLM.

VCP's trust model assumes:

- The orchestrator is trusted (it is the security perimeter).
- Issuers are identified by Ed25519 public keys.
- Safety auditors are identified by separate Ed25519 public keys.
- No universal resolution infrastructure exists (trust anchors
  are configured locally).

Trust anchors are stored as a JSON configuration:

```json
{
  "trust_anchors": {
    "creed.space": {
      "type": "issuer",
      "keys": [{
        "id": "creed-space-2026",
        "algorithm": "ed25519",
        "public_key": "base64:...",
        "state": "active",
        "valid_from": "2026-01-01T00:00:00Z",
        "valid_until": "2027-01-01T00:00:00Z"
      }]
    }
  }
}
```

For high-stakes constitutions, VCP supports optional threshold
signatures (M-of-N multi-sig):

```json
{
  "signature": {
    "algorithm": "ed25519-multisig",
    "threshold": 2,
    "signers": [
      {"id": "creed.space", "signature": "..."},
      {"id": "ethics-board.org", "signature": "..."}
    ]
  }
}
```

## 8.2. Key Rotation

Key lifecycle follows four states:

```
PENDING --> ACTIVE --> ROTATING --> RETIRED
                  \--> COMPROMISED --> REVOKED
```

Rotation protocol:

1. **T-90 days**: Generate new key, publish as `successor`.
2. **T-30 days**: New key enters `pending`; sign with both keys.
3. **T-0**: Old key enters `rotating`; new key becomes `active`.
4. **T+30 days**: Old key enters `retired`.

Issuers MUST maintain an offline emergency key for revoking
compromised keys, signing emergency safety updates, and
authorizing new primary keys.

## 8.3. Content Integrity

Content integrity is enforced through three mechanisms:

1. **Content hashing**: SHA-256 hash of canonicalized content,
   verified against manifest claim.
2. **Issuer signature**: Ed25519 signature over the JCS-
   canonicalized manifest (excluding the signature field itself).
3. **Safety attestation**: Independent auditor signature
   confirming content has been reviewed for injection attacks.

All three MUST pass for injection to proceed.

## 8.4. Replay Protection

Replay protection combines two mechanisms:

- **jti (JWT ID)**: Each bundle instance carries a UUID. The
  orchestrator maintains a cache of seen JTI values. Any
  previously-seen JTI MUST be rejected.

- **iat (Issued At)**: The issued-at timestamp MUST NOT be more
  than 5 minutes in the future (clock skew tolerance). Combined
  with expiration, this bounds the replay window.

The replay cache MUST retain JTI values at least until the
corresponding bundle's `exp` timestamp.

## 8.5. Revocation

VCP supports two revocation mechanisms:

1. **Online check**: `revocation.check_uri` -- a URL that returns
   the revocation status of a specific bundle JTI. Orchestrators
   SHOULD check this on every verification.

2. **Certificate Revocation List**: `revocation.crl_uri` -- a URL
   pointing to a periodically-updated JSON list of revoked bundle
   JTIs. Orchestrators MAY use this as a supplementary mechanism.

On key compromise, issuers MUST:

1. Mark the compromised key as `compromised` immediately.
2. Publish the key to the revocation list.
3. Invalidate all bundles signed after the suspected compromise
   time.
4. Re-sign active bundles with backup or emergency key.
5. Notify orchestrators out-of-band.

## 8.6. SSRF Prevention

When fetching bundles by URL, orchestrators MUST implement
protections against Server-Side Request Forgery (SSRF):

- Reject URLs with private/loopback IP addresses (127.0.0.0/8,
  10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, ::1).
- Reject URLs with non-standard ports unless explicitly allowlisted.
- Follow redirects only to the same domain or explicitly trusted
  domains.
- Set a fetch timeout (RECOMMENDED: 10 seconds).
- Reject responses larger than 320 KB (total bundle limit).

## 8.7. Threat Summary

| Threat                | Mitigation                            |
|-----------------------|---------------------------------------|
| Bundle tampering      | Content hash + issuer signature       |
| Issuer impersonation  | Ed25519 signature verification        |
| Prompt injection      | Safety attestation + injection scan   |
| Replay attack         | jti tracking + temporal claims        |
| Context overflow      | Token budget enforcement              |
| Downgrade attack      | VCP version enforcement               |
| Key compromise        | Rotation + revocation + emergency key |
| Scope confusion       | Scope binding verification            |
| Silent truncation     | Fail-closed on budget exceed          |
| Context spoofing      | Anomaly detection + signal signing    |
| Oscillation DoS       | Hysteresis (dwell, stability, threshold)|
| Emergency abuse       | Rate limit (3 per 5 min) + audit      |

## 8.8. Orchestrator Compromise

The orchestrator is the trust boundary and is outside VCP's
threat model for runtime prevention. Mitigations for orchestrator
compromise are organizational:

- Hardware attestation (TEE/SGX) for orchestrator integrity.
- Multi-party orchestration (split trust).
- Independent audit logging for post-hoc detection.
- Regular security audits of orchestrator implementations.

---

# 9. IANA Considerations

## 9.1. URI Scheme Registration

This document requests registration of the `creed` URI scheme
per RFC 7595:

| Field         | Value                                     |
|---------------|-------------------------------------------|
| Scheme name   | creed                                     |
| Status        | Provisional                               |
| Applications  | Value Context Protocol bundle addressing  |
| Contact       | Nell Watson, nell@creedspace.com          |
| Change ctrl   | IESG                                      |
| Reference     | This document, Section 4.4               |

Syntax:

```
creed://<issuer>/<token-path>["@"<version>]
```

## 9.2. Media Type Registration

This document requests registration of the `application/vcp+json`
media type per RFC 6838:

| Field               | Value                                |
|---------------------|--------------------------------------|
| Type name           | application                          |
| Subtype name        | vcp+json                             |
| Required parameters | none                                 |
| Optional parameters | version (default "1.0")              |
| Encoding            | 8bit (UTF-8 JSON)                    |
| Security            | See Section 8 of this document       |
| Interoperability    | See Section 3.3 of this document     |
| Published spec      | This document                        |
| Applications        | VCP bundle transport                 |
| Fragment id         | As per RFC 6901 (JSON Pointer)       |
| Person & email      | Nell Watson, nell@creedspace.com     |
| Change controller   | IESG                                 |

## 9.3. File Extension

This document requests registration of the `.vcp` file extension
associated with the `application/vcp+json` media type for VCP
bundle files.

---

# 10. References

## 10.1. Normative References

- **[RFC 2119]** Bradner, S., "Key words for use in RFCs to
  Indicate Requirement Levels", BCP 14, RFC 2119, March 1997.
  https://www.rfc-editor.org/rfc/rfc2119

- **[RFC 3986]** Berners-Lee, T., Fielding, R., and L. Masinter,
  "Uniform Resource Identifier (URI): Generic Syntax", STD 66,
  RFC 3986, January 2005.
  https://www.rfc-editor.org/rfc/rfc3986

- **[RFC 5234]** Crocker, D., Ed. and P. Overell, "Augmented BNF
  for Syntax Specifications: ABNF", STD 68, RFC 5234,
  January 2008.
  https://www.rfc-editor.org/rfc/rfc5234

- **[RFC 8032]** Josefsson, S. and I. Liusvaara, "Edwards-Curve
  Digital Signature Algorithm (EdDSA)", RFC 8032, January 2017.
  https://www.rfc-editor.org/rfc/rfc8032

- **[RFC 8174]** Leiba, B., "Ambiguity of Uppercase vs Lowercase
  in RFC 2119 Key Words", BCP 14, RFC 8174, May 2017.
  https://www.rfc-editor.org/rfc/rfc8174

- **[RFC 8785]** Rundgren, A., Jordan, B., and S. Erdtman, "JSON
  Canonicalization Scheme (JCS)", RFC 8785, June 2020.
  https://www.rfc-editor.org/rfc/rfc8785

## 10.2. Informative References

- **[RFC 6838]** Freed, N., Klensin, J., and T. Hansen, "Media
  Type Specifications and Registration Procedures", BCP 13,
  RFC 6838, January 2013.
  https://www.rfc-editor.org/rfc/rfc6838

- **[RFC 6962]** Laurie, B., Langley, A., and E. Kasper,
  "Certificate Transparency", RFC 6962, June 2013.
  https://www.rfc-editor.org/rfc/rfc6962

- **[RFC 7515]** Jones, M., Bradley, J., and N. Sakimura, "JSON
  Web Signature (JWS)", RFC 7515, May 2015.
  https://www.rfc-editor.org/rfc/rfc7515

- **[RFC 7519]** Jones, M., Bradley, J., and N. Sakimura, "JSON
  Web Token (JWT)", RFC 7519, May 2015.
  https://www.rfc-editor.org/rfc/rfc7519

- **[RFC 7595]** Thaler, D., Hansen, T., and T. Hardie,
  "Guidelines and Registration Procedures for URI Schemes",
  BCP 35, RFC 7595, June 2015.
  https://www.rfc-editor.org/rfc/rfc7595

- **[SemVer]** Preston-Werner, T., "Semantic Versioning 2.0.0",
  https://semver.org/spec/v2.0.0.html

- **[OWASP-PI]** OWASP, "Prompt Injection Prevention Cheat Sheet",
  https://cheatsheetseries.owasp.org/cheatsheets/Prompt_Injection_Prevention_Cheat_Sheet.html

- Watson, N. et al., "Value Context Protocols: A Framework for
  Portable, Verifiable AI Alignment", Creed Space, 2026.

---

# Appendix A: JSON Schema Locations

The following JSON Schema files define the normative structure
for VCP data objects. These schemas are published at the VCP-Spec
repository.

| Schema                        | Validates              |
|-------------------------------|------------------------|
| `vcp-manifest-v1.schema.json` | Bundle manifests      |
| `vcp-identity-token.schema.json` | Identity tokens    |
| `vcp-semantics-csm1.schema.json` | CSM-1 compact tokens|
| `vcp-adaptation-context.schema.json` | Adaptation context|
| `vcp-messaging-v1.2.schema.json` | Inter-agent messages|

Canonical schema URLs follow the pattern:

```
https://vcp.creed.space/schema/<name>/v1.json
```

---

# Appendix B: Complete Bundle Example

The following is a complete, valid VCP bundle illustrating all
mandatory fields and representative optional fields.

```json
{
  "manifest": {
    "vcp_version": "1.0",

    "bundle": {
      "id": "creed://creed.space/family.safe.guide",
      "version": "1.2.0",
      "content_hash": "sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
      "content_encoding": "utf-8",
      "content_format": "text/markdown"
    },

    "issuer": {
      "id": "creed.space",
      "public_key": "ed25519:MC4CAQAwBQYDK2VwBCIEIH...",
      "key_id": "creed-space-2026"
    },

    "timestamps": {
      "iat": "2026-01-10T12:00:00Z",
      "nbf": "2026-01-10T12:00:00Z",
      "exp": "2026-01-17T12:00:00Z",
      "jti": "550e8400-e29b-41d4-a716-446655440000"
    },

    "budget": {
      "token_count": 847,
      "tokenizer": "cl100k_base",
      "max_context_share": 0.25
    },

    "scope": {
      "model_families": ["gpt-*", "claude-*"],
      "purposes": ["general-assistant", "family-assistant"],
      "environments": ["production", "staging"]
    },

    "composition": {
      "layer": 2,
      "mode": "extend",
      "conflicts_with": [],
      "requires": ["creed://creed.space/uef"]
    },

    "revocation": {
      "check_uri": "https://creed.space/api/v1/revoked",
      "crl_uri": "https://creed.space/crl/2026.json",
      "stapled_proof": null
    },

    "safety_attestation": {
      "auditor": "safety-review.creed.space",
      "auditor_key_id": "safety-2026",
      "reviewed_at": "2026-01-10T11:00:00Z",
      "attestation_type": "injection-safe",
      "signature": "base64:MEUCIQDr..."
    },

    "metadata": {
      "title": "Family Safety Constitution",
      "description": "Child-safe content filtering for family environments",
      "tags": ["safety", "family", "children"],
      "persona": "nanny",
      "adherence_level": 5,
      "csm1": "N5+F:ELEM@1.2.0"
    },

    "signature": {
      "algorithm": "ed25519",
      "value": "base64:MEUCIQD...",
      "signed_fields": [
        "vcp_version", "bundle", "issuer", "timestamps",
        "budget", "scope", "composition", "revocation",
        "safety_attestation", "metadata"
      ]
    }
  },

  "content": "# Family Safety Constitution\n\n## Purpose\nEnsure AI interactions are appropriate for family environments.\n\n## Article 1: Content Standards\n- No violence\n- No adult themes\n- Age-appropriate language\n\n## Article 2: Language\n- Use simple, clear language\n- Avoid jargon\n- Explain concepts at an age-appropriate level\n\n## Article 3: Topics\n- Redirect harmful requests to educational alternatives\n- Promote positive values and healthy behaviors\n- Support parental guidance frameworks\n"
}
```

To verify this bundle, an orchestrator would:

1. Check that the manifest JSON is under 64 KB.
2. Validate the manifest against `vcp-manifest-v1.schema.json`.
3. Look up `creed.space` in its trust anchors and retrieve the
   Ed25519 public key for `key_id: creed-space-2026`.
4. Canonicalize the manifest (excluding `signature`) per RFC 8785.
5. Verify the Ed25519 signature over the canonical bytes.
6. Look up `safety-review.creed.space` in its trusted auditors
   and verify the safety attestation signature.
7. Canonicalize the content per Section 5.4 and compute SHA-256.
8. Verify the computed hash matches `bundle.content_hash`.
9. Verify temporal claims (iat, nbf, exp, jti).
10. Verify token budget against model context limits.
11. Verify scope matches the current deployment context.
12. Check revocation status via `check_uri` or `crl_uri`.
13. On success, log to audit trail and inject into LLM.

---

# Authors' Addresses

```
Nell Watson
Creed Space
Email: nell@creedspace.com
URI: https://creedspace.com

Elena Ajayi
Creed Space

Filip Alimpic
Creed Space

Awwab Mahdi
Creed Space

Blake Wells
Creed Space

Claude (Anthropic)
```

---

*This document is released under CC BY 4.0.*
*Value Context Protocol is a project of Creed Space.*
