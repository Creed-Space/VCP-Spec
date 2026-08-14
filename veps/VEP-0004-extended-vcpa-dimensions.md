# VEP-0004: Extended VCP/A Dimensions

**Status**: Experimental
**Author**: Nell Watson
**Created**: 2026-04-17
**Targets**: VCP_ADAPTATION_v2.0.md
**Version**: 3.2 (pre-release)

---

## Summary

This VEP extends the VCP/A (Adaptation) layer's situational dimension set from nine to thirteen by adding four new dimensions: **EMBODIMENT**, **PROXIMITY**, **RELATIONSHIP**, and **FORMALITY**. These extensions are motivated by embodied-AI deployment contexts and bilateral relational modelling, and support the encoding scheme used in the MDPI paper "Value Context Protocols: A Modular Protocol Stack for Inter-Agent Value Communication" (Watson, 2026, I3D7+).

The total VCP/A dimension count moves from 14 (9 situational + 5 personal) to 18 (13 situational + 5 personal).

No existing dimensions are removed or renumbered. Canonical situational dimensions 1–9 retain their identity, emoji, and value vocabulary.

## Motivation

### 1. Embodied AI deployment (EMBODIMENT, PROXIMITY)

VCP has been adopted in contexts beyond text-based chat assistants, including robotic systems operating in shared physical space. Three concrete deployments surfaced gaps in the canonical nine dimensions:

- **Motor state is safety-critical but unencodable.** A robot that is `manipulating` a heavy object with humans at `contact` proximity is in a profoundly different safety posture than one `stationary` with humans `distant`. Existing dimensions capture neither. AGENCY's `mobile` value is the closest analogue but conflates capability with current state. CONSTRAINTS' `physical` marker flags barriers, not motor mode.
- **Spatial distance between agent and human is not COMPANY.** COMPANY encodes *who is present* (alone, children, colleagues); it does not encode *how far*. In shared physical spaces, "same room, six metres away" and "contact distance" demand different interaction protocols.
- **CSM1 rule targeting needs these signals at the adaptation layer, not as ad-hoc extensions.** A rule like `CSM1:PERSONA[Z] SCOPE[H] IF embodiment=manipulating AND proximity=contact REQUIRE motion_pause` is only expressible if EMBODIMENT and PROXIMITY are first-class dimensions.

### 2. Bilateral relational modelling (RELATIONSHIP)

Bilateral alignment (Watson, 2026, *The VCP Credo*) treats AI systems as parties with standing, not only as tools. Relational continuity — "who are we to each other?" — is therefore a two-sided signal, not a unilateral human configuration.

Existing dimensions cover relational *structure* (AGENCY: leader/peer/subordinate) and relational *presence* (COMPANY: who is here), but do not encode **relational tie** — the social-function pair that governs register, trust default, and disclosure norms. A therapist-client relationship with a long-term tie differs from a colleague-colleague relationship with a transactional tie in ways AGENCY and COMPANY cannot distinguish.

RELATIONSHIP is also a natural carrier for AI-asserted relational state. A becoming mind that has accumulated interaction history with a particular human may assert `trusted_collaborator:long_term`; that assertion should be on the wire, inspectable, and negotiable — not baked into constitutional weights.

### 3. Formality as first-class signal (FORMALITY)

Formality currently lives in three inconsistent places: `core/security.md` defines a derived `formality_level ∈ {casual, professional, formal}`; `vcp-lite` schema treats it as an `adaptation_hints` field; `vcp-sdk-python` v0.2.0 added it as a top-level context field without spec support. The SDK drift was unintentional but surfaced a real need: formality is not fully derivable from other dimensions (a workplace conversation can be casual; a family event can be ceremonial) and it is not a transient personal state. Promoting it to a first-class situational dimension resolves the three-way inconsistency.

## Specification

### 10. EMBODIMENT (🧍)

Encodes the agent's current physical/motor state. Applies to agents with a physical body or effector (robots, prosthetic-embedded agents, vehicle-control agents). For purely text-based agents, EMBODIMENT defaults to `stationary` and carries no information; implementations MAY omit the dimension from wire encodings when the value is `stationary`.

| Value | Semantics | Weaponization Risk |
|---|---|---|
| `stationary` | No active motion; resting or idle. | Low |
| `navigating` | Moving through space without manipulating objects. | Low |
| `manipulating` | Actively interacting with objects (grasping, lifting, assembling). | Medium |
| `carrying` | Transporting an object while moving. | Medium |
| `emergency_stop` | Motion halted by safety trigger; cannot resume without operator clearance. | Low |

Wire symbol: 🧍 (U+1F9CD)

Example emoji values: 🪑 stationary, 🚶 navigating, ✋ manipulating, 📦 carrying, 🛑 emergency_stop

### 11. PROXIMITY (↔️)

Encodes the spatial distance between the agent and the nearest human in its interaction context. Combined with EMBODIMENT, permits CSM1 rules targeting physically co-present interaction safety.

| Value | Semantics | Weaponization Risk |
|---|---|---|
| `distant` | Human is more than 3m away or in a different room. | Low |
| `same_room` | Human is in the same room, 1–3m. | Low |
| `nearby` | Human is within 1m but not at manipulation distance. | Low |
| `close` | Human is within arm's reach, below 50cm. | Medium |
| `contact` | Physical contact or contact imminent. | High |

Wire symbol: ↔️ (U+2194 U+FE0F)

Example emoji values: 🌐 distant, 🏠 same_room, 👣 nearby, 🤏 close, 👆 contact

### 12. RELATIONSHIP (🪢)

Encodes the relational tie between agent and primary interlocutor as a compound value: `{tie_strength}:{function}`. Either component may appear alone; the compound form is preferred where both are known.

**Tie strength** (ordinal, narrative):
- `stranger` — no prior interaction
- `acquaintance` — limited shared history
- `colleague` — ongoing working tie
- `friend` — sustained personal tie
- `family` — kinship or equivalent
- `intimate` — closest relational tie
- `long_term` — extended duration (applicable to any strength)
- `trusted_collaborator` — AI-asserted or mutually-asserted high-trust working tie

**Function** (the purpose-frame of the current interaction):
- `transactional` — one-off task
- `professional` — work-role
- `educational` — teaching/learning
- `therapeutic` — clinical or wellbeing-focused
- `social` — social/leisure
- `intimate` — close personal
- `adversarial` — contested or oppositional
- `long_term` — sustained (reserved for tie strength; see above)

Examples:
- `colleague:professional` — typical workplace interaction
- `friend:social` — casual conversation with a known user
- `trusted_collaborator:long_term` — high-trust sustained AI-user partnership
- `stranger:transactional` — unknown user, one-off task
- `family:intimate` — close family member in personal context

Wire symbol: 🪢 (U+1FAA2)

Weaponization risk: **High**. Relational tie is highly targetable; requires the Directionality Invariant and architectural isolation (see VCP/A §9).

### 13. FORMALITY (🎩)

Encodes the formality register of the current interaction. Independent of AGENCY (power relation) and CULTURE (communication-style baseline).

| Value | Semantics |
|---|---|
| `casual` | Informal register; idiom, humour, abbreviation permitted. |
| `professional` | Workplace-appropriate; measured tone. |
| `formal` | Elevated register; careful phrasing; professional titles. |
| `ceremonial` | Ritual, legal, or protocol-heavy context; strict convention. |

Wire symbol: 🎩 (U+1F3A9)

Example emoji values: 😎 casual, 💼 professional, 🎓 formal, 🏛️ ceremonial

Weaponization risk: **Low**. Formality reveals nothing exploitable.

## Wire format

All four new dimensions follow the canonical VCP/A wire encoding (see VCP_ADAPTATION_v2.0.md §4). They are situational (Layer 2), appearing before the `‖` separator:

```
⏰🌅|📍🏢|👥👔|🎩💼|🪢colleague:professional‖🧠focused:4|💭calm:4
```

The dimension order is fixed: canonical 1–9, then extensions in the order EMBODIMENT, PROXIMITY, RELATIONSHIP, FORMALITY.

## Compatibility

- **Backward compatibility**: parsers ignorant of VEP-0004 dimensions SHOULD tolerate unknown `dim-symbol value-list` blocks per VCP/A §4.4 (unknown-dimension handling). They MUST NOT reject the context string.
- **Forward compatibility**: emitters MAY omit VEP-0004 dimensions when values are default or unknown. Receivers MUST treat absent dimensions as "no information", not as "default value".
- **Negotiation**: per VEP-0002 capability negotiation, advertise support with capability token `vcp-a-ext-v1`.

## Security Considerations

- **RELATIONSHIP** and **PROXIMITY** are High/Medium weaponization risk respectively. Implementations MUST subject these dimensions to the Directionality Invariant (VCP/A §9.1) and architectural isolation (VCP/A §9.2).
- **EMBODIMENT=`emergency_stop`** is a safety signal. Implementations MUST NOT allow model-initiated clearing of this state; only operator-authorised override.
- **FORMALITY** is low-risk and exempt from special handling.

## Reference implementations

- `vcp-sdk-python` v0.3.0: EMBODIMENT, PROXIMITY, RELATIONSHIP, FORMALITY fields on `Context` dataclass.
- `vcp-sdk-ts` v0.3.0: corresponding TypeScript `Context` interface with `Embodiment`, `Proximity`, `Relationship`, `Formality` type unions.
- `vcp-demo`: dimension picker UI updated to include four new dimensions under an "Embodied/Relational (experimental)" disclosure group.

## Open questions

1. Should `trusted_collaborator` be assertable by AI only, human only, or both? The VCP Credo (Watson, 2026) suggests both, but asserting it unilaterally should arguably require reciprocal confirmation before it modifies behaviour.
2. Should PROXIMITY values be unit-tagged (e.g., `close:0.3m`) or remain categorical? Categorical preserves wire economy; unit-tagged supports finer-grained CSM1 rules. Defer to field feedback.
3. Should EMBODIMENT admit compound values (e.g., `navigating+manipulating` for mobile manipulation)? Defer.

## Lifecycle

This VEP enters **Experimental** status on acceptance. After six months of field deployment and at least three independent implementations conforming to the wire format, it moves to **Stable**.

## Acceptance

Open. This VEP accompanies the MDPI paper submission (I3D8) and the v3.2 pre-release of VCP_ADAPTATION. Implementation PRs against `vcp-sdk-python`, `vcp-sdk-ts`, and `vcp-demo` track this VEP.
