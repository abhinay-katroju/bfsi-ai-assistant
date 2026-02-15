"""Setup script to initialize the BFSI AI Assistant"""
import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
RAG_KNOWLEDGE_DIR = PROJECT_ROOT / "rag_knowledge"

def run_command(cmd: list, description: str):
    """Run a shell command"""
    logger.info(f"{'='*80}")
    logger.info(f"📍 {description}")
    logger.info(f"{'='*80}")
    try:
        result = subprocess.run(cmd, check=True, cwd=PROJECT_ROOT)
        logger.info(f"✅ {description} completed successfully\n")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} failed: {e}\n")
        return False

def main():
    """Setup pipeline"""
    logger.info("🚀 Starting BFSI AI Assistant Setup\n")
    
    # Check Python version
    if sys.version_info < (3, 9):
        logger.error("❌ Python 3.9+ required")
        return False
    
    logger.info(f"✅ Python {sys.version.split()[0]} detected\n")
    
    # Create directories
    logger.info("📁 Creating directory structure...")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    RAG_KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    (MODELS_DIR / ".gitkeep").touch()
    logger.info("✅ Directories created\n")
    
    # Install dependencies
    if not run_command(
        [sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"],
        "Installing Python dependencies"
    ):
        return False
    
    # Generate dataset
    if not run_command(
        [sys.executable, "-m", "src.dataset_generator"],
        "Generating BFSI dataset (150+ samples)"
    ):
        return False
    
    # Initialize RAG knowledge base
    if not run_command(
        [sys.executable, "-c", "from src.rag_knowledge_base import RAGKnowledgeBase; from src.config import RAG_KNOWLEDGE_DIR; RAGKnowledgeBase(RAG_KNOWLEDGE_DIR); print('✅ RAG Knowledge Base initialized')"],
        "Initializing RAG knowledge base"
    ):
        return False
    
    logger.info(f"{'='*80}")
    logger.info("✅ SETUP COMPLETED SUCCESSFULLY!")
    logger.info(f"{'='*80}\n")
    
    print_next_steps()
    
    return True

def print_next_steps():
    """Print next steps"""
    print("\n" + "="*80)
    print("🎯 NEXT STEPS")
    print("="*80 + "\n")
    
    print("1️⃣  GENERATE DATASET (if not already done):")
    print("   python -m src.dataset_generator\n")
    
    print("2️⃣  (OPTIONAL) FINE-TUNE THE MODEL:")
    print("   python -m src.model_finetuning")
    print("   (Skip this if using base model - it will work without fine-tuning)\n")
    
    print("3️⃣  LAUNCH THE DEMO APP:")
    print("   streamlit run app.py\n")
    
    print("4️⃣  ACCESS THE APPLICATION:")
    print("   Open http://localhost:8501 in your browser\n")
    
    print("5️⃣  RUN TESTS:")
    print("   python -m pytest tests/\n")
    
    print("="*80)
    print("\n📚 PROJECT STRUCTURE:")
    print("""
    bfsi-ai-assistant/
    ├── data/
    │   └── bfsi_dataset.json          # 150+ BFSI conversation samples
    ├── models/
    │   └── fine_tuned_bfsi_model/    # (Optional) Fine-tuned model
    ├── rag_knowledge/
    │   └── knowledge_base.json        # Structured financial knowledge
    ├── src/
    │   ├── config.py                  # Configuration
    │   ├── dataset_generator.py       # Dataset generation
    │   ├── dataset_matcher.py         # Tier 1: Dataset matching
    │   ├── rag_knowledge_base.py      # Tier 3: RAG system
    │   ├── model_finetuning.py        # Model fine-tuning
    │   └── assistant.py               # Main 3-tier pipeline
    ├── app.py                         # Streamlit UI
    ├── requirements.txt               # Dependencies
    └── README.md                      # Documentation
    """)
    
    print("\n💡 KEY FEATURES:")
    print("""
    ✓ 3-Tier Response Pipeline:
      1. Dataset Similarity Matching (fastest, most reliable)
      2. RAG-Augmented Generation (knowledge-grounded)
      3. Fine-Tuned SLM Generation (for novel queries)
    
    ✓ Safety & Compliance:
      - Guardrails against unsafe/out-of-domain queries
      - RBI-compliant response generation
      - Automated safety checks
    
    ✓ Rich Demo Application:
      - Interactive Streamlit UI
      - Real-time response explanation
      - Confidence scores and source attribution
    """)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
