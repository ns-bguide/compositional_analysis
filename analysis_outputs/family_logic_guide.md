# Family Logic Guide

## Scope

This guide explains the current, simplified algorithm used by `analyze_compositionality.py`.

The pipeline is family-only:
- no canonicalization stage
- no n-gram modeling
- one best family assignment per term

## Simplified CLI

The script now exposes a small interface:
- `--input`
- `--output-dir`
- `--optionals on|off`
- `--progress-every`

`--optionals` is a master switch.

## Two Execution Modes

### Optionals On (`--optionals on`)

Uses the full enhanced pipeline:
- fuzzy slot matching
- XML vocabulary enrichment from `medical_conditions.xml` (if present)
- dynamic toxic-agent vocabulary expansion
- dynamic diagnostic-context vocabulary expansion
- auto-generated family templates
- single-slot and isolated-term fallback families
- chapter-policy soft scoring

### Optionals Off (`--optionals off`)

Uses core conservative behavior:
- strict slot matching
- no XML enrichment
- no dynamic vocabulary expansions
- no auto-generated family templates
- no single-slot or isolated-term fallback families
- chapter policy disabled

## End-to-End Algorithm

1. Read input terms from CSV.
2. Tokenize each term into normalized lowercase tokens.
3. Build candidate family matches from hand-authored template families.
4. If optionals are on, augment taxonomy and families with optional builders.
5. For each candidate family, fill required slots (exact match, then fuzzy/prefix as configured).
6. Enforce whole-term fit: all non-stopword tokens must be explainable by family slots.
7. Score candidate using specificity and distinctiveness.
8. If chapter policy is active, apply chapter compatibility adjustment.
9. Rank candidates and assign exactly one best family.
10. Export tables and markdown summaries.

## Slot and Family Mechanics

- Families are ordered slot schemas, such as `slot1_x_slot2_x_slot3`.
- A family candidate is valid only if all required slots are filled.
- Whole-term fit prevents partial explanations where extra term tokens are left unmatched.
- Assignment is exclusive: only one family is chosen for each matched term.

## Distinctiveness

Distinctiveness compares domain frequency vs general-English frequency:
- domain probability from corpus document frequency
- English baseline from `wordfreq` Zipf
- score uses log-ratio (`log2(p_domain / p_english)`)

Higher distinctiveness helps rank medically informative candidates above generic ones.

## Chapter Logic

Chapter letter is extracted from `ICD10CMCode`.

- In optionals-on mode, chapter policy is `soft`.
  - candidates are not dropped
  - compatibility adjusts score
- In optionals-off mode, chapter policy is `off`.
  - no chapter adjustment is applied

Strict chapter blocking is not exposed in the simplified CLI.

## Worked Example

Example term:
- Code: `T42.4X1A`
- Term: `Poisoning by benzodiazepines, accidental (unintentional), initial encounter`

Processing flow:
1. Tokenize to tokens like `poisoning`, `benzodiazepines`, `accidental`, `initial`, `encounter`.
2. Fill slots (for example `toxic_event`, `toxic_agent`, `toxic_intent`, `encounter`).
3. Keep only families that fully explain non-stopword tokens.
4. Extract chapter `T` from code.
5. Apply chapter score adjustment only if optionals are on.
6. Rank candidates and assign top family.

## Output Files

Each run writes to `analysis_outputs/`:
- `template_families.csv`
- `template_instances.csv`
- `term_family_assignments.csv`
- `chapter_coverage.csv`
- `family_chapter_drift.csv`
- `auto_family_comparison_report.md`
- `summary.md`

`family_logic_guide.md` is intentionally preserved during output cleanup.

## Reading the Outputs

Start with:
- `summary.md` for run-level coverage and diagnostics
- `term_family_assignments.csv` for per-term decisions

Then use:
- `chapter_coverage.csv` to find weak chapters
- `family_chapter_drift.csv` to detect diffuse or chapter-pure families

## Practical Notes

- Use `--optionals on` for best coverage and richer behavior.
- Use `--optionals off` for conservative, easy-to-audit baseline behavior.
- Compare both modes to understand recall vs simplicity tradeoffs before publishing results.
