#!/usr/bin/env python3
"""
Detailed analysis of remaining unmatched terms after partial coverage implementation.
Focuses on identifying specific gaps and opportunities.
"""

import csv
import re
from collections import Counter, defaultdict

def load_assignments():
    """Load assigned terms."""
    assigned = set()
    with open('analysis_outputs/term_family_assignments.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            assigned.add((row['icd10cm_code'], row['term']))
    return assigned

def load_all_terms():
    """Load all terms."""
    all_terms = []
    with open('icd10cm_terms_2026_full_with_chv_core.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            all_terms.append({
                'code': row['ICD10CMCode'],
                'term': row['Term'],
                'source': row.get('SourceType', ''),
                'chapter': row['ICD10CMCode'][0] if row['ICD10CMCode'] else '?'
            })
    return all_terms

def tokenize_term(term):
    """Tokenize term for analysis."""
    return re.findall(r'\b\w+\b', term.lower())

def analyze_by_length_and_chapter(unmatched):
    """Analyze unmatched terms by length and chapter."""

    length_chapter = defaultdict(lambda: defaultdict(int))
    length_samples = defaultdict(list)

    for item in unmatched:
        tokens = tokenize_term(item['term'])
        length = len(tokens)
        chapter = item['chapter']

        length_chapter[length][chapter] += 1

        if len(length_samples[length]) < 5:
            length_samples[length].append({
                'term': item['term'],
                'code': item['code'],
                'chapter': chapter
            })

    return length_chapter, length_samples

def find_common_missing_patterns(unmatched, top_n=50):
    """Find common patterns in unmatched terms that might indicate missing vocabulary."""

    # Look for medical terms not captured
    medical_terms = Counter()
    abbreviations = Counter()
    anatomical_terms = Counter()

    # Specific pattern categories
    location_phrases = Counter()
    severity_modifiers = Counter()
    temporal_markers = Counter()
    diagnostic_qualifiers = Counter()

    abbreviation_pattern = re.compile(r'\b[a-z]{2,4}\b')  # Short lowercase (likely abbrev)

    for item in unmatched[:50000]:  # Sample
        term = item['term'].lower()
        tokens = tokenize_term(term)

        # Find abbreviations
        for token in tokens:
            if len(token) <= 4 and token not in ['and', 'or', 'of', 'to', 'in', 'for', 'with', 'the']:
                abbreviations[token] += 1

        # Find location phrases (preposition + anatomy)
        if 'of' in term:
            parts = term.split('of')
            if len(parts) > 1:
                after_of = parts[1].strip().split()[0] if parts[1].strip() else ''
                if after_of and len(after_of) > 2:
                    location_phrases['of ' + after_of] += 1

        # Severity/qualifier patterns
        if 'unspecified' in tokens:
            # Find what's unspecified
            idx = tokens.index('unspecified')
            if idx > 0:
                diagnostic_qualifiers[tokens[idx-1] + ' unspecified'] += 1

        # Temporal markers
        if 'subsequent' in tokens or 'initial' in tokens or 'sequela' in tokens:
            temporal_markers[' '.join([t for t in tokens if t in ['subsequent', 'initial', 'sequela', 'encounter', 'for']])] += 1

    return {
        'abbreviations': abbreviations.most_common(top_n),
        'location_phrases': location_phrases.most_common(top_n),
        'temporal_markers': temporal_markers.most_common(30),
        'diagnostic_qualifiers': diagnostic_qualifiers.most_common(30)
    }

def analyze_chapter_characteristics(unmatched):
    """Analyze what makes unmatched terms in each chapter different."""

    chapter_stats = defaultdict(lambda: {
        'count': 0,
        'avg_length': 0,
        'has_abbrev': 0,
        'has_unspecified': 0,
        'has_comma': 0,
        'samples': []
    })

    for item in unmatched:
        chapter = item['chapter']
        term = item['term']
        tokens = tokenize_term(term)

        chapter_stats[chapter]['count'] += 1
        chapter_stats[chapter]['avg_length'] += len(tokens)

        if any(len(t) <= 4 for t in tokens):
            chapter_stats[chapter]['has_abbrev'] += 1
        if 'unspecified' in term.lower():
            chapter_stats[chapter]['has_unspecified'] += 1
        if ',' in term:
            chapter_stats[chapter]['has_comma'] += 1

        if len(chapter_stats[chapter]['samples']) < 10:
            chapter_stats[chapter]['samples'].append(term)

    # Calculate averages
    for chapter in chapter_stats:
        stats = chapter_stats[chapter]
        if stats['count'] > 0:
            stats['avg_length'] /= stats['count']
            stats['abbrev_pct'] = 100 * stats['has_abbrev'] / stats['count']
            stats['unspec_pct'] = 100 * stats['has_unspecified'] / stats['count']
            stats['comma_pct'] = 100 * stats['has_comma'] / stats['count']

    return chapter_stats

def main():
    print("Loading data...")
    assigned = load_assignments()
    all_terms = load_all_terms()

    print(f"Total terms: {len(all_terms):,}")
    print(f"Assigned terms: {len(assigned):,}")

    unmatched = [item for item in all_terms if (item['code'], item['term']) not in assigned]

    print(f"Unmatched terms: {len(unmatched):,}")
    print()

    # Length and chapter analysis
    print("=" * 80)
    print("LENGTH x CHAPTER DISTRIBUTION")
    print("=" * 80)
    print()

    length_chapter, length_samples = analyze_by_length_and_chapter(unmatched)

    # Show key length brackets
    print("Key length brackets:")
    print()

    length_brackets = [
        (1, 3, "Short (1-3 words)"),
        (4, 6, "Medium (4-6 words)"),
        (7, 12, "Long (7-12 words)"),
        (13, 100, "Very long (13+ words)")
    ]

    for min_len, max_len, label in length_brackets:
        total = sum(
            length_chapter[length][chapter]
            for length in range(min_len, max_len + 1)
            for chapter in length_chapter[length]
        )
        print(f"{label}: {total:,} terms")

        # Top chapters for this bracket
        chapter_counts = defaultdict(int)
        for length in range(min_len, max_len + 1):
            for chapter, count in length_chapter[length].items():
                chapter_counts[chapter] += count

        print("  Top chapters:")
        for chapter, count in sorted(chapter_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            pct = 100 * count / total if total > 0 else 0
            print(f"    {chapter}: {count:,} ({pct:.1f}%)")
        print()

    # Word length distribution detail
    print("=" * 80)
    print("WORD LENGTH DISTRIBUTION (detailed)")
    print("=" * 80)
    print()

    for length in sorted(length_chapter.keys())[:20]:
        total = sum(length_chapter[length].values())
        pct = 100 * total / len(unmatched)
        print(f"{length} words: {total:,} ({pct:.1f}%)")

        # Show top chapters for this length
        top_chapters = sorted(length_chapter[length].items(), key=lambda x: x[1], reverse=True)[:3]
        chapter_str = ", ".join([f"{ch}:{cnt}" for ch, cnt in top_chapters])
        print(f"  Top: {chapter_str}")

        # Show sample
        if length in length_samples and length_samples[length]:
            sample = length_samples[length][0]['term']
            if len(sample) > 70:
                sample = sample[:67] + "..."
            print(f"  Sample: {sample}")
        print()

    # Missing pattern analysis
    print("=" * 80)
    print("POTENTIAL VOCABULARY GAPS")
    print("=" * 80)
    print()

    patterns = find_common_missing_patterns(unmatched)

    print("TOP ABBREVIATIONS IN UNMATCHED:")
    print("-" * 80)
    for abbrev, count in patterns['abbreviations'][:30]:
        print(f"  {abbrev}: {count:,}")
    print()

    print("TOP LOCATION PHRASES:")
    print("-" * 80)
    for phrase, count in patterns['location_phrases'][:30]:
        print(f"  {phrase}: {count:,}")
    print()

    print("TEMPORAL MARKERS:")
    print("-" * 80)
    for marker, count in patterns['temporal_markers']:
        print(f"  {marker}: {count:,}")
    print()

    # Chapter characteristics
    print("=" * 80)
    print("CHAPTER CHARACTERISTICS (Unmatched)")
    print("=" * 80)
    print()

    chapter_stats = analyze_chapter_characteristics(unmatched)

    for chapter in sorted(chapter_stats.keys()):
        stats = chapter_stats[chapter]
        if stats['count'] < 100:  # Skip small chapters
            continue

        print(f"Chapter {chapter}: {stats['count']:,} terms")
        print(f"  Avg length: {stats['avg_length']:.1f} words")
        print(f"  Has abbreviations: {stats['abbrev_pct']:.1f}%")
        print(f"  Has 'unspecified': {stats['unspec_pct']:.1f}%")
        print(f"  Has commas: {stats['comma_pct']:.1f}%")
        print(f"  Samples:")
        for term in stats['samples'][:3]:
            if len(term) > 70:
                term = term[:67] + "..."
            print(f"    - {term}")
        print()

    # Export top unmatched by chapter for manual review
    print("=" * 80)
    print("EXPORTING SAMPLES FOR REVIEW")
    print("=" * 80)

    with open('analysis_outputs/unmatched_samples_by_chapter.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['chapter', 'code', 'term', 'word_count'])

        # Export 100 samples per major chapter
        chapter_samples = defaultdict(list)
        for item in unmatched:
            chapter = item['chapter']
            if len(chapter_samples[chapter]) < 100:
                tokens = tokenize_term(item['term'])
                chapter_samples[chapter].append([
                    chapter,
                    item['code'],
                    item['term'],
                    len(tokens)
                ])

        for chapter in sorted(chapter_samples.keys()):
            for row in chapter_samples[chapter]:
                writer.writerow(row)

    print("Exported to: analysis_outputs/unmatched_samples_by_chapter.csv")
    print()

if __name__ == '__main__':
    main()
