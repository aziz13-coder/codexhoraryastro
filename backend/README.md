# Backend Overview

This backend uses a central taxonomy defined in `taxonomy.py` to manage
question categories and their defaults. Modules such as
`question_analyzer`, `category_router` and the horary engine import the
`Category` enum instead of hard coded strings. Legacy string values are
still accepted but will emit a warning.

## Aggregation modes

The engine ships with a new DSL-based aggregation system enabled by
default. To revert to the legacy aggregator without editing
configuration files, set the `HORARY_USE_DSL` environment variable to
`false`. The `evaluate_chart` function also accepts a `use_dsl` argument
which callers can populate from a query parameter or HTTP header to
switch modes dynamically.

### Role importance

The DSL aggregator supports configurable weighting for key roles via the
`aggregator.role_importance` section of `horary_constants.yaml`. These
factors scale the contribution of testimonies involving a role. Default
weights:

```yaml
aggregator:
  role_importance:
    L1: 1.0   # Querent
    LQ: 1.0   # Quesited
    Moon: 0.7 # Moon baseline
    L10: 1.0  # Tenth house/examiner
    L3: 1.0   # Third house/messenger
```

Custom projects can adjust these values to tune the baseline importance
of each role.

### Translation and Collection tokens

Translations and collections of light now generate tokens that encode the
aspect type and whether reception is present. The dispatcher produces
names following the pattern `TRANSLATION_<ASPECT>_<WITH|WITHOUT>_RECEPTION`
and `COLLECTION_<ASPECT>_<WITH|WITHOUT>_RECEPTION`. All such testimonies
have a default absolute weight of `2.0`. Tokens with square or opposition
aspects without reception count as negative testimony; all others are
positive. Each dispatched entry also reports whether the aspect is
applying via an `applying` flag in the ledger.

## Reasoning output modes

The `/api/calculate-chart` endpoint can return reasoning details in two formats.
By default, responses include the legacy `rationale` array.
Setting the `useReasoningV1` flag—either as a `useReasoningV1=true` query
parameter or the `USE_REASONING_V1=true` environment variable—switches the
response to the new `reasoning_v1` field and omits `rationale`.
