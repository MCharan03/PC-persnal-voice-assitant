import chromadb
from sentence_transformers import SentenceTransformer
import os
import uuid
import datetime

class MemoryVector:
    def __init__(self, db_path="data/memory_db"):
        print("Initializing Vector Memory (The Soul)...")
        # Initialize ChromaDB (Persistent)
        os.makedirs(db_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Initialize Embedding Model (MiniLM is fast and good enough)
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Create or Get Collections
        self.facts = self.client.get_or_create_collection(name="user_facts")
        self.interactions = self.client.get_or_create_collection(name="interactions")
        
        print("Vector Memory Online.")

    def remember_fact(self, text, category="general"):
        """Stores a permanent fact about the user or world."""
        # Embed
        embedding = self.encoder.encode(text).tolist()
        
        # Store
        self.facts.add(
            documents=[text],
            metadatas=[{"category": category, "timestamp": str(datetime.datetime.now())}],
            ids=[str(uuid.uuid4())],
            embeddings=[embedding]
        )
        print(f"[Memory] Stored fact: {text}")

    def store_interaction(self, user_text, assistant_text):
        """Stores a conversation turn for context."""
        text = f"User: {user_text} | Cherry: {assistant_text}"
        embedding = self.encoder.encode(text).tolist()
        
        self.interactions.add(
            documents=[text],
            metadatas=[{"timestamp": str(datetime.datetime.now())}],
            ids=[str(uuid.uuid4())],
            embeddings=[embedding]
        )

    def recall(self, query, n_results=3):
        """Retrieves relevant facts or past interactions."""
        embedding = self.encoder.encode(query).tolist()
        
        results = self.facts.query(
            query_embeddings=[embedding],
            n_results=n_results
        )
        
        if results['documents'] and results['documents'][0]:
            return results['documents'][0] # Return list of matched strings
        return []

if __name__ == "__main__":
    mem = MemoryVector()
    mem.remember_fact("The user is a software engineer using Python.")
    print(mem.recall("What does the user do?"))
