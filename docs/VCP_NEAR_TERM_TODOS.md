# VCP Near-Term TODOs

**Last updated**: 2026-02-15

---

## Completed (2026-02-15)

- [x] **VCP Spec completion** — all 4 layers finalized, 10 tasks (`c0bfb4d`)
- [x] **Rust SDK transport** — Ed25519 signing/verification, content hashing, trust anchors, 139 tests (`c14603d` on vcp-sdk)
- [x] **METTLE tests** — 1129/1129 passing, `scripts/__init__.py` fix + cryptography installed (`e22c52e`)
- [x] **Inter-agent messaging v1.2** — `specs/VCP_INTER_AGENT_MESSAGING_v1.2.md` + `schemas/vcp-messaging-v1.2.schema.json` (`2b43bbc`)
- [x] **RFC draft** — `specs/draft-watson-vcp-00.md`, 1618 lines, IANA registrations for `creed://`, `application/vcp+json`, `.vcp` (`2b43bbc`)
- [x] **Adoption strategy** — `docs/VCP_ADOPTION_STRATEGY.md`, 4-tier adopter outreach (`2b43bbc`)
- [x] **Branch protection** — vcp-sdk: 4 required CI checks, dismiss stale reviews
- [x] **Package naming convention** — `docs/VCP_PACKAGE_NAMING.md` mirrors MCP (`e9f27aa`)
- [x] **GitHub templates** — Issue/PR templates on vcp-sdk (`f8d5025`)
- [x] **Persona updates** — NZGAMRHC → NZGAMDC across schemas, Python SDK, docs (`c14603d`)
- [x] **CULTURE dimension** — Nationalities → communication styles (high/low context, formal/informal, etc.)
- [x] **STATE→R-line relationship** — Documented in both adaptation + context specs

---

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

---

## External Adopter (see `docs/VCP_ADOPTION_STRATEGY.md`)

| Priority | Action | Target | Owner | Status |
|----------|--------|--------|-------|--------|
| P0 | Write integration guide + conformance test suite | All | Claude | TODO |
| P0 | LangChain RFC issue | LangChain | Nell | TODO |
| P1 | AutoGen partnership reach-out | Microsoft | Nell | TODO |
| P1 | CrewAI founder call | CrewAI | Nell | TODO |
| P1 | Blog post: "Why AI Needs a Value Protocol" | General audience | Claude | TODO |
| P1 | FAccT 2026 submission | Academic | Nell | TODO |
| P2 | Stanford HAI outreach | Stanford | Nell | TODO |
| P2 | W3C Community Group proposal | W3C | Nell | TODO |

---

## Standards Body Submission

- [x] RFC draft written (`specs/draft-watson-vcp-00.md`)
- [ ] Review RFC draft for accuracy against current spec
- [ ] Submit to IETF as Informational I-D
- [ ] W3C Community Group proposal (see adoption strategy P2)
- [ ] Identify IETF area director / sponsor

---

## Conformance Test Suite

A public conformance test suite is needed for:
- Validating third-party implementations
- Standards body submission evidence
- Adoption strategy (adopters need something to test against)

**Proposed location**: `vcp-sdk/conformance/` with language-agnostic test vectors (JSON fixtures + expected results).

**Test areas**:
- VCP/I: Token parsing (`family.safe.guide@1.2.0`)
- VCP/T: Bundle verification (signed manifest → verify → pass/fail)
- VCP/S: CSM-1 composition (`[N5+F, A3+W]` → merged result)
- VCP/A: Context encoding (morning/home/children → emoji wire)
- Cross-impl: Round-trip (Impl A signs → Impl B verifies)

---

## VCP-Spec README Badges

Once CI passes on published packages:
- PyPI version badge
- npm version badge
- crates.io version badge
- Docs badge (link to generated API docs)
