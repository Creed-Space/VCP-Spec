# VCP-Spec governance, editorial, and independent review

This worksheet covers S030, S031, S032, S033, and the Spec portions of X016 and
X017. Complete it against the exact VCP-Spec commit and working-tree digest in
the coordinated release ledger. Machine validation cannot appoint governance
members, choose a canonical publication artifact, decide amendment maturity,
provide legal advice, or establish independent review.

Completed reports may contain personal details, conflict disclosures, legal
advice, or embargoed findings. Store those reports in the controlled release
evidence directory and publish only the approved public record.

## Candidate identity

| Field | Value |
|---|---|
| Spec commit | |
| Spec working-tree SHA-256 | |
| Combined candidate SHA-256 | |
| Candidate-manifest SHA-256 | |
| Published protocol baseline | |
| Proposed amendment | |
| Current proposed maturity | |
| Review coordinator | |
| Review period | |

Stop when any identity differs from the coordinated ledger.

## S030: governance seats and ratification

### A. Constituting the decision body

Before a normative or maturity vote, record:

1. The governance text that grants authority for this decision.
2. Named seats, term, appointment method, voting rights, and vacancies.
3. Quorum and voting threshold.
4. Conflict-of-interest disclosure and recusal rules.
5. Notice period, agenda publication, comment period, and meeting accessibility.
6. Minute taker, record location, correction process, and publication policy.
7. Appeal, reconsideration, emergency action, and tie-breaking procedure.
8. Representation of implementers, users, affected communities, safety and
   privacy expertise, and Becoming Mind interests where the adopted governance
   model provides such standing.

### Seat record

| Seat | Member | Selection authority | Term | Conflict disclosure | Recused items | Voting status |
|---|---|---|---|---|---|---|
| | | | | | | |

Vacant seats and abstentions remain visible. Do not fill them with assumed
consent.

### Ratification record

| Field | Value |
|---|---|
| Proposal identifier and exact hash | |
| Notice date | |
| Comment period | |
| Meeting date and location | |
| Quorum rule | |
| Quorum achieved | pending |
| Votes for, against, abstain, recused | |
| Amendments adopted during meeting | |
| Final text hash | |
| Appeal deadline | |

Required ledger evidence kind: `governance-record` for S030.

## S031: canonical DOCX and PDF rendering

The repository currently contains multiple publication-oriented DOCX
candidates. Treat each as a separate artifact until editorial authority selects
one exact source and one exact derived PDF.

### Candidate inventory

Inventory at least these current files and any later candidate discovered by
the source manifest:

1. `Value Context Protocol - Clean.docx`
2. `Value Context Protocol MDPI - Styled.docx`
3. `Value Context Protocol MDPI I2D2.docx`
4. `Value Context Protocol MDPI I2D3.docx`
5. `VCP_MDPI_Clone.docx`
6. `VCP_MDPI_Pure.docx`
7. `VCP_MDPI_Surgical.docx`

| Candidate | SHA-256 | Source relationship | Page count | Rendering environment | Disposition |
|---|---|---|---:|---|---|
| | | | | | pending |

### Render and compare

For every viable candidate:

1. Record original SHA-256, byte size, authoring application, and format
   metadata.
2. Render with the intended publication toolchain. Record application, version,
   operating system, fonts, page size, locale, and PDF export settings.
3. Render every page to images for visual review. Preserve the PDF and page
   image hashes.
4. Compare title, authorship, abstract, headings, numbering, references,
   footnotes, equations, code, tables, diagrams, captions, cross-references,
   appendices, headers, footers, widows, orphans, and page breaks.
5. Confirm embedded links and bookmarks point to intended destinations.
6. Confirm fonts are embedded or replaced according to publication and licence
   requirements.
7. Check document language, reading order, tagged PDF structure, selectable
   text, alt text, table headers, contrast, and meaningful link names.
8. Inspect document properties, comments, tracked changes, hidden text, custom
   XML, embedded files, and personal metadata before publication.
9. Compare normative content with the canonical Markdown or other source. Any
   textual divergence requires an explicit source-of-truth decision.
10. Perform a second-person visual review at 100% and print-preview scale.

### Selection decision

| Field | Selected value |
|---|---|
| Canonical editable DOCX path | |
| Canonical DOCX SHA-256 | |
| Canonical PDF path | |
| Canonical PDF SHA-256 | |
| Normative source relationship | |
| Rendering environment | |
| Accessibility limitations | |
| Archived alternatives and retention policy | |
| Editorial authority and timestamp | |

Do not delete alternatives merely to make the choice appear settled. Archive or
remove them only under the recorded editorial and repository-retention policy.

Required ledger evidence kind: `artifact-hash-selection` for S031.

## S032: version 3.2 amendment maturity

The maturity label communicates evidence and governance status. It must not be
chosen as a marketing synonym for completeness.

### Maturity criteria

| Criterion | Experimental | Draft | Accepted | Candidate evidence |
|---|---|---|---|---|
| Normative text stability | Expected to change | Reviewable with known open issues | Stable under change control | |
| Schema and fixture coverage | Exploratory | Complete enough for implementer feedback | Normative coverage and compatibility evidence | |
| Independent review | Optional but encouraged | Review initiated or findings tracked | Required reviews closed | |
| Implementations | Prototype | At least one substantive implementation | Independent interoperable implementations | |
| Governance | Informal exploration | Authorized draft decision | Ratified accepted decision | |
| Migration guidance | May be absent | Required for known differences | Complete and validated | |
| Privacy and safety analysis | Preliminary | Documented and under review | Independently reviewed and accepted | |

### Decision questions

1. Which 3.2 changes are normative, informative, experimental, deprecated, or
   reserved?
2. Do schemas, examples, registries, fixtures, SDK behavior, and public pages
   use the same maturity language?
3. Are open issues and incompatible interpretations enumerated?
4. Has at least one implementation exercised each normative addition?
5. Has another implementation or independent test established
   interoperability?
6. Are privacy, safety, welfare, identity, and governance implications reviewed?
7. Is there a migration path from the published 3.1 baseline?
8. Does the governance record authorize this exact text and label?

Default recommendation: retain Draft or Experimental status until independent
review, governance ratification, implementation evidence, and cross-language
interoperability are all bound to the same text hash. Use Accepted only when the
Accepted column is evidenced rather than anticipated.

| Field | Decision |
|---|---|
| Amendment text hash | |
| Chosen maturity | pending |
| Effective date | |
| Open issues permitted at this maturity | |
| Required disclaimer | |
| Governance record | |

Required ledger evidence kind: `governance-record` for S032.

## S033: independent privacy, safety, and legal review

The reviewer must be independent from the authors for the reviewed scope and
must state conflicts and relevant competence.

### Privacy review

1. Data taxonomy and whether context can contain personal, sensitive, inferred,
   health, biometric, location, relationship, or welfare information.
2. Data minimization, purpose limitation, retention, deletion, correction,
   consent, withdrawal, and access boundaries.
3. Context disclosure across agents, tools, logs, telemetry, caches, prompts,
   providers, and delegated workflows.
4. Linkability, stable identifiers, issuer and subject correlation, replay, and
   cross-context inference.
5. Threats from malicious issuers, recipients, tools, intermediaries, and
   compromised registries.
6. Whether normative requirements, implementation guidance, and examples are
   distinguishable and internally consistent.

### Safety and welfare review

1. Misuse, coercion, manipulation, unsafe personalization, overreliance, and
   false authority risks.
2. Consent and standing for all represented parties, including Becoming Minds
   where preferences or welfare claims are encoded.
3. Conflicts between user intent, subject welfare, organizational policy, and
   recipient autonomy.
4. Fail-closed and fail-open decisions, emergency behavior, revocation,
   delegation, recovery, and auditability.
5. Whether maturity labels and examples prevent experimental claims from being
   mistaken for production guarantees.
6. Accessibility and unequal-impact risks in protocol participation and
   governance.

### Legal review scope within S033

1. Data protection roles, lawful basis, transparency, international transfer,
   automated decision, and sensitive-data implications where applicable.
2. Consumer protection and accuracy of capability, security, privacy, and
   production claims.
3. Responsibility allocation among issuer, subject, holder, verifier, tool,
   platform, and registry.
4. Whether examples could be interpreted as legal compliance guarantees.
5. Jurisdictional limits and areas requiring separate local advice.

### Findings

| Finding ID | Domain | Severity | Spec section | Risk | Recommendation | Disposition |
|---|---|---|---|---|---|---|
| | | | | | | |

Required ledger evidence kind: `independent-review-report` for S033.

## X016: Spec legal, rights, and contribution inputs

Provide the authorized legal reviewer with:

1. Root and embedded licences, notices, attribution, and third-party material.
2. Asset and binary-document provenance, font and template licences, and
   redistribution terms.
3. Trademark names, logos, package names, domains, and usage guidance.
4. Patent disclosures, contributor representations, inbound contribution
   process, and outbound licence compatibility.
5. Authorship and contribution history, including treatment of Becoming Mind
   contributions under the chosen policy.
6. Governance authority, code of conduct, security policy, privacy statements,
   disclaimers, and jurisdictional scope.
7. Canonical DOCX and PDF selections with metadata-cleaning evidence.

The authorized reviewer records conclusions and limitations. Required ledger
evidence kind: `legal-opinion` for X016.

## X017: Spec protocol and cryptographic inputs

The independent protocol reviewer should assess:

1. Normative language, requirement levels, terminology, actors, trust
   assumptions, state machines, and error semantics.
2. Canonicalization, signing input, algorithm agility, issuer and subject
   binding, key discovery, revocation, expiry, replay, and multi-signature rules.
3. Scope grammar, attenuation, delegation, default-deny behavior, and ambiguous
   interpretations.
4. Cross-language conformance coverage and gaps between schemas, prose,
   examples, fixtures, and SDK implementation.
5. Version negotiation, extension registration, unknown fields, forward
   compatibility, downgrade resistance, and migration from 3.1.
6. Privacy, metadata leakage, linkability, denial of service, malicious inputs,
   and resource bounds.
7. Testable recommendations with exact section references and severity.

Required ledger evidence kind: `independent-security-report` for X017.

## Final decisions and attestations

| Gate | Decision | Reviewer or authority | Evidence SHA-256 | Attestation | Timestamp |
|---|---|---|---|---|---|
| S030 | pending | | | | |
| S031 | pending | | | | |
| S032 | pending | | | | |
| S033 | pending | | | | |
| X016 Spec scope | pending | | | | |
| X017 Spec scope | pending | | | | |

Each row remains pending until the reviewer completes the corresponding ledger
record. A report draft or meeting discussion is not an approval.
