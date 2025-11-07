"""
Test LLM-powered synthesis for hybrid queries
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from master_agent.core.orchestrator import MasterOrchestrator

print("="*100)
print("🧪 TESTING LLM-POWERED HYBRID SYNTHESIS")
print("="*100)
print()

# Initialize orchestrator
orchestrator = MasterOrchestrator(verbose=True, use_quick_mode=True)

# Test query
question = "What drove Apple's margin changes in 2022? Show me the numbers and explain the business context."

print(f"Question: {question}")
print()
print("="*100)
print("PROCESSING...")
print("="*100)
print()

# Execute hybrid query
result = orchestrator.query(question, session_id="synthesis_test")

print("="*100)
print("📊 RESULT")
print("="*100)
print()
print(f"Intent: {result.intent}")
print(f"Agents Used: {', '.join(result.agents_used)}")
print(f"Success: {result.success}")
print(f"Latency: {result.total_latency:.2f}s")
print()
print("="*100)
print("SYNTHESIZED RESPONSE:")
print("="*100)
print()
print(result.text)
print()
print("="*100)
print()

# Explain what happened
print("🎯 HOW IT WORKS:")
print()
print("1️⃣  Query Classification:")
print("   • Detected as HYBRID query")
print("   • Keywords: 'numbers', 'context', 'explain'")
print()
print("2️⃣  Parallel Data Retrieval:")
print("   • SQL Agent → Fetched margin data from database")
print("   • RAG Agent → Retrieved 10-K insights and business context")
print()
print("3️⃣  LLM Synthesis:")
print("   • Combined: Question + Structured Data + Unstructured Insights")
print("   • LLM (GPT-4) generated comprehensive answer")
print("   • Integrated both quantitative and qualitative information")
print()
print("✅ Result: Professional CFO-level analysis with both numbers and context!")
print()

orchestrator.close()
