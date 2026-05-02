"""
AI Resume Analyzer - Main Flask Application
"""
import os
import json
from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
from werkzeug.utils import secure_filename
import datetime
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from parsing.resume_parser import ResumeParser
from nlp_engine.nlp_processor import NLPProcessor
from scoring_engine.ats_scorer import ATSScorer
from feedback_engine.feedback_generator import FeedbackGenerator
from advanced.bullet_improver import BulletImprover
from advanced.ats_simulator import ATSSimulator
from advanced.skill_gap_analyzer import SkillGapAnalyzer
from advanced.github_analyzer import GitHubAnalyzer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_FOLDER = os.path.join(BASE_DIR, "..", "frontend")
FRONTEND_FOLDER = os.path.abspath(FRONTEND_FOLDER)

app = Flask(__name__, static_folder=FRONTEND_FOLDER, static_url_path="")
CORS(app)


@app.route("/")
def index():
    return send_from_directory(FRONTEND_FOLDER, "index.html")

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB

# Initialize AI components once at startup (Models load lazily on first request)
print("[INFO] Initializing AI/NLP component wrappers...")
nlp_processor = NLPProcessor()
ats_scorer = ATSScorer(nlp_processor)
feedback_generator = FeedbackGenerator(nlp_processor)
resume_parser = ResumeParser()
bullet_improver = BulletImprover(nlp_processor)
ats_simulator = ATSSimulator(nlp_processor)
skill_gap_analyzer = SkillGapAnalyzer(nlp_processor)
github_analyzer = GitHubAnalyzer()
print("[INFO] AI component wrappers initialized successfully.")

# In-memory resume version store (keyed by session id)
version_store = {}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "AI Resume Analyzer API is running"})


@app.route("/api/analyze", methods=["POST"])
def analyze_resume():
    """
    Main endpoint: accepts resume file + job description text,
    returns full AI analysis.
    """
    if "resume" not in request.files:
        return jsonify({"error": "No resume file provided"}), 400

    file = request.files["resume"]
    job_description = request.form.get("job_description", "").strip()

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type. Use PDF, DOCX, or TXT"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    try:
        # Step 1: Parse resume text
        resume_text = resume_parser.parse(filepath)
        if not resume_text or len(resume_text.strip()) < 50:
            return jsonify({"error": "Could not extract meaningful text from resume"}), 400

        # Step 2: NLP Processing
        nlp_data = nlp_processor.process(resume_text)

        # Step 3: ATS Scoring
        score_data = ats_scorer.score(resume_text, nlp_data, job_description)

        # Step 4: Bullet Point Analysis (compute before feedback so feedback can use it)
        bullet_analysis = []
        for bullet in nlp_data.get("bullets", [])[:10]: # Limit to 10 for performance
            bullet_analysis.append(bullet_improver.improve(bullet))
        nlp_data["bullet_analysis"] = bullet_analysis

        # Step 5: Feedback Generation
        feedback_data = feedback_generator.generate(resume_text, nlp_data, score_data, job_description)

        # Compose final response
        response = {
            "success": True,
            "resume_text_preview": resume_text[:500] + "..." if len(resume_text) > 500 else resume_text,
            "nlp_analysis": nlp_data,
            "ats_score": score_data,
            "feedback": feedback_data,
            "bullet_analysis": bullet_analysis,
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


@app.route("/api/analyze-text", methods=["POST"])
def analyze_text():
    """
    Analyze raw resume text (no file upload needed).
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    resume_text = data.get("resume_text", "").strip()
    job_description = data.get("job_description", "").strip()

    if not resume_text or len(resume_text) < 50:
        return jsonify({"error": "Resume text too short or empty"}), 400

    try:
        nlp_data = nlp_processor.process(resume_text)
        score_data = ats_scorer.score(resume_text, nlp_data, job_description)
        
        bullet_analysis = []
        for bullet in nlp_data.get("bullets", [])[:10]:
            bullet_analysis.append(bullet_improver.improve(bullet))
        nlp_data["bullet_analysis"] = bullet_analysis
            
        feedback_data = feedback_generator.generate(resume_text, nlp_data, score_data, job_description)

        return jsonify({
            "success": True,
            "resume_text_preview": resume_text[:500] + "..." if len(resume_text) > 500 else resume_text,
            "nlp_analysis": nlp_data,
            "ats_score": score_data,
            "feedback": feedback_data,
            "bullet_analysis": bullet_analysis,
        })
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500



# ------------------------------------------------------------------ #
#  Feature 2: Bullet Improver                                         #
# ------------------------------------------------------------------ #

@app.route("/api/improve-bullet", methods=["POST"])
def improve_bullet():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400
    bullet = data.get("bullet", "").strip()
    if not bullet:
        return jsonify({"error": "No bullet text provided"}), 400
    try:
        result = bullet_improver.improve(bullet)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Improvement failed: {str(e)}"}), 500


# ------------------------------------------------------------------ #
#  Feature 3: ATS Simulation                                          #
# ------------------------------------------------------------------ #

@app.route("/api/ats-simulate", methods=["POST"])
def ats_simulate():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400
    resume_text = data.get("resume_text", "").strip()
    job_description = data.get("job_description", "").strip()
    if not resume_text or len(resume_text) < 50:
        return jsonify({"error": "Resume text too short or empty"}), 400
    try:
        result = ats_simulator.simulate(resume_text, job_description)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Simulation failed: {str(e)}"}), 500


# ------------------------------------------------------------------ #
#  Feature 4: Skill Gap Analyzer                                      #
# ------------------------------------------------------------------ #

@app.route("/api/skill-gap", methods=["POST"])
def skill_gap():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400
    resume_text = data.get("resume_text", "").strip()
    job_description = data.get("job_description", "").strip()
    if not resume_text or not job_description:
        return jsonify({"error": "Both resume text and job description are required"}), 400
    try:
        result = skill_gap_analyzer.analyze(resume_text, job_description)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Skill gap analysis failed: {str(e)}"}), 500


# ------------------------------------------------------------------ #
#  Feature 5: Resume Versioning                                       #
# ------------------------------------------------------------------ #

@app.route("/api/versions/save", methods=["POST"])
def save_version():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400
    session_id = data.get("session_id", "default")
    label = data.get("label", "").strip()
    resume_text = data.get("resume_text", "").strip()
    score_data = data.get("score_data", {})
    if not resume_text or not label:
        return jsonify({"error": "label and resume_text are required"}), 400
    if session_id not in version_store:
        version_store[session_id] = []
    version_store[session_id].append({
        "id": len(version_store[session_id]) + 1,
        "label": label,
        "resume_text": resume_text,
        "score": score_data.get("final_score", 0),
        "grade": score_data.get("grade", "N/A"),
        "dimension_scores": score_data.get("dimension_scores", {}),
    })
    return jsonify({"success": True, "versions": version_store[session_id]})


@app.route("/api/versions/list", methods=["POST"])
def list_versions():
    data = request.get_json() or {}
    session_id = data.get("session_id", "default")
    return jsonify({"versions": version_store.get(session_id, [])})


@app.route("/api/versions/compare", methods=["POST"])
def compare_versions():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400
    session_id = data.get("session_id", "default")
    id_a = data.get("id_a")
    id_b = data.get("id_b")
    versions = version_store.get(session_id, [])
    va = next((v for v in versions if v["id"] == id_a), None)
    vb = next((v for v in versions if v["id"] == id_b), None)
    if not va or not vb:
        return jsonify({"error": "One or both versions not found"}), 404
    dims = list(set(list(va["dimension_scores"].keys()) + list(vb["dimension_scores"].keys())))
    comparison = []
    for dim in dims:
        a_val = va["dimension_scores"].get(dim, 0)
        b_val = vb["dimension_scores"].get(dim, 0)
        comparison.append({
            "dimension": dim,
            "version_a": a_val,
            "version_b": b_val,
            "delta": round(b_val - a_val, 1),
        })
    return jsonify({
        "version_a": {"label": va["label"], "score": va["score"], "grade": va["grade"]},
        "version_b": {"label": vb["label"], "score": vb["score"], "grade": vb["grade"]},
        "score_delta": round(vb["score"] - va["score"], 1),
        "dimension_comparison": comparison,
    })


# ------------------------------------------------------------------ #
#  Feature 6: GitHub Analyzer                                         #
# ------------------------------------------------------------------ #

@app.route("/api/github-analyze", methods=["POST"])
def github_analyze():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400
    github_url = data.get("github_url", "").strip()
    if not github_url:
        return jsonify({"error": "GitHub URL is required"}), 400
    try:
        result = github_analyzer.analyze(github_url)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"GitHub analysis failed: {str(e)}"}), 500


# ------------------------------------------------------------------ #
#  Feature 7: Generate Summary                                        #
# ------------------------------------------------------------------ #

@app.route("/api/generate-summary", methods=["POST"])
def generate_summary():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400
    
    resume_text = data.get("resume_text", "").strip()
    if not resume_text:
        return jsonify({"error": "Resume text is required"}), 400
        
    try:
        # Extract skills and domain
        nlp_data = nlp_processor.process(resume_text)
        domain = nlp_data.get("domain", "General Professional")
        skills_dict = nlp_data.get("skills", {})
        strong_skills = skills_dict.get("strong", [])
        
        # Get top 3 skills
        top_skills = strong_skills[:3] if strong_skills else ["relevant technologies", "industry best practices", "problem solving"]
        skills_str = ", ".join(top_skills[:-1]) + f" and {top_skills[-1]}" if len(top_skills) > 1 else top_skills[0]
        
        # Create templates based on domain
        templates = [
            f"Results-driven {domain} professional with expertise in {skills_str}. Proven track record of delivering high-quality solutions and driving project success. Adept at collaborating with cross-functional teams to achieve strategic objectives.",
            f"Innovative {domain} specialist skilled in {skills_str}. Passionate about leveraging technology to solve complex problems and optimize workflows. Committed to continuous learning and implementing scalable methodologies.",
            f"Dedicated {domain} expert with a strong foundation in {skills_str}. Experienced in managing full-cycle projects and ensuring exceptional delivery. Focused on building robust applications that enhance user experience and operational efficiency."
        ]
        
        return jsonify({"success": True, "summaries": templates})
    except Exception as e:
        return jsonify({"error": f"Summary generation failed: {str(e)}"}), 500


# ------------------------------------------------------------------ #
#  Feature 8: Download Improved Resume (HTML)                         #
# ------------------------------------------------------------------ #

@app.route("/api/download-resume", methods=["POST"])
def download_resume():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400
        
    resume_text = data.get("resume_text", "").strip()
    bullet_analysis = data.get("bullet_analysis", [])
    
    if not resume_text:
        return jsonify({"error": "Resume text is required"}), 400
        
    try:
        # Replace original bullets with improved bullets where applicable
        improved_text = resume_text
        for item in bullet_analysis:
            orig = item.get("original")
            imp = item.get("improved")
            if orig and imp and orig in improved_text:
                improved_text = improved_text.replace(orig, imp)
                
        # Split into paragraphs for basic HTML structuring
        paragraphs = improved_text.split("\n\n")
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Improved Resume</title>
            <style>
                body {{ font-family: 'Arial', sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 40px; color: #333; }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                p {{ margin-bottom: 15px; }}
                .watermark {{ margin-top: 50px; font-size: 0.8em; color: #7f8c8d; text-align: center; border-top: 1px solid #eee; padding-top: 20px; }}
            </style>
        </head>
        <body>
            <h1>Optimized Resume</h1>
        """
        
        for p in paragraphs:
            if p.strip():
                # Convert list items to HTML lists roughly
                lines = p.split("\n")
                in_list = False
                for line in lines:
                    line = line.strip()
                    if not line: continue
                    if re.match(r'^[\-\*\•\u2022\u2023\u25E6]', line):
                        if not in_list:
                            html_content += "<ul>\n"
                            in_list = True
                        clean_line = re.sub(r'^[\-\*\•\u2022\u2023\u25E6]\s*', '', line)
                        html_content += f"<li>{clean_line}</li>\n"
                    else:
                        if in_list:
                            html_content += "</ul>\n"
                            in_list = False
                        html_content += f"<p>{line}</p>\n"
                if in_list:
                    html_content += "</ul>\n"
                    
        html_content += f"""
            <div class="watermark">Optimized with AI Resume Analyzer on {datetime.datetime.now().strftime('%Y-%m-%d')}</div>
        </body>
        </html>
        """
        
        return jsonify({"success": True, "html": html_content})
    except Exception as e:
        return jsonify({"error": f"Resume export failed: {str(e)}"}), 500


# ------------------------------------------------------------------ #
#  Feature 9: Full Resume AI Rewriter                                #
# ------------------------------------------------------------------ #

@app.route("/api/improve-resume", methods=["POST"])
def improve_resume():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400
    
    resume_text = data.get("resume_text", "").strip()
    if not resume_text:
        return jsonify({"error": "Resume text is required"}), 400
        
    try:
        # Since we do not have a full LLM, we will use the existing BulletImprover 
        # to find and improve bullet-like structures across the resume.
        lines = resume_text.split('\n')
        improved_lines = []
        for line in lines:
            # Simple heuristic for bullets
            if len(line.split()) > 3 and re.match(r'^[\-\*\•\u2022\u2023\u25E6]', line.strip()):
                res = bullet_improver.improve(line.strip())
                if res and res.get('improved'):
                    improved_lines.append(res.get('improved'))
                else:
                    improved_lines.append(line)
            else:
                improved_lines.append(line)
                
        improved_resume = '\n'.join(improved_lines)
        return jsonify({"success": True, "improved_resume": improved_resume})
    except Exception as e:
        return jsonify({"error": f"Improvement failed: {str(e)}"}), 500


# ------------------------------------------------------------------ #
#  Feature 10: Email Report System                                    #
# ------------------------------------------------------------------ #

@app.route("/api/send-email", methods=["POST"])
def send_email():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400
        
    email_address = data.get("email", "").strip()
    report_html = data.get("report_html", "")
    
    if not email_address:
        return jsonify({"error": "Email address is required"}), 400
        
    try:
        # Mock Email Sending
        print(f"[MOCK EMAIL] Sending report to {email_address}...")
        
        # Real implementation would be:
        # msg = MIMEMultipart()
        # msg['Subject'] = 'Your AI Resume Analysis Report'
        # msg['From'] = os.environ.get('SMTP_EMAIL')
        # msg['To'] = email_address
        # msg.attach(MIMEText(report_html, 'html'))
        # 
        # with smtplib.SMTP(os.environ.get('SMTP_SERVER', 'smtp.gmail.com'), 587) as server:
        #     server.starttls()
        #     server.login(os.environ.get('SMTP_EMAIL'), os.environ.get('SMTP_PASSWORD'))
        #     server.send_message(msg)
            
        return jsonify({"success": True, "message": "Email sent successfully (Mocked)"})
    except Exception as e:
        return jsonify({"error": f"Email failed: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
