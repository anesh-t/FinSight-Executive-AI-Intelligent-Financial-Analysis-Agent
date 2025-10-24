#!/bin/bash

# CFO Agent UI Launcher
# Starts both the FastAPI backend and Streamlit frontend

echo "🚀 CFO Intelligence Assistant Launcher"
echo "======================================"
echo ""

# Check if API server is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API server is already running at http://localhost:8000"
else
    echo "🔧 Starting API server..."
    python app.py &
    API_PID=$!
    echo "   API server PID: $API_PID"
    
    # Wait for API to be ready
    echo "   Waiting for API to be ready..."
    for i in {1..10}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo "   ✅ API server is ready!"
            break
        fi
        sleep 1
    done
fi

echo ""
echo "🎨 Starting Streamlit UI..."
echo "   UI will open at http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Start Streamlit
streamlit run streamlit_app.py

# Cleanup on exit
trap "kill $API_PID 2>/dev/null" EXIT
