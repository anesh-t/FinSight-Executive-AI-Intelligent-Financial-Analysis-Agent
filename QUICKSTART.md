# 🚀 Quick Start Guide - CFO Assistant Agent

## ⚡ Get Running in 3 Steps

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Update Database Password

Edit `.env` file and replace `[YOUR_PASSWORD]` with your Supabase database password:

```env
SUPABASE_DB_URL=postgresql://postgres:YOUR_ACTUAL_PASSWORD@db.ikhrfgywojsrvxgdojxd.supabase.co:5432/postgres
```

**Where to find your password:**
1. Go to https://ikhrfgywojsrvxgdojxd.supabase.co
2. Settings → Database
3. Copy the password from the connection string

### Step 3: Test & Run

```bash
# Test connection
python test_connection.py

# Launch dashboard
streamlit run app.py
```

## 🎯 Try These Queries

Once the dashboard opens, click "Initialize CFO Assistant" then try:

1. **"Compare Apple's revenue growth and stock return since 2020"**
2. **"Show GDP and CPI trends alongside Meta's operating margin"**
3. **"Visualize debt-to-equity ratios across all companies for 2023"**
4. **"Which quarters were most impacted by COVID-19 for Amazon?"**
5. **"Plot Apple's ROE vs. Fed Funds rate over time"**

## 📊 What You'll Get

Each query returns:
- 📋 **Executive Summary** - Quick overview
- 📊 **Visualization** - Beautiful Plotly chart with company colors
- 💼 **CFO Narrative** - Detailed analysis
- 📑 **Data Table** - Raw data (downloadable)

## 🐛 Troubleshooting

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Database connection failed"
- Make sure you updated the password in `.env`
- Run: `python test_connection.py` to diagnose

### "OpenAI API error"
- Verify your API key in `.env`
- Check you have credits at https://platform.openai.com/

---

**Ready to analyze!** 🎉

For full documentation, see `README.md`
