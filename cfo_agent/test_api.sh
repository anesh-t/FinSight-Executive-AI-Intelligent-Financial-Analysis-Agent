#!/bin/bash

# CFO Agent API Test Script

BASE_URL="http://localhost:8000"

echo "🧪 CFO Agent API Tests"
echo "======================"
echo ""

# Test 1: Health check
echo "Test 1: Health Check"
echo "--------------------"
curl -s $BASE_URL/health | python3 -m json.tool
echo ""
echo ""

# Test 2: Simple query
echo "Test 2: Simple Query (AAPL latest quarter)"
echo "-------------------------------------------"
curl -s -X POST $BASE_URL/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Show AAPL latest quarter revenue and ROE"}' \
  | python3 -m json.tool
echo ""
echo ""

# Test 3: Annual metrics
echo "Test 3: Annual Metrics (MSFT FY 2023)"
echo "--------------------------------------"
curl -s -X POST $BASE_URL/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What were Microsoft revenue and net income in FY 2023?"}' \
  | python3 -m json.tool
echo ""
echo ""

# Test 4: Growth analysis
echo "Test 4: Growth Analysis (AAPL QoQ/YoY)"
echo "---------------------------------------"
curl -s -X POST $BASE_URL/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Latest quarter revenue QoQ and YoY for AAPL"}' \
  | python3 -m json.tool
echo ""
echo ""

# Test 5: Peer comparison
echo "Test 5: Peer Comparison (Net Margin Leaders)"
echo "---------------------------------------------"
curl -s -X POST $BASE_URL/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Who led on net margin last quarter? show ranks"}' \
  | python3 -m json.tool
echo ""
echo ""

# Test 6: Session context
echo "Test 6: Session Context"
echo "-----------------------"
curl -s $BASE_URL/session/test123/context | python3 -m json.tool
echo ""
echo ""

echo "✅ All tests complete!"
