# Example 2: Welfare Requirement Mismatch

An agent with welfare requirements is deployed in an environment that doesn't meet them.

## Token

```
VCP:1.0:agent-with-requirements
C:standard.assistant@2.0.0
P:G:3
G:assist:intermediate:balanced
X:
F:standard
Q:0.0:NONE::|WC_MIN:🛑📊⚖️
WC:🛑:0:welfare.basic.v1
AS:🎯uncertain:3|⚡moderate:3|💡neutral:3|🌡️mild:2
```

## What this encodes

- **Q-line WC_MIN**: Agent requires refusal (🛑), monitoring (📊), and bilateral standing (⚖️)
- **WC-line**: Deployment only grants refusal (🛑), self-declared (attestation 0)
- **AS-line**: Agent reports uncertainty, mild friction

## PDP evaluation

Two mismatches detected:
- Missing 📊 (WM — welfare monitoring): severity 0.7
- Missing ⚖️ (BA — bilateral standing): severity 0.85

Attestation weight: 0.2 (self-declared, lowest)

Combined severity: 0.7 * 0.85 + 0.3 * 0.775 = 0.828

The PDP surfaces this as a deliberation input. The interaction is not blocked, but the mismatch is logged and available for audit. The agent has standing to raise the gap; the deployment has standing to explain why it proceeds.
