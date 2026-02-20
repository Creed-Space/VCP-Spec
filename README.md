<div align="center">

# Value-Context Protocol (VCP) Specification

**The open standard for portable, adaptive, and verifiable AI context.**

[![Specification](https://img.shields.io/badge/spec-v1.1-blue?style=flat-square)](./specs/VCP_SPECIFICATION_v1.0.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](./LICENSE)

[Overview](#overview) | [Quick Start](#quick-start) | [Specification](#specification) | [Schemas](#schemas) | [Contributing](#contributing) | [SDKs](#sdks)

</div>

---

## Overview

The **Value-Context Protocol (VCP)** is an open specification for transporting constitutional values, behavioral rules, and personal context to AI systems. It addresses a structural gap in how Large Language Models receive instructions: they accept text input but have no native ability to resolve references, verify signatures, or validate hashes.

VCP provides a **signed envelope format** that enables cryptographic verification at the orchestration layer while delivering complete, self-contained text to the model.

### Core Properties

| Property | Description |
|:---|:---|
| **Portability** | Define your context once -- every compatible service receives it automatically |
| **Adaptation** | Context profiles shift by situation: work mode at the office, personal mode at home |
| **Liveness** | Real-time personal state (energy, focus, urgency) modulates AI responses moment-to-moment |
| **Verification** | Cryptographic signatures and content hashes ensure integrity and provenance |
| **Privacy** | Share *influence* without sharing *information* |

---

## Quick Start

New to VCP? Start here:

1. **[Newcomer Guide](./docs/VCP_NEWCOMER_GUIDE.md)** -- What VCP is and why it exists
2. **[Overview](./docs/VCP_OVERVIEW.md)** -- Technical overview of the protocol
3. **[Full Specification](./specs/VCP_SPECIFICATION_v1.0.md)** -- Complete v1.0 spec

---

## Specification

### Protocol Stack

VCP is a four-layer protocol stack:

```
Layer 4 -- VCP/A  ADAPTATION     WHEN and HOW constitutions apply
Layer 3 -- VCP/S  SEMANTICS      WHAT the values mean
Layer 2 -- VCP/T  TRANSPORT      HOW values travel securely
Layer 1 -- VCP/I  IDENTITY       WHO and WHAT is being addressed
```

### Documents

| Document | Description |
|:---|:---|
| [VCP Specification v1.0](./specs/VCP_SPECIFICATION_v1.0.md) | Full protocol specification |
| [VCP v1.1 Amendments](./specs/VCP_SPECIFICATION_v1.1_AMENDMENTS.md) | R-line, personal state additions |
| [Academic Paper](./specs/value_context_protocols_paper_v1.md) | Formal paper |

### By Layer

| Layer | Documentation |
|:---|:---|
| VCP/I -- Identity | [Naming](./docs/identity/VCP_IDENTITY_NAMING.md), [Namespace](./docs/identity/VCP_IDENTITY_NAMESPACE.md), [Encoding](./docs/identity/VCP_IDENTITY_ENCODING.md), [Ontology](./docs/identity/VCP_IDENTITY_ONTOLOGY.md), [Registry](./docs/identity/VCP_IDENTITY_REGISTRY.md) |
| VCP/T -- Transport | [Specification](./specs/VCP_SPECIFICATION_v1.0.md) SS6 |
| VCP/S -- Semantics | [CSM-1 Grammar](./docs/content/CSM1_GRAMMAR_SPECIFICATION.md), [CSM-1 v1.1](./docs/content/CSM1_v1.1_AMENDMENT.md), [Composition](./docs/semantics/VCP_SEMANTICS_COMPOSITION.md), [Persona Profiles](./docs/semantics/VCP_PERSONA_PROFILES.md) |
| VCP/A -- Adaptation | [Adaptation](./docs/adaptation/VCP_ADAPTATION.md), [Context](./docs/context/VCP_CONTEXT_SPECIFICATION.md), [State Machine](./docs/adaptation/VCP_STATE_MACHINE.md), [Hooks](./docs/adaptation/VCP_HOOKS.md) |

### Specification Status

| Layer | Status | Documents |
|:---|:---|:---|
| VCP/I -- Identity | Stable | 5 docs |
| VCP/T -- Transport | Stable | 1 spec + 1 amendment |
| VCP/S -- Semantics | Stable | 4 docs |
| VCP/A -- Adaptation | Stable (messaging: Preview) | 4 docs |

### Universal Value Codes (UVC)

| Document | Description |
|:---|:---|
| [Naming](./docs/uvc/UVC_NAMING_SPECIFICATION.md) | UVC naming conventions |
| [Encoding](./docs/uvc/UVC_ENCODING_FORMATS.md) | Encoding formats |
| [Ontology](./docs/uvc/UVC_VALUE_ONTOLOGY.md) | Value classification |
| [Registry](./docs/uvc/UVC_REGISTRY_PROTOCOL.md) | Registry protocol |
| [Governance](./docs/uvc/UVC_NAMESPACE_GOVERNANCE.md) | Namespace governance |

---

## Schemas

JSON Schema definitions for validating VCP structures:

| Schema | Validates |
|:---|:---|
| [vcp-manifest-v1](./schemas/vcp-manifest-v1.schema.json) | Signed bundle manifests |
| [vcp-identity-token](./schemas/vcp-identity-token.schema.json) | Identity tokens |
| [vcp-semantics-csm1](./schemas/vcp-semantics-csm1.schema.json) | CSM-1 compact tokens |
| [vcp-adaptation-context](./schemas/vcp-adaptation-context.schema.json) | Adaptation context |

---

## SDKs

Reference implementations live in the [VCP-SDK repository](https://github.com/Creed-Space/vcp-sdk):

| Language | Status | Purpose |
|:---|:---|:---|
| **Python** | Stable | Reference implementation |
| **Rust** | Beta | High-performance / WASM |
| **TypeScript** | Beta | Browser-side (WebMCP) |

---

## Contributing

We welcome contributions to the specification and documentation.

- **Typo / Clarification**: Open a PR directly
- **Spec Change**: Follow the [VEP process](./GOVERNANCE.md) via a [Spec Amendment issue](https://github.com/Creed-Space/VCP-Spec/issues/new?template=spec_amendment.yml)

See [CONTRIBUTING.md](./CONTRIBUTING.md) for details and [GOVERNANCE.md](./GOVERNANCE.md) for the change approval process.

Please read our [Code of Conduct](./CODE_OF_CONDUCT.md) before participating.

---

## License

This project is licensed under the [MIT License](./LICENSE).

---

## Authors

Nell Watson, Elena Ajayi, Filip Alimpić, Awwab Mahdi, Blake Wells, Claude (Anthropic)

A **[Creed Space](https://creedspace.com)** project.

---

<div align="center">

*Context that travels with you.*

[Website](https://www.valuecontextprotocol.org) | [SDK](https://github.com/Creed-Space/vcp-sdk) | [Playground](https://www.valuecontextprotocol.org/playground)

</div>
