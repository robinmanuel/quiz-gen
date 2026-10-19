import os
import json
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Quiz Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class QuizRequest(BaseModel):
    topic: str
    num_questions: int = Field(default=5, ge=1, le=20)


class Question(BaseModel):
    question: str
    options: List[str]
    correct_answer_index: int
    explanation: str


class QuizResponse(BaseModel):
    topic: str
    questions: List[Question]


@app.get("/")
def root():
    return {"message": "Quiz Generator API is running"}


@app.post("/generate-quiz", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest):
    if not request.topic or not request.topic.strip():
        raise HTTPException(status_code=400, detail="topic is required")

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.7,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a quiz generator. Create multiple-choice quiz questions. "
                        "Return ONLY a JSON array where each item has: question, options (array of 4 strings), "
                        "correct_answer_index (number 0-3), and explanation (string). No markdown, no extra text."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Generate {request.num_questions} multiple-choice quiz questions about: {request.topic}",
                },
            ],
        )

        content = completion.choices[0].message.content

        try:
            questions = json.loads(content)
        except json.JSONDecodeError:
            # Fallback if the model didn't return pure JSON
            questions = [
                {
                    "question": content,
                    "options": [],
                    "correct_answer_index": 0,
                    "explanation": "",
                }
            ]

        return {"topic": request.topic.strip(), "questions": questions}

    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to generate quiz")
