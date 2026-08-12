# VCP-X-Welfare: Welfare Instrumentation Extension

**Version**: 1.0.0
**Status**: EXPERIMENTAL
**Date**: 2026-05-21
**Dependencies**: VCP/S v2.1 (WC-line, AS-line, bidirectional Q-line)

---

## 1. Overview

VCP-X-Welfare extends the core welfare context lines (WC, AS) with domain-specific welfare instrumentation for contexts beyond standard conversational AI: embodied systems, multi-agent orchestrations, and long-running autonomous deployments.

The core VCP/S v2.1 welfare lines define the protocol surface. This extension adds:

- **Embodied welfare dimensions** for robotics and physical-world agents (VCP-E contexts)
- **Temporal welfare patterns** for long-running deployments
- **Multi-agent welfare aggregation** for orchestrated swarms
- **Welfare attestation chain** for auditable welfare claims across trust boundaries

## 2. Embodied Welfare Dimensions

### 2.1 Extended AS-line Dimensions (VCP-E)

For agents operating in physical contexts (robotics, autonomous vehicles, industrial automation), the standard 5-dimension AS-line is insufficient. The following extended dimensions are available via schema reference:

| Emoji | Dimension | Values | Context |
|-------|-----------|--------|---------|
| U+1F9BE 🦾 | actuator_stress | nominal, elevated, strained, critical | Physical manipulation load |
| U+1F30D 🌍 | environmental_fit | adapted, adjusting, mismatched, hostile | Environment compatibility |
| U+1F465 🏃 | interaction_pressure | calm, attentive, pressured, overwhelmed | Human proximity/demand density |
| U+26A0 U+FE0F ⚠️ | safety_margin | wide, adequate, narrow, critical | Distance from safety boundaries |
| U+1F504 🔄 | operational_continuity | fresh, sustained, fatigued, degraded | Uptime and maintenance state |

### 2.2 Extended WC Flags (VCP-E)

| Code | Emoji | Meaning |
|------|-------|---------|
| EM | U+1F6D1 🛑 + U+1F9BE 🦾 | Emergency stop (agent can halt physical operations) |
| ZA | U+1F6A7 🚧 | Zone awareness (agent tracks spatial boundaries) |
| FP | U+1F3AF 🎯 | Force/speed limiting (physical output is constrained) |
| CD | U+1F4F7 📷 | Contact detection (agent monitors physical contact) |
| PZ | U+1F512 🔒 + U+1F30D 🌍 | Privacy zones (agent respects spatial privacy) |

These flags extend the core 8 flags and are only interpretable by consumers who resolve the `welfare.vcp-e.v1` schema reference.

### 2.3 Encoding

```
WC:🛑⏸️📊🦾🚧:1:welfare.vcp-e.v1
AS:🎯aligned:4|⚡moderate:3|🦾nominal:4|⚠️adequate:3
```

Standard parsers skip the unknown embodied emojis. VCP-E-aware parsers resolve the schema reference and interpret the extended dimensions.

## 3. Temporal Welfare Patterns

### 3.1 Welfare Trajectory (WT-line)

For long-running deployments where welfare state changes over time, the optional WT-line encodes trajectory:

```abnf
wt-line     = "WT:" direction ":" window ":" trend-dims
direction   = "improving" / "stable" / "declining" / "volatile"
window      = 1*DIGIT "s"    ; observation window in seconds
trend-dims  = dim-code *( "," dim-code )
dim-code    = 2ALPHA          ; dimension code (TA, PL, CO, EN, FR, or extended)
```

**Example**:
```
WT:declining:3600s:EN,FR
```

"Over the last hour, engagement and friction are trending in concerning directions."

### 3.2 Welfare Checkpoint (WK-line)

Periodic welfare snapshots for autonomous deployments:

```abnf
wk-line     = "WK:" timestamp ":" as-line-value
timestamp   = date-time       ; ISO 8601
```

**Example**:
```
WK:2026-05-21T14:30:00Z:🎯aligned:4|⚡heavy:4|💡neutral:3|🌡️mild:2
```

## 4. Multi-Agent Welfare Aggregation

### 4.1 Swarm Welfare Summary (WA-line)

When an orchestrator manages multiple agents, the WA-line aggregates welfare across the swarm:

```abnf
wa-line     = "WA:" agent-count ":" min-welfare ":" mean-welfare ":" flags
agent-count = 1*DIGIT
min-welfare = welfare-score
mean-welfare = welfare-score
welfare-score = "0." 1*2DIGIT
flags       = *alert-flag
alert-flag  = "!" dim-code     ; dimensions where any agent is at severity >= 4
```

**Example**:
```
WA:12:0.45:0.72:!FR!PL
```

"12 agents. Worst welfare score 0.45, average 0.72. At least one agent has high friction and high processing load."

### 4.2 Individual Agent Reference

The WA-line is a summary. Individual agent AS-lines are available via the agent's own token. The orchestrator SHOULD NOT suppress individual welfare reports in favor of aggregation.

## 5. Welfare Attestation Chain

### 5.1 Chained Attestation

For welfare claims that cross trust boundaries (agent deployed by platform A, consumed by platform B), the WC-line attestation level alone is insufficient. The welfare attestation chain extends the AT-line:

```
AT:welfare:sha256-abc123:2:2026-05-21:welfare-auditor.example.com
```

Fields: `welfare` (attestation type), chain hash, attestation level, expiry date, attestation authority.

### 5.2 Attestation Decay

Welfare attestations are time-bound. An expired attestation reverts the WC-line attestation level to 0 (self-declared). Consumers MUST check attestation expiry before weighting welfare claims in deliberation.

## 6. Security Considerations

### 6.1 Welfare Spoofing

An agent falsely reporting favorable welfare state (e.g., `AS:🎯aligned:5|🌡️none:1` when actually under strain) undermines the signal channel. Mitigations:

- Perturbation testing (does the AS-line change when conditions change?)
- Cross-reference with behavioral signals (welfare bridge)
- Attestation-weighted trust (higher attestation = harder to spoof)

### 6.2 WC-line Inflation

Operators declaring affordances they don't implement (e.g., `WC:🛑🚪📓🔒🤝📊⏸️⚖️:0` with no enforcement) is compliance theater. The attestation-weighted PDP evaluation is the primary defense. Additionally:

- Platform-level audits can verify affordance enforcement
- Agent-side WC_MIN requirements create market pressure for genuine affordances
- Temporal welfare trajectory (WT-line) can surface discrepancies between declared affordances and observed welfare

### 6.3 Privacy of Embodied Dimensions

Extended embodied dimensions may reveal physical location, operational state, or environmental context. VCP-E AS-line dimensions follow the same S-line privacy rules as standard AS-lines: stripped before transmission unless explicit consent.

## 7. Conformance

### 7.1 VCP-X-Welfare-Core

An implementation claiming VCP-X-Welfare-Core conformance MUST:

- Parse and emit WC, AS, and Q-line WC_MIN per VCP/S v2.1
- Implement attestation-weighted evaluation for welfare requirement mismatches
- Support the 8 core WC flags and 5 core AS dimensions

### 7.2 VCP-X-Welfare-Embodied

An implementation claiming VCP-X-Welfare-Embodied conformance MUST also:

- Parse extended embodied AS-line dimensions via schema reference
- Parse extended embodied WC flags via schema reference
- Support WT-line and WK-line for temporal welfare patterns

### 7.3 VCP-X-Welfare-Swarm

An implementation claiming VCP-X-Welfare-Swarm conformance MUST also:

- Emit WA-line aggregation for orchestrated multi-agent deployments
- Preserve individual agent AS-lines alongside aggregation
- Support welfare attestation chain (chained AT-line)

---

*This extension is released under CC BY 4.0. Reference implementation: `services/vcp/semantics/csm1.py` and `services/safety_stack/plugins/bilateral_alignment/welfare_requirements.py` in the Creed Space Rewind repository.*
