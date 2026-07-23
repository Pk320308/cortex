#!/usr/bin/env python3
"""
Aggregate Python requirements from all analyzers and produce a combined list.

Run: python3 scripts/aggregate_requirements.py
Produces: scripts/requirements-all.txt and prints a summary.
"""
import os
from collections import Counter

root = os.path.join(os.path.dirname(__file__), '..')
analyzers_dir = os.path.normpath(os.path.join(root, 'analyzers'))
out_path = os.path.join(os.path.dirname(__file__), 'requirements-all.txt')

pkgs = []
for dirpath, dirs, files in os.walk(analyzers_dir):
    for f in files:
        if f.lower() == 'requirements.txt':
            path = os.path.join(dirpath, f)
            try:
                with open(path, 'r', encoding='utf-8') as fh:
                    for line in fh:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        # ignore editable installs and local paths
                        if line.startswith('-e') or line.startswith('.') or line.startswith('/'):
                            continue
                        pkgs.append(line)
            except Exception:
                pass

unique = sorted(set(pkgs))
with open(out_path, 'w', encoding='utf-8') as out:
    out.write('\n'.join(unique))

print('Wrote', out_path)
cnt = Counter(pkgs)
print('\nTop packages (by occurrence in requirements files):')
for pkg, c in cnt.most_common(30):
    print(f'{pkg}: {c}')

print(f'Unique packages: {len(unique)}')
