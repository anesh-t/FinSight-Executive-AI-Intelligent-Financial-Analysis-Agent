# Cleanup Guide - Old vs New Files

## 🗑️ Files to DELETE (Old Implementation)

### **Old Agent Files (Replace with new cfo_agent/)**
- ❌ `app.py` - Old Streamlit app (replaced by `cfo_agent/app.py` FastAPI)
- ❌ `cfo_agent_graph.py` - Old LangGraph implementation (replaced by `cfo_agent/graph.py`)
- ❌ `cfo_assistant.py` - Old LangChain agent (replaced by new modular design)
- ❌ `example_usage.py` - Old usage examples (replaced by `cfo_agent/tests/`)
- ❌ `visualizations.py` - Old Plotly visualizations (not needed in API-first design)
- ❌ `test_connection.py` - Old connection test (replaced by `cfo_agent/app.py` health checks)
- ❌ `test_views.py` - Old view tests (replaced by `cfo_agent/tests/`)
- ❌ `ff.py` - Unknown/temporary file

### **Old Database Files (Keep database.py for backward compatibility)**
- ⚠️ `database.py` - Keep for now (used by migration scripts)

### **Migration Scripts (Keep - Still Useful)**
- ✅ `db_migration.py` - Keep (Prompts 1-3)
- ✅ `db_migration_part2.py` - Keep (Prompts 4-6)
- ✅ `db_migration_advanced.py` - Keep (Prompts A-H)
- ✅ `db_migration_governance.py` - Keep (Prompts 1-5)

### **Validation Scripts (Keep - Still Useful)**
- ✅ `validate_complete_migration.py` - Keep
- ✅ `validate_schema.py` - Keep
- ✅ `verify_advanced.py` - Keep
- ✅ `verify_governance.py` - Keep
- ✅ `verify_migration.py` - Keep

### **Documentation (Keep - Reference Material)**
- ✅ `MIGRATION_SUMMARY.md` - Keep
- ✅ `ADVANCED_MIGRATION_SUMMARY.md` - Keep
- ✅ `GOVERNANCE_MIGRATION_SUMMARY.md` - Keep
- ✅ `COMPLETE_MIGRATION_STATUS.md` - Keep
- ✅ `FINAL_VALIDATION_REPORT.md` - Keep
- ✅ `SCHEMA_VALIDATION_REPORT.md` - Keep
- ✅ `MODEL_UPGRADE_SUMMARY.md` - Keep
- ✅ `CFO_AGENT_IMPLEMENTATION_SUMMARY.md` - Keep (new)
- ✅ `QUICKSTART.md` - Keep
- ✅ `RATE_LIMIT_INFO.md` - Keep
- ✅ `README.md` - Update to point to new agent

### **Configuration Files (Keep)**
- ✅ `.env` - Keep (contains credentials)
- ✅ `.gitignore` - Keep
- ✅ `requirements.txt` - Update to match `cfo_agent/requirements.txt`

---

## ✅ Files to KEEP (New Implementation)

### **New CFO Agent (All files in cfo_agent/)**
- ✅ `cfo_agent/` - Entire directory (29 files)
  - All Python modules
  - All prompts
  - All templates
  - All tests
  - All documentation

### **Database & Migrations**
- ✅ `database.py` - Keep for backward compatibility
- ✅ All `db_migration_*.py` files
- ✅ All `validate_*.py` and `verify_*.py` files

### **Documentation**
- ✅ All `*_SUMMARY.md` files
- ✅ All `*_REPORT.md` files

---

## 🔧 Cleanup Commands

### **Safe Cleanup (Recommended)**

```bash
# Create a backup directory
mkdir -p old_implementation

# Move old files to backup
mv app.py old_implementation/
mv cfo_agent_graph.py old_implementation/
mv cfo_assistant.py old_implementation/
mv example_usage.py old_implementation/
mv visualizations.py old_implementation/
mv test_connection.py old_implementation/
mv test_views.py old_implementation/
mv ff.py old_implementation/

echo "✅ Old files moved to old_implementation/"
echo "   You can delete this directory later if everything works"
```

### **Aggressive Cleanup (Delete Permanently)**

```bash
# ⚠️ WARNING: This permanently deletes files!
rm -f app.py
rm -f cfo_agent_graph.py
rm -f cfo_assistant.py
rm -f example_usage.py
rm -f visualizations.py
rm -f test_connection.py
rm -f test_views.py
rm -f ff.py

echo "✅ Old files deleted permanently"
```

---

## 📝 Update README.md

Replace the old README.md with a pointer to the new agent:

```markdown
# CFO Assistant Project

## 🚀 New Implementation: CFO Agent

The CFO Assistant has been upgraded to a new **Structured-Only CFO Agent** with:
- LangGraph state machine
- Template-first SQL with guarded generation
- Full provenance tracking
- Human-in-the-loop approval
- Session memory

### Quick Start

See the new implementation in `cfo_agent/`:

\`\`\`bash
cd cfo_agent
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
python app.py
\`\`\`

### Documentation

- **[CFO Agent README](cfo_agent/README.md)** - Complete user guide
- **[Build Specification](cfo_agent/CFO_AGENT_BUILD_SPEC.md)** - Technical details
- **[Implementation Summary](CFO_AGENT_IMPLEMENTATION_SUMMARY.md)** - What was built

### Database Migrations

All database migrations are complete. See:
- `COMPLETE_MIGRATION_STATUS.md` - Full migration summary
- `FINAL_VALIDATION_REPORT.md` - Validation results
- `SCHEMA_VALIDATION_REPORT.md` - Schema completeness

### Old Implementation

The old Streamlit-based implementation has been replaced. Old files are in `old_implementation/` (if you ran the safe cleanup).
```

---

## 🎯 Recommended Action Plan

### **Step 1: Backup**
```bash
mkdir -p old_implementation
mv app.py cfo_agent_graph.py cfo_assistant.py example_usage.py visualizations.py test_connection.py test_views.py ff.py old_implementation/
```

### **Step 2: Update requirements.txt**
```bash
cp cfo_agent/requirements.txt requirements.txt
```

### **Step 3: Update README.md**
Point to new `cfo_agent/` directory

### **Step 4: Test New Agent**
```bash
cd cfo_agent
python app.py
```

### **Step 5: Delete Backup (After Testing)**
```bash
# Only after confirming everything works
rm -rf old_implementation/
```

---

## 📊 Summary

### **Files to Delete: 8**
1. app.py
2. cfo_agent_graph.py
3. cfo_assistant.py
4. example_usage.py
5. visualizations.py
6. test_connection.py
7. test_views.py
8. ff.py

### **Files to Keep: Everything Else**
- ✅ cfo_agent/ (29 files)
- ✅ database.py
- ✅ All migration scripts
- ✅ All validation scripts
- ✅ All documentation
- ✅ .env, .gitignore

### **Total Cleanup: ~8 old files → Backup or Delete**

---

**Recommendation: Use the "Safe Cleanup" approach first, test the new agent, then delete the backup directory.**
