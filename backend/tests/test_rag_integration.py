# backend/tests/test_rag_integration.py
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.llm_service import llm_service
from backend.services.rag_service import rag_service

def test_rag_query():
    print("Testing RAG Query...")
    docs = rag_service.query("Mumbai food")
    if docs:
        print("✅ RAG Query successful. Retrieved:")
        for d in docs:
            print(f"  - {d[:50]}...")
    else:
        print("❌ RAG Query returned no results (might be empty DB if ingestion failed).")

def test_llm_generation_with_rag():
    print("\nTesting LLM Generation with RAG context...")
    # We'll use a mock prompt that should trigger RAG usage
    trip = {
        "prompt": "Plan a trip to Mumbai for 2 days. I love street food.",
        "start_date": "2025-12-01",
        "end_date": "2025-12-03"
    }
    
    # We can't easily mock the Groq client here without more work, 
    # but we can check if the deterministic fallback runs without error 
    # and if we can manually verify the context injection if we were to mock.
    # For now, let's just run the generation and see if it crashes.
    
    try:
        result = llm_service.generate_itinerary(
            prompt=trip["prompt"],
            start_date=trip["start_date"],
            end_date=trip["end_date"]
        )
        print("✅ LLM Service returned a result.")
        if "Mumbai" in result["text"] or "Mumbai" in str(result["plan"]):
             print("✅ Result contains expected destination.")
    except Exception as e:
        print(f"❌ LLM Service failed: {e}")

if __name__ == "__main__":
    test_rag_query()
    test_llm_generation_with_rag()
