from __future__ import annotations

import base64
import copy
import json
import sys
import unittest
from pathlib import Path

from jsonschema.validators import validator_for

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from jsonschema_formats import strict_format_checker

ED25519_SIGNATURE = "base64:" + base64.b64encode(bytes(64)).decode("ascii")
ED448_SIGNATURE = "base64:" + base64.b64encode(bytes(114)).decode("ascii")
ED448_PUBLIC_KEY = "ed448:" + base64.b64encode(bytes(57)).decode("ascii")

from protocol_contracts import (
    canonical_csm1,
    parse_compact_csm1,
    parse_csm1,
    parse_minor,
    valid_extension_ids,
    validate_csm1_document,
    validate_handshake_exchange,
    validate_handshake_message,
    validate_manifest_document,
)


def load_json(relative: str) -> object:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def schema_validator(name: str):
    schema = load_json(f"schemas/{name}.schema.json")
    validator_class = validator_for(schema)
    validator_class.check_schema(schema)
    return validator_class(schema, format_checker=strict_format_checker())


class CSM1ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = schema_validator("vcp-semantics-csm1")

    def test_nano_micro_parse_and_canonicalization_matrix(self) -> None:
        cases = {
            "N0": "N0",
            "N5@latest": "N5@latest",
            "N5+F+E:TEAM@1.2.3": "N5+E+F:TEAM@1.2.3",
            "C3:ACME": "C3:ACME",
            "C3+W+O:ACME": "C3+O+W:ACME",
        }
        for wire, canonical in cases.items():
            with self.subTest(wire=wire):
                parsed = parse_csm1(wire)
                self.assertEqual(canonical_csm1(parsed), canonical)
                document = {"code": wire, **parsed, "canonical": canonical}
                self.assertFalse(list(self.validator.iter_errors(document)))
                self.assertEqual(validate_csm1_document(document), [])

    def test_nano_micro_rejects_malformed_and_ambiguous_codes(self) -> None:
        cases = (
            "",
            "N6",
            " N5",
            "N5 ",
            "C3",
            "N5+F+F",
            "N5+F+A",
            "N5+V+A",
            "N5+H+A",
            "N5:TEAM+F",
            "N5+F:toolongxx",
            "N5@01.2.3",
            "N5@1.2",
            "N5" + "+E" * 23,
        )
        for wire in cases:
            with self.subTest(wire=wire), self.assertRaises(ValueError):
                parse_csm1(wire)

    def test_compact_grammar_and_semantic_parity(self) -> None:
        wire = "CS1|nanny|5|family.safe.guide@1.2.3:CORE|F,E"
        parsed = parse_compact_csm1(wire)
        self.assertEqual(parsed["persona"], "N")
        self.assertEqual(parsed["scopes"], ["F", "E"])
        document = load_json("schemas/examples/vcp-semantics-csm1.valid.json")
        self.assertFalse(list(self.validator.iter_errors(document)))
        self.assertEqual(validate_csm1_document(document), [])

        malformed = (
            "CS1|nanny|5|family.safe.guide|",
            "CS1|nanny|5|family.safe.guide|F,F",
            "CS1|nanny|5|family.safe.guide|F,A",
            "CS1|Nanny|5|family.safe.guide|F",
            "CS1|nanny|5|family.guide|F",
            "CS1|nanny|5|a.b.c.d.e.f.g.h.i.j.k|F",
            "CS1|nanny|5|Family.safe.guide|F",
            "CS1|nanny|5|family.safe.guide@01.2.3|F",
        )
        for candidate in malformed:
            with self.subTest(candidate=candidate), self.assertRaises(ValueError):
                parse_compact_csm1(candidate)

    def test_document_cross_fields_cannot_contradict_wire_code(self) -> None:
        base = load_json("schemas/examples/vcp-semantics-csm1.valid.json")
        mutations = {
            "persona": "Z",
            "persona_name": "sentinel",
            "adherence": 4,
            "scopes": ["E", "F"],
            "namespace": "TEAM",
            "version": "1.0.0",
            "canonical": "N5+F+E",
            "compact": "CS1|sentinel|5|family.safe.guide|F,E",
        }
        for field, value in mutations.items():
            with self.subTest(field=field):
                document = copy.deepcopy(base)
                document[field] = value
                self.assertTrue(validate_csm1_document(document))


class HandshakeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = schema_validator("vcp-capability-handshake")
        cls.hello = load_json("schemas/examples/vcp-capability-handshake.valid-hello.json")
        cls.ack = load_json("schemas/examples/vcp-capability-handshake.valid-ack.json")

    def test_wire_shape_bounds_and_forward_compatibility(self) -> None:
        self.assertFalse(list(self.validator.iter_errors(self.hello)))
        self.assertFalse(list(self.validator.iter_errors(self.ack)))
        self.assertEqual(validate_handshake_message(self.hello), [])
        self.assertEqual(parse_minor("999999999.999999999"), (999999999, 999999999))

        cases = []
        duplicate = copy.deepcopy(self.hello)
        duplicate["extensions"] = ["VCP-X-Personal", "VCP-X-Personal"]
        cases.append(duplicate)
        wrong_case = copy.deepcopy(self.hello)
        wrong_case["type"] = "VCP-Hello"
        cases.append(wrong_case)
        leading_zero = copy.deepcopy(self.hello)
        leading_zero["version"] = "03.1"
        cases.append(leading_zero)
        too_wide = copy.deepcopy(self.hello)
        too_wide["version"] = "1000000000.0"
        cases.append(too_wide)
        empty_client = copy.deepcopy(self.hello)
        empty_client["client_id"] = ""
        cases.append(empty_client)
        too_many = copy.deepcopy(self.hello)
        too_many["extensions"] = [f"invalid-{index}" for index in range(257)]
        cases.append(too_many)
        for document in cases:
            with self.subTest(document=document):
                self.assertTrue(list(self.validator.iter_errors(document)))

        bounded = copy.deepcopy(self.hello)
        bounded["extensions"] = [f"invalid-{index}" for index in range(256)]
        self.assertFalse(list(self.validator.iter_errors(bounded)))

    def test_invalid_extension_ids_are_filtered_without_rewriting_valid_ids(self) -> None:
        values = [
            "VCP-X-Personal",
            "bad",
            "VCP-X-Relational",
            "VCP-X-" + "x" * 123,
            7,
        ]
        self.assertEqual(
            valid_extension_ids(values),
            ["VCP-X-Personal", "VCP-X-Relational"],
        )
        self.assertEqual(valid_extension_ids("VCP-X-Personal"), [])

    def test_success_exchange_invariants(self) -> None:
        hello = copy.deepcopy(self.hello)
        hello["extensions"] = [
            "VCP-X-Personal",
            "invalid-extension",
            "VCP-X-Relational",
        ]
        self.assertEqual(validate_handshake_exchange(hello, self.ack), [])

        mutations = []
        response = copy.deepcopy(self.ack)
        response["version"] = "4.0"
        mutations.append((hello, response, "outside"))
        response = copy.deepcopy(self.ack)
        response["unsupported"] = ["VCP-X-Personal", "VCP-X-Relational"]
        mutations.append((hello, response, "overlap"))
        response = copy.deepcopy(self.ack)
        response["unsupported"] = []
        mutations.append((hello, response, "partition"))
        response = copy.deepcopy(self.ack)
        response["capabilities"]["VCP-X-Relational"] = {}
        mutations.append((hello, response, "not supported"))
        wrong_order = copy.deepcopy(self.ack)
        mutations.append((wrong_order, hello, "vcp-hello then vcp-ack"))
        for request, response, expected in mutations:
            with self.subTest(expected=expected):
                self.assertTrue(
                    any(
                        expected in error
                        for error in validate_handshake_exchange(request, response)
                    )
                )

    def test_inverted_version_range_is_semantically_rejected(self) -> None:
        hello = copy.deepcopy(self.hello)
        hello["version"] = "2.0"
        hello["min_version"] = "3.0"
        self.assertFalse(list(self.validator.iter_errors(hello)))
        self.assertEqual(validate_handshake_message(hello), ["min_version exceeds version"])
        for value in (None, 3, "1", "1.0.0", "01.0", "1.-1"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_minor(value)

    def test_missing_extension_dependencies_require_degraded_capabilities(self) -> None:
        hello = copy.deepcopy(self.hello)
        hello["extensions"] = ["VCP-X-Torch", "VCP-X-Intent"]
        response = copy.deepcopy(self.ack)
        response["supported"] = ["VCP-X-Torch", "VCP-X-Intent"]
        response["unsupported"] = []
        response["capabilities"] = {
            "VCP-X-Torch": {},
            "VCP-X-Intent": {},
        }
        errors = validate_handshake_exchange(hello, response)
        self.assertTrue(any("Torch without Relational" in error for error in errors))
        self.assertTrue(any("Intent without Personal" in error for error in errors))

        response["capabilities"] = {
            "VCP-X-Torch": {"degraded": True},
            "VCP-X-Intent": {"personal_signals": False},
        }
        self.assertEqual(validate_handshake_exchange(hello, response), [])


class AdaptationAndManifestContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.context_validator = schema_validator("vcp-adaptation-context")
        cls.manifest_validator = schema_validator("vcp-manifest-v1")

    def test_context_size_structure_and_relationship_boundaries(self) -> None:
        accepted = (
            {"context": "x" * 8192},
            {"context": "x", "parsed": {"situational": {"relationship": ["friend"]}}},
            {
                "context": "x",
                "parsed": {
                    "situational": {"relationship": [":therapeutic"]},
                    "personal": {"cognitive_state": {"value": "deep_focus", "intensity": 5}},
                },
            },
        )
        for document in accepted:
            with self.subTest(document=document):
                self.assertFalse(list(self.context_validator.iter_errors(document)))

        rejected = (
            {"context": ""},
            {"context": "x" * 8193},
            {"context": "x y"},
            {"context": "x\u0000y"},
            {"context": "x", "unknown": True},
            {
                "context": "x",
                "parsed": {"situational": {"relationship": ["family:caregiving"]}},
            },
            {
                "context": "x",
                "parsed": {"situational": {"time": ["x"] * 17}},
            },
            {
                "context": "x",
                "parsed": {"situational": {"time": ["x", "x"]}},
            },
            {
                "context": "x",
                "parsed": {"personal": {"cognitive_state": {"value": "Upper"}}},
            },
        )
        for document in rejected:
            with self.subTest(document=document):
                self.assertTrue(list(self.context_validator.iter_errors(document)))

    def test_manifest_multisig_threshold_and_signer_identity(self) -> None:
        valid = load_json("schemas/examples/vcp-manifest-v1.valid-multisig.json")
        self.assertFalse(list(self.manifest_validator.iter_errors(valid)))
        self.assertEqual(validate_manifest_document(valid), [])

        threshold = copy.deepcopy(valid)
        threshold["signature"]["threshold"] = 3
        self.assertFalse(list(self.manifest_validator.iter_errors(threshold)))
        self.assertIn(
            "multisig threshold exceeds signer count",
            validate_manifest_document(threshold),
        )
        duplicate = copy.deepcopy(valid)
        duplicate["signature"]["signers"][1]["id"] = "signer-a"
        self.assertFalse(list(self.manifest_validator.iter_errors(duplicate)))
        self.assertIn(
            "multisig signer identifiers are not unique",
            validate_manifest_document(duplicate),
        )

    def test_manifest_signature_shape_is_conditionally_complete(self) -> None:
        ordinary = load_json("schemas/examples/vcp-manifest-v1.valid.json")
        self.assertFalse(list(self.manifest_validator.iter_errors(ordinary)))
        with_signers = copy.deepcopy(ordinary)
        with_signers["signature"]["threshold"] = 1
        with_signers["signature"]["signers"] = [
            {"id": "signer-a", "signature": ED25519_SIGNATURE}
        ]
        self.assertTrue(list(self.manifest_validator.iter_errors(with_signers)))

        unsigned = copy.deepcopy(ordinary)
        unsigned["signature"]["signed_fields"].remove("budget")
        self.assertTrue(list(self.manifest_validator.iter_errors(unsigned)))

        malformed = copy.deepcopy(ordinary)
        malformed["signature"]["value"] = "base64:" + "A" * 85 + "B=="
        self.assertTrue(list(self.manifest_validator.iter_errors(malformed)))

        ed448 = copy.deepcopy(ordinary)
        ed448["signature"]["algorithm"] = "ed448"
        ed448["signature"]["value"] = ED448_SIGNATURE
        ed448["issuer"]["public_key"] = ED448_PUBLIC_KEY
        self.assertFalse(list(self.manifest_validator.iter_errors(ed448)))
        ed448["issuer"]["public_key"] = ordinary["issuer"]["public_key"]
        self.assertTrue(list(self.manifest_validator.iter_errors(ed448)))

        multisig = load_json("schemas/examples/vcp-manifest-v1.valid-multisig.json")
        self.assertNotIn("value", multisig["signature"])
        with_value = copy.deepcopy(multisig)
        with_value["signature"]["value"] = ED25519_SIGNATURE
        self.assertTrue(list(self.manifest_validator.iter_errors(with_value)))

        bounded = copy.deepcopy(ordinary)
        bounded["scope"] = {"purposes": [f"purpose-{index}" for index in range(128)]}
        self.assertFalse(list(self.manifest_validator.iter_errors(bounded)))
        bounded["scope"]["purposes"].append("overflow")
        self.assertTrue(list(self.manifest_validator.iter_errors(bounded)))

        noncanonical_csm1 = copy.deepcopy(ordinary)
        noncanonical_csm1["metadata"] = {"csm1": "N5@01.2.3"}
        self.assertTrue(list(self.manifest_validator.iter_errors(noncanonical_csm1)))


class MessagingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = schema_validator("vcp-messaging-v1.2")
        cls.valid = load_json("schemas/examples/vcp-messaging-v1.2.valid.json")

    def test_envelope_crypto_utc_and_collection_bounds(self) -> None:
        self.assertFalse(list(self.validator.iter_errors(self.valid)))

        at_context_limit = copy.deepcopy(self.valid)
        at_context_limit["payload"]["context"] = "x" * 8192
        self.assertFalse(list(self.validator.iter_errors(at_context_limit)))

        announce = copy.deepcopy(self.valid)
        announce["type"] = "constitution_announce"
        announce["payload"] = {
            "constitution_ref": "creed://creed.space/family.safe.guide@1.2.0",
            "manifest_hash": "sha256:" + "a" * 64,
            "scope": {
                "purposes": [f"purpose-{index}" for index in range(50)]
            },
        }
        self.assertFalse(list(self.validator.iter_errors(announce)))

        constraints = copy.deepcopy(self.valid)
        constraints["type"] = "constraint_propagate"
        constraints["payload"] = {
            "constraints": [
                {
                    "type": f"constraint-{index}",
                    "value": index,
                    "source_constitution_ref": (
                        "creed://creed.space/family.safe.guide@1.2.0"
                    ),
                }
                for index in range(100)
            ],
            "propagation_mode": "merge",
        }
        self.assertFalse(list(self.validator.iter_errors(constraints)))

        rejected = []
        over_context = copy.deepcopy(at_context_limit)
        over_context["payload"]["context"] += "x"
        rejected.append(over_context)
        offset_timestamp = copy.deepcopy(self.valid)
        offset_timestamp["timestamp"] = "2026-02-15T10:30:00+00:00"
        rejected.append(offset_timestamp)
        bad_padding = copy.deepcopy(self.valid)
        bad_padding["signature"] = "base64:" + "A" * 85 + "B=="
        rejected.append(bad_padding)
        duplicate_scope = copy.deepcopy(announce)
        duplicate_scope["payload"]["scope"]["purposes"] = ["same", "same"]
        rejected.append(duplicate_scope)
        over_constraints = copy.deepcopy(constraints)
        over_constraints["payload"]["constraints"].append(
            {
                "type": "overflow",
                "value": 129,
                "source_constitution_ref": (
                    "creed://creed.space/family.safe.guide@1.2.0"
                ),
            }
        )
        rejected.append(over_constraints)
        for document in rejected:
            with self.subTest(document_type=document["type"]):
                self.assertTrue(list(self.validator.iter_errors(document)))


if __name__ == "__main__":
    unittest.main()
