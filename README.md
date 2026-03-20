# ICD-10 Family Compositional Analysis

A focused, family-only compositional analyzer for ICD-10 terms.

The project assigns each term to one best semantic family template and exports compact diagnostics for coverage and chapter behavior.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip pandas wordfreq nltk
python analyze_compositionality.py
```

Core-only baseline:

```bash
python analyze_compositionality.py --optionals off
```

## What This Repo Does

- Uses slot-based template families instead of n-grams.
- Performs exclusive assignment: one best family per term.
- Exports coverage, assignments, and chapter diagnostics.
- Keeps the CLI intentionally small.

## Input

Default input file:
- `icd10cm_terms_2026_full_with_chv_core.csv`

Required columns:
- `ICD10CMCode`
- `Term`

Optional vocabulary enrichment file:
- `medical_conditions.xml`

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip pandas wordfreq nltk
```

Note: If your environment already has these dependencies, you can skip installation.

## Run

Default run (all optional features enabled):

```bash
python analyze_compositionality.py
```

Minimal/core run (all optional features disabled):

```bash
python analyze_compositionality.py --optionals off
```

Custom paths:

```bash
python analyze_compositionality.py --input my_terms.csv --output-dir out
```

Use a custom family/vocabulary config:

```bash
python analyze_compositionality.py --family-config family_vocabularies.json
```

## CLI (Simplified)

- `--input`: input CSV path
- `--output-dir`: output directory
- `--optionals on|off`: master switch for all optional features
- `--progress-every`: progress print interval (rows)
- `--family-config`: editable JSON file for slots and template families
- `--validate-family-config`: validate config and exit

## Curating Families Outside Code

The pipeline now loads slot vocabularies and family definitions from:
- `family_vocabularies.json`

This file is intended for manual review and curation.

Structure:
- `slots`: vocabulary tokens per slot (for example `anatomy`, `injury`, `condition`)
- `slot_prefixes`: prefix vocab for prefix-aware slots
- `template_families`: family name to ordered slot list

Example:

```json
{
	"slots": {
		"anatomy": ["tibia", "fibula", "vertebra"],
		"injury": ["fracture", "laceration"]
	},
	"template_families": {
		"anatomy_x_injury_x_encounter": ["anatomy", "injury", "encounter"]
	}
}
```

Workflow:
1. Edit `family_vocabularies.json`.
2. Validate config quickly:

```bash
python analyze_compositionality.py --validate-family-config
```

3. Run analyzer.
3. Review `analysis_outputs/template_families.csv` and `analysis_outputs/term_family_assignments.csv`.
4. Repeat until families are specific and useful.

## Optionals Mode

`--optionals on` enables all optional enhancements as one bundle:
- fuzzy slot matching
- medical XML slot enrichment (if `medical_conditions.xml` exists)
- dynamic toxic agent expansion
- dynamic diagnostic context expansion
- auto-generated template families
- single-slot and isolated-term fallback families
- soft chapter-policy scoring

`--optionals off` disables all optional enhancements as one bundle:
- strict matching only
- no XML enrichment
- no dynamic expansions
- no auto-generated families
- no single-slot or isolated-term fallback families
- chapter policy disabled

## Outputs

Generated in `analysis_outputs/`:
- `template_families.csv`
- `template_instances.csv`
- `term_family_assignments.csv`
- `chapter_coverage.csv`
- `family_chapter_drift.csv`
- `auto_family_comparison_report.md`
- `summary.md`

The pipeline keeps `analysis_outputs/family_logic_guide.md` intact across runs.

## Publish Notes

Before pushing to Git:
- confirm `python analyze_compositionality.py --help` shows only the simplified CLI
- run once with `--optionals on` and once with `--optionals off`
- decide whether to commit `analysis_outputs/` artifacts or treat them as generated files
