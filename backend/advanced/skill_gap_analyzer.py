"""
Skill Gap Analyzer - Extracts missing skills from job description
and generates a learning roadmap for each gap.
"""
import re

# Learning roadmap database per skill category
LEARNING_ROADMAP = {
    "python": {
        "resources": ["Python.org official tutorial", "Automate the Boring Stuff (free online)", "Real Python tutorials"],
        "timeline": "4-8 weeks for proficiency",
        "projects": ["Build a CLI tool", "Create a REST API with Flask", "Data analysis with Pandas"],
    },
    "javascript": {
        "resources": ["MDN Web Docs", "javascript.info", "Eloquent JavaScript (free online)"],
        "timeline": "6-10 weeks for proficiency",
        "projects": ["Build a to-do app", "Create a weather dashboard", "Build a REST API with Node.js"],
    },
    "react": {
        "resources": ["React official docs (react.dev)", "Scrimba React course", "Full Stack Open (free)"],
        "timeline": "4-6 weeks after JavaScript basics",
        "projects": ["Build a portfolio site", "Create a task manager", "Build a real-time chat app"],
    },
    "node.js": {
        "resources": ["Node.js official docs", "The Odin Project", "NodeSchool.io (free)"],
        "timeline": "3-5 weeks after JavaScript basics",
        "projects": ["Build a REST API", "Create a CLI tool", "Build a real-time app with Socket.io"],
    },
    "sql": {
        "resources": ["SQLZoo (free)", "Mode Analytics SQL Tutorial", "PostgreSQL official docs"],
        "timeline": "2-4 weeks for basics",
        "projects": ["Design a database schema", "Write complex queries", "Build a reporting dashboard"],
    },
    "docker": {
        "resources": ["Docker official docs", "Play with Docker (free)", "Docker Deep Dive by Nigel Poulton"],
        "timeline": "2-3 weeks for basics",
        "projects": ["Containerize a web app", "Set up multi-container app with Compose", "Deploy to cloud"],
    },
    "aws": {
        "resources": ["AWS Free Tier + official docs", "A Cloud Guru (free tier)", "AWS Skill Builder"],
        "timeline": "6-12 weeks for associate level",
        "projects": ["Deploy a static site on S3", "Build a serverless API with Lambda", "Set up CI/CD pipeline"],
    },
    "kubernetes": {
        "resources": ["Kubernetes official docs", "Kubernetes the Hard Way (GitHub)", "KodeKloud free tier"],
        "timeline": "4-8 weeks after Docker basics",
        "projects": ["Deploy an app to a local cluster", "Set up auto-scaling", "Implement rolling updates"],
    },
    "machine learning": {
        "resources": ["fast.ai (free)", "Coursera ML Specialization (Andrew Ng)", "Kaggle Learn (free)"],
        "timeline": "8-16 weeks for fundamentals",
        "projects": ["Build a classifier", "Create a recommendation system", "Deploy a model as an API"],
    },
    "typescript": {
        "resources": ["TypeScript official docs", "Total TypeScript (free tier)", "Execute Program"],
        "timeline": "2-4 weeks after JavaScript basics",
        "projects": ["Convert a JS project to TS", "Build a typed REST API", "Create a typed React app"],
    },
    "git": {
        "resources": ["Pro Git book (free online)", "GitHub Skills (free)", "Learn Git Branching (interactive)"],
        "timeline": "1-2 weeks for basics",
        "projects": ["Contribute to an open source project", "Set up a CI/CD workflow", "Practice branching strategies"],
    },
    "mongodb": {
        "resources": ["MongoDB University (free)", "MongoDB official docs", "Mongoose docs"],
        "timeline": "2-3 weeks for basics",
        "projects": ["Build a CRUD API", "Design a document schema", "Implement aggregation pipelines"],
    },
    "graphql": {
        "resources": ["GraphQL official docs", "How to GraphQL (free)", "Apollo docs"],
        "timeline": "2-4 weeks after REST API basics",
        "projects": ["Build a GraphQL API", "Migrate a REST API to GraphQL", "Add subscriptions"],
    },
    "django": {
        "resources": ["Django official docs", "Django Girls Tutorial (free)", "Two Scoops of Django"],
        "timeline": "4-6 weeks after Python basics",
        "projects": ["Build a blog", "Create an e-commerce site", "Build a REST API with DRF"],
    },
    "flask": {
        "resources": ["Flask official docs", "Flask Mega-Tutorial (Miguel Grinberg)", "Real Python Flask tutorials"],
        "timeline": "2-4 weeks after Python basics",
        "projects": ["Build a REST API", "Create a web app with auth", "Deploy to Heroku/Render"],
    },
    "java": {
        "resources": ["Oracle Java tutorials", "Codecademy Java (free tier)", "Baeldung.com"],
        "timeline": "8-12 weeks for proficiency",
        "projects": ["Build a CLI app", "Create a Spring Boot REST API", "Implement data structures"],
    },
    "spring": {
        "resources": ["Spring official guides", "Baeldung Spring tutorials", "Spring in Action book"],
        "timeline": "4-6 weeks after Java basics",
        "projects": ["Build a REST API", "Add Spring Security", "Connect to a database with JPA"],
    },
    "ci/cd": {
        "resources": ["GitHub Actions docs", "GitLab CI/CD docs", "Jenkins official docs"],
        "timeline": "2-4 weeks for basics",
        "projects": ["Set up automated testing", "Build a deployment pipeline", "Add code quality checks"],
    },
    "redis": {
        "resources": ["Redis official docs", "Redis University (free)", "Redis in Action book"],
        "timeline": "1-2 weeks for basics",
        "projects": ["Implement caching", "Build a session store", "Create a rate limiter"],
    },
    "linux": {
        "resources": ["Linux Journey (free)", "The Linux Command Line (free online)", "OverTheWire Bandit"],
        "timeline": "3-5 weeks for basics",
        "projects": ["Set up a server", "Write shell scripts", "Configure a web server"],
    },
}

DEFAULT_ROADMAP = {
    "resources": ["Official documentation", "YouTube tutorials", "Udemy or Coursera courses"],
    "timeline": "4-8 weeks depending on complexity",
    "projects": ["Build a small project using this skill", "Contribute to an open source project"],
}

TECH_SKILL_PATTERNS = [
    r"\b(python|javascript|typescript|java|c\+\+|c#|ruby|go|rust|swift|kotlin|php|scala)\b",
    r"\b(react|angular|vue|svelte|next\.?js|nuxt|gatsby)\b",
    r"\b(node\.?js|express|django|flask|spring|rails|laravel|fastapi)\b",
    r"\b(sql|mysql|postgresql|mongodb|redis|elasticsearch|cassandra|dynamodb)\b",
    r"\b(aws|gcp|azure|docker|kubernetes|terraform|ansible|jenkins)\b",
    r"\b(machine learning|deep learning|nlp|computer vision|data science|tensorflow|pytorch)\b",
    r"\b(git|github|gitlab|bitbucket|ci/cd|devops|agile|scrum)\b",
    r"\b(graphql|rest|grpc|websocket|microservices|kafka|rabbitmq)\b",
    r"\b(linux|bash|shell|powershell|vim|nginx|apache)\b",
    r"\b(html|css|sass|tailwind|bootstrap|webpack|vite)\b",
]


class SkillGapAnalyzer:
    def __init__(self, nlp_processor):
        self.nlp = nlp_processor

    def analyze(self, resume_text: str, job_description: str) -> dict:
        resume_skills = self._extract_skills_from_text(resume_text)
        jd_skills = self._extract_skills_from_text(job_description)

        resume_lower = {s.lower() for s in resume_skills}
        jd_lower = {s.lower() for s in jd_skills}

        missing = jd_lower - resume_lower
        present = jd_lower & resume_lower
        extra = resume_lower - jd_lower

        match_percent = round(len(present) / max(len(jd_lower), 1) * 100, 1)

        roadmap = []
        for skill in sorted(missing):
            roadmap.append({
                "skill": skill,
                "roadmap": self._get_roadmap(skill),
            })

        return {
            "match_percent": match_percent,
            "skills_required": sorted(jd_lower),
            "skills_present": sorted(present),
            "skills_missing": sorted(missing),
            "skills_extra": sorted(extra)[:10],
            "learning_roadmap": roadmap,
            "priority_skills": self._prioritize(missing, job_description),
        }

    def _extract_skills_from_text(self, text: str) -> set:
        skills = set()
        text_lower = text.lower()
        for pattern in TECH_SKILL_PATTERNS:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            skills.update(m.lower() for m in matches)
        return skills

    def _get_roadmap(self, skill: str) -> dict:
        skill_lower = skill.lower()
        for key, roadmap in LEARNING_ROADMAP.items():
            if key in skill_lower or skill_lower in key:
                return roadmap
        return DEFAULT_ROADMAP

    def _prioritize(self, missing_skills: set, job_description: str) -> list:
        jd_lower = job_description.lower()
        scored = []
        for skill in missing_skills:
            count = len(re.findall(r"\b" + re.escape(skill) + r"\b", jd_lower))
            scored.append((skill, count))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in scored[:5]]
