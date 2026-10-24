import json

import pytest

from app.services import openai_service


@pytest.mark.parametrize(
    ("quiz_type", "prompt_requirement"),
    [
        ("general", "GENERAL quiz"),
        ("niche", "NICHE quiz"),
    ],
)
def test_generate_with_google_returns_valid_questions(monkeypatch, quiz_type, prompt_requirement):
    questions = [
        {
            "question_text": "Which collection is mutable in Python?",
            "options": ["A) Tuple", "B) String", "C) List", "D) Integer"],
            "correct_option": "C",
            "explanation": "Lists can be modified after they are created.",
        }
    ]

    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "candidates": [
                    {"content": {"parts": [{"text": json.dumps(questions)}]}}
                ]
            }

    def post(url, *, headers, json, timeout):
        assert url.endswith("gemini-test:generateContent")
        assert headers == {"x-goog-api-key": "test-key"}
        assert json["generationConfig"]["responseMimeType"] == "application/json"
        prompt = json["contents"][0]["parts"][0]["text"]
        assert prompt_requirement in prompt
        assert "exactly 1" in prompt
        return Response()

    monkeypatch.setattr(openai_service.settings, "GOOGLE_API_KEY", "test-key")
    monkeypatch.setattr(openai_service, "GEMINI_MODEL", "gemini-test")
    monkeypatch.setattr(openai_service.httpx, "post", post)

    assert openai_service._generate_with_google("Python", 1, quiz_type) == questions


def test_generate_with_google_rejects_invalid_question_shape(monkeypatch):
    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "text": '[{"question_text":"Question","options":["A"],"correct_option":"A","explanation":"Why"}]'
                                }
                            ]
                        }
                    }
                ]
            }

    monkeypatch.setattr(openai_service.settings, "GOOGLE_API_KEY", "test-key")
    monkeypatch.setattr(openai_service.httpx, "post", lambda *args, **kwargs: Response())
    monkeypatch.setattr(openai_service.time, "sleep", lambda _: None)

    with pytest.raises(ValueError, match="invalid shape"):
        openai_service._generate_with_google("Python", 1, "general")


def test_configured_provider_failure_does_not_silently_return_templates(monkeypatch):
    def fail_generation(topic, num_questions, quiz_type):
        raise RuntimeError("provider unavailable")

    monkeypatch.setattr(openai_service.settings, "GOOGLE_API_KEY", "test-key")
    monkeypatch.setattr(openai_service.settings, "QUIZ_FALLBACK_ENABLED", False)
    monkeypatch.setattr(openai_service, "_generate_with_google", fail_generation)

    with pytest.raises(RuntimeError, match="provider unavailable"):
        openai_service.generate_quiz_questions("Python", 1)
