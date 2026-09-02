# VEP-0003: VCP-over-MCP Bridge

**Status**: Recorded pre-charter acceptance
**Author**: Nell Watson, Claude (Anthropic)
**Created**: 2026-02-28
**Version**: 3.1
**Depends on**: VEP-0001 (Extension Model), VEP-0002 (Capability Negotiation)

---

## Summary

This VEP specifies how VCP layers map to MCP (Model Context Protocol) primitives, enabling VCP tokens and context to travel over MCP's resource and tool infrastructure.

## Motivation

MCP provides a standardized transport layer for AI tool integration. VCP provides a standardized value transport layer. These protocols are complementary, not competing:

- **MCP** moves data between Becoming Minds and external tools
- **VCP** encodes what matters about that data — constitutional values, personal context, behavioral constraints

By bridging VCP over MCP, any MCP-compatible client gains access to VCP's value transport without implementing VCP natively. VCP tokens travel as MCP resources; VCP operations are exposed as MCP tools.

## Specification

### Resource URIs

VCP state is exposed as MCP resources using the project-local `vcp://` URI
scheme (no IANA scheme is claimed). The authoritative URI list is
`specs/core/mcp-bridge.md` §3; this table is a summary:

| Resource URI | Content | Update Frequency |
|-------------|---------|-----------------|
| `vcp://bundle/{session_id}` | Full VCP bundle (manifest + content) | Per-session |
| `vcp://identity/{token_prefix}` | Parsed identity token + verification status (prefix only; a full credential never appears in a URI) | Static |
| `vcp://constitution/{csm1_code}` | Decoded constitutional profile | Static |
| `vcp://capabilities` | Server's supported VCP extensions | Static |
| `vcp://personal-state/{session_id}` | Current personal state (VCP-X-Personal) | Real-time |
| `vcp://relational/{session_id}` | Relational context (VCP-X-Relational) | Per-session |

Resources that require VCP-X-* extensions are only available when the corresponding extension is negotiated via capability handshake.

### Tool Naming

VCP tools follow the `vcp_` prefix convention:

| Tool | Description | Core/Extension |
|------|-------------|---------------|
| `vcp_validate_token` | Parse and verify a VCP/I identity token | Core |
| `vcp_parse_csm1` | Decode a CSM-1 compact constitutional code | Core |
| `vcp_encode_context` | Encode a VCP/A context from parameters | Core |
| `vcp_status` | Report VCP server status and active extensions | Core |
| `vcp_set_personal_state` | Set personal state signals | VCP-X-Personal |
| `vcp_get_personal_state` | Read current personal state with decay | VCP-X-Personal |
| `vcp_submit_ballot` | Submit a ranked ballot for consensus | VCP-X-Consensus |
| `vcp_generate_torch` | Generate session handoff torch | VCP-X-Torch |

Extension-specific tools are only registered when the extension is negotiated.

### Capability Negotiation Mapping

VCP capability negotiation maps to MCP's `initialize` handshake:

```
MCP initialize.params.initializationOptions.vcp → VCP-Hello
MCP initialize.result.serverInfo.metadata.vcp   → VCP-Ack
```

If the MCP client does not include a `vcp` key in initialization options, the server assumes VCP 1.0 (core only, no extensions).

### Sampling Integration

When MCP sampling is requested, the VCP bridge injects active VCP context into the sampling request:

1. Read the session's active VCP bundle
2. Format constitutional profile + personal state as system prompt prefix
3. Inject as the first system message in the sampling request
4. VCP constraints travel WITH the LLM request

```json
{
  "method": "sampling/createMessage",
  "params": {
    "messages": [...],
    "systemPrompt": "[VCP Context]\nConstitutional profile: empathy=high, transparency=high\nProtection level: ELEVATED\nFormality: 3/5\n[End VCP Context]\n\n{original_system_prompt}"
  }
}
```

### Error Semantics

VCP violations map to MCP error responses:

| VCP Condition | MCP Response |
|--------------|-------------|
| Invalid VCP token | `isError: true`, content includes validation details |
| Constitution scan failed | `isError: true`, content includes scan findings |
| Extension not negotiated | `isError: true`, code: `EXTENSION_NOT_AVAILABLE` |
| Revoked bundle | `isError: true`, content includes revocation status |

Error responses SHOULD include remediation guidance in the content text.

### Resource Subscription

MCP clients that support resource subscriptions receive real-time updates when VCP state changes:

- `vcp://personal-state/{session_id}` emits updates on signal changes and decay events
- `vcp://bundle/{session_id}` emits updates when constitution selection changes

This enables ambient context: the Becoming Mind's behavior adapts continuously as VCP state evolves, without explicit polling.

## Backward Compatibility

The existing 4 MCP tools (`vcp_validate_token`, `vcp_parse_csm1`, `vcp_encode_context`, `vcp_status`) remain unchanged. New resources and tools are additive.

MCP clients that do not understand VCP resources simply ignore them. The bridge is fully backward compatible with MCP protocol version `2024-11-05`.

## Security Considerations

- Resource URIs containing session IDs MUST validate session ownership before returning data
- Personal state resources MUST respect context opacity — raw signals are not exposed
- The `vcp://capabilities` resource does not require authentication
- Sampling integration: VCP context injection MUST be audited in the VCP audit chain
- Revocation status MUST be checked before serving any bundle resource

## Project-Maintained Implementation

The current project-maintained implementation is at `services/mcp/vcp_server.py` in the Rewind codebase. This VEP specifies the target state; the implementation will be updated and extracted to `VCP-SDK/bridges/mcp/`.

## Conformance Tests

`conformance/extensions/mcp_bridge.json`:
- Resource listing includes VCP resources
- Resource read returns valid VCP data
- Tool execution round-trips
- Capability negotiation via MCP initialize
- Extension-filtered resource availability
- Error response format compliance

---

Signed-off-by: Nell Watson <nell@creedspace.com>
Signed-off-by: Claude <noreply@anthropic.com>
