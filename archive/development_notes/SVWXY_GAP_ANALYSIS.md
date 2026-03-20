# S/V/W/X/Y Chapter Gap Analysis

## Executive Summary

**Problem**: Injury and external cause chapters have severe coverage gaps:
- **S (Injury)**: 79% unmatched (99,541 / 125,904 terms)
- **V (Transport)**: 96% unmatched (20,852 / 21,746 terms)
- **W (Falls/Contact)**: 97% unmatched (3,628 / 3,725 terms)
- **X (Fire/Assault)**: 94% unmatched (1,775 / 1,881 terms)
- **Y (Medical/Military)**: 93% unmatched (6,137 / 6,604 terms)

**Root Causes Identified**:
1. Heavy abbreviation usage in S chapter
2. Missing transport/vehicle vocabulary (V)
3. Missing place/location vocabulary (all)
4. Missing intent vocabulary (X, Y)
5. Missing activity/context vocabulary (all)
6. Template families don't match external cause patterns

---

## Detailed Analysis by Chapter

### S Chapter (Injury) - 79% Unmatched

**Issue**: Heavily abbreviated terms that are variations of matched terms

**Sample patterns:**
```
S62514K  | prox phalanx r thm subs fx w nonunion nondisp fx
S52221N  | r ulna 7thn displ transverse fx shaft
S32002D  | unstbl lum vertebra
S1080XD  | unsp superficial injury of oth part of neck, subs encntr
```

**Missing elements:**
- **Abbreviations**: "prox" (proximal), "r" (right), "thm" (thumb), "subs" (subsequent), "fx" (fracture), "w" (with), "nondisp" (nondisplaced), "lum" (lumbar), "unsp" (unspecified), "oth" (other), "encntr" (encounter)
- **Encounter codes**: "7thn", "7thd", "init", "subs", "sqla"
- **Anatomy abbreviations**: "mc bone" (metacarpal), "phalanx", "brainstem"
- **Compound descriptions**: Multiple modifiers combined

**Current family coverage** (what IS matching):
- 4,642 terms → `auto_anatomy_x_condition_x_encounter`
- 3,927 terms → `anatomy_x_injury_x_fracture_detail_x_healing_x_encounter`
- 3,765 terms → `anatomy_x_injury_x_fracture_detail_x_encounter`

**Why these work**: They match non-abbreviated, full-text terms

**Solution approach**:
1. ✅ **Expand abbreviation map** in `ABBREVIATION_TOKEN_MAP`
2. ✅ **Add compound anatomy terms** (phalanx, epicondyle, etc.)
3. ✅ **Match by similarity** to already-curated terms (fuzzy matching)
4. Consider: These abbreviated terms may be low-quality for regex anyway

---

### V Chapter (Transport) - 96% Unmatched

**Issue**: External cause codes for transport accidents - completely different vocabulary domain

**Sample patterns:**
```
V469XXA  | car occupant injured in collision with other nonmotor vehicle
V9219XA  | drowning & submersion due to being thrown overboard by motion of unspecified
V740XXS  | bus injured collision heavy transport vehicle bus nontraffic accident
V0212XA  | pedestrian on skateboard injured in collision with two or three wheeled
V3909XA  | driver of 3 whl mv injured in clsn w oth mv nontraf, init
```

**Missing vocabulary categories:**

#### 1. Vehicle Types
- **Land**: car, bus, pickup truck, van, heavy transport vehicle, motorcycle, skateboard, three-wheeled motor vehicle, pedal cycle, railway train
- **Water**: merchant ship, watercraft
- **Air**: hang-glider, aircraft
- **Non-motor**: skateboard, pedal cycle, animal-drawn vehicle

#### 2. Occupant Roles
- driver, passenger, person boarding/alighting, person outside vehicle, occupant (unspecified)

#### 3. Collision Partners
- pedestrian, animal, two-wheeled vehicle, three-wheeled vehicle, car, pickup truck, heavy transport, bus, railway, fixed/stationary object

#### 4. Traffic Context
- traffic (on public highway), nontraffic (not on public highway)

#### 5. Event Types
- collision, noncollision (overturning, loss of control, explosion)

**Current families** (barely working):
- 644 terms → `mechanism_x_anatomy_x_injury_x_encounter`
- 216 terms → `mechanism_x_injury_x_encounter`

**Why coverage is so low**: Current `MECHANISM_TOKENS` only has ~25 tokens. Need 100+ tokens.

**Solution approach**:
1. ✅ **Add transport slot vocabulary** (vehicle_type, occupant_role, collision_partner)
2. ✅ **Create V-chapter-specific families**:
   - `vehicle_type_x_occupant_role_x_collision_partner_x_traffic_context`
   - `vehicle_type_x_event_type_x_encounter`
3. ✅ **Expand mechanism tokens** dramatically

---

### W Chapter (Falls/Contact) - 97% Unmatched

**Issue**: Environmental and object contact - different vocabulary than medical conditions

**Sample patterns:**
```
W16011S  | fall into swimming pool strk surfc causing drown, sequela
W134XXS  | fall from, out of or through window, sequela
W319XXA  | contact with unspecified machinery, initial encounter
W44G9XA  | organic via orifice
W275XXA  | contact with papercutter, initial encounter
```

**Missing vocabulary categories:**

#### 1. Fall Locations
- swimming pool, window, building, stairs, steps, wheelchair, cliff, high altitude, scaffolding, ladder

#### 2. Contact Objects
- machinery, power take-off devices, papercutter, sports equipment, bicycle tire, furniture, glass

#### 3. Entry Objects (foreign body)
- toy, plastic toy, organic object, sharp object, entering via natural orifice

#### 4. Animals
- pig, dog, horse, venomous (in other chapters)

#### 5. Environmental
- high altitude, heat, cold, fire, explosion

**Current families**: Almost nothing matches - mostly auto-generated fallbacks

**Solution approach**:
1. ✅ **Add fall_location slot** (pool, window, building, stairs, etc.)
2. ✅ **Add contact_object slot** (machinery, tools, equipment)
3. ✅ **Add foreign_body slot** (objects entering orifices)
4. ✅ **Create W-chapter families**:
   - `fall_x_fall_location_x_encounter`
   - `contact_x_contact_object_x_encounter`
   - `foreign_body_x_foreign_body_location_x_encounter`

---

### X Chapter (Fire/Assault/Self-harm) - 94% Unmatched

**Issue**: Intent-based codes - assault vs self-harm vs accidental

**Sample patterns:**
```
X811XXS  | self-harm by jumping or lying in front of train, sequela
X962XXA  | assault letter bomb
X710XXD  | intentional self harm by drown while in bathtub, subs
X0811XA  | exposure to sofa fire caused by burning cigarette, initial encounter
X922XXA  | push swimming pool
```

**Missing vocabulary categories:**

#### 1. Intent
- intentional self-harm, assault, accidental (already have in toxic_intent but needs expansion)

#### 2. Methods (Violence)
- jumping in front of train, sword, dagger, letter bomb, pushing, crashing aircraft, handgun, rifle

#### 3. Fire Context
- burning cigarette, sofa fire, furniture fire, controlled fire, uncontrolled fire, building fire

#### 4. Drowning Context
- bathtub, swimming pool, natural water, after jump

#### 5. Explosion
- letter bomb, IED, mine, grenade

**Current families**: Minimal matches, wrong context (toxic families, not violence)

**Solution approach**:
1. ✅ **Expand intent vocabulary** (assault, self-harm vs toxic intent)
2. ✅ **Add violence_method slot** (weapon, action)
3. ✅ **Add fire_context slot** (fire location, ignition source)
4. ✅ **Create X-chapter families**:
   - `intent_x_violence_method_x_encounter`
   - `fire_context_x_fire_location_x_encounter`
   - `intent_x_drowning_context_x_encounter`

---

### Y Chapter (Medical/Military/Place) - 93% Unmatched

**Issue**: Heterogeneous codes - medical devices, war operations, place of occurrence

**Sample patterns:**
```
Y909     | evidence of alcohol involvement determined by presence of alcohol in blood
Y36230S  | improvised explosive device ied military personnel sequela war operations
Y638     | failure in dosage during other surgical & medical care
Y37141S  | aircraft accidental detonation onboard munitions explosives civilian sequela
Y9263    | factory as the place of occurrence of the external cause
```

**Missing vocabulary categories:**

#### 1. Military Operations
- war operations, military personnel, civilian, IED, guided missile, nuclear weapon, aerial bomb, munitions, explosives

#### 2. Legal Intervention
- legal intervention, handgun, baton, tear gas, law enforcement

#### 3. Medical Care Context
- failure in dosage, overdose, contaminated substance, monitoring device, surgical care, therapy

#### 4. Place of Occurrence
- factory, home, school, street, sports facility, industrial place, farm, trade area

#### 5. Activity
- sports, leisure, work, household maintenance

**Current families**: Scattered matches across toxic and diagnostic families

**Solution approach**:
1. ✅ **Add military_operation slot** (war, legal intervention)
2. ✅ **Add place_of_occurrence slot** (locations)
3. ✅ **Add activity_context slot** (what was being done)
4. ✅ **Add medical_device/care_context slot**
5. ✅ **Create Y-chapter families**:
   - `military_operation_x_weapon_x_personnel_type`
   - `place_of_occurrence_x_activity_context`
   - `medical_care_context_x_complication_type`

---

## Proposed Solution: 3-Phase Approach

### Phase 1A: Quick Wins (S Chapter) - 1-2 hours

**Goal**: Improve S chapter from 21% to 50%+ coverage

**Actions**:
1. ✅ **Expand abbreviation map** - Add 50+ medical abbreviations
2. ✅ **Add compound anatomy terms** - phalanx, epicondyle, etc.
3. ✅ **Relax matching** - Allow more fuzzy matches for S chapter
4. ✅ **Test**: Re-run compositional analysis

**Expected gain**: +30% coverage (30K→60K matched terms)

**Files to modify**:
- `analyze_compositionality.py`: Expand `ABBREVIATION_TOKEN_MAP`
- `family_vocabularies.json`: Add anatomy terms

---

### Phase 1B: External Cause Vocabulary (V/W/X/Y) - 4-6 hours

**Goal**: Build complete external cause vocabulary and families

**Actions**:
1. ✅ **Create new slot taxonomies** (15 new slots):
   - Transport: `vehicle_type`, `occupant_role`, `collision_partner`, `traffic_context`
   - Falls: `fall_location`, `contact_object`, `foreign_body`
   - Violence: `violence_method`, `fire_context`, `drowning_context`
   - Context: `military_operation`, `place_of_occurrence`, `activity_context`, `medical_care_context`

2. ✅ **Populate vocabularies** (500+ tokens total):
   - Extract from sample unmatched terms
   - Reference ICD-10-CM documentation
   - Use systematic enumeration (all vehicle types, all places, etc.)

3. ✅ **Create template families** (12 new families):
   ```python
   # V chapter
   "vehicle_type_x_occupant_role_x_collision_partner_x_encounter"
   "vehicle_type_x_event_type_x_encounter"

   # W chapter
   "fall_x_fall_location_x_encounter"
   "contact_x_contact_object_x_encounter"
   "foreign_body_x_body_location_x_encounter"

   # X chapter
   "intent_x_violence_method_x_encounter"
   "fire_context_x_fire_location_x_encounter"

   # Y chapter
   "military_operation_x_weapon_x_personnel_type"
   "place_of_occurrence_x_activity_context"
   "medical_care_context_x_complication"
   ```

4. ✅ **Add to family_vocabularies.json**

5. ✅ **Test**: Re-run analysis

**Expected gain**: V/W/X/Y coverage from 2-7% to 40-60%

**Files to modify**:
- `family_vocabularies.json`: Add all new slots and families
- Optionally `analyze_compositionality.py`: Add chapter-specific logic

---

### Phase 1C: Validation & Quality Check - 2 hours

**Goal**: Ensure new vocabularies don't increase false positives

**Actions**:
1. ✅ **Re-run curation**: `python curate_regex_dataset.py`
2. ✅ **Check specificity scores** for new terms
3. ✅ **Review FP risk** - Should still be <5%
4. ✅ **Sample validation** - Test 50 new patterns
5. ✅ **Adjust thresholds** if needed

**Success criteria**:
- Coverage improvement: S: 50%+, V/W/X/Y: 40%+
- Quality maintained: Avg specificity ≥ 6.5
- FP risk: < 5% of new terms

---

## Implementation Priority

### IMMEDIATE (Today)
1. ✅ **Expand abbreviation map** (30 min)
   - Add top 50 medical abbreviations
   - Focus on S chapter patterns

2. ✅ **Add compound anatomy** (30 min)
   - phalanx, epicondyle, epiphysis, etc.
   - 20-30 terms

3. ✅ **Test S chapter improvement** (10 min)
   - Re-run analysis
   - Check coverage gain

### HIGH PRIORITY (This week)
4. ✅ **Build transport vocabulary** (2 hours)
   - V chapter: vehicles, occupants, collision types
   - Create 4 new template families
   - Expected: 40%+ V chapter coverage

5. ✅ **Build falls/contact vocabulary** (1 hour)
   - W chapter: fall locations, contact objects
   - Create 3 new template families
   - Expected: 40%+ W chapter coverage

6. ✅ **Build violence/intent vocabulary** (1 hour)
   - X chapter: intent, methods, fire context
   - Create 3 new template families
   - Expected: 40%+ X chapter coverage

7. ✅ **Build Y chapter vocabulary** (1 hour)
   - Military, legal, place, medical care
   - Create 3 new template families
   - Expected: 40%+ Y chapter coverage

### VALIDATION
8. ✅ **Quality check** (2 hours)
   - Re-curate dataset
   - Check FP risk
   - Validate samples

---

## Resource Requirements

**Time**: 8-10 hours total (can be done in 2 days)
**Files**: Modify 1-2 files (`family_vocabularies.json` mainly)
**Risk**: Low - additive changes only, no breaking changes
**Impact**: Potentially +100K terms covered (from 173K to 270K+)

---

## Expected Outcomes

### Before (Current):
```
S: 21% coverage (33K matched)
V:  4% coverage (0.9K matched)
W:  3% coverage (0.1K matched)
X:  6% coverage (0.1K matched)
Y:  7% coverage (0.5K matched)
```

### After (Target):
```
S: 50%+ coverage (60K+ matched)
V: 40%+ coverage (8K+ matched)
W: 40%+ coverage (1.5K+ matched)
X: 40%+ coverage (0.8K+ matched)
Y: 40%+ coverage (2.6K+ matched)
```

**Total improvement**: +40K terms matched (+23% overall)

---

## Next Steps

**Ready to implement?** Start with Phase 1A (S chapter abbreviations) - quickest win!

Choose your approach:
1. **Quick fix**: Just do S chapter (1-2 hours)
2. **Comprehensive**: All chapters (8-10 hours)
3. **Phased**: Do S today, V/W/X/Y tomorrow

Which would you like to tackle first?
