import os
import re
import json
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai

st.set_page_config(page_title="Study Notes AI", page_icon="📚", layout="wide")

st.markdown("""
<style>
.main {max-width: 1200px; margin:auto;}
.stButton>button {border-radius:14px; width:100%; font-weight: bold;}
.card {padding:18px; border-radius:18px; background:#f7f7fb; margin:10px 0;}
.tab-content {padding: 20px;}
.flashcard {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 40px;
    border-radius: 20px;
    text-align: center;
    min-height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    cursor: pointer;
    transition: transform 0.3s;
}
.flashcard:hover {
    transform: scale(1.02);
}
.quiz-option {
    padding: 15px;
    margin: 8px 0;
    border-radius: 10px;
    border: 2px solid #e0e0e0;
    cursor: pointer;
    transition: all 0.3s;
}
.quiz-option:hover {
    border-color: #667eea;
    background: #f0f0ff;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "notes" not in st.session_state:
    st.session_state.notes = None
if "transcript" not in st.session_state:
    st.session_state.transcript = None
if "flashcards" not in st.session_state:
    st.session_state.flashcards = None
if "quiz" not in st.session_state:
    st.session_state.quiz = None
if "current_flashcard" not in st.session_state:
    st.session_state.current_flashcard = 0
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "quiz_completed" not in st.session_state:
    st.session_state.quiz_completed = False

st.title("📚 Study Notes AI")
st.caption("YouTube video → Study Notes → Flashcards → Quiz | For Class 8 Students")

# API Key setup
api_key = os.getenv("GEMINI_API_KEY")

def video_id(u):
    """Extract video ID from YouTube URL"""
    m = re.search(r"(?:v=|youtu\.be/|/shorts/|/embed/)([A-Za-z0-9_-]{11})", u or "")
    return m.group(1) if m else None

def get_transcript(vid):
    """Fetch transcript from YouTube video"""
    api = YouTubeTranscriptApi()
    try:
        tr = api.fetch(vid, languages=["en", "hi"])
        return " ".join(x["text"] for x in tr)
    except Exception:
        try:
            lst = api.list_transcripts(vid)
            for t in lst:
                try:
                    tr = t.fetch()
                    return " ".join(x["text"] for x in tr)
                except Exception:
                    pass
        except Exception:
            pass
    return None

def generate(prompt):
    """Generate content using Gemini API"""
    if not api_key:
        return None
    try:
        client = genai.Client(api_key=api_key)
        r = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return r.text
    except Exception as e:
        st.error(f"Error generating content: {str(e)}")
        return None

def generate_notes(transcript):
    """Generate study notes from transcript"""
    prompt = f"""Turn ONLY this transcript into short, accurate study notes for a Class 8 student.
Do not add facts not present in the transcript.
Use headings, bullet points, definitions, facts, formulas, examples and keywords when present.
Keep language simple and concise.
Format with clear sections and subsections.

TRANSCRIPT:
{transcript[:120000]}
"""
    return generate(prompt)

def generate_flashcards(transcript, num_cards=10):
    """Generate flashcards from transcript"""
    prompt = f"""Create exactly {num_cards} flashcards from this transcript for a Class 8 student.
Each flashcard should have a QUESTION and ANSWER separated by "|".
Format as JSON array with objects containing "question" and "answer" keys.
Make questions varied - some recall, some definition, some application.
Keep answers concise but complete.

TRANSCRIPT:
{transcript[:120000]}

Return ONLY valid JSON array, no other text."""
    
    result = generate(prompt)
    if result:
        try:
            # Clean JSON response
            result = result.strip()
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
            flashcards = json.loads(result)
            return flashcards
        except json.JSONDecodeError:
            st.error("Could not parse flashcards. Please try again.")
            return None
    return None

def generate_quiz(transcript, num_questions=5):
    """Generate multiple choice quiz from transcript"""
    prompt = f"""Create exactly {num_questions} multiple choice quiz questions from this transcript for a Class 8 student.
Each question should have 4 options (A, B, C, D) with exactly ONE correct answer.
Format as JSON array with objects containing:
- "question": the question text
- "options": array of 4 option strings
- "correct": the correct option letter (A, B, C, or D)
- "explanation": brief explanation of the answer

Make questions test understanding, not just memorization.

TRANSCRIPT:
{transcript[:120000]}

Return ONLY valid JSON array, no other text."""
    
    result = generate(prompt)
    if result:
        try:
            # Clean JSON response
            result = result.strip()
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
            quiz = json.loads(result)
            return quiz
        except json.JSONDecodeError:
            st.error("Could not parse quiz. Please try again.")
            return None
    return None

# Main Input Section
st.divider()
col1, col2 = st.columns([3, 1])
with col1:
    url = st.text_input("🔗 Paste YouTube video link", placeholder="https://www.youtube.com/watch?v=...")
with col2:
    if st.button("✨ Generate All", use_container_width=True):
        if not url:
            st.error("Please paste a YouTube link first!")
        else:
            vid = video_id(url)
            if not vid:
                st.error("❌ Invalid YouTube URL. Please check and try again.")
            else:
                # Get transcript
                with st.spinner("📖 Reading transcript..."):
                    transcript = get_transcript(vid)
                
                if not transcript:
                    st.warning("⚠️ Cannot access transcript. Try another video (English captions required).")
                else:
                    st.session_state.transcript = transcript
                    
                    if not api_key:
                        st.info("✋ Add GEMINI_API_KEY environment variable to generate AI content.")
                    else:
                        # Generate all three: notes, flashcards, quiz
                        progress_bar = st.progress(0)
                        
                        with st.spinner("📝 Generating notes..."):
                            st.session_state.notes = generate_notes(transcript)
                            progress_bar.progress(33)
                        
                        with st.spinner("🎴 Generating flashcards..."):
                            st.session_state.flashcards = generate_flashcards(transcript, 10)
                            progress_bar.progress(66)
                        
                        with st.spinner("❓ Generating quiz..."):
                            st.session_state.quiz = generate_quiz(transcript, 5)
                            progress_bar.progress(100)
                        
                        st.success("✅ All content generated successfully!")
                        st.session_state.current_flashcard = 0
                        st.session_state.quiz_answers = {}
                        st.session_state.quiz_completed = False

st.divider()

# Tabs for different sections
if st.session_state.notes or st.session_state.flashcards or st.session_state.quiz:
    tab1, tab2, tab3 = st.tabs(["📝 Study Notes", "🎴 Flashcards", "❓ Quiz"])
    
    # TAB 1: NOTES
    with tab1:
        if st.session_state.notes:
            st.markdown(st.session_state.notes)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📋 Copy Notes", use_container_width=True):
                    st.info("Copy the text above using Ctrl+C / Cmd+C")
            with col2:
                if st.button("🔄 Regenerate Notes", use_container_width=True):
                    if st.session_state.transcript:
                        with st.spinner("Regenerating notes..."):
                            st.session_state.notes = generate_notes(st.session_state.transcript)
                        st.rerun()
        else:
            st.info("👆 Generate content first using the button above")
    
    # TAB 2: FLASHCARDS
    with tab2:
        if st.session_state.flashcards:
            cards = st.session_state.flashcards
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                if st.button("⬅️ Previous", use_container_width=True):
                    if st.session_state.current_flashcard > 0:
                        st.session_state.current_flashcard -= 1
                        st.rerun()
            
            with col3:
                if st.button("Next ➡️", use_container_width=True):
                    if st.session_state.current_flashcard < len(cards) - 1:
                        st.session_state.current_flashcard += 1
                        st.rerun()
            
            with col2:
                st.markdown(f"<div style='text-align: center; padding: 10px;'><b>Card {st.session_state.current_flashcard + 1} of {len(cards)}</b></div>", unsafe_allow_html=True)
            
            current_card = cards[st.session_state.current_flashcard]
            
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"<h3>📌 Question</h3><p>{current_card.get('question', 'N/A')}</p>", unsafe_allow_html=True)
            
            if st.button("💡 Show Answer", use_container_width=True, key="show_answer"):
                st.markdown(f"<h3>✅ Answer</h3><p>{current_card.get('answer', 'N/A')}</p>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            if st.button("🔄 Regenerate Flashcards", use_container_width=True):
                if st.session_state.transcript:
                    with st.spinner("Regenerating flashcards..."):
                        st.session_state.flashcards = generate_flashcards(st.session_state.transcript, 10)
                        st.session_state.current_flashcard = 0
                    st.rerun()
        else:
            st.info("👆 Generate content first using the button above")
    
    # TAB 3: QUIZ
    with tab3:
        if st.session_state.quiz:
            quiz = st.session_state.quiz
            
            if not st.session_state.quiz_completed:
                for idx, q in enumerate(quiz):
                    st.markdown(f"### Question {idx + 1}/{len(quiz)}")
                    st.markdown(q["question"])
                    
                    answer = st.radio(
                        "Select your answer:",
                        options=["A", "B", "C", "D"],
                        format_func=lambda x: f"{x}: {q['options'][ord(x) - ord('A')]}",
                        key=f"q_{idx}",
                        label_visibility="collapsed"
                    )
                    
                    st.session_state.quiz_answers[idx] = answer
                    st.divider()
                
                if st.button("✅ Submit Quiz", use_container_width=True):
                    st.session_state.quiz_completed = True
                    st.rerun()
            else:
                # Show results
                st.markdown("### 📊 Quiz Results")
                
                correct = 0
                for idx, q in enumerate(quiz):
                    user_answer = st.session_state.quiz_answers.get(idx)
                    is_correct = user_answer == q["correct"]
                    
                    if is_correct:
                        correct += 1
                        st.success(f"✅ Q{idx + 1}: Correct! - {q['question']}")
                    else:
                        st.error(f"❌ Q{idx + 1}: Incorrect - {q['question']}")
                        st.markdown(f"**Your answer:** {user_answer}: {q['options'][ord(user_answer) - ord('A')]}")
                        st.markdown(f"**Correct answer:** {q['correct']}: {q['options'][ord(q['correct']) - ord('A')]}")
                    
                    st.markdown(f"**Explanation:** {q['explanation']}")
                    st.divider()
                
                score_percentage = (correct / len(quiz)) * 100
                st.markdown(f"### 🎯 Final Score: {correct}/{len(quiz)} ({score_percentage:.0f}%)")
                
                if score_percentage == 100:
                    st.balloons()
                    st.success("🌟 Perfect score! You've mastered this topic!")
                elif score_percentage >= 80:
                    st.success("🎉 Great job! Keep practicing!")
                elif score_percentage >= 60:
                    st.info("👍 Good effort! Review the material and try again.")
                else:
                    st.warning("📚 Keep studying! Go through the notes and flashcards again.")
                
                if st.button("🔄 Retake Quiz", use_container_width=True):
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_completed = False
                    st.rerun()
                
                if st.button("🆕 Regenerate Quiz", use_container_width=True):
                    if st.session_state.transcript:
                        with st.spinner("Regenerating quiz..."):
                            st.session_state.quiz = generate_quiz(st.session_state.transcript, 5)
                            st.session_state.quiz_answers = {}
                            st.session_state.quiz_completed = False
                        st.rerun()
        else:
            st.info("👆 Generate content first using the button above")
else:
    st.markdown("""
    ### 🎓 Welcome to Study Notes AI!
    
    **How to use:**
    1. Paste a YouTube video link (preferably educational content with captions)
    2. Click "Generate All" to create:
       - 📝 **Study Notes** - Concise, well-formatted notes
       - 🎴 **Flashcards** - Interactive flashcards for review
       - ❓ **Quiz** - Multiple choice questions to test your knowledge
    
    **Features:**
    - ✅ Supports English and Hindi subtitles
    - ✅ AI-powered content generation using Gemini
    - ✅ Simple language for Class 8 students
    - ✅ Interactive learning with instant feedback
    
    **Requirements:**
    - YouTube video with captions
    - GEMINI_API_KEY environment variable set
    
    Get started by pasting a video link! 🚀
    """)
