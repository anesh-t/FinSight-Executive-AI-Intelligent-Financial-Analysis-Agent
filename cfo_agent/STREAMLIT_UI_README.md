# 💼 CFO Intelligence Assistant - Streamlit UI

## 🎨 Perplexity-Style Chatbot Interface

A beautiful, conversational interface for the CFO Agent, inspired by Perplexity AI.

---

## ✨ Features

### **💬 Chat Interface**
- Clean, dark-themed UI similar to Perplexity
- Real-time conversational experience
- Message history with user/assistant distinction
- Markdown rendering for formatted responses

### **📊 Session Management**
- Persistent session tracking
- View recent tickers and query count
- Clear chat history
- Session context retention

### **💡 Example Queries**
- 8 pre-built example queries
- One-click to try common financial questions
- Covers: snapshots, growth, peers, macro, comparisons

### **⚙️ Settings**
- Enable/disable Human-in-the-Loop approval
- Clear chat functionality
- Session information display

---

## 🚀 Quick Start

### **Option 1: Launch Script (Recommended)**

```bash
chmod +x launch_ui.sh
./launch_ui.sh
```

This will:
1. Start the FastAPI backend (if not running)
2. Launch the Streamlit UI
3. Open browser at `http://localhost:8501`

### **Option 2: Manual Launch**

```bash
# Terminal 1: Start API server
python app.py

# Terminal 2: Start Streamlit UI
streamlit run streamlit_app.py
```

---

## 🎯 How to Use

### **1. Ask Questions**

Type natural language questions in the chat input:

**Examples:**
- "Show AAPL latest quarter revenue and ROE"
- "Who led on net margin last quarter?"
- "Compare Apple and Google ROE in 2023"
- "What's Amazon's 5-year revenue CAGR?"

### **2. Use Example Queries**

Click any example button in the sidebar:
- 📈 Quarter Snapshot
- 📊 Growth Analysis
- 🏆 Peer Rankings
- 🌍 Macro Analysis
- 💰 Annual Metrics
- 📉 CAGR
- ⚖️ Comparison
- 🔍 Health Check

### **3. View Session Info**

The sidebar shows:
- Session ID
- Number of queries
- Recently queried tickers

### **4. Clear Chat**

Click "🗑️ Clear Chat" to:
- Reset the conversation
- Clear session memory
- Start fresh

---

## 🎨 UI Features

### **Dark Theme**
- Perplexity-inspired dark color scheme
- Easy on the eyes for long sessions
- Professional financial interface

### **Message Styling**
- User messages: Dark blue background
- Assistant messages: Darker background with blue left border
- Code blocks: Syntax highlighting
- Tables: Formatted data display

### **Responsive Layout**
- Wide layout for better data visibility
- Sidebar for navigation and examples
- Full-width chat area

---

## 📊 Example Queries & Expected Responses

### **1. Quarter Snapshot**
**Query:** "Show AAPL latest quarter revenue, gross margin, and ROE"

**Response:**
- Compact table with metrics
- 2-3 CFO insights (growth, rankings, GP status)
- Sources citation

### **2. Peer Rankings**
**Query:** "Who led on net margin last quarter? show ranks"

**Response:**
- Table with all companies ranked
- Percentiles and z-scores
- Leader identification

### **3. Growth Analysis**
**Query:** "Latest quarter revenue QoQ and YoY for MSFT"

**Response:**
- QoQ and YoY growth percentages
- Trend analysis
- Historical context

### **4. Comparison**
**Query:** "Compare Apple and Google ROE in 2023"

**Response:**
- Side-by-side comparison table
- Winner identification
- Performance insights

---

## 🔧 Configuration

### **API Endpoint**

Edit `streamlit_app.py` line 93:
```python
API_BASE_URL = "http://localhost:8000"
```

### **Theme Customization**

Modify the CSS in `streamlit_app.py` lines 16-80 to customize:
- Colors
- Fonts
- Spacing
- Button styles

### **Example Queries**

Add/modify examples in `streamlit_app.py` lines 63-72:
```python
examples = {
    "Your Label": "Your query here",
    ...
}
```

---

## 🐛 Troubleshooting

### **"Cannot connect to CFO Agent API"**

**Solution:**
1. Check if API server is running: `curl http://localhost:8000/health`
2. Start API server: `python app.py`
3. Refresh Streamlit page

### **"Request timed out"**

**Solution:**
- Query might be too complex
- Try a simpler question
- Check API server logs

### **Blank responses**

**Solution:**
- Check API server is running
- Verify database connection
- Check `.env` file has correct credentials

### **Styling issues**

**Solution:**
- Clear Streamlit cache: `streamlit cache clear`
- Restart Streamlit: `Ctrl+C` then `streamlit run streamlit_app.py`

---

## 📝 Files

- **`streamlit_app.py`** - Main Streamlit application
- **`launch_ui.sh`** - Launch script for both servers
- **`STREAMLIT_UI_README.md`** - This file

---

## 🎯 Keyboard Shortcuts

- **Enter** - Send message
- **Shift+Enter** - New line in input
- **Ctrl+C** - Stop servers (in terminal)

---

## 🚀 Advanced Usage

### **Custom Session ID**

Modify session ID generation in `streamlit_app.py` line 104:
```python
st.session_state.session_id = "your-custom-id"
```

### **Enable HITL by Default**

Set default in `streamlit_app.py` line 87:
```python
enable_hitl = st.checkbox("Enable Human-in-the-Loop", value=True)
```

### **Add More Metrics**

The sidebar can display additional metrics from session context.

---

## 📊 Screenshots

### **Main Chat Interface**
- Dark theme with blue accents
- Clean message bubbles
- Markdown-formatted responses

### **Sidebar**
- Session information
- 8 example queries
- Settings and controls

---

## ✅ Checklist

Before using:
- [ ] API server running at `http://localhost:8000`
- [ ] Streamlit installed (`pip install streamlit`)
- [ ] `.env` file configured with API keys
- [ ] Database connection working

---

## 🎉 Summary

**The Streamlit UI provides:**
- ✅ Beautiful Perplexity-style interface
- ✅ Real-time conversational experience
- ✅ Session management
- ✅ Example queries for quick testing
- ✅ Dark theme optimized for financial data
- ✅ Full integration with CFO Agent API

**Access the UI at:** `http://localhost:8501`

---

**Built with Streamlit + FastAPI + LangGraph + GPT-4o** 🚀
