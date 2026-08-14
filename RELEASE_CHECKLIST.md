# Coordinated Release Evidence

<!-- vcp-document-control
status: Current candidate release checklist
normative-authority: Coordinated release process
protocol-version: VCP 3.1 baseline with candidate packages
last-reviewed: 2026-08-14 active authority and evidence boundary
owner: Authorized release maintainers
evidence-boundary: Required evidence classes, not release approval or publication receipt
-->

Complete this checklist against exact commit hashes. Evidence from one hash does
not transfer to a changed candidate.

## Candidate identity

- Spec commit:
- SDK commit:
- Demo commit:
- Protocol baseline and amendment status:
- Python, Rust, npm, and Demo versions:

## Machine gate

- [ ] Spec `make check`
- [ ] SDK Python lint, type check, tests, build, and dependency audit
- [ ] SDK Rust format, clippy, tests, docs, and package check
- [ ] SDK WebMCP check, tests, build, package-content check, and dependency audit
- [ ] Shared conformance and schema-sync checks
- [ ] Demo lint, type check, tests, links, build, budgets, and dependency audit
- [ ] Secret scan and package manifest review

## Human gate

- [ ] Accessibility and screen-reader review
- [ ] Protocol and cryptographic review
- [ ] Documentation examples reviewed for safe production interpretation
- [ ] Governance approval for normative and maturity changes

## Rights and policy gate

- [ ] Asset and binary-document provenance reviewed
- [ ] License, trademark, patent, contribution, and privacy posture approved

## Deployment and publication gate

- [ ] Authorized release owner approves exact hashes and release order
- [ ] Registry and hosting credentials used only by the authorized publisher
- [ ] Signed artifacts and provenance attestations recorded
- [ ] Production smoke tests run against deployed URLs and registry packages
- [ ] Rollback owners and instructions confirmed

Use `reviews/GOVERNANCE_EDITORIAL_INDEPENDENT_REVIEW.md` for the exact S030
through S033 evidence and the Spec inputs to X016 and X017. Index the completed
evidence in VCP-SDK's coordinated review ledger.
