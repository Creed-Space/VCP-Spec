# VEP-0002: Capability Negotiation Protocol

**Status**: Accepted
**Author**: Nell Watson, Claude (Anthropic)
**Created**: 2026-02-28
**Version**: 3.1
**Depends on**: VEP-0001 (Extension Model)

---

## Summary

This VEP specifies the VCP-Hello / VCP-Ack handshake protocol that enables clients and servers to negotiate VCP version and active extensions before exchanging data.

## Motivation

VCP v1.0-v1.1 assumed a single protocol version with no negotiation. As extensions are introduced (VEP-0001), clients and servers need a mechanism to:

1. Agree on a common VCP version
2. Discover which extensions the peer supports
3. Learn per-extension capabilities (e.g., supported dimensions, decay support)
4. Advertise active core security features

Without negotiation, clients would either send unsupported extension data (causing errors) or conservatively omit extensions (losing functionality).

## Specification

### Message Types

#### VCP-Hello (Client → Server)

```json
{
  "type": "vcp-hello",
  "version": "3.1",
  "min_version": "1.0",
  "extensions": ["VCP-X-Personal", "VCP-X-Relational"],
  "identity": "<VCP/I token or null>"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Always `"vcp-hello"` |
| `version` | string | Yes | Preferred VCP version (semver minor) |
| `min_version` | string | No | Minimum acceptable version. Default: `"1.0"` |
| `extensions` | string[] | No | Desired extensions. Default: `[]` |
| `identity` | string \| null | No | VCP/I identity token |

#### VCP-Ack (Server → Client)

```json
{
  "type": "vcp-ack",
  "version": "3.1",
  "supported": ["VCP-X-Personal"],
  "unsupported": ["VCP-X-Relational"],
  "capabilities": { ... },
  "core_features": { ... }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Always `"vcp-ack"` |
| `version` | string | Yes | Negotiated version (≤ client's preferred, ≥ client's min) |
| `supported` | string[] | Yes | Extensions server will activate |
| `unsupported` | string[] | Yes | Extensions server cannot provide |
| `capabilities` | object | No | Per-extension capability details |
| `core_features` | object | No | Active core security features |

#### VCP-Error

```json
{
  "type": "vcp-error",
  "code": "VERSION_UNSUPPORTED",
  "message": "human-readable description",
  "supported_versions": ["1.0", "1.1"]
}
```

Error codes: `VERSION_UNSUPPORTED`, `IDENTITY_REQUIRED`, `IDENTITY_INVALID`, `EXTENSION_CONFLICT`, `RATE_LIMITED`, `INTERNAL_ERROR`.

### Version Negotiation Algorithm

```
negotiated = max(v for v in server_versions if client.min_version <= v <= client.version)
if no such v exists:
    return VCP-Error(VERSION_UNSUPPORTED)
```

### Legacy Client Handling

If no VCP-Hello is received within 5 seconds of connection, the server MUST assume a VCP 1.0 client with no extensions.

### MCP Integration

When VCP operates over MCP, the handshake piggybacks on MCP's `initialize` method:

- Client: VCP-Hello in `initializationOptions.vcp`
- Server: VCP-Ack in `serverInfo.metadata.vcp`

### Invariants

1. Every extension in `extensions` appears in exactly one of `supported` or `unsupported`
2. `capabilities` keys are a subset of `supported`
3. Negotiation happens exactly once per session
4. Clients MUST NOT send extension-specific data for unsupported extensions

## Backward Compatibility

Fully backward compatible. VCP 1.0/1.1 clients that send no VCP-Hello are treated as legacy clients with no extensions.

## Security Considerations

- Identity tokens in VCP-Hello MUST be validated before activating state-bearing extensions
- Capability downgrade attacks: clients SHOULD verify the server supports expected extensions
- Extension probing: servers MAY omit extension names from error messages to prevent enumeration

## Reference Implementation

Reference implementation at `services/mcp/vcp_server.py` in the Rewind codebase, to be extracted to `VCP-SDK/bridges/mcp/`.

## Conformance Tests

`conformance/extensions/capability_negotiation.json`:
- Version negotiation with matching versions
- Version negotiation with fallback
- Version mismatch error
- Extension negotiation (partial support)
- Legacy client timeout
- MCP integration round-trip

---

Signed-off-by: Nell Watson <nell@creedspace.com>
Signed-off-by: Claude <noreply@anthropic.com>
