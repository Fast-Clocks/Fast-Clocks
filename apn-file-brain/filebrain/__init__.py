"""File Brain — a local-first, read-only evidence and knowledge index.

Phase-1 core: scan any roots on this machine, give every unique file a
SHA-256 content identity, keep one object with many occurrences, detect
duplicates, register artifacts through an ingress gate, checkpoint and
resume the newest meaningful work, and plan (never execute) cleanup.

Standard library only. Nothing here moves, renames, deletes, or uploads
your files. Originals are read, never written.
"""

__version__ = "0.1.0"
