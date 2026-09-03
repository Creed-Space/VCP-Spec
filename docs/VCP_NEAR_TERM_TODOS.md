# VCP Current Work Register

<!-- vcp-document-control
status: Current planning record
normative-authority: None
protocol-version: VCP 3.1
last-reviewed: 2026-08-13 status and authority classification
owner: VCP maintainers
evidence-boundary: Plans and gates only
-->

| Field | Value |
|:---|:---|
| Status | Current planning record |
| Normative authority | None |
| Protocol baseline | VCP 3.1 |
| Last reviewed | 2026-08-13 |
| Owner | VCP maintainers |
| Evidence boundary | Plans and gates. Completion requires linked machine or authorized human evidence. |

## Current state

- VCP 3.1 is the repository protocol baseline.
- VCP 3.2 material remains pre-release.
- VEP-0005 is a draft response to MCP 2026-07-28.
- SDK artifacts are published at 4.2.0; the next registry release needs a new
  coordinated review ledger.
- The Demo is not conformance evidence.
- Independent review, governance ratification, and canonical rendered documents
  still require separate authority and receipts; 4.2.0 shipped with X017, S033
  and K045 visibly waived under the runbook's first-publication exemption.

## Machine work before an immutable candidate

1. Keep public instructions synchronized with the publication-state record.
2. Run repository, schema, SDK, conformance, security, package, browser, and
   accessibility checks on the exact selected source tree.
3. Produce a coverage report whose unsupported suites remain explicit.
4. Build packages once, inspect their contents, generate SBOMs and attestable
   hashes, and create the release manifest last.
5. Select exact Spec, SDK, and Demo commits in the coordinated review ledger.
6. Run hosted CI on those immutable commits and retain workflow URLs and hashes.

## Decisions that machines cannot make

| Decision | Required authority |
|:---|:---|
| Final registry names and owners | Project owner, registry owners, and trademark review |
| VCP 3.2 maturity | Ratified protocol governance |
| Licensing matrix and IETF draft rights | Rights authority with appropriate legal review |
| Governance seats, quorum, and effective date | Constituting participants |
| Canonical DOCX and PDF | Editorial and publication authority |
| Independent protocol, cryptographic, privacy, and security acceptance | Reviewers independent of this implementation effort |
| Package publication and production deployment | Named release and deployment approvers |

## Evidence rule

Each completed item records an exact commit or artifact digest, the command or
workflow that produced the result, the result scope, and the identity of any
human approver. Earlier evidence is superseded whenever the candidate changes.
Passing source tests never substitutes for installed-artifact, deployed-runtime,
human-review, rights, or publication evidence.

The exhaustive improvement ledger for the current programme is maintained with
the coordinated implementation evidence, outside this normative repository.
