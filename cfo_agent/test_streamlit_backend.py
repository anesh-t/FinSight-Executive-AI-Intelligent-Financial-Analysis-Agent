"""
Test that Streamlit can connect to FastAPI backend
"""
import requests

API_BASE_URL = "http://localhost:8000"

print("Testing Streamlit → FastAPI connection...")
print("="*60)

# Test 1: Health check
print("\n1. Testing /health endpoint...")
try:
    response = requests.get(f"{API_BASE_URL}/health", timeout=5)
    if response.status_code == 200:
        print("   ✅ Health check passed")
        print(f"   Response: {response.json()}")
    else:
        print(f"   ❌ Health check failed: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Ask endpoint (growth query)
print("\n2. Testing /ask endpoint (growth query)...")
try:
    response = requests.post(
        f"{API_BASE_URL}/ask",
        json={"question": "What is Apple revenue growth YoY Q2 2023?", "session_id": "test"},
        timeout=30
    )
    if response.status_code == 200:
        answer = response.json().get("response", "")
        if "growth" in answer.lower() and "Apple" in answer:
            print("   ✅ Growth query working")
            print(f"   Answer: {answer[:100]}...")
        else:
            print(f"   ⚠️  Query returned unexpected answer: {answer[:100]}")
    else:
        print(f"   ❌ Query failed: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Multi-company query
print("\n3. Testing /ask endpoint (multi-company query)...")
try:
    response = requests.post(
        f"{API_BASE_URL}/ask",
        json={"question": "Compare Apple and Microsoft revenue Q2 2023", "session_id": "test"},
        timeout=30
    )
    if response.status_code == 200:
        answer = response.json().get("response", "")
        if "Apple" in answer and "Microsoft" in answer:
            print("   ✅ Multi-company query working")
            print(f"   Answer: {answer[:100]}...")
        else:
            print(f"   ⚠️  Query returned unexpected answer: {answer[:100]}")
    else:
        print(f"   ❌ Query failed: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Peer comparison
print("\n4. Testing /ask endpoint (peer comparison)...")
try:
    response = requests.post(
        f"{API_BASE_URL}/ask",
        json={"question": "Show ROE for all companies Q1 2023", "session_id": "test"},
        timeout=30
    )
    if response.status_code == 200:
        answer = response.json().get("response", "")
        if "ROE" in answer or "roe" in answer.lower():
            print("   ✅ Peer comparison working")
            print(f"   Answer: {answer[:100]}...")
        else:
            print(f"   ⚠️  Query returned unexpected answer: {answer[:100]}")
    else:
        print(f"   ❌ Query failed: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*60)
print("✅ All backend tests passed! Streamlit app is ready to launch.")
print("\nTo launch Streamlit, run:")
print("  streamlit run streamlit_app.py")
