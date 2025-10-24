"""
Router evaluation script
Tests routing accuracy against golden prompts
"""
import asyncio
import json
import yaml
from decomposer import QueryDecomposer
from router import IntentRouter


async def evaluate_router():
    """Evaluate router against golden prompts"""
    
    # Load golden prompts
    with open('tests/golden_prompts.yaml', 'r') as f:
        golden = yaml.safe_load(f)
    
    decomposer = QueryDecomposer()
    router = IntentRouter()
    
    results = []
    correct = 0
    total = 0
    
    print("\n" + "="*80)
    print("ROUTER EVALUATION")
    print("="*80)
    
    for prompt_spec in golden['prompts']:
        name = prompt_spec['name']
        question = prompt_spec['question']
        expected_intent = prompt_spec.get('expected_intent')
        expected_surface = prompt_spec.get('expected_surface')
        
        print(f"\n{name}:")
        print(f"  Question: {question}")
        
        try:
            # Decompose
            decomposed = await decomposer.decompose(question)
            tasks = decomposed.get('tasks', [])
            
            if not tasks:
                print(f"  ❌ No tasks generated")
                results.append({'name': name, 'passed': False, 'reason': 'No tasks'})
                total += 1
                continue
            
            # Route first task
            routed = router.route_task(tasks[0])
            actual_intent = routed['intent']
            actual_surfaces = routed['surfaces']
            
            print(f"  Expected: {expected_intent} → {expected_surface}")
            print(f"  Actual:   {actual_intent} → {', '.join(actual_surfaces)}")
            
            # Check if correct
            intent_match = actual_intent == expected_intent
            surface_match = expected_surface in ', '.join(actual_surfaces) if expected_surface else True
            
            if intent_match and surface_match:
                print(f"  ✅ PASSED")
                correct += 1
                results.append({'name': name, 'passed': True})
            else:
                print(f"  ❌ FAILED")
                results.append({
                    'name': name,
                    'passed': False,
                    'expected': expected_intent,
                    'actual': actual_intent
                })
            
            total += 1
            
        except Exception as e:
            print(f"  ❌ ERROR: {str(e)}")
            results.append({'name': name, 'passed': False, 'error': str(e)})
            total += 1
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Passed: {correct}/{total} ({correct/total*100:.1f}%)")
    print(f"Failed: {total - correct}/{total}")
    
    # Save results
    with open('tests/router_eval_results.json', 'w') as f:
        json.dump({
            'total': total,
            'correct': correct,
            'accuracy': correct/total if total > 0 else 0,
            'results': results
        }, f, indent=2)
    
    print(f"\nResults saved to: cfo_agent/tests/router_eval_results.json")
    
    return correct/total if total > 0 else 0


if __name__ == "__main__":
    accuracy = asyncio.run(evaluate_router())
    print(f"\n🎯 Router Accuracy: {accuracy*100:.1f}%")
