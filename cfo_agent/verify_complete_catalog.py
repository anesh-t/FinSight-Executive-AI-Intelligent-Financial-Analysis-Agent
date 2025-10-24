"""
COMPREHENSIVE CATALOG VERIFICATION
Tests ALL query types with formatted output capture
"""
import asyncio
import yaml
from graph import CFOAgentGraph
from datetime import datetime
import sys

async def verify_complete_catalog():
    """Verify all queries in complete catalog"""
    
    # Load complete query dictionary
    with open('COMPLETE_QUERY_DICTIONARY.yaml', 'r') as f:
        catalog = yaml.safe_load(f)
    
    agent = CFOAgentGraph()
    graph = agent.graph
    
    # Results storage
    results = {
        "test_timestamp": datetime.now().isoformat(),
        "categories": {},
        "summary": {
            "total_categories": 0,
            "total_queries": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0
        }
    }
    
    # Output file for formatted responses
    output_file = open('COMPLETE_VERIFICATION_OUTPUT.txt', 'w', encoding='utf-8')
    
    def write_output(text):
        """Write to both console and file"""
        print(text)
        output_file.write(text + '\n')
    
    write_output("\n" + "="*120)
    write_output("COMPLETE QUERY CATALOG VERIFICATION")
    write_output("="*120)
    write_output(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    write_output(f"Total Categories: {len(catalog)}")
    write_output("="*120 + "\n")
    
    # Process each category
    for category_key, category_data in catalog.items():
        results["summary"]["total_categories"] += 1
        
        # Skip if no queries field
        if 'queries' not in category_data:
            continue
            
        category_name = category_key.replace('_', ' ').title()
        description = category_data.get('description', '')
        queries = category_data['queries']
        
        write_output("\n" + "="*120)
        write_output(f"CATEGORY: {category_name}")
        write_output(f"Description: {description}")
        write_output(f"Query Count: {len(queries)}")
        write_output("="*120 + "\n")
        
        category_results = {
            "description": description,
            "total": len(queries),
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "queries": []
        }
        
        for idx, query in enumerate(queries, 1):
            results["summary"]["total_queries"] += 1
            
            write_output(f"\n[{idx}/{len(queries)}] Query: '{query}'")
            write_output("-" * 120)
            
            state = {
                "question": query,
                "session_id": f"verify_{category_key}_{idx}",
                "errors": []
            }
            
            try:
                result = await graph.ainvoke(state)
                response = result.get("final_response", "No response")
                
                # Validation
                has_dollar = "$" in response
                has_percent = "%" in response
                has_number = any(char.isdigit() for char in response)
                has_keywords = any(word in response.lower() for word in 
                                  ["revenue", "margin", "income", "price", "reported", "rate"])
                is_not_error = "error" not in response.lower()
                
                is_valid = (has_number and has_keywords and is_not_error)
                
                status = "✅ PASS" if is_valid else "⚠️  REVIEW"
                
                write_output(f"\nStatus: {status}")
                write_output(f"\nFormatted Response:")
                write_output("┌" + "─" * 118 + "┐")
                
                # Format response with proper wrapping
                lines = response.split('\n')
                for line in lines:
                    if len(line) <= 116:
                        write_output(f"│ {line:<116} │")
                    else:
                        # Wrap long lines
                        words = line.split()
                        current_line = ""
                        for word in words:
                            if len(current_line) + len(word) + 1 <= 116:
                                current_line += word + " "
                            else:
                                write_output(f"│ {current_line:<116} │")
                                current_line = word + " "
                        if current_line:
                            write_output(f"│ {current_line:<116} │")
                
                write_output("└" + "─" * 118 + "┘")
                
                if is_valid:
                    category_results["passed"] += 1
                    results["summary"]["passed"] += 1
                else:
                    category_results["failed"] += 1
                    results["summary"]["failed"] += 1
                
                category_results["queries"].append({
                    "query": query,
                    "status": "PASS" if is_valid else "REVIEW",
                    "response": response
                })
                
            except Exception as e:
                write_output(f"\n❌ ERROR: {str(e)}")
                category_results["errors"] += 1
                results["summary"]["errors"] += 1
                category_results["queries"].append({
                    "query": query,
                    "status": "ERROR",
                    "error": str(e)
                })
            
            write_output("")
        
        # Category summary
        write_output("\n" + "─"*120)
        write_output(f"Category Summary: {category_results['passed']}/{category_results['total']} passed " +
                    f"({category_results['passed']/category_results['total']*100:.1f}%)")
        write_output("─"*120)
        
        results["categories"][category_key] = category_results
    
    # Final summary
    write_output("\n\n" + "="*120)
    write_output("FINAL COMPREHENSIVE SUMMARY")
    write_output("="*120)
    
    total = results["summary"]["total_queries"]
    passed = results["summary"]["passed"]
    failed = results["summary"]["failed"]
    errors = results["summary"]["errors"]
    
    write_output(f"\n📊 OVERALL STATISTICS")
    write_output(f"   Total Categories: {results['summary']['total_categories']}")
    write_output(f"   Total Queries: {total}")
    write_output(f"   ✅ Passed: {passed} ({passed/total*100:.1f}%)")
    write_output(f"   ⚠️  Review: {failed} ({failed/total*100:.1f}%)")
    write_output(f"   ❌ Errors: {errors} ({errors/total*100:.1f}%)")
    
    write_output(f"\n📈 CATEGORY BREAKDOWN")
    write_output(f"   {'Category':<50} {'Queries':<10} {'Pass Rate':<15} {'Status'}")
    write_output("   " + "-"*115)
    
    for category, data in results["categories"].items():
        cat_name = category.replace('_', ' ').title()
        pass_rate = f"{data['passed']}/{data['total']}"
        percentage = f"({data['passed']/data['total']*100:.0f}%)"
        status = "✅" if data['passed'] == data['total'] else "⚠️" if data['passed'] > 0 else "❌"
        write_output(f"   {cat_name:<50} {data['total']:<10} {pass_rate:<7} {percentage:<8} {status}")
    
    write_output("\n" + "="*120)
    
    if failed + errors == 0:
        write_output("\n🎉 PERFECT SCORE! All queries passed validation!")
    elif errors == 0:
        write_output(f"\n✨ EXCELLENT! {passed} queries passed, {failed} need minor review.")
    else:
        write_output(f"\n⚠️  {errors} queries encountered errors and need attention.")
    
    write_output("="*120)
    
    write_output("\n📁 OUTPUT FILES GENERATED:")
    write_output("   1. COMPLETE_VERIFICATION_OUTPUT.txt - This file with all formatted responses")
    write_output("   2. complete_verification_results.yaml - Structured results data")
    
    output_file.close()
    
    # Save YAML results
    with open('complete_verification_results.yaml', 'w') as f:
        yaml.dump(results, f, default_flow_style=False, allow_unicode=True)
    
    print("\n✅ Verification complete! Check COMPLETE_VERIFICATION_OUTPUT.txt for all formatted responses.")
    
    return results

if __name__ == "__main__":
    asyncio.run(verify_complete_catalog())
