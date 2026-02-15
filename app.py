"""Streamlit UI for BFSI AI Assistant demo"""
import streamlit as st
import logging
from pathlib import Path
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.assistant import BFSIAssistant, ResponseTier

# Page config
st.set_page_config(
    page_title="BFSI AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 10px;
    }
    .tier-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    .tier-1 {
        background-color: #d4edda;
        color: #155724;
    }
    .tier-2 {
        background-color: #fff3cd;
        color: #856404;
    }
    .tier-3 {
        background-color: #cce5ff;
        color: #004085;
    }
    .error {
        background-color: #f8d7da;
        color: #721c24;
    }
    .response-box {
        background-color: #f8f9fa;
        border-left: 4px solid #1f77b4;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .confidence-bar {
        height: 10px;
        border-radius: 5px;
        background: linear-gradient(90deg, #ff6b6b 0%, #ffd93d 50%, #6bcf7f 100%);
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_assistant():
    """Load BFSI Assistant (cached)"""
    logger.info("Loading BFSI Assistant...")
    try:
        with st.spinner("⏳ Initializing BFSI Assistant (this may take a moment on first load)..."):
            assistant = BFSIAssistant()
        return assistant, None
    except Exception as e:
        logger.error(f"Error loading assistant: {e}")
        return None, str(e)

def get_tier_color(tier: str) -> str:
    """Get badge color for tier"""
    tier_map = {
        "dataset_match": "tier-1",
        "rag_retrieval": "tier-3",
        "slm_generation": "tier-2",
        "error": "error"
    }
    return tier_map.get(tier, "error")

def get_tier_emoji(tier: str) -> str:
    """Get emoji for tier"""
    tier_map = {
        "dataset_match": "📊",
        "rag_retrieval": "🔍",
        "slm_generation": "🧠",
        "error": "⚠️"
    }
    return tier_map.get(tier, "❓")

def main():
    """Main app function"""
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<h1 class="main-header">🏦 BFSI Call Center AI Assistant</h1>', unsafe_allow_html=True)
    with col2:
        st.image("https://img.icons8.com/color/96/000000/bank.png", width=80)
    
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Assistant Settings")
        
        show_stats = st.checkbox("Show Assistant Stats", value=False)
        show_examples = st.checkbox("Show Example Queries", value=True)
        explain_tier = st.checkbox("Explain Tier Selection", value=True)
        
        st.markdown("---")
        st.info("""
        ### 📖 How it works:
        
        **Tier 1**: 📊 Dataset Match
        - Searches curated BFSI responses
        - Fastest and most reliable
        
        **Tier 2**: 🧠 SLM Generation
        - Fine-tuned language model
        - For novel questions
        
        **Tier 3**: 🔍 RAG Retrieval
        - Knowledge-grounded generation
        - Best for complex queries
        """)
        
        st.markdown("---")
        st.markdown("**Support**: support@lendkraft.ai")
    
    # Load assistant
    assistant, error = load_assistant()
    
    if error:
        st.error(f"❌ Error loading assistant: {error}")
        st.info("Make sure you've generated the dataset and installed all dependencies.")
        return
    
    # Show assistant stats
    if show_stats:
        with st.expander("📊 Assistant Statistics", expanded=True):
            info = assistant.get_assistant_info()
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Dataset Samples", info['dataset_stats']['total_samples'])
                st.metric("RAG Documents", info['rag_stats']['total_documents'])
            
            with col2:
                st.write("**Response Tiers:**")
                for tier in info['tiers']:
                    st.write(f"✓ {tier}")
    
    # Main query input
    st.subheader("💬 Ask Your Question")
    query = st.text_area(
        "Enter your BFSI-related query:",
        placeholder="E.g., What is the interest rate for a personal loan? How is EMI calculated?",
        height=100,
        help="Ask anything about loans, EMI, interest rates, payments, account support, etc."
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        submit_button = st.button("🔍 Get Answer", use_container_width=True, key="submit")
    with col2:
        clear_button = st.button("🔄 Clear", use_container_width=True, key="clear")
    
    if clear_button:
        st.rerun()
    
    # Process query
    if submit_button and query:
        progress_bar = st.progress(0, text="Processing your query...")
        try:
            progress_bar.progress(25, text="Analyzing query...")
            result = assistant.process_query(query, explain_tier=explain_tier)
            progress_bar.progress(100, text="Complete!")
            import time
            time.sleep(0.5)
            progress_bar.empty()
        except Exception as e:
            progress_bar.empty()
            st.error(f"Error: {e}")
            return
        
        st.markdown("---")
        
        # Display results
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            tier_color = get_tier_color(result['tier'])
            tier_emoji = get_tier_emoji(result['tier'])
            st.markdown(
                f'<span class="tier-badge {tier_color}">{tier_emoji} {result["tier"].replace("_", " ").title()}</span>',
                unsafe_allow_html=True
            )
        
        with col2:
            confidence = result.get('confidence', 0) * 100
            st.metric("Confidence", f"{confidence:.0f}%")
        
        with col3:
            status = "✅ Success" if result.get('success') else "❌ Error"
            st.write(f"**Status**: {status}")
        
        # Main response
        st.markdown("### 📋 Response")
        st.markdown(f'<div class="response-box">{result["response"]}</div>', unsafe_allow_html=True)
        
        # Confidence visualization
        confidence = result.get('confidence', 0)
        st.markdown(f'<div class="confidence-bar" style="width: {confidence*100}%"></div>', unsafe_allow_html=True)
        
        # Additional details
        with st.expander("📌 Response Details"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Source**: {result['source']}")
                st.write(f"**Confidence**: {confidence:.2%}")
            
            with col2:
                if 'matched_instruction' in result:
                    st.write(f"**Matched Instruction**: {result['matched_instruction']}")
                if 'rag_sources' in result:
                    st.write(f"**RAG Sources**: {', '.join(result['rag_sources'])}")
            
            if explain_tier and result.get('explanation'):
                st.write(f"**Tier Selection**: {result['explanation']}")
    
    # Example queries
    if show_examples:
        st.markdown("---")
        st.subheader("💡 Example Queries")
        
        examples = [
            "What are the eligibility criteria for a personal loan?",
            "How is EMI calculated? Show an example.",
            "What happens if I miss an EMI payment?",
            "Can I prepay my loan early? Are there charges?",
            "What is the current interest rate for personal loans?",
            "How do I check my loan application status?",
            "Can I change my EMI due date?",
            "What documents do I need to apply for a loan?",
        ]
        
        cols = st.columns(2)
        for idx, example in enumerate(examples):
            col = cols[idx % 2]
            if col.button(f"📌 {example}", key=f"example_{idx}", use_container_width=True):
                st.session_state.query = example
                st.rerun()

if __name__ == "__main__":
    main()
