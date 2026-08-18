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
  **Partly addressed:** `apn-self-heal.yml` now refuses any repo not named in
  `vars.APN_HEAL_ALLOWLIST` (fail-closed, default empty, refusals announced). The
  daily scan documents the required read-only token shape. Neither replaces the
  App; both narrow the damage a broad token can do.
- 🟥 **`apn-self-heal.yml` and `apn-daily-estate-scan.yml` have NEVER EXECUTED.**
  Both are `schedule`/`workflow_dispatch` only, and neither file exists on `main`
  yet — GitHub will not dispatch a workflow that is not on the default branch, so
  they cannot even be triggered manually until PR #6 merges. What has actually been
  proven is narrower than it looks: the YAML parses, and the allowlist shell logic
  was dry-run by hand across three cases (empty allowlist permits only self; a
  two-repo allowlist permits exactly those; `privacy-scan` does not match
  `privacy-scan-old`). **Dry-running the logic is not running the workflow.** Do
  not describe this automation as working. First real evidence will be the first
  scheduled run after #6 merges, and it should be read sceptically.
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

## 13. 🔴 9 high-severity Next.js advisories, live in both copies — FIXED, PRs open

Found by reading the `npm ci` output that the repaired `privacy-scan` build finally
produced. Nearly dismissed as "transitive and unreachable" — that assumption was
wrong, and checking it took two minutes.

`next@16.2.6` in **both** `privacy-scan` and `trace` carried 9 high advisories,
all fixed in 16.2.11. npm reports the fix (16.3.1) as **`isSemVerMajor: false`** —
a minor bump inside 16.x, not the breaking upgrade the caution assumed.

Reachable, on a privacy product:

- **GHSA-68g3-v927-f742 / GHSA-4633-3j49-mh5q — cache confusion of response bodies
  for requests WITH bodies.** Both repos have **13 POST route handlers**, including
  `/api/breach` and `/api/scan/{breach,email,domain,wallet}`. On a breach-scanning
  endpoint that is one person's breach results served to another. That is a privacy
  incident shape, not a theoretical CVE.
- GHSA-q8wf-6r8g-63ch — DoS in Image Optimization via SVGs (`trace` ships
  `public/brand/apn-primary.svg`).
- GHSA-p9j2-gv94-2wf4 SSRF in rewrites; GHSA-955p-x3mx-jcvp unauthenticated
  disclosure of internal Server Function endpoints; GHSA-4c39-4ccg-62r3 unbounded
  Server Action payload in the Edge runtime (`app/opengraph-image.tsx` sets
  `runtime = 'edge'`).

Transitive `postcss` and `sharp` highs resolve through the same bump.

Fixed in **`trace` PR #1** and **`privacy-scan` PR #8**. Both repos also gained
`.github/dependabot.yml`, copied verbatim from `Fast-Clocks` — **neither had any
dependency automation**, which is the actual reason 9 highs sat unnoticed. That is
the recurrence fix; the version bump is only today's fix.

**Deliberately not fixed:** 1 LOW remains in both — esbuild arbitrary file read
running the DEV server ON WINDOWS. Not reachable in this deployment (Linux/Vercel,
production build). Left rather than churn the lockfile.

**Verified, both repos, after the bump:** lint 0, typecheck 0, 59 tests passing,
build 0, `npm audit` 0 high / 0 critical. CI `validate` **success** on both PR heads
(`trace` d6d9ae1, `privacy-scan` 1565469). Vercel Ready: `sovereign-markets`,
`trace-by-apn`, `executive-privacy`.

**NOT PROVEN:** no live deployment was tested. QUALITY-GATE's product checks have
still not been run on either.

**Open question for the estate:** how many of the other Next.js repos are on a
vulnerable version? Only these two were checked. Nothing else has Dependabot either.

## 14. 🔴 ESTATE-WIDE SWEEP — 9 repos on vulnerable Next.js, not 2

The open question from §13 ("how many of the other repos?") is now answered. All
27 repos were swept by reading `package.json` directly. **Seven more repos carry
the same 9 high-severity Next.js advisories.** Every version below is inside the
vulnerable range `>=16.0.0 <16.2.11`.

| repo | `next` | lint | ships | status |
|---|---|---|---|---|
| `privacy-scan` | 16.2.6 | ❌ exit 127 | Stripe | ✅ **FIXED** — PR #8 |
| `trace` | 16.2.6 | ❌ exit 2 | Stripe | ✅ **FIXED** — PR #1 |
| `apn-hub` | **16.2.7** | ✅ eslint pinned | Supabase | 🔴 open |
| `APN-Core-Site` | **16.2.6** | ❌ dead | Stripe | 🔴 open |
| `account-audit` | **16.2.6** | ❌ dead | Stripe | 🔴 open |
| `v0-claude-api-access` | **16.2.6** | ❌ dead | — | 🔴 open |
| `australian-data-removal` | **16.2.0** | ❌ dead | Stripe + Resend | 🔴 open |
| `v0-sovereignty-lab-ui` | **16.1.6** | ❌ `next lint` | — | 🔴 open |
| `sovereign-tank` | **16.1.6** | ❌ `next lint` | — | 🔴 open · **PUBLIC REPO** |

`next@16.3.1` fixes all nine and npm reports it `isSemVerMajor: false` — a minor
bump inside 16.x, verified non-breaking on two repos already.

**The dead-lint pattern is 8 repos, not 1.** Every Next.js repo in the estate
except `apn-hub` has a `lint` script with no `eslint` dependency. Two variants:
- six declare `"lint": "eslint ."` with eslint absent → exit 127, or worse,
  silently picks up whatever eslint is on the machine's PATH;
- `v0-sovereignty-lab-ui` and `sovereign-tank` declare `"lint": "next lint"`,
  **removed in Next 16**. Dead by a different route, same result.

`apn-hub` is the counter-example and the model: eslint + `eslint-config-next`
both pinned, and it has real tests (`node --test`). It is still on a vulnerable
`next` — being well-configured did not save it, because nothing was watching.

**Not affected (14 repos):** every Vite/TanStack app —`sovereign-suite-hub`,
`perthsafepet`, `filewitness`, `signal-trail-vault`, `sovereign-showcase`,
`apn-hub-connect`, `inbox-flow-agent`, `product-archetype`, `apn-surgery-suite`,
`pet-site-url-builder`, `your-next-best-step`, `sovereign-forge`,
`privacy-widget`, `apn-provenance-keeper`. No `next` dependency, and **all of them
have eslint correctly in devDependencies**. The Lovable/TanStack template is
better configured than the v0/Next one.

`sovereign-evidence-factory` remains the best-engineered repo: **zero runtime
dependencies**, `node --test`, no lint theatre. Nothing to patch.

`apn-vault` and `apn-certification-machine` have **no `package.json`** —
confirming §9, they are static shells, not applications.

**Dependency automation: 3 of 27 repos.** Only `Fast-Clocks`, `trace` and
`privacy-scan` have `.github/dependabot.yml`, and two of those were added today.
That is the actual root cause. The version bumps fix today; Dependabot is what
stops the estate drifting back.

**METHOD / LIMITS — read before acting.** This was a static read of each
`package.json` on the default branch. Nothing was installed, built, or run.
`npm audit` was NOT executed on these seven — the advisory-to-version mapping is
carried across from the two repos where it *was* verified. Transitive
vulnerabilities beyond `next` are unknown for all seven. Deliberately did **not**
mass-open PRs: a version bump that has not been built is exactly the kind of
unverified change this register exists to prevent. Each needs `npm ci`, bump,
then lint/typecheck/test/build before a PR — the same treatment `trace` and
`privacy-scan` got.

**Priority if working through them:** `APN-Core-Site` (the core site, ships
Stripe), then `australian-data-removal` (oldest version, ships Stripe + Resend),
then `account-audit`, then `apn-hub`, then `sovereign-tank` (public), then the
two v0 repos.

## 15. `APN-Core-Site` — 21 high advisories cleared; the cause was not Next.js

First repo worked through from §14's priority list, fully verified rather than
bumped blind. **Measured BEFORE, on a clean clone:**

| check | result |
|---|---|
| `pnpm run lint` | **exit 2** — eslint not a dependency; fell through to a different major on PATH |
| `pnpm run typecheck` | *no such script* |
| `pnpm run build` | 0 |
| `pnpm audit` | **45 vulnerabilities, 21 HIGH** |
| CI | **none — no workflows at all** |

**The dominant cause was `shadcn` in RUNTIME dependencies.** It is the CLI
scaffolding tool, imported nowhere in `app/`, `components/` or `lib/`, and it
dragged `hono`, `ajv`/`fast-uri`, `ip-address`, `js-yaml` and `brace-expansion`
into the shipped tree — **6 of the 9 distinct high-severity packages**. Removed;
`components.json` stays, since that is config for `npx shadcn add`.

Also: `postcss` sat pinned at 8.5.6 in the lockfile while the declared range
`^8.5` already permitted the patched 8.5.23. A stale lockfile entry, not a
version constraint. Worth checking for elsewhere.

**Two real bugs from the first-ever lint run, both in the Stripe checkout**
(`components/apn/checkout-button.tsx`):
1. `useEffect` called **after an early return** — a render taking the
   `!isStripeConfigured` branch ran one fewer hook than one that did not. Does
   not crash today only because `isStripeConfigured` is a module constant; the
   moment it became reactive React would throw "rendered fewer hooks than
   expected" and take the checkout button down. Hoisted, behaviour-neutral.
2. A **second, unreachable** `if (!isStripeConfigured)` block rendering a
   different "Payments temporarily unavailable" design. Two competing designs
   for one state, only one of which could ever display. Dead one removed.

**AFTER:** lint 0 · typecheck 0 · build 0 · `pnpm audit --prod` **no known
vulnerabilities** (was 21 high). Three high remain in `pnpm audit` overall, all
`brace-expansion` via the eslint toolchain — dev-only, never shipped, left
deliberately. Vercel `apn-core-site` deployed **Ready** from the PR.

**`Fast-Clocks/APN-Core-Site` PR #7.** Added `.github/workflows/quality-gate.yml`
(all checks blocking) and `.github/dependabot.yml`.

**My own new workflow failed on its first run** — `pnpm/action-setup@v4` errors
with "No pnpm version is specified" unless given `version:` or a
`packageManager` field, and this repo has neither. Fixed by pinning major 10.
Recording it because it is the same lesson as the `$?`/`PIPESTATUS` bug: a
workflow that has been written is not a workflow that has run. **Any repo in
this estate using pnpm needs that `version:` pin** — `account-audit`,
`v0-sovereignty-lab-ui` and `sovereign-tank` also carry pnpm config.

**NOT PROVEN:** no deployment tested beyond Vercel reporting Ready; QUALITY-GATE
product checks not run; 11 lint warnings remain unaddressed.

## 16. Vercel sprawl is worse than the three known orphans

§10 recorded 3 orphaned Vercel projects building from `Fast-Clocks/Fast-Clocks`.
Opening a PR on `APN-Core-Site` revealed **five more** wired to that one repo:
`apn-core-site-c932`, `apn-vault`, `apn-vault-cover`, `v0-apn-hub-deploy-prep`,
`v0-project` — all reporting *Ignored* on the PR.

`apn-vault` and `apn-vault-cover` deploying from `APN-Core-Site` is wrong on its
face: §9 records `apn-vault` as a static shell with its own repo. So at least
two Vercel projects point at a repo that is not their source.

**Not acting on this** — Vercel project wiring is Chris's call and §10's question
about the first three is still unanswered. But the count is now **8 known
misattached or orphaned Vercel projects**, not 3, and every one of them runs a
build on every push to a repo it should not be watching.

## 17. 🔴 `australian-data-removal` — unauthenticated Stripe webhook, and a build told to ignore type errors

Second repo from §14's list. **Measured BEFORE**, clean clone, pnpm (what Vercel picks):

| check | result |
|---|---|
| `lint` | exit 2 — eslint not a dependency |
| `typecheck` | **FAILED** — no script existed; `tsc` reports a real error |
| `build` | 0 — **because `next.config.mjs` set `ignoreBuildErrors`** |
| `pnpm audit` | **35 vulnerabilities, 19 HIGH, all in the PRODUCTION tree** |
| CI | none |

### The serious finding is not a dependency

`app/api/webhooks/stripe/route.ts` fell back to `JSON.parse(body)` whenever
`STRIPE_WEBHOOK_SECRET` was unset **or** the `stripe-signature` header was
missing, logging *"processing without verification"*. A forged
`checkout.session.completed` POST would then be written as a member record at an
**attacker-chosen tier**, and trigger an **APN-branded confirmation email via
Resend to an attacker-chosen address**.

**Exploitability depends on configuration and I could not verify it.** The unsafe
branch only executes when `STRIPE_WEBHOOK_SECRET` is absent from the environment.
If it is set in Vercel production, the path was never reachable there. This
session cannot read Vercel environment variables, so the honest statement is: the
**code** contained an unauthenticated write path into payment fulfilment; whether
production ever executed it is **UNKNOWN**. Chris should confirm the secret is
set in production *and* preview.

Fixed to fail closed — missing secret → 500, missing signature → 400.
**This is a behaviour change:** any environment without the secret now errors
instead of silently succeeding.

### A third distinct false-green shape

`next.config.mjs` carried `typescript: { ignoreBuildErrors: true }`. The build
reported green for months while `tsc` failed — on that same webhook file:
`apiVersion` pinned to `"2024-12-18.acacia"` while `stripe@17.7.0` expects
`"2025-02-24.acacia"`. On a webhook the API version governs the payload shape
being parsed, so this is not cosmetic. `QUALITY-GATE.md` lists "no ignored TS
errors" as mandatory; the flag was overriding it silently.

**Running tally of false-green mechanisms in this estate — four now:**
1. `$?` after a pipeline reading `tee`'s status (`Fast-Clocks` truth-scan gate)
2. `continue-on-error: true` on checks documented as mandatory (`trace`)
3. `typescript.ignoreBuildErrors: true` (this repo)
4. a lint script whose binary is not a dependency — silently resolving to
   whatever is on PATH, or nothing (8 repos)

Each was invisible to reading and only appeared by running the thing.

### Two lockfiles

Both `package-lock.json` and `pnpm-lock.yaml`, committed in the same 10 July
commit. Two lockfiles can resolve different trees and which wins depends on the
tool. Kept pnpm (Vercel's choice); removed the npm one. **Check the other repos
for this.**

**AFTER:** lint 0 · typecheck 0 · build 0 with `ignoreBuildErrors` GONE ·
`pnpm audit --prod` **0 high** (was 19), 1 moderate.
**`Fast-Clocks/australian-data-removal` PR #2.** Added quality-gate + dependabot.

**NOT PROVEN:** the fail-closed webhook change has NOT been exercised against a
real Stripe event. It needs `stripe listen` or a live test event before merge.

## 18. 🔴 `account-audit` — checkout very likely broken, six colourless borders, 20 high → 0

Third repo from §14. **BEFORE:** lint exit 2 · no typecheck script, `tsc` reports
**8 real errors** · build 0 *because* `ignoreBuildErrors` · **40 vulnerabilities,
20 HIGH, all production** · no CI.

**Second repo with `typescript.ignoreBuildErrors: true`.** What it was hiding:

1. **`app/api/checkout/route.ts` passed `customer_email_collection: 'required'`
   to Stripe Checkout — not a parameter the API accepts.** Stripe rejects unknown
   parameters with `400 Received unknown parameter`, which would drop every call
   into the catch block and return a 500. **NOT VERIFIED against the live API**
   (needs a real key), but no configuration makes an unknown parameter valid.
   Removed; Stripe Checkout collects the email by default in `mode: 'payment'`.
2. **`COLORS.muted` referenced six times, never defined.** Every one resolved to
   `borderColor: undefined` — borders on `engagement-forms.tsx` (×5) and
   `service-card.tsx` fell back to the browser default instead of a brand tone.
   A visible defect on a live site. Added as navy at 25% alpha: **derived from
   the palette, not invented**. Wants a design eye.
3. **`lib/stripe.ts` pinned `apiVersion '2024-12-15.acacia'` against
   `stripe@22.3.0`, which expects `'2026-06-24.dahlia'`** — ~18 months of drift.

### `shadcn` belongs in devDependencies, not dependencies

Refines §15. On `APN-Core-Site` shadcn was genuinely unused and deleting it was
right. **Here it IS used** — `app/globals.css` does
`@import 'shadcn/tailwind.css'` — but only at BUILD time. Moving it to
devDependencies takes `ts-morph`, `hono` and `brace-expansion` out of the
production tree while keeping the build working. That also made the repo's
existing `pnpm.overrides.hono` pin redundant — someone had already hit one of
these advisories and patched the symptom.

**I got this wrong first.** I deleted `shadcn` outright after grepping for
`from 'shadcn'` and finding nothing — a CSS import is invisible to that grep.
The build caught it. Then the first devDependency attempt *also* failed, on a
stale `.next` cache, which would have been an easy wrong conclusion ("devDeps
don't work for this"). A clean `.next` proved it does. **Check CSS imports, and
clear the build cache before concluding a dependency move failed.**

**AFTER:** lint 0 · typecheck 0 · build 0 with `ignoreBuildErrors` gone ·
`pnpm audit --prod` **no known vulnerabilities** (was 20 high).
**`Fast-Clocks/account-audit` PR #1.** Added quality-gate + dependabot.

**NOT PROVEN:** checkout fix not exercised against the live Stripe API — worth a
single test-mode purchase before merge. `muted` not design-reviewed.

### Estate scoreboard after three repos

| repo | high advisories before → after | hidden defects found |
|---|---|---|
| `APN-Core-Site` | 21 → 0 prod | rules-of-hooks in Stripe checkout; unreachable duplicate branch |
| `australian-data-removal` | 19 → 0 prod | unauthenticated webhook; Stripe apiVersion drift |
| `account-audit` | 20 → 0 prod | invalid Stripe param; 6 undefined colours; 18mo apiVersion drift |

Every one had **no CI at all** and a dead `lint` script. In all three the
dependency bump was the *least* valuable part of the change.

## 19. `apn-hub` — the counter-example, and what it proves

Fourth repo from §14, and the one that needed no repair. **BEFORE:** lint 0 *and
real* · test 0 · test:routes 0 · build 0 · tsc 0 · 6 high advisories · **two
substantial CI workflows already**.

**The lint here is genuinely working — do not "fix" it.** `"lint": "eslint"` with
no path argument looks exactly like the dead-lint pattern found in eight other
repos, so I checked rather than assumed: ESLint 9 defaults to the current
directory, and **70 files were inspected with zero messages** by both the bare
and explicit forms. Recorded so a later session does not "repair" something that
works.

**What this repo proves.** It is the only Next.js repo in the estate with eslint
correctly pinned AND real tests — and it was **still on a vulnerable `next`**.
Being well-configured did not save it, because nothing was watching. The lesson
of the whole sweep is not "configure better", it is **"something must run on a
schedule"**. That is the case for Dependabot, not for tidier config.

**Its governance is the estate's best and should be the model:**
- `operating-law.yml` verifies canonical instruction entrypoints exist as
  non-empty regular files (not symlinks) and **forbids shadow instruction
  files** — `AGENTS.override.md`, `CLAUDE.local.md`, `.claude/**`, `.codex/**`,
  `.gemini/**` — unless explicitly allowlisted.
- Actions are **SHA-pinned**, and checkouts use `persist-credentials: false`.
- It carries `docs/APN-OPERATING-CONSTITUTION.md`, `.github/CODEOWNERS`, issue
  and PR templates.

**Changes (`Fast-Clocks/apn-hub` PR #12):** next 16.2.7 → 16.3.1; `npm audit fix`
for two dev-only advisories → **0 vulnerabilities, dev included**; added a
`typecheck` script; added Lint / Type-check / blocking prod audit / advisory full
audit **to the existing `route-verification.yml`**, not a new file — this repo's
own §7 is one canonical system, and adding a competing `quality-gate.yml` would
violate the rule the repo exists to enforce. Added dependabot.

**No instruction files touched**, checked against `operating-law.yml`'s rules
before committing.

**`EXECUTION_LEDGER.md` deliberately untouched.** Merging these findings into it
is Chris's call and a separate change — not something to slip inside a
dependency bump.

### Sweep scoreboard, four of seven

| repo | high before → after | CI before | hidden defects |
|---|---|---|---|
| `APN-Core-Site` | 21 → 0 prod | none | rules-of-hooks in Stripe checkout; unreachable branch |
| `australian-data-removal` | 19 → 0 prod | none | **unauthenticated Stripe webhook**; apiVersion drift |
| `account-audit` | 20 → 0 prod | none | invalid Stripe param; 6 undefined colours; 18mo drift |
| `apn-hub` | 6 → **0 total** | **two workflows** | **none** |

**66 high advisories cleared.** The three repos with no CI each hid a real defect
in payment-handling code. The one repo with CI hid nothing. That correlation is
the finding.

## 20. `sovereign-tank` (PUBLIC) — 23 high → 0, a fifth dead-lint mechanism, 32 hidden bugs

Fifth repo from §14, and the only **public** one. **BEFORE:** lint exit 1 ·
no typecheck script, `tsc` **43 errors** · build 0 *because* `ignoreBuildErrors`
(third repo with it) · **46 vulnerabilities, 23 HIGH, all production** · no CI.

### A fifth way to have a dead lint

`next lint` is **removed in Next 16**, and Next parses `lint` as a positional
*directory* argument:
`Invalid project directory provided, no such directory: .../lint`.

Running tally of dead-lint mechanisms in this estate:
1. eslint not a dependency → exit 127 (`privacy-scan`)
2. eslint not a dependency but resolved from PATH at a **different major** (`trace`)
3. `continue-on-error` on a mandatory check (`trace` CI)
4. `next lint`, removed in Next 16 (`sovereign-tank`, `v0-sovereignty-lab-ui`)
5. …and one that **looked** dead and was fine — bare `eslint` (`apn-hub`, §19)

### Real runtime bugs behind `ignoreBuildErrors`

- `adr-dashboard.tsx` keyed hotspot state on `h.region`, but `Region` has
  `name`. **Every key was `undefined`** — all six hotspots collapsed into one
  `"undefined"` entry and shared a single state.
- `document-analyzer.tsx` — two `useCallback`s referenced `processFile` in its
  temporal dead zone. Declaration moved above them.
- `analytics/surface/route.ts` — `spfRecord` assigned inside a `forEach`
  callback, which TS flow analysis cannot track → stayed `null`, narrowed to
  `never` at `.trim()`. Converted to `for…of`.
- **all five `/api/ai/*` routes** used `maxTokens` and `toDataStreamResponse()`,
  neither of which exists in the installed AI SDK v6.
- `system-health-panel.tsx` rendered literal `//` separators.

### The mistake worth recording

Ten functions in `lib/` were marked `async` with non-Promise return
annotations. I "fixed" them by wrapping the annotations in `Promise<>` — and
the error count went **UP**, 28 → 31, because the call sites in `api/scan` and
`api/security/threats` then correctly complained they were using a Promise as a
value. **None of those functions contain `await`.** The right fix was removing
the spurious `async`, which cleared functions and callers together. Making an
error message disappear is not the same as fixing the thing it points at.

I also botched the eslint-disable placement first: I ran a single-pass inserter
three times, and each inserted comment shifted the next reported line, stacking
16 unused-disable warnings. Reverted and did one pass. Recorded because the
failure mode — a fix loop that reacts to output it is itself changing — will
recur.

### Bounded, not clean

`ignoreBuildErrors` **stays**, hiding exactly **11** errors: the AI SDK v5→v6
`useChat` migration in two chat components. v6 removed
`input`/`handleInputChange`/`handleSubmit`, replaced `isLoading` with `status`
and `append` with `sendMessage`, moved `api` into a transport, and changed
`message.content` to a `parts` array. That is a behavioural rewrite of the chat
UI; a green typecheck would **not** prove it works, and it cannot be validated
without running the app against a live model. The flag now carries a comment
naming exactly what it hides and when to remove it.

`typecheck` is deliberately **not** a CI step yet — adding it as
`continue-on-error` would be a check that cannot fail, the anti-pattern this
sweep exists to remove. It becomes blocking when the migration lands.

**AFTER:** lint **0** (first time this repo has ever linted) · build 0 ·
`pnpm audit` **0 vulnerabilities, production AND dev** (was 46 / 23 high) ·
typecheck 11, all accounted. **`Fast-Clocks/sovereign-tank` PR #1.**

### Sweep scoreboard, five of seven

| repo | high before → after | CI before | hidden defects |
|---|---|---|---|
| `APN-Core-Site` | 21 → 0 prod | none | hooks bug in Stripe checkout; dead branch |
| `australian-data-removal` | 19 → 0 prod | none | **unauthenticated Stripe webhook** |
| `account-audit` | 20 → 0 prod | none | invalid Stripe param; 6 undefined colours |
| `apn-hub` | 6 → **0 total** | **two workflows** | **none** |
| `sovereign-tank` | 23 → **0 total** | none | 32 type errors incl. 5 dead API routes |

**89 high advisories cleared.** Four of the five repos with no CI hid real
defects; the one with CI hid nothing. The correlation has held for every repo.

## 21. `v0-sovereignty-lab-ui` — 46 vulnerabilities to zero; and a pnpm trap that would have silently undone the last two repos

Sixth repo of the §14 sweep. Same v0 template as `sovereign-tank`, same damage.

**Measured BEFORE, clean clone, pnpm 10.15.1:**

| check | result |
|---|---|
| `pnpm run lint` | **exit 1** — `next lint`, removed in Next 16 |
| `pnpm run typecheck` | *no such script*; `tsc` reports **32 errors** |
| `pnpm run build` | 0 — **only because** `ignoreBuildErrors` was on |
| `pnpm audit --prod` | **46 vulnerabilities, 23 HIGH, all production** |
| CI | **none** |

**AFTER, verified from a clean `--frozen-lockfile` install:** lint **0** (first
time this repo has ever linted) · build 0 · `pnpm audit` **0 vulnerabilities,
production AND dev** · typecheck **11**, all the deferred `useChat` migration.
**`Fast-Clocks/v0-sovereignty-lab-ui` PR #4.** Vercel deployed **Ready**.

### 🔴 pnpm 11 silently ignores `pnpm.overrides` in `package.json`

The single most important finding here, and it is **retroactive**. Running
`pnpm install` under pnpm 11 emits:

> The "pnpm" field in package.json is no longer read by pnpm. The following keys
> were ignored: "pnpm.onlyBuiltDependencies", "pnpm.overrides".

Settings moved to `pnpm-workspace.yaml`. The consequence is not cosmetic: the
`pnpm.overrides` block is what pins `picomatch`, `lodash` and `d3-color` to
patched versions in **both this repo and `sovereign-tank`**, because those
arrive through `tailwindcss-animate`, `recharts@2` and `react-simple-maps` —
packages that cannot be upgraded without a major migration each. Under pnpm 11
those pins vanish, the tree resolves differently, and `pnpm audit` would find
vulnerabilities again.

**The `version: 10` pin in both quality gates is therefore load-bearing, not
housekeeping.** It was originally added for a completely different reason — the
`pnpm/action-setup@v4` "No pnpm version is specified" failure on `APN-Core-Site`
(§15). It happens to be the thing standing between this estate and a silent
regression. That is luck, not design, and it should be replaced by an actual
migration to `pnpm-workspace.yaml`.

Also worth recording: `npx pnpm@10` did **not** give pnpm 10. A `corepack
enable` earlier in the session shimmed the `pnpm` binary, and the shim resolved
to 11.21.0 regardless of the requested version. Every measurement taken through
that shim would have been against the wrong resolver. Caught only by running
`--version` and reading it.

### `postcss` pinned stale in the lockfile — third occurrence

`postcss` sat at 8.5.6 while the declared range `^8.5` already permitted the
patched 8.5.23+. Same drift as `APN-Core-Site` and `account-audit`. This is now
a pattern, not a coincidence: **a lockfile can hold a vulnerable version that
the manifest never asked for**, and no version-range audit of `package.json`
would ever reveal it.

### Real bugs the first-ever lint and typecheck found

- **`adr-dashboard.tsx` exported `ADRDashboard` twice** — `export function` plus
  a trailing `export { ADRDashboard }` (TS2323 + TS2484).
- **`adr-dashboard.tsx` keyed hotspot state on `h.region`**; `Region` declares
  `name`. Every key was `undefined`, collapsing six hotspots into one. **Stated
  honestly: that state is neither read nor written elsewhere, so this is latent,
  not visible today.** The same bug in `sovereign-tank` *was* live — the
  distinction matters and was checked, not assumed.
- **`analytics/surface/route.ts`** assigned `spfRecord` inside a `forEach`,
  which TS flow analysis cannot track → narrowed to `never`, failed at `.trim()`.
- **Five `/api/ai/*` routes** called `maxTokens` and `toDataStreamResponse()`,
  neither of which exists in the installed AI SDK v6.
- **`document-analyzer.tsx`** called `processFile` from two `useCallback` hooks
  while it was still in its temporal dead zone — identical to `sovereign-tank`.
- **`brokers/route.ts`** had an evolving implicit `any[]` read by `.includes()`.

### Lint fixes removed hazards rather than messages

`displayedBrokers` was a pure slice mirrored into state by an effect → derived
during render with `useMemo`. `attackVectors` was state populated from a mount
effect though `generateAttackVectors()` is fully deterministic → module constant.
`use-mobile` and `data-collection-notice` → `useSyncExternalStore` with server
snapshots.

**One near-regression worth recording.** Rewriting the consent notice to
`useSyncExternalStore` initially dropped the old `catch` branch's
`setIsVisible(false)`. That would have meant a visitor whose `localStorage`
throws — private mode, blocked cookies — could **never dismiss the privacy
notice**, because the write fails, the snapshot stays `true`, and Accept does
nothing. Trapping a modal on screen for exactly the privacy-conscious visitors
the notice exists for. Caught by re-reading the old error path rather than the
happy path, and fixed with a session-level fallback.

**Exactly one suppression remains**, documented at the line: `generateBrokers()`
builds 4,200 records with `Math.random()`, so it cannot run during render
without a hydration mismatch.

### Removed: `@tailwindcss/postcss`

The Tailwind **v4** PostCSS plugin, in a Tailwind **v3** project — `globals.css`
uses `@tailwind base/components/utilities` and `postcss.config.mjs` loads the
`tailwindcss` plugin. **Verified by building without it, not by grepping.** The
`shadcn` removal on `account-audit` (§18) was a grep that said "unused" and a
build that disagreed.

### 🟠 Flagged, deliberately NOT fixed: third-party CDN on a privacy product

`components/global-threat-map.tsx` fetches its world map at runtime from
`https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json`. Every visitor's
IP address goes to a third-party CDN. On a **privacy** product that is a
substantive issue, not a performance note, and my own truth scan flags exactly
this class under §23. Vendoring the file is a real change with a bundle-size
trade-off, so it is recorded for a decision rather than done quietly. Worth
sweeping the whole estate for the same pattern.

### Sweep scoreboard, six of seven

| repo | high before → after | CI before | hidden defects |
|---|---|---|---|
| `APN-Core-Site` | 21 → 0 prod | none | hooks bug in Stripe checkout; dead branch |
| `australian-data-removal` | 19 → 0 prod | none | **unauthenticated Stripe webhook** |
| `account-audit` | 20 → 0 prod | none | invalid Stripe param; 6 undefined colours |
| `apn-hub` | 6 → **0 total** | **two workflows** | **none** |
| `sovereign-tank` | 23 → **0 total** | none | 32 type errors incl. 5 dead API routes |
| `v0-sovereignty-lab-ui` | 23 → **0 total** | none | 32 type errors; duplicate export |

**112 high advisories cleared.** Five of the six repos with no CI hid real
defects; the one with CI hid nothing. The correlation has held for every repo in
the sweep without exception.

### Remaining

`v0-claude-api-access` (next 16.2.6, has `shadcn`) is the last of the seven.

### New estate-wide item

GitHub is deprecating Node 20 on Actions runners. `actions/checkout@v4`,
`actions/setup-node@v4` and `pnpm/action-setup@v4` all target it and are being
force-run on Node 24 with a warning. Every quality gate added in this sweep uses
those three. Not urgent, not broken, but it will become both.

## 22. `v0-claude-api-access` — the sweep closes; and a repo whose name is a lie

Seventh and **last** repo of the §14 sweep.

**Measured BEFORE, clean clone, pnpm 10.15.1:**

| check | result |
|---|---|
| `pnpm run lint` | **exit 2** — `eslint .` with eslint not a dependency |
| `pnpm run typecheck` | *no such script*; `tsc` reports **0 errors** |
| `pnpm run build` | 0, with `Skipping validation of types` |
| `pnpm audit --prod` | **45 vulnerabilities, 21 HIGH, all production** |
| CI | **none** |

**AFTER, verified from a clean `--frozen-lockfile` install:** lint **0** · typecheck
**0** · build **0** · `pnpm audit --prod` **no known vulnerabilities**.
**`Fast-Clocks/v0-claude-api-access` PR #3.**

### `shadcn` again — and the reason the checklist step exists

Six of the nine distinct high-severity packages (`fast-uri`, `hono`,
`ip-address`, `js-yaml`, `brace-expansion`, `postcss`) came through `shadcn` in
**runtime** dependencies, dragging `@modelcontextprotocol/sdk`, `express`,
`ts-morph` and `cosmiconfig` into the production graph. Identical to §17.

**But deleting it would have broken the build**, and checking that FIRST is the
entire lesson carried forward from `account-audit`: `app/globals.css` does
`@import 'shadcn/tailwind.css'`, which no `grep "from 'shadcn'"` will ever find.
It is required at BUILD time and ships no browser code, so the correct move is
`dependencies` → `devDependencies`. Production graph cleared; CSS import intact.

Verified on a **clean `.next`**. A stale Turbopack cache previously made this
exact change look broken on `account-audit` when it was fine, and re-running
without clearing it would have reproduced that false conclusion.

### The one repo where `ignoreBuildErrors` was DELETED, not bounded

Every other repo in this sweep needed the flag kept and documented because real
errors hid behind it. This one measured **zero** type errors both before and
after — the flag was suppressing nothing. It came with the v0 template and sat
one commit away from silently swallowing the first real type error anyone
introduced.

Proof the check is now genuinely running, not merely configured: the build log
prints `Running TypeScript ... Finished TypeScript` where it previously printed
`Skipping validation of types`. This is also the **first repo in the sweep where
`typecheck` is a BLOCKING CI step from day one** rather than a documented
backlog.

### `postcss` stale in the lockfile — FOURTH occurrence

8.5.6 while `^8.5` already permitted 8.5.26. Four of seven repos. This is not
drift, it is the default outcome of never re-resolving a lockfile.

### 🟠 Three names for one artifact

- **Repo name:** `v0-claude-api-access`
- **Repo description:** *"Internal utility — browser-based Claude API access tool"*
- **Actual contents:** a marketing site — `HeroSection`, `FounderSection`,
  `PhilosophySection`, `DomainPortfolio`, `TransparencySection`,
  `NetworkSection`, `FirstProduct`, `Footer`. **No API access of any kind.**
- **Vercel project it deploys to:** `under-construction`

**Checked, because the name demanded it: there is NO credential in this repo.**
The only `process.env` reference in the whole tree is `NODE_ENV`. No `sk-ant`,
no `*_API_KEY`, no tracked `.env`. Clean.

That check had to be run rather than assumed, and it points at the real cost of
the naming: a repo called "claude-api-access" is exactly where anyone auditing
for a leaked Anthropic key would look first, and exactly where someone in a
hurry might one day put one. A name that describes something the repo is not is
a trap set for a future reader. Renaming is a decision for Chris, not a quiet
fix — recorded here.

### ✅ SWEEP COMPLETE — all seven repos of §14

| repo | high before → after (prod) | CI before | hidden defects |
|---|---|---|---|
| `APN-Core-Site` | 21 → 0 | none | hooks bug in Stripe checkout; dead branch |
| `australian-data-removal` | 19 → 0 | none | **unauthenticated Stripe webhook** |
| `account-audit` | 20 → 0 | none | invalid Stripe param; 6 undefined colours |
| `apn-hub` | 6 → **0 total** | **two workflows** | **none** |
| `sovereign-tank` | 23 → **0 total** | none | 32 type errors incl. 5 dead API routes |
| `v0-sovereignty-lab-ui` | 23 → **0 total** | none | 32 type errors; duplicate export |
| `v0-claude-api-access` | 21 → 0 | none | false-green `ignoreBuildErrors` |

**133 high-severity production advisories cleared across seven repos.**
**Seven quality gates and seven Dependabot configs added where there were two.**

**The correlation held without a single exception.** Six of the seven repos had
no CI; all six hid at least one real defect. The one repo that had CI —
`apn-hub` — hid nothing, despite running a vulnerable Next.js. Being
well-configured did not protect it; being *watched* is what protected it.

**The dependency bump was the least valuable part of every single repo.** The
advisories were the reason to look; the bugs found while looking were the
return. Two of them were in live payment paths.

### What this sweep did NOT do — stated plainly

- **No deployment was functionally tested.** Vercel reporting *Ready* is a build
  result, not a working site. No page was opened, no checkout attempted.
- **No product check from QUALITY-GATE.md was run** — live domain, responsive,
  keyboard, contrast, metadata, conversion path. All seven gates check code
  only, and each one says so in its own header comment.
- **11 type errors remain** in each of `sovereign-tank` and
  `v0-sovereignty-lab-ui`: the AI SDK v5→v6 `useChat` migration. Deliberately
  not attempted — it is a behavioural rewrite a green typecheck would not prove.
- **Every one of the seven PRs is a DRAFT and none is merged.** Nothing in this
  sweep is live. The estate is not fixed; it is *ready to be fixed*, pending
  review.

## 23. ESTATE-WIDE CDN SWEEP — all 27 repos, and a correction to §21

Method: `list_repos` unfiltered confirmed **27 repos**. GitHub code search across
`user:Fast-Clocks` for all five hosts the §23 scanner knows, then **every hit
opened and read** to separate a real fetch from a mention. Counting hits without
reading them is how the scanner itself got this wrong (§22).

**`cdnjs.cloudflare.com`: ZERO. `unpkg.com`: ZERO.**

### 🔴 Google Fonts — six repos still fetch it at page load

The July fix (§23 scanner header cites commits 35e46c6, 19bf649, 464d0f5,
2d1bddf, 180d324) did not cover these, or they regressed:

| repo | file | shape |
|---|---|---|
| `privacy-widget` | `index.html` | preconnect ×2 + `<link rel=stylesheet>` |
| `signal-trail-vault` | `src/routes/__root.tsx` | preconnect gstatic + stylesheet |
| `apn-hub-connect` | `src/routes/__root.tsx` | preconnect gstatic + stylesheet |
| `sovereign-showcase` | `src/routes/__root.tsx` | preconnect ×2 + stylesheet |
| `product-archetype` | `src/routes/__root.tsx` | stylesheet only, no preconnect |
| `sovereign-evidence-factory` | `app/audit-machine-original.html` | **CSS `@import url(...)` inside `<style>`** |

Five are the same TanStack/Lovable `__root.tsx` template — one template defect
replicated five times, which is why §14's "the Lovable/TanStack template is
better configured than the v0/Next one" was only true about *eslint*. On fonts
it is the worse template.

`preconnect` is not a lesser problem than the stylesheet: it opens DNS + TLS to
Google **earlier**, before anything is even needed. And the
`sovereign-evidence-factory` hit is a CSS `@import` inside an inline `<style>`
block — invisible to any check that only looks at `<link>`/`<script>` tags.

### 🟠 jsdelivr — three files, and §21 was incomplete

| repo | file | what |
|---|---|---|
| `sovereign-tank` | `components/global-threat-map.tsx` | world-atlas topojson · **PUBLIC REPO** |
| `v0-sovereignty-lab-ui` | `components/global-threat-map.tsx` | byte-identical `geoUrl` line |
| `apn-certification-machine` | `index.html` | `<script src>` qrcodejs + html2canvas |

**CORRECTION TO §21.** I recorded the jsdelivr finding against
`v0-sovereignty-lab-ui` only. It is in **`sovereign-tank` too — the same file,
the same line** — and I had that exact file open to fix its type errors without
noticing the CDN in it. Two lessons, both mine: a defect found in one repo of a
template family must be checked against the whole family immediately, and
reading a file for one purpose does not mean it was reviewed for another.

### ✅ `sovereign-suite-hub` is the MODEL, not an offender

It appears in the raw grep for both `fonts.googleapis.com` and
`fonts.gstatic.com`, and it is **clean**. Both hits are prose:

- `src/routes/__root.tsx` — a comment: *"self-host the WOFF2 files under
  /public/fonts and add @font-face in index.css — do NOT re-add
  fonts.googleapis.com / fonts.gstatic.com."*
- `PROJECT_LINEAGE.md` — the decision recorded in full, naming the data-residency
  rule it protects and stating plainly *"this is a decision, not an oversight."*

That is exactly the standard this register asks for, written by someone else,
before this sweep existed.

### 🟡 `v0-sovereignty-lab-ui/middleware.ts` — a header, not a fetch

`fonts.gstatic.com` appears in a CSP **`font-src` allowlist**. It permits Google
Fonts; it does not load them. Not a leak.

It is, however, **internally inconsistent**: `font-src` allows `fonts.gstatic.com`
while `style-src` does NOT allow `fonts.googleapis.com` — so a Google Fonts
stylesheet would be blocked by this policy anyway, and the `font-src` entry
protects nothing. Its twin `sovereign-tank` already removed it (its README:
*"Google Fonts CDN removed from CSP middleware"*). The twins have drifted.

### 🔴 MY SCANNER STILL HAS TWO GAPS — found by using it, not by reading it

1. **A hostname in a source comment still blocks.** §22 fixed docs-vs-shipped by
   moving `.md`/`.json` to advisory. `sovereign-suite-hub/src/routes/__root.tsx`
   is a `.tsx` file whose only match is a comment saying *do not do this* — so
   the fixed check would **still fail a clean repo for documenting its own fix**.
   I wrote "a hit inside a source comment is the remaining false-positive shape"
   into that check's own record note. It is no longer hypothetical; it is here.
2. **The host list is too short.** The scanner knows five hosts. This sweep
   surfaced third-party asset egress from hosts it would never see:
   - `storage.googleapis.com` — OG image, `sovereign-suite-hub` (per its own doc)
   - `pub-*.r2.dev` — OG image, `sovereign-showcase` (Cloudflare R2)
   - `*.lovable.app` — referenced in `privacy-widget`'s structured data
   A privacy product's egress surface is not five hostnames long.

**Neither gap is fixed here.** Both are recorded rather than patched, because a
scanner change needs its own before/after test (§22) and this pass was scoped to
finding, not fixing.

### NOT DONE, deliberately

No file was changed by this sweep. The instruction was report, not mass-fix, and
that is right: self-hosting fonts changes rendering on six live surfaces and
vendoring world-atlas is a bundle-size trade-off. **Nothing here is fixed. Nine
files across eight repos currently send visitor IP addresses to Google or
jsdelivr on page load**, on an estate whose product is privacy.

## 24. pnpm settings migrated — the security property was resting on a coincidence

§21 recorded that pnpm 11 ignores the `pnpm` field in `package.json`, and that
`sovereign-tank` and `v0-sovereignty-lab-ui` only stayed clean because CI pins
pnpm 10. That is now fixed at the source in both repos: settings moved to
`pnpm-workspace.yaml`.

**The regression is measured, not asserted.** Reverting one repo to the old shape
and installing with pnpm 11.21.0:

```
[WARN] The "pnpm" field in package.json is no longer read by pnpm.
       The following keys were ignored: "pnpm.onlyBuiltDependencies",
       "pnpm.overrides".
```

→ **no `overrides` block in the regenerated lockfile at all**
→ `pnpm audit --prod`: **13 vulnerabilities, 4 HIGH, back in the production tree**

With `pnpm-workspace.yaml`, under **both** pnpm 10.15.1 and 11.21.0: overrides
block intact, both audits clean, and `pnpm-lock.yaml` **byte-identical** after a
pnpm 11 install — the two resolvers reach the same tree.

**Why this mattered more than it looked.** The `version: 10` pin in both quality
gates was added for an entirely unrelated reason: `pnpm/action-setup` erroring
with *"No pnpm version is specified"* on `APN-Core-Site` (§15). It happened to be
the only thing standing between this estate and four high-severity production
advisories returning. Correct behaviour resting on a coincidence is not correct
behaviour — it is a latent failure with good luck in front of it. The pin no
longer carries the security property.

### 🟠 NOT FIXED — pnpm 11 remains blocked, for a second and separate reason

The migration does **not** make pnpm 11 usable, and the file says so at the line.

`pnpm@11 install --frozen-lockfile` still exits **1** on
`ERR_PNPM_IGNORED_BUILDS` (`unrs-resolver`, a native binary in the eslint
toolchain). pnpm 10 treats the same condition as a warning and exits **0** —
a behaviour change worth knowing about on its own.

Adding `ignoredBuiltDependencies` did not clear it. pnpm 11 supersedes both
build lists with a per-package `allowBuilds` setting that refuses to guess —
`pnpm config list` literally reports `"unrs-resolver": "set this to true or
false"` — and **`allowBuilds` is rejected as an unknown key in
`pnpm-workspace.yaml` on both majors** (YAML schema error, tested).

So the upgrade needs a real decision: allow `unrs-resolver`'s postinstall script
to run, or route around it. **Enabling a postinstall build script on a privacy
product is not a housekeeping change**, so it was not taken unilaterally.

**Method note, because it nearly went wrong twice.** `npx pnpm@10` silently
resolved to 11.21.0 earlier in this session because `corepack enable` had
shimmed the binary — every measurement through that shim would have been against
the wrong resolver. Both versions were confirmed with `--version` before every
comparison in this section. And the first `allowBuilds` attempt was *written*
and assumed correct; running it produced a YAML schema error on both majors.
Written is not run.

**VERIFIED AFTER**, both repos, pnpm 10 (what CI actually uses):
`install --frozen-lockfile` 0 · `lint` 0 · `build` 0 · `audit --prod` clean.

## 25. Node 20 deprecation cleared across the gates — and one comment retired

Every run of every gate added in this sweep ended with:

> `Node.js 20 is deprecated. The following actions target Node.js 20 but are
> being forced to run on Node.js 24: actions/checkout@v4, actions/setup-node@v4,
> pnpm/action-setup@v4`

Nothing was broken — the runner was already forcing Node 24. But a permanent
warning on a green run is precisely the noise that teaches people to stop reading
logs, which is the failure this whole sweep exists to correct. A gate nobody
reads is a gate that has stopped working.

**`checkout` and `setup-node` → v6, SHA-PINNED rather than tagged.** A tag is
mutable and a SHA is not, so a retagged or compromised action cannot silently
enter a build. The two SHAs are lifted from `apn-hub/route-verification.yml` —
the healthiest repo in the estate, whose own operating law asks for SHA pinning,
and where those exact SHAs already run green. Trusted, not newly introduced.

**PROVEN ON ONE REPO FIRST.** `sovereign-tank` was changed alone and its job log
read before anything else was touched. The warning went from listing **three**
deprecated actions to listing **one**, with every step still green — checkout,
setup-node, install, lint, build, blocking production audit.

Then rolled to: `APN-Core-Site`, `australian-data-removal`, `account-audit`,
`v0-sovereignty-lab-ui`, `v0-claude-api-access`, `trace`, `privacy-scan`.

### `pnpm/action-setup` deliberately NOT bumped

It sits outside this session's repository scope — `get_latest_release` returns
`Access denied` — so whether a major beyond v4 exists **could not be verified**.
Bumping an action to a version nobody confirmed exists is how a gate breaks.
Left at v4; the `github-actions` Dependabot ecosystem configured in each repo
will propose it when there is one, with a diff a human can read. It is the sole
remaining entry in that warning, by choice rather than oversight.

### 🔴 A comment of mine had become a lie, one commit after I wrote it

`v0-sovereignty-lab-ui`'s gate said the `version: 10` pin was **LOAD-BEARING for
security**, because pnpm 11 ignores the `pnpm` field and would silently drop the
picomatch/lodash/d3-color overrides. True when written. **False one commit
later**, when §24 moved those settings to `pnpm-workspace.yaml`.

Leaving it would have been a comment warning about a danger that had already been
removed — a false statement sitting in the exact place someone would look to
understand why the pin exists. Corrected to say what is now true: the pin remains,
for a *different* and still-live reason (pnpm 11 exits 1 on
`ERR_PNPM_IGNORED_BUILDS` where pnpm 10 exits 0), and it names what clearing that
would require.

**Fixing my own comment matters as much as fixing my own scanner.** Both get
believed by whoever reads them next. A stale comment is the same defect class as
a vacuous check: something that looks like evidence and is not.

### Mistake made and corrected in this pass

I pushed six repos assuming a single branch name and **two failed**: `trace` is on
`claude/quality-gate-lint` and `privacy-scan` on
`claude/fix-package-json-conflict-markers`. The commits existed locally; only the
push refspec was wrong. Fixed by pushing to each repo's actual branch — the ones
their existing PRs already track. Recorded because "the estate is uniform" is an
assumption that has now been wrong twice, after the template-family assumption
in §23.

### 🟠 More Vercel project sprawl surfaced — still DO NOT quote a count

Pushing these revealed further project↔repo pairings worth an eye:
`trace` → **`sovereign-markets`**; `privacy-scan` → **`trace-by-apn`** *and*
**`executive-privacy`**; `APN-Core-Site` → five projects, four reporting
*Ignored*. Whether each is misattached or intentional is **not established**.
§22 already warned the "8 misattached projects" figure is unverified; this makes
recounting more necessary, not less. **No number should be quoted until someone
lists the actual set.**

**VERIFIED — all eight, now closed.** `sovereign-tank` (log-verified: the
deprecation warning went from three actions to one), `APN-Core-Site`,
`account-audit`, `v0-claude-api-access`, and — confirmed on the following
check-in rather than assumed — `trace`, `privacy-scan`,
`australian-data-removal`, `v0-sovereignty-lab-ui`. Every `validate` job
`success`.

This paragraph originally read "not yet confirmed, and not claimed as such" for
the last four. It is updated only because they were then actually checked. An
open claim in this register gets closed by evidence or not at all.

---

## 26. PR TRIAGE — 26 open, and proof that three orphan Vercel projects redden every Fast-Clocks PR

**Numbering note, because it is the same defect class this register keeps
catching.** Commit `6aa0b23`'s message says "and §26 the ledger merge". No §26
was ever written into this file — that work landed in `apn-hub#13`'s
`EXECUTION_LEDGER.md`, not here. A commit message naming a section that does not
exist is a stale comment by another route. **This is the real §26.**

Nothing was closed, merged, or pushed to any of these branches. This section is a
list and a set of recommendations. Every merge decision below is Chris's.

### 🔴 THE FINDING: every `Fast-Clocks` PR is permanently red, and its own code is fine

`Fast-Clocks` PRs show a red ✗. The red is not from any check in this repo. It is
three **orphan Vercel projects** attached to this repository, failing on every
commit they see. Measured on three separate commits, weeks apart:

| Vercel project | FC#4 (23 Jul) | FC#5 (14 Aug) | FC#6 (15 Aug) |
|---|---|---|---|
| `fast-clocks` — the correct one | ✅ success | ✅ success | ✅ success |
| `public-access-hub` | ❌ failure | ❌ failure | ❌ failure |
| `apn-privacy-atlas` | ❌ failure | ❌ failure | ❌ failure |
| `apn-hub-restored` | ❌ failure | ❌ failure | ❌ failure |
| **PR combined status** | **failure** | **failure** | **failure** |

These are exactly the three orphans §25 flagged and could not explain.
`apn-privacy-atlas` appears in the ledger's own **Deleted Repositories** table.
`public-access-hub` and `apn-hub-restored` are in **neither** the live 27 **nor**
the deleted list. A Vercel project outlives the deletion of the repo it was built
for, keeps its GitHub connection, and keeps building against whatever repo it can
still reach — which is this one.

**The cost is not the wasted build. It is the alarm budget.** Since at least
23 July, every pull request in this repository has carried a red ✗ that means
nothing. That is the precise mechanism this register has been dismantling all
week — a signal that renders identically whether or not anything is wrong — except
here it fails *red* rather than green. A permanently red repo trains everyone to
stop looking, and the day a real check fails it will look exactly the same.

### 🔴 Correction to my own reporting

**I have been reporting `Fast-Clocks#6` as green. That was half the picture.**

The checks I own are genuinely green — `Claims, secrets, CDN, finish quality` =
`success`, `Detect analysable source` = `success` (CodeQL `Analyze` correctly
`skipped`; there is no analysable source). But the PR's **combined status is
`failure`**, and anyone opening it sees a red ✗.

Both statements are true. I only reported the one I was responsible for. Stating
"the gate is green" about a PR that displays as failing is exactly the kind of
technically-true-but-misleading report the standard exists to prevent, and it is
worse coming from the person who wrote the gate.

**This is not fixable from code.** No commit to any branch clears it. It needs
someone with Vercel dashboard access to disconnect or pause the three orphan
projects. Per DELETE NEVER: **pause, do not delete.**

**Superseded explanation, flagged rather than hidden.** PR comment
`5301661662` (15 Aug, 09:45) explained these same three failures as the
**misattached**-project problem of §10/§16 — "eight or more projects pointing at
the wrong repo". That was wrong. They are not misattached to a repo that exists;
they are **orphans whose repo was deleted while the Vercel project survived**.
Comment `5302482437` carries the correct cause. GitHub comments cannot be edited
through the tools available here, so the wrong one stays on the thread with the
right one below it — noted here because a reader who stops at the first
explanation gets a false one, and the register is where that gets corrected.

### Triage — the 15 PRs that predate this sweep

Ages as of 2026-08-15. "Mergeable" is GitHub's computed state, freshly polled.
`dirty` = genuine merge conflict. All are drafts **except `filewitness#1`**.

| PR | Age | What it does | Size | Mergeable | Recommendation |
|---|---|---|---|---|---|
| **filewitness#1** | 16d | Removes "Public preview" banner, adds company footer/disclaimer, untracks `.env` | 8,774+ / 7 files | 🔴 **dirty** | **The only one actually waiting on you.** Only non-draft PR in the estate; its own body says "Do not merge/deploy without sign-off." Needs conflict resolution first. |
| **privacy-widget#4** | 20d | Adds CI to a repo with none — migration hygiene + verifier self-tests, credential-free | 133+ / 2 files | ✅ clean | **Best value-to-risk on the list.** Negative-tested (a deliberately bad migration produced 3 failures). Same class of work as this week's sweep. |
| **apn-hub#7** | 26d | Product-network section on the public front door | 39+ / 1 file | ✅ clean | Smallest item here. One file, one read. Check first whether `apn-hub#11`/`#13` superseded it. |
| **apn-provenance-keeper#1** | 26d | Ed25519 + SHA-256 verifier for external S1 receipts | 176+ / 1 file | ✅ clean | Real product capability, in the repo CLAUDE.md records as the one a session wrongly declared absent. Wants a test before merge. |
| **privacy-widget#3** | 20d | SafePet Price Shield no-surge invariant + export worker | 700+ / 11 files | ✅ clean | ⚠️ **The migration is already applied to production.** Merging is bookkeeping, not deployment — the record is trailing reality by 20 days. |
| **privacy-widget#5** | 20d | Wires `/contact` to existing `public.inquiries`, insert-only | 348+ / 4 files | ✅ clean | Carefully bounded (no service-role key, no new table). Its own body names an unresolved gap: **consent is required to submit but not stored**. |
| **privacy-widget#6** | 15d | Read-only forensic audit of the Sovereign ledger | 68+ / 1 file | ✅ clean | Docs only. Its verdict matters: 16,867 rows recompute correctly, **but the chain forks at 54 points** — tamper-evident, *not* "tamper-proof". |
| **apn-certification-machine#3** | 25d | Certificate Studio — centred seal, logo options, compose-from-description | 138+ / 1 file | ✅ clean | 🟠 **New CDN finding** — see below. |
| **v0-sovereignty-lab-ui#3** | 32d | New `[BOT.FACTORY]` third nav view | 516+ / 2 files | ✅ clean | Oldest open PR. Merge my `#4` (security) first, then rebase this. |
| **perthsafepet#4** | 1d | Installs APN operating law at repo root (`AGENTS.md` + `CLAUDE.md`) | 134+ / 2 files | ✅ clean | Docs only, preserves the existing Lovable notice verbatim. Draft pending your review **of the wording of the law itself**. |
| **perthsafepet#3** | 8d | LICENSE + README route table 8→23 routes | 46+ / 2 files | ✅ (Vercel green) | **Authored by Copilot, not a Claude session** — the only non-Claude PR here. Low risk. |
| **perthsafepet#2** | 26d | Proof journey → Ledger and Hub | 45+ / 5 files | 🔴 **dirty** | Needs a rebase before it can be judged at all. |
| **Fast-Clocks#5** | 1d | Cloudflare agent setup doc | 152+ / 1 file | ⚠️ false red | Docs only. Red is the orphan-Vercel issue above, not this PR. |
| **Fast-Clocks#4** | 23d | APN File Brain — local-first substrate | 8,142+ / 34 files | ⚠️ false red | **Self-declared WIP**; its own body lists missing CLI, tests, docs and packaging. Largest unfinished thing in the estate. Decide: continue or park. |
| **apn-hub#11** | 1d | Sovereign GitHub "finishing factory" gate | 8,374+ / 24 files | ✅ clean | Its own body says **keep draft, do not merge** — `release_decision_allowed=false`, and it names an unmet requirement: *a distinct eligible reviewer*. Respect that. |

### 🟠 A CDN dependency the §23 sweep never saw

`apn-certification-machine#3`'s own body states the QR and PNG export "rely on
jsdelivr CDN scripts". §23 swept **merged/main** code across 27 repos and found
jsdelivr in three files. It did not read open PR branches, so this is a
**fourth occurrence**, sitting in unmerged code, in a product that mints
certificates.

Merging that PR would reintroduce a dependency the estate has been removing.
Not a blocker — a thing to fix *in* the PR before it lands, not after.

### The 11 PRs from this week's sweep

`Fast-Clocks#6`, `privacy-scan#8`, `trace#1`, `APN-Core-Site#7`,
`australian-data-removal#2`, `account-audit#1`, `apn-hub#12`, `sovereign-tank#1`,
`v0-sovereignty-lab-ui#4`, `v0-claude-api-access#3`, `apn-hub#13`. All draft, all
with a green `validate`/gate job, all documented in §14–§25. They are ready for
review as a group; the security content is the reason to look, and the dependency
bumps are consistently the least valuable part.

### What this triage did NOT do

- **Nothing was closed.** Not one PR, however stale.
- **No branch was pushed to, rebased, or force-updated.**
- I did **not** read the diffs. Every "what it does" above is drawn from the PR's
  own title, body and file statistics — MEDIUM confidence, not HIGH. A body can
  be wrong or stale; three of them already disagree with their own age.
- I did **not** verify the two `dirty` PRs' conflicts are trivial. `dirty` says a
  conflict exists, not how bad it is.
- The orphan Vercel projects are **still live and still failing.** Identified and
  evidenced here; not fixed, because fixing needs dashboard access.

---

## 27. ALARM BUDGET, measured — and a green tick that builds nothing

Method: `get_status` on one open PR in each of the 15 repos that has one. This
reads the **commit statuses** GitHub shows on the PR, which is what a human
actually sees. It is not a Vercel dashboard listing and does not replace one.

### ✅ THE ANSWER: the false red is contained to ONE repo

**`Fast-Clocks` is the only repo in the estate with a failing status.** Every
other sampled repo reports `success` or has no deployment integration at all.

This is the good version of the answer. The alarm-budget damage §26 documented is
real but **bounded** — it does not generalise, no other repo has orphan projects
attached, and **one dashboard action fixes the estate's entire false-red
problem**. Worth stating plainly because the opposite result was the working
assumption an hour ago.

### 🔴 The mirror image: five green ticks at `APN-Core-Site` that built nothing

`APN-Core-Site` carries **six** Vercel statuses. One is a real deployment. The
other five report:

> `state: success` · *"Canceled by Ignored Build Step"*

| Vercel project | Reported | Actually did |
|---|---|---|
| `apn-core-site` | ✅ success | deployed |
| `v0-apn-hub-deploy-prep` | ✅ success | **nothing — build skipped** |
| `apn-vault` | ✅ success | **nothing — build skipped** |
| `apn-core-site-c932` | ✅ success | **nothing — build skipped** |
| `v0-project` | ✅ success | **nothing — build skipped** |
| `apn-vault-cover` | ✅ success | **nothing — build skipped** |

**This is the vacuous pass, in the deployment layer.** §14 established the defect
class in CI: *a check that inspected 0 objects renders identically to one that
inspected 400.* Here five projects that compiled nothing render identically to
the one that shipped the site — same green tick, same `success` state, and the
"Canceled" wording lives in a description field nobody reads.

Fast-Clocks fails **loudly and wrongly**. APN-Core-Site passes **quietly and
emptily**. The second is worse: a red mark eventually gets investigated, and five
false greens never do. §25 noted these as "four reporting *Ignored*" and treated
it as sprawl. It is five, and it is not merely sprawl — it is five green ticks
that mean nothing, on the repo behind the public front door.

Not fixed. Dashboard-only, same as the orphans.

### Observed project↔repo pairings — a LOWER BOUND, still not a count

**21 distinct Vercel projects** are visible from PR statuses alone. §26 said not
to quote a count until someone lists the real set from the dashboard. That still
stands — this is what leaks through pull requests, and projects with no open PR
in their repo are invisible to it. **Treat 21 as a floor, not a total.**

| Repo | Vercel projects seen |
|---|---|
| `APN-Core-Site` | 6 — one real, **five build-skipped** |
| `Fast-Clocks` | 4 — one real, **three orphans failing** |
| `perthsafepet` | 3 — `perthsafepet`, `pet-safe-perth`, `pet-safe-perth-2c`, all deploying |
| `privacy-scan` | 2 — `trace-by-apn`, `executive-privacy` |
| `trace` | 1 — `sovereign-markets` |
| `apn-hub` | 1 — `apn-hub-1h` |
| `v0-sovereignty-lab-ui`, `account-audit`, `sovereign-tank` | 1 each, same-named |
| `v0-claude-api-access` | 1 — **`under-construction`** |
| `apn-provenance-keeper`, `apn-certification-machine`, `privacy-widget`, `filewitness`, `australian-data-removal` | **none — no status at all** |

Two of these want an eye. `perthsafepet` deploys the same repo to **three**
projects simultaneously, all succeeding — triple hosting of one product.
`v0-claude-api-access` deploys to a project called **`under-construction`**,
which is relevant to the open question about renaming that repo.

### 🟠 `australian-data-removal` shows NO deployment status — check before the Stripe step

There is an open action to set `STRIPE_WEBHOOK_SECRET` in that repo's Vercel
**production and preview** environments before `#2` merges. Its PR shows **zero
Vercel statuses**.

Stated precisely, because the distinction matters: this proves **no Vercel Git
integration is reporting on that PR**. It does **not** prove no Vercel project
exists — a project can exist, hold the environment variables, and simply not be
connected to this repo's pull requests. Worth confirming the project is findable
before going looking for the settings screen, rather than discovering it midway.

### 🔴 Correction to §25 — Node 20 was NOT cleared here, and I said it was

§25 recorded the Node 20 deprecation as cleared, with `pnpm/action-setup@v4` the
**"sole remaining entry in that warning, by choice rather than oversight."**

**That is false for this repository.** Reading the actual job log of Fast-Clocks'
own truth-scan run — rather than its green tick — surfaced:

> `Node.js 20 is deprecated. The following actions target Node.js 20 but are being
> forced to run on Node.js 24: actions/checkout@v4, actions/github-script@v7`

§25 swept the **eight quality-gate workflows in other repos** and never touched
Fast-Clocks' own four. The repo that hosts the enforcement machinery was the
least-hardened in the estate — every action on a mutable tag, none SHA-pinned,
while the gates it exports to everyone else were pinned. The cobbler's children.

**Fixed:** all six `actions/checkout@v4` occurrences across the four workflows
pinned to `d23441a48e516b6c34aea4fa41551a30e30af803 # v6.1.0` — the exact SHA
already CI-verified green in eight repos under §25.

**NOT fixed, and deliberately not guessed:** `actions/github-script@v7`,
`actions/upload-artifact@v4`, `actions/download-artifact@v4`,
`github/codeql-action/*@v3`, `peter-evans/create-pull-request@v6`. Bumping these
needs their target versions and SHAs **verified**, and those repos are outside
this session's scope to read. Writing a version number I have not confirmed is
the same error as a green tick I have not read. The `github-actions` Dependabot
ecosystem is configured here and will propose them monthly with a readable diff.

**Also note:** two of the four workflows (`apn-self-heal.yml`,
`apn-daily-estate-scan.yml`) **have never executed once**, and still cannot until
`#6` merges. Their checkout pin is changed but **unexercised**. Changed ≠ run.

### 🟠 Dependabot's major-version ignore also suppresses SECURITY updates

`.github/dependabot.yml` ends its npm block with:

```yaml
ignore:
  - dependency-name: "*"
    update-types: [version-update:semver-major]
```

The comment above it reads *"Majors need a human — they break builds and that
breaks trust in the bot."* Sound reasoning. But Dependabot applies `ignore`
conditions to **security updates as well as version updates** — so an advisory
whose only remedy is a major bump is dropped silently, and the `security:` group
above it does not rescue it.

In an estate where this entire week was spent clearing 133 high advisories, a
rule that can silently withhold exactly the ones needing a major bump is worth
knowing about. **Not changed** — it is a deliberate policy choice with a stated
rationale, and reversing it unilaterally would trade one failure mode for
another. Flagged for a decision, with the trade named: fewer broken builds versus
possibly never being told about a major-only security fix.

**Confidence: MEDIUM.** This is documented Dependabot behaviour, not something
reproduced here — no advisory requiring a major bump has been observed being
suppressed in this estate. Verify before acting on it.

---

## 28. PR-BRANCH SWEEP — the CDN grep found nothing new, and reading the code found a receipt travelling in a URL

§23 swept **main** across 27 repos. Open PR branches were never swept, so unmerged
code is an entirely separate surface. This is a **partial** sweep of it.

**Scope, stated before the findings.** `get_files` returns full patches, and three
open PRs exceed 8,000 additions (`Fast-Clocks#4`, `apn-hub#11`, `filewitness#1`).
Pulling those would have flooded the context and produced a worse read of
everything else. **Swept: `apn-hub#7`, `apn-provenance-keeper#1`,
`perthsafepet#2`.** Not swept: the remaining twelve. This is a sample that found
something, not a clean bill of health.

### CDN result: nothing new

No `jsdelivr`, `googleapis`, `gstatic`, `unpkg` or `cdnjs` reference in any of the
three diffs. The only previously-known PR-branch CDN dependency remains
`apn-certification-machine#3` (§26), established from its own PR body.

### 🔴 The real finding: a full S1 receipt is passed cross-domain in a URL query string

Two PRs, written separately, form one data path. **Neither shows it alone.**

**Producer** — `perthsafepet#2`, `src/routes/proof.tsx`:

```
https://apn-provenance-keeper.lovable.app/verify?receipt=${encodeURIComponent(data.receipt)}
```

**Consumer** — `apn-provenance-keeper#1`, `src/pages/VerifyIndex.tsx`:

```js
const receipt = searchParams.get("receipt");
```

**And the same `perthsafepet#2` diff widened what a receipt contains.** Before, a
receipt carried `verificationId`, `recordType`, `contentHash`, `keyId`, `sealedAt`,
`publicUrl`. This PR adds **`fields`** (the record content itself), **`subjectId`**,
`prevHash`, `signature`, and `publicKeySpki`. So the payload that now travels in a
query string is materially larger than the one that used to — the change that
expanded it and the change that puts it in a URL are the same change.

**Why a query string is the wrong carrier for record content.** URLs are the least
private part of an HTTP request. They are written to server access logs and proxy
logs by default, retained in browser history and sync, and sent onward in the
`Referer` header of subsequent requests from the destination page. A request body
is none of those things. This is a cross-origin, same-tab navigation to a
third-party-hosted domain (`*.lovable.app`), so the receipt crosses an
organisational boundary in the most loggable position available.

**Scope, honestly.** Both PRs label this demonstration data — *"test data only ·
no production ledger write"*, and *"This demonstration receipt is not persisted in
The Ledger."* **No real personal data goes through this path today.**

**But this is the path that is meant to go live.** `perthsafepet#2`'s own README
marks `S1-PET-01` a **candidate**, explicitly *"do not promote to a verified
reusable variant until the public route and cross-product verification path pass
end-to-end testing"* — and the cross-product verification path *is* this URL. The
time to change the carrier is before promotion, not after.

**Not fixed.** Both are other repos' unmerged branches; the standing instruction
is to close and change nothing. Recorded so the decision happens deliberately
rather than by merging.

**Confidence: HIGH** on the mechanism — both halves are quoted literally from the
diffs. **Not established:** whether the receipt would carry personal data in
production. `fields` is typed `Record<string, unknown>`, so it is
content-agnostic; what a real pet-rehoming record puts in it is a question for
whoever promotes the variant.

### 🟡 `verify.sovereignledger.au` — a default that should be checked

`sovereign-engine.server.mjs` defaults every receipt's `publicUrl` to
`https://verify.sovereignledger.au/<verificationId>`. Whether that domain is
registered, owned by the company, and serving anything is **not verified here** —
this environment has no outbound HTTP. It is worth one look, because a receipt is
a durable artefact and the URL printed on it is a promise about where proof can be
resolved. A receipt pointing at a domain nobody owns is worse than one with no URL
at all.

### ✅ Worth recording: `apn-provenance-keeper#1` is good work

The verifier does the whole check in the browser with `crypto.subtle` — SHA-256
recompute plus Ed25519 signature verify, no library, no network call, no key
material held. Its own disclaimer is properly bounded: *"It does not prove that
the underlying event is true, lawful, complete or approved."* That is the claims
discipline this register keeps asking for, written by someone else, before anyone
asked. The URL-carrier problem above is a transport choice, not a flaw in the
cryptography.

### What this sweep did NOT do

- **Twelve of fifteen pre-existing PRs remain unswept**, including all three large
  ones. A finding rate of one real issue in three diffs is not a reason to assume
  the other twelve are clean — it is a reason to think they are not.
- No branch was checked out, built, or run. Everything above is read from diffs.
- The CDN grep result covers only the three swept diffs.

---

## 29. `privacy-widget#3` — the false green reaches production, and a security fix has sat unmerged for 20 days

§26's triage said of this PR: *"the migration is already applied to production."*
**Correct for one of three migrations, and the imprecision hid the important
part.** The PR carries `4110`, `4111` and `4112`. Only `4110` is evidenced as
applied. Corrected below.

### 🔴 The false-green pattern has a FOURTH instance — this one in production

This register has now found the same defect in four layers. The pattern: **a
success signal that is emitted by the wrapper, not earned by the work.**

| Layer | Instance | Recorded |
|---|---|---|
| CI | `$?` reading `tee`, `continue-on-error` on mandatory checks, `ignoreBuildErrors`, a lint whose binary wasn't installed | §14–§22 |
| Deployment | `APN-Core-Site` — five Vercel projects reporting `success` / *"Canceled by Ignored Build Step"* | §27 |
| **Scheduled jobs** | **`domain-watch` and `link-audit` crons** | **here** |
| **Evidence store** | **the ledger records those runs as `audit` events** | **here** |

**F1 — `sovereign-domain-watch`: 36 "succeeded" runs in 72h, 0 domains checked in
20 days.** The cron builds its header as
`'Bearer ' || current_setting(<the service-role GUC>, true)` — the literal setting
name is deliberately not reproduced here; see §29's closing note. That GUC is
unset, so the header is NULL, so the function returns **401 before running**. The
401s land in `net._http_response` on exactly the 2-hour cadence. The cron wrapper
logs `succeeded` regardless. The domain register has been frozen since
**2026-07-08** at a last-known **3 LIVE of 216**.

**F2 — `link-audit`: ~90% failure, still logging `succeeded`.** Last 24h of
outbound HTTP at audit time: **34 timeouts, 3× 401, 2× 200**. 221 of 1009
resources remain `unchecked`.

**The fourth layer is the one that matters most.** Both crons keep appending
`audit` events to the sovereign ledger while their actual work fails. So the
evidence system — the thing whose entire purpose is trustworthy record — is being
fed "this ran successfully" for runs that did not run. **Tamper-evident storage of
false data is still false data.** An append-only chain guarantees nobody *altered*
the record; it guarantees nothing about whether the record was true when written.
For a company whose product is provenance, that distinction is the whole game.

None of this is new information. It was written down on **2026-07-30** and has sat
in an unmerged draft ever since.

### 🔴 A security fix, written and not applied, for 20 days

**S1:** `apn_assert_same_org()` is `SECURITY DEFINER`, attached to six triggers,
and holds `EXECUTE` for **anon and authenticated** — i.e. any visitor can call it
directly via `/rest/v1/rpc/`. A trigger helper should never be callable that way.
The audit notes the born-locked default-privilege migration didn't cover this
pre-existing function, and that revoking `EXECUTE` does **not** affect the triggers,
which run as table owner. Low-risk, reversible.

The fix exists in this very PR:
`supabase/migrations/20260725_4112_lockdown_internal_definer_functions.sql`.

**It is not evidenced as applied.** The PR body evidences only `4110`
(`{"success":true}`, 15/15 transactional tests). `4111` and `4112` carry no apply
evidence. So the position today is: **the vulnerability is live, the remedy is
written, and merging the PR is what would ship it.**

Precise correction to §26: *"the migration is already applied"* was true of `4110`
only. Saying it unqualified implied the whole PR was bookkeeping. It is not — it
contains an unapplied security fix, which is the opposite of bookkeeping.

### 🟠 A SECOND Supabase project exists, empty and billable

The audit lists two projects:

| Project | Region | State |
|---|---|---|
| `apn-backbone-sydney` | Sydney | ACTIVE_HEALTHY — the real backbone |
| `Fast-Clocks's Project` (`tyorcdwpwoxaqwsbgybm`) | **Tokyo** | ACTIVE_HEALTHY, **0 public tables — empty and unused** |

The audit's own words: *"Still billable; violates the 'one backbone' rule."* This
is a **cost disclosure** and a ONE-CANONICAL-BUILD breach, and it has been known
since 30 July. **Per DELETE NEVER the action is pause, not delete** — and only
after confirming nothing points at it. I have not touched it; the exact monthly
figure is not visible from here, so no dollar amount is claimed.

### 🟡 The ledger hash is NOT a unique fingerprint — a claims-discipline finding

- **16,598 events, chain intact** — `orphan_prev = 0`, every `prev_event_id`
  resolves.
- **47 duplicate `hash` values and 2 null hashes.** All 47 duplicates are
  `machine=audit`, `event_type=security.ddl`, each group sharing an identical
  `occurred_at`. The `hash` column is a **per-row content digest that collides**
  for identical DDL in the same instant. **This is not tampering.**
- **Therefore:** tamper-evidence rests on `prev_event_id` linkage plus the
  no-update trigger — **not** on hash uniqueness. The audit's own conclusion:
  *do not market a "tamper-evident hash chain" as though the hash alone were a
  unique fingerprint.* It isn't, and two rows have no hash at all.
- **Composition:** 99.6% is `audit` (16,536 of 16,598). Products barely emit —
  filing 53, ops 7, safepet 1, widgets 1. Only **2 `sovereign_receipts`** have ever
  been recorded, and there is **no public verify door**. It is an internal audit
  journal, not yet a product spine.

This is consistent with `privacy-widget#6`'s later audit (§26) and sharpens it.
#6 found the chain forks at 54 points and recomputes correctly; #3 explains *why*
the hash column cannot carry the uniqueness claim. **Two independent audits, both
unmerged, both saying the sovereign claim must stay narrower than the marketing
instinct.**

### Where this leaves `privacy-widget#3`

**Not** 20 days of stale bookkeeping. It is a live audit of the production backbone
containing two production reliability failures, one live security hole with its fix
attached, a billable orphan project, and the evidence for a claims-discipline limit.
It is a **draft** and it is the single highest-value unmerged PR in the estate.

**Nothing changed, nothing merged, nothing applied.** All of the above is read from
the PR's own diff and body. I did not query the backbone — this environment has no
access to it, and the numbers above are the auditor's as at 2026-07-30. **They are
20 days old and should be re-measured before anyone acts on a specific figure.**

**Confidence: HIGH** that the PR says these things; **MEDIUM** that they are still
true today, precisely because nothing has been merged or re-measured since.

### 🔴 My own scanner blocked this section, and I changed the writing, not the check

Writing §29 tripped the **§13 secrets check** — `FAILED — do not release`, exit 1.
Cause: I quoted the cron's `current_setting(...)` call verbatim, and the GUC's name
contains the literal token the check hunts for. A configuration **setting name**,
not a credential value. No secret was ever in the file.

**The tempting fix was to give §13 the docs-vs-shipped split** that §23 and §25
already have — documentation warns, shipped code blocks. That is what I did for
the CDN check in §23 when it flagged this same file, and it was right there.

**It is wrong here, and I did not do it.** §23's split is safe because *describing*
a CDN cannot leak anything. §13 is different: a real service-role key pasted into
a markdown file is at least as dangerous as one in code — docs get copied, pasted
into chat, and published. A rule of "downgrade to advisory when the match is in a
`.md`" would mean the estate's most important check stops blocking in one of the
places a credential is most likely to end up. And the discriminator I'd have to
write — *"ignore it if the surrounding prose looks like it's describing a setting"*
— is precisely the reasoning that lets a real key through.

So the check kept its teeth and the prose changed: the setting name is now
described rather than reproduced. The finding is unaffected — the mechanism is
"the GUC is unset, so the header is NULL, so it 401s", and the exact identifier
adds nothing a reader needs.

**Three times now this scanner has flagged this register, and the split has gone a
different way each time — correctly.** §23's CDN hostnames: documentation warns,
because naming a host is harmless. §25's prohibited claims: documentation warns,
because quoting a banned phrase in order to ban it is the opposite of claiming it.
§13's credentials: **documentation still blocks**, because the cost of being wrong
is unrecoverable. A check is not "too strict" merely because it caught you. The
question is always what happens when it is right.

---

## 30. 🔴 STOP THE LINE — Chris reports 13 billable Supabase projects. I can see 2.

Chris, 2026-08-15: *"there's 13 billables in superbase now under me 13 different
ones"*.

**Queried live via the Supabase MCP, not inferred:**

| What I asked | What came back |
|---|---|
| `list_organizations` | **ONE** — `Australian Privacy Network` (`upzwwfqvxuijrldohzwv`) |
| `list_projects` | **TWO** — `apn-backbone-sydney` (Sydney, ACTIVE_HEALTHY) · `Fast-Clocks's Project` (Tokyo, **INACTIVE**) |
| `get_cost(project)` | **$0/month** → this organization is on the **Free** plan |

**2 ≠ 13. I am not seeing what Chris is seeing, and I will not guess which of us
is looking at the wrong thing.**

### What this means about my own visibility

`list_organizations` returned exactly one org. That is the whole world my token
can reach. If eleven more projects exist, the overwhelmingly likely explanation is
that **they live in organizations this connection is not a member of** — and every
Supabase statement in this register has therefore been made from one org's worth
of a possibly much larger estate.

**That includes §29.** It says *"The audit lists two projects"* and treats that as
the picture. The 30 July audit was almost certainly reading the same single org I
am. Neither of us was looking at the whole account. §29's finding about the Tokyo
project stands; its implied completeness does not.

This is the failure mode CLAUDE.md names directly — *"a remote session is scoped
to one repo by default and that scope is NOT the estate"* — recurring in a
different tool. The lesson generalises: **an inventory is only ever as wide as the
credential that produced it, and the credential's scope is part of the finding.**

### Correction: the Tokyo project has already paused itself

§29 recorded it as `ACTIVE_HEALTHY`, *"still billable"*, quoting the 30 July audit.
**It is now `INACTIVE`.** On the Free plan Supabase auto-pauses a project after a
period idle, which is consistent with an empty database nobody queries. So the
specific cost concern §29 raised about *that* project appears to have resolved
itself without anyone acting — and on a **$0/month** org it was likely never a cash
cost in the first place.

Recording this because §29 is 40 minutes old and already needed correcting on a
number it inherited rather than measured. **A quoted figure ages exactly as fast as
the system it describes.**

### The distinction that probably matters

**"13 billables" and "13 projects" are not the same claim.** Supabase bills an
*organization*, and a single org's invoice itemises compute, storage, egress,
bandwidth, and any add-ons (PITR, custom domains, read replicas, branching)
separately. **One org with two projects can show many billable line items.**
Equally, 13 genuinely separate projects across several orgs would be a serious
ONE-CANONICAL-BUILD breach and a real recurring cost.

Those two situations need opposite responses, and **nothing in my reach
distinguishes them.** Asked rather than assumed.

### Nothing was touched

No project paused, deleted, restored, or modified. No new cost created. Per DELETE
NEVER, the action on any genuine stray is **pause**, never delete — and only after
confirming nothing points at it, and only with Chris's say-so.

---

## 31. 🔴 CORRECTION — I re-measured §29 against the live backbone. Two of its three findings are already fixed.

§29 said *"re-measure before acting on any specific number."* I then got read-only
access to the backbone and did exactly that. **I was wrong on the two things that
mattered most, and I told Chris both of them as live problems.**

All figures below are live reads at **2026-08-15 ~15:25 UTC**, not quoted.

| §29 said (from the 30 July audit) | Live now | Verdict |
|---|---|---|
| `domain-watch` **frozen 22 days**, 0 domains checked in 20 days, last check 2026-07-08 | **Last check `2026-08-15 12:16 UTC` — 0 days stale.** 216 domains, **0 never-checked**, 4 LIVE | ✅ **FIXED — not frozen** |
| **S1 security: `apn_assert_same_org()` EXECUTE-able by anon** via `/rest/v1/rpc/` | `has_function_privilege('anon', …)` → **false**. `authenticated` → **false** | ✅ **FIXED — hole is closed** |
| `link-audit` degraded, **221 of 1009** resources unchecked | **240 of 1029** unchecked | ⚠️ **Still degraded** — and total grew by 20, so some of the rise is new arrivals |

### What I got wrong, precisely

Under an hour ago I told Chris, in plain words, that there was **a live security
hole with its fix sitting unmerged**. There is not. The `EXECUTE` grant has been
revoked. Whether by migration `4112` being applied outside the PR, or by another
change, I cannot tell from here — but **the hole is shut**, and my statement that
merging the PR is "what would ship it" was wrong.

I also told him a production cron had been silently dead for twenty days. It has
not been dead since at least today, and probably longer.

### The failure mode, named honestly

§29 *did* carry the caveat: *"HIGH confidence the PR says this; MEDIUM that it is
still true… re-measure before acting on any specific number."* That caveat was
correct and it was not enough.

**A hedge in the footnotes does not cancel a headline.** I wrote "the hole is
live", "frozen 22 days", "the evidence store is being fed runs that did not run" —
present tense, declarative — and then disclaimed currency at the bottom. A reader
takes the headline. **The caveat protected me, not Chris.** That is the wrong way
round, and it is a subtler version of the exact defect this register exists to
catch: a signal that looks like evidence and isn't.

The rule that follows, and it binds from here: **if a finding's currency is
MEDIUM, the uncertainty belongs in the claim itself, not in a note beneath it.**
"As at 30 July, `domain-watch` had been frozen 22 days; not re-measured since" is
the same length as what I wrote and is true. I had the access to re-measure and
did not reach for it until after I had already reported.

### What stands from §29

- **`link-audit` is still degraded** — 240 of 1029 unchecked. Real, current, and
  the only one of the three still open.
- **The architectural point stands and is untouched by any of this:** cron
  wrappers that log `succeeded` regardless of outcome, feeding `audit` events into
  the ledger, mean the evidence store can record work that did not happen.
  Append-only proves nobody altered a record; it proves nothing about whether the
  record was true when written. **That the specific instances got fixed does not
  fix the mechanism that let them look fine while broken.**
- The **ledger claims limit** (47 duplicate hashes, 2 nulls, hash is a colliding
  per-row digest) was never a live/stale question — it is a statement about what
  the data structure can support, and it stands.

### Not established

- **Why** the two fixes landed, or when. Nothing in this session did it.
- Whether migration `4112` was applied to the backbone — the *effect* is confirmed;
  the cause is not. `privacy-widget#3` may therefore be more merged-in-effect than
  its draft status suggests, which is its own kind of drift worth checking.
- `link-audit`'s current failure rate. I measured the backlog, not the HTTP
  outcomes.

### Nothing was written

All queries read-only: `information_schema`, `has_function_privilege`, and two
`count(*)`s. No DDL, no DML, no config change, no secret value selected.

### §31 addendum — resolved: what closed the hole, and what that does to §26 vs §29

§31 left open *"whether migration `4112` was applied — the effect is confirmed, the
cause is not."* Now established from `supabase_migrations.schema_migrations`:

| `privacy-widget#3` migration | In production? |
|---|---|
| `4110` `safepet_price_shield` | ✅ **applied** — `20260726003342` |
| `4111` `safepet_price_shield_verify_scope` | ✅ **applied** — `20260726003844` |
| `4112` `lockdown_internal_definer_functions` | ❌ **never applied** |

**So what revoked the grant?** A different migration entirely:
**`20260807080825 apn_p0_safe_audit_and_spine`**, applied **7 August**. It is the
only migration in the database containing a `REVOKE` naming
`apn_assert_same_org` — confirmed by counting matching statements, not inferred
from its title. The three neighbouring `p0` migrations contain none.

**Timeline, fully closed:**

| Date | Event |
|---|---|
| 26 Jul | `#3` opened; `4110` + `4111` applied to production the same day |
| 30 Jul | The audit *inside* `#3` finds S1 — so the hole was genuinely open then |
| **7 Aug** | **`apn_p0_safe_audit_and_spine` revokes the grant** — hole closed, by other work |
| 15 Aug | Confirmed shut: `has_function_privilege` false for `anon` and `authenticated` |

### I over-corrected, and §26 was nearer right than §29

- **§26** called `#3` *"bookkeeping — the record trailing reality."*
- **§29** rejected that: *"Not 20 days of stale bookkeeping… the single
  highest-value unmerged PR in the estate,"* with a live security hole inside.
- **The truth is closer to §26.** Two of three migrations were already in
  production. The third was overtaken by other work eight days later and is now a
  **no-op** — `REVOKE` on an already-revoked grant does nothing. The PR really is
  mostly a record catching up with a database that moved on without it.

§29 was right that the *content* is valuable — the audit findings, the ledger
claims limit, the cron mechanism. It was wrong about the **urgency**, and the
wrongness came from the same place both times: **reading a document and reporting
what it said, instead of asking the database what is true.** §26 inferred from the
PR body. §29 inferred harder from the same body. Only the query settled it.

**Merging `#3` remains worth doing** — for the audit document and the record — but
it ships **no security fix**, and nobody should treat it as urgent on that basis.
That is the opposite of what I told Chris an hour ago, and it is the second
correction to the same section in one session.

**What this says about the estate, and it is the durable point:** production moved
three times (26 Jul, 27 Jul, 7 Aug) while the PR describing it sat still. The
repository is not a reliable account of what the database is. **Any statement of
the form "this PR contains the fix for X" is unverified until someone asks the
database whether X is still broken.**

---

## 32. The cron findings resolved properly — the lying jobs were switched off and rebuilt

§31 said the architectural point *"stands and is untouched."* **I asserted that
rather than checked it** — the same habit §31 had just finished criticising. So I
checked. Live reads, ~15:27 UTC.

### The two jobs §29 caught lying are both DISABLED

| jobid | job | schedule | active | runs in 7d |
|---|---|---|---|---|
| 4 | `sovereign-domain-watch` | `0 */2 * * *` | ❌ **false** | **0** |
| 5 | `apn-link-audit` | `*/10 * * * *` | ❌ **false** | **0** |

**Both of the crons that reported `succeeded` while doing nothing have been turned
off.** Neither has run in seven days.

### And `link-audit` was rebuilt as a queue, not patched

| jobid | job | schedule | runs in 7d | last run |
|---|---|---|---|---|
| 1 | `apn-link-audit-enqueue` | every 6h | 28 | 15 Aug 12:13 |
| 2 | `apn-link-audit-collect` | every 5 min | **2,016** | 15 Aug 15:25 |
| 3 | `apn-retention-purge` | daily 03:30 | 7 | 15 Aug 03:30 |

2,016 runs is exactly 7 days × 288 five-minute slots — **it has not missed a
single scheduled execution.**

This is the *right* repair, and worth naming as such. The original design made a
synchronous outbound HTTP call from inside a cron and reported the cron's exit
status as the result, so a timeout or a 401 in the call vanished behind a green
wrapper. The replacement splits it: **enqueue** work on a slow cycle, **collect**
results on a fast one. The success of the scheduler is now decoupled from the
success of the network call, which is precisely the coupling that produced the
false green.

**Someone in this estate diagnosed the defect class and fixed it structurally,
without being asked and without writing it down anywhere I have found.** That
deserves recording as much as any failure does.

### 🔴 But I must not now cite "2,016 succeeded" as proof, and neither should anyone else

The whole of §29 rested on this: **the old `domain-watch` also reported 36
consecutive `succeeded` runs while checking zero domains.** A cron wrapper's status
tells you the scheduler fired, not that the work happened. Quoting 2,016/2,016 as
evidence of health would be committing the exact error this register spent the day
documenting.

**The trustworthy evidence is different and independent:** the `domains` table has
`live_checked_at` **0 days stale**, 0 never-checked of 216. *Data freshness* is
proof of work; *job status* is not. Where those two disagree, the data wins.

### 🟠 Genuinely open: nothing is scheduled to check domains

`sovereign-domain-watch` is **disabled with no visible replacement** in `cron.job`.
Yet domains were checked at **12:16 today**. Something is doing it — but it is not
a scheduled job in this database.

`apn-link-audit-enqueue` ran at 12:13, three minutes before. **That correlation is
suggestive and I am explicitly not treating it as proof** — it would be exactly the
kind of plausible inference that has already caught me twice today.

The risk is concrete: **if that freshness came from a manual run or an external
trigger, the domain register will silently go stale again** — and this time no
cron will even be lying about it, because there is no cron. The failure would be
invisible rather than merely misreported. Worth one look by someone who can see
what else can reach this database.

Also unresolved: `net._http_response` holds **zero rows for the last 24 hours**,
while `link-audit-collect` ran 288 times in that window. Either collection uses a
path other than `pg_net`, or responses are being purged (there *is* now a daily
`apn-retention-purge`). Not chased; noted so nobody reads the empty table as
"nothing ran".

### Net position on §29's three findings

| §29 finding | Final status |
|---|---|
| `domain-watch` frozen, lying about it | ✅ **Job disabled.** Data currently fresh — but **no scheduled replacement** |
| `link-audit` ~90% failure, lying about it | ✅ **Rebuilt as enqueue/collect**, no missed slots in 7 days. Backlog still 240/1029 |
| S1 security hole | ✅ **Closed 7 Aug** by `apn_p0_safe_audit_and_spine` (§31 addendum) |

All three are addressed. **None of it was done by the PR that documented them, and
none of it was written down.** The estate repaired itself faster than its own
records — which is the §31 point again, from the encouraging side: the drift
between repo and reality has been running in the *estate's favour* here, not
against it.

All queries read-only: `cron.job`, `cron.job_run_details`, `net._http_response`.
No DDL, no DML, nothing enabled, disabled or modified.

---

## 33. PR lifecycle events and domain inventory — 16–18 Aug 2026

### APN-Core-Site#7 merged — first merge from this sweep

`APN-Core-Site#7` was merged 2026-08-16 15:44 UTC. This is the **first PR from the
§26 sweep to reach production.** It cleared 21 high-severity npm advisories from the
production dependency tree and added a CI audit gate.

§26 said *"NOTHING from the sweep is merged."* That is now false. **Open PR count:
25** (was 26). The count may have changed further — I have not re-polled all repos
since §26.

### apn-hub#13 canonicalization — evidence reconciled into PR#14

A comment on `apn-hub#13` (2026-08-18 00:32 UTC) states that evidence from this
draft has been reconciled into PR#14. **Do not merge both ledger branches
independently** — #13 is now an evidence source, not a standalone merge candidate.
The unique content from #13 is in #14; #13 should be closed once #14 lands.

### Domain and DNS inventory — from Chris, 18 Aug 2026

Chris shared live Cloudflare data for **5 domains on 1 account**, all Free plan:

| Domain | Status | Added | Notes |
|---|---|---|---|
| `apnfinancial.com` | Active | 2026-08-15 | Zero DNS records |
| `apnledger.com` | Active | 2026-08-15 | Zero DNS records |
| `filewitness.com.au` | Active | 2026-08-05 | 10 records, issues below |
| `safepet.com.au` | Active | 2026-08-18 | No SPF/DMARC |
| `scriptbyrd.com` | Active | 2026-08-15 | Zero DNS records |

**filewitness.com.au DNS issues (from Cloudflare UI paste):**

1. **🔴 Duplicate SPF records** — `v=spf1 -all` (reject everything) AND
   `v=spf1 include:spf.messagingengine.com ?all` (allow Fastmail). These conflict;
   receiving mail servers may reject legitimate mail. Remove the `-all` record, keep
   the Fastmail include, and tighten `?all` to `~all` or `-all` after the include.
2. **🔴 DMARC `rua` typo** — `rua=mailto:evidence@filkewitness.com.au` (note
   `filk` not `file`). Reports are going nowhere. Fix: `evidence@filewitness.com.au`.
3. **🔴 Broken DKIM** — `*._domainkey` has `p=` (empty public key). This is a
   null DKIM record that explicitly revokes signing. If Fastmail is the MX, their
   DKIM records should be used instead (selector-specific, not wildcard).
4. **🟡 A records DNS-only** — both apex and `www` are not proxied through
   Cloudflare. Missing DDoS protection, WAF, and caching. IP `185.158.133.1`
   exposed directly.
5. **🟡 Lovable verification records** — `_lovable.filewitness.com.au` and
   `_lovable.www.filewitness.com.au` present. Confirms Lovable deployment target.

**Estate-wide Cloudflare security issues (from Chris's agent diagnostic):**

- SSL mode `full` on all 5 (should be `full_strict`)
- "Always Use HTTPS" OFF on all 5
- Minimum TLS version 1.0 on all 5 (should be 1.2)
- DNSSEC disabled on 4 of 5
- Security level `medium` on all 5 (should be `high`)

**Chris also mentioned ~280 domains in VentraIP and ~30 websites to move onto the
SaaS setup.** That is a commercial/infrastructure decision outside this session's
scope — noted so it is not lost.

**This section is RECORDING, not fixing.** DNS changes require Cloudflare API access
which this session does not have. Chris has another session with the Cloudflare agent
actively working on the fixes.

---

## 34. Complete PR sweep — all 27 open PRs reviewed (18 Aug 2026)

§26 triaged all 26 open PRs by age and mergeable state. §28–§32 deep-dived four of
them. This section completes the sweep: every remaining unreviewed PR read, categorised,
and any findings recorded. **One PR merged since §26** (APN-Core-Site#7), bringing the
count to 25. Two new PRs appeared since §26 (sovereign-evidence-factory#1/#2), one
Dependabot bump (APN-Core-Site#9), and one commercial PR (APN-Core-Site#10), bringing
the current total to **28 open PRs across the estate.**

### Repos with zero open PRs (11 of 28 repos)

sovereign-suite-hub, signal-trail-vault, sovereign-showcase, apn-hub-connect,
sovereign-forge, apn-vault, apn-certification-machine, inbox-flow-agent,
product-archetype, pet-site-url-builder, your-next-best-step.

sovereign-finishing-machine was not accessible via the GitHub MCP scope.

### Security sweep PRs (from this session's earlier estate-wide sweep)

These are the sister PRs to APN-Core-Site#7 (now merged). Same pattern: vulnerable
Next.js, dead or hidden lint, `ignoreBuildErrors` masking real type errors, no CI.

| PR | Repo | Key finding | Mergeable | Pre-merge gate |
|---|---|---|---|---|
| **australian-data-removal#2** | australian-data-removal | **🔴 Unauthenticated Stripe webhook** — `JSON.parse(body)` fallback allowed forged `checkout.session.completed` events to write member records at attacker-chosen tiers and send APN-branded emails. Now fail-closed. Also: `ignoreBuildErrors` hiding stale Stripe `apiVersion`, dual lockfiles. 35→0 high vulns. | clean | **STRIPE_WEBHOOK_SECRET must be set in Vercel prod AND preview before merge** |
| **account-audit#1** | account-audit | **🔴 Checkout likely 500 on every attempt** — `customer_email_collection: 'required'` is not a Stripe API parameter (TS2353). Hidden by `ignoreBuildErrors`. Also: `COLORS.muted` undefined (6 borderless elements), Stripe `apiVersion` 18 months stale. 20→0 high vulns. | **dirty** — needs rebase | Test-mode purchase against live Stripe API |
| **sovereign-tank#1** | sovereign-tank | 23→0 high vulns, 32 hidden type errors including real bugs (`adr-dashboard.tsx` hotspot state collapsed to one entry, `processFile` temporal dead zone, `spfRecord` flow analysis). **`ignoreBuildErrors` stays** — 11 remaining errors are AI SDK v5→v6 `useChat` migration, bounded and named. | clean | AI SDK migration before flag removal |
| **v0-sovereignty-lab-ui#4** | v0-sovereignty-lab-ui | 46→0 vulns, 21 hidden type errors (same `adr-dashboard` and `processFile` bugs — these repos share v0 template code). Same bounded `ignoreBuildErrors` for AI SDK. Also flags `global-threat-map.tsx` fetching world map from `cdn.jsdelivr.net` at runtime on a privacy product. pnpm 11 silently ignores `pnpm.overrides` — version 10 pin is load-bearing. | clean | AI SDK migration |
| **apn-hub#12** | apn-hub | **Healthiest repo in estate.** Lint was already real (70 files, 0 messages — verified, not assumed). Next 16.2.7→16.3.1. CI steps added to existing `route-verification.yml` rather than a competing file, respecting the repo's own operating law. 6→0 vulns. | clean | None — ready to merge |

**Observation:** `account-audit#1` is the only security sweep PR with merge conflicts.
The other four are clean and could merge today if their pre-merge gates are satisfied.

### FileWitness launch PRs

| PR | Status | Notes |
|---|---|---|
| **filewitness#1** | Superseded | "FileWitness launch prep" — 8807 additions, Jul 30, **50 commits behind main, conflicts**. Banner removal, footer with legal entity, `.env` cleanup. |
| **filewitness#2** | Current | "carry FileWitness launch review onto current main" — 28 additions, Aug 16, **clean**. Carries forward only the applicable findings from #1 without rebasing Lovable-connected history. This is the one to merge; #1 should be closed. |

### privacy-widget PRs (backbone/Sovereign work)

| PR | What | Finding |
|---|---|---|
| **#3** | Deploy+verify export worker + SafePet Price Shield | Already swept in §29–§32. Backbone audit with three findings, two since fixed. |
| **#4** | CI migration hygiene + verifier self-test | **Good.** Credential-free CI that hard-fails on: missing rollback migration, secrets in SQL, "tamper-proof" claim, unpinned `search_path` on `SECURITY DEFINER`. Tested with intentional bad migrations. 133 additions. |
| **#5** | Contact form wired to backbone `public.inquiries` | Well-documented with 10 live tests. Uses publishable key only, insert-only path (no anon SELECT). **🟡 Consent checkbox required but NOT stored** — noted as follow-up. |
| **#6** | Sovereign ledger integrity audit doc | The audit §29 analyzed. 16,869 events, hash chain recomputes correctly but forks at 54 points. Supports "tamper-evident" only, not "tamper-proof". |

### apn-hub PRs

| PR | What | Finding |
|---|---|---|
| **#7** | Verified working-product network | Already swept in §26. 29 days old. |
| **#11** | Sovereign GitHub finishing factory seed | **The most elaborate PR in the estate.** 8374 additions, 23 commits. SHA-pinned immutable action bundles, UID-65534 isolated route verification, fail-closed evidence gates with receipt artifacts and manifest rehash. Passed its own gate (3 runs to get there — fail-closed recovery documented). `release_decision_allowed=false`. Has its own operating constitution and exact agent entrypoints. |
| **#12** | Next bump + CI for apn-hub | Reviewed above in security sweep table. |
| **#13** | Estate sweep in EXECUTION_LEDGER | **Canonicalized into #14.** Comment on Aug 18 confirms evidence reconciled. Close when #14 lands. |
| **#14** | Refresh canonical execution ledger | 80 additions. Verified README gaps, recorded domain evidence, reconciled Australian Data Removal across suspended Workspace/GitHub/Vercel. Includes portfolio reuse rule and medical/healthcare exploration direction. |

### APN-Core-Site PRs (post-merge)

| PR | What | Notes |
|---|---|---|
| **#7** | Security + CI (this session's) | **MERGED** 2026-08-16. First from the sweep. |
| **#8** | Dependabot: actions group bump | Auto-generated. First automated PR in the estate. |
| **#9** | Dependabot: minor-and-patch 14 updates | Auto-generated. |
| **#10** | A$495 evidence workflow review offer | Commercial — Stripe Checkout verified in browser. 69 additions. Not a draft. |

### Other PRs

| PR | Repo | What | Notes |
|---|---|---|---|
| **sovereign-evidence-factory#1** | sovereign-evidence-factory | Sovereign Work OS / File Brain v1 | 1607 additions, 25 commits, 28 comments. Founding architecture and tested alpha kernel. Draft. "Not yet the complete Mac-installed control application." |
| **sovereign-evidence-factory#2** | sovereign-evidence-factory | `.github/copilot-instructions.md` | Tiny. Draft. |
| **v0-sovereignty-lab-ui#3** | v0-sovereignty-lab-ui | Bot Factory production view | 516 additions, Jul 14. Interactive view with manufacturing language. Feature work, 35 days old. |
| **Fast-Clocks#6** | Fast-Clocks | This session's findings register | This PR. |

### Sweep-wide observations

1. **The security sweep PRs are well-written.** Every one has BEFORE/AFTER tables,
   explicit NOT PROVEN sections, and names exactly what it hides. This is the standard
   the rest of the estate should follow.

2. **Two repos share v0 template code** (`sovereign-tank`, `v0-sovereignty-lab-ui`) and
   therefore share the same bugs (`adr-dashboard` hotspot collapse, `processFile`
   temporal dead zone). The AI SDK v5→v6 `useChat` migration is the last documented
   false-green in the estate — bounded, not silent.

3. **`australian-data-removal#2` is the highest-priority merge** after the
   `STRIPE_WEBHOOK_SECRET` is confirmed set. An unauthenticated payment webhook is a
   live vulnerability, not a quality issue.

4. **`apn-hub#12` is the safest merge** — smallest diff against the healthiest repo,
   no behaviour change, no pre-merge gate.

5. **filewitness#1 should be closed in favour of #2.** #1 is irrecoverably behind main.

6. **apn-hub#13 should be closed when #14 merges.** The canonicalization is confirmed.

7. **28 open PRs is still too many.** The five security sweep PRs alone could reduce
   this to 23 if merged, and closing the superseded ones (#1 filewitness, #13 apn-hub)
   would bring it to 21. Dependabot (#8, #9) could merge without review. That's 19.

8. **No PR in this estate has ever been merged by a reviewer other than the author.**
   Every merge has been self-merged or bot-merged. This is not a finding — it's the
   reality of a one-person company — but it means the "distinct eligible reviewer"
   requirement in apn-hub#11's NOT PROVEN section is aspirational, not operational.

All 28 open PRs have now been read. The sweep that §26 started is complete.
