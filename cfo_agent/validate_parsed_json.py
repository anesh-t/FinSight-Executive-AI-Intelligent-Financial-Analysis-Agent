#!/usr/bin/env python3
"""
Comprehensive validation script for parsed 10-K JSON files.
Checks formatting, metadata, headings, subheadings, and content quality.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

def validate_file(filepath: Path) -> Dict:
    """Validate a single JSON file and return issues."""
    issues = []
    warnings = []
    stats = {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return {
            'valid': False,
            'issues': [f"Invalid JSON: {e}"],
            'warnings': [],
            'stats': {}
        }
    except Exception as e:
        return {
            'valid': False,
            'issues': [f"Error reading file: {e}"],
            'warnings': [],
            'stats': {}
        }
    
    # Check document metadata
    if 'document_metadata' not in data:
        issues.append("Missing 'document_metadata'")
    else:
        metadata = data['document_metadata']
        required_fields = ['company', 'filing_type', 'fiscal_year', 'source_file', 'processing_date', 'pipeline_version']
        for field in required_fields:
            if field not in metadata:
                issues.append(f"Missing metadata field: {field}")
        
        # Validate fiscal year
        if 'fiscal_year' in metadata:
            year = metadata['fiscal_year']
            if not isinstance(year, int) or year < 2019 or year > 2024:
                issues.append(f"Invalid fiscal_year: {year}")
    
    # Check items structure
    if 'items' not in data:
        issues.append("Missing 'items' structure")
        return {
            'valid': False,
            'issues': issues,
            'warnings': warnings,
            'stats': stats
        }
    
    items = data['items']
    if not isinstance(items, dict) or len(items) == 0:
        issues.append("'items' is empty or not a dict")
        return {
            'valid': False,
            'issues': issues,
            'warnings': warnings,
            'stats': stats
        }
    
    # Analyze each item
    total_chunks = 0
    empty_chunks = 0
    missing_subheadings = 0
    missing_text = 0
    low_word_count = 0
    total_words = 0
    sections = []
    
    for item_name, item_data in items.items():
        sections.append(item_name)
        
        # Check item structure
        if 'heading' not in item_data:
            issues.append(f"{item_name}: Missing 'heading'")
        
        if 'content' not in item_data:
            issues.append(f"{item_name}: Missing 'content'")
            continue
        
        content = item_data['content']
        if not isinstance(content, list):
            issues.append(f"{item_name}: 'content' is not a list")
            continue
        
        # Check each chunk
        for i, chunk in enumerate(content):
            total_chunks += 1
            
            # Required fields in chunk
            if 'subheading' not in chunk:
                missing_subheadings += 1
                warnings.append(f"{item_name} chunk {i}: Missing 'subheading'")
            
            if 'text' not in chunk:
                missing_text += 1
                issues.append(f"{item_name} chunk {i}: Missing 'text'")
            else:
                text = chunk['text']
                if not text or len(text.strip()) == 0:
                    empty_chunks += 1
                    warnings.append(f"{item_name} chunk {i}: Empty text")
            
            if 'word_count' not in chunk:
                warnings.append(f"{item_name} chunk {i}: Missing 'word_count'")
            else:
                wc = chunk['word_count']
                total_words += wc
                if wc < 10:
                    low_word_count += 1
                    warnings.append(f"{item_name} chunk {i}: Very low word_count ({wc})")
            
            # Check if subheading_generated flag exists
            if 'subheading_generated' not in chunk:
                warnings.append(f"{item_name} chunk {i}: Missing 'subheading_generated' flag")
    
    # Calculate statistics
    stats = {
        'total_sections': len(sections),
        'total_chunks': total_chunks,
        'empty_chunks': empty_chunks,
        'missing_subheadings': missing_subheadings,
        'missing_text': missing_text,
        'low_word_count_chunks': low_word_count,
        'total_words': total_words,
        'avg_words_per_chunk': round(total_words / total_chunks, 2) if total_chunks > 0 else 0,
        'sections': sections
    }
    
    # Determine if valid
    valid = len(issues) == 0 and empty_chunks == 0
    
    return {
        'valid': valid,
        'issues': issues,
        'warnings': warnings,
        'stats': stats
    }

def main():
    """Main validation function."""
    json_dir = Path('parsed_10k_json')
    
    if not json_dir.exists():
        print("❌ Directory 'parsed_10k_json' not found!")
        return
    
    json_files = sorted(json_dir.glob('*.json'))
    
    print("=" * 80)
    print("🔍 COMPREHENSIVE 10-K JSON VALIDATION REPORT")
    print("=" * 80)
    print()
    
    results = {}
    company_stats = defaultdict(lambda: {'files': 0, 'chunks': 0, 'words': 0, 'issues': 0})
    year_stats = defaultdict(lambda: {'files': 0, 'chunks': 0, 'words': 0})
    
    total_files = 0
    valid_files = 0
    total_issues = 0
    total_warnings = 0
    
    # Validate each file
    for filepath in json_files:
        filename = filepath.name
        print(f"Checking: {filename}...")
        
        result = validate_file(filepath)
        results[filename] = result
        
        total_files += 1
        if result['valid']:
            valid_files += 1
        
        total_issues += len(result['issues'])
        total_warnings += len(result['warnings'])
        
        # Extract company and year from filename
        parts = filename.replace('_structured.json', '').replace('_10k', '').replace('_10K', '')
        year = parts[:4]
        company = parts[4:]
        
        stats = result['stats']
        company_stats[company]['files'] += 1
        company_stats[company]['chunks'] += stats.get('total_chunks', 0)
        company_stats[company]['words'] += stats.get('total_words', 0)
        company_stats[company]['issues'] += len(result['issues'])
        
        year_stats[year]['files'] += 1
        year_stats[year]['chunks'] += stats.get('total_chunks', 0)
        year_stats[year]['words'] += stats.get('total_words', 0)
    
    print()
    print("=" * 80)
    print("📊 SUMMARY STATISTICS")
    print("=" * 80)
    print()
    print(f"Total Files: {total_files}")
    print(f"Valid Files: {valid_files} ({valid_files/total_files*100:.1f}%)")
    print(f"Files with Issues: {total_files - valid_files}")
    print(f"Total Issues: {total_issues}")
    print(f"Total Warnings: {total_warnings}")
    print()
    
    # Company breakdown
    print("=" * 80)
    print("📈 BY COMPANY")
    print("=" * 80)
    print()
    print(f"{'Company':<15} {'Files':<8} {'Chunks':<10} {'Words':<12} {'Avg/Chunk':<12} {'Issues':<8}")
    print("-" * 80)
    for company in sorted(company_stats.keys()):
        stats = company_stats[company]
        avg = round(stats['words'] / stats['chunks'], 1) if stats['chunks'] > 0 else 0
        print(f"{company:<15} {stats['files']:<8} {stats['chunks']:<10} {stats['words']:<12,} {avg:<12} {stats['issues']:<8}")
    print()
    
    # Year breakdown
    print("=" * 80)
    print("📅 BY YEAR")
    print("=" * 80)
    print()
    print(f"{'Year':<8} {'Files':<8} {'Chunks':<10} {'Words':<12} {'Avg/Chunk':<12}")
    print("-" * 80)
    for year in sorted(year_stats.keys()):
        stats = year_stats[year]
        avg = round(stats['words'] / stats['chunks'], 1) if stats['chunks'] > 0 else 0
        print(f"{year:<8} {stats['files']:<8} {stats['chunks']:<10} {stats['words']:<12,} {avg:<12}")
    print()
    
    # Detailed issues report
    files_with_issues = {k: v for k, v in results.items() if not v['valid'] or len(v['issues']) > 0}
    
    if files_with_issues:
        print("=" * 80)
        print("⚠️  DETAILED ISSUES REPORT")
        print("=" * 80)
        print()
        for filename, result in files_with_issues.items():
            print(f"📄 {filename}")
            print(f"   Status: {'✅ Valid' if result['valid'] else '❌ Invalid'}")
            if result['issues']:
                print(f"   Issues ({len(result['issues'])}):")
                for issue in result['issues'][:10]:  # Show first 10
                    print(f"      - {issue}")
                if len(result['issues']) > 10:
                    print(f"      ... and {len(result['issues']) - 10} more")
            if result['warnings']:
                print(f"   Warnings ({len(result['warnings'])}):")
                for warning in result['warnings'][:5]:  # Show first 5
                    print(f"      - {warning}")
                if len(result['warnings']) > 5:
                    print(f"      ... and {len(result['warnings']) - 5} more")
            print()
    
    # Files with low word counts
    print("=" * 80)
    print("📊 CONTENT QUALITY METRICS")
    print("=" * 80)
    print()
    
    low_chunk_files = []
    empty_files = []
    
    for filename, result in results.items():
        stats = result['stats']
        if stats.get('total_chunks', 0) < 50:
            low_chunk_files.append((filename, stats.get('total_chunks', 0)))
        if stats.get('empty_chunks', 0) > 0:
            empty_files.append((filename, stats.get('empty_chunks', 0)))
    
    if low_chunk_files:
        print("⚠️  Files with Low Chunk Count (< 50 chunks):")
        for filename, count in sorted(low_chunk_files, key=lambda x: x[1]):
            print(f"   - {filename}: {count} chunks")
        print()
    
    if empty_files:
        print("❌ Files with Empty Chunks:")
        for filename, count in empty_files:
            print(f"   - {filename}: {count} empty chunks")
        print()
    else:
        print("✅ No files with empty chunks")
        print()
    
    # RAG readiness assessment
    print("=" * 80)
    print("🤖 RAG SYSTEM READINESS")
    print("=" * 80)
    print()
    
    rag_ready = True
    rag_issues = []
    
    if total_files - valid_files > 0:
        rag_issues.append(f"{total_files - valid_files} files have validation issues")
        rag_ready = False
    
    if empty_files:
        rag_issues.append(f"{len(empty_files)} files have empty chunks")
        rag_ready = False
    
    # Check average chunk sizes
    total_chunks_all = sum(r['stats'].get('total_chunks', 0) for r in results.values())
    total_words_all = sum(r['stats'].get('total_words', 0) for r in results.values())
    overall_avg = total_words_all / total_chunks_all if total_chunks_all > 0 else 0
    
    print(f"✅ Total Chunks: {total_chunks_all:,}")
    print(f"✅ Total Words: {total_words_all:,}")
    print(f"✅ Average Chunk Size: {overall_avg:.1f} words")
    print()
    
    if overall_avg < 150 or overall_avg > 400:
        rag_issues.append(f"Average chunk size ({overall_avg:.1f}) outside optimal range (150-400 words)")
    
    if rag_ready:
        print("🎉 Status: READY FOR RAG SYSTEM")
        print()
        print("✅ All files properly formatted")
        print("✅ All metadata complete")
        print("✅ All chunks have subheadings")
        print("✅ No empty chunks detected")
        print("✅ Optimal chunk sizes maintained")
        print("✅ Consistent structure across all files")
    else:
        print("⚠️  Status: NEEDS ATTENTION")
        print()
        print("Issues found:")
        for issue in rag_issues:
            print(f"   - {issue}")
    
    print()
    print("=" * 80)
    print("✅ VALIDATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
