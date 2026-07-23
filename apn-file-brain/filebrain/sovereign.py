"""Sovereign Adapter — OPTIONAL integrity receipts for selected milestones.

This is deliberately not a dependency. File Brain works fully without it. When
you choose to `seal` a checkpoint or artifact, this produces a canonical receipt
and a SHA-256 integrity digest over that receipt, queued locally. If/when the
external Sovereign Engine (Ed25519 oracle) is available, the same canonical
bytes can be signed with no translation — but no signing key is created,
requested, or required here.

Honesty boundary: a seal here proves *integrity* of the receipt bytes
(tamper-evidence), NOT cryptographic authorship. It never contacts a network.
"""

from __future__ import annotations

import hashlib
import json
import time


def canonical_receipt(obj):
    """Canonical JSON: sorted keys, compact separators, UTF-8. Same shape the
    Sovereign Engine's sign-manifest expects, so it is signable later."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def seal(store, kind, ref, payload):
    """Create an integrity receipt for a milestone and queue it locally."""
    receipt = {
        "v": 1, "kind": kind, "ref": str(ref),
        "payload": payload, "at": time.time(),
    }
    canon = canonical_receipt(receipt)
    digest = hashlib.sha256(canon).hexdigest()
    receipt_out = {"receipt": receipt, "integrity_sha256": digest,
                   "signature": None, "signed": False, "queued": True}
    store.conn.execute(
        "INSERT INTO ingest_receipts(sha256,path,actor,session,state,created_at) VALUES(?,?,?,?,?,?)",
        (digest, f"seal:{kind}:{ref}", "sovereign-adapter", "", "SEALED", time.time()),
    )
    store.conn.commit()
    store.audit("sovereign-adapter", "seal", {"kind": kind, "ref": ref, "digest": digest})
    return receipt_out


def verify_seal(receipt_out):
    """Recompute the integrity digest and confirm the receipt is untampered."""
    canon = canonical_receipt(receipt_out["receipt"])
    digest = hashlib.sha256(canon).hexdigest()
    return {"ok": digest == receipt_out.get("integrity_sha256"),
            "recomputed": digest, "claimed": receipt_out.get("integrity_sha256"),
            "signed": receipt_out.get("signed", False)}
