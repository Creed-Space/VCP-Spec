# VCP Conformance Claim Vocabulary

<!-- vcp-document-control
status: Current repository policy
normative-authority: Interim claim-control policy
protocol-version: VCP 3.1 with separately named amendments and extensions
last-reviewed: 2026-08-14 claim scope and governance boundary
owner: VCP Spec maintainers
evidence-boundary: Claim vocabulary and evidence requirements, not certification authority
-->

| Field | Value |
|:---|:---|
| Status | Current repository policy |
| Normative authority | Interim claim-control policy, subordinate to ratified protocol and governance decisions |
| Protocol baseline | VCP 3.1, with every amendment and extension named separately |
| Last reviewed | 2026-08-14 |
| Owner | VCP Spec maintainers |
| Evidence boundary | Controls repository and ecosystem wording. It does not create an independent certification authority or trademark permission. |

## Purpose

VCP claims must describe exactly what was tested. A repository build, fixture
count, same-project parity run, demonstration, badge, or package publication
cannot establish broader conformance by itself. Claims are valid only for the
immutable protocol revision, conformance profile, implementation artifact, and
environment named in their evidence.

## Reserved vocabulary

| Term | Permitted meaning | Minimum evidence |
|:---|:---|:---|
| **implements** | The named artifact provides a listed protocol feature. This is a capability statement, not a conformance result. | Versioned feature inventory, public API or wire behavior, and tests for the stated feature. |
| **compatible with** | The named implementation interoperates with one declared protocol, extension, API, runtime, or peer surface within a bounded matrix. | Exact versions, environment, applicable tests, unsupported areas, and known deviations. |
| **passes the named VCP test suite** | The exact artifact received passing results for the explicitly named suite or profile. | Machine-readable report, suite and runner hashes, artifact digest, environment, and complete passed, failed, unsupported, and not-applicable counts. |
| **VCP conformant for profile _P_** | The exact artifact passes every mandatory case for a versioned profile _P_, with no unresolved required failure. | Accepted profile definition, complete machine-readable results, reproducible runner, immutable artifact digest, and an authorized claim decision. |
| **interoperability-tested with _I_** | The artifact exchanged protocol data with separately named implementation _I_ for stated scenarios. | Both immutable implementation identities, scenario and profile coverage, deviations, and retained results. Organizational independence must be stated rather than implied. |
| **VCP Certified** | Reserved for a future authorized certification programme. | Ratified criteria and test authority, independent assessment rules, trademark authorization, appeals, expiry, surveillance or renewal, revocation, and a public certification record. |

The phrases **VCP compliant**, **fully VCP compatible**, **fully conformant**,
**official implementation**, and **project-maintained implementation** are prohibited
unless an authorized decision defines their exact scope and required evidence.
Unqualified compatibility or conformance language is prohibited.

## Required claim record

Every conformance or interoperability claim records:

1. the claim identifier, status, issuer, issue time, and expiry or review date;
2. the exact protocol baseline, amendments, extensions, and conformance profile;
3. the implementation name, version, source commit, packaged artifact digest,
   and installation method;
4. the conformance manifest, runner version, runner source hash, and report
   digest;
5. passed, failed, unsupported, and not-applicable totals, without counting an
   unsupported surface as a pass;
6. the operating system, architecture, language runtime, browser, feature
   configuration, and relevant dependency locks;
7. every exclusion, waiver, deviation, and untested optional behavior;
8. whether another implementation is organizationally independent or maintained
   by the same project;
9. the decision authority and any required independent reviewer;
10. links to the retained machine report, appeal path, and revocation status.

A source change, artifact rebuild, profile revision, runner change, expired
review interval, withdrawn implementation, or material finding invalidates the
claim until the affected evidence is rerun and reapproved.

## Badges and public summaries

Badges are generated only from an accepted machine-readable report and claim
record. The badge text names the profile and version, and its link resolves to
the full evidence. A badge must not collapse unsupported or not-applicable cases
into passes, outlive the underlying claim, or imply certification.

The current source candidate may state scoped suite results such as:

> VCP-SDK artifact `<digest>` passed conformance profile `<profile>` for VCP
> `<version>`: `<passed>` passed, `<unsupported>` unsupported, and
> `<not-applicable>` not applicable. Report `<report-digest>`.

It may not state that the ecosystem is independently interoperable or certified
until R054 and the relevant governance and trademark decisions are closed.

## Appeals, expiry, and revocation

An affected implementer may appeal a claim decision through the canonical VCP
governance record process. The appeal owner must be independent of the sole
original decision maker, disclose conflicts, record interim claim status, and
publish a reasoned outcome.

A claim is revoked or suspended when its artifact digest cannot be reproduced,
mandatory results no longer pass, evidence is materially incomplete, the named
profile is withdrawn, a serious undisclosed vulnerability invalidates the
tested property, or the issuing authority determines that the public wording is
misleading. Public status must change promptly and preserve the historical
record rather than silently deleting it.

No current repository actor is authorized to issue **VCP Certified** marks.
Certification criteria, trademark permission, fees if any, assessor
independence, appeals, expiry, renewal, and revocation require ratified
governance and authorized legal review.

Working if: every public claim identifies a versioned profile and immutable
artifact, unsupported coverage remains visible, badges are generated from the
same report, and no source-only or same-project result is described as
certification or independent interoperability.
