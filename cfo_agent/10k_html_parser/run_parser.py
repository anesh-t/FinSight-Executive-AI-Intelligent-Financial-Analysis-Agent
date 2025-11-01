#!/usr/bin/env python3
"""
Simple runner for HTML to JSON parser
Usage: python run_parser.py
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded environment\n")
except ImportError:
    pass

if not os.getenv('OPENAI_API_KEY'):
    print("❌ Error: OPENAI_API_KEY not set")
    sys.exit(1)

from pipeline import main

if __name__ == "__main__":
    print("🚀 Starting HTML to JSON Parser\n")
    main()
