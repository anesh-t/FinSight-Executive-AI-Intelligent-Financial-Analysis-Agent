"""
Test quarter pattern detection (Q3, q3, Q 3, 3rd Q, etc.)
"""
import re

def test_quarter_patterns():
    """Test all quarter pattern variations"""
    
    test_cases = [
        # Standard patterns
        ("Q1 2023", 1),
        ("Q2 2023", 2),
        ("Q3 2023", 3),
        ("Q4 2023", 4),
        
        # Lowercase
        ("q1 2023", 1),
        ("q2 2023", 2),
        ("q3 2023", 3),
        
        # With spaces
        ("Q 1 2023", 1),
        ("Q 2 2023", 2),
        ("Q 3 2023", 3),
        ("Q 4 2023", 4),
        
        # Ordinal + Q
        ("1st Q 2023", 1),
        ("2nd Q 2023", 2),
        ("3rd Q 2023", 3),
        ("4th Q 2023", 4),
        
        # Ordinal + quarter
        ("1st quarter 2023", 1),
        ("2nd quarter 2023", 2),
        ("3rd quarter 2023", 3),
        ("4th quarter 2023", 4),
        
        # Word form
        ("first quarter 2023", 1),
        ("second quarter 2023", 2),
        ("third quarter 2023", 3),
        ("fourth quarter 2023", 4),
    ]
    
    print("\n" + "="*100)
    print("TESTING QUARTER PATTERN DETECTION")
    print("="*100)
    
    passed = 0
    failed = 0
    
    for query, expected_q in test_cases:
        question_upper = query.upper()
        period = {"fy": None, "fq": None}
        
        # Pattern 1: 1st Q, 2nd Q, 3rd Q, 4th Q - CHECK FIRST
        if re.search(r'\b([1-4])(ST|ND|RD|TH)\s*Q\b', question_upper):
            quarter_num_match = re.search(r'\b([1-4])(ST|ND|RD|TH)\s*Q\b', question_upper)
            period["fq"] = int(quarter_num_match.group(1))
        # Pattern 2: 1st quarter, 2nd quarter, 3rd quarter, 4th quarter
        elif re.search(r'\b([1-4])(ST|ND|RD|TH)\s+QUARTER', question_upper):
            quarter_num_match = re.search(r'\b([1-4])(ST|ND|RD|TH)\s+QUARTER', question_upper)
            period["fq"] = int(quarter_num_match.group(1))
        # Pattern 3: Q1, Q2, Q3, Q4, q1, q 1, Q 1, etc.
        elif re.search(r'Q\s*([1-4])', question_upper):
            quarter_match = re.search(r'Q\s*([1-4])', question_upper)
            period["fq"] = int(quarter_match.group(1))
        # Pattern 4: first, second, third, fourth quarter
        elif 'FIRST QUARTER' in question_upper or 'FIRST-QUARTER' in question_upper:
            period["fq"] = 1
        elif 'SECOND QUARTER' in question_upper or 'SECOND-QUARTER' in question_upper:
            period["fq"] = 2
        elif 'THIRD QUARTER' in question_upper or 'THIRD-QUARTER' in question_upper:
            period["fq"] = 3
        elif 'FOURTH QUARTER' in question_upper or 'FOURTH-QUARTER' in question_upper:
            period["fq"] = 4
        
        detected_q = period["fq"]
        
        if detected_q == expected_q:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1
        
        print(f"{status} | Query: '{query:<25}' | Expected: Q{expected_q} | Detected: Q{detected_q if detected_q else 'None'}")
    
    print("\n" + "="*100)
    print(f"RESULTS: {passed}/{passed + failed} tests passing ({passed/(passed+failed)*100:.1f}%)")
    print("="*100)
    
    if passed == passed + failed:
        print("✅ ALL QUARTER PATTERNS WORKING!")
    else:
        print("❌ SOME PATTERNS FAILED")

if __name__ == "__main__":
    test_quarter_patterns()
