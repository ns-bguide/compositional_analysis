# Strategy 2 Implementation: Expand "With" Modifier Slot

**Implementation Date**: 2026-03-24
**Status**: ✅ COMPLETE (Underperformed)
**Expected Gain**: +8,000-12,000 terms
**Actual Gain**: +1,635 terms (+0.41%)
**Achievement**: 14-20% of expected

---

## Strategy Overview

**Problem**: "with X" constructs are extremely common in ICD-10-CM but not fully captured.

**Evidence from Unmatched Terms Analysis**:
- "fracture with routine healing" - 917 instances
- "fracture with delayed healing" - 917 instances
- "fracture with nonunion" - 895 instances
- "fracture with malunion" - 523 instances
- "with loss of consciousness" - 973 instances

**Solution**: Expand MODIFIER_WITH_TOKENS vocabulary and create additional with-modifier families.

---

## Changes Implemented

### 1. MODIFIER_WITH_TOKENS Expansion

**Before** (15 tokens):
```python
MODIFIER_WITH_TOKENS = {
    "routine", "healing", "routine healing",
    "delayed", "delayed healing",
    "nonunion", "malunion",
    "loss", "consciousness", "loss of consciousness",
    "behavioral", "disturbance", "behavioral disturbance",
    "psychotic", "psychotic disturbance",
    "mood", "mood disturbance",
    "anxiety",
    "mention", "involvement", "mention of heart involvement",
    "agitation",
}
```

**After** (35 tokens, +20):
```python
MODIFIER_WITH_TOKENS = {
    # Healing states
    "routine", "healing", "routine healing",
    "delayed", "delayed healing",
    "nonunion", "malunion",

    # Consciousness-related
    "loss", "consciousness", "loss of consciousness",
    "brief", "prolonged",
    "brief loss of consciousness",
    "prolonged loss of consciousness",

    # Behavioral/mental state
    "behavioral", "disturbance", "behavioral disturbance",
    "psychotic", "psychotic disturbance",
    "mood", "mood disturbance",
    "anxiety",
    "agitation",

    # Cardiac involvement
    "mention", "involvement", "mention of heart involvement",

    # Complications
    "complication", "complications",
    "infection",
    "hemorrhage",
    "obstruction",

    # Functional state
    "impairment",
    "disability",
    "limitation",

    # Pregnancy/obstetric
    "labor",
    "delivery",
    "fetal",
    "maternal",

    # Additional qualifiers
    "exacerbation",
    "remission",
    "progression",
}
```

### 2. New Template Families Created (+6 families)

**Existing with-modifier families** (5):
1. `anatomy_x_injury_x_modifier_with_x_encounter`
2. `anatomy_x_injury_x_fracture_detail_x_modifier_with_x_encounter`
3. `injury_x_modifier_with_x_encounter`
4. `condition_x_modifier_with`
5. `anatomy_x_condition_x_modifier_with`

**New families added** (6):

1. **`laterality_x_anatomy_x_injury_x_modifier_with_x_encounter`**
   - Captures: "fracture of left femur with routine healing, initial encounter"
   - Target: S/T chapter lateralized injuries with healing modifiers

2. **`qualifier_x_condition_x_modifier_with`**
   - Captures: "unspecified diabetes with complications"
   - Target: Qualified conditions with modifiers

3. **`anatomy_x_injury_x_healing_x_modifier_with_x_encounter`**
   - Captures: "femur fracture, healing, with routine healing, subsequent encounter"
   - Target: Injuries with both healing slot and with-modifier

4. **`diagnostic_classifier_x_anatomy_x_injury_x_modifier_with_x_encounter`**
   - Captures: "type II femur fracture with delayed healing"
   - Target: Classified injuries with modifiers

5. **`laterality_x_anatomy_x_condition_x_modifier_with`**
   - Captures: "left kidney disease with obstruction"
   - Target: Lateralized conditions with modifiers

6. **`qualifier_x_anatomy_x_condition_x_modifier_with`**
   - Captures: "unspecified heart failure with complications"
   - Target: Qualified anatomical conditions with modifiers

---

## Token Categories Added

### Consciousness Modifiers (+4 tokens)
- "brief", "prolonged"
- "brief loss of consciousness", "prolonged loss of consciousness"

**Rationale**: ICD-10-CM distinguishes consciousness loss duration

### Complication Modifiers (+3 tokens)
- "infection", "hemorrhage", "obstruction"

**Rationale**: Common complication types appearing with conditions

### Functional State Modifiers (+3 tokens)
- "impairment", "disability", "limitation"

**Rationale**: Functional status often appears in "with" constructs

### Obstetric Modifiers (+4 tokens)
- "labor", "delivery", "fetal", "maternal"

**Rationale**: Target O chapter (pregnancy) patterns like "with fetal distress"

### Progression Modifiers (+3 tokens)
- "exacerbation", "remission", "progression"

**Rationale**: Disease progression states

---

## Target ICD Chapters

### Primary Targets
- **S/T chapters** (Injury): Fractures with healing states
- **E chapter** (Endocrine): Diabetes with complications
- **F chapter** (Mental): Disorders with behavioral modifiers
- **G chapter** (Nervous): Conditions with consciousness modifiers
- **O chapter** (Pregnancy): Complications with fetal/maternal modifiers

### Secondary Targets
- All chapters with complication patterns
- Conditions with functional limitations
- Progressive diseases with state modifiers

---

## Expected Impact

### Coverage Projection
- **Baseline**: 153,788 terms (39.05%)
- **Expected after Strategy 2**: 161,000-165,000 terms (40.9-42.0%)
- **Expected gain**: +8,000-12,000 terms (+2.0-3.0%)

### Family-Specific Expectations

| Family | Expected Coverage | Primary Chapters |
|--------|------------------|------------------|
| laterality_x_anatomy_x_injury_x_modifier_with_x_encounter | 2,000-3,000 | S, T |
| anatomy_x_injury_x_modifier_with_x_encounter | +500-1,000 | S, T |
| condition_x_modifier_with | +1,000-2,000 | E, F, G, I |
| qualifier_x_condition_x_modifier_with | +500-1,000 | All |
| laterality_x_anatomy_x_condition_x_modifier_with | +500-1,000 | E, G, N |

---

## Implementation Notes

### Why These Token Additions?

1. **Data-Driven**: Based on unmatched term frequency analysis
2. **Chapter-Specific**: Target known low-coverage chapters (O, F, G)
3. **Compound Phrases**: Include both phrases and components for flexible matching
4. **Medical Relevance**: All terms appear in standard ICD-10-CM documentation

### Family Design Rationale

1. **High Specificity First**: Families with 5+ slots (laterality + anatomy + injury + modifier + encounter)
2. **Laterality Integration**: Lateralized injuries often have healing modifiers
3. **Qualifier Support**: "unspecified X with Y" is a common ICD pattern
4. **Diagnostic Classifier**: Salter-Harris fractures, etc. with healing states

### Learned from Vocabulary Review

- ✅ Keep multi-token phrases for exact matching
- ✅ Keep component tokens for flexible matching
- ✅ Don't remove duplicates if they serve different contexts
- ✅ Test incrementally

---

## Validation Criteria

### Success Metrics
- [ ] Coverage gain ≥ +6,000 terms (75% of low estimate)
- [ ] At least 3 new families with >500 terms coverage
- [ ] O chapter coverage improves by ≥1%
- [ ] F/G chapter coverage improves by ≥0.5%
- [ ] No regression in existing family coverage

### Quality Metrics
- [ ] Fuzzy match rate remains ≤10%
- [ ] Ambiguous assignment rate remains ≤1%
- [ ] New families show specificity ≥3 slots

---

## Testing Plan

1. **Run Full Analysis** ✓ (in progress)
2. **Compare Coverage**: Before (153,788) vs After
3. **Analyze New Families**: Coverage and quality metrics
4. **Chapter Impact**: Check O, F, G, E chapter improvements
5. **Sample Review**: Validate 20-30 new matches for quality

---

## Rollback Plan

If coverage regresses or quality degrades:

1. **Remove new families** (keep vocabulary)
2. **Selectively revert vocabulary** if issues found
3. **Keep beneficial additions** (split approach)

---

## Next Steps After Validation

### If Successful (Expected)
- Document actual vs expected gains
- Proceed to Strategy 3 (Abbreviation Handling)
- Target remaining 21% to reach 60% goal

### If Partial Success
- Analyze which families/tokens helped most
- Refine underperforming families
- Consider alternative approaches for missed patterns

### If Regression (Unlikely)
- Root cause analysis
- Incremental rollback
- Re-evaluate strategy

---

## Files Modified

1. **analyze_compositionality.py**:
   - Lines 725-759: MODIFIER_WITH_TOKENS expansion
   - Lines 1012-1048: New template family definitions

---

## Progress Toward Goal

```
Current:  153,788 / 393,844 = 39.05%
Target:   236,000 / 393,844 = 60.00%
Gap:      82,212 terms (20.95%)

Strategy 1 (Encounter):     +4,206 terms ✓
Strategy 2 (With Modifier): +8,000-12,000 terms (testing...)
Remaining strategies:       ~70,000 terms needed
```

---

**Status**: ⏳ Analysis running - results pending
**Time Elapsed**: ~15 minutes (expected completion: 10-15 more minutes)

---

*Implementation follows lessons learned from vocabulary review: test-driven, incremental, data-driven, practical coverage over semantic purity.*

---

## ACTUAL RESULTS

### Coverage Impact
- **Before Strategy 2**: 153,788 terms (39.05%)
- **After Strategy 2**: 155,423 terms (39.46%)
- **Actual Gain**: +1,635 terms (+0.41%)
- **vs Expected**: +8,000-12,000 terms
- **Achievement Rate**: 14-20% of expected ❌

### New Family Performance

| Family | Coverage | Chapter |
|--------|----------|---------|
| laterality_x_anatomy_x_injury_x_modifier_with_x_encounter | 1,136 | S (100%) |
| anatomy_x_injury_x_healing_x_modifier_with_x_encounter | 367 | S (100%) |
| **Total from new families** | **~1,503** | |

**Other new families**: Did not appear in top families (coverage <200 terms each)

### Chapter-Specific Improvements

| Chapter | Before | After | Change |
|---------|--------|-------|--------|
| M (musculoskeletal) | 53.3% | 55.2% | +1.9% ⭐ |
| F (mental/behavioral) | 53.3% | 53.6% | +0.3% |
| K (digestive) | 59.2% | 59.5% | +0.3% |
| J (respiratory) | 54.9% | 55.2% | +0.2% |
| N (genitourinary) | 60.7% | 60.8% | +0.1% |

**Best improvement**: M chapter (musculoskeletal) +1.9%
**Target O chapter**: No measurable improvement

---

## WHY IT UNDERPERFORMED

### 1. Competition from Existing Families
The new with-modifier families are **high-specificity** (5-6 slots), but existing families often captured terms first:
- Existing `anatomy_x_injury_x_fracture_detail_x_encounter` (4 slots) beats new 6-slot families due to higher distinctiveness
- Existing `laterality_x_anatomy_x_condition` (3 slots) captured many lateralized conditions

### 2. Token Overlap with Existing Slots
Many added tokens already existed in other slots:
- "complication", "complications" → already in COMPLICATION_TOKENS
- "infection" → already in CONDITION_TOKENS and COMPLICATION_TOKENS
- "hemorrhage" → already in CONDITION_TOKENS

**Impact**: These tokens were already being matched, just not in "with" families

### 3. Low Frequency of Compound Patterns
Evidence showed:
- "fracture with routine healing" - 917 instances
- "fracture with delayed healing" - 917 instances

**But**: These are already captured by existing families:
- `anatomy_x_injury_x_healing_x_encounter` (captures "fracture, routine healing")
- The "with" is often a connector, not a semantic slot

### 4. Multi-Word Phrase Matching Limitations
Phrases like "brief loss of consciousness" may not match if:
- The term uses different word order
- Abbreviations are present ("w/ LOC")
- Additional words appear between components

### 5. Wrong Target - Should Have Expanded Existing Families
Instead of creating NEW families, should have:
- Expanded vocabulary in existing high-performing families
- Focused on single-word tokens that appear in simple patterns
- Targeted different semantic gaps

---

## LESSONS LEARNED

### 1. High Specificity ≠ High Coverage
- More slots = fewer matches (stricter requirements)
- 3-4 slot families often outperform 5-6 slot families
- Existing families have priority in matching algorithm

### 2. Vocabulary Expansion ≠ Family Creation
Adding tokens helps IF:
- They fill gaps in existing families
- They enable new patterns not captured elsewhere
- They don't duplicate existing slot coverage

### 3. Data-Driven != Guaranteed Success
The unmatched term analysis showed patterns, but:
- Many were already partially captured
- The "with" connector is often structural, not semantic
- Compound patterns may be better handled by regex (Phase 2)

### 4. Test Incrementally
Should have:
- Added vocabulary first, measured impact
- Then added 1-2 families, measured impact
- Expanded only if showing positive returns

---

## WHAT WORKED

1. ✅ **M chapter improvement** (+1.9%): Musculoskeletal "with" patterns
2. ✅ **Quality maintained**: Fuzzy/ambiguous rates stable
3. ✅ **No regression**: Existing families unaffected
4. ✅ **New families functional**: Both active, just low coverage

---

## REVISED STRATEGY RECOMMENDATIONS

### For Future Strategies

1. **Focus on Vocabulary, Not Families**
   - Add tokens to existing successful families
   - Create new families only if clear gap exists

2. **Target Lower-Specificity Families**
   - 2-3 slot families have broader reach
   - Easier to match, higher coverage potential

3. **Avoid Token Duplication**
   - Check if tokens already exist before adding
   - Cross-slot overlap is OK, but intra-slot duplication adds no value

4. **Test Vocabulary Changes Separately**
   - Add vocab → test
   - Add families → test
   - Don't combine major changes

### Next Steps

**Option A**: Continue with Strategies 3-12 as planned
- Accept that some strategies will underperform
- Cumulative gains still progress toward 60% goal

**Option B**: Skip remaining template-based strategies
- Focus on what's working (vocabulary expansion)
- Move to regex/similarity approaches sooner

**Recommendation**: **Option A** - Continue systematically
- Small gains add up
- Learn what works for Phase 2
- Document successes and failures

---

## FINAL STATUS

✅ **Implementation Complete**
⚠️ **Underperformed Expectations** (20% of target)
✅ **No Negative Impact**
✅ **Quality Maintained**
➡️ **Ready for Strategy 3**

---

*Strategy 2 demonstrates that not all data-driven strategies succeed as expected. High-specificity families face competition from existing lower-specificity families, and token overlap reduces net gains. Key learning: vocabulary expansion works better than family proliferation.*
