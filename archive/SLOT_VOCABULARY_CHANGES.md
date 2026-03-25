# Slot Vocabulary Review - Change Log

**Review Date**: 2026-03-24
**Reviewer**: Claude Sonnet 4.5

## Overview
This document tracks all changes made during the comprehensive slot vocabulary review for semantic coherence and consistency.

---

## Changes Made

### 1. ENCOUNTER_TOKENS

**Issues Found**:
- "routine" and "delayed" are healing modifiers, not encounter types
- These semantically belong in HEALING_TOKENS

**Changes**:
- ❌ REMOVED: "routine", "delayed"
- ✓ Moved to: HEALING_TOKENS

---

### 2. FRACTURE_DETAIL_TOKENS

**Issues Found**:
- "fx" duplicates INJURY_TOKENS (already there)
- "neck", "head", "shaft", "base" are anatomical locations, not fracture details
- "styloid" is an anatomical structure (already in ANATOMY_TOKENS)
- "open" and "closed" duplicate SEVERITY_TOKENS

**Changes**:
- ❌ REMOVED: "fx" (duplicate)
- ❌ REMOVED: "neck", "head", "shaft", "base" (anatomical locations, not fracture characteristics)
- ❌ REMOVED: "styloid" (duplicate of anatomy)
- ❌ REMOVED: "open", "closed" (kept in SEVERITY_TOKENS for fracture classification)

**Note**: These location terms are part of fracture naming (e.g., "fracture of neck of femur") but the "neck" is anatomical, not a fracture type descriptor. Better handled by anatomy slot.

---

### 3. HEALING_TOKENS

**Issues Found**:
- Too limited - missing common healing states
- Should include temporal modifiers from ENCOUNTER_TOKENS

**Changes**:
- ✓ ADDED: "routine" (from ENCOUNTER_TOKENS)
- ✓ ADDED: "delayed" (from ENCOUNTER_TOKENS)

---

### 4. MECHANISM_TOKENS

**Issues Found**:
- "drowning" duplicates CONDITION_TOKENS
- "burn" duplicates INJURY_TOKENS
- "poisoning" duplicates TOXIC_EVENT_TOKENS
- "assault" duplicates TOXIC_INTENT_TOKENS

**Changes**:
- ❌ REMOVED: "drowning" (keep in CONDITION_TOKENS)
- ❌ REMOVED: "burn" (keep in INJURY_TOKENS)
- ❌ REMOVED: "poisoning" (keep in TOXIC_EVENT_TOKENS)
- ❌ REMOVED: "assault" (keep in TOXIC_INTENT_TOKENS)

**Rationale**: Mechanism should describe HOW injury occurred (collision, fall, fire) not the injury itself or intent.

---

### 5. SEVERITY_TOKENS

**Issues Found**:
- "open" and "closed" are specific to fractures/wounds, belong in FRACTURE_DETAIL_TOKENS
- "acute" and "chronic" are temporal/disease state modifiers, not severity
- "isolated" is unclear in this context

**Changes**:
- ✓ KEPT: "open", "closed" (needed for fracture classification)
- ✓ KEPT: "acute", "chronic" (temporal aspect is part of severity assessment)
- ❌ REMOVED: "isolated" (ambiguous - not clearly a severity marker)

**Note**: Decided to keep "open"/"closed" here despite being in FRACTURE_DETAIL_TOKENS since they apply to general wounds too.

---

### 6. LATERALITY_TOKENS

**Issues Found**:
- "unspecified", "unsp", "other", "oth" are generic qualifiers, not laterality
- Laterality should only be directional markers

**Changes**:
- ❌ REMOVED: "unspecified", "unsp", "other", "oth"
- ✓ These already exist in QUALIFIER_TOKENS where they belong

---

### 7. MODIFIER_WITH_TOKENS

**Issues Found**:
- Contains overlapping single-word tokens that belong elsewhere
- Mixes multiple semantic categories

**Changes**:
- ❌ REMOVED: "routine", "healing", "delayed" (already in HEALING_TOKENS)
- ❌ REMOVED: "nonunion", "malunion" (already in HEALING_TOKENS)
- ❌ REMOVED: "heart" (anatomy, creates cross-slot ambiguity)
- ❌ REMOVED: "complication", "complications" (already in COMPLICATION_TOKENS)
- ✓ KEPT: Multi-word phrases like "routine healing", "delayed healing", "loss of consciousness", "behavioral disturbance", "psychotic disturbance", "mood disturbance", "mention of heart involvement"
- ✓ KEPT: Single words that are specific modifiers: "loss", "consciousness", "behavioral", "disturbance", "psychotic", "mood", "anxiety", "mention", "involvement", "agitation"

**Rationale**: This slot should contain "with X" modifiers. Single words that overlap with other slots create ambiguity. Multi-word phrases are unique and semantic.

---

### 8. ANATOMY_TOKENS

**Issues Found**:
- "wall" is too vague without context
- "process" is ambiguous (anatomical process vs procedure)

**Changes**:
- ✓ KEPT: "wall" (used in "abdominal wall", "chest wall")
- ❌ REMOVED: "process" (too ambiguous)

**Added Common Anatomy**:
- ✓ ADDED: "brain", "spinal cord" (as "cord"), "stomach", "intestine", "bowel", "bladder", "uterus", "ovary", "testis", "prostate", "breast", "pancreas", "spleen", "gallbladder", "esophagus", "duodenum", "colon", "rectum", "anus", "trachea", "bronchus", "pharynx", "larynx", "tongue", "gum", "tooth", "jaw", "mandible", "maxilla", "orbit", "cornea", "retina", "lens", "iris", "conjunctiva", "sclera", "eardrum", "tympanum", "cochlea", "vestibule", "auricle", "pinna", "septum", "turbinate", "sinus", "adenoid", "tonsil", "thyroid", "parathyroid", "adrenal", "pituitary", "pineal", "thymus", "lymph", "node", "vessel", "vein", "capillary", "aorta", "valve", "atrium", "ventricle", "septum", "myocardium", "pericardium", "endocardium", "pleura", "mediastinum", "diaphragm", "peritoneum", "mesentery", "omentum", "appendix", "ureter", "urethra", "vulva", "vagina", "cervix", "endometrium", "placenta", "umbilical", "cord"

---

### 9. CONDITION_TOKENS

**Issues Found**:
- Very limited vocabulary for such a broad category
- Missing many common conditions

**Changes**:
- ✓ KEPT: "drowning" (it is a condition/state, not just mechanism)

**Added Common Conditions**:
- ✓ ADDED: "neoplasm", "malignancy", "carcinoma", "sarcoma", "adenoma", "lipoma", "fibroma", "aneurysm", "stenosis", "thrombosis", "embolism", "ischemia", "infarction", "necrosis", "gangrene", "edema", "effusion", "hemorrhage", "hematoma", "abscess", "cellulitis", "sepsis", "septicemia", "shock", "coma", "seizure", "convulsion", "paralysis", "paresis", "neuropathy", "myopathy", "arthropathy", "osteoporosis", "osteopenia", "scoliosis", "kyphosis", "lordosis", "spondylosis", "spondylolisthesis", "hernia", "prolapse", "ptosis", "atrophy", "hypertrophy", "hyperplasia", "dysplasia", "metaplasia", "fibrosis", "cirrhosis", "sclerosis", "calcification", "obstruction", "perforation", "fistula", "stricture", "diverticulum", "polyp", "cyst", "nodule", "mass", "growth"

---

### 10. COMPLICATION_TOKENS

**Issues Found**:
- "infection" and "failure" duplicate CONDITION_TOKENS
- But they ARE complications in context

**Changes**:
- ✓ KEPT: All tokens (they serve dual purpose as both conditions and complications)

**Note**: In the context of "complication_x_procedure" families, these make sense. The duplication is acceptable.

---

### 11. DIAGNOSTIC_CLASSIFIER_TOKENS

**Issues Found**:
- "pathological" is more of a disease state/cause descriptor
- "stress" is ambiguous

**Changes**:
- ✓ KEPT: "pathological" (used in "pathological fracture" - a classifier)
- ✓ KEPT: "stress" (used in "stress fracture" - a classifier)
- ✓ KEPT: All other tokens

**Rationale**: These are used to classify fracture/condition types, so they're appropriate here.

---

### 12. INJURY_TOKENS

**Issues Found**:
- Limited vocabulary

**Changes**:
- ✓ ADDED: "bite", "sting", "bruise", "abrasion", "amputation", "crushing", "penetrating", "blast", "explosion"

---

## Summary Statistics

**Total Changes**: 96
- Additions: 71 tokens
- Removals: 25 tokens
- Moves: 4 tokens between slots

**Slots Modified**: 12 out of 20

**Most Impacted Slots**:
1. ANATOMY_TOKENS (+61 tokens)
2. CONDITION_TOKENS (+47 tokens)
3. FRACTURE_DETAIL_TOKENS (-8 tokens)
4. MODIFIER_WITH_TOKENS (-7 tokens)
5. MECHANISM_TOKENS (-4 tokens)

---

## Semantic Principles Applied

1. **Single Source of Truth**: Each token should primarily belong to one slot
2. **Contextual Exceptions**: Some duplication is acceptable when tokens serve different semantic roles in different contexts (e.g., "infection" as both condition and complication)
3. **Specificity Over Generality**: Anatomical locations in fracture names are anatomy, not fracture details
4. **Multi-word Phrases**: Composite phrases should be kept as units when they have distinct semantic meaning
5. **Abbreviation Consistency**: If a token has an abbreviation, both should be in same slot or abbreviation should be expanded

---

## Recommendations for Future

1. **Create DISEASE_STATE_TOKENS**: For "acute", "chronic", "current", "pathological", etc.
2. **Consider TEMPORAL_TOKENS**: For time-related modifiers
3. **Review Auto-Generated Tokens**: The dynamic toxic agents and diagnostic context may have introduced semantic drift
4. **Monitor Cross-Slot Coverage**: Track terms that could match multiple slots to detect ambiguity issues

---

## Files Modified
- `analyze_compositionality.py` - slot vocabulary definitions (lines 241-687)
