# Repository security controls

<!-- vcp-document-control
status: Partial external repository state
normative-authority: Repository administration policy
protocol-version: Protocol independent repository control
last-reviewed: 2026-08-15 hosted security readback and evidence boundary
owner: Authorized repository administrators
evidence-boundary: Recorded desired settings and authenticated readback, not proof of untested branch controls
-->

**Status:** repository security features applied; branch protection pending candidate integration

Authenticated GitHub API changes and readback on 2026-08-15 enabled private
vulnerability reporting, Dependabot alerts and security updates, secret
scanning, push protection, non-provider patterns, and validity checks. Default
workflow permissions are read-only and Actions cannot approve pull requests.
Repository metadata and topics were updated. The candidate adds CodeQL and
dependency-review workflows.

`main` branch protection remains deliberately pending until this candidate is
integrated and its exact contexts exist. Applying the future context list first
would deadlock integration. After integration, an authorized administrator must
enable pull-request review, CODEOWNERS, last-push approval, conversation
resolution, strict current checks, administrator enforcement, and deletion and
force-push blocks.

The retained API transcript proves the settings already applied. Final branch
protection evidence is a second API readback plus a test pull request that
cannot merge with an unresolved conversation, absent review, missing current
check, vulnerable dependency, or detected secret. Source presence does not
prove hosted enforcement.

Working signal: the readback matches `.github/repository-policy.json`, required
contexts all exist, and the deliberately failing test pull request is blocked.
