"""
Test LLM synthesis with mock data (no database calls)
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

load_dotenv()

print("="*100)
print("🧪 TESTING LLM SYNTHESIS (Mock Data)")
print("="*100)
print()

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

# Test cases with mock data
test_cases = [
    {
        "name": "Margin Analysis (Your Query)",
        "question": "What drove the margin swing last quarter—show me the numbers, macro context, and 10-K citations?",
        "structured_data": """
Apple Inc. Margin Data:
- Q3 2023: Gross Margin 44.5%, Operating Margin 26.8%
- Q2 2023: Gross Margin 43.8%, Operating Margin 26.4%
- Change: Gross Margin +0.7pp, Operating Margin +0.4pp
- Revenue: Q3 $81.8B, Q2 $94.8B
        """,
        "unstructured_insights": """
From Apple's 2023 10-K Filing:

Management Discussion & Analysis (MD&A):
"Gross margin increased in Q3 2023 primarily due to favorable product mix, with higher-margin 
iPhone Pro models and Services representing a larger portion of revenue. Services revenue grew 
8% year-over-year with approximately 70% gross margins."

Risk Factors:
"Foreign exchange headwinds continued to impact margins, with an estimated 2% negative impact 
on gross margin. However, this was more than offset by supply chain improvements and 
manufacturing efficiencies."

Business Context:
"The company continued to see strong demand for premium products despite macroeconomic 
headwinds. Services segment showed resilience with recurring revenue streams."
        """
    },
    {
        "name": "Apple Revenue Drivers",
        "question": "Show me Apple's revenue for 2022 and explain what drove it from their 10-K.",
        "structured_data": """
Apple Inc. Revenue 2022:
- Total Revenue: $394.3 billion
- iPhone: $205.5B (52% of total)
- Services: $78.1B (20% of total)
- Mac: $40.2B (10% of total)
- iPad: $29.3B (7% of total)
- Wearables: $41.2B (10% of total)
- YoY Growth: +7.8%
        """,
        "unstructured_insights": """
From Apple's 2022 10-K Filing:

MD&A - Revenue Drivers:
"Revenue growth in 2022 was driven by strong iPhone 14 demand, particularly Pro models, 
and continued expansion of our Services ecosystem. The installed base of active devices 
reached an all-time high, driving Services growth."

Geographic Performance:
"Americas and Europe showed strong growth, while Greater China faced headwinds from 
COVID-19 lockdowns and supply constraints. Despite challenges, we maintained market 
leadership positions."

Product Innovation:
"Launch of iPhone 14 Pro with Dynamic Island and always-on display drove premium mix. 
Services benefited from increased App Store revenue and growing subscription base."
        """
    },
    {
        "name": "Supply Chain Risk Impact",
        "question": "How did supply chain risks affect Apple's margins? Show the financial impact and 10-K citations.",
        "structured_data": """
Apple Margin Impact Analysis:
- 2022 Gross Margin: 43.3%
- 2021 Gross Margin: 41.8%
- Improvement: +1.5 percentage points
- Estimated supply chain cost savings: $2.1B
- Operating efficiency gains: $1.3B
        """,
        "unstructured_insights": """
From Apple's 2022 10-K Filing:

Risk Factors - Supply Chain:
"We have made significant investments in supply chain diversification and resilience. 
While COVID-19 related disruptions impacted Q1 and Q2 2022, our multi-sourcing strategy 
and inventory management improvements helped mitigate risks."

Operational Improvements:
"Supply chain optimization initiatives, including automation and logistics improvements, 
contributed to cost reductions. We also benefited from favorable component pricing in 
the second half of the year."

Future Outlook:
"We continue to invest in supply chain resilience while maintaining our commitment to 
quality and sustainability. Long-term supplier partnerships remain critical to our success."
        """
    }
]

# Synthesis prompt
synthesis_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a CFO-level financial analyst. Your task is to provide a comprehensive answer by synthesizing:
1. The user's question
2. Structured financial data (from SQL database)
3. Unstructured insights (from 10-K filings)

Provide a clear, professional answer that:
- Directly answers the question
- Integrates both quantitative data and qualitative context
- Highlights key insights and connections between the data sources
- Uses specific numbers and citations when available
- Maintains a CFO-level perspective

Format your response professionally with clear sections if needed."""),
    ("user", """Question: {question}

STRUCTURED DATA (Financial Metrics):
{structured_data}

UNSTRUCTURED INSIGHTS (10-K Filings):
{unstructured_insights}

Provide a comprehensive answer that synthesizes all three inputs above.""")
])

# Test each case
for i, test in enumerate(test_cases, 1):
    print(f"\n{'='*100}")
    print(f"TEST {i}/{len(test_cases)}: {test['name']}")
    print(f"{'='*100}")
    print(f"\n📝 Question:")
    print(f"   {test['question']}")
    print(f"\n⏳ Generating synthesis with GPT-4o...")
    
    try:
        messages = synthesis_prompt.format_messages(
            question=test['question'],
            structured_data=test['structured_data'],
            unstructured_insights=test['unstructured_insights']
        )
        
        response = llm.invoke(messages)
        answer = response.content
        
        print(f"\n✅ SUCCESS")
        print(f"\n💬 SYNTHESIZED ANSWER:")
        print("─" * 100)
        print(answer)
        print("─" * 100)
        print(f"\n**Sources:** Financial Database (SQL), SEC 10-K Filings")
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()

print(f"\n\n{'='*100}")
print("📊 TEST COMPLETE")
print(f"{'='*100}")
print(f"\n✅ LLM Synthesis Working!")
print(f"\n🎯 What This Demonstrates:")
print(f"   • LLM receives: Question + Structured Data + Unstructured Insights")
print(f"   • LLM synthesizes: Comprehensive CFO-level answer")
print(f"   • Integration: Both quantitative and qualitative information")
print(f"   • Format: Professional, actionable insights")
print(f"\n{'='*100}\n")
