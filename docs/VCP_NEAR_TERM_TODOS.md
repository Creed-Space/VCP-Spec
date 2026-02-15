# VCP Near-Term TODOs

**Last updated**: 2026-02-15

## Package Publishing (BLOCKED: needs design decisions)

Before publishing to any registry, the following must be confirmed:

| Decision | Options | Status |
|----------|---------|--------|
| Package names | `vcp` / `@valuecontextprotocol/sdk` / `rvcp` (mirrors MCP) | Proposed, see `docs/VCP_PACKAGE_NAMING.md` |
| GitHub org | `valuecontextprotocol` (mirrors `modelcontextprotocol`) | Not yet created |
| PyPI account | Who owns `vcp` on PyPI? Need to register | Not checked |
| npm scope | `@valuecontextprotocol` — need npm org | Not created |
| crates.io | `rvcp` — need to check availability | Not checked |
| Versioning | Start at 0.1.0 (pre-1.0 signals prototype) or 1.0.0 (matches spec)? | Undecided |
| Foundation donation | Mirror MCP's donation to Agentic AI Foundation? | Strategic discussion needed |

**Next step**: Nell to confirm naming convention and create `valuecontextprotocol` org on GitHub/npm/crates.io before any publishing.

## Conformance Test Suite

A public conformance test suite is needed for:
- Validating third-party implementations
- Standards body submission evidence
- Adoption strategy (adopters need something to test against)

**Proposed location**: `vcp-sdk/conformance/` with language-agnostic test vectors (JSON fixtures + expected results).

## VCP-Spec README Badges

Once CI passes on published packages:
- PyPI version badge
- npm version badge
- crates.io version badge
- Docs badge (link to generated API docs)
