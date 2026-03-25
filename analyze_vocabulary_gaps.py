#!/usr/bin/env python3
"""
Analyze vocabulary gaps in short unmatched terms to identify high-impact additions.
"""

import csv
import re
from collections import Counter, defaultdict

def load_assigned():
    """Load assigned terms."""
    assigned = set()
    with open('analysis_outputs/term_family_assignments.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            assigned.add((row['icd10cm_code'], row['term']))
    return assigned

def load_all_terms():
    """Load all terms."""
    all_terms = []
    with open('icd10cm_terms_2026_full_with_chv_core.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            all_terms.append({
                'code': row['ICD10CMCode'],
                'term': row['Term'],
                'chapter': row['ICD10CMCode'][0] if row['ICD10CMCode'] else '?'
            })
    return all_terms

def tokenize(text):
    """Simple tokenization."""
    return re.findall(r'\b[a-z]+\b', text.lower())

def load_existing_vocabularies():
    """Load existing slot vocabularies from analyze_compositionality.py."""
    vocab = {}

    with open('analyze_compositionality.py', 'r') as f:
        content = f.read()

    # Extract token sets using regex
    pattern = r'([A-Z_]+TOKENS)\s*=\s*\{([^}]+)\}'
    matches = re.findall(pattern, content, re.DOTALL)

    for slot_name, tokens_str in matches:
        # Parse tokens from the set definition
        tokens = set()
        # Match quoted strings
        quoted = re.findall(r'"([^"]+)"', tokens_str)
        tokens.update(quoted)
        # Match single words without quotes
        unquoted = re.findall(r'\b([a-z][a-z]+)\b', tokens_str)
        tokens.update(unquoted)

        vocab[slot_name] = tokens

    return vocab

def main():
    print("Loading data...")
    assigned = load_assigned()
    all_terms = load_all_terms()
    existing_vocab = load_existing_vocabularies()

    # Get unmatched
    unmatched = [item for item in all_terms if (item['code'], item['term']) not in assigned]

    print(f"Total terms: {len(all_terms):,}")
    print(f"Assigned: {len(assigned):,}")
    print(f"Unmatched: {len(unmatched):,}")
    print()

    # Analyze SHORT unmatched terms (2-6 words) for vocabulary gaps
    short_unmatched = [item for item in unmatched if 2 <= len(tokenize(item['term'])) <= 6]

    print(f"Short unmatched (2-6 words): {len(short_unmatched):,}")
    print()

    # Find high-frequency words in short unmatched that are NOT in any vocabulary
    all_vocab_tokens = set()
    for slot_name, tokens in existing_vocab.items():
        all_vocab_tokens.update(tokens)

    # Count words in short unmatched
    word_freq = Counter()
    word_examples = defaultdict(list)

    for item in short_unmatched:
        tokens = tokenize(item['term'])
        for token in tokens:
            # Skip stopwords and very short tokens
            if len(token) <= 2:
                continue
            if token in ['and', 'or', 'of', 'to', 'in', 'for', 'with', 'the', 'from', 'are', 'has', 'can', 'was', 'not', 'had', 'but', 'been', 'have', 'than', 'that', 'this', 'its', 'at', 'by', 'on', 'as', 'an', 'be', 'is', 'it']:
                continue

            # Check if NOT in any existing vocabulary
            if token not in all_vocab_tokens:
                word_freq[token] += 1
                if len(word_examples[token]) < 3:
                    word_examples[token].append(item['term'])

    print("=" * 80)
    print("HIGH-IMPACT VOCABULARY GAPS")
    print("=" * 80)
    print()
    print("Top 100 missing words in SHORT unmatched terms (2-6 words):")
    print("These words appear frequently but are NOT in any existing slot vocabulary")
    print()

    for i, (word, count) in enumerate(word_freq.most_common(100), 1):
        print(f"{i:3d}. {word:20s} {count:5d} occurrences")
        for example in word_examples[word][:2]:
            print(f"      Example: {example[:70]}")
        print()

    # Analyze by chapter
    print("=" * 80)
    print("VOCABULARY GAPS BY CHAPTER (Short Terms)")
    print("=" * 80)
    print()

    chapter_word_freq = defaultdict(Counter)
    chapter_examples = defaultdict(lambda: defaultdict(list))

    for item in short_unmatched:
        chapter = item['chapter']
        tokens = tokenize(item['term'])
        for token in tokens:
            if len(token) <= 2:
                continue
            if token in ['and', 'or', 'of', 'to', 'in', 'for', 'with', 'the', 'from', 'are', 'has', 'can', 'was', 'not', 'had', 'but', 'been', 'have', 'than', 'that', 'this', 'its', 'at', 'by', 'on', 'as', 'an', 'be', 'is', 'it']:
                continue

            if token not in all_vocab_tokens:
                chapter_word_freq[chapter][token] += 1
                if len(chapter_examples[chapter][token]) < 2:
                    chapter_examples[chapter][token].append(item['term'])

    # Show top chapters with vocabulary gaps
    for chapter in ['H', 'I', 'E', 'A', 'L', 'M', 'C']:
        if chapter not in chapter_word_freq:
            continue

        print(f"Chapter {chapter} - Top 20 missing vocabulary:")
        for word, count in chapter_word_freq[chapter].most_common(20):
            print(f"  {word:20s} {count:4d} | {chapter_examples[chapter][word][0][:50]}")
        print()

    # Export vocabulary recommendations
    print("=" * 80)
    print("EXPORTING VOCABULARY RECOMMENDATIONS")
    print("=" * 80)

    with open('analysis_outputs/vocabulary_gap_analysis.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['word', 'frequency', 'example1', 'example2', 'example3'])

        for word, count in word_freq.most_common(200):
            examples = word_examples[word]
            row = [word, count]
            row.extend(examples[:3])
            # Pad with empty strings if fewer than 3 examples
            while len(row) < 5:
                row.append('')
            writer.writerow(row)

    print("Exported to: analysis_outputs/vocabulary_gap_analysis.csv")
    print()

if __name__ == '__main__':
    main()
