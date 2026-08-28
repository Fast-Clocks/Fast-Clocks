# SUPABASE SOURCE REPORT — APN Backend Inventory

**Authority:** Claude (Supabase / backend integrity / ledger / security / data-sovereignty).
**Mode:** READ-ONLY. No production changes were made.
**Inspection date:** 2026-07-23.
**Evidence labels:** CONFIRMED FACT · LIVE-DB (live database evidence) · SRC (source-code evidence) · INFERENCE · UNVERIFIED · PROPOSED.
**Reconciliation:** Temporary IDs use `SUP-` prefix, marked `AWAITING_CODEX_RECONCILIATION`.

---

## 1. Projects (Track A) — LIVE-DB

| backend_id | project | ref | region | status | PG | created |
|---|---|---|---|---|---|---|
| SUP-PROJ-SYDNEY | apn-backbone-sydney | `plhpjktkzsbfnltemhdl` | ap-southeast-2 | **ACTIVE_HEALTHY** | 17.6.1.127 | 2026-06-06 |
| SUP-PROJ-FASTCLOCKS | Fast-Clocks's Project | `tyorcdwpwoxaqwsbgybm` | ap-northeast-1 | **INACTIVE** | 17 | 2026-06-04 |

- Organization: **Australian Privacy Network** (`upzwwfqvxuijrldohzwv`). Both projects in this one org. **CONFIRMED**.
- `Fast-Clocks's Project` is INACTIVE and **not inspectable without a restore** (a prohibited op). Its purpose is **UNVERIFIED** — likely an early/abandoned project (created 2 days before Sydney, Tokyo region). Codex/Chris to confirm before any retirement.
- Canonical active backend = **apn-backbone-sydney**. **CONFIRMED**.

## 2. Public schema objects (Track C) — LIVE-DB

**21 base tables, 3 views, 1 storage bucket, 17 functions, 3 triggers, 5 cron jobs, 3 installed non-default extensions.** All 21 tables report `rls_enabled = true`.

Row counts at inspection (time-sensitive): resources **1423**, apn_ledger_events **13158**, domains **216**, resource_categories 30, packages 7, brands 5, verticals 4, audit_config 1, company_profile 1. All other public tables **0 rows** (inbox_*, network_*, ads, inquiries, jobs, waitlist, manual_resources, resource_submissions, link_audit_queue). → Most of the "network / inbox / sales" layer is **DEPLOYED BUT EMPTY** (schema shipped, not yet populated). Do not read an empty table as a finished product.

Views: `resource_register`, `contributor_wall`, `security_audit_log` — **no anon/authenticated grant** (service_role only). Not a public surface today.
Storage: one bucket `inbox-uploads`, **private**. **CONFIRMED**.

## 3. Read/write surface & tenant isolation (Track D) — LIVE-DB

**Anonymous (`anon`) can SELECT (RLS-gated):** ads (active window), brands (active), domains (`status in live/listed-for-sale`), jobs (active window), network_nodes (active), packages (active+listed), resource_categories (active), resources (`is_published AND link_status<>'broken' AND distribution_scope='network-wide' AND withheld_reason IS NULL`), verticals (active).
**Anonymous can INSERT (validated WITH CHECK):** inquiries (email format + length caps), resource_submissions (status forced `pending`, email validated), waitlist (email validated).
**Deny-all to public (`USING false` or no grant):** link_audit_queue, manual_resources, resource_submissions SELECT, network_events, apn_ledger_events (no anon grant), audit_config, inbox_* (owner-isolated by `auth.uid()`).

Classifications:
- `audit_config` → **DENY-ALL INTENTIONAL**. RLS enabled, zero policies, grant only to service_role. Holds the link-audit `cron_secret`. Advisor `rls_enabled_no_policy` is **expected**, not a defect. **CONFIRMED** (leak-free).
- `company_profile` → **DENY-ALL to anon in practice**. RLS enabled + zero policies means anon SELECT returns **no rows** even though a legacy `SELECT` grant exists for anon/authenticated. No private company data is exposed. The `SELECT` grant is a harmless leftover (RLS wins). **CONFIRMED** (no leak). *Open question:* how is public company info meant to surface? No public view/function currently exposes it → **DOCUMENTATION GAP**.
- `resources` → **PUBLIC READ INTENTIONAL** but **column-broad**. RLS filters rows correctly (withheld/unpublished/broken cannot leak — CONFIRMED), **but** anon reads the **base table with all columns**, including internal ops fields (`check_notes`, `verification_evidence`, `source`, `escalate_to_adr`, `http_status`, `distribution_scope`, `withheld_reason`). The `resource_register` view (public-safe columns) exists but is **not granted to anon**, so the site reads the base table. → **MEDIUM finding**: internal columns exposed to anon for published rows. Confirm intent / switch public reads to the view.
- `inbox_*` → **AUTHENTICATED USER ISOLATED** by `auth.uid() = created_by`. No org/tenant field yet (single-user isolation, not multi-tenant). **LIVE-DB**.
- `resource_submissions` → **PUBLIC INSERT VALIDATED**; contributor_email private (no public SELECT). **CONFIRMED**.

FORCE ROW LEVEL SECURITY: **none** of the tables set FORCE RLS → table owner and `service_role` (BYPASSRLS) are not constrained by RLS. Expected for service-role server logic; noted for completeness.

## 4. Functions (Track C/D) — LIVE-DB

17 functions. **14 SECURITY DEFINER**, all with pinned `search_path` (hardened — good). 3 SECURITY INVOKER trigger/helper fns with `search_path=''` (born-locked).

**Critical grant finding:** every SECURITY DEFINER "public-safe" read function — `recent_ledger`, `ledger_counts_public`, `lookup_verification`, `resources_status_public`, `link_health_summary` — is `EXECUTE`-granted to **service_role only**. `anon`/`authenticated` are **not** granted EXECUTE. Only `apn_block_ledger_mutations` and `set_updated_at` (triggers) are PUBLIC/anon-executable (harmless). → **There is no direct anonymous DB verification pathway today.** Public verification, if any, must route through a server holding the service key. **CONFIRMED (LIVE-DB).**

Admin/maintenance SECURITY DEFINER fns (service_role only): `accept_resource_submission`, `erase_subject` (GDPR/APP erasure by email), `purge_expired` (retention), `audit_enqueue`/`audit_collect` (link-audit pipeline), `apn_audit_ddl_end`/`apn_audit_sql_drop` (DDL self-audit), `security_definer_leaks` (self-monitoring).

## 5. Ledger (Track E) — LIVE-DB + SRC

`apn_ledger_events` (13,158 rows). Comment: *"Shared append-only audit spine for all four APN machines. Hash chain optional. No public SELECT."* Machines: `hash-cert`, `audit`, `communication`, `filing`.

- **Triggers:** `apn_ledger_no_update` BEFORE UPDATE/DELETE → `apn_block_ledger_mutations()` which `RAISE EXCEPTION 'apn_ledger_events is append-only'`. `ledger_chain_trg` BEFORE INSERT → `ledger_chain()`.
- **`ledger_chain()`** (SECURITY DEFINER) sets `new.prev_event_id` = latest row (global, `order by occurred_at desc, id desc limit 1`) and `new.hash = sha256(prev.hash|'genesis' || occurred_at || event_type || subject_id || payload::text)`. → the chain is a **single GLOBAL chain**, hash set on **every** insert (so "optional" understates it — it is effectively mandatory & global). **HASH-LINKED (global).**
- **Contradiction (SRC):** `domain-watch` computes its own **per-machine** hash and supplies `hash`/`prev_event_id` on INSERT, but the BEFORE-INSERT trigger **overwrites** both. The per-machine hash never persists. Two chaining schemes collide; the global one wins. → flag `LEDGER-CHAIN-DUAL-SCHEME`.
- **Append-only gap (LIVE-DB):** UPDATE/DELETE are blocked for all roles (triggers fire regardless of role; service_role is not superuser). **BUT** row triggers do **not** fire on `TRUNCATE`, and `service_role` holds the `TRUNCATE` grant on `apn_ledger_events`. → a service-role key could wipe the ledger. **MEDIUM finding** `LEDGER-TRUNCATE-BYPASS`.
- **Concurrency (INFERENCE from SRC):** `ledger_chain()` reads the head with no advisory lock; concurrent inserts can both read the same `prev` and create sibling entries sharing `prev_event_id` (a fork). Low likelihood at current volume, real at scale. `LEDGER-CONCURRENT-FORK`.
- **Determinism / portability:** payload is hashed as `payload::text` (Postgres jsonb text form) — deterministic **inside** PG, but there is **no documented canonical serialization** and **no hash-format version field**. Independent verification outside Supabase is **not currently reproducible without replicating PG's jsonb text + the exact concatenation**. → **APN-DEPENDENT VERIFICATION.**
- **Timestamps:** `occurred_at default now()` = **database-generated** server clock. Not a trusted external timestamp. Do not claim "trusted timestamp".
- **Public read of ledger:** only via SECURITY DEFINER fns, and those are **not granted to anon** (see §4). So the ledger is neither publicly readable nor publicly verifiable in this project today.

**Two-ledger reconciliation (UNVERIFIED / CONFLICT):** the Sovereign Engine *System Definition* doc describes a different ledger — `ledger_entries` with `UNIQUE(event_id, seq)`, `verification_records`, RFC 6962 Merkle roots, Ed25519 `sign-manifest`, `network_ledger_entries`. **None of those objects exist in this account.** That schema belongs to the Lovable "APN Ledger Trust" project (`54595d8a-…`) and its Supabase is **not visible in org `upzwwfqvxuijrldohzwv`**. → `SUP-RECON-LEDGER-LOCATION`: locate the APN-Ledger-Trust Supabase project (may be a separate account/org or Lovable-managed). Do **not** conflate `apn_ledger_events` (this project) with `ledger_entries` (the doc).

## 6. Edge Functions & cron (Track G) — SRC + LIVE-DB

| fn | verify_jwt | auth | schedule(s) | writes | external calls |
|---|---|---|---|---|---|
| `domain-watch` v1 | **true** | service-role JWT (cron passes `app.settings.service_role_key`) | `sovereign-domain-watch` `0 */2 * * *` | domains, apn_ledger_events | `dns.google`, `https://{domain}` HEAD |
| `link-audit` v2 | **false** | **custom**: `x-audit-key` == `audit_config.cron_secret` (else 401) | `apn-link-audit` `*/10 * * * *` | resources (PATCH), apn_ledger_events | curated resource URLs (HEAD/GET) |

Additional cron (pg_cron): `apn-link-audit-enqueue` (`13 */6 * * *` → `audit_enqueue(60)`), `apn-link-audit-collect` (`*/5 * * * *` → `audit_collect()`), `apn-retention-purge` (`30 3 * * *` → `purge_expired()`).

- `link-audit` **verify_jwt:false is legitimate** — complete shared-secret auth, secret read server-side by pg_cron / service-role REST and never returned to clients. **CONFIRMED (SRC).** No replay protection (nonce/timestamp) — LOW risk for an idempotent job.
- **SSRF (SRC, MEDIUM-LOW):** both functions `fetch()` external URLs with `redirect: "follow"` and **no private-IP / metadata egress filtering**. URLs are curated (resources are admin/reviewed; domains are the register) so request-time attacker control is low, but a curated/redirecting URL could reach internal/metadata addresses. Recommend an egress allowlist / block RFC1918 + link-local. `EDGE-SSRF-EGRESS`.
- Secret handling: `domain-watch` cron embeds `service_role_key` via `current_setting('app.settings.service_role_key')` (a DB GUC). Secret-at-rest in Postgres settings — standard pattern; **value not retrieved**. Env names only recorded: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`.

## 7. Migrations & drift (Track F) — LIVE-DB (names only)

33 migrations. Named migrations (26) show a coherent arc: engine-room → resources v2 → waitlist → import staging → sales/community/jobs/network → machines foundation → domain classification → link-audit engine → **tamper-evident ledger & API** → retention/erasure → resource lockdown → **harden search_path & lockdown destructive RPCs** → **least-privilege grants** → **born-locked default privileges** → domain live-check + watch cron → resource register public view → submissions & recognition → accept-submission fn → audit_config secret → **inbox v0 schema & ledger lane**.
**7 generated-UUID-named migrations** (2026-07-17 → 2026-07-21) = **Lovable dashboard authorship signature**. Their SQL is **not retrievable via MCP** → content is **UNVERIFIED**; needs repo reconciliation (Codex). This confirms **dual migration ownership** (named CLI/Claude migrations + UUID Lovable migrations) → drift risk. `SUP-RECON-MIGRATIONS`.

## 8. Personal information (Track H) — LIVE-DB. **REQUIRES LEGAL REVIEW** for lawful-basis conclusions.

| object | fields | collected by | public exposure | retention |
|---|---|---|---|---|
| inquiries | name,email,phone,company,message | anon contact form | none (service SELECT only) | `purge_expired` (verify rule) |
| waitlist | email,name,message,user_agent,referrer | anon launch signup | none (no SELECT) | verify |
| resource_submissions | contributor_name,contributor_email,contributor_note | anon submit | email **private** | until reviewed |
| inbox_projects/queue/rules | created_by (auth uid) | authenticated | owner-isolated | n/a |
| network_events | ip_hash (hashed), user_agent | system | none | verify |
| company_profile | ACN, contact_email, postal_address | internal | denied to anon | n/a |

No raw biometrics, no government IDs, no card data observed. `erase_subject(email)` provides an erasure pathway (verify coverage). Residency: **ap-southeast-2 (Sydney)** for all of the above. **CONFIRMED.**

## 9. Advisors — LIVE-DB
- Security: `rls_enabled_no_policy` on `audit_config` + `company_profile` (both **intentional deny-all**, INFO), `extension_in_public: pg_net` (WARN — move out of `public`).
- Performance: 8 unindexed FKs (incl. `apn_ledger_events.prev_event_id` — relevant to chain lookups), 13 `auth_rls_initplan` re-eval warnings on inbox/ledger policies (wrap `auth.uid()` in `(select …)`), 7 unused indexes.

---
_Generated by [Claude Code](https://claude.ai/code)_
