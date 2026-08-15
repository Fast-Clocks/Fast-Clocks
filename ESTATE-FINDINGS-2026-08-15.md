# APN estate findings — 14–15 Aug 2026

**Why this file exists.** These findings were written into the `apn-state-of-play`
skill three times and wiped each time — `~/.claude/skills/synced/` syncs *from* an
upstream source and overwrites local edits (confirmed: file rewritten 2026-08-15
04:03:50, all additions gone). Git is durable; the skill directory is not.

**Where this belongs.** Merge into **`apn-hub/EXECUTION_LEDGER.md`**, the canonical
cleanup register. Do not start another register.

---

## 0. Estate map correction — `list_repos` unfiltered, at session start

**There are 27 repos, not 8.** A filtered `list_repos(query:"apn")` returns 8 and
hides 19. A remote session is scoped to ONE repo by default and that scope is not
the estate.

On 14 Aug a session reviewed the Graphene architecture for an hour inside
`Fast-Clocks/Fast-Clocks` — a README-only profile stub — declared the architecture
absent, and recommended building from scratch. Most of it already existed.

Full list: `sovereign-suite-hub`, `perthsafepet`, `apn-provenance-keeper`,
`Fast-Clocks`, `apn-hub`, `filewitness`, `APN-Core-Site`, `privacy-widget`,
`signal-trail-vault`, `sovereign-evidence-factory`, `sovereign-showcase`,
`apn-hub-connect`, `inbox-flow-agent`, `apn-certification-machine`,
`product-archetype`, `apn-surgery-suite`, `pet-site-url-builder`,
`v0-sovereignty-lab-ui`, `privacy-scan`, `your-next-best-step`,
`australian-data-removal`, `account-audit`, `v0-claude-api-access`, `trace`,
`apn-vault`, `sovereign-forge`, `sovereign-tank` (**public**).

## 1. `apn-hub/EXECUTION_LEDGER.md` — the cleanup register already exists

Dated **10 July 2026**, status "Active — In Progress", **stalled five weeks**. It
already holds: 15 repos classified; 7 repos deleted with reasons; 6 compliance
fixes with commit SHAs (3× "military-grade" stripped from `account-audit` `6a79ed7`;
Google Fonts CDN removed from `sovereign-tank` `35e46c6`, `v0-sovereignty-lab-ui`
`19bf649`, `your-next-best-step` `464d0f5`, `apn-certification-machine` `2d1bddf`,
`apn-vault` `180d324`); Lovable→GitHub gap list; Vercel map.

Last line: **"Next Phase: Deep review of each remaining repo."** It is referenced
nowhere in continuity, which is why every session restarts the cleanup instead of
continuing it. **12 repos have appeared since 10 July and are unclassified in it.**

## 2. 🔴 `privacy-scan` could not build — FIXED, PR open

`package.json` on `main` carried unresolved git merge conflict markers
(`<<<<<<< HEAD` / `=======` / `>>>>>>> origin/fix/phase3-public-safety`). Invalid
JSON, so `npm ci`/`install`/`build`/`test` all failed. Org-wide search: exactly one
file affected.

Fixed in **`Fast-Clocks/privacy-scan` PR #8**, which also cleared what the working
build then exposed:
- a duplicate `BreachResult` interface contradicting the canonical `BreachItem`
- a date guard that never narrowed the value passed to `new Date()` — would have
  rendered "Invalid Date" instead of "Date unknown"
- `tests/stripe-safety.test.ts` used bare `describe/it/expect` with no
  `globals: true` — it failed typecheck and **was never executing**
- `npm run lint` exited **127, eslint was never a dependency** — QUALITY-GATE's
  mandatory lint step had never run once. Added ESLint 9 + eslint-config-next 16.

Verified locally: lint 0, typecheck 0, **59 tests passing**, build 0. Vercel
`trace-by-apn` and `executive-privacy` now deploy Ready.

**NOT PROVEN:** QUALITY-GATE's product checks (live domain, responsive, keyboard/
contrast, metadata, conversion path) have not been run.

## 3. `privacy-scan` and `trace` are the same codebase — but NOT equally healthy

Same dependency blocks, near-identical trees. The ledger lists them as two separate
products. **One canonical, one donor.**

**Corrected 15 Aug after actually running both.** An earlier note here assumed
`trace` carried the same defects as `privacy-scan` because they share a
`package.json`. It does not. Measured:

| | `privacy-scan` (before PR #8) | `trace` (before PR #1) |
|---|---|---|
| `package.json` valid | ❌ merge conflict markers | ✅ |
| `typecheck` | ❌ failed | ✅ **0** |
| `test` | ❌ never executed | ✅ **59 passing** |
| `lint` | ❌ exit 127 | ❌ exit 2 |
| `"name"` field | `my-project` (template default) | `trace` |

`trace` is the **healthier copy** and the better consolidation base. It also has the
branding (`public/brand/apn-primary.svg`, `apn-emblem.png`, `app/opengraph-image.tsx`)
and correctly gitignores `*.tsbuildinfo` — which `privacy-scan` has committed.

Two things found in `trace` and fixed in **`Fast-Clocks/trace` PR #1**:

- **`npm run lint` was worse than dead.** eslint was not a dependency, so the
  command fell through to whatever eslint sat on the machine's PATH — on the
  verification container, a *different major version* (10.1.0). Non-deterministic
  by machine, and lint had never once run. First real run surfaced 6 errors.
- **CI passed a test suite it never enforced.** `quality-gate.yml` had
  `continue-on-error: true` on Lint **and** Test, under a comment claiming neither
  was configured "(no eslint/vitest deps)". Half false: vitest *was* a dependency
  and 59 tests were passing, so a genuinely broken test would have reported green.
  A second false-green, in a different repo, in a different shape from the
  `$?`/`PIPESTATUS` one — found only by running the thing rather than reading it.

Verified after the fix, all four: lint 0, typecheck 0, 59 tests passing, build 0.
Vercel `sovereign-markets` (which builds from `trace`) deployed Ready from the PR.

## 4. `QUALITY-GATE.md` already exists — align to it, don't write another

In `privacy-scan` and `trace`. Mandatory engineering checks (`npm ci`, lint,
typecheck, test, build, no ignored TS errors, no fabricated claims, no committed
secrets, honest error states) plus product checks. Ends: **"A green Vercel build
alone is not approval."** `Fast-Clocks/scripts/apn-truth-scan.sh` should be treated
as its enforcement arm, not a competing standard.

## 5. `sovereign-evidence-factory` — best-engineered repo in the estate

Only repo using `.env.example` instead of a tracked `.env`; only one with
`SECURITY.md` + `LICENSE` + `research/` + `docs/` + `test/`. README claims **70/70
tests** incl. 3 red-team rounds and 9 adversarial cases (tamper, forged signature,
wrong-key-fails-closed, replay, offline timestamp, quarantine). **Claim not
independently verified — tests not run by Claude.**

Claims discipline is the house standard: *"Tamper-evident, not tamper-proof /
immutable / certified / government-approved"*, and *"no Australian regulator
mandates cryptographic tamper-evidence today."* States its own weakness (Ed25519
key in browser storage ≠ hardware-backed non-repudiation).

Explicitly **not** a fork of `apn-provenance-keeper`; backbone writes are
approval-gated through the locked `apn_record_receipt` RPC. Respect that boundary.
Has its own `CHRIS_ACTIONS.md` — read before asking Chris anything.

## 6. `apn-provenance-keeper` — evidence kernel, already built

20 tables, RLS on all 20, 42 policies, 12 edge functions. `events`,
`event_transitions`, `evidence`, `verification_records`, `checkpoints`, `epochs`,
`ledger_entries`, `signing_log`, `mirror_peers`, `mirror_checks`, `org_entitlements`,
`api_tokens`, `provider_stubs`. Functions: `admit-event`, `transition-event`,
`verify-chain`, `sign-manifest`, `issue-document-certificate`, `issue-verification`,
`mirror-check`, `public-ledger`, `public-key`, `head`.

`src/lib/merkle.ts` implements **RFC 6962** correctly (odd nodes carried up, never
duplicated), with a legacy variant retained and labelled CVE-2012-2459-vulnerable
for pre-v0.2 certificates. `epochs` + `checkpoints` + `mirror_peers` + `head` +
RFC 6962 = a Certificate-Transparency-grade verifiable log with independent mirrors.

**NOT PROVEN:** nothing here has been run, attacked or verified. Schema and code
inspected only. RLS existing ≠ RLS correct.

## 7. Credentials — one resolved, one open

- **`perthsafepet/.env.production` — BENIGN.** `VITE_PAYMENTS_CLIENT_TOKEN` holds a
  **Stripe publishable key** `pk_live_51SlrQ3KTqLnnhY8Y…` (matches
  `acct_1SlrQ3KTqLnnhY8Y`). Publishable keys ship in the browser by design. **Not an
  incident. No action.**
- **`sovereign-suite-hub/.env.production` — OPEN.** `VITE_PAYMENTS_CLIENT_TOKEN`
  holds a bare **`live_`**-prefixed value, 31 chars, **no `pk_` prefix** — not Stripe
  publishable format. Provider unidentified. Confirm with the issuer whether it is
  publishable; if not, it is compromised and needs rotating.

## 8. Two different things are called "Graphene"

- **Marketplace** — Codex 14–15 Aug concept: pseudonymous contribution marketplace,
  mission-locked governance, capped founder return. Paper design, Level 4–5.
- **Fabric** — the architecture packet: proof-carrying contract fabric over the
  50–60-site estate; deterministic gate kernel, capsules, receipts, membrane.

**Not the same product.** The fabric is what `apn-provenance-keeper` partially
implements. One name, two things, is how an estate grows fifteen filing machines.

## 9. Shells, not products

`apn-vault` and `apn-certification-machine` have byte-identical root listings
(`.gitignore`, `READ-FIRST.md`, `README.md`, 3 icons, `index.html`). `apn-vault`
self-reports "Static cover live (~25%)". Fill or archive.

## 10. Three orphaned Vercel projects fail on every commit

`apn-privacy-atlas`, `apn-hub-restored`, `public-access-hub` all build from
`Fast-Clocks/Fast-Clocks` — a repo containing one README — and error every push.
`apn-privacy-atlas` is in the ledger's **deleted** list (clone of apn-hub, deleted
July); the repo is gone, the Vercel project outlived it.

Recommend disconnecting all three. Nothing is lost — Vercel projects are
recreatable and hold no data. **This question was already asked by the "Go" session
on 14 Aug and left unanswered.**

## 11. Open / unverified — do not report as done

- `npm run lint` dead-by-missing-dependency: **confirmed in `trace`** (§3) and fixed.
  Still unchecked in the other Next.js repos in the estate.
- `privacy-scan` has `tsconfig.tsbuildinfo` committed and does not gitignore
  `*.tsbuildinfo`; `trace` does. Small, unfixed.
- `components/ui/use-mobile.tsx` in `privacy-scan` is byte-identical to
  `hooks/use-mobile.ts` and imported by nothing — dead duplicate.
- `account-audit` doubles as a document dump: 5 audit/handoff `.md` files dated
  27 Jun plus `APN_REVENUE_MACHINE.md`, `SOVEREIGN_TANK_DEPLOYMENT.md`.
- The estate-wide daily scan currently wants one broad cross-repo PAT. External
  review flagged the blast radius; per-repo or an allowlisted GitHub App is right.
- `scripts/apn-truth-scan.sh` is a low-level detector, **not** the scanner/risk
  engine of the architecture. The four gaps named here on 15 Aug — no
  inspected-object counts, no confidence, no evidence age, no estate alarm budget —
  are now **closed** (§12). What remains true: it is a static text scanner. It
  proves nothing about whether a product runs.

## 12. Evidence accounting and the estate alarm budget — built 15 Aug

The Graphene review's R-3 was the most likely real-world failure of the whole
thing, and it was still unbuilt: a scan that reports *findings* without reporting
*coverage* cannot be trusted, and a scan that raises more alarms than one person
can act on has failed even when every alarm is correct.

Four things now exist that did not:

**Inspected-object counts, per check.** Every verdict carries `↳ inspected N
object(s)`. This immediately exposed something that was invisible before: on
`Fast-Clocks` itself, **three of the green ticks inspected zero objects**. A PASS
over nothing looked exactly like a PASS over 400 files. The report now calls those
**vacuous passes** by name and tells the reader to treat them as UNKNOWN.

**Confidence, as a claim about method — not about feelings.**
`HIGH` = structural fact from git or the filesystem (a path is in the index, or it
is not). `MEDIUM` = literal match over a bounded surface (a hostname appears, or it
does not). `LOW` = regex over prose or markup, where meaning decides. LOW is
measured, not modest: every false positive corrected in this estate came from a LOW
check — `placeholder` matching a Tailwind class (10 bad hits in one repo),
`pk_live_` flagged when Stripe publishable keys are public by design, documentation
quoting a banned phrase in order to ban it.

**Evidence age.** Every scan records HEAD sha, date, and age in days. A clean scan
of code untouched for five weeks says the repo is quiet, not that it is correct —
`EXECUTION_LEDGER.md` stalled exactly that way without anyone noticing. Repos with
HEAD older than 14 days are surfaced in the report.

**The alarm budget.** `vars.APN_ALARM_BUDGET` (default 10) caps how many advisory
repos are written up per run, ranked by confidence first and finding count second.
Two rules keep it honest: blocking failures are **never** budget-limited, and
everything suppressed is **named and counted** in the report. Silent truncation
reads as "we covered everything" when we did not — the exact failure this scanner
exists to prevent.

`scripts/apn-estate-report.py` is the new half. The scanner writes machine-readable
evidence (`APN_SCAN_JSON`); the report ranks, budgets and states coverage before it
states results.

**Tested, not assumed:**
- 24-repo synthetic estate: budget 5 → 5 shown / 9 held and named; budget 0 → all
  14 held; budget 100 → none held; default → 10 shown / 4 held. Blocking never
  budgeted in any case. Empty results directory does not crash.
- End-to-end on four real repos + one simulated unreachable: 244 files inspected,
  vacuous repo correctly flagged while still listed clean, unreachable correctly
  separated from clean.
- The CI gate self-test still fires against the rewritten scanner: seeded blocking
  finding → exit 1, evidence records `FAIL`, while bare `$?` on the same pipeline
  still returns 0 — the original trap is still real and still caught.

**NOT PROVEN:** none of this has run in CI yet against the full 27-repo estate —
that needs `APN_ESTATE_TOKEN`, which is not set. Without it the daily scan silently
narrows to this one repo. The workflow warns loudly when that happens.
