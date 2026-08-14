# Artifact Canonicality and Provenance

<!-- vcp-document-control
status: Current artifact-classification policy
normative-authority: Repository artifact ownership policy
protocol-version: VCP 3.1 baseline and candidate materials
last-reviewed: 2026-08-14 active authority and evidence boundary
owner: VCP Spec maintainers
evidence-boundary: Canonicality and packaging classification, not publication authority
-->

## Normative sources

Markdown under `specs/`, JSON under `schemas/`, and each extension's `spec.md`
and `schema.json` are reviewable source artifacts. Schema changes must include
fixtures and pass `make check`. Where prose and schema disagree, the conflict is
a release blocker rather than an implicit precedence rule.

## Generated and copied material

The root DOCX files are editorial working artifacts. None is declared the
publication-canonical rendering. Their internal DOCX package integrity is
machine-checked, while their layout, accessibility, rights, and publication
fitness require human review. The current files are:

| File | Bytes | SHA-256 |
|:---|---:|:---|
| `VCP_MDPI_Clone.docx` | 1,660,107 | `a9f6cb65128d90b5f0c80d1cfb407225693cec1bca8c30c2a2a4b6cbb0d62ca6` |
| `VCP_MDPI_Pure.docx` | 1,744,247 | `6a61cec873b41f70bd288ac7b17287dac6d8f8efe7cfeeda16aa267ceb6bb1b4` |
| `VCP_MDPI_Surgical.docx` | 1,674,361 | `de03e84704cd6d68ab02dd286ca446a5a0f522579905581014d1d6aa50cdf4e4` |
| `Value Context Protocol - Clean.docx` | 49,449 | `88bc28a3a68bc1c6043f6e9e0e2221f6b7ce705f91dee09b998379366aa442c2` |
| `Value Context Protocol MDPI - Styled.docx` | 1,645,120 | `76b90d4247b5d875ebbdd7680d4118ce9f6ae327a28d72fb5dbf5e5c16afbded` |
| `Value Context Protocol MDPI I2D2.docx` | 1,737,317 | `4c7df5b6b8212261e9dec2c8a9b8732878839a5ec132320da2bb92a6a12c821f` |
| `Value Context Protocol MDPI I2D3.docx` | 1,673,908 | `2850fd5053ddbdc4b1b9864099a0e3840b9b3c724c0b03ad5df941aa35e6e4e8` |

Historical Markdown remains useful evidence of protocol evolution. It must keep
its version in the filename or heading and must not be silently synchronized to
newer normative behavior.

## Update rule

Edit canonical sources first, update schemas and fixtures in the same change,
then regenerate any selected publication artifact. Record the source commit and
rendering tool in the release evidence. Do not hand-edit a generated copy and
present it as synchronized source.
