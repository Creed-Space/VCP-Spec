# VCP issue and decision routing

<!-- vcp-document-control
status: Current contribution routing policy
normative-authority: Interim repository process
protocol-version: Protocol independent process
last-reviewed: 2026-08-15
owner: VCP maintainers
evidence-boundary: Intake classification and response expectations, not permanent governance authority
-->

| Report class | Public route | Private route or restriction | Decision owner |
|:---|:---|:---|:---|
| Reproducible SDK defect | VCP-SDK bug form | Use security route if exploitation or private data is involved | SDK maintainers |
| SDK enhancement | VCP-SDK feature form | Do not include confidential adopter details | SDK maintainers within compatibility policy |
| Specification ambiguity or amendment | VCP-Spec amendment form | Security-sensitive meaning stays embargoed | Interim protocol authority pending ratification |
| Documentation or example error | Issue in the owning repository | Remove personal data before reporting | Document owner |
| Demo accessibility, privacy, or usability | Demo feedback page and public Spec or SDK route where applicable | Email for personal or security-sensitive detail | Demo maintainers plus required human reviewer |
| Vulnerability | No public issue | Private vulnerability report or `security@creedspace.com` | Security coordinator |
| Governance decision | Public decision template | Conflicts and protected evidence follow the governance process | Recorded authorized decision maker |
| Appeal or dispute | Appeal template | Reporter safety or embargo may require a private appendix | Appeal owner independent of the sole original decision maker |

Every public template warns against credentials, private context, personal
state, private prompts, unreleased vulnerabilities, and third-party data. A
maintainer who sees such content limits further exposure, preserves necessary
evidence privately, and asks the platform owner to remove the public copy.

Response targets follow the security process for vulnerabilities. Ordinary
issues receive triage when maintainer capacity permits; the project does not
promise a service-level agreement. A triaged item receives a type, affected
version or commit, evidence state, owner role, and disposition such as accepted,
needs reproduction, authority decision required, externally blocked,
superseded, or declined with reason.

Discussions support open questions and adopter experience. They do not ratify a
protocol change, reserve a namespace, certify an implementation, or grant
rights. Any accepted change moves into a reviewable issue, VEP, or decision
record.

## Working signal

A newcomer is routed without guessing, sensitive content stays private, and a
closed thread states what evidence or authority resolved it rather than using
closure as a substitute for a decision record.
