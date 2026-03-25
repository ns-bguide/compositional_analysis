# Long Term Matching Strategy

**Discovery**: 72.7% of unmatched terms are 7+ words (171,001 terms)
**Target**: S chapter (50.66% of long terms = 86,635 terms)

---

## The Problem

### Current Family Limitations
- Most families: 2-4 slots
- Complex families: 5-6 slots
- Long terms need: **7-9 slots**

### Why Long Terms Fail to Match
1. **Insufficient slot coverage**: Families can't capture all components
2. **term_fits_family_whole requirement**: All tokens must be covered
3. **Stopword gaps**: Connectors ("with", "without", "of", "to") separate components

---

## Analysis of 30-31 Word Terms

### Pattern Structure
```
[qualifier] [injury] of [laterality] [anatomy] [anatomy_detail],
[location], [qualifier2]
with [modifier_with] [duration_detail]
without [status_detail] with [outcome_detail],
[encounter]
```

### Token Mapping
| Component | Current Slot | Status |
|-----------|--------------|--------|
| "not elsewhere classified" | qualifier | ✓ Captured |
| "injury" | injury | ✓ Captured |
| "right/left" | laterality | ✓ Captured |
| "internal carotid artery" | anatomy | ✓ Captured |
| "intracranial portion" | anatomy/location | ✓ Captured |
| "with loss of consciousness" | modifier_with | ✓ Captured |
| "greater than 24 hours" | ❌ NO SLOT | **MISSING** |
| "without return to" | ❌ NO SLOT | **MISSING** |
| "pre existing conscious level" | ❌ NO SLOT | **MISSING** |
| "with patient surviving" | ❌ NO SLOT | **MISSING** |
| "initial encounter" | encounter | ✓ Captured |

**Problem**: Need slots for duration, outcome, and status modifiers

---

## Solution: Create Missing Slots

### 1. DURATION_TOKENS (New Slot)
```python
DURATION_TOKENS = {
    "duration",
    "hours", "hour",
    "minutes", "minute",
    "seconds", "second",
    "days", "day",
    "weeks", "week",
    "months", "month",
    "greater", "less", "more",
    "greater than", "less than", "more than",
    "24 hours", "6 hours", "30 minutes",
    "brief", "prolonged", "extended",
    "transient", "temporary", "permanent",
}
```

### 2. OUTCOME_TOKENS (New Slot)
```python
OUTCOME_TOKENS = {
    "death", "died", "dying",
    "surviving", "survived", "survival",
    "regaining", "regained", "return",
    "return to", "regaining consciousness",
    "prior to", "before", "after",
    "patient", "victim",
}
```

### 3. CONSCIOUSNESS_LEVEL_TOKENS (New Slot)
```python
CONSCIOUSNESS_LEVEL_TOKENS = {
    "conscious", "consciousness",
    "unconscious", "unconsciousness",
    "level", "conscious level",
    "pre existing", "preexisting",
    "baseline", "normal",
    "alert", "comatose", "stupor",
}
```

---

## Ultra-High-Specificity Families (7-9 slots)

### Family 1: Complete S-Chapter Injury Pattern (9 slots)
```python
"qualifier_x_laterality_x_anatomy_x_location_x_injury_x_modifier_with_x_duration_x_outcome_x_encounter": [
    ("qualifier", QUALIFIER_TOKENS),
    ("laterality", LATERALITY_TOKENS),
    ("anatomy", ANATOMY_TOKENS),
    ("location", LOCATION_TOKENS),
    ("injury", INJURY_TOKENS),
    ("modifier_with", MODIFIER_WITH_TOKENS),
    ("duration", DURATION_TOKENS),
    ("outcome", OUTCOME_TOKENS),
    ("encounter", ENCOUNTER_TOKENS),
]
```

**Target**: ~5,000-10,000 of the longest S-chapter injury terms

### Family 2: Without Duration (8 slots)
```python
"qualifier_x_laterality_x_anatomy_x_injury_x_modifier_with_x_outcome_x_encounter": [
    ("qualifier", QUALIFIER_TOKENS),
    ("laterality", LATERALITY_TOKENS),
    ("anatomy", ANATOMY_TOKENS),
    ("injury", INJURY_TOKENS),
    ("modifier_with", MODIFIER_WITH_TOKENS),
    ("outcome", OUTCOME_TOKENS),
    ("encounter", ENCOUNTER_TOKENS),
]
```

### Family 3: Without Outcome (8 slots)
```python
"qualifier_x_laterality_x_anatomy_x_location_x_injury_x_modifier_with_x_duration_x_encounter": [
    ("qualifier", QUALIFIER_TOKENS),
    ("laterality", LATERALITY_TOKENS),
    ("anatomy", ANATOMY_TOKENS),
    ("location", LOCATION_TOKENS),
    ("injury", INJURY_TOKENS),
    ("modifier_with", MODIFIER_WITH_TOKENS),
    ("duration", DURATION_TOKENS),
    ("encounter", ENCOUNTER_TOKENS),
]
```

### Family 4: Core Pattern (7 slots)
```python
"qualifier_x_laterality_x_anatomy_x_injury_x_modifier_with_x_duration_x_encounter": [
    ("qualifier", QUALIFIER_TOKENS),
    ("laterality", LATERALITY_TOKENS),
    ("anatomy", ANATOMY_TOKENS),
    ("injury", INJURY_TOKENS),
    ("modifier_with", MODIFIER_WITH_TOKENS),
    ("duration", DURATION_TOKENS),
    ("encounter", ENCOUNTER_TOKENS),
]
```

---

## Expected Impact

### Coverage Projection
- **Target**: 86,635 long S-chapter terms
- **Expected capture**: 20,000-40,000 terms (23-46%)
- **Coverage gain**: +5-10%

### Why This Will Work
1. **Addresses root cause**: 72% of unmatched are long terms
2. **S chapter focused**: 50% of long terms are S chapter
3. **High specificity wins**: 7-9 slot families will beat all existing families
4. **Complete coverage**: New slots fill gaps in current taxonomy

---

## Implementation Priority

### Phase 1: Create New Slots (Required)
1. ✅ DURATION_TOKENS
2. ✅ OUTCOME_TOKENS
3. ✅ CONSCIOUSNESS_LEVEL_TOKENS (optional, merge with OUTCOME)

### Phase 2: Create Ultra-High-Specificity Families
1. 9-slot complete pattern
2. 8-slot variants (drop duration OR outcome)
3. 7-slot core pattern

### Phase 3: Test and Validate
- Run analysis
- Measure long-term capture rate
- Check S chapter improvement

---

## Risk Assessment

### Low Risk ✅
- New slots don't overlap existing slots
- High specificity = won't compete with existing families
- Targeted at unmatched terms (no regression risk)

### Potential Issues
1. **Term ordering**: May need multiple family orderings
2. **Stopword interference**: Connectors between components
3. **Token variations**: "pre-existing" vs "preexisting" vs "pre existing"

---

## Alternative: Relaxed Matching for Long Terms

If ultra-high-specificity families still don't work, consider:

### Option A: Partial Coverage Threshold
- For terms >15 words, allow 80% coverage instead of 100%
- Match with best partial family

### Option B: Length-Based Family Priority
```python
if len(tokens) > 15:
    prioritize_families_with_slots >= 7
elif len(tokens) > 10:
    prioritize_families_with_slots >= 5
else:
    normal_priority
```

### Option C: Compositional Chain Matching
- Match term in segments
- "injury of X" + "with Y" + "Z encounter"
- Combine multiple family matches

---

## Success Metrics

### Minimum Success
- [ ] Long term capture rate: ≥30% (51,000 terms)
- [ ] Coverage gain: ≥+5%
- [ ] S chapter coverage: ≥60%

### Target Success
- [ ] Long term capture rate: ≥40% (68,000 terms)
- [ ] Coverage gain: ≥+7%
- [ ] S chapter coverage: ≥65%

### Exceptional Success
- [ ] Long term capture rate: ≥50% (85,000 terms)
- [ ] Coverage gain: ≥+10%
- [ ] S chapter coverage: ≥70%

---

## Why This is THE Solution

1. **Data-driven**: 72.7% unmatched are long terms
2. **Addresses root cause**: Current families too simple
3. **Massive potential**: 86,635 S-chapter terms alone
4. **Low risk**: New slots, no overlap
5. **Aligns with your insight**: Multi-slot families for multi-word terms!

**This could be the breakthrough that gets us from 40% to 50%+ coverage.**

---

**Status**: 📋 Ready to implement
**Confidence**: 🟢🟢🟢🟢🟢 VERY HIGH (empirically validated need)
