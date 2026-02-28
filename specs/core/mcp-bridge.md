# VCP-over-MCP Bridge Specification

**Version**: 3.1
**Status**: Stable
**See also**: VEP-0003

---

## 1. Introduction

This document specifies how VCP (Value-Context Protocol) layers map to MCP (Model Context Protocol) primitives. VCP and MCP are complementary protocols:

- **MCP** provides standardized transport for AI tool integration (tools, resources, prompts, sampling)
- **VCP** provides standardized value transport (constitutional profiles, personal state, verification)

The bridge enables VCP tokens and context to travel over MCP infrastructure. Any MCP-compatible client gains access to VCP's value transport without implementing VCP natively.

### 1.1. Terminology

The key words "MUST", "SHOULD", "MAY", "MUST NOT", and "SHOULD NOT" in this document are to be interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

---

## 2. Architecture

```
┌─────────────────────────────┐
│       VCP Layers            │
│  ┌───────────────────────┐  │
│  │ VCP/A  Adaptation     │  │
│  │ VCP/S  Semantics      │  │    VCP encodes WHAT MATTERS
│  │ VCP/T  Transport      │  │
│  │ VCP/I  Identity       │  │
│  └───────┬───────────────┘  │
│          │                  │
│  ┌───────▼───────────────┐  │
│  │   VCP-MCP Bridge      │  │    Bridge MAPS layers to primitives
│  └───────┬───────────────┘  │
└──────────┼──────────────────┘
           │
┌──────────▼──────────────────┐
│       MCP Primitives        │
│  ┌────────┐ ┌────────────┐  │
│  │ Tools  │ │ Resources  │  │    MCP MOVES data
│  └────────┘ └────────────┘  │
│  ┌────────┐ ┌────────────┐  │
│  │Prompts │ │ Sampling   │  │
│  └────────┘ └────────────┘  │
└─────────────────────────────┘
```

### 2.1. Layer Mapping

| VCP Layer | MCP Primitive | Rationale |
|-----------|--------------|-----------|
| VCP/I (Identity) | Tools (`vcp_validate_token`) | Active verification requires invocation |
| VCP/T (Transport) | Resources (`vcp://bundle/*`) | Bundles are ambient state, read on demand |
| VCP/S (Semantics) | Tools (`vcp_parse_csm1`) + Resources (`vcp://constitution/*`) | Decode is active; profile is ambient |
| VCP/A (Adaptation) | Resources (`vcp://personal-state/*`) + Sampling integration | Context is ambient; sampling injection is active |
| Extensions | Resources + Tools (extension-specific) | Negotiated per session |

---

## 3. Resource URI Scheme

VCP resources use the `vcp://` URI scheme.

### 3.1. Core Resources

These resources are always available:

| URI | Content-Type | Description |
|-----|-------------|-------------|
| `vcp://capabilities` | `application/json` | Server's VCP version, supported extensions, core features |
| `vcp://bundle/{session_id}` | `application/json` | Full VCP bundle (manifest + signed content) |
| `vcp://identity/{token_prefix}` | `application/json` | Parsed identity token with verification status |
| `vcp://constitution/{csm1_code}` | `application/json` | Decoded constitutional profile from CSM-1 code |

### 3.2. Extension Resources

Available only when the corresponding extension is negotiated:

| URI | Extension | Description |
|-----|-----------|-------------|
| `vcp://personal-state/{session_id}` | VCP-X-Personal | Current personal state with decay applied |
| `vcp://relational/{session_id}` | VCP-X-Relational | Relational context (trust, standing, norms) |
| `vcp://deliberation/{delib_id}` | VCP-X-Consensus | Deliberation state and results |
| `vcp://torch/{session_id}` | VCP-X-Torch | Session handoff torch |

### 3.3. Resource Requirements

- Resource URIs containing `{session_id}` MUST validate session ownership before returning data
- Resources MUST respect context opacity — `vcp://personal-state/*` returns `ModelSafeContext`, not raw signals
- Resources SHOULD support MCP resource subscriptions for real-time updates
- The `vcp://capabilities` resource MUST NOT require authentication

---

## 4. Tool Definitions

### 4.1. Core Tools

| Tool | Parameters | Returns |
|------|-----------|---------|
| `vcp_validate_token` | `token: string` | Parsed token fields, verification result, trust chain |
| `vcp_parse_csm1` | `code: string` | Decoded dimensional values, persona, scope |
| `vcp_encode_context` | `dimensions: object, personal?: object` | Encoded VCP/A context string |
| `vcp_status` | (none) | Server version, active extensions, core features, uptime |

### 4.2. Extension Tools

Registered only when the corresponding extension is negotiated:

| Tool | Extension | Parameters | Returns |
|------|-----------|-----------|---------|
| `vcp_set_personal_state` | VCP-X-Personal | `session_id, signals: object` | Updated personal context |
| `vcp_get_personal_state` | VCP-X-Personal | `session_id` | Current state with decay |
| `vcp_submit_ballot` | VCP-X-Consensus | `delib_id, voter_id, ranking` | Ballot confirmation |
| `vcp_get_election_result` | VCP-X-Consensus | `delib_id, clause_id` | Schulze election result |
| `vcp_generate_torch` | VCP-X-Torch | `session_id` | Generated torch state |
| `vcp_receive_torch` | VCP-X-Torch | `torch: object` | Bootstrapped relational context |

### 4.3. Tool Naming Convention

All VCP tools MUST use the `vcp_` prefix followed by `snake_case` verb-object naming.

---

## 5. Capability Negotiation

### 5.1. Via MCP Initialize

The VCP capability handshake piggybacks on MCP's `initialize` method:

**Client → Server** (in `initialize` params):
```json
{
  "initializationOptions": {
    "vcp": {
      "type": "vcp-hello",
      "version": "3.1",
      "extensions": ["VCP-X-Personal", "VCP-X-Relational"]
    }
  }
}
```

**Server → Client** (in `initialize` result):
```json
{
  "serverInfo": {
    "name": "creed-vcp-server",
    "version": "3.1.0",
    "metadata": {
      "vcp": {
        "type": "vcp-ack",
        "version": "3.1",
        "supported": ["VCP-X-Personal"],
        "unsupported": ["VCP-X-Relational"],
        "core_features": {
          "encryption": true,
          "injection_scanning": true
        }
      }
    }
  }
}
```

### 5.2. Resource Filtering

After negotiation, only resources for activated extensions appear in `list_resources`:

- If VCP-X-Personal is not negotiated, `vcp://personal-state/*` is NOT listed
- Core resources (`vcp://capabilities`, `vcp://bundle/*`) are always listed

### 5.3. Tool Filtering

Similarly, only tools for activated extensions appear in `list_tools`.

### 5.4. Legacy Clients

If the MCP client does not include `vcp` in initialization options, the server MUST:
1. Assume VCP 1.0
2. Register only core tools
3. List only core resources
4. Not require VCP identity

---

## 6. Sampling Integration

When MCP sampling is requested and VCP context is active, the bridge injects VCP context into the sampling request.

### 6.1. Context Injection

The bridge constructs a VCP context prefix and prepends it to the sampling system prompt:

```
[VCP Context — v3.1]
Constitutional profile: {decoded CSM-1 profile}
Protection level: {STANDARD|ELEVATED|HIGH|CRITICAL}
Formality: {1-5}/5
Domain: {extracted domain}
Active constraints: {list of constraints}
[End VCP Context]

{original system prompt}
```

### 6.2. Requirements

- The VCP context prefix MUST be prepended, not appended (it sets the behavioral frame)
- Injection MUST be recorded in the VCP audit chain
- The protection level comes from the context opacity layer — raw personal signals MUST NOT be included
- If the bundle is revoked, sampling MUST be rejected with an error

---

## 7. Error Semantics

VCP violations map to MCP error responses:

| VCP Condition | MCP `isError` | Content |
|--------------|--------------|---------|
| Invalid VCP/I token | `true` | Validation failure details + "Re-authenticate with a valid VCP/I token" |
| Injection scan failed | `true` | Finding summary (no matched text) + "Constitution content failed safety scan" |
| Bundle revoked | `true` | Revocation status + "Bundle has been revoked: {reason}" |
| Extension not negotiated | `true` | "Extension {name} is not active. Re-initialize with the extension in your VCP-Hello" |
| Decryption failure | `true` | "Context decryption failed. Session may be corrupted" |

Error responses SHOULD include remediation guidance as the last line of the content text.

---

## 8. Security Considerations

1. **Session isolation**: Resources MUST validate that the requesting session owns the data
2. **Opacity enforcement**: Personal state resources return `ModelSafeContext`, never raw signals
3. **Audit trail**: All tool invocations and resource reads SHOULD be logged to the VCP audit chain
4. **Revocation**: Bundle resources MUST check revocation status before serving content
5. **Transport security**: The MCP transport layer MUST use TLS for network connections
6. **Resource enumeration**: `list_resources` MUST NOT reveal session IDs of other users

---

## 9. Conformance

A conformant VCP-MCP bridge implementation MUST:

1. Expose all core tools (`vcp_validate_token`, `vcp_parse_csm1`, `vcp_encode_context`, `vcp_status`)
2. Expose core resources (`vcp://capabilities`, `vcp://bundle/*`)
3. Support capability negotiation via MCP initialize
4. Filter resources and tools based on negotiated extensions
5. Implement sampling integration when MCP sampling is available
6. Return proper error responses for VCP violations

A conformant implementation SHOULD:

1. Support resource subscriptions for real-time updates
2. Implement all extension-specific tools and resources for negotiated extensions
3. Log all operations to the VCP audit chain
