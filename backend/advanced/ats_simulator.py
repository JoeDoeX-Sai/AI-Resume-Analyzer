"""
ATS Simulator - Simulates a recruiter 6-second scan and ATS parsing.
Gives pass/fail result with detailed reasoning.
"""
import re


CRITICAL_SECTIONS = ["experience", "education", "skills", "summary"]
SECTION_PATTERNS = {
    "experience": r"(work experience|professional experience|employment|experience|work history)",
    "education": r"(education|academic|qualification|degree|university|college)",
    "skills": r"(skills|technical skills|core competencies|technologies|tools|expertise)",
    "summary": r"(summary|objective|profile|about me|professional summary)",
    "contact": r"(@|phone|mobile|email|linkedin|github|\+\d)",
    "projects": r"(projects|personal projects|key projects|portfolio)",
    "certifications": r"(certifications|certificates|licenses|credentials)",
}

ATS_UNFRIENDLY_PATTERNS = [
    (r"<[^>]+>", "HTML tags detected — ATS cannot parse HTML."),
    (r"\|{2,}", "Multiple pipe characters may confuse ATS parsers."),
    (r"[^\x00-\x7F]{3,}", "Non-ASCII characters may not parse correctly."),
    (r"\t{3,}", "Excessive tabs may indicate table formatting — avoid tables."),
]


class ATSSimulator:
    def __init__(self, nlp_processor):
        self.nlp = nlp_processor

    def simulate(self, resume_text: str, job_description: str = "") -> dict:
        text_lower = resume_text.lower()
        word_count = len(resume_text.split())

        # --- 6-second scan simulation ---
        first_third = resume_text[:len(resume_text) // 3]
        scan_result = self._six_second_scan(first_third, word_count)

        # --- Section detection ---
        sections_found = {}
        for section, pattern in SECTION_PATTERNS.items():
            sections_found[section] = bool(re.search(pattern, text_lower, re.IGNORECASE))

        # --- ATS parse checks ---
        parse_issues = self._check_parse_issues(resume_text)

        # --- Keyword density ---
        keyword_density = self._keyword_density(resume_text, job_description)

        # --- Weak sections ---
        weak_sections = self._identify_weak_sections(resume_text, sections_found, word_count)

        # --- Pass/Fail decision ---
        verdict, score, reasoning = self._verdict(
            sections_found, parse_issues, scan_result, keyword_density, weak_sections
        )

        return {
            "verdict": verdict,
            "ats_score": score,
            "reasoning": reasoning,
            "six_second_scan": scan_result,
            "sections_found": sections_found,
            "parse_issues": parse_issues,
            "weak_sections": weak_sections,
            "keyword_density": keyword_density,
            "recommendations": self._recommendations(sections_found, parse_issues, weak_sections, keyword_density),
        }

    def _six_second_scan(self, first_third: str, total_words: int) -> dict:
        issues = []
        strengths = []

        # Contact info visible early
        has_contact = bool(re.search(r"@|phone|mobile|\+\d{5,}", first_third, re.IGNORECASE))
        if has_contact:
            strengths.append("Contact information is visible at the top.")
        else:
            issues.append("Contact information not found in the top section.")

        # Name/title visible
        lines = [l.strip() for l in first_third.split("\n") if l.strip()]
        has_title = len(lines) > 0 and len(lines[0].split()) <= 5
        if has_title:
            strengths.append("Name or title appears at the top.")
        else:
            issues.append("Name or professional title not clearly visible at the top.")

        # Summary present early
        has_summary = bool(re.search(r"summary|objective|profile|about", first_third, re.IGNORECASE))
        if has_summary:
            strengths.append("Professional summary found near the top.")
        else:
            issues.append("No professional summary in the top section — recruiters expect this.")

        # Word count check
        if total_words < 200:
            issues.append("Resume is too sparse — likely to be dismissed quickly.")
        elif total_words > 1200:
            issues.append("Resume is too long — key information may be buried.")
        else:
            strengths.append(f"Resume length ({total_words} words) is within acceptable range.")

        return {
            "passed": len(issues) == 0,
            "strengths": strengths,
            "issues": issues,
        }

    def _check_parse_issues(self, resume_text: str) -> list:
        issues = []
        for pattern, message in ATS_UNFRIENDLY_PATTERNS:
            if re.search(pattern, resume_text):
                issues.append(message)

        # Check for date formats
        has_dates = bool(re.search(r"\b(19|20)\d{2}\b", resume_text))
        if not has_dates:
            issues.append("No dates detected — ATS expects date ranges in experience/education.")

        # Check for bullet points
        bullet_count = len(re.findall(r"^[\s]*[•\-\*]", resume_text, re.MULTILINE))
        if bullet_count < 3:
            issues.append("Few or no bullet points — ATS prefers structured bullet-point format.")

        return issues

    def _keyword_density(self, resume_text: str, job_description: str) -> dict:
        if not job_description:
            return {"note": "No job description provided for keyword density analysis."}

        jd_words = set(re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#.]{2,}\b", job_description.lower()))
        resume_lower = resume_text.lower()
        stop = {"the", "and", "for", "with", "that", "this", "are", "you",
                "will", "have", "from", "our", "your", "they", "their", "was",
                "has", "been", "its", "not", "but", "can", "all", "any"}
        jd_words -= stop

        matched = [w for w in jd_words if w in resume_lower]
        missing = [w for w in jd_words if w not in resume_lower]
        density = round(len(matched) / max(len(jd_words), 1) * 100, 1)

        return {
            "density_percent": density,
            "matched_count": len(matched),
            "total_jd_words": len(jd_words),
            "top_missing": sorted(missing)[:10],
        }

    def _identify_weak_sections(self, resume_text: str, sections_found: dict, word_count: int) -> list:
        weak = []
        text_lower = resume_text.lower()

        if not sections_found.get("contact"):
            weak.append({
                "section": "Contact Information",
                "reason": "No contact details detected. ATS requires email and phone.",
                "severity": "critical",
            })

        if not sections_found.get("experience"):
            weak.append({
                "section": "Work Experience",
                "reason": "No experience section found. This is the most critical section.",
                "severity": "critical",
            })
        else:
            # Check experience has enough content
            exp_bullets = len(re.findall(r"^[\s]*[•\-\*]", resume_text, re.MULTILINE))
            if exp_bullets < 4:
                weak.append({
                    "section": "Work Experience",
                    "reason": "Experience section has few bullet points. Add 3-5 bullets per role.",
                    "severity": "high",
                })

        if not sections_found.get("skills"):
            weak.append({
                "section": "Skills",
                "reason": "No skills section found. ATS scans for skill keywords.",
                "severity": "critical",
            })

        if not sections_found.get("education"):
            weak.append({
                "section": "Education",
                "reason": "No education section found.",
                "severity": "high",
            })

        if not sections_found.get("summary"):
            weak.append({
                "section": "Professional Summary",
                "reason": "No summary section. A 2-3 sentence summary improves ATS ranking.",
                "severity": "medium",
            })

        # Check quantification
        numbers = re.findall(r"\b\d+[\%\+]?\b", resume_text)
        if len(numbers) < 3:
            weak.append({
                "section": "Achievements",
                "reason": "Very few quantified metrics. Add numbers to demonstrate impact.",
                "severity": "medium",
            })

        return weak

    def _verdict(self, sections_found, parse_issues, scan_result, keyword_density, weak_sections) -> tuple:
        score = 100
        reasoning = []

        # Critical section penalties
        critical_missing = [s for s in ["experience", "skills", "education", "contact"]
                            if not sections_found.get(s)]
        score -= len(critical_missing) * 20
        if critical_missing:
            reasoning.append(f"Missing critical sections: {', '.join(critical_missing)}.")

        # Parse issue penalties
        score -= len(parse_issues) * 8
        if parse_issues:
            reasoning.append(f"{len(parse_issues)} ATS parsing issue(s) detected.")

        # 6-second scan penalties
        score -= len(scan_result.get("issues", [])) * 5
        if scan_result.get("issues"):
            reasoning.append("Failed 6-second recruiter scan on key visibility checks.")

        # Keyword density
        density = keyword_density.get("density_percent", 50)
        if density < 30:
            score -= 15
            reasoning.append(f"Low keyword match ({density}%) with job description.")
        elif density < 50:
            score -= 5

        # Weak sections
        critical_weak = [w for w in weak_sections if w["severity"] == "critical"]
        score -= len(critical_weak) * 10

        score = max(0, min(100, score))

        if score >= 70:
            verdict = "PASS"
            if not reasoning:
                reasoning.append("Resume meets core ATS requirements.")
        elif score >= 45:
            verdict = "CONDITIONAL"
            reasoning.append("Resume needs improvements before it will reliably pass ATS filters.")
        else:
            verdict = "FAIL"
            reasoning.append("Resume is likely to be rejected by ATS systems without significant revision.")

        return verdict, score, reasoning

    def _recommendations(self, sections_found, parse_issues, weak_sections, keyword_density) -> list:
        recs = []

        for issue in parse_issues[:3]:
            recs.append({"priority": "high", "action": issue})

        for ws in weak_sections:
            if ws["severity"] == "critical":
                recs.append({"priority": "critical", "action": ws["reason"]})

        missing_kw = keyword_density.get("top_missing", [])
        if missing_kw:
            recs.append({
                "priority": "medium",
                "action": f"Add these missing keywords from the job description: {', '.join(missing_kw[:5])}.",
            })

        for ws in weak_sections:
            if ws["severity"] == "high":
                recs.append({"priority": "high", "action": ws["reason"]})

        return recs[:8]
