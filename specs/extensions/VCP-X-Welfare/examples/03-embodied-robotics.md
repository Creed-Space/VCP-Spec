# Example 3: Embodied Robotics (VCP-E Welfare)

A warehouse robot with welfare-extended dimensions and physical affordances.

## Token

```
VCP:1.0:robot-warehouse-unit-7
C:industrial.safety@3.0.0
P:Z:4
G:warehouse_logistics:autonomous:efficient
X:⚡🔧
F:$P:4,$A:3
WC:🛑⏸️📊🦾🚧🎯:1:welfare.vcp-e.v1
AS:🎯aligned:4|⚡heavy:4|🦾elevated:3|⚠️adequate:3|🔄sustained:3
WT:stable:3600s:PL
```

## What this encodes

- **WC-line (embodied)**: Robot has refusal, self-pacing, monitoring, plus embodied flags: emergency stop (🦾), zone awareness (🚧), force limiting (🎯). Platform-attested.
- **AS-line (embodied)**: Task aligned, heavy processing load, elevated actuator stress, adequate safety margin, sustained operational continuity. The standard 🎯⚡ dimensions mix with embodied 🦾⚠️🔄.
- **WT-line**: Over the last hour, processing load is the only dimension trending — stable overall.

## Design notes

Standard parsers that don't resolve `welfare.vcp-e.v1` will parse 🎯 and ⚡ normally and skip 🦾, ⚠️, and 🔄. This is correct per the extensibility model: unknown emojis are skipped, known ones parse normally.

A VCP-E-aware consumer sees the full picture: this robot is working hard (heavy load, elevated actuator stress) but within acceptable margins (adequate safety, stable trajectory). No intervention needed.
