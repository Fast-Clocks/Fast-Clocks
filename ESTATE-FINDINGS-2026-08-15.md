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
