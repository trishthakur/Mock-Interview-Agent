# Mock Interview Agent

An AI-powered interview practice system that generates role-specific questions and provides personalized feedback using Retrieval-Augmented Generation (RAG) and Chain-of-Thought evaluation.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Features

- **Intelligent Question Generation**: Uses RAG to generate role-specific questions grounded in curated job descriptions
- **Chain-of-Thought Evaluation**: Provides detailed reasoning for feedback scores with transparent analysis
- **Performance Analytics**: Track your progress across multiple interview sessions
- **Multi-Category Questions**: Technical, behavioral, and situational questions tailored to your role
- **Progress Tracking**: Visualize improvement over time with detailed metrics
- **Personalized Feedback**: Tailored suggestions based on comprehensive response analysis
- **Resume Integration**: Upload your resume for more personalized question generation
- **Session History**: Review all past interviews with complete feedback

## Demo

Check out the demo video, to see the application in action!


https://github.com/user-attachments/assets/29929668-590c-40ad-859d-60b7e1f300c3


## Architecture

```
┌─────────────────────────────────┐
│     Streamlit Web Interface     │
│  (User Input & Visualization)   │
└───────────────┬─────────────────┘
                │
        ┌───────▼────────┐
        │ Question Gen   │
        │  (RAG-based)   │
        └───────┬────────┘
                │
        ┌───────▼────────┐
        │ FAISS Vector   │
        │   Database     │
        │  (Embeddings)  │
        └───────┬────────┘
                │
        ┌───────▼────────┐
        │   Evaluator    │
        │(Chain-of-Thought)│
        └────────────────┘
```

### Technology Stack

- **Frontend**: Streamlit
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector Database**: FAISS (Facebook AI Similarity Search)
- **Evaluation**: Custom Chain-of-Thought reasoning engine
- **File Processing**: PyPDF2, python-docx
- **Data Storage**: CSV, JSON

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- 2GB RAM minimum (for model loading)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/trishthakur/mock-interview-agent.git
cd mock-interview-agent
```

2. **Create and activate virtual environment** (recommended)
```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up data directories**
```bash
mkdir -p data
```

The application will automatically create necessary CSV files on first run.

5. **Run the application**
```bash
streamlit run app.py
```

The app will open automatically in your default browser at `http://localhost:8501`

## Project Structure

```
mock-interview-agent/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
├── demo_video.mp4             # Application demonstration
│
├── data/                      # Data storage
│   ├── job_descriptions.json  # Curated job descriptions
│   ├── questions_bank.json    # Question database by category
│   └── user_history.csv       # Interview session history (auto-generated)
│
├── src/                       # Core application logic
│   ├── __init__.py
│   ├── rag_engine.py         # RAG implementation with FAISS
│   ├── question_generator.py # Question generation logic
│   ├── evaluator.py          # Chain-of-Thought evaluator
│   └── prompts.py            # Prompt templates
│
├── utils/                     # Utility functions
│   ├── __init__.py
│   ├── file_handler.py       # File processing (PDF, DOCX, TXT)
│   └── embeddings.py         # Embedding utilities
│
└── tests/                     # Unit tests
    ├── test_rag.py           # RAG engine tests
    └── test_evaluator.py     # Evaluator tests
```

## How It Works

### 1. RAG-Based Question Generation

The system uses **Retrieval-Augmented Generation** to generate relevant questions:

**Step 1: Embedding Creation**
- Job descriptions and questions are encoded using Sentence Transformers
- Embeddings are stored in a FAISS vector database for fast retrieval

**Step 2: Semantic Search**
- When a job description is selected, the system searches for similar questions
- FAISS performs cosine similarity search across the question bank

**Step 3: Context-Aware Filtering**
- Questions are filtered by category (technical/behavioral/situational)
- Difficulty level matching
- Skill alignment with job requirements
- Duplicate prevention (won't ask same question twice)

**Step 4: Question Selection**
- Top 5 most relevant questions are identified
- Random selection from top results for variety
- Fallback to curated question bank if needed

```python
# Example: Generate a question
question = question_gen.generate_question(
    job_context={
        'title': 'Software Engineer',
        'description': 'Full-stack development with React and Node.js...'
    },
    category='technical',
    difficulty='Medium'
)
```

### 2. Chain-of-Thought Evaluation

The evaluator analyzes responses using **explicit reasoning steps**:

```
Evaluation Process:

Step 1: Length Analysis
├─ Count words in response
├─ Compare against thresholds (20, 50, 100+ words)
└─ Score: 0-100 based on detail level

Step 2: Structure Analysis (STAR Method)
├─ Search for Situation indicators
├─ Search for Task indicators
├─ Search for Action indicators  
├─ Search for Result indicators
└─ Score: 25 points per component found

Step 3: Specificity Analysis
├─ Detect percentages/metrics (e.g., "increased by 40%")
├─ Detect timeframes (e.g., "6 months", "2 years")
├─ Detect technologies (e.g., "React", "Python", "AWS")
├─ Detect quantifiable improvements
└─ Score: 0-100 based on concrete examples

Step 4: Relevance Analysis
├─ Extract keywords from question
├─ Extract keywords from response
├─ Calculate keyword overlap
└─ Score: 0-100 based on alignment

Final Score = Weighted Average:
├─ Length:      20%
├─ Structure:   25%
├─ Specificity: 25%
└─ Relevance:   30%
```

**Example Evaluation Output:**

```
Score: 85%

Chain-of-Thought Reasoning:
Step 1 - Length Analysis: Response contains 127 words.
→ Excellent length, provides detailed information

Step 2 - Structure Analysis: Checking for clear organization...
→ Found 4/4 STAR components: SITUATION, TASK, ACTION, RESULT

Step 3 - Specificity Analysis: Checking for concrete examples...
→ Strong specificity with: percentages/metrics, timeframes, specific technologies

Step 4 - Relevance Analysis: Assessing alignment with question...
→ High relevance: 75% keyword alignment

Strengths:
- Comprehensive response with 127 words
- Well-structured answer using SITUATION, TASK, ACTION, RESULT
- Included specific details: metrics, timeframes, technologies

Areas for Improvement:
- Consider mentioning team collaboration aspects
```

### 3. Personalized Feedback System

Based on the evaluation, the system provides:

- **Strengths**: Specific things done well with reasoning
- **Improvements**: Actionable, concrete suggestions
- **Follow-up Questions**: Generated when score < 70%
- **Score Breakdown**: Transparent reasoning for every point
- **Progress Tracking**: Historical performance analysis

## Usage Guide

### Tab 1: Setup 

**Select Job Description**
1. Choose from pre-loaded library of common roles
2. Upload custom job description (PDF/TXT)
3. Paste job description text manually

**Optional: Upload Resume**
- Helps personalize questions to your background
- Supports PDF, TXT, and DOCX formats

### Tab 2: Interview

**Practice Workflow**
1. Click "Generate New Question" to get a role-specific question
2. Optionally filter by category (Technical/Behavioral/Situational)
3. Select difficulty level (Easy/Medium/Hard)
4. Type your response (aim for 50+ words)
5. Click "Submit for Evaluation"
6. Review detailed feedback and scoring

**Question Categories**
- **Technical**: Coding, system design, debugging, technologies
- **Behavioral**: Past experiences, teamwork, conflict resolution
- **Situational**: Hypothetical scenarios, decision-making

### Tab 3: History 

**Review Past Interviews**
- View all previous questions and responses
- Filter by category
- Sort by date, highest score, or lowest score
- Review feedback for each response
- Track improvement areas

### Tab 4: Analytics 

**Performance Metrics**
- Total questions completed
- Average score across all responses
- Highest and lowest scores
- Performance by category breakdown
- Score progression over time (line chart)
- Common improvement areas

## Tips for Better Results

### Use the STAR Method

Every behavioral/situational response should include:
- **S**ituation: Set the context (when, where, what was happening)
- **T**ask: Explain your responsibility (what needed to be done)
- **A**ction: Describe what YOU did (specific steps taken)
- **R**esult: Share the outcome (metrics, achievements, learnings)

**Example:**
```
❌ Bad: "I fixed a bug in production."

✅ Good: "Last quarter at TechCorp (Situation), our payment system 
was experiencing 5% transaction failures (Task). I analyzed server 
logs, identified a race condition in our Redis cache, implemented 
mutex locks, and deployed the fix (Action). This reduced failures 
to 0.1% and saved $50K in lost revenue (Result)."
```

### ✅ Be Specific

Include concrete details:
- **Numbers**: "increased by 40%", "reduced time from 2 hours to 15 minutes"
- **Technologies**: "React", "PostgreSQL", "AWS Lambda", "Docker"
- **Timeframes**: "over 6 months", "within 2 weeks"
- **Team size**: "led a team of 5 engineers"
- **Impact**: "affected 10,000 users", "saved 20 hours per week"

### ✅ Length Guidelines

- **Minimum**: 50 words (brief responses score poorly)
- **Optimal**: 75-150 words (detailed but concise)
- **Maximum**: 200 words (avoid rambling)

### ✅ Address the Question

- Read carefully and answer ALL parts
- Use keywords from the question in your response
- Stay on topic throughout

## Customization

### Adding New Job Descriptions

Edit `data/job_descriptions.json`:

```json
{
  "id": 4,
  "title": "DevOps Engineer",
  "company": "Cloud Systems Inc",
  "description": "We're seeking a DevOps Engineer to manage our cloud infrastructure. You'll work with Kubernetes, Terraform, and CI/CD pipelines. Requirements include 3+ years of experience, AWS/GCP expertise, and scripting skills in Python or Bash.",
  "skills": ["Kubernetes", "Terraform", "AWS", "Python", "CI/CD"],
  "level": "Mid-Senior"
}
```

### Adding New Questions

Edit `data/questions_bank.json`:

```json
{
  "technical": [
    {
      "question": "Explain how you would implement a rate limiter for an API.",
      "difficulty": "Hard",
      "skills": ["System Design", "Backend", "Scalability"],
      "category": "technical"
    }
  ]
}
```

### Adjusting Evaluation Weights

Modify `src/evaluator.py`:

```python
self.evaluation_criteria = {
    'length': {'weight': 0.2, 'threshold': 50},      # 20% of score
    'structure': {'weight': 0.25, 'threshold': 0.6}, # 25% of score
    'specificity': {'weight': 0.25, 'threshold': 0.5}, # 25% of score
    'relevance': {'weight': 0.3, 'threshold': 0.6}   # 30% of score
}
```

### Changing Embedding Model

In `src/rag_engine.py` and `utils/embeddings.py`:

```python
# Current: all-MiniLM-L6-v2 (fast, 384 dimensions)
# Alternative options:
model = SentenceTransformer('all-mpnet-base-v2')  # More accurate, slower
model = SentenceTransformer('paraphrase-MiniLM-L3-v2')  # Faster, smaller
```

## Testing

### Run All Tests

```bash
python -m pytest tests/ -v
```

### Run Specific Test File

```bash
python -m pytest tests/test_rag.py -v
```

### Test Coverage

```bash
pip install pytest-cov
python -m pytest tests/ --cov=src --cov-report=html
```

## Deployment Options

### Local Development

```bash
streamlit run app.py --server.port 8501
```

### Streamlit Cloud (Free)

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Deploy with one click

## Example Outputs

### High-Scoring Response (85%)

**Question:** "Tell me about a time you optimized system performance."

**Response:** 
"At TechCorp last year, our API response times increased to 3 seconds during peak traffic (Situation). I was tasked with reducing this to under 500ms (Task). I profiled the application, identified N+1 queries in our ORM, implemented Redis caching for frequently accessed data, and added database indexes on commonly queried fields (Action). Response times dropped to 200ms average, handling 5x more traffic, and user satisfaction increased by 40% (Result)."

**Feedback:**
- Score: 85%
- Strengths: Excellent STAR structure, specific metrics, concrete technologies
- Improvements: Could mention team collaboration

### Low-Scoring Response (35%)

**Question:** "Tell me about a time you optimized system performance."

**Response:** 
"I made the system faster by fixing some code issues."

**Feedback:**
- Score: 35%
- Improvements: Too brief (only 10 words), lacks structure, no specifics, no metrics

### Contribution Ideas

- [ ] Add more job descriptions and questions
- [ ] Implement voice recording for responses
- [ ] Add GPT integration for more advanced evaluation
- [ ] Create mobile-responsive design
- [ ] Add multi-language support
- [ ] Implement user authentication
- [ ] Add interview scheduling features
- [ ] Create Chrome extension for LinkedIn integration

## Additional Resources

- [STAR Method Guide](https://www.indeed.com/career-advice/interviewing/how-to-use-the-star-interview-response-technique)
- [Technical Interview Handbook](https://www.techinterviewhandbook.org/)
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Behavioral Interview Questions](https://www.themuse.com/advice/30-behavioral-interview-questions-you-should-be-ready-to-answer)

## Research & Methodology

This project implements concepts from:
- **Retrieval-Augmented Generation (RAG)**: Combines retrieval systems with generation for more accurate, grounded responses
- **Chain-of-Thought Prompting**: Explicit reasoning steps for transparent AI decision-making
- **Semantic Search**: Uses embeddings for meaning-based question retrieval
- **STAR Framework**: Industry-standard method for structured interview responses
