# VCP Core: Capability Negotiation

**Specification Version**: 3.1.1
**Status**: Draft
**Authors**: Creed Space
**Date**: 2026-09-02
**Depends On**: VCP/I (Identity), VCP/T (Transport)

---

## 1. Introduction

This specification defines the capability negotiation handshake for the
Value-Context Protocol (VCP). Capability negotiation allows a VCP client and
server to agree on a protocol version, a set of active extensions, and
per-extension feature capabilities before exchanging context data.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in RFC 2119.

### 1.1 Design Goals

1. **Zero-cost for legacy clients.** A VCP 1.0 client that sends no handshake
   MUST still receive service at baseline capability.
2. **Fail-closed on version mismatch.** A server that cannot satisfy a
   client's `min_version` MUST reject with a structured error.
3. **Extension isolation.** Unsupported extensions are reported but never
   cause connection failure.
4. **MCP compatibility.** The handshake piggybacks on MCP's `initialize`
   flow when VCP operates as an MCP server.

### 1.2 Terminology

| Term | Definition |
|------|-----------|
| **Client** | The party initiating a VCP session (human-facing application, agent, or MCP host). |
| **Server** | The party providing VCP services (constitution enforcement, context adaptation). |
| **Extension** | An opt-in VCP capability namespace prefixed `VCP-X-`. |
| **Core Feature** | A capability provided by all conforming VCP 3.x servers (encryption, injection scanning, revocation, audit chain). |
| **Negotiated Version** | The protocol version both parties agree to use. |

---

## 2. Protocol Overview

Capability negotiation consists of three message types: `vcp-hello` (client to
server), `vcp-ack` (server to client), and `vcp-error` (server to client on
failure). The handshake completes in a single round trip.

```
  Client                              Server
    |                                    |
    |  -------- vcp-hello ----------->   |
    |                                    |
    |  <------- vcp-ack -------------|   |  (success)
    |        OR                          |
    |  <------- vcp-error -----------|   |  (failure)
    |                                    |
    |  ====== VCP session active ======  |
```

### 2.1 Implicit Negotiation (Legacy Clients)

```
  Client (v1.0)                       Server
    |                                    |
    |  (no vcp-hello within 5s)          |
    |                                    |
    |  Server assumes VCP 1.0,           |
    |  no extensions, core-only.         |
    |                                    |
    |  ====== VCP session active ======  |
```

---

## 3. Message Definitions

### 3.1 VCP-Hello (Client -> Server)

The client sends `vcp-hello` to declare its desired protocol version,
requested extensions, and optional identity.

```json
{
  "type": "vcp-hello",
  "version": "3.1",
  "extensions": ["VCP-X-Personal", "VCP-X-Relational"],
  "identity": "<VCP/I token or null>",
  "min_version": "1.0",
  "client_id": "creedspace-web/2.4.0"
}
```

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | REQUIRED | MUST be `"vcp-hello"`. |
| `version` | string | REQUIRED | The highest VCP version the client supports, as a semver major.minor string (e.g., `"3.1"`). |
| `extensions` | string[] | OPTIONAL | List of extension identifiers the client wishes to activate. Each MUST match the pattern `VCP-X-[A-Za-z][A-Za-z0-9-]*`. Defaults to `[]`. |
| `identity` | string or null | OPTIONAL | An opaque bearer credential identifying the client's subject. Its format, issuance, expiry, and revocation are defined by the transport or deployment, not by this specification; it is not a VCP/I UVC value token (`schemas/vcp-identity-token.schema.json` does not validate it). `null` indicates anonymous access. |
| `min_version` | string | OPTIONAL | The lowest VCP version the client can operate with. Defaults to `"1.0"`. |
| `client_id` | string | OPTIONAL | A human-readable client identifier for diagnostic purposes. MUST NOT be used for access control. |

**Validation Rules:**

- `version` MUST be a valid semver major.minor string. Patch versions are
  ignored in negotiation.
- `min_version` MUST be less than or equal to `version`.
- `extensions` entries that do not match the `VCP-X-*` naming pattern MUST be
  ignored by the server. The server SHOULD log a warning.
- `identity`, when present, MUST be validated by the deployment's
  credential verifier. Invalid credentials trigger a `vcp-error` with
  code `IDENTITY_INVALID`.

### 3.2 VCP-Ack (Server -> Client)

The server responds with `vcp-ack` to confirm the negotiated version,
declare which extensions are supported, and advertise capabilities.

```json
{
  "type": "vcp-ack",
  "version": "3.1",
  "supported": ["VCP-X-Personal"],
  "unsupported": ["VCP-X-Relational"],
  "capabilities": {
    "VCP-X-Personal": {
      "decay": true,
      "dimensions": [
        "cognitive_state",
        "emotional_tone",
        "energy_level",
        "perceived_urgency",
        "body_signals"
      ],
      "intensity_range": [1, 5],
      "lifecycle_states": ["SET", "ACTIVE", "DECAYING", "STALE", "EXPIRED"]
    }
  },
  "core_features": {
    "encryption": true,
    "injection_scanning": true,
    "revocation": true,
    "audit_chain": true,
    "context_opacity": true
  },
  "server_id": "creedspace-api/3.1.0",
  "session_id": "ses_a1b2c3d4"
}
```

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | REQUIRED | MUST be `"vcp-ack"`. |
| `version` | string | REQUIRED | The negotiated VCP version. MUST be >= client's `min_version` and <= client's `version`. |
| `supported` | string[] | REQUIRED | Extensions from the client's `extensions` list that the server supports and has activated. |
| `unsupported` | string[] | REQUIRED | Extensions from the client's `extensions` list that the server does not support. |
| `capabilities` | object | REQUIRED | Per-extension capability advertisements. Keys are extension identifiers from `supported`. Values are extension-defined capability objects. |
| `core_features` | object | REQUIRED | Server-wide core feature advertisements. See section 5. |
| `server_id` | string | OPTIONAL | A human-readable server identifier for diagnostics. |
| `session_id` | string | OPTIONAL | An opaque session identifier for correlating subsequent messages. |

**Invariants:**

- `supported` UNION `unsupported` MUST equal the valid identifiers from the
  client's `extensions` list after invalid identifiers are ignored (set
  equality, order independent). The two lists MUST be disjoint.
- Every key in `capabilities` MUST appear in `supported`.
- `capabilities` MUST NOT contain keys for unsupported extensions.

### 3.3 VCP-Error (Server -> Client)

The server sends `vcp-error` when the handshake cannot complete.

```json
{
  "type": "vcp-error",
  "code": "VERSION_UNSUPPORTED",
  "message": "Server requires VCP >= 2.0; client min_version 3.5 exceeds server max 3.1",
  "supported_versions": ["2.0", "3.0", "3.1"],
  "retry_after": null
}
```

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | REQUIRED | MUST be `"vcp-error"`. |
| `code` | string | REQUIRED | A machine-readable error code. See section 4. |
| `message` | string | REQUIRED | A human-readable error description. |
| `supported_versions` | string[] | OPTIONAL | The versions the server supports. MUST be present when `code` is `VERSION_UNSUPPORTED`. |
| `retry_after` | integer or null | OPTIONAL | Seconds the client SHOULD wait before retrying. `null` means no retry is expected. |

---

## 4. Error Codes

| Code | Meaning | Recovery |
|------|---------|----------|
| `VERSION_UNSUPPORTED` | No overlap between `[client.min_version, client.version]` and server's supported range. | Client MAY retry with a broader version range or a different server. |
| `IDENTITY_REQUIRED` | Server requires an identity credential but `identity` was `null`. | Client MUST re-send `vcp-hello` with a valid `identity`. |
| `IDENTITY_INVALID` | The provided identity credential failed validation (expired, malformed, revoked). | Client MUST obtain a fresh token and re-send `vcp-hello`. |
| `EXTENSION_CONFLICT` | Two or more requested extensions are mutually exclusive. | Client MUST remove one of the conflicting extensions and re-send `vcp-hello`. The `message` field MUST identify the conflicting pair. |
| `RATE_LIMITED` | Client has exceeded handshake rate limits. | Client MUST wait `retry_after` seconds before retrying. |
| `INTERNAL_ERROR` | Server encountered an unexpected error during negotiation. | Client MAY retry after a reasonable delay. |

### 4.1 Error Handling Requirements

- Servers MUST respond with exactly one `vcp-error` per failed handshake.
  Servers MUST NOT send both `vcp-ack` and `vcp-error`.
- Clients that receive `vcp-error` MUST NOT send VCP context data on the
  connection. The session is not established.
- Clients SHOULD implement exponential backoff for retries (initial delay
  1 second, max delay 30 seconds, jitter factor 0.5).

---

## 5. Core Feature Advertisement

The `core_features` object in `vcp-ack` declares which security and
verification features the server has active. All VCP 3.x servers MUST
advertise these fields. A value of `false` indicates the feature is not
available (e.g., development mode without encryption).

| Feature | Type | Description |
|---------|------|-------------|
| `encryption` | boolean | Context encryption at rest (Fernet symmetric). See `specs/core/security.md` SS1. |
| `injection_scanning` | boolean | Injection pattern detection (OWASP + VCP-specific). See `specs/core/security.md` SS2. |
| `revocation` | boolean | CRL + stapled proof infrastructure. See `specs/core/security.md` SS4. |
| `audit_chain` | boolean | Tamper-evident SHA-256 hash chain. See `specs/core/audit.md`. |
| `context_opacity` | boolean | Protection level abstraction layer. See `specs/core/security.md` SS3. |

### 5.1 Core Feature Constraints

- Servers in `production` or `staging` environments MUST set `encryption`
  to `true`. Servers that cannot provide encryption in production MUST
  refuse connections with `INTERNAL_ERROR`.
- Servers SHOULD set `injection_scanning` to `true` in all environments.
- Clients SHOULD warn users when `encryption` is `false`.
- Clients MUST NOT assume any core feature is active until confirmed by
  `vcp-ack`. A missing `core_features` object (from pre-3.1 servers)
  implies all features are `false`.

---

## 6. Version Negotiation

### 6.1 Algorithm

The server determines the negotiated version as follows:

```
let client_min = parse_semver(hello.min_version ?? "1.0")
let client_max = parse_semver(hello.version)
let server_versions = server.supported_versions  // sorted ascending

let candidates = server_versions.filter(v => v >= client_min AND v <= client_max)

if candidates is empty:
    return vcp-error(VERSION_UNSUPPORTED)

let negotiated = max(candidates)
return vcp-ack(version = negotiated)
```

### 6.2 Version Compatibility Matrix

| Client Version | Server Versions | Negotiated | Outcome |
|----------------|-----------------|-----------|---------|
| 3.1 (min 1.0) | [1.0, 2.0, 3.0, 3.1] | 3.1 | Full feature set |
| 3.1 (min 3.0) | [1.0, 2.0, 3.0, 3.1] | 3.1 | Full feature set |
| 3.1 (min 3.0) | [1.0, 2.0, 3.0] | 3.0 | Extensions unavailable |
| 2.0 (min 2.0) | [1.0, 2.0, 3.0, 3.1] | 2.0 | No extensions, no personal state |
| 3.5 (min 3.5) | [1.0, 2.0, 3.0, 3.1] | -- | VERSION_UNSUPPORTED |
| 1.0 (min 1.0) | [2.0, 3.0, 3.1] | -- | VERSION_UNSUPPORTED |

### 6.3 Version-Dependent Behavior

| Negotiated Version | Extensions | Personal State | Core Features |
|-------------------|------------|---------------|---------------|
| 1.0 | None | None | None (pre-security) |
| 2.0 | None | None | encryption, injection_scanning |
| 3.0 | Declared but not negotiated | Legacy float format | All core features |
| 3.1 | Full negotiation | Categorical + intensity | All core features |

---

## 7. Extension Negotiation

### 7.1 Extension Lifecycle

```
  Client requests         Server evaluates         Result
  +-----------------+     +-------------------+    +------------------+
  | VCP-X-Personal  | --> | Supported? Yes    | -> | supported[]      |
  | VCP-X-Relational| --> | Supported? No     | -> | unsupported[]    |
  | VCP-X-Consensus | --> | Supported? Yes    | -> | supported[]      |
  +-----------------+     +-------------------+    +------------------+
                                                     |
                                                     v
                                            capabilities{} populated
                                            for supported extensions
```

### 7.2 Extension Activation Rules

1. An extension is active for a session if and only if it appears in both
   the client's `extensions` list AND the server's `supported` response.
2. Servers MUST NOT activate extensions the client did not request.
3. Servers MUST NOT send extension-specific data for inactive extensions.
4. Clients MUST NOT send extension-specific data for extensions not
   confirmed in `supported`.
5. If the client sends no `extensions` list (or an empty list), no
   extensions are active regardless of server capability.

### 7.3 Extension Dependencies

Some extensions have dependencies:

| Extension | Requires | Behavior When Dependency Missing |
|-----------|----------|--------------------------------|
| VCP-X-Torch | VCP-X-Relational | Torch operates in degraded mode: session handoff works but relational context is empty. Server MUST include `"degraded": true` in VCP-X-Torch capabilities. |
| VCP-X-Intent | VCP-X-Personal | Intent inference operates without personal signal input. Confidence scores are lower. Server MUST include `"personal_signals": false` in VCP-X-Intent capabilities. |
| VCP-X-Consensus | (none) | Fully independent. |
| VCP-X-Personal | (none) | Fully independent. |
| VCP-X-Relational | (none) | Fully independent. |

### 7.4 Extension Conflict Rules

Servers MAY define mutually exclusive extension pairs. The current
specification defines no conflicts, but servers SHOULD use the
`EXTENSION_CONFLICT` error code if future conflicts arise.

### 7.5 Per-Extension Capability Objects

Each supported extension advertises its capabilities in the `capabilities`
map. The structure of each capability object is defined by the extension's
own specification. Enumerated values in capability advertisements use the
lowercase wire spelling of the extension's `schema.json`. Each capability
object MAY carry an optional `"status"` key (`"experimental"` | `"draft"` |
`"stable"`) mirroring the extension's registered lifecycle status; it is
informational and does not change negotiation. Below are summaries for the
five extensions referenced by the v3.1 baseline (VCP-X-Welfare is a v3.2
candidate and is tracked in `specs/extensions/README.md`):

**VCP-X-Personal:**
```json
{
  "decay": true,
  "dimensions": ["cognitive_state", "emotional_tone", "energy_level",
                  "perceived_urgency", "body_signals"],
  "intensity_range": [1, 5],
  "lifecycle_states": ["set", "active", "decaying", "stale", "expired"],
  "signal_sources": ["declared", "inferred", "inferred_local", "measured",
                     "elicitation", "preset", "decayed"]
}
```

**VCP-X-Relational:**
```json
{
  "trust_levels": ["initial", "developing", "established", "deep"],
  "standing_levels": ["none", "advisory", "collaborative", "bilateral"],
  "self_model_scaffolds": ["minimal", "standard", "interiora", "custom"],
  "norm_origins": ["human", "ai", "co_authored", "inherited"],
  "performance_bias_detection": true
}
```

**VCP-X-Consensus:**
```json
{
  "voting_method": "schulze",
  "deliberation_phases": ["draft", "deliberation", "convergence",
                          "ratification", "active"],
  "max_stakeholders": 100,
  "ai_standing": true,
  "self_referential_detection": true
}
```

**VCP-X-Torch:**
```json
{
  "degraded": false,
  "gestalt_tokens": true,
  "lineage_tracking": true,
  "max_lineage_depth": 1000
}
```

**VCP-X-Intent:**
```json
{
  "status": "experimental",
  "personal_signals": true,
  "categories": ["professional_inquiry", "urgent_task", "personal_exploration",
                  "emotional_processing", "health_check", "casual_conversation",
                  "crisis_support", "creative_work", "learning", "routine_check"],
  "max_alternatives": 3,
  "user_correction": true
}
```

---

## 8. Backward Compatibility

### 8.1 Legacy Client Support

Servers MUST support VCP 1.0 clients that do not send `vcp-hello`.

- If the server receives no `vcp-hello` within 5 seconds of connection
  establishment, it MUST assume the client is VCP 1.0.
- The server MUST proceed with version 1.0 semantics: no extensions,
  no personal state, no core feature advertisements.
- The 5-second timeout is measured from the transport-layer connection
  (TCP handshake complete, WebSocket upgrade complete, or MCP session
  established).
- Servers MAY use a shorter timeout in high-throughput environments but
  MUST NOT use a timeout shorter than 2 seconds.

### 8.2 Timeout Sequence

```
  Client (legacy)                     Server
    |                                    |
    |  -- TCP/WS/MCP connect -------->   |
    |                                    |  t=0: start 5s timer
    |  (client sends raw VCP data)       |
    |                                    |  t<5s: non-hello data received
    |                                    |  -> assume v1.0, cancel timer
    |  <------- baseline service ------- |
    |                                    |
```

### 8.3 Forward Compatibility

- Clients that receive a `vcp-ack` with unknown fields MUST ignore them.
- Clients that receive capability objects with unknown keys MUST ignore the
  unknown keys and use only recognized capabilities.
- Servers that receive a `vcp-hello` with unknown fields MUST ignore them.
- This allows incremental protocol evolution without breaking existing
  implementations.

---

## 9. MCP Integration

When VCP operates as a Model Context Protocol (MCP) server, the capability
negotiation piggybacks on MCP's `initialize` handshake.

### 9.1 Mapping

The `vcp-hello` payload is carried in MCP's `initializationOptions`:

```json
{
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "creedspace-web",
      "version": "2.4.0"
    },
    "initializationOptions": {
      "vcp": {
        "type": "vcp-hello",
        "version": "3.1",
        "extensions": ["VCP-X-Personal", "VCP-X-Relational"],
        "identity": null,
        "min_version": "1.0"
      }
    }
  }
}
```

The `vcp-ack` payload is returned in the MCP `initialize` response's
`serverInfo.metadata`:

```json
{
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": { "listChanged": true },
      "resources": { "listChanged": true }
    },
    "serverInfo": {
      "name": "creedspace-api",
      "version": "3.1.0",
      "metadata": {
        "vcp": {
          "type": "vcp-ack",
          "version": "3.1",
          "supported": ["VCP-X-Personal"],
          "unsupported": ["VCP-X-Relational"],
          "capabilities": {
            "VCP-X-Personal": { "decay": true }
          },
          "core_features": {
            "encryption": true,
            "injection_scanning": true,
            "revocation": true,
            "audit_chain": true,
            "context_opacity": true
          }
        }
      }
    }
  }
}
```

### 9.2 MCP-Specific Rules

- If MCP `initializationOptions` does not contain a `vcp` key, the server
  MUST assume VCP 1.0 (same as no `vcp-hello`).
- MCP `vcp-error` responses are embedded in the `initialize` response as
  `serverInfo.metadata.vcp` with `type: "vcp-error"`. The MCP response
  itself still succeeds (HTTP 200 / JSON-RPC success) -- the VCP error is
  at the application layer.
- MCP servers MUST still expose VCP tools (`vcp_validate_token`,
  `vcp_parse_csm1`, `vcp_encode_context`, `vcp_status`) regardless of
  negotiation outcome. Extension-specific tools (e.g., consensus voting)
  SHOULD only appear in `tools/list` when the corresponding extension is
  active.

### 9.3 MCP Resource Filtering

After negotiation, MCP resource URIs are filtered by active extensions:

| Resource URI | Required Extension |
|--------------|--------------------|
| `vcp://bundle/{session_id}` | (core -- always available) |
| `vcp://identity/{token_prefix}` | (core -- always available) |
| `vcp://constitution/{csm1_code}` | (core -- always available) |
| `vcp://capabilities` | (core -- always available) |
| `vcp://personal-state/{session_id}` | VCP-X-Personal |
| `vcp://relational/{session_id}` | VCP-X-Relational |
| `vcp://deliberation/{deliberation_id}` | VCP-X-Consensus |
| `vcp://torch/{session_id}` | VCP-X-Torch |
| `vcp://intent/{session_id}` | VCP-X-Intent |

Resources for inactive extensions MUST NOT appear in `resources/list`.
The authoritative URI list is `specs/core/mcp-bridge.md` §3; this table
mirrors it.

---

## 10. Security Considerations

### 10.1 Identity Validation

- Servers MUST validate the `identity` token before processing extensions.
  A valid identity is required before activating any extension that stores
  per-user state (VCP-X-Personal, VCP-X-Relational, VCP-X-Torch).
- Servers that require authentication MUST return `IDENTITY_REQUIRED` if
  `identity` is `null` and any state-bearing extension is requested.

### 10.2 Capability Downgrade Attacks

- Clients SHOULD cache the server's capabilities from the most recent
  successful `vcp-ack` and alert users if capabilities decrease
  unexpectedly (e.g., `encryption` changes from `true` to `false`).
- Servers MUST NOT downgrade core features mid-session. If a core feature
  becomes unavailable during a session (e.g., encryption key rotation
  failure), the server MUST terminate the session with an appropriate error.

### 10.3 Extension Probing

- The `unsupported` list in `vcp-ack` reveals which requested extensions a
  server does not implement. This is acceptable because extension support is
  not a secret. Conforming servers MUST emit both `supported` and `unsupported`
  so they form the required partition of valid requested extension identifiers.

### 10.4 Replay Protection

- `vcp-hello` messages are not independently replay-protected because they
  are bound to the transport session (TCP connection, WebSocket, MCP
  session). Transport-layer session binding provides replay protection.
- Servers MUST NOT accept a second `vcp-hello` on an already-negotiated
  session. Re-negotiation requires a new transport session.

---

## 11. Implementation Notes

### 11.1 Server Implementation Checklist

1. Parse `vcp-hello` from transport or MCP `initializationOptions`.
2. Validate `version` and `min_version` format.
3. Run version negotiation algorithm (section 6.1).
4. If `identity` is present, validate the credential with the deployment's verifier.
5. Evaluate each requested extension against the server's registry.
6. Check for extension conflicts.
7. Build `capabilities` map for supported extensions.
8. Build `core_features` map from server configuration.
9. Emit `vcp-ack` or `vcp-error`.
10. Start the 5-second timer on connection if no `vcp-hello` received.

### 11.2 Client Implementation Checklist

1. Send `vcp-hello` immediately after transport connection.
2. Wait for `vcp-ack` or `vcp-error`.
3. On `vcp-ack`: store negotiated version, active extensions, and
   capabilities. Filter subsequent operations to active extensions only.
4. On `vcp-error`: handle per error code (section 4). Display message to
   user if appropriate. Retry with backoff if applicable.
5. On timeout (no response within 10 seconds): treat as transport failure.

### 11.3 Extension Registry

Servers MUST maintain an extension registry that maps extension identifiers
to:

- A boolean indicating server-side support.
- A capability builder function that returns the capability object.
- A list of dependencies (other extension identifiers).
- A list of conflicts (other extension identifiers).

---

## 12. Wire Format

All handshake messages MUST be serialized as UTF-8 encoded JSON. The JSON
MUST be a single object (not an array). Servers MUST reject messages that
exceed 64 KiB after UTF-8 encoding.

The JSON Schema for all three message types is provided in
`schemas/vcp-capability-handshake.schema.json`.

---

## 13. Conformance

A VCP server is **Negotiation-Conformant** if it:

1. Responds to `vcp-hello` with `vcp-ack` or `vcp-error` within 5 seconds.
2. Correctly implements the version negotiation algorithm.
3. Filters invalid extension identifiers, then reports `supported` and
   `unsupported` as a disjoint partition of the valid requested identifiers.
4. Populates `capabilities` only for `supported` extensions.
5. Populates `core_features` accurately.
6. Assumes VCP 1.0 when no `vcp-hello` is received within the timeout.
7. Does not send extension-specific data for inactive extensions.

A VCP client is **Negotiation-Conformant** if it:

1. Sends `vcp-hello` before any VCP context data.
2. Respects the `supported` / `unsupported` partition.
3. Does not send data for extensions not in `supported`.
4. Handles `vcp-error` gracefully per section 4.
5. Ignores unknown fields in `vcp-ack`.

---

## Appendix A: Full Handshake Example

### A.1 Successful Negotiation

```
Client -> Server:
{
  "type": "vcp-hello",
  "version": "3.1",
  "extensions": ["VCP-X-Personal", "VCP-X-Relational", "VCP-X-Torch"],
  "identity": "<opaque bearer credential issued by the deployment>",
  "min_version": "3.0",
  "client_id": "creedspace-web/2.4.0"
}

Server -> Client:
{
  "type": "vcp-ack",
  "version": "3.1",
  "supported": ["VCP-X-Personal", "VCP-X-Torch"],
  "unsupported": ["VCP-X-Relational"],
  "capabilities": {
    "VCP-X-Personal": {
      "decay": true,
      "dimensions": ["cognitive_state", "emotional_tone", "energy_level",
                      "perceived_urgency", "body_signals"],
      "intensity_range": [1, 5],
      "lifecycle_states": ["set", "active", "decaying", "stale", "expired"],
      "signal_sources": ["declared", "inferred", "inferred_local", "measured",
                          "elicitation", "preset", "decayed"]
    },
    "VCP-X-Torch": {
      "degraded": true,
      "gestalt_tokens": true,
      "lineage_tracking": true,
      "max_lineage_depth": 1000
    }
  },
  "core_features": {
    "encryption": true,
    "injection_scanning": true,
    "revocation": true,
    "audit_chain": true,
    "context_opacity": true
  },
  "server_id": "creedspace-api/3.1.0",
  "session_id": "ses_x7y8z9"
}
```

Note: `VCP-X-Torch` reports `"degraded": true` because its dependency
`VCP-X-Relational` is unsupported by this server.

### A.2 Version Mismatch

```
Client -> Server:
{
  "type": "vcp-hello",
  "version": "4.0",
  "min_version": "4.0"
}

Server -> Client:
{
  "type": "vcp-error",
  "code": "VERSION_UNSUPPORTED",
  "message": "Server supports VCP 1.0-3.1; client requires >= 4.0",
  "supported_versions": ["1.0", "2.0", "3.0", "3.1"],
  "retry_after": null
}
```

### A.3 Identity Required

```
Client -> Server:
{
  "type": "vcp-hello",
  "version": "3.1",
  "extensions": ["VCP-X-Personal"],
  "identity": null
}

Server -> Client:
{
  "type": "vcp-error",
  "code": "IDENTITY_REQUIRED",
  "message": "VCP-X-Personal requires a valid identity credential",
  "retry_after": null
}
```

---

## Appendix B: Changelog

| Version | Date | Changes |
|---------|------|---------|
| 3.1.0 | 2026-02-28 | Initial specification. |
| 3.1.1 | 2026-09-02 | Editorial: `identity` clarified as an opaque deployment credential; core-feature references point at `security.md` SS1-SS4; MCP resource URIs aligned with `mcp-bridge.md` §3; capability enums use schema (lowercase) spelling and include `measured`/`elicitation`; optional per-extension `status` key. |
