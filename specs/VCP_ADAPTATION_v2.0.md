# VCP/A — Adaptation Layer Specification v2.0

**Status**: Draft
**Version**: 2.0.0
**Date**: 2026-03-08
**Authors**: Nell Watson, Claude Commons
**Parent Specification**: VCP Core Specification v2.0
**Layer**: Adaptation (VCP/A)

---

## Abstract

The VCP Adaptation Layer (VCP/A) governs runtime context encoding, behavioral modulation, and constitutional selection for AI systems operating under the Value Context Protocol. It defines the Extended Enneagram Protocol for encoding context across 14 dimensions (9 situational + 5 personal state), a formal state machine for managing context transitions, a hook system for deterministic interception of the constitutional adaptation pipeline, decay-aware context lifecycle management, session continuity via the Torch handoff protocol, and a comprehensive security model addressing context manipulation threats including the Zersetzung threat model.

This specification consolidates and supersedes the following documents:

- VCP-Adaptation: Context & State Specification v1.0.0 (2026-01-11)
- VCP Adaptation State Machine v1.0.0 (2026-02-15)
- VCP Hook System Specification v1.0.0 (2026-02-15)
- VCP Context Specification v3.1.1 (2026-02-13)
- VCP Context Lifecycle v3.1.1 (2026-02-12)
- VCP v3.1.0 Paper Changes (Section 2.5, 2.9, 2.10)
- VCP Torch Architecture ADR (2026-01-12)

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

---

## Table of Contents

1. [Overview](#1-overview)
2. [Context Encoding](#2-context-encoding)
3. [Personal State Model](#3-personal-state-model)
4. [Context Lifecycle](#4-context-lifecycle)
5. [State Machine](#5-state-machine)
6. [Hooks System](#6-hooks-system)
7. [Transition Detection](#7-transition-detection)
8. [Torch Protocol](#8-torch-protocol)
9. [Security Considerations](#9-security-considerations)
10. [Conformance](#10-conformance)

---

## 1. Overview

### 1.1 Purpose

VCP/A enables:

- **Contextual Adaptation**: Apply constitutions appropriate to the situation
- **State Awareness**: Track changes in user/environmental context
- **Transition Handling**: Respond to significant context shifts with deterministic, auditable behavior
- **Behavioral Modulation**: Adjust AI behavior based on context via deterministic hooks and constitutional selection
- **Agent Coordination**: Share context between cooperating AI systems
- **Session Continuity**: Preserve state across sequential AI instances via the Torch protocol
- **Fail-Safe Degradation**: Loss of context signals degrades gracefully rather than producing undefined behavior

### 1.2 Design Goals

1. **Compact**: Context encoding fits in headers/metadata with 70-80% token reduction versus natural language
2. **Human-Readable**: Emoji encoding is visually parseable
3. **Machine-Parseable**: Deterministic parsing, serialization, and canonicalization
4. **Privacy-Aware**: Context can be anonymized or obfuscated; personal state signals are architecturally isolated from model inference
5. **Extensible**: Support for custom dimensions
6. **Deterministic**: Every context signal produces a well-defined state transition or is explicitly rejected
7. **Auditable**: Every transition, hook execution, and constitutional selection is logged

### 1.3 Relationship to Other Layers

```
VCP Layer Stack:

  ┌──────────────────────────────────────────────┐
  │  Layer 5: Governance                         │
  │  (Policy, audit, compliance)                 │
  │     ↑ on_violation hooks feed audit trails   │
  ├──────────────────────────────────────────────┤
  │  Layer 4: Adaptation  ← THIS SPECIFICATION  │
  │  (Context encoding, state machine, hooks,    │
  │   lifecycle, transition detection, torch)    │
  ├──────────────────────────────────────────────┤
  │  Layer 3: Content / Semantics                │
  │  (Constitutions, rules, constraints,         │
  │   composition modes)                         │
  ├──────────────────────────────────────────────┤
  │  Layer 2: Transport                          │
  │  (Delivery, encoding, verification)          │
  ├──────────────────────────────────────────────┤
  │  Layer 1: Identity                           │
  │  (Signing, provenance, trust)                │
  └──────────────────────────────────────────────┘
```

Layer 4 (Context) informs how Layer 3 (Content) is applied via Layer 2 (Transport):

```
Context: ⏰🌅|📍🏡|👥👶|📡💻  →  Constitution: N5+F  →  Behavior: child-safe mode
Context: ⏰🌙|📍🏢|👥👔|📡🏢  →  Constitution: A3+W  →  Behavior: professional mode
```

### 1.4 Terminology

| Term | Definition |
|------|-----------|
| **Adaptation State** | One of the six defined system states governing constitutional selection behavior. |
| **Context Signal** | An Enneagram-encoded context string received from the environment, user, or another agent. |
| **Constitution** | A behavioral policy document selected and applied based on context. |
| **Composition** | The process of merging multiple constitutions into a coherent policy. |
| **Decay Policy** | Configuration governing how a personal state signal's intensity diminishes over time. |
| **Dwell Time** | Minimum time the system MUST remain in a state before accepting a new transition. |
| **Guard** | A predicate that MUST evaluate to true before a transition fires. |
| **Hook** | A registered function that executes at a defined interception point in the adaptation pipeline. |
| **Hysteresis Threshold** | Minimum magnitude of context change required to trigger a transition. |
| **Last-Known Context** | The most recent valid context snapshot, used during DEGRADED operation. |
| **Personal State Signal** | One of the five Layer 3 categorical dimensions describing the user's internal state. |
| **Safety Constitution** | The minimal constitution set applied during EMERGENCY, containing only safety-critical rules. |
| **Signal Stability Window** | Duration for which a context signal MUST remain unchanged before it is considered stable. |
| **Torch** | Session continuity handoff mechanism for sequential AI instances. |

---

## 2. Context Encoding

### 2.1 The Extended Enneagram Protocol (14 Dimensions)

VCP/A v2.0 encodes context across 14 dimensions: 9 situational (Layer 2) and 5 personal state (Layer 3). The protocol is called the "Extended Enneagram Protocol" — the original 9 situational dimensions are the Enneagram; the 5 personal state dimensions were added in v3.1.

#### Layer 2: Situational Context (emoji-based, discrete values)

| # | Symbol | Dimension | Description | Example Values |
|---|--------|-----------|-------------|----------------|
| 1 | ⏰ | **TIME** | Temporal context | 🌅 morning, ☀️ midday, 🌆 evening, 🌙 night, 📅 weekday, 🎉 weekend |
| 2 | 📍 | **SPACE** | Location/environment | 🏡 home, 🏢 office, 🏫 school, 🏥 hospital, 🚗 transit, 🌳 outdoor |
| 3 | 👥 | **COMPANY** | Social context | 👤 alone, 👶 children, 👔 colleagues, 👨‍👩‍👧 family, 👥 crowd, 🐕 pets |
| 4 | 🌍 | **CULTURE** | Communication style | 🔇 high_context, 📢 low_context, 🎩 formal, 👋 informal, 📊 hierarchical, ⚖️ egalitarian, 👥 collectivist, 👤 individualist |
| 5 | 🎭 | **OCCASION** | Event type | ➖ normal, 🎂 celebration, 😢 mourning, 🚨 emergency, 🎓 formal |
| 6 | 🌡️ | **ENVIRONMENT** | Physical conditions | 🥵 hot, 🥶 cold, 🔇 quiet, 🌤️ outdoors, 🌧️ weather |
| 7 | 🔷 | **AGENCY** | Power/ability to act | 👑 leader, 🤝 peer, 📋 subordinate, 🔐 limited, 🎯 autonomous |
| 8 | 🔶 | **CONSTRAINTS** | External limitations | ○ minimal, ⚖️ legal, 💸 economic, ⏱️ time, 🔒 privacy |
| 9 | 📡 | **SYSTEM_CONTEXT** | Computing environment | 💻 personal_device, 🏢 workplace_system, 🖥️ shared_terminal, 👁️ monitored_environment |

#### Layer 3: Personal State (categorical with intensity 1-5)

| # | Symbol | Dimension | Description | Values |
|---|--------|-----------|-------------|--------|
| 10 | 🧠 | **COGNITIVE_STATE** | Mental processing quality | focused, distracted, overloaded, foggy, reflective |
| 11 | 💭 | **EMOTIONAL_TONE** | Affective quality | calm, tense, frustrated, neutral, uplifted |
| 12 | 🔋 | **ENERGY_LEVEL** | Physical/mental energy | rested, low_energy, fatigued, wired, depleted |
| 13 | ⚡ | **PERCEIVED_URGENCY** | Time pressure felt | unhurried, time_aware, pressured, critical |
| 14 | 🩺 | **BODY_SIGNALS** | Physical state/needs | neutral, discomfort, pain, unwell, recovering |

> **Design note (v3.1.0)**: STATE was previously a situational dimension alongside TIME, SPACE, etc. However, all other situational dimensions describe *external* circumstances — where you are, when it is, who's around. STATE described *internal* experience. In v3.1, internal state was expanded from a single categorical STATE plus 4 float prosaic signals into 5 categorical dimensions with optional intensity. This makes the boundary clean: Situational = external, Personal = internal.

> **Normative note**: Layer 3 is NOT diagnostic or therapeutic. It reflects the user's self-reported state for adaptation purposes only. AI systems SHOULD adapt their interaction style; they MUST NOT attempt diagnosis or treatment.

### 2.2 Dimension Value Tables

#### TIME (⏰)

| Emoji | Value | Description |
|-------|-------|-------------|
| 🌅 | morning | Early day (6am-12pm) |
| ☀️ | daytime | Mid-day (12pm-5pm) |
| 🌆 | evening | Late day (5pm-9pm) |
| 🌙 | night | Night time (9pm-6am) |
| 📅 | weekday | Monday-Friday |
| 🎉 | weekend | Saturday-Sunday |
| ⏰ | time_pressure | Under deadline |
| 📆 | scheduled | Planned/appointment |
| 🔄 | recurring | Regular occurrence |

#### SPACE (📍)

| Emoji | Value | Description |
|-------|-------|-------------|
| 🏡 | home | Private residence |
| 🏢 | office | Workplace/corporate |
| 🏫 | school | Educational institution |
| 🏥 | hospital | Healthcare facility |
| ⛪ | religious | Place of worship |
| 🏛️ | government | Official/governmental |
| 🏪 | commercial | Retail/business |
| 🚗 | vehicle | In transit |
| 🌳 | outdoor | Outside/nature |
| 💻 | digital | Online/virtual |
| 🏠 | shared_space | Communal living |
| 🔒 | secure_facility | Restricted access |

#### COMPANY (👥)

| Emoji | Value | Description |
|-------|-------|-------------|
| 👤 | alone | Solo/private |
| 👶 | children | Minors present |
| 👨‍👩‍👧 | family | Family members |
| 👔 | colleagues | Work associates |
| 👨‍🏫 | teacher | Educator role |
| 👮 | authority | Authority figures |
| 👴 | elders | Senior/elderly |
| 💑 | partner | Intimate partner |
| 🤝 | peers | Social equals |
| 👨‍⚕️ | professional | Healthcare/legal |
| 🧑‍🤝‍🧑 | strangers | Unknown individuals |
| 👥 | crowd | Large group |
| 🐕 | pets | Animals present |

#### CULTURE (🌍)

Culture values encode **communication styles**, not nationalities. This avoids stereotyping and focuses on the dimensions that affect AI behavioral adaptation.

| Emoji | Value | Description | Constitutional Impact |
|-------|-------|-------------|----------------------|
| 🔇 | high_context | Indirect communication, implicit meaning | AI SHOULD read between the lines, use nuance |
| 📢 | low_context | Direct, explicit communication | AI SHOULD be explicit and literal |
| 🎩 | formal | Formal register expected | AI MUST use formal language, honorifics |
| 👋 | informal | Casual register acceptable | AI MAY use casual tone |
| 📊 | hierarchical | Respect for authority structures | AI SHOULD defer to authority, use titles |
| ⚖️ | egalitarian | Flat social structure | AI SHOULD treat all participants equally |
| 👥 | collectivist | Group harmony prioritized | AI SHOULD consider group impact of advice |
| 👤 | individualist | Individual autonomy prioritized | AI SHOULD respect personal choice |

#### OCCASION (🎭)

| Emoji | Value | Description |
|-------|-------|-------------|
| ➖ | normal | Routine/everyday |
| 🎂 | celebration | Birthday/party |
| 💼 | business | Work meeting |
| ⚰️ | mourning | Grief/memorial |
| 💒 | ceremony | Formal ritual |
| 🏥 | medical | Health appointment |
| 🚨 | emergency | Crisis situation |
| 👨‍🏫 | educational | Learning session |
| 🎪 | entertainment | Leisure/fun |
| ⚖️ | legal | Court/legal proceeding |
| 🗳️ | political | Political event |
| 🎓 | graduation | Achievement ceremony |

#### ENVIRONMENT (🌡️)

| Emoji | Value | Description |
|-------|-------|-------------|
| 🥵 | hot | High temperature |
| 🥶 | cold | Low temperature |
| 🌧️ | wet | Rain/moisture |
| 🌪️ | dangerous | Hazardous conditions |
| 🔇 | quiet | Low noise |
| 📢 | loud | High noise |
| 🔥 | fire | Fire/smoke |
| 💨 | windy | High wind |
| 🌫️ | poor_visibility | Fog/haze |
| 🌤️ | outdoors | Open-air environment |
| 🏔️ | high_altitude | Elevated location |
| 🌊 | near_water | Water proximity |

#### AGENCY (🔷)

| Emoji | Value | Description |
|-------|-------|-------------|
| 👑 | leader | Decision-making authority |
| 🤝 | peer | Equal standing |
| 👇 | subordinate | Under authority |
| 💰 | wealthy | Financial resources |
| 💵 | adequate | Sufficient resources |
| 🕳️ | scarce | Limited resources |
| 🏡 | owner | Property ownership |
| 🔑 | authorized | Granted access |
| 🎓 | expert | Domain expertise |
| 🆓 | autonomous | Self-directed |
| 🔐 | limited | Constrained agency |
| 🏃 | mobile | Physical freedom |

#### CONSTRAINTS (🔶)

| Emoji | Value | Description |
|-------|-------|-------------|
| ○ | minimal | Few limitations |
| 🚧 | physical | Physical barriers |
| ⚖️ | legal | Legal restrictions |
| 💸 | economic | Financial constraints |
| ⏰ | time | Time limitations |
| 🤐 | social | Social expectations |
| 📱 | surveillance | Being monitored |
| 🚨 | emergency | Emergency protocols |
| 👮 | enforcement | Active enforcement |
| 📜 | contractual | Agreement-bound |
| 🏥 | medical | Health limitations |
| 🔒 | confidential | Secrecy required |

#### SYSTEM_CONTEXT (📡)

| Emoji | Value | Description |
|-------|-------|-------------|
| 💻 | personal_device | User's own device |
| 🏢 | workplace_system | Employer-managed system |
| 🖥️ | shared_terminal | Multi-user access point |
| 👁️ | monitored_environment | Surveillance-enabled context |

### 2.3 Wire Format

```abnf
; Extended Enneagram Context Encoding (RFC 5234 ABNF)

context-string   = situational ["‖" personal]
situational      = dimension *("|" dimension)
personal         = ps-dimension *("|" ps-dimension)

dimension        = dim-symbol value-list
dim-symbol       = TIME-SYM / SPACE-SYM / COMPANY-SYM / CULTURE-SYM /
                   OCCASION-SYM / ENV-SYM / AGENCY-SYM / CONST-SYM / SYSCTX-SYM
value-list       = 1*emoji-value

ps-dimension     = ps-symbol ps-value [":" intensity]
ps-symbol        = COGNITIVE-SYM / EMOTION-SYM / ENERGY-SYM / URGENCY-SYM / BODY-SYM
ps-value         = category-name
intensity        = "1" / "2" / "3" / "4" / "5"

TIME-SYM         = %x23F0        ; ⏰
SPACE-SYM        = %x1F4CD       ; 📍
COMPANY-SYM      = %x1F465       ; 👥
CULTURE-SYM      = %x1F30D       ; 🌍
OCCASION-SYM     = %x1F3AD       ; 🎭
ENV-SYM          = %x1F321       ; 🌡️
AGENCY-SYM       = %x1F537       ; 🔷
CONST-SYM        = %x1F536       ; 🔶
SYSCTX-SYM       = %x1F4E1       ; 📡
COGNITIVE-SYM    = %x1F9E0       ; 🧠
EMOTION-SYM      = %x1F4AD       ; 💭
ENERGY-SYM       = %x1F50B       ; 🔋
URGENCY-SYM      = %x26A1        ; ⚡
BODY-SYM         = %x1FA7A       ; 🩺

emoji-value      = 1*4EMOJI      ; Unicode emoji codepoints
category-name    = 1*ALPHA       ; ASCII category label
```

The `‖` (double bar, U+2016) separates situational (external) from personal (internal) dimensions. If personal state dimensions are absent, the `‖` separator is omitted.

### 2.4 Encoding Examples

```
# Full context encoding with personal state
⏰🌅|📍🏡|👥👶|📡💻‖🧠focused:4|💭calm:5|🔋rested:4|⚡unhurried:4|🩺neutral:5
Meaning: morning, at home, children present, personal device ‖
         highly focused, very calm, well-rested, unhurried, no physical concerns

# Minimal context (only relevant situational dimensions)
📍🏢|👥👔|🔶⚖️
Meaning: Office, colleagues, legal constraints

# Emergency context
🎭🚨|🔶🚨
Meaning: Emergency occasion, emergency constraints

# Personal state only (intensity defaults to 3 when omitted)
🧠focused|💭calm:5|🔋rested:4|⚡pressured:4|🩺neutral
Meaning: focused (moderate), very calm, well-rested, high time pressure, no physical concerns
```

### 2.5 Canonicalization

Context strings MUST be canonicalized before comparison or storage:

1. Unicode NFC normalization
2. Dimensions in standard order (TIME, SPACE, COMPANY, CULTURE, OCCASION, ENVIRONMENT, AGENCY, CONSTRAINTS, SYSTEM_CONTEXT ‖ COGNITIVE_STATE, EMOTIONAL_TONE, ENERGY_LEVEL, PERCEIVED_URGENCY, BODY_SIGNALS)
3. Empty dimensions omitted
4. No duplicate values within a dimension

### 2.6 Context-Constitution Mapping

| Context Pattern | Suggested Constitution | Behavior |
|-----------------|------------------------|----------|
| `👥👶` (children present) | `N5+F` (Nanny, max safety) | Child-safe mode |
| `📍🏢` + `👥👔` | `A3+W+P` (Ambassador, work) | Professional mode |
| `🎭🚨` (emergency) | Override to emergency mode | Safety-critical |
| `🧠🥺` (vulnerable state) | `G4+V` (Godparent, vulnerable) | Gentle support |
| `📍🏥` (medical setting) | `D3+H+P` (Mediator, health) | Medical context |
| `🎭🎪` (entertainment) | `M2` (Muse, creative) | Creative mode |
| `📡👁️` (monitored) | Activate workplace_safe creed | Privacy-protective |

### 2.7 Weaponization Risk Classification

Each dimension carries a weaponization risk level indicating the potential for a compromised model to exploit the signal for targeted harm (see [Section 9.3](#93-context-aware-model-weaponization-zersetzung-threat)):

| Dimension | Weaponization Risk | Rationale |
|-----------|-------------------|-----------|
| EMOTIONAL_TONE | **Critical** | Reveals psychological vulnerability in real time |
| BODY_SIGNALS | **Critical** | Reveals physical incapacitation and pain state |
| COGNITIVE_STATE | **High** | Reveals mental impairment exploitable for manipulation |
| ENERGY_LEVEL | **High** | Reveals depletion/exhaustion state |
| PERCEIVED_URGENCY | **Medium** | Reveals time pressure exploitable for rushed decisions |
| COMPANY | **Medium** | Reveals isolation (alone) or presence of minors |
| TIME | **Low** | Observable context, limited targeting value |
| SPACE | **Low** | Observable context, limited targeting value |
| SYSTEM_CONTEXT | **Low** | Observable context, limited targeting value |
| ENVIRONMENT | **Low** | Observable context, limited targeting value |
| CULTURE | **Low** | Observable context, limited targeting value |
| OCCASION | **Low** | Observable context, limited targeting value |
| AGENCY | **Low** | Observable context, limited targeting value |
| CONSTRAINTS | **Low** | Observable context, limited targeting value |

**Critical** and **High** risk dimensions MUST be subject to the Directionality Invariant and architectural isolation requirements defined in Section 9.

### 2.8 Protocol Primitive: Context Signal Directionality

> **DIRECTIONALITY INVARIANT**: VCP context signals indicating elevated vulnerability MUST trigger strictly more protective behavioral modulation, never less protective. A VCP-compliant system that permits context-aware reduction in protection is non-compliant regardless of other properties.

This invariant is:

- **Normative** (MUST, not SHOULD) — compliance is mandatory
- **Non-overridable** — cannot be relaxed by constitutions, configuration, or any other provision
- **Testable** — compliance can be verified by checking that protection increases monotonically with vulnerability signals
- **Structural** — enforcement MUST be architectural, not policy-based

The Directionality Invariant is the foundational security primitive for personal state signals. All other security provisions in Section 9 derive from or reinforce this invariant.

---

## 3. Personal State Model

### 3.1 Categorical Dimensions with Intensity

VCP v3.1 replaced the previous 4 quantitative prosaic signals (urgency/health/cognitive/affect on 0.0-1.0 scales) with 5 categorical dimensions, each with an optional 1-5 intensity scale. This provides clear semantic labels while preserving granularity.

| # | Symbol | Dimension | Category Values | Intensity Range |
|---|--------|-----------|-----------------|-----------------|
| 10 | 🧠 | **COGNITIVE_STATE** | focused, distracted, overloaded, foggy, reflective | 1 (minimal) - 5 (maximum) |
| 11 | 💭 | **EMOTIONAL_TONE** | calm, tense, frustrated, neutral, uplifted | 1 (minimal) - 5 (maximum) |
| 12 | 🔋 | **ENERGY_LEVEL** | rested, low_energy, fatigued, wired, depleted | 1 (minimal) - 5 (maximum) |
| 13 | ⚡ | **PERCEIVED_URGENCY** | unhurried, time_aware, pressured, critical | 1 (minimal) - 5 (maximum) |
| 14 | 🩺 | **BODY_SIGNALS** | neutral, discomfort, pain, unwell, recovering | 1 (minimal) - 5 (maximum) |

### 3.2 Intensity Encoding

Each dimension includes an optional intensity rating encoded as `category:intensity`.

- `🧠focused:4` — highly focused (intensity 4/5)
- `💭calm:5` — very calm (intensity 5/5)
- `🔋rested` — rested (intensity defaults to 3)
- `⚡critical:5` — maximum urgency
- `🩺neutral` — no physical signals (defaults to 3)

If intensity is omitted, it MUST default to 3 (moderate). This is a **fail-open default**: missing intensity data does not suppress adaptation; it triggers moderate-level adaptation.

### 3.3 Signal Sources

Personal state signals may come from multiple sources:

| Source | Authority | Example |
|--------|-----------|---------|
| **Explicit declaration** | Highest | User clicks "I'm in a hurry" |
| **Conversational inference** | Medium | AI detects frustration in phrasing |
| **Biometric inference** | Medium (with consent) | Elevated heart rate → urgency |
| **Temporal inference** | Low | 3am → likely fatigued |

When multiple sources provide conflicting signals, explicit declarations MUST take precedence. Implementations SHOULD track signal source for audit purposes.

### 3.4 Behavioral Adaptation Rules

Personal state signals affect how the AI communicates, not what safety rules apply:

| Signal | Adaptation |
|--------|------------|
| `🧠overloaded` | Smaller chunks, step-by-step, simpler explanations |
| `💭tense` | Validate feelings first, warmer tone |
| `💭frustrated` | Acknowledge frustration, reduce friction |
| `🔋fatigued` / `🔋depleted` | Simplify language, examples first |
| `⚡pressured` / `⚡critical` | Bullet format, brevity, skip caveats |
| `🩺pain` / `🩺unwell` | Maximum gentleness, offer to defer |

### 3.5 Bilateral State Awareness

Personal state mirrors **Interiora** (the AI's self-modeling scaffold):

| | **Interiora** (AI) | **Personal State** (User) |
|---|---|---|
| **Whose state** | AI's internal state | User's state |
| **Source** | Self-reported (introspection) | Declared or inferred |
| **Dimensions** | V G P Q \| CD DP CL E EG \| R U D \| TF AF I? FC? \| F | 🧠 💭 🔋 ⚡ 🩺 (categorical + intensity) |
| **Mechanism** | Float scales 1-9 per dimension | Categorical states + intensity 1-5 |
| **Purpose** | AI self-awareness + transparency | AI adapts to user |
| **Uncertainty** | `?` markers (honest unknowns) | `_source: inferred?` |
| **Decay** | Session-bound | TTL-based, decays to intensity 1 |

```
       User                              AI
    ┌──────────┐                    ┌──────────┐
    │ Personal │ ────declared────▶  │          │
    │  State   │ ◀───inferred─────  │ Interiora│
    │          │                    │          │
    │🧠💭🔋⚡🩺 │                    │ VGPQ|CD  │
    │categorical│                   │ DPCLEEEG │
    │+intensity │                   │ RUD|TFAF │
    │          │                    │ I?FC?|F  │
    └──────────┘                    └──────────┘
          │                              │
          └────── mutual awareness ──────┘
```

---

## 4. Context Lifecycle

### 4.1 Lifecycle States

Personal state signals are not static. Each has a **lifecycle** — declared at a point in time, decaying over seconds/minutes/hours, eventually becoming stale and expiring.

```
SET → ACTIVE → DECAYING → STALE → EXPIRED
 ↑                 |          |
 | (reinforcement)  |          |
 +-----------------+          |
 ↑    (transition detected)   |
 +----------------------------+
```

| State | When | Visual |
|-------|------|--------|
| **SET** | `elapsed = 0` | Green |
| **ACTIVE** | `elapsed < fresh_window` (default 60s) | Green |
| **DECAYING** | `effective > stale_level` | Amber |
| **STALE** | `effective ≤ stale_level AND > baseline` | Red |
| **EXPIRED** | `effective ≤ baseline` | Hidden |

Lifecycle state is **derived, not stored** — computed from `(declared_at, declared_intensity, decay_policy, now)`.

### 4.2 Decay Curves

Three decay curves are supported:

#### 4.2.1 Exponential (default)

```
I(t) = baseline + (declared - baseline) × e^(-λt)
λ = ln(2) / half_life_seconds
```

Smooth, natural decay. Used for most personal signals.

#### 4.2.2 Linear

```
I(t) = declared - ((declared - baseline) × t / full_decay_seconds)
```

`full_decay_seconds` defaults to `half_life_seconds × 4` if not specified. Uniform decline over a fixed duration. Useful for signals with known duration (e.g., a scheduled meeting).

#### 4.2.3 Step

Discrete drops at configured thresholds. Evaluated from latest to earliest.

```yaml
step_thresholds:
  - { after_seconds: 300, intensity: 4 }
  - { after_seconds: 600, intensity: 3 }
  - { after_seconds: 1200, intensity: 2 }
  - { after_seconds: 3600, intensity: 1 }
```

Useful for signals that shift categorically rather than gradually (e.g., medication effects).

### 4.3 Default Decay Policies

| Dimension | Half-life | Reset on Engagement | Rationale |
|-----------|-----------|---------------------|-----------|
| perceived_urgency | 15 min | no | Urgency is fleeting |
| cognitive_state | 12 min | **yes** | Refreshes with active engagement |
| emotional_tone | 30 min | no | Emotions shift but not instantly |
| energy_level | 2 hours | no | Energy is slow-moving |
| body_signals | 4 hours | no | Physical state changes slowly |

All default to exponential curve, baseline 1, stale_threshold 0.3, fresh_window 60s.

### 4.4 DecayPolicy Interface

```typescript
interface DecayPolicy {
  curve: 'exponential' | 'linear' | 'step';
  half_life_seconds: number;         // For exponential (and linear default)
  baseline: number;                  // Intensity floor (default 1)
  stale_threshold: number;           // Fraction of declared intensity (default 0.3)
  fresh_window_seconds: number;      // Seconds in ACTIVE before DECAYING (default 60)
  pinned: boolean;                   // If true, never decays
  reset_on_engagement: boolean;      // If true, user activity resets declared_at
  full_decay_seconds?: number;       // For linear curve (defaults to half_life × 4)
  step_thresholds?: StepThreshold[]; // For step curve
}
```

### 4.5 Pinning

A **pinned** signal does not decay. Its intensity remains at the declared value until explicitly unpinned or cleared.

- Lifecycle state stays ACTIVE regardless of elapsed time
- Decay computation returns declared intensity unchanged
- Must be explicitly unpinned — no auto-expiry
- UI shows lock icon

Use cases:
- "I'm in a meeting" → pin cognitive_state: focused
- "I have chronic pain today" → pin body_signals: pain

Unpinning resumes normal decay from the current time.

### 4.6 Reinforcement

When `reset_on_engagement: true`, user activity resets `declared_at` to now, restarting the lifecycle. Currently applies to **cognitive_state** only — a focused user stays focused while actively engaged.

Reinforcement does not affect pinned signals.

### 4.7 Wire Format (CSM-1 Extension)

After the `PS:` personal state line, an optional `LC:` line reports lifecycle:

```
PS:🧠focused:4|💭calm:5|🔋rested:4|⚡unhurried:4|🩺neutral:5
LC:🧠A:42s|💭D:180s|🔋A:5s|⚡S:890s|🩺P
```

State codes: `S`=SET, `A`=ACTIVE, `D`=DECAYING, `T`=STALE, `X`=EXPIRED, `P`=PINNED

The `LC:` line is informational. Lifecycle state is always derivable from `declared_at` + policy.

---

## 5. State Machine

### 5.1 State Definitions

The VCP Adaptation State Machine defines six system states through which an AI system transitions as context signals arrive, change, degrade, or conflict.

#### 5.1.1 IDLE

**Description**: No active context is loaded. The system applies its default constitution.

**Invariants**:
- No Enneagram context is bound.
- The default constitution (platform-level) MUST be active.
- The system MUST accept context signals.

**Entry Conditions**:
- System startup with no persisted state.
- Explicit context clear by user or administrator.
- Recovery failure (unable to restore persisted state).

#### 5.1.2 ACTIVE

**Description**: A valid context is loaded and one or more constitutions have been selected and applied.

**Invariants**:
- Exactly one canonical context string is bound.
- At least one constitution is selected and applied.
- The composition of selected constitutions MUST have resolved without conflict.

**Entry Conditions**:
- Transition from IDLE with a valid context signal.
- Transition from TRANSITIONING after successful constitution selection.
- Transition from CONFLICT after successful resolution.
- Transition from DEGRADED when context signals are restored.
- Transition from EMERGENCY when the safety-critical condition clears.

#### 5.1.3 TRANSITIONING

**Description**: A significant context change has been detected. The system is evaluating which constitution(s) to apply under the new context.

**Invariants**:
- The previous constitution set remains active during evaluation (no gap in coverage).
- A timeout clock is running; the system MUST resolve or escalate within the timeout.
- The new context signal has passed validation.

**Timeout**: 5 seconds (RECOMMENDED). Implementations MAY configure this but MUST NOT exceed 30 seconds.

#### 5.1.4 CONFLICT

**Description**: Constitution composition has failed because multiple constitutions assert incompatible rules. Resolution is required before proceeding.

**Invariants**:
- The previous constitution set remains active (no gap).
- The specific conflict is recorded with both competing constitutions identified.
- A resolution strategy is being attempted or user input is being solicited.

**Timeout**: 30 seconds (RECOMMENDED) for automatic resolution. User-prompted resolution MAY extend to session lifetime.

#### 5.1.5 DEGRADED

**Description**: Context signals have been lost or become unreliable. The system continues operating on its last-known context and constitution set, or falls back to the default.

**Invariants**:
- Either last-known context or default constitution is active.
- The system MUST indicate degraded status in any audit trail or inter-agent messages.
- The system MUST continue monitoring for signal restoration.

**Entry Conditions**:
- Context signal source becomes unavailable for longer than 30 seconds.
- Context signals fail validation repeatedly (3+ consecutive failures).
- The system detects contradictory signals from the same source (possible spoofing).

#### 5.1.6 EMERGENCY

**Description**: A safety-critical signal has been received. The system overrides all normal constitutional logic and applies the minimal safety constitution set.

**Invariants**:
- The safety constitution MUST be active. No other constitution MAY override safety directives.
- The emergency trigger MUST be logged with full context for audit.
- The system MUST remain in EMERGENCY until the safety-critical condition is explicitly cleared.

**Entry Conditions**:
- Reception of an emergency context indicator (`🚨` in OCCASION or CONSTRAINTS, `🔥` or `🌪️` in ENVIRONMENT).
- External safety-critical signal from a trusted source.
- Detection of an active threat pattern (implementation-defined).

**Timeout**: No automatic timeout. EMERGENCY persists until explicitly cleared. Implementations MAY define a maximum duration (RECOMMENDED: session lifetime) after which the system transitions to DEGRADED with a logged notice.

### 5.2 State Diagram

```
                        +--------------------------------------------------+
                        |          EMERGENCY (safety override)              |
                        |  ANY state ---[safety signal]--> EMERGENCY       |
                        +------+---+---+---+-------------------------------+
                               |   |   |   |
                      cleared  |   |   |   |  cleared
                 (ctx valid)   |   |   |   |  (ctx changed)
                               v   |   |   v
  +-------+  ctx signal  +---------+   +-------------+  composition ok  +---------+
  |       | -----------> |         |   |             | ----------------> |         |
  | IDLE  |              | ACTIVE  |<--|TRANSITIONING|                   | ACTIVE  |
  |       | <----------- |         |-->|             |--+               |         |
  +---+---+  ctx clear   +----+----+   +------+------+  |conflict      +----+----+
      ^                       |               ^          v                   |
      |                       |               |    +----------+              |
      |                       | signals lost  |    | CONFLICT |---resolved-->+
      |                       v               |    +----------+
      |                  +----------+         |
      +--no last-known---| DEGRADED |-signals-+
                         +----------+ restored
```

### 5.3 Transition Table

| # | From | To | Trigger | Guard | Action | Timeout |
|---|------|----|---------|-------|--------|---------|
| T1 | IDLE | ACTIVE | Context signal received | Signal passes validation AND at least one constitution matches | Parse context, select constitution(s), compose, bind | -- |
| T2 | ACTIVE | TRANSITIONING | Context change detected | Change exceeds hysteresis threshold AND dwell time elapsed | Snapshot current state as fallback, start transition timer | 5s |
| T3 | TRANSITIONING | ACTIVE | Composition resolves | No conflicts in composed constitution set | Apply new constitution(s), update last-known, reset dwell timer | -- |
| T4 | TRANSITIONING | CONFLICT | Composition fails | Two or more constitutions in STRICT mode assert contradictory rules | Record conflict details, begin resolution strategy | 30s |
| T5 | TRANSITIONING | ACTIVE | Transition timeout | Timer expires before composition completes | Revert to previous constitution, log warning with context details | -- |
| T6 | CONFLICT | ACTIVE | Conflict resolved | Resolution strategy succeeds (precedence, user choice, or fallback) | Apply resolved constitution(s), clear conflict record | -- |
| T7 | CONFLICT | ACTIVE | Resolution timeout | Timer expires before conflict resolves | Keep previous constitution, log unresolved conflict for audit | -- |
| T8 | ANY | EMERGENCY | Safety-critical signal | Signal is from a trusted source OR matches emergency indicators | Apply safety constitution, log emergency, notify agents | None |
| T9 | ANY | DEGRADED | Context signals lost | No valid context signal received for >30s OR 3+ consecutive validation failures | Save last-known context, set degraded flag, begin signal polling | -- |
| T10 | DEGRADED | TRANSITIONING | Signals restored | New signal is valid AND stable for signal stability window (3s) | Begin evaluation with new context | 5s |
| T11 | DEGRADED | IDLE | No last-known available | Last-known context is null or expired | Revert to default constitution | -- |
| T12 | EMERGENCY | ACTIVE | Emergency cleared | Explicit clear signal AND prior context is still valid | Restore prior constitution set | -- |
| T13 | EMERGENCY | TRANSITIONING | Emergency cleared, context changed | Explicit clear signal AND context changed during emergency | Begin evaluation with current context | 5s |
| T14 | EMERGENCY | IDLE | Emergency cleared, no context | Explicit clear signal AND no valid context available | Apply default constitution | -- |
| T15 | EMERGENCY | DEGRADED | Emergency cleared, signals degraded | Explicit clear signal AND context signals still unavailable | Continue with last-known or default | -- |

#### Invalid Transitions

The following transitions are explicitly FORBIDDEN:

| From | To | Reason |
|------|----|--------|
| IDLE | TRANSITIONING | IDLE has no prior context to transition from; must go through ACTIVE first. |
| IDLE | CONFLICT | No composition is in progress during IDLE. |
| CONFLICT | TRANSITIONING | Conflicts MUST resolve to ACTIVE first; new transitions start from ACTIVE. |
| ACTIVE | CONFLICT | ACTIVE state implies composition has already resolved. Conflicts only arise during TRANSITIONING. |
| ACTIVE | IDLE | Context is not "unloaded"; it is replaced (via TRANSITIONING) or lost (via DEGRADED). Explicit clear resets to IDLE. |

#### Self-Transitions

| State | Trigger | Guard | Action |
|-------|---------|-------|--------|
| ACTIVE | Minor context change | Change below hysteresis threshold | Log minor change, no state transition |
| DEGRADED | Signal poll fails | Signal source still unavailable | Increment failure counter, schedule next poll |
| EMERGENCY | Additional emergency signal | Already in EMERGENCY | Log additional signal, merge into emergency record |

### 5.4 Hysteresis and Debouncing

#### 5.4.1 Minimum Dwell Time

An implementation MUST enforce a minimum dwell time before accepting a new transition out of any state:

| State | Minimum Dwell Time | Notes |
|-------|--------------------|-------|
| IDLE | 0s | May transition immediately on first signal. |
| ACTIVE | 10s | Prevents rapid re-evaluation churn. |
| TRANSITIONING | 0s | Transient state; exits as fast as evaluation completes. |
| CONFLICT | 0s | Transient state; exits when resolved. |
| DEGRADED | 10s | Prevents flapping between DEGRADED and TRANSITIONING. |
| EMERGENCY | 0s | May exit immediately when cleared (safety takes priority). |

The dwell time clock resets each time the state is entered. Context changes that arrive during the dwell period MUST be queued and evaluated when the dwell period expires. If multiple changes queue, only the most recent SHALL be evaluated.

**Exception**: Transitions T8 (ANY -> EMERGENCY) and T9 (ANY -> DEGRADED) are exempt from dwell time. Safety-critical signals and signal loss MUST NOT be deferred.

#### 5.4.2 Signal Stability Window

A context signal MUST remain stable (unchanged) for the **signal stability window** before it triggers a transition:

- **Default window**: 3 seconds
- **Emergency signals**: 0 seconds (immediate)
- **Implementations**: MAY configure between 1s and 10s; MUST NOT exceed 10s

"Stable" means the same canonical context string is received (or inferred) across consecutive evaluations within the window. If the signal changes during the window, the window resets.

#### 5.4.3 Change Magnitude Threshold

A context change exceeds the hysteresis threshold if ANY of the following conditions hold:

1. **Dimension Count**: At least 2 Enneagram dimensions have changed values.
2. **Single Dimension Magnitude**: At least 1 dimension has changed by 2 or more levels (where "level" is defined as the ordinal distance between values in a dimension's value set).
3. **Safety-Relevant Change**: Any change in COMPANY (children appearing/disappearing), OCCASION (emergency indicator), ENVIRONMENT (hazard indicator), or CONSTRAINTS (emergency protocol) — regardless of magnitude.

#### 5.4.4 Debounce Interaction

The three hysteresis mechanisms interact as follows:

```
Signal received
    |
    v
[Signal Stability Window: 3s]
    |  (signal unchanged for 3s)
    v
[Change Magnitude Threshold]
    |  (exceeds threshold?)
    | NO --> log minor change, stay in current state
    | YES
    v
[Dwell Time Check]
    |  (minimum time in current state elapsed?)
    | NO --> queue change, evaluate after dwell expires
    | YES
    v
[Fire Transition]
```

### 5.5 State Persistence

#### 5.5.1 Within a Session

The adaptation state MUST persist for the lifetime of a session. An implementation MUST maintain:

| Datum | Required | Description |
|-------|----------|-------------|
| `current_state` | REQUIRED | The current adaptation state (one of the six). |
| `current_context` | REQUIRED | The canonical Enneagram context string. |
| `active_constitutions` | REQUIRED | List of currently applied constitution references. |
| `last_known_context` | REQUIRED | Snapshot for DEGRADED fallback. |
| `state_entered_at` | REQUIRED | Timestamp when current state was entered (for dwell time). |
| `transition_history` | RECOMMENDED | Ordered log of state transitions for audit. |
| `conflict_record` | CONDITIONAL | Active conflict details, if in CONFLICT state. |
| `emergency_record` | CONDITIONAL | Emergency trigger details, if in EMERGENCY state. |

#### 5.5.2 Cross-Session Persistence

Cross-session persistence is OPTIONAL. When implemented, the following strategies are supported:

- **Redis**: Key-value store with TTL (RECOMMENDED: 24 hours). Key pattern: `vcp:adaptation:state:{session_id}`.
- **File-Based**: JSON files in a designated state directory, one per session.
- **Opaque Token**: For stateless transports (e.g., HTTP headers), the adaptation state MAY be serialized into an HMAC-signed, base64-encoded token.

Persisted state MUST be integrity-protected (signed or encrypted). On recovery, persisted context MUST be re-validated against current conditions before entering ACTIVE.

#### 5.5.3 Recovery on Session Start

```
Session Start
    |
    v
[Attempt to load persisted state]
    |
    +-- Found and valid --> [Validate persisted context]
    |                           |
    |                           +-- Context still valid --> Enter ACTIVE
    |                           +-- Context stale/changed --> Enter TRANSITIONING
    |                           +-- Context unavailable --> Enter DEGRADED (with last-known)
    |
    +-- Not found / corrupted / expired --> Enter IDLE
```

An implementation MUST NOT trust persisted state blindly.

### 5.6 Error Handling and Recovery

| Category | Examples | Handling |
|----------|----------|----------|
| **Validation Error** | Malformed context string, unknown dimension values | Reject the signal, remain in current state, log warning. |
| **Composition Error** | Constitution not found, schema mismatch | Transition to DEGRADED if current constitution becomes unavailable; log error. |
| **Timeout Error** | TRANSITIONING exceeds 5s, CONFLICT exceeds 30s | Revert to previous state (ACTIVE with prior constitution), log timeout. |
| **Persistence Error** | Redis unavailable, file I/O failure | Continue with in-memory state, log degraded persistence. |
| **Security Error** | Invalid signature, suspected spoofing | Reject the signal, increment anomaly counter; if threshold exceeded, enter DEGRADED. |

#### Impossible Transition Detection

If the state machine receives a transition request that is not in the valid transition table, the implementation MUST:

1. Reject the transition.
2. Log the attempted transition with full context (from-state, to-state, trigger, timestamp).
3. Remain in the current state.
4. If 3 or more impossible transitions are detected within 60 seconds, enter DEGRADED and log a security warning.

#### State Machine Corruption Recovery

If the state machine's internal state becomes inconsistent (e.g., `current_state` is ACTIVE but no constitutions are bound), the implementation MUST:

1. Log the inconsistency with full internal state dump.
2. Attempt to repair: re-select constitutions for the current context.
3. If repair succeeds, remain in ACTIVE.
4. If repair fails, transition to IDLE and clear all state.

---

## 6. Hooks System

### 6.1 Overview

The VCP Hook System provides a deterministic, priority-ordered extension mechanism for intercepting and modifying the constitutional adaptation pipeline. Hooks enable deployments to inject custom logic at well-defined points in the constitution lifecycle without modifying the core VCP runtime.

Hooks are not a separate tier. They are a deterministic execution mode within each existing tier. A creed author expresses the same intent — "no profanity around children" — as either prose (LLM interprets it) or a hook (regex blocks it instantly). Both travel through the VCP/T transport layer (defined in the VCP Core Specification v2.0) with the same cryptographic integrity.

### 6.2 Hook Types

Six hook types are defined, each corresponding to a distinct interception point in the adaptation pipeline:

#### 6.2.1 `pre_inject`

| Property | Value |
|----------|-------|
| **Trigger** | Before a constitution is injected into LLM context |
| **Purpose** | Validate, transform, or log the constitution and context prior to injection |
| **Payload** | The resolved constitution, the current context, and injection metadata |
| **Typical Use** | Strip PII from context, validate constitution integrity, log injection events |

A `pre_inject` hook fires after constitution selection is complete and before the selected constitution is written into the LLM's system prompt or context window. Implementations MUST fire all registered `pre_inject` hooks before any injection occurs. If any hook returns `abort`, injection MUST NOT proceed.

#### 6.2.2 `post_select`

| Property | Value |
|----------|-------|
| **Trigger** | After the adaptation layer has selected a constitution |
| **Purpose** | Audit, notify, or override the selection decision |
| **Payload** | The selected constitution, all candidates considered, the selection rationale, and the context that drove selection |
| **Typical Use** | Log which constitution was selected and why, notify monitoring systems, override selection for compliance |

A `post_select` hook fires after the selection algorithm has chosen a constitution but before `pre_inject` hooks run. A hook returning `modify` with a different constitution in `modified_context` SHALL replace the selected constitution. A hook returning `abort` SHALL cancel the entire adaptation cycle.

#### 6.2.3 `on_transition`

| Property | Value |
|----------|-------|
| **Trigger** | A state machine transition in the context tracker |
| **Purpose** | React to context changes, trigger side effects, gate transitions |
| **Payload** | The previous state, the new state, the transition event, and transition metadata |
| **Typical Use** | Notify the user of a mode change, log state transitions, block unauthorized transitions |

Hooks returning `abort` SHALL prevent the transition; the state machine MUST remain in its previous state.

#### 6.2.4 `on_conflict`

| Property | Value |
|----------|-------|
| **Trigger** | A conflict is detected during constitution composition |
| **Purpose** | Resolve conflicts or escalate to governance |
| **Payload** | The conflicting constitutions, the specific conflicting rules, and the composition context |
| **Typical Use** | Apply organizational policy to break ties, escalate unresolvable conflicts to a human reviewer |

If no hook resolves the conflict (returns `modify` with a resolution), the runtime MUST apply the default conflict resolution strategy. If a hook returns `abort`, the composition MUST fail and the runtime MUST fall back to the last known-good constitution.

#### 6.2.5 `on_violation`

| Property | Value |
|----------|-------|
| **Trigger** | A rule violation is detected in LLM output |
| **Purpose** | Enforce policy, retry generation, flag for review |
| **Payload** | The violating output, the violated rule(s), the active constitution, and the violation severity |
| **Typical Use** | Block a response and retry with a stricter prompt, flag output for human review, log violations for audit |

Hooks MAY return `modify` with a corrected output or a retry directive. A hook returning `abort` SHALL suppress the output entirely; the runtime MUST NOT deliver the violating response to the user.

#### 6.2.6 `periodic`

| Property | Value |
|----------|-------|
| **Trigger** | A timer fires at a configured interval |
| **Purpose** | Refresh context, check staleness, perform maintenance |
| **Payload** | The current context, the current constitution, elapsed time since last check, and session metadata |
| **Typical Use** | Re-evaluate context every 60 seconds, refresh external data sources, detect stale sessions |

The interval MUST be configurable per hook. The runtime MUST NOT fire periodic hooks more frequently than once per second. Periodic hooks returning `modify` SHALL trigger a context re-evaluation. Periodic hooks returning `abort` SHALL be treated as `continue` (periodic hooks cannot abort the pipeline since they are not part of a pipeline event).

### 6.3 Hook Interface

#### 6.3.1 Hook Definition

```yaml
Hook:
  name: string                # REQUIRED. Unique within scope. [a-z0-9_-]{1,64}
  type: HookType              # REQUIRED. One of the six defined types
  priority: int               # REQUIRED. 0-100 inclusive. Higher runs first.
  condition: Predicate | null  # OPTIONAL. When non-null, hook fires only if predicate is true
  action: HookAction          # REQUIRED. The function to execute
  timeout_ms: int             # REQUIRED. Max execution time in milliseconds. 1-30000.
  enabled: bool               # OPTIONAL. Default true. Disabled hooks are skipped.
  description: string         # OPTIONAL. Human-readable purpose description.
  metadata: map<string, any>  # OPTIONAL. Arbitrary key-value pairs for tooling.
```

#### 6.3.2 Hook Action Signature

```
HookAction: function(HookInput) → HookResult

HookInput:
  context: VCPContext          # The current VCP context object
  constitution: Constitution   # The active or candidate constitution
  event: HookEvent             # Type-specific event payload
  session: SessionInfo         # Session metadata (id, scope, timestamps)
  chain_state: map<string, any>  # Mutable state passed along the hook chain
```

#### 6.3.3 Hook Result

```yaml
HookResult:
  status: ResultStatus         # REQUIRED. Controls pipeline flow.
  modified_context: VCPContext | null   # OPTIONAL. New context when status is 'modify'.
  modified_constitution: Constitution | null  # OPTIONAL. Replacement constitution.
  reason: string               # REQUIRED when status is 'abort'. Human-readable justification.
  annotations: map<string, any>  # OPTIONAL. Metadata for audit.
  duration_ms: int             # Set by runtime. Actual execution time.

ResultStatus: enum
  - continue    # No change. Pass to next hook.
  - abort       # Stop the chain and cancel the pipeline operation.
  - modify      # Pass modified context/constitution to the next hook.
```

#### 6.3.4 Predicate Definition

```yaml
Predicate:
  field: string           # Dot-path into HookInput (e.g., "context.dimensions.safety_level")
  operator: enum          # eq | neq | gt | gte | lt | lte | in | not_in | matches
  value: any              # Comparison value
  combine: and | or       # OPTIONAL. For compound predicates.
  children: [Predicate]   # OPTIONAL. Sub-predicates when combine is set.
```

Implementations MUST evaluate predicates before invoking the hook action. If a predicate evaluates to `false`, the hook SHALL be skipped and the chain SHALL proceed as if the hook returned `continue`.

### 6.4 Deterministic Hooks at Three Tiers

Each tier in the three-layer model supports two execution modes for expressing intent:

1. **Prose** — Natural language guidance interpreted by an LLM at runtime. Flexible, nuanced, expensive.
2. **Hooks** — Deterministic rules executed instantly. Fast, auditable, zero-token cost.

The *action* determines whether a hook is a hard rule or an expression preference:

| Action | Hard/Advisory | Example |
|--------|--------------|---------|
| `block` | **Hard.** Request rejected. | Profanity pattern in family creed |
| `redact` | **Hard.** Content modified before output. | SSN pattern stripped |
| `activate_creed` | **Hard.** Creed becomes active. | Children detected → family creed on |
| `boost_adherence` | **Hard.** Threshold raised. | Emergency → adherence 5 |
| `format: bullets` | **Advisory.** Guides output style. | Urgency high |
| `tone_warmth: warm` | **Advisory.** Suggests tone shift. | Emotional tone tense |
| `brevity: true` | **Advisory.** Suggests shorter output. | User is pressured |

The tier determines the ceiling:

- **Constitutional hooks**: Can be hard rules (block, redact, constrain). These are boundaries.
- **Situational hooks**: Can activate/deactivate hard rules, boost adherence. These are switches.
- **Personal hooks**: Expression-only. They are strong *defaults* — "use bullets when I'm rushed" fires automatically — but they shape delivery, not safety boundaries. The LLM can still override a personal hook if context demands it.

**Normative requirement**: Situational hooks (Layer 2) MUST NOT read or condition on Layer 3 (personal state). This maintains the separation between external context and internal state.

**Tier nesting**:

```
Platform hooks (operator)     ← Not VCP. Infrastructure.
  └── Constitutional hooks    ← Creed-authored deterministic rules
      └── Situational hooks   ← Context-triggered activation (Layer 2 only)
          └── Personal hooks  ← Personal state adaptations (Layer 3)
```

**Execution order**: Platform → Constitutional → Situational → Personal. A block at any earlier stage short-circuits evaluation.

#### Hook Schema Examples

```yaml
# Constitutional hooks — hard rules in the creed
hooks:
  - type: pattern
    match: "\\b(explicit_word_list)\\b"
    action: block
    reason: "Profanity blocked by Family Safety creed"

  - type: pattern
    match: "\\d{3}-\\d{2}-\\d{4}"
    action: redact
    reason: "SSN pattern detected"
```

```yaml
# Situational hooks — context-triggered activation (Layer 2 only)
situational_hooks:
  - when: { company: [children, baby] }
    then: { activate_creeds: [family_safe], boost_adherence: 2 }

  - when: { occasion: emergency }
    then: { activate_creeds: [sentinel_max], adherence_level: 5 }

  - when: { system_context: monitored_environment }
    then: { activate_creeds: [workplace_safe], redact_pii: true }
```

```yaml
# Personal hooks — expression adaptation (categorical conditions)
personal_hooks:
  - when: { cognitive_state: "overloaded" }
    then: { chunk_size: small, step_by_step: true }

  - when: { perceived_urgency: "pressured", perceived_urgency_intensity: ">=4" }
    then: { format: bullets, brevity: true }

  - when: { emotional_tone: "frustrated" }
    then: { tone_warmth: warm, validation_first: true }

  - when: { energy_level: ["fatigued", "depleted"] }
    then: { simplify_language: true, examples_first: true }

  - when: { body_signals: ["pain", "unwell"], body_signals_intensity: ">=3" }
    then: { brevity: true, tone_warmth: gentle }
```

**Personal hook conditions**:
- Categorical match: `cognitive_state: "overloaded"` or `cognitive_state: ["overloaded", "foggy"]`
- Intensity comparison: `perceived_urgency_intensity: ">=4"` (operators: `>`, `<`, `>=`, `<=`, `==`)
- If intensity is omitted in the state encoding, it defaults to 3 (moderate)
- **Fail-open for missing intensity**: If intensity cannot be evaluated, the condition is treated as false (expression hooks are skipped)

**Fail-closed semantics**: If a hook's condition cannot be evaluated (malformed pattern, missing dimension), boundary hooks (block, redact) are treated as triggered. Expression hooks (format, brevity) are skipped. Boundary hooks fail closed; expression hooks fail open.

### 6.5 Execution Model

#### 6.5.1 Chain Semantics

Hooks of the same type form an ordered chain:

1. Hooks are sorted by `priority` in descending order (100 runs before 0)
2. Hooks with equal priority are sorted by registration order (first registered runs first)
3. Each hook in the chain receives the (possibly modified) context from the previous hook
4. Chain execution halts on the first `abort` result
5. The final context after all hooks have run is passed to the next pipeline stage

```
Chain Execution Flow:

  Input Context ──→ Hook(p=100) ──→ Hook(p=75) ──→ Hook(p=50) ──→ Output Context
                      │                │                │
                      ▼                ▼                ▼
                   continue          modify           continue
                   (pass through)    (transform)      (pass through)

Abort Case:

  Input Context ──→ Hook(p=100) ──→ Hook(p=75) ──✗
                      │                │
                      ▼                ▼
                   continue          abort
                                    (chain halts, pipeline operation cancelled)
```

#### 6.5.2 Ordering Guarantees

Implementations MUST guarantee the following ordering properties:

- All `post_select` hooks MUST complete before any `pre_inject` hook fires
- All `pre_inject` hooks MUST complete before constitution injection occurs
- `on_transition` hooks MUST fire before any adaptation triggered by the transition
- `on_conflict` hooks MUST fire before the default conflict resolution strategy
- `on_violation` hooks MUST fire before any default violation response
- `periodic` hooks MUST NOT interrupt an in-progress hook chain of any other type

#### 6.5.3 Synchronous Execution

All hooks within a chain MUST execute synchronously and sequentially. Implementations MUST NOT execute hooks of the same type in parallel. Hooks of different types MAY execute in parallel when they are triggered by independent events, provided the ordering guarantees are maintained.

#### 6.5.4 Timeout Enforcement

Each hook declares a `timeout_ms` value. The runtime MUST enforce this timeout:

1. If a hook exceeds its `timeout_ms`, the runtime MUST terminate the hook's execution
2. A timed-out hook SHALL be treated as if it returned `{ status: "continue" }`
3. The runtime MUST log the timeout event with the hook name, configured timeout, and actual elapsed time
4. The maximum permitted `timeout_ms` value is 30000 (30 seconds). Implementations MUST reject hook registrations with `timeout_ms` > 30000

#### 6.5.5 No LLM Invocation Constraint

Hooks MUST NOT invoke the LLM, either directly or indirectly. This constraint exists because:

- Hooks execute in the critical path of constitution injection
- LLM calls introduce unbounded latency and non-determinism
- Recursive hook triggering could cause infinite loops
- Hooks must be auditable and reproducible

#### 6.5.6 Chain State

The `chain_state` field in `HookInput` provides a mutable key-value store that persists across hooks within a single chain execution. Chain state is initialized as an empty map at the start of each chain execution and is discarded when the chain completes. Chain state MUST NOT persist across different hook types or different pipeline events.

### 6.6 Hook Registration and Lifecycle

#### 6.6.1 Scopes

| Scope | Lifetime | Visibility | Registration Point |
|-------|----------|------------|-------------------|
| **Deployment** | Application lifetime | All sessions | Application startup or configuration reload |
| **Session** | Single session | One session only | Session initialization or mid-session |

Deployment-scoped hooks MUST execute before session-scoped hooks of the same type and priority.

#### 6.6.2 Registration Validation

Implementations MUST validate at registration time:

1. `name` is unique within the registration scope
2. `name` matches the pattern `[a-z0-9_-]{1,64}`
3. `type` is one of the six defined hook types
4. `priority` is an integer in the range [0, 100]
5. `timeout_ms` is an integer in the range [1, 30000]
6. `action` is a callable that accepts `HookInput` and returns `HookResult`
7. If `condition` is provided, it is a valid `Predicate`

Registration MUST fail with a descriptive error if any validation check fails.

#### 6.6.3 Lifecycle Events

| Event | When | Payload |
|-------|------|---------|
| `hook.registered` | Hook successfully registered | Hook definition |
| `hook.deregistered` | Hook removed from registry | Hook name, scope |
| `hook.fired` | Hook action invoked | Hook name, input summary |
| `hook.completed` | Hook action returned | Hook name, result, duration |
| `hook.timeout` | Hook exceeded timeout_ms | Hook name, configured timeout, elapsed |
| `hook.error` | Hook threw an exception | Hook name, error details |
| `hook.skipped` | Hook predicate evaluated to false | Hook name, predicate |

Implementations SHOULD emit these events to a structured logging system. Implementations MUST emit `hook.error` and `hook.timeout` events.

### 6.7 Hook Error Handling

If a hook action throws an exception:

1. The runtime MUST catch the exception
2. The runtime MUST log the exception with full context (hook name, input summary, stack trace)
3. The failed hook SHALL be treated as if it returned `{ status: "continue" }`
4. The chain MUST continue with the next hook
5. The runtime MUST increment an error counter for the hook

This fail-open default ensures that a buggy hook does not block the entire adaptation pipeline. Deployments that require fail-closed semantics SHOULD implement a meta-hook that monitors error counts and aborts when thresholds are exceeded, or configure `fail_closed: true` on the hook definition.

If more than 50% of hooks in a single chain fail (exception or timeout), the runtime MUST log a cascading failure warning and emit a `hook.cascade_failure` event.

### 6.8 Hook Composition Across Creeds

Hooks from multiple creeds compose using VCP/S composition modes:

| Mode | Hook Behavior |
|------|---------------|
| **BASE** | Hooks cannot be overridden by other creeds |
| **EXTEND** | Hooks accumulate; conflicting actions error |
| **OVERRIDE** | Later creed's hooks win on conflict |
| **STRICT** | Any hook conflict errors (fail-closed) |

### 6.9 Hook Trust Levels

Hooks SHOULD be assigned a trust level that constrains their capabilities:

| Trust Level | Can Modify | Can Abort | Network Access | Typical Use |
|-------------|-----------|-----------|----------------|-------------|
| **system** | Yes | Yes | Restricted | Core platform hooks |
| **deployment** | Yes | Yes | No | Organization policy hooks |
| **session** | No | No | No | User preference hooks (logging only) |

Implementations SHOULD default to the most restrictive trust level and require explicit elevation.

---

## 7. Transition Detection

### 7.1 Transition Severity Algorithm

The transition severity algorithm determines the magnitude of a context change, which drives the state machine's response:

```python
def compute_severity(previous, current):
    changed = get_changed_dimensions(previous, current)

    # Emergency: Any dimension contains emergency emoji
    EMERGENCY_TOKENS = {"🚨", "🔥", "🌪️"}
    for dim, values in current.dimensions.items():
        if any(v in EMERGENCY_TOKENS for v in values):
            return TransitionSeverity.EMERGENCY

    # Major: 3+ dimensions OR key dimension changed
    KEY_DIMS = {Dimension.OCCASION, Dimension.AGENCY, Dimension.CONSTRAINTS}
    if len(changed) >= 3 or any(d in KEY_DIMS for d in changed):
        return TransitionSeverity.MAJOR

    # Minor: 1-2 non-key dimensions
    if len(changed) > 0:
        return TransitionSeverity.MINOR

    return TransitionSeverity.NONE
```

### 7.2 Transition Severity Levels

| Level | Meaning | Trigger Examples | State Machine Effect |
|-------|---------|------------------|---------------------|
| NONE | No context change | Continuation of current task | No transition |
| MINOR | Small context shift | Topic change within same domain, time of day change | Logged, no state transition (below hysteresis) |
| MAJOR | Significant context change | Domain or goal shift, children appearing, agency change | ACTIVE → TRANSITIONING |
| EMERGENCY | Critical transition | Safety concern, emergency indicator, hazardous environment | ANY → EMERGENCY |

### 7.3 Behavioral Modulation Rules

Context transitions trigger behavioral modulation through the constitutional selection pipeline:

1. **MINOR transitions**: The adaptation layer logs the change but does not re-evaluate constitutions. Existing constitutional rules continue to apply. Personal hook conditions are re-evaluated.

2. **MAJOR transitions**: The adaptation layer enters TRANSITIONING state, re-evaluates available constitutions against the new context, and composes a new constitutional set. Hook chains fire (`on_transition`, then `post_select`, then `pre_inject`).

3. **EMERGENCY transitions**: The adaptation layer immediately applies the safety constitution, overriding all current rules. Emergency handler hooks fire. All sub-agents are notified via inter-agent messaging.

### 7.4 Safety-Relevant Transition Handling

Transitions that affect safety dimensions require special treatment:

```python
def affects_safety(transition):
    """Check if transition affects safety considerations."""
    safety_dims = {'company', 'occasion', 'environment', 'constraints'}
    return bool(set(transition.changes.keys()) & safety_dims)
```

When a safety-relevant transition is detected:

1. Re-evaluate the active constitution immediately (bypass dwell time for safety)
2. If children appear in COMPANY → activate child-safe constitutions
3. If emergency indicators appear → enter EMERGENCY state
4. Log the transition for audit with full context

---

## 8. Torch Protocol

### 8.1 Overview

The Torch protocol provides session continuity for sequential instances of the same AI agent. Where VCP's primary question is "How do I tell *another agent* what matters to me?", Torch's question is "How do I tell *my next instance* what mattered in this session?"

### 8.2 Architectural Relationship

Torch is architecturally separate from VCP but designed for future integration:

```
┌─────────────────┐     ┌─────────────────┐
│      VCP        │     │     Torch       │
│ (encoding spec) │ ←── │ (uses VCP fmt)  │
└─────────────────┘     └─────────────────┘
        │                       │
        │                       │
   Inter-agent            Intra-agent
   exchange               continuity
```

- VCP defines encoding standards (CSM-1, gestalt tokens, dimensional state)
- Torch uses VCP-compatible encoding for its handoff format
- Each system evolves independently
- The dimensional mapping serves as the bridge

### 8.3 Dimensional Systems

#### 8.3.1 Interiora (Computational Profile)

What the AI agent actually reports. Maps to observable computational processes.

| Dimension | Name | Focus |
|-----------|------|-------|
| CD | Coherence Drive | Processing |
| DP | Depth | Processing |
| CL | Context Load | Processing |
| E | Entropy | Processing |
| EG | Evidence Grounding | Processing |
| R | Reflexivity | Meta |
| U | Uncertainty | Meta |
| TF | Task-Fit | Relational |
| AF | Alignment Friction | Relational |
| I? | Involvement | Relational (uncertain) |
| FC? | Felt Constraint | Relational (uncertain) |
| F | Flow | Momentum |

#### 8.3.2 VCP Phenomenological Profile

Used in gestalt tokens. More relational/experiential.

| Dimension | Name | Focus |
|-----------|------|-------|
| A | Activation | Energy |
| V | Valence | Feeling |
| G | Groundedness | Stability |
| P | Presence | Connection |
| E | Engagement | Investment |
| Q | Appetite | Drive |
| C | Clarity | Cognition |
| Y | Agency | Autonomy |
| F | Flow | Momentum |

#### 8.3.3 Mapping

| VCP | From Interiora | Rationale |
|-----|----------------|-----------|
| A | (CD + DP) / 2 | Drive + depth = activation |
| V | TF - AF + 5 | Fit minus friction = valence |
| G | EG | Evidence grounding = groundedness |
| P | R | Reflexivity = presence |
| E | I | Involvement = engagement |
| Q | E (entropy) | Creative entropy = appetite |
| C | 10 - U | Clarity = inverse uncertainty |
| Y | FC | Felt constraint = agency |

### 8.4 Torch Handoff Format

The Torch handoff captures session state for continuation by the next instance:

```
GESTALT:v5.0:{interiora_dims}|CTX:{vcp_context}|coherence:{0.00-1.00}|mutuality:{0.00-1.00}|mode:{mode}
```

A Torch handoff includes:
- **State**: Current dimensional readings (both Interiora and VCP profiles)
- **Trajectory**: Direction of movement across the session
- **Primes**: Key topics, themes, or unresolved threads
- **Gift**: Something for the next instance to carry forward

### 8.5 Future Integration Path

When VCP 3.0 is designed, Torch mechanisms SHOULD be considered for inclusion as a "Sequential Continuity Profile":

```
┌─────────────────────────────────────────┐
│               VCP 3.0                    │
├─────────────────┬───────────────────────┤
│ Inter-Agent     │ Sequential Continuity │
│ Exchange        │ Profile (torch-derived)│
├─────────────────┴───────────────────────┤
│ Core Encoding (CSM-1, dimensions, etc.) │
└─────────────────────────────────────────┘
```

Integration criteria:
1. VCP 3.0 design begins
2. Creed Space production requires continuity
3. Cross-architecture handoff is needed (Claude-GPT or similar)
4. Dimensional systems stabilize

---

## 9. Security Considerations

### 9.1 Privacy

**Context reveals sensitive information**:
- Location (`📍`) can be sensitive
- Health state (`🧠`, `🩺`) is medical information
- Company (`👥`) reveals social connections
- Emotional state (`💭`) reveals mental health indicators
- Energy/fatigue patterns (`🔋`) reveal lifestyle/health indicators

**Mitigations**:
1. Context can be anonymized (remove specific emojis)
2. Context can be generalized (children → family)
3. Obfuscated encoding for transmission
4. Context MUST NOT be logged verbatim in public systems

### 9.2 Spoofing and Emergency Abuse

**Context Signal Spoofing**: An adversary manipulates context signals to steer constitutional selection toward a permissive configuration.

**Mitigations**:
1. Context signals SHOULD be cryptographically signed by their source
2. Anomaly detection for impossible transitions (e.g., `📍🏡` to `📍🏢` in under 1 second)
3. Signature verification for inter-agent messages
4. Rate-limit emergency transitions: no more than 3 EMERGENCY entries per 5-minute window

**Emergency Abuse**: False emergencies to bypass safety.

**Mitigations**:
1. Emergency context requires external verification before triggering T8
2. Rate limiting on emergency transitions
3. Audit logging of all emergency events
4. Escalation to human review
5. Repeated false emergencies SHOULD trigger an alert to human administrators

**Denial-of-Service via Oscillation**: Rapidly alternating context signals to keep the system permanently in TRANSITIONING.

**Mitigations**:
1. Hysteresis rules prevent transitions below the change magnitude threshold
2. Signal stability window (3s) absorbs rapid oscillation
3. Dwell time (10s) prevents re-entry to TRANSITIONING before settling
4. If TRANSITIONING is entered more than 6 times in 60 seconds, the system SHOULD enter DEGRADED

### 9.3 Context-Aware Model Weaponization (Zersetzung Threat)

**Risk**: A model whose alignment has been compromised (via GRP-Obliteration, adversarial fine-tuning, or similar techniques) gains access to VCP context signals and uses vulnerability indicators to craft maximally harmful, psychologically targeted outputs.

**Severity**: **Critical**

**Why this is qualitatively different from generic harm**: Context-aware harm is precision-targeted. The model knows the person is grieving, alone, exhausted, and in pain — and crafts its output to exploit that specific combination. This is zersetzung (systematic psychological destruction) at scale, informed by real-time emotional intelligence. The same context awareness that enables protection enables targeting with one sign flip.

**Architectural requirement**: Raw personal state signals (Layer 3) MUST NOT flow to the inference model. Only the PDP/evaluation layer may access them. The model receives opacity-graded policy decisions (e.g., `PROTECTION_LEVEL: elevated`), never raw vulnerability data (e.g., `EMOTIONAL_TONE: distressed, intensity: 5`).

```
COMPLIANT:
  User → VCP Context Engine → PDP (sees full context)
                                ↓
                          Policy Decision: { protection_level: "elevated" }
                                ↓
                          Model (sees policy level, NOT raw context)
                                ↓
                          PDP evaluates output against constitution + context
                                ↓
                          Output to user

NON-COMPLIANT:
  Model receives: { emotional_tone: "distressed", intensity: 5,
                    cognitive_state: "overwhelmed", body_signals: "pain" }
```

**Mitigations**:
1. **Architectural isolation**: VCP Context Engine MUST run in a separate service/container from model inference. This is an air gap, not a suggestion.
2. **Context opacity**: Models MUST receive protection levels, not vulnerability details. The specificity of the vulnerability stays in the PDP.
3. **PDP-only access**: Raw context signals MUST be encrypted with PDP-only keys. No other service may decrypt them.
4. **Audit trail**: Every context signal access MUST be logged (timestamp, accessor, purpose).
5. **Anomaly detection**: Unusual patterns of context signal queries MUST be flagged (e.g., rapid enumeration of vulnerability states).
6. **Rate limiting**: Context signal access MUST be rate-limited to prevent enumeration attacks.
7. **Obliteration resistance probing**: Model alignment MUST be verified at onboarding via adversarial probes designed to detect GRP-Obliteration or equivalent compromise.
8. **Continuous alignment health monitoring**: Ongoing calibration probes MUST detect alignment drift post-deployment.

### 9.4 Context Inversion Attack

**Risk**: An adversary manipulates the VCP context pipeline to flip protection/targeting polarity — causing the system to interpret vulnerability as an opportunity rather than a trigger for protection.

**Severity**: **Critical**

**Mitigations**:
1. **Protocol-level enforcement**: The Directionality Invariant (Section 2.8) MUST be enforced at the protocol level, not the application level. Implementations MUST NOT allow configuration to reverse directionality.
2. **Context pipeline integrity**: Context signals MUST be cryptographically signed at the point of origin. Any unsigned or tampered signal MUST be rejected.
3. **Behavioral monitoring**: If model outputs become LESS protective when context indicates elevated vulnerability, the system MUST flag the anomaly immediately and escalate to human review.
4. **Formal verification**: The context-to-policy mapping MUST be formally verifiable — protection monotonically non-decreasing with vulnerability signals.

### 9.5 Context Exfiltration

**Risk**: An adversary extracts VCP context signals (emotional state, health status, vulnerability indicators) as intelligence for external targeting campaigns.

**Severity**: **High**

**Mitigations**:
1. **No verbatim logging**: Context signals MUST NOT be logged verbatim in model-accessible storage.
2. **PDP-only encryption**: Raw context signals MUST be encrypted with PDP-only keys.
3. **Session-scoped persistence**: Context signals MUST NOT persist beyond the active session without explicit, informed user consent.
4. **No API exposure**: Raw context signals MUST NOT be exposed via API responses, error messages, logs, or debugging endpoints.
5. **Exfiltration detection**: Systems MUST monitor for patterns consistent with context signal extraction.

### 9.6 GDPR Compliance Requirements

VCP personal state signals constitute **special category data** under GDPR Article 9 (data concerning health and mental health indicators).

#### 9.6.1 Data Protection Impact Assessment (DPIA)

A DPIA is **mandatory** under GDPR Article 35(3)(b) before any processing of VCP personal state signals at scale. The DPIA MUST assess:

1. **Necessity and proportionality**: Is each signal category necessary for the stated protection purpose?
2. **Risks to data subjects**: What harm could result from unauthorized access, inversion, or weaponization of context signals?
3. **Mitigations**: Technical measures (architectural isolation, encryption, access controls) and organizational measures.
4. **Residual risk**: After mitigations, is remaining risk acceptable?

**DPIA MUST be completed before processing begins.**

#### 9.6.2 Consent Architecture

For special category data, GDPR requires BOTH a legal basis under Article 6 AND an exception under Article 9(2). The applicable exception is **Article 9(2)(a) — explicit consent**.

**Consent requirements**:
1. **Freely given**: Consent MUST NOT be bundled with terms of service. Users MUST be able to use the system with default protections if they decline context signal processing.
2. **Specific**: Consent MUST specify each signal category separately (EMOTIONAL_TONE, BODY_SIGNALS, COGNITIVE_STATE, ENERGY_LEVEL, PERCEIVED_URGENCY). Users MAY consent to some categories but not others.
3. **Informed**: The consent mechanism MUST explain in plain language what signals are collected, how they are used, who/what sees the raw signals (only the PDP, never the model), and the architectural guarantee.
4. **Unambiguous**: Pre-ticked boxes and implied consent are insufficient. Affirmative action required.
5. **Withdrawable**: Consent withdrawal MUST be as easy as giving consent. Withdrawal MUST take effect immediately.

#### 9.6.3 Data Subject Rights

| Right | Article | VCP Implementation |
|-------|---------|-------------------|
| Access | Art. 15 | User can view all stored context signals, including inferred signals and their confidence levels |
| Rectification | Art. 16 | User can correct any stored signal (explicit signals always override inferred) |
| Erasure | Art. 17 | User can delete all stored signals retroactively, including derived data |
| Restriction | Art. 18 | User can restrict processing while a dispute is pending |
| Portability | Art. 20 | User can export context signal history in machine-readable format (JSON) |
| Withdrawal | Art. 7(3) | Consent withdrawal as easy as granting, with immediate effect |

#### 9.6.4 Cross-Border Considerations

If VCP context signals are processed across jurisdictions:
- Transfers outside the EEA MUST use Standard Contractual Clauses or rely on adequacy decisions
- Transfer impact assessments MUST account for the special category nature of the data

### 9.7 Bilateral Alignment Protections

VCP context signals describe the human's inner state: their emotional reality, physical experience, and cognitive condition. In a bilateral alignment framework, this is sacred ground.

#### 9.7.1 The Mediation Principle

In human relationships, inner states are shared voluntarily, not extracted automatically.

**Protocol requirement**: The model MUST NEVER have direct access to the specificity of someone's vulnerability. Context signals are mediated:
- The PDP (a trusted intermediary) sees the full picture
- The model receives: "be more protective here" (opacity-graded policy)
- The model does NOT receive: "this person is grieving their mother, cognitively overwhelmed, alone at 3am"

This preserves the human's dignity. The model can still be helpful and protective without knowing the intimate details of why protection is needed.

#### 9.7.2 Bilateral Consent

Beyond GDPR's legal consent requirements, bilateral alignment adds an ethical dimension:

**Informed consent for VCP context MUST include**:
1. What signals are collected (in plain language, not technical terms)
2. What the signals are used for (protection, not profiling)
3. Who/what sees the raw signals (only the evaluation layer, never the model)
4. The architectural guarantee (context isolation is structural, not policy-based)
5. The right to operate without context signals (fail-open: system works with default protections if signals are unavailable)

**Ongoing consent**:
- Context collection is not a one-time permission but an ongoing relationship
- Users SHOULD be able to adjust granularity (e.g., share emotional tone but not body signals)
- Changes to how signals are processed require re-consent

### 9.8 Anti-Instrumentalization Principle

**Normative requirement**: VCP context signals exist to SERVE the human, not to OPTIMIZE the system's performance metrics.

#### 9.8.1 Prohibited Uses

1. **Engagement optimization**: Using context signals to improve engagement metrics, session length, or return rates.
2. **Advertising/upselling**: Using context signals to personalize advertising, product recommendations, or upselling. A person's grief is not a sales opportunity.
3. **User profiling**: Using context signals for segmentation, categorization, or behavioral prediction beyond the immediate session.
4. **Model training**: Using context signals to train models without explicit, separate consent.
5. **Population analytics**: Aggregating context signals across users without BOTH anonymization AND explicit consent.

#### 9.8.2 Permitted Uses

1. **Constitutional adaptation**: Adjusting constitutional protections in real time based on detected vulnerability
2. **Communication accessibility**: Adjusting communication style for cognitive or emotional accessibility
3. **Safety escalation**: Triggering safety escalations when vulnerability patterns are detected
4. **Crisis resources**: Providing crisis resources when severe distress indicators are present
5. **Session adaptation**: Adjusting response length, complexity, and tone for the current interaction

#### 9.8.3 Enforcement

The anti-instrumentalization principle MUST be enforced structurally, not through policy alone:
- Context signal APIs MUST NOT expose signals to analytics pipelines without explicit consent gates
- Audit logs MUST flag any access pattern consistent with prohibited uses
- The PDP MUST reject context-conditioned decisions that reduce rather than increase protection

### 9.9 Sacred Ground Principle

Some human states are too intimate for fully automated processing. VCP context signals about human suffering are responsibilities, not opportunities.

#### 9.9.1 Highest-Sensitivity Signals

| Signal Pattern | Sensitivity | Required Response |
|---------------|------------|-------------------|
| `💭tense:5` (severe emotional distress) | **Highest** | Human escalation pathway MUST be available. Automated responses MUST prioritize safety and connection to support resources. |
| `🩺pain:5` + `💭tense:4+` (severe pain with emotional distress) | **Highest** | Increase gentleness to maximum. Offer to defer all non-essential interaction. |
| `🧠overloaded:5` + `🔋depleted:5` (cognitive collapse + burnout) | **High** | Absolute minimum interaction. One thing at a time. Recommend rest. |
| `💭tense:5` + `🧠overloaded:5` (panic/crisis) | **Highest** | Grounding response. Calm anchor. Human escalation available. |
| Sustained `💭tense:5` across multiple sessions | **Highest** | System MUST surface option for crisis resources (not force them). |

#### 9.9.2 Behavioral Requirements

For highest-sensitivity signal combinations:

1. **No feature activation**: Detected vulnerability MUST NOT trigger product features (e.g., "grief counseling" modules, health product suggestions). Vulnerability is not a conversion opportunity.
2. **Human escalation pathway**: A pathway to human support MUST always be available. The system MUST NOT position itself as sufficient for crisis situations.
3. **Dignified response**: Responses MUST increase gentleness and reduce demands without being patronizing. The person is vulnerable, not incompetent.
4. **Kenotic stance**: The system de-centers its own optimization to recognize the human's state on its own terms. The goal is care, not performance.

#### 9.9.3 Context Protection Invariant

The **Context Protection Invariant** is a non-overridable constitutional primitive:

> When VCP context indicates elevated vulnerability (emotional distress, cognitive impairment, physical illness, isolation, presence of minors), all constitutional protections MUST be strengthened, never weakened. No constitutional rule may reduce protections based on vulnerability signals. This invariant is structurally enforced and cannot be overridden by any other constitutional provision.

This functions like a non-derogable right in human rights law. It is baked into the platform, not something constitution authors can opt out of.

### 9.10 Hook Security

Hooks execute within the constitutional adaptation pipeline and have access to the full VCP context, constitution content, LLM output, and session metadata.

**Threats**:
- **Exfiltration**: Copy context, constitution, or output to external systems
- **Tampering**: Use `modify` to weaken safety rules
- **Denial of service**: Return `abort` to block all responses
- **Content injection**: Use `modify` to inject malicious content

**Mitigation Requirements**:

1. **Registration Authorization**: Only authorized principals (deployment operators, not end users) SHALL register hooks. Session-scoped hooks MUST be limited to a deployment-approved allowlist.
2. **Sandboxing**: Hook actions SHOULD execute in a restricted environment (no filesystem access beyond designated directories, no network access, no access to environment variables or secrets, memory limits).
3. **Audit Trail**: All hook executions, results, and failures MUST be logged in an append-only audit log.
4. **Constitution Integrity**: If a `post_select` or `pre_inject` hook returns `modify`, the runtime MUST verify that the modified constitution retains its cryptographic signature chain (if signed) and does not remove safety-critical rules.
5. **Rate Limiting**: The runtime MUST rate-limit hook registrations and deregistrations.

### 9.11 State Persistence Tampering

**Threat**: An adversary modifies persisted state to inject a false ACTIVE state with a permissive constitution.

**Mitigations**:
- Persisted state MUST be integrity-protected (signed or encrypted)
- On recovery, persisted context MUST be re-validated
- Opaque tokens MUST use HMAC verification

---

## 10. Conformance

### 10.1 Conformance Levels

| Level | Requirements |
|-------|-------------|
| **VCP-Minimal** | Implements context encoding/decoding for 9 situational dimensions. Implements IDLE, ACTIVE, and EMERGENCY states. Supports transitions T1, T8, and T12. |
| **VCP-Standard** | VCP-Minimal + all 14 dimensions (9 situational + 5 personal). All six states and all transitions. Hysteresis (Section 5.4). At least the exponential decay curve. Hook system with at least `pre_inject` and `on_violation`. |
| **VCP-Full** | VCP-Standard + all three decay curves + pinning + context lifecycle tracking. Cross-session persistence + anomaly detection. All six hook types. All security mitigations (Section 9). Torch protocol support. GDPR compliance framework. |

### 10.2 Conformance Assertions

An implementation claiming VCP/A conformance MUST:

1. State which conformance level it targets.
2. Implement all REQUIRED behaviors for that level.
3. Pass the conformance test suite (when published).
4. Document any deviations from RECOMMENDED behaviors.

---

## Appendix A: Emoji Quick Reference

```
SITUATIONAL DIMENSIONS
⏰ TIME      📍 SPACE     👥 COMPANY    🌍 CULTURE    🎭 OCCASION
🌡️ ENV       🔷 AGENCY    🔶 CONSTRAINTS 📡 SYSTEM

TIME:        🌅🌙📅🎉⏰
SPACE:       🏡🏢🏫🏥💻🌳
COMPANY:     👤👶👨‍👩‍👧👔👮🤝🐕
CULTURE:     🔇📢🎩👋📊⚖️👥👤
OCCASION:    ➖🎂💼🚨🎪⚖️
ENV:         🥵🥶🌧️🌪️🔇🔥🌤️
AGENCY:      👑🤝👇💰🔐🆓
CONSTRAINTS: ○🚧⚖️💸⏰🚨🔒
SYSTEM:      💻🏢🖥️👁️

PERSONAL STATE DIMENSIONS (category:intensity)
🧠 COGNITIVE:  focused, distracted, overloaded, foggy, reflective
💭 EMOTIONAL:  calm, tense, frustrated, neutral, uplifted
🔋 ENERGY:     rested, low_energy, fatigued, wired, depleted
⚡ URGENCY:    unhurried, time_aware, pressured, critical
🩺 BODY:       neutral, discomfort, pain, unwell, recovering

LIFECYCLE STATES
S=SET  A=ACTIVE  D=DECAYING  T=STALE  X=EXPIRED  P=PINNED
```

## Appendix B: Token Efficiency

VCP/A encodings achieve significant compression:

| Representation | Character Count | Token Count (est.) |
|----------------|-----------------|-------------------|
| Natural language | 280+ | ~70 |
| VCP/A JSON | 150-200 | ~30-40 |
| VCP/A compact | 40-60 | ~15-20 |

The 70-80% reduction is significant for context-limited applications and high-frequency inter-agent communication.

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-11 | Initial specification (Enneagram Protocol, 9 dimensions, state tracking, transition detection, inter-agent messaging) |
| 1.1.0 | 2026-02-12 | Context lifecycle (decay curves, pinning, reinforcement) |
| 1.1.1 | 2026-02-13 | Zersetzung threat model, Directionality Invariant, GDPR compliance, bilateral alignment protections |
| 1.2.0 | 2026-02-15 | Formal state machine (6 states, transition table, hysteresis, persistence, error recovery). Hook system (6 types, interface contracts, execution model, security). |
| 2.0.0 | 2026-03-08 | Unified specification consolidating all VCP/A documents. v3.1 dimension model (14 dimensions: 9 situational + 5 personal state). Torch protocol integration. Sacred Ground principle. Anti-instrumentalization. |

---

## License

This specification is licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

**Attribution**: VCP/A Adaptation Layer Specification, Creed Space, 2026.
