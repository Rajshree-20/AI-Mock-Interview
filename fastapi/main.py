import re
from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List

from resume_parser import extract_text_from_pdf, parse_resume_sections
from question_generator import generate_questions
from generate_feedback import generate_feedback

app = FastAPI()

# (Optional) CORS if your frontend runs separately
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload-resume/")
async def upload_resume(file: UploadFile, difficulty: str = Form("medium")):
    content = await file.read()

    # Extract raw text
    raw_text = extract_text_from_pdf(content)

    # Parse resume sections to build context
    sections = parse_resume_sections(raw_text)

    # Build context
    context = " ".join([ 
        sections.get("projects", ""), 
        sections.get("experience", ""), 
        sections.get("internships", ""), 
        sections.get("skills", "") 
    ])

    if not context.strip():
        return {"message": "Could not find relevant resume content."}

    # Generate questions (returns a string)
    raw_output = generate_questions(context, difficulty)

    # Parse questions using regex
    questions = re.findall(r'\d+\.\s+(.*?)(?=\n\d+\.|\Z)', raw_output, re.DOTALL)

    if not questions:
        return {"message": "No questions generated."}

    return {"questions": questions}


# ✅ Updated: Accept JSON body using Pydantic model
class AnswerSubmission(BaseModel):
    questions: List[str]
    answers: List[str]

@app.post("/submit-answers/")
async def submit_answers(payload: AnswerSubmission):
    questions = payload.questions
    answers = payload.answers

    if len(answers) != len(questions):
        return JSONResponse(status_code=400, content={"message": "Number of answers does not match number of questions."})

    # Generate feedback using GPT or a custom model
    feedback = generate_feedback(questions, answers)

    return {"feedback": feedback}
    
