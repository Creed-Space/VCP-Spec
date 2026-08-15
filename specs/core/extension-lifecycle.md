# VCP candidate extension lifecycle and collision policy

**Status:** Candidate process note. Governance authority has not ratified this
policy. It defines a safe default for source review without promoting any
extension.

## States

| State | Meaning | Compatibility expectation |
|:---|:---|:---|
| `proposed` | Identifier requested; design may change freely | No implementation claim |
| `experimental` | Bounded trials and fixtures exist | Explicit opt-in; breaking changes allowed with notice |
| `draft` | Design is reviewable and implementation candidates exist | Changes require migration notes |
| `stable` | Accepted in an authorized release | Wire and semantic compatibility protected |
| `deprecated` | Supported temporarily with replacement | No new use; warning and migration required |
| `withdrawn` | Rejected or abandoned before stability | Identifier remains reserved |
| `retired` | Stable extension support ended under policy | Historical resolution remains available |

Presence in a repository does not change state. Only an authorized, recorded
decision may promote, deprecate, withdraw, or retire an extension.

## Identifier allocation

1. The canonical key includes owner namespace, extension name, and major
   version.
2. Case-folded, Unicode-confusable, semantic, and abbreviation collisions are
   reviewed before allocation.
3. Allocated and withdrawn identifiers are never reused for unrelated meaning.
4. Private experiments use a private namespace and must not imply registry
   acceptance.
5. Each record names its schema, negotiation token, security and privacy owner,
   conformance profile, and status decision.

## Promotion evidence

Promotion requires a threat model, privacy analysis, complete examples,
negative fixtures, cross-language candidate behavior, migration analysis,
editorial review, and an explicit authority record. Stable promotion also
requires independent implementation or review evidence appropriate to the
risk. Same-programme parity alone is insufficient.

## Deprecation and removal

A deprecation record names the first warning version, replacement, migration
guide, support window, telemetry boundary, final compatible version, and target
removal decision. Security emergencies may shorten the window, but require a
public rationale and correction path. Unknown or retired required extensions
fail negotiation rather than disappearing silently.

## Errata

Errata use immutable identifiers and classify editorial, clarifying,
interoperability, security, privacy, or breaking impact. A correction never
rewrites a released artifact. It links the affected digest, corrected source,
implementation impact, conformance changes, and superseding release.

## Working signal

The policy is working when a new extension cannot appear in public
compatibility claims without a registry record, collision review, fixtures,
named status decision, and explicit negotiation behavior.
