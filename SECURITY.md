# Security Policy

<!-- vcp-document-control
status: Current candidate security policy
normative-authority: Repository security process
protocol-version: VCP 3.1 baseline and source candidates
last-reviewed: 2026-08-15 reporting and response coordination
owner: VCP Spec maintainers
evidence-boundary: Reporting and source security scope, not independent security certification
-->

## Supported versions

| Surface | Status |
|:---|:---|
| VCP v3.1 core specification | Supported |
| v3.2 amendments and VEP-0004 | Pre-release review candidate |
| Older specification versions | Security fixes considered case by case |

An extension's `Stable` status does not make an unreleased core amendment a
published release. Reports should name the affected document and commit hash.

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability. Use the repository's
[private vulnerability report](https://github.com/Creed-Space/VCP-Spec/security/advisories/new).
Email [security@creedspace.com](mailto:security@creedspace.com) if the GitHub
route is unavailable. The hosted private-report setting was enabled and read
back on 15 August 2026; a successful reporter-side test remains operational
evidence rather than source evidence.

Include the affected section or schema, an impact analysis, reproduction steps,
and any proposed mitigation. Do not include live credentials or personal data.

## Scope

Protocol parsing, signatures, revocation, namespace verification, privacy and
consent boundaries, schema bypasses, denial of service, and unsafe normative
examples are in scope. Editorial disagreements and governance proposals without
a security impact belong in the public VEP process.

The [coordinated security response](./docs/SECURITY_RESPONSE.md) defines
severity, acknowledgement targets, embargo, disclosure, backport, advisory,
release, and revocation roles. The [ecosystem threat model](./docs/THREAT_MODEL.md)
maps material trust boundaries to controls and residual gates. These are
interim process targets, not proof of staffing, a completed exercise, or
independent assurance.
