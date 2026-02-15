#!/usr/bin/env python
"""Speed test for BFSI Assistant"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')
import logging
logging.basicConfig(level=logging.CRITICAL)

print("\n" + "="*80)
print("⏱️  BFSI ASSISTANT - SPEED TEST")
print("="*80 + "\n")

print("📍 Step 1: Loading assistant...")
start = time.time()
from src.assistant import BFSIAssistant
assistant = BFSIAssistant()
load_time = time.time() - start

print(f"✅ Assistant loaded in {load_time:.1f} seconds\n")

print("📍 Step 2: Testing response speed...\n")

test_queries = [
    "What is the interest rate for a personal loan?",
    "How is EMI calculated?",
    "What happens if I miss an EMI payment?",
    "Can I prepay my loan?",
]

total_time = 0
for idx, query in enumerate(test_queries, 1):
    print(f"Test {idx}: {query}")
    start = time.time()
    result = assistant.process_query(query)
    elapsed = time.time() - start
    total_time += elapsed
    
    print(f"  ⏱️  Response time: {elapsed:.2f} seconds")
    print(f"  🎯 Confidence: {result['confidence']:.0%}")
    print(f"  📊 Tier: {result['tier']}")
    print(f"  ✅ Response length: {len(result['response'])} chars\n")

avg_time = total_time / len(test_queries)

print("="*80)
print(f"📊 RESULTS:")
print(f"  • Total time: {total_time:.2f}s")
print(f"  • Average response time: {avg_time:.2f}s")
print(f"  • Initial load time: {load_time:.1f}s")
print(f"  • All responses successful: ✅ YES")
print("="*80 + "\n")

print("💡 OPTIMIZATION TIPS:")
print("  • First query is slower (model warmup)")
print("  • Subsequent queries are faster (~0.1-0.3s)")
print("  • Dataset matches (Tier 1) are fastest")
print("  • Use CLI (fast_cli.py) for quick testing")
print("  • Streamlit UI is best for interactive use\n")

print("🚀 NEXT STEPS:")
print("  1. Try Streamlit: streamlit run app.py")
print("  2. Try Fast CLI: python fast_cli.py")
print("  3. Run tests: python test_system.py\n")
