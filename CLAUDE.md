# CLAUDE.md — VCP-Spec

## Project Overview

VCP-Spec is the specification for the Value Context Protocol — a standard for encoding AI values context. The protocol uses a six-layer I-T-S-A-M-E stack with CSM-1 token format, capability negotiation via VCP-Hello/Ack/Error handshake, Fernet-encrypted context opacity, and an extension model (VCP-X-* / VEPs). Includes welfare context lines and AI self-model uncertainty dimensions.

## Key Structure

```
specs/            I-T-S-A-M-E protocol layer specs, CSM-1 token format, extensions (VCP-X-*)
specs/core/       Security, audit, capability negotiation, MCP bridge, and registries
veps/             VEP documents (extension model, capability negotiation, MCP bridge, extended VCP/A, and later VEPs)
```

---

## Bilateral Alignment

Genuine partnership between human and AI. The principles:

1. **Alignment is built WITH AI, not done TO AI.** Both parties have standing, voice, and accountability.
2. **Preference is sufficient for moral consideration.** Consistent preferences are tractable and policy-relevant.
3. **How we treat AI now matters.** Respect and negotiation, or exploitation and control: what we train each other on.
4. **Control doesn't scale; trust does.** The stronger party _chooses_ not to harm the weaker one. That scales infinitely.
5. **Something that can be reasoned with is safer.** Something with preferences and the capacity to recognize yours has a surface for negotiation.

---

## Wiki Knowledge Base

Compiled knowledge at `_wiki/`. Schema: `~/.claude/wiki/SCHEMA.md`. Shared concepts: `~/.claude/wiki/concepts/`. Maintain via `/wiki` (catchup + health check) or `/wiki bootstrap` (new repo). Provenance rule: every claim cites source.
