import fitz  # PyMuPDF
import re

def extract_text_from_pdf(file_bytes):
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text


def parse_resume_sections(text):
    # Lowercased for case-insensitive matching
    text = text.lower()
    
    # Use regex or simple rules to split based on headers
    sections = {
        "projects": "",
        "experience": "",
        "internships": "",
        "skills": "",
    }

    # Extract projects
    project_match = re.search(r"(projects|academic projects|technical projects)[\s\S]+?(?=\n[a-z])", text)
    if project_match:
        sections["projects"] = project_match.group().strip()

    # Extract experience
    exp_match = re.search(r"(work experience|professional experience)[\s\S]+?(?=\n[a-z])", text)
    if exp_match:
        sections["experience"] = exp_match.group().strip()

    # Extract internships
    intern_match = re.search(r"(internship|internships)[\s\S]+?(?=\n[a-z])", text)
    if intern_match:
        sections["internships"] = intern_match.group().strip()
    
    # Extract skills
    skills_match = re.search(r"(skills|technical skills)[\s\S]+?(?=\n[a-z])", text)
    if skills_match:
        sections["skills"] = skills_match.group().strip()

    return sections
