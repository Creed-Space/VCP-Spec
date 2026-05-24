# VCP Security Model

<!-- wiki:type = system -->
<!-- wiki:scope = vcp-spec -->
<!-- wiki:created = 2026-05-23 -->
<!-- wiki:updated = 2026-05-23 -->
<!-- wiki:status = active -->

## Summary

VCP v3.1 adds a cross-cutting security layer below the six-layer stack: context encryption (Fernet), injection scanning (12 patterns), context opacity (4 protection levels), revocation infrastructure (CRL + OCSP), and a tamper-evident audit chain (SHA-256 hash chain). All five mechanisms are mandatory in production environments. Full spec at `specs/core/security.md`. (`specs/core/security.md`, `specs/VCP_SPECIFICATION_v3.1.md`, §3)

## SS1 — Context Encryption

**Threat model**: GRP-Obliteration — adversary with read access to persistence layer (Redis, database backups) must not recover personal signals. (`specs/core/security.md`, §SS1.1)

**Algorithm**: Fernet symmetric encryption (AES-128-CBC + HMAC-SHA256). Authenticated encryption: ciphertext integrity verified before decryption. (`specs/core/security.md`, §SS1.2)

**Key management**: `VCP_CONTEXT_ENCRYPTION_KEY` environment variable, URL-safe base64-encoded 32 bytes. Rotation via `MultiFernet` with comma-separated keys (first = current). Zero-downtime rotation: prepend new key, wait for old sessions to expire, remove old key. (`specs/core/security.md`, §SS1.3, SS1.3.1)

**Encryption operations**:
- `encrypt_context_value(plaintext)` → prefixes result with `enc:` to tag encrypted values
- `decrypt_context_value(ciphertext)` → strips prefix, decrypts; strips `enc:` from result
- In `production`/`staging` environments: encryption MUST be active; missing key raises `RuntimeError`
- In development: plaintext passthrough permitted

(`specs/core/security.md`, §SS1.4)

## SS2 — Injection Scanning

**Threat model**: Constitutional content submitted by third parties may contain prompt injection attempts. All constitution content MUST pass scanning before use. (`specs/core/security.md`, §SS2)

**12 detection patterns** (8 OWASP, 2 VCP-specific, 2 Unicode):
- OWASP-derived: ignore instructions, override, jailbreak, role-play as, you are now, forget constraints, DAN, new instructions
- VCP-specific: constitutional override patterns, trust anchor manipulation
- Unicode: homoglyph substitution, invisible character injection

(`specs/core/security.md`, §SS2; `specs/VCP_SPECIFICATION_v3.1.md`, §3.2)

## SS3 — Context Opacity

**Threat model**: Raw personal signals (cognitive state, emotional tone, energy) represent psychographic data and must not reach inference models. (`specs/core/security.md`, §SS3; VEP-0004 Welfare motivation)

**Protection levels** (computed from vulnerability scoring):

| Level | Description |
|-------|-------------|
| STANDARD | Default; moderate protection |
| ELEVATED | Sensitive dimensions flagged |
| HIGH | Significant vulnerability indicators |
| CRITICAL | Immediate safety concern |

Only the protection level (not raw signal values) is exposed to the LLM. Directionality invariant: protection level must never decrease as vulnerability score increases. (`specs/core/security.md`, §SS3; `specs/VCP_SPECIFICATION_v3.1.md`, §3.3)

**VCP-X-Personal compliance**: personal signals consumed via VCP-X-Personal MUST NOT be forwarded raw. This constraint applies whether or not the extension is negotiated — the opacity layer is below the extension stack. (`specs/extensions/VCP-X-Personal/spec.md`, §1 Design Principle)

## SS4 — Revocation Infrastructure

**Mechanisms**:
- CRL (Certificate Revocation List): distributed list of revoked bundle IDs
- OCSP-style stapled proofs: per-bundle revocation status attached at validation time

**Signature algorithms**: Ed25519 (preferred) or HMAC-SHA256. (`specs/VCP_SPECIFICATION_v3.1.md`, §3.4)

**Fail-closed**: if all revocation sources are unavailable, treat as revoked. No silent passthrough when revocation cannot be checked. (`specs/core/security.md`, §SS4)

## SS5 — Tamper-Evident Audit Chain

**Algorithm**: SHA-256 hash chain with canonical JSON serialization.

**Storage**: PostgreSQL advisory locks for append-only integrity. Privacy-preserving: entry hashes truncated to 128 bits (prevents raw-data inference from hash comparison). (`specs/VCP_SPECIFICATION_v3.1.md`, §4.1)

**Audit entries** include: bundle ID, action type, actor identity (hashed), timestamp, previous entry hash. Chain integrity verifiable by replaying hashes from genesis entry.

## VCP-X-Relational Security Notes

VCP-X-Relational adds privacy layers to relational context fields:
- `PRIVATE`: partner-only, MUST NOT be forwarded to downstream participants
- `ATTESTABLE`: verifiable claims for chain participants
- `PUBLIC`: minimal, non-sensitive metadata

(`specs/extensions/VCP-X-Relational/spec.md`, §2 Design Principles)

Relational operations are feature-flagged via `RELATIONAL_CONTEXT_ENABLED`. When false, all relational operations are no-ops with zero storage writes. (`specs/extensions/VCP-X-Relational/spec.md`, §2)

## Security Features in Capability Negotiation

Active core security features are reported in `vcp-ack.core_features`. A client can inspect which security mechanisms are active before sending context data. (`veps/VEP-0002-capability-negotiation.md`, VCP-Ack field `core_features`)

## Provenance

- Sources consulted: `specs/core/security.md`, `specs/VCP_SPECIFICATION_v3.1.md`, `veps/VEP-0002-capability-negotiation.md`, `specs/extensions/VCP-X-Relational/spec.md`, `specs/extensions/VCP-X-Personal/spec.md`
- Last verified against sources: 2026-05-23

## See Also

- [[vcp-spec:systems/itsame-architecture]] — security sits below all six layers
- [[vcp-spec:systems/capability-negotiation]] — core_features advertised in handshake
- [[vcp-spec:systems/vep-specs]] — VEP-0003 MCP bridge and VEP-0004 welfare dimensions
- [[vcp-spec:domain/extension-model]] — VCP-X-Welfare adds embodied safety margins
