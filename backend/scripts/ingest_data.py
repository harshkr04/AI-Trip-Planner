# backend/scripts/ingest_data.py
import sys
import os

# Add parent directory to path so we can import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.services.rag_service import rag_service

def main():
    print("Starting ingestion...")
    success = rag_service.ingest_data()
    if success:
        print("Ingestion complete!")
    else:
        print("Ingestion failed.")

if __name__ == "__main__":
    main()
