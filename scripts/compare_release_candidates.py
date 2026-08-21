#!/usr/bin/env python3
"""Compare two specification candidate directories byte for byte."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from validation_utils import regular_file_snapshots_below, sha256_regular

MAX_FILES = 10_000
MAX_FILE_BYTES = 50 * 1024 * 1024
MAX_TOTAL_BYTES = 1024 * 1024 * 1024


def inventory(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    snapshots = regular_file_snapshots_below(
        root,
        max_files=MAX_FILES,
        max_file_bytes=MAX_FILE_BYTES,
        max_total_bytes=MAX_TOTAL_BYTES,
        purpose="candidate",
    )
    for snapshot in snapshots:
        path = snapshot.path
        digest, _ = sha256_regular(
            path,
            max_bytes=MAX_FILE_BYTES,
            root=root,
            purpose="candidate file",
            expected=snapshot,
        )
        result[path.relative_to(root).as_posix()] = digest
    if not result:
        raise ValueError(f"candidate directory contains no files: {root}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("first", type=Path)
    parser.add_argument("second", type=Path)
    args = parser.parse_args()
    try:
        first = inventory(args.first)
        second = inventory(args.second)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    changed = sorted(
        name for name in first.keys() & second if first[name] != second[name]
    )
    missing = sorted(set(first) - set(second))
    unexpected = sorted(set(second) - set(first))
    if changed or missing or unexpected:
        print(f"digest mismatches: {changed}", file=sys.stderr)
        print(f"missing from second: {missing}", file=sys.stderr)
        print(f"unexpected in second: {unexpected}", file=sys.stderr)
        return 1
    print(f"Spec reproducibility comparison passed for {len(first)} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
