# Dependency maintenance policy

<!-- vcp-document-control
status: Current candidate dependency policy
normative-authority: Repository maintenance policy
protocol-version: Tooling for VCP 3.1 and candidate materials
last-reviewed: 2026-08-14 active authority and evidence boundary
owner: VCP Spec maintainers
evidence-boundary: Dependency review process, not hosted update or vulnerability remediation proof
-->

Status: maintained candidate policy
Owner: specification maintainers
Last reviewed: 2026-08-14

The specification repository uses weekly Dependabot checks for npm, Python, and
GitHub Actions. Compatible minor and patch updates are grouped by ecosystem.
Major updates remain separate so their migration impact, minimum runtime, and
validation-tool behavior can be reviewed explicitly.

Every dependency update must preserve the exact lock or requirement files,
complete repository validation, schema example checks, link and prose audits,
and any package-specific tests. A security update may bypass the weekly cadence
and grouping when delay creates material exposure. Rejecting or deferring an
update requires a recorded reason, security consequence, review date, and
revisit trigger.

GitHub Actions must remain pinned to immutable commit SHAs. A maintainer verifies
the upstream repository identity and advertised release before accepting a new
pin. A candidate only supersedes an older dependency pull request when its
resolved version is equal or newer and the relevant checks pass.

Working if: Dependabot produces bounded minor and patch groups, majors remain
individually reviewable, every merged update has candidate-bound validation, and
no workflow uses a mutable action reference.
