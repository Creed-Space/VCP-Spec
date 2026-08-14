# VCP Package Identifier Decision Record

<!-- vcp-document-control
status: Unratified decision record
normative-authority: None
protocol-version: Independent of protocol version
last-reviewed: 2026-08-13 status and authority classification
owner: VCP release authority
evidence-boundary: Candidate identifiers only
-->

| Field | Value |
|:---|:---|
| Status | Unratified, publication-blocking decision record |
| Normative authority | None |
| Protocol baseline | Independent of protocol version |
| Last reviewed | 2026-08-13 |
| Owner | VCP release authority |
| Evidence boundary | Candidate metadata only. This page does not grant ownership or availability. |

## Present rule

No registry name is approved for public installation instructions. The machine
[publication-state record](../status/publication-state.json) therefore permits
source installs only. Existing package metadata identifiers are review
candidates and may change before the first public release.

The former proposal to publish Python as `vcp` is withdrawn. That PyPI name is
already associated with an unrelated project, so directing users to it would be
unsafe. The former assumption that mirroring MCP names proves ownership or
standards equivalence is also withdrawn.

## Candidate identifiers under review

| Surface | Repository metadata | Registry claim |
|:---|:---|:---|
| Python distribution | `value-context-protocol` | Unverified and unratified |
| Python import | `vcp` | Local import namespace, not a registry claim |
| WebMCP npm package | `@creed-space/vcp-sdk` | Unverified and unratified |
| Rust library | `vcp-core` | Local crate identifier, not a registry claim |
| Rust CLI | `vcp-cli` | Local binary and crate identifier, not a registry claim |
| Rust WASM | `vcp-wasm` | Local package identifier, not a registry claim |

## Ratification checks

Before any name becomes public guidance, release authority records:

1. registry availability and existing ownership;
2. confusingly similar projects and dependency-confusion risk;
3. trademark and descriptive-use review;
4. organization, maintainer, recovery-contact, and mandatory 2FA ownership;
5. import, package, binary, and documentation consistency;
6. protocol compatibility and semver policy;
7. trusted-publishing workflow identity;
8. recovery, deprecation, transfer, and yanking procedures;
9. first-release approval and immutable publication receipt.

## Source-only installation

Select a reviewed VCP-SDK commit, check it out exactly, and run commands from
that checkout:

```bash
git checkout --detach <reviewed-vcp-sdk-commit>
python -m pip install ./python
npm install ./webmcp
cargo build --manifest-path ./rust/Cargo.toml -p vcp-core
```

Moving branch URLs are excluded from release evidence.
