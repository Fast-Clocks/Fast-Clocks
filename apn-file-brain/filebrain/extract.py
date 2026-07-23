"""Ordered, typed extraction with provenance.

Deterministic (no model required) heuristics that turn text into typed units:
page/section, paragraph, sentence, fact, idea, decision, question, task and
project — each carrying its source coordinate (character offsets) so every
extracted unit is traceable back to exactly where it came from.

These are *extractions*, labelled DIRECT (explicitly present in the source).
Nothing here invents content; a later phase may add SYNTHESIS records that are
clearly marked as generated. Confidence is a coarse, honest signal.
"""

from __future__ import annotations

import re

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])")

_DECISION = re.compile(r"(?i)\b(we (?:will|have|decided)|decided|decision|chosen|"
                       r"selected|approved|agreed|going with|locked)\b")
_TASK = re.compile(r"(?i)^(?:\s*[-*]\s*\[[ xX]\]|\s*(?:todo|action|next|task)\s*[:\-])")
_IDEA = re.compile(r"(?i)\b(idea|concept|what if|could we|proposal|imagine|"
                   r"we could|might)\b")
_PROJECT = re.compile(r"(?i)\b(project|build|system|machine|engine|platform|app)\b")


def sentences(block, base_offset):
    """Yield (sentence_text, char_start, char_end) within block."""
    pos = 0
    for chunk in _SENT_SPLIT.split(block):
        chunk = chunk.strip()
        if not chunk:
            continue
        start = block.find(chunk, pos)
        if start < 0:
            start = pos
        end = start + len(chunk)
        pos = end
        yield chunk, base_offset + start, base_offset + end


def _classify(sentence):
    s = sentence.strip()
    low = s.lower()
    if _TASK.match(s):
        return "task", 0.8
    if s.endswith("?") or re.match(r"(?i)^(who|what|why|how|when|where|should|can|is|are|do|does)\b", low):
        return "question", 0.7
    if _DECISION.search(low):
        return "decision", 0.75
    if _IDEA.search(low):
        return "idea", 0.6
    # a plain declarative clause is treated as a fact/assertion
    if re.search(r"\b(is|are|was|were|will|has|have|had|provides|uses|stores|"
                 r"produces|requires|must|should)\b", low) and len(s.split()) >= 4:
        return "fact", 0.55
    return None, 0.0


def extract_records(raw):
    """Return list of (part_idx, rtype, text, char_start, char_end, confidence, evidence)."""
    out = []
    part_idx = 0
    offset = 0
    for block in re.split(r"\n\s*\n", raw):
        stripped = block.strip()
        if not stripped:
            offset += len(block) + 2
            continue
        start = raw.find(stripped, offset)
        if start < 0:
            start = offset
        # heading / project detection at the block level
        is_heading = bool(re.match(r"^#{1,6}\s|^[A-Z0-9 \-—:]{6,}$", stripped))
        if is_heading:
            rtype = "project" if _PROJECT.search(stripped) else "section"
            out.append((part_idx, rtype, stripped[:400], start, start + len(stripped),
                        0.6, "DIRECT"))
        else:
            for sent, cs, ce in sentences(stripped, start):
                rtype, conf = _classify(sent)
                if rtype:
                    out.append((part_idx, rtype, sent[:1000], cs, ce, conf, "DIRECT"))
        part_idx += 1
        offset = start + len(stripped)
    return out
