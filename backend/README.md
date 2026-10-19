# Quiz Generator Backend (FastAPI + OpenAI)

Modular FastAPI backend for generating and managing quizzes using OpenAI's API.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app + router registration
│   ├── config.py            # Pydantic settings / env vars
│   ├── database.py          # SQLAlchemy engine, session, Base
│   ├── security.py          # Password hashing, JWT tokens
│   ├── dependencies.py      # DB session, current user auth
│   ├── models/              # SQLAlchemy DB models
│   │   ├── user.py
│   │   ├── quiz.py
│   │   ├── question.py
│   │   └── attempt.py
│   ├── schemas/             # Pydantic request/response models
│   │   ├── user.py
│   │   ├── quiz.py
│   │   ├── question.py
│   │   ├── attempt.py
│   │   └── token.py
│   ├── routers/             # API route handlers
│   │   ├── auth.py          # register / login
│   │   ├── users.py         # current user profile
│   │   ├── quizzes.py       # generate, list, get, submit
│   │   └── health.py        # health check
│   └── services/            # Business logic
│       ├── openai_service.py   # OpenAI API calls
│       └── quiz_service.py     # Quiz assembly
├── tests/                   # pytest tests
├── .env                     # copy from .env.example
├── .env.example
├── requirements.txt
└── README.md
```

## Setup

1. Create & activate a virtual environment:
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

3. Create `.env` from the example and add your OpenAI key:
   ```bash
   copy .env.example .env     # Windows
   cp .env.example .env       # Mac/Linux
   # Edit .env: OPENAI_API_KEY=sk-...
   ```

4. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

   Interactive API docs: http://localhost:8000/docs

## Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/health` | Health check | No |
| POST | `/auth/register` | Register a new user | No |
| POST | `/auth/token` | Login (get JWT access token) | No |
| GET | `/users/me` | Current user profile | Yes |
| POST | `/quizzes/generate` | Generate a quiz via OpenAI | Yes |
| GET | `/quizzes` | List your quizzes | Yes |
| GET | `/quizzes/{id}` | Get a single quiz | Yes |
| POST | `/quizzes/{id}/submit` | Submit answers and get score | Yes |

## Example: Generate a quiz

```bash
curl -X POST "http://localhost:8000/quizzes/generate" \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "JavaScript Basics", "topic": "JavaScript"}'
```

## Next steps

- Add Alembic for database migrations
- Add pytest test suite
- Add rate limiting on OpenAI calls
- Add caching (Redis) for frequent topics
- Dockerize the app
