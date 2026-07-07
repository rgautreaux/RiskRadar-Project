#!/usr/bin/env python3
"""Simple validator for docs/PARITY_MATRIX.md ensuring core entries exist."""
import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--matrix",
        type=Path,
        default=Path("docs/PARITY_MATRIX.md"),
        help="Path to parity matrix markdown file (default: docs/PARITY_MATRIX.md)",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    matrix = args.matrix if args.matrix.is_absolute() else repo_root / args.matrix
    if not matrix.exists():
        print("PARITY_MATRIX.md not found", file=sys.stderr)
        return 2
    text = matrix.read_text(encoding="utf-8")
    required = ["/api/v1/trips/{id}/safety", "/api/v1/trips/{id}/places", "/api/v1/trips/{id}/lodging"]
    missing = [r for r in required if r not in text and r.replace('{id}','{trip_id}') not in text]
    if missing:
        print("Missing parity entries:", missing, file=sys.stderr)
        return 3
    print("Parity matrix validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
