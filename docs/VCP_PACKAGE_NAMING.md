# VCP Package Identifier Decision Record

<!-- vcp-document-control
status: Ratified decision record
normative-authority: None
protocol-version: Independent of protocol version
last-reviewed: 2026-09-24 publication status
owner: VCP release authority
evidence-boundary: Ratified identifiers; registry receipts in publication-state
-->

| Field | Value |
|:---|:---|
| Status | Ratified decision record; names ratified 3 September 2026 (VCP-SDK #97) and published at 4.2.0 |
| Normative authority | None |
| Protocol baseline | Independent of protocol version |
| Last reviewed | 2026-09-24 |
| Owner | VCP release authority |
| Evidence boundary | Ratified identifiers. Registry receipts live in the publication-state record; this page does not grant ownership. |

## Present rule

The names below were ratified on 3 September 2026 and published at 4.2.0. The
machine [publication-state record](../status/publication-state.json) records a
registry receipt for each artifact and permits registry install commands:

```bash
python -m pip install value-context-protocol==4.2.0
npm install @creedspace/vcp-sdk@4.2.0
cargo add vcp-core@4.2.0
```

The former proposal to publish Python as `vcp` is withdrawn. That PyPI name is
already associated with an unrelated project, so directing users to it would be
unsafe. The former assumption that mirroring MCP names proves ownership or
standards equivalence is also withdrawn.

## Ratified identifiers

| Surface | Repository metadata | Registry claim |
|:---|:---|:---|
| Python distribution | `value-context-protocol` | PyPI, published 4.2.0 |
| Python import | `vcp` | Import namespace, not a registry name |
| WebMCP npm package | `@creedspace/vcp-sdk` | npm, published 4.2.0 |
| Rust library | `vcp-core` | crates.io, published 4.2.0 |
| Rust CLI | `vcp-cli` | crates.io, published 4.2.0 |
| Rust WASM | `vcp-wasm` | crates.io, published 4.2.0; the generated WebAssembly package is not on npm |

## Ratification checks

Before a new or changed name becomes public guidance, release authority records
the checks below. For the ratified 4.2.0 names, registry ownership, account
recovery, and trusted-publishing provenance remain open to the closure standard
(VCP-RISK-005 in [`status/residual-risks.json`](../status/residual-risks.json)).

1. registry availability and existing ownership;
2. confusingly similar projects and dependency-confusion risk;
3. trademark and descriptive-use review;
4. organization, maintainer, recovery-contact, and mandatory 2FA ownership;
5. import, package, binary, and documentation consistency;
6. protocol compatibility and semver policy;
7. trusted-publishing workflow identity;
8. recovery, deprecation, transfer, and yanking procedures;
9. first-release approval and immutable publication receipt.

## Source installation (alternative)

To build from source instead, check out the published tag in a VCP-SDK clone
and run these commands from that checkout:

```bash
git checkout --detach v4.2.0
python -m pip install ./python
npm install ./webmcp
cargo build --manifest-path ./rust/Cargo.toml -p vcp-core
```

Moving branch URLs are excluded from release evidence.
