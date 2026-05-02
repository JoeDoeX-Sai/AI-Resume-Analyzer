# 🏗️ AI Resume Analyzer - Technical Architecture

## System Architecture

\\\
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                             │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │  index.html │  │  styles.css  │  │     app.js       │   │
│  │  (UI/UX)    │  │  (Styling)   │  │  (API Client)    │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST API
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      FLASK BACKEND                           │
│                        (app.py)                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  API Endpoints: /analyze, /analyze-text, /health    │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   PARSING    │  │  NLP ENGINE  │  │   SCORING    │
│              │  │              │  │    ENGINE    │
│ resume_      │  │ nlp_         │  │ ats_         │
│ parser.py    │  │ processor.py │  │ scorer.py    │
│              │  │              │  │              │
│ • PDF        │  │ • spaCy NER  │  │ • Semantic   │
│ • DOCX       │  │ • RAKE       │  │ • Keywords   │
│ • TXT        │  │ • Embeddings │  │ • Sections   │
└──────────────┘  └──────────────┘  └──────────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │  FEEDBACK    │
                  │   ENGINE     │
                  │              │
                  │ feedback_    │
                  │ generator.py │
                  │              │
                  │ • Suggestions│
                  │ • Improvements│
                  └──────────────┘
\\\

## Data Flow

1. **Upload** → User uploads resume (PDF/DOCX/TXT) + job description
2. **Parse** → Extract raw text from document
3. **NLP Processing** → spaCy pipeline, NER, skill extraction, RAKE
4. **Embedding** → Generate semantic embeddings
5. **Scoring** → Multi-dimensional ATS scoring (0-100)
6. **Feedback** → AI-generated suggestions
7. **Display** → Render results in dashboard

## Core Components

### 1. Resume Parser (\parsing/resume_parser.py\)
- **Purpose**: Extract text from various file formats
- **Technologies**: pdfminer.six, python-docx
- **Output**: Clean, normalized text

### 2. NLP Processor (\
lp_engine/nlp_processor.py\)
- **Purpose**: Deep NLP analysis
- **Technologies**: spaCy, RAKE, sentence-transformers
- **Features**:
  - Named Entity Recognition (NER)
  - Skill extraction (pattern matching + noun chunks)
  - Action verb detection
  - Keyword extraction
  - Semantic embeddings
  - Readability scoring

### 3. ATS Scorer (\scoring_engine/ats_scorer.py\)
- **Purpose**: Multi-factor resume scoring
- **Dimensions**:
  - Semantic Similarity (30%)
  - Keyword Coverage (25%)
  - Section Completeness (20%)
  - Content Strength (15%)
  - Readability (10%)
- **Output**: 0-100 score with grade

### 4. Feedback Generator (\eedback_engine/feedback_generator.py\)
- **Purpose**: Context-aware suggestions
- **Features**:
  - Missing skills identification
  - Weak verb replacements
  - Content improvements
  - Structure recommendations

## AI/NLP Pipeline Details

### spaCy Pipeline
\\\
Text → Tokenization → POS Tagging → NER → Dependency Parsing
\\\

### Skill Extraction Strategy
1. **Pattern Matching**: Regex for tech terms (Python, AWS, etc.)
2. **Noun Chunks**: spaCy noun phrase extraction
3. **RAKE**: Keyword phrase extraction
4. **Deduplication**: Clean and merge results

### Semantic Similarity
\\\
Resume Text → Sentence Transformer → Embedding Vector
                                           ↓
Job Description → Sentence Transformer → Embedding Vector
                                           ↓
                                    Cosine Similarity
\\\

## Scoring Algorithm

\\\python
final_score = (
    0.30 * semantic_similarity +
    0.25 * keyword_coverage +
    0.20 * section_completeness +
    0.15 * content_strength +
    0.10 * readability
) * 100
\\\

## API Specification

### POST /api/analyze
**Request**: multipart/form-data
- \esume\: File (PDF/DOCX/TXT)
- \job_description\: String

**Response**: JSON
\\\json
{
  \"success\": true,
  \"nlp_analysis\": {...},
  \"ats_score\": {...},
  \"feedback\": {...}
}
\\\

### POST /api/analyze-text
**Request**: application/json
\\\json
{
  \"resume_text\": \"...\",
  \"job_description\": \"...\"
}
\\\

## Performance Characteristics

- **First Analysis**: ~5-10 seconds (model loading)
- **Subsequent**: ~2-3 seconds
- **Memory**: ~1-2 GB (with models loaded)
- **Concurrent Users**: 10-20 (single instance)

## Security Features

- File size limit: 5MB
- Allowed formats: PDF, DOCX, TXT only
- Automatic file cleanup after processing
- Input sanitization
- CORS protection

## Scalability Considerations

### Current Limitations
- Single-threaded Flask (development server)
- In-memory model loading
- No caching

### Production Improvements
- Use Gunicorn/uWSGI with multiple workers
- Redis caching for embeddings
- Load balancer for horizontal scaling
- Database for analytics
- CDN for frontend assets

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | HTML/CSS/JS | User interface |
| Backend | Flask | REST API server |
| NLP | spaCy | Core NLP pipeline |
| Embeddings | Sentence Transformers | Semantic similarity |
| ML | scikit-learn | TF-IDF, cosine similarity |
| Keywords | RAKE-NLTK | Phrase extraction |
| Parsing | pdfminer.six, python-docx | Document parsing |
| Deep Learning | PyTorch | Model backend |

## File Structure Rationale

\\\
backend/
├── app.py                    # Main Flask app (routing)
├── parsing/                  # Document parsing layer
├── nlp_engine/              # Core AI/NLP logic
├── scoring_engine/          # ATS scoring algorithms
└── feedback_engine/         # Feedback generation
\\\

**Separation of Concerns**:
- Each module has single responsibility
- Easy to test independently
- Modular and maintainable
- Can swap implementations

## Future Architecture Enhancements

1. **Microservices**: Split into separate services
2. **Message Queue**: Async processing with Celery/RabbitMQ
3. **Database**: PostgreSQL for user data and analytics
4. **Caching**: Redis for embeddings and results
5. **Monitoring**: Prometheus + Grafana
6. **Logging**: ELK stack
7. **Authentication**: JWT tokens
8. **Rate Limiting**: API throttling

---

**Built with production-grade architecture principles** 🏗️
