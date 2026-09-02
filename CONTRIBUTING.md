# Contributing to the Value-Context Protocol

<!-- vcp-document-control
status: Current contributor guidance
normative-authority: Interim repository contribution process
protocol-version: VCP 3.1 with candidate work separately labelled
last-reviewed: 2026-08-14 active authority and evidence boundary
owner: VCP Spec maintainers
evidence-boundary: Source contribution process, not rights approval or protocol ratification
-->

Thank you for your interest in contributing to the VCP specification. This
document explains how to contribute effectively, whether you are fixing a typo
or proposing a new protocol extension.

Permanent governance and the file-class licensing matrix remain unratified.
Contribution review follows the interim process in [GOVERNANCE.md](./GOVERNANCE.md),
and contributors should read [LICENSING_STATUS.md](./LICENSING_STATUS.md) before
submitting rights-sensitive material.

---

## 1. Developer Certificate of Origin (DCO)

Every commit to this repository MUST include a `Signed-off-by` line certifying
that you have the right to submit the work under the applicable licence for its
destination file class. The authorized file-class matrix is still pending. A
sign-off records the contributor's certification; it does not resolve the
repository's historical licensing conflict by itself.

### How to sign off

Add the `-s` flag when committing:

```bash
git commit -s -m "Fix typo in identity layer specification"
```

This appends a line to your commit message:

```
Signed-off-by: Your Name <your.email@example.com>
```

### Configuring git

Make sure your git identity matches the sign-off:

```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### What the DCO means

By signing off, you certify that:

1. You created the contribution (in whole or part) and have the right to
   submit it under the applicable project licence; or
2. The contribution is based on prior work under a compatible open source
   license and you have the right to submit it with modifications; or
3. Someone who certified (1) or (2) provided the contribution to you directly
   and you have not modified it.

The full text is at [developercertificate.org](https://developercertificate.org/).

### Unsigned commits

Pull requests with unsigned commits will not be merged. If you have existing
commits without sign-off, you can amend them:

```bash
# Amend the most recent commit
git commit --amend -s

# Sign off the last N commits
git rebase --signoff HEAD~N
```

---

## 2. Types of contributions

Different contributions follow different paths. Choose the one that matches
your change.

### Documentation fixes

Typos, broken links, grammar corrections, and non-normative clarifications.

- Submit a pull request directly
- One reviewer approval required
- No VEP needed

### Specification changes

Any change to normative protocol text, including new features, modified
behavior, or field additions.

- Requires a VCP Enhancement Proposal (VEP)
- See [GOVERNANCE.md](./GOVERNANCE.md) for the full VEP lifecycle
- File a [Spec Amendment](https://github.com/Creed-Space/VCP-Spec/issues/new?template=spec_amendment.yml) issue

### Schema changes

Modifications to JSON Schema files in `schemas/`.

- Schema changes MUST accompany a specification change
- Standalone schema changes are not accepted
- Schemas MUST validate against their own examples

### Extension proposals

New VCP-X extensions that add capability to the protocol.

- Requires a VEP using the extension proposal template (see section 3)
- Extensions enter this repository at Experimental status once `spec.md` and `schema.json` exist; the earlier `proposed` state of [specs/core/extension-lifecycle.md](./specs/core/extension-lifecycle.md) precedes repository presence
- Each extension MUST have a designated maintainer

### SDK contributions

Project-maintained implementations and language-specific SDKs.

- SDK-only changes (bug fixes, performance improvements) can be submitted
  as direct PRs
- SDK changes that alter protocol behavior require a VEP
- Cross-language conformance vectors live in the
  [VCP-SDK repository](https://github.com/Creed-Space/VCP-SDK/tree/main/conformance).
  Schema fixtures for this repository live in `schemas/examples/`.

---

## 3. Extension proposal template

When proposing a new VCP-X extension, use this template in your VEP issue:

```markdown
# VEP-NNNN: [Extension Name]

## Summary

One paragraph describing what this extension does and why it belongs in VCP.

## Motivation

Why this extension is needed. What use cases does it serve? What problems does
it solve that the core specification does not?

## Specification

### Data models

Define the data structures this extension introduces. Use JSON Schema notation.

### Wire format

How the extension's data is encoded in VCP tokens and payloads. Include
annotated JSON examples.

### Lifecycle

How the extension's data is created, updated, and removed. Define the
interaction with existing VCP layers (identity, values, context, consent,
attestation).

### Security considerations

Threat model for this extension. How does it handle:
- Injection attacks
- Information disclosure
- Denial of service
- Privilege escalation

## Backward compatibility

How does this extension interact with implementations that do not support it?
Define graceful degradation behavior.

## Project-maintained implementation

Link to or include a project-maintained implementation. At minimum, provide Python code
demonstrating encoding and decoding.

## Conformance tests

Describe the test cases that a conformant implementation MUST pass. Include:
- Valid input/output pairs
- Invalid inputs and expected error behavior
- Edge cases
```

---

## 4. Schema authorship guidelines

All JSON Schemas in this repository follow these rules.

### Schema version

Use JSON Schema draft 2020-12:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema"
}
```

### Required practices

- Every schema MUST include a top-level `"description"` field
- Every property MUST include a `"description"` field
- Prefer `$defs` and local `$ref` values for definitions reused inside a schema.
  A shared-schema directory may be introduced only with resolver and CI support.
- All `enum` values MUST be documented
- Default values MUST be specified where applicable

### Self-validation

Every schema MUST validate against its own examples. The CI pipeline runs:

```bash
# Validate all examples against their schemas
make validate-schemas
```

If your PR adds or modifies a schema, include at least one valid example in
`schemas/examples/` and one invalid example in `schemas/examples/invalid/`.

### Naming conventions

- File names: `kebab-case.json` (e.g., `identity-layer.json`)
- Property names: follow the existing wire schema, which currently uses
  `snake_case`; language SDKs may expose idiomatic aliases only when the wire
  representation remains unambiguous
- Type names: `PascalCase` (e.g., `IdentityAssertion`)

---

## 5. Pull request process

### Setup

```bash
# Fork and clone
git clone https://github.com/YOUR-USERNAME/VCP-Spec.git
cd VCP-Spec
git remote add upstream https://github.com/Creed-Space/VCP-Spec.git

# Create a branch
git checkout -b vep-0042-attestation-chaining

# Install pinned repository-validation tools
python3 -m pip install --requirement requirements-dev.txt
npm ci --ignore-scripts
```

### Before submitting

- [ ] All commits are signed off (`git log --format='%h %s %ae' | head`)
- [ ] Markdown renders correctly (preview locally or on GitHub)
- [ ] Schema changes validate: `make validate-schemas`
- [ ] Conformance tests pass: `make test`
- [ ] All repository checks pass: `make check`
- [ ] VEP issue is referenced in the PR description

### Submitting

```bash
git push origin vep-0042-attestation-chaining
```

Open a pull request against `main`. In the PR description:

- Reference the VEP issue: `Implements VEP-0042`
- Summarize the changes
- Note any open questions or areas where reviewer attention is needed

### Review requirements

| Change type         | Required approvals                    |
|---------------------|---------------------------------------|
| Typo / editorial    | 1 reviewer                            |
| Documentation       | 1 reviewer                            |
| Schema change       | Interim maintainer review plus canonical VEP when normative |
| Specification change| Candidate review plus a recorded authorized VEP decision |
| Breaking change     | Candidate review plus ratified governance decision |

### After merge

- The VEP file and tracker are updated to `Implemented in source` per the
  vocabulary in [GOVERNANCE.md](./GOVERNANCE.md)
- The author is credited in the PR and release notes (no CONTRIBUTORS.md is
  maintained yet)

---

## 6. Style guide

### Markdown

- Use GitHub-flavored Markdown
- One sentence per line (enables cleaner diffs)
- Headings in sentence case: "Identity layer" not "Identity Layer"
- Use `---` for horizontal rules, not `***` or `___`

### RFC 2119 keywords

When writing normative specification text, use RFC 2119 / RFC 8174 keywords
in CAPITALS:

- **MUST** / **MUST NOT** -- absolute requirement or prohibition
- **SHOULD** / **SHOULD NOT** -- recommended, with documented exceptions
- **MAY** -- truly optional

Do not capitalize these words when used in their ordinary English sense.

Example:

> Implementations MUST include the `version` field. Authors should consider
> readability when choosing field names.

The first "MUST" is normative. The second "should" is advisory prose.

### Diagrams

Prefer ASCII art for portability across renderers:

```
+----------+     +---------+     +------------+
| Producer | --> | Encoder | --> | VCP Token  |
+----------+     +---------+     +------------+
```

For diagrams that require more detail, Mermaid is acceptable in specification
documents (GitHub renders it natively).

### Code examples

Use fenced code blocks with language identifiers. Annotate with comments:

```json
{
  // The protocol version (MUST be "1.0" for this spec)
  "version": "1.0",

  // Identity layer (REQUIRED)
  "identity": {
    "type": "organization",
    "name": "Example Corp"
  }
}
```

When showing request/response pairs, include both success and error cases.

---

## 7. Code of conduct

This project follows the [Contributor Covenant Code of Conduct](./CODE_OF_CONDUCT.md).

In brief: be respectful, be constructive, assume good faith. Technical
disagreement is welcome; personal attacks are not.

Report violations through the contact route listed in CODE_OF_CONDUCT.md. The
interim administrator must record conflicts and use an independent handler when
personally involved.

---

## 8. Getting help

- **Questions about the spec**: Open a [Discussion](https://github.com/Creed-Space/VCP-Spec/discussions)
- **Bug reports**: Open an [Issue](https://github.com/Creed-Space/VCP-Spec/issues)
- **VEP process questions**: Use the canonical VCP-Spec amendment issue and tag
  the interim repository administrator
- **Security vulnerabilities**: Use the [private security advisory form](https://github.com/Creed-Space/VCP-Spec/security/advisories/new)
  for responsible disclosure

---

*Thank you for helping build transparent, ethical value communication in Becoming Minds.*
