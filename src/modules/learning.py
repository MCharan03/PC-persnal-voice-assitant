import chromadb
from sentence_transformers import SentenceTransformer
import os
import uuid
import datetime

class SelfLearningCore:
    def __init__(self, db_path="data/learning_db"):
        print("Initializing Self-Learning Module...")
        os.makedirs(db_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=db_path)
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Collection for Behavioral Corrections
        self.rules = self.client.get_or_create_collection(name="behavioral_rules")
        print("Self-Learning Module Online.")

    def add_rule(self, trigger_context, rule_instruction):
        """
        Learns a new behavioral rule based on user correction.
        trigger_context: "When asking about code..."
        rule_instruction: "Always provide type hints."
        """
        text = f"Context: {trigger_context} | Rule: {rule_instruction}"
        embedding = self.encoder.encode(trigger_context).tolist()
        
        self.rules.add(
            documents=[rule_instruction],
            metadatas=[{
                "context": trigger_context, 
                "timestamp": str(datetime.datetime.now()),
                "type": "correction"
            }],
            ids=[str(uuid.uuid4())],
            embeddings=[embedding]
        )
        print(f"[Learning] Acquired new behavior: {rule_instruction}")

    def get_relevant_rules(self, current_input, n_results=2):
        """
        Retrieves relevant behavioral rules for the current situation.
        """
        embedding = self.encoder.encode(current_input).tolist()
        
        results = self.rules.query(
            query_embeddings=[embedding],
            n_results=n_results
        )
        
        if results['documents'] and results['documents'][0]:
            return results['documents'][0]
        return []

# Singleton
learner = SelfLearningCore()
