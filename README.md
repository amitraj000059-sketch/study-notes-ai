# 📚 Study Notes AI

A Streamlit web app that converts YouTube educational videos into study notes, flashcards, and quizzes for Class 8 students.

## Features

✨ **YouTube to Study Materials**
- 📖 Extract transcript from YouTube videos
- 📝 AI-generated concise study notes
- 🎴 Interactive flashcards (10 cards per video)
- ❓ Multiple-choice quiz (5 questions per video)

✅ **For Students**
- Simple, easy-to-understand language
- Interactive learning with instant feedback
- Multiple study formats in one place
- Works on desktop and mobile

## How to Use

### Online (Recommended for Android)
Open the deployed app on your Android phone browser and follow these steps:
1. Paste a YouTube educational video link
2. Click "✨ Generate All"
3. Study using Notes, Flashcards, and Quiz tabs

### Local Installation (For Development)

**Requirements:**
- Python 3.8+
- YouTube video must have captions (English or Hindi)

**Steps:**
```bash
# 1. Clone the repository
git clone https://github.com/amitraj000059-sketch/study-notes-ai.git
cd study-notes-ai

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up API key
# Create a .env file in the project root:
echo "GEMINI_API_KEY=your_api_key_here" > .env

# 5. Run the app
streamlit run app.py
```

## Getting Gemini API Key (Free)

1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key
4. Add it to deployment secrets

## Requirements

- `streamlit` - Web app framework
- `youtube-transcript-api` - Extract YouTube transcripts
- `google-genai` - Gemini AI for content generation
- `python-dotenv` - Environment variable management

## Technical Details

- **Backend:** Streamlit + Gemini API
- **Frontend:** Streamlit UI components
- **Data Storage:** Session state (temporary, per user)
- **API:** Google Gemini 2.5 Flash

## Supported Formats

- YouTube video URLs: `youtube.com/watch?v=XXX`
- YouTube shorts: `youtu.be/XXX`
- Embedded videos: `youtube.com/embed/XXX`

## License

MIT

---

**Made with ❤️ using Streamlit and Google Gemini**
