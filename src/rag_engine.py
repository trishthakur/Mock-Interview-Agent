from sentence_transformers import SentenceTransformer
import numpy as np
import json
from typing import List, Dict
import faiss

class RAGEngine:
    """Retrieval-Augmented Generation engine for job descriptions and questions."""
    
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.documents = []
        self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """Load job descriptions and questions into the vector database."""
        try:
            # Load job descriptions
            with open('data/job_descriptions.json', 'r') as f:
                jd_data = json.load(f)
            
            # Load questions bank
            with open('data/questions_bank.json', 'r') as f:
                questions_data = json.load(f)
            
            # Combine all documents
            self.documents = []
            for jd in jd_data:
                self.documents.append({
                    'type': 'job_description',
                    'content': jd['description'],
                    'metadata': jd
                })
            
            for category, questions in questions_data.items():
                for q in questions:
                    self.documents.append({
                        'type': 'question',
                        'content': q['question'],
                        'metadata': {
                            'category': category,
                            'difficulty': q.get('difficulty', 'Medium'),
                            'skills': q.get('skills', [])
                        }
                    })
            
            # Create embeddings
            texts = [doc['content'] for doc in self.documents]
            embeddings = self.model.encode(texts)
            
            # Build FAISS index
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings.astype('float32'))
            
            print(f"Loaded {len(self.documents)} documents into knowledge base")
            
        except FileNotFoundError as e:
            print(f"Warning: Could not load knowledge base - {e}")
    
    def retrieve(self, query: str, k: int = 5, doc_type: str = None) -> List[Dict]:
        """Retrieve most relevant documents for a query."""
        if self.index is None:
            return []
        
        # Encode query
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search
        distances, indices = self.index.search(query_embedding.astype('float32'), k * 2)
        
        # Filter and return results
        results = []
        for idx, score in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                doc = self.documents[idx]
                if doc_type is None or doc['type'] == doc_type:
                    results.append({
                        'document': doc,
                        'score': float(score)
                    })
                    if len(results) >= k:
                        break
        
        return results
    
    def get_relevant_context(self, job_description: str, query: str = "") -> str:
        """Get relevant context from job description for question generation."""
        # Extract key information from job description
        results = self.retrieve(job_description, k=3, doc_type='question')
        
        context = f"Job Description:\n{job_description}\n\n"
        context += "Similar Interview Questions:\n"
        for result in results:
            context += f"- {result['document']['content']}\n"
        
        return context