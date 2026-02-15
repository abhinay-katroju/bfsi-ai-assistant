#!/usr/bin/env python
"""
BFSI AI Assistant - Main Entry Point
Usage: python -m bfsi_ai_assistant
"""
import sys
from pathlib import Path

# Add project to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def main():
    """Main entry point"""
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║         🏦 BFSI CALL CENTER AI ASSISTANT                      ║
    ║                                                                ║
    ║              Choose how to run the application:               ║
    ║                                                                ║
    ║    1. Interactive CLI (Command-line interface)                ║
    ║    2. Streamlit UI (Web-based interface)                      ║
    ║    3. Python API (For integration)                            ║
    ║    4. Run Tests (Validate system)                             ║
    ║    5. Initialize/Regenerate Dataset                           ║
    ║    6. Exit                                                    ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    choice = input("Select option (1-6): ").strip()
    
    if choice == "1":
        print("\n🚀 Launching CLI Interface...\n")
        from cli import main as cli_main
        cli_main()
    
    elif choice == "2":
        print("\n🚀 Launching Streamlit UI...\n")
        print("Opening http://localhost:8501")
        print("(Press Ctrl+C to stop)\n")
        import subprocess
        subprocess.run(["streamlit", "run", "app.py"])
    
    elif choice == "3":
        print("\n🚀 Python API Mode\n")
        from src.assistant import BFSIAssistant
        
        print("Assistant loaded successfully!")
        print("Usage:")
        print("  from src.assistant import BFSIAssistant")
        print("  assistant = BFSIAssistant()")
        print("  result = assistant.process_query('Your query')")
        print("\nStarting interactive Python...\n")
        
        import code
        assistant = BFSIAssistant()
        code.interact(local=locals(), banner="", exitmsg="")
    
    elif choice == "4":
        print("\n🧪 Running Tests...\n")
        import subprocess
        result = subprocess.run(["python", "-m", "pytest", "tests/", "-v"])
        sys.exit(result.returncode)
    
    elif choice == "5":
        print("\n📊 Initializing Dataset...\n")
        from init import main as init_main
        init_main()
    
    elif choice == "6":
        print("\n👋 Goodbye!\n")
        sys.exit(0)
    
    else:
        print("\n❌ Invalid option. Please select 1-6.\n")
        main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)
