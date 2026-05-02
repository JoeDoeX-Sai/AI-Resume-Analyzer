"""
ATS Scorer - Multi-factor intelligent scoring engine.
Scores: semantic similarity, keyword coverage, section completeness,
readability, content strength. Final score: 0-100.
"""
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Weights for each scoring dimension
SCORE_WEIGHTS = {
    "semantic_similarity": 0.30,
    "keyword_coverage": 0.25,
    "section_completeness": 0.20,
    "content_strength": 0.15,
    "readability": 0.10,
}

REQUIRED_SECTIONS = ["experience", "education", "skills"]
BONUS_SECTIONS = ["projects", "summary", "certifications", "achievements"]


class ATSScorer:
    """
    Advanced ATS scoring engine using semantic similarity,
    TF-IDF keyword analysis, and multi-factor evaluation.
    """

    def __init__(self, nlp_processor):
        self.nlp = nlp_processor

    def score(self, resume_text: str, nlp_data: dict, job_description: str) -> dict:
        """Compute full ATS score with breakdown."""

        scores = {}
        details = {}

        # 1. Semantic Similarity (vs job description)
        sem_score, sem_detail = self._score_semantic_similarity(resume_text, job_description)
        scores["semantic_similarity"] = sem_score
        details["semantic_similarity"] = sem_detail

        # 2. Keyword Coverage
        kw_score, kw_detail = self._score_keyword_coverage(resume_text, nlp_data, job_description)
        scores["keyword_coverage"] = kw_score
        details["keyword_coverage"] = kw_detail

        # 3. Section Completeness
        sec_score, sec_detail = self._score_section_completeness(nlp_data["sections"])
        scores["section_completeness"] = sec_score
        details["section_completeness"] = sec_detail

        # 4. Content Strength
        cs_score, cs_detail = self._score_content_strength(resume_text, nlp_data)
        scores["content_strength"] = cs_score
        details["content_strength"] = cs_detail

        # 5. Readability
        rd_score, rd_detail = self._score_readability(nlp_data["readability"])
        scores["readability"] = rd_score
        details["readability"] = rd_detail

        # Weighted final score
        final = sum(scores[k] * SCORE_WEIGHTS[k] for k in scores) * 100
        final = round(min(100, max(0, final)), 1)

        return {
            "final_score": final,
            "grade": self._grade(final),
            "dimension_scores": {k: round(v * 100, 1) for k, v in scores.items()},
            "weights": SCORE_WEIGHTS,
            "details": details,
            "matched_keywords": kw_detail.get("matched", []),
            "missing_keywords": kw_detail.get("missing", []),
        }

    # ------------------------------------------------------------------ #
    #  Dimension scorers                                                   #
    # ------------------------------------------------------------------ #

    def _score_semantic_similarity(self, resume_text: str, job_description: str):
        if not job_description:
            # No JD provided – give neutral score
            return 0.6, {"note": "No job description provided; neutral score applied", "similarity": None}

        # Sentence-transformer semantic similarity
        sem_sim = self.nlp.get_semantic_similarity(resume_text, job_description)
        # TF-IDF cosine similarity
        tfidf_sim = self.nlp.get_tfidf_similarity(resume_text, job_description)
        # Blend: 70% semantic, 30% TF-IDF
        blended = 0.7 * sem_sim + 0.3 * tfidf_sim

        return blended, {
            "semantic_similarity": round(sem_sim, 3),
            "tfidf_similarity": round(tfidf_sim, 3),
            "blended": round(blended, 3),
        }

    def _score_keyword_coverage(self, resume_text: str, nlp_data: dict, job_description: str):
        if not job_description:
            # Fall back to resume's own strong skills if no JD
            resume_skills = nlp_data.get("skills", {})
            jd_keywords = set(resume_skills.get("strong", []))
            return 0.5, {"note": "No keywords to match", "matched": list(jd_keywords)[:20], "missing": []}

        # Extract strict skills from JD using the same pipeline
        jd_doc = self.nlp.nlp(job_description)
        jd_skills_dict = self.nlp._extract_skills(job_description, jd_doc)
        
        # Combine valid skills from JD
        jd_keywords = set(jd_skills_dict["Technical Skills"] + jd_skills_dict["Tools & Technologies"] + jd_skills_dict["Soft Skills"])

        if not jd_keywords:
            return 0.5, {"note": "No valid skills detected in JD", "matched": [], "missing": []}

        # Combine valid skills from Resume
        resume_skills_dict = nlp_data.get("skills", {})
        resume_keywords = set(resume_skills_dict.get("Technical Skills", []) + 
                            resume_skills_dict.get("Tools & Technologies", []) + 
                            resume_skills_dict.get("Soft Skills", []))

        # Strict Set Comparison
        matched = list(jd_keywords.intersection(resume_keywords))
        missing = list(jd_keywords.difference(resume_keywords))

        coverage = len(matched) / max(len(jd_keywords), 1)

        # Weighted: exact matches + partial match bonus
        partial_bonus = 0.0
        resume_lower = resume_text.lower()
        for kw in missing[:]:
            # if a missing skill is found in the raw text (even if filtered out as noise), give partial credit
            if kw.lower() in resume_lower:
                partial_bonus += 0.5 / max(len(jd_keywords), 1)
                missing.remove(kw)
                matched.append(kw)

        final_coverage = min(1.0, coverage + partial_bonus)

        return final_coverage, {
            "total_jd_keywords": len(jd_keywords),
            "matched_count": len(matched),
            "missing_count": len(missing),
            "coverage_ratio": round(coverage, 3),
            "matched": matched[:20],
            "missing": missing[:20],
        }

    def _score_section_completeness(self, sections: dict):
        required_present = sum(1 for s in REQUIRED_SECTIONS if sections.get(s))
        bonus_present = sum(1 for s in BONUS_SECTIONS if sections.get(s))

        required_score = required_present / len(REQUIRED_SECTIONS)
        bonus_score = bonus_present / len(BONUS_SECTIONS)

        # Required sections worth 80%, bonus 20%
        final = 0.8 * required_score + 0.2 * bonus_score

        return final, {
            "required_sections": {s: sections.get(s, False) for s in REQUIRED_SECTIONS},
            "bonus_sections": {s: sections.get(s, False) for s in BONUS_SECTIONS},
            "required_score": round(required_score, 3),
            "bonus_score": round(bonus_score, 3),
        }

    def _score_content_strength(self, resume_text: str, nlp_data: dict):
        action_verbs = nlp_data.get("action_verbs", [])
        weak_verbs = nlp_data.get("weak_verbs", [])
        word_count = nlp_data["readability"]["word_count"]

        # Action verb density
        verb_score = min(1.0, len(action_verbs) / 10)

        # Penalize weak verbs
        weak_penalty = min(0.3, len(weak_verbs) * 0.05)

        # Quantification: look for numbers/metrics
        numbers = re.findall(r"\b\d+[\%\+]?\b", resume_text)
        quant_score = min(1.0, len(numbers) / 10)

        # Word count adequacy (ideal: 400-800 words)
        if word_count < 150:
            length_score = 0.3
        elif word_count < 300:
            length_score = 0.6
        elif word_count <= 900:
            length_score = 1.0
        elif word_count <= 1200:
            length_score = 0.8
        else:
            length_score = 0.6

        final = (0.35 * verb_score + 0.25 * quant_score + 0.25 * length_score - weak_penalty)
        final = max(0.0, min(1.0, final))

        return final, {
            "action_verb_count": len(action_verbs),
            "weak_verb_count": len(weak_verbs),
            "quantification_count": len(numbers),
            "word_count": word_count,
            "verb_score": round(verb_score, 3),
            "quant_score": round(quant_score, 3),
            "length_score": round(length_score, 3),
        }

    def _score_readability(self, readability: dict):
        fk = readability.get("flesch_kincaid_score", 50)
        avg_words = readability.get("avg_words_per_sentence", 15)

        # Ideal FK for resume: 50-70
        if 50 <= fk <= 70:
            fk_score = 1.0
        elif 30 <= fk < 50 or 70 < fk <= 80:
            fk_score = 0.75
        else:
            fk_score = 0.5

        # Ideal sentence length: 10-20 words
        if 10 <= avg_words <= 20:
            len_score = 1.0
        elif 8 <= avg_words < 10 or 20 < avg_words <= 25:
            len_score = 0.75
        else:
            len_score = 0.5

        final = 0.6 * fk_score + 0.4 * len_score
        return final, {
            "flesch_kincaid": fk,
            "avg_sentence_length": avg_words,
            "grade": readability.get("readability_grade", "Unknown"),
        }

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    # Removed _extract_jd_keywords as it is now handled by nlp_processor.

    def _grade(self, score: float) -> str:
        if score >= 85:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 55:
            return "Average"
        elif score >= 40:
            return "Below Average"
        else:
            return "Poor"
