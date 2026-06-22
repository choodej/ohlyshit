# Deferred work log

Anything built out of skeleton order (RULES.md §8), and any spike/prototype kept
around, gets an entry here. The rule allows deferring — it does **not** allow
hiding. No silent shortcuts: a deferred item is tracked, not forgotten.

**Promotion gate:** an organ cannot move `sandbox/ -> project/` while it has an
open item with `must_close_before_promotion: true`.

Copy the block below per deferred item. Keep it short and honest.

```yaml
DEFERRED_LAYER: <which layer/step was skipped, e.g. "adapters: real ClickUp POST">
why_deferred: <why it is not done in order yet — be specific>
risk: <what could bite us if it stays open>
must_close_before_promotion: true | false
owner_decision_needed: <what a human must decide, or "none">
status: open | closed
```

## Example (delete me)

```yaml
DEFERRED_LAYER: adapters: real ClickUp HTTP POST
why_deferred: contract + dry-run proven; real endpoint needs an org API token
risk: low — guarded by DryRunGate, nothing is written until a real gate is set
must_close_before_promotion: false
owner_decision_needed: which ClickUp list id + token to use in prod
status: open
```
