# question_generator.py
from openai import OpenAI

client = OpenAI(api_key="ENTER YOUR API KEY HERE")

def generate_questions(resume_context, difficulty):
    prompt = f"""
You are an AI interviewer. Based on the candidate's resume context below, generate 6 {difficulty} interview questions. 
- If difficulty is easy: ask general and introductory questions.
- If medium: ask about technical skills and past experience with some depth.
- If hard: ask in-depth technical questions, theoretical concepts, problem-solving, or design challenges.
Ensure the questions are relevant to the field or projects mentioned. Make it little interactive and engaging.Fix the first question to be a warm-up question. Like tell me about yourself.
Make sure to ask about the candidate's experience, skills, and projects. And at last ask about their future goals and aspirations. or Why should we hire you?

Resume context:
\"\"\"
{resume_context}
\"\"\"

Questions:
1.
2.
3.
4.
5.
6.
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()
