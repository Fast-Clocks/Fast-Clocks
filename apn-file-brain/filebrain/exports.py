"""Human- and machine-readable exports: CSV, JSON, NDJSON, Markdown.

Exports are additive files written to an output directory. They never modify
the index or the source estate.
"""

from __future__ import annotations

import csv
import json
import os


def _rows(store):
    return [dict(r) for r in store.conn.execute(
        "SELECT path,sha256,size,ext,mtime,present FROM occurrences ORDER BY path").fetchall()]


def export_csv(store, path):
    rows = _rows(store)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["path", "sha256", "size", "ext", "mtime", "present"])
        for r in rows:
            w.writerow([r["path"], r["sha256"], r["size"], r["ext"], r["mtime"], r["present"]])
    return path


def export_json(store, path):
    payload = {
        "status": store.status(),
        "occurrences": _rows(store),
        "duplicate_groups": store.duplicate_groups(),
        "timeline": store.timeline(),
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    return path


def export_ndjson(store, path):
    with open(path, "w", encoding="utf-8") as fh:
        for r in _rows(store):
            fh.write(json.dumps(r) + "\n")
    return path


def export_markdown(store, path):
    s = store.status()
    groups = store.duplicate_groups()
    lines = ["# APN File Brain — Inventory\n",
             "## Summary\n",
             f"- Occurrences indexed: **{s['occurrences']}**",
             f"- Unique content objects: **{s['content_objects']}**",
             f"- Exact-duplicate groups: **{s['duplicate_groups']}**",
             f"- Redundant copies: **{s['redundant_copies']}**",
             f"- Sensitivity findings (redacted): **{s['sensitivity_findings']}**\n",
             "## Exact-duplicate groups\n"]
    if not groups:
        lines.append("_None found._")
    for g in groups:
        lines.append(f"### {g['count']} copies · {g['size']} bytes · `{g['sha256'][:12]}…`")
        for p in g["paths"]:
            lines.append(f"- `{p}`")
        lines.append("")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    return path


def export_all(store, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    return {
        "csv": export_csv(store, os.path.join(out_dir, "inventory.csv")),
        "json": export_json(store, os.path.join(out_dir, "inventory.json")),
        "ndjson": export_ndjson(store, os.path.join(out_dir, "occurrences.ndjson")),
        "markdown": export_markdown(store, os.path.join(out_dir, "inventory.md")),
    }
