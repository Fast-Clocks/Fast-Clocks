"""Idea genealogy — how smaller thoughts form larger ideas and projects.

An idea is a versioned composition with lineage, not a summary string.
Composing an idea from component records:
  * never deletes or rewrites the components;
  * records each component's role and order;
  * writes a `combines` relationship from the idea to each component;
  * lets a larger idea be composed from smaller ideas, keeping every point
    beneath it (nested provenance / a directed acyclic composition).
"""

from __future__ import annotations

import time


def compose(store, title, record_ids, state="EMERGENT_IDEA", note=""):
    """Compose an idea version from extracted record ids. Returns idea id."""
    cur = store.conn.execute(
        "INSERT INTO idea_versions(title,state,created_at,note) VALUES(?,?,?,?)",
        (title, state, time.time(), note),
    )
    idea_id = cur.lastrowid
    for pos, rid in enumerate(record_ids):
        store.conn.execute(
            "INSERT INTO idea_components(idea_id,record_id,role,position) VALUES(?,?,?,?)",
            (idea_id, rid, "component", pos),
        )
        store.conn.execute(
            "INSERT INTO relationships(src_kind,src_id,dst_kind,dst_id,rtype,confidence,evidence,created_at)"
            " VALUES(?,?,?,?,?,?,?,?)",
            ("idea", str(idea_id), "record", str(rid), "combines", 1.0, "DIRECT", time.time()),
        )
    store.conn.commit()
    store.audit("system", "idea_compose", {"idea_id": idea_id, "title": title,
                                           "components": len(record_ids)})
    store.activity("idea_compose", str(idea_id), {"title": title})
    return idea_id


def compose_from_ideas(store, title, idea_ids, state="COMPOSED_IDEA", note=""):
    """Compose a larger idea from smaller ideas, preserving each idea's lineage."""
    cur = store.conn.execute(
        "INSERT INTO idea_versions(title,state,created_at,note) VALUES(?,?,?,?)",
        (title, state, time.time(), note),
    )
    big = cur.lastrowid
    for pos, iid in enumerate(idea_ids):
        store.conn.execute(
            "INSERT INTO relationships(src_kind,src_id,dst_kind,dst_id,rtype,confidence,evidence,created_at)"
            " VALUES(?,?,?,?,?,?,?,?)",
            ("idea", str(big), "idea", str(iid), "combines", 1.0, "DIRECT", time.time()),
        )
    store.conn.commit()
    store.audit("system", "idea_compose_ideas", {"idea_id": big, "from": idea_ids})
    return big


def genealogy(store, idea_id, _depth=0, _seen=None):
    """Return the full nested composition beneath an idea, with every source."""
    _seen = _seen or set()
    if idea_id in _seen:
        return {"idea_id": idea_id, "cycle": True}
    _seen.add(idea_id)
    iv = store.conn.execute("SELECT * FROM idea_versions WHERE id=?", (idea_id,)).fetchone()
    if not iv:
        return None
    node = {"idea_id": idea_id, "title": iv["title"], "state": iv["state"],
            "records": [], "sub_ideas": []}
    for rel in store.conn.execute(
            "SELECT dst_kind,dst_id FROM relationships WHERE src_kind='idea' AND src_id=? AND rtype='combines'",
            (str(idea_id),)):
        if rel["dst_kind"] == "record":
            rec = store.conn.execute(
                "SELECT id,rtype,text,sha256,char_start,char_end FROM records WHERE id=?",
                (rel["dst_id"],)).fetchone()
            if rec:
                node["records"].append(dict(rec))
        elif rel["dst_kind"] == "idea":
            sub = genealogy(store, int(rel["dst_id"]), _depth + 1, _seen)
            if sub:
                node["sub_ideas"].append(sub)
    return node
