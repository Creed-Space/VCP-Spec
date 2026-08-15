# VCP candidate protocol operations profile

**Status:** Candidate design note. This document is non-normative until an
authorized VCP release incorporates it. Requirement identifiers are stable
within this candidate and may be cited by tests.

This profile closes ambiguity around negotiation, downgrade behavior,
revocation freshness, scope attenuation, delegation, state transitions, media
types, URI use, and namespace ownership. It narrows behavior without claiming
that any media type, URI scheme, or namespace has been registered externally.

## 1. Requirement identifier policy

Identifiers have the form `VCP-OP-{AREA}-{NUMBER}`. Once published in a VCP
source candidate, an identifier is never reused for a different requirement.
If a requirement changes incompatibly, the old identifier remains reserved and
a new identifier is allocated. Tests report both the identifier and exact
candidate digest.

## 2. Version negotiation and downgrade resistance

### VCP-OP-NEG-001: explicit offers

Each peer offers an ordered set of exact protocol and extension versions. An
omitted offer means unsupported. A version range may be used only when both
range grammar and prerelease handling are negotiated.

### VCP-OP-NEG-002: deterministic selection

The selected version is the highest mutually supported stable version within
the caller's policy. Experimental versions are excluded unless both peers opt
in to the named experiment. Selection is deterministic over the same offers.

### VCP-OP-NEG-003: no silent fallback

Failure to find a mutually supported version returns an explicit negotiation
error. A peer must not reinterpret an unknown major as an older major, omit an
unrecognized required extension, or proceed with local defaults.

### VCP-OP-NEG-004: bind offers to the session

Authenticated transports bind both original offers, the selected versions,
required extensions, and a nonce or session identifier to the protected
transcript. If the transport cannot protect that transcript, the application
must label downgrade resistance unavailable and apply its fail-closed policy.

### VCP-OP-NEG-005: capability loss

If a previously selected required capability disappears, the session returns
to negotiation. Cached success does not authorize continued use after expiry,
revocation, reconnect, trust-anchor change, or material policy change.

## 3. Revocation and freshness

### VCP-OP-REV-001: authoritative binding

A status response is usable only when it is authenticated under configured
trust, identifies the queried issuer and object identifier, and is valid for
the selected revocation profile. A response for another object is rejected.

### VCP-OP-REV-002: bounded freshness

Status evidence carries `this_update` and either `next_update` or a profile
maximum age. The verifier evaluates those claims against an explicit clock and
bounded skew. Missing, future, expired, or unparseable freshness evidence is
unavailable evidence, not a clean status.

### VCP-OP-REV-003: fail closed when required

When current revocation evidence is required, network failure, timeout,
redirect-policy rejection, malformed response, stale cache entry, or unknown
status returns `REVOCATION_UNAVAILABLE`. None of those conditions means
`not_revoked`.

### VCP-OP-REV-004: cache partitioning

Cache keys include issuer, object identifier, status authority, verification
profile, and trust configuration identity. Negative results are not shared
across those boundaries. Cache lifetime never exceeds authoritative freshness.

### VCP-OP-REV-005: confirmed revocation

A confirmed revocation response includes a non-empty reason and a
timezone-qualified `revoked_at`. Verification returns `REVOKED`. Retry does not
restore authority unless newer authenticated evidence explicitly supersedes the
revocation under an authorized correction policy.

## 4. Scope, audience, delegation, and attenuation

### VCP-OP-SCP-001: intersection only

Effective authority is the intersection of issuer grant, subject scope,
audience, selected protocol profile, application policy, time validity, and all
delegation constraints. Composition never forms a union of grants.

### VCP-OP-SCP-002: explicit audience

An audience-bound object is accepted only by a matching audience identifier.
Wildcard audiences require an explicit profile and must not be inferred from a
missing field.

### VCP-OP-SCP-003: monotonic delegation

Each delegation step may reduce scope, audience, duration, action set, budget,
or redelegation depth. It must not expand any parent grant. The verifier checks
the complete chain before use.

### VCP-OP-SCP-004: bounded depth and cycles

Delegation chains have a profile-defined maximum depth and unique identifiers.
Repeated identifiers, cycles, missing parents, or ambiguous parent selection
fail closed.

### VCP-OP-SCP-005: purpose and context separation

A grant for context receipt does not imply permission to persist, disclose,
train on, infer sensitive attributes from, execute tools from, transact on, or
redelegate that context. Those authorities are separately represented.

## 5. State machines

### 5.1 Verification object

| State | Entry | Permitted transition |
|:---|:---|:---|
| `received` | Bounded bytes accepted | `parsed`, `rejected` |
| `parsed` | Syntax and schema accepted | `integrity_checked`, `rejected` |
| `integrity_checked` | Hash and signature checks complete | `trust_checked`, `rejected` |
| `trust_checked` | Issuer, audience, and scope accepted | `freshness_checked`, `rejected` |
| `freshness_checked` | Time and required revocation checks complete | `authorized`, `rejected` |
| `authorized` | Exact operation may proceed | `consumed`, `revoked`, `expired` |
| `consumed` | One-shot or replay-bound authority used | terminal |
| `rejected` | Stable failure code recorded | terminal for this attempt |
| `revoked` | New authoritative status invalidates use | terminal |
| `expired` | Validity or evidence lifetime ended | terminal |

### VCP-OP-STM-001: no skipped gates

An implementation must not enter `authorized` without completing every gate
required by the selected profile. Parallel checks are allowed, but successful
completion is equivalent to the ordered state machine.

### VCP-OP-STM-002: cancellation

Cancellation before `authorized` produces no partial authority. Cancellation
after an external side effect follows the operation's transaction and recovery
contract; it must not report the action as unperformed merely because the local
request was cancelled.

### VCP-OP-STM-003: retry identity

A retry is a new attempt with a new correlation identifier. Replay identifiers
and idempotency keys retain their original meaning. Retrying a transient error
must not bypass a consumed or revoked state.

## 6. Representation and registry identifiers

### VCP-OP-REG-001: unregistered identifiers are labelled

No VCP-specific media type or `vcp:` URI scheme is currently claimed as an
IANA-registered identifier. Until registration and governance approval, network
interfaces use `application/json` with an explicit HTTPS profile URI, or a
documented application-local media type. Public documentation must not imply
external registration.

### VCP-OP-REG-002: profile URIs

Candidate profile identifiers use stable HTTPS URLs under the project domain
and resolve to a versioned description. Redirects may move the representation,
but must not silently change the identified semantics.

### VCP-OP-REG-003: namespace ownership

Every public namespace record identifies the owner, recovery owner, contact,
status, creation decision, allowed object classes, collision policy, and
revocation procedure. Unregistered names remain local and must not masquerade
as globally assigned names.

### VCP-OP-REG-004: collision handling

Exact canonical names are unique within a registry generation. Confusable or
case-folded collisions are rejected or escalated for review. Resolution returns
the canonical name and registry generation so consumers can detect drift.

### VCP-OP-REG-005: immutable historical resolution

Reassignment does not rewrite historical ownership. Superseded and revoked
records remain retrievable by immutable generation or digest for audit.

## 7. Error mapping

All failures use the exact code from the candidate
[verification status-code registry](./status-code-registry.md). An unknown code
is preserved for diagnostics and treated as failure. Human messages may vary;
numeric code and wire label remain stable within the selected registry
generation.

## 8. Test obligations

Conformance fixtures should include equal-version success, disjoint-version
failure, prerelease opt-in, stripped offers, lost capabilities, stale and
misbound revocation responses, scope expansion attempts, audience mismatch,
delegation cycles, cancellation at every gate, retry after consumption,
identifier collision, and unknown status codes. Each result cites the relevant
`VCP-OP-*` identifier and exact candidate digest.
