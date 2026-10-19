import json
from openai import OpenAI
from app.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_quiz_questions(topic: str, num_questions: int = 5) -> list[dict]:
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0.7,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a quiz generator. Return ONLY a JSON array where each item has: "
                    "question_text (string), options (array of 4 strings), "
                    "correct_option (string 'A'|'B'|'C'|'D'), and explanation (string). "
                    "No markdown, no extra text."
                ),
            },
            {
                "role": "user",
                "content": f"Generate {num_questions} multiple-choice quiz questions about: {topic}",
            },
        ],
    )

    content = completion.choices[0].message.content
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return [
            {
                "question_text": content,
                "options": [],
                "correct_option": "A",
                "explanation": "",
            }
        ]
