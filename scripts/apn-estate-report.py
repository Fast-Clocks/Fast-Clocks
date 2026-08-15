#!/usr/bin/env python3
"""Turn a directory of per-repo scan artefacts into ONE prioritised fix list.

Two jobs, and the second is the one that has been missing:

1.  Rank findings so the most actionable are at the top.

2.  Enforce an ALARM BUDGET. A system that raises more alarms than an operator
    can act on has failed, even when every individual alarm is correct. Across
    27 repos this scan can trivially produce a couple of hundred advisories;
    a list that long is not read, so nothing gets fixed, and the estate stays
    broken while the dashboard looks busy. The budget caps how many advisory
    repos are written up in full per run.

    Two rules make the cap honest:
      · Blocking failures are NEVER budgeted away. They are the release gate.
      · Anything suppressed is named and counted in the report. Silent
        truncation reads as "we covered everything" when we did not — the exact
        failure mode this whole scanner exists to prevent.

It also reports COVERAGE, because "0 findings" is not a result on its own. A
check that inspected zero objects prints the same green tick as one that
inspected four hundred files, and only the object count tells them apart.

Usage:  apn-estate-report.py <results-dir> <output.md>
Writes GITHUB_OUTPUT-style key=value lines to stdout.
Env:    ALARM_BUDGET (default 10)
"""
import json
import os
import pathlib
import sys
from datetime import datetime, timezone

CONFIDENCE_RANK = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}

# Exit codes from apn-truth-scan.sh
CLEAN, BLOCKING, ADVISORY = "0", "1", "2"


def load(results_dir):
    """Collect (repo, exit_code, report_text, evidence_json) for every repo."""
    repos = []
    for code_file in sorted(pathlib.Path(results_dir).glob("code-*.txt")):
        repo = code_file.name[len("code-"):-len(".txt")]
        code = code_file.read_text().strip()
        report = pathlib.Path(results_dir, f"result-{repo}.txt")
        evidence = pathlib.Path(results_dir, f"evidence-{repo}.json")
        text = report.read_text() if report.exists() else ""
        try:
            data = json.loads(evidence.read_text()) if evidence.exists() else {}
        except json.JSONDecodeError:
            # A malformed evidence file is itself worth knowing about. Do not
            # let it masquerade as a repo with nothing to report.
            data = {"parse_error": True}
        repos.append((repo, code, text, data))
    return repos


def severity(evidence):
    """Rank an advisory repo. Higher sorts first.

    Confidence dominates count deliberately: one HIGH-confidence structural
    finding (a credential is in the git index) outranks a dozen LOW-confidence
    regex hits over prose, which in this estate have repeatedly turned out to be
    quotations rather than claims.
    """
    best, total = 0, 0
    for check in evidence.get("checks", []):
        if check.get("verdict") in ("WARN", "FAIL"):
            best = max(best, CONFIDENCE_RANK.get(check.get("confidence", "LOW"), 1))
            total += check.get("findings", 0)
    return (best, total)


# Any line that starts a NEW verdict. An excerpt must stop when it reaches one,
# or a 5-line window bleeds the next check's result into this one's evidence —
# which is how a warning ends up quoted as though it were a failure.
VERDICT_PREFIXES = ("✅", "❌", "⚠️", "➖", "===", "---")


def excerpt(text, marker, limit):
    """Pull the lines under each marker, stopping at the next verdict."""
    out, grab = [], 0
    for line in text.splitlines():
        starts_verdict = line.lstrip().startswith(VERDICT_PREFIXES)
        if marker in line:
            grab = 5
        elif grab and starts_verdict:
            grab = 0  # next check begins — this excerpt is finished
        if grab:
            out.append(line)
            grab -= 1
        if len(out) >= limit:
            break
    return out


def main():
    results_dir, out_path = sys.argv[1], sys.argv[2]
    budget = int(os.environ.get("ALARM_BUDGET", "10"))
    repos = load(results_dir)

    blocking = [r for r in repos if r[1] == BLOCKING]
    advisory = [r for r in repos if r[1] == ADVISORY]
    clean = [r for r in repos if r[1] == CLEAN]
    unreachable = [r for r in repos if r[1] not in (CLEAN, BLOCKING, ADVISORY)]

    advisory.sort(key=lambda r: severity(r[3]), reverse=True)
    shown, suppressed = advisory[:budget], advisory[budget:]

    # ── Coverage: what was actually looked at ─────────────────────────────────
    total_files = sum(r[3].get("files_inspected", 0) or 0 for r in repos)
    vacuous = [r[0] for r in repos
               if r[1] in (CLEAN, ADVISORY) and not (r[3].get("files_inspected") or 0)]
    ages = [(r[0], r[3].get("head_age_days")) for r in repos
            if isinstance(r[3].get("head_age_days"), int)]
    stalest = sorted(ages, key=lambda a: -a[1])[:5]

    L = []
    add = L.append
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    add(f"_Generated {now} by APN Daily Estate Scan._")
    add("")
    add("**NO TEST = NO CLAIM.** This is a static scan of source. Nothing here was run, "
        "deployed, or verified live. A clean scan does NOT mean a product works.")
    add("")

    # ── Coverage first, deliberately ──────────────────────────────────────────
    # Put the honesty above the good news. A reader who sees "🟢 Clean × 20"
    # before learning that four of those inspected zero files has been misled.
    add("## Coverage — read this before the fix list")
    add("")
    add(f"| | |")
    add(f"|---|---|")
    add(f"| Repos scanned | {len(repos) - len(unreachable)} of {len(repos)} |")
    add(f"| Source files inspected | {total_files} |")
    add(f"| Unreachable (never looked at) | {len(unreachable)} |")
    add("")
    if vacuous:
        add("> ### ⚠️ Vacuous passes")
        add("> ")
        add("> These repos returned a clean or advisory result while **inspecting zero "
            "source files**. That is absence of evidence, not evidence of correctness — "
            "read each as UNKNOWN:")
        add("> ")
        for repo in vacuous:
            add(f"> - `{repo}`")
        add("")
    if stalest and stalest[0][1] >= 14:
        add("**Staleness.** A clean scan of code nobody has touched in weeks says the repo "
            "is quiet, not that it is correct. Oldest HEADs:")
        add("")
        for repo, days in stalest:
            if days >= 14:
                add(f"- `{repo}` — last commit {days}d ago")
        add("")

    # ── Fix list ──────────────────────────────────────────────────────────────
    add("## Fix list — in priority order")
    add("")
    if blocking:
        add(f"### 🔴 Blocking — release-gate failures (§30) · {len(blocking)}")
        add("")
        add("_Never budget-limited. These block release._")
        add("")
        for repo, _, text, _ in blocking:
            add(f"<details><summary><code>{repo}</code></summary>")
            add("")
            add("```")
            L.extend(excerpt(text, "❌ FAIL", 40))
            add("```")
            add("</details>")
        add("")
    else:
        add("### 🔴 Blocking — none")
        add("")

    if shown:
        add(f"### 🟡 Advisory — {len(shown)} shown"
            + (f", {len(suppressed)} held back by the alarm budget" if suppressed else ""))
        add("")
        add("_Ranked by confidence first, then finding count. A HIGH-confidence structural "
            "finding outranks a pile of LOW-confidence regex hits over prose._")
        add("")
        for repo, _, text, evidence in shown:
            conf, count = severity(evidence)
            label = {3: "HIGH", 2: "MEDIUM", 1: "LOW"}.get(conf, "LOW")
            files = evidence.get("files_inspected", "?")
            add(f"<details><summary><code>{repo}</code> — {count} finding(s), "
                f"confidence {label}, {files} file(s) inspected</summary>")
            add("")
            add("```")
            L.extend(excerpt(text, "⚠️  WARN", 30))
            add("```")
            add("</details>")
        add("")

    if suppressed:
        add(f"### ⏸️ Held back by the alarm budget — {len(suppressed)}")
        add("")
        add(f"The budget is **{budget} advisory repos per run** "
            "(`vars.APN_ALARM_BUDGET`). These were ranked below the cut and are "
            "**not** written up today. They are listed so nothing is silently "
            "dropped — raise the budget or clear the queue above to reach them:")
        add("")
        for repo, _, _, evidence in suppressed:
            conf, count = severity(evidence)
            label = {3: "HIGH", 2: "MEDIUM", 1: "LOW"}.get(conf, "LOW")
            add(f"- `{repo}` — {count} finding(s), confidence {label}")
        add("")

    if clean:
        add(f"### 🟢 Clean — {len(clean)}")
        add("")
        add(", ".join(f"`{r[0]}`" for r in clean))
        add("")

    if unreachable:
        add(f"### ⚫ Unreachable — {len(unreachable)} · NOT a finding about these repos")
        add("")
        add("The scan could not read these. This says nothing about their state.")
        add("")
        add(", ".join(f"`{r[0]}`" for r in unreachable))
        add("")

    add("---")
    add("")
    add("Canonical cleanup register: "
        "[`apn-hub/EXECUTION_LEDGER.md`]"
        "(https://github.com/Fast-Clocks/apn-hub/blob/main/EXECUTION_LEDGER.md).")
    add("**Record outcomes there. Do not open a second tracking document (§7).**")

    pathlib.Path(out_path).write_text("\n".join(L) + "\n")

    print(f"blocking_count={len(blocking)}")
    print(f"advisory_count={len(advisory)}")
    print(f"suppressed_count={len(suppressed)}")
    print(f"vacuous_count={len(vacuous)}")
    print(f"files_inspected={total_files}")


if __name__ == "__main__":
    main()
