"""Prompt templates for the interview agent."""

QUESTION_GENERATION_PROMPT = """
Based on the following job description, generate a relevant interview question:

Job Title: {job_title}
Company: {company}
Description: {job_description}

Key Skills Required: {skills}

Generate a {category} question at {difficulty} difficulty level that:
1. Tests relevant skills for this role
2. Is appropriate for the experience level
3. Allows candidate to demonstrate their qualifications
4. Is clear and specific

Question:
"""

EVALUATION_PROMPT = """
Evaluate the following interview response using Chain-of-Thought reasoning:

Question: {question}
Response: {response}

Evaluate based on:
1. Content Quality (Does it answer the question?)
2. Structure (Is it well-organized, follows STAR method?)
3. Specificity (Includes examples, metrics, technologies?)
4. Communication (Clear, professional, appropriate length?)

Provide:
- Overall Score (0-100)
- Strengths (list)
- Areas for Improvement (list)
- Detailed reasoning for the score

Analysis:
"""

FEEDBACK_PROMPT = """
Based on the evaluation, provide personalized constructive feedback:

Score: {score}
Strengths: {strengths}
Improvements Needed: {improvements}

Generate encouraging, specific, actionable feedback that:
1. Acknowledges what was done well
2. Explains why improvements are needed
3. Provides concrete examples of how to improve
4. Maintains a supportive, growth-oriented tone

Feedback:
"""