# VCP Core: Audit Chain Specification

**Section**: SS12
**Status**: Stable
**Version**: 1.1.0
**Project-maintained implementation**: `services/vcp/audit.py`, `services/vcp/audit_chain.py`, `services/vcp/audit_store.py`

---

## 1. Overview

The VCP audit chain provides tamper-evident, privacy-preserving logging of all
VCP verification operations. Every verification produces an AuditEntry that is
appended to a SHA-256 hash chain. Each entry's hash includes the previous
entry's hash, creating an unbroken chain where any modification to a historical
entry invalidates all subsequent hashes.

The audit system operates at four configurable detail levels and supports two
storage backends: an in-memory store for development and a PostgreSQL store for
production deployments.


## 2. Design Principles

### 2.1 Privacy Preservation

Audit logs MUST NOT contain full constitution content, raw user messages, or
personally identifiable information. All identifiers (session IDs, bundle IDs,
issuer IDs) are stored as keyed one-way privacy hashes (Section 6). Content is
represented only by its cryptographic hash, never by its plaintext. Hashing is
pseudonymization, not anonymization: stable or low-entropy identifiers remain
linkable across entries, so deployments MUST separately address minimisation,
access control, retention, and erasure (see VCP v3.1 §4.1).

### 2.2 Append-Only

The audit chain is strictly append-only. There is no update or delete operation.
Entries may be queried and verified but never modified after insertion. This
property is enforced at the application level (for in-memory stores) and at the
database level (for PostgreSQL stores, via table permissions and advisory locks).

### 2.3 Tamper Evidence

The hash chain provides cryptographic tamper evidence. Modifying any entry --
changing a field, inserting a record, or deleting a record -- produces a hash
mismatch that is detectable by the verification procedure defined in Section 5.


## 3. Data Model

### 3.1 AuditLevel

Controls the verbosity of audit entries. Higher levels include all fields from
lower levels.

| Level        | Description                                                              |
|--------------|--------------------------------------------------------------------------|
| `minimal`    | Timestamp, session hash, verification result, bundle reference.          |
| `standard`   | Minimal fields plus checks passed, manifest signature.                   |
| `full`       | Standard fields plus duration_ms, token_count.                           |
| `diagnostic` | Full fields plus content_preview (first 100 characters of bundle content). Intended for debugging only. MUST NOT be used in production. |

### 3.2 AuditEntry

The in-flight representation of an audit log entry before chain insertion.

| Field                | Type              | Level      | Description                                                        |
|----------------------|-------------------|------------|--------------------------------------------------------------------|
| `timestamp`          | datetime          | minimal    | UTC time of the verification event.                                |
| `session_id_hash`    | string            | minimal    | Privacy hash of the session identifier.                            |
| `verification_result`| string            | minimal    | Verification outcome name (e.g., `"VALID"`, `"EXPIRED"`).         |
| `checks_passed`      | array of string   | standard   | Ordered list of verification checks that passed.                   |
| `bundle_id_hash`     | string            | minimal    | Privacy hash of the bundle identifier.                             |
| `content_hash`       | string            | minimal    | SHA-256 hash of the bundle content.                                |
| `issuer_hash`        | string            | minimal    | Privacy hash of the bundle issuer identifier.                      |
| `version`            | string            | minimal    | Bundle manifest version string.                                    |
| `manifest_signature` | string            | standard   | Truncated manifest signature (first 32 characters plus `"..."`).   |
| `audit_level`        | AuditLevel        | minimal    | The detail level at which this entry was recorded.                 |
| `request_id`         | string or null    | standard   | Privacy hash of the request identifier, if available.              |
| `duration_ms`        | integer or null   | full       | Verification duration in whole milliseconds.                       |
| `token_count`        | integer or null   | full       | Token count from the bundle's budget manifest.                     |
| `content_preview`    | string or null    | diagnostic | First 100 characters of bundle content. Diagnostic only.           |

### 3.3 AuditStoreEntry

The storage representation, extending AuditEntry with chain metadata.

| Field                | Type              | Description                                                        |
|----------------------|-------------------|-------------------------------------------------------------------|
| `session_id_hash`    | string            | Privacy hash of the session identifier.                            |
| `request_id_hash`    | string or null    | Privacy hash of the request identifier.                            |
| `verification_result`| string            | Verification outcome name.                                         |
| `checks_passed`      | array of string   | Ordered list of checks that passed.                                |
| `failed_step`        | string or null    | Name of the first check that failed, if any.                       |
| `duration_ms`        | integer or null   | Verification duration in whole milliseconds.                       |
| `bundle_id_hash`     | string            | Privacy hash of the bundle identifier.                             |
| `content_hash`       | string            | SHA-256 hash of the bundle content.                                |
| `issuer_hash`        | string            | Privacy hash of the issuer identifier.                             |
| `bundle_version`     | string            | Bundle manifest version string.                                    |
| `manifest_signature` | string            | Truncated manifest signature.                                      |
| `audit_level`        | string            | Audit level value (e.g., `"standard"`).                            |
| `token_count`        | integer or null   | Token count from the budget manifest.                              |
| `content_preview`    | string or null    | Content preview (diagnostic level only).                           |
| `created_at`         | string            | RFC 3339 UTC timestamp with trailing `Z`.                          |
| `chain_position`     | integer           | Monotonically increasing position in the hash chain.               |
| `previous_hash`      | string or null    | SHA-256 hex digest of the previous entry's hash. Null for the genesis entry. |
| `entry_hash`         | string            | SHA-256 hex digest of this entry.                                  |


## 4. Hash Chain Algorithm

### 4.1 Hash Fields

The hash is computed over exactly 15 fields, in canonical order:

```
session_id_hash, request_id_hash, verification_result, checks_passed,
failed_step, duration_ms, bundle_id_hash, content_hash, issuer_hash,
bundle_version, manifest_signature, audit_level, previous_hash,
chain_position, created_at
```

### 4.2 Computation Procedure

Given an entry dict `E` and the previous entry's hash `P`:

1. **Extract**: For each of the 15 hash fields, extract the value from `E`.
   If a field contains an array, sort the array elements lexicographically.
2. **Link**: Set `previous_hash` to `P`. For the genesis entry (first entry
   in the chain), the stored `previous_hash` is `null` but the hashed value
   is the JSON string `""`.
3. **Serialize**: Serialize the 15-field object using the RFC 8785 JSON
   Canonicalization Scheme (JCS), as adopted in VCP v1.1 Amendment D. JSON
   `null` is serialized as the literal `null`, booleans as `true`/`false`,
   integers without a fractional part, and strings with JCS escaping and
   UTF-8 encoding. No language-specific string conversion is permitted.
4. **Hash**: Compute SHA-256 over the UTF-8 encoding of the serialized string.
5. **Output**: The hex digest of the SHA-256 hash is the `entry_hash`.

### 4.3 Genesis Entry

The first entry in the chain has:
- `chain_position`: 1
- `previous_hash`: stored as `null`; hashed as the JSON string `""`

### 4.4 Pseudocode

```
function compute_entry_hash(entry, previous_hash):
    hashable = {}
    for field in HASH_FIELDS:
        value = entry[field]
        if is_array(value):
            value = sort(value)
        hashable[field] = value

    hashable["previous_hash"] = previous_hash or ""

    canonical = rfc8785_canonicalize(hashable)   # JCS, VCP v1.1 Amendment D
    return sha256(utf8_encode(canonical)).hex_digest()
```

Test vector (genesis entry, `previous_hash` hashed as `""`):

```
input  = {"audit_level":"minimal","bundle_id_hash":"hmac-sha256:0123456789abcdef0123456789abcdef",
          "bundle_version":"1.0.0","chain_position":1,"checks_passed":["hash","signature"],
          "content_hash":"sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          "created_at":"2026-02-28T00:00:00Z","duration_ms":12,"failed_step":null,
          "issuer_hash":"hmac-sha256:fedcba9876543210fedcba9876543210",
          "manifest_signature":"base64:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA...",
          "previous_hash":"","request_id_hash":null,
          "session_id_hash":"hmac-sha256:00112233445566778899aabbccddeeff",
          "verification_result":"VALID"}
JCS    = the object above with keys in code-point order, no whitespace
entry_hash = aa0de40bf33cf3cc0326564f5fd567a0edf52d48bacf3a5ce8d3a1f593d91073
```


## 5. Chain Verification

### 5.1 Verification Procedure

Given an ordered list of audit entries `[E_1, E_2, ..., E_n]`:

For each entry `E_i` (where `i` ranges from 1 to `n`):

1. **Position monotonicity**: If `i > 1`, verify that
   `E_i.chain_position > E_{i-1}.chain_position`. If not, the chain is
   **INVALID** at position `E_i.chain_position`.

2. **Hash linkage**: Verify that `E_i.previous_hash` equals
   `E_{i-1}.entry_hash`. For `i == 1`, `E_1.previous_hash` must be `null`.
   If the linkage fails, the chain is **BROKEN** at position
   `E_i.chain_position`.

3. **Entry hash integrity**: Recompute `E_i`'s hash using the algorithm in
   Section 4.2 with `previous_hash = E_{i-1}.entry_hash` (or `null` for
   `i == 1`). Compare the computed hash to `E_i.entry_hash`. If they differ,
   the entry has been **TAMPERED** at position `E_i.chain_position`.

If all entries pass all three checks, the chain segment is **VALID**.

### 5.2 Partial Verification

The verification procedure supports partial chain verification over arbitrary
position ranges. This is useful for incremental audits of large chains. When
verifying a range `[start, end]`, the first entry in the range has its
`previous_hash` validated against the entry immediately before the range (if
available) or accepted as given (if the prior entry is not loaded).

### 5.3 Return Value

Verification returns a tuple of `(is_valid: boolean, error_message: string or null)`.
- On success: `(true, null)`
- On failure: `(false, "<description of the first detected violation>")`


## 6. Privacy Hash Function

All identifiers stored in the audit chain are processed through the privacy
hash function before storage:

```
function privacy_hash(value):
    full_hash = hmac_sha256(K_audit, utf8_encode(value)).hex_digest()
    return "hmac-sha256:" + full_hash[0:32]
```

`K_audit` is a deployment secret dedicated to audit pseudonymization, managed
and rotated under the key lifecycle rules of VCP v1.1 Amendment F. This
produces a 128-bit (32 hex character) truncated tag prefixed with
`"hmac-sha256:"`. The truncation provides sufficient collision resistance for
audit purposes while reducing storage requirements; the prefix names the
algorithm, supporting migration.

The unkeyed legacy form `"sha256:" + sha256(value)[0:32]` MAY be used only
where the input carries at least 128 bits of entropy (for example a random
UUID request ID) and MUST be recognised by verifiers of pre-existing chains.
Session IDs, bundle IDs, and issuer IDs are low-entropy or enumerable, so an
unkeyed hash over them is a dictionary-reversible pseudonym and MUST NOT be
used for new entries.


## 7. Storage Backends

### 7.1 InMemoryAuditStore

A list-backed store for development and testing.

**Properties**:
- Entries stored in a Python list, ordered by insertion.
- `_last_hash` tracks the most recent entry hash for chain linkage.
- `_next_position` tracks the next chain position (starts at 1).
- Supports the same query interface as the PostgreSQL store.
- No persistence guarantees -- entries are lost on process restart.

**Operations**:
- `append(entry)`: Compute hash, append to list, return chain position.
- `get_entries(...)`: Filter by session hash, bundle hash, issuer hash, or verification result. Supports limit/offset.
- `get_all_entries()`: Return all entries for full chain verification.
- `verify_chain()`: Delegate to `AuditChainBuilder.verify_chain()`.

### 7.2 PostgresAuditStore

An append-only PostgreSQL table with advisory locking.

**Table**: `vcp_audit_log`

**Concurrency control**: Uses `pg_advisory_xact_lock` with lock ID `0x56435041`
(ASCII: `VCPA`) to serialize chain writes within a transaction. This prevents
concurrent writes from computing hashes against stale `previous_hash` values.

**Append procedure** (within a single transaction):
1. Acquire advisory lock: `SELECT pg_advisory_xact_lock(0x56435041)`.
2. Read the last entry: `SELECT chain_position, entry_hash FROM vcp_audit_log ORDER BY chain_position DESC LIMIT 1`.
3. Compute `chain_position` as `last.chain_position + 1` (or `1` if no entries exist).
4. Compute `entry_hash` using `AuditChainBuilder.compute_entry_hash()`.
5. Insert the new row with all fields including `previous_hash`, `entry_hash`, and `chain_position`.
6. Commit. The advisory lock is released automatically at transaction end.

**Query operations**: Support filtering by session hash, bundle hash, issuer
hash, verification result, and time range (`since`/`until`). Results are ordered
by `chain_position ASC` with limit/offset pagination.

**Range verification**: `verify_chain_range(pool, start_position, end_position)`
loads entries in the specified range and delegates to `AuditChainBuilder.verify_chain()`.


## 8. Verification Check Order

When a bundle is verified, the audit entry records which checks passed. The
canonical check order for a fully valid bundle is:

```
size, schema, signature, attestation, hash, temporal, replay, budget, scope, revocation
```

For partial failures, the checks before the failing step are recorded. The
extended check order (used for finer-grained error mapping) is:

```
size, schema, issuer, signature, auditor, attestation, hash,
nbf, exp, timestamp, replay, tokens, budget, scope, revoked
```


## 9. Timestamp Format

All timestamps in audit entries use RFC 3339 UTC format with a trailing `Z`:

```
2026-02-28T14:30:00.000000Z
```

Naive datetime values (without timezone) are treated as UTC and formatted with
an appended `Z`. Timezone-aware values are converted to UTC before formatting,
with `+00:00` replaced by `Z`.


## 10. Security Considerations

- **Advisory lock scope**: The `pg_advisory_xact_lock` is transaction-scoped.
  If the transaction is long-running, it blocks other audit writes. Implementations
  SHOULD keep audit transactions short (under 100ms).
- **Linkability**: Privacy hashes are stable per key, so the same identifier
  yields the same pseudonym across entries and is linkable. Rotating `K_audit`
  breaks linkage across rotation boundaries. Deployments MUST treat pseudonymous
  audit rows as personal data for access, retention, and erasure purposes.
- **Hash algorithm migration**: The current implementation uses SHA-256. If
  migration to a different algorithm becomes necessary, a new column
  (`entry_hash_v2`) can be added alongside the existing column, with both
  maintained during a transition period.
- **Diagnostic level in production**: The `content_preview` field at diagnostic
  level contains raw bundle content. This level MUST NOT be enabled in production
  environments as it violates the privacy preservation requirement.
- **Chain gaps**: If entries are lost (e.g., due to storage failure), the chain
  cannot be verified across the gap. Implementations SHOULD alert on chain gaps
  and maintain secondary audit mechanisms (e.g., structured logs) as a fallback.


## 11. Conformance

An implementation conforms to VCP SS12 if it:

1. Computes entry hashes using the exact algorithm in Section 4.2.
2. Stores all 15 hash fields and does not omit any from the hash computation.
3. Implements chain verification per Section 5.1.
4. Uses the keyed privacy hash function from Section 6 for all identifier fields; the unkeyed `sha256:` form MAY be used only where the input has at least 128 bits of entropy.
5. Supports at least one storage backend (in-memory or PostgreSQL).
6. Enforces append-only semantics -- no update or delete operations on stored entries.
7. Respects audit level boundaries -- does not store diagnostic-level fields at lower levels.


## 12. Changelog

| Version | Date       | Changes                                                            |
|---------|------------|--------------------------------------------------------------------|
| 1.0.0   | 2026-02-28 | Initial stable release. SHA-256 hash chain with 15 fields, PostgreSQL and in-memory backends, four audit levels. |
| 1.1.0   | 2026-09-02 | Entry-hash serialization pinned to RFC 8785 JCS (Amendment D); `duration_ms` is an integer; privacy hash is keyed HMAC-SHA256 (`hmac-sha256:` prefix) with the unkeyed form restricted to high-entropy inputs; linkability caveat added. |
