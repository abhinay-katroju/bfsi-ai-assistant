#!/usr/bin/env python
"""Fast CLI interface for BFSI Assistant - Optimized for speed"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Run fast CLI"""
    import logging
    logging.basicConfig(level=logging.WARNING)  # Reduce logging for speed
    
    print("\n" + "="*80)
    print("🏦 BFSI AI ASSISTANT - FAST CLI")
    print("="*80)
    print("\n⏳ Loading assistant (first time only)...\n")
    
    from src.assistant import BFSIAssistant
    start_load = time.time()
    assistant = BFSIAssistant()
    load_time = time.time() - start_load
    
    print(f"✅ Ready! (Loaded in {load_time:.1f}s)\n")
    print("Commands: 'help', 'stats', 'exit'\n")
    print("="*80 + "\n")
    
    while True:
        try:
            query = input("🤔 You: ").strip()
            
            if not query:
                continue
            
            if query.lower() == 'exit':
                print("\n👋 Goodbye!\n")
                break
            elif query.lower() == 'help':
                print("\n📚 HELP - 3-Tier Response System:")
                print("  Tier 1 (Dataset): Fast, 150+ curated responses")
                print("  Tier 2 (RAG): Knowledge-grounded generation")
                print("  Tier 3 (SLM): Fallback generation\n")
                continue
            elif query.lower() == 'stats':
                info = assistant.get_assistant_info()
                print(f"\n📊 Dataset: {info['dataset_stats']['total_samples']} samples")
                print(f"📚 RAG KB: {info['rag_stats']['total_documents']} documents\n")
                continue
            
            # Process query
            start = time.time()
            result = assistant.process_query(query)
            elapsed = time.time() - start
            
            print(f"\n{'─'*80}")
            print(f"✅ {result['tier'].replace('_', ' ').title()}")
            print(f"{'─'*80}")
            print(f"\n{result['response']}\n")
            print(f"{'─'*80}")
            print(f"🎯 Confidence: {result['confidence']:.0%} | ⏱️ Time: {elapsed:.1f}s")
            print(f"{'─'*80}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

if __name__ == "__main__":
    main()
