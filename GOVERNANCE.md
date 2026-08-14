# Interim governance and authority record

<!-- vcp-document-control
status: Interim and unratified
normative-authority: governance/authority.json
protocol-version: Protocol independent governance layer
last-reviewed: 2026-08-14 active authority and evidence boundary
owner: Interim repository administrator
evidence-boundary: Present authority and proposed process, not permanent-governance ratification
-->

**Status:** active interim repository process, unratified as a permanent charter
**Canonical authority:** this VCP-Spec repository
**Machine-readable state:** [`governance/authority.json`](./governance/authority.json)
**Last reviewed:** 2026-08-14

## Present truth

The permanent VCP governance model has not been ratified. A Technical Steering
Committee has not been constituted, community seats have not been filled, and
no neutral foundation currently controls this protocol. Repository records name
Nell Watson as the present interim administrator. That administrative fact does
not supply independent review, legal authority, registry authority, or the
multi-party quorum contemplated by the proposed charter.

The former charter is preserved as an explicitly unratified proposal in
[`governance/PROPOSED_TSC_CHARTER.md`](./governance/PROPOSED_TSC_CHARTER.md).
No provision in that proposal is treated as effective merely because the file
exists or was previously merged.

Working signal: public files describe governance as interim, the authority JSON
reports `tsc.constituted: false`, and no release gate accepts a TSC vote until a
ratification decision is recorded.

## Authority boundaries

VCP-Spec is the canonical repository for protocol text, schemas, VEP numbering,
protocol maturity, and the governance process. Other repositories may implement
or demonstrate VCP, but they link here for protocol decisions and must not run a
second VEP intake.

| Decision | Current path | Additional authority required |
|:---|:---|:---|
| Editorial correction | Reviewed VCP-Spec pull request | Interim repository administrator or delegated reviewer |
| Normative protocol or schema change | Canonical VEP issue and candidate pull request | Ratified protocol decision before release status changes |
| Extension maturity change | Canonical VEP and evidence record | Ratified governance decision |
| Permanent governance charter | Public proposal, disclosures, discussion, and vote record | Constituted participants with recorded quorum |
| Licence, patent, trademark, or contribution policy | Review pack and proposed text | Authorized rights and legal review |
| Certification mark or compatibility claim | Conformance definition and appeals process | Trademark authority and ratified governance |
| Registry publication | Coordinated release ledger | Named release and registry authority |
| Foundation transfer | Executed transfer record | Current rights holder and accepting foundation |

Working signal: SDK and Demo contribution routes point protocol proposals to the
single VCP-Spec template, and release validation rejects absent governance,
rights, or publication evidence.

## Interim operating process

### Routine repository work

Editorial corrections, broken links, validation repairs, archive classification,
and implementation-neutral clarifications may proceed through a reviewed pull
request. The pull request records scope, evidence, and whether normative meaning
could change. A change that may alter interoperable behavior is routed to a VEP.

### Normative candidates

Normative changes use the issue template in
`.github/ISSUE_TEMPLATE/spec_amendment.yml`. A proposal receives the next
number only in this repository. Discussion and candidate implementation may
proceed, but merge history alone does not establish ratification or public
release maturity.

The canonical interim status vocabulary is:

| Status | Meaning |
|:---|:---|
| Draft | Open proposal without a decision |
| Recorded pre-charter acceptance | Historical repository label, retained for provenance, without evidence of a constituted TSC vote |
| Experimental | Available for evaluation, outside the published baseline |
| Implemented in source | Candidate behavior exists, without publication authority |
| Released | Included in an authorized immutable protocol release |
| Deferred | Work deliberately postponed with a recorded reason |
| Declined | Rejected by an authorized decision record |
| Withdrawn | Removed from current consideration by its author or authority |

VEP-0001 through VEP-0003 retain their historical role in the v3.1 source
baseline. Their former `Accepted` labels are now described as recorded
pre-charter acceptance, because the repository contains no evidence of the TSC
process the former charter claimed. This truth correction does not silently
change wire behavior.

Working signal: every VEP has one status in its file and tracker, status changes
cite a decision record, and source implementation is never presented as
publication or standards-body acceptance.

## Decisions, meetings, and records

Public decisions belong in `governance/decisions/` using the decision template.
Meeting records belong in `governance/meetings/`. Each record names attendees,
authority, candidate hashes, disclosures, quorum basis, votes or objections,
conditions, effective date, and superseded decisions. If no meeting occurs, an
asynchronous decision uses the same fields.

Security-sensitive material is not forced into a public record. The public
decision records the existence, scope, authority, date, and eventual disclosure
status of an embargoed decision without publishing exploit details.

Working signal: a reader can trace every maturity or process change to a dated
record, while private vulnerability details stay in the security advisory.

## Conflicts and recusal

Anyone exercising decision authority discloses employment, funding, authorship,
close collaboration, registry ownership, intellectual-property interests, and
other relationships that a reasonable participant would consider relevant. The
decision record states whether the person participated, recused, or supplied
information without voting.

No person may count as the independent reviewer of their own work. A recusal
cannot reduce the decision below its required quorum. If all available authority
is conflicted, the item remains pending and an external reviewer is sought.

Working signal: every completed decision lists disclosures and recusals, and an
independence gate names a reviewer other than the relevant author.

## Appeals

An affected contributor may file an appeal using
`governance/APPEAL_TEMPLATE.md`. The appeal identifies the decision, alleged
process or factual error, requested remedy, and evidence. The original decision
maker may answer but does not solely decide the appeal. Until a qualified appeal
authority exists, appeals remain open rather than being deemed denied by
silence.

Working signal: appeals have identifiers, an owner who did not solely make the
original decision, a response deadline, and a reasoned outcome.

## Emergency and embargoed changes

An interim administrator may make the minimum reversible change needed to stop
an active security, privacy, safety, or data-loss risk. The change is recorded
with scope, reason, affected versions, rollback path, and a follow-up review
deadline. It cannot be used to introduce unrelated normative behavior or to
bypass a publication gate.

Embargoed security decisions use the private GitHub security advisory process
and `governance/security/SECURITY_DECISION_TEMPLATE.md`. A public summary is
published when disclosure is safe and authorized.

Working signal: emergency changes are narrow, timestamped, reversible, and
receive a later review instead of becoming permanent through inertia.

## Succession and inactivity

The interim administrator may nominate a successor in a public signed record.
A successor must affirm the interim boundaries and disclose conflicts. If the
administrator is inactive for 90 days and no succession record exists,
maintainers may continue reversible security and repository-preservation work,
but normative, legal, maturity, certification, and publication decisions remain
pending until legitimate authority is re-established.

The detailed procedure is in
[`governance/SUCCESSION_AND_INACTIVITY.md`](./governance/SUCCESSION_AND_INACTIVITY.md).

Working signal: loss of one administrator does not erase source maintenance,
and it also does not allow remaining contributors to manufacture legal or
governance authority.

## Ratifying a permanent charter

A permanent charter becomes active only when one decision record contains:

1. the exact charter hash and effective date;
2. named members, affiliations, terms, and conflict disclosures;
3. who was entitled to participate and why;
4. quorum and vote results;
5. appeal and amendment procedures;
6. security and embargo procedures;
7. succession and inactivity rules;
8. an authorized rights review for licence, patent, trademark, contribution,
   certification, and any foundation-transfer provisions;
9. repository and registry control assignments;
10. public copy updates that remove interim wording only after the decision is
    effective.

Until then, `governance/authority.json` remains `interim-unratified` and all
foundation, neutral-governance, certification, canonical-render, and public
maturity claims remain contingent.

## Rights boundary

This file is an operational truth record, not a legal opinion or rights grant.
The unresolved file-class licensing matrix is in
[`LICENSING_STATUS.md`](./LICENSING_STATUS.md). The proposed patent and marks
policy in `governance/PROPOSED_IP_AND_MARKS_POLICY.md` has no legal effect until
authorized review and adoption are recorded.
