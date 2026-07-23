"""Named views over the index. None of these move or alter a source file.

  * Whole Estate   — everything indexed, unique content vs occurrences.
  * New and Unseen — occurrences first seen in the most recent run.
  * Quick Capture  — the register/ingress receipts (things dropped in).
  * Resume Now     — the latest checkpoint and newest meaningful activity,
                     ordered by meaningful activity, NOT raw filesystem mtime.
"""

from __future__ import annotations


def whole_estate(store, limit=500):
    rows = store.conn.execute(
        "SELECT o.path,o.sha256,o.size,o.ext,o.mtime,"
        "(SELECT COUNT(*) FROM occurrences x WHERE x.sha256=o.sha256 AND x.present=1) AS occ "
        "FROM occurrences o WHERE o.present=1 ORDER BY o.size DESC LIMIT ?", (limit,)).fetchall()
    return [dict(r) for r in rows]


def new_and_unseen(store, limit=200):
    last = store.conn.execute("SELECT MAX(id) m FROM scan_runs").fetchone()["m"]
    if last is None:
        return []
    rows = store.conn.execute(
        "SELECT path,sha256,size,ext,last_seen_at FROM occurrences "
        "WHERE first_seen_run=? AND present=1 ORDER BY last_seen_at DESC LIMIT ?",
        (last, limit)).fetchall()
    return [dict(r) for r in rows]


def quick_capture(store, limit=100):
    rows = store.conn.execute(
        "SELECT path,sha256,actor,session,state,created_at FROM ingest_receipts "
        "ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    return [dict(r) for r in rows]


def resume_now(store):
    cp, newest = store.resume_card()
    meaningful = store.conn.execute(
        "SELECT kind,ref,ts FROM activity_events ORDER BY ts DESC LIMIT 12").fetchall()
    return {
        "checkpoint": dict(cp) if cp else None,
        "newest_occurrences": [dict(r) for r in newest],
        "meaningful_activity": [dict(r) for r in meaningful],
    }
