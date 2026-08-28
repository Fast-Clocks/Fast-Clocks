"""Sovereign Adapter — OPTIONAL integrity receipts for selected milestones.

Aligned to the APN "Sovereign Engine — System Definition v1.0 (23 Jul 2026)".
This is deliberately NOT a dependency: File Brain works fully without it.

What this adapter does, faithful to the Engine's rules:
  * Smart Evidence Envelope — a standard SHA-256 fingerprint plus *selected*
    context. No proprietary "smart hash" algorithm; the value is the bound,
    signed context, not a secret primitive.
  * Two-envelope model — a PRIVATE manifest (full detail, kept local) and a
    PUBLIC attestation manifest (purpose-selected fields only). The private
    manifest's digest is bound into the public one. Sensitive fields
    (filenames, paths, notes) NEVER appear in the public manifest.
  * Canonical JSON (sorted keys, compact) — the same canonicalisation the
    Engine's `sign-manifest` expects, so the public manifest is Ed25519-
    signable later with no translation.
  * Scope of attestation — states exactly what a seal proves and does not.

Honesty boundary (matches the Engine's "buyer-safe promise today"): a seal here
is an INTEGRITY receipt (tamper-evidence over the canonical bytes). It is NOT a
cryptographic signature and NOT proof of truth, ownership or legality. No key is
created or required; nothing contacts a network. When the external Sovereign
Engine issuing key is available, it signs THIS public manifest unchanged.
"""

from __future__ import annotations

import hashlib
import json
import time

MANIFEST_VERSION = "APN-VR/0.2"

# Fields that may appear in a PUBLIC attestation manifest. Everything else in
# the private manifest is withheld unless a field is explicitly released.
PUBLIC_ALLOWLIST = {
    "manifest_version", "kind", "subject_ref", "artefact_sha256", "byte_size",
    "mime_type", "source_time", "sealed_at", "scope", "private_manifest_sha256",
    "signature", "signed", "key_id", "algorithm",
}

SCOPE_STATEMENT = {
    "proves": ("the issuing system sealed a defined byte sequence and declared "
               "context under a stated process at a stated time"),
    "does_not_prove": ("truth, ownership, legality, regulatory compliance, "
                       "safety, authorship beyond the asserted identity process, "
                       "or the accuracy of untrusted metadata"),
}


def canonical_bytes(obj):
    """Canonical JSON: sorted keys, compact separators, UTF-8."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def build_envelope(artefact_sha256, *, byte_size=None, mime_type=None,
                   source_time=None, subject_ref=None, private_context=None):
    """Build a Smart Evidence Envelope split into private + public manifests.

    private_context: dict of full/sensitive detail (filenames, notes, actor…).
    Returns (private_manifest, public_manifest).
    """
    private_manifest = {
        "manifest_version": MANIFEST_VERSION,
        "artefact_sha256": artefact_sha256,
        "byte_size": byte_size,
        "mime_type": mime_type,
        "source_time": source_time,
        "subject_ref": subject_ref,
        "context": private_context or {},
    }
    private_digest = hashlib.sha256(canonical_bytes(private_manifest)).hexdigest()
    public_manifest = {
        "manifest_version": MANIFEST_VERSION,
        "subject_ref": subject_ref,
        "artefact_sha256": artefact_sha256,
        "byte_size": byte_size,
        "mime_type": mime_type,
        "source_time": source_time,
        "scope": SCOPE_STATEMENT,
        "private_manifest_sha256": private_digest,
        "signature": None,
        "signed": False,
        "key_id": None,
        "algorithm": "Ed25519",  # the algorithm the external issuer WILL use
    }
    return private_manifest, public_manifest


def public_leak_check(public_manifest):
    """Return any keys in the public manifest outside the release allowlist."""
    return [k for k in public_manifest if k not in PUBLIC_ALLOWLIST]


def seal(store, kind, ref, *, artefact_sha256, byte_size=None, mime_type=None,
         source_time=None, private_context=None):
    """Create a two-envelope integrity receipt for a milestone and queue it."""
    subject_ref = f"{kind}:{ref}"
    private_manifest, public_manifest = build_envelope(
        artefact_sha256, byte_size=byte_size, mime_type=mime_type,
        source_time=source_time, subject_ref=subject_ref, private_context=private_context)
    public_manifest = {"kind": kind, "sealed_at": time.time(), **public_manifest}
    leaks = public_leak_check(public_manifest)
    if leaks:  # never emit a public manifest carrying private fields
        raise ValueError(f"public manifest would leak fields: {leaks}")
    integrity = hashlib.sha256(canonical_bytes(public_manifest)).hexdigest()
    receipt = {"public_manifest": public_manifest,
               "private_manifest": private_manifest,
               "integrity_sha256": integrity, "signed": False, "queued": True}
    store.conn.execute(
        "INSERT INTO ingest_receipts(sha256,path,actor,session,state,created_at) VALUES(?,?,?,?,?,?)",
        (integrity, f"seal:{subject_ref}", "sovereign-adapter", "", "SEALED", time.time()))
    store.conn.commit()
    store.audit("sovereign-adapter", "seal", {"kind": kind, "ref": ref, "integrity": integrity})
    return receipt


def verify_seal(receipt):
    """Recompute integrity and confirm the public manifest carries no private
    fields. Returns ok + the checks performed."""
    pub = receipt["public_manifest"]
    recomputed = hashlib.sha256(canonical_bytes(pub)).hexdigest()
    leaks = public_leak_check(pub)
    return {
        "ok": recomputed == receipt.get("integrity_sha256") and not leaks,
        "integrity_matches": recomputed == receipt.get("integrity_sha256"),
        "no_public_leak": not leaks,
        "leaked_fields": leaks,
        "signed": pub.get("signed", False),
        "recomputed": recomputed,
    }
