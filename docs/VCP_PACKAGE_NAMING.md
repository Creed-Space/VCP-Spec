# VCP Package Naming Convention

**Status**: Decision Record (pending final confirmation before publishing)
**Date**: 2026-02-15
**Principle**: Mirror MCP's naming exactly, substituting `value` for `model`.

## Naming Table

| Registry | MCP (reference) | VCP (ours) |
|----------|----------------|------------|
| **PyPI** | `mcp` | `vcp` |
| **npm (SDK)** | `@modelcontextprotocol/sdk` | `@valuecontextprotocol/sdk` |
| **npm (servers)** | `@modelcontextprotocol/server-*` | `@valuecontextprotocol/server-*` |
| **crates.io** | `rmcp` | `rvcp` |
| **GitHub org** | `modelcontextprotocol` | `valuecontextprotocol` |

## Rationale

1. **Standards equivalence** — VCP and MCP are complementary protocols at the same architectural level. Parallel naming signals this.
2. **Foundation-ready** — MCP was donated to the Agentic AI Foundation (Linux Foundation). Using the full `valuecontextprotocol` org name ensures clean handoff if/when VCP follows the same path.
3. **Namespace room** — The `@valuecontextprotocol/` npm scope accommodates ecosystem growth: `server-creedspace`, `inspector`, `ext-*`, etc.
4. **Discoverability** — Developers familiar with MCP's naming will intuitively find VCP packages.

## Package Contents (Planned)

| Package | Contents |
|---------|----------|
| `vcp` (PyPI) | Python SDK: identity, transport, semantics, adaptation, MCP server, FastAPI router |
| `@valuecontextprotocol/sdk` (npm) | TypeScript SDK: WebMCP tools, browser polyfill |
| `rvcp` (crates.io) | Rust SDK: `vcp-core` (identity, semantics, adaptation), transport, `no_std` support |

## Not Yet Decided

- Exact version to publish (waiting for Rust transport completion)
- Whether to create the `valuecontextprotocol` GitHub org now or at donation time
- Sub-crate naming for Rust (`rvcp-core`, `rvcp-wasm`, `rvcp-cli` vs monolithic `rvcp`)
