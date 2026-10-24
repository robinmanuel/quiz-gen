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

3. Create `.env` from the example and add an OpenAI or Google AI key:
   ```bash
   copy .env.example .env     # Windows
   cp .env.example .env       # Mac/Linux
   # Edit .env: set OPENAI_API_KEY or GOOGLE_API_KEY
   ```

4. Apply the database migrations:
   ```bash
   alembic upgrade head
   ```
   For a local database created by an older version of the app (before Alembic
   tracked it), first back up the database, then mark the existing initial
   schema as applied and run the new migration:
   ```bash
   alembic stamp 405269557eb2
   alembic upgrade head
   ```

5. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

   Interactive API docs: http://localhost:8000/docs

6. Start the frontend (in a separate terminal):
   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```
   The app is served on http://localhost:5173 and proxies `/api/*` to this
   server, so CORS never comes into play. See `frontend/README.md` for details.

## Environment variables

| Variable                | Description                                                        |
|-------------------------|--------------------------------------------------------------------|
| `DATABASE_URL`          | SQLAlchemy connection string. Use `sqlite:///./quiz_gen.db` locally |
| `SECRET_KEY`            | JWT signing key — change this before deploying                      |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime (default 30)                                   |
| `OPENAI_API_KEY`        | OpenAI key used to generate questions                               |
| `OPENAI_MODEL`          | OpenAI model (default `gpt-4o-mini`)                                 |
| `GOOGLE_API_KEY`        | Optional Gemini key; takes precedence over OpenAI when set           |
| `GEMINI_MODEL`          | Gemini model (default `gemini-3.1-flash-lite`)                       |
| `QUIZ_FALLBACK_ENABLED` | `false`; set to `true` to allow template questions on provider failure |

With fallback disabled, provider failures surface instead of silently
returning template questions that could be mistaken for generated output.
Enable the setting only when offline template questions are desired.

## Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/health` | Health check | No |
| POST | `/auth/register` | Register a new user | No |
| POST | `/auth/token` | Login (get JWT access token) | No |
| GET | `/users/me` | Current user profile | Yes |
| POST | `/quizzes/generate` | Generate an eight-question general or niche quiz | Yes |
| POST | `/quizzes/` | Create a quiz with 1-50 manually written questions | Yes |
| GET | `/quizzes` | List your quizzes | Yes |
| GET | `/quizzes/public` | Browse quizzes their owners shared publicly | No |
| GET | `/quizzes/leaderboard` | View best scores on public quizzes | No |
| GET | `/quizzes/shared/{id}` | Read a shared quiz without exposing its answer key | No |
| PATCH | `/quizzes/{id}/share` | Make your quiz public or private | Yes |
| GET | `/quizzes/{id}` | Get a single quiz | Yes |
| POST | `/quizzes/{id}/submit` | Submit answers and get score | Yes |

Shared quiz links and the public directory do not expose answer keys. Taking a
shared quiz and recording a leaderboard score requires an account. The
leaderboard shows usernames and each player's best score on quizzes currently
shared publicly; making a quiz private removes its attempts from the public
leaderboard.

Quiz generation can use a topic or up to 20,000 characters of pasted source
material. Source-based questions are instructed to rely only on that material;
provider failures are returned rather than replaced with generic fallback
questions.

## Example: Generate a niche quiz

```bash
curl -X POST "http://localhost:8000/quizzes/generate" \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "JavaScript Basics", "topic": "JavaScript", "quiz_type": "niche"}'
```

## Next steps

- Add rate limiting on OpenAI calls
- Add caching (Redis) for frequent topics
- Dockerize the app
