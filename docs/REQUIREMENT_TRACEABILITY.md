# VCP requirement traceability status

<!-- vcp-document-control
status: Current candidate traceability report
normative-authority: None
protocol-version: VCP 3.1 source baseline with candidate operations profile
last-reviewed: 2026-08-15
owner: VCP-Spec and VCP-SDK maintainers
evidence-boundary: Generated coverage and gaps, not a complete normative registry or conformance claim
-->

The generated
[`candidate-requirements.json`](../registries/candidate-requirements.json)
records every stable `VCP-OP-*` requirement in the candidate operations
profile, its actor, precondition, testability, failure semantics, source anchor,
and current evidence mapping. It also inventories legacy uppercase normative
statements that do not yet have durable identifiers.

An empty evidence list is an uncovered requirement. A detected legacy statement
is an open identification gap. Neither is counted as a pass, and the current
registry does not claim complete VCP 3.1 normative coverage.

## Maintenance workflow

1. Add or change requirements in the controlling specification source.
2. Preserve an existing identifier unless the semantic requirement is replaced.
3. Add positive, negative, unsupported, or human-review evidence references.
4. Regenerate the registry and update the SDK conformance mapping.
5. Reject duplicate identifiers, missing sources, stale digests, vanished
   evidence, or a decrease in identified coverage without an explicit
   deprecation record.

## Current closure boundary

The candidate operations profile has stable identifiers. The broader VCP 3.1
source and core companions still contain unassigned normative statements, and
the operations requirements have not yet been mapped to case-level conformance
evidence. Those gaps remain open until human editorial classification and
cross-repository test mapping are complete.

## Working signal

The report improves when stable identified coverage and mapped evidence rise,
while each remaining gap stays visible by source digest. It fails when prose,
registry, or test evidence drifts silently.
