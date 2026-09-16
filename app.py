from flask import Flask, render_template, request
from pypdf import PdfReader
from markupsafe import Markup, escape
import re
import io

app = Flask(__name__)

# Maximum upload size: 10 MB
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


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


def format_resume_text(text):
    lines = text.splitlines()
    output = []

    for line in lines:
        line = line.strip()

        if not line:
            output.append('<div class="resume-space"></div>')
            continue

        normalized = re.sub(r"[^a-zA-Z ]", "", line.lower()).strip()

        if normalized in SECTION_HEADINGS:
            output.append(
                f'<div class="resume-heading">{escape(line)}</div>'
            )

        elif line.isupper() and len(line) <= 60:
            output.append(
                f'<div class="resume-title">{escape(line)}</div>'
            )

        else:
            output.append(
                f'<div class="resume-line">{escape(line)}</div>'
            )

    return Markup("".join(output))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    try:
        file = request.files.get("resume")

        if not file or file.filename == "":
            return "Please upload a resume PDF."

        if not file.filename.lower().endswith(".pdf"):
            return "Please upload a PDF file only."

        # Read uploaded file safely
        file_bytes = file.read()

        if not file_bytes:
            return "The uploaded file is empty. Please select the PDF again."

        # Read PDF from memory
        reader = PdfReader(io.BytesIO(file_bytes))

        resume_text = ""

        for page in reader.pages:
            text = page.extract_text()

            if text:
                resume_text += text + "\n"

        resume_text = resume_text.strip()

        if not resume_text:
            return (
                "Could not extract text from this PDF. "
                "Please upload a text-based PDF."
            )

        resume_lower = resume_text.lower()
        lines = [line.strip() for line in resume_text.splitlines() if line.strip()]

        # --------------------------------
        # SKILLS
        # --------------------------------

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

        # --------------------------------
        # EDUCATION
        # --------------------------------

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

        for item in education_keywords:
            if item.lower() in resume_lower:
                education.append(item)

        # --------------------------------
        # EXPERIENCE
        # --------------------------------

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

        experience_headings = {
            "experience",
            "work experience",
            "professional experience",
            "employment"
        }

        experience_section_found = False
        experience_content_found = False

        for i, line in enumerate(lines):

            normalized = re.sub(
                r"[^a-zA-Z ]",
                "",
                line.lower()
            ).strip()

            if normalized in experience_headings:
                experience_section_found = True

                # Check next few lines for actual experience
                for next_line in lines[i + 1:i + 8]:

                    next_lower = next_line.lower()

                    if any(word in next_lower for word in [
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
                    ]):
                        experience_content_found = True
                        break

        # Add detected experience keywords
        if experience_section_found and experience_content_found:

            for keyword in experience_keywords:
                if keyword.lower() in resume_lower:
                    experience.append(keyword)

        # --------------------------------
        # MISSING SKILLS
        # --------------------------------

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

        # --------------------------------
        # TECHNICAL SKILLS SCORE - 25
        # --------------------------------

        skill_count = len(skills)

        if skill_count >= 8:
            technical_score = 25
        elif skill_count >= 6:
            technical_score = 22
        elif skill_count >= 4:
            technical_score = 18
        elif skill_count >= 2:
            technical_score = 12
        elif skill_count >= 1:
            technical_score = 6
        else:
            technical_score = 0

        # --------------------------------
        # EDUCATION SCORE - 15
        # --------------------------------

        education_count = len(education)

        if education_count >= 3:
            education_score = 15
        elif education_count >= 2:
            education_score = 12
        elif education_count >= 1:
            education_score = 8
        else:
            education_score = 0

        # --------------------------------
        # PROJECT + EXPERIENCE SCORE - 25
        # --------------------------------

        project_headings = {
            "projects",
            "project",
            "academic projects",
            "personal projects"
        }

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

        has_project = False

        for i, line in enumerate(lines):

            normalized = re.sub(
                r"[^a-zA-Z ]",
                "",
                line.lower()
            ).strip()

            if normalized in project_headings:

                # Look at next lines
                for next_line in lines[i + 1:i + 6]:

                    next_normalized = re.sub(
                        r"[^a-zA-Z ]",
                        "",
                        next_line.lower()
                    ).strip()

                    if next_normalized in SECTION_HEADINGS:
                        break

                    if (
                        "project" in next_line.lower()
                        or any(
                            word in next_line.lower()
                            for word in project_words
                        )
                    ):
                        has_project = True
                        break

            if has_project:
                break

        has_real_experience = (
            experience_section_found
            and experience_content_found
        )

        if has_project and has_real_experience:
            project_experience_score = 25

        elif has_project:
            project_experience_score = 15

        elif has_real_experience:
            project_experience_score = 12

        else:
            project_experience_score = 0

        # --------------------------------
        # RESUME SECTIONS SCORE - 20
        # --------------------------------

        important_sections = [
            "career objective",
            "education",
            "technical skills",
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

        # --------------------------------
        # RESUME QUALITY SCORE - 15
        # --------------------------------

        quality_score = 0

        if re.search(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            resume_text
        ):
            quality_score += 2

        if re.search(r"\b\d{10}\b", resume_text):
            quality_score += 2

        if (
            "certification" in resume_lower
            or "certificate" in resume_lower
        ):
            quality_score += 2

        if (
            "achievement" in resume_lower
            or "achievements" in resume_lower
        ):
            quality_score += 2

        if (
            "communication" in resume_lower
            or "teamwork" in resume_lower
        ):
            quality_score += 2

        text_length = len(resume_text)

        if text_length >= 1000:
            quality_score += 3
        elif text_length >= 600:
            quality_score += 2
        elif text_length >= 300:
            quality_score += 1

        if "measurable" not in resume_lower:
            quality_score -= 1

        if "%" not in resume_text and "increase" not in resume_lower:
            quality_score -= 1

        quality_score = max(0, min(15, quality_score))

        # --------------------------------
        # FINAL SCORE
        # --------------------------------

        score = (
            technical_score
            + education_score
            + project_experience_score
            + section_score
            + quality_score
        )

        score = min(score, 100)

        # --------------------------------
        # SCORE RATING
        # --------------------------------

        if score >= 80:
            score_rating = "Excellent Resume"

        elif score >= 60:
            score_rating = "Good Resume - Some Improvements Needed"

        elif score >= 40:
            score_rating = "Average Resume - Needs Improvement"

        else:
            score_rating = "Needs Significant Improvement"

        # --------------------------------
        # STRENGTHS
        # --------------------------------

        strengths = []

        if len(skills) >= 3:
            strengths.append(
                "The resume contains multiple technical skills."
            )

        if education:
            strengths.append(
                "Education details are present."
            )

        if has_real_experience:
            strengths.append(
                "Relevant experience details are present."
            )

        if has_project:
            strengths.append(
                "Project information is included."
            )

        if len(resume_text) > 300:
            strengths.append(
                "The resume contains sufficient information for analysis."
            )

        # --------------------------------
        # SUGGESTIONS
        # --------------------------------

        suggestions = []

        if not re.search(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            resume_text
        ):
            suggestions.append(
                "Add a professional email address."
            )

        if not re.search(r"\b\d{10}\b", resume_text):
            suggestions.append(
                "Add a valid phone number."
            )

        if not has_project:
            suggestions.append(
                "Add academic or personal projects with proper descriptions."
            )

        if (
            "certification" not in resume_lower
            and "certificate" not in resume_lower
        ):
            suggestions.append(
                "Add relevant certifications if available."
            )

        if (
            "achievement" not in resume_lower
            and "achievements" not in resume_lower
        ):
            suggestions.append(
                "Add achievements or academic accomplishments."
            )

        if (
            "communication" not in resume_lower
            and "teamwork" not in resume_lower
        ):
            suggestions.append(
                "Add important soft skills such as communication and teamwork."
            )

        if (
            "measurable" not in resume_lower
            and "%" not in resume_text
            and "increase" not in resume_lower
        ):
            suggestions.append(
                "Use measurable results in project or experience descriptions."
            )

        if section_count < 6:
            suggestions.append(
                "Use clear and relevant resume section headings."
            )

        # --------------------------------
        # FORMATTED RESUME TEXT
        # --------------------------------

        formatted_resume = format_resume_text(resume_text)

        # --------------------------------
        # RESULT PAGE
        # --------------------------------

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


if __name__ == "__main__":
    app.run(debug=True)
