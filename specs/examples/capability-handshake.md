# Wire Format Example: Capability Handshake

**VCP Version**: 3.1
**Purpose**: Demonstrates the full capability negotiation flow between a VCP client and server.

---

## Scenario

A therapy chatbot client connects to a VCP-enabled server. The client needs personal state tracking and relational context but does not use consensus voting.

---

## Step 1: Client Sends VCP-Hello

The client initiates the handshake with its desired extensions and identity token.

```json
{
  "type": "vcp-hello",
  "version": "3.1",
  "min_version": "1.0",
  "extensions": [
    "VCP-X-Personal",
    "VCP-X-Relational",
    "VCP-X-Torch"
  ],
  "identity": "vcp-i:creed:user:u_8f3k2m:ed25519:base64url_signature"
}
```

**Annotations**:
- `version`: The client's preferred VCP version
- `min_version`: The oldest version the client can fall back to
- `extensions`: Ordered by preference; server negotiates each independently
- `identity`: A VCP/I identity token for authentication; `null` if anonymous

---

## Step 2: Server Responds with VCP-Ack

The server supports Personal and Torch but not Relational.

```json
{
  "type": "vcp-ack",
  "version": "3.1",
  "supported": [
    "VCP-X-Personal",
    "VCP-X-Torch"
  ],
  "unsupported": [
    "VCP-X-Relational"
  ],
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
      "max_intensity": 5,
      "lifecycle_tracking": true
    },
    "VCP-X-Torch": {
      "lineage_depth": 100,
      "gestalt_tokens": true
    }
  },
  "core_features": {
    "encryption": true,
    "injection_scanning": true,
    "context_opacity": true,
    "revocation": true,
    "audit_chain": true
  }
}
```

**Annotations**:
- `supported`/`unsupported`: Definitive lists; every requested extension appears in exactly one
- `capabilities`: Per-extension capability details; clients use this to adapt behavior
- `core_features`: Server declares which core security features are active
- The session now operates with VCP-X-Personal + VCP-X-Torch active

---

## Step 3: Subsequent Context Exchange

With negotiation complete, the client sends a VCP context request including only the negotiated extensions:

```json
{
  "version": "3.1",
  "categorical": {
    "wire": "🧑‍⚕️:💬:🔒:🌙:🏠:👤:📱:🧘:🇬🇧"
  },
  "personal": {
    "signals": {
      "emotional_tone": {
        "category": "emotional_tone",
        "value": "tense",
        "intensity": 3,
        "source": "declared",
        "confidence": 0.9,
        "declared_at": "2026-02-28T21:30:00Z"
      },
      "energy_level": {
        "category": "energy_level",
        "value": "fatigued",
        "intensity": 4,
        "source": "declared",
        "confidence": 0.85,
        "declared_at": "2026-02-28T21:30:00Z"
      }
    }
  },
  "generation_preferences": {
    "depth": 4,
    "formality": 2,
    "directness": 3,
    "technical_level": 2
  }
}
```

The client omits `relational_context` because VCP-X-Relational was not negotiated.

---

## Error Case: Version Mismatch

If the server cannot satisfy the client's minimum version requirement:

```json
{
  "type": "vcp-error",
  "code": "VERSION_UNSUPPORTED",
  "message": "Server requires VCP >= 2.0; client min_version is 3.0",
  "supported_versions": ["1.0", "1.1"]
}
```

---

## Error Case: Identity Required

If the server requires authentication but the client sent `identity: null`:

```json
{
  "type": "vcp-error",
  "code": "IDENTITY_REQUIRED",
  "message": "This server requires a valid VCP/I identity token"
}
```

---

## MCP Bridge Integration

When VCP runs over MCP, the capability handshake piggybacks on MCP's `initialize` method:

```json
{
  "jsonrpc": "2.0",
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "therapy-chatbot",
      "version": "2.1.0"
    },
    "vcp": {
      "type": "vcp-hello",
      "version": "3.1",
      "extensions": ["VCP-X-Personal", "VCP-X-Torch"],
      "identity": null
    }
  }
}
```

The server includes VCP-Ack in its initialize response under a `vcp` key:

```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "resources": {},
      "tools": {}
    },
    "serverInfo": {
      "name": "creed-vcp-server",
      "version": "3.1.0"
    },
    "vcp": {
      "type": "vcp-ack",
      "version": "3.1",
      "supported": ["VCP-X-Personal", "VCP-X-Torch"],
      "unsupported": [],
      "capabilities": {
        "VCP-X-Personal": { "decay": true }
      },
      "core_features": {
        "encryption": true,
        "injection_scanning": true
      }
    }
  }
}
```

---

## Sequence Diagram

```
Client                          Server
  |                               |
  |  VCP-Hello                    |
  |  version: 3.1                |
  |  extensions: [Personal,      |
  |    Relational, Torch]        |
  |------------------------------>|
  |                               |
  |                  VCP-Ack      |
  |          supported: [Personal,|
  |                      Torch]  |
  |          unsupported:        |
  |            [Relational]      |
  |<------------------------------|
  |                               |
  |  Context Request              |
  |  (Personal + Torch only)     |
  |------------------------------>|
  |                               |
  |              Context Response |
  |<------------------------------|
  |                               |
```

---

## Key Invariants

1. Every extension listed in `extensions` appears in exactly one of `supported` or `unsupported`
2. `capabilities` keys are a subset of `supported`
3. If `min_version` > server's max version → VCP-Error
4. If no VCP-Hello received within 5 seconds → assume VCP 1.0 client (no extensions)
5. Clients MUST NOT send extension-specific data for unsupported extensions
