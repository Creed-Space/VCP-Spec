# Repository security controls

<!-- vcp-document-control
status: Desired external repository state
normative-authority: Repository administration policy
protocol-version: Protocol independent repository control
last-reviewed: 2026-08-14 active authority and evidence boundary
owner: Authorized repository administrators
evidence-boundary: Recorded desired settings and read-only observations, not proof settings were applied
-->

**Status:** desired state recorded; external application pending

Read-only GitHub API probes on 2026-08-14 found no `main` branch protection, no
rulesets, no CodeQL analysis, and disabled secret scanning. The candidate adds
immutable CodeQL and dependency-review workflows. The intended branch and
security settings are machine-readable in `.github/repository-policy.json`.

An authorized administrator must wait until each candidate workflow has emitted
its exact context, then enable pull-request review, CODEOWNERS, last-push
approval, conversation resolution, strict current checks, administrator
enforcement, deletion and force-push blocks, dependency graph and security
updates, secret scanning and push protection, validity checks, and CodeQL.

The external closure evidence is an API readback plus a test pull request that
cannot merge with an unresolved conversation, absent review, missing current
check, vulnerable dependency, or detected secret. Source presence does not prove
those settings are enabled.

Working signal: the readback matches `.github/repository-policy.json`, required
contexts all exist, and the deliberately failing test pull request is blocked.
