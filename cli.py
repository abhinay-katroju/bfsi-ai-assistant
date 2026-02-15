"""Command-line interface for BFSI Assistant"""
import sys
import logging
from pathlib import Path
from typing import Optional

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.assistant import BFSIAssistant, ResponseTier
from src.config import DATA_DIR, MODELS_DIR, RAG_KNOWLEDGE_DIR

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BFSICLIInterface:
    """Command-line interface for BFSI Assistant"""
    
    def __init__(self):
        logger.info("Initializing BFSI Assistant...")
        self.assistant = BFSIAssistant()
        self.conversation_history = []
        
    def print_header(self):
        """Print application header"""
        print("\n" + "="*80)
        print("🏦 BFSI CALL CENTER AI ASSISTANT")
        print("="*80)
        print("\n📖 This assistant helps with BFSI-related queries including:")
        print("   • Loan eligibility and application")
        print("   • EMI details and payment schedules")
        print("   • Interest rates and calculations")
        print("   • Account and customer support")
        print("\n💡 Commands:")
        print("   • Type your question and press Enter")
        print("   • 'help' - Show help message")
        print("   • 'stats' - Show assistant statistics")
        print("   • 'history' - Show conversation history")
        print("   • 'clear' - Clear conversation history")
        print("   • 'exit' - Exit the application")
        print("\n" + "="*80 + "\n")
    
    def print_help(self):
        """Print help message"""
        print("\n" + "-"*80)
        print("📚 HELP")
        print("-"*80)
        print("\nThis BFSI Assistant uses a 3-tier response system:\n")
        print("Tier 1 - Dataset Matching (Green ✅)")
        print("  • Fastest and most reliable")
        print("  • Searches 150+ curated BFSI responses")
        print("  • Used for common, well-answered questions")
        print("  • Confidence: 90%+\n")
        
        print("Tier 2 - RAG-Augmented Generation (Yellow ⚠️)")
        print("  • Knowledge-grounded responses")
        print("  • Combines RAG retrieval with SLM generation")
        print("  • Used for complex financial queries")
        print("  • Confidence: 80-90%\n")
        
        print("Tier 3 - SLM Generation (Blue ℹ️)")
        print("  • Fine-tuned small language model")
        print("  • Fallback for novel queries")
        print("  • May have lower confidence")
        print("  • Confidence: 60-80%\n")
        
        print("Safety Features:")
        print("  • Guardrails against unsafe/out-of-domain queries")
        print("  • RBI-compliant response generation")
        print("  • Automatic compliance disclaimers")
        print("  • Privacy and data security enforced\n")
        
        print("-"*80 + "\n")
    
    def print_stats(self):
        """Print assistant statistics"""
        info = self.assistant.get_assistant_info()
        
        print("\n" + "-"*80)
        print("📊 ASSISTANT STATISTICS")
        print("-"*80)
        print(f"\nSystem: {info['system']}")
        print(f"Version: {info['version']}")
        print(f"Status: {info['compliance']}")
        
        print(f"\nDataset:")
        print(f"  • Total samples: {info['dataset_stats']['total_samples']}")
        print(f"  • Categories: {', '.join(info['dataset_stats']['categories'].keys())}")
        
        print(f"\nRAG Knowledge Base:")
        print(f"  • Total documents: {info['rag_stats']['total_documents']}")
        print(f"  • Categories: {', '.join(info['rag_stats']['categories'].keys())}")
        
        print(f"\nResponse Tiers:")
        for tier in info['tiers']:
            print(f"  • {tier}")
        
        print(f"\nConversation History:")
        print(f"  • Queries processed: {len(self.conversation_history)}")
        
        print("-"*80 + "\n")
    
    def print_history(self):
        """Print conversation history"""
        if not self.conversation_history:
            print("\n📝 No conversation history yet.\n")
            return
        
        print("\n" + "-"*80)
        print("📝 CONVERSATION HISTORY")
        print("-"*80 + "\n")
        
        for idx, entry in enumerate(self.conversation_history, 1):
            print(f"{idx}. Question: {entry['query'][:50]}...")
            print(f"   Tier: {entry['tier']} | Confidence: {entry['confidence']:.0%}")
            print()
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("\n✅ Conversation history cleared.\n")
    
    def format_response(self, result: dict) -> str:
        """Format response for display"""
        tier_emoji = {
            "dataset_match": "✅",
            "rag_retrieval": "⚠️",
            "slm_generation": "ℹ️",
            "error": "❌"
        }
        
        output = "\n" + "-"*80 + "\n"
        output += f"{tier_emoji.get(result['tier'], '❓')} RESPONSE\n"
        output += "-"*80 + "\n\n"
        
        output += result['response'] + "\n\n"
        
        output += "-"*80 + "\n"
        output += f"📊 Tier: {result['tier'].replace('_', ' ').title()}\n"
        output += f"🎯 Confidence: {result['confidence']:.0%}\n"
        output += f"📝 Source: {result['source']}\n"
        
        if 'matched_instruction' in result:
            output += f"🎯 Matched: {result['matched_instruction'][:50]}...\n"
        
        if 'rag_sources' in result and result['rag_sources']:
            output += f"📚 RAG Sources: {', '.join(result['rag_sources'][:2])}\n"
        
        if 'error' in result:
            output += f"⚠️ Error: {result['error']}\n"
        
        output += "-"*80 + "\n"
        
        return output
    
    def run(self):
        """Run interactive CLI"""
        self.print_header()
        
        try:
            while True:
                try:
                    # Get user input
                    user_input = input("🤔 You: ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Handle special commands
                    if user_input.lower() == 'exit':
                        print("\n👋 Goodbye! Thank you for using BFSI Assistant.\n")
                        break
                    elif user_input.lower() == 'help':
                        self.print_help()
                        continue
                    elif user_input.lower() == 'stats':
                        self.print_stats()
                        continue
                    elif user_input.lower() == 'history':
                        self.print_history()
                        continue
                    elif user_input.lower() == 'clear':
                        self.clear_history()
                        continue
                    
                    # Process query
                    print("\n⏳ Processing...\n")
                    result = self.assistant.process_query(user_input, explain_tier=True)
                    
                    # Store in history
                    self.conversation_history.append({
                        'query': user_input,
                        'tier': result['tier'],
                        'confidence': result['confidence'],
                        'source': result['source']
                    })
                    
                    # Display formatted response
                    print(self.format_response(result))
                    
                except KeyboardInterrupt:
                    print("\n\n⚠️ Interrupted. Type 'exit' to quit.\n")
                except Exception as e:
                    logger.error(f"Error processing query: {e}")
                    print(f"\n❌ Error: {str(e)}\n")
        
        except EOFError:
            print("\n👋 Goodbye!\n")

def main():
    """Main entry point"""
    try:
        cli = BFSICLIInterface()
        cli.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Fatal error: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
