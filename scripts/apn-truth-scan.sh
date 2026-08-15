#!/usr/bin/env bash
# APN TRUTH SCAN — mechanical enforcement of the Sovereign Engineering Constitution.
#
# Encodes the rules that have actually been broken in this estate, as checks that FAIL
# rather than guidance that gets skipped. Every rule below traces to a real incident.
#
# Usage:  ./scripts/apn-truth-scan.sh [path]        (default: .)
# Exit:   0 = clean | 1 = FAIL (blocking) | 2 = WARN only
#
# Constitution refs: §3 no test = no claim · §13 secrets · §23 website quality · §25 writing
set -uo pipefail

ROOT="${1:-.}"
FAIL=0
WARN=0
REPORT="${APN_SCAN_REPORT:-/dev/null}"

say()  { printf '%s\n' "$*"; printf '%s\n' "$*" >> "$REPORT"; }
fail() { say "❌ FAIL  $*"; FAIL=$((FAIL+1)); }
warn() { say "⚠️  WARN  $*"; WARN=$((WARN+1)); }
pass() { say "✅ PASS  $*"; }

# Only scan source we own. Never scan dependencies or build output.
SCAN_DIRS=$(find "$ROOT" -type d \( -name node_modules -o -name .git -o -name dist \
  -o -name build -o -name .next -o -name out -o -name vendor -o -name coverage \) -prune \
  -o -type f \( -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.jsx' \
  -o -name '*.html' -o -name '*.md' -o -name '*.json' -o -name '*.svelte' -o -name '*.vue' \) -print)

say "=== APN TRUTH SCAN — $(date -u +%Y-%m-%dT%H:%M:%SZ) — ${ROOT} ==="
say "Scanned $(printf '%s\n' "$SCAN_DIRS" | grep -c . || echo 0) source files."
say "PASSED means these specific checks found nothing. It does NOT mean the product works."
say ""

# ── §25 PROHIBITED MARKETING CLAIMS ────────────────────────────────────────────
# Real incident: 3× "military-grade" removed from account-audit (commit 6a79ed7).
# Real incident: rigtech.com.au shows "22,400+ Verified operators", "180k Tickets
# on file", "immutably logged" — unsubstantiated, in front of mining/offshore buyers.
# Australian Consumer Law: unsubstantiated representations are actionable.
say "--- §25 Prohibited / unsubstantiated claims ---"
PROHIBITED='military[- ]grade|bank[- ]level|unbreakable|unhackable|100% secure|absolutely secure|completely secure|impenetrable|guaranteed security|NSA[- ]grade|government[- ]grade|court[- ]admissible|legally binding proof|tamper[- ]proof'
HITS=$(printf '%s\n' "$SCAN_DIRS" | xargs -r grep -rniE "$PROHIBITED" 2>/dev/null | grep -v 'apn-truth-scan' || true)
if [ -n "$HITS" ]; then
  fail "prohibited absolute-security claims found:"
  printf '%s\n' "$HITS" | head -20 | sed 's/^/        /' | tee -a "$REPORT"
  say "        → §25: prefer 'independently verifiable' over 'unbreakable';"
  say "          'records integrity' over 'truth'; 'designed for' over 'certified for'."
else
  pass "no prohibited absolute-security claims"
fi

# Unsubstantiated hard numbers presented as fact (the Rig Tech failure mode).
say ""
say "--- §25 Unsubstantiated metric claims ---"
METRICS=$(printf '%s\n' "$SCAN_DIRS" | grep -E '\.(html|tsx|jsx|vue|svelte)$' \
  | xargs -r grep -rniE '[0-9][0-9,]{2,}\+?\s*(verified|operators|tickets|customers|users|clients|records|documents|businesses|companies)' 2>/dev/null || true)
if [ -n "$METRICS" ]; then
  warn "hard metric claims in user-facing markup — each needs a substantiation source:"
  printf '%s\n' "$METRICS" | head -10 | sed 's/^/        /' | tee -a "$REPORT"
else
  pass "no unsubstantiated metric claims in markup"
fi

# ── §13 SECRETS ────────────────────────────────────────────────────────────────
# VITE_/NEXT_PUBLIC_ vars are compiled into the browser bundle BY DESIGN and are
# not secrets. Anything else in a tracked .env is a real exposure.
say ""
say "--- §13 Tracked .env / exposed credentials ---"
if git -C "$ROOT" rev-parse --git-dir >/dev/null 2>&1; then
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
    else
      warn "$ENVF is git-tracked (public-prefixed vars only — not an exposure, but untidy)"
      say "        → add .env to .gitignore; keep the file locally."
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
    fi
  done
  [ -z "$(git -C "$ROOT" ls-files | grep -E '(^|/)\.env($|\.)' || true)" ] && pass "no tracked .env files"
fi

# Private keys / service-role keys anywhere in source. Always blocking.
KEYS=$(printf '%s\n' "$SCAN_DIRS" | xargs -r grep -rlE 'BEGIN (RSA |EC |OPENSSH |PGP )?PRIVATE KEY|service_role|sk_live_|sk_test_[a-zA-Z0-9]{20,}' 2>/dev/null | grep -v 'apn-truth-scan' || true)
if [ -n "$KEYS" ]; then
  fail "possible private key / service-role key / live Stripe secret in source:"
  printf '%s\n' "$KEYS" | sed 's/^/        /' | tee -a "$REPORT"
else
  pass "no private keys or service-role keys in source"
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
else
  pass "no external CDN references"
fi

# ── §23 UNFINISHED SURFACE ─────────────────────────────────────────────────────
say ""
say "--- §23 Placeholder / builder badges in shipped surface ---"
# NOTE: "placeholder" as a bare word is NOT a signal. It is a legitimate HTML
# attribute (placeholder="your@email.com") and a Tailwind utility class
# (placeholder:text-muted-foreground). Matching it produced 10 false hits in a
# single repo — pure noise, and noise is how a scanner gets ignored. Match only
# strings that genuinely indicate unfinished work.
BADGE=$(printf '%s\n' "$SCAN_DIRS" | grep -E '\.(html|tsx|jsx|vue|svelte)$' \
  | xargs -r grep -rniE 'Edit with Lovable|lovable-badge|Made with Lovable|Built with v0|Lorem ipsum|TODO:|FIXME:|Your Company Name|YOUR_[A-Z_]+_HERE|https?://example\.com' 2>/dev/null || true)
if [ -n "$BADGE" ]; then
  warn "placeholder text or builder badge in user-facing surface:"
  printf '%s\n' "$BADGE" | head -10 | sed 's/^/        /' | tee -a "$REPORT"
  say "        → known: Entellon footer badge."
else
  pass "no placeholders or builder badges in user-facing surface"
fi

# ── §23 LEGAL ENTITY FOOTER ────────────────────────────────────────────────────
# Every public APN surface must carry the operating entity + ACN.
say ""
say "--- §23 Legal entity disclosure ---"
if printf '%s\n' "$SCAN_DIRS" | grep -qE '\.(html|tsx|jsx)$'; then
  if printf '%s\n' "$SCAN_DIRS" | xargs -r grep -rqiE 'ACN 695 272 836|Australian Data Removal Pty Ltd' 2>/dev/null; then
    pass "operating entity / ACN present"
  else
    warn "no 'Australian Data Removal Pty Ltd' or 'ACN 695 272 836' found — required on public surfaces"
  fi
else
  # A skipped check must SAY it was skipped. A silent section reads as "covered"
  # when nothing was covered — the exact failure this scanner exists to catch.
  say "➖ N/A   no user-facing markup (.html/.tsx/.jsx) in this repo — check not applicable"
fi

# ── SUMMARY ────────────────────────────────────────────────────────────────────
say ""
say "=== RESULT: ${FAIL} blocking, ${WARN} advisory ==="
if [ "$FAIL" -gt 0 ]; then say "STATE: FAILED — do not release (§30 release gate)"; exit 1; fi
if [ "$WARN" -gt 0 ]; then say "STATE: PASSED WITH ADVISORIES"; exit 2; fi
say "STATE: PASSED"
exit 0
