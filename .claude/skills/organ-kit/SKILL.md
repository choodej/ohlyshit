---
name: organ-kit
description: Scaffold and grow an "organ-based" backend — independent, testable modules ("organs") in clean OOP/Hexagonal style, connected only through adapters. Use when the user wants to add a new module/service/"department"/"organ", set up this architecture in any project, or asks for a safe scaffold with ask-before-create guards, local JSONL logging, and an auto-generated dependency catalog. Language-agnostic in spirit; ships a Python generator.
---

# organ-kit

A small, neutral kit for building systems out of **organs**: each organ is an
independent unit you can build, test, and repair on its own, then connect to the
rest through adapters. Designed so a big system stays controllable instead of
turning into one tangled blob.

ใช้ภาษาไทยกับผู้ใช้ได้ แต่ไฟล์ที่ generate เป็นกลาง ใช้ได้ทุกโปรเจค

## When to use
- User asks to add a new organ / module / "department" / service.
- User wants to set up the organ architecture in a fresh or existing project.
- User wants a scaffold that already runs and passes a smoke test.

## Core rules (read `reference/RULES.md` for the why)
1. **Separate `sandbox/` from `project/`.** Prove an organ in sandbox first;
   promote to project only when complete.
2. **Every organ is OOP + Hexagonal:** pure `domain/` talks to the world only
   through `ports/` (interfaces); real I/O lives in `adapters/`. Swap or fix one
   adapter without touching domain.
3. **Organs connect only via contracts/adapters** — never reach inside each other.
4. **Safe but not slow:** reversible work proceeds; risky work (overwrite,
   duplicate id, duplicate name, cross-organ impact) must return *choices* for a
   human to decide — never create-over silently. Always mark a recommended choice.
5. **Real logs are local JSONL** (fast, queryable). External tools (ClickUp,
   Sheets) receive only *summaries* through a separate adapter — never raw logs.
6. **The catalog/graph is auto-generated from code only** (`tools/graphify.py`),
   which also detects "shadows" (circular deps, data-domain overlaps, dangling
   deps, unguarded external writes). Never hand-write it, so it can never drift.
7. **Every external write goes through a `SafetyGate`** (`shared/safety.py`):
   dry-run preview + explicit approval; reversible work auto-approves.
8. **Skeleton-first inside an organ** (bone before tissue): skeleton → ports →
   a failing test → domain logic → adapters → UI → optimization. Work that jumps
   ahead is *deferred* (log it in `DEFERRED.md` — never hide it), not invalid;
   learning spikes are fine. System-wide, still build a vertical slice first.
   See `reference/RULES.md` §8.
9. **Two-tier "done"** (`reference/RULES.md` §9): *learning done* = you can state
   what you learned + logged every shortcut in `DEFERRED.md`. *implementation
   done* = tests pass + no unguarded external writes (`graphify --strict` clean) +
   clean boundary. Only *implementation done* may be promoted to `project/`.
   Never claim implementation-done for a prototype.

## Built-in framework features
- **Hexagonal OOP** scaffolding for every organ.
- **Graphify** auto-mapping + shadow detection (`tools/graphify.py`, Mermaid output).
- **Token optimization** for agent context/state (`tools/token_compressor.py`) —
  never applied to the canonical audit log.
- **Safety gates** for human-in-the-loop external writes (`shared/safety.py`).

## How to create a new organ

Prefer the deterministic generator (works with or without me):

```bash
python .claude/skills/organ-kit/scripts/new_organ.py <organ_name> \
    --title "Human title" --dir sandbox/organs
```

It will:
- refuse if the organ already exists (rule 4 — ask before create),
- ensure `shared/` and `tools/` exist (created once, never overwritten),
- stamp out a self-contained organ: `domain/ ports/ adapters/ tests/ app.py manifest.json`,
- leave you an organ that **already runs and passes its smoke test**.

Then:
```bash
cd sandbox
python -m pytest organs/<organ_name>/tests -q     # should pass immediately
python organs/<organ_name>/app.py --demo          # see the slice run
python tools/graphify.py                           # refresh CATALOG.md / graph.json / graph.mmd
```

## What I (Claude) should do when asked to add an organ
1. Confirm the organ name + one-line purpose (ask if unclear — one question at a time).
2. Run the generator. Do **not** hand-write the scaffold.
3. Fill in the real domain logic inside `domain/service.py` only; keep ports/adapters thin.
4. Run the tests, then regenerate the catalog.
5. Report results plainly (tests passing/failing as they are).

## Distributing this skill
Copy `.claude/skills/organ-kit/` into any repo's `.claude/skills/`. It is
project-agnostic: no hard-coded tokens, names, or paths. Telegram/ClickUp
adapters are optional plug-ins, not requirements.
