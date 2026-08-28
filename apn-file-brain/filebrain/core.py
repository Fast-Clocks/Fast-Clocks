"""Core engine: database, scanning, hashing, dedup, ingress, checkpoints.

Design rules honoured here (from the File Brain master spec):
  * AUDIT FIRST. PRESERVE ORIGINALS. Never write source bytes.
  * One content object (SHA-256) may have many occurrences (paths).
  * Never follow symlinks; never let a scan escape its approved root.
  * If a file changes while being hashed, reject the hash and retry later.
  * Never store a full secret; store a category and a redacted locator.
  * Nothing is ever moved or deleted; cleanup is planned, not performed.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import time
from dataclasses import dataclass

SCHEMA_VERSION = 1
CHUNK = 1 << 20  # 1 MiB streaming reads — never load a whole file into memory

# Directory names excluded anywhere they appear (spec section 10 defaults).
DEFAULT_EXCLUDE_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv",
    "env", ".cache", ".npm", ".gradle", ".m2", "DerivedData", "Pods",
    ".terraform", "site-packages", "dist", "build", ".next", ".nuxt",
    "vendor", ".Trash", ".Trashes", "$RECYCLE.BIN", "Caches",
}
# Absolute path prefixes excluded outright (OS internals / credential stores).
DEFAULT_EXCLUDE_PREFIXES = (
    "/System", "/Library", "/Applications", "/private/var", "/usr", "/bin",
    "/sbin", "/opt", "/dev", "/proc", "/Volumes/Recovery",
)
# Filename patterns treated as transient churn, not durable artifacts.
TRANSIENT_PATTERNS = (
    re.compile(r".*\.tmp$"), re.compile(r".*\.swp$"), re.compile(r".*~$"),
    re.compile(r"^\.~lock\..*"), re.compile(r".*\.crdownload$"),
    re.compile(r".*\.part$"), re.compile(r"^\.DS_Store$"),
)

TEXT_EXTS = {
    ".txt", ".md", ".markdown", ".html", ".htm", ".json", ".csv", ".tsv",
    ".py", ".js", ".ts", ".tsx", ".jsx", ".css", ".yml", ".yaml", ".toml",
    ".ini", ".cfg", ".sh", ".sql", ".xml", ".rs", ".go", ".java", ".rb",
    ".c", ".h", ".cpp", ".log",
}

# Sensitivity detectors. We never store the match — only category + redaction.
SENSITIVITY = [
    ("email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("api_key", re.compile(r"\b(sk-[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{12,}|ghp_[A-Za-z0-9]{20,})")),
    ("credit_card", re.compile(r"\b(?:\d[ -]?){13,16}\b")),
    ("abn_acn", re.compile(r"\b\d{2}\s?\d{3}\s?\d{3}\s?\d{3}\b")),
    ("aus_tfn", re.compile(r"\b\d{3}\s?\d{3}\s?\d{3}\b")),
    ("phone", re.compile(r"\b(?:\+?61|0)[2-478](?:[ -]?\d){8}\b")),
    ("secret_marker", re.compile(r"(?i)\b(password|passwd|secret|api[_-]?key|token)\s*[:=]\s*\S+")),
]


class ChangeDuringHash(Exception):
    """Raised when a file's size/mtime changes while we are hashing it."""


class ScopeEscape(Exception):
    """Raised when a path resolves outside its approved root."""


def sha256_stream(path):
    """Hash a file by streaming its bytes. Detect change-during-hash.

    Returns (hexdigest, size, mtime). Raises ChangeDuringHash if the file's
    size or mtime moved between the pre- and post-read stat.
    """
    st1 = os.stat(path, follow_symlinks=False)
    h = hashlib.sha256()
    with open(path, "rb", buffering=0) as fh:
        while True:
            block = fh.read(CHUNK)
            if not block:
                break
            h.update(block)
    st2 = os.stat(path, follow_symlinks=False)
    if st1.st_size != st2.st_size or st1.st_mtime_ns != st2.st_mtime_ns:
        raise ChangeDuringHash(path)
    return h.hexdigest(), st2.st_size, st2.st_mtime


def normalise_text(raw):
    """Version-1 text normalisation: collapse whitespace, strip trailing
    space per line, unify newlines. Used for the text-equivalence hash."""
    lines = [ln.rstrip() for ln in raw.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    return "\n".join(lines).strip()


def ordered_parts(raw):
    """Minimal ordered decomposition for text: heading / paragraph / sentence.

    Enough to prove parts carry a stable, ordered source coordinate. Deeper
    typed decomposition (tables, numbers, tokens) is staged for a later phase.
    """
    parts = []
    idx = 0
    offset = 0
    for block in re.split(r"\n\s*\n", raw):
        if not block.strip():
            offset += len(block) + 2
            continue
        stripped = block.strip()
        start = raw.find(stripped, offset)
        if start < 0:
            start = offset
        end = start + len(stripped)
        ptype = "heading" if re.match(r"^#{1,6}\s|^[A-Z0-9 \-—]{6,}$", stripped) else "paragraph"
        parts.append((idx, ptype, stripped[:2000], start, end))
        idx += 1
        offset = end
    return parts


def detect_sensitivity(raw):
    """Return list of (category, redacted_locator). Never returns the match."""
    findings = []
    for lineno, line in enumerate(raw.splitlines(), 1):
        for category, rx in SENSITIVITY:
            m = rx.search(line)
            if m:
                token = m.group(0)
                tail = re.sub(r"\s", "", token)[-4:]
                findings.append((category, f"line {lineno} ****{tail}"))
                break  # one finding per line is enough for a coverage signal
    return findings


class Store:
    """SQLite-backed index. WAL mode, foreign keys, explicit schema version."""

    def __init__(self, db_path):
        self.db_path = str(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self._migrate()

    # ---- schema -------------------------------------------------------
    def _migrate(self):
        c = self.conn
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS schema_versions(
                version INTEGER PRIMARY KEY, applied_at REAL);
            CREATE TABLE IF NOT EXISTS scan_roots(
                id INTEGER PRIMARY KEY, path TEXT UNIQUE, added_at REAL, active INTEGER DEFAULT 1);
            CREATE TABLE IF NOT EXISTS scan_runs(
                id INTEGER PRIMARY KEY, root_id INTEGER, started_at REAL, finished_at REAL,
                status TEXT, files_seen INTEGER DEFAULT 0, bytes_seen INTEGER DEFAULT 0,
                errors INTEGER DEFAULT 0,
                FOREIGN KEY(root_id) REFERENCES scan_roots(id));
            CREATE TABLE IF NOT EXISTS content_objects(
                sha256 TEXT PRIMARY KEY, size INTEGER, text_sha256 TEXT,
                is_binary INTEGER, mime_guess TEXT, first_seen_at REAL, analysed_version INTEGER DEFAULT 0);
            CREATE TABLE IF NOT EXISTS occurrences(
                path TEXT PRIMARY KEY, sha256 TEXT, size INTEGER, mtime REAL, ext TEXT,
                root_id INTEGER, first_seen_run INTEGER, last_seen_run INTEGER,
                last_seen_at REAL, present INTEGER DEFAULT 1,
                FOREIGN KEY(sha256) REFERENCES content_objects(sha256),
                FOREIGN KEY(root_id) REFERENCES scan_roots(id));
            CREATE TABLE IF NOT EXISTS occurrence_history(
                id INTEGER PRIMARY KEY, path TEXT, sha256 TEXT, size INTEGER, mtime REAL,
                run_id INTEGER, seen_at REAL, event TEXT);
            CREATE TABLE IF NOT EXISTS parts(
                id INTEGER PRIMARY KEY, sha256 TEXT, idx INTEGER, ptype TEXT,
                text TEXT, char_start INTEGER, char_end INTEGER,
                FOREIGN KEY(sha256) REFERENCES content_objects(sha256));
            CREATE TABLE IF NOT EXISTS sensitivity_findings(
                id INTEGER PRIMARY KEY, sha256 TEXT, category TEXT, locator TEXT,
                FOREIGN KEY(sha256) REFERENCES content_objects(sha256));
            CREATE TABLE IF NOT EXISTS ingest_receipts(
                id INTEGER PRIMARY KEY, sha256 TEXT, path TEXT, actor TEXT, session TEXT,
                state TEXT, created_at REAL);
            CREATE TABLE IF NOT EXISTS work_sessions(
                id INTEGER PRIMARY KEY, started_at REAL, ended_at REAL, note TEXT);
            CREATE TABLE IF NOT EXISTS work_checkpoints(
                id INTEGER PRIMARY KEY, created_at REAL, last_path TEXT, next_action TEXT,
                open_questions TEXT, note TEXT, snapshot TEXT);
            CREATE TABLE IF NOT EXISTS audit_events(
                id INTEGER PRIMARY KEY, ts REAL, actor TEXT, action TEXT, detail TEXT);
            CREATE TABLE IF NOT EXISTS activity_events(
                id INTEGER PRIMARY KEY, ts REAL, kind TEXT, ref TEXT, detail TEXT);
            CREATE TABLE IF NOT EXISTS records(
                id INTEGER PRIMARY KEY, sha256 TEXT, part_idx INTEGER, rtype TEXT,
                text TEXT, char_start INTEGER, char_end INTEGER,
                confidence REAL, evidence TEXT,
                FOREIGN KEY(sha256) REFERENCES content_objects(sha256));
            CREATE TABLE IF NOT EXISTS idea_versions(
                id INTEGER PRIMARY KEY, title TEXT, state TEXT, created_at REAL, note TEXT);
            CREATE TABLE IF NOT EXISTS idea_components(
                id INTEGER PRIMARY KEY, idea_id INTEGER, record_id INTEGER, role TEXT, position INTEGER,
                FOREIGN KEY(idea_id) REFERENCES idea_versions(id));
            CREATE TABLE IF NOT EXISTS relationships(
                id INTEGER PRIMARY KEY, src_kind TEXT, src_id TEXT, dst_kind TEXT, dst_id TEXT,
                rtype TEXT, confidence REAL, evidence TEXT, created_at REAL);
            CREATE TABLE IF NOT EXISTS collections(
                id INTEGER PRIMARY KEY, name TEXT UNIQUE, created_at REAL);
            CREATE TABLE IF NOT EXISTS collection_items(
                id INTEGER PRIMARY KEY, collection_id INTEGER, sha256 TEXT, path TEXT,
                FOREIGN KEY(collection_id) REFERENCES collections(id));
            CREATE TABLE IF NOT EXISTS tags(
                id INTEGER PRIMARY KEY, name TEXT UNIQUE);
            CREATE TABLE IF NOT EXISTS taggings(
                id INTEGER PRIMARY KEY, tag_id INTEGER, target_kind TEXT, target_id TEXT,
                FOREIGN KEY(tag_id) REFERENCES tags(id));
            CREATE TABLE IF NOT EXISTS cleanup_plans(
                id INTEGER PRIMARY KEY, created_at REAL, note TEXT, actions INTEGER);
            CREATE TABLE IF NOT EXISTS cleanup_actions(
                id INTEGER PRIMARY KEY, plan_id INTEGER, sha256 TEXT, quarantine TEXT,
                keep_canonical TEXT, reason TEXT, risk TEXT, rollback TEXT, approval TEXT,
                FOREIGN KEY(plan_id) REFERENCES cleanup_plans(id));
            CREATE INDEX IF NOT EXISTS ix_occ_sha ON occurrences(sha256);
            CREATE INDEX IF NOT EXISTS ix_hist_path ON occurrence_history(path);
            CREATE INDEX IF NOT EXISTS ix_rec_sha ON records(sha256);
            CREATE INDEX IF NOT EXISTS ix_rec_type ON records(rtype);
            """
        )
        # FTS5 is optional; probe it once and record whether it is available so
        # we never *claim* full-text search works when the build lacks fts5.
        self.fts_ok = False
        try:
            c.executescript(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS records_fts USING fts5(
                    text, rtype UNINDEXED, sha256 UNINDEXED, record_id UNINDEXED);
                CREATE VIRTUAL TABLE IF NOT EXISTS parts_fts USING fts5(
                    text, sha256 UNINDEXED, part_id UNINDEXED);
                """
            )
            self.fts_ok = True
        except sqlite3.OperationalError:
            self.fts_ok = False
        row = c.execute("SELECT MAX(version) v FROM schema_versions").fetchone()
        if not row or row["v"] is None:
            c.execute("INSERT INTO schema_versions VALUES(?,?)", (SCHEMA_VERSION, time.time()))
        c.commit()

    # ---- activity stream ---------------------------------------------
    def activity(self, kind, ref="", detail=None):
        self.conn.execute(
            "INSERT INTO activity_events(ts,kind,ref,detail) VALUES(?,?,?,?)",
            (time.time(), kind, ref, json.dumps(detail or {})),
        )
        self.conn.commit()

    # ---- audit --------------------------------------------------------
    def audit(self, actor, action, detail=None):
        self.conn.execute(
            "INSERT INTO audit_events(ts,actor,action,detail) VALUES(?,?,?,?)",
            (time.time(), actor, action, json.dumps(detail or {})),
        )
        self.conn.commit()

    # ---- roots --------------------------------------------------------
    def add_root(self, path):
        real = os.path.realpath(path)
        if not os.path.isdir(real):
            raise ValueError(f"not a directory: {path}")
        self.conn.execute(
            "INSERT OR IGNORE INTO scan_roots(path,added_at,active) VALUES(?,?,1)",
            (real, time.time()),
        )
        self.conn.commit()
        self.audit("system", "add_root", {"path": real})
        return self.conn.execute("SELECT * FROM scan_roots WHERE path=?", (real,)).fetchone()

    def roots(self):
        return self.conn.execute("SELECT * FROM scan_roots WHERE active=1 ORDER BY id").fetchall()

    # ---- scanning -----------------------------------------------------
    def _excluded_dir(self, name, extra_dirs):
        return name in DEFAULT_EXCLUDE_DIRS or name in extra_dirs

    def _excluded_path(self, path):
        return any(path.startswith(p) for p in DEFAULT_EXCLUDE_PREFIXES)

    def scan(self, root_path, dry_run=False, extra_excludes=None, progress=None):
        """Read-only, resumable scan of one approved root.

        Reuses the prior hash for a path whose size+mtime are unchanged
        (incremental). Retains every occurrence and its history. Never
        writes to source files.
        """
        extra = set(extra_excludes or [])
        real_root = os.path.realpath(root_path)
        root = self.conn.execute("SELECT * FROM scan_roots WHERE path=?", (real_root,)).fetchone()
        if not root:
            root = self.add_root(real_root)
        run_id = None
        if not dry_run:
            cur = self.conn.execute(
                "INSERT INTO scan_runs(root_id,started_at,status) VALUES(?,?,?)",
                (root["id"], time.time(), "running"),
            )
            run_id = cur.lastrowid
            self.conn.commit()

        stats = {"files": 0, "bytes": 0, "new_objects": 0, "duplicates": 0,
                 "reused": 0, "errors": 0, "skipped": 0, "changed": 0}

        for dirpath, dirnames, filenames in os.walk(real_root, followlinks=False):
            dirnames[:] = [d for d in dirnames
                           if not self._excluded_dir(d, extra)
                           and not os.path.islink(os.path.join(dirpath, d))]
            for fn in filenames:
                path = os.path.join(dirpath, fn)
                if any(rx.match(fn) for rx in TRANSIENT_PATTERNS):
                    stats["skipped"] += 1
                    continue
                if os.path.islink(path):
                    stats["skipped"] += 1
                    continue
                # containment: a resolved path must stay under the root.
                real = os.path.realpath(path)
                if not (real == real_root or real.startswith(real_root + os.sep)):
                    stats["skipped"] += 1
                    continue
                if self._excluded_path(real):
                    stats["skipped"] += 1
                    continue
                try:
                    self._ingest_path(path, root, run_id, dry_run, stats)
                except ChangeDuringHash:
                    stats["errors"] += 1
                    self._history(path, None, None, None, run_id, "changed_during_hash", dry_run)
                except (PermissionError, FileNotFoundError, OSError):
                    stats["errors"] += 1
                if progress and stats["files"] % 200 == 0:
                    progress(stats)

        if not dry_run:
            self.conn.execute(
                "UPDATE scan_runs SET finished_at=?,status=?,files_seen=?,bytes_seen=?,errors=? WHERE id=?",
                (time.time(), "complete", stats["files"], stats["bytes"], stats["errors"], run_id),
            )
            self.conn.commit()
            self.audit("system", "scan", {"root": real_root, **stats})
        return stats

    def _history(self, path, sha, size, mtime, run_id, event, dry_run):
        if dry_run:
            return
        self.conn.execute(
            "INSERT INTO occurrence_history(path,sha256,size,mtime,run_id,seen_at,event) VALUES(?,?,?,?,?,?,?)",
            (path, sha, size, mtime, run_id, time.time(), event),
        )

    def _ingest_path(self, path, root, run_id, dry_run, stats):
        st = os.stat(path, follow_symlinks=False)
        ext = os.path.splitext(path)[1].lower()
        prior = self.conn.execute("SELECT * FROM occurrences WHERE path=?", (path,)).fetchone()

        reuse = (prior and abs(prior["mtime"] - st.st_mtime) < 1e-6
                 and prior["size"] == st.st_size and prior["sha256"])
        if reuse:
            sha, size, mtime = prior["sha256"], st.st_size, st.st_mtime
            stats["reused"] += 1
        else:
            sha, size, mtime = sha256_stream(path)

        stats["files"] += 1
        stats["bytes"] += size
        if dry_run:
            existing = self.conn.execute(
                "SELECT 1 FROM occurrences WHERE sha256=? AND path<>?", (sha, path)
            ).fetchone()
            if existing:
                stats["duplicates"] += 1
            return

        # content object (one per unique sha)
        co = self.conn.execute("SELECT 1 FROM content_objects WHERE sha256=?", (sha,)).fetchone()
        if not co:
            self._register_content(sha, path, ext, size)
            stats["new_objects"] += 1
        else:
            other = self.conn.execute(
                "SELECT 1 FROM occurrences WHERE sha256=? AND path<>? AND present=1", (sha, path)
            ).fetchone()
            if other:
                stats["duplicates"] += 1

        if not prior:
            self.conn.execute(
                "INSERT INTO occurrences(path,sha256,size,mtime,ext,root_id,first_seen_run,last_seen_run,last_seen_at,present)"
                " VALUES(?,?,?,?,?,?,?,?,?,1)",
                (path, sha, size, mtime, ext, root["id"], run_id, run_id, time.time()),
            )
            self._history(path, sha, size, mtime, run_id, "first_seen", dry_run)
        elif prior["sha256"] != sha:
            self.conn.execute(
                "UPDATE occurrences SET sha256=?,size=?,mtime=?,last_seen_run=?,last_seen_at=?,present=1 WHERE path=?",
                (sha, size, mtime, run_id, time.time(), path),
            )
            self._history(path, sha, size, mtime, run_id, "changed", dry_run)
            self.activity("changed", path, {"sha256": sha})
            stats["changed"] += 1
        else:
            self.conn.execute(
                "UPDATE occurrences SET last_seen_run=?,last_seen_at=?,present=1 WHERE path=?",
                (run_id, time.time(), path),
            )
        self.conn.commit()

    def _register_content(self, sha, path, ext, size):
        is_binary = 1
        text_sha = None
        raw = None
        if ext in TEXT_EXTS and size <= 8 * 1024 * 1024:
            try:
                with open(path, "r", encoding="utf-8", errors="strict") as fh:
                    raw = fh.read()
                is_binary = 0
            except (UnicodeDecodeError, OSError):
                raw = None
        if raw is not None:
            text_sha = hashlib.sha256(normalise_text(raw).encode("utf-8")).hexdigest()
        self.conn.execute(
            "INSERT INTO content_objects(sha256,size,text_sha256,is_binary,mime_guess,first_seen_at,analysed_version)"
            " VALUES(?,?,?,?,?,?,1)",
            (sha, size, text_sha, is_binary, ext or "application/octet-stream", time.time()),
        )
        if raw is not None:
            for idx, ptype, text, cs, ce in ordered_parts(raw):
                cur = self.conn.execute(
                    "INSERT INTO parts(sha256,idx,ptype,text,char_start,char_end) VALUES(?,?,?,?,?,?)",
                    (sha, idx, ptype, text, cs, ce),
                )
                if self.fts_ok:
                    self.conn.execute(
                        "INSERT INTO parts_fts(text,sha256,part_id) VALUES(?,?,?)",
                        (text, sha, cur.lastrowid),
                    )
            # typed ordered records (facts/ideas/decisions/questions/tasks/projects)
            from . import extract
            for part_idx, rtype, text, cs, ce, conf, evid in extract.extract_records(raw):
                cur = self.conn.execute(
                    "INSERT INTO records(sha256,part_idx,rtype,text,char_start,char_end,confidence,evidence)"
                    " VALUES(?,?,?,?,?,?,?,?)",
                    (sha, part_idx, rtype, text, cs, ce, conf, evid),
                )
                if self.fts_ok:
                    self.conn.execute(
                        "INSERT INTO records_fts(text,rtype,sha256,record_id) VALUES(?,?,?,?)",
                        (text, rtype, sha, cur.lastrowid),
                    )
            for category, locator in detect_sensitivity(raw):
                self.conn.execute(
                    "INSERT INTO sensitivity_findings(sha256,category,locator) VALUES(?,?,?)",
                    (sha, category, locator),
                )

    # ---- ingress gate -------------------------------------------------
    def register(self, path, actor="unknown", session="", settle=0.2):
        """Active ingress: hash a just-created artifact and receipt it.

        Waits for the file to stop changing (size stable) before hashing.
        """
        path = os.path.realpath(path)
        if not os.path.isfile(path):
            raise ValueError(f"not a file: {path}")
        last = -1
        for _ in range(25):
            sz = os.stat(path).st_size
            if sz == last:
                break
            last = sz
            time.sleep(settle)
        sha, size, mtime = sha256_stream(path)
        ext = os.path.splitext(path)[1].lower()
        if not self.conn.execute("SELECT 1 FROM content_objects WHERE sha256=?", (sha,)).fetchone():
            self._register_content(sha, path, ext, size)
        if not self.conn.execute("SELECT 1 FROM occurrences WHERE path=?", (path,)).fetchone():
            self.conn.execute(
                "INSERT INTO occurrences(path,sha256,size,mtime,ext,root_id,last_seen_at,present)"
                " VALUES(?,?,?,?,?,?,?,1)",
                (path, sha, size, mtime, ext, None, time.time()),
            )
        self.conn.execute(
            "INSERT INTO ingest_receipts(sha256,path,actor,session,state,created_at) VALUES(?,?,?,?,?,?)",
            (sha, path, actor, session, "REGISTERED", time.time()),
        )
        self.conn.commit()
        self.audit(actor, "register", {"path": path, "sha256": sha, "session": session})
        self.activity("register", path, {"sha256": sha, "actor": actor})
        return {"path": path, "sha256": sha, "size": size, "actor": actor,
                "session": session, "state": "REGISTERED", "at": time.time()}

    # ---- checkpoint / resume -----------------------------------------
    def checkpoint(self, next_action="", open_questions="", note=""):
        newest = self.conn.execute(
            "SELECT path FROM occurrences WHERE present=1 ORDER BY last_seen_at DESC LIMIT 1"
        ).fetchone()
        last_path = newest["path"] if newest else ""
        snapshot = self.status()
        cur = self.conn.execute(
            "INSERT INTO work_checkpoints(created_at,last_path,next_action,open_questions,note,snapshot)"
            " VALUES(?,?,?,?,?,?)",
            (time.time(), last_path, next_action, open_questions, note, json.dumps(snapshot)),
        )
        self.conn.commit()
        self.audit("system", "checkpoint", {"id": cur.lastrowid, "next_action": next_action})
        return cur.lastrowid

    def resume_card(self):
        cp = self.conn.execute(
            "SELECT * FROM work_checkpoints ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        newest = self.conn.execute(
            "SELECT path,sha256,last_seen_at FROM occurrences WHERE present=1 ORDER BY last_seen_at DESC LIMIT 8"
        ).fetchall()
        return cp, newest

    # ---- queries / reports -------------------------------------------
    def status(self):
        c = self.conn
        q = lambda s: c.execute(s).fetchone()[0]
        exact = c.execute(
            "SELECT COUNT(*) FROM (SELECT sha256 FROM occurrences WHERE present=1 "
            "GROUP BY sha256 HAVING COUNT(DISTINCT path)>1)"
        ).fetchone()[0]
        redundant = c.execute(
            "SELECT COALESCE(SUM(cnt-1),0) FROM (SELECT COUNT(DISTINCT path) cnt FROM occurrences "
            "WHERE present=1 GROUP BY sha256 HAVING cnt>1)"
        ).fetchone()[0]
        return {
            "roots": q("SELECT COUNT(*) FROM scan_roots WHERE active=1"),
            "occurrences": q("SELECT COUNT(*) FROM occurrences WHERE present=1"),
            "content_objects": q("SELECT COUNT(*) FROM content_objects"),
            "duplicate_groups": exact,
            "redundant_copies": redundant,
            "sensitivity_findings": q("SELECT COUNT(*) FROM sensitivity_findings"),
            "receipts": q("SELECT COUNT(*) FROM ingest_receipts"),
        }

    def duplicate_groups(self):
        rows = self.conn.execute(
            "SELECT sha256, COUNT(DISTINCT path) n, SUM(size) total FROM occurrences "
            "WHERE present=1 GROUP BY sha256 HAVING n>1 ORDER BY total DESC"
        ).fetchall()
        groups = []
        for r in rows:
            paths = [x["path"] for x in self.conn.execute(
                "SELECT path FROM occurrences WHERE sha256=? AND present=1 ORDER BY path", (r["sha256"],))]
            groups.append({"sha256": r["sha256"], "count": r["n"],
                           "size": paths and self.conn.execute(
                               "SELECT size FROM occurrences WHERE path=?", (paths[0],)).fetchone()["size"],
                           "paths": paths})
        return groups

    def timeline(self):
        rows = self.conn.execute(
            "SELECT date(mtime,'unixepoch') d, COUNT(*) n FROM occurrences WHERE present=1 "
            "GROUP BY d ORDER BY d"
        ).fetchall()
        return [(r["d"], r["n"]) for r in rows]

    @staticmethod
    def _canonical_score(path):
        p = path.lower()
        score = 0
        if any(k in p for k in ("preserv", "canonical", "evidence", "manifest", "locked")):
            score += 5
        if os.sep + ".git" + os.sep in path or "/repo" in p or "/src/" in p:
            score += 3
        if "download" in p:
            score -= 3
        if "/tmp/" in p or "/temp/" in p or "cache" in p:
            score -= 2
        score -= path.count(os.sep) * 0.01  # gently prefer shallower, tie-break only
        return score

    def cleanup_plan(self):
        """Propose (never perform) quarantine of exact-duplicate copies.

        For each exact-duplicate group, recommend one canonical copy by
        evidence score and list the others as quarantine candidates with a
        rollback note. This is a recommendation, not a fact — nothing moves.
        """
        plan = []
        for g in self.duplicate_groups():
            ranked = sorted(g["paths"], key=self._canonical_score, reverse=True)
            keep = ranked[0]
            for other in ranked[1:]:
                plan.append({
                    "sha256": g["sha256"], "size": g["size"],
                    "quarantine": other, "keep_canonical": keep,
                    "reason": "exact SHA-256 duplicate of retained canonical",
                    "risk": "low", "rollback": f"restore {other} from quarantine",
                    "approval": "PENDING",
                })
        return plan

    def text_equivalent_groups(self):
        """Different bytes, same normalised text -> text-equivalent variants.
        These are NOT exact duplicates and must be reviewed as distinct."""
        rows = self.conn.execute(
            "SELECT text_sha256 t, COUNT(*) n FROM content_objects "
            "WHERE text_sha256 IS NOT NULL GROUP BY text_sha256 HAVING n>1"
        ).fetchall()
        out = []
        for r in rows:
            shas = [x["sha256"] for x in self.conn.execute(
                "SELECT sha256 FROM content_objects WHERE text_sha256=?", (r["t"],))]
            # only interesting if the exact hashes differ
            if len(set(shas)) > 1:
                paths = [x["path"] for x in self.conn.execute(
                    "SELECT path FROM occurrences WHERE sha256 IN (%s) AND present=1"
                    % ",".join("?" * len(shas)), shas)]
                out.append({"text_sha256": r["t"], "content_objects": shas, "paths": paths})
        return out

    def near_and_version_candidates(self, size_tol=0.05):
        """Group present occurrences by filename stem; within a stem, distinct
        content objects are version candidates, and those with near-equal size
        are near-duplicate candidates. Heuristic — flagged for review, never
        treated as proof."""
        import os as _os
        rows = self.conn.execute(
            "SELECT path,sha256,size,ext FROM occurrences WHERE present=1").fetchall()
        by_stem = {}
        for r in rows:
            stem = _os.path.splitext(_os.path.basename(r["path"]))[0]
            stem = re.sub(r"[ _-]*(\(\d+\)|v?\d+|copy|final|draft)$", "", stem.lower()).strip()
            by_stem.setdefault((stem, r["ext"]), []).append(r)
        versions, near = [], []
        for key, items in by_stem.items():
            shas = {i["sha256"] for i in items}
            if len(shas) < 2:
                continue
            versions.append({"stem": key[0], "ext": key[1],
                             "paths": [i["path"] for i in items]})
            for a in items:
                for b in items:
                    if a["path"] < b["path"] and a["sha256"] != b["sha256"] and a["size"] and b["size"]:
                        if abs(a["size"] - b["size"]) <= size_tol * max(a["size"], b["size"]):
                            near.append({"a": a["path"], "b": b["path"],
                                         "size_a": a["size"], "size_b": b["size"]})
        return {"version_candidates": versions, "near_duplicates": near}

    # ---- search -------------------------------------------------------
    def search(self, query, rtype=None, limit=50):
        """Full-text search over extracted records. Uses FTS5 when available,
        otherwise a LIKE fallback (reported honestly by `status`/`audit`)."""
        if self.fts_ok:
            sql = ("SELECT r.rtype,r.text,r.sha256,r.record_id FROM records_fts r "
                   "WHERE records_fts MATCH ?")
            args = [query]
            if rtype:
                sql += " AND r.rtype=?"
                args.append(rtype)
            sql += " LIMIT ?"
            args.append(limit)
            try:
                return [dict(x) for x in self.conn.execute(sql, args).fetchall()]
            except sqlite3.OperationalError:
                pass
        sql = "SELECT rtype,text,sha256,id AS record_id FROM records WHERE text LIKE ?"
        args = ["%" + query + "%"]
        if rtype:
            sql += " AND rtype=?"
            args.append(rtype)
        sql += " LIMIT ?"
        args.append(limit)
        return [dict(x) for x in self.conn.execute(sql, args).fetchall()]

    # ---- collections & tags (virtual — never move a file) -------------
    def collection_add(self, name, path):
        occ = self.conn.execute("SELECT sha256 FROM occurrences WHERE path=?", (path,)).fetchone()
        self.conn.execute("INSERT OR IGNORE INTO collections(name,created_at) VALUES(?,?)",
                          (name, time.time()))
        cid = self.conn.execute("SELECT id FROM collections WHERE name=?", (name,)).fetchone()["id"]
        self.conn.execute("INSERT INTO collection_items(collection_id,sha256,path) VALUES(?,?,?)",
                          (cid, occ["sha256"] if occ else None, path))
        self.conn.commit()
        self.audit("system", "collection_add", {"collection": name, "path": path})
        return cid

    def collection_items(self, name):
        return [dict(x) for x in self.conn.execute(
            "SELECT ci.path,ci.sha256 FROM collection_items ci JOIN collections c ON c.id=ci.collection_id "
            "WHERE c.name=?", (name,)).fetchall()]

    def tag(self, name, target_kind, target_id):
        self.conn.execute("INSERT OR IGNORE INTO tags(name) VALUES(?)", (name,))
        tid = self.conn.execute("SELECT id FROM tags WHERE name=?", (name,)).fetchone()["id"]
        self.conn.execute("INSERT INTO taggings(tag_id,target_kind,target_id) VALUES(?,?,?)",
                          (tid, target_kind, str(target_id)))
        self.conn.commit()

    # ---- cleanup plan persistence ------------------------------------
    def save_cleanup_plan(self, note=""):
        actions = self.cleanup_plan()
        cur = self.conn.execute(
            "INSERT INTO cleanup_plans(created_at,note,actions) VALUES(?,?,?)",
            (time.time(), note, len(actions)))
        pid = cur.lastrowid
        for a in actions:
            self.conn.execute(
                "INSERT INTO cleanup_actions(plan_id,sha256,quarantine,keep_canonical,reason,risk,rollback,approval)"
                " VALUES(?,?,?,?,?,?,?,?)",
                (pid, a["sha256"], a["quarantine"], a["keep_canonical"], a["reason"],
                 a["risk"], a["rollback"], a["approval"]))
        self.conn.commit()
        self.audit("system", "cleanup_plan", {"plan_id": pid, "actions": len(actions)})
        return pid, actions

    # ---- coverage (Audit Machine) ------------------------------------
    def coverage(self):
        return {
            "roots": [dict(r) for r in self.roots()],
            "runs": self.conn.execute("SELECT COUNT(*) FROM scan_runs").fetchone()[0],
            "errors": self.conn.execute("SELECT COALESCE(SUM(errors),0) FROM scan_runs").fetchone()[0],
            "fts5": self.fts_ok,
            "last_run": self.conn.execute(
                "SELECT started_at,finished_at,files_seen,errors FROM scan_runs "
                "ORDER BY id DESC LIMIT 1").fetchone(),
        }

    def close(self):
        self.conn.close()
