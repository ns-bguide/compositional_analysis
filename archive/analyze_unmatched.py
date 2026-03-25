#!/usr/bin/env python3
"""
Analyze unmatched terms to identify patterns and opportunities for coverage increase.
"""

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

def load_assignments():
    """Load assigned terms to identify unmatched."""
    assigned = set()
    with open('analysis_outputs/term_family_assignments.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            assigned.add((row['icd10cm_code'], row['term']))
    return assigned

def load_all_terms():
    """Load all terms from input."""
    all_terms = []
    with open('icd10cm_terms_2026_full_with_chv_core.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            all_terms.append((row['ICD10CMCode'], row['Term'], row.get('SourceType', '')))
    return all_terms

def analyze_patterns(unmatched):
    """Analyze patterns in unmatched terms."""

    # Word frequency
    word_freq = Counter()
    bigram_freq = Counter()
    trigram_freq = Counter()

    # Chapter distribution
    chapter_dist = Counter()
    chapter_samples = defaultdict(list)

    # Length distribution
    length_dist = Counter()

    # Common patterns
    has_comma = 0
    has_semicolon = 0
    has_parens = 0
    single_word = 0

    for code, term, source in unmatched[:100000]:  # Sample first 100k
        chapter = code[0] if code else '?'
        chapter_dist[chapter] += 1
        if len(chapter_samples[chapter]) < 10:
            chapter_samples[chapter].append(term)

        # Tokenize
        tokens = re.findall(r'\b\w+\b', term.lower())
        word_freq.update(tokens)

        length_dist[len(tokens)] += 1

        if len(tokens) == 1:
            single_word += 1

        # Bigrams
        for i in range(len(tokens) - 1):
            bigram_freq[(tokens[i], tokens[i+1])] += 1

        # Trigrams
        for i in range(len(tokens) - 2):
            trigram_freq[(tokens[i], tokens[i+1], tokens[i+2])] += 1

        # Punctuation patterns
        if ',' in term:
            has_comma += 1
        if ';' in term:
            has_semicolon += 1
        if '(' in term or ')' in term:
            has_parens += 1

    return {
        'word_freq': word_freq,
        'bigram_freq': bigram_freq,
        'trigram_freq': trigram_freq,
        'chapter_dist': chapter_dist,
        'chapter_samples': chapter_samples,
        'length_dist': length_dist,
        'has_comma': has_comma,
        'has_semicolon': has_semicolon,
        'has_parens': has_parens,
        'single_word': single_word,
        'total_sampled': min(100000, len(unmatched))
    }

def main():
    print("Loading data...")
    assigned = load_assignments()
    all_terms = load_all_terms()

    print(f"Total terms: {len(all_terms)}")
    print(f"Assigned terms: {len(assigned)}")

    # Find unmatched
    unmatched = [(code, term, source) for code, term, source in all_terms
                 if (code, term) not in assigned]

    print(f"Unmatched terms: {len(unmatched)}")
    print()

    # Analyze patterns
    print("Analyzing patterns in unmatched terms...")
    patterns = analyze_patterns(unmatched)

    # Report
    print("=" * 80)
    print("UNMATCHED TERMS ANALYSIS")
    print("=" * 80)
    print()

    print(f"Sample size: {patterns['total_sampled']:,} / {len(unmatched):,}")
    print()

    print("CHAPTER DISTRIBUTION")
    print("-" * 80)
    for chapter, count in patterns['chapter_dist'].most_common():
        pct = 100 * count / patterns['total_sampled']
        print(f"  {chapter}: {count:,} ({pct:.1f}%)")
    print()

    print("LENGTH DISTRIBUTION (words)")
    print("-" * 80)
    for length in sorted(patterns['length_dist'].keys())[:15]:
        count = patterns['length_dist'][length]
        pct = 100 * count / patterns['total_sampled']
        print(f"  {length} words: {count:,} ({pct:.1f}%)")
    print()

    print("PUNCTUATION PATTERNS")
    print("-" * 80)
    print(f"  Has comma: {patterns['has_comma']:,} ({100*patterns['has_comma']/patterns['total_sampled']:.1f}%)")
    print(f"  Has semicolon: {patterns['has_semicolon']:,} ({100*patterns['has_semicolon']/patterns['total_sampled']:.1f}%)")
    print(f"  Has parentheses: {patterns['has_parens']:,} ({100*patterns['has_parens']/patterns['total_sampled']:.1f}%)")
    print(f"  Single word: {patterns['single_word']:,} ({100*patterns['single_word']/patterns['total_sampled']:.1f}%)")
    print()

    print("TOP 50 WORDS IN UNMATCHED")
    print("-" * 80)
    for word, count in patterns['word_freq'].most_common(50):
        print(f"  {word}: {count:,}")
    print()

    print("TOP 30 BIGRAMS IN UNMATCHED")
    print("-" * 80)
    for bigram, count in patterns['bigram_freq'].most_common(30):
        print(f"  {' '.join(bigram)}: {count:,}")
    print()

    print("TOP 30 TRIGRAMS IN UNMATCHED")
    print("-" * 80)
    for trigram, count in patterns['trigram_freq'].most_common(30):
        print(f"  {' '.join(trigram)}: {count:,}")
    print()

    print("SAMPLE UNMATCHED TERMS BY CHAPTER")
    print("-" * 80)
    for chapter in sorted(patterns['chapter_samples'].keys()):
        print(f"\nChapter {chapter}:")
        for term in patterns['chapter_samples'][chapter][:5]:
            print(f"  - {term}")
    print()

if __name__ == '__main__':
    main()
