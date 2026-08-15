# VCP verification status-code registry

**Status:** Candidate registry derived from the VCP-SDK 4.2.0 implementation.
It is not normative until accepted by authorized VCP release governance.

The machine-readable registry is
[`../../registries/verification-status-codes.json`](../../registries/verification-status-codes.json).
Its schema is
[`../../schemas/vcp-verification-status-registry.schema.json`](../../schemas/vcp-verification-status-registry.schema.json).

## Stability rules

1. A numeric code and wire label must never be reused for a different meaning.
2. Existing meanings may be clarified without widening authority or changing
   retry behavior. Any other change requires a new code.
3. Unknown codes fail closed. A consumer may preserve the raw value for
   diagnostics, but must not map it to `VALID`.
4. Retryability is guidance for orchestration. It never converts failure into
   authorization and does not override a caller's deadline or retry budget.
5. Security and privacy logs record the code, candidate identity, and safe
   correlation identifier. They do not record payloads, keys, personal state,
   or provider error bodies by default.
6. Registry additions require cross-language fixtures and a compatibility
   review. Removal is prohibited; superseded codes remain reserved.

## Categories

`success` represents verified acceptance. `security` represents integrity,
replay, revocation, or other adversarial failure. `temporal` represents declared
time validity. `transient` represents unavailable supporting evidence.
`configuration` represents policy, trust, schema, scope, or budget mismatch.

The category is a stable coarse class, not a substitute for the exact code.
Applications must use the exact code when choosing user messages, retries,
alerts, or remediation.
