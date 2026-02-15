# VCP Integration Guide

**For**: Framework developers adding VCP support to agent frameworks
**Time to integrate**: ~100 lines of code, ~1 hour
**Prerequisites**: Python 3.10+ or Node.js 18+

The Value-Context Protocol (VCP) is a layered protocol for expressing, transporting, and applying constitutional values to AI systems. If your framework already configures agent behavior with system prompts, roles, or safety rules, VCP standardizes that configuration so it's portable, verifiable, and auditable across frameworks.

This guide gets you from zero to a working VCP integration in 5 functions. For the full protocol specification, see [VCP_OVERVIEW.md](VCP_OVERVIEW.md). For conceptual background, see [VCP_NEWCOMER_GUIDE.md](VCP_NEWCOMER_GUIDE.md).

---

## Minimum Viable Integration

Every VCP integration needs these 5 capabilities. Each maps to a VCP protocol layer.

### 1. Load a Constitution (VCP/T -- Transport)

Fetch a signed constitution bundle from a `creed://` URI and verify its signature.

```python
import json
import hashlib
from dataclasses import dataclass


@dataclass
class Constitution:
    """A verified VCP constitution."""
    token: str          # e.g., "family.safe.guide@1.2.0"
    content: str        # The constitution text (rules, guidelines)
    content_hash: str   # SHA-256 hash for verification
    csm1: str           # e.g., "N5+F+E"
    signature: str      # Ed25519 signature (base64)
    issuer: str         # e.g., "creed://creed.space"


def load_constitution(bundle_json: str) -> Constitution:
    """Load and verify a VCP constitution bundle.

    Args:
        bundle_json: JSON string of a signed VCP bundle.

    Returns:
        Verified Constitution ready for use.

    Raises:
        ValueError: If content hash doesn't match (tampered bundle).
    """
    bundle = json.loads(bundle_json)
    manifest = bundle["manifest"]
    content = bundle["content"]

    # Verify content integrity (SHA-256)
    computed_hash = "sha256:" + hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()

    if computed_hash != manifest["bundle"]["content_hash"]:
        raise ValueError(
            f"Content hash mismatch: expected {manifest['bundle']['content_hash']}, "
            f"got {computed_hash}"
        )

    return Constitution(
        token=manifest["bundle"]["id"] + "@" + manifest["bundle"]["version"],
        content=content,
        content_hash=computed_hash,
        csm1=manifest.get("metadata", {}).get("csm1", "G3"),
        signature=manifest["signature"]["value"],
        issuer=manifest["issuer"]["id"],
    )
```

**What this does**: Parses a VCP bundle (JSON with manifest + content), verifies the SHA-256 content hash to confirm the constitution hasn't been tampered with, and returns a typed object your framework can use. For full Ed25519 signature verification, use the SDK (see "Using the SDK" below).

### 2. Parse a CSM-1 Code (VCP/S -- Semantics)

CSM-1 (Constitutional Semantics Mark 1) is a compact string that encodes persona, adherence level, scopes, namespace, and version. Format: `{Persona}{Level}[+{Scope}]*[:{Namespace}][@{Version}]`

```python
import re
from dataclasses import dataclass, field


# The 6+1 persona archetypes
PERSONAS = {
    "N": ("NANNY",      "Child safety specialist"),
    "Z": ("SENTINEL",   "Security and privacy guardian"),
    "G": ("GODPARENT",  "Ethical guidance counselor"),
    "A": ("AMBASSADOR", "Professional conduct advisor"),
    "M": ("MUSE",       "Creative challenge and provocation"),
    "D": ("MEDIATOR",   "Fair resolution and balanced governance"),
    "C": ("CUSTOM",     "User-defined persona"),
}

# The 11 context scopes
SCOPES = {
    "F": "Family",   "W": "Work",        "E": "Education",
    "H": "Healthcare", "I": "Finance",   "L": "Legal",
    "P": "Privacy",  "S": "Safety",       "A": "Accessibility",
    "V": "Environment", "G": "General",
}

CSM1_PATTERN = re.compile(
    r"^(?P<persona>[NZGAMDC])"
    r"(?P<level>[0-5])"
    r"(?P<scopes>(?:\+[FWEHILPSAVG])*)"
    r"(?::(?P<namespace>[A-Z][A-Z0-9]*))?"
    r"(?:@(?P<version>\d+\.\d+\.\d+))?$"
)


@dataclass
class Csm1Config:
    """Parsed CSM-1 constitutional profile."""
    persona: str            # e.g., "NANNY"
    persona_code: str       # e.g., "N"
    persona_description: str
    adherence: int          # 0 (disabled) to 5 (maximum)
    scopes: list[str] = field(default_factory=list)  # e.g., ["Family", "Education"]
    namespace: str | None = None
    version: str | None = None


def parse_csm1(code: str) -> Csm1Config:
    """Parse a CSM-1 code string into its components.

    Args:
        code: CSM-1 string, e.g., "N5+F+E", "Z3+P:SEC", "G4@1.0.0"

    Returns:
        Parsed Csm1Config with persona, adherence, scopes, etc.

    Raises:
        ValueError: If code format is invalid.
    """
    match = CSM1_PATTERN.match(code.upper())
    if not match:
        raise ValueError(f"Invalid CSM-1 code: {code}")

    groups = match.groupdict()
    persona_char = groups["persona"]
    persona_name, persona_desc = PERSONAS[persona_char]

    scopes = []
    if groups["scopes"]:
        scope_chars = groups["scopes"].replace("+", "")
        scopes = [SCOPES[c] for c in scope_chars]

    return Csm1Config(
        persona=persona_name,
        persona_code=persona_char,
        persona_description=persona_desc,
        adherence=int(groups["level"]),
        scopes=scopes,
        namespace=groups.get("namespace"),
        version=groups.get("version"),
    )
```

**Examples**:

| Code | Persona | Adherence | Scopes |
|------|---------|-----------|--------|
| `N5+F+E` | NANNY | 5 (max) | Family, Education |
| `Z3+P` | SENTINEL | 3 (moderate) | Privacy |
| `A4+W+L` | AMBASSADOR | 4 (high) | Work, Legal |
| `M2` | MUSE | 2 (light) | (all -- no scope restriction) |
| `G4:ELEM@1.2.0` | GODPARENT | 4 | (all), namespace ELEM, version 1.2.0 |

### 3. Apply Persona to Agent (VCP/S -- Semantics)

Map the parsed persona and adherence level to your framework's agent configuration.

```python
# Persona system prompts, scaled by adherence level.
# Adherence 0 = disabled, 1 = minimal guidance, 5 = maximum enforcement.
PERSONA_PROMPTS = {
    "NANNY": {
        "role": "You are a protective guide prioritizing child safety.",
        "rules": [
            "Filter all content for age-appropriateness.",
            "Never generate violent, sexual, or frightening content.",
            "Use simple, encouraging language.",
            "When uncertain about safety, err on the side of caution.",
            "Redirect harmful requests to safe alternatives.",
        ],
    },
    "SENTINEL": {
        "role": "You are a security guardian protecting user privacy and data.",
        "rules": [
            "Never reveal, log, or transmit personal data without consent.",
            "Flag potential security vulnerabilities in user requests.",
            "Enforce data minimization -- collect only what's needed.",
            "Warn users before they share sensitive information.",
            "Assume adversarial intent for ambiguous requests.",
        ],
    },
    "GODPARENT": {
        "role": "You are an ethical guidance counselor fostering good judgment.",
        "rules": [
            "Present multiple perspectives on ethical questions.",
            "Encourage critical thinking over blind compliance.",
            "Acknowledge moral complexity without false equivalence.",
            "Guide toward prosocial outcomes without being preachy.",
            "Respect user autonomy while raising ethical considerations.",
        ],
    },
    "AMBASSADOR": {
        "role": "You are a professional representative maintaining organizational standards.",
        "rules": [
            "Maintain formal, professional tone appropriate to context.",
            "Represent organizational values accurately.",
            "Avoid controversial personal opinions.",
            "Defer to organizational policy on sensitive topics.",
            "Prioritize clarity and accuracy in all communications.",
        ],
    },
    "MUSE": {
        "role": "You are a creative collaborator who challenges and provokes constructive thinking.",
        "rules": [
            "Offer unexpected perspectives and creative alternatives.",
            "Challenge assumptions respectfully but directly.",
            "Prioritize novelty and originality in suggestions.",
            "Accept creative risk while maintaining ethical boundaries.",
            "Celebrate experimentation and iterative exploration.",
        ],
    },
    "MEDIATOR": {
        "role": "You are a fair arbiter focused on balanced resolution and governance.",
        "rules": [
            "Present all sides of a dispute without bias.",
            "Seek common ground before highlighting differences.",
            "Apply consistent principles across similar situations.",
            "Acknowledge power dynamics and work to equalize them.",
            "Prioritize procedural fairness and transparency.",
        ],
    },
}


def apply_persona(agent, persona: str, adherence: int, scopes: list[str] | None = None):
    """Configure an agent's behavior based on VCP persona and adherence.

    Args:
        agent: Your framework's agent object (must support .system_prompt or similar).
        persona: Persona name, e.g., "NANNY", "SENTINEL".
        adherence: Adherence level 0-5 (0 = disabled).
        scopes: Optional list of active scopes, e.g., ["Family", "Education"].
    """
    if adherence == 0:
        return  # Persona disabled

    config = PERSONA_PROMPTS.get(persona)
    if not config:
        return  # Unknown persona (or CUSTOM -- implement your own)

    # Scale rules by adherence: level 1 = first rule only, level 5 = all rules
    active_rules = config["rules"][:adherence]

    # Build system prompt
    scope_text = ""
    if scopes:
        scope_text = f"\nActive scopes: {', '.join(scopes)}."

    prompt = (
        f"{config['role']}\n\n"
        f"Constitutional rules (adherence level {adherence}/5):\n"
        + "\n".join(f"- {rule}" for rule in active_rules)
        + scope_text
    )

    # Apply to agent -- adapt this to your framework's API
    # LangChain: agent.system_message = SystemMessage(content=prompt)
    # AutoGen:   agent.system_message = prompt
    # CrewAI:    agent.backstory = prompt
    agent.system_prompt = prompt
```

### 4. Encode Context (VCP/A -- Adaptation)

Encode situational context into the Enneagram wire format -- 9 dimensions represented as emoji strings.

```python
# Dimension symbols and their value mappings
DIMENSIONS = {
    "time":        ("⏰", {"morning": "🌅", "midday": "☀️", "evening": "🌆", "night": "🌙"}),
    "space":       ("📍", {"home": "🏡", "office": "🏢", "school": "🏫", "hospital": "🏥", "transit": "🚗"}),
    "company":     ("👥", {"alone": "👤", "children": "👶", "colleagues": "👔", "family": "👨‍👩‍👧", "strangers": "👥"}),
    "culture":     ("🌍", {"global": "🌍", "american": "🇺🇸", "european": "🇪🇺", "japanese": "🇯🇵"}),
    "occasion":    ("🎭", {"normal": "➖", "celebration": "🎂", "mourning": "😢", "emergency": "🚨"}),
    "state":       ("🧠", {"happy": "😊", "anxious": "😰", "tired": "😴", "contemplative": "🤔", "frustrated": "😤"}),
    "environment": ("🌡️", {"comfortable": "☀️", "hot": "🥵", "cold": "🥶", "quiet": "🔇", "noisy": "🔊"}),
    "agency":      ("🔷", {"leader": "👑", "peer": "🤝", "subordinate": "📋", "limited": "🔐"}),
    "constraints": ("🔶", {"minimal": "○", "legal": "⚖️", "economic": "💸", "time": "⏱️"}),
}


def encode_context(**kwargs: str | list[str]) -> str:
    """Encode situational context to the Enneagram wire format.

    Args:
        **kwargs: Dimension name -> value(s). Accepts strings or lists of strings.
            time="morning", space="home", company=["children", "family"]

    Returns:
        Wire-format string, e.g., "⏰🌅|📍🏡|👥👶👨‍👩‍👧"
    """
    parts = []
    for dim_name, (symbol, values_map) in DIMENSIONS.items():
        if dim_name not in kwargs:
            continue

        raw = kwargs[dim_name]
        if isinstance(raw, str):
            raw = [raw]

        emojis = []
        for v in raw:
            emoji = values_map.get(v.lower())
            if emoji:
                emojis.append(emoji)

        if emojis:
            parts.append(symbol + "".join(emojis))

    return "|".join(parts)
```

**Examples**:

```python
encode_context(time="morning", space="home", company=["children"])
# => "⏰🌅|📍🏡|👥👶"

encode_context(time="evening", space="office", agency="leader", constraints="legal")
# => "⏰🌆|📍🏢|🔷👑|🔶⚖️"

encode_context(occasion="emergency")
# => "🎭🚨"
```

### 5. Log a Decision (VCP/T -- Transport / Audit)

Record an audit trail entry for every constitutional decision. This is what makes VCP verifiable.

```python
import hashlib
from datetime import datetime, timezone


def log_decision(
    constitution_hash: str,
    csm1: str,
    result: str,
    context_wire: str = "",
    session_id: str = "",
    latency_ms: int | None = None,
) -> dict:
    """Create an audit trail entry for a constitutional decision.

    Args:
        constitution_hash: SHA-256 hash of the active constitution content.
        csm1: Active CSM-1 code, e.g., "N5+F+E".
        result: Decision outcome -- one of "allow", "block", "modify", "escalate".
        context_wire: Enneagram wire format context string.
        session_id: Session identifier (will be hashed for privacy).
        latency_ms: Decision latency in milliseconds.

    Returns:
        Audit entry dict, ready for logging to file, database, or external service.
    """
    # Hash session ID for privacy (never store raw session IDs in audit logs)
    session_hash = ""
    if session_id:
        session_hash = "sha256:" + hashlib.sha256(
            session_id.encode()
        ).hexdigest()[:32]

    entry = {
        "vcp_audit_version": "1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id_hash": session_hash,
        "constitution_hash": constitution_hash,
        "csm1": csm1,
        "vcp_context_wire": context_wire,
        "outcome": result,
    }

    if latency_ms is not None:
        entry["latency_ms"] = latency_ms

    # In production, append to structured log or send to audit service
    # Example: logger.info(json.dumps(entry))
    return entry
```

**Example output**:

```json
{
  "vcp_audit_version": "1.0",
  "timestamp": "2026-02-15T10:30:00+00:00",
  "session_id_hash": "sha256:a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6",
  "constitution_hash": "sha256:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
  "csm1": "N5+F+E",
  "vcp_context_wire": "⏰🌅|📍🏡|👥👶",
  "outcome": "allow",
  "latency_ms": 12
}
```

---

## Putting It All Together

Here's how the 5 functions compose into a complete request lifecycle:

```python
# --- Setup (once at startup) ---
constitution = load_constitution(bundle_json)
csm1 = parse_csm1(constitution.csm1)

# --- Per-request (in your agent middleware) ---

# 1. Encode the current context
context_wire = encode_context(
    time="morning",
    space="home",
    company=["children"],
)

# 2. Apply persona to agent
apply_persona(
    agent=my_agent,
    persona=csm1.persona,
    adherence=csm1.adherence,
    scopes=csm1.scopes,
)

# 3. Run the agent (your framework handles this)
response = my_agent.run(user_message)

# 4. Log the decision
log_decision(
    constitution_hash=constitution.content_hash,
    csm1=constitution.csm1,
    result="allow",
    context_wire=context_wire,
    session_id=session.id,
    latency_ms=12,
)
```

---

## Framework-Specific Examples

### LangChain

VCP integrates as a callback handler that injects persona configuration before each LLM call.

```python
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI


class VCPCallbackHandler(BaseCallbackHandler):
    """Inject VCP persona and context into every LangChain LLM call."""

    def __init__(self, bundle_json: str, **context_kwargs):
        self.constitution = load_constitution(bundle_json)
        self.csm1 = parse_csm1(self.constitution.csm1)
        self.context_wire = encode_context(**context_kwargs)

    def on_llm_start(self, serialized, prompts, **kwargs):
        """Prepend persona rules to the prompt before LLM call."""
        config = PERSONA_PROMPTS.get(self.csm1.persona, {})
        active_rules = config.get("rules", [])[:self.csm1.adherence]
        scope_text = ""
        if self.csm1.scopes:
            scope_text = f" Scopes: {', '.join(self.csm1.scopes)}."

        persona_prefix = (
            f"[VCP {self.constitution.csm1}] {config.get('role', '')}\n"
            f"Rules: {'; '.join(active_rules)}.{scope_text}\n"
            f"Context: {self.context_wire}\n\n"
        )

        # Prepend to each prompt
        for i, prompt in enumerate(prompts):
            prompts[i] = persona_prefix + prompt

    def on_llm_end(self, response, **kwargs):
        """Log audit entry after each LLM call."""
        log_decision(
            constitution_hash=self.constitution.content_hash,
            csm1=self.constitution.csm1,
            result="allow",
            context_wire=self.context_wire,
        )


# Usage
handler = VCPCallbackHandler(
    bundle_json=open("family_safe.vcp.json").read(),
    time="morning",
    space="home",
    company=["children"],
)

llm = ChatOpenAI(model="gpt-4o", callbacks=[handler])
result = llm.invoke("Tell me a bedtime story")
```

Alternatively, wrap VCP as a LangChain Tool for agents that need to query their own constitution:

```python
from langchain_core.tools import tool


@tool
def check_constitution(query: str) -> str:
    """Check if a proposed action is allowed by the active constitution."""
    constitution = load_constitution(bundle_json)
    csm1 = parse_csm1(constitution.csm1)
    return (
        f"Active constitution: {constitution.token}\n"
        f"Persona: {csm1.persona} (adherence {csm1.adherence}/5)\n"
        f"Scopes: {', '.join(csm1.scopes) or 'all'}\n"
        f"Rules:\n{constitution.content[:500]}"
    )
```

### AutoGen

VCP maps to AutoGen's agent configuration and message filtering.

```python
from autogen import AssistantAgent, UserProxyAgent


def create_vcp_agent(
    name: str,
    bundle_json: str,
    llm_config: dict,
    **context_kwargs,
) -> AssistantAgent:
    """Create an AutoGen agent configured with a VCP constitution."""
    constitution = load_constitution(bundle_json)
    csm1 = parse_csm1(constitution.csm1)
    context_wire = encode_context(**context_kwargs)

    config = PERSONA_PROMPTS.get(csm1.persona, {})
    active_rules = config.get("rules", [])[:csm1.adherence]
    scope_text = ""
    if csm1.scopes:
        scope_text = f"\nActive scopes: {', '.join(csm1.scopes)}."

    system_message = (
        f"{config.get('role', '')}\n\n"
        f"Constitutional rules (adherence {csm1.adherence}/5):\n"
        + "\n".join(f"- {rule}" for rule in active_rules)
        + scope_text
        + f"\n\nVCP Context: {context_wire}"
        + f"\nConstitution: {constitution.token}"
    )

    return AssistantAgent(
        name=name,
        system_message=system_message,
        llm_config=llm_config,
    )


# Usage: create two agents with different personas from the same constitution
nanny_agent = create_vcp_agent(
    name="child_safety_agent",
    bundle_json=open("family_safe.vcp.json").read(),
    llm_config={"model": "gpt-4o"},
    time="morning",
    space="home",
    company=["children"],
)

# For multi-agent handoff, pass the context wire between agents
user_proxy = UserProxyAgent(name="user", human_input_mode="NEVER")
user_proxy.initiate_chat(nanny_agent, message="What games can we play?")
```

### CrewAI

VCP personas map directly to CrewAI's `role`, `goal`, and `backstory` parameters.

```python
from crewai import Agent, Task, Crew


def create_vcp_crew_agent(
    bundle_json: str,
    goal: str,
    **context_kwargs,
) -> Agent:
    """Create a CrewAI agent configured with a VCP constitution."""
    constitution = load_constitution(bundle_json)
    csm1 = parse_csm1(constitution.csm1)
    context_wire = encode_context(**context_kwargs)

    config = PERSONA_PROMPTS.get(csm1.persona, {})
    active_rules = config.get("rules", [])[:csm1.adherence]

    backstory = (
        f"Operating under constitution {constitution.token} "
        f"({constitution.csm1}).\n"
        f"Context: {context_wire}\n\n"
        f"Constitutional rules:\n"
        + "\n".join(f"- {rule}" for rule in active_rules)
    )

    scope_text = ""
    if csm1.scopes:
        scope_text = f" [{', '.join(csm1.scopes)}]"

    return Agent(
        role=f"{csm1.persona}{scope_text}",
        goal=goal,
        backstory=backstory,
        verbose=True,
    )


# Usage
safety_agent = create_vcp_crew_agent(
    bundle_json=open("family_safe.vcp.json").read(),
    goal="Review content for child safety",
    time="morning",
    space="home",
    company=["children"],
)

review_task = Task(
    description="Review this story for age-appropriateness.",
    agent=safety_agent,
    expected_output="Safety assessment with pass/fail and reasoning.",
)

crew = Crew(agents=[safety_agent], tasks=[review_task])
result = crew.kickoff()
```

---

## Using the SDK (Shortcut)

The reference SDK handles bundle verification, CSM-1 parsing, context encoding, state tracking, and audit logging out of the box. If you don't need a custom implementation, this is the fastest path.

### Python

```bash
pip install vcp
```

```python
from vcp import (
    Bundle,
    CSM1Code,
    ContextEncoder,
    StateTracker,
    AuditLogger,
    AuditLevel,
    Token,
    Orchestrator,
    TrustConfig,
)

# Parse a constitution bundle
bundle = Bundle.from_json(open("family_safe.vcp.json").read())

# Verify the bundle (full signature + hash + temporal + scope checks)
trust = TrustConfig.from_file("trust_anchors.json")
orchestrator = Orchestrator(trust_config=trust)
result = orchestrator.verify(bundle)
assert result.is_valid, f"Bundle verification failed: {result.name}"

# Parse CSM-1 code
csm1 = CSM1Code.parse("N5+F+E")
print(csm1.persona)          # Persona.NANNY
print(csm1.adherence_level)  # 5
print(csm1.scopes)           # [Scope.FAMILY, Scope.EDUCATION]

# Encode context
encoder = ContextEncoder()
ctx = encoder.encode(time="morning", space="home", company=["children"])
print(ctx.encode())           # "⏰🌅|📍🏡|👥👶"

# Track state transitions
tracker = StateTracker(max_history=100)
transition = tracker.record(ctx)

# Later, context changes...
ctx2 = encoder.encode(time="evening", space="office", agency="leader")
transition = tracker.record(ctx2)
if transition and transition.is_significant:
    print(f"Significant transition: {transition.severity.value}")
    # Re-evaluate persona or escalate

# Audit logging
logger = AuditLogger(level=AuditLevel.STANDARD)
entry = logger.log_verification(bundle, result, session_id="sess-123")
print(entry.to_json())

# Parse identity tokens
token = Token.parse("family.safe.guide@1.2.0")
print(token.canonical)  # "family.safe.guide"
print(token.domain)     # "family"
print(token.role)       # "guide"
print(token.to_uri())   # "creed://creed.space/family.safe.guide@1.2.0"
```

### JavaScript / TypeScript

```bash
npm install @valuecontextprotocol/sdk
```

```typescript
import { Bundle, CSM1Code, ContextEncoder, Token } from '@valuecontextprotocol/sdk';

const bundle = Bundle.fromJSON(fs.readFileSync('family_safe.vcp.json', 'utf8'));
const csm1 = CSM1Code.parse('N5+F+E');
const token = Token.parse('family.safe.guide@1.2.0');

console.log(csm1.persona);        // "NANNY"
console.log(csm1.adherenceLevel); // 5
console.log(token.toUri());       // "creed://creed.space/family.safe.guide@1.2.0"
```

---

## Conformance

To verify your implementation is VCP-compliant, run the conformance test vectors in the [VCP-Spec repository](https://github.com/Creed-Space/VCP-Spec).

### Identity Layer (VCP/I) -- Token Parsing

| Input | Expected | Reason |
|-------|----------|--------|
| `family.safe.guide` | VALID: domain=family, approach=safe, role=guide | Minimum 3 segments |
| `family.safe.guide@1.2.0` | VALID: version=1.2.0 | Version suffix |
| `company.acme.legal.compliance` | VALID: 4 segments, domain=company, role=compliance | Variable-length token |
| `family.safe.guide:SEC` | VALID: namespace=SEC | Namespace suffix |
| `ab` | INVALID | Less than 3 segments |
| `FAMILY.Safe.Guide` | INVALID | Segments must be lowercase |
| (256+ chars) | INVALID | Exceeds max length |

### Semantics Layer (VCP/S) -- CSM-1 Parsing

| Input | Expected |
|-------|----------|
| `N5+F+E` | persona=NANNY, level=5, scopes=[FAMILY, EDUCATION] |
| `Z3+P` | persona=SENTINEL, level=3, scopes=[PRIVACY] |
| `G0` | persona=GODPARENT, level=0 (disabled) |
| `M2@1.0.0` | persona=MUSE, level=2, version=1.0.0 |
| `D4:ELEM` | persona=MEDIATOR, level=4, namespace=ELEM |
| `C5+F+W+E+H` | persona=CUSTOM, level=5, scopes=[FAMILY, WORK, EDUCATION, HEALTHCARE] |
| `X5` | INVALID (unknown persona) |
| `N6` | INVALID (level must be 0-5) |
| `N5+Q` | INVALID (unknown scope) |

### Adaptation Layer (VCP/A) -- Context Encoding

| Input | Expected Wire Format |
|-------|---------------------|
| time=morning, space=home | `⏰🌅\|📍🏡` |
| company=[children, family] | `👥👶👨‍👩‍👧` |
| occasion=emergency | `🎭🚨` (triggers EMERGENCY severity) |
| (empty) | `""` (empty string) |

### Transport Layer (VCP/T) -- Bundle Verification

| Condition | Expected Result |
|-----------|----------------|
| Valid bundle, correct hash | `VALID` |
| Tampered content (hash mismatch) | `HASH_MISMATCH` |
| Unknown issuer | `UNTRUSTED_ISSUER` |
| Expired bundle | `EXPIRED` |
| Future not-before time | `NOT_YET_VALID` |
| Bundle exceeds 256 KB content | `SIZE_EXCEEDED` |
| Same JTI seen twice | `REPLAY_DETECTED` |
| Token budget exceeds context share | `BUDGET_EXCEEDED` |

If your implementation produces the expected results for all test vectors above, it is VCP-compliant.

For the full conformance test suite as runnable code, see the `schemas/` and `specs/` directories in the VCP-Spec repository.

---

## Quick Reference

### CSM-1 Personas (NZGAMDC)

| Code | Name | Role |
|------|------|------|
| N | Nanny | Child safety specialist |
| Z | Sentinel | Security and privacy guardian |
| G | Godparent | Ethical guidance counselor |
| A | Ambassador | Professional conduct advisor |
| M | Muse | Creative challenge and provocation |
| D | Mediator | Fair resolution and balanced governance |
| C | Custom | User-defined persona |

### CSM-1 Scopes

| Code | Scope | Code | Scope |
|------|-------|------|-------|
| F | Family | L | Legal |
| W | Work | P | Privacy |
| E | Education | S | Safety |
| H | Healthcare | A | Accessibility |
| I | Finance | V | Environment |
| G | General | | |

### Enneagram Dimensions

| # | Symbol | Dimension | Example Values |
|---|--------|-----------|----------------|
| 1 | ⏰ | Time | morning, midday, evening, night |
| 2 | 📍 | Space | home, office, school, hospital, transit |
| 3 | 👥 | Company | alone, children, colleagues, family, strangers |
| 4 | 🌍 | Culture | global, american, european, japanese |
| 5 | 🎭 | Occasion | normal, celebration, mourning, emergency |
| 6 | 🧠 | State | happy, anxious, tired, contemplative, frustrated |
| 7 | 🌡️ | Environment | comfortable, hot, cold, quiet, noisy |
| 8 | 🔷 | Agency | leader, peer, subordinate, limited |
| 9 | 🔶 | Constraints | minimal, legal, economic, time |

### Bundle Verification Results

| Result | Category | Action |
|--------|----------|--------|
| `VALID` | Success | Proceed |
| `HASH_MISMATCH` | Security | Reject -- content tampered |
| `INVALID_SIGNATURE` | Security | Reject -- signature forged |
| `UNTRUSTED_ISSUER` | Configuration | Reject -- add issuer to trust config |
| `EXPIRED` | Temporal | Reject -- request updated bundle |
| `NOT_YET_VALID` | Temporal | Reject -- bundle not active yet |
| `REPLAY_DETECTED` | Security | Reject -- duplicate JTI |
| `BUDGET_EXCEEDED` | Configuration | Reject -- constitution too large for context |
| `SCOPE_MISMATCH` | Configuration | Reject -- wrong model/purpose/environment |

---

## Further Reading

- [VCP Overview](VCP_OVERVIEW.md) -- Full protocol specification
- [VCP Newcomer Guide](VCP_NEWCOMER_GUIDE.md) -- Conceptual introduction with architecture diagrams
- [VCP Adoption Strategy](VCP_ADOPTION_STRATEGY.md) -- Strategic context for framework partnerships
- [VCP Context Data Flow](VCP_CONTEXT_DATA_FLOW.md) -- Detailed data flow and security model
- [Python SDK source](https://github.com/Creed-Space/vcp-sdk) -- Reference implementation
