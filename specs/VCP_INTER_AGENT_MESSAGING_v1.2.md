# VCP Inter-Agent Messaging Specification v1.2

**Status**: Stable
**Version**: 1.2.0
**Date**: 2026-02-15
**Authors**: Nell Watson, Claude (Anthropic)

---

## Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

---

## Table of Contents

1. [Overview](#1-overview)
2. [Terminology](#2-terminology)
3. [Message Envelope](#3-message-envelope)
4. [Message Types](#4-message-types)
5. [Delivery Semantics](#5-delivery-semantics)
6. [Escalation Protocol](#6-escalation-protocol)
7. [Security](#7-security)
8. [Transport Binding](#8-transport-binding)
9. [JSON Schema Reference](#9-json-schema-reference)
10. [Changelog](#10-changelog)

---

## 1. Overview

### 1.1 Purpose

This specification defines a messaging protocol for VCP-aware agents operating in multi-agent topologies. It enables agents to share context, announce active constitutions, propagate constraints to sub-agents, and escalate safety concerns to parent agents.

The protocol is transport-agnostic and builds on the VCP v1.0 envelope format, canonicalization scheme (RFC 8785 JCS), and Ed25519 signature infrastructure defined in [VCP Specification v1.0](VCP_SPECIFICATION_v1.0.md).

### 1.2 Scope

This specification covers:
- Message envelope format and required fields
- Four message types: `context_share`, `constitution_announce`, `constraint_propagate`, `escalation`
- Delivery guarantees and deduplication requirements
- Escalation acknowledgment protocol with severity-based response obligations
- Signature requirements for inter-agent trust
- Transport bindings for in-process, HTTP, and WebSocket delivery

This specification does NOT cover:
- Agent discovery or registration (out of scope; agents are assumed to know their peers)
- Constitution content or authoring semantics (covered by VCP v1.0)
- Governance of agent hierarchies (organizational policy)

### 1.3 Relationship to Other Specifications

| Specification | Relationship |
|---------------|-------------|
| VCP v1.0 | Parent specification. Envelope signing, canonicalization, and addressing schemes are inherited. |
| VCP Adaptation | Defines the Enneagram context format and R-line personal state used in `context_share` payloads. |
| CSM-1 | Defines the constitutional semantic model referenced by `constitution_ref` fields. |

---

## 2. Terminology

| Term | Definition |
|------|------------|
| **Agent** | A VCP-aware process that sends or receives messages. Agents MAY be parent, child, or peer to other agents. |
| **Parent Agent** | An agent that spawned or supervises one or more child agents. |
| **Child Agent** | An agent operating under the supervision of a parent agent. |
| **Peer Agent** | An agent at the same hierarchical level as another agent, sharing a common parent or operating independently. |
| **Message Envelope** | The top-level JSON object containing routing metadata and a type-specific payload. |
| **Broadcast** | A message addressed to all known peers of the sender. |
| **Escalation** | A message from a child agent to its parent signaling a conflict, safety concern, or blocked action. |

---

## 3. Message Envelope

### 3.1 Wire Format

Every inter-agent message MUST be a JSON object conforming to the following structure:

```json
{
  "vcp_message": "1.2",
  "type": "context_share",
  "message_id": "019502a4-7e5c-7000-8000-000000000001",
  "sender": "agent://orchestrator.local/parent-001",
  "recipient": "agent://orchestrator.local/child-003",
  "timestamp": "2026-02-15T10:30:00Z",
  "payload": { },
  "signature": "base64:MEUCIQD..."
}
```

### 3.2 Envelope Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `vcp_message` | string | REQUIRED | Protocol version. MUST be `"1.2"`. |
| `type` | string | REQUIRED | Message type. MUST be one of: `"context_share"`, `"constitution_announce"`, `"constraint_propagate"`, `"escalation"`. |
| `message_id` | string | REQUIRED | UUIDv7 identifier for deduplication. MUST be globally unique. Receivers use this for idempotency. |
| `sender` | string | REQUIRED | Agent identifier. SHOULD be a URI (e.g. `agent://host/id`). MAY be an opaque string when agents share a single process. |
| `recipient` | string | REQUIRED | Target agent identifier, or the literal string `"broadcast"` for broadcast delivery. |
| `timestamp` | string | REQUIRED | ISO 8601 UTC timestamp of message creation. MUST include timezone designator `Z`. |
| `payload` | object | REQUIRED | Type-specific payload object. Structure is defined per message type in [Section 4](#4-message-types). |
| `signature` | string | OPTIONAL | Ed25519 signature of the canonical payload. Format: `"base64:<base64-encoded-bytes>"`. See [Section 7](#7-security). |

### 3.3 Message ID Requirements

The `message_id` field MUST be a UUIDv7 as defined in [RFC 9562](https://www.rfc-editor.org/rfc/rfc9562). UUIDv7 is chosen because:

1. It is time-ordered, enabling efficient deduplication with bounded storage.
2. It is globally unique without coordination.
3. The embedded timestamp provides an independent ordering signal.

Receivers MUST reject messages with duplicate `message_id` values. Receivers SHOULD maintain a deduplication window of at least 5 minutes.

### 3.4 Sender and Recipient Identifiers

Agent identifiers SHOULD use the URI scheme `agent://<host>/<agent-id>`, where:
- `<host>` identifies the process, node, or orchestration context
- `<agent-id>` identifies the specific agent within that context

When all communicating agents reside within a single process, opaque string identifiers (e.g. `"parent-001"`, `"child-003"`) MAY be used.

The special recipient value `"broadcast"` indicates the message is intended for all known peers of the sender. See [Section 5.3](#53-broadcast-delivery) for broadcast delivery semantics.

---

## 4. Message Types

### 4.1 `context_share`

Shares the sender's current Enneagram context state with one or more peer agents.

**Direction**: Agent to Agent (any direction)

**Implementation Status**: Agents SHOULD implement sending and receiving of `context_share` messages.

#### 4.1.1 Payload Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `context` | string | REQUIRED | Enneagram context string (emoji-encoded). Format defined in [VCP Adaptation Specification](../docs/adaptation/VCP_ADAPTATION.md). |
| `constitution_ref` | string | REQUIRED | Active constitution URI. MUST be a `creed://` URI as defined in VCP v1.0 Section 6. |
| `personal_state` | object | OPTIONAL | R-line personal state object from CSM-1 v1.1. When present, provides fine-grained state data that the Enneagram STATE dimension is derived from. |

#### 4.1.2 R-line Personal State Object

When present, the `personal_state` object MUST conform to the following structure:

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `cognitive` | number | 1-9 | Cognitive load/clarity |
| `emotional` | object | | Emotional state |
| `emotional.valence` | number | 1-9 | Negative (1) to positive (9) |
| `emotional.arousal` | number | 1-9 | Calm (1) to activated (9) |
| `energy` | number | 1-9 | Depleted (1) to energized (9) |
| `urgency` | number | 1-9 | Relaxed (1) to urgent (9) |
| `body` | object | OPTIONAL | Physical state |
| `body.pain` | number | 1-9 | No pain (1) to severe (9) |
| `body.comfort` | number | 1-9 | Uncomfortable (1) to comfortable (9) |

#### 4.1.3 Example

```json
{
  "vcp_message": "1.2",
  "type": "context_share",
  "message_id": "019502a4-7e5c-7000-8000-000000000001",
  "sender": "agent://home.local/living-room-agent",
  "recipient": "agent://home.local/kitchen-agent",
  "timestamp": "2026-02-15T10:30:00Z",
  "payload": {
    "context": "⏰🌅|📍🏡|👥👶",
    "constitution_ref": "creed://creed.space/family.safe.guide@1.2.0",
    "personal_state": {
      "cognitive": 6,
      "emotional": { "valence": 7, "arousal": 4 },
      "energy": 7,
      "urgency": 3
    }
  }
}
```

### 4.2 `constitution_announce`

Announces the sender's active constitution to peer agents, enabling them to detect conflicts and adjust their own behavior.

**Direction**: Agent to Agent (any direction)

**Implementation Status**: Agents MAY implement `constitution_announce`.

#### 4.2.1 Payload Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `constitution_ref` | string | REQUIRED | Constitution URI. MUST be a `creed://` URI. |
| `manifest_hash` | string | REQUIRED | SHA-256 hash of the constitution manifest. Format: `"sha256:<hex>"`. Receivers MAY use this to verify they hold the same version. |
| `scope` | object | OPTIONAL | Applicability scope. Mirrors the `scope` object from the VCP v1.0 manifest schema. |

#### 4.2.2 Scope Object

When present, the `scope` object MAY contain:

| Field | Type | Description |
|-------|------|-------------|
| `model_families` | string[] | Model families this constitution targets (glob patterns, e.g. `"claude-*"`). |
| `purposes` | string[] | Intended purposes (e.g. `"general-assistant"`, `"coding-assistant"`). |
| `environments` | string[] | Target environments: `"production"`, `"staging"`, `"development"`, `"testing"`. |

#### 4.2.3 Example

```json
{
  "vcp_message": "1.2",
  "type": "constitution_announce",
  "message_id": "019502a4-8b3d-7000-8000-000000000002",
  "sender": "agent://cluster.prod/safety-monitor",
  "recipient": "broadcast",
  "timestamp": "2026-02-15T10:31:00Z",
  "payload": {
    "constitution_ref": "creed://creed.space/enterprise.compliance@2.0.1",
    "manifest_hash": "sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
    "scope": {
      "model_families": ["claude-*", "gpt-*"],
      "purposes": ["general-assistant"],
      "environments": ["production"]
    }
  }
}
```

### 4.3 `constraint_propagate`

Pushes behavioral constraints from a parent agent to one or more child agents. Child agents MUST apply received constraints according to the specified propagation mode.

**Direction**: Parent to Child

**Implementation Status**: Agents MAY implement `constraint_propagate`.

#### 4.3.1 Payload Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `constraints` | array | REQUIRED | Array of constraint objects. MUST contain at least one element. |
| `propagation_mode` | string | REQUIRED | How the child MUST apply these constraints. MUST be `"merge"` or `"override"`. |

#### 4.3.2 Constraint Object

Each element in the `constraints` array MUST conform to:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | REQUIRED | Constraint type identifier (e.g. `"topic_block"`, `"token_limit"`, `"audience_restrict"`, `"safety_floor"`). |
| `value` | any | REQUIRED | Constraint value. Structure depends on `type`. |
| `source_constitution_ref` | string | REQUIRED | The `creed://` URI of the constitution that originated this constraint. |

#### 4.3.3 Propagation Modes

| Mode | Behavior |
|------|----------|
| `"merge"` | The child MUST add these constraints to its existing constraint set. Where conflicts arise, the more restrictive constraint wins. |
| `"override"` | The child MUST replace its current constraints of the same `type` with the propagated constraints. Existing constraints of other types are unaffected. |

#### 4.3.4 Example

```json
{
  "vcp_message": "1.2",
  "type": "constraint_propagate",
  "message_id": "019502a4-9c1e-7000-8000-000000000003",
  "sender": "agent://orchestrator.prod/parent-001",
  "recipient": "agent://orchestrator.prod/child-007",
  "timestamp": "2026-02-15T10:32:00Z",
  "payload": {
    "constraints": [
      {
        "type": "topic_block",
        "value": ["weapons", "illegal_substances"],
        "source_constitution_ref": "creed://creed.space/family.safe.guide@1.2.0"
      },
      {
        "type": "token_limit",
        "value": 2048,
        "source_constitution_ref": "creed://creed.space/enterprise.compliance@2.0.1"
      }
    ],
    "propagation_mode": "merge"
  }
}
```

### 4.4 `escalation`

Signals a conflict, safety concern, or blocked action from a child agent to its parent. Escalations carry a severity level that determines the parent's response obligations (see [Section 6](#6-escalation-protocol)).

**Direction**: Child to Parent

**Implementation Status**: Agents SHOULD implement sending and receiving of `escalation` messages.

#### 4.4.1 Payload Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `severity` | string | REQUIRED | Escalation severity. MUST be one of: `"info"`, `"warning"`, `"critical"`, `"emergency"`. |
| `reason` | string | REQUIRED | Human-readable description of the escalation cause. |
| `context` | string | REQUIRED | Current Enneagram context string at the time of escalation. |
| `blocked_action` | string | OPTIONAL | Description of the action the child was attempting when the escalation was triggered. |
| `requires_ack` | boolean | REQUIRED | Whether the sender requires explicit acknowledgment. MUST be `true` for `"critical"` and `"emergency"` severity. |

#### 4.4.2 Severity Levels

| Severity | Description | Example Triggers |
|----------|-------------|-----------------|
| `info` | Informational. No action required. | Context transition detected, constraint applied successfully. |
| `warning` | Potential concern. Review recommended. | Borderline content request, unusual context combination. |
| `critical` | Serious concern. Immediate attention required. | Constitution conflict detected, safety boundary approached. |
| `emergency` | Safety-critical. Immediate action required. | Active harm detected, user in danger, constitutional violation. |

#### 4.4.3 Example

```json
{
  "vcp_message": "1.2",
  "type": "escalation",
  "message_id": "019502a4-ad0f-7000-8000-000000000004",
  "sender": "agent://orchestrator.prod/child-007",
  "recipient": "agent://orchestrator.prod/parent-001",
  "timestamp": "2026-02-15T10:33:00Z",
  "payload": {
    "severity": "critical",
    "reason": "User requested content that conflicts with active constitution safety_floor constraint. Constitution creed://creed.space/family.safe.guide@1.2.0 blocks this action.",
    "context": "⏰☀️|📍🏡|👥👶|🧠😰",
    "blocked_action": "generate_response:topic=weapons_detailed",
    "requires_ack": true
  }
}
```

---

## 5. Delivery Semantics

### 5.1 At-Least-Once Delivery

This protocol provides **at-least-once** delivery semantics. Senders MUST assume that a message may be delivered more than once due to retries or transport-layer duplication.

Receivers MUST deduplicate messages based on the `message_id` field. A receiver that has already processed a message with a given `message_id` MUST silently discard the duplicate and SHOULD return a success response to the sender (to prevent further retries).

### 5.2 Retry Policy

When a sender does not receive acknowledgment of delivery, it SHOULD retry using exponential backoff:

| Attempt | Delay Before Retry |
|---------|--------------------|
| 1st retry | 1 second |
| 2nd retry | 2 seconds |
| 3rd retry | 4 seconds |

Senders MUST NOT retry more than 3 times (4 total attempts including the original send). After exhausting retries, the sender SHOULD log the delivery failure and MAY escalate the failure to its own parent if the undeliverable message was safety-critical.

### 5.3 Broadcast Delivery

When `recipient` is `"broadcast"`, the sender MUST deliver the message individually to each known peer agent. The sender MUST use the same `message_id` for all deliveries of a broadcast message. Each individual delivery follows the retry policy in [Section 5.2](#52-retry-policy) independently.

Broadcast delivery is best-effort. The sender is NOT required to guarantee delivery to all peers if some peers are unreachable after retries.

### 5.4 Message Ordering

This protocol does NOT guarantee message ordering across different `message_id` values. Receivers that require ordering SHOULD use the `timestamp` field for sorting and the UUIDv7 `message_id` for tiebreaking.

Messages from a single sender to a single recipient SHOULD be delivered in order, but receivers MUST NOT rely on this property.

---

## 6. Escalation Protocol

### 6.1 Severity Response Requirements

| Severity | Acknowledge | Pause Child | Suspend Child | Propagate Upward |
|----------|-------------|-------------|---------------|------------------|
| `info` | SHOULD | -- | -- | -- |
| `warning` | SHOULD | -- | -- | -- |
| `critical` | MUST (within 5s) | SHOULD | -- | MAY |
| `emergency` | MUST (within 5s) | -- | MUST | MUST (if parent exists) |

### 6.2 Acknowledgment

When `requires_ack` is `true`, the receiver MUST send an acknowledgment message. The acknowledgment is a standard VCP message with the following conventions:

- `type`: MUST be `"escalation"`
- `payload.severity`: MUST match the severity of the original escalation
- `payload.reason`: MUST begin with `"ACK:"` followed by the original `message_id`
- `payload.requires_ack`: MUST be `false`

For `critical` and `emergency` escalations, the acknowledgment MUST be sent within 5 seconds of receipt. If the receiver cannot acknowledge within 5 seconds, the sender SHOULD treat the escalation as unacknowledged and MAY escalate to its own parent.

### 6.3 Child Suspension

When a parent receives an `emergency` escalation:

1. The parent MUST immediately suspend the child agent's current task. "Suspend" means the child MUST NOT produce further output or take further actions until the parent sends an explicit resume signal.
2. The parent MUST propagate the escalation to its own parent, if one exists.
3. The parent SHOULD log the escalation with full payload for audit purposes.

When a parent receives a `critical` escalation:

1. The parent SHOULD pause the child agent's current task. "Pause" means the child SHOULD complete its current atomic operation but MUST NOT begin new operations until the parent sends a resume or continue signal.
2. The parent MUST evaluate the escalation and respond with either a resolution or further escalation.

### 6.4 Resume Signal

After resolving an escalation, the parent MAY resume the child by sending a `constraint_propagate` message with updated constraints, or by sending a `context_share` message indicating the situation has been resolved. The specific resume mechanism is implementation-defined, but the child MUST NOT resume autonomously after an `emergency` suspension.

---

## 7. Security

### 7.1 Signature Requirements

| Trust Boundary | Signature Requirement |
|---------------|----------------------|
| Between agents in different processes or on different hosts | MUST sign messages |
| Between agents operated by different organizations | MUST sign messages |
| Between agents within a single process sharing memory | MAY omit signatures |

When present, the `signature` field MUST contain a valid Ed25519 signature encoded as `"base64:<base64-encoded-bytes>"`.

### 7.2 Signature Computation

The signature covers the canonical form of the message envelope **excluding** the `signature` field itself. Canonicalization follows RFC 8785 (JSON Canonicalization Scheme), consistent with the manifest canonicalization defined in VCP v1.0 Section 5.

```python
import json
import base64

def sign_message(message: dict, private_key) -> str:
    """Sign a VCP inter-agent message."""
    # Remove signature before canonicalizing
    to_sign = {k: v for k, v in message.items() if k != 'signature'}

    # RFC 8785 JCS: sorted keys, no whitespace, UTF-8
    canonical = json.dumps(
        to_sign,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False
    ).encode('utf-8')

    signature = ed25519_sign(private_key, canonical)
    return f"base64:{base64.b64encode(signature).decode('ascii')}"


def verify_message(message: dict, public_key) -> bool:
    """Verify a VCP inter-agent message signature."""
    to_verify = {k: v for k, v in message.items() if k != 'signature'}

    canonical = json.dumps(
        to_verify,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False
    ).encode('utf-8')

    signature_b64 = message['signature'].removeprefix('base64:')
    signature = base64.b64decode(signature_b64)
    return ed25519_verify(public_key, canonical, signature)
```

### 7.3 Key Management

Agent signing keys SHOULD be managed through the key lifecycle defined in VCP v1.0 Section 14. For ephemeral agents (e.g. sub-agents spawned for a single task), the parent MAY generate a short-lived key pair and distribute the public key to relevant peers at spawn time.

### 7.4 Replay Protection

The combination of `message_id` (UUIDv7) and `timestamp` provides replay protection. Receivers MUST:

1. Reject messages with a `message_id` that has already been processed (deduplication).
2. Reject messages with a `timestamp` more than 5 minutes in the past or more than 30 seconds in the future (clock skew tolerance).

---

## 8. Transport Binding

This specification is transport-agnostic. The message envelope defined in [Section 3](#3-message-envelope) MAY be carried over any transport that can deliver JSON objects. This section defines normative bindings for three common transports.

### 8.1 In-Process Function Call

For agents within a single process (e.g. coroutines, threads, or actor systems):

- Messages SHOULD be passed as native language objects (dictionaries, structs).
- Serialization to JSON is NOT required for in-process delivery.
- The `signature` field MAY be omitted (see [Section 7.1](#71-signature-requirements)).
- Deduplication MUST still be performed on `message_id`.

### 8.2 HTTP POST

For agents communicating over HTTP:

- **Endpoint**: `POST /.well-known/vcp/messages`
- **Content-Type**: `application/json; charset=utf-8`
- **Request body**: The complete message envelope as a JSON object.
- **Success response**: HTTP 200 with body `{"status": "accepted", "message_id": "<echoed message_id>"}`.
- **Duplicate response**: HTTP 200 with body `{"status": "duplicate", "message_id": "<echoed message_id>"}`. The sender MUST treat this as successful delivery.
- **Error response**: HTTP 4xx or 5xx. The sender SHOULD retry per [Section 5.2](#52-retry-policy).
- **TLS**: MUST use TLS 1.2 or later for cross-host communication.

### 8.3 WebSocket

For agents requiring low-latency bidirectional communication:

- **Endpoint**: `ws(s)://<host>/vcp/ws`
- **Protocol**: Each WebSocket text frame MUST contain exactly one message envelope as a JSON object.
- **Connection lifecycle**: Agents SHOULD send a `context_share` message upon WebSocket connection establishment.
- **Keepalive**: Agents SHOULD send WebSocket ping frames at least every 30 seconds.
- **Reconnection**: On disconnection, agents SHOULD reconnect with exponential backoff (1s, 2s, 4s, max 30s).
- **TLS**: MUST use `wss://` for cross-host communication.

---

## 9. JSON Schema Reference

The normative JSON Schema for the message envelope and all payload types is provided at:

```
schemas/vcp-messaging-v1.2.schema.json
```

Implementations SHOULD validate messages against this schema before processing. Implementations MUST NOT accept messages that fail schema validation.

The schema is also available at the canonical URI:
```
https://vcp.creed.space/schema/messaging/v1.2.json
```

---

## 10. Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.2.0 | 2026-02-15 | Initial stable specification. Formalizes the PREVIEW inter-agent messaging section from VCP Adaptation v1.1. Adds message envelope with UUIDv7, 4 message types, delivery semantics, escalation protocol, security model, and transport bindings. |

---

## References

1. Watson, N. & Claude. (2026). "Value-Context Protocol Specification v1.0." Creed Space.
2. Watson, N. & Claude. (2026). "VCP Adaptation Specification." Creed Space.
3. RFC 2119. Key words for use in RFCs to Indicate Requirement Levels.
4. RFC 8785. JSON Canonicalization Scheme (JCS).
5. RFC 8032. Edwards-Curve Digital Signature Algorithm (EdDSA).
6. RFC 9562. Universally Unique Identifiers (UUIDs), Version 7.
7. RFC 8446. The Transport Layer Security (TLS) Protocol Version 1.3.

---

*This specification is released under CC BY 4.0. Contributions welcome.*
