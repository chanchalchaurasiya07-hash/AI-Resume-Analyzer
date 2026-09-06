from flask import Flask, render_template, request
from pypdf import PdfReader

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    file = request.files.get("resume")

    if not file or file.filename == "":
        return "Please upload a resume PDF."

    if not file.filename.lower().endswith(".pdf"):
        return "Please upload a PDF file only."

    try:

        # -----------------------------
        # PDF TEXT EXTRACTION
        # -----------------------------

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


        # -----------------------------
        # SKILLS DETECTION
        # -----------------------------

        skills_list = [
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

        for skill in skills_list:

            if skill.lower() in resume_lower:
                skills.append(skill)


        # -----------------------------
        # EDUCATION DETECTION
        # -----------------------------

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


        # -----------------------------
        # EXPERIENCE DETECTION
        # -----------------------------

        experience_keywords = [
    "Internship",
    "Intern",
    "Developer",
    "Engineer"
]

        experience = []

        for keyword in experience_keywords:

            if keyword.lower() in resume_lower:
                experience.append(keyword)


        # -----------------------------
        # MISSING SKILLS
        # -----------------------------

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


        # -----------------------------
        # RESUME SCORE
        # -----------------------------

        # Technical Skills - 25 marks

        technical_score = 0

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


        # Education - 15 marks

        education_score = 0

        if len(education) >= 3:
            education_score = 15

        elif len(education) >= 2:
            education_score = 12

        elif len(education) >= 1:
            education_score = 8
            # Projects and Experience - 25 marks

        has_project = (
    "projects" in resume_lower
    and "student project" in resume_lower
)

        has_real_experience = (
    "internship" in resume_lower
    or "intern" in resume_lower
    or "work experience" in resume_lower
)

        project_experience_score = 0

        if has_project and has_real_experience:
           project_experience_score = 25

        elif has_project:
           project_experience_score = 15

        elif has_real_experience:
           project_experience_score = 12


       
        # Resume Sections - 20 marks

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

        sections_found = 0

        for section in important_sections:

            if section in resume_lower:
                sections_found += 1


        if sections_found >= 8:
            section_score = 20

        elif sections_found >= 6:
            section_score = 16

        elif sections_found >= 4:
            section_score = 12

        elif sections_found >= 2:
            section_score = 8

        else:
            section_score = 4


        # Resume Quality - 15 marks

        quality_score = 0

        if "email" in resume_lower:
            quality_score += 2

        if "phone" in resume_lower:
            quality_score += 2

        if (
            "certification" in resume_lower
            or "certificate" in resume_lower
        ):
            quality_score += 2

        if "achievement" in resume_lower:
            quality_score += 2

        if (
            "communication" in resume_lower
            or "teamwork" in resume_lower
        ):
            quality_score += 2

        if len(resume_text) >= 1000:
            quality_score += 3

        elif len(resume_text) >= 600:
            quality_score += 2

        elif len(resume_text) >= 300:
            quality_score += 1


        if "measurable" not in resume_lower:
            quality_score -= 1

        if "%" not in resume_text and "increase" not in resume_lower:
            quality_score -= 1


        quality_score = max(0, min(15, quality_score))


        # Final Score

        score = (
            technical_score
            + education_score
            + project_experience_score
            + section_score
            + quality_score
        )

        score = min(score, 100)
        # -----------------------------
# SCORE RATING
# -----------------------------

        if score >= 80:
           score_rating = "Excellent Resume"
        elif score >= 60:
           score_rating = "Good Resume - Some Improvements Needed"
        elif score >= 40:
          score_rating = "Average Resume - Needs Improvement"
        else:
          score_rating = "Needs Significant Improvement"




        # -----------------------------
        # STRENGTHS AND SUGGESTIONS
        # -----------------------------

        strengths = []
        suggestions = []


        if len(skills) >= 3:

            strengths.append(
                "Good range of technical skills identified."
            )

        else:

            suggestions.append(
                "Add more relevant technical skills."
            )


        if len(education) > 0:

            strengths.append(
                "Education information is clearly mentioned."
            )

        else:

            suggestions.append(
                "Add your education details."
            )


        if len(experience) > 0:

            strengths.append(
                "Experience or internship information is present."
            )

        else:

            suggestions.append(
                "Add internship or experience details."
            )


        if len(resume_text) > 300:

            strengths.append(
                "Resume contains sufficient information."
            )

        else:

            suggestions.append(
                "Add more relevant details to your resume."
            )


        # -----------------------------
        # SMART RESUME SUGGESTIONS
        # -----------------------------

        if "email" not in resume_lower:

            suggestions.append(
                "Add a professional email address."
            )


        if "phone" not in resume_lower:

            suggestions.append(
                "Add your contact number."
            )


        if "project" not in resume_lower:

            suggestions.append(
                "Add relevant projects to showcase your practical skills."
            )


        if (
            "certification" not in resume_lower
            and "certificate" not in resume_lower
        ):

            suggestions.append(
                "Add relevant certifications to strengthen your profile."
            )


        if "achievement" not in resume_lower:

            suggestions.append(
                "Add your academic or professional achievements."
            )


        if (
            "communication" not in resume_lower
            and "teamwork" not in resume_lower
        ):

            suggestions.append(
                "Mention soft skills such as communication and teamwork."
            )


        if (
            "%" not in resume_text
            and "increase" not in resume_lower
        ):

            suggestions.append(
                "Add measurable results or achievements wherever possible."
            )


        suggestions.append(
            "Use clear headings and consistent formatting."
        )

        suggestions.append(
            "Mention relevant tools and technologies used in your projects."
        )


        # -----------------------------
        # DISPLAY RESULT
        # -----------------------------

        return render_template(
            "result.html",

            skills=skills,

            education=education,

            experience=experience,

            resume_text=resume_text,

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

        return f"Error while reading PDF: {e}"


if __name__ == "__main__":

    app.run(debug=True)