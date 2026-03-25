#!/usr/bin/env python3
"""
Analyze long unmatched terms to identify multi-slot family patterns.
"""

import csv
from collections import Counter

# Load matched term IDs
matched_ids = set()
with open("analysis_outputs/term_family_assignments.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        matched_ids.add(int(row["row_id"]))

# Analyze unmatched terms by length
length_dist = Counter()
long_terms = []

with open("icd10cm_terms_2026_full_with_chv_core.csv", "r") as f:
    reader = csv.DictReader(f)
    for idx, row in enumerate(reader, start=1):
        if idx in matched_ids:
            continue

        term = row.get("Term", "")
        word_count = len(term.split())
        length_dist[word_count] += 1

        if word_count >= 7:
            long_terms.append({
                "term": term,
                "code": row.get("ICD10CMCode", ""),
                "length": word_count
            })

print("=== UNMATCHED TERM LENGTH DISTRIBUTION ===\n")
print("Length | Count | Percentage")
print("-------|-------|------------")
total_unmatched = sum(length_dist.values())
for length in sorted(length_dist.keys(), reverse=True)[:15]:
    count = length_dist[length]
    pct = 100 * count / total_unmatched
    print(f"{length:6} | {count:5} | {pct:5.2f}%")

print(f"\nTotal unmatched: {total_unmatched:,}")
print(f"Long terms (7+ words): {len(long_terms):,} ({100*len(long_terms)/total_unmatched:.2f}%)")

# Sample long terms
print("\n=== SAMPLE LONG UNMATCHED TERMS (7+ words) ===\n")
for item in sorted(long_terms, key=lambda x: x["length"], reverse=True)[:30]:
    print(f"[{item['length']} words] {item['code']}: {item['term']}")

# Analyze by chapter
chapter_long = Counter()
for item in long_terms:
    chapter = item["code"][0] if item["code"] else "?"
    chapter_long[chapter] += 1

print("\n=== LONG TERM DISTRIBUTION BY CHAPTER ===\n")
print("Chapter | Count | % of Long")
print("--------|-------|----------")
for chapter, count in chapter_long.most_common(15):
    pct = 100 * count / len(long_terms)
    print(f"{chapter:7} | {count:5} | {pct:5.2f}%")
