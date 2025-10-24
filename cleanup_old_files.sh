#!/bin/bash

# CFO Agent Cleanup Script
# Moves old implementation files to backup directory

echo "🧹 CFO Agent Cleanup Script"
echo "==========================="
echo ""

# Check if we're in the right directory
if [ ! -d "cfo_agent" ]; then
    echo "❌ Error: cfo_agent/ directory not found"
    echo "   Please run this script from the project root"
    exit 1
fi

# Create backup directory
echo "📁 Creating backup directory..."
mkdir -p old_implementation
echo "✅ Created: old_implementation/"
echo ""

# List of files to move
OLD_FILES=(
    "app.py"
    "cfo_agent_graph.py"
    "cfo_assistant.py"
    "example_usage.py"
    "visualizations.py"
    "test_connection.py"
    "test_views.py"
    "ff.py"
)

echo "🗑️  Moving old files to backup..."
echo ""

MOVED_COUNT=0
MISSING_COUNT=0

for file in "${OLD_FILES[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" old_implementation/
        echo "  ✅ Moved: $file"
        ((MOVED_COUNT++))
    else
        echo "  ⚠️  Not found: $file (skipping)"
        ((MISSING_COUNT++))
    fi
done

echo ""
echo "📊 Summary:"
echo "   Moved: $MOVED_COUNT files"
echo "   Missing: $MISSING_COUNT files"
echo ""

# Update requirements.txt
if [ -f "cfo_agent/requirements.txt" ]; then
    echo "📝 Updating requirements.txt..."
    cp cfo_agent/requirements.txt requirements.txt
    echo "✅ Updated: requirements.txt"
    echo ""
fi

# Show what's in backup
echo "📦 Backup directory contents:"
ls -lh old_implementation/
echo ""

echo "✅ Cleanup complete!"
echo ""
echo "📌 Next steps:"
echo "   1. Test the new agent: cd cfo_agent && python app.py"
echo "   2. If everything works, delete backup: rm -rf old_implementation/"
echo "   3. Update README.md to point to cfo_agent/"
echo ""
echo "⚠️  The old files are in: old_implementation/"
echo "   You can restore them if needed or delete when confident"
