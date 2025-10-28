from typing import Dict, List
import re

class ResponseEvaluator:
    """Evaluate interview responses using Chain-of-Thought reasoning."""
    
    def __init__(self):
        self.evaluation_criteria = {
            'length': {'weight': 0.2, 'threshold': 50},
            'structure': {'weight': 0.25, 'threshold': 0.6},
            'specificity': {'weight': 0.25, 'threshold': 0.5},
            'relevance': {'weight': 0.3, 'threshold': 0.6}
        }
    
    def evaluate_response(self, question: str, response: str, 
                         job_context: Dict = None) -> Dict:
        """
        Evaluate response using Chain-of-Thought prompting approach.
        
        Returns detailed feedback with reasoning process.
        """
        # Initialize evaluation
        evaluation = {
            'score': 0,
            'strengths': [],
            'improvements': [],
            'reasoning': "",
            'overall_assessment': ""
        }
        
        reasoning_steps = []
        
        # Step 1: Length Analysis
        word_count = len(response.split())
        reasoning_steps.append(f"Step 1 - Length Analysis: Response contains {word_count} words.")
        
        if word_count >= 100:
            length_score = 100
            evaluation['strengths'].append(f"Comprehensive response with {word_count} words")
            reasoning_steps.append("→ Excellent length, provides detailed information")
        elif word_count >= 50:
            length_score = 70
            reasoning_steps.append("→ Good length, could add more detail")
        elif word_count >= 20:
            length_score = 40
            evaluation['improvements'].append("Expand your response with more details and examples")
            reasoning_steps.append("→ Response is brief, needs more elaboration")
        else:
            length_score = 20
            evaluation['improvements'].append("Response is too short - aim for 50+ words")
            reasoning_steps.append("→ Response is very brief, significantly expand your answer")
        
        # Step 2: Structure Analysis (STAR method)
        reasoning_steps.append("\nStep 2 - Structure Analysis: Checking for clear organization...")
        
        structure_indicators = {
            'situation': ['situation', 'context', 'background', 'when', 'where'],
            'task': ['task', 'challenge', 'problem', 'objective', 'goal'],
            'action': ['action', 'did', 'implemented', 'developed', 'created', 'led'],
            'result': ['result', 'outcome', 'achieved', 'improved', 'increased', 'decreased']
        }
        
        response_lower = response.lower()
        structure_score = 0
        found_components = []
        
        for component, keywords in structure_indicators.items():
            if any(keyword in response_lower for keyword in keywords):
                structure_score += 25
                found_components.append(component.upper())
        
        if structure_score >= 75:
            evaluation['strengths'].append(f"Well-structured answer using {', '.join(found_components)} components")
            reasoning_steps.append(f"→ Found {len(found_components)}/4 STAR components: {', '.join(found_components)}")
        elif structure_score >= 50:
            missing = [c.upper() for c in structure_indicators.keys() if c.upper() not in found_components]
            evaluation['improvements'].append(f"Consider adding {', '.join(missing)} to strengthen structure")
            reasoning_steps.append(f"→ Partial structure detected, missing: {', '.join(missing)}")
        else:
            evaluation['improvements'].append("Use STAR method: Situation, Task, Action, Result")
            reasoning_steps.append("→ Lacks clear structure, recommend STAR framework")
        
        # Step 3: Specificity Analysis
        reasoning_steps.append("\nStep 3 - Specificity Analysis: Checking for concrete examples...")
        
        specificity_indicators = [
            (r'\d+%', 'percentages/metrics'),
            (r'\d+\s*(months?|years?|weeks?|days?)', 'timeframes'),
            (r'(\$\d+|revenue|cost|budget)', 'financial metrics'),
            (r'(increased|decreased|improved|reduced)\s+\w+\s+by', 'quantifiable improvements'),
            (r'(React|Python|Java|SQL|AWS|Docker|Kubernetes|[A-Z][a-z]+\s+[A-Z][a-z]+)', 'specific technologies/methods')
        ]
        
        specifics_found = []
        for pattern, description in specificity_indicators:
            if re.search(pattern, response, re.IGNORECASE):
                specifics_found.append(description)
        
        specificity_score = min(len(specifics_found) * 25, 100)
        
        if specificity_score >= 75:
            evaluation['strengths'].append(f"Included specific details: {', '.join(specifics_found[:3])}")
            reasoning_steps.append(f"→ Strong specificity with: {', '.join(specifics_found)}")
        elif specificity_score >= 50:
            reasoning_steps.append(f"→ Some specifics found: {', '.join(specifics_found)}")
        else:
            evaluation['improvements'].append("Add specific examples, numbers, or technologies used")
            reasoning_steps.append("→ Lacks concrete examples and metrics")
        
        # Step 4: Relevance Analysis
        reasoning_steps.append("\nStep 4 - Relevance Analysis: Assessing alignment with question...")
        
        question_keywords = set(re.findall(r'\b\w+\b', question.lower())) - {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        response_keywords = set(re.findall(r'\b\w+\b', response.lower()))
        
        keyword_overlap = len(question_keywords & response_keywords) / max(len(question_keywords), 1)
        relevance_score = min(keyword_overlap * 150, 100)  # Scale up
        
        if relevance_score >= 70:
            evaluation['strengths'].append("Response directly addresses the question")
            reasoning_steps.append(f"→ High relevance: {keyword_overlap:.1%} keyword alignment")
        elif relevance_score >= 50:
            reasoning_steps.append(f"→ Moderate relevance: {keyword_overlap:.1%} keyword alignment")
        else:
            evaluation['improvements'].append("Ensure response directly addresses all parts of the question")
            reasoning_steps.append(f"→ Low relevance: {keyword_overlap:.1%} keyword alignment - refocus answer")
        
        # Calculate weighted final score
        final_score = (
            length_score * 0.20 +
            structure_score * 0.25 +
            specificity_score * 0.25 +
            relevance_score * 0.30
        )
        
        evaluation['score'] = round(final_score)
        evaluation['reasoning'] = "\n".join(reasoning_steps)
        
        # Overall assessment
        if final_score >= 80:
            evaluation['overall_assessment'] = "Excellent response! Strong across all criteria."
        elif final_score >= 70:
            evaluation['overall_assessment'] = "Good response with minor areas for improvement."
        elif final_score >= 60:
            evaluation['overall_assessment'] = "Satisfactory response, but needs strengthening."
        elif final_score >= 50:
            evaluation['overall_assessment'] = "Adequate foundation, significant improvement needed."
        else:
            evaluation['overall_assessment'] = "Response needs major improvement in multiple areas."
        
        # Generate follow-up question if score is low
        if final_score < 70:
            evaluation['follow_up'] = self._generate_followup(question, evaluation['improvements'])
        
        return evaluation
    
    def _generate_followup(self, original_question: str, improvements: List[str]) -> str:
        """Generate a follow-up question based on identified gaps."""
        if any('example' in imp.lower() or 'specific' in imp.lower() for imp in improvements):
            return "Can you provide a specific example with measurable results?"
        elif any('structure' in imp.lower() or 'star' in imp.lower() for imp in improvements):
            return "Can you walk me through the situation, your specific actions, and the results?"
        elif any('detail' in imp.lower() for imp in improvements):
            return "Can you elaborate on that with more context and details?"
        else:
            return "Is there anything else you'd like to add to strengthen your answer?"