from typing import Dict, List
import random
import json

class QuestionGenerator:
    """Generate role-specific interview questions using RAG."""
    
    def __init__(self, rag_engine):
        self.rag_engine = rag_engine
        self.load_question_templates()
    
    def load_question_templates(self):
        """Load question templates from JSON."""
        try:
            with open('data/questions_bank.json', 'r') as f:
                self.questions_bank = json.load(f)
        except FileNotFoundError:
            self.questions_bank = {
                'technical': [],
                'behavioral': [],
                'situational': []
            }
    
    def extract_key_skills(self, job_description: str) -> List[str]:
        """Extract key skills from job description."""
        # Simple keyword extraction (can be enhanced with NLP)
        common_skills = [
            'python', 'java', 'javascript', 'react', 'node', 'sql', 'aws', 'docker',
            'kubernetes', 'machine learning', 'data analysis', 'leadership', 'agile',
            'communication', 'problem solving', 'teamwork'
        ]
        
        skills_found = []
        jd_lower = job_description.lower()
        for skill in common_skills:
            if skill in jd_lower:
                skills_found.append(skill)
        
        return skills_found
    
    def generate_question(self, job_context: Dict, history: List = None, 
                         category: str = None, difficulty: str = None) -> Dict:
        """Generate a relevant interview question based on job context.
        
        Uses RAG to retrieve relevant questions from knowledge base.
        """
        if history is None:
            history = []
        
        # Extract key skills from job description
        skills = self.extract_key_skills(job_context['description'])
        
        # Use RAG to find relevant questions
        search_query = f"{job_context['title']} {' '.join(skills)}"
        relevant_docs = self.rag_engine.retrieve(search_query, k=10, doc_type='question')
        
        # Filter by category if specified
        if category and category != "All":
            relevant_docs = [d for d in relevant_docs if d['document']['metadata'].get('category') == category.lower()]
        
        # Filter by difficulty if specified
        if difficulty and difficulty != "All":
            relevant_docs = [d for d in relevant_docs if d['document']['metadata'].get('difficulty') == difficulty]
        
        # Exclude already asked questions
        asked_questions = {h.get('question', '') for h in history}
        relevant_docs = [d for d in relevant_docs if d['document']['content'] not in asked_questions]
        
        # Select question
        if relevant_docs:
            selected = random.choice(relevant_docs[:5])  # Top 5 most relevant
            return {
                'question': selected['document']['content'],
                'category': selected['document']['metadata'].get('category', 'General'),
                'difficulty': selected['document']['metadata'].get('difficulty', 'Medium'),
                'skills': selected['document']['metadata'].get('skills', []),
                'relevance_score': selected['score']
            }
        
        # Fallback to random question from bank
        categories = list(self.questions_bank.keys())
        selected_category = category.lower() if category and category != "All" else random.choice(categories)
        
        if selected_category in self.questions_bank and self.questions_bank[selected_category]:
            question = random.choice(self.questions_bank[selected_category])
            return {
                'question': question['question'],
                'category': selected_category,
                'difficulty': question.get('difficulty', 'Medium'),
                'skills': question.get('skills', [])
            }
        
        return {
            'question': "Tell me about your experience with this role.",
            'category': 'General',
            'difficulty': 'Easy'
        }