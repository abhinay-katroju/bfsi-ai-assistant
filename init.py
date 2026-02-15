#!/usr/bin/env python
"""
BFSI AI Assistant - Quick Start Script
Generates dataset and initializes the system
"""
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"

def main():
    """Run initialization"""
    logger.info("🚀 BFSI AI Assistant - Dataset Generation\n")
    
    # Step 1: Generate dataset
    logger.info("Step 1: Generating BFSI dataset...")
    try:
        from src.dataset_generator import generate_bfsi_dataset, save_dataset
        dataset = generate_bfsi_dataset()
        save_dataset(dataset, DATA_DIR / "bfsi_dataset.json")
        logger.info(f"✅ Dataset generated: {len(dataset)} samples\n")
    except Exception as e:
        logger.error(f"❌ Failed to generate dataset: {e}\n")
        return False
    
    # Step 2: Initialize RAG Knowledge Base
    logger.info("Step 2: Initializing RAG Knowledge Base...")
    try:
        from src.rag_knowledge_base import RAGKnowledgeBase
        from src.config import RAG_KNOWLEDGE_DIR
        kb = RAGKnowledgeBase(RAG_KNOWLEDGE_DIR)
        logger.info(f"✅ RAG KB initialized: {len(kb.knowledge_base)} documents\n")
    except Exception as e:
        logger.error(f"❌ Failed to initialize RAG KB: {e}\n")
        return False
    
    # Step 3: Verify dataset matcher
    logger.info("Step 3: Verifying Dataset Matcher...")
    try:
        from src.dataset_matcher import DatasetMatcher
        matcher = DatasetMatcher(DATA_DIR / "bfsi_dataset.json")
        stats = matcher.get_dataset_stats()
        logger.info(f"✅ Dataset Matcher ready")
        logger.info(f"   - Total samples: {stats['total_samples']}")
        logger.info(f"   - Categories: {len(stats['categories'])}\n")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Dataset Matcher: {e}\n")
        return False
    
    # Step 4: Test the assistant
    logger.info("Step 4: Testing BFSI Assistant...")
    try:
        from src.assistant import BFSIAssistant
        assistant = BFSIAssistant()
        
        # Test query
        test_query = "What is the interest rate for a personal loan?"
        result = assistant.process_query(test_query)
        
        logger.info(f"✅ Assistant test successful")
        logger.info(f"   - Query: {test_query[:50]}...")
        logger.info(f"   - Tier: {result['tier']}")
        logger.info(f"   - Confidence: {result['confidence']:.0%}\n")
    except Exception as e:
        logger.error(f"❌ Failed to test assistant: {e}\n")
        return False
    
    # Final summary
    print("\n" + "="*80)
    print("✅ INITIALIZATION SUCCESSFUL!")
    print("="*80 + "\n")
    
    print("🎯 Next Steps:\n")
    print("1️⃣  Launch the Interactive CLI:")
    print("   python cli.py\n")
    print("2️⃣  Launch the Streamlit UI:")
    print("   streamlit run app.py\n")
    print("3️⃣  Run Tests:")
    print("   python -m pytest tests/ -v\n")
    print("4️⃣  (Optional) Fine-tune the Model:")
    print("   python -m src.model_finetuning\n")
    
    print("📚 Documentation:")
    print("   • README.md - Full documentation")
    print("   • config.py - Configuration options")
    print("   • src/assistant.py - Main pipeline\n")
    
    print("💡 Example Queries:")
    print("   • What is the interest rate?")
    print("   • How is EMI calculated?")
    print("   • What happens if I miss an EMI?")
    print("   • Can I prepay my loan early?\n")
    
    print("="*80 + "\n")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
