# ⚡ Quick Start Guide

Get the AI Resume Analyzer running in 5 minutes!

## 🚀 Fast Track Setup

### Step 1: Install Dependencies (2 minutes)

```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Step 2: Start Backend (30 seconds)

```bash
# Make sure venv is activated
python app.py
```

You should see:
```
🔄 Loading AI/NLP models...
✅ AI models loaded successfully.
 * Running on http://127.0.0.1:5000
```

### Step 3: Open Frontend (10 seconds)

Open `frontend/index.html` in your browser, or:

```bash
# In a new terminal
cd frontend
python -m http.server 8000
```

Then visit: `http://localhost:8000`

### Step 4: Test It! (1 minute)

1. Click "Browse File" and select `sample_resume.txt`
2. Copy content from `sample_job_description.txt` and paste into the job description field
3. Click "🚀 Analyze Resume"
4. View your AI-powered analysis!

## 🎯 What You'll See

- **ATS Score**: 0-100 score with grade
- **Dimension Breakdown**: 5 scoring factors
- **Extracted Skills**: AI-detected skills
- **Keyword Analysis**: Matched vs missing keywords
- **Named Entities**: People, organizations, locations
- **Action Verbs**: Strong vs weak verbs
- **AI Feedback**: Personalized suggestions

## 🔧 Troubleshooting

### "Module not found"
```bash
pip install -r requirements.txt
```

### "spaCy model not found"
```bash
python -m spacy download en_core_web_sm
```

### "Port already in use"
Change port in `backend/app.py`:
```python
app.run(debug=True, port=5001)
```

### Backend won't start
Make sure virtual environment is activated:
```bash
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

## 📝 Next Steps

- Try analyzing your own resume
- Experiment with different job descriptions
- Check out `SETUP_GUIDE.md` for detailed setup
- Read `ARCHITECTURE.md` to understand the system
- Explore the code in `backend/` folders

## 💡 Tips for Best Results

✅ **DO:**
- Provide a job description for targeted analysis
- Use standard resume format with clear sections
- Include quantifiable achievements (numbers, percentages)
- Start bullet points with action verbs

❌ **DON'T:**
- Upload files larger than 5MB
- Use unusual file formats (stick to PDF, DOCX, TXT)
- Expect instant results on first run (models need to load)

## 🎨 Customize It

Want to modify the system?

- **Scoring weights**: Edit `backend/scoring_engine/ats_scorer.py`
- **Action verbs**: Add to `backend/nlp_engine/nlp_processor.py`
- **UI colors**: Modify `frontend/styles.css`
- **Feedback messages**: Update `backend/feedback_engine/feedback_generator.py`

## 📊 Understanding Your Score

| Score | Grade | Meaning |
|-------|-------|---------|
| 85-100 | Excellent | ATS-optimized, strong match |
| 70-84 | Good | Solid resume, minor improvements |
| 55-69 | Average | Needs work, follow suggestions |
| 40-54 | Below Average | Major improvements needed |
| 0-39 | Poor | Significant restructuring required |

## 🔬 What Makes This AI-Powered?

Unlike basic keyword matchers, this system uses:

1. **spaCy NLP**: Real linguistic analysis
2. **Sentence Transformers**: Semantic understanding
3. **Named Entity Recognition**: Intelligent entity extraction
4. **RAKE**: Advanced keyword extraction
5. **Multi-factor Scoring**: Holistic evaluation
6. **Context-aware Feedback**: Personalized suggestions

## 🚀 Ready to Go!

You now have a production-quality AI resume analyzer running locally. Use it to:

- Optimize your resume for ATS systems
- Get data-driven feedback
- Understand what recruiters look for
- Showcase your AI/NLP skills

---

**Questions? Check `README.md` or `SETUP_GUIDE.md`** 📚
