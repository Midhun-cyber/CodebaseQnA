import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def ask_llm(question, context):
    prompt = f"""
    You are an expert software engineer.

    Answer ONLY using the repository context.

    Rules:
    - Write a clear answer in about 120–180 words.
    - Mention the file name(s) where the implementation exists.
    - Explain both what the code does and how it works.
    - Use short paragraphs or 3–5 bullet points if helpful.
    - Do not use headings like Summary, Functionality, etc.
    - Do not repeat information.
    - If the answer is not found, reply exactly:
    "I couldn't find relevant information in this repository."

    Repository Context:
    {context}

    Question:
    {question}
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You answer only from the repository context."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content

def generate_readme(context):
    prompt = f"""
    You are an expert software engineer.

    Generate a professional README.md.

    Use ONLY the repository information below.

    Repository:

    {context}

    Use ### for the project title and #### for all section headings.
    Do not use # or ## headings.

    Include:

    ### Project Title

    #### Overview

    #### Features

    #### Technologies Used

    #### Project Structure

    #### How It Works

    #### Future Improvements

    Return Markdown only.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are an expert technical writer who generates README files using only the provided repository context."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content