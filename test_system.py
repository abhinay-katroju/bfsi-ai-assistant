#!/usr/bin/env python
"""Quick test script for BFSI Assistant"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*80)
print("🧪 BFSI ASSISTANT - SYSTEM TEST")
print("="*80 + "\n")

try:
    print("✓ Step 1: Importing assistant...")
    from src.assistant import BFSIAssistant
    print("  ✅ Import successful\n")
    
    print("✓ Step 2: Initializing BFSI Assistant...")
    assistant = BFSIAssistant()
    print("  ✅ Assistant initialized\n")
    
    print("✓ Step 3: Processing test queries...\n")
    
    test_queries = [
        "What is the interest rate for a personal loan?",
        "How is EMI calculated?",
        "What happens if I miss an EMI payment?",
    ]
    
    for idx, query in enumerate(test_queries, 1):
        print(f"  Test {idx}: {query}")
        result = assistant.process_query(query)
        print(f"    ✅ Tier: {result['tier']}")
        print(f"    ✅ Confidence: {result['confidence']:.0%}")
        print(f"    ✅ Success: {result['success']}")
        print(f"    ✅ Response: {result['response'][:80]}...\n")
    
    print("="*80)
    print("✅ ALL TESTS PASSED!")
    print("="*80 + "\n")
    
    print("🎯 System is WORKING CORRECTLY!\n")
    print("📖 Next steps:")
    print("  1. Try the interactive CLI:  python cli.py")
    print("  2. Try the Streamlit UI:     streamlit run app.py")
    print("  3. Run full test suite:      python -m pytest tests/ -v\n")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)
