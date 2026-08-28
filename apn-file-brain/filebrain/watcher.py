"""Filesystem watcher — DISABLED until explicitly enabled.

Portable, standard-library polling reconciler (no FSEvents dependency, so it
runs anywhere and in tests). It NEVER runs on its own: it is off until you turn
it on for a named root, and turning it off is reflected in status immediately.

It observes -> waits for stability -> hashes -> registers -> receipts. It never
moves, rewrites, or deletes a source file. It is honest about coverage: it can
only see approved roots it is running against, and it says so.
"""

from __future__ import annotations

import os
import time


def _ensure(store):
    store.conn.execute(
        "CREATE TABLE IF NOT EXISTS watcher_state("
        "root TEXT PRIMARY KEY, enabled INTEGER, last_reconcile REAL, seen INTEGER DEFAULT 0)")
    store.conn.commit()


def enable(store, root):
    _ensure(store)
    root = os.path.realpath(root)
    store.conn.execute(
        "INSERT INTO watcher_state(root,enabled,last_reconcile) VALUES(?,?,?) "
        "ON CONFLICT(root) DO UPDATE SET enabled=1", (root, 1, 0.0))
    store.conn.commit()
    store.audit("system", "watch_enable", {"root": root})
    return status(store)


def disable(store, root=None):
    _ensure(store)
    if root:
        store.conn.execute("UPDATE watcher_state SET enabled=0 WHERE root=?",
                          (os.path.realpath(root),))
    else:
        store.conn.execute("UPDATE watcher_state SET enabled=0")
    store.conn.commit()
    store.audit("system", "watch_disable", {"root": root})
    return status(store)


def status(store):
    _ensure(store)
    rows = store.conn.execute("SELECT root,enabled,last_reconcile,seen FROM watcher_state").fetchall()
    return {"watchers": [dict(r) for r in rows],
            "any_enabled": any(r["enabled"] for r in rows)}


def reconcile(store, root, actor="watcher", session=""):
    """One reconciliation pass: register durable artifacts under an ENABLED root.

    Coalesces transient/temp files. Registering the same stable content twice
    does not create a false new version (idempotent by SHA-256).
    """
    _ensure(store)
    root = os.path.realpath(root)
    st = store.conn.execute("SELECT enabled FROM watcher_state WHERE root=?", (root,)).fetchone()
    if not st or not st["enabled"]:
        return {"skipped": "watcher disabled for root", "root": root, "registered": 0}
    from .core import TRANSIENT_PATTERNS
    import re as _re
    registered = 0
    for dp, dn, fn in os.walk(root, followlinks=False):
        dn[:] = [d for d in dn if not d.startswith(".")]
        for name in fn:
            if any(rx.match(name) for rx in TRANSIENT_PATTERNS):
                continue
            path = os.path.join(dp, name)
            if os.path.islink(path):
                continue
            try:
                store.register(path, actor=actor, session=session, settle=0.0)
                registered += 1
            except Exception:
                continue
    store.conn.execute(
        "UPDATE watcher_state SET last_reconcile=?, seen=seen+? WHERE root=?",
        (time.time(), registered, root))
    store.conn.commit()
    return {"root": root, "registered": registered}
