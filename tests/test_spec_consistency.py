"""Cross-document consistency checks for the 2026-09-27 canon reconciliation.

Each test ties a normative table or constant in a layer specification to the
schema, test vector, or companion text that repeats it, so that the two cannot
drift silently.
"""

from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path
from typing import ClassVar

ROOT = Path(__file__).resolve().parents[1]
ADAPTATION = ROOT / "specs/VCP_ADAPTATION_v2.0.md"
IDENTITY = ROOT / "specs/VCP_IDENTITY_v2.0.md"
SEMANTICS = ROOT / "specs/VCP_SEMANTICS_v2.0.md"
AUDIT = ROOT / "specs/core/audit.md"
AMENDMENTS = ROOT / "specs/VCP_SPECIFICATION_v1.1_AMENDMENTS.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def value_table(text: str, heading: str) -> dict[str, str]:
    """Return {emoji: value} from the Markdown table under a §2.2 heading."""
    start = text.index(f"#### {heading}")
    end = text.find("\n#### ", start + 1)
    section = text[start:end]
    table: dict[str, str] = {}
    for line in section.splitlines():
        match = re.fullmatch(r"\| (\S+) \| ([a-z_]+) \|.*", line)
        if match:
            table[match.group(1)] = match.group(2)
    return table


class AdaptationVocabularyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = read(ADAPTATION)
        cls.definitions = load_json("schemas/vcp-adaptation-context.schema.json")[
            "definitions"
        ]

    def test_system_context_enum_matches_spec_table(self) -> None:
        table = value_table(self.text, "SYSTEM_CONTEXT (📡)")
        self.assertEqual(
            table,
            {
                "💻": "personal_device",
                "🏢": "workplace_system",
                "🖥️": "shared_terminal",
                "👁️": "monitored_environment",
            },
        )
        self.assertEqual(self.definitions["system_context_values"]["enum"], list(table))

    def test_culture_enum_matches_spec_table(self) -> None:
        table = value_table(self.text, "CULTURE (🌍)")
        self.assertEqual(
            list(table.values()),
            [
                "high_context",
                "low_context",
                "formal",
                "informal",
                "hierarchical",
                "egalitarian",
                "collectivist",
                "individualist",
            ],
        )
        self.assertEqual(self.definitions["culture_values"]["enum"], list(table))

    SITUATIONAL: ClassVar[dict[str, str]] = {
        "time_values": "TIME (⏰)",
        "space_values": "SPACE (📍)",
        "company_values": "COMPANY (👥)",
        "culture_values": "CULTURE (🌍)",
        "occasion_values": "OCCASION (🎭)",
        "environment_values": "ENVIRONMENT (🌡️)",
        "agency_values": "AGENCY (🔷)",
        "constraints_values": "CONSTRAINTS (🔶)",
        "system_context_values": "SYSTEM_CONTEXT (📡)",
        "embodiment_values": "EMBODIMENT (🧍)",
        "proximity_values": "PROXIMITY (↔️)",
        "formality_values": "FORMALITY (🎩)",
    }
    PERSONAL: ClassVar[dict[str, str]] = {
        "cognitive_state_values": "cognitive_state",
        "emotional_tone_values": "emotional_tone",
        "energy_level_values": "energy_level",
        "perceived_urgency_values": "perceived_urgency",
        "body_signals_values": "body_signals",
    }

    def test_every_situational_enum_matches_its_spec_table(self) -> None:
        for name, heading in self.SITUATIONAL.items():
            table = value_table(self.text, heading)
            with self.subTest(definition=name):
                self.assertTrue(table)
                self.assertEqual(self.definitions[name]["enum"], list(table))
                for emoji, value in table.items():
                    self.assertIn(f"{emoji} {value}", self.definitions[name]["description"])

    def test_summary_table_examples_come_from_the_value_tables(self) -> None:
        rows = re.findall(
            r"^\| \d+ \| \S+ \| \*\*(\w+)\*\* \| [^|]+\| ([^|]+) \|$",
            self.text,
            re.MULTILINE,
        )
        headings = {heading.split(" ")[0]: heading for heading in self.SITUATIONAL.values()}
        checked = 0
        for dimension, examples in rows:
            if dimension not in headings:
                continue
            table = value_table(self.text, headings[dimension])
            for pair in examples.strip().split(", "):
                emoji, value = pair.split(" ", 1)
                with self.subTest(dimension=dimension, example=pair):
                    self.assertEqual(table.get(emoji), value)
                    checked += 1
        self.assertGreater(checked, 50)

    def test_personal_state_enums_match_vcp_x_personal(self) -> None:
        personal = load_json("specs/extensions/VCP-X-Personal/schema.json")
        text = json.dumps(personal, ensure_ascii=False)
        for name, dimension in self.PERSONAL.items():
            enum = self.definitions[name]["enum"]
            with self.subTest(definition=name):
                self.assertIn(json.dumps(enum, ensure_ascii=False), text)
                self.assertRegex(self.text, rf"\*\*{dimension.upper()}\*\* \| [^|]+\| {', '.join(enum)} \|")

    def test_unknown_values_are_tolerated_not_rejected(self) -> None:
        self.assertIn(
            "A receiver or decoder MUST NOT reject a context string because a dimension carries a value",
            self.text,
        )
        self.assertNotIn("unknown dimension values | Reject the signal", self.text)
        self.assertIn("| **Unknown Value** |", self.text)
        self.assertIn("VCP/A §2.3 (unknown values and dimensions)", read(ROOT / "veps/VEP-0004-extended-vcpa-dimensions.md"))

    def test_dimension_count_statement(self) -> None:
        self.assertNotIn("encodes context across 18 dimensions", self.text)
        self.assertIn("14 baseline dimensions: 9 in the situational tier", self.text)


class EmergencyIndicatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = read(ADAPTATION)

    def emergency_tokens(self) -> set[str]:
        match = re.search(r"EMERGENCY_TOKENS = \{([^}]*)\}", self.text)
        self.assertIsNotNone(match)
        return set(re.findall(r'"([^"]+)"', match.group(1)))

    def test_canonical_emergency_set(self) -> None:
        self.assertEqual(self.emergency_tokens(), {"🚨", "🔥", "🌪️", "🛑"})

    def test_each_indicator_is_a_defined_dimension_value(self) -> None:
        expected = {
            "🚨": ("OCCASION (🎭)", "emergency"),
            "🔥": ("ENVIRONMENT (🌡️)", "fire"),
            "🌪️": ("ENVIRONMENT (🌡️)", "dangerous"),
            "🛑": ("EMBODIMENT (🧍)", "emergency_stop"),
        }
        self.assertEqual(set(expected), self.emergency_tokens())
        for emoji, (heading, value) in expected.items():
            with self.subTest(emoji=emoji):
                self.assertEqual(value_table(self.text, heading).get(emoji), value)

    def test_free_form_indicators_are_permitted_not_required(self) -> None:
        self.assertIn(
            "Implementations MAY also treat `⚠️` and `🆘` as emergency indicators",
            self.text,
        )
        self.assertNotIn("⚠️", self.emergency_tokens())
        self.assertNotIn("🆘", self.emergency_tokens())


class IdentityPrefixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = read(IDENTITY)
        cls.schema = load_json("schemas/vcp-identity-token.schema.json")

    def test_max_segments_agrees_with_abnf_and_schema(self) -> None:
        rule = re.search(r"'max_segments': (\d+),", self.text)
        self.assertIsNotNone(rule)
        self.assertEqual(int(rule.group(1)), 10)
        self.assertIn("token-path        = segment 2*9(\".\" segment)", self.text)
        self.assertIn("if len(segments) > 10:", self.text)
        self.assertEqual(self.schema["properties"]["segments"]["maxItems"], 10)

    def test_core_prefixes_agree_across_abnf_table_and_schema(self) -> None:
        core = ["family", "work", "secure", "creative", "reality"]
        comment = re.search(r"^;   Core: (.+)$", self.text, re.MULTILINE)
        self.assertIsNotNone(comment)
        self.assertEqual(comment.group(1).split(", "), core)
        self.assertEqual(self.schema["definitions"]["core_namespace"]["enum"], core)
        self.assertIn(
            "| **Core** | `family`, `work`, `secure`, `creative`, `reality` |",
            self.text,
        )

    def test_schema_examples_use_listed_prefixes(self) -> None:
        definitions = self.schema["definitions"]
        prefixes = {
            *definitions["core_namespace"]["enum"],
            *definitions["org_prefix"]["enum"],
            *definitions["community_prefix"]["enum"],
            "user",
        }
        tokens = list(self.schema["properties"]["token"]["examples"])
        tokens += [example["token"] for example in self.schema["examples"]]
        for token in tokens:
            with self.subTest(token=token):
                self.assertIn(token.split(".", 1)[0], prefixes)


class IdentityRuleSetTests(unittest.TestCase):
    """VCP/I §3.4.1: one segment rule, one length limit, syntax vs semantics."""

    SAMPLES = (
        "family.safe.guide",
        "family.safe.guide@1.2.0",
        "family.safe-.guide",
        "creative.growth.muse",
        "family.safe.guide.extra",
        "family.safe",
        "company.acme--x.legal.compliance:SEC",
        "company.acme.legal@^2.0.0",
        "religion.buddhist.meditation",
        "user.alice.personal",
        "user.alice",
        "user.al_ice.personal",
        "education.safe.guide",
        "org.example.dept.team.policy",
        "personal.alice.notes",
        "core.ethics.consent",
        "Family.safe.guide",
        "company.a.b.c.d.e.f.g.h.i",
        "company.a.b.c.d.e.f.g.h.i.j",
    )

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = read(IDENTITY)
        schema = load_json("schemas/vcp-identity-token.schema.json")
        cls.token_schema = schema["properties"]["token"]
        source = re.search(r'UVC_TOKEN_PATTERN = r"""(.*?)"""', cls.text, re.DOTALL)
        cls.spec_regex = re.compile(source.group(1), re.VERBOSE)

    def schema_accepts(self, token: str) -> bool:
        schema = self.token_schema
        return (
            len(token) <= schema["maxLength"]
            and re.fullmatch(schema["pattern"], token) is not None
            and all(re.fullmatch(rule["pattern"], token) for rule in schema["allOf"])
        )

    def test_spec_regex_and_schema_agree(self) -> None:
        for token in self.SAMPLES:
            with self.subTest(token=token):
                self.assertEqual(
                    self.spec_regex.fullmatch(token) is not None,
                    self.schema_accepts(token),
                )

    def test_syntax_pattern_accepts_unknown_prefixes(self) -> None:
        for token in ("education.safe.guide", "org.example.dept.team.policy"):
            with self.subTest(token=token):
                self.assertIsNotNone(re.fullmatch(self.token_schema["pattern"], token))
                self.assertFalse(self.schema_accepts(token))

    def test_single_length_limit_and_hyphen_rule(self) -> None:
        self.assertEqual(self.token_schema["maxLength"], 256)
        self.assertIn("'max_total_length': 256,", self.text)
        self.assertIn("if len(token) > 256:", self.text)
        self.assertIn("1. Hard limit of 256 characters total", self.text)
        self.assertIn("2. Maximum 10 segments", self.text)
        self.assertNotIn("cannot end with hyphen", self.text)
        self.assertNotIn("'no_trailing_hyphen': True", self.text)
        self.assertNotIn("1-32 lowercase alpha", self.text)


class SemanticsNotationTests(unittest.TestCase):
    def test_retired_bracket_notation_is_absent(self) -> None:
        # The changelog may name the retired notation; the body must not use it.
        text = read(SEMANTICS).split("\n## Changelog", 1)[0]
        for retired in ("CSM:SCOPE[", "PERSONA[", "REQUIRE[", "PRIORITY[", "PROOF["):
            with self.subTest(retired=retired):
                self.assertFalse(retired in text, f"{retired} appears in VCP/S")


class AuditLevelTests(unittest.TestCase):
    LEVELS = ("minimal", "standard", "full", "diagnostic")
    PLACEMENT: ClassVar[dict[str, str]] = {
        "timestamp": "standard",
        "session_id_hash": "standard",
        "verification_result": "minimal",
        "checks_passed": "standard",
        "bundle_id_hash": "minimal",
        "content_hash": "minimal",
        "issuer_hash": "standard",
        "version": "standard",
        "manifest_signature": "standard",
        "audit_level": "minimal",
        "request_id": "standard",
        "duration_ms": "full",
        "token_count": "full",
        "content_preview": "diagnostic",
    }

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = read(AUDIT)

    def test_default_level_is_stated(self) -> None:
        self.assertIn("The default audit level is `minimal`.", self.text)
        self.assertIn("The default level is `minimal`.", read(AMENDMENTS))

    def test_field_placement_table(self) -> None:
        start = self.text.index("### 3.2 AuditEntry")
        end = self.text.index("### 3.3 AuditStoreEntry")
        placement = {
            match.group(1): match.group(2)
            for match in re.finditer(
                r"^\| `(\w+)`\s*\|[^|]+\|\s*(\w+)\s*\|", self.text[start:end], re.MULTILINE
            )
        }
        self.assertEqual(placement, self.PLACEMENT)

    def test_amendment_j_lists_the_same_first_level_for_each_field(self) -> None:
        text = read(AMENDMENTS)
        start = text.index("### Audit Levels")
        end = text.index("### Privacy-Preserving Audit Entry")
        rows = {
            match.group(1): set(re.findall(r"`(\w+)`", match.group(2)))
            for match in re.finditer(
                r"^\| `(\w+)` \| ([^|]+) \|", text[start:end], re.MULTILINE
            )
        }
        self.assertEqual(list(rows), list(self.LEVELS))
        for level, fields in rows.items():
            expected = {
                field for field, first in self.PLACEMENT.items() if first == level
            }
            with self.subTest(level=level):
                self.assertEqual(fields, expected)

    def test_privacy_hash_vectors(self) -> None:
        import hmac

        key = bytes(range(32))
        vectors = re.findall(
            r'`privacy_hash\("([^"]+)"\)` is\s+`(hmac-sha256:[0-9a-f]{32})`', self.text
        )
        self.assertEqual(len(vectors), 2)
        for value, expected in vectors:
            digest = hmac.new(key, value.encode("utf-8"), hashlib.sha256).hexdigest()
            with self.subTest(value=value):
                self.assertEqual(f"hmac-sha256:{digest[:32]}", expected)
                self.assertEqual(len(expected), 44)
        self.assertIn("**Per-process random key.**", self.text)
        self.assertIn("**Operator secret.**", self.text)

    def test_hash_vector_reproduces_and_respects_its_level(self) -> None:
        match = re.search(
            r"^input  = (\{.*?\})\nJCS .*?\nentry_hash = ([0-9a-f]{64})$",
            self.text,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(match)
        vector = json.loads(re.sub(r"\n\s+", "", match.group(1)))
        canonical = json.dumps(
            vector, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        self.assertEqual(
            hashlib.sha256(canonical.encode("utf-8")).hexdigest(), match.group(2)
        )
        level = self.LEVELS.index(vector["audit_level"])
        store_names = {
            "request_id_hash": "request_id",
            "bundle_version": "version",
        }
        for field, value in vector.items():
            first = self.PLACEMENT.get(store_names.get(field, field))
            if value is None or first is None:
                continue
            with self.subTest(field=field):
                self.assertLessEqual(self.LEVELS.index(first), level)


PREFIXES = {
    "family", "work", "secure", "creative", "reality",
    "company", "school", "ngo", "religion", "culture", "community", "user",
}
HISTORICAL_STATUSES = {
    "historical-archived",
    "historical-non-normative",
    "superseded-source-generation",
    "research-or-submission-draft",
}
SUPERSEDED_MARKERS = ("> **Superseded", "> **Consolidated.", "> **Merged copy.")


def current_documents() -> list[Path]:
    """Markdown, JSON and YAML sources that are neither historical nor superseded."""
    inventory = {
        item["path"]: item["status"]
        for item in load_json("status/document-inventory.json")["artifacts"]
    }
    roots = ("specs", "schemas", "veps", "docs", "_wiki")
    paths = [ROOT / "README.md"]
    for root in roots:
        for suffix in ("*.md", "*.json", "*.yaml", "*.yml"):
            paths.extend((ROOT / root).rglob(suffix))
    selected = []
    for path in sorted(set(paths)):
        relative = path.relative_to(ROOT).as_posix()
        if "/invalid/" in relative or relative.endswith(("CHANGELOG.md", "_wiki/log.md")):
            continue
        if inventory.get(relative) in HISTORICAL_STATUSES:
            continue
        head = read(path)[:3000]
        if any(marker in head for marker in SUPERSEDED_MARKERS):
            continue
        selected.append(path)
    return selected


class CurrentDocumentSweepTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.documents = {path: read(path) for path in current_documents()}

    def test_sweep_covers_the_expected_documents(self) -> None:
        names = {path.relative_to(ROOT).as_posix() for path in self.documents}
        self.assertIn("specs/VCP_SEMANTICS_v2.0.md", names)
        self.assertIn("_wiki/systems/vep-specs.md", names)
        self.assertNotIn("specs/VCP_PAPER_SPEC_CONTENT.md", names)
        self.assertNotIn("docs/semantics/VCP_SEMANTICS_CSM1.md", names)

    def test_no_retired_bracket_notation(self) -> None:
        for path, text in self.documents.items():
            body = text.split("\n## Changelog", 1)[0]
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertIsNone(re.search(r"(?:PERSONA|SCOPE|REQUIRE|PROOF)\[", body))

    def test_versioned_tokens_use_listed_prefixes(self) -> None:
        token = re.compile(
            r"(?<![\w.@/-])([a-z][a-z0-9-]*(?:\.[a-z0-9-]+)+)@(?:[0-9^~]|latest|canary)"
        )
        for path, text in self.documents.items():
            for match in token.finditer(text):
                with self.subTest(path=path.relative_to(ROOT).as_posix(), token=match.group(1)):
                    self.assertIn(match.group(1).split(".")[0], PREFIXES)

    def test_prose_spells_csm_1_with_a_hyphen(self) -> None:
        bare = re.compile(r"(?<![\w/.#-])CSM1(?![\w-])")
        for path, text in self.documents.items():
            if path.suffix != ".md":
                continue
            in_fence = False
            for number, line in enumerate(text.splitlines(), start=1):
                if re.match(r"^\s{0,3}(```|~~~)", line):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    continue
                prose = re.sub(r"`[^`]*`|\]\([^)]*\)", "", line)
                with self.subTest(path=path.relative_to(ROOT).as_posix(), line=number):
                    self.assertIsNone(bare.search(prose))

    def test_mcp_initialize_mentions_carry_the_revision_caveat(self) -> None:
        for path, text in self.documents.items():
            if "MCP" in text and re.search(r"`initialize`", text):
                with self.subTest(path=path.relative_to(ROOT).as_posix()):
                    self.assertIn("2025-11-25", text)


if __name__ == "__main__":
    unittest.main()
