"""Synthetic fixture estate generator — the only data the tests are built on.

Produces a small, self-contained, clearly-fake estate exercising: exact
duplicates, same-text-different-format, changed versions, conflicting facts, an
idea evolving across files, fake sensitive strings, an ordered document, an
empty file, a hidden file, an unsupported binary, and a symlink that must not
escape the root.
"""

from __future__ import annotations

import os

ORDERED_DOC = """# Sovereign Engine Overview

The Sovereign Engine signs a manifest and verifies it against a key the company
does not control. This is the substrate.

## Decisions

We decided to ship the pilot first. We chose customer-held keys for authorship.

## Open questions

How should the blind judge prove it did not leak? What is the payout split?

## Tasks

- [ ] Ship one clip-on
- [ ] Stand up the second node

The price is 49 dollars per seal. Contact test@example.com for the fake demo.
"""

IDEA_A = "Idea: a signed fragment can prove ownership across time.\n"
IDEA_B = "Idea: an escrow can pay a contributor when a puzzle completes.\n"
CONFLICT_1 = "The company ABN is 11 111 111 111 and the price is 49 dollars.\n"
CONFLICT_2 = "The company ABN is 22 222 222 222 and the price is 99 dollars.\n"
FAKE_SECRET = "api_key: sk-THISISAFAKEKEY000000000000\npassword: hunter2demo\n"


def build_estate(root):
    """Create the fixture tree under `root`. Returns a dict of key paths."""
    os.makedirs(root, exist_ok=True)
    paths = {}

    def w(rel, text):
        full = os.path.join(root, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as fh:
            fh.write(text)
        return full

    # exact duplicates: same bytes, different paths/names
    paths["dup_a"] = w("inbox/report.md", "# Report\n\nShared body text.\n")
    paths["dup_b"] = w("archive/report-copy.md", "# Report\n\nShared body text.\n")

    # text-equivalent: same normalised text, different bytes (trailing spaces)
    paths["teq_a"] = w("a/notes.txt", "line one\nline two\n")
    paths["teq_b"] = w("b/notes.txt", "line one   \nline two\n")

    # a versioned file (changed content later via mutate_version)
    paths["ver"] = w("work/spec.md", "# Spec\n\nVersion one body.\n")

    # conflicting facts
    paths["conf_a"] = w("legal/claim1.md", CONFLICT_1)
    paths["conf_b"] = w("legal/claim2.md", CONFLICT_2)

    # an idea evolving across files
    paths["idea_a"] = w("ideas/a.md", IDEA_A)
    paths["idea_b"] = w("ideas/b.md", IDEA_B)

    # ordered document with headings/paras/decisions/questions/tasks/numbers
    paths["ordered"] = w("docs/overview.md", ORDERED_DOC)

    # fake sensitive strings (clearly not real)
    paths["secret"] = w("secrets/leak.txt", FAKE_SECRET)

    # empty + hidden + unsupported binary
    paths["empty"] = w("edge/empty.txt", "")
    paths["hidden"] = w("edge/.hidden.md", "hidden but real\n")
    binp = os.path.join(root, "edge/blob.bin")
    with open(binp, "wb") as fh:
        fh.write(bytes(range(256)) * 4)
    paths["binary"] = binp

    # symlink that points OUTSIDE the root — must never be followed/escape
    link = os.path.join(root, "edge/escape_link")
    try:
        if not os.path.exists(link):
            os.symlink(os.path.dirname(root), link)
        paths["symlink"] = link
    except OSError:
        paths["symlink"] = None

    return paths


def mutate_version(path):
    """Change a file's content to simulate a new version."""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("# Spec\n\nVersion TWO body, materially changed.\n")
