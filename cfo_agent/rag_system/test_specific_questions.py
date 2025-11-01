"""
Test Suite for Specific CFO Question Patterns
Tests real-world questions across all categories
"""

import sys
from pathlib import Path
import time
from typing import List, Dict
import json

sys.path.insert(0, str(Path(__file__).parent / '3_generation'))
from rag_agent import RAGAgent

# ============================================================================
# SPECIFIC QUESTION PATTERNS (From User Requirements)
# ============================================================================

TEST_QUESTIONS = {
    "A_RISK_FACTORS_MULTI_COMPANY_YEAR": {
        "questions": [
            "Compare top risk factors reported by Apple and Microsoft for the year 2022",
            "How did Microsoft's cybersecurity risks evolve between 2019 and 2022?",
            "Which company—Apple or Microsoft—disclosed more regulatory risks in 2022?",
            "Summarize supply chain risks for Apple and Microsoft in 2022",
        ],
        "expected_features": ["multi_company", "comparison", "specific_year"],
        "priority": "HIGH"
    },
    
    "B_MANAGEMENT_DISCUSSION_COMPARISON": {
        "questions": [
            "How did management at Apple and Microsoft explain strategic shifts in 2022?",
            "Compare management discussions on R&D innovation for Microsoft and Apple in 2022",
            "What future market outlooks were described by Apple in their 2022 filing?",
        ],
        "expected_features": ["management_discussion", "strategy", "outlook"],
        "priority": "HIGH"
    },
    
    "C_MARKET_RISK_DISCLOSURE": {
        "questions": [
            "Compare interest rate risk exposure described by Apple and Microsoft in 2022",
            "How did foreign exchange risk disclosures change for Apple from 2019 through 2022?",
            "What market risks did Microsoft highlight in 2022?",
        ],
        "expected_features": ["market_risk", "specific_risk_type"],
        "priority": "MEDIUM"
    },
    
    "D_REGULATORY_COMPLIANCE_ESG": {
        "questions": [
            "Which companies cited climate change risk in their 2022 filings: Apple or Microsoft?",
            "How have regulatory risks evolved for Apple since 2019?",
            "What compliance challenges did Microsoft disclose in 2022?",
        ],
        "expected_features": ["regulatory", "compliance", "esg"],
        "priority": "MEDIUM"
    },
    
    "E_LITIGATION_LEGAL": {
        "questions": [
            "Compare patent litigation risks for Apple and Microsoft in 2022",
            "What legal issues did Apple disclose in its 2022 filing?",
            "How did antitrust risk discussions evolve for Microsoft?",
        ],
        "expected_features": ["litigation", "legal", "antitrust"],
        "priority": "MEDIUM"
    },
    
    "F_CRISIS_MANAGEMENT": {
        "questions": [
            "Review COVID-19 risk mitigation strategies disclosed by Apple in 2022",
            "How did Microsoft address cybersecurity risk in 2022?",
            "What crisis management approaches did Apple describe?",
        ],
        "expected_features": ["crisis", "mitigation", "response"],
        "priority": "HIGH"
    },
    
    "G_STRATEGIC_OUTLOOK": {
        "questions": [
            "Compare international expansion plans discussed by Apple and Microsoft in 2022",
            "How did Apple's management describe changes in capital allocation in 2022?",
            "What strategic priorities did Microsoft highlight in 2022?",
        ],
        "expected_features": ["strategy", "expansion", "future_plans"],
        "priority": "HIGH"
    },
    
    "H_OPERATIONAL_CHANGES": {
        "questions": [
            "What supply chain restructurings have been described by Apple in 2022?",
            "Compare changes in product innovation focus for Apple versus Microsoft",
            "What operational challenges did Microsoft discuss in 2022?",
        ],
        "expected_features": ["operations", "changes", "restructuring"],
        "priority": "MEDIUM"
    },
    
    "I_SINGLE_COMPANY_SPECIFIC": {
        "questions": [
            "What are the top risks for Apple disclosed in 2022?",
            "Summarize cybersecurity risks faced by Microsoft in 2022",
            "What reasons did Apple's management give for operational challenges in 2022?",
            "What acquisitions did Microsoft's management discuss in 2022?",
        ],
        "expected_features": ["single_company", "specific_topic"],
        "priority": "HIGH"
    },
    
    "J_SECTION_SPECIFIC": {
        "questions": [
            "What does Apple's Item 1A say about cybersecurity risks in 2022?",
            "Summarize Apple's management discussion (Item 7) about strategy in 2022",
            "What market risks did Microsoft disclose in Item 7A for 2022?",
        ],
        "expected_features": ["section_specific", "item_1a", "item_7"],
        "priority": "MEDIUM"
    }
}

# ============================================================================
# EVALUATION
# ============================================================================

def evaluate_answer(question: str, answer: str, expected_features: List[str]) -> Dict:
    """
    Evaluate answer quality
    """
    
    evaluation = {
        "has_content": len(answer) > 100,
        "has_sources": "[" in answer or "SOURCE" in answer.upper() or "Source" in answer,
        "is_structured": any(marker in answer for marker in ["**", "###", "─", "•", "-", "Priority", "PRIORITY"]),
        "not_empty": answer.strip() != "" and "I don't have" not in answer,
        "has_analysis": len(answer) > 300,  # Substantial analysis
    }
    
    # Check for comparison keywords if it's a comparison question
    if "compare" in question.lower() or "versus" in question.lower():
        evaluation["has_comparison"] = any(word in answer.lower() for word in ["both", "whereas", "while", "contrast", "difference", "similar", "common"])
    
    evaluation["passed"] = all([
        evaluation["has_content"],
        evaluation["has_sources"],
        evaluation["not_empty"]
    ])
    
    evaluation["score"] = sum(1 for v in evaluation.values() if v is True) / len(evaluation) * 100
    
    return evaluation

# ============================================================================
# RUN TESTS
# ============================================================================

def run_specific_question_tests(agent: RAGAgent, max_per_category: int = 3):
    """Run tests on specific question patterns"""
    
    print("\n" + "=" * 80)
    print("🎯 TESTING SPECIFIC CFO QUESTION PATTERNS")
    print("=" * 80)
    print()
    
    results = {
        "categories": {},
        "overall": {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "avg_time": 0,
            "total_time": 0,
            "total_cost": 0
        }
    }
    
    total_time = 0
    all_times = []
    
    for category, data in TEST_QUESTIONS.items():
        print(f"\n{'─' * 80}")
        print(f"📋 {category.replace('_', ' ')}")
        print(f"   Priority: {data['priority']}")
        print(f"{'─' * 80}")
        
        cat_results = {
            "priority": data["priority"],
            "tested": 0,
            "passed": 0,
            "failed": 0,
            "tests": []
        }
        
        questions = data["questions"][:max_per_category]
        
        for i, question in enumerate(questions, 1):
            print(f"\n  {i}. {question}")
            
            try:
                start = time.time()
                result = agent.query(question, top_k=5)
                elapsed = time.time() - start
                
                evaluation = evaluate_answer(question, result.text, data["expected_features"])
                
                test_result = {
                    "question": question,
                    "passed": evaluation["passed"],
                    "score": evaluation["score"],
                    "time": elapsed,
                    "cost": result.metadata.get("cost", 0),
                    "answer_length": len(result.text)
                }
                
                cat_results["tests"].append(test_result)
                cat_results["tested"] += 1
                
                if evaluation["passed"]:
                    cat_results["passed"] += 1
                    print(f"     ✅ PASS - {elapsed:.1f}s, Score: {evaluation['score']:.0f}%")
                else:
                    cat_results["failed"] += 1
                    print(f"     ❌ FAIL - {elapsed:.1f}s, Score: {evaluation['score']:.0f}%")
                    issues = [k for k, v in evaluation.items() if not v and k not in ['passed', 'score']]
                    if issues:
                        print(f"        Issues: {issues}")
                
                total_time += elapsed
                all_times.append(elapsed)
                
                # Show preview
                preview = result.text[:200].replace('\n', ' ')
                print(f"     Preview: {preview}...")
                
                time.sleep(0.3)  # Rate limiting
                
            except Exception as e:
                print(f"     ❌ ERROR: {str(e)[:150]}")
                cat_results["failed"] += 1
                cat_results["tests"].append({
                    "question": question,
                    "passed": False,
                    "error": str(e)
                })
        
        # Category stats
        if cat_results["tested"] > 0:
            cat_results["pass_rate"] = (cat_results["passed"] / cat_results["tested"]) * 100
            cat_results["avg_time"] = sum(t["time"] for t in cat_results["tests"] if "time" in t) / cat_results["tested"]
            cat_results["avg_score"] = sum(t.get("score", 0) for t in cat_results["tests"]) / cat_results["tested"]
        
        results["categories"][category] = cat_results
        
        print(f"\n  📊 Category: {cat_results.get('pass_rate', 0):.0f}% pass, {cat_results.get('avg_time', 0):.1f}s avg")
    
    # Overall stats
    results["overall"]["total"] = sum(c["tested"] for c in results["categories"].values())
    results["overall"]["passed"] = sum(c["passed"] for c in results["categories"].values())
    results["overall"]["failed"] = sum(c["failed"] for c in results["categories"].values())
    results["overall"]["total_time"] = total_time
    
    if results["overall"]["total"] > 0:
        results["overall"]["pass_rate"] = (results["overall"]["passed"] / results["overall"]["total"]) * 100
        results["overall"]["avg_time"] = total_time / results["overall"]["total"]
        results["overall"]["min_time"] = min(all_times) if all_times else 0
        results["overall"]["max_time"] = max(all_times) if all_times else 0
        results["overall"]["total_cost"] = sum(
            sum(t.get("cost", 0) for t in c["tests"])
            for c in results["categories"].values()
        )
    
    return results

# ============================================================================
# PRINT REPORT
# ============================================================================

def print_report(results: Dict):
    """Print test report"""
    
    print("\n\n" + "=" * 80)
    print("📊 TEST RESULTS - SPECIFIC QUESTION PATTERNS")
    print("=" * 80)
    
    overall = results["overall"]
    
    print(f"\n🎯 OVERALL PERFORMANCE:")
    print(f"   Total Questions: {overall['total']}")
    print(f"   Passed: {overall['passed']} ✅")
    print(f"   Failed: {overall['failed']} ❌")
    print(f"   Pass Rate: {overall.get('pass_rate', 0):.1f}%")
    print(f"   Avg Time: {overall.get('avg_time', 0):.2f}s")
    print(f"   Min Time: {overall.get('min_time', 0):.2f}s")
    print(f"   Max Time: {overall.get('max_time', 0):.2f}s")
    print(f"   Total Cost: ${overall.get('total_cost', 0):.4f}")
    
    print(f"\n📋 CATEGORY BREAKDOWN:")
    print(f"{'─' * 80}")
    print(f"{'Category':<45} {'Priority':<10} {'Pass Rate':<12} {'Avg Time'}")
    print(f"{'─' * 80}")
    
    for cat, data in results["categories"].items():
        cat_name = cat.replace("_", " ")[:40]
        print(f"{cat_name:<45} {data['priority']:<10} {data.get('pass_rate', 0):>6.0f}%     {data.get('avg_time', 0):>6.1f}s")
    
    print(f"{'─' * 80}")
    
    # Problem areas
    print(f"\n⚠️  NEEDS ATTENTION:")
    problems = [(c, d) for c, d in results["categories"].items() if d.get("pass_rate", 0) < 80]
    
    if problems:
        for cat, data in problems:
            print(f"   • {cat.replace('_', ' ')}: {data.get('pass_rate', 0):.0f}% pass rate")
    else:
        print(f"   ✅ All categories performing well!")
    
    # Speed analysis
    avg_time = overall.get('avg_time', 0)
    print(f"\n⚡ SPEED ANALYSIS:")
    if avg_time <= 4:
        print(f"   ✅ EXCELLENT - {avg_time:.1f}s average (target: <5s)")
    elif avg_time <= 6:
        print(f"   ✅ GOOD - {avg_time:.1f}s average (target: <7s)")
    elif avg_time <= 8:
        print(f"   ⚠️  ACCEPTABLE - {avg_time:.1f}s average (could be faster)")
    else:
        print(f"   ❌ SLOW - {avg_time:.1f}s average (needs optimization)")
    
    # Grade
    pass_rate = overall.get('pass_rate', 0)
    if pass_rate >= 95:
        grade = "A+"
    elif pass_rate >= 90:
        grade = "A"
    elif pass_rate >= 85:
        grade = "B+"
    elif pass_rate >= 80:
        grade = "B"
    else:
        grade = "C"
    
    print(f"\n🎓 GRADE: {grade}")
    
    print("\n" + "=" * 80)
    
    # Save
    with open("specific_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n✅ Results saved to: specific_test_results.json\n")
    
    return results

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\nInitializing CFO Assistant (GPT-3.5-Turbo, optimized)...")
    agent = RAGAgent(model="gpt-3.5-turbo", verbose=False)
    
    try:
        # Run tests
        results = run_specific_question_tests(agent, max_per_category=3)
        
        # Print report
        final_results = print_report(results)
        
        # Recommendations
        pass_rate = final_results["overall"].get("pass_rate", 0)
        avg_time = final_results["overall"].get("avg_time", 0)
        
        print("💡 NEXT STEPS:")
        
        if pass_rate < 90:
            print("   1. Review failed questions")
            print("   2. Improve prompts for low-scoring categories")
            print("   3. Check retrieval quality")
        else:
            print("   ✅ Excellent performance!")
        
        if avg_time > 6:
            print(f"   4. Speed optimization needed (current: {avg_time:.1f}s)")
            print("   5. Consider reducing max_tokens or using faster model")
        else:
            print(f"   ✅ Speed is good! ({avg_time:.1f}s)")
        
    finally:
        agent.close()
        print("\n✅ Testing complete!\n")
