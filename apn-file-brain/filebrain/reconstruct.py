"""Scramble-and-rebuild proof — ordered decomposition with lossless rebuild.

This is Chris's own description made testable: break a file into ordered parts,
shuffle them, then rebuild strictly from the recorded order and prove the result
equals the original.

Honesty boundary (enforced by the spec): byte-for-byte reconstruction is proven
ONLY for text this function decomposes with explicit separators. It is NOT
claimed for PDF/DOCX/binary — those keep their original bytes as the source of
truth and are never reassembled from normalised fragments.
"""

from __future__ import annotations

import re


def decompose(raw):
    """Split text into ordered parts that can be perfectly reconstructed.

    Returns a list of dicts: {idx, type, text, sep}. The invariant is:
        "".join(p["text"] + p["sep"] for p in parts) == raw
    """
    parts = []
    # split into paragraphs while capturing the exact whitespace separators
    tokens = re.split(r"(\n\s*\n)", raw)
    idx = 0
    buf_text = None
    for tok in tokens:
        if tok is None:
            continue
        if re.fullmatch(r"\n\s*\n", tok):
            parts.append({"idx": idx, "type": _ptype(buf_text or ""),
                          "text": buf_text or "", "sep": tok})
            idx += 1
            buf_text = None
        else:
            buf_text = tok
    if buf_text is not None:
        parts.append({"idx": idx, "type": _ptype(buf_text), "text": buf_text, "sep": ""})
    return parts


def _ptype(block):
    s = block.strip()
    if not s:
        return "blank"
    if re.match(r"^#{1,6}\s|^[A-Z0-9 \-—:]{6,}$", s):
        return "heading"
    if re.match(r"^\s*[-*]\s", s):
        return "list"
    return "paragraph"


def rebuild(parts):
    """Reconstruct text from parts, strictly honouring recorded order."""
    ordered = sorted(parts, key=lambda p: p["idx"])
    return "".join(p["text"] + p["sep"] for p in ordered)


def prove(raw, shuffle_seed=1234):
    """Decompose, shuffle, rebuild-from-order, and diff against the original.

    Returns {ok, parts, byte_exact, rebuilt_len, original_len}.
    """
    import random
    parts = decompose(raw)
    scrambled = list(parts)
    random.Random(shuffle_seed).shuffle(scrambled)
    rebuilt = rebuild(scrambled)
    return {
        "ok": rebuilt == raw,
        "byte_exact": rebuilt == raw,
        "parts": len(parts),
        "rebuilt_len": len(rebuilt),
        "original_len": len(raw),
    }
