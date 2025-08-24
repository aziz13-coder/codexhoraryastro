# Confidence System Improvements

## Current Problem
The engine returns "No 0%" when it should return meaningful confidence percentages. The issue is that "fatal blockers" override token-based confidence calculations.

## Proposed Solutions

### 1. IMMEDIATE FIX: Differentiate "No" vs "Cannot Judge"

Instead of setting confidence to 0 for blocked perfection, use different response types:

**Current Logic (engine.py:1967-1968):**
```python
return {
    "result": "NO",
    "confidence": min(confidence, top_blocker.get("confidence", 85)),
    ...
}
```

**Improved Logic:**
```python
# If blocker has high confidence in denial, use that
blocker_confidence = top_blocker.get("confidence", 0)
if blocker_confidence >= 60:
    return {
        "result": "NO", 
        "confidence": blocker_confidence,
        "reason": f"Blocked by {top_blocker['type']}: {top_blocker['reason']}",
        ...
    }
else:
    return {
        "result": "CANNOT_JUDGE",
        "confidence": 0,
        "reason": "Insufficient reliable testimony due to blockers",
        ...
    }
```

### 2. ENHANCED FIX: Hybrid Confidence System

Combine token scores with blocker analysis for more nuanced confidence:

```python
def calculate_hybrid_confidence(self, token_score, blockers, base_confidence=100):
    """Calculate confidence considering both tokens and blockers"""
    
    # Start with token-based confidence
    if token_score == 0:
        confidence = 50  # Neutral
    elif token_score > 0:
        confidence = min(50 + (token_score * 10), 85)  # YES bias
    else:
        confidence = max(50 + (token_score * 10), 15)  # NO bias
    
    # Apply blocker penalties
    for blocker in blockers:
        severity = blocker.get("severity", "warning")
        if severity == "fatal":
            confidence = max(confidence * 0.2, 10)  # Severe reduction, not elimination
        elif severity == "severe":
            confidence = max(confidence * 0.6, 20)
        elif severity == "warning":
            confidence = max(confidence * 0.8, 30)
    
    return round(confidence)
```

### 3. SPECIFIC IMPROVEMENTS FOR LOTTERY CHART

For your chart with token_score = -3:
- **Base assessment**: Strong "No" (score -3 = ~20% confidence in No)
- **Fatal blocker present**: Reduces to ~4% confidence  
- **Result**: "NO, 4%" instead of "NO, 0%"

This would be more meaningful because:
- It acknowledges the strong negative tokens
- It shows the blocker impact
- It avoids the meaningless 0% that suggests "no information"

### 4. CONFIGURATION-BASED APPROACH

Add settings to control confidence behavior:

```yaml
confidence:
  min_confidence: 5          # Never go below 5%
  blocker_behavior: "reduce" # "reduce" vs "override"
  token_weight: 0.7         # How much tokens matter vs blockers
  show_reasoning: true      # Include detailed reasoning in response
```

### 5. IMPROVED RESPONSE STRUCTURE

Instead of just confidence percentage, provide breakdown:

```json
{
  "verdict": "NO",
  "confidence": 15,
  "confidence_breakdown": {
    "token_based": 20,
    "blocker_penalty": -5,
    "final": 15
  },
  "primary_reason": "Multiple house rulers severely debilitated",
  "blocking_factors": ["frustration", "moon_void_of_course"],
  "strength": "moderate"  // weak/moderate/strong
}
```

## Implementation Priority

1. **Quick Fix**: Modify blocker confidence handling (engine.py:1968)
2. **Medium Term**: Implement hybrid confidence system
3. **Long Term**: Add configuration options and enhanced response structure

## Code Changes Needed

### File: `horary_engine/engine.py`

**Line 1968 - Current:**
```python
"confidence": min(confidence, top_blocker.get("confidence", 85)),
```

**Line 1968 - Improved:**
```python
"confidence": self._calculate_blocker_adjusted_confidence(
    token_score, blocker_eval["blockers"], confidence
),
```

Add new method:
```python
def _calculate_blocker_adjusted_confidence(self, token_score, blockers, base_confidence):
    # Implementation of hybrid system above
    pass
```

This would make the confidence percentages much more meaningful and informative.