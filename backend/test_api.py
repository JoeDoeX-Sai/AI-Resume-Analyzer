"""
Quick test script to verify backend functionality
Run this after setup to ensure everything works
"""
import sys
import os

print("🧪 Testing AI Resume Analyzer Backend...\n")

# Test 1: Import all required packages
print("1️⃣ Testing imports...")
try:
    import flask
    import spacy
    import sklearn
    import rake_nltk
    import nltk
    from sentence_transformers import SentenceTransformer
    from pdfminer.high_level import extract_text
    import docx
    print("   ✅ All packages imported successfully")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
    print("   Run: pip install -r requirements.txt")
    sys.exit(1)

# Test 2: Load spaCy model
print("\n2️⃣ Testing spaCy model...")
try:
    nlp = spacy.load("en_core_web_sm")
    doc = nlp("This is a test sentence.")
    print(f"   ✅ spaCy model loaded ({len(doc)} tokens processed)")
except OSError:
    print("   ❌ spaCy model not found")
    print("   Run: python -m spacy download en_core_web_sm")
    sys.exit(1)

# Test 3: Load sentence transformer
print("\n3️⃣ Testing Sentence Transformer...")
try:
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    embedding = embedder.encode("Test sentence")
    print(f"   ✅ Sentence Transformer loaded (embedding dim: {len(embedding)})")
except Exception as e:
    print(f"   ❌ Sentence Transformer failed: {e}")
    sys.exit(1)

# Test 4: Test NLP processor
print("\n4️⃣ Testing NLP Processor...")
try:
    from nlp_engine.nlp_processor import NLPProcessor
    processor = NLPProcessor()
    test_text = "John Doe is a Software Engineer at Google in San Francisco. He developed Python applications."
    result = processor.process(test_text)
    print(f"   ✅ NLP Processor working")
    print(f"      - Entities found: {len(result['entities'])}")
    print(f"      - Skills extracted: {len(result['skills'])}")
    print(f"      - Sections detected: {sum(result['sections'].values())}")
except Exception as e:
    print(f"   ❌ NLP Processor failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Test ATS Scorer
print("\n5️⃣ Testing ATS Scorer...")
try:
    from scoring_engine.ats_scorer import ATSScorer
    scorer = ATSScorer(processor)
    score_result = scorer.score(test_text, result, "Software Engineer with Python experience")
    print(f"   ✅ ATS Scorer working")
    print(f"      - Final score: {score_result['final_score']}/100")
    print(f"      - Grade: {score_result['grade']}")
except Exception as e:
    print(f"   ❌ ATS Scorer failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Test Feedback Generator
print("\n6️⃣ Testing Feedback Generator...")
try:
    from feedback_engine.feedback_generator import FeedbackGenerator
    feedback_gen = FeedbackGenerator(processor)
    feedback = feedback_gen.generate(test_text, result, score_result, "Software Engineer")
    print(f"   ✅ Feedback Generator working")
    print(f"      - Top suggestions: {len(feedback['top_suggestions'])}")
except Exception as e:
    print(f"   ❌ Feedback Generator failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 7: Test Resume Parser
print("\n7️⃣ Testing Resume Parser...")
try:
    from parsing.resume_parser import ResumeParser
    parser = ResumeParser()
    # Test text parsing
    test_file = "test_resume.txt"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("Test Resume\nJohn Doe\nSoftware Engineer")
    parsed = parser.parse(test_file)
    os.remove(test_file)
    print(f"   ✅ Resume Parser working")
    print(f"      - Parsed {len(parsed)} characters")
except Exception as e:
    print(f"   ❌ Resume Parser failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*50)
print("✅ ALL TESTS PASSED!")
print("="*50)
print("\n🚀 Backend is ready to use!")
print("   Run: python app.py")
print("   Then open frontend/index.html in your browser")
