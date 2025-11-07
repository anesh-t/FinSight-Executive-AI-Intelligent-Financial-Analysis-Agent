"""
Test ALL 445 Questions from CFO_COMPREHENSIVE_TEST_QUESTIONS.md
"""
import requests
import json
import time
from datetime import datetime
import re

API_URL = "http://localhost:8000/ask"

def extract_questions_from_md():
    """Extract all questions from the markdown file"""
    questions_by_category = {}
    current_category = None
    
    with open('/Users/aneshthangaraj/CascadeProjects/windsurf-project-2/CFO_COMPREHENSIVE_TEST_QUESTIONS.md', 'r') as f:
        content = f.read()
    
    # Split by category headers (##)
    lines = content.split('\n')
    
    for line in lines:
        # Check for category header
        if line.startswith('## ') and 'Category' in line:
            current_category = line.replace('##', '').strip()
            questions_by_category[current_category] = []
        # Check for numbered questions (e.g., "1. ", "10. ", "100. ")
        elif current_category and re.match(r'^\d+\.\s+"', line):
            # Extract question between quotes
            match = re.search(r'"([^"]+)"', line)
            if match:
                question = match.group(1)
                questions_by_category[current_category].append(question)
    
    return questions_by_category

def test_question(question: str, session_id: str = "test_445"):
    """Test a single question"""
    try:
        response = requests.post(
            API_URL,
            json={"question": question, "session_id": session_id},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("response", "")
            
            # Criteria 1: SQL executed (got 200 response)
            sql_executed = True
            
            # Criteria 2: Data retrieved and shown
            data_retrieved = len(answer) > 0
            response_shown = len(answer) > 20
            
            # Check for known issues
            if "data found for" in answer.lower() and len(answer) < 100:
                failure_reason = "DATA_FOUND_BUT_NOT_SHOWN"
                status = "FAIL"
            elif "no results for this task" in answer.lower():
                failure_reason = "NO_RESULTS"
                status = "FAIL"
            elif not answer or len(answer.strip()) < 20:
                failure_reason = "EMPTY_RESPONSE"
                status = "FAIL"
            elif any(err in answer.lower() for err in ["error", "failed", "could not"]):
                failure_reason = "ERROR_IN_RESPONSE"
                status = "FAIL"
            else:
                # Criteria 3: Answer makes sense (has numbers and relevant content)
                has_numbers = any(char.isdigit() for char in answer)
                has_company = any(c in answer for c in ["Apple", "Microsoft", "Google", "Amazon", "Meta", "Alphabet", "Inc.", "Corporation"])
                has_metrics = any(m in answer.lower() for m in [
                    "revenue", "income", "margin", "price", "stock", "gdp", "cpi",
                    "unemployment", "fed", "federal funds", "s&p", "sp500", "index",
                    "roe", "roa", "debt", "ratio", "assets", "liabilities", "equity",
                    "cash flow", "r&d", "sg&a", "cogs", "dividend", "buyback", "eps",
                    "reported", "was", "were", "for", "fy", "quarter"
                ])
                
                if has_numbers and (has_company or has_metrics):
                    failure_reason = None
                    status = "PASS"
                else:
                    failure_reason = "ANSWER_LACKS_DATA"
                    status = "FAIL"
            
            return {
                "status": status,
                "answer": answer,
                "failure_reason": failure_reason,
                "sql_executed": sql_executed,
                "data_retrieved": data_retrieved,
                "response_shown": response_shown
            }
        else:
            return {
                "status": "ERROR",
                "answer": "",
                "failure_reason": f"HTTP_{response.status_code}",
                "sql_executed": False,
                "data_retrieved": False,
                "response_shown": False
            }
    except Exception as e:
        return {
            "status": "ERROR",
            "answer": "",
            "failure_reason": str(e),
            "sql_executed": False,
            "data_retrieved": False,
            "response_shown": False
        }

def main():
    """Run all 445 tests"""
    print("="*100)
    print("🚀 TESTING ALL 445 QUESTIONS FROM CFO_COMPREHENSIVE_TEST_QUESTIONS.md")
    print("="*100)
    
    # Extract questions
    print("\n📖 Extracting questions from markdown file...")
    questions_by_category = extract_questions_from_md()
    
    total_questions = sum(len(q) for q in questions_by_category.values())
    print(f"✅ Extracted {total_questions} questions across {len(questions_by_category)} categories")
    
    # Run tests
    all_results = []
    category_summaries = []
    overall_start = time.time()
    question_number = 0
    
    for category, questions in questions_by_category.items():
        if not questions:
            continue
            
        print(f"\n{'='*100}")
        print(f"📂 {category} ({len(questions)} questions)")
        print(f"{'='*100}")
        
        category_results = []
        
        for i, question in enumerate(questions, 1):
            question_number += 1
            print(f"\n[{question_number}/{total_questions}] {question[:80]}...")
            
            start_time = time.time()
            result = test_question(question)
            execution_time = time.time() - start_time
            
            result["question"] = question
            result["category"] = category
            result["execution_time"] = execution_time
            category_results.append(result)
            all_results.append(result)
            
            # Print result
            status_emoji = "✅" if result["status"] == "PASS" else "❌"
            print(f"  {status_emoji} {result['status']}", end="")
            if result["failure_reason"]:
                print(f" - {result['failure_reason']}", end="")
            print(f" ({execution_time:.2f}s)")
            
            # Show first 100 chars of answer for failed tests
            if result["status"] != "PASS":
                print(f"  💬 {result['answer'][:100]}")
        
        # Category summary
        passed = sum(1 for r in category_results if r["status"] == "PASS")
        failed = sum(1 for r in category_results if r["status"] == "FAIL")
        errors = sum(1 for r in category_results if r["status"] == "ERROR")
        pass_rate = (passed / len(category_results) * 100) if category_results else 0
        
        category_summaries.append({
            "category": category,
            "total": len(category_results),
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "pass_rate": pass_rate
        })
        
        print(f"\n📊 Category: {passed}/{len(category_results)} passed ({pass_rate:.1f}%)")
    
    # Overall summary
    total_time = time.time() - overall_start
    print("\n" + "="*100)
    print("📊 OVERALL RESULTS - ALL 445 QUESTIONS")
    print("="*100)
    
    total_passed = sum(1 for r in all_results if r["status"] == "PASS")
    total_failed = sum(1 for r in all_results if r["status"] == "FAIL")
    total_errors = sum(1 for r in all_results if r["status"] == "ERROR")
    overall_pass_rate = (total_passed / len(all_results) * 100) if all_results else 0
    
    print(f"\n✅ PASSED: {total_passed}/{len(all_results)} ({overall_pass_rate:.1f}%)")
    print(f"❌ FAILED: {total_failed}/{len(all_results)}")
    print(f"⚠️  ERRORS: {total_errors}/{len(all_results)}")
    print(f"⏱️  Total Time: {total_time/60:.1f} minutes")
    print(f"⚱️  Avg Time per Question: {total_time/len(all_results):.2f}s")
    
    # Failure analysis
    if total_failed > 0 or total_errors > 0:
        print("\n" + "="*100)
        print("🔍 FAILURE ANALYSIS")
        print("="*100)
        
        failure_categories = {}
        for result in all_results:
            if result["status"] != "PASS":
                reason = result["failure_reason"] or "UNKNOWN"
                if reason not in failure_categories:
                    failure_categories[reason] = []
                failure_categories[reason].append(result)
        
        for reason, failures in failure_categories.items():
            print(f"\n❌ {reason}: {len(failures)} questions")
            for failure in failures[:5]:  # Show first 5
                print(f"   - {failure['question'][:80]}")
            if len(failures) > 5:
                print(f"   ... and {len(failures) - 5} more")
    
    # Category breakdown
    print("\n" + "="*100)
    print("📋 CATEGORY BREAKDOWN")
    print("="*100)
    for summary in category_summaries:
        status = "✅" if summary["pass_rate"] == 100 else "⚠️" if summary["pass_rate"] >= 90 else "❌"
        print(f"{status} {summary['category'][:60]:60} {summary['passed']:3}/{summary['total']:3} ({summary['pass_rate']:5.1f}%)")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"test_results_all_445_{timestamp}.json"
    
    output_data = {
        "timestamp": timestamp,
        "total_questions": len(all_results),
        "summary": {
            "passed": total_passed,
            "failed": total_failed,
            "errors": total_errors,
            "pass_rate": overall_pass_rate,
            "total_time_seconds": total_time,
            "avg_time_per_question": total_time/len(all_results)
        },
        "category_summaries": category_summaries,
        "failure_categories": {k: len(v) for k, v in failure_categories.items()} if total_failed > 0 or total_errors > 0 else {},
        "detailed_results": all_results
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    print("\n" + "="*100)
    print("✅ TEST SUITE COMPLETE!")
    print("="*100)

if __name__ == "__main__":
    main()
