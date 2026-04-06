#!/usr/bin/env python3
"""Prefix local COPY source paths in a Dockerfile with a given directory.

Usage: prefix-copy.py <prefix> < input_dockerfile

For each COPY instruction that does not use --from=, prefix every source token
(all tokens except the last, which is the destination) that is a relative local
path (i.e. does not start with '-' or '/') with <prefix>/.

This allows the upstream tailrelay Dockerfile (which expects its own directory
as the build context) to work when the build context is the repo root.
"""

import sys
import re

prefix = sys.argv[1].rstrip("/") + "/"

for line in sys.stdin:
    if re.match(r"COPY ", line) and "--from=" not in line:
        parts = line.split()
        # parts[0] = 'COPY', parts[1:-1] = sources, parts[-1] = dest
        srcs = [prefix + p if not p.startswith(("-", "/")) else p for p in parts[1:-1]]
        line = "COPY " + " ".join(srcs) + " " + parts[-1] + "\n"
    sys.stdout.write(line)
