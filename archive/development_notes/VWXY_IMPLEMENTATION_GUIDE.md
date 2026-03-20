# V/W/X/Y Implementation Guide

## Overview

This guide explains how to integrate the V/W/X/Y vocabulary expansion into your project.

**Files prepared:**
- ✅ `VWXY_VOCABULARY_EXPANSION.json` - Complete vocabulary and template definitions
- ✅ This guide - Step-by-step implementation

---

## Summary of Changes

### New Vocabulary: 580 tokens across 17 new slots

| Chapter | Slots | Tokens | Purpose |
|---------|-------|--------|---------|
| **V** | 5 | 150 | Transport accidents |
| **W** | 3 | 120 | Falls, contact, foreign bodies |
| **X** | 4 | 100 | Violence, fire, drowning |
| **Y** | 5 | 210 | Military, legal, places, activities, medical |

### New Template Families: 16 families

| Chapter | Families | Example |
|---------|----------|---------|
| **V** | 5 | `vehicle_type_x_occupant_role_x_collision_partner_x_traffic_context` |
| **W** | 4 | `fall_x_fall_location_x_encounter` |
| **X** | 4 | `intent_x_violence_method_x_encounter` |
| **Y** | 3 | `military_operation_x_encounter` |

---

## Option A: Automated Integration (Recommended)

### Step 1: Run the merge script

```bash
python3 << 'EOF'
import json

# Load existing family_vocabularies.json
with open("family_vocabularies.json", "r") as f:
    existing = json.load(f)

# Load VWXY expansion
with open("VWXY_VOCABULARY_EXPANSION.json", "r") as f:
    expansion = json.load(f)

# Merge slots
if "slots" not in existing:
    existing["slots"] = {}

for slot_name, tokens in expansion["slots"].items():
    if slot_name in existing["slots"]:
        print(f"⚠️  Slot '{slot_name}' already exists, merging...")
        existing["slots"][slot_name].extend(tokens)
        # Remove duplicates
        existing["slots"][slot_name] = list(set(existing["slots"][slot_name]))
    else:
        existing["slots"][slot_name] = tokens
        print(f"✓ Added new slot: {slot_name} ({len(tokens)} tokens)")

# Merge template families
if "template_families" not in existing:
    existing["template_families"] = {}

for family_name, slots in expansion["template_families"].items():
    if family_name in existing["template_families"]:
        print(f"⚠️  Family '{family_name}' already exists, skipping...")
    else:
        existing["template_families"][family_name] = slots
        print(f"✓ Added new family: {family_name}")

# Save merged version
with open("family_vocabularies.json", "w") as f:
    json.dump(existing, f, indent=2)

print("\n✓ Successfully merged VWXY vocabularies into family_vocabularies.json")
print(f"  Total slots: {len(existing['slots'])}")
print(f"  Total families: {len(existing['template_families'])}")

EOF
```

### Step 2: Validate the merged config

```bash
python analyze_compositionality.py --validate-family-config
```

### Step 3: Re-run analysis

```bash
python analyze_compositionality.py --optionals on
```

---

## Option B: Manual Integration

If you prefer manual control, follow these steps:

### Step 1: Open family_vocabularies.json

### Step 2: Add new slots to "slots" section

Copy from `VWXY_VOCABULARY_EXPANSION.json` → `slots`:
- vehicle_type
- occupant_role
- collision_partner
- traffic_context
- transport_event
- fall_location
- contact_object
- foreign_body_type
- foreign_body_location
- violence_method
- fire_context
- drowning_context
- intent (expand existing if present)
- military_operation
- legal_intervention
- place_of_occurrence
- activity_context
- medical_care_context

### Step 3: Add new families to "template_families" section

Copy all 16 families from `VWXY_VOCABULARY_EXPANSION.json` → `template_families`

### Step 4: Validate and test

```bash
python analyze_compositionality.py --validate-family-config
python analyze_compositionality.py --optionals on
```

---

## Expected Results

### Before (Current State):
```
V: 4.1% coverage (894 / 21,746 terms)
W: 2.6% coverage (97 / 3,725 terms)
X: 5.6% coverage (106 / 1,881 terms)
Y: 7.1% coverage (467 / 6,604 terms)
```

### After (Projected):
```
V: 40-50% coverage (~9,000 / 21,746 terms)  +8,100 terms
W: 35-45% coverage (~1,500 / 3,725 terms)   +1,400 terms
X: 40-50% coverage (~850 / 1,881 terms)     +750 terms
Y: 35-45% coverage (~2,500 / 6,604 terms)   +2,000 terms

Total improvement: +12,250 terms
```

### Conservative Estimates:
```
V: 30% coverage (+5,600 terms)
W: 30% coverage (+1,000 terms)
X: 30% coverage (+500 terms)
Y: 30% coverage (+1,500 terms)

Total: +8,600 terms minimum
```

---

## Vocabulary Highlights

### V Chapter (Transport)

**Most impactful tokens:**
- Vehicle types: car, bus, truck, motorcycle, bicycle, pedestrian
- Roles: driver, passenger, person outside
- Events: collision, overturning, fall from vehicle
- Context: traffic vs nontraffic

**Sample matches enabled:**
```
V469XXA | car occupant injured in collision with other nonmotor vehicle
        → vehicle_type=car, occupant_role=occupant, collision_partner=nonmotor vehicle

V0212XA | pedestrian on skateboard injured in collision with two wheeled
        → vehicle_type=skateboard, occupant_role=pedestrian, collision_partner=two wheeled
```

### W Chapter (Falls/Contact)

**Most impactful tokens:**
- Fall locations: stairs, ladder, building, pool, bathtub, bed, wheelchair
- Contact objects: machinery, sharp object, hot object, animal, firearm
- Foreign bodies: food, toy, battery, entering via natural orifice

**Sample matches enabled:**
```
W16011S | fall into swimming pool striking surface causing drowning
        → injury=fall, fall_location=swimming pool, encounter=sequela

W134XXS | fall from window
        → injury=fall, fall_location=window, encounter=sequela

W319XXA | contact with unspecified machinery
        → contact_object=machinery, encounter=initial
```

### X Chapter (Violence/Fire)

**Most impactful tokens:**
- Intent: intentional self-harm, assault, accidental
- Methods: handgun, knife, pushing, hanging, explosive
- Fire context: building fire, furniture fire, burning cigarette
- Drowning: bathtub, pool, natural water, following fall/jump

**Sample matches enabled:**
```
X811XXS | intentional self harm by jumping in front of train
        → intent=intentional self harm, violence_method=jumping, encounter=sequela

X0811XA | exposure to sofa fire caused by burning cigarette
        → fire_context=sofa fire, fire_context=burning cigarette, encounter=initial
```

### Y Chapter (Medical/Military/Place)

**Most impactful tokens:**
- Military: war operations, explosion, munitions, nuclear weapon
- Legal: law enforcement, handgun, baton, tear gas
- Places: home, school, street, factory, farm, hospital, sports facility
- Activities: work, sports, leisure, household maintenance
- Medical: surgical procedure, anesthesia, implant, contaminated, wrong dosage

**Sample matches enabled:**
```
Y36230S | war operations involving IED, military personnel
        → military_operation=war operations, military_operation=ied, encounter=sequela

Y9263   | factory as place of occurrence
        → place_of_occurrence=factory

Y638    | failure in dosage during surgical care
        → medical_care_context=failure in dosage, medical_care_context=surgical care
```

---

## Quality Assurance

### After implementation, check:

1. **Config validation passes:**
   ```bash
   python analyze_compositionality.py --validate-family-config
   ```
   Expected: No errors

2. **Coverage improves:**
   ```bash
   # Before and after comparison
   grep "V,external_causes" analysis_outputs/chapter_coverage.csv
   ```
   Expected: assigned_ratio increases from 0.04 to 0.35+

3. **No quality degradation:**
   ```bash
   python curate_regex_dataset.py
   # Check avg specificity in regex_dataset_quality_report.md
   ```
   Expected: Avg specificity remains ≥ 7.0

4. **Sample validation:**
   Review 50 newly-matched V/W/X/Y terms for sensibility

---

## Rollback Plan

If results are not satisfactory:

```bash
# Restore original
git checkout family_vocabularies.json

# Or keep backup
cp family_vocabularies.json family_vocabularies.json.backup
# ... test changes ...
mv family_vocabularies.json.backup family_vocabularies.json
```

---

## Integration Timeline

**Quick implementation**: 10 minutes
- Run automated merge script
- Validate config
- Re-run analysis (5 min wait)
- Check results

**Total**: 15-20 minutes

---

## Next Steps After Integration

1. ✅ Validate coverage improvements
2. ✅ Re-curate dataset: `python curate_regex_dataset.py`
3. ✅ Review quality metrics
4. ✅ Update Phase 1 reports with final numbers
5. 🚀 Proceed to Phase 2: Regex generation

---

## Troubleshooting

### "Unknown slot in template_families"
**Solution**: Ensure all slots are defined in the "slots" section before adding families that reference them.

### "Config validation fails"
**Solution**: Check JSON syntax, ensure all slot names match exactly (case-sensitive).

### "Coverage doesn't improve"
**Solution**: Check that:
- Analysis was re-run after config changes
- Optionals mode is ON
- family_vocabularies.json is in the correct location

### "Quality drops"
**Solution**: Some external cause terms are inherently less specific. Consider:
- Filtering by specificity threshold (≥5.0 for Phase 2)
- Adjusting tier limits in curate_regex_dataset.py

---

**Status**: Ready for integration!

Choose Option A (automated) for fastest implementation.
