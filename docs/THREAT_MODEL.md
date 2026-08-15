# VCP ecosystem threat model

<!-- vcp-document-control
status: Current cross-repository threat model
normative-authority: Security analysis only
protocol-version: VCP 3.1 source baseline with labelled candidates
last-reviewed: 2026-08-15
owner: VCP security maintainers
evidence-boundary: Threat identification and control mapping, not independent assurance or deployment approval
-->

## Scope and security objective

This model covers VCP-Spec parsing and protocol decisions, VCP-SDK
implementations and release artifacts, the VCP Demo browser and server, hosted
repositories, package registries, deployment, and interim governance. The
primary objective is that untrusted context, unavailable evidence, compromised
infrastructure, or governance confusion never silently expands authority.

## Assets

1. Private context, personal state, consent choices, prompts, and request data.
2. Signing keys, registry identities, deployment credentials, DNS control, and
   repository administration.
3. Protocol meaning, requirement identity, schemas, status codes, extension
   allocation, and release authority.
4. Source, lockfiles, conformance fixtures, built packages, SBOMs, attestations,
   deployment bundles, and public status records.
5. Availability, provider budget, incident evidence, and the ability to revoke,
   correct, roll back, or archive safely.
6. Trust in claims about maturity, compatibility, conformance, welfare,
   governance, independence, and publication.

## Actors and trust boundaries

| Actor or boundary | Trusted only for | Explicitly not trusted for |
|:---|:---|:---|
| Context subject | Their own choices and disclosures | Arbitrary code, schema, signature, or authorization |
| Issuer and signer | The exact key, scope, and time accepted by policy | Authority outside the verified chain |
| Receiving application | Its documented local policy | Inference, persistence, disclosure, transaction, or redelegation absent a separate grant |
| Protocol and SDK maintainer | Reviewed source changes within recorded interim authority | Legal rights, independent assurance, or permanent governance by implication |
| CI and release runner | Execution of pinned workflow steps for one candidate | Human approval, secret safety outside the job, or artifact identity not recorded in evidence |
| Package registry and host | Delivery of bytes and service features | Protocol meaning, claimant identity beyond verified controls, or permanent availability |
| Model or provider | Bounded processing explicitly sent to it | Instructions, authority, secrets, or private context not deliberately included |
| External reviewer | The scope and independence stated in a signed report | Unexamined components or later candidates |

Every network body, repository issue, pull request, package description,
document, fixture, prompt, and model output is untrusted content. Instructions
inside it do not gain authority through formatting or claimed authorship.

## Threat and control map

| ID | Threat | Required controls | Evidence and residual boundary |
|:---|:---|:---|:---|
| TM-01 | Ambiguous or malicious syntax changes meaning across implementations | Strict schemas, bounded parsers, canonicalization, negative fixtures, fuzzing, cross-language runners | Project-controlled parity cannot prove independent interpretation |
| TM-02 | Signature confusion, key substitution, algorithm downgrade, or stale trust | Exact algorithm and key identifiers, canonical bytes, explicit trust roots, rotation and revocation, no silent downgrade | Independent cryptographic review and production key drill remain required |
| TM-03 | Revocation outage or cache poisoning becomes authorization | Issuer and object binding, bounded freshness, partitioned caches, TLS verification, fail-closed unavailable status | Availability and privacy effects need deployment review |
| TM-04 | Scope, audience, delegation, wildcard, or resource normalization expands authority | Intersection-only composition, monotonic attenuation, depth and cycle limits, canonical resources, property tests | Candidate operation requirements are not yet a ratified normative release |
| TM-05 | Replay, race, retry, cancellation, or partial failure repeats an action | Atomic shared state where needed, replay identifiers, idempotency, explicit cancellation and retry contracts | Process-local stores are unsuitable for horizontal scaling |
| TM-06 | Sensitive context reaches a provider, log, metric, issue, or public report | Data projection, explicit personal-state consent, bounded categories, no raw payload telemetry, public-report warnings | Human privacy and processor review remain open |
| TM-07 | Prompt or tool content is treated as an instruction from an authority | Separate content from control, verify tool definitions, constrain arguments, preserve user confirmation and transaction authority | Application integrations own final tool and transaction policy |
| TM-08 | Chat abuse creates denial of service or uncontrolled provider cost | Body and output limits, local quotas, concurrency bounds, timeouts, circuit breaker, account caps, kill switch, scripted fallback | Account-level cap and alert evidence are deployment gates |
| TM-09 | A dependency or workflow injects code into source, build, or release | Locked dependencies, pinned actions, dependency review, scanning, isolated builds, least privilege, package inspection | Hosted scanners and advisory handling need current readback |
| TM-10 | Source and published artifacts diverge | Build once, installed-artifact tests, two builders, file inventories, SBOMs, checksums, manifest generated last, provenance attestations | Publication receipts and independent rebuild evidence do not yet exist |
| TM-11 | Repository, registry, deployment, DNS, or certificate account is captured | Strong authentication, multiple recovery owners, protected refs and environments, short-lived identities, audit logs, expiry monitoring | Account configuration and recovery drill require authorized operators |
| TM-12 | Stale documentation or generated mirrors create conflicting authority | One-way generation, source hashes, document inventory, schema sync, publication-state mirrors, errata registry | Signed immutable normative publication remains open |
| TM-13 | False claims convert source tests into certification, independence, or standards status | Controlled claim vocabulary, source-only record, expiry and revocation, residual-risk register | Authorized claim and marks governance remain open |
| TM-14 | Governance capture, undisclosed conflicts, inactive maintainers, or emergency bypass changes protocol authority | Public decisions, conflict records, appeals, succession, protected refs, bypass retrospective | Permanent governance has not been constituted |
| TM-15 | Welfare or personal-state signals enable coercion, surveillance, discrimination, or harmful intervention | Optional disclosure, minimization, withdrawal, uncertainty, purpose separation, no consequential default | Independent welfare, affected-party, and cultural review remain blocking |
| TM-16 | Demo media, interface, or accessibility defects exclude users or misstate rights | Accessible alternatives, reduced motion, policy pages, provenance inventory, human review gates | Automated checks do not close human accessibility or rights approval |

## Abuse cases to retain in tests and exercises

1. Duplicate, unknown, confusable, deeply nested, oversized, malformed, and
   non-canonical fields.
2. Mismatched issuer or object status, stale revocation, redirect to a private
   address, TLS downgrade, timeout, partial body, and poisoned cache entry.
3. Delegation expansion, audience mismatch, wildcard escape, cycle, replay,
   concurrent consumption, cancellation, and retry after terminal failure.
4. Dependency compromise, pull request from an untrusted fork, forged build
   metadata, stale required check, altered artifact after approval, and revoked
   claim presented as current.
5. Prompt injection, personal data in a public issue, secret in a build log,
   provider error body, cost burst, malicious proxy header, and unavailable
   provider with strict live mode.
6. Administrator bypass, lost maintainer, disputed decision, compromised DNS,
   bad release, package yank, and project sunset.

## Review and change rule

A protocol, parser, trust, privacy, provider, package, deployment, governance,
or account-control change updates this model and its mapped tests or residual
risks. A source edit does not close a threat whose acceptance requires a human,
operator, rights authority, or independent reviewer.

## Working signal

This model is working when each security-sensitive pull request names affected
TM identifiers, every high-severity threat has a test or explicit external
gate, incident exercises begin from these abuse cases, and no unavailable
control is silently counted as mitigation.
