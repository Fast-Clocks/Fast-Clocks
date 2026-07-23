"""Captain Anchor — portable verification and restoration checks.

Builds a SHA-256 manifest over a directory tree and verifies a tree against a
manifest, reporting matched / changed / missing / new. This is how the package
itself is verified, and how a Vault of canonical originals can be checked for
tampering later. Read-only: it computes hashes, it does not modify anything.
"""

from __future__ import annotations

import hashlib
import json
import os


def _sha(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb", buffering=0) as fh:
        while True:
            b = fh.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def build_manifest(root, out_path=None, exclude=(".git", "__pycache__", "dist")):
    root = os.path.realpath(root)
    entries = {}
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in exclude]
        for name in sorted(fn):
            full = os.path.join(dp, name)
            if os.path.islink(full):
                continue
            rel = os.path.relpath(full, root)
            entries[rel] = {"sha256": _sha(full), "size": os.path.getsize(full)}
    manifest = {"root": os.path.basename(root), "count": len(entries), "entries": entries}
    if out_path:
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=2, sort_keys=True)
    return manifest


def write_sha256sum(root, out_path, exclude=(".git", "__pycache__", "dist")):
    """Write a `sha256sum -c`-compatible file."""
    root = os.path.realpath(root)
    lines = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in exclude]
        for name in sorted(fn):
            full = os.path.join(dp, name)
            if os.path.islink(full) or os.path.realpath(full) == os.path.realpath(out_path):
                continue
            rel = os.path.relpath(full, root)
            lines.append(f"{_sha(full)}  {rel}")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return out_path


def verify(root, manifest):
    """Compare a tree to a manifest. Returns matched/changed/missing/new."""
    root = os.path.realpath(root)
    result = {"matched": [], "changed": [], "missing": [], "new": []}
    seen = set()
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in (".git", "__pycache__", "dist")]
        for name in fn:
            full = os.path.join(dp, name)
            if os.path.islink(full):
                continue
            rel = os.path.relpath(full, root)
            seen.add(rel)
            if rel not in manifest["entries"]:
                result["new"].append(rel)
            elif _sha(full) == manifest["entries"][rel]["sha256"]:
                result["matched"].append(rel)
            else:
                result["changed"].append(rel)
    for rel in manifest["entries"]:
        if rel not in seen:
            result["missing"].append(rel)
    return result
