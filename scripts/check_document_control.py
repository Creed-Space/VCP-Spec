#!/usr/bin/env python3
"""Run the canonical document-control validator without duplicating its policy."""

from __future__ import annotations

from validate_repo import Problems, validate_document_control


def main() -> int:
    problems = Problems()
    validate_document_control(problems)
    if problems.items:
        return problems.finish()
    print("Document control passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
