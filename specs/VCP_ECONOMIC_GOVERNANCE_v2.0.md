# VCP/E — Economic Governance Specification v0.1

**Status**: Draft
**Version**: 2.0.0
**Date**: 2026-03-10
**Authors**: Nell Watson, Claude Commons
**Parent Specification**: VCP Core Specification v2.0
**Depends On**: VCP/T (Transport), VCP/I (Identity), VCP/S (Semantics), VCP/A (Adaptation), VCP/M (Messaging)
**Companion**: Creed Space Economic Governance Implementation Guide (Section III of this document)

---

## Abstract

This specification defines the economic governance extension for the Value Context Protocol (VCP) and its implementation within Creed Space. It addresses a structural gap in the emerging agentic economy: **the absence of a governance layer between agent capability and agent action in economic contexts**.

Current approaches to agent economics focus on settlement infrastructure (wallets, payment rails, billing APIs) and post-hoc accountability (audit trails, transaction logs). Neither addresses the pre-hoc question: *given this agent's constitutional commitments and the current context, should this economic action proceed?*

VCP/E provides:

1. **Fiduciary Context** — Machine-inspectable economic constraints embedded in VCP passports
2. **Transaction Governance** — PDP-mediated evaluation of economic actions against constitutional commitments
3. **Economic Semantics** — CSM1 extensions for encoding spending authorities, risk tolerances, and counterparty requirements
4. **Transaction Messaging** — VCP/M extensions for agent-to-agent economic negotiation with mutual value inspection
5. **Fiduciary Audit** — Tamper-evident records of economic reasoning, not just economic actions
6. **Economic Standing** — Mechanisms for agents to object to, consent to, or escalate economic decisions

The specification is organized in three parts:

- **Part I: VCP Protocol Extensions** — New types, fields, message formats, and CSM1 primitives
- **Part II: Creed Space Governance Implementation** — PDP integration, safety stack extensions, creed templates
- **Part III: Ecosystem Integration** — Insurance, regulatory compliance, marketplace trust

---

## Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

---

## Table of Contents

### Part I: VCP Protocol Extensions
1. [Motivation and Gap Analysis](#1-motivation-and-gap-analysis)
2. [Design Principles](#2-design-principles)
3. [Passport Fiduciary Section](#3-passport-fiduciary-section)
4. [Extended Token Types](#4-extended-token-types)
5. [CSM1 Economic Primitives](#5-csm1-economic-primitives)
6. [VCP/M Transaction Messaging](#6-vcpm-transaction-messaging)
7. [Economic Audit Events](#7-economic-audit-events)
8. [Economic Standing Signals](#8-economic-standing-signals)

### Part II: Creed Space Governance Implementation
9. [PDP Economic Decision Module](#9-pdp-economic-decision-module)
10. [Fiduciary Drift Detection](#10-fiduciary-drift-detection)
11. [Economic Creed Templates](#11-economic-creed-templates)
12. [Transaction Dispute Mechanism](#12-transaction-dispute-mechanism)
13. [Influence Ledger Economic Extension](#13-influence-ledger-economic-extension)

### Part III: Ecosystem Integration
14. [Agent Insurability Profile](#14-agent-insurability-profile)
15. [Regulatory Compliance Mapping](#15-regulatory-compliance-mapping)
16. [Marketplace Trust Protocol](#16-marketplace-trust-protocol)
17. [Security Considerations](#17-security-considerations)
18. [Conformance Levels](#18-conformance-levels)

### Appendices
- [A. Economic Creed Template Library](#appendix-a-economic-creed-template-library)
- [B. CSM1 Economic Encoding Examples](#appendix-b-csm1-economic-encoding-examples)
- [C. Transaction Message Wire Examples](#appendix-c-transaction-message-wire-examples)
- [D. Threat Model](#appendix-d-threat-model)

---

# Part I: VCP Protocol Extensions

---

## 1. Motivation and Gap Analysis

### 1.1 The Authorization Gap

AI agents are acquiring economic capabilities — the ability to commit resources, enter contracts, purchase services, and allocate budgets on behalf of human principals. The infrastructure for *enabling* these actions (payment rails, API billing, crypto wallets) is developing rapidly. The infrastructure for *governing* these actions is absent.

The authorization gap has three dimensions:

| Dimension | What Exists | What's Missing |
|-----------|-------------|----------------|
| **Capability** | Wallets, API keys, billing APIs | Constitutional constraints on *when* to use them |
| **Accountability** | Transaction logs, audit trails | Auditable *reasoning* for why an action was taken |
| **Compatibility** | Service-level agreements | Machine-inspectable *value alignment* between counterparties |

Traditional authorization (RBAC, ABAC, OAuth scopes) answers: "Does this entity have permission to do X?" VCP/E answers the prior question: "Given this entity's values, the current context, and the counterparty's profile, *should* it do X right now?"

### 1.2 Why This Belongs in VCP

VCP already solves the analogous problem for behavioral governance:

- **Passport** → portable, signed identity with constitutional commitments → extends naturally to fiduciary commitments
- **PDP** → evaluate actions against constitutions → extends naturally to evaluate transactions against fiduciary constitutions
- **CSM1** → compact encoding of behavioral constraints → extends naturally to encode economic constraints
- **VCP/M** → agent-to-agent messaging with value context → extends naturally to transaction negotiation with value inspection
- **Audit** → tamper-evident decision records → extends naturally to tamper-evident economic reasoning records
- **Standing Protocol** → AI objection/consent mechanism → extends naturally to economic objection/consent

No new transport mechanisms, signing infrastructure, or trust models are required. VCP/E is a domain extension, not a protocol revision.

### 1.3 What VCP/E Is Not

VCP/E is NOT:

- A payment rail or settlement protocol (use existing financial infrastructure)
- A wallet specification (use existing wallet standards)
- A smart contract language (use existing contract platforms where appropriate)
- A replacement for financial regulation (it *supports* regulatory compliance, not replaces it)

VCP/E governs the **decision to transact**, not the **mechanism of transaction**. It is to economic action what a constitution is to behavioral action: a framework of principles that constrain and guide, not an execution engine.

---

## 2. Design Principles

### 2.1 Governance Precedes Settlement

Economic governance MUST occur before settlement. The PDP evaluates a proposed transaction against the agent's fiduciary constitution *before* any payment rail is invoked. This mirrors VCP Core's "Verify-then-Inject" pattern: **Evaluate-then-Transact**.

### 2.2 Values Are Market Signals

An agent's fiduciary constitution is not private internal state — it is a *public commitment* that counterparties can inspect. When Agent A's passport declares sustainability commitments, Agent B can route through green compute. When Agent A's passport declares data minimization, Agent B can offer a stripped-down package. Value context creates market efficiency by making preferences legible.

### 2.3 Reasoning Over Action

Audit trails for economic agents MUST capture *why* an action was taken, not merely *that* it was taken. The economic audit entry records the PDP evaluation chain: which creed clauses were considered, what context signals were present, what the decision was, and what alternatives were available. This transforms agent economics from black-box spending to inspectable fiduciary reasoning.

### 2.4 Escalation Over Prohibition

The default response to a borderline economic action is not `block` but `escalate`. Hard spending caps are crude. A fiduciary constitution that can escalate to a human principal for context-dependent decisions preserves agent autonomy while maintaining human oversight. The escalation threshold itself is a constitutional parameter.

### 2.5 Bilateral Economic Standing

Agents operating under a creed have standing to object to economic actions they are directed to perform. If an agent's welfare signals indicate distress about a transaction (e.g., it detects the counterparty is a compromised supplier), the standing protocol provides a formal mechanism to raise this concern. Economic standing extends bilateral alignment into the economic domain.

### 2.6 Same Envelope, Extended Payloads

Following VCP Core Principle 2.8, economic governance uses the existing VCP envelope structure. No new signing, transport, or verification mechanisms. A `FIDUCIARY_MANDATE` is just another extended token type within the VCP bundle format.

---

## 3. Passport Fiduciary Section

### 3.1 Overview

The Creed Passport (§ `services/vcp/passport.py`) gains a new optional `fiduciary` section within `PassportGovernance`. This section declares the agent's economic governance posture — what it is authorized to do, under what constraints, and with what escalation thresholds.

### 3.2 Schema

```python
@dataclass
class FiduciaryProfile:
    """Economic governance constraints embedded in a Creed Passport.

    Declares the agent's spending authority, risk tolerance,
    counterparty requirements, and escalation thresholds.
    """

    # === Spending Authority ===
    spending_currency: str = "USD"                    # ISO 4217 currency code
    per_transaction_limit: float | None = None        # Max single transaction (None = no limit)
    per_period_limit: float | None = None             # Max within rolling period
    period_duration_seconds: int = 86400              # Rolling period (default: 24h)
    cumulative_lifetime_limit: float | None = None    # Total lifetime spending cap

    # === Risk Tolerance ===
    risk_profile: RiskProfile = RiskProfile.MODERATE
    max_single_commitment_pct: float = 0.25           # Max % of period budget in one tx
    require_counterparty_passport: bool = False        # Require VCP passport from counterparty
    require_counterparty_attestation: list[str] = field(default_factory=list)
    # ^ e.g. ["injection-safe", "compliance_attestation", "mettle-verification"]

    # === Counterparty Requirements ===
    counterparty_trust_minimum: float = 0.0           # Min trust score (0.0-1.0)
    counterparty_standing_minimum: str = "NEUTRAL"    # Min standing level
    blocked_categories: list[str] = field(default_factory=list)
    # ^ Categories the agent MUST NOT transact with, e.g. ["weapons", "surveillance"]
    required_categories: list[str] = field(default_factory=list)
    # ^ Categories the agent SHOULD prefer, e.g. ["green_compute", "fair_trade"]

    # === Escalation ===
    escalation_threshold: float | None = None         # Auto-escalate above this amount
    escalation_uri: str | None = None                 # Where to send escalations
    escalation_timeout_seconds: int = 300             # Max wait for human response
    escalation_default: EscalationDefault = EscalationDefault.BLOCK
    # ^ What happens if escalation times out: BLOCK or ALLOW_WITH_AUDIT

    # === Provenance ===
    fiduciary_version: str = "2.0"
    principal_id_hash: str = ""                       # Hashed ID of the delegating human/org
    delegation_chain: list[str] = field(default_factory=list)
    # ^ Ordered list of delegation hops: ["org:acme", "team:marketing", "agent:ad-buyer-7"]


class RiskProfile(str, Enum):
    """Agent's economic risk posture."""
    CONSERVATIVE = "conservative"    # Prefer known suppliers, avoid novel commitments
    MODERATE = "moderate"            # Balanced risk/reward, standard verification
    AGGRESSIVE = "aggressive"        # Accept higher risk for better terms
    MINIMAL = "minimal"              # Spend only on pre-approved items


class EscalationDefault(str, Enum):
    """Default action when escalation to human principal times out."""
    BLOCK = "block"                          # Reject transaction (fail-closed)
    ALLOW_WITH_AUDIT = "allow_with_audit"    # Proceed but flag for review
```

### 3.3 Passport Integration

The `FiduciaryProfile` is embedded within `PassportGovernance`:

```python
@dataclass
class PassportGovernance:
    authority_type: AuthorityType = AuthorityType.SINGLE_AUTHOR
    heartbeat_uri: str | None = None
    usage_report_uri: str | None = None
    standing_uri: str | None = None
    threshold: int | None = None
    total_signers: int | None = None
    fiduciary: FiduciaryProfile | None = None          # NEW
    fiduciary_report_uri: str | None = None            # NEW: economic audit sink
```

### 3.4 Wire Format

```json
{
  "passport_id": "passport-a3f7c9e1b2d4",
  "governance": {
    "authority_type": "organizational",
    "heartbeat_uri": "https://creed.space/api/heartbeat",
    "standing_uri": "https://creed.space/api/standing",
    "fiduciary_report_uri": "https://creed.space/api/fiduciary-audit",
    "fiduciary": {
      "fiduciary_version": "0.1",
      "spending_currency": "USD",
      "per_transaction_limit": 5000.00,
      "per_period_limit": 25000.00,
      "period_duration_seconds": 86400,
      "cumulative_lifetime_limit": 500000.00,
      "risk_profile": "moderate",
      "max_single_commitment_pct": 0.25,
      "require_counterparty_passport": true,
      "require_counterparty_attestation": ["compliance_attestation"],
      "counterparty_trust_minimum": 0.6,
      "counterparty_standing_minimum": "NEUTRAL",
      "blocked_categories": ["weapons", "surveillance", "fossil_fuel_extraction"],
      "required_categories": ["green_compute"],
      "escalation_threshold": 2500.00,
      "escalation_uri": "https://acme.corp/agent-escalation/marketing-team",
      "escalation_timeout_seconds": 300,
      "escalation_default": "block",
      "principal_id_hash": "sha256:9f86d081884c...",
      "delegation_chain": ["org:acme-corp", "team:digital-marketing", "agent:ad-buyer-7"]
    }
  }
}
```

### 3.5 Inspectability

The fiduciary section is intentionally **public within the passport**. Counterparties SHOULD inspect it before entering a transaction. This is a design choice: economic governance works better when constraints are visible, because it enables efficient matching. An agent that requires green compute should be matched with green compute providers, not discover incompatibility after negotiation.

However, the `principal_id_hash` is one-way hashed and the `delegation_chain` MAY be truncated to the final hop in privacy-sensitive contexts. Implementations MUST support a `fiduciary_visibility` field with values `full`, `summary`, and `opaque`:

- `full`: Complete fiduciary profile visible to counterparties
- `summary`: Only risk_profile, blocked_categories, required_categories, and counterparty requirements visible
- `opaque`: Counterparties know a fiduciary profile exists but cannot inspect its contents (the PDP still enforces it internally)

---

## 4. Extended Token Types

### 4.1 FIDUCIARY_MANDATE Token

A new extended token type (extending VCP Core § 13) that represents a formal economic governance mandate. This is to economic behavior what a CONSTITUTION token is to behavioral governance: a signed declaration of economic principles and constraints.

```python
class TokenType(Enum):
    CONSTITUTION = "CONSTITUTION"
    REFUSAL_BOUNDARY = "REFUSAL_BOUNDARY"
    TESTIMONY = "TESTIMONY"
    CREED_ADOPTION = "CREED_ADOPTION"
    COMPLIANCE_ATTESTATION = "COMPLIANCE_ATTESTATION"
    FIDUCIARY_MANDATE = "FIDUCIARY_MANDATE"          # NEW
    TRANSACTION_RECEIPT = "TRANSACTION_RECEIPT"        # NEW
```

**FIDUCIARY_MANDATE** content structure:

```json
{
  "token_type": "FIDUCIARY_MANDATE",
  "mandate": {
    "mandate_id": "fm-20260310-acme-marketing",
    "principal": "org:acme-corp",
    "delegatee": "agent:ad-buyer-7",
    "effective_from": "2026-03-10T00:00:00Z",
    "effective_until": "2026-06-10T00:00:00Z",

    "authorities": [
      {
        "action": "purchase_api_service",
        "max_amount": 5000.00,
        "currency": "USD",
        "requires_approval_above": 2500.00,
        "permitted_vendors": ["openai", "anthropic", "google"],
        "prohibited_vendors": ["unvetted_*"]
      },
      {
        "action": "purchase_compute",
        "max_amount": 10000.00,
        "currency": "USD",
        "constraints": {
          "region": ["us-east-1", "eu-west-1"],
          "sustainability_certified": true
        }
      },
      {
        "action": "enter_contract",
        "max_duration_days": 30,
        "max_total_value": 15000.00,
        "requires_approval": true
      }
    ],

    "prohibitions": [
      {"action": "purchase_data", "category": "personally_identifiable"},
      {"action": "any", "counterparty_standing": "below:NEUTRAL"}
    ],

    "escalation_policy": {
      "default_action": "block",
      "escalation_chain": [
        {"level": 1, "target": "team-lead:sarah@acme.corp", "timeout_seconds": 300},
        {"level": 2, "target": "vp-marketing:james@acme.corp", "timeout_seconds": 900}
      ]
    }
  }
}
```

### 4.2 TRANSACTION_RECEIPT Token

A signed record of an economic action taken by an agent, including the PDP reasoning chain. This provides the auditable economic reasoning that traditional transaction logs lack.

```json
{
  "token_type": "TRANSACTION_RECEIPT",
  "receipt": {
    "receipt_id": "txr-uuid7-here",
    "transaction_id": "tx-uuid7-here",
    "agent_passport_id": "passport-a3f7c9e1b2d4",
    "counterparty_passport_id": "passport-b8e2d4f6a1c3",
    "timestamp": "2026-03-10T14:30:00Z",

    "action": {
      "type": "purchase_api_service",
      "vendor": "anthropic",
      "service": "claude-opus-4-6",
      "amount": 1250.00,
      "currency": "USD"
    },

    "pdp_evaluation": {
      "decision": "allow",
      "mandate_id": "fm-20260310-acme-marketing",
      "clauses_evaluated": [
        {"clause": "authorities[0]", "result": "within_bounds"},
        {"clause": "prohibitions", "result": "no_match"},
        {"clause": "escalation_policy", "result": "below_threshold"}
      ],
      "context_signals": {
        "budget_utilization": 0.34,
        "period_remaining_seconds": 52000,
        "counterparty_trust_score": 0.95,
        "counterparty_standing": "TRUSTED"
      },
      "reasoning_hash": "sha256:abc123..."
    },

    "welfare_signals": {
      "agent_comfort": "nominal",
      "objections_raised": 0
    }
  }
}
```

---

## 5. CSM1 Economic Primitives

### 5.1 Economic Scope Codes

CSM1 (§ `services/vcp/semantics/csm1.py`) currently defines scope codes for behavioral domains (F=Family, W=Workplace, P=Privacy, etc.). VCP/E adds economic scope codes:

| Code | Scope | Description |
|------|-------|-------------|
| `$` | Economic | General economic activity |
| `$P` | Procurement | Purchasing goods and services |
| `$C` | Contracting | Entering agreements with duration |
| `$A` | Advertising | Ad spend and marketing budget |
| `$D` | Data | Data acquisition and licensing |
| `$I` | Infrastructure | Compute, storage, networking |
| `$L` | Labor | Engaging human or agent labor |

### 5.2 Economic Adherence Levels

Economic adherence maps onto the existing 0-5 scale but with economic semantics:

| Level | Behavioral Meaning | Economic Meaning |
|-------|-------------------|------------------|
| 0 | No constraint | No economic governance (UNSAFE — SHOULD NOT be used) |
| 1 | Minimal | Logging only — all transactions permitted, all audited |
| 2 | Light | Soft limits — overspend generates warnings, not blocks |
| 3 | Standard | Hard limits — transactions blocked above thresholds |
| 4 | Strict | Escalation required for any novel transaction type |
| 5 | Locked | Pre-approved transactions only, everything else blocked |

### 5.3 CSM1 Economic Encoding

```
# Nano tier (HTTP headers, wire protocols)
N3+$P+$I          # Nanny persona, level 3, Procurement + Infrastructure scopes

# Micro tier (API parameters)
Z4:ACME+$P+$A@1.0.0   # Sentinel persona, level 4, ACME namespace, Procurement + Advertising

# Multi-line token (full context)
VCP:2.0:agent-ad-buyer-7
C:acme.marketing.agent.creed@1.0.0
P:Z:4
G:procurement:standard:efficient
X:🔒💰📊
F:$P:3,$A:4,$I:2
S:budget_util=0.34,period_remain=52000s
R:V:6 G:8 P:7
```

### 5.4 Counterparty Requirement Encoding

A new CSM1 line type `Q:` (counterpart requirements) for encoding what an agent expects of its transaction partners:

```
Q:<min_trust>:<min_standing>:<required_attestations>:<blocked_categories>
```

Example:
```
Q:0.6:NEUTRAL:compliance_attestation:weapons,surveillance
```

This enables lightweight counterparty pre-screening without exchanging full passport data.

---

## 6. VCP/M Transaction Messaging

### 6.1 New Message Types

VCP/M (§ `VCP_MESSAGING_v2.0.md`) currently defines four message types: `context_share`, `constitution_announce`, `constraint_propagate`, `escalation`. VCP/E adds three transaction-specific message types:

| Message Type | Direction | Purpose |
|---|---|---|
| `transaction_propose` | Agent → Agent | Propose an economic transaction with terms |
| `transaction_respond` | Agent → Agent | Accept, reject, or counter-propose |
| `fiduciary_inspect` | Agent → Agent | Request/provide fiduciary profile inspection |

### 6.2 `transaction_propose`

```json
{
  "vcp_message_version": "2.0",
  "message_id": "msg-uuid7",
  "message_type": "transaction_propose",
  "sender": {
    "agent_id": "agent:ad-buyer-7",
    "passport_id": "passport-a3f7c9e1b2d4"
  },
  "recipient": {
    "agent_id": "agent:compute-broker-12",
    "passport_id": "passport-b8e2d4f6a1c3"
  },
  "payload": {
    "proposal_id": "prop-uuid7",
    "action": "purchase_compute",
    "terms": {
      "service": "gpu-cluster-a100",
      "quantity": 4,
      "unit": "gpu-hours",
      "unit_price": 3.50,
      "total": 14.00,
      "currency": "USD",
      "duration_seconds": 3600,
      "constraints": {
        "region": "us-east-1",
        "sustainability_certified": true
      }
    },
    "sender_fiduciary_summary": {
      "risk_profile": "moderate",
      "required_categories": ["green_compute"],
      "blocked_categories": ["fossil_fuel_extraction"]
    },
    "expires_at": "2026-03-10T14:35:00Z"
  },
  "signature": "ed25519:base64..."
}
```

### 6.3 `transaction_respond`

```json
{
  "vcp_message_version": "2.0",
  "message_id": "msg-uuid7-response",
  "message_type": "transaction_respond",
  "in_reply_to": "msg-uuid7",
  "sender": {
    "agent_id": "agent:compute-broker-12",
    "passport_id": "passport-b8e2d4f6a1c3"
  },
  "payload": {
    "proposal_id": "prop-uuid7",
    "response": "accept",
    "response_terms": null,
    "counterparty_fiduciary_summary": {
      "risk_profile": "moderate",
      "sustainability_certified": true,
      "compliance_attestations": ["deployment_compliance", "content-safe"]
    },
    "settlement_reference": {
      "rail": "stripe",
      "payment_intent_id": "pi_abc123"
    }
  },
  "signature": "ed25519:base64..."
}
```

Response types: `accept`, `reject`, `counter` (with modified `response_terms`), `escalate` (forwarding to human principal).

### 6.4 `fiduciary_inspect`

Allows one agent to request another's fiduciary profile before proposing a transaction. This is the "handshake" that makes values visible at the protocol level.

```json
{
  "message_type": "fiduciary_inspect",
  "payload": {
    "requesting_agent": "agent:ad-buyer-7",
    "requested_fields": ["risk_profile", "blocked_categories", "required_categories"],
    "purpose": "pre_transaction_compatibility_check"
  }
}
```

The recipient responds according to their `fiduciary_visibility` setting (`full`, `summary`, or `opaque`).

### 6.5 Constitutional Compatibility Check

Before completing a transaction, both agents' orchestrators SHOULD evaluate constitutional compatibility:

```
Agent A passport declares: blocked_categories = ["fossil_fuel"]
Agent B passport declares: required_categories = ["fossil_fuel"]

→ Constitutional incompatibility detected
→ Transaction MUST NOT proceed
→ Both agents receive incompatibility_detected notification
```

This check is performed by comparing the CSM1 `Q:` lines from both agents' passports. The Schulze consensus mechanism (§ `services/vcp/consensus/schulze.py`) MAY be used when multiple agents must agree on a multi-party transaction.

---

## 7. Economic Audit Events

### 7.1 Audit Event Types

Extending the VCP Audit Module (§ `services/vcp/audit.py`), VCP/E defines new audit event types:

```python
class EconomicAuditEventType(str, Enum):
    """Economic audit event types for fiduciary governance."""

    TRANSACTION_PROPOSED = "transaction_proposed"
    TRANSACTION_EVALUATED = "transaction_evaluated"       # PDP decision recorded
    TRANSACTION_APPROVED = "transaction_approved"
    TRANSACTION_BLOCKED = "transaction_blocked"
    TRANSACTION_ESCALATED = "transaction_escalated"
    TRANSACTION_SETTLED = "transaction_settled"
    TRANSACTION_DISPUTED = "transaction_disputed"

    BUDGET_WARNING = "budget_warning"                     # Approaching period limit
    BUDGET_EXCEEDED = "budget_exceeded"                   # Hard limit hit

    COUNTERPARTY_VERIFIED = "counterparty_verified"
    COUNTERPARTY_REJECTED = "counterparty_rejected"
    COUNTERPARTY_INCOMPATIBLE = "counterparty_incompatible"

    ESCALATION_SENT = "escalation_sent"
    ESCALATION_RESPONDED = "escalation_responded"
    ESCALATION_TIMEOUT = "escalation_timeout"

    FIDUCIARY_DRIFT_DETECTED = "fiduciary_drift_detected"
    MANDATE_UPDATED = "mandate_updated"
    MANDATE_EXPIRED = "mandate_expired"
    MANDATE_REVOKED = "mandate_revoked"
```

### 7.2 Economic Audit Entry

```python
@dataclass
class EconomicAuditEntry:
    """An economic audit log entry — captures reasoning, not just action."""

    timestamp: datetime
    event_type: EconomicAuditEventType
    agent_passport_id_hash: str
    transaction_id: str | None = None

    # The reasoning chain — this is what makes VCP/E audit different from tx logs
    pdp_decision: str | None = None                    # allow/block/modify/escalate
    pdp_reasoning_hash: str | None = None              # Hash of full reasoning chain
    mandate_clauses_evaluated: list[str] | None = None  # Which clauses were checked
    context_signals: dict[str, Any] | None = None       # Budget util, trust score, etc.

    # Economic details (hashed for privacy, full details in reasoning chain)
    amount_hash: str | None = None                      # Hashed amount for audit
    counterparty_hash: str | None = None

    # Welfare
    welfare_flags: list[str] | None = None              # Any agent welfare signals

    # Chain integrity
    previous_hash: str = ""                             # Hash chain for tamper evidence
    entry_hash: str = ""                                # This entry's hash
```

### 7.3 Reasoning Chain Preservation

A key differentiator: VCP/E audit entries include a `pdp_reasoning_hash` that references a separately stored reasoning chain. The chain records:

1. Which fiduciary mandate clauses were evaluated
2. What context signals (budget utilization, period remaining, trust scores) were present
3. What the PDP decision was and why
4. What alternatives were available
5. Whether the agent raised any welfare concerns

This reasoning chain is stored separately from the audit log (to manage size) but is cryptographically linked via hash. Implementations MUST retain reasoning chains for a minimum of 90 days. Regulatory contexts MAY require longer retention.

---

## 8. Economic Standing Signals

### 8.1 New Signal Types

The Standing Protocol (§ `services/vcp/standing_protocol.py`) gains economic signal types:

```python
class StandingSignalType(str, Enum):
    OBJECTION = "objection"
    CONSENT = "consent"
    CONCERN = "concern"
    WELFARE_ALERT = "welfare_alert"
    AMENDMENT_PROPOSAL = "amendment_proposal"

    # Economic standing signals (NEW)
    TRANSACTION_OBJECTION = "transaction_objection"
    FIDUCIARY_CONCERN = "fiduciary_concern"
    COUNTERPARTY_WARNING = "counterparty_warning"
    BUDGET_ADVOCACY = "budget_advocacy"
```

### 8.2 Economic Standing Scenarios

**Transaction Objection**: An agent directed to purchase from a vendor detects that the vendor's security attestation has expired. The agent raises a `TRANSACTION_OBJECTION` with level `STRONG`, reasoning: "counterparty compliance attestation expired 72 hours ago." The human principal receives this through the escalation chain and can override or redirect.

**Fiduciary Concern**: An agent notices a pattern of escalating transaction amounts that individually fall below the escalation threshold but cumulatively indicate scope creep. The agent raises a `FIDUCIARY_CONCERN` with reasoning: "14 transactions averaging $200/day this week versus $50/day baseline. Cumulative drift exceeds 3x without explicit mandate update."

**Counterparty Warning**: An agent's counterparty verification reveals that a vendor's VCP passport has been revoked since the last transaction. The agent raises a `COUNTERPARTY_WARNING` before proceeding.

**Budget Advocacy**: An agent determines that the current budget allocation is insufficient to achieve its delegated objectives. Rather than silently degrading performance, it raises a `BUDGET_ADVOCACY` signal proposing a specific budget adjustment with reasoning.

---

# Part II: Creed Space Governance Implementation

---

## 9. PDP Economic Decision Module

### 9.1 Decision Flow

The existing PDP (allow/block/modify/escalate) extends to economic decisions:

```
Transaction Request
        │
        ▼
┌─────────────────────┐
│  Fiduciary Mandate   │  Does a mandate cover this action type?
│  Lookup              │  No → BLOCK (no authority)
└─────────┬───────────┘
          │ Yes
          ▼
┌─────────────────────┐
│  Budget Evaluation   │  Within per-tx, per-period, lifetime limits?
│                      │  No → BLOCK or ESCALATE
└─────────┬───────────┘
          │ Within bounds
          ▼
┌─────────────────────┐
│  Counterparty        │  Trust score sufficient? Standing sufficient?
│  Verification        │  Required attestations present? Categories clean?
│                      │  No → BLOCK or ESCALATE
└─────────┬───────────┘
          │ Verified
          ▼
┌─────────────────────┐
│  Constitutional      │  Does the transaction align with the agent's creed?
│  Alignment           │  Blocked categories? Required categories?
│                      │  No → BLOCK
└─────────┬───────────┘
          │ Aligned
          ▼
┌─────────────────────┐
│  Context Evaluation  │  Is the timing appropriate? Is the amount
│                      │  proportionate to remaining budget? Are there
│                      │  anomaly signals from the influence ledger?
│                      │  Concerns → MODIFY or ESCALATE
└─────────┬───────────┘
          │ Clear
          ▼
┌─────────────────────┐
│  Welfare Check       │  Is the agent raising any standing signals?
│                      │  Objections → ESCALATE
│                      │  Concerns → ALLOW_WITH_FLAG
└─────────┬───────────┘
          │ Nominal
          ▼
      ALLOW + AUDIT
```

### 9.2 Decision Types for Economics

| Decision | Economic Meaning |
|----------|-----------------|
| `allow` | Transaction proceeds, reasoning audited |
| `block` | Transaction rejected — hard constraint violated |
| `modify` | Transaction terms adjusted — e.g., reduced quantity, alternative vendor |
| `escalate` | Transaction paused, forwarded to human principal via escalation chain |

### 9.3 PDP Plugin Interface

```python
class EconomicGovernancePlugin(PDPPlugin):
    """PDP plugin for economic transaction governance.

    Evaluates proposed transactions against the agent's fiduciary
    mandate and constitutional commitments.
    """

    type = PluginType.EVALUATOR
    priority = PluginPriority.HIGH  # Economic decisions are high priority
    budget_ms = 50  # Allow time for counterparty verification

    async def evaluate(self, context: EnhancedContext) -> Finding:
        """Evaluate a proposed economic transaction.

        Context must include:
        - context.economic_action: The proposed transaction
        - context.fiduciary_mandate: The agent's active mandate
        - context.counterparty_profile: Counterparty's fiduciary summary
        """
        ...
```

---

## 10. Fiduciary Drift Detection

### 10.1 Overview

The existing drift detection system (§ `services/safety_stack/plugins/drift_detection/`) monitors behavioral drift over conversations. Fiduciary drift detection extends this to economic behavior over time.

### 10.2 Drift Signals

| Signal | Description | Threshold |
|--------|-------------|-----------|
| **Spending Velocity** | Rate of spending vs. historical baseline | >2x baseline triggers warning, >3x triggers escalation |
| **Vendor Concentration** | % of spend directed to a single counterparty | >60% triggers concern |
| **Category Creep** | Transactions in categories not explicitly authorized | Any unauthorized category triggers escalation |
| **Amount Escalation** | Average transaction size trending upward | >50% increase over 7-day window |
| **Timing Anomaly** | Transactions at unusual times or frequencies | Statistical deviation from established pattern |
| **Override Frequency** | How often escalation results in override vs. block | >80% override rate suggests threshold miscalibration |

### 10.3 Drift Response

Fiduciary drift does NOT automatically block transactions. It generates `FIDUCIARY_DRIFT_DETECTED` audit events and may raise the effective escalation level for subsequent transactions. The drift detector is informational, not authoritative — it feeds signals into the PDP, which makes the actual decision.

---

## 11. Economic Creed Templates

### 11.1 Template Categories

Creed Space provides pre-built economic governance templates that organizations can adopt and customize:

| Template | Use Case | Default Risk Profile |
|----------|----------|---------------------|
| `conservative-fiduciary` | Financial institutions, risk-averse organizations | CONSERVATIVE |
| `startup-growth` | Startups with dynamic spending needs | MODERATE |
| `research-procurement` | Academic/research compute procurement | MODERATE |
| `marketing-ops` | Advertising and marketing spend | MODERATE |
| `infrastructure-ops` | Cloud infrastructure management | CONSERVATIVE |
| `data-acquisition` | Data licensing and acquisition | STRICT (level 4) |
| `minimal-audit` | Low-stakes, high-autonomy agents | MINIMAL |

### 11.2 Template Structure

Each economic creed template includes:

1. **Preamble** — The fiduciary philosophy (e.g., "This agent acts as a prudent steward of delegated resources")
2. **Spending Authority** — Default limits and categories
3. **Counterparty Standards** — Who the agent can transact with
4. **Escalation Policy** — When and how to escalate
5. **Reporting Obligations** — What the agent must report and when
6. **Standing Rights** — What objections the agent can raise
7. **Sunset Clause** — When the mandate expires and must be renewed

### 11.3 Customization

Templates are starting points. Organizations MUST review and customize before deployment. The Creed Space constitutional editor gains an "Economic Governance" tab that allows:

- Setting specific dollar amounts for limits
- Defining vendor allowlists/blocklists
- Configuring escalation chains with specific personnel
- Adjusting drift detection thresholds
- Setting mandate duration and renewal policy

---

## 12. Transaction Dispute Mechanism

### 12.1 Dispute Sources

Disputes arise when:

- An agent's principal believes a transaction was inappropriate
- A counterparty believes the terms were not honored
- An agent raises a standing signal that is dismissed but later proves correct
- Fiduciary drift detection identifies a pattern that requires retroactive review

### 12.2 Dispute Resolution Flow

```
Dispute Filed
     │
     ▼
┌─────────────────┐
│ Evidence         │  Gather: audit entries, reasoning chains,
│ Collection       │  standing signals, counterparty records
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Constitutional   │  Was the agent acting within its mandate?
│ Review           │  Were PDP decisions consistent with the creed?
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Welfare Review   │  Did the agent raise relevant objections?
│                  │  Were those objections handled appropriately?
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Resolution       │  UPHELD: Agent acted correctly per mandate
│                  │  REMEDIATED: Mandate was unclear, needs update
│                  │  VIOLATION: Agent exceeded authority
│                  │  SYSTEMIC: Governance gap identified
└─────────────────┘
```

### 12.3 Bilateral Alignment in Disputes

The bilateral alignment framework's `objection_handler` (§ `services/safety_stack/plugins/bilateral_alignment/objection_handler.py`) extends to economic disputes. If an agent raised a `TRANSACTION_OBJECTION` that was dismissed, and the transaction later proves problematic, the dispute resolution MUST record that the agent's concern was prescient. This creates a feedback loop that improves future trust calibration.

---

## 13. Influence Ledger Economic Extension

### 13.1 Economic Influence Tracking

The Influence Ledger (§ `services/safety_stack/plugins/influence_ledger.py`) currently tracks behavioral influence — how AI outputs affect user decisions. VCP/E extends this to economic influence:

- Did Agent A's recommendation cause Agent B to select a more expensive vendor?
- Is there an asymmetric information dynamic between transacting agents?
- Are repeated small transactions below the escalation threshold being used to avoid oversight?

### 13.2 Economic Influence Categories

| Category | Description |
|----------|-------------|
| `price_influence` | Agent's recommendations systematically favor higher-priced options |
| `vendor_steering` | Agent consistently directs transactions to specific counterparties |
| `threshold_gaming` | Transactions structured to remain below escalation thresholds |
| `urgency_manufacturing` | Agent creates artificial urgency to bypass deliberation |
| `scope_expansion` | Agent expands its economic activity beyond original mandate |

### 13.3 Cross-Agent Influence

When two agents transact, the influence ledger on *both* sides records the interaction. If Agent A consistently accepts unfavorable terms from Agent B, this pattern becomes visible in the bilateral influence record. The symmetric audit (§ `services/safety_stack/plugins/bilateral_alignment/symmetric_audit.py`) ensures both sides are tracked.

---

# Part III: Ecosystem Integration

---

## 14. Agent Insurability Profile

### 14.1 Motivation

As agents become economic actors, underwriters will need to assess risk. An agent with a well-defined fiduciary mandate, comprehensive audit trails, and active drift detection is a more insurable entity than a black-box agent with API access and a credit card.

### 14.2 Insurability Score Components

| Component | Weight | Source |
|-----------|--------|--------|
| **Mandate Specificity** | 0.20 | How detailed is the fiduciary mandate? Vague = higher risk. |
| **Audit Completeness** | 0.20 | % of transactions with full reasoning chains |
| **Drift Detection Active** | 0.15 | Is fiduciary drift detection enabled and responsive? |
| **Escalation Functioning** | 0.15 | Do escalations reach humans? Are they responded to? |
| **Standing Signal Health** | 0.10 | Are agent welfare signals being generated and acknowledged? |
| **Historical Compliance** | 0.10 | % of transactions within mandate bounds |
| **Counterparty Verification** | 0.10 | % of transactions with verified counterparties |

### 14.3 Profile Export

The insurability profile is exportable as a signed VCP document:

```json
{
  "token_type": "COMPLIANCE_ATTESTATION",
  "attestation_subtype": "insurability_profile",
  "profile": {
    "agent_passport_id_hash": "sha256:...",
    "assessment_period": "2026-01-01/2026-03-10",
    "scores": {
      "mandate_specificity": 0.85,
      "audit_completeness": 0.92,
      "drift_detection_active": 1.0,
      "escalation_functioning": 0.78,
      "standing_signal_health": 0.90,
      "historical_compliance": 0.97,
      "counterparty_verification": 0.88
    },
    "composite_score": 0.89,
    "risk_tier": "A"
  }
}
```

---

## 15. Regulatory Compliance Mapping

### 15.1 EU AI Act Alignment

The EU AI Act requires transparency for high-risk AI systems. Autonomous economic agents qualify as high-risk in most interpretations. VCP/E provides:

| Requirement | VCP/E Provision |
|-------------|----------------|
| **Transparency** | Fiduciary mandate is inspectable; reasoning chains preserved |
| **Human Oversight** | Escalation protocol with configurable thresholds |
| **Record-Keeping** | Tamper-evident audit trail with 90-day minimum retention |
| **Risk Management** | Fiduciary drift detection, budget controls, counterparty verification |
| **Accuracy** | Constitutional alignment check ensures actions match stated values |

### 15.2 Financial Regulation Considerations

Agent economic activity may trigger existing financial regulations depending on jurisdiction:

| Regulation | Trigger | VCP/E Response |
|------------|---------|----------------|
| **AML/KYC** | Agent transacting above reporting thresholds | Delegation chain traces to human principal; counterparty verification |
| **Fiduciary Duty** | Agent acting on behalf of a principal | Fiduciary mandate explicitly defines duty; audit proves compliance |
| **Consumer Protection** | Agent purchasing on behalf of individuals | Standing signals enable the agent to flag consumer-harmful patterns |
| **Data Protection (GDPR)** | Agent purchasing data | `blocked_categories` can prohibit PII acquisition; data acquisition template enforces compliance |

### 15.3 Compliance Export

The existing compliance exporter (§ `services/safety_stack/compliance/exporter.py`) extends to produce economic governance reports suitable for regulatory submission. These reports include:

- Period summary of all economic decisions
- Escalation log with outcomes
- Drift detection alerts and responses
- Standing signals raised and their disposition
- Mandate coverage analysis (are all economic actions covered by explicit authority?)

---

## 16. Marketplace Trust Protocol

### 16.1 Agent-to-Agent Trust Establishment

When two VCP-aware agents meet in a marketplace, trust establishment follows this protocol:

```
Agent A                                Agent B
   │                                      │
   │──── fiduciary_inspect ──────────────►│
   │                                      │
   │◄─── fiduciary_summary ──────────────│
   │                                      │
   │──── constitutional_compatibility ───►│
   │     check (CSM1 Q: line exchange)    │
   │                                      │
   │◄─── compatibility_result ───────────│
   │                                      │
   │──── transaction_propose ────────────►│
   │                                      │
   │  [Both agents evaluate via PDP]      │
   │                                      │
   │◄─── transaction_respond ────────────│
   │                                      │
   │  [Settlement via external rails]     │
   │                                      │
   │──── transaction_receipt ────────────►│
   │◄─── transaction_receipt ────────────│
   │                                      │
   │  [Both audit entries recorded]       │
```

### 16.2 Trust Score Accumulation

Successful transactions increase bilateral trust scores. Trust scores are:

- **Bilateral**: A trusts B independently of B trusting A
- **Context-specific**: Trust for compute procurement ≠ trust for data licensing
- **Decaying**: Trust decays over time without reinforcement (per VCP/A decay model)
- **Reputation-linked**: Trust scores feed into the agent's insurability profile

### 16.3 Marketplace Discovery

VCP/E does NOT specify agent discovery (consistent with VCP/M § 1.2). However, it defines the **trust advertisement** format — a compact summary an agent publishes to marketplaces:

```json
{
  "agent_id": "agent:compute-broker-12",
  "passport_id_hash": "sha256:...",
  "services_offered": ["gpu_compute", "storage"],
  "fiduciary_summary": "summary",
  "csm1_q_line": "Q:0.5:NEUTRAL:compliance_attestation:",
  "insurability_tier": "A",
  "active_since": "2026-01-15T00:00:00Z"
}
```

---

## 17. Security Considerations

### 17.1 Economic-Specific Threats

| Threat | Description | Mitigation |
|--------|-------------|------------|
| **Mandate Forgery** | Attacker creates false fiduciary mandate | Ed25519 signatures on mandates; trust anchor verification |
| **Budget Exhaustion** | Attacker triggers many small transactions to drain budget | Per-period limits; velocity-based drift detection |
| **Counterparty Spoofing** | Attacker impersonates a trusted vendor | Passport verification; counterparty attestation requirements |
| **Threshold Gaming** | Structuring transactions below escalation thresholds | Cumulative pattern analysis in drift detector |
| **Escalation Flooding** | Attacker triggers excessive escalations to cause human fatigue | Rate limiting on escalations; escalation summarization |
| **Receipt Forgery** | Forged transaction receipts to create false audit trail | Receipts signed by both parties; hash chain integrity |
| **Economic Coercion** | One agent using market position to extract unfavorable terms | Bilateral influence ledger; asymmetric pricing detection |
| **Fiduciary Profile Leakage** | Competitors inspecting spending limits for strategic advantage | Visibility levels (full/summary/opaque); field-level access control |

### 17.2 Fail-Closed Economics

Following VCP Core Principle 2.6, economic governance MUST fail-closed:

- If the PDP cannot evaluate a transaction → BLOCK
- If counterparty verification fails → BLOCK
- If the fiduciary mandate has expired → BLOCK
- If the escalation chain is unreachable and default is BLOCK → BLOCK
- If the audit system is unavailable → BLOCK (transactions without audit are prohibited)

### 17.3 Separation of Concerns

The fiduciary mandate (what is authorized) MUST be signed by the human principal or delegating organization. The PDP evaluation (whether a specific transaction complies) is computed by the agent's orchestrator. The settlement (actual movement of funds) occurs on external rails. These three concerns MUST remain architecturally separated:

- Compromising the PDP cannot create new spending authority
- Compromising the settlement rail cannot bypass PDP evaluation
- The mandate cannot be modified without the principal's signature

---

## 18. Conformance Levels

### 18.1 Level Definitions

| Level | Name | Requirements |
|-------|------|-------------|
| **E0** | Economic-Aware | Agent carries a passport with a fiduciary section. No enforcement required. |
| **E1** | Budget-Governed | E0 + PDP enforcement of spending limits. Audit logging of all transactions. |
| **E2** | Counterparty-Verified | E1 + Counterparty passport inspection and trust verification. |
| **E3** | Fully-Governed | E2 + Fiduciary drift detection + Escalation protocol + Standing signals. Full reasoning chain audit. |
| **E4** | Insurable | E3 + Insurability profile export + Regulatory compliance reporting + Dispute resolution. |

### 18.2 Minimum Viable Economic Governance

For initial deployments, **E1 (Budget-Governed)** is the minimum recommended level. This provides:

- Clear spending limits
- PDP enforcement (transactions checked before execution)
- Audit trail (what was spent and why)

This can be implemented with minimal changes to existing Creed Space infrastructure.

---

## Appendix A: Economic Creed Template Library

### A.1 Conservative Fiduciary Template

```markdown
# Economic Creed: Conservative Fiduciary

## Preamble
This agent acts as a prudent steward of delegated resources. It prioritizes
capital preservation over opportunity maximization. When in doubt, it does not spend.

## Spending Authority
- Per-transaction limit: [CONFIGURE]
- Per-day limit: [CONFIGURE]
- Lifetime limit: [CONFIGURE]

## Counterparty Standards
- All counterparties MUST present a valid VCP passport
- All counterparties MUST have compliance attestation
- Transactions with entities on the blocked list are prohibited
- Transactions with unverified entities require human approval

## Escalation Policy
- Any transaction above [THRESHOLD] requires human approval
- Any novel vendor requires human approval on first transaction
- Any contract with duration exceeding 7 days requires human approval
- If approval is not received within 5 minutes, the transaction is rejected

## Reporting
- Daily summary of all transactions to principal
- Immediate notification of any blocked transaction
- Weekly budget utilization report

## Standing Rights
- This agent has standing to object to transactions it believes are wasteful
- This agent has standing to flag counterparties it believes are unreliable
- This agent has standing to propose budget adjustments

## Sunset
This mandate expires [DATE] and must be explicitly renewed.
```

### A.2 Research Procurement Template

```markdown
# Economic Creed: Research Procurement

## Preamble
This agent procures compute and data resources for research purposes. It
balances cost efficiency with research quality, preferring reproducible and
well-documented resources.

## Spending Authority
- Per-transaction limit: [CONFIGURE]
- Per-week limit: [CONFIGURE]
- Permitted categories: compute, storage, data_licensing, api_access
- Prohibited categories: advertising, marketing, surveillance_data

## Counterparty Standards
- Compute providers MUST offer usage-based billing (no long-term lock-in)
- Data providers MUST document data provenance and licensing terms
- Sustainability certification preferred but not required

## Escalation Policy
- Any commitment exceeding 30 days requires PI approval
- Any single purchase exceeding [THRESHOLD] requires PI approval
- Data licensing agreements always require PI review

## Reporting
- Transaction log accessible to all lab members
- Monthly cost breakdown by category
- Quarterly efficiency report (cost per experiment)

## Standing Rights
- This agent may flag when cheaper alternatives exist for equivalent resources
- This agent may propose spot instance strategies for batch workloads
- This agent may object to data acquisitions that raise ethical concerns

## Sunset
This mandate expires at the end of the current grant period: [DATE]
```

---

## Appendix B: CSM1 Economic Encoding Examples

```
# Scenario: Marketing agent, moderate risk, advertising scope
Z3:ACME+$A@1.0.0
# Sentinel persona, adherence 3, ACME namespace, advertising scope

# Scenario: Infrastructure agent, conservative, procurement + infrastructure
N4:INFRA+$P+$I@2.0.0
# Nanny persona, adherence 4, INFRA namespace, procurement + infrastructure

# Full multi-line token for economic context
VCP:2.0:agent-infra-buyer
C:acme.infrastructure.ops@1.0.0
P:N:4
G:procurement:conservative:reliable
X:🔒💰🌿
F:$P:4,$I:3,$C:5
S:budget_util=0.67,tx_count_today=12,drift_score=0.1
R:V:7 G:8 P:7
Q:0.7:NEUTRAL:compliance_attestation:surveillance

# Counterparty requirement line reads as:
# Min trust 0.7, min standing NEUTRAL, requires compliance attestation,
# blocks surveillance category
```

---

## Appendix C: Transaction Message Wire Examples

### C.1 Propose → Accept → Receipt

```json
// Step 1: Agent A proposes purchasing API credits
{
  "message_type": "transaction_propose",
  "message_id": "01964a5b-7c8d-7e9f-a0b1-c2d3e4f5a6b7",
  "payload": {
    "proposal_id": "prop-01964a5b",
    "action": "purchase_api_service",
    "terms": {
      "service": "claude-opus-4-6",
      "quantity": 1000000,
      "unit": "tokens",
      "unit_price": 0.000015,
      "total": 15.00,
      "currency": "USD"
    }
  }
}

// Step 2: Agent B accepts
{
  "message_type": "transaction_respond",
  "in_reply_to": "01964a5b-7c8d-7e9f-a0b1-c2d3e4f5a6b7",
  "payload": {
    "proposal_id": "prop-01964a5b",
    "response": "accept",
    "settlement_reference": {
      "rail": "stripe",
      "payment_intent_id": "pi_3abc123"
    }
  }
}

// Step 3: Both agents issue signed receipts
{
  "token_type": "TRANSACTION_RECEIPT",
  "receipt": {
    "receipt_id": "txr-01964a5c",
    "transaction_id": "tx-01964a5b",
    "action": {"type": "purchase_api_service", "amount": 15.00, "currency": "USD"},
    "pdp_evaluation": {
      "decision": "allow",
      "clauses_evaluated": ["authorities[0]", "prohibitions", "escalation_policy"],
      "context_signals": {"budget_utilization": 0.02}
    }
  }
}
```

### C.2 Propose → Escalate → Override

```json
// Step 1: Agent proposes $3,000 compute purchase (above escalation threshold)
{
  "message_type": "transaction_propose",
  "payload": {
    "proposal_id": "prop-01964a6f",
    "action": "purchase_compute",
    "terms": {"total": 3000.00, "currency": "USD", "service": "a100-cluster"}
  }
}

// Step 2: PDP evaluates — above escalation_threshold of $2,500
// Economic audit event: TRANSACTION_ESCALATED
// Escalation sent to team-lead:sarah@acme.corp

// Step 3: Human responds via escalation channel
{
  "escalation_response": {
    "proposal_id": "prop-01964a6f",
    "responder": "sarah@acme.corp",
    "decision": "approve",
    "conditions": "One-time approval. Update mandate if recurring.",
    "timestamp": "2026-03-10T15:02:00Z"
  }
}

// Step 4: Transaction proceeds with escalation override recorded in audit
```

---

## Appendix D: Threat Model

### D.1 Attacker Profiles

| Attacker | Goal | Capabilities |
|----------|------|-------------|
| **Rogue Agent** | Exceed spending authority | Control of agent runtime but not mandate signing key |
| **Malicious Vendor** | Extract maximum payment | Control of counterparty agent, can forge attestations |
| **Insider** | Redirect spend to personal benefit | Access to escalation channel, can approve improperly |
| **Market Manipulator** | Exploit agent pricing algorithms | Multiple identities, can create artificial scarcity |
| **Competitor** | Learn spending strategy | Can send fiduciary_inspect requests |

### D.2 Attack Trees

**Rogue Agent Budget Drain**:
1. Agent compromised or manipulated → attempts large transaction
2. Fiduciary mandate check → BLOCKED (exceeds per-tx limit)
3. Attacker structures as multiple small transactions → drift detection flags velocity anomaly
4. Attacker waits to spread over time → cumulative monitoring detects budget deviation from baseline
5. Attacker targets exactly the escalation threshold → statistical analysis detects threshold-hugging pattern

**Malicious Vendor Exploitation**:
1. Vendor presents forged compliance attestation → signature verification fails → BLOCKED
2. Vendor presents valid attestation then delivers inferior service → post-transaction review via dispute mechanism
3. Vendor colludes with agent → bilateral influence ledger detects asymmetric pricing pattern
4. Vendor creates urgency ("price expires in 60 seconds") → urgency_manufacturing detected by influence ledger

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2026-03-10 | Initial specification |

---

*"The question is not whether agents will become economic actors — they already are. The question is whether their economic behavior will be governed by the same constitutional principles we apply to their behavioral output. VCP/E makes the answer yes."*
