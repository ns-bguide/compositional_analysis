# Unmatched Terms Analysis Report

**Date**: 2026-03-25
**Current Coverage**: 50.64% (199,427 / 393,844 terms)
**Unmatched**: 194,417 terms (49.36%)

---

## Executive Summary

After implementing partial coverage matching, **194,417 terms remain unmatched**. Analysis reveals:

1. **67% of unmatched (130,626 terms) are 7+ words** - Partial coverage helped but long terms still dominate
2. **S-chapter accounts for 30%** (58,915 terms, avg 10 words)
3. **Short terms (1-6 words) represent 33%** (63,791 terms) - Unexpectedly high; suggests vocabulary gaps
4. **High abbreviation usage** in all unmatched (92% in S/T/V chapters)
5. **Common missing patterns**: "unspecified", laterality phrases, temporal markers

---

## Key Findings

### 1. Length Distribution Analysis

| Length Bracket | Count | % of Unmatched | Top Chapters |
|----------------|-------|----------------|--------------|
| Short (1-3 words) | 31,044 | 16.0% | E (10.3%), A (9.7%), Q (8.1%) |
| Medium (4-6 words) | 32,747 | 16.8% | S (12.2%), H (9.0%), M (8.7%) |
| **Long (7-12 words)** | **109,759** | **56.5%** | **S (42.6%), T (13.4%), V (7.8%)** |
| **Very long (13+ words)** | **20,867** | **10.7%** | **V (40.7%), S (37.5%), T (5.6%)** |

**Critical Insight**: 67.2% of unmatched terms are 7+ words. Partial coverage (80% threshold) helped but not enough.

### 2. Chapter-Specific Patterns

#### High-Volume Unmatched Chapters

| Chapter | Count | Avg Length | Characteristics |
|---------|-------|------------|-----------------|
| **S** | 58,915 (30.3%) | 10.0 words | 96.8% have abbreviations, 61.5% commas |
| **T** | 17,860 (9.2%) | 9.2 words | 94.0% abbreviations, 73.3% commas |
| **V** | 17,910 (9.2%) | 12.9 words | 94.8% abbreviations, 86.4% commas |
| **M** | 11,295 (5.8%) | 7.4 words | 83.6% abbreviations, 64.6% commas |
| **H** | 7,513 (3.9%) | 6.1 words | 78.8% abbreviations, 44.4% commas |

**S-chapter (Injury)**: 58,915 unmatched despite fracture families showing +237% improvement. Still massive gap.

**V-chapter (External causes)**: 17,910 terms, avg 12.9 words - ultra-long structured descriptions.

#### Short-Term Unmatched Chapters

| Chapter | Count | Avg Length | Pattern |
|---------|-------|------------|---------|
| A | 5,093 | 3.6 words | Bacterial diseases, taxonomy variations |
| B | 3,663 | 3.7 words | Infections, synonyms |
| E | 6,738 | 4.5 words | Metabolic/endocrine, compound terms |
| Q | 4,568 | 3.9 words | Congenital conditions, synonyms |

**Insight**: Short terms failing suggests **vocabulary gaps**, not length issues.

### 3. Common Missing Patterns

#### Top Unmatched Words

| Word | Count | Context |
|------|-------|---------|
| unspecified | 15,627 | Qualifier for uncertain diagnoses |
| unsp | 10,055 | Abbreviation of "unspecified" |
| fx | 8,825 | Abbreviation of "fracture" |
| w | 7,963 | Abbreviation of "with" |
| left | 7,107 | Laterality (not matched) |
| right | 7,002 | Laterality (not matched) |
| encounter | 7,132 | Encounter context |
| for | 6,550 | Encounter phrase connector |
| subsequent | 4,085 | Temporal marker |
| init / initial | 6,782 | Temporal marker |

**Critical**: "fx", "w", "unsp", "subs", "init" are **abbreviations not in our vocabularies**.

#### Top Bigrams

| Bigram | Count | Analysis |
|--------|-------|----------|
| subsequent encounter | 4,048 | Temporal - already in ENCOUNTER_TOKENS? |
| of unspecified | 3,923 | "unspecified" as anatomical/location modifier |
| of left / of right | 7,657 | Laterality phrases |
| fracture of | 3,594 | "fracture" not matching? |
| fx of | 2,603 | "fx" abbreviation missing |
| due to | 2,253 | Causation phrase |
| injury of | 2,120 | "injury" not matching? |

**Critical**: "fracture of" (3,594) and "injury of" (2,120) suggests these base terms **should match but don't**.

#### Top Trigrams

| Trigram | Count | Analysis |
|---------|-------|----------|
| subsequent encounter for | 2,023 | Should be in ENCOUNTER families |
| nondisp fx of | 1,463 | "nondisp" + "fx" abbreviations |
| subs for fx | 1,430 | Abbreviation-heavy phrase |
| for fx w | 1,430 | "fx" + "w" abbreviations |
| encounter for fracture | 1,422 | Should match encounter families |
| for fracture with | 1,283 | Should match modifier_with families |
| for open fracture | 1,105 | "open fracture" should match |

**Critical**: Phrases like "subsequent encounter for" (2,023) and "encounter for fracture" (1,422) **should be matching** encounter families.

---

## Root Cause Analysis

### Why Are These Terms Unmatched?

#### 1. **Abbreviation Gap** (High Impact)

**Problem**: Common ICD-10-CM abbreviations not in vocabularies

**Evidence**:
- "fx" (8,825 occurrences) - not in FRACTURE_DETAIL_TOKENS
- "w" (7,963 occurrences) - not in any slot
- "unsp" (10,055 occurrences) - not in QUALIFIER_TOKENS
- "subs" (3,940 occurrences) - not in ENCOUNTER_TOKENS
- "init" (3,657 occurrences) - not in ENCOUNTER_TOKENS
- "oth" (3,059 occurrences) - not in QUALIFIER_TOKENS
- "disp/nondisp" (3,633 occurrences) - not in FRACTURE_DETAIL_TOKENS

**Impact**: ~40,000-50,000 terms potentially affected

**Solution**: Add abbreviations to existing slots

#### 2. **"Unspecified" Variation Gap** (Medium Impact)

**Problem**: "unspecified" used as modifier in many contexts not captured

**Evidence**:
- "of unspecified" (3,923) - location modifier
- "disorder, unspecified" patterns
- "unspecified [anatomy]" patterns

**Current State**: "unspecified" in QUALIFIER_TOKENS but not matching these patterns

**Impact**: ~15,000-20,000 terms

**Solution**: Better "unspecified" slot coverage or multi-slot matching

#### 3. **Synonym/Variation Gap** (Medium Impact)

**Problem**: Medical term synonyms not in vocabularies

**Evidence**:
- Chapter A: "vibrio cholerae" variations, "cholera eltor"
- Chapter B: "eczema herpeticum" vs "herpeticum eczema"
- Chapter E: compound metabolic terms
- Chapter Q: congenital condition synonyms

**Impact**: ~10,000-15,000 terms (mostly short)

**Solution**: Vocabulary expansion with synonyms

#### 4. **Partial Coverage Still Insufficient** (Medium Impact)

**Problem**: 80% threshold for long terms (13+ words) may still be too strict

**Evidence**:
- 20,867 very long terms (13+ words) remain unmatched
- V-chapter: avg 12.9 words, 17,910 unmatched
- Many structured descriptions with >50% coverage but <80%

**Impact**: ~15,000-20,000 terms

**Solution**: Lower threshold for ultra-long terms (20+ words: 70%?)

#### 5. **Structured Description Gap** (Medium Impact)

**Problem**: V/W/X/Y chapters have highly structured external cause descriptions

**Evidence**:
- V-chapter: "pedestrian on foot injured in collision with..."
- Format: [person] + [action] + [mechanism] + [location] + [encounter]
- Current families don't capture this structure

**Impact**: ~25,000-30,000 terms (V/W/X/Y chapters)

**Solution**: Dedicated external cause families or lower threshold

---

## Opportunity Analysis

### Quick Wins (High ROI)

#### 1. Abbreviation Expansion (+40K-50K terms potential)

**Action**: Add common abbreviations to existing slots

| Slot | Add Abbreviations |
|------|-------------------|
| FRACTURE_DETAIL_TOKENS | "fx", "disp", "nondisp", "displ" |
| ENCOUNTER_TOKENS | "init", "subs", "encntr", "enc" |
| QUALIFIER_TOKENS | "unsp", "oth", "nos" |
| MODIFIER_WITH_TOKENS | "w" (with), "w/o" (without) |

**Expected gain**: 30,000-40,000 terms (15-20% of unmatched)

**Effort**: 1-2 hours (low)

**Risk**: Low - abbreviations are standard ICD-10-CM

#### 2. Short-Term Vocabulary Expansion (+10K-15K terms)

**Action**: Add synonyms for common medical terms

**Target chapters**: A, B, E, Q (short terms with vocabulary gaps)

**Examples**:
- Chapter A: bacterial species variations
- Chapter E: metabolic compound terms
- Chapter Q: congenital synonym patterns

**Expected gain**: 10,000-15,000 terms (5-8% of unmatched)

**Effort**: 4-6 hours (medium)

**Risk**: Medium - need domain expertise for synonyms

#### 3. Threshold Tuning for Ultra-Long Terms (+5K-10K terms)

**Action**: Lower threshold to 70% for terms 20+ words

**Rationale**:
- 20,867 very long terms (13+ words) unmatched
- Many V-chapter terms with 60-75% coverage fail at 80%

**Expected gain**: 5,000-10,000 terms (3-5% of unmatched)

**Effort**: 30 minutes (very low)

**Risk**: Low - quality maintained with specificity scoring

### Medium-Term Opportunities

#### 4. External Cause Families (+20K-25K terms)

**Action**: Create V/W/X/Y-specific families

**Structure**:
```
person_type_x_action_x_mechanism_x_location_x_encounter
vehicle_type_x_collision_type_x_person_role_x_encounter
exposure_type_x_substance_x_location_x_intent_x_encounter
```

**Expected gain**: 20,000-25,000 terms (10-13% of unmatched)

**Effort**: 8-12 hours (high)

**Risk**: Medium - new slot vocabularies needed

#### 5. S-Chapter Deep Dive (+10K-15K terms)

**Action**: Analyze 58,915 S-chapter unmatched for specific patterns

**Hypothesis**: Fracture families improved dramatically (+237%) but still missing patterns

**Potential gaps**:
- "unspecified superficial injury" patterns
- Specific anatomical location granularity
- Fracture healing stage variations

**Expected gain**: 10,000-15,000 terms (5-8% of unmatched)

**Effort**: 6-8 hours (high)

**Risk**: Medium - may hit diminishing returns

---

## Recommended Action Plan

### Phase 1: Quick Wins (Total: +45K-65K terms, 23-33% gain)

**Priority 1: Abbreviation Expansion** ⭐⭐⭐⭐⭐
- Add "fx", "disp", "nondisp" to FRACTURE_DETAIL_TOKENS
- Add "init", "subs", "encntr" to ENCOUNTER_TOKENS
- Add "unsp", "oth", "nos" to QUALIFIER_TOKENS
- Add "w", "w/o" as synonyms in relevant slots
- **Expected**: +30K-40K terms
- **Effort**: 1-2 hours
- **Confidence**: HIGH

**Priority 2: Threshold Tuning** ⭐⭐⭐⭐
- Lower threshold to 70% for 20+ word terms
- Keep 80% for 13-19 words, 90% for 7-12 words
- **Expected**: +5K-10K terms
- **Effort**: 30 minutes
- **Confidence**: HIGH

**Priority 3: Short-Term Vocabulary** ⭐⭐⭐
- Expand A, B, E, Q vocabularies with synonyms
- Focus on 3-5 word terms (high matchability)
- **Expected**: +10K-15K terms
- **Effort**: 4-6 hours
- **Confidence**: MEDIUM-HIGH

**Phase 1 Total Expected**: 50.64% → **62-71% coverage** (242K-280K terms)

### Phase 2: Strategic Expansion (if Phase 1 reaches 65%+)

**Priority 4: External Cause Families**
- Create V/W/X/Y-specific families
- **Expected**: +20K-25K terms
- **Effort**: 8-12 hours

**Priority 5: S-Chapter Analysis**
- Deep dive into injury patterns
- **Expected**: +10K-15K terms
- **Effort**: 6-8 hours

---

## Success Metrics

### Phase 1 Targets

| Metric | Current | Minimum | Target | Exceptional |
|--------|---------|---------|--------|-------------|
| Overall Coverage | 50.64% | 55% | 60% | 65% |
| Coverage Gain | 199,427 | +20K | +40K | +60K |
| Short Terms (1-6 words) | - | 60% | 70% | 80% |
| Long Terms (7-12 words) | - | 45% | 55% | 65% |
| V-chapter Coverage | - | 30% | 40% | 50% |

### Quality Gates

- Fuzzy match rate: ≤8% (currently 5.7%)
- Ambiguous rate: ≤1.0% (currently 0.46%)
- No false positives in manual spot checks

---

## Files Generated

- `analysis_outputs/unmatched_samples_by_chapter.csv` - 100 samples per chapter for manual review

---

## Conclusion

**The remaining 194,417 unmatched terms (49.36%) are addressable with abbreviation expansion and threshold tuning.**

**Key Insight**: The high percentage of short unmatched terms (33%) indicates **vocabulary gaps**, not algorithmic limitations. Adding standard ICD-10-CM abbreviations ("fx", "w", "unsp", "init", "subs") could unlock 30K-40K terms with minimal effort.

**Recommended Path**:
1. Abbreviation expansion (1-2 hours) → +30K-40K
2. Threshold tuning (30 minutes) → +5K-10K
3. Vocabulary expansion (4-6 hours) → +10K-15K

**Expected Outcome**: 50.64% → 60-65% coverage with 6-9 hours of work.

**Next decision point**: If Phase 1 reaches 60%+, evaluate whether 70%+ is achievable or if we've hit the compositional ceiling.
