"""
NLP Processor - Core AI/NLP pipeline using spaCy, RAKE, NER, and sentence embeddings.
"""
import re
import spacy
from spacy.matcher import PhraseMatcher
import nltk
from rake_nltk import Rake
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Domain inference dictionaries
DOMAINS = {
    "Web Development": {"react", "node", "html", "css", "javascript", "typescript", "django", "flask", "express", "mongodb", "next.js", "vue", "angular"},
    "Data Science & AI": {"python", "machine learning", "deep learning", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn", "nlp", "sql", "data analysis", "artificial intelligence"},
    "Cloud & DevOps": {"aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "ci/cd", "terraform", "linux", "bash"},
    "Mobile Development": {"swift", "kotlin", "flutter", "react native", "android", "ios"},
    "UI/UX Design": {"figma", "adobe xd", "sketch", "user research", "wireframing", "prototyping"}
}

# Comprehensive Skill Extraction Dictionaries
TECH_SKILLS_WHITELIST = {
    "python", "javascript", "typescript", "java", "c++", "c#", "ruby", "go", "rust", "php", "swift", "kotlin",
    "html", "css", "sql", "nosql", "graphql", "rest api", "machine learning", "deep learning", "artificial intelligence",
    "data structures", "algorithms", "object-oriented programming", "system design", "microservices",
    "react", "angular", "vue", "node.js", "express.js", "django", "flask", "fastapi", "spring boot", "ruby on rails",
    "next.js", "nuxt", "svelte", "bootstrap", "tailwind css", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "keras", "opencv", "nltk", "spacy", "hadoop", "spark", "kafka", "rabbitmq", "celery", "redis", "elasticsearch",
    "mongodb", "postgresql", "mysql", "sqlite", "cassandra", "dynamodb", "neo4j", "firebase", "supabase",
    "ci/cd", "devops", "agile", "scrum", "kanban", "tdd", "bdd", "cybersecurity", "penetration testing",
    "cloud computing", "web scraping", "data analysis", "data engineering", "nlp", "computer vision",
    "blockchain", "smart contracts", "web3", "iot", "ar/vr", "game development", "mobile development"
}

TOOLS_WHITELIST = {
    "git", "github", "gitlab", "bitbucket", "docker", "kubernetes", "jenkins", "travis ci", "circleci", "github actions",
    "aws", "azure", "gcp", "google cloud platform", "heroku", "digitalocean", "vercel", "netlify",
    "terraform", "ansible", "chef", "puppet", "linux", "unix", "bash", "powershell",
    "jira", "trello", "asana", "confluence", "slack", "microsoft teams", "zoom",
    "figma", "adobe xd", "sketch", "invision", "photoshop", "illustrator", "premiere pro", "after effects",
    "postman", "swagger", "insomnia", "webpack", "babel", "vite", "npm", "yarn", "pnpm", "pip", "conda",
    "jupyter notebook", "google colab", "tableau", "power bi", "looker", "excel", "word", "powerpoint",
    "visual studio code", "intellij idea", "pycharm", "webstorm", "eclipse", "android studio", "xcode", "unity", "unreal engine"
}

SOFT_SKILLS_WHITELIST = {
    "leadership", "communication", "teamwork", "problem solving", "critical thinking", "time management",
    "adaptability", "flexibility", "creativity", "innovation", "emotional intelligence", "conflict resolution",
    "decision making", "project management", "customer service", "public speaking", "presentation skills",
    "negotiation", "active listening", "empathy", "work ethic", "attention to detail"
}

NORMALIZATION_DICT = {
    "react.js": "React", "reactjs": "React", "node.js": "Node.js", "nodejs": "Node.js",
    "vue.js": "Vue", "vuejs": "Vue", "express.js": "Express.js", "expressjs": "Express.js",
    "next.js": "Next.js", "nextjs": "Next.js", "mongo db": "MongoDB", "mongodb": "MongoDB",
    "postgre sql": "PostgreSQL", "postgres": "PostgreSQL", "mysql": "MySQL", "my sql": "MySQL",
    "restful api": "REST API", "restful apis": "REST API", "rest apis": "REST API",
    "machine learning": "Machine Learning", "ml": "Machine Learning",
    "artificial intelligence": "Artificial Intelligence", "ai": "Artificial Intelligence",
    "deep learning": "Deep Learning", "dl": "Deep Learning",
    "natural language processing": "NLP", "nlp": "NLP",
    "amazon web services": "AWS", "aws": "AWS", "google cloud platform": "GCP", "gcp": "GCP",
    "microsoft azure": "Azure", "azure": "Azure", "the mern stack": "MERN Stack", "mern": "MERN Stack",
    "object oriented programming": "Object-Oriented Programming", "oop": "Object-Oriented Programming"
}

BLACKLIST_TERMS = {
    "cgpa", "college", "school", "university", "matriculation", "intermediate", "high school", "diploma",
    "course", "internship", "cohort", "text", "requirements", "responsibilities", "company benefits",
    "salary", "working conditions", "gained", "learned", "understanding", "knowledge", "skills",
    "experience", "years", "months", "bachelor", "master", "phd", "degree", "certification",
    "developer", "engineer", "designer", "manager", "analyst", "student", "candidate", "professional"
}

WEAK_SKILLS = {
    "hardworking", "quick learner", "team player", "motivated", "passionate",
    "multitasking", "organized", "dedicated", "punctual", "reliable", "self-motivated", "fast learner"
}

# Download required NLTK data
nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)

# Section header patterns
SECTION_PATTERNS = {
    "experience": r"(work experience|professional experience|employment|experience|work history)",
    "education": r"(education|academic|qualification|degree|university|college)",
    "skills": r"(skills|technical skills|core competencies|technologies|tools|expertise)",
    "projects": r"(projects|personal projects|key projects|portfolio)",
    "summary": r"(summary|objective|profile|about me|professional summary)",
    "certifications": r"(certifications|certificates|licenses|credentials)",
    "achievements": r"(achievements|awards|honors|accomplishments)",
}

# Strong action verbs for resume
ACTION_VERBS = {
    "led", "built", "developed", "designed", "implemented", "architected",
    "optimized", "reduced", "increased", "improved", "managed", "created",
    "launched", "delivered", "engineered", "automated", "deployed", "scaled",
    "mentored", "collaborated", "analyzed", "researched", "established",
    "streamlined", "transformed", "spearheaded", "drove", "achieved",
    "generated", "negotiated", "coordinated", "executed", "facilitated",
}

WEAK_VERBS = {
    "worked", "helped", "assisted", "did", "made", "used", "tried",
    "participated", "involved", "responsible", "handled", "dealt",
}


class NLPProcessor:
    """
    Core NLP pipeline: spaCy NER, RAKE keyword extraction,
    section detection, sentence embeddings.
    """
    
    def __init__(self):
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_lg")
        except OSError:
            try:
                self.nlp = spacy.load("en_core_web_md")
            except OSError:
                self.nlp = spacy.load("en_core_web_sm")

        # Add EntityRuler for tech skills
        ruler = self.nlp.add_pipe("entity_ruler", before="ner")
        tech_labels = [
            {"label": "Technology/Tool", "pattern": t} for t in [
                "Python", "JavaScript", "TypeScript", "Java", "SQL", "React",
                "Node.js", "Flask", "Django", "TensorFlow", "PyTorch", "Docker",
                "Kubernetes", "AWS", "GCP", "Azure", "MongoDB", "PostgreSQL",
                "Redis", "Kafka", "GraphQL", "REST", "CI/CD", "Git", "Jenkins",
                "spaCy", "NLTK", "scikit-learn", "NumPy", "Pandas", "Figma",
                "HTML", "CSS", "C++", "C#"
            ]
        ]
        ruler.add_patterns(tech_labels)

        # Sentence transformer for semantic embeddings
        try:
            self.embedder = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
        except Exception:
            self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

        # PhraseMatcher for rigorous skill extraction
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        
        # Add tech skills to matcher
        tech_patterns = [self.nlp.make_doc(text) for text in TECH_SKILLS_WHITELIST]
        self.matcher.add("TECH_SKILLS", tech_patterns)
        
        # Add tools to matcher
        tool_patterns = [self.nlp.make_doc(text) for text in TOOLS_WHITELIST]
        self.matcher.add("TOOLS", tool_patterns)
        
        # Add soft skills to matcher
        soft_patterns = [self.nlp.make_doc(text) for text in SOFT_SKILLS_WHITELIST]
        self.matcher.add("SOFT_SKILLS", soft_patterns)

        # RAKE for keyword extraction
        self.rake = Rake()

        # TF-IDF vectorizer
        self.tfidf = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 3),
            max_features=500,
        )

    def process(self, text: str) -> dict:
        """Run full NLP pipeline on resume text."""
        doc = self.nlp(text)
        skills_data = self._extract_skills(text, doc)

        return {
            "domain": self._infer_domain(skills_data["strong"]),
            "entities": self._extract_entities(doc),
            "skills": skills_data,
            "sections": self._detect_sections(text),
            "bullets": self._extract_all_bullets(text),
            "action_verbs": self._extract_action_verbs(doc),
            "weak_verbs": self._find_weak_verbs(doc),
            "keywords": self._extract_keywords(text),
            "sentences": self._extract_sentences(doc),
            "readability": self._compute_readability(text, doc),
            "embedding": self._get_embedding(text),
        }

    def _infer_domain(self, skills: list) -> str:
        """Infer the primary domain based on technical skills."""
        domain_scores = {domain: 0 for domain in DOMAINS}
        skills_lower = [s.lower() for s in skills]
        
        for skill in skills_lower:
            for domain, keywords in DOMAINS.items():
                if skill in keywords:
                    domain_scores[domain] += 1
                else:
                    # Partial match
                    if any(kw in skill for kw in keywords if len(kw) > 3):
                        domain_scores[domain] += 0.5
                        
        best_domain = max(domain_scores, key=domain_scores.get)
        if domain_scores[best_domain] > 0:
            return best_domain
        return "General/Software Engineering"

    def _extract_all_bullets(self, text: str) -> list:
        """Extract all bullet points from the resume for strength analysis."""
        bullets = []
        # Match lines starting with common bullet characters or dashes
        for line in text.split('\n'):
            line = line.strip()
            if re.match(r'^[\-\*\•\u2022\u2023\u25E6]\s+', line):
                clean_bullet = re.sub(r'^[\-\*\•\u2022\u2023\u25E6]\s+', '', line).strip()
                if len(clean_bullet) > 15: # Ignore very short bullets
                    bullets.append(clean_bullet)
        return bullets

    def _extract_entities(self, doc) -> dict:
        """NER: extract named entities grouped by simplified labels."""
        entities = {"Technologies & Tools": [], "Organizations": [], "Platforms/Products": []}
        
        # Map spaCy labels to our simplified meaningful labels
        label_map = {
            "Technology/Tool": "Technologies & Tools",
            "ORG": "Organizations",
            "PRODUCT": "Platforms/Products"
        }
        
        for ent in doc.ents:
            if ent.label_ in label_map:
                mapped_label = label_map[ent.label_]
                val = ent.text.strip()
                if val and val not in entities[mapped_label] and len(val) > 2:
                    entities[mapped_label].append(val)
                    
        # Remove empty lists
        return {k: v for k, v in entities.items() if v}

    def _extract_skills(self, text: str, doc) -> dict:
        """
        Extract skills using a strict whitelist and PhraseMatcher.
        Fall back to high-frequency noun chunks if strictly valid.
        Categorize into Technical, Tools, and Soft Skills.
        """
        extracted = {
            "Technical Skills": set(),
            "Tools & Technologies": set(),
            "Soft Skills": set()
        }
        
        # 1. PhraseMatcher for whitelists
        matches = self.matcher(doc)
        for match_id, start, end in matches:
            match_label = self.nlp.vocab.strings[match_id]
            phrase = doc[start:end].text.lower()
            
            # Normalize
            normalized = NORMALIZATION_DICT.get(phrase, phrase.title() if len(phrase) > 3 else phrase.upper())
            # Fix case for specific ones explicitly
            if phrase in ["node.js", "nodejs"]: normalized = "Node.js"
            elif phrase in ["react.js", "reactjs"]: normalized = "React"
            elif phrase in ["mongodb", "mongo db"]: normalized = "MongoDB"
            elif phrase == "javascript": normalized = "JavaScript"
            elif phrase == "typescript": normalized = "TypeScript"
            elif phrase == "html": normalized = "HTML"
            elif phrase == "css": normalized = "CSS"
            elif phrase == "sql": normalized = "SQL"
            
            if match_label == "TECH_SKILLS":
                extracted["Technical Skills"].add(normalized)
            elif match_label == "TOOLS":
                extracted["Tools & Technologies"].add(normalized)
            elif match_label == "SOFT_SKILLS":
                extracted["Soft Skills"].add(normalized.title())

        # 2. Extract multiple-occurrence noun chunks (Confidence Threshold)
        candidate_counts = {}
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower().strip()
            chunk_text = re.sub(r'[^a-z0-9\s\.\+]', '', chunk_text).strip()
            if 2 < len(chunk_text) < 30 and not self._is_noise_strict(chunk_text):
                candidate_counts[chunk_text] = candidate_counts.get(chunk_text, 0) + 1
                
        self.rake.extract_keywords_from_text(text)
        for phrase in self.rake.get_ranked_phrases():
            phrase = phrase.lower().strip()
            if 2 < len(phrase) < 30 and not self._is_noise_strict(phrase):
                candidate_counts[phrase] = candidate_counts.get(phrase, 0) + 1

        for candidate, count in candidate_counts.items():
            if count > 1: # Appears multiple times
                normalized = NORMALIZATION_DICT.get(candidate, candidate.title())
                # Only add if not already extracted
                already_extracted = any(normalized.lower() == s.lower() for cat in extracted.values() for s in cat)
                if not already_extracted and candidate not in WEAK_SKILLS:
                    # POS Check: ensure it's mostly nouns
                    candidate_doc = self.nlp(candidate)
                    is_valid_pos = all(t.pos_ in ["NOUN", "PROPN", "ADJ"] for t in candidate_doc if not t.is_stop)
                    if is_valid_pos:
                        extracted["Technical Skills"].add(normalized)

        weak_skills = set()
        for candidate in candidate_counts:
            if candidate in WEAK_SKILLS or any(w in candidate for w in WEAK_SKILLS):
                weak_skills.add(candidate.title())
        
        # Convert sets to sorted lists
        return {
            "Technical Skills": sorted(list(extracted["Technical Skills"])),
            "Tools & Technologies": sorted(list(extracted["Tools & Technologies"])),
            "Soft Skills": sorted(list(extracted["Soft Skills"])),
            "weak": sorted(list(weak_skills)), # Keep for feedback
            "strong": sorted(list(extracted["Technical Skills"])) # Keep for _infer_domain compatibility
        }

    def _is_noise_strict(self, text_lower: str) -> bool:
        """Strict noise filtering using blacklist and patterns."""
        if not text_lower or len(text_lower) < 2:
            return True
            
        # Blacklist check
        if text_lower in BLACKLIST_TERMS:
            return True
            
        # Partial blacklist check (if a blacklist term is part of the phrase)
        for term in BLACKLIST_TERMS:
            if re.search(r'\b' + re.escape(term) + r'\b', text_lower):
                return True
                
        # Dates, numbers
        if re.search(r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b', text_lower): return True
        if re.search(r'\b(19|20)\d{2}\b', text_lower): return True
        if text_lower.isdigit(): return True
        if sum(c.isdigit() for c in text_lower) > len(text_lower) * 0.4: return True
        
        # Action verbs
        if text_lower in WEAK_VERBS or text_lower in [v.lower() for v in ACTION_VERBS]:
            return True
            
        # Stopwords
        doc = self.nlp(text_lower)
        if all(token.is_stop for token in doc):
            return True
            
        return False

    def _detect_sections(self, text: str) -> dict:
        """Detect which resume sections are present."""
        text_lower = text.lower()
        found = {}
        for section, pattern in SECTION_PATTERNS.items():
            match = re.search(pattern, text_lower)
            found[section] = bool(match)
        return found

    def _extract_action_verbs(self, doc) -> list:
        """Find strong action verbs used in the resume."""
        found = []
        for token in doc:
            # Accept VERB and also past-tense forms (VBD/VBN tags)
            is_verb = token.pos_ == "VERB" or token.tag_ in ("VBD", "VBN")
            lemma = token.lemma_.lower()
            text_lower = token.text.lower()
            if is_verb and (lemma in ACTION_VERBS or text_lower in ACTION_VERBS):
                key = lemma if lemma in ACTION_VERBS else text_lower
                if key not in found:
                    found.append(key)
        return found

    def _find_weak_verbs(self, doc) -> list:
        """Find weak/passive verbs that should be replaced."""
        found = []
        for token in doc:
            if token.pos_ == "VERB" and token.lemma_.lower() in WEAK_VERBS:
                if token.text.lower() not in found:
                    found.append(token.text.lower())
        return found

    def _extract_keywords(self, text: str) -> list:
        """RAKE-based keyword extraction with scores."""
        self.rake.extract_keywords_from_text(text)
        phrases = self.rake.get_ranked_phrases_with_scores()
        return [
            {"phrase": phrase, "score": round(score, 2)}
            for score, phrase in phrases[:20]
        ]

    def _extract_sentences(self, doc) -> list:
        """Extract meaningful sentences from resume."""
        sentences = []
        for sent in doc.sents:
            text = sent.text.strip()
            if len(text) > 20:
                sentences.append(text)
        return sentences[:50]

    def _compute_readability(self, text: str, doc) -> dict:
        """Compute basic readability metrics."""
        # Pre-split on bullet characters so spaCy gets better sentence boundaries
        normalized = re.sub(r'[•\-*\u2022\u2023\u25E6]\s*', '\n', text)
        norm_doc = self.nlp(normalized)
        sentences = [s for s in norm_doc.sents if len(s.text.strip()) > 5]
        words = [t for t in norm_doc if not t.is_punct and not t.is_space]
        num_sentences = max(len(sentences), 1)
        num_words = max(len(words), 1)
        avg_words_per_sentence = num_words / num_sentences

        # Flesch-Kincaid approximation
        syllables = sum(self._count_syllables(w.text) for w in words)
        avg_syllables = syllables / num_words
        fk_score = 206.835 - 1.015 * avg_words_per_sentence - 84.6 * avg_syllables
        fk_score = max(0, min(100, fk_score))

        return {
            "word_count": num_words,
            "sentence_count": num_sentences,
            "avg_words_per_sentence": round(avg_words_per_sentence, 1),
            "flesch_kincaid_score": round(fk_score, 1),
            "readability_grade": self._fk_grade(fk_score),
        }

    def _count_syllables(self, word: str) -> int:
        word = word.lower()
        vowels = "aeiouy"
        count = 0
        prev_vowel = False
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_vowel:
                count += 1
            prev_vowel = is_vowel
        return max(1, count)

    def _fk_grade(self, score: float) -> str:
        if score >= 70:
            return "Easy"
        elif score >= 50:
            return "Standard"
        elif score >= 30:
            return "Difficult"
        else:
            return "Very Difficult"

    def _get_embedding(self, text: str) -> list:
        """Generate sentence embedding for semantic similarity."""
        embedding = self.embedder.encode(text[:2000], convert_to_numpy=True)
        return embedding.tolist()

    def get_semantic_similarity(self, text1: str, text2: str) -> float:
        """Compute cosine similarity between two texts using sentence embeddings."""
        if not text1.strip() or not text2.strip():
            return 0.0
        emb1 = self.embedder.encode(text1[:2000], convert_to_numpy=True)
        emb2 = self.embedder.encode(text2[:2000], convert_to_numpy=True)
        sim = cosine_similarity([emb1], [emb2])[0][0]
        return float(sim)

    def get_tfidf_similarity(self, text1: str, text2: str) -> float:
        """Compute TF-IDF cosine similarity between two texts."""
        if not text1.strip() or not text2.strip():
            return 0.0
        try:
            matrix = self.tfidf.fit_transform([text1, text2])
            sim = cosine_similarity(matrix[0], matrix[1])[0][0]
            return float(sim)
        except Exception:
            return 0.0
