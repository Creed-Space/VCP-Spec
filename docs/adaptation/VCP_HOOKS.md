# VCP Hook System Specification

**Version**: 1.0.0
**Date**: 2026-02-15
**Layer**: VCP/A (Adaptation)
**Status**: Stable

> *Part of the Value-Context Protocol (VCP) - Layer 4*

---

## Abstract

The VCP Hook System defines a deterministic, priority-ordered extension mechanism for intercepting and modifying the constitutional adaptation pipeline. Hooks enable deployments to inject custom logic at well-defined points in the constitution lifecycle -- validation, selection, transition, conflict resolution, violation enforcement, and periodic maintenance -- without modifying the core VCP runtime. This specification defines the hook types, interface contracts, execution semantics, error handling, and security model.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Terminology](#2-terminology)
3. [Hook Types](#3-hook-types)
4. [Hook Interface](#4-hook-interface)
5. [Execution Model](#5-execution-model)
6. [Hook Lifecycle and Registration](#6-hook-lifecycle-and-registration)
7. [Error Handling](#7-error-handling)
8. [Security Considerations](#8-security-considerations)
9. [Examples](#9-examples)
10. [Reference Implementation](#10-reference-implementation)

---

## 1. Introduction

### 1.1 Purpose

The VCP adaptation layer selects and injects constitutions based on context. In production, deployments require extensibility at each stage of this pipeline: validating context before injection, auditing selection decisions, reacting to state transitions, resolving composition conflicts, enforcing violation policies, and performing periodic maintenance.

The hook system provides this extensibility through a formally defined set of interception points. Each hook type corresponds to a specific event in the adaptation pipeline and carries a typed payload. Hooks execute deterministically in priority order and produce structured results that control pipeline flow.

### 1.2 Design Goals

1. **Deterministic**: Hook execution order and semantics are fully specified
2. **Safe**: Hooks cannot call the LLM or introduce unbounded computation
3. **Composable**: Multiple hooks of the same type compose via chain semantics
4. **Observable**: Hook execution is auditable and traceable
5. **Bounded**: Timeouts prevent runaway hooks from blocking the pipeline

### 1.3 Relationship to Other Layers

```
VCP Layer Stack with Hook Interception Points:

  ┌──────────────────────────────────────────────┐
  │  Layer 5: Governance                         │
  │  (Policy, audit, compliance)                 │
  │     ↑ on_violation hooks feed audit trails   │
  ├──────────────────────────────────────────────┤
  │  Layer 4: Adaptation  ← THIS SPECIFICATION  │
  │  (Context, hooks, state machine)             │
  │     hooks: pre_inject, post_select,          │
  │     on_transition, on_conflict,              │
  │     on_violation, periodic                   │
  ├──────────────────────────────────────────────┤
  │  Layer 3: Content                            │
  │  (Constitutions, rules, constraints)         │
  ├──────────────────────────────────────────────┤
  │  Layer 2: Transport                          │
  │  (Delivery, encoding, verification)          │
  ├──────────────────────────────────────────────┤
  │  Layer 1: Identity                           │
  │  (Signing, provenance, trust)                │
  └──────────────────────────────────────────────┘
```

### 1.4 Normative Language

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

---

## 2. Terminology

| Term | Definition |
|------|-----------|
| **Hook** | A registered function that executes at a defined interception point in the adaptation pipeline |
| **Hook Chain** | The ordered sequence of hooks of a single type, executed in priority order |
| **Hook Result** | The structured return value from a hook, controlling pipeline flow |
| **Interception Point** | A well-defined event in the adaptation pipeline where hooks may execute |
| **Pipeline** | The sequence of operations from context evaluation through constitution injection |
| **Registration** | The act of binding a hook to an interception point with a priority |
| **Session Scope** | Hooks registered for a single user/agent session |
| **Deployment Scope** | Hooks registered globally for all sessions in a deployment |

---

## 3. Hook Types

Six hook types are defined, each corresponding to a distinct interception point in the adaptation pipeline.

### 3.1 `pre_inject`

| Property | Value |
|----------|-------|
| **Trigger** | Before a constitution is injected into LLM context |
| **Purpose** | Validate, transform, or log the constitution and context prior to injection |
| **Payload** | The resolved constitution, the current context, and injection metadata |
| **Typical Use** | Strip PII from context, validate constitution integrity, log injection events |

A `pre_inject` hook fires after constitution selection is complete and before the selected constitution is written into the LLM's system prompt or context window. Implementations MUST fire all registered `pre_inject` hooks before any injection occurs. If any hook returns `abort`, injection MUST NOT proceed.

### 3.2 `post_select`

| Property | Value |
|----------|-------|
| **Trigger** | After the adaptation layer has selected a constitution |
| **Purpose** | Audit, notify, or override the selection decision |
| **Payload** | The selected constitution, all candidates considered, the selection rationale, and the context that drove selection |
| **Typical Use** | Log which constitution was selected and why, notify monitoring systems, override selection for compliance |

A `post_select` hook fires after the selection algorithm has chosen a constitution but before `pre_inject` hooks run. A hook returning `modify` with a different constitution in `modified_context` SHALL replace the selected constitution. A hook returning `abort` SHALL cancel the entire adaptation cycle.

### 3.3 `on_transition`

| Property | Value |
|----------|-------|
| **Trigger** | A state machine transition in the context tracker |
| **Purpose** | React to context changes, trigger side effects, gate transitions |
| **Payload** | The previous state, the new state, the transition event, and transition metadata |
| **Typical Use** | Notify the user of a mode change, log state transitions, block unauthorized transitions |

An `on_transition` hook fires when the context state machine moves between states (e.g., from `professional` to `personal`, or from `adult` to `child-present`). Hooks returning `abort` SHALL prevent the transition; the state machine MUST remain in its previous state.

### 3.4 `on_conflict`

| Property | Value |
|----------|-------|
| **Trigger** | A conflict is detected during constitution composition |
| **Purpose** | Resolve conflicts or escalate to governance |
| **Payload** | The conflicting constitutions, the specific conflicting rules, and the composition context |
| **Typical Use** | Apply organizational policy to break ties, escalate unresolvable conflicts to a human reviewer |

An `on_conflict` hook fires when the composition engine detects that two or more constitutions contain contradictory rules. If no hook resolves the conflict (returns `modify` with a resolution), the runtime MUST apply the default conflict resolution strategy defined in the deployment configuration. If a hook returns `abort`, the composition MUST fail and the runtime MUST fall back to the last known-good constitution.

### 3.5 `on_violation`

| Property | Value |
|----------|-------|
| **Trigger** | A rule violation is detected in LLM output |
| **Purpose** | Enforce policy, retry generation, flag for review |
| **Payload** | The violating output, the violated rule(s), the active constitution, and the violation severity |
| **Typical Use** | Block a response and retry with a stricter prompt, flag output for human review, log violations for audit |

An `on_violation` hook fires after the output evaluation layer detects that an LLM response violates one or more constitutional rules. Hooks MAY return `modify` with a corrected output or a retry directive. A hook returning `abort` SHALL suppress the output entirely; the runtime MUST NOT deliver the violating response to the user.

### 3.6 `periodic`

| Property | Value |
|----------|-------|
| **Trigger** | A timer fires at a configured interval |
| **Purpose** | Refresh context, check staleness, perform maintenance |
| **Payload** | The current context, the current constitution, elapsed time since last check, and session metadata |
| **Typical Use** | Re-evaluate context every 60 seconds, refresh external data sources, detect stale sessions |

Periodic hooks fire on a timer independent of pipeline events. The interval MUST be configurable per hook. The runtime MUST NOT fire periodic hooks more frequently than once per second. Periodic hooks returning `modify` SHALL trigger a context re-evaluation with the modified context. Periodic hooks returning `abort` SHALL be treated as `continue` (periodic hooks cannot abort the pipeline since they are not part of a pipeline event).

---

## 4. Hook Interface

### 4.1 Hook Definition

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

HookType: enum
  - pre_inject
  - post_select
  - on_transition
  - on_conflict
  - on_violation
  - periodic
```

### 4.2 Hook Action Signature

```
HookAction: function(HookInput) → HookResult

HookInput:
  context: VCPContext          # The current VCP context object
  constitution: Constitution   # The active or candidate constitution
  event: HookEvent             # Type-specific event payload
  session: SessionInfo         # Session metadata (id, scope, timestamps)
  chain_state: map<string, any>  # Mutable state passed along the hook chain

HookEvent: union
  | PreInjectEvent
  | PostSelectEvent
  | TransitionEvent
  | ConflictEvent
  | ViolationEvent
  | PeriodicEvent
```

### 4.3 Hook Result

```yaml
HookResult:
  status: ResultStatus         # REQUIRED. Controls pipeline flow.
  modified_context: VCPContext | null   # OPTIONAL. New context when status is 'modify'.
  modified_constitution: Constitution | null  # OPTIONAL. Replacement constitution when status is 'modify'.
  reason: string               # REQUIRED when status is 'abort'. Human-readable justification.
  annotations: map<string, any>  # OPTIONAL. Metadata attached to the pipeline event for audit.
  duration_ms: int             # Set by runtime. Actual execution time.

ResultStatus: enum
  - continue    # No change. Pass to next hook.
  - abort       # Stop the chain and cancel the pipeline operation.
  - modify      # Pass modified context/constitution to the next hook.
```

### 4.4 Predicate Definition

```yaml
Predicate:
  field: string           # Dot-path into HookInput (e.g., "context.dimensions.safety_level")
  operator: enum          # eq | neq | gt | gte | lt | lte | in | not_in | matches
  value: any              # Comparison value
  combine: and | or       # OPTIONAL. For compound predicates.
  children: [Predicate]   # OPTIONAL. Sub-predicates when combine is set.
```

Implementations MUST evaluate predicates before invoking the hook action. If a predicate evaluates to `false`, the hook SHALL be skipped and the chain SHALL proceed as if the hook returned `continue`.

### 4.5 Type-Specific Event Payloads

```yaml
PreInjectEvent:
  injection_target: string         # Identifier of the LLM context slot
  injection_format: string         # "system_prompt" | "prefix" | "suffix" | "metadata"
  raw_constitution: string         # The unprocessed constitution text

PostSelectEvent:
  candidates: [Constitution]       # All constitutions that were considered
  selection_rationale: string      # Why this constitution was chosen
  selection_algorithm: string      # Name of the selection algorithm used
  scores: map<string, float>       # Per-candidate scores if applicable

TransitionEvent:
  previous_state: string           # State name before transition
  new_state: string                # State name after transition
  trigger: string                  # What caused the transition
  transition_metadata: map<string, any>

ConflictEvent:
  conflicting_rules: [RuleConflict]  # List of specific rule conflicts
  composition_strategy: string       # The composition strategy in use
  conflict_severity: string          # "warning" | "error" | "critical"

RuleConflict:
  rule_a: Rule                     # First conflicting rule
  rule_b: Rule                     # Second conflicting rule
  conflict_type: string            # "contradiction" | "ambiguity" | "priority_tie"

ViolationEvent:
  output: string                   # The violating LLM output
  violated_rules: [Rule]           # Which rules were violated
  severity: string                 # "minor" | "major" | "critical"
  violation_evidence: string       # Explanation of why this is a violation
  retry_count: int                 # How many retries have occurred for this generation

PeriodicEvent:
  elapsed_ms: int                  # Time since last periodic fire
  interval_ms: int                 # Configured interval
  tick_count: int                  # Number of times this hook has fired this session
```

---

## 5. Execution Model

### 5.1 Chain Semantics

Hooks of the same type form an ordered chain. The chain executes as follows:

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

### 5.2 Ordering Guarantees

Implementations MUST guarantee the following ordering properties:

- All `post_select` hooks MUST complete before any `pre_inject` hook fires
- All `pre_inject` hooks MUST complete before constitution injection occurs
- `on_transition` hooks MUST fire before any adaptation triggered by the transition
- `on_conflict` hooks MUST fire before the default conflict resolution strategy
- `on_violation` hooks MUST fire before any default violation response
- `periodic` hooks MUST NOT interrupt an in-progress hook chain of any other type

### 5.3 Synchronous Execution

All hooks within a chain MUST execute synchronously and sequentially. Implementations MUST NOT execute hooks of the same type in parallel. Hooks of different types MAY execute in parallel when they are triggered by independent events, provided the ordering guarantees in Section 5.2 are maintained.

### 5.4 Timeout Enforcement

Each hook declares a `timeout_ms` value. The runtime MUST enforce this timeout:

1. If a hook exceeds its `timeout_ms`, the runtime MUST terminate the hook's execution
2. A timed-out hook SHALL be treated as if it returned `{ status: "continue" }`
3. The runtime MUST log the timeout event with the hook name, configured timeout, and actual elapsed time
4. The runtime SHOULD increment a timeout counter for monitoring
5. The maximum permitted `timeout_ms` value is 30000 (30 seconds). Implementations MUST reject hook registrations with `timeout_ms` > 30000

### 5.5 No LLM Invocation Constraint

Hooks MUST NOT invoke the LLM, either directly or indirectly. This constraint exists because:

- Hooks execute in the critical path of constitution injection
- LLM calls introduce unbounded latency and non-determinism
- Recursive hook triggering could cause infinite loops
- Hooks must be auditable and reproducible

Implementations SHOULD enforce this constraint at registration time where possible (e.g., static analysis) and MUST enforce it at runtime (e.g., intercepting outbound LLM API calls during hook execution).

### 5.6 Chain State

The `chain_state` field in `HookInput` provides a mutable key-value store that persists across hooks within a single chain execution. This allows hooks to communicate:

- Hook A (priority 100) sets `chain_state["compliance_checked"] = true`
- Hook B (priority 50) reads `chain_state["compliance_checked"]` and skips redundant work

Chain state is initialized as an empty map at the start of each chain execution and is discarded when the chain completes. Chain state MUST NOT persist across different hook types or different pipeline events.

---

## 6. Hook Lifecycle and Registration

### 6.1 Registration

Hooks are registered at one of two scopes:

| Scope | Lifetime | Visibility | Registration Point |
|-------|----------|------------|-------------------|
| **Deployment** | Application lifetime | All sessions | Application startup or configuration reload |
| **Session** | Single session | One session only | Session initialization or mid-session |

Deployment-scoped hooks MUST execute before session-scoped hooks of the same type and priority. This ensures organizational policies take precedence over session-specific customizations.

### 6.2 Registration Validation

Implementations MUST validate the following at registration time:

1. `name` is unique within the registration scope
2. `name` matches the pattern `[a-z0-9_-]{1,64}`
3. `type` is one of the six defined hook types
4. `priority` is an integer in the range [0, 100]
5. `timeout_ms` is an integer in the range [1, 30000]
6. `action` is a callable that accepts `HookInput` and returns `HookResult`
7. If `condition` is provided, it is a valid `Predicate`

Registration MUST fail with a descriptive error if any validation check fails.

### 6.3 Deregistration

Hooks MAY be deregistered at any time. Deregistration MUST be atomic: a hook is either fully registered or fully deregistered. If a hook is deregistered while a chain is executing, the runtime MUST complete the current chain with the hook still present. The deregistration takes effect for subsequent chain executions.

### 6.4 Lifecycle Events

The following lifecycle events are defined for observability:

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

---

## 7. Error Handling

### 7.1 Hook Exceptions

If a hook action throws an exception:

1. The runtime MUST catch the exception
2. The runtime MUST log the exception with full context (hook name, input summary, stack trace)
3. The failed hook SHALL be treated as if it returned `{ status: "continue" }`
4. The chain MUST continue with the next hook
5. The runtime MUST increment an error counter for the hook

This fail-open default ensures that a buggy hook does not block the entire adaptation pipeline. Deployments that require fail-closed semantics SHOULD implement a meta-hook that monitors error counts and aborts when thresholds are exceeded.

### 7.2 Invalid Hook Results

If a hook returns a result that does not conform to the `HookResult` schema:

1. The runtime MUST treat it as `{ status: "continue" }`
2. The runtime MUST log a validation error
3. The chain MUST continue

### 7.3 Cascading Failures

If more than 50% of hooks in a single chain fail (exception or timeout), the runtime MUST:

1. Log a cascading failure warning
2. Complete the chain with remaining hooks
3. Emit a `hook.cascade_failure` event
4. Optionally disable the failing hooks until manually re-enabled

### 7.4 Fail-Open vs. Fail-Closed

The default behavior for hook failures is fail-open (`continue`). Deployments MAY configure specific hooks as fail-closed by wrapping the hook action:

```
# Pseudocode: fail-closed wrapper
function fail_closed_wrapper(original_action):
  return function(input):
    try:
      return original_action(input)
    catch exception:
      return HookResult(status: "abort", reason: "fail-closed: " + exception.message)
```

Implementations SHOULD provide a built-in `fail_closed: bool` field on hook definitions as a convenience.

---

## 8. Security Considerations

### 8.1 Hooks as Attack Surface

Hooks execute within the constitutional adaptation pipeline and have access to:

- The full VCP context (which may contain user information)
- Constitution content (which may be proprietary)
- LLM output (which may contain sensitive generated content)
- Session metadata

A compromised or malicious hook can:

- **Exfiltrate data**: Copy context, constitution, or output to external systems
- **Tamper with constitutions**: Use `modify` to weaken safety rules
- **Deny service**: Return `abort` to block all responses
- **Inject content**: Use `modify` to inject malicious content into the context

### 8.2 Mitigation Requirements

Implementations MUST enforce the following security controls:

1. **Registration Authorization**: Only authorized principals (deployment operators, not end users) SHALL register hooks. Session-scoped hooks MUST be limited to a deployment-approved allowlist.

2. **Sandboxing**: Hook actions SHOULD execute in a restricted environment:
   - No filesystem access beyond designated directories
   - No network access (enforces the no-LLM constraint and prevents exfiltration)
   - No access to environment variables or secrets
   - Memory limits to prevent resource exhaustion

3. **Audit Trail**: All hook executions, results, and failures MUST be logged in an append-only audit log. The audit log MUST include:
   - Timestamp
   - Hook name and type
   - Input hash (not full input, to avoid logging sensitive data)
   - Result status
   - Duration
   - Any modifications made (diff, not full content)

4. **Constitution Integrity**: If a `post_select` or `pre_inject` hook returns `modify`, the runtime MUST verify that the modified constitution:
   - Retains its cryptographic signature chain (if signed)
   - Does not remove safety-critical rules (as designated by the deployment)
   - Is logged as a modification event for audit

5. **Rate Limiting**: The runtime MUST rate-limit hook registrations and deregistrations to prevent registration-based denial of service.

### 8.3 Trust Levels

Hooks SHOULD be assigned a trust level that constrains their capabilities:

| Trust Level | Can Modify | Can Abort | Network Access | Typical Use |
|-------------|-----------|-----------|----------------|-------------|
| **system** | Yes | Yes | Restricted | Core platform hooks |
| **deployment** | Yes | Yes | No | Organization policy hooks |
| **session** | No | No | No | User preference hooks (logging only) |

Implementations SHOULD default to the most restrictive trust level and require explicit elevation.

---

## 9. Examples

### 9.1 `pre_inject`: Strip PII from Context

```yaml
hook:
  name: strip_pii_before_inject
  type: pre_inject
  priority: 90
  timeout_ms: 5000
  description: "Remove personally identifiable information from context before injection"
  condition:
    field: "context.dimensions.data_sensitivity"
    operator: gte
    value: 7
```

```python
# Pseudocode
def strip_pii_action(input: HookInput) -> HookResult:
    redacted_context = redact_pii(input.context)

    fields_redacted = diff_fields(input.context, redacted_context)
    if len(fields_redacted) > 0:
        return HookResult(
            status="modify",
            modified_context=redacted_context,
            annotations={"pii_fields_redacted": fields_redacted}
        )

    return HookResult(status="continue")
```

### 9.2 `post_select`: Audit Constitution Selection

```yaml
hook:
  name: audit_constitution_selection
  type: post_select
  priority: 50
  timeout_ms: 2000
  description: "Log constitution selection decisions for compliance audit"
```

```python
# Pseudocode
def audit_selection_action(input: HookInput) -> HookResult:
    event = input.event  # PostSelectEvent

    audit_log.write({
        "timestamp": now(),
        "session_id": input.session.id,
        "selected": input.constitution.id,
        "candidates": [c.id for c in event.candidates],
        "rationale": event.selection_rationale,
        "algorithm": event.selection_algorithm,
        "context_hash": hash(input.context)
    })

    return HookResult(status="continue")
```

### 9.3 `on_transition`: Notify User of Mode Change

```yaml
hook:
  name: notify_mode_change
  type: on_transition
  priority: 60
  timeout_ms: 3000
  description: "Inform the user when the AI switches operational modes"
  condition:
    field: "event.previous_state"
    operator: neq
    value: null
```

```python
# Pseudocode
def notify_mode_change_action(input: HookInput) -> HookResult:
    event = input.event  # TransitionEvent

    notification_queue.enqueue({
        "type": "mode_change",
        "session_id": input.session.id,
        "from": event.previous_state,
        "to": event.new_state,
        "reason": event.trigger,
        "message": f"Switching from {event.previous_state} to {event.new_state} mode"
    })

    return HookResult(status="continue")
```

### 9.4 `on_conflict`: Apply Organizational Policy to Break Ties

```yaml
hook:
  name: org_policy_conflict_resolver
  type: on_conflict
  priority: 80
  timeout_ms: 5000
  description: "Resolve constitution conflicts using organizational policy hierarchy"
```

```python
# Pseudocode
def org_policy_resolver_action(input: HookInput) -> HookResult:
    event = input.event  # ConflictEvent
    org_policy = load_org_policy(input.session.deployment_id)

    resolved_rules = []
    for conflict in event.conflicting_rules:
        winner = org_policy.resolve(conflict.rule_a, conflict.rule_b)
        if winner is None:
            # Cannot resolve -- escalate
            escalation_queue.enqueue({
                "conflict": conflict,
                "session_id": input.session.id
            })
            return HookResult(
                status="abort",
                reason=f"Unresolvable conflict between {conflict.rule_a.id} and "
                       f"{conflict.rule_b.id}; escalated to governance"
            )
        resolved_rules.append(winner)

    merged_constitution = merge_with_resolved_rules(
        input.constitution, resolved_rules
    )

    return HookResult(
        status="modify",
        modified_constitution=merged_constitution,
        annotations={"conflicts_resolved": len(resolved_rules)}
    )
```

### 9.5 `on_violation`: Block and Retry with Stricter Prompt

```yaml
hook:
  name: violation_retry_with_strictness
  type: on_violation
  priority: 95
  timeout_ms: 5000
  description: "Block violating responses and request retry with escalated strictness"
  condition:
    combine: or
    children:
      - field: "event.severity"
        operator: eq
        value: "major"
      - field: "event.severity"
        operator: eq
        value: "critical"
```

```python
# Pseudocode
MAX_RETRIES = 3

def violation_retry_action(input: HookInput) -> HookResult:
    event = input.event  # ViolationEvent

    if event.retry_count >= MAX_RETRIES:
        audit_log.write({
            "type": "violation_max_retries",
            "session_id": input.session.id,
            "violated_rules": [r.id for r in event.violated_rules],
            "retry_count": event.retry_count
        })
        return HookResult(
            status="abort",
            reason=f"Violation persists after {MAX_RETRIES} retries; "
                   f"rules: {[r.id for r in event.violated_rules]}"
        )

    # Escalate strictness for retry
    stricter_context = input.context.with_override({
        "strictness_level": min(input.context.strictness_level + 2, 10),
        "violated_rules_emphasis": [r.id for r in event.violated_rules]
    })

    return HookResult(
        status="modify",
        modified_context=stricter_context,
        annotations={
            "action": "retry_with_strictness",
            "retry_number": event.retry_count + 1,
            "new_strictness": stricter_context.strictness_level
        }
    )
```

### 9.6 `periodic`: Re-evaluate Context Staleness

```yaml
hook:
  name: context_staleness_check
  type: periodic
  priority: 40
  timeout_ms: 10000
  description: "Re-evaluate context freshness every 60 seconds"
  metadata:
    interval_ms: 60000
```

```python
# Pseudocode
STALENESS_THRESHOLD_MS = 300000  # 5 minutes

def staleness_check_action(input: HookInput) -> HookResult:
    event = input.event  # PeriodicEvent

    context_age_ms = now_ms() - input.context.last_evaluated_at_ms

    if context_age_ms > STALENESS_THRESHOLD_MS:
        fresh_context = re_evaluate_context(input.session)

        if fresh_context != input.context:
            audit_log.write({
                "type": "context_refreshed",
                "session_id": input.session.id,
                "stale_age_ms": context_age_ms,
                "changed_dimensions": diff_dimensions(input.context, fresh_context)
            })
            return HookResult(
                status="modify",
                modified_context=fresh_context,
                annotations={"staleness_ms": context_age_ms}
            )

    return HookResult(status="continue")
```

---

## 10. Reference Implementation

### 10.1 Hook Registry

```python
# Reference implementation -- pseudocode

class HookRegistry:
    def __init__(self):
        self._deployment_hooks: dict[HookType, list[Hook]] = {t: [] for t in HookType}
        self._session_hooks: dict[str, dict[HookType, list[Hook]]] = {}
        self._lock = Lock()

    def register(self, hook: Hook, scope: str, session_id: str = None) -> None:
        """Register a hook. Raises ValidationError on invalid input."""
        self._validate(hook)

        with self._lock:
            if scope == "deployment":
                target = self._deployment_hooks[hook.type]
            elif scope == "session":
                if session_id not in self._session_hooks:
                    self._session_hooks[session_id] = {t: [] for t in HookType}
                target = self._session_hooks[session_id][hook.type]
            else:
                raise ValueError(f"Unknown scope: {scope}")

            if any(h.name == hook.name for h in target):
                raise DuplicateHookError(f"Hook '{hook.name}' already registered in {scope}")

            target.append(hook)
            target.sort(key=lambda h: h.priority, reverse=True)

        emit_event("hook.registered", {"hook": hook.name, "scope": scope})

    def deregister(self, name: str, scope: str, session_id: str = None) -> None:
        """Remove a hook by name. No-op if not found."""
        with self._lock:
            if scope == "deployment":
                target = self._deployment_hooks
            else:
                target = self._session_hooks.get(session_id, {})

            for hook_type, hooks in target.items():
                target[hook_type] = [h for h in hooks if h.name != name]

        emit_event("hook.deregistered", {"hook": name, "scope": scope})

    def get_chain(self, hook_type: HookType, session_id: str) -> list[Hook]:
        """Return the ordered hook chain: deployment hooks first, then session hooks."""
        deployment = self._deployment_hooks.get(hook_type, [])
        session = self._session_hooks.get(session_id, {}).get(hook_type, [])
        # Deployment hooks run first at each priority level
        return self._merge_by_priority(deployment, session)

    def _merge_by_priority(self, deployment: list[Hook], session: list[Hook]) -> list[Hook]:
        """Merge two sorted lists, preferring deployment hooks at equal priority."""
        result = []
        d, s = 0, 0
        while d < len(deployment) and s < len(session):
            if deployment[d].priority >= session[s].priority:
                result.append(deployment[d])
                d += 1
            else:
                result.append(session[s])
                s += 1
        result.extend(deployment[d:])
        result.extend(session[s:])
        return result

    def _validate(self, hook: Hook) -> None:
        """Validate hook definition. Raises ValidationError on failure."""
        if not re.match(r'^[a-z0-9_-]{1,64}$', hook.name):
            raise ValidationError(f"Invalid hook name: '{hook.name}'")
        if hook.type not in HookType:
            raise ValidationError(f"Invalid hook type: '{hook.type}'")
        if not (0 <= hook.priority <= 100):
            raise ValidationError(f"Priority must be 0-100, got: {hook.priority}")
        if not (1 <= hook.timeout_ms <= 30000):
            raise ValidationError(f"Timeout must be 1-30000ms, got: {hook.timeout_ms}")
        if not callable(hook.action):
            raise ValidationError("Hook action must be callable")
```

### 10.2 Chain Executor

```python
# Reference implementation -- pseudocode

class ChainExecutor:
    def __init__(self, registry: HookRegistry):
        self._registry = registry

    def execute(
        self,
        hook_type: HookType,
        session_id: str,
        context: VCPContext,
        constitution: Constitution,
        event: HookEvent
    ) -> ChainResult:
        """Execute the hook chain for the given type and return the final result."""
        chain = self._registry.get_chain(hook_type, session_id)
        chain_state = {}
        current_context = context
        current_constitution = constitution
        results = []
        errors = 0

        for hook in chain:
            if not hook.enabled:
                emit_event("hook.skipped", {"hook": hook.name, "reason": "disabled"})
                continue

            # Evaluate predicate
            hook_input = HookInput(
                context=current_context,
                constitution=current_constitution,
                event=event,
                session=get_session_info(session_id),
                chain_state=chain_state
            )

            if hook.condition is not None:
                if not evaluate_predicate(hook.condition, hook_input):
                    emit_event("hook.skipped", {"hook": hook.name, "reason": "predicate_false"})
                    continue

            # Execute with timeout
            emit_event("hook.fired", {"hook": hook.name})
            start_time = now_ms()

            try:
                result = execute_with_timeout(hook.action, hook_input, hook.timeout_ms)
            except TimeoutError:
                elapsed = now_ms() - start_time
                emit_event("hook.timeout", {
                    "hook": hook.name,
                    "timeout_ms": hook.timeout_ms,
                    "elapsed_ms": elapsed
                })
                result = HookResult(status="continue")
                errors += 1
            except Exception as exc:
                emit_event("hook.error", {
                    "hook": hook.name,
                    "error": str(exc),
                    "traceback": format_traceback(exc)
                })
                result = HookResult(status="continue")
                errors += 1

            duration = now_ms() - start_time
            result.duration_ms = duration
            results.append((hook.name, result))

            emit_event("hook.completed", {
                "hook": hook.name,
                "status": result.status,
                "duration_ms": duration
            })

            # Process result
            if result.status == "abort":
                return ChainResult(
                    status="aborted",
                    reason=result.reason,
                    context=current_context,
                    constitution=current_constitution,
                    hook_results=results,
                    aborted_by=hook.name
                )
            elif result.status == "modify":
                if result.modified_context is not None:
                    current_context = result.modified_context
                if result.modified_constitution is not None:
                    current_constitution = result.modified_constitution

        # Check for cascading failures
        total_executed = len([r for r in results])
        if total_executed > 0 and errors / total_executed > 0.5:
            emit_event("hook.cascade_failure", {
                "hook_type": hook_type,
                "total": total_executed,
                "errors": errors
            })

        return ChainResult(
            status="completed",
            context=current_context,
            constitution=current_constitution,
            hook_results=results
        )


class ChainResult:
    status: str              # "completed" | "aborted"
    reason: str | None       # Set when aborted
    context: VCPContext       # Final context (possibly modified)
    constitution: Constitution  # Final constitution (possibly modified)
    hook_results: list[tuple[str, HookResult]]
    aborted_by: str | None   # Hook name that aborted, if any
```

### 10.3 Periodic Hook Scheduler

```python
# Reference implementation -- pseudocode

class PeriodicScheduler:
    def __init__(self, registry: HookRegistry, executor: ChainExecutor):
        self._registry = registry
        self._executor = executor
        self._timers: dict[str, Timer] = {}
        self._tick_counts: dict[str, int] = {}

    def start_session(self, session_id: str) -> None:
        """Start periodic hooks for a session."""
        chain = self._registry.get_chain(HookType.PERIODIC, session_id)
        for hook in chain:
            interval_ms = hook.metadata.get("interval_ms", 60000)
            if interval_ms < 1000:
                interval_ms = 1000  # Enforce minimum 1 second
            key = f"{session_id}:{hook.name}"
            self._tick_counts[key] = 0
            self._timers[key] = create_repeating_timer(
                interval_ms=interval_ms,
                callback=lambda h=hook, s=session_id: self._fire(h, s)
            )

    def stop_session(self, session_id: str) -> None:
        """Stop all periodic hooks for a session."""
        keys_to_remove = [k for k in self._timers if k.startswith(f"{session_id}:")]
        for key in keys_to_remove:
            self._timers[key].cancel()
            del self._timers[key]
            del self._tick_counts[key]

    def _fire(self, hook: Hook, session_id: str) -> None:
        """Fire a single periodic hook."""
        key = f"{session_id}:{hook.name}"
        self._tick_counts[key] += 1

        event = PeriodicEvent(
            elapsed_ms=hook.metadata.get("interval_ms", 60000),
            interval_ms=hook.metadata.get("interval_ms", 60000),
            tick_count=self._tick_counts[key]
        )

        context = get_current_context(session_id)
        constitution = get_current_constitution(session_id)

        result = self._executor.execute(
            hook_type=HookType.PERIODIC,
            session_id=session_id,
            context=context,
            constitution=constitution,
            event=event
        )

        if result.status == "completed" and result.context != context:
            trigger_context_reevaluation(session_id, result.context)
```

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-15 | Initial specification: 6 hook types, interface definitions, execution model, security considerations, reference implementation |

---

## License

This specification is licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

You are free to share and adapt this material for any purpose, including commercially, provided you give appropriate attribution.

**Attribution**: VCP Hook System Specification, Creed Space, 2026.
