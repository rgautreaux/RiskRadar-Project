#!/usr/bin/env python3
"""
Simple Markdown checker: scans docs/ and docs/expansion for trailing
whitespace and lines longer than 120 characters. Exits with 1 on issues.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
paths = list(ROOT.joinpath('docs').rglob('*.md')) + list(ROOT.joinpath('docs', 'expansion').rglob('*.md'))
issues = []
for p in set(paths):
    try:
        for i, line in enumerate(p.read_text(encoding='utf-8').splitlines(), start=1):
            if line.rstrip('\n') != line.rstrip():
                issues.append(f"{p}:{i}: trailing whitespace")
            if len(line) > 120:
                issues.append(f"{p}:{i}: line length {len(line)} > 120")
    except Exception as e:
        issues.append(f"{p}: unreadable ({e})")

if issues:
    print('Markdown check failed — issues found:')
    for it in issues:
        print(it)
    sys.exit(1)
else:
    print('Markdown check passed — no issues found.')
    sys.exit(0)
