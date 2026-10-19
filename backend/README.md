# Quiz Generator Backend (FastAPI + OpenAI)

Minimal FastAPI backend that generates quiz questions using OpenAI's Chat Completions API.

## Setup

1. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file and add your OpenAI API key:
   ```bash
   copy .env.example .env   # Windows
   # or
   cp .env.example .env     # Mac/Linux
   # Then edit .env: OPENAI_API_KEY=sk-...
   ```

4. Start the server:
   ```bash
   uvicorn main:app --reload
   ```

   API docs available at: http://localhost:8000/docs

## Usage

**POST** `http://localhost:8000/generate-quiz`

Request body:
```json
{
  "topic": "JavaScript",
  "num_questions": 5
}
```

Example response:
```json
{
  "topic": "JavaScript",
  "questions": [
    {
      "question": "What does `const` declare in JavaScript?",
      "options": ["A constant variable", "A function", "A class", "A loop"],
      "correct_answer_index": 0,
      "explanation": "`const` declares a block-scoped variable that cannot be reassigned."
    }
  ]
}
```

## Next steps

- Add input validation refinements
- Add a simple frontend to call this endpoint
- Persist quizzes to a database
- Add user accounts and quiz history
