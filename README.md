# AI Resume Analyzer 🧠📄

An advanced, NLP-powered AI Resume Analyzer designed to help candidates optimize their resumes to pass Applicant Tracking Systems (ATS) and impress recruiters. It uses natural language processing (spaCy), semantic sentence embeddings (Sentence Transformers), and intelligent algorithms to evaluate your resume against targeted job descriptions.

## ✨ Features

- **Deep NLP Analysis**: Uses spaCy for Named Entity Recognition (NER) to accurately extract technologies, tools, and soft skills instead of relying on basic keyword matching.
- **ATS Scoring Engine**: Simulates an actual ATS 6-second scan and calculates a comprehensive score (0-100) based on semantic similarity, keyword coverage, and section completeness.
- **GitHub Analyzer**: Paste your GitHub URL to instantly extract your tech stack, calculate your top repositories' impact, and generate high-quality resume bullet points based on your open-source work.
- **Skill Gap Analyzer**: Compares your resume against a target job description to identify missing skills and provides a step-by-step learning roadmap to acquire them.
- **AI Bullet Point Improver**: Paste a weak bullet point and get an optimized, action-driven replacement utilizing strong action verbs.
- **Readability & Grammar**: Computes Flesch-Kincaid readability scores and identifies passive/weak verbs.
- **Export to PDF**: Generate a clean, modern, ATS-friendly PDF resume directly from your analyzed content.

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **NLP & ML**: spaCy (`en_core_web_sm`), Sentence Transformers (`all-MiniLM-L6-v2`), scikit-learn (TF-IDF), RAKE (Keyword Extraction), NLTK
- **File Parsing**: pdfminer.six (PDFs), python-docx (Word Documents)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3 (Inter font, Lucide icons)

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/JoeDoeX-Sai/AI-Resume-Analyzer.git
cd AI-Resume-Analyzer
```

### 2. Set up the Backend
```bash
cd backend
python -m venv venv

# On Windows
venv\Scripts\activate

# On Mac/Linux
source venv/bin/activate

pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Download required NLP models
python -m spacy download en_core_web_sm
python -m nltk.downloader stopwords punkt
```

### 3. Run the Application
```bash
python app.py
```
*The web interface will automatically be available at `http://localhost:5000`.*

## 📸 Usage
1. Upload your resume (PDF, DOCX, or TXT).
2. (Optional) Paste the target job description to get a tailored ATS score and skill gap analysis.
3. Click "Analyze" and review the AI-generated feedback!

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page.
