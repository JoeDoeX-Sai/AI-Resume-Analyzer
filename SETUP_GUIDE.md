# 🚀 Complete Setup Guide

## Step-by-Step Installation

### 1. Prerequisites Check

Ensure you have:
- **Python 3.8 or higher**: Check with `python --version` or `python3 --version`
- **pip**: Check with `pip --version`
- **Git** (optional): For cloning the repository

### 2. Backend Setup

#### Option A: Automated Setup (Recommended)

**Windows:**
```bash
cd backend
setup.bat
```

**Linux/Mac:**
```bash
cd backend
chmod +x setup.sh
./setup.sh
```

#### Option B: Manual Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Download spaCy English model
python -m spacy download en_core_web_sm

# Optional: Download larger model for better accuracy
# python -m spacy download en_core_web_md
# or
# python -m spacy download en_core_web_lg
```

### 3. Verify Installation

```bash
# With venv activated
python -c "import spacy; import flask; import sentence_transformers; print('✅ All imports successful!')"
```

### 4. Start the Application

#### Option A: Quick Start Scripts

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

#### Option B: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
# Activate venv first
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
python -m http.server 8000
```

Then open browser to: `http://localhost:8000`

### 5. Test the Application

1. Open `http://localhost:8000` in your browser
2. Upload `sample_resume.txt` (provided in root directory)
3. Paste content from `sample_job_description.txt` into the job description field
4. Click "Analyze Resume"
5. View the comprehensive AI analysis results

## 🔧 Troubleshooting

### Issue: "Module not found" errors

**Solution:**
```bash
# Make sure virtual environment is activated
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: spaCy model not found

**Solution:**
```bash
python -m spacy download en_core_web_sm
```

### Issue: Port already in use

**Solution:**
```bash
# Change port in backend/app.py
app.run(debug=True, port=5001)  # Change 5000 to 5001

# Update frontend/app.js
const API_BASE = "http://localhost:5001/api";
```

### Issue: CORS errors

**Solution:**
- Make sure backend is running before accessing frontend
- Check that `flask-cors` is installed: `pip install flask-cors`

### Issue: Slow first analysis

**Explanation:** First run downloads ML models (~500MB). Subsequent analyses are fast.

### Issue: PDF parsing fails

**Solution:**
```bash
pip install --upgrade pdfminer.six
```

### Issue: Out of memory

**Solution:**
- Use smaller spaCy model: `en_core_web_sm` instead of `en_core_web_lg`
- Reduce batch size in sentence-transformers
- Close other applications

## 📦 Dependency Details

### Core ML/NLP Libraries:
- **spacy**: NLP pipeline, NER, POS tagging
- **sentence-transformers**: Semantic embeddings
- **scikit-learn**: TF-IDF, cosine similarity
- **rake-nltk**: Keyword extraction
- **nltk**: Text preprocessing

### Backend Framework:
- **flask**: Web server
- **flask-cors**: Cross-origin requests

### Document Parsing:
- **pdfminer.six**: PDF extraction
- **python-docx**: DOCX parsing

### Deep Learning:
- **torch**: PyTorch (required by sentence-transformers)
- **transformers**: Hugging Face transformers

## 🎯 First-Time Setup Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed from requirements.txt
- [ ] spaCy model downloaded
- [ ] Backend starts without errors
- [ ] Frontend accessible in browser
- [ ] Sample resume analysis works
- [ ] No CORS errors

## 🚀 Production Deployment

### Environment Variables

Create `.env` file in backend/:
```
FLASK_ENV=production
FLASK_DEBUG=False
MAX_CONTENT_LENGTH=5242880
UPLOAD_FOLDER=uploads
```

### Using Gunicorn (Linux/Mac)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Waitress (Windows)

```bash
pip install waitress
waitress-serve --port=5000 app:app
```

### Docker Deployment (Advanced)

Create `Dockerfile` in backend/:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t resume-analyzer .
docker run -p 5000:5000 resume-analyzer
```

## 📊 Performance Optimization

### For Faster Analysis:
1. Use `en_core_web_sm` (smallest spaCy model)
2. Reduce max_features in TF-IDF vectorizer
3. Limit skill extraction to top 50 items
4. Cache sentence embeddings for repeated analyses

### For Better Accuracy:
1. Use `en_core_web_lg` (largest spaCy model)
2. Fine-tune sentence-transformer model on resume data
3. Expand action verb dictionary
4. Add domain-specific skill patterns

## 🔐 Security Considerations

- File upload size limited to 5MB
- Only PDF, DOCX, TXT allowed
- Files deleted after processing
- Input sanitization in place
- CORS configured for localhost (update for production)

## 📝 Next Steps

After successful setup:
1. Try analyzing your own resume
2. Experiment with different job descriptions
3. Review the AI feedback suggestions
4. Explore the codebase to understand the NLP pipeline
5. Customize scoring weights in `ats_scorer.py`
6. Add custom skills or action verbs
7. Modify UI styling in `styles.css`

## 💡 Tips

- **Better Results**: Always provide a job description for targeted analysis
- **Skill Detection**: Use standard tech terms (e.g., "Python" not "python programming")
- **Action Verbs**: Start bullet points with strong verbs (Led, Built, Optimized)
- **Quantification**: Include numbers and metrics (increased by 40%, managed team of 5)
- **Format**: Use clear section headers (Experience, Education, Skills)

## 🆘 Getting Help

If you encounter issues:
1. Check this guide's troubleshooting section
2. Verify all dependencies are installed
3. Check backend logs for error messages
4. Ensure virtual environment is activated
5. Try with sample files first

---

**Ready to analyze resumes with AI! 🎉**
