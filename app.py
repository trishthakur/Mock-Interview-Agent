import streamlit as st
from src.rag_engine import RAGEngine
from src.question_generator import QuestionGenerator
from src.evaluator import ResponseEvaluator
from utils.file_handler import FileHandler
import json
import pandas as pd
from datetime import datetime
import os
print("Current working directory:", os.getcwd())


# Page config
st.set_page_config(
    page_title="Mock Interview Agent",
    layout="wide"
)

# Initialize components
@st.cache_resource
def load_components():
    rag_engine = RAGEngine()
    question_gen = QuestionGenerator(rag_engine)
    evaluator = ResponseEvaluator()
    return rag_engine, question_gen, evaluator

rag_engine, question_gen, evaluator = load_components()

# Initialize session state
if 'job_context' not in st.session_state:
    st.session_state.job_context = None
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'interview_history' not in st.session_state:
    st.session_state.interview_history = []
if 'question_count' not in st.session_state:
    st.session_state.question_count = 0

# Header
st.title("Mock Interview Agent")
st.markdown("AI-Powered Interview Practice with Personalized Feedback")

# Sidebar
with st.sidebar:
    st.header("Statistics")
    st.metric("Questions Completed", st.session_state.question_count)
    
    if st.session_state.interview_history:
        avg_score = sum(h['score'] for h in st.session_state.interview_history) / len(st.session_state.interview_history)
        st.metric("Average Score", f"{avg_score:.1f}%")
    
    st.divider()
    st.header("Tips")
    st.info("""
    **STAR Method:**
    - **S**ituation
    - **T**ask
    - **A**ction
    - **R**esult
    """)

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["Setup", "Interview", "History", "Analytics"])

with tab1:
    st.header("Job Description Setup")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Option to load existing JD or create new
        jd_option = st.radio("Choose option:", ["Select from library", "Upload custom JD", "Paste JD text"])
        
        if jd_option == "Select from library":
            # Load from JSON
            with open('data/job_descriptions.json', 'r') as f:
                jd_library = json.load(f)
            
            job_titles = [jd['title'] for jd in jd_library]
            selected_title = st.selectbox("Select position:", job_titles)
            
            if selected_title:
                selected_jd = next(jd for jd in jd_library if jd['title'] == selected_title)
                st.session_state.job_context = selected_jd
                
                st.subheader(f"{selected_jd['title']} at {selected_jd['company']}")
                st.write(selected_jd['description'])
                
        elif jd_option == "Upload custom JD":
            uploaded_file = st.file_uploader("Upload job description (PDF/TXT)", type=['pdf', 'txt'])
            if uploaded_file:
                jd_text = FileHandler.extract_text(uploaded_file)
                st.session_state.job_context = {
                    'title': 'Custom Position',
                    'company': 'Company',
                    'description': jd_text
                }
                st.text_area("Extracted text:", jd_text, height=200)
        
        else:  # Paste text
            jd_text = st.text_area("Paste job description:", height=300)
            job_title = st.text_input("Job Title:")
            company = st.text_input("Company:")
            
            if st.button("Save Job Description"):
                if jd_text and job_title:
                    st.session_state.job_context = {
                        'title': job_title,
                        'company': company,
                        'description': jd_text
                    }
                    st.success("Job description saved!")
    
    with col2:
        st.subheader("Optional")
        resume_file = st.file_uploader("Upload your resume", type=['pdf', 'txt', 'docx'])
        if resume_file:
            resume_text = FileHandler.extract_text(resume_file)
            st.session_state.resume = resume_text
            st.success("Resume uploaded!")

with tab2:
    st.header("Interview Practice")
    
    if not st.session_state.job_context:
        st.warning("Please set up a job description in the Setup tab first!")
    else:
        # Display current job context
        st.info(f"**Interviewing for:** {st.session_state.job_context['title']} at {st.session_state.job_context['company']}")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if st.button("Generate New Question", use_container_width=True):
                # Generate question using RAG
                question = question_gen.generate_question(
                    st.session_state.job_context,
                    st.session_state.interview_history
                )
                st.session_state.current_question = question
                st.session_state.question_count += 1
        
        with col2:
            category = st.selectbox("Category:", ["All", "Technical", "Behavioral", "Situational"])
        
        with col3:
            difficulty = st.selectbox("Difficulty:", ["All", "Easy", "Medium", "Hard"])
        
        # Display current question
        if st.session_state.current_question:
            st.markdown("---")
            question_data = st.session_state.current_question
            
            st.markdown(f"### Question #{st.session_state.question_count}")
            st.markdown(f"**Category:** {question_data.get('category', 'General')}")
            st.markdown(f"**Difficulty:** {question_data.get('difficulty', 'Medium')}")
            
            st.markdown(f"#### {question_data['question']}")
            
            # Response input
            response_method = st.radio("Response method:", ["Text", "Voice (Coming Soon)"], horizontal=True)
            
            if response_method == "Text":
                user_response = st.text_area(
                    "Your answer:",
                    height=200,
                    placeholder="Type your response here... Aim for 50+ words with specific examples."
                )
                
                if st.button("📤 Submit for Evaluation", type="primary"):
                    if user_response.strip():
                        with st.spinner("Evaluating your response..."):
                            # Chain-of-Thought evaluation
                            evaluation = evaluator.evaluate_response(
                                question=question_data['question'],
                                response=user_response,
                                job_context=st.session_state.job_context
                            )
                            
                            # Store in history
                            st.session_state.interview_history.append({
                                'timestamp': datetime.now().isoformat(),
                                'question': question_data['question'],
                                'category': question_data.get('category', 'General'),
                                'response': user_response,
                                'score': evaluation['score'],
                                'feedback': evaluation
                            })
                            
                            # Save to CSV
                            pd.DataFrame([st.session_state.interview_history[-1]]).to_csv(
                                'data/user_history.csv', 
                                mode='a', 
                                header=not os.path.exists('data/user_history.csv'),
                                index=False
                            )
                            
                            # Display evaluation
                            st.markdown("---")
                            st.markdown("##Evaluation Results")
                            
                            col1, col2 = st.columns([1, 3])
                            
                            with col1:
                                score = evaluation['score']
                                color = "green" if score >= 70 else "orange" if score >= 50 else "red"
                                st.markdown(f"### <span style='color:{color}'>{score}%</span>", unsafe_allow_html=True)
                                st.progress(score / 100)
                            
                            with col2:
                                st.markdown(f"**Overall:** {evaluation['overall_assessment']}")
                                st.markdown(f"**Chain-of-Thought Analysis:**")
                                st.caption(evaluation['reasoning'])
                            
                            # Strengths
                            if evaluation['strengths']:
                                st.success("**Strengths:**")
                                for strength in evaluation['strengths']:
                                    st.write(f"- {strength}")
                            
                            # Improvements
                            if evaluation['improvements']:
                                st.warning("**Areas for Improvement:**")
                                for improvement in evaluation['improvements']:
                                    st.write(f"- {improvement}")
                            
                            # Suggested follow-up
                            if 'follow_up' in evaluation:
                                st.info(f"**Follow-up Question:** {evaluation['follow_up']}")
                    else:
                        st.error("Please provide a response before submitting.")

with tab3:
    st.header("Interview History")
    
    if not st.session_state.interview_history:
        st.info("No interview history yet. Start practicing in the Interview tab!")
    else:
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            filter_category = st.selectbox("Filter by category:", ["All"] + list(set(h['category'] for h in st.session_state.interview_history)))
        with col2:
            sort_by = st.selectbox("Sort by:", ["Most Recent", "Highest Score", "Lowest Score"])
        
        # Sort history
        history = st.session_state.interview_history.copy()
        if sort_by == "Highest Score":
            history.sort(key=lambda x: x['score'], reverse=True)
        elif sort_by == "Lowest Score":
            history.sort(key=lambda x: x['score'])
        else:
            history.reverse()
        
        # Filter by category
        if filter_category != "All":
            history = [h for h in history if h['category'] == filter_category]
        
        # Display history
        for idx, entry in enumerate(history):
            with st.expander(f"Q{idx+1}: {entry['question'][:80]}... - Score: {entry['score']}%"):
                st.markdown(f"**Category:** {entry['category']}")
                st.markdown(f"**Timestamp:** {entry['timestamp']}")
                st.markdown(f"**Question:** {entry['question']}")
                st.markdown(f"**Your Response:**")
                st.write(entry['response'])
                st.markdown(f"**Score:** {entry['score']}%")
                
                if 'feedback' in entry:
                    if entry['feedback'].get('strengths'):
                        st.success("Strengths: " + ", ".join(entry['feedback']['strengths']))
                    if entry['feedback'].get('improvements'):
                        st.warning("Improvements: " + ", ".join(entry['feedback']['improvements']))

with tab4:
    st.header("Performance Analytics")
    
    if not st.session_state.interview_history:
        st.info("Complete some interviews to see your analytics!")
    else:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        scores = [h['score'] for h in st.session_state.interview_history]
        
        with col1:
            st.metric("Total Questions", len(st.session_state.interview_history))
        with col2:
            st.metric("Average Score", f"{sum(scores)/len(scores):.1f}%")
        with col3:
            st.metric("Highest Score", f"{max(scores)}%")
        with col4:
            st.metric("Lowest Score", f"{min(scores)}%")
        
        # Score distribution by category
        st.subheader("Performance by Category")
        category_data = {}
        for h in st.session_state.interview_history:
            cat = h['category']
            if cat not in category_data:
                category_data[cat] = []
            category_data[cat].append(h['score'])
        
        category_df = pd.DataFrame([
            {'Category': cat, 'Average Score': sum(scores)/len(scores), 'Questions': len(scores)}
            for cat, scores in category_data.items()
        ])
        st.dataframe(category_df, use_container_width=True)
        
        # Progress over time
        st.subheader("Score Progression")
        progress_df = pd.DataFrame([
            {'Question #': idx+1, 'Score': h['score']}
            for idx, h in enumerate(st.session_state.interview_history)
        ])
        st.line_chart(progress_df.set_index('Question #'))
        
        # Common improvement areas
        st.subheader("Common Areas for Improvement")
        all_improvements = []
        for h in st.session_state.interview_history:
            if 'feedback' in h and 'improvements' in h['feedback']:
                all_improvements.extend(h['feedback']['improvements'])
        
        if all_improvements:
            from collections import Counter
            improvement_counts = Counter(all_improvements)
            for improvement, count in improvement_counts.most_common(5):
                st.write(f"- {improvement} (mentioned {count} times)")

# Footer
st.markdown("---")
st.caption("Mock Interview Agent | Powered by RAG + Chain-of-Thought Evaluation")