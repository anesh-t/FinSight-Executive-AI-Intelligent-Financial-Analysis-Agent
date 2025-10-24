"""
Quick connection test script for CFO Assistant Agent.
Run this to verify all components are properly configured.
"""

import os
import sys
from dotenv import load_dotenv

def test_environment_variables():
    """Test if all required environment variables are set."""
    print("🔍 Testing Environment Variables...")
    print("-" * 60)
    
    load_dotenv()
    
    required_vars = [
        'OPENAI_API_KEY',
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'SUPABASE_DB_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'KEY' in var or 'URL' in var:
                masked = value[:10] + '...' if len(value) > 10 else '***'
                print(f"✅ {var}: {masked}")
            else:
                print(f"✅ {var}: Set")
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    print()
    if missing_vars:
        print(f"⚠️  Missing variables: {', '.join(missing_vars)}")
        print("Please configure these in your .env file")
        return False
    else:
        print("✅ All environment variables configured!")
        return True


def test_imports():
    """Test if all required packages are installed."""
    print("\n🔍 Testing Package Imports...")
    print("-" * 60)
    
    packages = {
        'langchain': 'LangChain',
        'langchain_openai': 'LangChain OpenAI',
        'langchain_community': 'LangChain Community',
        'openai': 'OpenAI',
        'pandas': 'Pandas',
        'plotly': 'Plotly',
        'streamlit': 'Streamlit',
        'sqlalchemy': 'SQLAlchemy',
        'supabase': 'Supabase',
        'dotenv': 'Python Dotenv'
    }
    
    failed_imports = []
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name}")
            failed_imports.append(package)
    
    print()
    if failed_imports:
        print(f"⚠️  Missing packages: {', '.join(failed_imports)}")
        print("Install with: pip install -r requirements.txt")
        return False
    else:
        print("✅ All packages installed!")
        return True


def test_database_connection():
    """Test Supabase database connection."""
    print("\n🔍 Testing Database Connection...")
    print("-" * 60)
    
    try:
        from database import SupabaseConnector
        
        connector = SupabaseConnector()
        print("✅ Database connector initialized")
        
        # Test connection
        if connector.test_connection():
            print("✅ Database connection successful!")
            
            # Try a simple query
            result = connector.execute_query("SELECT 1 as test")
            if not result.empty:
                print("✅ Query execution successful!")
                return True
            else:
                print("❌ Query returned empty result")
                return False
        else:
            print("❌ Database connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


def test_openai_connection():
    """Test OpenAI API connection."""
    print("\n🔍 Testing OpenAI Connection...")
    print("-" * 60)
    
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        print("✅ OpenAI client initialized")
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Say 'test successful'"}],
            max_tokens=10
        )
        
        if response.choices[0].message.content:
            print("✅ OpenAI API connection successful!")
            return True
        else:
            print("❌ OpenAI API returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI test failed: {e}")
        return False


def test_cfo_assistant():
    """Test CFO Assistant initialization."""
    print("\n🔍 Testing CFO Assistant...")
    print("-" * 60)
    
    try:
        from cfo_assistant import CFOAssistant
        
        cfo = CFOAssistant(verbose=False)
        print("✅ CFO Assistant initialized successfully!")
        
        # Test components
        if cfo.db_connector:
            print("✅ Database connector loaded")
        if cfo.visualizer:
            print("✅ Visualizer loaded")
        if cfo.llm:
            print("✅ LLM loaded")
        if cfo.agent:
            print("✅ LangChain agent loaded")
        
        return True
        
    except Exception as e:
        print(f"❌ CFO Assistant test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("CFO ASSISTANT - CONNECTION TEST")
    print("=" * 60)
    print()
    
    results = {
        'Environment Variables': test_environment_variables(),
        'Package Imports': test_imports(),
        'Database Connection': test_database_connection(),
        'OpenAI Connection': test_openai_connection(),
        'CFO Assistant': test_cfo_assistant()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print()
    
    all_passed = all(results.values())
    if all_passed:
        print("🎉 All tests passed! Your CFO Assistant is ready to use.")
        print("\nNext steps:")
        print("1. Run the dashboard: streamlit run app.py")
        print("2. Or try examples: python example_usage.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("1. Check your .env file configuration")
        print("2. Install missing packages: pip install -r requirements.txt")
        print("3. Verify your Supabase database is accessible")
        print("4. Verify your OpenAI API key is valid")
        print("5. Make sure to replace [YOUR_PASSWORD] in SUPABASE_DB_URL")
    
    print()
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
