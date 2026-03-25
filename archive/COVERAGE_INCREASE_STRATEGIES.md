# Strategies to Increase Template Family Coverage

**Current State**: 38% coverage (149,582 / 393,844 terms)
**Goal**: Achieve 60%+ coverage before moving to regex generation

---

## Analysis Summary

**Unmatched Terms**: 244,262 (62%)

**Top Unmatched Chapters**:
- S (Injury/Poisoning): 16.7% of unmatched
- M (Musculoskeletal): 11.5%
- H (Eye/Ear): 7.1%
- E (Endocrine): 7.0%
- O (Pregnancy): 6.5%

**Patterns in Unmatched**:
- 48% contain commas (complex multi-part terms)
- Top bigrams: "subsequent encounter", "encounter for", "fracture of"
- Top trigrams: "encounter for fracture", "for fracture with"
- Common words: "unspecified", "with", "fracture", "encounter", "disorder"

---

## Strategy 1: Expand Encounter Slot Variations

**Problem**: Many encounter phrases aren't matching.

**Evidence**:
```
"subsequent encounter for fracture" - 3,247 instances
"initial encounter for" - 1,305 instances
"encounter for fracture" - 3,471 instances
```

**Current State**: Encounter slot has ~10 tokens (initial, subsequent, sequela, etc.)

**Action**:
1. Add **composite encounter phrases**:
   - "subsequent encounter"
   - "initial encounter"
   - "encounter for"
   - "subs encntr"
   - "init encntr"

2. Create **encounter phrase families**:
   - `encounter_phrase_x_context` (e.g., "encounter for fracture")
   - `encounter_phrase_x_anatomy_x_injury`

**Expected Gain**: +5,000-10,000 terms

---

## Strategy 2: Add "With" Modifier Slot

**Problem**: "with X" constructs are extremely common but not captured.

**Evidence**:
```
"fracture with routine healing" - 917 instances
"fracture with delayed healing" - 917 instances
"fracture with nonunion" - 895 instances
"fracture with malunion" - 523 instances
"with loss of consciousness" - 973 instances
```

**Action**:
1. Create new **`modifier_with` slot**:
   ```python
   MODIFIER_WITH_TOKENS = {
       "routine healing", "delayed healing", "nonunion", "malunion",
       "loss of consciousness", "behavioral disturbance",
       "psychotic disturbance", "mood disturbance", "anxiety",
       "mention of heart involvement", "agitation"
   }
   ```

2. Create **with-modifier families**:
   - `anatomy_x_injury_x_modifier_with_x_encounter`
   - `condition_x_modifier_with`
   - `anatomy_x_injury_x_fracture_detail_x_modifier_with_x_encounter`

**Expected Gain**: +8,000-12,000 terms

---

## Strategy 3: Expand Abbreviation Handling

**Problem**: Abbreviations are being expanded but terms still not matching.

**Evidence**:
```
Top words: "w" (7,799), "unsp" (7,672), "fx" (5,243), "subs" (3,312),
           "oth" (2,794), "init" (2,599), "o" (1,696)
```

**Current Issues**:
- "w" often means "with" not "week"
- "o" often means "without"
- Abbreviations in context need better handling

**Action**:
1. **Context-aware abbreviation expansion**:
   ```python
   "w": ["with", "week"],  # Currently just "with"
   "o": ["without", "other"],  # Add "without"
   "w/o": ["without"],
   "w/": ["with"],
   "nec": ["not elsewhere classified"],
   "nos": ["not otherwise specified"]
   ```

2. **Multi-token abbreviations**:
   - "fx w" → "fracture with"
   - "subs for" → "subsequent for"
   - "subs encntr" → "subsequent encounter"

**Expected Gain**: +3,000-5,000 terms

---

## Strategy 4: Add Laterality/Specificity Slot

**Problem**: Many terms differ only by laterality or specificity markers.

**Evidence**:
```
"of unspecified" - 3,757 instances
"of left" - 3,204 instances
"of right" - 3,199 instances
"unspecified" - 16,471 total occurrences
```

**Action**:
1. Create **`laterality` slot**:
   ```python
   LATERALITY_TOKENS = {
       "left", "right", "bilateral", "unilateral",
       "unspecified", "unsp", "oth", "other"
   }
   ```

2. Add **laterality-aware families**:
   - `anatomy_x_laterality_x_condition`
   - `injury_x_laterality_x_anatomy_x_encounter`
   - `qualifier_x_anatomy_x_laterality_x_injury_x_encounter`

**Expected Gain**: +10,000-15,000 terms

---

## Strategy 5: Expand "Of" Chain Patterns

**Problem**: Many anatomical relationships use "of" chains not captured.

**Evidence**:
```
"fracture of" - 3,785 instances
"injury of" - 2,127 instances
"neoplasm of" - 1,558 instances
"ulcer of" - 1,185 instances
```

**Action**:
1. Create **explicit "of" connector families**:
   - `condition_of_anatomy`
   - `injury_of_anatomy_x_encounter`
   - `neoplasm_of_anatomy`
   - `qualifier_x_condition_of_anatomy`

2. **Pattern matching for "X of Y"**:
   - Allow slot-filling to recognize "condition of anatomy" pattern
   - Add "of" as a structural marker in fuzzy matching

**Expected Gain**: +8,000-12,000 terms

---

## Strategy 6: Etiology Patterns (Due To / Caused By / Because Of)

**Problem**: Causal relationships common but not well-captured.

**Evidence**:
```
"due to" - 2,419 instances
"caused by" - 1,878 instances
"because of" - 1,785 instances
```

**Action**:
1. Expand **`etiology` slot** vocabulary:
   ```python
   ETIOLOGY_TOKENS = {
       "due", "caused", "because", "secondary", "following",
       "due to", "caused by", "because of", "secondary to",
       "associated with", "complicating", "in"
   }
   ```

2. Create **better etiology families**:
   - `condition_x_etiology_x_agent`
   - `anatomy_x_condition_x_etiology_x_agent`
   - `condition_x_etiology_x_condition` (e.g., "meningitis due to salmonella")

**Expected Gain**: +5,000-8,000 terms

---

## Strategy 7: Maternal/Obstetric Patterns

**Problem**: O chapter (pregnancy) has low coverage (37%).

**Evidence**:
```
"maternal care for" - 1,323 instances
"fetus" - 2,598 occurrences
"trimester" - 2,417 occurrences
"molar pregnancy" patterns
```

**Action**:
1. Create **maternal care slot**:
   ```python
   MATERNAL_CONTEXT_TOKENS = {
       "maternal care", "care for", "mother", "maternal",
       "fetus", "fetal", "newborn", "newborn affected by"
   }
   ```

2. Create **O-chapter specific families**:
   - `maternal_care_x_condition`
   - `maternal_care_x_complication_x_trimester`
   - `newborn_affected_by_x_maternal_condition`
   - `pregnancy_x_complication_x_trimester`

**Expected Gain**: +4,000-6,000 terms

---

## Strategy 8: Eye/Ear Anatomical Detail (H Chapter)

**Problem**: H chapter has many specific anatomical terms.

**Evidence**:
```
"right upper eyelid" - multiple instances
"hordeolum externum of right upper eyelid"
Specific eye structures need better coverage
```

**Action**:
1. Expand **eye/ear anatomy** vocabulary:
   ```python
   EYE_EAR_ANATOMY = {
       "eyelid", "upper eyelid", "lower eyelid",
       "right upper eyelid", "left upper eyelid",
       "right lower eyelid", "left lower eyelid",
       "external ear", "middle ear", "inner ear",
       "tympanic membrane", "mastoid", "auditory canal"
   }
   ```

2. Create **compound anatomy tokens** for H chapter
3. Add **H-specific families** with detailed eye/ear anatomy

**Expected Gain**: +3,000-5,000 terms

---

## Strategy 9: Pathological/Current Modifiers

**Problem**: Disease state modifiers not captured.

**Evidence**:
```
"pathological fracture" - 1,507 instances
"current pathological fracture" - 712 instances
"osteoporosis with current pathological fracture" - 708 instances
"chronic gout" - 1,367 instances
"chronic ulcer" - 646+ instances
```

**Action**:
1. Create **disease state slot**:
   ```python
   DISEASE_STATE_TOKENS = {
       "acute", "chronic", "current", "recurrent", "persistent",
       "pathological", "traumatic", "spontaneous", "active", "inactive"
   }
   ```

2. Add **state-aware families**:
   - `disease_state_x_condition`
   - `disease_state_x_anatomy_x_condition`
   - `condition_x_disease_state_x_condition` (e.g., "osteoporosis with current fracture")

**Expected Gain**: +6,000-10,000 terms

---

## Strategy 10: Severity/Behavioral Qualifiers

**Problem**: Mental/behavioral chapters (F, G) need qualifier support.

**Evidence**:
```
"vascular dementia, unspecified severity, without behavioral disturbance..."
"with agitation", "with other behavioral disturbance"
Multiple qualifiers stacked: "without beh/psych/mood/anx"
```

**Action**:
1. Create **severity/behavioral slot**:
   ```python
   SEVERITY_BEHAVIORAL_TOKENS = {
       "mild", "moderate", "severe", "unspecified severity",
       "with agitation", "without behavioral disturbance",
       "with behavioral disturbance", "psychotic disturbance",
       "mood disturbance", "anxiety"
   }
   ```

2. Create **F/G-specific families**:
   - `condition_x_severity_x_behavioral_modifier`
   - `condition_x_severity` (simple)

**Expected Gain**: +2,000-4,000 terms

---

## Strategy 11: Auto-Generate Families from Unmatched

**Problem**: May be systematic patterns we're missing.

**Action**:
1. **Run n-gram analysis on unmatched** to discover new patterns
2. **Cluster similar unmatched terms** to identify template candidates
3. **Generate candidate families** from frequent unmatched patterns
4. **Validate** against ICD chapter alignment

**Expected Gain**: +5,000-10,000 terms (speculative)

---

## Strategy 12: Foreign Body Patterns

**Evidence**:
```
"foreign body of" - 916 instances
```

**Action**:
1. Create **foreign body families**:
   - `foreign_body_x_anatomy`
   - `foreign_body_x_anatomy_x_encounter`

**Expected Gain**: +1,000-2,000 terms

---

## Implementation Priority (Phased Approach)

### **Phase A: Quick Wins** (Target: +25K terms, 44% coverage)
1. ✅ Strategy 2: Add "With" Modifier Slot (+10K)
2. ✅ Strategy 4: Laterality/Specificity Slot (+15K)
3. ✅ Strategy 3: Better Abbreviation Handling (+5K)

### **Phase B: Structural Improvements** (Target: +25K terms, 51% coverage)
4. ✅ Strategy 5: "Of" Chain Patterns (+10K)
5. ✅ Strategy 1: Encounter Variations (+8K)
6. ✅ Strategy 6: Etiology Patterns (+7K)

### **Phase C: Domain-Specific** (Target: +15K terms, 55% coverage)
7. ✅ Strategy 9: Pathological/State Modifiers (+8K)
8. ✅ Strategy 7: Maternal/Obstetric Patterns (+5K)
9. ✅ Strategy 12: Foreign Body Patterns (+2K)

### **Phase D: Advanced** (Target: +10K terms, 58%+ coverage)
10. ✅ Strategy 8: Eye/Ear Detail (+4K)
11. ✅ Strategy 10: Severity/Behavioral (+3K)
12. ✅ Strategy 11: Auto-Generation (+3K)

---

## Success Metrics

- **Phase A Complete**: 44% coverage (173K terms)
- **Phase B Complete**: 51% coverage (201K terms)
- **Phase C Complete**: 55% coverage (217K terms)
- **Phase D Complete**: 58%+ coverage (228K+ terms)

**Target Before Regex Phase**: 60% coverage (236K terms)

---

## Technical Implementation Notes

### Code Changes Needed:

1. **Expand `SLOT_TAXONOMY`** in `analyze_compositionality.py`:
   - Add new slots: `modifier_with`, `laterality`, `disease_state`, `severity_behavioral`, `maternal_context`
   - Expand existing slots with new vocabulary

2. **Add families to `TEMPLATE_FAMILY_SPECS`**:
   - 20-30 new families across all strategies
   - Use chapter policy to guide domain-specific families

3. **Improve fuzzy matching**:
   - Handle multi-token patterns better
   - Add "of" as structural connector
   - Context-aware abbreviation expansion

4. **Auto-family generation enhancements**:
   - Run discovery on unmatched terms
   - Add validation checks for new auto-families

### Validation Approach:

1. After each phase, run full analysis
2. Check chapter coverage improvement
3. Sample-review new matches for quality
4. Adjust if false positives increase
5. Document gains in analysis_outputs/

---

## Notes

- These strategies are **data-driven** from analyzing 100K unmatched terms
- Expected gains are **conservative estimates** based on n-gram frequencies
- Some strategies may overlap (terms matching multiple new families)
- Total expected gain: **+60K-85K terms** → **55-60% coverage**
- Remaining 40% will likely need **similarity-based approaches** (Phase 2)
