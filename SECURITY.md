# Security Policy

<!-- vcp-document-control
status: Current candidate security policy
normative-authority: Repository security process
protocol-version: VCP 3.1 baseline and source candidates
last-reviewed: 2026-08-14 active authority and evidence boundary
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

Do not open a public issue for a suspected vulnerability. Use
[GitHub private vulnerability reporting](https://github.com/Creed-Space/VCP-Spec/security/advisories/new)
or email [security@creedspace.com](mailto:security@creedspace.com).

Include the affected section or schema, an impact analysis, reproduction steps,
and any proposed mitigation. Do not include live credentials or personal data.

## Scope

Protocol parsing, signatures, revocation, namespace verification, privacy and
consent boundaries, schema bypasses, denial of service, and unsafe normative
examples are in scope. Editorial disagreements and governance proposals without
a security impact belong in the public VEP process.

Receipt is normally acknowledged within two business days. Remediation and
disclosure timing depend on severity and coordinated-release needs.
