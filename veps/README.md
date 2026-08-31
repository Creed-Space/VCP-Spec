# VCP Enhancement Proposals

<!-- vcp-document-control
status: Current VEP tracker
normative-authority: Canonical interim VEP intake and status index
protocol-version: VCP 3.1 with separately recorded proposals
last-reviewed: 2026-08-14 active authority and evidence boundary
owner: VCP Spec maintainers
evidence-boundary: Proposal numbering and status tracking, not proposal ratification
-->

| VEP | Title | Status | Target |
|:---|:---|:---|:---|
| [0001](./VEP-0001-extension-model.md) | Extension Model Architecture | Recorded pre-charter acceptance | v3.1 |
| [0002](./VEP-0002-capability-negotiation.md) | Capability Negotiation Protocol | Recorded pre-charter acceptance | v3.1 |
| [0003](./VEP-0003-mcp-bridge.md) | VCP-over-MCP Bridge | Recorded pre-charter acceptance | v3.1 |
| [0004](./VEP-0004-extended-vcpa-dimensions.md) | Extended VCP/A Dimensions | Experimental | v3.2 pre-release |
| [0005](./VEP-0005-stateless-mcp.md) | Stateless MCP Adaptation | Draft | v3.3 candidate |
| [0006](./VEP-0006-agent-runtime-profile.md) | Agent Runtime Profile | Draft | separate 0.1 candidate |

The interim lifecycle and authority boundaries are defined in
[`GOVERNANCE.md`](../GOVERNANCE.md). The first three labels preserve historical
source-baseline decisions, but no evidence establishes the constituted TSC vote
formerly claimed by the repository. Repository presence does not itself confer
ratification or release status.

VEP-0005 reconciles the proposal from branch
`vcp/mcp-20260728-stateless`. Its runtime changes are explicitly deferred until
the VEP is accepted and the MCP SDK v2 migration is independently reviewed.
