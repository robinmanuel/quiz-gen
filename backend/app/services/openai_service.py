import json
import logging

from openai import OpenAI

from app.config import settings

logger = logging.getLogger("quizgen")

# Google AI (Gemini) exposes an OpenAI-compatible chat completions API, so the
# OpenAI SDK can talk to it by just pointing base_url at Google's endpoint.
client = None
api_key = settings.GOOGLE_API_KEY or settings.OPENAI_API_KEY
if api_key:
    client = OpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

GEMINI_MODEL = settings.GEMINI_MODEL or "gemini-2.0-flash"

# Used when the generation call is unavailable (no API key, rate limit, network
# error) and QUIZ_FALLBACK_ENABLED is on. Keeps the app usable in dev.
_FALLBACK_TEMPLATES = [
    {
        "question_text": "Which statement best describes {topic}?",
        "correct": "It is a subject defined by a specific set of principles and practices.",
        "distractors": [
            "It has no connection to any other field of study.",
            "It only exists in written form and has no practical use.",
            "It developed entirely within the past century.",
        ],
        "explanation": "{topic} is best understood through the core principles and practices that define it.",
    },
    {
        "question_text": "What is the most useful way to learn about {topic}?",
        "correct": "Studying its core concepts, terminology and key examples.",
        "distractors": [
            "Memorising isolated facts without understanding their context.",
            "Skipping the fundamentals and studying only advanced material.",
            "Reading a single summary and assuming mastery.",
        ],
        "explanation": "Building on core concepts and terminology is what makes the rest of {topic} intelligible.",
    },
    {
        "question_text": "Why is it worth understanding {topic}?",
        "correct": "It underpins further study and practical problem-solving.",
        "distractors": [
            "It is only required for passing examinations.",
            "It has no bearing on professional or academic work.",
            "It is useful only for historical interest.",
        ],
        "explanation": "Understanding {topic} transfers to many other situations, which is why it keeps its value over time.",
    },
    {
        "question_text": "Which of the following best demonstrates knowledge of {topic}?",
        "correct": "Explaining its main ideas and applying them to a new situation.",
        "distractors": [
            "Repeating a definition word for word.",
            "Listing unrelated topics that sound similar.",
            "Avoiding questions about it entirely.",
        ],
        "explanation": "Application to a new situation shows real understanding of {topic}, not just recall.",
    },
    {
        "question_text": "How does {topic} usually relate to other fields of study?",
        "correct": "By sharing concepts and methods that cross disciplinary boundaries.",
        "distractors": [
            "By being completely isolated from every other field.",
            "By removing the need to understand anything else.",
            "By existing only within a single narrow context.",
        ],
        "explanation": "Most subjects, {topic} included, borrow methods and vocabulary from neighbouring fields.",
    },
]


def _fallback_questions(topic: str, num_questions: int) -> list[dict]:
    """Deterministic placeholder questions so the API still works offline."""
    questions = []
    for index in range(num_questions):
        template = _FALLBACK_TEMPLATES[index % len(_FALLBACK_TEMPLATES)]
        options = list(template["distractors"])
        position = index % 4
        options.insert(position, template["correct"])
        questions.append(
            {
                "question_text": template["question_text"].format(topic=topic),
                "options": options,
                "correct_option": "ABCD"[position],
                "explanation": template["explanation"].format(topic=topic),
            }
        )
    return questions


def generate_quiz_questions(topic: str, num_questions: int = 5) -> list[dict]:
    if not client:
        if settings.QUIZ_FALLBACK_ENABLED:
            logger.warning(
                "No AI provider API key configured; using offline quiz templates."
            )
            return _fallback_questions(topic, num_questions)
        raise RuntimeError("No AI provider API key configured for quiz generation.")

    try:
        completion = client.chat.completions.create(
            model=GEMINI_MODEL,
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
        return json.loads(content)
    except Exception as exc:  # noqa: BLE001 - any provider failure is handled here
        if not settings.QUIZ_FALLBACK_ENABLED:
            logger.error("Gemini question generation failed: %s", exc)
            raise

        logger.warning(
            "Gemini question generation failed (%s); falling back to offline questions.", exc
        )
        return _fallback_questions(topic, num_questions)
