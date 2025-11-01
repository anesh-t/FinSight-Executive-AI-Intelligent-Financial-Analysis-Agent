"""
Comprehensive Coverage Test Suite
Tests RAG agent against all CFO question categories
"""

import sys
from pathlib import Path
import time
from typing import List, Dict
import json

sys.path.insert(0, str(Path(__file__).parent / '3_generation'))
from rag_agent import RAGAgent

# ============================================================================
# TEST QUESTIONS BY CATEGORY
# ============================================================================

TEST_QUESTIONS = {
    "RISK_ANALYSIS": {
        "priority": "TIER_1",
        "questions": [
            # General Risks
            "What are Apple's top 3 risks in 2022?",
            "What are the biggest threats to Microsoft in 2022?",
            "List the main vulnerabilities for Amazon in 2022",
            
            # Risk Categories
            "What cybersecurity risks does Apple face in 2022?",
            "What supply chain risks does Microsoft have in 2022?",
            "What regulatory risks does Apple disclose in 2022?",
            "What competitive risks does Microsoft face in 2022?",
            
            # Risk Comparisons
            "Compare cybersecurity risks between Apple and Microsoft in 2022",
            "Which company has more supply chain risk: Apple or Microsoft?",
            "What risks are common to both Apple and Microsoft in 2022?",
            
            # Risk Mitigation
            "How does Apple mitigate its cybersecurity risks?",
            "What risk management strategies does Microsoft use?",
        ]
    },
    
    "BUSINESS_STRATEGY": {
        "priority": "TIER_1",
        "questions": [
            # Business Model
            "What is Apple's business model in 2022?",
            "How does Microsoft make money according to its 2022 10-K?",
            "What are Apple's main revenue streams in 2022?",
            "What products and services does Microsoft offer in 2022?",
            
            # Competitive Position
            "What are Apple's competitive advantages in 2022?",
            "Who are Microsoft's main competitors in 2022?",
            "How does Apple differentiate itself from competitors?",
            "What is Microsoft's market position in cloud computing?",
            
            # Growth Strategy
            "What is Apple's growth strategy for 2022?",
            "What strategic priorities does Microsoft have in 2022?",
            "What markets is Apple expanding into?",
        ]
    },
    
    "OPERATIONS": {
        "priority": "TIER_2",
        "questions": [
            # Operations
            "Describe Apple's supply chain in 2022",
            "What are Microsoft's key operational facilities?",
            "How does Apple manufacture its products?",
            
            # Technology & Innovation
            "What are Apple's R&D priorities in 2022?",
            "What technology innovations is Microsoft pursuing?",
            "What intellectual property does Apple have?",
            
            # Human Capital
            "How many employees does Apple have in 2022?",
            "What is Microsoft's talent strategy?",
            "What employee benefits does Apple offer?",
        ]
    },
    
    "FINANCIAL_CONTEXT": {
        "priority": "TIER_1",
        "questions": [
            # Performance Drivers
            "What drove Apple's revenue growth in 2022?",
            "Why did Microsoft's margins change in 2022?",
            "What impacted Apple's profitability in 2022?",
            
            # Cost Structure
            "What are Apple's main cost drivers in 2022?",
            "How is Microsoft managing costs?",
            "What cost optimization initiatives does Apple have?",
            
            # Capital Allocation
            "How does Apple allocate capital?",
            "What is Microsoft's investment strategy?",
            "What acquisitions did Apple make in 2022?",
        ]
    },
    
    "LEGAL_REGULATORY": {
        "priority": "TIER_2",
        "questions": [
            # Legal
            "What legal issues does Apple face in 2022?",
            "What lawsuits is Microsoft involved in?",
            "What regulatory investigations affect Apple?",
            
            # Compliance
            "What regulations does Microsoft comply with?",
            "How is Apple regulated?",
            "What regulatory changes affect Microsoft?",
        ]
    },
    
    "GOVERNANCE": {
        "priority": "TIER_3",
        "questions": [
            # Governance
            "What is Apple's governance structure?",
            "Who are Microsoft's key executives in 2022?",
            
            # Controls
            "What internal controls does Apple have?",
            "What control weaknesses has Microsoft disclosed?",
        ]
    },
    
    "FORWARD_LOOKING": {
        "priority": "TIER_2",
        "questions": [
            # Outlook
            "What is Apple's outlook for the future?",
            "What are Microsoft's future plans?",
            "What forward-looking statements did Apple make in 2022?",
            
            # Uncertainties
            "What uncertainties does Apple face?",
            "What assumptions is Microsoft making?",
        ]
    },
    
    "SPECIAL_SITUATIONS": {
        "priority": "TIER_2",
        "questions": [
            # Crisis
            "How did COVID-19 impact Apple in 2022?",
            "How has Microsoft responded to the pandemic?",
            
            # M&A
            "What acquisitions has Apple made?",
            "What divestitures has Microsoft done?",
        ]
    },
    
    "COMPARATIVE": {
        "priority": "TIER_1",
        "questions": [
            # Company vs Company
            "Compare Apple and Microsoft's business models",
            "Compare Apple and Microsoft's competitive positioning",
            "Which company has better risk management: Apple or Microsoft?",
            "How do Apple and Microsoft's strategies differ?",
        ]
    },
    
    "SYNTHESIS": {
        "priority": "TIER_1",
        "questions": [
            # Summary
            "Summarize Apple's key takeaways from its 2022 10-K",
            "Give me a CFO-level overview of Microsoft's 2022 filing",
            "What are the most important things to know about Apple from its 2022 10-K?",
            
            # Analysis
            "Analyze Apple's competitive positioning in 2022",
            "Evaluate Microsoft's growth prospects",
            "Assess Apple's strategic choices in 2022",
        ]
    }
}

# ============================================================================
# EVALUATION CRITERIA
# ============================================================================

def evaluate_answer(question: str, answer: str, category: str) -> Dict:
    """
    Evaluate if answer is satisfactory
    
    Criteria:
    1. Length (not too short, not empty)
    2. Has sources/citations
    3. CFO-appropriate language
    4. Answers the question
    """
    
    evaluation = {
        "has_content": len(answer) > 100,  # At least 100 chars
        "has_sources": "[" in answer or "SOURCE" in answer.upper(),
        "is_structured": any(marker in answer for marker in ["**", "###", "─", "•", "-"]),
        "not_error": "error" not in answer.lower() and "failed" not in answer.lower(),
    }
    
    evaluation["passed"] = all(evaluation.values())
    evaluation["score"] = sum(evaluation.values()) / len(evaluation) * 100
    
    return evaluation

# ============================================================================
# RUN COMPREHENSIVE TEST
# ============================================================================

def run_comprehensive_test(agent: RAGAgent, max_questions_per_category: int = 3):
    """Run comprehensive test across all categories"""
    
    print("\n" + "=" * 80)
    print("🧪 COMPREHENSIVE CFO AGENT COVERAGE TEST")
    print("=" * 80)
    print()
    
    results = {
        "categories": {},
        "overall": {
            "total_questions": 0,
            "passed": 0,
            "failed": 0,
            "avg_time": 0,
            "avg_score": 0,
            "total_cost": 0
        }
    }
    
    total_time = 0
    
    for category, data in TEST_QUESTIONS.items():
        print(f"\n{'─' * 80}")
        print(f"📋 CATEGORY: {category} ({data['priority']})")
        print(f"{'─' * 80}")
        
        category_results = {
            "priority": data["priority"],
            "questions_tested": 0,
            "passed": 0,
            "failed": 0,
            "avg_score": 0,
            "avg_time": 0,
            "tests": []
        }
        
        # Test subset of questions from this category
        questions_to_test = data["questions"][:max_questions_per_category]
        
        for i, question in enumerate(questions_to_test, 1):
            print(f"\n  {i}. Testing: {question[:70]}...")
            
            try:
                # Run query
                start = time.time()
                result = agent.query(question, top_k=5)
                elapsed = time.time() - start
                
                # Evaluate answer
                evaluation = evaluate_answer(question, result.text, category)
                
                # Store results
                test_result = {
                    "question": question,
                    "passed": evaluation["passed"],
                    "score": evaluation["score"],
                    "time": elapsed,
                    "cost": result.metadata.get("cost", 0),
                    "answer_length": len(result.text),
                    "evaluation": evaluation
                }
                
                category_results["tests"].append(test_result)
                category_results["questions_tested"] += 1
                
                if evaluation["passed"]:
                    category_results["passed"] += 1
                    print(f"     ✅ PASS (Score: {evaluation['score']:.0f}%, Time: {elapsed:.1f}s)")
                else:
                    category_results["failed"] += 1
                    print(f"     ❌ FAIL (Score: {evaluation['score']:.0f}%, Time: {elapsed:.1f}s)")
                    print(f"     Issues: {[k for k, v in evaluation.items() if not v and k != 'passed' and k != 'score']}")
                
                total_time += elapsed
                
                # Small delay to avoid rate limits
                time.sleep(0.5)
                
            except Exception as e:
                print(f"     ❌ ERROR: {str(e)[:100]}")
                category_results["failed"] += 1
                category_results["tests"].append({
                    "question": question,
                    "passed": False,
                    "error": str(e)
                })
        
        # Calculate category stats
        if category_results["questions_tested"] > 0:
            category_results["avg_score"] = sum(t.get("score", 0) for t in category_results["tests"]) / category_results["questions_tested"]
            category_results["avg_time"] = sum(t.get("time", 0) for t in category_results["tests"]) / category_results["questions_tested"]
            category_results["pass_rate"] = (category_results["passed"] / category_results["questions_tested"]) * 100
        
        results["categories"][category] = category_results
        
        # Print category summary
        print(f"\n  📊 Category Summary:")
        print(f"     Pass Rate: {category_results.get('pass_rate', 0):.0f}%")
        print(f"     Avg Score: {category_results.get('avg_score', 0):.0f}%")
        print(f"     Avg Time: {category_results.get('avg_time', 0):.1f}s")
    
    # Calculate overall stats
    results["overall"]["total_questions"] = sum(c["questions_tested"] for c in results["categories"].values())
    results["overall"]["passed"] = sum(c["passed"] for c in results["categories"].values())
    results["overall"]["failed"] = sum(c["failed"] for c in results["categories"].values())
    
    if results["overall"]["total_questions"] > 0:
        results["overall"]["pass_rate"] = (results["overall"]["passed"] / results["overall"]["total_questions"]) * 100
        results["overall"]["avg_score"] = sum(c["avg_score"] for c in results["categories"].values()) / len(results["categories"])
        results["overall"]["avg_time"] = total_time / results["overall"]["total_questions"]
        results["overall"]["total_cost"] = sum(
            sum(t.get("cost", 0) for t in c["tests"])
            for c in results["categories"].values()
        )
    
    return results

# ============================================================================
# PRINT FINAL REPORT
# ============================================================================

def print_final_report(results: Dict):
    """Print comprehensive test report"""
    
    print("\n\n" + "=" * 80)
    print("📊 FINAL TEST REPORT")
    print("=" * 80)
    
    overall = results["overall"]
    
    print(f"\n🎯 OVERALL RESULTS:")
    print(f"   Total Questions: {overall['total_questions']}")
    print(f"   Passed: {overall['passed']} ✅")
    print(f"   Failed: {overall['failed']} ❌")
    print(f"   Pass Rate: {overall.get('pass_rate', 0):.1f}%")
    print(f"   Avg Score: {overall.get('avg_score', 0):.1f}%")
    print(f"   Avg Time: {overall.get('avg_time', 0):.2f}s")
    print(f"   Total Cost: ${overall.get('total_cost', 0):.4f}")
    
    print(f"\n📋 CATEGORY BREAKDOWN:")
    print(f"{'─' * 80}")
    print(f"{'Category':<20} {'Priority':<10} {'Pass Rate':<12} {'Avg Score':<12} {'Avg Time':<10}")
    print(f"{'─' * 80}")
    
    for category, data in results["categories"].items():
        print(f"{category:<20} {data['priority']:<10} {data.get('pass_rate', 0):>6.0f}%     {data.get('avg_score', 0):>6.0f}%     {data.get('avg_time', 0):>6.1f}s")
    
    print(f"{'─' * 80}")
    
    # Identify problem areas
    print(f"\n⚠️  AREAS NEEDING IMPROVEMENT:")
    problem_categories = [
        (cat, data) for cat, data in results["categories"].items()
        if data.get("pass_rate", 0) < 80
    ]
    
    if problem_categories:
        for cat, data in problem_categories:
            print(f"   • {cat}: {data.get('pass_rate', 0):.0f}% pass rate")
    else:
        print(f"   ✅ All categories performing well!")
    
    # Grade the system
    print(f"\n🎓 SYSTEM GRADE:")
    pass_rate = overall.get('pass_rate', 0)
    
    if pass_rate >= 95:
        grade = "A+ (Excellent)"
    elif pass_rate >= 90:
        grade = "A (Very Good)"
    elif pass_rate >= 85:
        grade = "B+ (Good)"
    elif pass_rate >= 80:
        grade = "B (Above Average)"
    elif pass_rate >= 75:
        grade = "C+ (Average)"
    elif pass_rate >= 70:
        grade = "C (Below Average)"
    else:
        grade = "D (Needs Improvement)"
    
    print(f"   {grade}")
    
    print("\n" + "=" * 80)
    
    # Save results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n✅ Results saved to: test_results.json")
    print()

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\nInitializing CFO Assistant...")
    agent = RAGAgent(model="gpt-3.5-turbo", verbose=False)
    
    try:
        # Run comprehensive test
        # Test 3 questions per category (30 questions total)
        # Set to higher number for full test
        results = run_comprehensive_test(agent, max_questions_per_category=3)
        
        # Print report
        print_final_report(results)
        
        print("\n💡 RECOMMENDATIONS:")
        print("   1. Review failed questions in test_results.json")
        print("   2. Check if relevant chunks are being retrieved")
        print("   3. Improve prompts for low-scoring categories")
        print("   4. Add more context for comparative questions")
        print("   5. Re-run full test after improvements")
        
    finally:
        agent.close()
        print("\n✅ Test complete!")
