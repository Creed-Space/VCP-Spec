from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path
from unittest import mock

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_document_inventory
import generate_requirement_registry
import validate_repo
from jsonschema_formats import is_rfc3339_date_time, strict_format_checker
from validate_repo import (
    DuplicateKeyError,
    Problems,
    UniqueKeyLoader,
    _resolve_local_schema_reference,
    has_unclosed_fence,
    json_files,
    load_json,
    markdown_anchors,
    protocol_prose_errors,
    repository_source_files,
    strip_fenced_code,
    validate_docx,
    validate_embedded_schema_examples,
    validate_schema_references,
    validate_structure_bounds,
    validate_yaml,
)


class StrictDataLoadingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def load(self, text: str):
        path = self.root / "input.json"
        path.write_text(text, encoding="utf-8")
        problems = Problems()
        with mock.patch.object(validate_repo, "ROOT", self.root):
            result = load_json(path, problems)
        return result, problems.items

    def test_json_rejects_lexical_ambiguity_and_nonfinite_numbers(self) -> None:
        cases = (
            ('{"a": 1, "a": 2}', "duplicate JSON object key"),
            ('{"a": 1, "\\u0061": 2}', "duplicate JSON object key"),
            ('{"value": NaN}', "non-finite JSON number"),
            ('{"value": Infinity}', "non-finite JSON number"),
            ('{"value": -Infinity}', "non-finite JSON number"),
            ('{"value": 01}', "not valid bounded UTF-8 JSON"),
        )
        for text, expected in cases:
            with self.subTest(text=text):
                result, errors = self.load(text)
                self.assertIsNone(result)
                self.assertTrue(any(expected in error for error in errors))

        result, errors = self.load('{"a": 1, "nested": [true, null]}')
        self.assertEqual(result, {"a": 1, "nested": [True, None]})
        self.assertEqual(errors, [])

    def test_datetime_format_is_semantic_without_optional_checker_extras(self) -> None:
        accepted = (
            "2024-02-29T23:59:59Z",
            "2026-01-01t00:00:00.123456789z",
            "2026-01-01T00:00:00-00:00",
            "9999-12-31T23:59:59+23:59",
        )
        rejected = (
            "0000-01-01T00:00:00Z",
            "2026-02-29T00:00:00Z",
            "2026-01-01T24:00:00Z",
            "2026-01-01T23:59:60Z",
            "2026-01-01T00:00:00+24:00",
            "2026-01-01T00:00:00+00:60",
        )
        checker = strict_format_checker()
        self.assertIn("date-time", checker.checkers)
        for value in accepted:
            with self.subTest(value=value, expected="accepted"):
                self.assertTrue(is_rfc3339_date_time(value))
                self.assertTrue(checker.conforms(value, "date-time"))
        for value in rejected:
            with self.subTest(value=value, expected="rejected"):
                self.assertFalse(is_rfc3339_date_time(value))
                self.assertFalse(checker.conforms(value, "date-time"))

    def test_structure_depth_node_count_cycle_and_mapping_key_bounds(self) -> None:
        accepted: object = 0
        for _ in range(validate_repo.MAX_DATA_DEPTH - 1):
            accepted = [accepted]
        validate_structure_bounds(accepted)
        rejected = [accepted]
        with self.assertRaisesRegex(ValueError, "depth limit"):
            validate_structure_bounds(rejected)

        with (
            mock.patch.object(validate_repo, "MAX_DATA_NODES", 3),
            self.assertRaisesRegex(ValueError, "node limit"),
        ):
            validate_structure_bounds([1, 2, 3])

        cycle: list[object] = []
        cycle.append(cycle)
        with self.assertRaisesRegex(ValueError, "alias cycle"):
            validate_structure_bounds(cycle)
        with self.assertRaisesRegex(ValueError, "keys must be strings"):
            validate_structure_bounds({1: "value"})

        shared = ["value"]
        validate_structure_bounds({"a": shared, "b": shared})

    def test_yaml_rejects_duplicates_alias_exhaustion_depth_and_cycles(self) -> None:
        with self.assertRaises(DuplicateKeyError):
            validate_repo._unique_json_object([("a", 1), ("a", 2)])
        with self.assertRaises(yaml.YAMLError):
            yaml.load("a: 1\na: 2\n", Loader=UniqueKeyLoader)
        with (
            mock.patch.object(validate_repo, "MAX_YAML_ALIASES", 2),
            self.assertRaisesRegex(yaml.YAMLError, "alias limit"),
        ):
            yaml.load("a: &a [1]\nb: *a\nc: *a\nd: *a\n", Loader=UniqueKeyLoader)
        with (
            mock.patch.object(validate_repo, "MAX_DATA_DEPTH", 3),
            self.assertRaisesRegex(yaml.YAMLError, "construction limit"),
        ):
            yaml.load("a:\n  b:\n    c: 1\n", Loader=UniqueKeyLoader)
        loaded = yaml.load("a: &a [*a]\n", Loader=UniqueKeyLoader)
        with self.assertRaisesRegex(ValueError, "alias cycle"):
            validate_structure_bounds(loaded)

        workflow = yaml.load("on: [push]\nenabled: true\n", Loader=UniqueKeyLoader)
        self.assertEqual(workflow, {"on": ["push"], "enabled": True})
        validate_structure_bounds(workflow)

        (self.root / ".github" / "workflows").mkdir(parents=True)
        (self.root / ".github" / "workflows" / "ci.yml").write_text(
            "on: [push]\njobs: {}\n", encoding="utf-8"
        )
        (self.root / "node_modules" / "dependency").mkdir(parents=True)
        (self.root / "node_modules" / "dependency" / "invalid.yml").write_text(
            "broken: [\n", encoding="utf-8"
        )
        problems = Problems()
        with mock.patch.object(validate_repo, "ROOT", self.root):
            validate_yaml(problems)
            self.assertEqual(
                [path.relative_to(self.root).as_posix() for path in repository_source_files(".yml")],
                [".github/workflows/ci.yml"],
            )
            with (
                mock.patch.object(validate_repo, "MAX_REPOSITORY_FILES", 1),
                self.assertRaisesRegex(ValueError, "source inventory exceeds"),
            ):
                repository_source_files(".yml")
            with (
                mock.patch.object(validate_repo, "MAX_REPOSITORY_FILES", 1),
                mock.patch.object(validate_repo, "SCHEMA_ROOTS", (self.root,)),
                self.assertRaisesRegex(ValueError, "source inventory exceeds"),
            ):
                json_files()
        self.assertEqual(problems.items, [])

    def test_docx_validation_uses_one_immutable_bounded_package_read(self) -> None:
        def package_bytes(entries: list[tuple[str, str]]) -> bytes:
            output = io.BytesIO()
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                with zipfile.ZipFile(output, "w") as archive:
                    for name, content in entries:
                        archive.writestr(name, content)
            return output.getvalue()

        document = self.root / "document.docx"
        valid_package = package_bytes([("word/document.xml", "<document/>")])
        document.write_bytes(valid_package)
        outside = self.root / "outside.bin"
        outside.write_bytes(b"not a ZIP package")
        real_read = validate_repo.read_regular_bytes
        swapped = False

        def read_then_replace(*args, **kwargs):
            nonlocal swapped
            content = real_read(*args, **kwargs)
            document.unlink()
            document.symlink_to(outside)
            swapped = True
            return content

        problems = Problems()
        with (
            mock.patch.object(validate_repo, "ROOT", self.root),
            mock.patch.object(
                validate_repo, "repository_source_files", return_value=[document]
            ),
            mock.patch.object(
                validate_repo,
                "read_regular_bytes",
                side_effect=read_then_replace,
            ),
        ):
            validate_docx(problems)
        self.assertTrue(swapped)
        self.assertTrue(document.is_symlink())
        self.assertEqual(problems.items, [])

        document.unlink()
        cases = (
            ("member count", valid_package, "MAX_DOCX_MEMBERS", 0, "has 1 members"),
            (
                "duplicate names",
                package_bytes(
                    [
                        ("word/document.xml", "<document/>"),
                        ("word/document.xml", "<other/>"),
                    ]
                ),
                None,
                None,
                "duplicate ZIP member names",
            ),
            (
                "member size",
                valid_package,
                "MAX_DOCX_MEMBER_BYTES",
                0,
                "unsafe member size",
            ),
            (
                "required member",
                package_bytes([("other.xml", "<other/>")]),
                None,
                None,
                "missing word/document.xml",
            ),
            ("malformed ZIP", b"not a ZIP", None, None, "not a valid DOCX package"),
        )
        for name, content, bound, value, expected in cases:
            with self.subTest(name=name):
                document.write_bytes(content)
                problems = Problems()
                with contextlib.ExitStack() as stack:
                    stack.enter_context(mock.patch.object(validate_repo, "ROOT", self.root))
                    stack.enter_context(
                        mock.patch.object(
                            validate_repo,
                            "repository_source_files",
                            return_value=[document],
                        )
                    )
                    if bound is not None:
                        stack.enter_context(
                            mock.patch.object(validate_repo, bound, value)
                        )
                    validate_docx(problems)
                self.assertTrue(any(expected in error for error in problems.items))

        problems = Problems()
        with mock.patch.object(
            validate_repo,
            "repository_source_files",
            side_effect=OSError("inventory failed"),
        ):
            validate_docx(problems)
        self.assertTrue(any("inventory failed" in error for error in problems.items))


class SchemaAndMarkdownValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_schema_reference_resolution_covers_pointers_anchors_and_escapes(self) -> None:
        schema = {
            "$defs": {"a/b": {"type": "string"}},
            "properties": {"x": {"$anchor": "named"}},
        }
        accepted = ("#", "#/$defs/a~1b", "#named", "#/%24defs/a~1b")
        rejected = (
            "https://example.test/schema.json",
            "#/missing",
            "#/$defs/a~2b",
            "#unknown",
            "#/$defs/0",
        )
        for reference in accepted:
            with self.subTest(reference=reference):
                self.assertTrue(_resolve_local_schema_reference(schema, reference))
        for reference in rejected:
            with self.subTest(reference=reference):
                self.assertFalse(_resolve_local_schema_reference(schema, reference))

        path = self.root / "schema.json"
        problems = Problems()
        with mock.patch.object(validate_repo, "ROOT", self.root):
            validate_schema_references(
                path,
                {"$ref": "https://example.test/schema", "items": {"$ref": "#/bad"}},
                problems,
            )
        self.assertEqual(len(problems.items), 2)

    def test_nested_schema_examples_are_validated_against_their_subschema(self) -> None:
        path = self.root / "schema.json"
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "definitions": {
                "bounded": {
                    "type": "string",
                    "maxLength": 2,
                    "examples": ["ok", "too long"],
                }
            },
            "properties": {"value": {"$ref": "#/definitions/bounded"}},
        }
        path.write_text(json.dumps(schema), encoding="utf-8")
        problems = Problems()
        with mock.patch.object(validate_repo, "ROOT", self.root):
            validate_embedded_schema_examples(path, schema, problems)
        self.assertEqual(len(problems.items), 1)
        self.assertIn("examples/1 is invalid", problems.items[0])

    def test_fence_parser_does_not_strip_after_mismatched_or_short_closers(self) -> None:
        text = "before\n````python\ninside\n```\nstill inside\n````\nafter"
        self.assertFalse(has_unclosed_fence(text))
        self.assertEqual(strip_fenced_code(text), "before\nafter")
        self.assertTrue(has_unclosed_fence("before\n```\ninside"))
        self.assertTrue(has_unclosed_fence("~~~\ninside\n```"))

    def test_markdown_anchor_generation_handles_duplicates_markup_and_unicode(self) -> None:
        text = """# Hello, `World`!
## [Café](target.md)
## Café
<a id="explicit"></a>
```
# Hidden
```
"""
        self.assertEqual(
            markdown_anchors(text),
            {"hello-world", "café", "café-1", "explicit"},
        )

    def test_protocol_drift_rules_detect_removal_and_obsolete_reintroduction(self) -> None:
        documents = {
            name: (ROOT / name).read_text(encoding="utf-8")
            for name in validate_repo.PROTOCOL_PROSE_RULES
        }
        self.assertEqual(protocol_prose_errors(documents), [])
        mutated = dict(documents)
        name = "specs/VCP_ADAPTATION_v2.0.md"
        mutated[name] = mutated[name].replace(
            "Hook execution failures are fail-closed.",
            "The default behavior for hook failures is fail-open.",
        )
        errors = protocol_prose_errors(mutated)
        self.assertTrue(any("missing required" in error for error in errors))
        self.assertTrue(any("obsolete contract" in error for error in errors))
        identity = dict(documents)
        name = "specs/VCP_IDENTITY_v2.0.md"
        identity[name] = identity[name].replace(
            'token-path = segment 2*9("." segment)',
            'path    = segment *("/" segment)',
        )
        errors = protocol_prose_errors(identity)
        self.assertTrue(any("missing required" in error for error in errors))
        self.assertTrue(any("obsolete contract" in error for error in errors))
        missing = dict(documents)
        missing.pop("specs/VCP_MESSAGING_v2.0.md")
        self.assertTrue(any("source is missing" in error for error in protocol_prose_errors(missing)))


class GeneratorSafetyTests(unittest.TestCase):
    def test_document_inventory_is_globally_bounded_and_snapshot_consistent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, content in (("one", b"old!"), ("two", b"peer")):
                directory = root / name
                directory.mkdir()
                (directory / "item.md").write_bytes(content)
            with (
                mock.patch.object(generate_document_inventory, "ROOT", root),
                mock.patch.object(
                    generate_document_inventory, "ROOTS", ("one", "two")
                ),
                mock.patch.object(
                    generate_document_inventory, "EXTRA_ARTIFACTS", ()
                ),
            ):
                with (
                    mock.patch.object(
                        generate_document_inventory, "MAX_ARTIFACT_FILES", 1
                    ),
                    self.assertRaisesRegex(ValueError, "exceeds 0 files"),
                ):
                    generate_document_inventory.artifact_snapshots()
                snapshots = generate_document_inventory.artifact_snapshots()
                source = root / "one" / "item.md"
                source.unlink()
                source.write_bytes(b"new!")
                with self.assertRaisesRegex(ValueError, "changed since inventory"):
                    generate_document_inventory.classify(snapshots[0])


class RequirementRegistryParserTests(unittest.TestCase):
    def test_requirement_parser_ignores_fences_and_rejects_ambiguity(self) -> None:
        valid = """### VCP-OP-NEG-001: Negotiate

The peer MUST select a supported version.

```md
### VCP-OP-NEG-999: Not a requirement
The peer MUST ignore this example.
```

### VCP-OP-REV-002: Revoke

The verifier MUST reject a revoked credential.
"""
        records = generate_requirement_registry.requirements(valid)
        self.assertEqual([record["id"] for record in records], ["VCP-OP-NEG-001", "VCP-OP-REV-002"])

        duplicate = valid + "\n### VCP-OP-NEG-001: Duplicate\n\nThe peer MUST stop.\n"
        with self.assertRaisesRegex(ValueError, "duplicate"):
            generate_requirement_registry.requirements(duplicate)
        with self.assertRaisesRegex(ValueError, "unclosed Markdown fence"):
            generate_requirement_registry.requirements("```\n### VCP-OP-NEG-001: Hidden")
        with self.assertRaisesRegex(ValueError, "no stable requirement IDs"):
            generate_requirement_registry.requirements("ordinary prose")


if __name__ == "__main__":
    unittest.main()
