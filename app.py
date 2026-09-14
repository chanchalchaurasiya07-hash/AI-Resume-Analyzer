from flask import Flask, render_template, request
from pypdf import PdfReader
from markupsafe import Markup, escape
import re

app = Flask(__name__)


# =========================================================
# RESUME SECTION HEADINGS
# =========================================================

SECTION_HEADINGS = {
    "career objective",
    "objective",
    "profile",
    "summary",

    "education",
    "academic qualification",
    "qualifications",

    "skills",
    "technical skills",

    "experience",
    "work experience",
    "professional experience",
    "employment",

    "projects",
    "project",
    "academic projects",
    "personal projects",

    "certifications",
    "certification",
    "certificates",

    "achievements",
    "achievement",

    "languages",
    "hobbies",
    "declaration"
}


# =========================================================
# FORMAT EXTRACTED RESUME TEXT
# =========================================================

def format_resume_text(text):

    html = []

    for line in text.splitlines():

        line = line.strip()

        # Empty line
        if not line:
            html.append('<div class="resume-space"></div>')
            continue

        normalized = re.sub(r'[:\-]+$', '', line.lower()).strip()

        # Section heading
        if normalized in SECTION_HEADINGS:

            html.append(
                f'<div class="resume-heading">{escape(line)}</div>'
            )

        # Other uppercase title/name
        elif line.isupper() and len(line) <= 60:

            html.append(
                f'<div class="resume-title">{escape(line)}</div>'
            )

        # Normal text
        else:

            html.append(
                f'<div class="resume-line">{escape(line)}</div>'
            )

    return Markup("".join(html))


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================================
# ANALYZE RESUME
# =========================================================

@app.route("/analyze", methods=["POST"])
def analyze():

    try:

        # -------------------------------------------------
        # GET FILE
        # -------------------------------------------------

        file = request.files.get("resume")

        if not file or file.filename == "":
            return "Please upload a resume PDF."

        if not file.filename.lower().endswith(".pdf"):
            return "Please upload a PDF file only."


        # -------------------------------------------------
        # EXTRACT PDF TEXT
        # -------------------------------------------------

        reader = PdfReader(file)

        resume_text = ""

        for page in reader.pages:

            text = page.extract_text()

            if text:
                resume_text += text + "\n"

        resume_text = resume_text.strip()

        if not resume_text:
            return "Could not extract text from this PDF. Please upload a text-based PDF."

        resume_lower = resume_text.lower()


        # =================================================
        # SKILLS DETECTION
        # =================================================

        skill_keywords = [

            "Python",
            "C++",
            "Java",
            "JavaScript",
            "HTML",
            "CSS",
            "SQL",
            "Machine Learning",
            "Artificial Intelligence",
            "Flask",
            "Django",
            "React",
            "Git",
            "Communication"

        ]

        skills = []

        for skill in skill_keywords:

            if skill.lower() in resume_lower:

                skills.append(skill)


        # =================================================
        # EDUCATION DETECTION
        # =================================================

        education_keywords = [

            "B.Tech",
            "B.E.",
            "Bachelor",
            "Master",
            "M.Tech",
            "MCA",
            "BCA",
            "Degree",
            "Education"

        ]

        education = []

        for keyword in education_keywords:

            if keyword.lower() in resume_lower:

                education.append(keyword)


        # =================================================
        # EXPERIENCE DETECTION
        # =================================================

        experience_keywords = [

            "Internship",
            "Intern",
            "Developer",
            "Engineer",
            "Software",
            "Analyst",
            "Manager"

        ]

        experience = []

        for keyword in experience_keywords:

            if keyword.lower() in resume_lower:

                experience.append(keyword)


        # =================================================
        # MISSING SKILLS
        # =================================================

        recommended_skills = [

            "Python",
            "SQL",
            "Git",
            "Machine Learning",
            "Communication"

        ]

        missing_skills = []

        for skill in recommended_skills:

            if skill.lower() not in resume_lower:

                missing_skills.append(skill)


        # =================================================
        # SCORE - TECHNICAL SKILLS
        # 25 MARKS
        # =================================================

        if len(skills) >= 8:

            technical_score = 25

        elif len(skills) >= 6:

            technical_score = 22

        elif len(skills) >= 4:

            technical_score = 18

        elif len(skills) >= 2:

            technical_score = 12

        elif len(skills) >= 1:

            technical_score = 6

        else:

            technical_score = 0


        # =================================================
        # SCORE - EDUCATION
        # 15 MARKS
        # =================================================

        if len(education) >= 3:

            education_score = 15

        elif len(education) >= 2:

            education_score = 12

        elif len(education) >= 1:

            education_score = 8

        else:

            education_score = 0


        # =================================================
        # PROJECT + EXPERIENCE DETECTION
        # 25 MARKS
        # =================================================

        lines = [
            line.strip()
            for line in resume_text.splitlines()
            if line.strip()
        ]


        # -----------------------------------------------
        # PROJECT DETECTION
        # -----------------------------------------------

        project_section_found = False
        project_content_found = False

        project_headings = [

            "projects",
            "project",
            "academic projects",
            "personal projects"

        ]

        for i, line in enumerate(lines):

            normalized_line = line.lower().strip()
            normalized_line = re.sub(
                r'[:\-]+$',
                '',
                normalized_line
            ).strip()

            if normalized_line in project_headings:

                project_section_found = True

                # Check content after project heading
                if i + 1 < len(lines):

                    next_line = lines[i + 1].lower()

                    if next_line not in project_headings:

                        if next_line not in [
                            "experience",
                            "work experience",
                            "education",
                            "skills",
                            "technical skills",
                            "certifications",
                            "achievements",
                            "languages"
                        ]:

                            project_content_found = True

                break


        # Also detect common project wording
        project_words = [

            "student project",
            "academic project",
            "personal project",
            "developed",
            "designed",
            "built",
            "implemented",
            "created"

        ]

        if any(word in resume_lower for word in project_words):

            if "project" in resume_lower:

                project_content_found = True


        has_project = (
            project_section_found and project_content_found
        )


        # -----------------------------------------------
        # EXPERIENCE DETECTION
        # -----------------------------------------------

        experience_section_found = False
        experience_content_found = False

        experience_headings = [

            "experience",
            "work experience",
            "professional experience",
            "employment"

        ]

        real_experience_words = [

            "developer",
            "engineer",
            "software developer",
            "software engineer",
            "intern",
            "internship",
            "analyst",
            "manager",
            "employee",
            "worked",
            "working",
            "company"

        ]

        for i, line in enumerate(lines):

            normalized_line = line.lower().strip()
            normalized_line = re.sub(
                r'[:\-]+$',
                '',
                normalized_line
            ).strip()

            if normalized_line in experience_headings:

                experience_section_found = True

                # Check lines after experience heading
                remaining_text = " ".join(
                    lines[i + 1:i + 8]
                ).lower()

                if any(
                    word in remaining_text
                    for word in real_experience_words
                ):

                    experience_content_found = True

                break


        # Developer / Engineer anywhere in resume
        # can also indicate real experience

        if any(
            word in resume_lower
            for word in [
                "software developer",
                "software engineer",
                "developer",
                "engineer",
                "internship",
                "intern"
            ]
        ):

            if "experience" in resume_lower:

                experience_content_found = True


        has_real_experience = (
            experience_section_found
            and experience_content_found
        )


        # -----------------------------------------------
        # PROJECT + EXPERIENCE SCORE
        # -----------------------------------------------

        if has_project and has_real_experience:

            project_experience_score = 25

        elif has_project:

            project_experience_score = 15

        elif has_real_experience:

            project_experience_score = 12

        else:

            project_experience_score = 0


        # =================================================
        # RESUME SECTIONS
        # 20 MARKS
        # =================================================

        important_sections = [

            "career objective",
            "education",
            "technical skills",
            "skills",
            "projects",
            "experience",
            "certifications",
            "achievements",
            "soft skills",
            "languages"

        ]

        section_count = 0

        for section in important_sections:

            if section in resume_lower:

                section_count += 1


        if section_count >= 8:

            section_score = 20

        elif section_count >= 6:

            section_score = 16

        elif section_count >= 4:

            section_score = 12

        elif section_count >= 2:

            section_score = 8

        else:

            section_score = 4


        # =================================================
        # RESUME QUALITY
        # 15 MARKS
        # =================================================

        quality_score = 0


        # Email

        if "@" in resume_text:

            quality_score += 2


        # Phone

        phone_pattern = r'\b\d{10}\b'

        if re.search(phone_pattern, resume_text):

            quality_score += 2


        # Certification

        if (
            "certification" in resume_lower
            or "certificate" in resume_lower
        ):

            quality_score += 2


        # Achievement

        if "achievement" in resume_lower:

            quality_score += 2


        # Communication / teamwork

        if (
            "communication" in resume_lower
            or "teamwork" in resume_lower
        ):

            quality_score += 2


        # Resume length

        if len(resume_text) >= 1000:

            quality_score += 3

        elif len(resume_text) >= 600:

            quality_score += 2

        elif len(resume_text) >= 300:

            quality_score += 1


        # Measurable results

        if "measurable" not in resume_lower:

            quality_score -= 1


        # Percentage / increase

        if (
            "%" not in resume_text
            and "increase" not in resume_lower
        ):

            quality_score -= 1


        quality_score = max(
            0,
            min(15, quality_score)
        )


        # =================================================
        # FINAL SCORE
        # =================================================

        score = (

            technical_score
            + education_score
            + project_experience_score
            + section_score
            + quality_score

        )

        score = min(100, score)


        # =================================================
        # SCORE RATING
        # =================================================

        if score >= 80:

            score_rating = "Excellent Resume"

        elif score >= 60:

            score_rating = "Good Resume - Some Improvements Needed"

        elif score >= 40:

            score_rating = "Average Resume - Needs Improvement"

        else:

            score_rating = "Needs Significant Improvement"


        # =================================================
        # STRENGTHS
        # =================================================

        strengths = []


        if len(skills) >= 3:

            strengths.append(
                "Good technical skills are identified in the resume."
            )


        if education:

            strengths.append(
                "Educational qualification is clearly mentioned."
            )


        if experience:

            strengths.append(
                "Experience-related information is present."
            )


        if has_project:

            strengths.append(
                "Project experience is included in the resume."
            )


        if len(resume_text) > 300:

            strengths.append(
                "The resume contains sufficient information for analysis."
            )


        # =================================================
        # SUGGESTIONS
        # =================================================

        suggestions = []


        if len(skills) < 3:

            suggestions.append(
                "Add more relevant technical skills."
            )


        if not education:

            suggestions.append(
                "Clearly mention your educational qualifications."
            )


        if not has_real_experience:

            suggestions.append(
                "Add internship or relevant work experience if available."
            )


        if not has_project:

            suggestions.append(
                "Add at least one relevant academic or personal project."
            )


        if "@" not in resume_text:

            suggestions.append(
                "Add a professional email address."
            )


        if not re.search(phone_pattern, resume_text):

            suggestions.append(
                "Add a valid phone number."
            )


        if (
            "certification" not in resume_lower
            and "certificate" not in resume_lower
        ):

            suggestions.append(
                "Add relevant certifications or courses."
            )


        if "achievement" not in resume_lower:

            suggestions.append(
                "Add academic or professional achievements."
            )


        if (
            "communication" not in resume_lower
            and "teamwork" not in resume_lower
        ):

            suggestions.append(
                "Mention important soft skills such as communication and teamwork."
            )


        if (
            "measurable" not in resume_lower
            and "%" not in resume_text
        ):

            suggestions.append(
                "Add measurable results or percentages to describe your achievements."
            )


        # =================================================
        # FORMATTED RESUME
        # =================================================

        formatted_resume = format_resume_text(
            resume_text
        )


        # =================================================
        # RESULT PAGE
        # =================================================

        return render_template(

            "result.html",

            skills=skills,

            education=education,

            experience=experience,

            resume_text=resume_text,

            formatted_resume=formatted_resume,

            score=score,

            score_rating=score_rating,

            strengths=strengths,

            suggestions=suggestions,

            missing_skills=missing_skills,

            technical_score=technical_score,

            education_score=education_score,

            project_experience_score=project_experience_score,

            section_score=section_score,

            quality_score=quality_score

        )


    except Exception as e:

        return f"Error while analyzing resume: {str(e)}"


# =========================================================
# RUN APP
# =========================================================

if __name__ == "__main__":

    app.run(debug=True)
