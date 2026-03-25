# Vocabulary Review Correction Report

**Date**: 2026-03-24
**Status**: 🔴 **CRITICAL - COVERAGE REGRESSION**

---

## Issue Summary

The vocabulary review caused a **-1.83% coverage regression** (-7,213 terms), opposite of the expected +3-5% improvement.

### Coverage Impact
- **Before**: 152,848 / 393,844 = **38.80%**
- **After**: 145,635 / 393,844 = **36.98%**
- **Change**: **-7,213 terms (-1.83%)**

---

## Root Cause Analysis

### Primary Cause: FRACTURE_DETAIL_TOKENS Over-Cleanup

**Changes Made**:
```diff
FRACTURE_DETAIL_TOKENS removed:
- "fx" (duplicate of INJURY_TOKENS)
- "open", "closed" (overlap with SEVERITY_TOKENS)
- "neck", "head", "shaft", "base" (anatomical locations)
- "styloid" (anatomical structure)
```

**Impact**:
| Family | Before | After | Loss | % Drop |
|--------|--------|-------|------|--------|
| laterality_x_anatomy_x_injury_x_fracture_detail_x_encounter | 5,728 | 655 | -5,073 | -88% |
| anatomy_x_injury_x_fracture_detail_x_healing_x_encounter | 4,043 | 1,247 | -2,796 | -69% |
| **Total from these 2 families** | **9,771** | **1,902** | **-7,869** | **-81%** |

---

## Why The Semantic Reasoning Failed

### The Semantic Argument (Correct but Impractical)
✅ "neck" in "fracture of neck of femur" IS anatomically the neck of the femur
✅ "open" and "closed" describe wound state, which is a severity aspect
✅ These create cross-slot ambiguity

### The Practical Reality (Why ICD-10-CM Works Differently)
❌ FRACTURE_DETAIL slot is **not** purely fracture pattern descriptors
❌ It serves as a **compound fracture modifier slot** in ICD-10-CM
❌ Terms like "closed fracture", "neck fracture", "shaft fracture" are **lexical units**
❌ The families are designed to capture these compound modifiers

### Example: "Closed displaced comminuted fracture of shaft of left femur, initial encounter"

**How it should tokenize**:
- closed = fracture_detail
- displaced = fracture_detail
- comminuted = fracture_detail
- fracture = injury
- shaft = ??? (PROBLEM: removed from fracture_detail)
- left = laterality
- femur = anatomy
- initial encounter = encounter

**Without "shaft" in fracture_detail**:
- The term doesn't match `laterality_x_anatomy_x_injury_x_fracture_detail_x_encounter`
- Falls through to lower-specificity family
- May not match at all

---

## Secondary Causes

### 2. LATERALITY_TOKENS Over-Cleanup
Removed: "unspecified", "unsp", "other", "oth"

**Impact**: Minor (-200 to -500 terms estimated)
**Rationale**: These DO appear in laterality context ("unspecified side")

### 3. MODIFIER_WITH_TOKENS Over-Cleanup
Removed: "routine", "healing", "delayed", "nonunion", "malunion"

**Impact**: Moderate (-500 to -1000 terms estimated)
**Rationale**: While these exist in HEALING_TOKENS, they also appear in "with" constructs

### 4. MECHANISM_TOKENS Cleanup
Removed: "drowning", "burn", "poisoning", "assault"

**Impact**: Minor to moderate (-200 to -500 terms estimated)

---

## Lessons Learned

### 1. Semantic Purity vs. Practical Coverage
**Finding**: ICD-10-CM slot vocabularies are optimized for **coverage**, not **semantic purity**

**Principle**: When a token appears in multiple semantic contexts, it should be in **ALL relevant slots** if it improves matching

### 2. Compound Terms in Medical Coding
**Finding**: Medical terminology uses compound modifiers that don't decompose semantically

**Example**:
- "closed fracture" is a lexical unit
- Even though "closed" describes wound state, "closed" must be in FRACTURE_DETAIL for "closed fracture" to match

### 3. Cross-Slot Duplication is Often Necessary
**Finding**: Some duplication is not just acceptable, it's **required** for proper coverage

**Guideline**: Keep tokens in multiple slots when:
- They appear in domain-specific compound terms
- Removal causes >1% coverage loss in any family
- The term is used differently in different contexts

### 4. Test Before Committing Large Changes
**Finding**: Should have tested incrementally

**Better Approach**:
1. Make changes to one slot at a time
2. Run analysis after each change
3. Measure impact
4. Roll back if negative
5. Proceed to next slot

---

## Correction Plan

### Phase 1: Revert FRACTURE_DETAIL_TOKENS Changes ✅ **HIGH PRIORITY**

```python
FRACTURE_DETAIL_TOKENS = {
    "fx",  # RESTORE: used in "fx with..."
    "open",  # RESTORE: "open fracture"
    "closed",  # RESTORE: "closed fracture"
    "displaced",
    "nondisplaced",
    "disp",
    "nondisp",
    "comminuted",
    "segmental",
    "transverse",
    "oblique",
    "spiral",
    "intraarticular",
    "intra-articular",
    "extraarticular",
    "extra-articular",
    "shaft",  # RESTORE: "shaft fracture"
    "neck",  # RESTORE: "neck fracture"
    "head",  # RESTORE: "head fracture"
    "base",  # RESTORE: "base fracture"
    "epiphysis",
    "physeal",
    "styloid",  # RESTORE: "styloid fracture"
    "trochanteric",
    "subtrochanteric",
}
```

**Expected Recovery**: +7,000 to +8,000 terms (back to ~38.5-39%)

### Phase 2: Partial Revert of LATERALITY_TOKENS

```python
LATERALITY_TOKENS = {
    "left", "right", "bilateral", "unilateral",
    "lt", "rt",
    "unspecified", "unsp",  # RESTORE: used in "unspecified side"
}
```

**Expected Recovery**: +200 to +500 terms

### Phase 3: Selective Revert of MODIFIER_WITH_TOKENS

```python
MODIFIER_WITH_TOKENS = {
    "routine healing",
    "delayed healing",
    "routine",  # RESTORE: for flexible matching
    "delayed",  # RESTORE: for flexible matching
    "nonunion",  # RESTORE: appears in "with nonunion"
    "malunion",  # RESTORE: appears in "with malunion"
    "loss", "consciousness", "loss of consciousness",
    "behavioral", "disturbance", "behavioral disturbance",
    "psychotic", "psychotic disturbance",
    "mood", "mood disturbance",
    "anxiety",
    "mention", "involvement", "mention of heart involvement",
    "agitation",
}
```

**Expected Recovery**: +500 to +1,000 terms

### Phase 4: Keep Beneficial Additions

✅ **KEEP** all additions to:
- ANATOMY_TOKENS (+61 tokens)
- CONDITION_TOKENS (+47 tokens)
- INJURY_TOKENS (+8 tokens)

These will provide additional coverage once the fracture issues are fixed.

---

## Revised Expected Outcome

### After Corrections:
- **Baseline (before any changes)**: 149,582 terms (38.0%)
- **Strategy 1 (encounter expansion)**: 152,848 terms (38.8%)
- **After vocabulary additions**: 145,635 terms (36.98%) ← CURRENT (BROKEN)
- **After corrections**: ~153,000-155,000 terms (38.8-39.4%) ← TARGET

**Net Expected Improvement over Baseline**: +3,500 to +5,500 terms (+0.9% to +1.4%)

---

## Revised Semantic Principles

### 1. Practical Coverage > Semantic Purity
When in doubt, favor coverage. ICD-10-CM is optimized for coding, not semantic elegance.

### 2. Domain-Specific Compound Terms
Medical compound terms (e.g., "closed fracture") should have all components in their domain slot.

### 3. Acceptable Duplication Categories
- **Fracture modifiers**: Can exist in both FRACTURE_DETAIL and other slots
- **Temporal/state modifiers**: Can exist in both domain slots and general slots
- **Qualifiers**: "unspecified" can be in both LATERALITY and QUALIFIER

### 4. Test-Driven Vocabulary Changes
- Change one slot at a time
- Measure impact immediately
- Require >0% coverage gain to proceed
- Document all regressions

---

## Action Items

- [x] Identify root cause
- [x] Document failure analysis
- [ ] Revert FRACTURE_DETAIL_TOKENS changes
- [ ] Revert LATERALITY_TOKENS changes (partial)
- [ ] Revert MODIFIER_WITH_TOKENS changes (selective)
- [ ] Re-run analysis
- [ ] Verify recovery to 38.5%+ coverage
- [ ] Update SLOT_VOCABULARY_REVIEW_REPORT.md with corrections

---

## Conclusion

The vocabulary review identified valid semantic issues but applied overly aggressive cleanup. The key insight is that **ICD-10-CM slot vocabularies prioritize coverage over semantic purity**. Cross-slot duplication is often necessary for proper matching of medical compound terms.

**Status**: Corrective actions pending
**Risk Level**: 🟢 **LOW** - Clear path to recovery identified
**Timeline**: 15-20 minutes to implement and validate

---

*This correction demonstrates the importance of incremental testing and the principle that medical coding systems optimize for practical coverage rather than pure semantic decomposition.*
