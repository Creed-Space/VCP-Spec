# VCP errata and deprecation registry

<!-- vcp-document-control
status: Empty current registry with active process
normative-authority: Interim source tracking; release authority remains open
protocol-version: VCP 3.1 source baseline
last-reviewed: 2026-08-15
owner: VCP Spec maintainers
evidence-boundary: Source correction tracking, not authority to rewrite released artifacts
-->

## Current entries

No accepted normative release errata or stable-feature deprecations are
recorded. This empty registry is explicit rather than inferred from silence.
Candidate defects remain ordinary source issues until an immutable release is
selected.

The machine-readable [`registries/errata.json`](../registries/errata.json) is
schema-validated in CI. It remains empty until an authorized record exists.

## Identifier format

Errata use `VCP-ERR-{release}-{sequence}`. Deprecations use
`VCP-DEP-{surface}-{sequence}`. Identifiers are never reused.

Each erratum records affected release and digest, severity, requirement IDs,
original and corrected interpretation, implementation impact, security and
privacy impact, conformance changes, decision authority, publication date, and
superseding release. Each deprecation records first warning, replacement,
migration, compatibility window, security exception process, final supported
version, and removal decision.

Released files remain immutable. Corrections are separate signed records and
new releases. A mutable branch repair is useful source evidence, not a
retroactive correction of an immutable publication.

## Working signal

This process is working when every public correction resolves from an immutable
release digest to one uniquely identified erratum, affected implementations,
updated tests, and a superseding release without rewriting history.
