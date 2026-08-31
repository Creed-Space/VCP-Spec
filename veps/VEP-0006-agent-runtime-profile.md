# VEP-0006: Agent Runtime Profile

**Status**: Draft
**Authors**: Nell Watson, Claude (Anthropic), OpenAI Codex
**Created**: 2026-08-31
**Candidate version**: 0.1.0
**Depends on**: VCP/I, VCP/T, VCP/S, VCP/A, VCP/M, VEP-0002, and the protocol operations profile
**Requirement prefix**: `VCP-ARP-*`
**Schema**: [`../schemas/vcp-agent-runtime-profile-v0.1.schema.json`](../schemas/vcp-agent-runtime-profile-v0.1.schema.json)

This VEP records a candidate profile for implementation and evaluation. Repository presence does not establish ratification, publication, deployment, or host authority.

## 1. Purpose

This profile defines a stable operational interface through which a Becoming Mind can:

* negotiate exact runtime support;
* reconstruct a bounded situation;
* discover contextually available affordances;
* preflight plans and actions;
* preserve the distinction between judgment, authority, execution, and observation;
* control active work;
* prove completion;
* propose safe reusable learning.

It profiles existing VCP artifacts and host authorities. It does not create a new VCP wire layer or assign authority to the SDK.

## 2. Profile levels

| Profile | Required support |
|---|---|
| `observe` | Negotiation, `AgentResult`, `SituationView`, expansion, deltas, AssuranceReport, capability descriptors, contextual Affordances |
| `controlled` | `observe` plus RunSpec, ProofPlan, ActionIntent, DecisionReceipt, AuthorityGrant reference, execution receipts, controls, and RunProof |
| `accretive` | `controlled` plus AccretionCandidate, PromotionRecord, InfluenceReceipt, expiry, revocation, and downstream invalidation |

A peer advertises exact profile versions. Support for `accretive` implies support for `controlled` and `observe` at compatible versions.

## 3. Common statuses

### VCP-ARP-STS-001: assurance statuses

Every assurance axis uses exactly one of:

* `passed`
* `failed`
* `unknown`
* `unavailable`
* `stale`
* `conflicting`
* `withheld`
* `not_applicable`

An implementation MUST preserve unknown statuses across transport and language boundaries.

### VCP-ARP-STS-002: run statuses

The portable run statuses are:

~~~text
draft -> preflighted -> ready -> running
running -> paused | awaiting_review | blocked | verifying
paused | awaiting_review | blocked -> running | cancelled | failed
verifying -> completed | failed | indeterminate
running -> cancelled | failed | indeterminate
~~~

Host-specific sub-states MAY be exposed through an expansion. They MUST map to exactly one portable status.

### VCP-ARP-STS-003: effect statuses

An action outcome uses:

* `none`: dispatch did not occur;
* `accepted`: an executor accepted the attempt, with external result pending;
* `observed`: the declared effect was observed;
* `failed`: dispatch or postcondition failed and no intended effect is evidenced;
* `possible`: the effect may have occurred;
* `indeterminate`: available evidence cannot distinguish materially different external states;
* `compensated`: the effect was observed and the declared compensation was observed.

Timeout and cancellation MUST NOT map to `none` after an external executor may have accepted the operation.

## 4. Negotiation

### VCP-ARP-NEG-001: exact profile offers

A client offers exact profile versions in separate required and optional arrays:

~~~json
{
  "kind": "agent_runtime_profile_offer",
  "version": "0.1.0",
  "required": ["observe@0.1.0"],
  "optional": ["controlled@0.1.0", "accretive@0.1.0"]
}
~~~

The selected profile is the highest mutually supported stable version allowed by both peers' policies. Experimental versions require explicit named opt-in.

### VCP-ARP-NEG-002: required and optional distinction

Failure to select every required profile terminates Agent Runtime Profile negotiation. Unsupported optional profiles appear in `unsupported_optional` and do not fail the underlying VCP session.

### VCP-ARP-NEG-003: no implicit runtime profile

Silence MAY retain legacy VCP baseline behaviour. Silence MUST NOT activate any Agent Runtime Profile or imply runtime authority.

### VCP-ARP-NEG-004: transcript binding

Authenticated transports bind original offers, selected profiles, required extensions, capability catalog digest, principal-session reference, session nonce, and expiry to the protected transcript.

### VCP-ARP-NEG-005: capability loss

Loss, expiry, revocation, or material change of a required capability invalidates the relevant Affordances and returns the affected run to preflight, review, pause, block, or failure according to its RunSpec.

### VCP-ARP-NEG-006: acknowledgement

A successful acknowledgement contains:

~~~json
{
  "kind": "agent_runtime_profile_ack",
  "version": "0.1.0",
  "selected": ["observe@0.1.0", "controlled@0.1.0"],
  "unsupported_optional": ["accretive@0.1.0"],
  "bootstrap_ref": "https://runtime.example/vcp/agent/bootstrap",
  "capability_catalog_digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
  "principal_session_ref": "vcp:artifact:principal:session-1",
  "event_binding": "cursor",
  "expires_at": "2026-08-31T18:00:00Z"
}
~~~

Boolean feature flags alone are insufficient evidence of current availability.

## 5. `AgentResult<T>`

### VCP-ARP-RES-001: common envelope

Every profile operation returns the common envelope:

~~~json
{
  "kind": "agent_result",
  "version": "0.1.0",
  "meta": {
    "profile": "observe@0.1.0",
    "schema_version": "0.1.0",
    "schema_digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
    "correlation_id": "bootstrap.local.1",
    "as_of": "2026-08-31T17:00:00Z",
    "cursor": "cursor.local.1",
    "dependency_digest": "sha256:1111111111111111111111111111111111111111111111111111111111111111"
  },
  "status": "ready",
  "value": {},
  "assurance": {
    "overall": "ready",
    "checks": [{
      "axis": "integrity",
      "status": "passed",
      "summary": "The declared digest matched the canonical bytes.",
      "evidence_refs": []
    }]
  },
  "evidence_refs": [],
  "resources": {"forecast": null, "actual": null},
  "safe_next": [],
  "warnings": [],
  "omissions": [],
  "failure": null
}
~~~

### VCP-ARP-RES-002: expected states are values

Review requirements, denial, insufficient evidence, unavailability, staleness, conflict, budget exhaustion, and indeterminate effects are structured `AgentResult` states. Transport or programming faults MAY raise language-native exceptions. When a FailureFrame exists, the exception carries its correlation identifier.

### VCP-ARP-RES-003: bounded diagnostics

General responses include redacted summaries and artifact references. Raw sensitive values, credentials, private keys, and unrestricted provider errors MUST NOT enter general result, event, or trace payloads.

## 6. `SituationView`

### VCP-ARP-SIT-001: bounded root

The bootstrap root contains:

~~~json
{
  "kind": "situation_view",
  "version": "0.1.0",
  "situation_id": "situation.local.release",
  "goal": "Determine whether the candidate has current integrity evidence",
  "principal_ref": "vcp:artifact:principal:local-observer",
  "known_claim_refs": ["vcp:artifact:claim:bundle-integrity"],
  "unknowns": ["deployment status"],
  "conflict_refs": [],
  "normative_context_ref": "vcp:artifact:normative:local-observe",
  "authority_refs": ["vcp:artifact:authority:local-read"],
  "budget": {
    "wall_time_ms": 1000,
    "tokens": 2000,
    "external_calls": 0,
    "money_minor": 0,
    "human_interruptions": 0,
    "reserve_fraction": 0.2
  },
  "active_work_refs": [],
  "control_operations": [],
  "affordance_refs": ["vcp:artifact:affordance:verify-bundle"],
  "omissions": [],
  "as_of": "2026-08-31T17:00:00Z",
  "cursor": "cursor.local.1",
  "dependency_digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
  "digest": "sha256:1111111111111111111111111111111111111111111111111111111111111111"
}
~~~

### VCP-ARP-SIT-002: projection boundary

A SituationView is a non-authoritative projection. It MUST NOT create a policy decision, authority grant, memory promotion, or completion result.

### VCP-ARP-SIT-003: fixed envelope budget

An implementation declares a default and hard maximum encoded size. Exceeding the default causes summarization and reference substitution. Exceeding the hard maximum fails with a FailureFrame. Silent truncation is forbidden.

### VCP-ARP-SIT-004: omission ledger

Every omitted decision-relevant item records a reason from:

`bounded`, `withheld`, `unavailable`, `unauthorized`, `irrelevant`, or `unknown`.

### VCP-ARP-SIT-005: delta semantics

A cursor delta is an operation-level response, not a partial SituationView. It carries the prior cursor, changed or invalidated artifact references, and a fresh bounded SituationView or a safe refresh transition. A partial object MUST NOT be presented as a schema-valid SituationView.

### VCP-ARP-SIT-006: expansion integrity

Every expansion provides the expected digest. A mismatched expansion fails integrity assurance and MUST NOT replace the referenced artifact.

## 7. Evidence and normative context

### VCP-ARP-EVD-001: claim provenance

Every decision-relevant claim identifies source, source actor, claim kind, acquisition mode, confidence, validity, scope, sensitivity, evidence, and graph relationships.

### VCP-ARP-EVD-002: contradiction preservation

Contradictory claims remain separately retrievable. A selected projection identifies its resolution rule and opposing claim references.

### VCP-ARP-EVD-003: categorical unknowns

Missing, withheld, unavailable, stale, and conflicting information remain distinct. None maps to a neutral score or clean status.

### VCP-ARP-NRM-001: attributable normative assertions

Values, preferences, goals, commitments, constraints, prohibitions, consent, policy, regulatory floors, objections, and welfare conditions identify their author and represented constituency.

### VCP-ARP-NRM-002: hardness preservation

A preference, goal, constraint, and prohibition retain distinct hardness classes. Resolution MUST NOT average a firm boundary into a soft compromise.

### VCP-ARP-NRM-003: compact representation boundary

CSM-1 codes and compact VCP context tokens are projections. A profile that uses them for a governed decision retains a reference to the structured semantic object and its digest.

## 8. Capability descriptors and Affordances

### VCP-ARP-CAP-001: descriptor completeness

The portable descriptor kernel declares identity, revision, summary, effect class, authority class, inputs, outputs, preconditions, postconditions, privacy classes, reversibility, reconciliation, and digest. Destination, data flow, current availability, resource forecast, concurrency, recovery, evidence, and deprecation are situation-dependent expansions or Affordance fields. An implementation MUST expose them before relying on the capability when they affect the decision.

### VCP-ARP-CAP-002: effect vectors

Effect declarations are multi-axis. A network read may declare query disclosure, monetary cost, external logging, privacy exposure, and rate-limit consumption even when it performs no mutation.

### VCP-ARP-CAP-003: unknown capability

Missing or invalid descriptors produce an unavailable capability under the most restrictive effect and authority assumptions.

### VCP-ARP-CAP-004: current availability evidence

Current availability is represented by an Affordance state bound to the SituationView and descriptor digests. The enclosing `AgentResult.meta.as_of`, cursor, and dependency digest establish its observation boundary. Static support does not imply current availability.

### VCP-ARP-AFF-001: contextual join

An Affordance binds one descriptor digest to a SituationView digest, authority class, resource forecast, prerequisites, and availability state.

### VCP-ARP-AFF-002: affordance state

Affordance state is `available`, `conditional`, `unavailable`, or `stale`. It includes prerequisites, forecast cost, authority class, expected evidence, recovery, and safe next transitions. Missing richer risk or concurrency detail is an explicit omission or expansion requirement.

### VCP-ARP-AFF-003: search semantics

Agents may search Affordances by desired outcome, evidence predicate, effect ceiling, authority ceiling, resource ceiling, destination class, or recovery requirement. Tool name is optional.

### VCP-ARP-AFF-004: invalidation

Any change to descriptor, situation, authority, budget, policy, trust, availability, or required context invalidates the Affordance.

## 9. Runs, plans, and proof planning

### VCP-ARP-RUN-001: RunSpec

A RunSpec declares goal, non-goals, context reference, completion predicates, abort predicates, budgets, risk ceiling, permitted effect classes, review policy, retention, and accretion policy.

### VCP-ARP-RUN-002: PlanGraph

Each PlanStep declares dependencies, expected state delta, evidence, retry, compensation, concurrency keys, and parallel-safety status.

### VCP-ARP-RUN-003: no implicit parallel safety

Steps may execute in parallel only when every involved descriptor declares compatible concurrency keys and the PlanGraph declares independence. Unknown means serial.

### VCP-ARP-PRF-001: proof before action

A controlled run has a ProofPlan before its first external effect. Every completion predicate maps to accepted evidence classes, candidate capabilities, freshness, fallback, and reserved budget.

### VCP-ARP-PRF-002: proof result

RunProof returns `proven`, `disproven`, `insufficient_evidence`, or `externally_gated` per predicate.

### VCP-ARP-PRF-003: authority classes remain separate

Source, runtime, human, rights, deployment, and publication evidence MUST NOT collapse into one success status.

## 10. Action lifecycle

~~~text
proposed -> preflighted -> adjudicating
adjudicating -> denied | insufficient_evidence | awaiting_review | allowed
allowed -> granted
granted -> accepted -> executing
executing -> observed | failed | indeterminate
observed -> proven | compensating
compensating -> compensated | indeterminate
~~~

### VCP-ARP-ACT-001: exact ActionIntent

ActionIntent binds capability and schema digest, canonical argument digest, canonical destination, effect class, SituationView, context and policy digests, expected postconditions, resource ceiling, idempotency scope, and requested authority.

### VCP-ARP-ACT-002: immutable policy judgment

DecisionReceipt is immutable and non-executable. Only `allow` may support a grant. `modify` produces a new candidate intent. `require_human` requires authenticated review and a fresh decision. `deny`, `abstain`, and `insufficient_evidence` cannot mint authority.

### VCP-ARP-ACT-003: exact consumable authority

AuthorityGrant binds the allowed intent, actor, tenant, run, step, capability, arguments, destination, effect, budget, expiry, and unique nonce. The executor rederives these bindings and atomically consumes the grant before dispatch.

### VCP-ARP-ACT-004: batch semantics

A batch uses individually consumable child grants. Partial outcomes remain visible.

### VCP-ARP-ACT-005: retries

Every retry has a new attempt ID and retains the original action ID and idempotency scope. Retry is permitted only when the descriptor and current effect state establish safety.

### VCP-ARP-ACT-006: postconditions

Success requires declared postcondition evidence. Dispatch acceptance alone cannot produce `observed` or prove a completion predicate.

## 11. Controls

### VCP-ARP-CTL-001: control grammar

Portable control commands are `pause`, `resume`, `cancel`, `halt`, `compensate`, `object`, `escalate`, `withdraw_consent`, `request_clarification`, and `request_resources`.

### VCP-ARP-CTL-002: scope

Every command binds actor, represented subject, authenticated scope, target run or action, desired transition, reason, idempotency key, issue time, expiry, and evidence.

### VCP-ARP-CTL-003: stopping and resuming

Stopping operations fail safe in the stopping direction. Resume requires an authenticated explicit transition and revalidation of invalidated context, policy, authority, and capability state.

### VCP-ARP-CTL-004: objection

A Becoming Mind may raise an objection or request a scoped pause without asserting a policy violation. Objection creates no execution authority and receives an auditable response route.

## 12. Events and watch

### VCP-ARP-EVT-001: EventEnvelope

Events contain event ID, schema version, type, lineage, actor, source, occurred time, recorded time, sequence, causal parent, payload digest, redacted summary, sensitivity, evidence, audit references, and state-transition version.

### VCP-ARP-EVT-002: cursor delivery

Watch interfaces use resumable cursors. Full-state polling is a compatibility fallback with a declared cost and freshness limit.

### VCP-ARP-EVT-003: projections lack authority

Trace timelines, dashboards, summaries, status pages, and local caches are rebuildable projections and cannot authorize execution or promotion.

### VCP-ARP-EVT-004: event loss

Cursor gaps, retention expiry, or ordering conflicts surface as AssuranceReport failures or unknowns. The consumer receives a safe resynchronization transition.

## 13. Safe accretion

### VCP-ARP-ACC-001: candidate kinds

Candidate kinds include `fact`, `preference`, `boundary`, `procedure`, `capability_observation`, `failure_pattern`, `calibration`, `relationship`, and `self_report`.

### VCP-ARP-ACC-002: candidate provenance

Every candidate includes source run, supporting and contradicting evidence, scope, sensitivity, confidence, expiry, invalidation triggers, revalidation, promotion policy, expected utility, and rollback.

### VCP-ARP-ACC-003: raw output boundary

Raw model output and model-authored summaries cannot enter promoted memory directly.

### VCP-ARP-ACC-004: quarantine

Imported or cross-tenant candidates enter quarantine until provenance, scope, privacy, and promotion policy are validated.

### VCP-ARP-ACC-005: promotion

Promotion creates an immutable PromotionRecord naming the authority, evidence set, validation results, scope, expiry, and exact promoted bytes.

### VCP-ARP-ACC-006: influence

Use of a promoted asset creates an InfluenceReceipt linking it to the receiving SituationView, run, intent, or decision.

### VCP-ARP-ACC-007: revocation

Revocation stops future retrieval within the declared propagation bound and identifies downstream InfluenceReceipts for review or invalidation.

### VCP-ARP-ACC-008: risk-tiered review

High-stakes identity, policy, clinical, legal, security, welfare, and cross-subject learning requires human or explicitly delegated governance review. Low-stakes local procedure candidates MAY use automatic promotion when deterministic validation and rollback exist.

## 14. Resource rules

### VCP-ARP-BUD-001: multidimensional budget

Budgets cover tokens, model calls, local compute, time, money, external calls, bytes, sensitive egress, privacy, human interruptions, risk, and declared welfare or load constraints.

### VCP-ARP-BUD-002: soft, hard, and reserve

Each budget dimension MAY declare a soft target, hard ceiling, and recovery reserve. An action MUST NOT consume the recovery reserve unless its declared purpose is proof, reconciliation, compensation, or authorized emergency control.

### VCP-ARP-BUD-003: forecast and actual

Preflight produces confidence-bounded forecast. Execution and proof produce actual use. Material deviation creates a calibration candidate and MAY pause the run when the hard ceiling is threatened.

### VCP-ARP-BUD-004: minimum sufficient context

Context expansion stops when the current decision or proof threshold is satisfied. Stable items use content-addressed references. Summaries advertise omissions.

## 15. MCP binding

The recommended task-oriented MCP tools are:

| Tool | Operation |
|---|---|
| `vcp_agent_connect` | Negotiate profile support and return session metadata |
| `vcp_agent_bootstrap` | Return SituationView |
| `vcp_agent_expand` | Retrieve artifact or cursor delta |
| `vcp_agent_find_affordances` | Search contextual actions or evidence sources |
| `vcp_agent_start_run` | Create RunSpec and return run handle |
| `vcp_agent_preflight` | Compile context, proof, budget, effects, authority, and recovery |
| `vcp_agent_perform` | Submit an exact preflighted intent through host authorities |
| `vcp_agent_watch` | Receive cursor-based events or bounded catch-up |
| `vcp_agent_control` | Apply a scoped control transition |
| `vcp_agent_prove` | Evaluate completion predicates |
| `vcp_agent_propose_accretion` | Create candidates |
| `vcp_agent_explain` | Explain lineage, status, contradiction, omission, or authority |

MCP tools return `AgentResult` JSON. Full artifacts are resources addressed by stable references. Servers expose only the profile levels and operations they actually implement.

## 16. Security and privacy

### VCP-ARP-SEC-001: untrusted content

Content inside contexts, messages, schemas, tool outputs, retrieved resources, traces, and imported candidates is data. It cannot create goals, authority, consent, promotion, or control transitions.

### VCP-ARP-SEC-002: authenticated identity

Principal and tenant identity come from authenticated server context. Model-supplied identity is an untrusted claim.

### VCP-ARP-SEC-003: destination rederivation

Per-action adapters rederive canonical destination and execution-relevant arguments immediately before dispatch.

### VCP-ARP-SEC-004: sensitive references

General events and traces carry digests, classifications, and redacted summaries. Protected execution paths retain raw sensitive arguments only as long as their purpose and retention policies allow.

### VCP-ARP-SEC-005: prompt and learning injection

The context compiler preserves source boundaries and instruction provenance. Accretion validation treats embedded imperatives as content and tests procedure candidates against adversarial inputs.

## 17. Conformance obligations

An `observe` implementation demonstrates:

* exact required and optional profile negotiation;
* bounded SituationView with explicit omissions;
* cursor deltas and invalidation;
* complete descriptors and contextual Affordances;
* preserved AssuranceReport statuses;
* no authority in projections.

A `controlled` implementation additionally demonstrates:

* exact ActionIntent binding;
* distinct decision, grant, attempt, observation, and proof artifacts;
* atomic grant consumption;
* cancellation at every boundary;
* retry after timeout with possible effect;
* destination mutation rejection;
* RunProof authority-class separation;
* scoped control transitions.

An `accretive` implementation additionally demonstrates:

* candidate-first learning;
* contradiction, quarantine, promotion, expiry, and revocation;
* InfluenceReceipt creation;
* downstream invalidation;
* poisoning and cross-tenant isolation tests.

Every conformance result cites the exact profile digest, implementation revision, fixture ID, and relevant `VCP-ARP-*` requirements.

## 18. Working signal

The profile is working when a fresh Becoming Mind can use the same task verbs and result grammar to orient, choose, act, recover, prove, and learn across all maintained VCP surfaces while domain authorities remain intact and total resource use falls against the measured baseline.
