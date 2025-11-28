
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    print("Checking imports...")
    from backend.app.main import app
    from backend.app.rag_pipeline import RAGPipeline
    print("✅ Backend modules imported successfully.")

    print("Checking RAG Pipeline initialization...")
    rag = RAGPipeline()
    print("✅ RAG Pipeline initialized.")
    
    if rag.llm:
        print("✅ LLM initialized successfully.")
    else:
        print("⚠️ LLM not initialized (check API token).")

except Exception as e:
    print(f"❌ Verification failed: {e}")
    sys.exit(1)
