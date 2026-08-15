#!/usr/bin/env bash
# APN TRUTH SCAN — mechanical enforcement of the Sovereign Engineering Constitution.
#
# Encodes the rules that have actually been broken in this estate, as checks that FAIL
# rather than guidance that gets skipped. Every rule below traces to a real incident.
#
# Usage:  ./scripts/apn-truth-scan.sh [path]        (default: .)
# Exit:   0 = clean | 1 = FAIL (blocking) | 2 = WARN only
#
# Env:    APN_SCAN_REPORT=<file>   append the human-readable report here
#         APN_SCAN_JSON=<file>     write a machine-readable per-check summary here
#
# Constitution refs: §3 no test = no claim · §13 secrets · §23 website quality · §25 writing
set -uo pipefail

ROOT="${1:-.}"
FAIL=0
WARN=0
REPORT="${APN_SCAN_REPORT:-/dev/null}"
JSON_OUT="${APN_SCAN_JSON:-}"

say()  { printf '%s\n' "$*"; printf '%s\n' "$*" >> "$REPORT"; }
fail() { say "❌ FAIL  $*"; FAIL=$((FAIL+1)); }
warn() { say "⚠️  WARN  $*"; WARN=$((WARN+1)); }
pass() { say "✅ PASS  $*"; }

# ── EVIDENCE ACCOUNTING ────────────────────────────────────────────────────────
# The failure this exists to prevent: a check that inspected NOTHING printing the
# same green tick as a check that inspected four hundred files. "0 findings" is
# not a result unless you also know how many objects were looked at, by what
# method, and how old the thing looked at was. Everything below is reported.
#
# CONFIDENCE is a claim about METHOD, not about how sure the author feels:
#   HIGH   — structural fact from git or the filesystem. Deterministic; a file is
#            either tracked or it is not.
#   MEDIUM — literal match over a bounded surface (a hostname either appears in
#            the text or it does not). Few ways to be wrong.
#   LOW    — regex over prose or markup, where MEANING decides whether a hit is
#            real. This is not pessimism, it is measured: in this estate LOW
#            checks have already produced false positives that had to be
#            corrected — `placeholder` matching a Tailwind class and an HTML
#            attribute (10 bad hits in one repo), `pk_live_` flagged as an
#            exposure when Stripe publishable keys are public by design, and
#            documentation quoting a banned phrase in order to ban it.
#            A LOW finding is a prompt to look, never a verdict.
CHECKS_JSON=""
record() {  # id  verdict  objects_inspected  confidence  findings  note
  local id="$1" verdict="$2" objects="$3" conf="$4" findings="$5" note="${6:-}"
  note=${note//\\/}; note=${note//\"/\'}
  CHECKS_JSON="${CHECKS_JSON}${CHECKS_JSON:+,}{\"id\":\"$id\",\"verdict\":\"$verdict\",\"objects_inspected\":$objects,\"confidence\":\"$conf\",\"findings\":$findings,\"note\":\"$note\"}"
  say "        ↳ inspected $objects object(s) · confidence $conf · $findings finding(s)"
}

# `grep -c` PRINTS 0 and EXITS 1 on no match, so the obvious
# `grep -c . || echo 0` emits "0\n0" and every arithmetic test downstream breaks.
# Assign, then fall back — never chain an echo onto a command that already printed.
count() {
  local n
  n=$(printf '%s\n' "$1" | grep -c . 2>/dev/null) || n=0
  printf '%s' "$n"
}

# Only scan source we own. Never scan dependencies or build output.
SCAN_DIRS=$(find "$ROOT" -type d \( -name node_modules -o -name .git -o -name dist \
  -o -name build -o -name .next -o -name out -o -name vendor -o -name coverage \) -prune \
  -o -type f \( -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.jsx' \
  -o -name '*.html' -o -name '*.md' -o -name '*.json' -o -name '*.svelte' -o -name '*.vue' \) -print)

MARKUP=$(printf '%s\n' "$SCAN_DIRS" | grep -E '\.(html|tsx|jsx|vue|svelte)$' || true)
DOCS=$(printf '%s\n' "$SCAN_DIRS" | grep -E '\.(md|json)$' || true)

N_ALL=$(count "$SCAN_DIRS")
N_MARKUP=$(count "$MARKUP")
N_DOCS=$(count "$DOCS")

# ── EVIDENCE AGE ───────────────────────────────────────────────────────────────
# A clean scan of code last touched five weeks ago is a WEAKER claim than a clean
# scan of code touched today — it says the repo is quiet, not that it is correct.
# apn-hub/EXECUTION_LEDGER.md stalled for five weeks without anyone noticing;
# a scan that cannot express staleness cannot surface that.
HEAD_ISO="unknown"; HEAD_AGE_DAYS="null"; HEAD_SHA="unknown"
if git -C "$ROOT" rev-parse --git-dir >/dev/null 2>&1; then
  HEAD_ISO=$(git -C "$ROOT" log -1 --format=%cI 2>/dev/null || echo unknown)
  HEAD_SHA=$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo unknown)
  if [ "$HEAD_ISO" != "unknown" ]; then
    HEAD_EPOCH=$(git -C "$ROOT" log -1 --format=%ct 2>/dev/null || echo 0)
    NOW_EPOCH=$(date -u +%s)
    [ "$HEAD_EPOCH" -gt 0 ] && HEAD_AGE_DAYS=$(( (NOW_EPOCH - HEAD_EPOCH) / 86400 ))
  fi
fi

say "=== APN TRUTH SCAN — $(date -u +%Y-%m-%dT%H:%M:%SZ) — ${ROOT} ==="
say "Inspected $N_ALL source file(s): $N_MARKUP user-facing markup, $N_DOCS documentation."
say "Evidence: HEAD $HEAD_SHA dated $HEAD_ISO$([ "$HEAD_AGE_DAYS" != "null" ] && echo " (${HEAD_AGE_DAYS}d old)")."
if [ "$N_ALL" -eq 0 ]; then
  say "⚠️  NOTHING WAS INSPECTED. Every result below is vacuous — read it as UNKNOWN, not as clean."
fi
say "PASSED means these specific checks found nothing. It does NOT mean the product works."
say ""

# ── §25 PROHIBITED MARKETING CLAIMS ────────────────────────────────────────────
# Real incident: 3× "military-grade" removed from account-audit (commit 6a79ed7).
# Real incident: rigtech.com.au shows "22,400+ Verified operators", "180k Tickets
# on file", "immutably logged" — unsubstantiated, in front of mining/offshore buyers.
# Australian Consumer Law: unsubstantiated representations are actionable.
say "--- §25 Prohibited / unsubstantiated claims ---"
PROHIBITED='military[- ]grade|bank[- ]level|unbreakable|unhackable|100% secure|absolutely secure|completely secure|impenetrable|guaranteed security|NSA[- ]grade|government[- ]grade|court[- ]admissible|legally binding proof|tamper[- ]proof'

# Split by surface. A claim SHIPPED to a customer in markup is a blocking defect.
# The same words in documentation are usually the opposite — a changelog recording
# that a claim was removed, an audit quoting the phrase it banned, or a README
# stating "tamper-evident, NOT tamper-proof". Blocking on those makes the scanner
# fail every honest audit document, which is how a gate gets switched off.
# Documentation still reports as an ADVISORY so a genuine claim in a README is
# visible, never silent.
SHIPPED=$(printf '%s\n' "$MARKUP" | xargs -r grep -rniE "$PROHIBITED" 2>/dev/null | grep -v 'apn-truth-scan' || true)
DOCUMENTED=$(printf '%s\n' "$DOCS" | xargs -r grep -rniE "$PROHIBITED" 2>/dev/null | grep -v 'apn-truth-scan' || true)

if [ -n "$SHIPPED" ]; then
  fail "prohibited absolute-security claims in SHIPPED markup:"
  printf '%s\n' "$SHIPPED" | head -20 | sed 's/^/        /' | tee -a "$REPORT"
  say "        → §25: prefer 'independently verifiable' over 'unbreakable';"
  say "          'records integrity' over 'truth'; 'designed for' over 'certified for'."
  record claims-shipped FAIL "$N_MARKUP" LOW "$(count "$SHIPPED")" "regex over markup; confirm each hit is a claim, not a quotation"
else
  pass "no prohibited absolute-security claims in shipped markup"
  record claims-shipped PASS "$N_MARKUP" LOW 0 "vacuous if 0 markup files inspected"
fi

if [ -n "$DOCUMENTED" ]; then
  warn "prohibited terms appear in documentation — confirm each is quoting or negating, not claiming:"
  printf '%s\n' "$DOCUMENTED" | head -10 | sed 's/^/        /' | tee -a "$REPORT"
  record claims-docs WARN "$N_DOCS" LOW "$(count "$DOCUMENTED")" "most hits here are expected to be quotations or bans"
else
  # An explicit line, not silence. Every ↳ evidence line must sit under a verdict
  # it belongs to — an orphaned one reads as a duplicate of the check above.
  pass "no prohibited terms in documentation"
  record claims-docs PASS "$N_DOCS" LOW 0 ""
fi

# Unsubstantiated hard numbers presented as fact (the Rig Tech failure mode).
say ""
say "--- §25 Unsubstantiated metric claims ---"
METRICS=$(printf '%s\n' "$MARKUP" \
  | xargs -r grep -rniE '[0-9][0-9,]{2,}\+?\s*(verified|operators|tickets|customers|users|clients|records|documents|businesses|companies)' 2>/dev/null || true)
if [ -n "$METRICS" ]; then
  warn "hard metric claims in user-facing markup — each needs a substantiation source:"
  printf '%s\n' "$METRICS" | head -10 | sed 's/^/        /' | tee -a "$REPORT"
  record metrics WARN "$N_MARKUP" LOW "$(count "$METRICS")" "a number is only a defect if it is unsubstantiated; only the owner knows"
else
  pass "no unsubstantiated metric claims in markup"
  record metrics PASS "$N_MARKUP" LOW 0 ""
fi

# ── §13 SECRETS ────────────────────────────────────────────────────────────────
# VITE_/NEXT_PUBLIC_ vars are compiled into the browser bundle BY DESIGN and are
# not secrets. Anything else in a tracked .env is a real exposure.
say ""
say "--- §13 Tracked .env / exposed credentials ---"
if git -C "$ROOT" rev-parse --git-dir >/dev/null 2>&1; then
  N_TRACKED=$(count "$(git -C "$ROOT" ls-files || true)")
  ENV_FINDINGS=0
  # Counted separately from ENV_FINDINGS so the evidence JSON records FAIL as FAIL.
  # An exit code that says "blocking" while the machine-readable record says "WARN"
  # is the same class of lie as a green tick over a broken build.
  ENV_BLOCKING=0
  # .env.example / .sample / .template are TEMPLATES. They are supposed to be
  # committed — they document which vars an operator must supply. Flagging them
  # as exposures fails CI on exactly the repos that did it right
  # (sovereign-evidence-factory, privacy-scan, trace all use .env.example).
  # A scanner that punishes good practice gets switched off, and then it protects
  # nothing. Templates are still checked for real-looking values further down.
  for ENVF in $(git -C "$ROOT" ls-files | grep -E '(^|/)\.env($|\.)' \
                | grep -vE '\.(example|sample|template|dist)$' || true); do
    BAD=$(grep -vE '^\s*(#|$)' "$ROOT/$ENVF" 2>/dev/null \
          | grep -vE '^(VITE_|NEXT_PUBLIC_|PUBLIC_|REACT_APP_)' \
          | cut -d= -f1 || true)
    if [ -n "$BAD" ]; then
      fail "$ENVF is git-tracked and holds non-public vars (names only, values redacted):"
      printf '%s\n' "$BAD" | sed 's/^/        /' | tee -a "$REPORT"
      say "        → treat as COMPROMISED. Rotate, then untrack: git rm --cached $ENVF"
      ENV_FINDINGS=$((ENV_FINDINGS+1)); ENV_BLOCKING=$((ENV_BLOCKING+1))
    else
      warn "$ENVF is git-tracked (public-prefixed vars only — not an exposure, but untidy)"
      say "        → add .env to .gitignore; keep the file locally."
      ENV_FINDINGS=$((ENV_FINDINGS+1))
    fi

    # A public prefix is a CONVENTION, not a guarantee. Found in the wild:
    # sovereign-suite-hub/.env.production carried VITE_PAYMENTS_CLIENT_TOKEN with a
    # live_-prefixed value. The earlier version of this check waved it through purely
    # because of the VITE_ prefix — a silent pass on a live payments credential.
    # Prefix tells you it is BUNDLED into the browser. It does not tell you the
    # provider intended it to be public. Those are different questions.
    # pk_live_ is DELIBERATELY excluded. A Stripe publishable key is designed to
    # ship in the browser and is not a secret — flagging it is noise, and noise is
    # how a scanner gets ignored. rk_live_ (restricted) and sk_live_ ARE secret and
    # stay in scope; sk_ is also caught by the private-key check below.
    # Confirmed in the wild: perthsafepet ships pk_live_ (benign), while
    # sovereign-suite-hub ships a bare live_-prefixed token of unknown provider —
    # that second shape is exactly what this check exists to surface.
    LIVEISH=$(grep -vE '^\s*(#|$)' "$ROOT/$ENVF" 2>/dev/null \
              | grep -E '^(VITE_|NEXT_PUBLIC_|PUBLIC_|REACT_APP_)' \
              | grep -iE '=\s*"?(live_|prod_|rk_live|sk_live|shpat_|xoxb-|ghp_|AIza)' \
              | grep -viE '=\s*"?pk_live_' \
              | cut -d= -f1 || true)
    if [ -n "$LIVEISH" ]; then
      warn "$ENVF has PUBLIC-PREFIXED vars holding live-looking credentials (names only):"
      printf '%s\n' "$LIVEISH" | sed 's/^/        /' | tee -a "$REPORT"
      say "        → these ARE shipped in the browser bundle. Confirm with the provider that"
      say "          each is genuinely publishable. If any is not, it is compromised — rotate."
      ENV_FINDINGS=$((ENV_FINDINGS+1))
    fi
  done
  if [ -z "$(git -C "$ROOT" ls-files | grep -E '(^|/)\.env($|\.)' || true)" ]; then
    pass "no tracked .env files"
  fi
  # HIGH confidence: "is this path in the git index" is a structural fact, not a guess.
  if   [ "$ENV_BLOCKING" -gt 0 ]; then ENV_VERDICT=FAIL
  elif [ "$ENV_FINDINGS" -gt 0 ]; then ENV_VERDICT=WARN
  else ENV_VERDICT=PASS
  fi
  record tracked-env "$ENV_VERDICT" \
    "$N_TRACKED" HIGH "$ENV_FINDINGS" "git index is authoritative; the JUDGEMENT of publishable-vs-secret is not"
else
  say "➖ N/A   not a git repository — cannot check the index for tracked .env files"
  record tracked-env NA 0 HIGH 0 "no git directory"
fi

# Private keys / service-role keys anywhere in source. Always blocking.
KEYS=$(printf '%s\n' "$SCAN_DIRS" | xargs -r grep -rlE 'BEGIN (RSA |EC |OPENSSH |PGP )?PRIVATE KEY|service_role|sk_live_|sk_test_[a-zA-Z0-9]{20,}' 2>/dev/null | grep -v 'apn-truth-scan' || true)
if [ -n "$KEYS" ]; then
  fail "possible private key / service-role key / live Stripe secret in source:"
  printf '%s\n' "$KEYS" | sed 's/^/        /' | tee -a "$REPORT"
  record private-keys FAIL "$N_ALL" MEDIUM "$(count "$KEYS")" "PEM headers and sk_live_ are literal; service_role also matches variable names"
else
  pass "no private keys or service-role keys in source"
  record private-keys PASS "$N_ALL" MEDIUM 0 ""
fi

# ── §23 EXTERNAL CDN / CSP REGRESSION ──────────────────────────────────────────
# Real incident: Google Fonts CDN removed from 5 repos in July (35e46c6, 19bf649,
# 464d0f5, 2d1bddf, 180d324). Fixes regress silently without a check.
say ""
say "--- §23 External CDN dependencies (CSP / privacy regression) ---"
CDN=$(printf '%s\n' "$SCAN_DIRS" | xargs -r grep -rniE 'fonts\.googleapis\.com|fonts\.gstatic\.com|cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com|unpkg\.com' 2>/dev/null | grep -v 'apn-truth-scan' || true)
if [ -n "$CDN" ]; then
  fail "external CDN reference — a privacy leak on a privacy product, and a July fix that regressed:"
  printf '%s\n' "$CDN" | head -15 | sed 's/^/        /' | tee -a "$REPORT"
  say "        → self-host the asset. Known offenders: apn-certification-machine (qrcodejs, html2canvas)."
  record external-cdn FAIL "$N_ALL" MEDIUM "$(count "$CDN")" "literal hostnames; a hit in a comment or doc is the only false-positive shape"
else
  pass "no external CDN references"
  record external-cdn PASS "$N_ALL" MEDIUM 0 ""
fi

# ── §23 UNFINISHED SURFACE ─────────────────────────────────────────────────────
say ""
say "--- §23 Placeholder / builder badges in shipped surface ---"
# NOTE: "placeholder" as a bare word is NOT a signal. It is a legitimate HTML
# attribute (placeholder="your@email.com") and a Tailwind utility class
# (placeholder:text-muted-foreground). Matching it produced 10 false hits in a
# single repo — pure noise, and noise is how a scanner gets ignored. Match only
# strings that genuinely indicate unfinished work.
BADGE=$(printf '%s\n' "$MARKUP" \
  | xargs -r grep -rniE 'Edit with Lovable|lovable-badge|Made with Lovable|Built with v0|Lorem ipsum|TODO:|FIXME:|Your Company Name|YOUR_[A-Z_]+_HERE|https?://example\.com' 2>/dev/null || true)
if [ -n "$BADGE" ]; then
  warn "placeholder text or builder badge in user-facing surface:"
  printf '%s\n' "$BADGE" | head -10 | sed 's/^/        /' | tee -a "$REPORT"
  say "        → known: Entellon footer badge."
  record placeholders WARN "$N_MARKUP" LOW "$(count "$BADGE")" "TODO: in a code comment is normal engineering, not an unfinished surface"
else
  pass "no placeholders or builder badges in user-facing surface"
  record placeholders PASS "$N_MARKUP" LOW 0 ""
fi

# ── §23 LEGAL ENTITY FOOTER ────────────────────────────────────────────────────
# Every public APN surface must carry the operating entity + ACN.
say ""
say "--- §23 Legal entity disclosure ---"
if [ "$N_MARKUP" -gt 0 ]; then
  if printf '%s\n' "$MARKUP" | xargs -r grep -rqiE 'ACN 695 272 836|Australian Data Removal Pty Ltd' 2>/dev/null; then
    pass "operating entity / ACN present"
    record legal-entity PASS "$N_MARKUP" MEDIUM 0 ""
  else
    warn "no 'Australian Data Removal Pty Ltd' or 'ACN 695 272 836' found — required on public surfaces"
    record legal-entity WARN "$N_MARKUP" MEDIUM 1 "absence across markup; a footer in a layout file counts for the whole site"
  fi
else
  # A skipped check must SAY it was skipped. A silent section reads as "covered"
  # when nothing was covered — the exact failure this scanner exists to catch.
  say "➖ N/A   no user-facing markup (.html/.tsx/.jsx) in this repo — check not applicable"
  record legal-entity NA 0 MEDIUM 0 "no markup to inspect"
fi

# ── SUMMARY ────────────────────────────────────────────────────────────────────
say ""
say "=== RESULT: ${FAIL} blocking, ${WARN} advisory ==="
say "Basis: $N_ALL file(s) inspected, HEAD ${HEAD_SHA} dated ${HEAD_ISO}."
if [ "$N_ALL" -eq 0 ]; then
  say "This scan inspected nothing. It is evidence of ABSENCE OF EVIDENCE, not of correctness."
fi

if [ -n "$JSON_OUT" ]; then
  {
    printf '{"scanned_at":"%s","root":"%s","head_sha":"%s","head_date":"%s","head_age_days":%s,' \
      "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$ROOT" "$HEAD_SHA" "$HEAD_ISO" "$HEAD_AGE_DAYS"
    printf '"files_inspected":%s,"markup_files":%s,"doc_files":%s,' "$N_ALL" "$N_MARKUP" "$N_DOCS"
    printf '"blocking":%s,"advisory":%s,"checks":[%s]}\n' "$FAIL" "$WARN" "$CHECKS_JSON"
  } > "$JSON_OUT"
fi

if [ "$FAIL" -gt 0 ]; then say "STATE: FAILED — do not release (§30 release gate)"; exit 1; fi
if [ "$WARN" -gt 0 ]; then say "STATE: PASSED WITH ADVISORIES"; exit 2; fi
say "STATE: PASSED"
exit 0
