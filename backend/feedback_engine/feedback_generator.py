"""
Feedback Generator - AI-driven, context-aware resume feedback.
Uses NLP analysis + scoring data to produce actionable suggestions.
"""
import re


# Action verb upgrade map
WEAK_TO_STRONG = {
    "worked": "collaborated / engineered / delivered",
    "helped": "supported / facilitated / enabled",
    "assisted": "contributed / accelerated / strengthened",
    "did": "executed / implemented / achieved",
    "made": "developed / built / created",
    "used": "leveraged / utilized / applied",
    "tried": "pursued / explored / implemented",
    "participated": "contributed / engaged / drove",
    "involved": "spearheaded / led / directed",
    "responsible": "owned / managed / oversaw",
    "handled": "managed / directed / coordinated",
    "dealt": "resolved / managed / navigated",
}

SECTION_ADVICE = {
    "summary": "Add a professional summary (2-3 sentences) at the top highlighting your value proposition.",
    "experience": "Add a Work Experience section with role titles, company names, dates, and bullet-point achievements.",
    "education": "Add an Education section with degree, institution, and graduation year.",
    "skills": "Add a Skills section listing technical and soft skills relevant to your target role.",
    "projects": "Add a Projects section showcasing 2-3 relevant projects with tech stack and outcomes.",
    "certifications": "Consider adding certifications to strengthen your credibility.",
    "achievements": "Add an Achievements section to highlight awards, recognitions, or notable accomplishments.",
}


class FeedbackGenerator:
    """
    Generates intelligent, context-aware feedback using:
    - NLP analysis results
    - ATS score breakdown
    - Rule-based + NLP-based logic
    """

    def __init__(self, nlp_processor):
        self.nlp = nlp_processor

    def generate(self, resume_text: str, nlp_data: dict, score_data: dict, job_description: str) -> dict:
        feedback = {
            "overall_summary": self._overall_summary(score_data),
            "missing_sections": self._missing_sections_feedback(nlp_data["sections"]),
            "action_verb_feedback": self._action_verb_feedback(nlp_data),
            "keyword_feedback": self._keyword_feedback(score_data, job_description),
            "content_feedback": self._content_feedback(resume_text, nlp_data, score_data),
            "readability_feedback": self._readability_feedback(nlp_data["readability"]),
            "structure_feedback": self._structure_feedback(resume_text, nlp_data),
            "project_strength_feedback": self._project_strength_feedback(nlp_data),
            "top_suggestions": [],
        }
        feedback["top_suggestions"] = self._compile_top_suggestions(feedback)
        return feedback

    def _project_strength_feedback(self, nlp_data: dict) -> dict:
        bullet_analysis = nlp_data.get("bullet_analysis", [])
        if not bullet_analysis:
            return {
                "score": 0,
                "message": "No bullet points found to analyze. Please use bullet points for experience and projects.",
                "tips": ["Convert paragraphs into bullet points for better readability and impact."]
            }
            
        total = len(bullet_analysis)
        with_quant = sum(1 for b in bullet_analysis if b.get("has_quantification", False))
        with_strong = sum(1 for b in bullet_analysis if b.get("has_strong_verb", False))
        
        # Calculate a score out of 100 based on metrics and action verbs
        score = min(100, int(((with_quant / total) * 60) + ((with_strong / total) * 40)))
        
        tips = []
        if score < 50:
            tips.append("Most of your bullets lack measurable results or strong action verbs.")
        elif score < 80:
            tips.append("Good start, but add more numbers and metrics to strengthen your impact.")
        else:
            tips.append("Excellent project descriptions with strong action verbs and quantified impact.")
            
        if with_quant < total * 0.5:
            tips.append("Try to add specific metrics (e.g., 'improved by 20%', 'led team of 5') to more bullets.")
            
        return {
            "score": score,
            "total_bullets": total,
            "quantified_bullets": with_quant,
            "strong_verb_bullets": with_strong,
            "message": f"Project Strength Score: {score}/100 based on {total} bullet points.",
            "tips": tips
        }

    def _overall_summary(self, score_data: dict) -> str:
        score = score_data["final_score"]
        grade = score_data["grade"]
        dim = score_data["dimension_scores"]

        weakest = min(dim, key=dim.get)
        strongest = max(dim, key=dim.get)

        label_map = {
            "semantic_similarity": "semantic alignment with the job description",
            "keyword_coverage": "keyword coverage",
            "section_completeness": "section completeness",
            "content_strength": "content strength",
            "readability": "readability",
        }

        return (
            f"Your resume scored {score}/100 ({grade}). "
            f"Your strongest area is {label_map.get(strongest, strongest)} "
            f"({dim[strongest]}/100), while {label_map.get(weakest, weakest)} "
            f"({dim[weakest]}/100) needs the most improvement."
        )

    def _missing_sections_feedback(self, sections: dict) -> list:
        suggestions = []
        for section, present in sections.items():
            if not present and section in SECTION_ADVICE:
                suggestions.append({
                    "section": section,
                    "priority": "high" if section in ["experience", "skills", "education"] else "medium",
                    "suggestion": SECTION_ADVICE[section],
                })
        return suggestions

    def _action_verb_feedback(self, nlp_data: dict) -> dict:
        action_verbs = nlp_data.get("action_verbs", [])
        weak_verbs = nlp_data.get("weak_verbs", [])
        weak_skills = nlp_data.get("skills", {}).get("weak", [])

        upgrades = []
        for wv in weak_verbs:
            if wv in WEAK_TO_STRONG:
                upgrades.append({
                    "weak": wv,
                    "suggestions": WEAK_TO_STRONG[wv],
                })
        
        # Add weak skills suggestions
        weak_skill_map = {
            "Hardworking": "Dedicated / Results-driven / Diligent",
            "Quick Learner": "Adaptable / Fast-paced environment thrives",
            "Team Player": "Collaborative / Cross-functional team member",
            "Motivated": "Proactive / Self-starter",
            "Passionate": "Enthusiastic / Committed",
            "Multitasking": "Prioritization / Time management",
            "Organized": "Detail-oriented / Methodical",
            "Dedicated": "Committed / Mission-driven",
            "Punctual": "Reliable / Consistent",
            "Reliable": "Dependable / Proven track record",
            "Self-Motivated": "Proactive / Autonomous",
            "Fast Learner": "Adaptable / Quick to master new tech"
        }
        
        for ws in weak_skills:
            if ws in weak_skill_map:
                upgrades.append({
                    "weak": f"Skill: '{ws}'",
                    "suggestions": weak_skill_map[ws]
                })
            else:
                upgrades.append({
                    "weak": f"Skill: '{ws}'",
                    "suggestions": "Show, don't tell! Use concrete examples instead of this generic term."
                })

        strength = "strong" if len(action_verbs) >= 8 else "moderate" if len(action_verbs) >= 4 else "weak"

        return {
            "action_verb_count": len(action_verbs),
            "action_verbs_found": action_verbs[:10],
            "verb_strength": strength,
            "weak_verbs_found": weak_verbs,
            "upgrade_suggestions": upgrades,
            "tip": (
                "Great use of action verbs!" if strength == "strong"
                else "Start bullet points with strong action verbs like 'Led', 'Built', 'Optimized', 'Reduced'."
            ),
        }

    def _keyword_feedback(self, score_data: dict, job_description: str) -> dict:
        missing = score_data.get("missing_keywords", [])
        matched = score_data.get("matched_keywords", [])
        kw_score = score_data["dimension_scores"].get("keyword_coverage", 0)

        if not job_description:
            return {
                "note": "No job description provided. Paste a job description for targeted keyword analysis.",
                "matched_keywords": [],
                "missing_keywords": [],
            }

        suggestions = []
        actionable_suggestions = []
        templates = [
            "Developed robust solutions using {kw} to improve system efficiency by 20%.",
            "Leveraged {kw} to optimize workflows and deliver high-quality results.",
            "Integrated {kw} within the project architecture, reducing processing time.",
            "Collaborated with cross-functional teams utilizing {kw} to achieve project milestones."
        ]
        
        for i, kw in enumerate(missing[:10]):
            suggestions.append(f"Consider adding '{kw}' — it appears in the job description but not your resume.")
            template = templates[i % len(templates)].format(kw=kw)
            actionable_suggestions.append({
                "keyword": kw,
                "suggestion": f"Add this keyword to improve your score by ~2%.",
                "example": template
            })

        return {
            "keyword_score": kw_score,
            "matched_keywords": matched[:15],
            "missing_keywords": missing[:15],
            "suggestions": suggestions,
            "actionable_suggestions": actionable_suggestions,
            "tip": (
                "Good keyword alignment!" if kw_score >= 70
                else "Incorporate more keywords from the job description naturally into your experience bullets."
            ),
        }

    def _content_feedback(self, resume_text: str, nlp_data: dict, score_data: dict) -> list:
        feedback = []
        details = score_data["details"].get("content_strength", {})

        # Quantification
        quant = details.get("quantification_count", 0)
        if quant < 3:
            feedback.append({
                "type": "quantification",
                "priority": "high",
                "message": "Add measurable achievements. Use numbers, percentages, and metrics (e.g., 'Reduced load time by 40%', 'Managed team of 8 engineers').",
            })
        elif quant < 6:
            feedback.append({
                "type": "quantification",
                "priority": "medium",
                "message": f"You have {quant} quantified points. Aim for at least 6-8 metrics to strengthen impact.",
            })

        # Word count
        wc = details.get("word_count", 0)
        if wc < 200:
            feedback.append({
                "type": "length",
                "priority": "high",
                "message": f"Resume is too short ({wc} words). Expand your experience and skills sections to 400-700 words.",
            })
        elif wc > 1000:
            feedback.append({
                "type": "length",
                "priority": "medium",
                "message": f"Resume is quite long ({wc} words). Consider trimming to 600-800 words for better ATS parsing.",
            })

        # Skills count
        skills_data = nlp_data.get("skills", {})
        strong_skills = skills_data.get("strong", [])
        if len(strong_skills) < 10:
            feedback.append({
                "type": "skills",
                "priority": "medium",
                "message": "Expand your skills section. List specific tools, technologies, frameworks, and methodologies.",
            })

        # Contact info check
        has_email = bool(re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", resume_text))
        has_phone = bool(re.search(r"(\+?\d[\d\s\-().]{7,}\d)", resume_text))
        if not has_email:
            feedback.append({
                "type": "contact",
                "priority": "high",
                "message": "No email address detected. Ensure your contact information is clearly visible.",
            })
        if not has_phone:
            feedback.append({
                "type": "contact",
                "priority": "medium",
                "message": "No phone number detected. Add your phone number to the contact section.",
            })

        return feedback

    def _readability_feedback(self, readability: dict) -> dict:
        fk = readability.get("flesch_kincaid_score", 50)
        avg_words = readability.get("avg_words_per_sentence", 15)
        grade = readability.get("readability_grade", "Standard")

        tips = []
        actionable_fixes = []
        if avg_words > 25:
            tips.append("Your sentences are too long. Break them into shorter, punchy bullet points.")
            actionable_fixes.append({
                "issue": "Overly Long Sentences",
                "before": "I was responsible for designing and developing the frontend of the application using React and Redux while also managing the backend API creation using Node.js and ensuring everything was deployed to AWS properly.",
                "after": "• Developed React/Redux frontend.\n• Built Node.js API.\n• Managed AWS deployment."
            })
        if avg_words < 6:
            tips.append("Some sentences are very short. Ensure bullet points are descriptive enough.")
        if fk < 30:
            tips.append("Text is complex. Use simpler, clearer language for better ATS parsing.")
            actionable_fixes.append({
                "issue": "High Complexity",
                "before": "Utilized synergized methodologies to operationalize cross-functional paradigms.",
                "after": "Collaborated with teams to implement standard processes."
            })
        if fk > 80:
            tips.append("Text may be too simple. Add more technical depth to demonstrate expertise.")

        return {
            "flesch_kincaid_score": fk,
            "grade": grade,
            "avg_sentence_length": avg_words,
            "tips": tips if tips else ["Readability looks good!"],
            "actionable_fixes": actionable_fixes
        }

    def _structure_feedback(self, resume_text: str, nlp_data: dict) -> list:
        feedback = []

        # Check for dates
        date_pattern = re.compile(r"\b(19|20)\d{2}\b|\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*(19|20)\d{2}\b", re.IGNORECASE)
        dates = date_pattern.findall(resume_text)
        if len(dates) < 2:
            feedback.append({
                "type": "dates",
                "message": "Add clear date ranges to your experience and education entries (e.g., 'Jan 2021 – Present').",
            })

        # Check for URLs/LinkedIn
        has_linkedin = "linkedin" in resume_text.lower()
        has_github = "github" in resume_text.lower()
        if not has_linkedin:
            feedback.append({
                "type": "links",
                "message": "Add your LinkedIn profile URL to increase credibility.",
            })
        if not has_github and any(s in resume_text.lower() for s in ["developer", "engineer", "programmer", "software"]):
            feedback.append({
                "type": "links",
                "message": "Add your GitHub profile to showcase your code and projects.",
            })

        # Bullet point check
        bullet_count = len(re.findall(r"^[\s]*[•\-\*\u2022\u2023\u25E6]", resume_text, re.MULTILINE))
        if bullet_count < 5:
            feedback.append({
                "type": "formatting",
                "message": "Use bullet points to list achievements and responsibilities. Bullet-point format is more ATS-friendly.",
            })

        return feedback

    def _compile_top_suggestions(self, feedback: dict) -> list:
        """Compile the top 5 most impactful suggestions across all categories."""
        suggestions = []

        # High priority missing sections
        for item in feedback.get("missing_sections", []):
            if item["priority"] == "high":
                suggestions.append(item["suggestion"])

        # High priority content feedback
        for item in feedback.get("content_feedback", []):
            if item["priority"] == "high":
                suggestions.append(item["message"])

        # Keyword suggestions
        kw = feedback.get("keyword_feedback", {})
        if kw.get("suggestions"):
            suggestions.append(kw["suggestions"][0])

        # Action verb tip
        av = feedback.get("action_verb_feedback", {})
        if av.get("verb_strength") != "strong" and av.get("action_verb_count", 0) == 0:
            if av.get("tip", ""):
                suggestions.append(av.get("tip", ""))

        # Structure feedback
        for item in feedback.get("structure_feedback", []):
            suggestions.append(item["message"])

        # Deduplicate and limit
        seen = set()
        top = []
        for s in suggestions:
            if s and s not in seen:
                seen.add(s)
                top.append(s)
            if len(top) >= 5:
                break

        return top
