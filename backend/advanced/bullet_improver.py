"""
Bullet Improver - Rewrites resume bullet points using strong action verbs
and quantified metrics patterns.
"""
import re

# Strong action verb replacements by category
VERB_UPGRADES = {
    "worked": "engineered",
    "helped": "facilitated",
    "assisted": "supported",
    "did": "executed",
    "made": "developed",
    "used": "leveraged",
    "tried": "implemented",
    "participated": "contributed to",
    "involved": "led",
    "responsible for": "owned",
    "handled": "managed",
    "dealt with": "resolved",
    "was part of": "collaborated on",
    "contributed": "delivered",
    "created": "built",
    "wrote": "developed",
    "fixed": "resolved",
    "improved": "optimized",
    "set up": "architected",
    "worked on": "engineered",
}

# Templates for adding quantification hints
QUANTIFICATION_HINTS = [
    "resulting in X% improvement",
    "reducing processing time by X%",
    "increasing efficiency by X%",
    "serving X+ users",
    "cutting costs by $X",
    "improving performance by X%",
]

STRONG_STARTERS = [
    "Engineered", "Architected", "Developed", "Implemented", "Optimized",
    "Designed", "Built", "Deployed", "Automated", "Streamlined",
    "Led", "Delivered", "Reduced", "Increased", "Improved",
    "Collaborated", "Managed", "Launched", "Scaled", "Analyzed",
]


class BulletImprover:
    def __init__(self, nlp_processor):
        self.nlp = nlp_processor

    def improve(self, bullet: str) -> dict:
        original = bullet.strip()
        improved = self._rewrite(original)
        issues = self._detect_issues(original)
        suggestions = self._generate_suggestions(original, improved)

        return {
            "original": original,
            "improved": improved,
            "issues": issues,
            "suggestions": suggestions,
            "has_quantification": self._has_quantification(original),
            "has_strong_verb": self._has_strong_verb(original),
        }

    def _rewrite(self, bullet: str) -> str:
        result = bullet

        # Replace weak verb at start
        for weak, strong in VERB_UPGRADES.items():
            pattern = re.compile(r"^" + re.escape(weak) + r"\b", re.IGNORECASE)
            if pattern.match(result):
                result = pattern.sub(strong.capitalize(), result, count=1)
                break

        # Ensure starts with capital
        if result:
            result = result[0].upper() + result[1:]

        # Remove trailing period for consistency
        result = result.rstrip(".")

        # If no quantification, append a hint
        if not self._has_quantification(result):
            result = result + ", resulting in measurable improvement"

        return result

    def _detect_issues(self, bullet: str) -> list:
        issues = []
        lower = bullet.lower()

        # Weak verb at start
        for weak in VERB_UPGRADES:
            if re.match(r"^" + re.escape(weak) + r"\b", lower):
                issues.append(f"Starts with weak verb '{weak}' — replace with a strong action verb.")
                break

        # No quantification
        if not self._has_quantification(bullet):
            issues.append("No quantified metric detected — add numbers, percentages, or scale.")

        # Too short
        words = bullet.split()
        if len(words) < 6:
            issues.append("Bullet is too short — add more context about impact or scope.")

        # Too long
        if len(words) > 30:
            issues.append("Bullet is too long — trim to 15-20 words for clarity.")

        # Passive voice indicators
        passive_patterns = [r"\bwas\b", r"\bwere\b", r"\bbeen\b", r"\bbeing\b"]
        for p in passive_patterns:
            if re.search(p, lower):
                issues.append("Possible passive voice detected — use active voice for stronger impact.")
                break

        return issues

    def _generate_suggestions(self, original: str, improved: str) -> list:
        suggestions = []

        if not self._has_quantification(original):
            suggestions.append("Add a specific metric: e.g., 'by 40%', 'for 500+ users', 'saving $10K/year'.")

        if not self._has_strong_verb(original):
            suggestions.append(
                "Start with a strong verb such as: " + ", ".join(STRONG_STARTERS[:6]) + "."
            )

        words = original.split()
        if len(words) < 8:
            suggestions.append("Expand the bullet to include: what you did, how you did it, and the result.")

        suggestions.append("Consider adding the technology or tool used (e.g., 'using Python', 'via AWS Lambda').")

        return suggestions[:3]

    def _has_quantification(self, text: str) -> bool:
        return bool(re.search(r"\d+[\%\+\$]?|\$\d+|[Xx]\d+", text))

    def _has_strong_verb(self, text: str) -> bool:
        first_word = text.strip().split()[0].lower().rstrip(".,;") if text.strip() else ""
        return first_word in {v.lower() for v in STRONG_STARTERS}
