#!/usr/bin/env python3
"""Fail when active Markdown documentation lacks machine-readable control fields."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "status",
    "normative-authority",
    "protocol-version",
    "last-reviewed",
    "owner",
    "evidence-boundary",
)
failures: list[str] = []
for path in sorted((ROOT / "docs").rglob("*.md")):
    text = path.read_text(encoding="utf-8")
    match = re.search(r"<!-- vcp-document-control\n(.*?)\n-->", text, re.DOTALL)
    if not match:
        failures.append(f"{path.relative_to(ROOT)}: missing document-control header")
        continue
    values = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if separator:
            values[key.strip()] = value.strip()
    for key in REQUIRED:
        if not values.get(key):
            failures.append(f"{path.relative_to(ROOT)}: missing {key}")
if failures:
    print("Document control failures:", file=sys.stderr)
    print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
    raise SystemExit(1)
print(
    f"Document control passed: {len(list((ROOT / 'docs').rglob('*.md')))} active Markdown files"
)
