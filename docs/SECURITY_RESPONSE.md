# VCP coordinated security response

<!-- vcp-document-control
status: Current interim security process
normative-authority: Repository security operations
protocol-version: Protocol independent process
last-reviewed: 2026-08-15
owner: VCP security maintainers
evidence-boundary: Response roles and targets, not proof of staffing or completed exercise
-->

## Intake and ownership

Suspected vulnerabilities stay private. Public repositories use GitHub private
vulnerability reporting when the hosted setting is enabled. The fallback and
the private Demo contact are `security@creedspace.com`. A test report must be
acknowledged by the named operator before either route is advertised as
verified.

The initial coordinator owns acknowledgement, evidence protection, severity,
embargo, and assignment. Component owners investigate. A release authority
approves publication or package action. A privacy authority handles personal
data. A rights authority reviews wording with legal consequences. One person
may hold multiple interim roles, but the record must disclose that fact.

## Severity and target clocks

| Severity | Example | Acknowledge target | Initial containment or plan target |
|:---|:---|---:|---:|
| Critical | Active compromise, credential or private-context exposure, signature bypass, uncontrolled publication | 4 hours | 24 hours |
| High | Reliable authorization bypass, material parser or revocation failure, serious supply-chain exposure | 1 business day | 3 business days |
| Medium | Bounded security weakness with prerequisites or limited impact | 3 business days | 10 business days |
| Low | Defense-in-depth or hardening issue | 5 business days | Next planned maintenance review |

Targets are an interim process goal, not a service-level agreement. The
coordinator records missed targets and current risk rather than changing the
timestamp or severity to appear compliant.

## Response flow

1. Assign an opaque incident ID. Keep secrets, personal data, exploit details,
   and reporter identity out of public trackers.
2. Preserve the affected source commit, artifact digest, registry receipt,
   deployment identity, logs, and minimal reproduction.
3. Classify affected protocol versions, packages, deployment routes, keys,
   claims, and downstream consumers.
4. Contain through a reversible feature disable, credential rotation, ref
   protection, deployment rollback, claim suspension, or access restriction.
5. Repair in a private advisory or access-controlled branch. Add a regression
   that fails before the repair and passes after it.
6. Rebuild and rerun candidate-specific security, conformance, package, and
   deployment gates. Review whether keys, attestations, badges, or prior claims
   require revocation.
7. Coordinate disclosure with the reporter. Publish an advisory only through
   the authorized role, with affected versions, impact, remediation, credit,
   and evidence boundaries.
8. Backport only to a named supported line. Otherwise document the upgrade,
   deprecation, or source-only mitigation.
9. Complete a review covering detection, decisions, timing, data handling,
   communications, control gaps, and owners.

## Embargo and disclosure

Embargo access is least privilege. Every recipient receives the minimum needed
for their role and is recorded. The project does not promise a fixed public
disclosure date before impact, downstream coordination, and reporter safety are
understood. Indefinite silence requires a recorded reason and review date.

Public advisories distinguish a confirmed exploit, plausible exposure,
defense-in-depth repair, and unverified report. Credit follows reporter wishes.
An absence of known exploitation is never phrased as proof that none occurred.

## Keys, releases, and revocation

Compromised signing or publishing identity triggers immediate suspension of
affected releases and claims, credential rotation through the owning service,
inventory of all uses since the last known safe event, and an immutable
revocation or supersession record. Package yanks, deprecations, deployment
rollbacks, Spec corrections, and badge revocation are coordinated rather than
performed as unrelated actions.

## Exercise requirement

Before an immutable public release, run a timestamped tabletop from private
report intake through triage, repair, review, advisory, rebuilt artifacts,
rollback or yank, claim revocation, and public correction. The report records
role gaps and delivery evidence. This document remains process evidence only
until that exercise exists.

## Working signal

The process is working when a simulated critical report has one owner at each
step, confidential material never enters a public issue or log, every affected
artifact and claim is identified, and closure cites rebuilt or deployed
evidence rather than source intent.
