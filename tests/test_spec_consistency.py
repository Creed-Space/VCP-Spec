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

    def test_every_enum_value_is_named_in_its_description(self) -> None:
        for name in ("system_context_values", "culture_values"):
            definition = self.definitions[name]
            for emoji in definition["enum"]:
                with self.subTest(definition=name, emoji=emoji):
                    self.assertIn(emoji, definition["description"])

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


if __name__ == "__main__":
    unittest.main()
