# MCP Stateless Branch Reconciliation

| Field | Value |
|:---|:---|
| Source branch | `vcp/mcp-20260728-stateless` |
| Source commit | `da6e6c9` |
| Decision date | 2026-08-13 |
| Disposition | Proposal incorporated as Draft VEP-0005; runtime and broad document edits deferred |
| Release effect | None on VCP 3.1 or VCP 3.2 |

The branch combined a valuable MCP 2026-07-28 proposal with broad edits based on
an earlier repository state. Merging it wholesale would overwrite later schema,
documentation, security, and evidence work. The candidate therefore preserves
the proposal as VEP-0005, adds draft conformance fixtures in VCP-SDK, and defers
runtime migration until the VEP and the relevant MCP SDK interfaces are accepted.

This record resolves the branch before candidate freeze without claiming that a
single-project source decision constitutes governance acceptance.
