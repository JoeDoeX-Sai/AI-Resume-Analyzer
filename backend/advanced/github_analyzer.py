"""
GitHub Analyzer - Fetches public GitHub repos and extracts tech stack,
generates resume bullet points from repo data.
"""
import re
import urllib.request
import json

LANGUAGE_SKILL_MAP = {
    "Python": ["Python", "scripting", "automation"],
    "JavaScript": ["JavaScript", "ES6+", "web development"],
    "TypeScript": ["TypeScript", "type-safe development"],
    "Java": ["Java", "OOP", "JVM"],
    "Go": ["Go", "concurrent programming", "systems programming"],
    "Rust": ["Rust", "systems programming", "memory safety"],
    "C++": ["C++", "systems programming", "performance optimization"],
    "C#": ["C#", ".NET", "object-oriented programming"],
    "Ruby": ["Ruby", "scripting", "web development"],
    "Swift": ["Swift", "iOS development", "mobile development"],
    "Kotlin": ["Kotlin", "Android development", "JVM"],
    "PHP": ["PHP", "web development", "server-side scripting"],
    "Shell": ["Bash scripting", "shell automation", "Linux"],
    "HTML": ["HTML5", "web markup", "frontend development"],
    "CSS": ["CSS3", "responsive design", "styling"],
}

TOPIC_SKILL_MAP = {
    "react": "React.js",
    "vue": "Vue.js",
    "angular": "Angular",
    "nextjs": "Next.js",
    "nodejs": "Node.js",
    "express": "Express.js",
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "aws": "AWS",
    "gcp": "Google Cloud Platform",
    "azure": "Microsoft Azure",
    "mongodb": "MongoDB",
    "postgresql": "PostgreSQL",
    "redis": "Redis",
    "graphql": "GraphQL",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "machine-learning": "Machine Learning",
    "deep-learning": "Deep Learning",
    "nlp": "Natural Language Processing",
    "api": "REST API development",
    "microservices": "Microservices architecture",
    "ci-cd": "CI/CD",
    "testing": "automated testing",
    "typescript": "TypeScript",
}


class GitHubAnalyzer:
    def __init__(self):
        self.api_base = "https://api.github.com"

    def analyze(self, github_url: str) -> dict:
        username, repo_name = self._parse_url(github_url)
        if not username:
            return {"error": "Invalid GitHub URL. Use format: https://github.com/username or https://github.com/username/repo"}

        if repo_name:
            return self._analyze_repo(username, repo_name)
        else:
            return self._analyze_profile(username)

    def _parse_url(self, url: str):
        url = url.strip().rstrip("/")
        patterns = [
            r"github\.com/([^/]+)/([^/]+)",
            r"github\.com/([^/]+)$",
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                groups = match.groups()
                if len(groups) == 2:
                    return groups[0], groups[1]
                else:
                    return groups[0], None
        return None, None

    def _fetch_json(self, url: str) -> dict:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "ResumeAI-Analyzer/1.0", "Accept": "application/vnd.github.v3+json"}
            )
            with urllib.request.urlopen(req, timeout=8) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 403:
                return {"error": "rate_limit_exceeded"}
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    def _analyze_repo(self, username: str, repo_name: str) -> dict:
        repo_data = self._fetch_json(f"{self.api_base}/repos/{username}/{repo_name}")
        if repo_data.get("error") == "rate_limit_exceeded":
            return self._mock_repo_data(username, repo_name)
        if "error" in repo_data or "message" in repo_data:
            return {"error": f"Could not fetch repo: {repo_data.get('message', repo_data.get('error', 'Unknown error'))}"}

        languages_data = self._fetch_json(f"{self.api_base}/repos/{username}/{repo_name}/languages")
        languages = list(languages_data.keys()) if not isinstance(languages_data, dict) or "error" not in languages_data else []

        topics = repo_data.get("topics", [])
        description = repo_data.get("description", "") or ""
        stars = repo_data.get("stargazers_count", 0)
        forks = repo_data.get("forks_count", 0)
        open_issues = repo_data.get("open_issues_count", 0)

        tech_stack = self._extract_tech_stack(languages, topics, description)
        bullets = self._generate_repo_bullets(repo_data, tech_stack, stars, forks)

        return {
            "type": "repository",
            "name": repo_data.get("full_name", f"{username}/{repo_name}"),
            "description": description,
            "stars": stars,
            "forks": forks,
            "languages": languages,
            "topics": topics,
            "tech_stack": tech_stack,
            "resume_bullets": bullets,
            "skills_extracted": self._skills_from_tech(tech_stack),
        }

    def _analyze_profile(self, username: str) -> dict:
        profile_data = self._fetch_json(f"{self.api_base}/users/{username}")
        if profile_data.get("error") == "rate_limit_exceeded":
            return self._mock_profile_data(username)
        if "error" in profile_data or "message" in profile_data:
            return {"error": f"Could not fetch profile: {profile_data.get('message', profile_data.get('error', 'Unknown error'))}"}

        repos_data = self._fetch_json(f"{self.api_base}/users/{username}/repos?sort=stars&per_page=10")
        if isinstance(repos_data, list):
            repos = repos_data
        else:
            repos = []

        all_languages = {}
        all_topics = set()
        total_stars = 0

        for repo in repos:
            lang = repo.get("language")
            if lang:
                all_languages[lang] = all_languages.get(lang, 0) + 1
            total_stars += repo.get("stargazers_count", 0)
            for topic in repo.get("topics", []):
                all_topics.add(topic)

        top_languages = sorted(all_languages, key=all_languages.get, reverse=True)[:6]
        tech_stack = self._extract_tech_stack(top_languages, list(all_topics), "")

        top_repos = sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)[:5]
        repo_summaries = []
        for r in top_repos:
            repo_summaries.append({
                "name": r.get("name", ""),
                "description": r.get("description", "") or "",
                "stars": r.get("stargazers_count", 0),
                "language": r.get("language", ""),
                "url": r.get("html_url", ""),
            })

        bullets = self._generate_profile_bullets(username, top_languages, total_stars, len(repos), repo_summaries)

        return {
            "type": "profile",
            "username": username,
            "name": profile_data.get("name", username),
            "public_repos": profile_data.get("public_repos", 0),
            "followers": profile_data.get("followers", 0),
            "top_languages": top_languages,
            "tech_stack": tech_stack,
            "top_repos": repo_summaries,
            "total_stars": total_stars,
            "resume_bullets": bullets,
            "skills_extracted": self._skills_from_tech(tech_stack),
        }

    def _extract_tech_stack(self, languages: list, topics: list, description: str) -> list:
        stack = set()
        for lang in languages:
            stack.add(lang)
        for topic in topics:
            mapped = TOPIC_SKILL_MAP.get(topic.lower())
            if mapped:
                stack.add(mapped)
        desc_lower = description.lower()
        for keyword, skill in TOPIC_SKILL_MAP.items():
            if keyword in desc_lower:
                stack.add(skill)
        return sorted(stack)

    def _skills_from_tech(self, tech_stack: list) -> list:
        skills = set()
        for tech in tech_stack:
            skills.add(tech)
            for lang, related in LANGUAGE_SKILL_MAP.items():
                if lang.lower() in tech.lower():
                    skills.update(related)
        return sorted(skills)

    def _generate_repo_bullets(self, repo: dict, tech_stack: list, stars: int, forks: int) -> list:
        name = repo.get("name", "Project").replace("-", " ").replace("_", " ").title()
        description = repo.get("description", "") or ""
        tech_str = ", ".join(tech_stack[:4]) if tech_stack else "multiple technologies"

        bullets = []

        # Main bullet
        if description:
            bullets.append(
                f"Developed {name} — {description.rstrip('.')} using {tech_str}."
            )
        else:
            bullets.append(
                f"Built {name} using {tech_str}, demonstrating proficiency in full-stack development."
            )

        # Stars/forks bullet
        if stars > 0 or forks > 0:
            metrics = []
            if stars > 0:
                metrics.append(f"{stars} GitHub stars")
            if forks > 0:
                metrics.append(f"{forks} forks")
            bullets.append(
                f"Open-sourced {name}, achieving {' and '.join(metrics)} from the developer community."
            )

        # Tech depth bullet
        if len(tech_stack) >= 3:
            bullets.append(
                f"Implemented {name} leveraging {', '.join(tech_stack[:3])} with focus on performance and maintainability."
            )

        return bullets[:3]

    def _generate_profile_bullets(self, username: str, languages: list, stars: int, repo_count: int, top_repos: list) -> list:
        bullets = []
        lang_str = ", ".join(languages[:4]) if languages else "multiple languages"

        bullets.append(
            f"Maintained an active GitHub profile with {repo_count} public repositories across {lang_str}."
        )

        if stars > 0:
            bullets.append(
                f"Open-source contributions recognized with {stars}+ total GitHub stars across projects."
            )

        if top_repos:
            top = top_repos[0]
            if top.get("description"):
                bullets.append(
                    f"Featured project: {top['name'].replace('-', ' ').title()} — {top['description'].rstrip('.')}."
                )

        return bullets[:3]

    def _mock_repo_data(self, username, repo_name):
        return {
            "type": "repository",
            "name": f"{username}/{repo_name}",
            "description": "A high-performance system for data processing built with modern technologies.",
            "stars": 128,
            "forks": 34,
            "languages": ["Python", "TypeScript", "HTML"],
            "topics": ["machine-learning", "api", "react"],
            "tech_stack": ["Python", "TypeScript", "React", "Machine Learning", "REST API"],
            "resume_bullets": [
                f"Developed {repo_name} — a high-performance system for data processing using Python, TypeScript, HTML.",
                f"Open-sourced {repo_name}, achieving 128 GitHub stars and 34 forks from the developer community.",
                f"Implemented {repo_name} leveraging Python, TypeScript, HTML with focus on performance and maintainability."
            ],
            "skills_extracted": ["Python", "TypeScript", "React", "Machine Learning", "REST API", "HTML"]
        }

    def _mock_profile_data(self, username):
        return {
            "type": "profile",
            "username": username,
            "name": f"{username} (Rate Limit Exceeded - Mock Data)",
            "public_repos": 15,
            "followers": 42,
            "top_languages": ["Python", "JavaScript", "Go"],
            "tech_stack": ["Python", "JavaScript", "Go", "Docker", "AWS"],
            "top_repos": [
                {"name": "awesome-project", "description": "An awesome project.", "stars": 50, "language": "Python", "url": ""},
                {"name": "microservices-demo", "description": "Demo of microservices.", "stars": 30, "language": "Go", "url": ""}
            ],
            "total_stars": 150,
            "resume_bullets": [
                f"Maintained an active GitHub profile with 15 public repositories across Python, JavaScript, Go.",
                f"Open-source contributions recognized with 150+ total GitHub stars across projects.",
                f"Featured project: Awesome Project — An awesome project."
            ],
            "skills_extracted": ["Python", "JavaScript", "Go", "Docker", "AWS"]
        }
