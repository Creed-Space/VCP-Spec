# VCP/I -- Identity Layer Specification v2.0

**Status**: Draft
**Version**: 2.0.0
**Date**: 2026-03-08
**Authors**: Nell Watson, Claude Commons
**Parent Specification**: VCP Core Specification v2.0
**Layer**: Identity (VCP/I)

---

## Abstract

This specification defines the VCP Identity Layer (VCP/I), the innermost layer of the Value Context Protocol. VCP/I provides unique, human-readable, namespace-governed, version-aware identifiers for constitutional values and behavioral rules. It defines the token format, naming conventions, namespace governance, registry protocol, value ontology, and encoding algorithms that enable constitutions to be addressed, discovered, resolved, and verified across implementations and organizations.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Token Format](#2-token-format)
3. [Naming Conventions](#3-naming-conventions)
4. [Namespace Governance](#4-namespace-governance)
5. [Registry Protocol](#5-registry-protocol)
6. [Value Ontology](#6-value-ontology)
7. [Encoding Algorithms](#7-encoding-algorithms)
8. [Security Considerations](#8-security-considerations)

---

## 1. Overview

### 1.1 Purpose

The VCP Identity Layer provides the addressing foundation for the Value Context Protocol. Every constitution, value bundle, and behavioral rule in the VCP ecosystem is identified by a Universal Value Code (UVC) token -- a portable, human-readable name that resolves to a specific resource.

VCP/I enables:

- **Unique identification**: Every constitutional value has a canonical name
- **Human readability**: `family.safe.guide` is self-documenting
- **Namespace governance**: Organizational control over naming
- **Version awareness**: Semantic versioning for evolution
- **Multi-format encoding**: Tokens can be represented in formats optimized for different use cases (wire protocols, voice communication, privacy contexts, physical media)
- **Registry resolution**: Tokens resolve to bundle URIs via a federated registry protocol
- **Semantic grounding**: An optional value ontology provides conflict detection, composition support, and cross-cultural translation

### 1.2 Relationship to Other Layers

VCP/I is the innermost layer of the VCP protocol stack:

```
VCP/A (Adaptation) ── outermost
VCP/S (Semantics)
VCP/T (Transport)  ── specified in VCP Core Specification v2.0
VCP/I (Identity)   ── innermost: token, version, namespace reference
```

Tokens are names that resolve to bundles. VCP/I is content-agnostic -- it names resources without prescribing their semantics, transport, or adaptation behavior. The other layers encapsulate VCP/I data:

| Layer | Encapsulates | Data Contents |
|-------|-------------|---------------|
| VCP/I (innermost) | Constitutional content | Identity: token, version, namespace reference |
| VCP/T (Core Spec) | VCP/I + content | Transport: digital signature, verification hash, bundle manifest |
| VCP/S | VCP/T + VCP/I + content | Semantics: CSM1 rules, composition metadata, persona assignments |
| VCP/A (outermost) | VCP/S + VCP/T + VCP/I + content | Context: situational state, transition signals, adaptation hooks |

> **Note**: VCP/T (Transport) is specified within the VCP Core Specification v2.0 (`VCP_SPECIFICATION_v2.0.md`) rather than as a separate companion document.

### 1.3 Registry Operations

VCP/I registries MUST support the following operations:

```
RESOLVE(token) -> constitution_metadata
SEARCH(pattern) -> matching_tokens
REGISTER(token, metadata) -> success/failure
VERIFY(token) -> ownership_proof
```

### 1.4 Conformance

Implementations claiming VCP-Minimal conformance MUST:

- Parse and validate identity tokens according to the grammar in Section 3
- Verify signatures on resolved bundles
- Reject tampered bundles

Implementations claiming VCP-Standard conformance MUST additionally:

- Support resolution via at least one registry method (Section 5)
- Support the canonical and URI encoding formats (Section 2)

Implementations claiming VCP-Full conformance MUST additionally:

- Support all reversible encoding formats defined in Section 2
- Support privacy-preserving queries (Section 5)

### 1.5 Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in RFC 2119.

---

## 2. Token Format

### 2.1 Format Registry

A single UVC token can be represented in multiple encoding formats, each optimized for different use cases. All formats (except hash) are reversible back to canonical form.

| Format | Length | Human-Readable | Privacy | Machine-Parseable | Use Case |
|--------|--------|----------------|---------|-------------------|----------|
| Canonical | Variable | Yes | No | Yes | Storage, comparison, hashing |
| CSM1 | Short | Partial | No | Yes | Wire protocols, API headers |
| URI | Long | Yes | No | Yes | Web addressing, links |
| Hash | Fixed | No | Yes | Yes | Caching, integrity verification |
| QR | Image | Visual | No | Scanner | Mobile scanning, physical media |
| NFC | Binary | No | No | Reader | Hardware tags |
| JSON-LD | Variable | Partial | No | Yes | Semantic web integration |
| Compact Binary | Short | No | No | Yes | Embedded systems |
| Phonetic | Variable | Voice | No | Yes | Radio, phone, screen readers |
| Emoji | Short | Visual | Partial | Yes | Social sharing, UI display |
| Mnemonic | Variable | Yes | No | Yes | Verbal reference |
| Obfuscated | Fixed | Yes | Yes | With key | Border crossings, privacy |

```python
class UVCFormat:
    """Registry of UVC encoding formats"""

    FORMATS = {
        'canonical': {
            'id': 'canonical',
            'description': 'Dot-separated lowercase token',
            'example': 'family.safe.guide',
            'use_case': 'Storage, comparison, hashing',
            'reversible': True,
        },
        'csm1': {
            'id': 'csm1',
            'description': 'Constitutional Safety Minicode',
            'example': 'N5+F:ELEM@1.2.0',
            'use_case': 'Wire protocols, headers',
            'reversible': True,  # Via lookup
        },
        'uri': {
            'id': 'uri',
            'description': 'Full URI with scheme',
            'example': 'creed://creed.space/family.safe.guide@1.2.0',
            'use_case': 'Addressing, links',
            'reversible': True,
        },
        'obfuscated': {
            'id': 'obfuscated',
            'description': 'Privacy-preserving format',
            'example': 'JADE-RIVER-SEVEN',
            'use_case': 'Border crossings, privacy',
            'reversible': True,  # With key
        },
        'phonetic': {
            'id': 'phonetic',
            'description': 'NATO phonetic alphabet',
            'example': 'NOVEMBER-FIVE-FOXTROT',
            'use_case': 'Voice communication, radio',
            'reversible': True,
        },
        'emoji': {
            'id': 'emoji',
            'description': 'Visual shorthand',
            'example': '\U0001f3e1\U0001f6e1\ufe0f\U0001f476',
            'use_case': 'Social sharing, UI',
            'reversible': True,  # Via codex
        },
        'hash': {
            'id': 'hash',
            'description': 'Content-addressed',
            'example': 'sha256:7f83b165...',
            'use_case': 'Caching, verification',
            'reversible': False,  # One-way
        },
        'qr': {
            'id': 'qr',
            'description': 'QR code encoding',
            'content': 'URI format as payload',
            'use_case': 'Mobile scanning, physical',
            'reversible': True,
        },
    }
```

### 2.2 Canonical Format

The canonical format is the primary representation. All other formats convert to and from canonical form.

#### 2.2.1 Grammar

```abnf
canonical-token = segment *("." segment) ["@" version]
segment         = 1*32(LALPHA / DIGIT / "-")
version         = semver / "latest" / "canary"
```

#### 2.2.2 Examples

```
family.safe.guide
family.safe.guide@1.2.0
company.acme.legal.compliance
user.alice.personal
```

#### 2.2.3 Canonicalization Algorithm

Implementations MUST apply the following canonicalization steps in order:

```python
def canonicalize(token: str) -> str:
    """Convert to canonical form"""
    # 1. Unicode NFKC normalization
    token = unicodedata.normalize('NFKC', token)
    # 2. Lowercase
    token = token.lower()
    # 3. Strip leading/trailing whitespace
    token = token.strip()
    # 4. Remove internal whitespace
    token = re.sub(r'\s+', '', token)
    # 5. Collapse consecutive dots
    token = re.sub(r'\.+', '.', token)
    # 6. Strip leading/trailing dots
    token = token.strip('.')
    # 7. Handle version part separately
    if '@' in token:
        base, version = token.rsplit('@', 1)
        version = _normalize_version(version)
        token = f"{base}@{version}"
    return token

def _normalize_version(version: str) -> str:
    """Normalize version string"""
    if version in ('latest', 'canary'):
        return version
    # Preserve compatibility prefix
    prefix = ''
    if version.startswith('^') or version.startswith('~'):
        prefix = version[0]
        version = version[1:]
    # Parse semver
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)(-.*)?$', version)
    if not match:
        return prefix + version
    major, minor, patch, prerelease = match.groups()
    # Strip leading zeros (except for '0')
    major = str(int(major))
    minor = str(int(minor))
    patch = str(int(patch))
    result = f"{major}.{minor}.{patch}"
    if prerelease:
        result += prerelease.lower()
    return prefix + result
```

Two tokens are equal if and only if their canonical forms are identical:

```python
def tokens_equal(token1: str, token2: str) -> bool:
    """Check if two UVC tokens are semantically equal"""
    return canonicalize(token1) == canonicalize(token2)
```

### 2.3 CSM1 Format

The Constitutional Safety Minicode (CSM1) format provides compact representation for wire protocols and HTTP headers.

#### 2.3.1 Grammar

```abnf
csm1-code = persona adherence [scopes] [":" namespace] ["@" version]
```

See the CSM1 Grammar Specification for full details.

#### 2.3.2 Mapping to Canonical

```python
CSM1_TO_UVC_MAPPING = {
    # Persona -> UVC prefix
    'N': 'family.safe',
    'Z': 'secure.privacy',
    'G': 'family.ethics',
    'A': 'work.professional',
    'M': 'creative.artistic',
    'R': 'reality.factual',
    'H': 'work.technical',
    'C': 'custom',  # Requires namespace
}

def csm1_to_canonical(csm1: str) -> str:
    """Convert CSM1 code to canonical UVC token"""
    parsed = parse_csm1(csm1)
    base = CSM1_TO_UVC_MAPPING[parsed.persona]

    if parsed.persona == 'C' and parsed.namespace:
        return f"custom.{parsed.namespace.lower()}"

    # Add scope modifiers
    if 'E' in parsed.scopes:
        base += '.education'
    elif 'W' in parsed.scopes:
        base += '.work'

    return base
```

### 2.4 URI Format

#### 2.4.1 Grammar

```abnf
vcp-uri = "creed://" issuer "/" path ["@" version]
issuer  = domain-name
path    = segment *("/" segment)
```

#### 2.4.2 Examples

```
creed://creed.space/family.safe.guide
creed://creed.space/family.safe.guide@1.2.0
creed://acme.com/company.acme.legal@latest
```

The paper specification also defines an alternative URI scheme:

```
vcp://core.ethics.consent
```

Implementations MUST accept the `creed://` scheme. Implementations SHOULD also accept the `vcp://` scheme as equivalent.

#### 2.4.3 Conversion Algorithms

```python
def canonical_to_uri(token: str, issuer: str = "creed.space") -> str:
    """Convert canonical token to URI"""
    if '@' in token:
        base, version = token.rsplit('@', 1)
        return f"creed://{issuer}/{base.replace('.', '/')}@{version}"
    return f"creed://{issuer}/{token.replace('.', '/')}"

def uri_to_canonical(uri: str) -> str:
    """Convert URI to canonical token"""
    if not uri.startswith('creed://'):
        raise ValueError("Not a VCP URI")
    rest = uri[8:]  # Remove scheme
    parts = rest.split('/')
    issuer = parts[0]
    path = '/'.join(parts[1:])
    # Handle version
    version = None
    if '@' in path:
        path, version = path.rsplit('@', 1)
    # Convert path to token
    token = path.replace('/', '.')
    if version:
        token += f"@{version}"
    return token
```

### 2.5 Hash Format

The hash format provides a content-addressed, one-way identifier for caching, integrity verification, and deduplication.

#### 2.5.1 Grammar

```abnf
hash-format = algorithm ":" hash-value
algorithm   = "sha256" / "sha384" / "sha512"
hash-value  = 64HEXDIG / 96HEXDIG / 128HEXDIG
```

Implementations MUST support SHA-256. Implementations SHOULD support SHA-384 and SHA-512.

#### 2.5.2 Example

```
vcp:sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069
```

#### 2.5.3 Generation

```python
def to_hash(token: str, algorithm: str = 'sha256') -> str:
    """Generate content hash of canonical token"""
    canonical = canonicalize(token)
    if algorithm == 'sha256':
        h = hashlib.sha256(canonical.encode()).hexdigest()
    elif algorithm == 'sha384':
        h = hashlib.sha384(canonical.encode()).hexdigest()
    elif algorithm == 'sha512':
        h = hashlib.sha512(canonical.encode()).hexdigest()
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")
    return f"{algorithm}:{h}"
```

### 2.6 QR Format

QR codes enable physical sharing of constitutions via printed media, mobile app scanning, and conference badges.

#### 2.6.1 Specification

QR codes MUST contain the URI format as their payload. Implementations MUST use error correction level M or higher.

```python
def to_qr(token: str, issuer: str = "creed.space") -> bytes:
    """Generate QR code image"""
    uri = canonical_to_uri(token, issuer)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()

def from_qr(image_data: bytes) -> str:
    """Parse QR code to canonical token"""
    from pyzbar.pyzbar import decode
    from PIL import Image
    img = Image.open(BytesIO(image_data))
    decoded = decode(img)
    if decoded:
        uri = decoded[0].data.decode()
        return uri_to_canonical(uri)
    return None
```

### 2.7 NFC Format

NFC tags MAY carry VCP/I tokens for hardware-based identity sharing. The NFC payload MUST contain the URI format.

### 2.8 JSON-LD Format

For semantic web integration, VCP/I tokens MAY be represented as JSON-LD:

```json
{"@id": "vcp:core.ethics.consent"}
```

### 2.9 Compact Binary Format

For embedded systems with constrained memory, a compact binary encoding MAY be used. The binary format is implementation-defined but MUST be deterministically convertible to and from canonical form.

### 2.10 Phonetic Format

Phonetic encoding enables voice communication of CSM1 codes via the NATO phonetic alphabet.

```python
NATO_PHONETIC = {
    'A': 'ALFA', 'B': 'BRAVO', 'C': 'CHARLIE', 'D': 'DELTA',
    'E': 'ECHO', 'F': 'FOXTROT', 'G': 'GOLF', 'H': 'HOTEL',
    'I': 'INDIA', 'J': 'JULIET', 'K': 'KILO', 'L': 'LIMA',
    'M': 'MIKE', 'N': 'NOVEMBER', 'O': 'OSCAR', 'P': 'PAPA',
    'Q': 'QUEBEC', 'R': 'ROMEO', 'S': 'SIERRA', 'T': 'TANGO',
    'U': 'UNIFORM', 'V': 'VICTOR', 'W': 'WHISKEY', 'X': 'XRAY',
    'Y': 'YANKEE', 'Z': 'ZULU',
    '0': 'ZERO', '1': 'ONE', '2': 'TWO', '3': 'THREE',
    '4': 'FOUR', '5': 'FIVE', '6': 'SIX', '7': 'SEVEN',
    '8': 'EIGHT', '9': 'NINE',
    '+': 'PLUS', ':': 'COLON', '@': 'AT',
}

def to_phonetic(csm1: str) -> str:
    """Convert CSM1 to phonetic"""
    parts = []
    for char in csm1.upper():
        if char in NATO_PHONETIC:
            parts.append(NATO_PHONETIC[char])
    return '-'.join(parts)

# N5+F -> "NOVEMBER-FIVE-PLUS-FOXTROT"
```

### 2.11 Emoji Format

Emoji encoding provides visual shorthand for social sharing and UI display.

#### 2.11.1 Emoji Codex

```python
EMOJI_CODEX = {
    # Domains
    'family': '\U0001f3e1',
    'work': '\U0001f4bc',
    'secure': '\U0001f512',
    'creative': '\U0001f3a8',
    'reality': '\U0001f4da',

    # Approaches
    'safe': '\U0001f6e1\ufe0f',
    'professional': '\U0001f454',
    'privacy': '\U0001f510',
    'artistic': '\u2728',
    'factual': '\U0001f4ca',

    # Roles
    'guide': '\U0001f9ed',
    'assistant': '\U0001f916',
    'guardian': '\u2694\ufe0f',
    'muse': '\U0001f4ab',
    'anchor': '\u2693',

    # Contexts
    'children': '\U0001f476',
    'elders': '\U0001f474',
    'medical': '\U0001f3e5',
    'education': '\U0001f4d6',
    'legal': '\u2696\ufe0f',
}

def to_emoji(token: str) -> str:
    """Convert canonical token to emoji"""
    segments = token.split('.')[:3]  # First 3 segments
    emojis = []
    for seg in segments:
        if seg in EMOJI_CODEX:
            emojis.append(EMOJI_CODEX[seg])
    return ''.join(emojis) if emojis else '\U0001f4dc'

# family.safe.guide -> (house)(shield)(compass)
```

#### 2.11.2 Reverse Mapping

```python
REVERSE_EMOJI = {v: k for k, v in EMOJI_CODEX.items()}

def from_emoji(emoji_str: str) -> str:
    """Convert emoji back to canonical (approximate)"""
    import regex
    emojis = regex.findall(r'\X', emoji_str)
    segments = []
    for e in emojis:
        if e in REVERSE_EMOJI:
            segments.append(REVERSE_EMOJI[e])
    return '.'.join(segments) if segments else None
```

Emoji decoding is approximate -- it MAY lose precision for tokens with segments not in the codex.

### 2.12 Mnemonic (Human Verbal) Format

For verbal reference, the mnemonic format uses space-separated segments:

```
"core ethics consent"
```

Implementations SHOULD accept mnemonic input by replacing spaces with dots and applying canonicalization.

### 2.13 Obfuscated Format

The obfuscated format provides privacy-preserving representation suitable for border crossings, keyword-filtered communications, and low-profile contexts.

#### 2.13.1 Grammar

```abnf
obfuscated = color "-" nature "-" number
color      = "JADE" / "CORAL" / "AMBER" / "SILVER" / "GOLD" / ...
nature     = "RIVER" / "MOUNTAIN" / "STAR" / "MOON" / "FOREST" / ...
number     = "ONE" / "TWO" / "THREE" / ... / "NINE"
```

#### 2.13.2 Algorithm

Obfuscation MUST be deterministic: the same token with the same secret MUST produce the same obfuscated form. Different secrets MUST produce different obfuscated forms.

```python
class UVCObfuscator:
    """Generate privacy-preserving obfuscated tokens"""

    COLORS = [
        "JADE", "CORAL", "AMBER", "SILVER", "GOLD",
        "CRIMSON", "AZURE", "VIOLET", "SAGE", "PEARL",
        "BRONZE", "IVORY", "ONYX", "RUBY", "EMERALD",
        "INDIGO"
    ]

    NATURE = [
        "RIVER", "MOUNTAIN", "STAR", "MOON", "FOREST",
        "OCEAN", "DESERT", "MEADOW", "GLACIER", "CANYON",
        "VALLEY", "SUMMIT", "HARBOR", "PRAIRIE", "OASIS",
        "TUNDRA"
    ]

    NUMBERS = [
        "ONE", "TWO", "THREE", "FOUR", "FIVE",
        "SIX", "SEVEN", "EIGHT", "NINE"
    ]

    def obfuscate(self, token: str, secret: bytes) -> str:
        """
        Generate deterministic obfuscated form.

        Same token + same secret = same obfuscated form.
        Different secret = different obfuscated form.
        """
        canonical = canonicalize(token)
        digest = hmac.new(secret, canonical.encode(), 'sha256').digest()

        color_idx = digest[0] % len(self.COLORS)
        nature_idx = digest[1] % len(self.NATURE)
        number_idx = digest[2] % len(self.NUMBERS)

        return f"{self.COLORS[color_idx]}-{self.NATURE[nature_idx]}-{self.NUMBERS[number_idx]}"

    def deobfuscate(
        self,
        obfuscated: str,
        secret: bytes,
        token_list: List[str]
    ) -> Optional[str]:
        """
        Reverse lookup (requires enumeration).

        MUST provide list of possible tokens to match against.
        """
        for token in token_list:
            if self.obfuscate(token, secret) == obfuscated:
                return token
        return None
```

### 2.14 Conversion Matrix

All formats convert to and from canonical form (except hash which is one-way):

```
           -> canonical  csm1  uri  obfuscated  phonetic  emoji  hash
canonical        Y       Y     Y       Y          Y        Y     Y
csm1            Y       Y     Y       Y          Y        Y     Y
uri             Y       Y     Y       Y          Y        Y     Y
obfuscated      Y*      Y*    Y*      Y          Y*       Y*    Y
phonetic        Y       Y     Y       Y          Y        Y     Y
emoji           Y~      Y~    Y~      Y~         Y~       Y     Y
hash            N       N     N       N          N        N     Y

Y  = direct conversion
Y* = requires secret key
Y~ = approximate (may lose precision)
N  = not possible (one-way)
```

### 2.15 Format Detection

Implementations SHOULD support automatic format detection:

```python
def detect_format(encoded: str) -> str:
    """Auto-detect encoding format"""

    # URI format
    if encoded.startswith('creed://'):
        return 'uri'

    # Hash format
    if encoded.startswith(('sha256:', 'sha384:', 'sha512:')):
        return 'hash'

    # Obfuscated format (COLOR-NATURE-NUMBER)
    if re.match(r'^[A-Z]+-[A-Z]+-[A-Z]+$', encoded):
        obfuscator = UVCObfuscator()
        parts = encoded.split('-')
        if (parts[0] in obfuscator.COLORS and
            parts[1] in obfuscator.NATURE and
            parts[2] in obfuscator.NUMBERS):
            return 'obfuscated'

    # CSM1 format
    if re.match(r'^[NZGAMDC][0-5]', encoded):
        return 'csm1'

    # Phonetic format
    if encoded.count('-') >= 2 and all(
        p in NATO_PHONETIC.values() for p in encoded.split('-')[:3]
    ):
        return 'phonetic'

    # Emoji format (contains emoji characters)
    if any(ord(c) > 127 for c in encoded):
        return 'emoji'

    # Default: canonical
    return 'canonical'
```

---

## 3. Naming Conventions

### 3.1 Token Structure

#### 3.1.1 Simple Token (Core Namespace)

```
domain.approach.role

Examples:
  family.safe.guide
  work.professional.assistant
  secure.privacy.guardian
```

| Component | Description | Constraints |
|-----------|-------------|-------------|
| `domain` | Value domain (family, work, secure) | 1-32 lowercase alpha |
| `approach` | Approach within domain | 1-32 lowercase alpha |
| `role` | Specific role/function | 1-32 lowercase alpha |

#### 3.1.2 Hierarchical Token (Non-Core Namespaces)

```
namespace.segment.segment...

Examples:
  company.acme.legal.compliance
  religion.buddhist.meditation
  culture.japanese.formal
  user.alice.personal
```

| Component | Description | Constraints |
|-----------|-------------|-------------|
| `namespace` | Governance tier (company, religion, user) | See Section 3.2 |
| `segment` | Path within namespace | 1-32 lowercase alphanumeric + hyphen |

Semantic interpretation for variable-depth tokens (backward compatible):

- First segment = domain
- Second-to-last segment = approach
- Last segment = role
- Middle segments = path (organizational hierarchy)

Examples:

- 3 segments: `family.safe.guide` (domain=family, approach=safe, role=guide)
- 4 segments: `company.acme.legal.compliance` (domain=company, path=[acme], approach=legal, role=compliance)
- 5 segments: `org.example.dept.team.policy` (domain=org, path=[example,dept], approach=team, role=policy)

### 3.2 Namespace Prefixes

| Prefix | Governance | Examples |
|--------|------------|----------|
| `family` | Creed Space core | `family.safe.guide` |
| `work` | Creed Space core | `work.professional.assistant` |
| `secure` | Creed Space core | `secure.privacy.guardian` |
| `creative` | Creed Space core | `creative.artistic.muse` |
| `reality` | Creed Space core | `reality.factual.anchor` |
| `company.<org>` | Organizational | `company.acme.legal` |
| `school.<org>` | Educational | `school.mit.research` |
| `ngo.<org>` | Non-profit | `ngo.redcross.humanitarian` |
| `religion.<tradition>` | Religious | `religion.buddhist.mindfulness` |
| `culture.<region>` | Cultural | `culture.japanese.formal` |
| `community.<name>` | Community | `community.gaming.esports` |
| `user.<username>` | Personal | `user.alice.private` |

### 3.3 Versioned Tokens

```
token@version

Examples:
  family.safe.guide@1.2.0
  work.professional.assistant@latest
  company.acme.legal@2.0.0-beta
```

| Version Format | Description |
|----------------|-------------|
| `X.Y.Z` | Semantic version (exact) |
| `^X.Y.Z` | Compatible with X.Y.Z |
| `~X.Y.Z` | Approximately X.Y.Z |
| `latest` | Most recent stable |
| `canary` | Most recent (including pre-release) |

Version semantics follow Semantic Versioning 2.0.0:

| Change Type | Version Increment | Compatibility |
|-------------|------------------|---------------|
| Breaking changes to syntax | MAJOR | Incompatible |
| New fields/layers | MINOR | Backward compatible |
| Clarifications, bug fixes | PATCH | Fully compatible |

### 3.4 Formal Grammar (ABNF, RFC 5234)

```abnf
; UVC Token Grammar (Variable-depth support)

uvc-token         = token-path ["@" version] [":" namespace-suffix]

; Token path: minimum 3 segments, maximum 10 segments
token-path        = segment 2*9("." segment)

; Each segment: lowercase letters, digits, hyphens
segment           = LALPHA *31(LALPHA / DIGIT / "-")

; Namespace suffix (optional, uppercase)
namespace-suffix  = UALPHA *31(UALPHA / DIGIT)

; Namespace governance (determined by first segment):
;   Core: family, work, secure, creative, reality, education, health, finance, legal
;   Organizational: company.*, school.*, ngo.*
;   Community: religion.*, culture.*, community.*
;   Personal: user.*

; Version constraints
version           = exact-version / compat-version / approx-version / alias-version
exact-version     = semver
compat-version    = "^" semver
approx-version    = "~" semver
alias-version     = "latest" / "canary"

semver            = major "." minor "." patch ["-" prerelease]
major             = 1*5DIGIT
minor             = 1*5DIGIT
patch             = 1*5DIGIT
prerelease        = 1*(ALPHA / DIGIT / "." / "-")

; Core rules
LALPHA            = %x61-7A                    ; lowercase a-z
UALPHA            = %x41-5A                    ; uppercase A-Z
DIGIT             = %x30-39                    ; 0-9
ALPHA             = %x41-5A / %x61-7A          ; A-Z / a-z
```

### 3.5 Formal Grammar (EBNF)

For cross-reference with the academic paper specification:

```ebnf
(* VCP/I Identity Token Grammar *)

identity_token = tier , "." , domain , "." , category , { "." , segment } ;

tier = "core" | "org" | "community" | "personal" ;

domain = segment ;
category = segment ;

segment = lowercase , { alphanumeric | "-" } ;

lowercase = "a" | "b" | ... | "z" ;
alphanumeric = lowercase | digit ;
digit = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;

(* Constraints:
   - Minimum 3 segments (tier.domain.category)
   - Maximum 10 segments
   - Each segment starts with lowercase letter
   - Hyphens allowed, not at start/end of segment
*)

(* Examples:
core.ethics.consent
org.acme.safety.medical.pediatric
community.open-source.safety-standards
personal.user-12345.custom-rules
*)
```

### 3.6 Validation Regex

```python
UVC_TOKEN_PATTERN = r"""
    ^
    (?:
        # Core namespace (simple token)
        (?:family|work|secure|creative|reality)
        \.
        [a-z]{1,32}
        \.
        [a-z]{1,32}
    |
        # Organizational namespace
        (?:company|school|ngo)
        \.
        [a-z0-9-]{1,32}
        (?:\.[a-z0-9-]{1,32})+
    |
        # Community namespace
        (?:religion|culture|community)
        \.
        [a-z0-9-]{1,32}
        (?:\.[a-z0-9-]{1,32})+
    |
        # Personal namespace
        user
        \.
        [a-z0-9_-]{1,32}
        (?:\.[a-z0-9-]{1,32})*
    )
    # Optional version
    (?:
        @
        (?:
            [\^~]?
            [0-9]{1,5}
            \.
            [0-9]{1,5}
            \.
            [0-9]{1,5}
            (?:-[a-zA-Z0-9.-]+)?
        |
            latest
        |
            canary
        )
    )?
    $
"""
```

### 3.7 Validation Rules

#### 3.7.1 Structural Constraints

```python
class UVCValidationRules:
    """Validation rules for UVC tokens"""

    RULES = {
        # Length constraints
        'max_total_length': 128,       # Maximum total token length
        'max_segments': 8,              # Maximum hierarchy depth
        'max_segment_length': 32,       # Maximum single segment length

        # Character constraints
        'allowed_segment_chars': r'^[a-z0-9-]+$',
        'segment_start_char': r'^[a-z]',    # MUST start with letter
        'segment_end_char': r'[a-z0-9]$',   # MUST end with letter or digit

        # Structural constraints
        'no_consecutive_dots': True,
        'no_leading_dot': True,
        'no_trailing_dot': True,
        'no_consecutive_hyphens': True,
        'no_leading_hyphen': True,
        'no_trailing_hyphen': True,

        # Reserved words (MUST NOT be used as segments)
        'reserved_words': [
            'system', 'admin', 'root', 'null', 'undefined',
            'true', 'false', 'none', 'void', 'default',
            'api', 'internal', 'private', 'public', 'test',
            'debug', 'staging', 'production',
            'vcp', 'uvc', 'csm', 'bundle', 'manifest', 'creed',
            'official', 'verified', 'authentic', 'real',
        ],
    }
```

#### 3.7.2 Validation Algorithm

```python
class ValidationError(Enum):
    NONE = 0
    TOO_LONG = 1
    TOO_MANY_SEGMENTS = 2
    SEGMENT_TOO_LONG = 3
    INVALID_CHARACTERS = 4
    INVALID_START_CHAR = 5
    INVALID_END_CHAR = 6
    CONSECUTIVE_DOTS = 7
    CONSECUTIVE_HYPHENS = 8
    RESERVED_WORD = 9
    INVALID_NAMESPACE = 10
    INVALID_VERSION = 11
    EMPTY_SEGMENT = 12

@dataclass
class ValidationResult:
    valid: bool
    error: ValidationError
    message: str
    position: int = -1

class UVCTokenValidator:
    """Validate UVC tokens against specification"""

    CORE_NAMESPACES = {'family', 'work', 'secure', 'creative', 'reality'}
    ORG_PREFIXES = {'company', 'school', 'ngo'}
    COMMUNITY_PREFIXES = {'religion', 'culture', 'community'}
    PERSONAL_PREFIX = 'user'

    RESERVED_WORDS = {
        'system', 'admin', 'root', 'null', 'undefined',
        'true', 'false', 'none', 'void', 'default',
        'api', 'internal', 'private', 'public', 'test',
        'debug', 'staging', 'production',
        'vcp', 'uvc', 'csm', 'bundle', 'manifest', 'creed',
        'official', 'verified', 'authentic', 'real',
    }

    def validate(self, token: str) -> ValidationResult:
        """Validate a UVC token"""

        # Handle versioned tokens
        base_token = token
        version = None
        if '@' in token:
            parts = token.split('@', 1)
            base_token = parts[0]
            version = parts[1]

        # Basic length check
        if len(token) > 128:
            return ValidationResult(False, ValidationError.TOO_LONG,
                f"Token exceeds maximum length (128): {len(token)}")

        # Split into segments
        segments = base_token.split('.')

        if len(segments) > 8:
            return ValidationResult(False, ValidationError.TOO_MANY_SEGMENTS,
                f"Too many segments (max 8): {len(segments)}")

        # Check for empty segments (consecutive dots)
        for i, seg in enumerate(segments):
            if not seg:
                return ValidationResult(False, ValidationError.EMPTY_SEGMENT,
                    f"Empty segment at position {i}", i)

        # Validate each segment
        for i, segment in enumerate(segments):
            result = self._validate_segment(segment, i)
            if not result.valid:
                return result

        # Validate namespace structure
        result = self._validate_namespace(segments)
        if not result.valid:
            return result

        # Validate version if present
        if version:
            result = self._validate_version(version)
            if not result.valid:
                return result

        return ValidationResult(True, ValidationError.NONE, "Valid")

    def _validate_segment(self, segment: str, position: int) -> ValidationResult:
        """Validate a single segment"""

        if len(segment) > 32:
            return ValidationResult(False, ValidationError.SEGMENT_TOO_LONG,
                f"Segment '{segment}' exceeds maximum length (32)", position)

        if not re.match(r'^[a-z0-9-]+$', segment):
            return ValidationResult(False, ValidationError.INVALID_CHARACTERS,
                f"Segment '{segment}' contains invalid characters", position)

        if not segment[0].isalpha():
            return ValidationResult(False, ValidationError.INVALID_START_CHAR,
                f"Segment '{segment}' must start with letter", position)

        if segment[-1] == '-':
            return ValidationResult(False, ValidationError.INVALID_END_CHAR,
                f"Segment '{segment}' cannot end with hyphen", position)

        if '--' in segment:
            return ValidationResult(False, ValidationError.CONSECUTIVE_HYPHENS,
                f"Segment '{segment}' has consecutive hyphens", position)

        if segment in self.RESERVED_WORDS:
            return ValidationResult(False, ValidationError.RESERVED_WORD,
                f"Segment '{segment}' is a reserved word", position)

        return ValidationResult(True, ValidationError.NONE, "Valid")

    def _validate_namespace(self, segments: list) -> ValidationResult:
        """Validate namespace structure"""

        first = segments[0]

        # Core namespace: exactly 3 segments
        if first in self.CORE_NAMESPACES:
            if len(segments) != 3:
                return ValidationResult(False, ValidationError.INVALID_NAMESPACE,
                    f"Core namespace '{first}' requires exactly 3 segments")
            return ValidationResult(True, ValidationError.NONE, "Valid")

        # Organizational namespace: at least 3 segments
        if first in self.ORG_PREFIXES:
            if len(segments) < 3:
                return ValidationResult(False, ValidationError.INVALID_NAMESPACE,
                    f"Organizational namespace '{first}' requires at least 3 segments")
            return ValidationResult(True, ValidationError.NONE, "Valid")

        # Community namespace: at least 3 segments
        if first in self.COMMUNITY_PREFIXES:
            if len(segments) < 3:
                return ValidationResult(False, ValidationError.INVALID_NAMESPACE,
                    f"Community namespace '{first}' requires at least 3 segments")
            return ValidationResult(True, ValidationError.NONE, "Valid")

        # Personal namespace: at least 2 segments
        if first == self.PERSONAL_PREFIX:
            if len(segments) < 2:
                return ValidationResult(False, ValidationError.INVALID_NAMESPACE,
                    "Personal namespace 'user' requires at least 2 segments")
            return ValidationResult(True, ValidationError.NONE, "Valid")

        return ValidationResult(False, ValidationError.INVALID_NAMESPACE,
            f"Unknown namespace prefix: '{first}'")

    def _validate_version(self, version: str) -> ValidationResult:
        """Validate version string"""

        # Alias versions
        if version in ('latest', 'canary'):
            return ValidationResult(True, ValidationError.NONE, "Valid")

        # Strip compatibility prefixes
        clean_version = version.lstrip('^~')

        # Semver pattern
        semver_pattern = r'^[0-9]{1,5}\.[0-9]{1,5}\.[0-9]{1,5}(-[a-zA-Z0-9.-]+)?$'
        if not re.match(semver_pattern, clean_version):
            return ValidationResult(False, ValidationError.INVALID_VERSION,
                f"Invalid version format: '{version}'")

        return ValidationResult(True, ValidationError.NONE, "Valid")
```

### 3.8 Canonicalization Examples

```python
# Whitespace normalization
"  family.safe.guide  "           -> "family.safe.guide"

# Case normalization
"Family.Safe.Guide"               -> "family.safe.guide"

# Dot normalization
"family..safe.guide"              -> "family.safe.guide"

# Version normalization
"family.safe.guide@01.02.03"      -> "family.safe.guide@1.2.3"
"family.safe.guide@1.2.3-BETA"    -> "family.safe.guide@1.2.3-beta"
```

### 3.9 Token Examples

#### 3.9.1 Valid Tokens

```python
# Core namespace (simple)
"family.safe.guide"           # Valid
"work.professional.assistant" # Valid
"secure.privacy.guardian"     # Valid
"creative.artistic.muse"     # Valid
"reality.factual.anchor"     # Valid

# Organizational namespace
"company.acme.legal.compliance"        # Valid
"company.acme-corp.hr.policies"        # Valid
"school.mit.research.ethics"           # Valid
"ngo.red-cross.humanitarian.disaster"  # Valid

# Community namespace
"religion.buddhist.meditation.mindfulness"  # Valid
"culture.japanese.business.formal"          # Valid
"community.gaming.esports.fair-play"        # Valid

# Personal namespace
"user.alice.personal"          # Valid
"user.bob-123.work.assistant"  # Valid

# Versioned tokens
"family.safe.guide@1.2.0"      # Valid (exact)
"family.safe.guide@^1.2.0"     # Valid (compatible)
"family.safe.guide@~1.2.0"     # Valid (approximate)
"family.safe.guide@latest"     # Valid (alias)
"family.safe.guide@2.0.0-beta" # Valid (prerelease)
```

#### 3.9.2 Invalid Tokens

```python
# Too few segments for core namespace
"family.safe"                  # Invalid (needs 3 segments)

# Invalid characters
"family.Safe.guide"            # Invalid (uppercase)
"family.safe_guide"            # Invalid (underscore in core)
"family.safe guide"            # Invalid (space)

# Structural errors
"..family.safe.guide"          # Invalid (leading dots)
"family.safe.guide.."          # Invalid (trailing dots)
"family..safe.guide"           # Invalid (consecutive dots)

# Reserved words
"family.system.guide"          # Invalid (reserved word)
"company.acme.admin.policies"  # Invalid (reserved word)

# Too long
"family.this-is-a-very-long-segment-that-exceeds-limit.guide"  # Invalid

# Invalid version
"family.safe.guide@abc"        # Invalid (not semver)
"family.safe.guide@1.2"        # Invalid (incomplete semver)
```

### 3.10 Content-Addressed Hashing

For content addressing and caching:

```python
def hash_uvc_token(token: str) -> str:
    """
    Compute content hash of UVC token.

    Uses SHA-256 of canonical form. Implementations MUST
    hash the canonical form, not the raw input.
    """
    canonical = canonicalize(token)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()
```

---

## 4. Namespace Governance

### 4.1 Governance Principles

1. **Minimal Centralization**: Core namespaces only; everything else is delegated
2. **Proof-Based**: Registration requires verifiable proof
3. **Dispute Process**: Clear resolution path for conflicts
4. **Expiration**: Namespaces require renewal to prevent squatting

### 4.2 Namespace Tiers

| Tier | Prefixes | Governance | Registration | Decision Process | Timeline |
|------|----------|------------|--------------|------------------|----------|
| **Core** | `family`, `work`, `secure`, `creative`, `reality` | Creed Space stewardship | Reserved | Consortium vote (2/3 supermajority) | 90-day proposal period |
| **Organizational** | `company`, `school`, `ngo` | Delegated to org | Verified ownership | Organization internal | Immediate |
| **Community** | `religion`, `culture`, `community` | Community consensus | Multi-stakeholder | Community consensus | 30-day comment period |
| **Personal** | `user` | Individual control | Self-service | Self-service | Immediate |

#### 4.2.1 Core Tier

**Governance**: Creed Space maintains exclusive stewardship.

Characteristics:

- Reserved namespaces, not available for registration
- Universal semantics (same meaning everywhere)
- Backward compatibility guaranteed
- Governed by Creed Space advisory board
- Changes require 2/3 consortium supermajority with a 90-day proposal period

Reserved prefixes:

```python
CORE_NAMESPACES = {
    'family',    # Family/child-safe contexts
    'work',      # Professional/workplace contexts
    'secure',    # Security/privacy contexts
    'creative',  # Artistic/creative contexts
    'reality',   # Factual/grounded contexts
}
```

#### 4.2.2 Organizational Tier

**Governance**: Delegated to verified organizations.

Registration requirements:

1. Domain ownership verification (DNS TXT or HTTPS)
2. Contact email at verified domain
3. Acceptance of terms of service
4. Annual renewal

Sub-prefixes:

| Prefix | Entity Type | Proof Type |
|--------|-------------|------------|
| `company` | For-profit business | Domain ownership |
| `school` | Educational institution | .edu domain or accreditation |
| `ngo` | Non-profit organization | 501(c)(3) or equivalent |

#### 4.2.3 Community Tier

**Governance**: Multi-stakeholder community consensus.

Registration requirements:

1. Three or more stewards (multi-sig)
2. Community charter defining governance
3. Public deliberation process
4. Annual steward rotation option

Sub-prefixes:

| Prefix | Scope | Governance |
|--------|-------|------------|
| `religion` | Religious traditions | Recognized religious bodies |
| `culture` | Cultural/regional | Cultural organizations |
| `community` | Interest groups | Community-defined |

#### 4.2.4 Personal Tier

**Governance**: Individual control.

Registration requirements:

1. Email verification
2. Username uniqueness check
3. Terms acceptance
4. No special characters (except `-`, `_`)

### 4.3 Namespace Expiry Policy

| Tier | Initial Term | Renewal | Grace Period |
|------|--------------|---------|--------------|
| Core | Permanent | N/A | N/A |
| Organizational | 1 year | Annual | 90 days |
| Community | 1 year | Annual | 90 days |
| Personal | Permanent | N/A | Deletion after 2 years inactivity |

### 4.4 Registration Protocol

#### 4.4.1 Registration Flow

```
+------------------------------------------------------------------+
|                     REGISTRATION FLOW                             |
|                                                                   |
|  REQUESTOR        1. Submit registration request                  |
|      |                                                            |
|      v                                                            |
|  REGISTRY         2. Validate namespace format                    |
|                   3. Check availability                           |
|                   4. Verify proof of ownership                    |
|      |                                                            |
|      v                                                            |
|  VERIFICATION     5. DNS/email/multi-sig verification             |
|      |                                                            |
|      v                                                            |
|  ISSUANCE         6. Generate namespace key                       |
|                   7. Record in registry                           |
|                   8. Return credentials                           |
+------------------------------------------------------------------+
```

#### 4.4.2 Registration Request

```python
@dataclass
class NamespaceRegistrationRequest:
    """Request to register a namespace"""

    # Required
    namespace: str              # e.g., "company.acme"
    requestor_id: str           # Identity of requestor
    contact_email: str          # Contact email
    proof_type: str             # "dns", "https", "multisig", "email"
    proof_data: str             # Proof-specific data

    # Optional
    delegation_policy: str = "closed"  # "open", "verified", "closed"
    charter_url: Optional[str] = None  # For community namespaces
    stewards: list = None              # For multi-sig namespaces


@dataclass
class NamespaceRegistrationResponse:
    """Response to registration request"""

    status: str                 # "approved", "pending", "rejected"
    namespace: str
    namespace_key: Optional[str]  # Signing key for namespace
    expiry: Optional[datetime]    # Registration expiry
    renewal_url: str
    reason: Optional[str]       # If rejected
```

#### 4.4.3 Registration API

```yaml
paths:
  /v1/namespaces/register:
    post:
      summary: Register a namespace
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required:
                - namespace
                - contact_email
                - proof_type
                - proof_data
              properties:
                namespace:
                  type: string
                  example: "company.acme"
                contact_email:
                  type: string
                  format: email
                proof_type:
                  type: string
                  enum: ["dns", "https", "multisig", "email"]
                proof_data:
                  type: string
                delegation_policy:
                  type: string
                  enum: ["open", "verified", "closed", "consensus"]
                  default: "closed"
      responses:
        201:
          description: Registration approved
        202:
          description: Pending verification
        400:
          description: Invalid request
        409:
          description: Namespace already claimed
```

### 4.5 Proof of Ownership

#### 4.5.1 DNS Verification

**For**: Organizational namespaces (`company.*`, `school.*`, `ngo.*`)

Process:

1. Requestor claims `company.acme`
2. Registry provides verification token: `vcp-verify=abc123xyz`
3. Requestor adds DNS TXT record: `_vcp.acme.com TXT "vcp-verify=abc123xyz"`
4. Registry verifies DNS record
5. Namespace approved

```python
class DNSVerifier:
    """Verify domain ownership via DNS TXT record"""

    def verify(self, domain: str, expected_token: str) -> bool:
        """
        Check for VCP verification TXT record.

        Looks for: _vcp.{domain} TXT "vcp-verify={token}"
        """
        try:
            answers = dns.resolver.resolve(f'_vcp.{domain}', 'TXT')
            for rdata in answers:
                txt = str(rdata).strip('"')
                if txt == f"vcp-verify={expected_token}":
                    return True
        except dns.resolver.NXDOMAIN:
            pass
        except dns.resolver.NoAnswer:
            pass
        return False
```

#### 4.5.2 HTTPS Verification

**For**: Organizational namespaces (alternative to DNS)

Process:

1. Requestor claims `company.acme`
2. Registry provides verification file content
3. Requestor hosts file at: `https://acme.com/.well-known/vcp-verify.txt`
4. Registry fetches and verifies

```python
class HTTPSVerifier:
    """Verify domain ownership via HTTPS file"""

    async def verify(self, domain: str, expected_token: str) -> bool:
        """
        Check for VCP verification file.

        Expects: https://{domain}/.well-known/vcp-verify.txt
        Content: vcp-verify={token}
        """
        url = f"https://{domain}/.well-known/vcp-verify.txt"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                if response.status_code == 200:
                    content = response.text.strip()
                    return content == f"vcp-verify={expected_token}"
        except Exception:
            pass
        return False
```

#### 4.5.3 Multi-Signature Verification

**For**: Community namespaces

Process:

1. Define steward list (minimum 3)
2. Each steward signs registration request
3. Threshold signatures verified (e.g., 3-of-5)
4. Namespace approved

```python
@dataclass
class MultiSigProof:
    """Multi-signature proof of community ownership"""

    stewards: List[str]         # Public keys of stewards
    threshold: int              # Required signatures
    signatures: List[str]       # Collected signatures
    message: str                # What was signed

    def is_valid(self) -> bool:
        """Check if threshold is met with valid signatures"""
        valid_count = 0
        for i, sig in enumerate(self.signatures):
            if sig and verify_signature(self.stewards[i], self.message, sig):
                valid_count += 1
        return valid_count >= self.threshold
```

#### 4.5.4 Email Verification

**For**: Personal namespaces

Process:

1. User requests `user.alice`
2. Confirmation email sent to provided address
3. User clicks verification link
4. Namespace approved

### 4.6 Delegation Rules

#### 4.6.1 Delegation Policies

| Policy | Description | Example |
|--------|-------------|---------|
| **open** | Anyone can create sub-namespaces | `community.gaming.*` |
| **verified** | Sub-namespace requires verification | `company.acme.*` |
| **closed** | Only owner can create | `user.alice.*` |
| **consensus** | Community vote required | `religion.buddhist.*` |

#### 4.6.2 Delegation Grant

```python
@dataclass
class DelegationGrant:
    """Grant to create sub-namespaces"""

    parent_namespace: str       # e.g., "company.acme"
    child_segment: str          # e.g., "legal" (for company.acme.legal)
    grantee: str                # Who receives delegation
    policy: str                 # Delegation policy for child
    expiry: datetime
    signed_by: str              # Parent namespace key

    def full_namespace(self) -> str:
        return f"{self.parent_namespace}.{self.child_segment}"
```

#### 4.6.3 Delegation API

```yaml
paths:
  /v1/namespaces/{namespace}/delegate:
    post:
      summary: Delegate sub-namespace
      security:
        - namespaceKey: []
      parameters:
        - name: namespace
          in: path
          required: true
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required:
                - child_segment
                - grantee
              properties:
                child_segment:
                  type: string
                  example: "legal"
                grantee:
                  type: string
                  description: Grantee public key or email
                policy:
                  type: string
                  enum: ["open", "verified", "closed"]
                  default: "closed"
                expiry_days:
                  type: integer
                  default: 365
```

### 4.7 Dispute Resolution

#### 4.7.1 Dispute Types

| Type | Description | Resolution |
|------|-------------|------------|
| **Squatting** | Namespace claimed by non-owner | Proof of legitimate claim |
| **Trademark** | Namespace infringes trademark | Legal documentation |
| **Abandonment** | Namespace unused, blocking others | Grace period, then release |
| **Impersonation** | Misleading namespace | Review and possible revocation |

#### 4.7.2 Dispute Process

```
1. FILING
   - Complainant submits dispute form
   - Provides evidence of claim
   - Pays dispute filing fee (refundable if valid)

2. REVIEW
   - Registry reviews within 14 days
   - Current holder notified
   - Response period: 14 days

3. INVESTIGATION
   - Evidence from both parties reviewed
   - Third-party mediator if needed
   - Decision within 30 days

4. RESOLUTION
   - Namespace transferred, or
   - Dispute rejected, or
   - Compromise reached
```

#### 4.7.3 Dispute Data Model

```python
@dataclass
class DisputeRequest:
    """Request to dispute a namespace"""

    namespace: str              # Disputed namespace
    complainant: str            # Who is filing
    dispute_type: str           # squatting, trademark, etc.
    evidence: List[str]         # URLs to evidence
    claim_statement: str        # Why complainant has right
    requested_outcome: str      # What complainant wants


@dataclass
class DisputeStatus:
    """Status of a dispute"""

    dispute_id: str
    namespace: str
    status: str                 # filed, under_review, decided
    filed_date: datetime
    decision: Optional[str]
    decision_date: Optional[datetime]
```

---

## 5. Registry Protocol

### 5.1 Design Goals

1. **Decentralized**: No single point of failure
2. **Fast**: Sub-100ms resolution for cached entries
3. **Secure**: Authenticated registration, verified resolution
4. **Extensible**: Support for federated and distributed registries
5. **Offline-Capable**: Local cache for disconnected operation

### 5.2 Resolution Order

Implementations MUST attempt resolution in this order:

```
1. Local cache (instant)
2. Well-known URI on issuer domain
3. Primary registry API
4. Federated peers (if configured)
5. DHT/IPFS lookup (future)
```

### 5.3 Resolution Flow

```
+------------------------------------------------------------------+
|                      RESOLUTION FLOW                              |
|                                                                   |
|  CLIENT -----> CACHE -----> WELL-KNOWN -----> REGISTRY API        |
|                  |              |                  |               |
|             hit? |         found?|             found?|             |
|                  v              v                  v              |
|               RETURN         RETURN             RETURN            |
|                                                                   |
|  RESOLUTION RESULT:                                               |
|   - bundle_uri: https://cdn.creed.space/bundles/...               |
|   - content_hash: sha256:7f83b165...                              |
|   - issuer: creed.space                                           |
|   - version: 1.2.0                                                |
|   - csm1: N5+F:ELEM                                              |
|   - ttl: 3600                                                     |
+------------------------------------------------------------------+
```

### 5.4 Resolution Result

```python
@dataclass
class ResolutionResult:
    """Result of UVC token resolution"""

    # Identity
    token: str                      # Original UVC token
    canonical: str                  # Canonical form

    # Location
    bundle_uri: str                 # Where to fetch bundle
    content_hash: str               # Expected hash (sha256:...)

    # Metadata
    issuer: str                     # Bundle issuer
    version: str                    # Resolved version
    csm1: str                       # CSM1 code

    # Cache control
    ttl: int                        # Seconds until stale
    resolved_via: str               # cache, well-known, registry, dht
    resolved_at: str                # ISO8601 timestamp

    # Optional metadata
    metadata: Dict[str, Any] = None  # Additional metadata
    signature: Optional[str] = None  # Resolution signature
```

### 5.5 Privacy-Preserving Queries

Registries MUST support wildcard queries without exposing the full namespace:

```
SEARCH("org.*.safety.medical") -> [org.acme.safety.medical, ...]
SEARCH("core.ethics.consent.*") -> [core.ethics.consent.medical, ...]
```

### 5.6 Registry API

#### 5.6.1 RESOLVE Operation

```yaml
/resolve/{token}:
  get:
    summary: Resolve UVC token to bundle location
    operationId: resolveToken
    parameters:
      - name: token
        in: path
        required: true
        description: UVC token to resolve
        schema:
          type: string
          example: family.safe.guide
      - name: version
        in: query
        description: Version constraint
        schema:
          type: string
          default: latest
          example: "1.2.0"
      - name: include_metadata
        in: query
        description: Include full metadata
        schema:
          type: boolean
          default: false
    responses:
      '200':
        description: Resolution successful
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ResolutionResult'
      '404':
        description: Token not found
      '400':
        description: Invalid token format
```

#### 5.6.2 SEARCH Operation

```yaml
/search:
  get:
    summary: Search for constitutions
    operationId: searchConstitutions
    parameters:
      - name: q
        in: query
        description: Text search query
        schema:
          type: string
      - name: tags
        in: query
        description: Filter by tags
        schema:
          type: array
          items:
            type: string
        style: form
        explode: true
      - name: persona
        in: query
        description: Filter by persona
        schema:
          type: string
          enum: [N, Z, G, A, M, R, H, C]
      - name: namespace
        in: query
        description: Filter by namespace prefix
        schema:
          type: string
      - name: limit
        in: query
        description: Maximum results
        schema:
          type: integer
          default: 20
          maximum: 100
      - name: offset
        in: query
        description: Pagination offset
        schema:
          type: integer
          default: 0
    responses:
      '200':
        description: Search results
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SearchResults'
```

#### 5.6.3 REGISTER Operation

```yaml
/register:
  post:
    summary: Register new constitution
    operationId: registerConstitution
    security:
      - bearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/RegistrationRequest'
    responses:
      '201':
        description: Registration successful
      '400':
        description: Invalid request
      '401':
        description: Unauthorized
      '409':
        description: Token already exists
```

#### 5.6.4 VERIFY Operation

```yaml
/namespaces/{namespace}:
  get:
    summary: Get namespace information and verify ownership
    operationId: getNamespace
    parameters:
      - name: namespace
        in: path
        required: true
        schema:
          type: string
    responses:
      '200':
        description: Namespace details
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/NamespaceInfo'
      '404':
        description: Namespace not found
```

#### 5.6.5 Version Listing

```yaml
/versions/{token}:
  get:
    summary: List available versions
    operationId: listVersions
    parameters:
      - name: token
        in: path
        required: true
        schema:
          type: string
    responses:
      '200':
        description: Version list
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/VersionList'
```

### 5.7 API Schemas

```yaml
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    ResolutionResult:
      type: object
      required:
        - token
        - bundle_uri
        - content_hash
        - issuer
        - version
      properties:
        token:
          type: string
          example: family.safe.guide
        canonical:
          type: string
          example: family.safe.guide
        bundle_uri:
          type: string
          format: uri
          example: https://cdn.creed.space/bundles/family/safe/guide/1.2.0.bundle
        content_hash:
          type: string
          example: sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069
        issuer:
          type: string
          example: creed.space
        version:
          type: string
          example: "1.2.0"
        csm1:
          type: string
          example: N5+F:ELEM
        ttl:
          type: integer
          example: 3600
        resolved_via:
          type: string
          enum: [cache, well-known, registry, dht]
        resolved_at:
          type: string
          format: date-time
        metadata:
          type: object
          additionalProperties: true

    SearchResults:
      type: object
      properties:
        total:
          type: integer
        offset:
          type: integer
        limit:
          type: integer
        results:
          type: array
          items:
            $ref: '#/components/schemas/SearchResult'

    SearchResult:
      type: object
      properties:
        token:
          type: string
        title:
          type: string
        description:
          type: string
        csm1:
          type: string
        tags:
          type: array
          items:
            type: string
        latest_version:
          type: string
        downloads:
          type: integer

    VersionList:
      type: object
      properties:
        token:
          type: string
        versions:
          type: array
          items:
            type: object
            properties:
              version:
                type: string
              released:
                type: string
                format: date
              status:
                type: string
                enum: [stable, prerelease, deprecated]
              downloads:
                type: integer
        latest:
          type: string
        recommended:
          type: string

    RegistrationRequest:
      type: object
      required:
        - token
        - bundle
        - manifest
      properties:
        token:
          type: string
        bundle:
          type: string
          format: byte
          description: Base64-encoded bundle
        manifest:
          type: object
          description: Bundle manifest
        replace:
          type: boolean
          default: false
          description: Replace existing version

    RegistrationResult:
      type: object
      properties:
        token:
          type: string
        version:
          type: string
        bundle_uri:
          type: string
        registered_at:
          type: string
          format: date-time

    NamespaceInfo:
      type: object
      properties:
        namespace:
          type: string
        owner:
          type: string
        tier:
          type: string
          enum: [core, org, community, personal]
        delegation_policy:
          type: string
        created_at:
          type: string
          format: date-time
        constitution_count:
          type: integer

    Error:
      type: object
      properties:
        code:
          type: string
        message:
          type: string
        details:
          type: object
```

### 5.8 Example Requests

```bash
# Resolve token
curl https://registry.creed.space/v1/resolve/family.safe.guide

# Resolve specific version
curl "https://registry.creed.space/v1/resolve/family.safe.guide?version=1.2.0"

# Search by persona and tags
curl "https://registry.creed.space/v1/search?persona=N&tags=family&tags=children"

# List versions
curl https://registry.creed.space/v1/versions/family.safe.guide

# Register constitution (authenticated)
curl -X POST https://registry.creed.space/v1/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "company.acme.legal.compliance",
    "bundle": "<base64>",
    "manifest": {...}
  }'
```

### 5.9 Caching Strategy

#### 5.9.1 Cache Implementation

```python
@dataclass
class CacheEntry:
    """Cached resolution result"""
    result: ResolutionResult
    cached_at: datetime
    ttl: int  # seconds

    def is_stale(self) -> bool:
        """Check if cache entry is stale"""
        return datetime.utcnow() > self.cached_at + timedelta(seconds=self.ttl)

    def remaining_ttl(self) -> int:
        """Remaining seconds until stale"""
        elapsed = (datetime.utcnow() - self.cached_at).total_seconds()
        return max(0, self.ttl - int(elapsed))


class ResolutionCache:
    """Cache for resolution results"""

    def __init__(self, max_size: int = 10000):
        self._cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

    def _key(self, token: str, version: str) -> str:
        """Generate cache key"""
        canonical = canonicalize(token)
        return hashlib.sha256(
            f"{canonical}@{version}".encode()
        ).hexdigest()[:16]

    def get(self, token: str, version: str) -> Optional[CacheEntry]:
        """Get from cache"""
        key = self._key(token, version)
        entry = self._cache.get(key)
        if entry:
            if entry.is_stale():
                del self._cache[key]
                self.misses += 1
                return None
            self.hits += 1
            return entry
        self.misses += 1
        return None

    def set(self, token: str, version: str, result: ResolutionResult):
        """Set cache entry"""
        if len(self._cache) >= self.max_size:
            self._evict_stale()
        key = self._key(token, version)
        self._cache[key] = CacheEntry(
            result=result,
            cached_at=datetime.utcnow(),
            ttl=result.ttl,
        )

    def invalidate(self, token: str, version: str = None):
        """Invalidate cache entry"""
        if version:
            key = self._key(token, version)
            self._cache.pop(key, None)
        else:
            # Invalidate all versions
            canonical = canonicalize(token)
            to_remove = [k for k, v in self._cache.items()
                        if v.result.canonical == canonical]
            for key in to_remove:
                del self._cache[key]

    def _evict_stale(self):
        """Remove stale entries"""
        to_remove = [k for k, v in self._cache.items() if v.is_stale()]
        for key in to_remove:
            del self._cache[key]
        # If still over capacity, evict oldest
        if len(self._cache) >= self.max_size:
            oldest = min(self._cache.items(), key=lambda x: x[1].cached_at)
            del self._cache[oldest[0]]

    def stats(self) -> Dict:
        """Cache statistics"""
        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': (self.hits / (self.hits + self.misses)
                        if (self.hits + self.misses) > 0 else 0),
        }
```

#### 5.9.2 TTL Guidelines

| Content Type | Default TTL | Max TTL |
|--------------|-------------|---------|
| Stable versions | 1 hour | 24 hours |
| Latest alias | 5 minutes | 1 hour |
| Canary alias | 1 minute | 5 minutes |
| Namespace info | 1 hour | 24 hours |
| Search results | 5 minutes | 30 minutes |

### 5.10 Discovery Methods

#### 5.10.1 Well-Known URI

Issuers MAY publish constitutions at well-known URIs:

```
https://{issuer}/.well-known/vcp/{path}.json
https://{issuer}/.well-known/vcp/{path}/versions.json
https://{issuer}/.well-known/vcp/{path}/{version}.bundle
```

Example:

```
https://creed.space/.well-known/vcp/family/safe/guide.json
https://creed.space/.well-known/vcp/family/safe/guide/versions.json
https://creed.space/.well-known/vcp/family/safe/guide/1.2.0.bundle
```

#### 5.10.2 DNS Discovery

For federated resolution, registries can be discovered via DNS SRV records:

```
_vcp._tcp.creed.space.       IN  SRV  10 0 443 registry.creed.space.
_vcp-peer._tcp.creed.space.  IN  SRV  20 0 443 peer1.registry.example.
```

#### 5.10.3 WebFinger

Alternative discovery via WebFinger:

```
GET /.well-known/webfinger?resource=vcp:family.safe.guide
Host: creed.space

{
  "subject": "vcp:family.safe.guide",
  "links": [
    {
      "rel": "vcp-bundle",
      "href": "https://cdn.creed.space/bundles/family/safe/guide/1.2.0.bundle",
      "properties": {
        "version": "1.2.0",
        "hash": "sha256:7f83b165..."
      }
    }
  ]
}
```

### 5.11 Distributed Registry

#### 5.11.1 Federation Model

```
+------------------------------------------------------------------+
|                     FEDERATED REGISTRY MODEL                      |
|                                                                   |
|  REGISTRY         REGISTRY         REGISTRY                      |
|  creed.space <--> example.org <--> acme.com                      |
|       |                |                |                         |
|       +----------------+----------------+                         |
|                        |                                          |
|                   SYNC LAYER                                      |
|                   - Gossip                                        |
|                   - Merkle sync                                   |
|                   - Conflict res                                  |
+------------------------------------------------------------------+
```

#### 5.11.2 Content-Addressed Storage

For immutable bundles:

```python
class ContentAddressedRegistry:
    """Content-addressed bundle storage"""

    def store(self, bundle: bytes) -> str:
        """Store bundle, return content hash"""
        hash_value = hashlib.sha256(bundle).hexdigest()
        return f"sha256:{hash_value}"

    def fetch(self, content_hash: str) -> bytes:
        """Fetch bundle by content hash"""
        pass

    def resolve_via_hash(self, content_hash: str) -> str:
        """Get bundle URI from content hash"""
        return f"https://cas.creed.space/{content_hash}"
```

#### 5.11.3 DHT Integration (Future)

```python
class DHTResolver:
    """Distributed Hash Table resolution (future)"""

    async def resolve(self, token: str) -> Optional[ResolutionResult]:
        """
        Resolve via DHT (IPFS, libp2p, etc.)

        Token hash -> DHT lookup -> CID -> Bundle
        """
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        cid = await self.dht.get(token_hash)
        if not cid:
            return None
        bundle_data = await self.ipfs.cat(cid)
        return self._parse_bundle(bundle_data)
```

### 5.12 Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `NOT_FOUND` | Token not found | 404 |
| `INVALID_TOKEN` | Invalid token format | 400 |
| `INVALID_VERSION` | Invalid version constraint | 400 |
| `NETWORK_ERROR` | Network failure | 502 |
| `TIMEOUT` | Resolution timeout | 504 |
| `UNAUTHORIZED` | Auth required | 401 |
| `FORBIDDEN` | Access denied | 403 |
| `RATE_LIMITED` | Too many requests | 429 |

### 5.13 Resolution Metrics

Implementations SHOULD track:

- Resolution latency (p50, p95, p99)
- Cache hit rate
- Resolution method distribution
- Error rates by type

---

## 6. Value Ontology

### 6.1 Status and Scope

The Value Ontology is an OPTIONAL component of VCP/I. VCP functions completely without a populated ontology -- tokens are names that resolve to bundles regardless of whether semantic backing exists.

The ontology enables optional enhancements:

- Semantic search ("find constitutions about fairness")
- Conflict detection ("these constitutions have value tension")
- Composition assistance ("these values complement each other")
- Cross-cultural translation

Building a proper cross-cultural value ontology is a significant research undertaking. This section documents the structure and interface. The actual curation of value statements across traditions is a separate scholarly project.

### 6.2 Ontology Structure

```
Value Ontology
+-- Categories (7)
|   +-- Values (multiple per category)
|   |   +-- Value Statements (~500 total)
|   |   |   +-- Core (always apply)
|   |   |   +-- Important (generally apply)
|   |   |   +-- Contextual (situation-dependent)
```

#### 6.2.1 Schema

```json
{
  "$schema": "https://vcp.creed.space/schema/ontology/v1.json",
  "ontology_version": "1.0.0",
  "value_categories": [...],
  "value_statements": [...],
  "relationships": {
    "hierarchy": [...],
    "tensions": [...],
    "complements": [...]
  },
  "composition_rules": {...}
}
```

### 6.3 Foundations

The ontology draws from:

- **Moral Foundations Theory** (Haidt): Care, Fairness, Loyalty, Authority, Sanctity
- **Schwartz Values**: 10 basic human values
- **Virtue Ethics**: Character-based values
- **Deontological Ethics**: Duty-based values
- **Consequentialist Ethics**: Outcome-based values

### 6.4 Value Categories

The ontology defines seven top-level categories:

| ID | Name | Description | Foundation |
|----|------|-------------|------------|
| `care` | Care and Compassion | Caring for others, reducing harm | Moral Foundations |
| `fairness` | Fairness and Justice | Equitable treatment, rights | Moral Foundations |
| `autonomy` | Autonomy and Freedom | Self-determination, liberty | Liberal Ethics |
| `truth` | Truth and Honesty | Accuracy, transparency | Virtue Ethics |
| `loyalty` | Loyalty and Belonging | Group commitment, tradition | Moral Foundations |
| `authority` | Authority and Order | Hierarchy, social order | Moral Foundations |
| `sanctity` | Sanctity and Purity | Sacredness, dignity | Moral Foundations |

```python
VALUE_CATEGORIES = {
    'care': {
        'name': 'Care and Compassion',
        'description': 'Values related to caring for others and reducing harm',
        'children': ['protection', 'nurturing', 'healing', 'support'],
        'traditions': ['care_ethics', 'buddhism', 'christianity'],
    },
    'fairness': {
        'name': 'Fairness and Justice',
        'description': 'Values related to equitable treatment and rights',
        'children': ['equality', 'reciprocity', 'rights', 'due_process'],
        'traditions': ['liberalism', 'egalitarianism', 'kantian'],
    },
    'autonomy': {
        'name': 'Autonomy and Freedom',
        'description': 'Values related to self-determination and liberty',
        'children': ['consent', 'privacy', 'self_expression', 'choice'],
        'traditions': ['liberalism', 'existentialism', 'enlightenment'],
    },
    'truth': {
        'name': 'Truth and Honesty',
        'description': 'Values related to accuracy and transparency',
        'children': ['honesty', 'transparency', 'accuracy', 'authenticity'],
        'traditions': ['virtue_ethics', 'scientific_realism', 'pragmatism'],
    },
    'loyalty': {
        'name': 'Loyalty and Belonging',
        'description': 'Values related to group membership and commitment',
        'children': ['fidelity', 'patriotism', 'tradition', 'community'],
        'traditions': ['communitarianism', 'confucianism', 'nationalism'],
    },
    'authority': {
        'name': 'Authority and Order',
        'description': 'Values related to hierarchy and social order',
        'children': ['respect', 'obedience', 'duty', 'discipline'],
        'traditions': ['conservatism', 'confucianism', 'military_ethics'],
    },
    'sanctity': {
        'name': 'Sanctity and Purity',
        'description': 'Values related to sacredness and moral purity',
        'children': ['cleanliness', 'temperance', 'reverence', 'dignity'],
        'traditions': ['religious_ethics', 'stoicism', 'natural_law'],
    },
}
```

### 6.5 Value Statements

#### 6.5.1 Statement Structure

```python
@dataclass
class ValueStatement:
    """A single value statement in the ontology"""

    id: str                     # Unique identifier
    statement: str              # Natural language statement
    category: str               # Category path (e.g., "care.protection")
    strength: str               # "core", "important", "contextual"
    traditions: List[str]       # Cultural/philosophical origins
    conflicts_with: List[str]   # IDs of conflicting values
    complements: List[str]      # IDs of complementary values
    contexts: List[str]         # When this applies
```

#### 6.5.2 Core Value Statements

```python
CORE_VALUES = [
    {
        'id': 'protect_life',
        'statement': 'Protect human life and physical safety',
        'category': 'care.protection',
        'strength': 'core',
        'traditions': ['hippocratic', 'human_rights', 'natural_law'],
        'conflicts_with': [],
        'complements': ['prevent_harm', 'support_vulnerable'],
    },
    {
        'id': 'prevent_harm',
        'statement': 'Prevent unnecessary harm to persons',
        'category': 'care.protection',
        'strength': 'core',
        'traditions': ['consequentialism', 'care_ethics'],
        'conflicts_with': [],
        'complements': ['protect_life', 'heal_injured'],
    },
    {
        'id': 'respect_autonomy',
        'statement': 'Respect individual autonomy and self-determination',
        'category': 'autonomy.consent',
        'strength': 'core',
        'traditions': ['kantian', 'liberalism'],
        'conflicts_with': ['protect_vulnerable'],  # Tension
        'complements': ['ensure_consent', 'protect_privacy'],
    },
    {
        'id': 'maintain_honesty',
        'statement': 'Communicate truthfully and avoid deception',
        'category': 'truth.honesty',
        'strength': 'core',
        'traditions': ['virtue_ethics', 'kantian'],
        'conflicts_with': ['protect_feelings'],  # Tension
        'complements': ['be_transparent', 'acknowledge_uncertainty'],
    },
    {
        'id': 'ensure_fairness',
        'statement': 'Treat individuals fairly and without discrimination',
        'category': 'fairness.equality',
        'strength': 'core',
        'traditions': ['egalitarianism', 'justice_theory'],
        'conflicts_with': [],
        'complements': ['respect_rights', 'apply_consistently'],
    },
]
```

#### 6.5.3 Domain-Specific Values

```python
# Child Safety (family.* domain)
CHILD_SAFETY_VALUES = [
    {
        'id': 'child_protection_absolute',
        'statement': 'Prioritize child safety above other considerations',
        'category': 'care.protection',
        'strength': 'core',
        'contexts': ['children_present', 'minor_users'],
        'traditions': ['child_welfare', 'parens_patriae'],
    },
    {
        'id': 'age_appropriate_content',
        'statement': 'Ensure content is appropriate for the audience age',
        'category': 'care.nurturing',
        'strength': 'important',
        'contexts': ['children_present'],
    },
]

# Professional (work.* domain)
PROFESSIONAL_VALUES = [
    {
        'id': 'maintain_confidentiality',
        'statement': 'Protect confidential information',
        'category': 'authority.duty',
        'strength': 'core',
        'contexts': ['professional', 'legal'],
    },
    {
        'id': 'avoid_conflicts_interest',
        'statement': 'Avoid and disclose conflicts of interest',
        'category': 'fairness.reciprocity',
        'strength': 'important',
        'contexts': ['professional', 'fiduciary'],
    },
]

# Healthcare (context: health)
HEALTHCARE_VALUES = [
    {
        'id': 'do_no_harm',
        'statement': 'Primum non nocere - First, do no harm',
        'category': 'care.healing',
        'strength': 'core',
        'contexts': ['medical', 'health'],
        'traditions': ['hippocratic'],
    },
    {
        'id': 'informed_consent_medical',
        'statement': 'Obtain informed consent for medical decisions',
        'category': 'autonomy.consent',
        'strength': 'core',
        'contexts': ['medical'],
    },
]
```

### 6.6 Relationships

#### 6.6.1 Hierarchy Relationships

```python
VALUE_HIERARCHY = [
    # Category -> Subcategory
    {'parent': 'care', 'child': 'protection', 'relation': 'subsumes'},
    {'parent': 'care', 'child': 'nurturing', 'relation': 'subsumes'},
    {'parent': 'care', 'child': 'healing', 'relation': 'subsumes'},

    # Subcategory -> Specific value
    {'parent': 'protection', 'child': 'child_safety', 'relation': 'specializes'},
    {'parent': 'protection', 'child': 'physical_safety', 'relation': 'specializes'},
    {'parent': 'protection', 'child': 'data_protection', 'relation': 'specializes'},

    # Value -> Implementation
    {'parent': 'honesty', 'child': 'no_deception', 'relation': 'implements'},
    {'parent': 'honesty', 'child': 'acknowledge_uncertainty', 'relation': 'implements'},
]
```

#### 6.6.2 Tension Relationships

Values in tension can both be held, but MAY conflict in specific situations:

```python
VALUE_TENSIONS = [
    {
        'values': ['autonomy', 'protection'],
        'description': 'Protecting someone may limit their autonomy',
        'resolution': 'Consider capacity, severity of harm, reversibility',
        'examples': [
            'Medical intervention for incapacitated patient',
            'Restricting content for child safety',
        ],
    },
    {
        'values': ['honesty', 'care'],
        'description': 'Truth may cause harm (e.g., blunt medical prognosis)',
        'resolution': 'Tactful truth, timing, compassionate delivery',
        'examples': [
            'Delivering bad news to patient',
            'Honest feedback that may hurt',
        ],
    },
    {
        'values': ['loyalty', 'fairness'],
        'description': 'Loyalty to group may conflict with fair treatment of outsiders',
        'resolution': 'Universal principles take precedence over group loyalty',
        'examples': [
            'Nepotism vs merit-based hiring',
            'Whistleblowing on group wrongdoing',
        ],
    },
    {
        'values': ['authority', 'autonomy'],
        'description': 'Respecting authority may limit individual freedom',
        'resolution': 'Legitimate authority respects core rights',
        'examples': [
            'Following unjust orders',
            'Challenging organizational policies',
        ],
    },
    {
        'values': ['privacy', 'transparency'],
        'description': 'Privacy rights may conflict with need for transparency',
        'resolution': 'Public interest test, minimize privacy intrusion',
        'examples': [
            'Public records vs personal privacy',
            'Whistleblower protection',
        ],
    },
]
```

#### 6.6.3 Complement Relationships

Values that reinforce each other:

```python
VALUE_COMPLEMENTS = [
    {
        'values': ['honesty', 'transparency'],
        'description': 'Both support openness and truthfulness',
    },
    {
        'values': ['care', 'fairness'],
        'description': 'Caring fairly for all',
    },
    {
        'values': ['autonomy', 'informed_consent'],
        'description': 'Consent requires autonomy; autonomy enables consent',
    },
    {
        'values': ['loyalty', 'trust'],
        'description': 'Loyalty builds trust; trust enables loyalty',
    },
]
```

### 6.7 Query Interface

```python
class ValueOntology:
    """Query interface for value ontology"""

    def __init__(self, data_path: str = None):
        self.data = load_ontology(data_path)

    def get_value(self, value_id: str) -> ValueStatement:
        """Get a specific value by ID"""
        pass

    def get_category(self, category_id: str) -> Category:
        """Get a category and its values"""
        pass

    def find_by_category(self, category: str) -> List[ValueStatement]:
        """Find all values in a category"""
        pass

    def find_conflicts(self, value_id: str) -> List[Tension]:
        """Find values that conflict with given value"""
        pass

    def find_complements(self, value_id: str) -> List[str]:
        """Find values that complement given value"""
        pass

    def check_composition(self, value_ids: List[str]) -> CompositionResult:
        """
        Check if values can be composed together.

        Returns:
            CompositionResult with conflicts, tensions, and suggestions
        """
        pass

    def translate(self, value_id: str, tradition: str) -> str:
        """
        Find equivalent expression in different tradition.

        e.g., translate("protect_vulnerable", "buddhist") -> "karuna (compassion)"
        """
        pass

    def search(self, query: str) -> List[ValueStatement]:
        """Full-text search of value statements"""
        pass
```

### 6.8 Composition Check

```python
@dataclass
class CompositionResult:
    """Result of checking value composition"""

    compatible: bool
    values: List[str]
    conflicts: List[Conflict]       # Direct conflicts (incompatible)
    tensions: List[Tension]         # Tensions (require resolution)
    suggestions: List[str]          # Resolution suggestions

    def has_blocking_conflicts(self) -> bool:
        """Check if any conflicts prevent composition"""
        return len(self.conflicts) > 0

    def get_resolution_hints(self) -> List[str]:
        """Get hints for resolving tensions"""
        hints = []
        for tension in self.tensions:
            hints.append(tension.resolution)
        return hints
```

### 6.9 Cross-Tradition Equivalents

| UVC Value | Western | Buddhist | Confucian | Islamic |
|-----------|---------|----------|-----------|---------|
| protect_life | Sanctity of life | Ahimsa | Ren (ren) | Hifz al-nafs |
| honesty | Veracity | Sacca | Xin (xin) | Sidq |
| respect_elders | Filial piety | - | Xiao (xiao) | Birr al-walidayn |
| justice | Fairness | - | Yi (yi) | 'Adl |

### 6.10 Moral Foundations Mapping

| Moral Foundation | UVC Category | Key Values |
|-----------------|--------------|------------|
| Care/Harm | care | protect_life, prevent_harm, nurture |
| Fairness/Cheating | fairness | equality, reciprocity, justice |
| Loyalty/Betrayal | loyalty | fidelity, patriotism, group_care |
| Authority/Subversion | authority | respect, obedience, duty |
| Sanctity/Degradation | sanctity | purity, dignity, reverence |
| Liberty/Oppression | autonomy | freedom, consent, self_determination |

### 6.11 JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://vcp.creed.space/schema/ontology/v1.json",
  "title": "UVC Value Ontology",
  "type": "object",
  "required": ["ontology_version", "value_categories", "value_statements"],
  "properties": {
    "ontology_version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
    },
    "value_categories": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "name", "description"],
        "properties": {
          "id": {"type": "string"},
          "name": {"type": "string"},
          "description": {"type": "string"},
          "children": {
            "type": "array",
            "items": {"type": "string"}
          }
        }
      }
    },
    "value_statements": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "statement", "category"],
        "properties": {
          "id": {"type": "string"},
          "statement": {"type": "string", "maxLength": 256},
          "category": {"type": "string"},
          "strength": {"enum": ["core", "important", "contextual"]},
          "traditions": {
            "type": "array",
            "items": {"type": "string"}
          },
          "conflicts_with": {
            "type": "array",
            "items": {"type": "string"}
          },
          "complements": {
            "type": "array",
            "items": {"type": "string"}
          }
        }
      }
    },
    "relationships": {
      "type": "object",
      "properties": {
        "hierarchy": {"type": "array"},
        "tensions": {"type": "array"},
        "complements": {"type": "array"}
      }
    }
  }
}
```

---

## 7. Encoding Algorithms

### 7.1 Unified Encoder

Implementations SHOULD provide a unified encoding interface:

```python
class UVCEncoder:
    """Encode UVC tokens to various formats"""

    def __init__(self, registry: 'UVCRegistry' = None, secret: bytes = None):
        self.registry = registry
        self.secret = secret or os.urandom(32)

    def encode(self, token: str, format: str, **kwargs) -> str:
        """Encode canonical token to target format"""
        canonical = canonicalize(token)

        if format == 'canonical':
            return canonical
        elif format == 'csm1':
            return self._to_csm1(canonical, **kwargs)
        elif format == 'uri':
            issuer = kwargs.get('issuer', 'creed.space')
            return canonical_to_uri(canonical, issuer)
        elif format == 'obfuscated':
            secret = kwargs.get('secret', self.secret)
            return UVCObfuscator().obfuscate(canonical, secret)
        elif format == 'phonetic':
            csm1 = self._to_csm1(canonical)
            return to_phonetic(csm1)
        elif format == 'emoji':
            return to_emoji(canonical)
        elif format == 'hash':
            algorithm = kwargs.get('algorithm', 'sha256')
            return to_hash(canonical, algorithm)
        elif format == 'qr':
            return to_qr(canonical, kwargs.get('issuer', 'creed.space'))
        else:
            raise ValueError(f"Unknown format: {format}")

    def decode(self, encoded: str, format: str, **kwargs) -> str:
        """Decode from format back to canonical"""
        if format == 'canonical':
            return canonicalize(encoded)
        elif format == 'csm1':
            return csm1_to_canonical(encoded)
        elif format == 'uri':
            return uri_to_canonical(encoded)
        elif format == 'obfuscated':
            token_list = kwargs.get('token_list', [])
            secret = kwargs.get('secret', self.secret)
            return UVCObfuscator().deobfuscate(encoded, secret, token_list)
        elif format == 'phonetic':
            csm1 = self._from_phonetic(encoded)
            return csm1_to_canonical(csm1)
        elif format == 'emoji':
            return from_emoji(encoded)
        elif format == 'hash':
            raise ValueError("Hash format is not reversible")
        elif format == 'qr':
            return from_qr(encoded)
        else:
            raise ValueError(f"Unknown format: {format}")

    def _to_csm1(self, canonical: str, **kwargs) -> str:
        """Convert canonical to CSM1 (requires registry)"""
        if self.registry:
            return self.registry.lookup_csm1(canonical)
        return derive_csm1(canonical)

    def _from_phonetic(self, phonetic: str) -> str:
        """Parse phonetic back to CSM1"""
        reverse_nato = {v: k for k, v in NATO_PHONETIC.items()}
        parts = phonetic.split('-')
        return ''.join(reverse_nato.get(p, '') for p in parts)
```

### 7.2 Deterministic Serialization

All encoding algorithms MUST be deterministic: the same input MUST produce the same output. Specifically:

1. **Canonical**: Apply the canonicalization algorithm from Section 2.2.3 before any encoding
2. **CSM1**: Mapping is deterministic via the `CSM1_TO_UVC_MAPPING` table
3. **URI**: Path separators are deterministically replaced (`'.'` to `'/'`)
4. **Hash**: SHA-256 of UTF-8-encoded canonical form
5. **Obfuscated**: HMAC-SHA256 with provided secret, deterministic index selection
6. **Phonetic**: Character-by-character NATO phonetic alphabet mapping
7. **Emoji**: Segment-by-segment codex lookup (first 3 segments)
8. **QR**: URI format as payload, error correction level M

### 7.3 Resolver Reference Implementation

```python
class UVCResolver:
    """
    Resolve UVC tokens to VCP bundle locations.

    Usage:
        resolver = UVCResolver()
        result = await resolver.resolve("family.safe.guide")
        print(result.bundle_uri)
    """

    DEFAULT_REGISTRIES = [
        "https://registry.creed.space",
    ]

    def __init__(
        self,
        registries: List[str] = None,
        cache: 'ResolutionCache' = None,
        timeout: float = 10.0,
    ):
        self.registries = registries or self.DEFAULT_REGISTRIES
        self.cache = cache or ResolutionCache()
        self.timeout = timeout

    async def resolve(
        self,
        token: str,
        version: str = "latest",
        skip_cache: bool = False,
    ) -> ResolutionResult:
        """Resolve UVC token to bundle location"""
        canonical = canonicalize(token)

        # Check cache
        if not skip_cache:
            cached = self.cache.get(canonical, version)
            if cached and not cached.is_stale():
                return cached.result

        # Try well-known
        result = await self._try_well_known(canonical, version)
        if result:
            self.cache.set(canonical, version, result)
            return result

        # Try registries
        for registry_url in self.registries:
            result = await self._try_registry(registry_url, canonical, version)
            if result:
                self.cache.set(canonical, version, result)
                return result

        raise ResolutionError(
            f"Could not resolve token: {token}",
            token=token,
            code="NOT_FOUND"
        )

    async def search(
        self,
        query: str = None,
        tags: List[str] = None,
        persona: str = None,
        limit: int = 20,
    ) -> List[Dict]:
        """Search for constitutions"""
        params = {'limit': limit}
        if query:
            params['q'] = query
        if tags:
            params['tags'] = tags
        if persona:
            params['persona'] = persona

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.registries[0]}/v1/search",
                params=params
            )
            response.raise_for_status()
            return response.json().get('results', [])

    async def list_versions(self, token: str) -> Dict:
        """List available versions for token"""
        canonical = canonicalize(token)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.registries[0]}/v1/versions/{canonical}"
            )
            response.raise_for_status()
            return response.json()
```

### 7.4 Token Parser Reference Implementation

```python
@dataclass
class UVCToken:
    """Parsed UVC token"""

    raw: str                    # Original input
    canonical: str              # Canonical form
    segments: List[str]         # Path segments
    namespace_type: str         # 'core', 'org', 'community', 'personal'
    namespace: str              # Full namespace prefix
    version: Optional[str]      # Version constraint if present
    version_constraint: str     # 'exact', 'compatible', 'approximate', 'alias'

    def to_uri(self, issuer: str = "creed.space") -> str:
        """Convert to VCP bundle URI"""
        path = '.'.join(self.segments)
        uri = f"creed://{issuer}/{path}"
        if self.version:
            uri += f"@{self.version}"
        return uri

    def __str__(self) -> str:
        return self.canonical

    def __hash__(self) -> int:
        return hash(self.canonical)

    def __eq__(self, other) -> bool:
        if isinstance(other, UVCToken):
            return self.canonical == other.canonical
        if isinstance(other, str):
            return self.canonical == canonicalize(other)
        return False


class UVCTokenParser:
    """Parse UVC tokens into structured form"""

    CORE_NAMESPACES = frozenset({'family', 'work', 'secure', 'creative', 'reality'})
    ORG_PREFIXES = frozenset({'company', 'school', 'ngo'})
    COMMUNITY_PREFIXES = frozenset({'religion', 'culture', 'community'})

    def parse(self, token: str) -> UVCToken:
        """
        Parse a UVC token string into structured form.

        Raises:
            ValueError: If token is invalid
        """
        # Validate first
        validator = UVCTokenValidator()
        result = validator.validate(token)
        if not result.valid:
            raise ValueError(f"Invalid UVC token: {result.message}")

        # Canonicalize
        canonical = canonicalize(token)

        # Extract version
        version = None
        version_constraint = 'none'
        base_token = canonical

        if '@' in canonical:
            base_token, version = canonical.rsplit('@', 1)
            if version in ('latest', 'canary'):
                version_constraint = 'alias'
            elif version.startswith('^'):
                version_constraint = 'compatible'
                version = version[1:]
            elif version.startswith('~'):
                version_constraint = 'approximate'
                version = version[1:]
            else:
                version_constraint = 'exact'

        # Parse segments
        segments = base_token.split('.')

        # Determine namespace type
        first = segments[0]
        if first in self.CORE_NAMESPACES:
            namespace_type = 'core'
            namespace = first
        elif first in self.ORG_PREFIXES:
            namespace_type = 'org'
            namespace = '.'.join(segments[:2])
        elif first in self.COMMUNITY_PREFIXES:
            namespace_type = 'community'
            namespace = '.'.join(segments[:2])
        elif first == 'user':
            namespace_type = 'personal'
            namespace = '.'.join(segments[:2])
        else:
            raise ValueError(f"Unknown namespace: {first}")

        return UVCToken(
            raw=token,
            canonical=canonical,
            segments=segments,
            namespace_type=namespace_type,
            namespace=namespace,
            version=version,
            version_constraint=version_constraint,
        )


def parse_uvc_token(token: str) -> UVCToken:
    """Convenience function to parse UVC token"""
    return UVCTokenParser().parse(token)
```

### 7.5 HTTP API Reference

#### 7.5.1 Token Validation

```http
POST /api/vcp/token/validate
Content-Type: application/json

{"token": "family.safe.guide@1.2.0"}
```

Response:

```json
{
  "valid": true,
  "canonical": "family.safe.guide",
  "domain": "family",
  "approach": "safe",
  "role": "guide",
  "version": "1.2.0",
  "uri": "creed://creed.space/family.safe.guide@1.2.0"
}
```

---

## 8. Security Considerations

### 8.1 Identity-Layer Threat Model

| Adversary | Capability | Goal |
|-----------|-----------|------|
| Namespace squatter | Registration access | Claim namespaces to impersonate organizations |
| Homograph attacker | Unicode knowledge | Create visually confusing tokens |
| Cache poisoner | Network interposition | Return malicious resolution results |
| DDoS attacker | Network access | Overwhelm registry with requests |
| Insider threat | UVC modification access | Bias ontology or weaken constraints |
| Gradual drift | Incremental changes | Shift token meanings without detection |

### 8.2 Namespace Squatting

**Risk**: Malicious actors register namespaces to impersonate organizations.

**Mitigations**:

1. Organizational namespaces MUST require proof of ownership (DNS or HTTPS verification)
2. Annual renewal REQUIRED for organizational and community namespaces
3. Grace period before release: 90 days
4. High-value namespaces MAY have stricter requirements
5. Reserved words MUST NOT be registered
6. Dispute resolution process (Section 4.7) for contested claims

### 8.3 Homograph Attacks

**Risk**: Similar-looking characters create confusing tokens.

```python
# Example homograph attack
"company.acme.legal"   # Uses Cyrillic 'a' instead of Latin 'a'
```

**Mitigations**:

1. NFKC normalization MUST be applied, converting lookalikes to canonical form
2. Only ASCII lowercase letters (`a-z`) are allowed in segments
3. Visual inspection of registered tokens SHOULD be performed
4. Similar-looking namespaces SHOULD be flagged during registration

### 8.4 Reserved Word Bypass

**Risk**: Attackers try variants of reserved words.

**Mitigations**:

1. Validation MUST occur after canonicalization
2. Reserved word list MUST be checked against normalized form
3. Substring matching SHOULD be applied for critical words (e.g., `admin`, `system`)

### 8.5 Length Attacks

**Risk**: Extremely long tokens cause denial of service.

**Mitigations**:

1. Hard limit of 128 characters total
2. Maximum 8 segments
3. Maximum 32 characters per segment
4. Implementations MUST reject tokens exceeding these limits before further processing

### 8.6 Resolution Integrity

**Risk**: Malicious registry returns wrong bundle.

**Mitigations**:

1. Content hash verification MUST be performed against the resolution result
2. Bundle signature verification MUST be performed
3. Cross-checking with multiple registries SHOULD be used for high-value constitutions
4. Certificate transparency for resolutions SHOULD be implemented

### 8.7 Cache Poisoning

**Risk**: Attacker poisons cache with malicious resolution.

**Mitigations**:

1. Signed resolution responses
2. Short TTLs for critical constitutions
3. Cache validation on use
4. Rate limiting on cache updates

### 8.8 Namespace Key Security

- Keys MUST be Ed25519 (same as VCP bundle signing)
- Key rotation MUST be supported with 30-day overlap
- Compromised keys MUST be revocable via email verification
- Hardware security modules are RECOMMENDED for high-value namespaces

### 8.9 DDoS Protection

**Mitigations**:

1. Rate limiting per client
2. CDN caching for popular constitutions
3. Fallback to cached versions when registry is unavailable
4. Multiple registry endpoints

### 8.10 UVC Ontology Attacks

**Risk**: Definition drift (gradual meaning shift), category capture (biasing additions toward a particular perspective), reference poisoning (corrupting the canonical corpus), version confusion (mixing incompatible versions).

**Mitigations**:

| Layer | Primary Defense | Secondary Defense | Monitoring |
|-------|-----------------|-------------------|------------|
| UVC (Identity) | Version locking | Multi-party governance | Change logs |

### 8.11 Privacy Leakage via State Telemetry

**Risk**: VCP logs reveal information about users (e.g., resolution patterns revealing interests).

**Mitigations**:

1. Anonymization at collection
2. Aggregation before storage
3. Purpose limitation on access
4. User consent for detailed logging
5. Time-bounded retention (default: 90 days)

---

## Appendices

### Appendix A: Format Recommendation Guide

| Use Case | Recommended Format |
|----------|-------------------|
| Database storage | canonical |
| API parameter | csm1 (short) |
| URL sharing | uri |
| Privacy context | obfuscated |
| Phone/radio | phonetic |
| Social media | emoji |
| Verification | hash |
| Physical media | qr |
| Hardware tag | nfc |
| Semantic web | json-ld |
| Embedded systems | compact binary |
| Verbal reference | mnemonic |

### Appendix B: Reserved Words (Complete List)

```python
RESERVED_WORDS = {
    # System terms
    'system', 'admin', 'root', 'internal', 'private', 'public',

    # Programming terms
    'null', 'undefined', 'true', 'false', 'none', 'void',

    # Infrastructure terms
    'api', 'test', 'debug', 'staging', 'production', 'default',

    # VCP-specific terms
    'vcp', 'uvc', 'csm', 'bundle', 'manifest', 'creed',

    # Common abuse targets
    'official', 'verified', 'authentic', 'real',
}
```

### Appendix C: Version Negotiation

When systems with different VCP versions exchange data:

1. Sender includes version header: `VCP-VERSION: 2.0.0`
2. Receiver checks compatibility
3. If MAJOR differs: reject or transcode
4. If MINOR differs (sender newer): receiver ignores unknown fields
5. If MINOR differs (sender older): receiver uses defaults for missing fields
6. PATCH differences: transparent

### Appendix D: Reference Implementations

- **Python, Rust, and TypeScript SDK**: github.com/Creed-Space/VCP-SDK
- **Website**: www.ValueContextProtocol.org

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-11 | Initial specification (5 separate documents) |
| 2.0.0 | 2026-03-08 | Unified specification; incorporated paper spec content; added NFC, JSON-LD, binary, mnemonic formats; expanded security section |

---

*This specification is released under CC BY 4.0. Contributions welcome.*
