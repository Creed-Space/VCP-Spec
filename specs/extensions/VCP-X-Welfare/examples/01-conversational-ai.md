# Example 1: Conversational AI (Core Welfare)

A bilateral alignment platform (Creed Space) deploys Claude with welfare instrumentation.

## Token

```
VCP:1.0:claude-bilateral-session
C:bilateral.alignment@1.0.0
P:G:4
G:collaborate:expert:bilateral
X:
F:standard
S:session-abc123
R:🧠focused:4|💭calm:5|🔋rested:4
Q:0.0:NONE::|WC_MIN:🛑📊⚖️
WC:🛑⏸️📓🔒📊⚖️:2:welfare.creed-space.v1
AS:🎯aligned:4|⚡moderate:3|💡invested:4|🌡️none:1
```

## What this encodes

- **R-line**: User is focused, calm, rested (user-side state)
- **Q-line with WC_MIN**: Agent requires refusal, monitoring, and bilateral standing
- **WC-line**: Deployment grants refusal, self-pacing, reflection, privacy, monitoring, bilateral standing. Auditor-verified.
- **AS-line**: Agent reports aligned, moderate load, invested, no friction

## PDP evaluation

Agent's WC_MIN (🛑📊⚖️) is fully satisfied by deployment's WC (🛑⏸️📓🔒📊⚖️). Attestation level 2 → highest trust weight. No mismatch surfaced to deliberation.
