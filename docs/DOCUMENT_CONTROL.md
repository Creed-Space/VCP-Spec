# VCP Document Control

<!-- vcp-document-control
status: Current repository policy
normative-authority: Interim governance process
protocol-version: VCP 3.1
last-reviewed: 2026-08-15 status and authority classification
owner: VCP Spec maintainers
evidence-boundary: Classification and precedence policy
-->

| Field | Value |
|:---|:---|
| Status | Current repository policy |
| Normative authority | Interim governance process |
| Protocol baseline | VCP 3.1 |
| Last reviewed | 2026-08-15 |
| Owner | VCP Spec maintainers |
| Evidence boundary | Classification and precedence policy |

The machine-readable
[`status/document-inventory.json`](../status/document-inventory.json) records
the status, effective version, authority, owner, replacement, publication
class, review date, and digest of every specification, schema, registry, VEP,
example, and archived generation. CI regenerates the inventory and rejects
unclassified or drifted artifacts. Empty dependency or replacement fields mean
that no relationship has yet been asserted, not that no relationship exists.

## Required header

Every active Markdown page under `docs/`, every named public repository policy,
and the canonical VEP tracker records six fields near its title: status,
normative authority, protocol version, last reviewed date, owner, and evidence
boundary. Generated files may carry the same fields in machine metadata.
Versioned normative specifications retain their existing normative headers and
status rules. Archived evidence is exempt when an archive index records its
provenance and withdrawn authority.

Repository validation rejects a missing, duplicate, malformed, empty, or
unknown field, a future review date, and a review older than 366 days.

## Precedence

When documents conflict, use this order:

1. ratified governance and recorded protocol decisions, when such records exist;
2. versioned normative source baselines with their actual authority status;
3. versioned machine schemas for the same protocol revision;
4. VEPs with a recorded authorized decision that explicitly amend that revision;
5. conformance profiles and fixture manifests;
6. current non-normative companions and guides;
7. implementation documentation;
8. demos, plans, research notes, and archives.

A schema and specification conflict is a release blocker. Maintainers do not
choose whichever copy makes a test pass.

## Status vocabulary

| Status | Meaning |
|:---|:---|
| Published baseline | Current repository protocol reference, without implying external standards status |
| Recorded pre-charter acceptance | Historical baseline label without evidence of a constituted TSC vote |
| Accepted | Approved by a recorded, authorized governance decision |
| Candidate | Reviewable pre-release material |
| Experimental | Behavior available for evaluation, excluded from baseline guarantees |
| Draft | Proposal without approval |
| Companion | Explanatory material subordinate to normative authority |
| Historical | Preserved provenance with no current authority |
| Withdrawn | Explicitly excluded from current use or publication readiness |

## Evidence boundaries

Source correctness, installed artifacts, hosted CI, deployed runtime, human
review, rights approval, governance ratification, and publication receipts are
separate evidence classes. A document states which class it can support.

## Review rule

Any normative or public-status change updates its header, changelog, affected
schemas, fixtures, generated status page, and cross-repository contract checks.
The candidate is then validated again from its exact source state.
