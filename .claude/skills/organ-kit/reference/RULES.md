# organ-kit — rules & rationale

Neutralized from a real build. Each rule fixes a concrete failure mode and is
written so it stays cheap (no bloat, no slowdown).

## 1. sandbox / project separation
**Why:** designing big and stuffing everything into one place becomes
uncontrollable. Prove organs in `sandbox/`; only finished, ready organs move to
`project/`. The two never mix.

## 2. OOP + Hexagonal, but only at the boundary
**Why:** forcing OOP and an adapter onto *every* line is itself bloat. The win
comes from one rule: **domain talks to the outside only through `ports/`
(interfaces); real I/O lives in `adapters/`.** Inside domain, write plain code.
- Downside if over-applied: indirection everywhere, slower to read. So bound it.

## 3. Organs connect only through contracts
**Why:** when something breaks you repair one organ without a chain reaction.
No organ imports another organ's internals — only its published interface/adapter.

## 4. Safe but not slow — tiered "ask before create"
Don't ask on every action (that contradicts "be on time"). Tier it:
- **Auto-proceed:** reversible, new, non-conflicting work.
- **Ask first (return choices + a recommendation):** overwrite/delete, duplicate
  id, duplicate name, anything touching multiple organs.

The code expresses this with a `Result` that can be `OK`, `NEEDS_DECISION`
(carries choices), or `REJECTED`. Risky paths return `NEEDS_DECISION` instead of
acting.

## 5. Logs local, summaries external
**Why:** ClickUp/Sheets are not log stores — slow, rate-limited, not queryable.
Raw logs go to local JSONL (fast). A separate decorator adapter forwards only
*reportable* events (e.g. "created") to ClickUp. Swap it in without touching domain.
- Downside avoided: one slow external call per log line dragging the whole system.

## 6. Auto-generated catalog (graphify)
**Why a graph helps:** in a multi-organ/multi-repo system you need a dependency
map + index to find things fast and avoid duplicate work.
**Its real downsides:** hand-maintained graphs go stale and become a second thing
to maintain. **Fix:** generate it from `manifest.json` files only, in one command
(or CI). The code is the single source of truth; the graph can never drift.
`tools/graphify.py` also flags **shadows**: circular dependencies, two organs
owning the same data domain, dependencies on missing organs, and external writes
without a declared safety gate. Run with `--strict` to fail CI on any shadow.

## 7. Safety gates for external writes
**Why:** an agent should never silently hit a real database/API. Every external
write is described as a `WriteIntent` and routed through a `SafetyGate`
(`shared/safety.py`). `PolicyGate` auto-approves reversible work and requires
explicit approval for irreversible work; `DryRunGate` previews and never writes.
Blocked writes return `Result.NEEDS_DECISION`, reusing the same ask-before-create
contract — no parallel concept.
- Bounded, not bloated: enforced by a small `ExternalWriteAdapter` base class +
  convention, not a heavy framework.

## 8. Skeleton-first build order (bone before tissue)
**Why:** the classic failure is building "tissue" (real adapters, UI, deep
workflow logic) before the "bone" (contracts and a proof) exists — so the proof
never comes and the design ossifies around accidental choices.

**Scope: this order applies _within one organ_, not as a global gate across the
whole system.** At the system level you still build a thin **vertical slice**
first (rule below) — one path cut through every layer — then widen. The two are
not in conflict: the slice decides _which_ organ to build next; this rule
decides the _order inside_ that organ.

Default order inside an organ:
1. skeleton — minimal class/object shells, manifest, audit/event schema
2. contracts — the `ports/` (ABC interfaces) the domain needs
3. harness proof — a test that **fails first**, pinning the intended behavior
4. domain logic — make the failing test pass (pure, no I/O)
5. adapters — real I/O behind the ports (DB, API, Telegram, ...)
6. UI / workflow detail
7. optimization (incl. token compression, caching)

**A good worked example** to copy the shape of: `ProductCatalog` (owns products)
→ `Inventory.preview_adjust` (projects the result of a stock change *without
writing*; asks before going negative) → a **replay harness** that rebuilds
inventory state from the event log alone. It exercises everything at once: a
cross-organ dependency through a contract (not internals), preview-before-write,
ask-before-create, and "the log is the source of truth, state is a projection".

**Rule, not a straitjacket:** a task that lands in a later step before an
earlier one is finished is **deferred by default** — mark it deferred, note why,
and return to the missing bone first. It is *not* "invalid". Throwaway spikes to
_learn_ a contract are allowed and encouraged; just discard them once the
contract is understood, then build it properly in order. Deep adapter logic
before its port + a failing test exist is the one hard "no".

("Models" is intentionally not a numbered step: domain models are bone and live
in step 1/4; serving an ML model is tissue and lives in step 5+.)

**Track every deferral.** Deferring is allowed; hiding is not. Each out-of-order
or spike item gets one honest block in a `DEFERRED.md` (template ships in the
kit): `why_deferred`, `risk`, `must_close_before_promotion`, `owner_decision_needed`,
`status`. An organ cannot be promoted `sandbox/ -> project/` while any
`must_close_before_promotion: true` item is still open.

## 9. Definition of Done — two tiers
A newcomer's most common mistake is calling a *prototype* "done". Separate the
two so nobody over-claims:

**Learning / prototype done** (a spike is finished when):
- you can state **what you learned** (the contract/shape it revealed), and
- every shortcut is **logged in `DEFERRED.md`** with its risk.
- Throwaway code is fine here — it does NOT count as implementation.

**Implementation done** (a real layer is finished when):
- its **harness/tests pass** (the failing test from step 3 now passes),
- **no unguarded external writes** — every external write goes through a
  `SafetyGate`, and `python tools/graphify.py --strict` reports no shadows,
- the **boundary is clean**: domain imports no I/O; ports/adapters are thin; the
  organ depends on others only through declared contracts,
- the manifest is accurate (ports, depends_on, owns_data, external_writes).

Only *implementation done* work is eligible for promotion to `project/`.

## What this kit deliberately does NOT do
- No mandatory message broker, no mandatory DB, no mandatory cloud. Start with
  files; add infrastructure only when an organ proves it needs it.
- No global "brain" until enough organs are individually proven. Build a thin
  end-to-end slice first, then widen.
