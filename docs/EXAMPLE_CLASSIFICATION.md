# VCP example classification policy

<!-- vcp-document-control
status: Current repository policy
normative-authority: Interim source-maintenance policy
protocol-version: VCP 3.1 source baseline and labelled candidates
last-reviewed: 2026-08-15
owner: VCP Spec maintainers
evidence-boundary: Example interpretation and validation policy, not normative release authority
-->

Examples support comprehension and testing. They do not acquire normative
authority merely because they are machine-readable or appear inside a
specification.

## Classes

| Class | Meaning | May define a requirement? |
|:---|:---|:---|
| `normative-candidate` | A requirement or algorithm in candidate specification prose | Yes, subject to the document's authority and release status |
| `informative` | Explanation consistent with controlling requirements | No |
| `illustrative` | One possible payload, workflow, or result | No |
| `conformance fixture` | Executable accept or reject case tied to named requirements | It tests requirements; it does not create them |
| `historical` | Preserved lineage or superseded syntax | No |

The generated
[`status/document-inventory.json`](../status/document-inventory.json) assigns a
publication class and digest to every standalone example and schema fixture.
CI rejects inventory drift.

## Embedded examples

An embedded example inherits the containing document's status but remains
illustrative unless the surrounding text explicitly states that exact bytes are
normative. Words such as “example”, “for instance”, and “one encoding” are not
requirements. A normative byte sequence must have a stable requirement
identifier, exact canonicalization rules, and a conformance fixture.

## Conflict handling

When an example conflicts with a schema or an identified requirement, the
example is defective. Implementations must not choose whichever representation
is easier. The issue record names the affected candidate digest, and the repair
updates or supersedes all mirrors plus conformance evidence.

## Security and privacy

Examples use synthetic identifiers and must not contain credentials, personal
data, live endpoints that invite unsafe traffic, or realistic secrets. Example
keys are labelled non-production. Invalid security examples are stored only in
explicit negative-fixture locations.

## Working signal

This policy is working when a reader can determine, from the inventory and
containing document, whether a payload is a requirement, a test of one, an
illustration, or historical material without inferring authority from file
format.
