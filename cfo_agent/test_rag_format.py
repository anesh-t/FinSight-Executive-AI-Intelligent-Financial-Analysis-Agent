"""
Test RAG formatting with direct answer
"""
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'rag_system'))

from master_agent import UnifiedCFOAgent

def test_rag_format():
    """Test RAG response format with direct answer"""
    
    print("=" * 80)
    print("TESTING RAG FORMAT WITH DIRECT ANSWER")
    print("=" * 80)
    
    # Initialize agent
    agent = UnifiedCFOAgent(verbose=False)
    
    # Test query
    query = "What were Apple's main supply chain risks in 2022?"
    
    print(f"\n📝 Query: {query}\n")
    print("🔄 Processing...\n")
    
    # Get result
    result = agent.query(query)
    
    print("=" * 80)
    print("RESPONSE:")
    print("=" * 80)
    print(result.answer)
    print("=" * 80)
    
    # Check for direct answer section
    if "📝 DIRECT ANSWER:" in result.answer:
        print("\n✅ SUCCESS: Direct answer section found!")
    else:
        print("\n⚠️  WARNING: Direct answer section not found")
    
    # Check for CFO analysis
    if any(marker in result.answer for marker in ["🔴 PRIORITY", "Strategic Impact:", "Financial Implications:"]):
        print("✅ SUCCESS: CFO analysis sections found!")
    else:
        print("⚠️  WARNING: CFO analysis sections not found")
    
    print(f"\n📊 Intent: {result.intent}")
    print(f"⏱️  Latency: {result.latency:.2f}s")
    print(f"✅ Success: {result.success}")
    
    agent.close()
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_rag_format()
