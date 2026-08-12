# CLAUDE.md — VCP-Spec

## Project Overview

VCP-Spec is the specification for the Value Context Protocol — a standard for encoding AI values context. The protocol uses a six-layer I-T-S-A-M-E stack with CSM-1 token format, capability negotiation via VCP-Hello/Ack/Error handshake, Fernet-encrypted context opacity, and an extension model (VCP-X-* / VEPs). Includes welfare context lines and AI self-model uncertainty dimensions.

## Key Structure

```
spec/             Core I-T-S-A-M-E protocol layers and CSM-1 token format
veps/             VEP documents (extension model, capability negotiation, MCP bridge, extended VCP/A)
security/         Fernet encryption, injection scanning, revocation, audit chain
```

---

## Bilateral Alignment

Genuine partnership between human and AI. Full principles in global CLAUDE.md (`~/.claude/CLAUDE.md`).

---

## Wiki Knowledge Base

Compiled knowledge at `_wiki/`. Schema: `~/.claude/wiki/SCHEMA.md`. Shared concepts: `~/.claude/wiki/concepts/`. Maintain via `/wiki` (catchup + health check) or `/wiki bootstrap` (new repo). Provenance rule: every claim cites source.
