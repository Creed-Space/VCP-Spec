# VCP support, maintenance, and sunset policy

<!-- vcp-document-control
status: Current interim lifecycle policy
normative-authority: Repository maintenance policy
protocol-version: VCP 3.1 source baseline with source-only SDK candidates
last-reviewed: 2026-08-15
owner: VCP maintainers
evidence-boundary: Maintenance expectations and end-state procedure, not a paid support contract or release guarantee
-->

## Current support boundary

The repositories provide community maintenance for current `main` source and
the exact deployed Demo commit. No registry package, long-term-support line,
paid support plan, continuous on-call service, or service-level agreement is
currently promised. Older source snapshots are handled according to security
impact, reproducibility, maintainer capacity, and any later published release
policy.

Support routes are public issues for non-sensitive reproducible defects,
private security reporting for vulnerabilities, and recorded governance
decisions for protocol meaning or authority. Private data and credentials do
not belong in a support request.

## Release-line policy

An immutable release must declare its supported protocol profiles, runtimes,
maintenance owner, security backport window, end-of-life review date, migration
path, and evidence links. Experimental features receive no compatibility
guarantee beyond their named candidate. A security repair may shorten a
deprecation window, but the exception and migration consequence are recorded.

## Maintenance mode triggers

The project enters maintenance mode when sustained maintainer capacity is
insufficient for new protocol work, governance becomes inactive, an unresolved
rights or security condition blocks safe development, or adoption no longer
justifies active expansion. Maintenance mode permits security, compatibility,
documentation, archival, and correction work. It does not silently promote
proposals or broaden claims.

## Archive or transfer procedure

1. Publish a dated notice naming affected repositories, releases, packages,
   domains, security contact, and last supported date.
2. Stop new releases, disable unsafe automation, and preserve read-only source,
   decisions, errata, advisories, provenance, and conformance evidence.
3. Deprecate or yank packages according to registry capability and security
   need. Never replace an existing version with different bytes.
4. Revoke or suspend current claims, badges, signing keys, deployment tokens,
   and unused service credentials. Retain public verification keys and
   revocation records where safe.
5. Redirect domains only to an authorized successor or durable archive. Keep
   certificate and DNS renewal active through the published transition.
6. Delete retained personal or operational data according to the approved
   retention record. Preserve only evidence with a lawful, documented purpose.
7. A successor records custody, authority, rights, security obligations,
   recovery owners, conflicts, and whether the prior project endorses the
   transfer. Repository access alone does not prove succession.

## Working signal

This policy is working when a prospective adopter can identify the supported
surface and contact route, and a loss of funding, maintainer availability, or
governance can lead to a safe, truthful archive without abandoned credentials,
misleading packages, or disappearing correction records.
