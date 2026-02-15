#!/usr/bin/env python
"""Quick speed test - Dataset matching (Tier 1) only"""
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
print("⚡ BFSI ASSISTANT - QUICK TEST (Dataset Matching)")
print("="*80 + "\n")

print("Loading assistant...")
start = time.time()
from src.assistant import BFSIAssistant
assistant = BFSIAssistant()
load_time = time.time() - start

print(f"✅ Ready in {load_time:.1f}s\n")

# Use queries that MATCH the dataset (fast)
queries = [
    "What is the interest rate?",
    "How is EMI calculated?",
    "What happens if I miss payment?",
    "Can I get a loan?",
    "Tell me about interest rates",
]

print("Testing response speed:\n")

total = 0
for idx, q in enumerate(queries, 1):
    start = time.time()
    result = assistant.process_query(q)
    elapsed = time.time() - start
    total += elapsed
    
    status = "✅" if result['tier'] == 'dataset_match' else "⚠️"
    print(f"{status} Query {idx}: {elapsed:.3f}s ({result['confidence']:.0%}) - {result['tier']}")

avg = total / len(queries)
print(f"\n📊 Average response time: {avg:.3f}s")
print(f"📊 Total for 5 queries: {total:.2f}s")
print("\n✨ System ready for use!")
