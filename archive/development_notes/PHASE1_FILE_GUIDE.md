# Phase 1: File Reference Guide

## 📂 Key Files to Review

### 🎯 Start Here (Phase 1 Reports)
- **`PHASE1_BASELINE_REPORT.md`** - Comprehensive 8-section analysis
  - Executive summary, coverage analysis, quality metrics
  - Chapter-by-chapter breakdown
  - Recommendations for Phase 2

- **`PHASE1_QUICK_STATS.md`** - Visual dashboard
  - Quick metrics at a glance
  - Charts and tables
  - Action items

- **`PHASE1_SUMMARY.txt`** - Executive summary
  - One-page overview
  - Key achievements and findings

### 📊 Existing Analysis Outputs

#### High Priority - Review These
1. **`analysis_outputs/icd10cm_regex_dataset.csv`** (18 MB)
   - **THE MAIN DATASET** - 173,187 curated terms
   - Columns: Code, Term, SourceType, SourceTier, SpecificityScore, WordCount, MedicalDensity, StopwordRatio
   - Ready for regex generation

2. **`analysis_outputs/regex_dataset_quality_report.md`** (6.7 KB)
   - Quality metrics, tier distribution
   - False positive analysis
   - Sample high-quality terms
   - **ACTION**: Review FP risk section

3. **`analysis_outputs/fp_risk_terms.csv`** (273 KB)
   - 3,793 terms with specificity < 4.0
   - Sorted by risk (lowest first)
   - **ACTION**: Decide which to drop in Phase 2

4. **`analysis_outputs/chapter_coverage.csv`** (1.4 KB)
   - Per-chapter statistics
   - Identifies coverage gaps (V/W/X/Y, S)
   - **ACTION**: Use to prioritize Phase 2 work

#### Medium Priority - Reference as Needed
5. **`analysis_outputs/summary.md`** (4.2 KB)
   - Compositional analysis results
   - Family performance metrics
   - XML vocabulary ingestion stats

6. **`analysis_outputs/template_families.csv`** (20 KB)
   - All template families with coverage and scores
   - Top instances per family
   - Distinctiveness metrics

7. **`analysis_outputs/term_family_assignments.csv`** (54 MB)
   - **LARGE FILE** - Every term's family assignment
   - Includes runner-up families, chapter policy outcomes
   - Useful for debugging specific codes

#### Low Priority - Background Info
8. **`analysis_outputs/template_instances.csv`** (61 KB)
   - Individual template instances
   - Useful for understanding slot filling patterns

9. **`analysis_outputs/family_chapter_drift.csv`** (3.5 KB)
   - Family-to-chapter concentration analysis
   - Identifies diffuse vs. chapter-pure families

10. **`analysis_outputs/auto_family_comparison_report.md`** (2.1 KB)
    - Auto-generated family performance
    - Coverage gain from auto families

### 📥 Input Data
- **`icd10cm_terms_2026_full_with_chv_core.csv`** (33 MB)
  - 393,844 enriched terms (input to analysis)
  - Multiple sources: Official, UMLS, CHV, enrichments

- **`icd10cm_terms_2026.csv`** (31 MB)
  - 74,681 official ICD-10-CM terms (baseline)

- **`family_vocabularies.json`** (16 KB)
  - Slot definitions for compositional analysis
  - Template family specifications
  - Can be edited to tune matching

- **`medical_conditions.xml`**
  - External vocabulary source
  - Added 8,910 tokens to slot taxonomies

### 🔧 Scripts
- **`analyze_compositionality.py`** (2,275 lines)
  - Main compositional analyzer
  - Family-based term classification
  - Run with: `python analyze_compositionality.py --optionals on`

- **`curate_regex_dataset.py`** (793 lines)
  - Dataset curation and quality filtering
  - Specificity scoring
  - Run with: `python curate_regex_dataset.py`

---

## 🔍 Quick Lookup: What File Has...?

### "I want to see..."
- **All curated terms ready for regex** → `icd10cm_regex_dataset.csv`
- **Quality metrics and FP analysis** → `regex_dataset_quality_report.md`
- **Low-quality terms to review** → `fp_risk_terms.csv`
- **Chapter coverage gaps** → `chapter_coverage.csv`
- **How compositional analysis performed** → `summary.md`
- **Which families are effective** → `template_families.csv`
- **Specific code's family assignment** → `term_family_assignments.csv` (search by code)

### "I need to know..."
- **Average specificity score** → 7.35 (in `regex_dataset_quality_report.md`)
- **Total codes covered** → 74,681 / 74,681 (100%)
- **Total curated terms** → 173,187
- **FP risk terms** → 3,793 (2.2%)
- **Best performing chapter** → S (Injury) - 8.37 avg specificity
- **Worst coverage gap** → V (External Causes) - 4.1% compositional

---

## 📖 How to Use These Files

### For Phase 2 Planning:
1. Review `PHASE1_BASELINE_REPORT.md` sections 4-6
2. Check `fp_risk_terms.csv` to see what needs filtering
3. Look at `chapter_coverage.csv` to prioritize chapters
4. Read recommendations in `PHASE1_BASELINE_REPORT.md` section 6

### For Regex Generation (Phase 3):
1. Load `icd10cm_regex_dataset.csv` as your primary dataset
2. Filter by specificity threshold (e.g., ≥ 5.0)
3. Group by ICD10CMCode
4. Generate patterns from Term column
5. Validate using SourceTier for quality prioritization

### For Quality Analysis:
1. Start with `regex_dataset_quality_report.md`
2. Drill into `fp_risk_terms.csv` for problem terms
3. Use `term_family_assignments.csv` to trace specific codes
4. Check `template_families.csv` to understand pattern coverage

---

## 💾 File Sizes (for reference)

```
Large (>10 MB):
  54 MB  term_family_assignments.csv  ← Full assignment details
  33 MB  icd10cm_terms_2026_full...   ← Input enriched terms
  31 MB  icd10cm_terms_2026.csv       ← Official baseline
  18 MB  icd10cm_regex_dataset.csv    ← **MAIN OUTPUT**

Medium (100KB - 10MB):
 273 KB  fp_risk_terms.csv             ← Terms to review
  61 KB  template_instances.csv
  20 KB  template_families.csv

Small (<100KB):
   7 KB  PHASE1_BASELINE_REPORT.md    ← **READ THIS**
   6.7 KB regex_dataset_quality_report.md
   4.2 KB summary.md
   4 KB   PHASE1_QUICK_STATS.md       ← **AND THIS**
   3.5 KB family_chapter_drift.csv
   2.1 KB auto_family_comparison_report.md
   1.4 KB chapter_coverage.csv
```

---

## 🎓 Recommended Reading Order

**For Quick Understanding:**
1. `PHASE1_QUICK_STATS.md` (5 min)
2. `regex_dataset_quality_report.md` (10 min)
3. `chapter_coverage.csv` (5 min)

**For Deep Dive:**
1. `PHASE1_BASELINE_REPORT.md` (30 min)
2. Browse `icd10cm_regex_dataset.csv` samples (10 min)
3. Review `fp_risk_terms.csv` top 100 (15 min)
4. Skim `template_families.csv` (10 min)

**For Technical Details:**
1. `summary.md` - Compositional analysis internals
2. `term_family_assignments.csv` - Individual decisions
3. `family_logic_guide.md` - Algorithm explanation
4. `analyze_compositionality.py` - Source code

---

**Quick Tip**: Most important files for moving forward:
- ✅ `icd10cm_regex_dataset.csv` - Your main dataset
- ✅ `fp_risk_terms.csv` - What to filter
- ✅ `PHASE1_BASELINE_REPORT.md` - Next steps
