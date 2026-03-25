# High-Impact Strategy Bundle

**Date**: 2026-03-24
**Approach**: Bundle proven high-impact strategies (vocabulary expansion) and skip low-impact ones (family proliferation)

---

## Why This Approach?

### Lessons from Strategies 1-2

**What Worked** ✅:
- **Vocabulary expansion**: ANATOMY +61 tokens, CONDITION +47 tokens → solid gains
- **Simple encounter phrases**: Multi-word tokens in ENCOUNTER_TOKENS → +3,266 terms
- **Existing family enhancement**: Adding vocabulary to proven families

**What Didn't Work** ⚠️:
- **High-specificity families**: 5-6 slot families compete poorly with existing 3-4 slot families
- **Token duplication**: Adding tokens that exist elsewhere provides minimal gain
- **Complex patterns**: "with" constructs often already captured by simpler patterns

### Revised Strategy: Vocabulary-First Approach

**Principle**: **Expand vocabularies aggressively, create families sparingly**

1. Add tokens to underutilized slots
2. Create new slots for clear semantic gaps
3. Only create families if they're 2-3 slots (high coverage potential)
4. Bundle related changes for efficient testing

---

## High-Impact Bundle Contents

### Bundle Components (3 strategies combined)

#### 1. Disease State Slot (Strategy 9) - Expected +6K-10K
- **Create new slot**: DISEASE_STATE_TOKENS
- **Target**: Temporal and pathological modifiers currently scattered
- **Impact**: E, I, M, N chapters (degenerative, vascular diseases)

#### 2. Maternal/Obstetric Vocabulary (Strategy 7) - Expected +4K-6K
- **Create new slot**: MATERNAL_CONTEXT_TOKENS
- **Expand**: Pregnancy-specific terms
- **Impact**: O chapter (currently 37% coverage)

#### 3. Enhanced "Of" Pattern Vocabulary (Strategy 5) - Expected +8K-12K
- **Expand existing slots**: ANATOMY_TOKENS, CONDITION_TOKENS
- **Add**: Anatomical relationships, pathological states
- **Impact**: All chapters (universal pattern)

**Combined Expected Gain**: +18K-28K terms (+4.6-7.1% coverage)

---

## Detailed Implementation Plan

### Part 1: Create DISEASE_STATE_TOKENS (New Slot)

**Purpose**: Capture disease temporal/pathological states currently misclassified

**Tokens to Add** (~25 tokens):
```python
DISEASE_STATE_TOKENS = {
    # Temporal states
    "acute",
    "chronic",
    "current",
    "recurrent",
    "persistent",
    "transient",
    "intermittent",

    # Pathological states
    "pathological",
    "traumatic",
    "spontaneous",
    "idiopathic",
    "congenital",
    "acquired",

    # Activity states
    "active",
    "inactive",
    "dormant",
    "latent",
    "quiescent",

    # Progression states
    "progressive",
    "stable",
    "resolving",
    "worsening",
    "advancing",
}
```

**Move from other slots**:
- "acute", "chronic" from SEVERITY_TOKENS → DISEASE_STATE_TOKENS
- "pathological" from DIAGNOSTIC_CLASSIFIER_TOKENS → DISEASE_STATE_TOKENS (keep in both)

**Create families** (2-3 slots only):
1. `disease_state_x_condition` (2 slots)
2. `disease_state_x_anatomy_x_condition` (3 slots)

---

### Part 2: Create MATERNAL_CONTEXT_TOKENS (New Slot)

**Purpose**: Target O chapter (pregnancy) - currently only 37% coverage

**Tokens to Add** (~30 tokens):
```python
MATERNAL_CONTEXT_TOKENS = {
    # Care context
    "maternal", "care", "maternal care",

    # Pregnancy states
    "pregnancy", "pregnant", "gravid",
    "antepartum", "prenatal", "antenatal",
    "intrapartum", "labor", "delivery", "childbirth",
    "postpartum", "puerperium", "postnatal",

    # Fetal context
    "fetus", "fetal",
    "newborn", "neonatal",
    "affected", "newborn affected by",

    # Pregnancy types
    "molar", "ectopic", "tubal",
    "multiple", "twin", "triplet",

    # Pregnancy complications
    "trimester",
    "first trimester", "second trimester", "third trimester",
    "gestation", "gestational",

    # Outcomes
    "abortion", "miscarriage",
    "stillbirth", "livebirth",
}
```

**Create families** (2-3 slots):
1. `maternal_context_x_condition` (2 slots)
2. `maternal_context_x_complication` (2 slots)
3. `condition_x_maternal_context` (2 slots - different order)

---

### Part 3: Enhance "Of" Pattern Vocabulary (No New Slot)

**Purpose**: Better capture "X of Y" patterns common in ICD-10-CM

**Expand ANATOMY_TOKENS** (+20 tokens):
```python
# Anatomical relationships often in "of" patterns
"lobe", "segment", "portion", "region", "area", "zone",
"body", "tail", "fundus", "apex", "dome",
"hilum", "hilus", "porta",
"bifurcation", "junction", "anastomosis",
"outlet", "inlet", "opening", "orifice",
```

**Expand CONDITION_TOKENS** (+25 tokens):
```python
# Conditions commonly in "of" patterns
"anomaly", "malformation", "deformity",
"absence", "agenesis", "aplasia", "hypoplasia",
"hypertrophy", "enlargement", "dilation", "dilatation",
"narrowing", "constriction",
"rupture", "tear", "laceration",
"compression", "entrapment",
"displacement", "malposition",
"torsion", "volvulus",
"adhesion", "contracture",
"bleeding", "oozing",
```

**Create families** (2 slots only):
1. `condition_of_anatomy` - implicit "of" (relies on word order)
2. Keep existing `anatomy_x_condition` (already covers many "of" patterns)

---

## Why This Bundle Works

### 1. Proven Approach
- Vocabulary expansion has consistent positive ROI
- New slots address clear semantic gaps
- Low-specificity families have high coverage potential

### 2. Targeted Chapter Impact
- **O chapter**: 37% → expected 45-50% (+8-13%)
- **E chapter**: Expected +2-3% (disease states)
- **M chapter**: Expected +1-2% (pathological states)
- **All chapters**: "of" patterns are universal

### 3. Minimal Competition Risk
- New slots don't compete with existing families
- 2-3 slot families have high priority in matching
- Vocabulary fills gaps, doesn't duplicate

### 4. Efficient Testing
- One analysis run tests all three strategies
- Easier to measure combined impact
- Faster iteration to 60% goal

---

## Expected Results

### Coverage Projection

| Metric | Current | Expected | Gain |
|--------|---------|----------|------|
| Overall | 39.46% | 44-46% | +4.5-6.5% |
| O chapter | 37% | 45-50% | +8-13% |
| E chapter | ~40% | 42-43% | +2-3% |
| M chapter | 55.2% | 56-57% | +1-2% |
| Total terms | 155,423 | 173,000-181,000 | +18K-26K |

### Family Performance Expectations

| Family | Expected Coverage | Primary Chapters |
|--------|------------------|------------------|
| maternal_context_x_condition | 3,000-5,000 | O |
| disease_state_x_condition | 4,000-6,000 | All |
| disease_state_x_anatomy_x_condition | 2,000-3,000 | E, I, M, N |
| Existing families (enhanced vocab) | +8,000-12,000 | All |

---

## Implementation Steps

1. ✅ Analyze and document strategy bundle
2. ⏳ Create DISEASE_STATE_TOKENS slot
3. ⏳ Create MATERNAL_CONTEXT_TOKENS slot
4. ⏳ Expand ANATOMY_TOKENS (+20)
5. ⏳ Expand CONDITION_TOKENS (+25)
6. ⏳ Create 5 new families (all 2-3 slots)
7. ⏳ Run analysis
8. ⏳ Validate results

**Estimated Time**: 30-40 minutes
**Risk Level**: 🟢 LOW (proven approaches)

---

## Success Criteria

### Minimum Success
- [ ] Coverage ≥ 42% (+2.5%)
- [ ] O chapter ≥ 42% (+5%)
- [ ] No regression in any chapter

### Target Success
- [ ] Coverage ≥ 44% (+4.5%)
- [ ] O chapter ≥ 45% (+8%)
- [ ] At least 2 new families with >1,000 terms

### Exceptional Success
- [ ] Coverage ≥ 46% (+6.5%)
- [ ] O chapter ≥ 50% (+13%)
- [ ] Total gain ≥ 20,000 terms

---

## Strategies Deferred/Skipped

### Lower Priority (for now)
- **Strategy 3**: Abbreviation Handling - complex, regex better
- **Strategy 4**: Already have LATERALITY_TOKENS
- **Strategy 6**: Etiology patterns - low specificity
- **Strategy 8**: Eye/Ear detail - narrow scope
- **Strategy 10**: Severity/Behavioral - overlap with existing
- **Strategy 11**: Auto-generation - Phase 2 technique
- **Strategy 12**: Foreign body - narrow scope

**Rationale**: Focus resources on highest-impact changes. Can revisit if needed.

---

## Next Steps After This Bundle

### If Successful (≥42% coverage)
1. **Evaluate remaining gap**: 236K - 165K = ~71K terms
2. **Consider Phase 2 approaches**: Regex, similarity matching
3. **Or continue with remaining strategies**: 6, 8, 10, 12

### If Partially Successful (40-42% coverage)
1. **Refine underperforming parts**
2. **Add more vocabulary to successful slots**
3. **Try 1-2 more targeted strategies**

### If Unsuccessful (<40% coverage)
1. **Root cause analysis**
2. **Rollback problematic changes**
3. **Reconsider approach**

---

## Risk Mitigation

### Potential Issues

1. **Token Overlap**: Disease state tokens may exist in other slots
   - **Mitigation**: Acceptable if they serve different semantic roles

2. **O Chapter Specificity**: Maternal terms very domain-specific
   - **Mitigation**: That's the goal - fill a clear gap

3. **Family Competition**: New families may lose to existing ones
   - **Mitigation**: Using 2-3 slots (high priority in matching)

4. **Testing Time**: Bundle approach means longer analysis run
   - **Mitigation**: Worth it for faster progress to goal

---

## Progress Tracking

```
Current:  155,423 / 393,844 = 39.46%
Bundle Target: 173,000-181,000 / 393,844 = 44-46%
Final Goal:    236,000 / 393,844 = 60%

After this bundle:
  Gap to goal: ~55K-63K terms (14-16%)
  Remaining strategies: Can reach goal with 2-3 more bundles
```

---

**Status**: 📋 Ready to implement
**Confidence**: 🟢🟢🟢🟢 HIGH (proven approach, targeted gaps, low risk)

---

*This bundle combines three high-impact strategies using proven vocabulary expansion techniques. Expected gain: +18K-28K terms toward the 60% coverage goal.*
