"""
Test script to validate HTML parser setup
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test all imports"""
    print("Testing imports...")
    try:
        from config import HTMLParserConfig
        print("  ✅ config.py")
        
        from html_parser import HTMLParser
        print("  ✅ html_parser.py")
        
        from table_extractor import TableExtractor
        print("  ✅ table_extractor.py")
        
        from text_rewriter import TextRewriter
        print("  ✅ text_rewriter.py")
        
        from text_chunker import TextChunker
        print("  ✅ text_chunker.py")
        
        from pipeline import HTMLToJSONPipeline
        print("  ✅ pipeline.py")
        
        return True
    except Exception as e:
        print(f"  ❌ Import error: {e}")
        return False

def test_directories():
    """Test directory creation"""
    print("\nTesting directories...")
    try:
        from config import HTMLParserConfig
        HTMLParserConfig.ensure_directories()
        
        if HTMLParserConfig.INPUT_DIR.exists():
            print(f"  ✅ Input: {HTMLParserConfig.INPUT_DIR}")
        else:
            print(f"  ❌ Input directory not found")
            return False
            
        if HTMLParserConfig.OUTPUT_DIR.exists():
            print(f"  ✅ Output: {HTMLParserConfig.OUTPUT_DIR}")
        else:
            print(f"  ❌ Output directory not created")
            return False
        
        return True
    except Exception as e:
        print(f"  ❌ Directory error: {e}")
        return False

def test_pdf_files():
    """Check for PDF files"""
    print("\nChecking for PDF files...")
    try:
        from config import HTMLParserConfig
        
        pdf_files = list(HTMLParserConfig.INPUT_DIR.glob("*.pdf")) + \
                   list(HTMLParserConfig.INPUT_DIR.glob("*.PDF"))
        
        if pdf_files:
            print(f"  ✅ Found {len(pdf_files)} PDF file(s):")
            for f in pdf_files:
                print(f"     - {f.name}")
            return True
        else:
            print(f"  ⚠️  No PDF files in: {HTMLParserConfig.INPUT_DIR}")
            print(f"     Add .pdf files to process")
            return False
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_openai_key():
    """Test OpenAI API key"""
    print("\nTesting OpenAI API key...")
    
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).parent.parent / '.env'
        if env_path.exists():
            load_dotenv(env_path)
    except ImportError:
        pass
    
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("  ❌ OPENAI_API_KEY not found")
        return False
    
    if not api_key.startswith('sk-'):
        print("  ⚠️  API key format looks incorrect")
        return False
    
    print(f"  ✅ API key found")
    return True

def test_dependencies():
    """Test required dependencies"""
    print("\nTesting dependencies...")
    
    required = ['pdfplumber', 'openai']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} not installed")
            missing.append(package)
    
    if missing:
        print(f"\n  Install with: pip install {' '.join(missing)}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("="*60)
    print("10-K HTML Parser - Setup Validation")
    print("="*60 + "\n")
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Imports", test_imports),
        ("Directories", test_directories),
        ("PDF Files", test_pdf_files),
        ("OpenAI API Key", test_openai_key)
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    all_passed = all(r for _, r in results)
    
    if all_passed:
        print("\n✅ All tests passed! Ready to parse HTML files.")
        print("\nTo process files, run:")
        print("  python 10k_html_parser/run_parser.py")
    else:
        print("\n❌ Some tests failed. Fix issues above.")
    
    print("="*60 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
