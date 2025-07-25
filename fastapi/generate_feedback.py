from openai import OpenAI

client = OpenAI(api_key="ENTER YOUR API KEY HERE")

      
def generate_feedback(questions, answers):
    qna_pairs = "\n".join(
        [f"Q{i+1}: {q}\nA{i+1}: {a}" for i, (q, a) in enumerate(zip(questions, answers))]
    )
    prompt = f"""
    You are a professional interviewer. Here is a mock interview transcript:

    {qna_pairs}

    Please analyze the candidate's responses and provide feedback in the following clear sections using **bold** labels:

    **Strengths**:
    - List the positive points

    **Weaknesses**:
    - List the negative points

    **Constructive Criticism**:
    - Suggest improvements

    Format each section clearly and consistently.
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()