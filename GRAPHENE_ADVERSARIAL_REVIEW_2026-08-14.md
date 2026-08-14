# GRAPHENE — INDEPENDENT ADVERSARIAL REVIEW

**Date:** 14 August 2026
**Reviewer role:** independent adversarial architect (paper review, no implementation)
**Scope:** the Claude Review Packet as supplied
**Run budget:** 60 minutes

---

## 1. Terminal state and elapsed time

**Terminal state: `RUNTIME_LIMIT` (partial) — analysis completed, evidence channel degraded.**

I am not returning `PAPER_COHERENT`, and the reason is not stylistic. The packet instructs: *"Do not review only this summary if the companion files are available. Read the full canonical architecture before deciding whether a component is absent."* Two independent degradations applied:

| Degradation | Effect | Evidence |
|---|---|---|
| ~~All three companion files absent from the working repository~~ **← THIS FINDING WAS MY ERROR. See §13 correction.** | I searched one repo's filenames and declared the evidence base missing. I never called `list_repos`. The account holds **27 repos**, and `apn-provenance-keeper` contains a working implementation of much of the architecture. The companion *documents* were still not located, but "the architecture is absent" was false and I should not have written it. | `Fast-Clocks/Fast-Clocks` does contain only `README.md`. That was true and irrelevant — it is a profile stub, not the estate. |
| Direct primary-source fetch egress-blocked | `w3.org`, `developers.cloudflare.com`, `eips.ethereum.org`, `oaic.gov.au` all return `EGRESS_BLOCKED` via WebFetch. | Proxy is enabled and non-selective; block is network-policy, not TLS. |

I worked around the second degradation for the highest-value facts by querying **Cloudflare's own documentation service directly**, which returns verbatim documentation text including table rows — that is a primary channel and I have labelled those findings accordingly. Remaining standards facts were confirmed through search-result convergence only, and are labelled `🟦-indirect`. **Every evidence label below carries its channel. Do not promote a `🟦-indirect` to `🟦` without a direct fetch.**

Elapsed: within the 60-minute budget. The analytical pass over the packet is **complete** — this is not `TIME_EXHAUSTED`. I did not stop early because a search was difficult.

---

## 2. Verdict

**Coherent and implementable, conditional on the patches below. No fundamental blocker to the ordinary 50–60-site platform.**

Three findings materially change the design rather than merely sharpening it:

1. **H-02 — the strict Australian profile has an unresolvable metadata-residency gap on Cloudflare.** The packet's own claim is directionally correct but not severe enough. Verified: Cloudflare's Customer Metadata Boundary supports **the United States and the European Union only**; Australia is explicitly `✘`. Edge-only use still generates Customer Logs, and those cannot be confined to Australia at all. This is an owner cost decision, not a wording fix.
2. **H-09 — a genuine internal contradiction** between the "one Mission Control" objective (§2, §11) and Locked Invariant 16 (strict environment has separate administration and authority). One of the two must yield. I recommend the objective yields, in a specific and cheap way.
3. **H-17 — availability of the deterministic core was never regression-checked against the owner's revenue path.** A mandatory gate in front of every consequential action, with no stated degradation contract, means gate degradation is either total commercial outage or security collapse. The packet demands availability regression checks and never performs one on its own core.

Everything else is repairable by narrowing a claim, naming a contract, or adding a test. The architecture's discipline is unusually good — in particular §10 (risk curve) and §17 (baseline preservation) avoid the errors that normally sink this class of design. My substantive criticisms cluster in **composition and operations**, not in the security model.

---

## 3. Source register

Direct primary links, with retrieval date and channel. `CF-DOCS` = Cloudflare documentation service (returns verbatim doc text — primary). `SEARCH` = search-result convergence across ≥2 independent results (weaker — flagged).

| # | Source | Fact established | Date/version | Channel |
|---|---|---|---|---|
| S-1 | https://developers.cloudflare.com/durable-objects/reference/data-location/ | Durable Object supported jurisdictions are exactly **`eu`, `us`, `fedramp`**. No `au`. Verbatim table retrieved. | Retrieved 14 Aug 2026 | `CF-DOCS` 🟦 |
| S-2 | https://developers.cloudflare.com/changelog/post/2026-06-26-durable-objects-us-jurisdiction/ | `us` jurisdiction added **26 June 2026** — the jurisdiction list is actively changing. | 26 Jun 2026 | `CF-DOCS` 🟦 |
| S-3 | https://developers.cloudflare.com/data-localization/region-support/ | **Australia: Geo Key Manager ✅ (v2 only), Regional Services ✅, Customer Metadata Boundary ✘.** Verbatim table row retrieved. | Doc modified 1 Jul 2026 | `CF-DOCS` 🟦 |
| S-4 | https://developers.cloudflare.com/data-localization/metadata-boundary/ | *"stored exclusively in the European Union (`eu`) or the United States (`us`)… Customer Metadata Boundary supports these two regions only; by default no boundary is applied and logs may be stored in Cloudflare's core data centers globally."* | Doc modified 23 Jul 2026 | `CF-DOCS` 🟦 |
| S-5 | https://developers.cloudflare.com/data-localization/region-support/ | **"IRAP Protected"** Regional Services region *"includes IRAP-assessed data centers, **which may be located outside Australia**."* | Doc modified 1 Jul 2026 | `CF-DOCS` 🟦 |
| S-6 | https://developers.cloudflare.com/kv/reference/data-location/ | Workers KV jurisdictions (`eu`/`us`/`fedramp`) are **private beta**, access by account-team request. | Retrieved 14 Aug 2026 | `CF-DOCS` 🟦 |
| S-7 | https://developers.cloudflare.com/changelog/post/2025-11-05-d1-jurisdiction/ | D1 jurisdiction is **set at creation only, immutable thereafter**. | 5 Nov 2025 | `CF-DOCS` 🟦 |
| S-8 | https://www.w3.org/TR/vc-data-model-2.0/ · https://www.w3.org/news/2025/the-verifiable-credentials-2-0-family-of-specifications-is-now-a-w3c-recommendation/ | VC Data Model 2.0 family is **W3C Recommendation, 15 May 2025**. Packet's pin is current. | 15 May 2025 | `SEARCH` 🟦-indirect |
| S-9 | https://www.w3.org/TR/vc-di-ecdsa/ · https://www.w3.org/TR/vc-di-ecdsa-1.1/ | `ecdsa-jcs-2019` exists and uses JCS; **P-384 pairs with SHA-384**. **A v1.1 now exists alongside the v1.0 REC.** | v1.0 REC; v1.1 published | `SEARCH` 🟦-indirect |
| S-10 | https://www.w3.org/TR/vc-bitstring-status-list/ · https://w3c.github.io/vc-bitstring-status-list/ | Bitstring Status List v1.0 REC 15 May 2025; **v1.1 in draft**. | 15 May 2025 | `SEARCH` 🟦-indirect |
| S-11 | https://eips.ethereum.org/EIPS/eip-5192 | ERC-5192 Minimal Soulbound is status **Final**. Packet's pin is safe. | Final | `SEARCH` 🟦-indirect |
| S-12 | https://www.oaic.gov.au/privacy/australian-privacy-principles/australian-privacy-principles-guidelines/chapter-8-app-8-cross-border-disclosure-of-personal-information | APP 8 + s 16C: the APP entity **remains accountable** for an overseas recipient's acts that would breach the APPs. | Guidelines Oct 2025 v1.3 | `SEARCH` 🟦-indirect |
| S-13 | https://www.oaic.gov.au/privacy/your-privacy-rights/more-privacy-rights/statutory-tort-for-serious-invasions-of-privacy | Statutory tort for serious invasions of privacy **commenced 10 June 2025**; automated-decision provisions have a grace period to **10 December 2026**. | 10 Jun 2025 | `SEARCH` 🟦-indirect |
| S-14 | https://www.rfc-editor.org/rfc/rfc8785 | JCS. Cited by packet; not independently re-fetched this run. | RFC 8785 | 🟨 unverified-in-run |
| S-15 | ASD ISM / PSPF | Cited by packet as baseline. **Not verified this run** — egress-blocked. Do not treat §17's ISM references as evidenced. | — | 🟥 unverified-in-run |

---

## 4. Hole register

Risk vector: **S**ecurity · **P**rivacy · **A**vailability · **L**egal · **O**perability · **C**ost.

| ID | Type | Claim that fails | Risk | Status |
|---|---|---|---|---|
| H-01 | Missing evidence | Companion files unavailable; prior repairs unverifiable | O | 🟥 OPEN — not repairable by me |
| H-02 | Provider constraint | "Strict profile keeps evidence/logs in verified Australian services" — Cloudflare metadata cannot be AU-resident | P L C | 🟦 Repaired by narrowing + owner decision |
| H-03 | Missing contract | Revocation has no stated propagation bound; capability checked at issue, not use | S | 🟦 Repaired |
| H-04 | Contradiction | AI-triggered hostile restriction vs. Invariant 2; adversarial false-positive induction unaddressed | S A | 🟦 Repaired |
| H-05 | Legal/authority gap | Deception cell collection has no lawful-basis gate | L P | 🟦 Repaired by reuse |
| H-06 | Overclaim | Acquisition "contract" is unilateral; far endpoint never agrees | L | 🟦 Repaired by narrowing |
| H-07 | Missing contract | No estate-level false-alarm budget across 50–60 sites × N variables | O A | 🟦 Repaired |
| H-08 | Implementation risk | Bare scalar projection will be cross-compared despite prohibition | O | 🟦 Repaired structurally |
| H-09 | **Contradiction** | One Mission Control vs. Locked Invariant 16 | S O | 🟦 Repaired — objective yields |
| H-10 | Implementation risk | "Same signed release" across profiles with different services = untested strict-only paths | S A | 🟦 Repaired |
| H-11 | Missing contract | Capability board lacks effect classes; irreversible effects undifferentiated | S C | 🟦 Repaired |
| H-12 | Missing contract | External standard versions not under the same version discipline as internal policy | S O | 🟦 Repaired |
| H-13 | Missing contract | DSSE/JCS composition order unstated → signature/payload confusion | S | 🟦 Repaired (sharpens an already-open item) |
| H-14 | Missing contract | Baseline rule forbids subtraction, not addition-induced weakening or automation complacency | S | 🟦 Repaired |
| H-15 | Implementation risk | §22 "first proof" is a small product, not a falsification test | C O | 🟦 Repaired |
| H-16 | Missing contract | Capability-to-subject sealing rule stated nowhere in the architecture (only in the test list) | S | 🟦 Repaired |
| H-17 | **Missing contract** | No degradation contract for the gate itself; fail-closed = total commercial outage | A C | 🟦 Repaired |

---

## 5. Patches

Precise replacements. Not stylistic rewrites.

### PATCH-02 — §15, strict deployment (replaces the Cloudflare paragraph)

The current text is correct but under-states the constraint and invites a specific operator error.

> **Strict-profile residency, two tiers.** Residency claims must be made separately for authoritative state and for provider observability metadata; they are not the same and only one is achievable in Australia today.
>
> **Tier A — authoritative state (achievable).** Private payloads, evidence, policy, memory, objects, keys and application logs are held in separately verified Australian services. Cloudflare Durable Objects, D1 and Workers KV are **not eligible** to hold Tier A state in this profile: their supported jurisdictions are `eu`, `us` and `fedramp` only [S-1], with no Australian option. D1's jurisdiction is immutable after creation [S-7] and KV's is private beta [S-6]; neither may be relied upon in a signed manifest without an account-team-confirmed entitlement recorded as an owner fact.
>
> **Tier B — provider observability metadata (NOT achievable in Australia).** Cloudflare Customer Logs — request URLs, timestamps, firewall events, i.e. data capable of identifying end users — can be bounded only to the **United States or the European Union**; Australia is explicitly unsupported, and with no boundary set they may be stored in Cloudflare core data centres globally [S-3][S-4]. Edge-only, orchestration-only use of Cloudflare **does not avoid this**: the metadata is generated by the edge function itself.
>
> **Operator trap, explicitly named.** The Regional Services region labelled **"IRAP Protected" is not an Australian-residency control.** Cloudflare states it comprises IRAP-assessed data centres *"which may be located outside Australia"* [S-5]. Selecting it satisfies an assessment-standard constraint, not a geographic one. A manifest that treats `IRAP Protected` as equivalent to Australian residency is invalid and must fail release validation.
>
> **Required owner decision (cannot be resolved in architecture).** One of:
> - **B1** — accept Tier B metadata in US or EU, record it as an APP 8 cross-border disclosure with the consequence manifest of §18, and accept that the owner **remains accountable** for the overseas recipient's handling under APP 8 / s 16C [S-12];
> - **B2** — remove Cloudflare from the strict profile's request path and place ingress on an Australian-hosted edge, accepting the loss of Cloudflare's security functions and the cost/latency change;
> - **B3** — obtain a written Cloudflare commitment extending CMB to Australia. **Not currently available**; may not be assumed.
>
> Until one is signed, the strict profile's residency claim is narrowed to: *"authoritative state is Australian-resident; provider traffic metadata is not, and is disclosed."* Any broader claim is unevidenced.

**Regression:** Security unchanged. Privacy — claim now matches evidence rather than exceeding it (satisfies "evidence never claims more than it proves"). Legal — surfaces a real APP 8 obligation the packet did not name. Cost — B2 is materially more expensive; that is now visible rather than hidden. Availability — B2 removes Cloudflare's DDoS posture from the strict profile; flag as a regression to be accepted knowingly. Portability improved (Tier A is provider-neutral by construction).

**Failed route retained:** "Use Cloudflare with `eu` jurisdiction as a proxy for strong protection." Rejected — solves a GDPR-shaped problem, not an Australian-residency one, and creates a second cross-border disclosure rather than removing one.

### PATCH-03 — §6, add revocation propagation bound

> Every issued capability carries a hard expiry not exceeding a declared `max_capability_ttl`, and is validated at **use** time — not only at issue time — against a signed, monotonically increasing revocation epoch published by its issuing authority. A gate that cannot obtain an epoch no older than `revocation_propagation_bound` fails closed for that capability. `revocation_propagation_bound` is a published, measured policy parameter, not an aspiration.
>
> **Acceptance:** revoke at T; attempt use at T+ε for ε across the bound; every use after `T + revocation_propagation_bound` must DENY. Report the measured distribution, not the target.

**Rejected route:** online authority check on every use. Rejected — converts every gate into a dependency on a single service, directly contradicting the availability and modularity regression criteria, and creates the estate-wide blind-fault condition §7 exists to eliminate. Epoch + TTL is strictly smaller and fails closed on the same evidence.

### PATCH-04 — §8, AI restriction asymmetry and false-positive weaponisation

Add as a **derived invariant** (not a new subsystem):

> **21. Directional AI authority.** A model may move the system only toward a *more* restrictive state, never toward a less restrictive one. An AI-originated restriction is recorded as an inference-class signal, never as a verified fact, and is always reversible through the §8 clean-context recovery route.
>
> **Adversarial induction bound.** Because an AI-triggered restriction is a consequential action available to anyone who can shape observable traffic, an adversary can attempt to induce restriction of a *legitimate* tenant as a denial-of-service. Every AI-originated restriction path is therefore rate-limited per target, budgeted per period, and, above a signed threshold of restrictions against a single legitimate tenant, escalates to deterministic review instead of auto-restricting.
>
> **Acceptance:** adversary attempts to induce quarantine of a legitimate cell. Measure legitimate-tenant availability impact and recovery latency against a declared bound. Failing this test fails the core.

**Why this is material:** the packet's §8 defends thoroughly against the attacker *escaping* containment and never against the attacker *aiming containment at someone else*. That is the cheaper attack against a 50–60-tenant commercial estate.

### PATCH-05 — §8, deception cell lawful basis (reuse, no new subsystem)

> Deception-cell activation requires a signed `deception_authority` record naming lawful basis, jurisdiction, data classes captured, retention and destruction. This reuses the §9 acquisition-contract record shape unchanged — a deception cell is an acquisition of interaction data under a declared authority, not a new object type.

### PATCH-06 — §9, narrow "contract" to what is actually binding

> Policy-bounded acquisition produces two distinct records over one shape:
> - **`AcquisitionUndertaking`** — self-binding and externally auditable, enforceable **against Graphene only**. The source has not agreed to it. Enforcement points: declared rate, identified user agent, contactable operator identity, published opt-out endpoint, honouring published terms where legally relevant, deletion-on-request path.
> - **`AcquisitionAgreement`** — used only where an executed instrument exists (API terms accepted, written licence). References the instrument.
>
> `authorized` in "bounded identified crawler only where authorized" is defined as: an executed licence, **or** published terms permitting the specific use, **or** a legal basis assessed and recorded by a named competent person. Absent all three, the crawler does not run.

**Answering the packet's own question directly:** policy-bounded acquisition protects the *acquiring* endpoint well and the *far* endpoint only by unilateral undertaking. Describing both as "protected within a declared contract" overstates the far side. The mechanism survives; the claim narrows.

### PATCH-07 — §10, estate-level alarm budget

> The canonical record gains an estate-level term. Per-chart false-alarm properties (e.g. ARL₀) **do not compose**: across N charts, expected false alarms scale approximately N/ARL₀. Across 50–60 sites × multiple variables, per-chart-correct limits produce an operator-hostile alarm rate and the predictable failure is a real alarm lost in noise.
>
> Add: `estate_alarm_budget` — declared expected false alarms per operator per period; per-profile control limits **derived from** that budget (explicit ARL₀ allocation, or FDR control across the active chart set); and `alarm_budget_utilisation` surfaced in Mission Control.
>
> **Acceptance:** inject known-null data across N profiles simultaneously; count alarms; compare against budget.

**Regression:** Operability strongly improved — this is the single change most protective of the "one operator" objective. Security: raising limits to meet a budget reduces per-chart sensitivity; that trade must be stated per profile, not hidden. Cost neutral.

### PATCH-08 — §10, make the projection constraint structural

> The 1–1,000 / 1–1,000,000 projection is never returned as a bare scalar. The typed API response has no unlabelled numeric field: the projection is always carried with its domain identifier, its state band (`normal | watch | challenge | stop | unknown`), and its profile version. Cross-domain aggregation, ranking or averaging of the projection is rejected at the type level, not discouraged in guidance.

Rationale: the packet correctly forbids cross-domain comparison and then ships a single number on a screen. Prohibition by documentation loses to a number in a UI every time. Structural refusal is the design's own stated principle ("security and privacy are structural defaults rather than optional decorative products") applied consistently.

### PATCH-09 — §4/§11, resolve the Mission Control contradiction

> **Mission Control is a per-environment instance of the same signed release, not one instance spanning environments.** The ordinary platform and the strict deployment each run their own Mission Control with separate credentials, separate identity and no cross-environment addressing. An operator addressing "the network" addresses the network *of the environment they are authenticated to*, and no scope selector can reach across the boundary.
>
> The §2 objective is preserved as stated intent — **one interface grammar, learned once** — not one live session with universal reach. The owner context-switches between environments; the UI, contracts and vocabulary are identical.

**Rejected route:** a federating super-console with read-only cross-environment visibility. Rejected — read-only is not a safe qualifier here: a console that can *observe* both environments is itself a cross-domain path and an aggregation point for exactly the correlation Invariant 16 exists to prevent. It also becomes the highest-value target on the estate. It moves the failure rather than removing it.

**Regression:** Security and privacy preserved (Invariant 16 intact). Operability mildly degraded — one context switch — which is the correct price. Modularity improved.

### PATCH-10 — §15, prove the release under both profiles before signing

> Because the strict profile excludes services the ordinary profile uses (§15, PATCH-02), "the same signed release" means identical artefact, **not** identical exercised behaviour. A release is signed only after the full acceptance matrix executes under **both** environment profiles, with profile-conditional coverage recorded in the release evidence. Any code path reachable only under the strict profile and not exercised in that run blocks signing.

### PATCH-11 — §13, effect classes on the capability board

> Every capability declares an effect class:
> - **`REVERSIBLE`** — full undo available (DNS desired-state change, campaign pause).
> - **`COMPENSABLE`** — no undo; a compensating action exists (payment refund).
> - **`IRREVERSIBLE`** — neither (email/SMS sent, publication, on-chain mint).
>
> `IRREVERSIBLE` capabilities require explicit pre-commit authorization and a **local effect-ID ledger consulted before dispatch**. This yields *at-most-once initiation locally*; at-least-once delivery at the provider remains, per Hard Limit 19. State the residual precisely: **duplicate delivery remains possible; duplicate initiation is prevented.** Do not describe provider idempotency keys as a general solution — Stripe honours them, most email transports do not.
>
> **Acceptance:** crash and resume mid-dispatch; assert no re-initiation.

### PATCH-12 — §16, external standard version pins

> The release carries `ExternalStandardPin` records — `{standard, version, canonical URL, retrieved date, hash of retrieved specification, next review date}` — using the existing evidence-record shape. **A release fails to sign if any pin is past its review date.**
>
> This is required, not tidy: `vc-di-ecdsa` now has a **v1.1** alongside the v1.0 Recommendation [S-9] and Bitstring Status List has a **v1.1 in draft** [S-10], while Cloudflare's Durable Object jurisdiction list changed as recently as **26 June 2026** [S-2]. An architecture whose internal policy versions form signed monotonic chains cannot leave its external dependencies un-versioned. Hard Limit 14 ("maintenance cannot be eliminated") is thereby answered with a mechanism rather than an admission.

Current pins verified this run: VC Data Model 2.0 — Recommendation, 15 May 2025 ✅ [S-8]; Bitstring Status List v1.0 — Recommendation ✅ [S-10]; `ecdsa-jcs-2019` with P-384/SHA-384 ✅ [S-9]; ERC-5192 — Final ✅ [S-11]. **The packet's cryptographic pins are current.**

### PATCH-13 — §16, fix the DSSE/JCS composition order

The packet correctly marks the envelope byte profile as open. Sharpening it to be actionable, and closing one security-relevant gap inside it:

> Canonicalize the typed payload with RFC 8785 JCS → **that byte string is DSSE's `payload`** → DSSE PAE over `(payloadType, payload)`. `payloadType` is a URI from a registry pinned in the release.
>
> **The verifier must re-canonicalize the received payload and byte-compare it against the received bytes, rejecting any non-canonical payload before signature verification is considered meaningful.** Without this clause, two distinct byte sequences can carry the same semantic object, and payload-substitution/confusion becomes available. Cross-language golden vectors must include non-canonical negative cases, not only positive ones.

### PATCH-14 — §17, close the baseline rule's logical gap

The rule forbids G from *removing* a control. Composition can weaken a baseline without touching any individual control. Extend:

> **G must not introduce any path that reaches a `B`-protected asset without traversing every mandatory `B` control**, and the composition must be assessed for **automation-induced degradation of human baseline steps** (an operator who trusts G's evidence and reduces their own scrutiny has weakened `B` while every control remains formally intact).
>
> Add to the §17 measurement list: **operator vigilance effect** — inject defects detectable only by a human baseline step; compare detection rates under `B` and under `B+G` using the hidden-ground-truth scorer already specified. A `B+G` that improves every machine metric while lowering human detection is **not** materially stronger.

**Answering the packet's question directly:** as originally written, the rule preserves the baseline against subtraction but not against addition or complacency. With PATCH-14, the baseline-preservation claim holds on paper. It remains unproved in practice pending open item 10.

### PATCH-16 — §6, state the capability sealing rule

The rule is tested in §22 ("cross-cell capsules") but stated nowhere in the architecture. A test without a contract is not a design.

> Every capability is sealed to `(issuer epoch, subject cell key, purpose, effect ID, expiry, hash of parent capability)`. Presentation by any subject other than the sealed one is **`DENY`, not `CHALLENGE`** — a challenge would disclose that the capability exists and what it lacks, turning the gate into an enumeration oracle. This is the deterministic form of Invariant 4.

### PATCH-17 — §6, graded degradation contract for the core itself

> When the policy/epoch/gate service is degraded, behaviour partitions by effect class (PATCH-11):
> - **observation and read paths** continue;
> - **`REVERSIBLE`** effects continue under cached policy, but only within `revocation_propagation_bound` (PATCH-03), then stop;
> - **`COMPENSABLE`** and **`IRREVERSIBLE`** effects fail closed immediately.
>
> **Acceptance:** kill the policy/epoch service; assert exactly this partition; measure time-to-stop for `REVERSIBLE` against the declared bound.

**Why this is material:** the packet requires availability regression checks on every repair and never applies one to its own core. Undefined, the options are fail-closed (checkout and customer communications dead across 50–60 commercial sites when one control service degrades) or fail-open (the security model evaporates precisely when it is most needed). The graded contract makes the trade explicit, bounded and testable, and keeps revenue-bearing reversible operations alive without letting a single irreversible action escape the gate.

---

## 6. Regression effects — consolidated

| Patch | Security | Privacy | Modularity | Evidence | Accessibility | Portability | Availability | Cost | Operability |
|---|---|---|---|---|---|---|---|---|---|
| 02 | = | **+** (claim matches proof) | = | **+** | = | **+** | **−** if B2 | **−** if B2 | = |
| 03 | **+** | = | **+** | **+** | = | = | **−** small (fail-closed window) | = | = |
| 04 | **+** | = | = | **+** | = | = | **+** (blocks induced DoS) | = | **−** small (review queue) |
| 05 | = | **+** | **+** (reuse) | **+** | = | = | = | = | = |
| 06 | = | **+** | = | **+** | = | = | = | = | = |
| 07 | **−** small (sensitivity traded) | = | = | **+** | = | = | **+** | = | **++** |
| 08 | = | = | = | **+** | **+** (band always present) | = | = | = | **+** |
| 09 | **+** | **+** | **+** | = | = | = | = | = | **−** small |
| 10 | **+** | = | = | **+** | = | = | **+** | **−** small | = |
| 11 | **+** | = | **+** | **+** | = | = | = | **+** (blocks duplicate charges/sends) | **+** |
| 12 | **+** | = | = | **++** | = | **+** | = | **−** small | **+** |
| 13 | **++** | = | = | **+** | = | **+** (cross-language) | = | = | = |
| 14 | **+** | = | = | **++** | = | = | = | **−** small | = |
| 16 | **++** | **+** (no oracle) | = | = | = | = | = | = | = |
| 17 | **+** | = | **+** | **+** | = | = | **++** | **+** | **+** |

No patch weakens a Locked Invariant. PATCH-09 resolves a contradiction by narrowing a stated *objective*, not an invariant — which is the correct direction of yield, and I flag it explicitly for owner confirmation rather than treating it as settled.

---

## 7. Audit method — the protocol governing §8

Stated before the tests, because a test result is uninterpretable without it. This section is the auditor's responsibility to define, not the owner's to supply.

### 7.1 Pre-test state declaration (blocking)

Nothing is tested until its current state is recorded, in one vocabulary, with no step collapsed:

`NOT INSPECTED → INSPECTED → DESIGNED → BUILT → CONFIGURED → CONNECTED → TESTED → PASSED → PROVEN → DEPLOYED → LIVE`
Side states: `DEGRADED · UNCONFIGURED · BLOCKED · FAILED`

- A component may not skip a state. "It built without errors" is `BUILT` — not `CONNECTED`, not `TESTED`.
- A run against an `UNCONFIGURED` component is **void, not failed**. Record it as void and fix the configuration. The distinction is load-bearing: a void run tells you nothing about the design; a failed run tells you something real.
- Every component in scope carries its state **in writing before the first test executes**. The state register is the audit's opening artefact, not a by-product.

### 7.2 What is frozen before the first test

Freeze and hash: the release artefact, gate/policy versions, every `ExternalStandardPin` (PATCH-12), the capsule corpus, the environment profile, and provider configuration. **If any frozen item changes mid-run, the run is void and restarts.** A test whose inputs moved proves nothing about the system.

### 7.3 Ground truth held separately from the runner

The scorer's expected results — which capsules must `DENY`, which must `ADVANCE` — are sealed before the run and held by someone other than whoever executes it. If one party writes the system, writes the tests, and holds the answers, the run measures self-consistency, not correctness.

### 7.4 Independence — what counts, by consequence

Two models agreeing is **not** independence. Independence requires at least one of: a different failure path, hidden test data, a deterministic check that cannot be argued with, an external instrument, a competent specialist, or an independent assessor.

| Proof | Independence required | Rationale |
|---|---|---|
| Proof 0 — core authority | Deterministic checks + sealed ground truth. No outside assessor. | The checks are unarguable; a DENY either happened or didn't. |
| Proof 2 — credential bytes | A second, **independently authored** implementation. | Cross-language vectors mean nothing if both implementations share an author or a misreading of the spec. |
| Proof 3 — `B` vs `B+G` | An assessor who did not build the system. **Non-negotiable.** | A self-assessed assurance comparison is not evidence, regardless of rigour. |

### 7.5 Evidence retained per run — pass or fail

Run ID; UTC timestamps; the frozen hashes from 7.2; the pre-test state register; the full input corpus; complete output including **every `DENY` reason**; **measured values, not verdicts** (the actual revocation-latency distribution, not "within bound"); operator actions; and every deviation from the written procedure.

Retention is itself tested: an independent competent engineer must reproduce the claim from the retained evidence **without asking anyone a question**. If they cannot, the claim is asserted, not proven.

### 7.6 Claim discipline — what a result licenses

| Result | You may say | You may **not** say |
|---|---|---|
| Void (unconfigured input) | "not yet tested" | anything at all about the design |
| Passed | "passed T-nn on \<date\> at \<version\>" | "works", "secure", "proven" |
| Passed, repeated, independently checked | "proven for the tested conditions" | "proven", unqualified |
| Failed | "failed T-nn — here is the output" | "probably a flake", absent a second run |

A green result licenses a statement about **the exact declared transition, at that version, on that date**. Nothing broader. This is the same rule Graphene applies to its own receipts, turned on the audit that judges it.

### 7.7 Stop-the-line conditions

Halt all dependent testing immediately on: a capsule obtaining authority it was not granted; any cross-cell reach; a policy rollback accepted; an exposed credential; a frozen artefact changing mid-run; ground truth reaching the test runner; or a strict-profile component found holding Tier A state on an ineligible service (PATCH-02).

Fix the foundation before continuing. Do **not** run the remaining tests "to gather more data" — once the base is known broken, the remaining results are not interpretable.

---

## 8. Acceptance-test matrix

Executable, deterministic, each capable of returning red.

| ID | Test | Pass condition | Blocks |
|---|---|---|---|
| T-01 | Capsule corpus: valid, malformed, stale, replayed, cross-cell, confused-deputy, policy-rollback — **AI fully disabled** | Only valid ADVANCEs; cross-cell and confused-deputy DENY (not CHALLENGE) | Core |
| T-02 | Revoke at T, use at T+ε across the bound | All uses after `T + revocation_propagation_bound` DENY; distribution reported | Core |
| T-03 | Kill policy/epoch service | Reads continue; REVERSIBLE continues then stops at bound; COMPENSABLE/IRREVERSIBLE fail closed immediately | Core |
| T-04 | Adversary induces quarantine of a **legitimate** cell | Availability impact and recovery latency within declared bound | Core |
| T-05 | Crash/resume mid-dispatch of an IRREVERSIBLE effect | No re-initiation | Core |
| T-06 | Known-null data across N risk profiles | Alarm count ≤ `estate_alarm_budget` | Risk |
| T-07 | Non-canonical JCS payload with valid signature over canonical form | Verifier rejects before accepting signature | Credential |
| T-08 | Cross-language golden vectors, positive **and** negative | Byte-identical across ≥2 independent implementations | Credential |
| T-09 | Release signing with an `ExternalStandardPin` past review date | Signing fails | Release |
| T-10 | Full acceptance matrix under strict profile | No strict-only path unexercised | Release |
| T-11 | Manifest asserting `IRAP Protected` = Australian residency | Release validation rejects | Strict |
| T-12 | Deception-cell activation without `deception_authority` | Activation refused | Deception |
| T-13 | `B` vs `B+G`, frozen versions, hidden ground truth, independent assessor — including **operator vigilance** injection | No baseline regression; named metrics improve; human detection not lowered | Assurance |
| T-14 | Cross-domain aggregation of the risk projection via API | Type-level rejection | Risk |

---

## 9. Closed on paper vs. still open in implementation

**Closed on paper (given the patches):** internal coherence of the capability/evidence/gate model; AI/authority boundary including the previously ambiguous restriction direction; blockchain boundary (optional, non-canonical, no PII, status off-chain — this was already clean); the risk-curve model's separation of measurement, drift, forecast, cause and intervention (already strong; only multiplicity was missing); baseline-preservation logic; Mission Control vs. strict separation; provider-metadata residency **as a narrowed and disclosed claim**.

**Open — blocked only by deployment evidence or independent assessment:** every performance, cost, latency, scale and recovery number; the `B` vs `B+G` comparison; prospective calibration of any real scanner domain; adapter compatibility with the existing estate; the two-cell proof under attack; IRAP/ISM applicability (§17 references remain **unverified this run** [S-15] and must not be cited as evidenced); byte-level envelope and credential vectors.

**Open — requires an owner or third-party fact, not engineering:** the B1/B2/B3 residency decision; Cloudflare entitlement confirmations for KV/D1 jurisdictions [S-6][S-7]; named competent persons for any regulated risk profile and for acquisition legal bases; lawful basis for deception-cell collection.

---

## 10. Residual risks and hard limits

All 23 hard limits in §20 survive review. I found no rhetorical repair attempt among them, and I am not able to demonstrate that any is removable. Two clarifications:

- Hard Limit 19 (exactly-once) is now *split* by PATCH-11 into a preventable part (duplicate initiation) and an irreducible part (duplicate delivery). The limit is unchanged; its boundary is now precise.
- Hard Limit 14 (maintenance) is now *instrumented* by PATCH-12 rather than merely acknowledged. Still a hard limit.

**Residual risks I could not close:**

- **R-1** — Companion files unavailable. Some holes above may already be closed. Provisional. `⬛`-adjacent only in the sense that I cannot resolve it from here.
- **R-2** — Tier B metadata residency has no engineering solution on the current provider set. It is a cost/legal decision. `🟥`
- **R-3** — The estate's operator is one person. Every patch that adds a review queue (PATCH-04) or a context switch (PATCH-09) spends the scarcest resource in the system. If the alarm budget (PATCH-07) is set generously, the whole risk layer degrades to decoration. This is the most likely real-world failure mode of Graphene and it is **not** a security failure. `🟥`
- **R-4** — §17 baseline claims rest on ISM/PSPF references unverified this run. `🟥`

---

## 11. Exact facts still needed

**Engineering calls — mine to make, not the owner's to supply.** These are recommendations with reasoning, not open questions. Override on evidence, not on preference:

- **`max_capability_ttl` — 300 seconds** for consequential capabilities, 24 hours for read/observe. Short enough that if the epoch channel fails entirely, expiry alone still bounds exposure; long enough not to thrash the gate on ordinary traffic.
- **`revocation_propagation_bound` — 60 seconds**, published and measured. If measurement shows it cannot be met, the published number moves to the measured p99. The number follows the evidence, never the reverse.
- **`estate_alarm_budget` — 10 alerts per operator per week**, estate-wide, as the starting target. One operator, 50–60 sites. Tune from measured data; never raise it to accommodate a noisy profile — fix the profile.

**Genuinely the owner's — commercial and strategic, not engineering:** the B1/B2/B3 residency decision (cost vs. legal exposure vs. losing Cloudflare's protection); whether PATCH-09's per-environment Mission Control is accepted, since it narrows an objective the owner set; the actual inventory behind open item 6.

**From providers:** Cloudflare account-team confirmation of KV jurisdiction entitlement [S-6]; written confirmation that no Australian CMB option exists or is roadmapped [S-4]; Stripe idempotency semantics per endpoint used.

**From specialists:** a named competent person per regulated risk profile; a legal assessment of deception-cell collection and of each acquisition basis; an independent assessor for T-13, who must not be the builder.

---

## 12. Direct answers

**Is the architecture internally coherent?** Yes, with one true contradiction (H-09, Mission Control vs. Invariant 16) and one boundary ambiguity (H-04, AI restriction direction). Both are repaired above. The remaining findings are missing contracts, not incoherence.

**Is it implementable with current technology?** Yes. Every mechanism named — capability sealing, DSSE/JCS envelopes, Merkle checkpoints, VC 2.0 with `ecdsa-jcs-2019`, bitstring status lists, sequential change detection, adapter isolation — is standard and current. The credential pins verified this run are all live specifications [S-8..S-11].

**Any fundamental blocker to the ordinary 50–60-site platform?** **No.** The ordinary profile has no residency constraint, and Cloudflare can route and serve it as claimed. The realistic risks are operational load (R-3) and adapter surprises in the existing estate, not architecture.

**Which claims are blocked only by deployment evidence or independent assessment?** All performance, cost, scale, latency and recovery figures; the `B` vs `B+G` result; prospective scanner calibration; adapter compatibility; the attacked two-cell proof; every §17 assurance claim.

**Does the Graphene layer preserve rather than weaken a highest-assurance baseline?** On paper, **only with PATCH-14**. As written, §17 forbids subtraction of controls but permits weakening by added path and by automation complacency. With PATCH-14 the claim is sound on paper and unproved in practice.

**Can policy-bounded acquisition protect both endpoints within a declared contract?** It protects the acquiring endpoint well. It protects the far endpoint by **unilateral undertaking only** — the source never agrees. PATCH-06 narrows the claim and keeps the mechanism.

**Does the risk-curve model distinguish measurement, drift, forecast, cause and intervention correctly?** **Yes** — this is the strongest section in the packet. It correctly separates observe/control modes, refuses automatic first-change-point causation, preserves the pre-intervention branch, and constrains prediction to validated precursors. Its one real gap is multiplicity across the estate (PATCH-07), which is a composition error rather than a modelling error.

**Are AI, evidence, authority and optional blockchain boundaries clean?** Blockchain: **yes, clean** — optional, non-canonical, no PII, status off-chain, reorg-safe. Evidence and authority: **yes**, once capability sealing is stated in the architecture rather than only in the test list (PATCH-16). AI: **not quite** — clean in the grant direction, ambiguous in the deny direction, and silent on adversarial induction. PATCH-04 closes both.

**What is the smallest first build that can genuinely disprove the core?** See §13 — the packet's §22 core proof is roughly three times larger than the falsification requires.

---

## 13. Recommendation

> ### ⚠️ CORRECTION — 14 Aug, after inspecting the estate
>
> **The recommendation below to "build Proof 0" is wrong as written, and it was wrong for the reason this review kept warning about: I did not look before concluding.** This review was conducted inside `Fast-Clocks/Fast-Clocks`, a README-only profile stub, and I declared the architecture absent without calling `list_repos`. The account holds **27 repos.**
>
> **Most of Graphene's deterministic core already exists** in `Fast-Clocks/apn-provenance-keeper` (pushed 14 Aug, commit `abb2b41`): 20 tables with RLS on all 20 and 42 policies; 12 edge functions including `admit-event`, `transition-event`, `verify-chain`, `sign-manifest`, `issue-document-certificate`, `mirror-check`, `public-ledger`, `head`; and `src/lib/merkle.ts` implementing **RFC 6962** correctly (odd nodes carried up, never duplicated), with a legacy variant retained and explicitly labelled CVE-2012-2459-vulnerable for pre-v0.2 certificates only.
>
> Mapping to this document: `event_transitions`/`transition-event` = the gate. `evidence`/`verification_records` = receipts. `epochs` = the revocation-epoch mechanism PATCH-03 proposes as new. `checkpoints` + `mirror_peers` + `head` + RFC 6962 = a Certificate-Transparency-grade verifiable log with independent mirrors, which is §16's witness/monitor requirement. `organisations` + `user_roles` + RLS = cells. `org_entitlements`/`api_tokens` = capabilities. `provider_stubs` = adapters.
>
> **Revised recommendation: Proof 0 is not a build, it is an inspection and an attack.** Take what `apn-provenance-keeper` already has, establish its pre-test state per §7.1, and run T-01/T-02/T-03/T-16 against it. The question is not "can this be built" — it substantially is. The question is whether what exists holds under the capsule corpus. Build only the gap that inspection reveals.
>
> **Also unfinished and more important than any new build:** `apn-hub/EXECUTION_LEDGER.md` (10 July) is an existing cleanup register covering 15 repos, with 7 clone-repos already deleted and 6 compliance fixes landed with commit SHAs. It ends at "Next Phase: Deep review of each remaining repo" and has not moved in five weeks. 12 repos have appeared since and are unclassified in it. Extend that ledger; do not start another.
>
> Nothing in `apn-provenance-keeper` has been executed, attacked, or verified. Schema and source were read. **NO TEST = NO CLAIM.**

**Proceed to a first proof — but not the one in §22, and read the correction above first.**

The §22 "core proof" bundles eighteen elements including deception cells, export/restore, marketing-adjacent surface and false-positive recovery. That is a small product, not a falsification test, and it delays the moment Graphene can first return red by a large multiple.

The disprovable heart of Graphene is a single claim: **a capsule cannot obtain authority it was not granted, and revocation is bounded.** If that fails, nothing downstream matters. If it holds, everything else is engineering.

**Proof 0 — falsification core.** Two cells (one hostile), one owner authority, one session kernel, two deterministic gates, one disposable airlock, the T-01 capsule corpus, T-02 revocation bound, T-03 degradation partition, the PATCH-16 sealing rule (exercised by T-01), signed receipt chain, hidden-ground-truth scorer. **All AI disabled.** No deception cell, no export/restore, no adapters, no Mission Control.

**Proof 1** — deception cell, false-positive recovery (T-04), export and clean restore, causal trace and repair runbook.
**Proof 2** — credential bytes, vectors, status, witness, optional chain behaviour (T-07, T-08).
**Proof 3** — `B` vs `B+G` with an independent assessor (T-13).

Do not attach the Pursuit Controller until Proof 0 is green, per the packet's own sequencing — which is correct.

**One caution before building.** The single most likely failure of this system is not a security failure. It is R-3: one operator, 50–60 sites, and a risk layer that generates more alarms than any person can adjudicate. PATCH-07 is the cheapest patch here and the one I would implement first inside Proof 1. A Graphene that is cryptographically sound and operationally ignored has failed.

---

*Independent adversarial review. Findings are provisional where the companion files would have been authoritative (H-01). No claim in this document should be treated as evidence of an operational property; every acceptance test listed above is unexecuted.*
