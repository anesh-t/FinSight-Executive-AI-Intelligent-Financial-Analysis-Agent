"""Test full flow including planner"""
import asyncio
from decomposer import QueryDecomposer
from router import IntentRouter
from planner import TaskPlanner

async def test_full_flow():
    decomposer = QueryDecomposer()
    router = IntentRouter()
    planner = TaskPlanner()
    
    query = "show closing stock price for apple and microsoft for year 2023"
    
    print(f"Query: {query}\n")
    
    # Step 1: Decompose
    decomposed = await decomposer.decompose(query)
    tasks = decomposed.get('tasks', [])
    print(f"Step 1 - Decomposed tasks: {len(tasks)}")
    for task in tasks:
        print(f"  - Intent: {task.get('intent')}, Entities: {task.get('entities')}")
    
    # Step 2: Route
    routed_tasks = router.route_all_tasks(tasks)
    print(f"\nStep 2 - Routed tasks: {len(routed_tasks)}")
    for task in routed_tasks:
        print(f"  - Intent: {task.get('intent')}, Entities: {task.get('entities')}")
    
    # Step 3: Plan
    plans = []
    for routed_task in routed_tasks:
        plan = await planner.plan_task(routed_task)
        plans.append(plan)
    
    print(f"\nStep 3 - Plans: {len(plans)}")
    for i, plan in enumerate(plans):
        print(f"  Plan {i+1}:")
        print(f"    - Intent: {plan.get('intent')}")
        print(f"    - Entities resolved: {plan.get('entities_resolved')}")
        print(f"    - SQL params: {plan.get('params')}")

if __name__ == "__main__":
    asyncio.run(test_full_flow())
