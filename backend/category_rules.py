from __future__ import annotations

"""Category-specific ruleset definitions for scoring.

Each taxonomy.Category can define:

- primary_significators: list of house lords always considered primary
- allowed_turned_houses: mapping of base significator to list of turned houses
- outcome_houses: radical houses whose rulers may affect the outcome
- scored_factors: list of factor names enabled for this category

The structure is intentionally data driven so additional categories can be
extended without modifying engine logic.
"""

from typing import Any, Dict

try:  # Allow usage as package or standalone module
    from .taxonomy import Category
except ImportError:  # pragma: no cover
    from taxonomy import Category

# Default rule template used when a category has no specific definition.
DEFAULT_RULE: Dict[str, Any] = {
    "primary_significators": [],
    "allowed_turned_houses": {},
    "outcome_houses": [4],
    # By default consider general debilitation and cadent placement factors
    "scored_factors": ["debilitation", "cadent_significator"],
}

# Ruleset mapping categories to their specific configuration.
CATEGORY_RULES: Dict[Category, Dict[str, Any]] = {
    cat: {k: (v.copy() if isinstance(v, dict) else list(v) if isinstance(v, list) else v)
          for k, v in DEFAULT_RULE.items()}
    for cat in Category
}

# Template for relationship / partner's maturity/healing questions.
CATEGORY_RULES[Category.RELATIONSHIP] = {
    "primary_significators": ["L1", "L7", "L4"],
    # Partner's health/maturity uses turned 6th and 9th from the 7th
    # which correspond to radical 12th and 3rd houses respectively.
    "allowed_turned_houses": {"L7": [6, 9]},
    "outcome_houses": [4, 12, 3],
    # Default scored factors; L2/L11 are excluded unless added here explicitly.
    "scored_factors": ["debilitation", "cadent_significator"],
}

def get_category_rules(category: Category | None) -> Dict[str, Any]:
    """Return rules for a given category, falling back to defaults."""
    if category is None:
        return DEFAULT_RULE.copy()
    return CATEGORY_RULES.get(category, DEFAULT_RULE).copy()
