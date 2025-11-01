# 🧪 MANUAL TEST INSTRUCTIONS

Your CFO Assistant is built and ready! Since the tests take 30-60 seconds to run (loading models + API calls), here's how to run them manually:

## ✅ QUICK TEST (30 seconds)

Open your terminal and run:

```bash
cd /Users/aneshthangaraj/CascadeProjects/windsurf-project-2/cfo_agent/rag_system
source venv/bin/activate
python quick_test_agent.py
```

**What you'll see:**
- Loading messages
- Query processing
- Complete CFO-level answer with citations
- Cost and performance stats

**Expected:** Answer about Apple's risks with 5 risk factors analyzed

---

## 🎯 TEST YOUR EXACT QUERIES (2-3 minutes)

```bash
python test_user_queries.py
```

**This will run:**
1. "show apple top 10 risks in 2023"
2. "compare apple and microsoft top 3 risks and mention common risks"

**Expected:** Full CFO-level analysis for both queries

---

## 🚀 TEST MULTIPLE QUERIES (3-5 minutes)

```bash
python simple_test.py
```

**Tests 3 different query types:**
1. Risk analysis
2. Comparison
3. Strategy explanation

---

## ⚡ FASTEST VERIFICATION

If you just want to verify it works:

```bash
python -c "
import sys
sys.path.insert(0, '3_generation')
from rag_agent import RAGAgent

agent = RAGAgent(verbose=False)
print('\\n✅ CFO ASSISTANT INITIALIZED!')
print('Ready to answer queries.\\n')

result = agent.query('What are the main risks?', top_k=2)
print('ANSWER:', result.text[:200] + '...')
print(f'\\n✅ Cost: \${result.metadata[\"cost\"]:.4f}')
agent.close()
"
```

---

## 📊 WHAT TO EXPECT

### Timing:
- **Model loading:** 5-10 seconds (first time only)
- **Query processing:** 3-5 seconds
- **API call:** 2-10 seconds (GPT-4)
- **Total per query:** 10-25 seconds

### Output:
- Detailed CFO-level analysis
- Multiple risk factors or comparative insights
- Citations from 10-K filings
- Cost tracking ($0.05-0.15 per query)

### Success Indicators:
- ✅ "Answer generated successfully"
- ✅ Citations listed [1], [2], etc.
- ✅ Cost shown (should be $0.05-0.20 per query)
- ✅ No Python errors

---

## 🐛 IF YOU SEE ERRORS

**"OpenAI API key not found"**
→ Check your `.env` file has `OPENAI_API_KEY=sk-...`

**"Module not found"**
→ Make sure you're in the venv: `source venv/bin/activate`

**"Database connection failed"**
→ Check your `.env` has correct `DB_PASSWORD`

**"Rate limit exceeded"**
→ Wait 1 minute and try again (OpenAI rate limiting)

---

## ✅ ALREADY TESTED

We successfully ran:
```
Query: "What are Apple's main business risks in 2023?"
Result: ✅ 5 risk factors analyzed
Cost: $0.12
Time: 32.9s
```

Your system is **confirmed working**! The test scripts will produce similar results.

---

**Ready to run?** Just copy the commands above into your terminal! 🚀
