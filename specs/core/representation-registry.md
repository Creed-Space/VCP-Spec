# VCP candidate representation and identifier registry

**Status**: Candidate design note. This document and its registry are
project-local source controls. They do not claim an IANA media type, URI scheme,
standards-body allocation, or permanent namespace authority.

The machine-readable
[`provisional-identifiers.json`](../../registries/provisional-identifiers.json)
is the current candidate registry generation. Each entry records canonical
spelling, collision key, owner and recovery roles, allowed use, status, creation
date, replacement, and an authorized decision when one exists.

## Wire representation

Until a registered VCP-specific media type is authorized, HTTP interfaces use
`application/json` and identify the exact protocol profile through a stable
HTTPS profile URL or an application-specific contract. A missing profile must
not be interpreted as the newest protocol. A receiver rejects an unknown
mandatory profile rather than guessing from payload shape.

No `vcp:` URI scheme is allocated. Source examples that use a VCP-looking
identifier are local examples unless their registry entry states otherwise.

## Allocation and collision policy

1. Canonical values and Unicode case-folded collision keys are unique within a
   generation.
2. Confusable names, reused historical names, or values controlled by an
   unrelated authority are rejected or escalated.
3. Allocation records owner and recovery roles before use. A repository account
   or domain login alone does not grant protocol authority.
4. Deprecation and revocation preserve historical resolution. Reassignment does
   not rewrite an earlier generation.
5. Formal registration requires governance and rights approval, accurate
   security and interoperability considerations, and the external registry's
   process. Source text never asserts that the external authority accepted an
   application before a verifiable receipt exists.

## Working signal

Independent implementations can resolve one spelling, generation, status, and
owner for every project identifier, while an unregistered value is always
recognizable as project-local or provisional.
