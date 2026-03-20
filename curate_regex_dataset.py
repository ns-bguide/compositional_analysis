#!/usr/bin/env python3
"""Curate a high-quality ICD-10-CM regex dataset from the enriched term file.

Filters noise, scores specificity, deduplicates per code, and evaluates quality.

Usage:
    python curate_regex_dataset.py                         # curate + evaluate
    python curate_regex_dataset.py --evaluate-only         # evaluate existing dataset
    python curate_regex_dataset.py --input other.csv       # custom input
"""

import argparse
import csv
import math
import os
import re
import sys
from collections import Counter, defaultdict
from difflib import SequenceMatcher

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

INPUT_DEFAULT = "icd10cm_terms_2026_full_with_chv_core.csv"
OUTPUT_DIR = "analysis_outputs"
OUTPUT_DATASET = "icd10cm_regex_dataset.csv"
OUTPUT_REPORT = "regex_dataset_quality_report.md"
OUTPUT_FP_RISK = "fp_risk_terms.csv"

MIN_WORD_COUNT = 2  # hard minimum
MIN_SPECIFICITY_SHORT = 3.5  # extra threshold for 2-word terms
MAX_STOPWORD_RATIO = 0.80  # terms with higher stopword fraction are dropped

# Types to always drop
DROP_TYPES = {
    "coreTermExtraction",  # bag-of-words, no word order
}

# Base types whose base form uses semicolons (not natural language)
DROP_BASE_TYPES_EXACT = {
    "umls:ICPC2ICD10ENG",
    "umls:ICPC2P",
}

# Source quality tiers (base type → tier)
TIER_MAP = {
    # Tier 1: gold standard
    "official": 1,
    "official+abbr": 1,
    # Tier 2: high-quality clinical synonyms
    "umls:SNOMEDCT_US": 2,
    "umls:MEDCIN": 2,
    "umls:CHV": 4,
    "umls:NCI": 2,
    "umls:MDR": 2,
    "umls:HPO": 2,
    "umls:MSH": 2,
    "umls:ORPHANET": 2,
    "umls:OMIM": 2,
    "chv": 4,
    # Tier 3: useful enrichments and secondary UMLS
    "enriched:C1": 3,
    "enriched:P1": 3,
    "enriched:A1": 3,
    "umls:RCD": 3,
    "umls:SNMI": 3,
    "umls:SNM": 3,
    "umls:ICD10": 3,
    "umls:ICD10AM": 3,
    "umls:ICD10CM": 3,
    "umls:ICD9CM": 3,
    "umls:MTHICD9": 3,
    "umls:MTH": 3,
    "umls:MEDLINEPLUS": 3,
    "canonical:official": 3,
}
# Everything else → Tier 4

# Max terms to keep per code per tier
TIER_LIMITS = {1: 999, 2: 5, 3: 3, 4: 2}

# Medical vocabulary tokens (combined from analyze_compositionality.py)
MEDICAL_TOKENS = {
    # Anatomy
    "head", "neck", "chest", "abdomen", "pelvis", "spine", "arm", "forearm",
    "hand", "femur", "thigh", "knee", "leg", "ankle", "foot", "toe",
    "extremity", "fascia", "nail", "wall", "hip", "thorax", "artery",
    "patella", "calcaneus", "limb", "vertebra", "thoracic", "cervical",
    "peritoneal", "finger", "thumb", "radius", "ulna", "tibia", "fibula",
    "humerus", "phalanx", "condyle", "shoulder", "wrist", "eye", "ear",
    "nose", "mouth", "throat", "lung", "heart", "liver", "kidney", "skin",
    "bone", "joint", "nerve", "muscle", "tendon",
    # Injuries
    "fracture", "dislocation", "sprain", "strain", "laceration", "contusion",
    "puncture", "wound", "burn", "corrosion", "injury", "trauma", "avulsion",
    "rupture",
    # Conditions
    "disease", "disorder", "syndrome", "infection", "inflammation", "lesion",
    "ulcer", "tumor", "cancer", "deficiency", "pain", "complication",
    "failure", "occlusion", "diabetes", "atherosclerosis", "subluxation",
    "neoplasm", "malignant", "benign", "carcinoma", "melanoma", "sarcoma",
    "lymphoma", "leukemia", "anemia", "hypertension", "hypotension",
    "tachycardia", "bradycardia", "fibrosis", "cirrhosis", "stenosis",
    "thrombosis", "embolism", "hemorrhage", "edema", "abscess", "cyst",
    "polyp", "hernia", "prolapse", "obstruction", "perforation",
    "pneumonia", "bronchitis", "asthma", "emphysema", "tuberculosis",
    "hepatitis", "pancreatitis", "colitis", "gastritis", "nephritis",
    "arthritis", "dermatitis", "encephalitis", "meningitis", "myocarditis",
    "pericarditis", "endocarditis", "osteomyelitis", "cellulitis",
    "sepsis", "septicemia",
    # Procedures / encounters
    "encounter", "initial", "subsequent", "sequela", "diagnosis",
    "screening", "examination", "aftercare", "surveillance",
    # Severity / qualifiers
    "acute", "chronic", "mild", "moderate", "severe", "bilateral",
    "unilateral", "displaced", "nondisplaced", "open", "closed",
    # Toxic / external
    "poisoning", "toxic", "adverse", "effect", "underdosing", "overdose",
    "accidental", "intentional", "assault", "collision", "traffic",
    "pedestrian", "vehicle", "motorcycle",
    # Fracture details
    "comminuted", "segmental", "transverse", "oblique", "spiral",
    "epiphysis", "physeal", "trochanteric", "subtrochanteric",
    "malunion", "nonunion",
    # Anatomy prefixes (as standalone for compound detection)
    "gastro", "hepato", "nephro", "neuro", "cardio", "pulmo", "pneumo",
    "dermato", "osteo", "arthro", "myo", "oto", "ophthalmo", "uro",
    "entero", "broncho", "laryngo", "rhino", "cervico", "thoraco",
}

ENGLISH_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "had",
    "has", "have", "he", "her", "his", "how", "i", "if", "in", "is", "it",
    "its", "my", "no", "nor", "not", "of", "on", "or", "our", "out", "own",
    "she", "so", "than", "that", "the", "their", "them", "then", "there",
    "these", "they", "this", "to", "too", "up", "us", "was", "we", "were",
    "what", "when", "where", "which", "who", "will", "with", "without",
    "you", "your",
}

# Parenthetical annotations to strip
PAREN_ANNOTATION_RE = re.compile(
    r"\s*\((disorder|diagnosis|finding|morphologic abnormality|situation|"
    r"observable entity|qualifier value|procedure|event|body structure|"
    r"substance|product|physical object|occupation|organism|"
    r"cell structure|cell|geographic location|regime/therapy)\)\s*",
    re.IGNORECASE,
)

TOKEN_RE = re.compile(r"[a-z0-9]+")

ICD_CHAPTER_BY_LETTER = {
    "A": "Infectious/Parasitic", "B": "Infectious/Parasitic",
    "C": "Neoplasms", "D": "Neoplasms/Blood",
    "E": "Endocrine/Metabolic", "F": "Mental/Behavioral",
    "G": "Nervous System", "H": "Eye/Ear",
    "I": "Circulatory", "J": "Respiratory",
    "K": "Digestive", "L": "Skin",
    "M": "Musculoskeletal", "N": "Genitourinary",
    "O": "Pregnancy", "P": "Perinatal",
    "Q": "Congenital", "R": "Symptoms/Signs",
    "S": "Injury", "T": "Injury/Poisoning",
    "U": "Reserved", "V": "External Causes",
    "W": "External Causes", "X": "External Causes",
    "Y": "External Causes", "Z": "Health Factors",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def get_base_type(type_str: str) -> str:
    """Extract the base source type, stripping enrichment suffixes like :P1, :A1."""
    # Types like 'umls:SNOMEDCT_US:P1' → base is 'umls:SNOMEDCT_US'
    # Types like 'enriched:C1' → base is 'enriched:C1' (the suffix IS the type)
    # Types like 'official+abbr' → base is 'official+abbr'
    # Types like 'umls:MEDCIN:A1' → base is 'umls:MEDCIN'
    if type_str.startswith("enriched:") or type_str.startswith("canonical:"):
        return type_str
    if type_str.startswith("chv:"):
        return "chv"
    parts = type_str.split(":")
    if len(parts) >= 3 and parts[-1] and (
        parts[-1][0] in "PAC" and (len(parts[-1]) <= 2 or parts[-1][1:].isdigit())
    ):
        return ":".join(parts[:-1])
    return type_str


def get_tier(type_str: str) -> int:
    base = get_base_type(type_str)
    return TIER_MAP.get(base, 4)


SNOMED_ARTIFACT_WORDS = {
    "disorder", "disease", "diagnosis", "finding",
    "morphologic abnormality", "situation", "observable entity",
    "qualifier value", "procedure", "event", "body structure",
    "substance", "product", "physical object", "occupation",
    "organism", "cell structure", "cell", "geographic location",
}

COMMA_SPACE_RE = re.compile(r"\s+,")


def clean_term(term: str, source_type: str = "") -> str:
    """Clean a term for regex use."""
    # Strip SNOMED/UMLS parenthetical annotations
    cleaned = PAREN_ANNOTATION_RE.sub(" ", term)
    # For P1-enriched types (parenthetical removal), strip trailing artifact words
    # These types had parentheticals stripped, leaving bare annotation words
    is_p1 = source_type.endswith(":P1") or source_type.endswith(":C1")
    if is_p1:
        words = cleaned.lower().split()
        if len(words) >= 2 and words[-1] in SNOMED_ARTIFACT_WORDS:
            cleaned = cleaned[:cleaned.lower().rfind(words[-1])].strip()
            # Check again for double artifacts like "disorder clinical disorder"
            words = cleaned.lower().split()
            if len(words) >= 2 and words[-1] in SNOMED_ARTIFACT_WORDS:
                cleaned = cleaned[:cleaned.lower().rfind(words[-1])].strip()
    else:
        # For non-P1 types, only strip if the trailing word is a duplicate
        words = cleaned.lower().split()
        if len(words) >= 2:
            trailing = words[-1]
            if trailing in SNOMED_ARTIFACT_WORDS and trailing in words[:-1]:
                cleaned = cleaned[:cleaned.lower().rfind(trailing)].strip()
    # Fix comma spacing artifacts: " ," → ","
    cleaned = COMMA_SPACE_RE.sub(",", cleaned)
    # Collapse whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def compute_medical_density(tokens: list[str]) -> float:
    if not tokens:
        return 0.0
    medical_count = sum(1 for t in tokens if t in MEDICAL_TOKENS)
    return medical_count / len(tokens)


def compute_stopword_ratio(tokens: list[str]) -> float:
    if not tokens:
        return 1.0
    stop_count = sum(1 for t in tokens if t in ENGLISH_STOPWORDS)
    return stop_count / len(tokens)


def compute_specificity_score(
    word_count: int, medical_density: float, stopword_ratio: float, tier: int
) -> float:
    """Higher = more specific = better for regex.
    
    Components:
    - length_score: log2(word_count) bounded [0, 4] — longer terms are more specific
    - medical_score: medical_density * 5 — medical tokens add specificity
    - stopword_penalty: -stopword_ratio * 3 — generic words reduce specificity
    - tier_bonus: (5 - tier) — higher-quality sources get a bonus
    """
    length_score = min(math.log2(max(word_count, 1) + 1), 4.0)
    medical_score = medical_density * 5.0
    stopword_penalty = stopword_ratio * 3.0
    tier_bonus = (5 - tier) * 1.0
    return round(length_score + medical_score - stopword_penalty + tier_bonus, 3)


def normalized_similarity(a: str, b: str) -> float:
    """Quick similarity check using token Jaccard."""
    ta = set(tokenize(a))
    tb = set(tokenize(b))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def should_drop_type(type_str: str) -> bool:
    if type_str in DROP_TYPES:
        return True
    base = get_base_type(type_str)
    if base in DROP_BASE_TYPES_EXACT:
        return True
    # Also drop derived forms of dropped base types
    for dropped in DROP_BASE_TYPES_EXACT:
        if type_str.startswith(dropped + ":"):
            return True
    return False


def get_chapter(code: str) -> str:
    if code and code[0].isalpha():
        return code[0].upper()
    return "?"


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def load_input(path: str) -> list[dict]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def curate(rows: list[dict]) -> list[dict]:
    """Filter, score, deduplicate, and select terms."""
    stats = Counter()
    stats["input_total"] = len(rows)

    # Phase 1: filter and score each term
    scored = []
    for row in rows:
        code = row["ICD10CMCode"].strip()
        raw_term = row["Term"].strip()
        type_str = row["Type"].strip()

        # Drop by type
        if should_drop_type(type_str):
            stats["dropped_type"] += 1
            continue

        # Clean term
        term = clean_term(raw_term, type_str)
        if not term:
            stats["dropped_empty"] += 1
            continue

        tokens = tokenize(term)
        word_count = len(tokens)

        # Drop too-short terms
        if word_count < MIN_WORD_COUNT:
            stats["dropped_short"] += 1
            continue

        # Compute metrics
        stopword_ratio = compute_stopword_ratio(tokens)
        if stopword_ratio > MAX_STOPWORD_RATIO:
            stats["dropped_stopword"] += 1
            continue

        medical_density = compute_medical_density(tokens)
        tier = get_tier(type_str)
        specificity = compute_specificity_score(word_count, medical_density, stopword_ratio, tier)

        # Short terms need higher specificity to be worth keeping
        if word_count <= 2 and specificity < MIN_SPECIFICITY_SHORT:
            stats["dropped_short_low_spec"] += 1
            continue

        scored.append({
            "ICD10CMCode": code,
            "Term": term,
            "SourceType": type_str,
            "SourceTier": tier,
            "SpecificityScore": specificity,
            "WordCount": word_count,
            "MedicalDensity": round(medical_density, 3),
            "StopwordRatio": round(stopword_ratio, 3),
        })

    stats["after_filter"] = len(scored)

    # Phase 2: per-code selection with dedup and reordering detection
    by_code = defaultdict(list)
    for item in scored:
        by_code[item["ICD10CMCode"]].append(item)

    selected = []
    for code, items in by_code.items():
        # Sort by tier first (lower = better), then specificity (higher = better)
        items.sort(key=lambda x: (x["SourceTier"], -x["SpecificityScore"]))

        # Find the official term for reordering detection
        official_text = ""
        for item in items:
            if item["SourceType"] == "official":
                official_text = item["Term"].lower()
                break

        kept = []
        kept_normalized = []  # track normalized forms for dedup

        for item in items:
            tier = item["SourceTier"]
            tier_count = sum(1 for k in kept if k["SourceTier"] == tier)
            limit = TIER_LIMITS.get(tier, 2)

            if tier_count >= limit:
                stats["dropped_tier_cap"] += 1
                continue

            # Dedup: skip if too similar to already-kept term for this code
            norm = item["Term"].lower().strip()
            is_dup = False
            for existing_norm in kept_normalized:
                if normalized_similarity(norm, existing_norm) > 0.85:
                    is_dup = True
                    break
            if is_dup:
                stats["dropped_dedup"] += 1
                continue

            # Reordering detection: skip non-official terms that share most tokens
            # with the official term but have very different word order
            if official_text and item["SourceType"] != "official":
                off_tokens = set(tokenize(official_text))
                cur_tokens = set(tokenize(norm))
                if off_tokens and cur_tokens:
                    jaccard = len(off_tokens & cur_tokens) / len(off_tokens | cur_tokens)
                    if jaccard > 0.75:
                        seq_ratio = SequenceMatcher(None, official_text, norm).ratio()
                        if seq_ratio < 0.60:
                            stats["dropped_reorder"] += 1
                            continue

            kept.append(item)
            kept_normalized.append(norm)

        selected.extend(kept)

    # Phase 3: ensure every code has at least one term (fallback for single-word codes)
    selected_codes = set(item["ICD10CMCode"] for item in selected)
    all_input_codes = set(row["ICD10CMCode"].strip() for row in rows)
    missing_codes = all_input_codes - selected_codes

    if missing_codes:
        # Build a lookup of best available term per missing code
        for row in rows:
            code = row["ICD10CMCode"].strip()
            if code not in missing_codes:
                continue
            raw_term = row["Term"].strip()
            type_str = row["Type"].strip()
            if should_drop_type(type_str):
                continue
            term = clean_term(raw_term, type_str)
            if not term:
                continue
            tokens = tokenize(term)
            word_count = len(tokens)
            if word_count < 1:
                continue
            medical_density = compute_medical_density(tokens)
            stopword_ratio = compute_stopword_ratio(tokens)
            tier = get_tier(type_str)
            specificity = compute_specificity_score(word_count, medical_density, stopword_ratio, tier)

            # Only take one term per missing code, prefer official
            if code in missing_codes:
                selected.append({
                    "ICD10CMCode": code,
                    "Term": term,
                    "SourceType": type_str,
                    "SourceTier": tier,
                    "SpecificityScore": specificity,
                    "WordCount": word_count,
                    "MedicalDensity": round(medical_density, 3),
                    "StopwordRatio": round(stopword_ratio, 3),
                })
                missing_codes.discard(code)
                stats["fallback_rescued"] += 1

    stats["still_missing"] = len(missing_codes)

    # Phase 4: last-resort fallback from base ICD-10-CM file for codes with no terms
    if missing_codes:
        base_path = os.path.join(os.path.dirname(os.path.abspath(rows[0].get("__source__", ""))), "icd10cm_terms_2026.csv")
        # Try common locations
        for candidate in ["icd10cm_terms_2026.csv", os.path.join(os.path.dirname(__file__), "icd10cm_terms_2026.csv")]:
            if os.path.exists(candidate):
                base_path = candidate
                break
        if os.path.exists(base_path):
            with open(base_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    code = row["ICD10CMCode"].strip()
                    if code not in missing_codes:
                        continue
                    type_str = row.get("Type", "official").strip()
                    if type_str != "official":
                        continue
                    raw_term = row["Term"].strip()
                    term = clean_term(raw_term, type_str)
                    if not term:
                        continue
                    tokens = tokenize(term)
                    word_count = len(tokens)
                    medical_density = compute_medical_density(tokens)
                    stopword_ratio = compute_stopword_ratio(tokens)
                    tier = get_tier(type_str)
                    specificity = compute_specificity_score(word_count, medical_density, stopword_ratio, tier)
                    selected.append({
                        "ICD10CMCode": code,
                        "Term": term,
                        "SourceType": "official (base file)",
                        "SourceTier": tier,
                        "SpecificityScore": specificity,
                        "WordCount": word_count,
                        "MedicalDensity": round(medical_density, 3),
                        "StopwordRatio": round(stopword_ratio, 3),
                    })
                    missing_codes.discard(code)
                    stats["base_file_rescued"] += 1

    stats["still_missing"] = len(missing_codes)

    stats["selected"] = len(selected)
    stats["codes_covered"] = len(set(item["ICD10CMCode"] for item in selected))

    return selected, stats


def write_dataset(items: list[dict], path: str):
    fieldnames = [
        "ICD10CMCode", "Term", "SourceType", "SourceTier",
        "SpecificityScore", "WordCount", "MedicalDensity", "StopwordRatio",
    ]
    items.sort(key=lambda x: (x["ICD10CMCode"], x["SourceTier"], -x["SpecificityScore"]))
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(items)


# ---------------------------------------------------------------------------
# Quality evaluation
# ---------------------------------------------------------------------------

def evaluate(items: list[dict], output_dir: str):
    """Run quality evaluation on the curated dataset."""

    total = len(items)
    codes = set(item["ICD10CMCode"] for item in items)
    num_codes = len(codes)

    # --- Per-chapter stats ---
    chapter_stats = defaultdict(lambda: {"terms": 0, "codes": set(), "scores": []})
    for item in items:
        ch = get_chapter(item["ICD10CMCode"])
        chapter_stats[ch]["terms"] += 1
        chapter_stats[ch]["codes"].add(item["ICD10CMCode"])
        chapter_stats[ch]["scores"].append(item["SpecificityScore"])

    # --- Tier distribution ---
    tier_counts = Counter(item["SourceTier"] for item in items)

    # --- Specificity distribution ---
    scores = [item["SpecificityScore"] for item in items]
    score_buckets = Counter()
    for s in scores:
        bucket = int(s)
        score_buckets[bucket] += 1

    # --- Terms per code distribution ---
    terms_per_code = Counter()
    code_term_counts = Counter(item["ICD10CMCode"] for item in items)
    for _, count in code_term_counts.items():
        terms_per_code[count] += 1

    # --- FP risk: terms with low specificity ---
    fp_risk = [item for item in items if item["SpecificityScore"] < 4.0]
    fp_risk.sort(key=lambda x: x["SpecificityScore"])

    # Write FP risk CSV
    fp_path = os.path.join(output_dir, OUTPUT_FP_RISK)
    if fp_risk:
        fieldnames = [
            "ICD10CMCode", "Term", "SourceType", "SourceTier",
            "SpecificityScore", "WordCount", "MedicalDensity", "StopwordRatio",
        ]
        with open(fp_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(fp_risk[:5000])

    # --- Variation diversity per code (sample) ---
    diversity_scores = []
    by_code = defaultdict(list)
    for item in items:
        by_code[item["ICD10CMCode"]].append(item["Term"])
    for code, terms in by_code.items():
        if len(terms) < 2:
            diversity_scores.append(1.0)
            continue
        similarities = []
        for i in range(len(terms)):
            for j in range(i + 1, min(len(terms), i + 5)):
                sim = SequenceMatcher(None, terms[i].lower(), terms[j].lower()).ratio()
                similarities.append(sim)
        avg_sim = sum(similarities) / len(similarities) if similarities else 0
        diversity_scores.append(round(1.0 - avg_sim, 3))

    avg_diversity = sum(diversity_scores) / len(diversity_scores) if diversity_scores else 0

    # --- Regex fitness sample ---
    # Pick 20 random high-specificity terms and check they wouldn't match trivially
    import random
    random.seed(42)
    high_spec = [item for item in items if item["SpecificityScore"] >= 6.0]
    sample_terms = random.sample(high_spec, min(30, len(high_spec)))

    generic_sentences = [
        "The patient went to the store to buy groceries.",
        "She walked her dog in the park yesterday afternoon.",
        "The weather forecast calls for rain this weekend.",
        "He submitted his tax return before the deadline.",
        "The company reported strong quarterly earnings growth.",
        "Students gathered in the library to study for exams.",
        "The restaurant serves excellent Italian cuisine downtown.",
        "Traffic was heavy on the highway during rush hour.",
        "They planned a vacation to visit historical landmarks.",
        "The software update fixed several known bugs.",
    ]

    regex_fp_count = 0
    regex_tests = []
    for item in sample_terms:
        # Build a simple regex: escape the term, allow flexible whitespace
        pattern_str = r"\b" + re.sub(r"\s+", r"\\s+", re.escape(item["Term"].lower())) + r"\b"
        try:
            pattern = re.compile(pattern_str, re.IGNORECASE)
            matched_generic = False
            for sent in generic_sentences:
                if pattern.search(sent):
                    matched_generic = True
                    regex_fp_count += 1
                    break
            regex_tests.append({
                "term": item["Term"],
                "code": item["ICD10CMCode"],
                "score": item["SpecificityScore"],
                "matched_generic": matched_generic,
            })
        except re.error:
            pass

    # --- Build report ---
    lines = []
    lines.append("# Regex Dataset Quality Report\n")
    lines.append(f"**Total curated terms**: {total:,}")
    lines.append(f"**ICD-10-CM codes covered**: {num_codes:,} / 74,681 ({num_codes/74681*100:.1f}%)")
    lines.append(f"**Average terms per code**: {total/num_codes:.1f}" if num_codes else "N/A")
    lines.append(f"**Average diversity score**: {avg_diversity:.3f} (1.0 = maximally diverse)\n")

    lines.append("## Tier Distribution\n")
    lines.append("| Tier | Description | Count | % |")
    lines.append("|------|------------|-------|---|")
    tier_names = {1: "Official/Abbr", 2: "Clinical Synonyms", 3: "Enrichments", 4: "Other UMLS"}
    for tier in range(1, 5):
        count = tier_counts.get(tier, 0)
        pct = count / total * 100 if total else 0
        lines.append(f"| {tier} | {tier_names.get(tier, '?')} | {count:,} | {pct:.1f}% |")

    lines.append("\n## Specificity Score Distribution\n")
    lines.append("| Score Range | Count | % |")
    lines.append("|------------|-------|---|")
    for bucket in sorted(score_buckets.keys()):
        count = score_buckets[bucket]
        pct = count / total * 100 if total else 0
        lines.append(f"| {bucket}-{bucket+1} | {count:,} | {pct:.1f}% |")

    lines.append("\n## Terms Per Code Distribution\n")
    lines.append("| Terms/Code | Codes |")
    lines.append("|-----------|-------|")
    for n in sorted(terms_per_code.keys()):
        lines.append(f"| {n} | {terms_per_code[n]:,} |")

    lines.append("\n## Chapter Coverage\n")
    lines.append("| Chapter | Name | Codes | Terms | Avg Score |")
    lines.append("|---------|------|-------|-------|-----------|")
    for ch in sorted(chapter_stats.keys()):
        s = chapter_stats[ch]
        name = ICD_CHAPTER_BY_LETTER.get(ch, "Unknown")
        avg_score = sum(s["scores"]) / len(s["scores"]) if s["scores"] else 0
        lines.append(f"| {ch} | {name} | {len(s['codes']):,} | {s['terms']:,} | {avg_score:.2f} |")

    lines.append(f"\n## FP Risk Analysis\n")
    lines.append(f"**Terms with specificity < 4.0**: {len(fp_risk):,} ({len(fp_risk)/total*100:.1f}%)")
    if fp_risk:
        lines.append(f"\nExported to `{OUTPUT_FP_RISK}` for manual review.\n")
        lines.append("### Top 20 Highest-FP-Risk Terms\n")
        lines.append("| Code | Term | Score | Words | Source |")
        lines.append("|------|------|-------|-------|--------|")
        for item in fp_risk[:20]:
            lines.append(
                f"| {item['ICD10CMCode']} | {item['Term'][:60]} | "
                f"{item['SpecificityScore']} | {item['WordCount']} | {item['SourceType']} |"
            )

    lines.append(f"\n## Regex Fitness Test (sample of {len(sample_terms)} high-specificity terms)\n")
    lines.append(f"**FP matches against generic English**: {regex_fp_count} / {len(sample_terms)}")
    if regex_fp_count > 0:
        lines.append("\nTerms that matched generic sentences:")
        for t in regex_tests:
            if t["matched_generic"]:
                lines.append(f"  - `{t['term']}` ({t['code']}, score={t['score']})")
    else:
        lines.append("\n✅ No high-specificity terms matched generic English sentences.")

    lines.append("\n## Sample High-Quality Terms\n")
    lines.append("| Code | Term | Score | Tier |")
    lines.append("|------|------|-------|------|")
    top_items = sorted(items, key=lambda x: -x["SpecificityScore"])[:30]
    for item in top_items:
        lines.append(
            f"| {item['ICD10CMCode']} | {item['Term'][:80]} | "
            f"{item['SpecificityScore']} | {item['SourceTier']} |"
        )

    report_path = os.path.join(output_dir, OUTPUT_REPORT)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return report_path, fp_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Curate ICD-10-CM regex dataset")
    parser.add_argument("--input", default=INPUT_DEFAULT, help="Input CSV path")
    parser.add_argument("--output-dir", default=OUTPUT_DIR, help="Output directory")
    parser.add_argument("--evaluate-only", action="store_true",
                        help="Only evaluate existing dataset (skip curation)")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    dataset_path = os.path.join(args.output_dir, OUTPUT_DATASET)

    if args.evaluate_only:
        if not os.path.exists(dataset_path):
            print(f"ERROR: {dataset_path} not found. Run curation first.", file=sys.stderr)
            sys.exit(1)
        print(f"Loading existing dataset from {dataset_path}...")
        items = load_input(dataset_path)
        # Convert types
        for item in items:
            item["SourceTier"] = int(item["SourceTier"])
            item["SpecificityScore"] = float(item["SpecificityScore"])
            item["WordCount"] = int(item["WordCount"])
            item["MedicalDensity"] = float(item["MedicalDensity"])
            item["StopwordRatio"] = float(item["StopwordRatio"])
    else:
        print(f"Loading input from {args.input}...")
        rows = load_input(args.input)
        print(f"  {len(rows):,} rows loaded")

        print("Curating...")
        items, stats = curate(rows)

        print(f"\n  Pipeline stats:")
        print(f"    Input rows:         {stats['input_total']:>10,}")
        print(f"    Dropped (type):     {stats.get('dropped_type', 0):>10,}")
        print(f"    Dropped (empty):    {stats.get('dropped_empty', 0):>10,}")
        print(f"    Dropped (short):    {stats.get('dropped_short', 0):>10,}")
        print(f"    Dropped (short+lo): {stats.get('dropped_short_low_spec', 0):>10,}")
        print(f"    Dropped (stopword): {stats.get('dropped_stopword', 0):>10,}")
        print(f"    After filter:       {stats['after_filter']:>10,}")
        print(f"    Dropped (tier cap): {stats.get('dropped_tier_cap', 0):>10,}")
        print(f"    Dropped (dedup):    {stats.get('dropped_dedup', 0):>10,}")
        print(f"    Dropped (reorder):  {stats.get('dropped_reorder', 0):>10,}")
        print(f"    Fallback rescued:   {stats.get('fallback_rescued', 0):>10,}")
        print(f"    Base file rescued:  {stats.get('base_file_rescued', 0):>10,}")
        print(f"    Still missing:      {stats.get('still_missing', 0):>10,}")
        print(f"    Selected:           {stats['selected']:>10,}")
        print(f"    Codes covered:      {stats['codes_covered']:>10,}")

        print(f"\nWriting dataset to {dataset_path}...")
        write_dataset(items, dataset_path)

    print(f"\nEvaluating quality...")
    report_path, fp_path = evaluate(items, args.output_dir)
    print(f"  Report: {report_path}")
    print(f"  FP risk: {fp_path}")
    print("Done.")


if __name__ == "__main__":
    main()
