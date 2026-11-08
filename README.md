# QuizGen

Create quizzes by generating questions from a topic, generating from pasted
study material, or writing questions yourself. AI-generated quizzes support 1 to
20 multiple-choice questions across `general`, `niche`, `beginner`,
`intermediate`, and `advanced` tiers; manual quizzes can contain 1 to 50. Take
quizzes, review answers, track attempt history, export to JSON/CSV, share
quizzes publicly, and compete on global and per-quiz leaderboards.

```
quiz-gen/
├── backend/            # FastAPI + SQLAlchemy + Alembic + OpenAI/Gemini
├── frontend/           # React 19 + TypeScript + Vite + Tailwind
└── docker-compose.yml  # PostgreSQL + Backend + Nginx Frontend
```

## Quick Deployment (Docker Compose)

```bash
docker compose up --build -d
```

This starts PostgreSQL 16, runs Alembic database migrations automatically,
starts the FastAPI backend on port `8000`, and serves the production React build
behind Nginx on port `80` (with `/api/*` reverse-proxied to the backend).

## Running it locally

Two terminals — the frontend proxies `/api/*` to the backend, so start the
backend first.

```bash
# terminal 1 — API on http://127.0.0.1:8000
cd backend
pip install -r requirements.txt
alembic upgrade head
python -m uvicorn app.main:app --reload
```

```bash
# terminal 2 — app on http://localhost:5173
cd frontend
npm install
npm run dev
```

Then open <http://localhost:5173>, create an account and create a quiz.

## API

| Method   | Path                        | Auth  | Purpose                                      |
| -------- | --------------------------- | ----- | -------------------------------------------- |
| `GET`    | `/health`                   | –     | Liveness & DB readiness check                |
| `POST`   | `/auth/register`            | –     | Create a user                                |
| `POST`   | `/auth/token`               | –     | OAuth2 login → access + refresh tokens       |
| `POST`   | `/auth/refresh`             | –     | Rotate refresh token for a new token pair    |
| `POST`   | `/auth/logout`              | ✓     | Revoke current access and refresh tokens     |
| `POST`   | `/auth/forgot-password`     | –     | Generate a password reset token              |
| `POST`   | `/auth/reset-password`      | –     | Reset password using a reset token           |
| `GET`    | `/users/me`                 | ✓     | Current user profile                         |
| `PATCH`  | `/users/me`                 | ✓     | Update email, username, or password          |
| `DELETE` | `/users/me`                 | ✓     | Delete account and associated data           |
| `POST`   | `/quizzes/generate`         | ✓     | Generate 1–20 AI questions from topic/notes  |
| `POST`   | `/quizzes/`                 | ✓     | Create a quiz with 1–50 manual questions     |
| `GET`    | `/quizzes/`                 | ✓     | List the caller's quizzes                    |
| `GET`    | `/quizzes/attempts`         | ✓     | List the caller's past quiz attempts         |
| `GET`    | `/quizzes/attempts/{id}`    | ✓     | Get attempt details and question review      |
| `GET`    | `/quizzes/public`           | –     | Browse/search public quizzes (`?search=...`) |
| `GET`    | `/quizzes/leaderboard`      | –     | Global public quiz leaderboard               |
| `GET`    | `/quizzes/{id}/leaderboard` | –     | Per-quiz public leaderboard                  |
| `GET`    | `/quizzes/shared/{id}`      | –     | Fetch shared quiz without answer keys        |
| `PATCH`  | `/quizzes/{id}/share`       | ✓     | Toggle public/private sharing                |
| `GET`    | `/quizzes/{id}`             | ✓     | Fetch one quiz with its questions            |
| `GET`    | `/quizzes/{id}/export`      | ✓     | Export quiz as JSON or CSV (`?format=csv`)   |
| `PATCH`  | `/quizzes/{id}`             | ✓     | Edit quiz title, topic, type, or sharing     |
| `DELETE` | `/quizzes/{id}`             | ✓     | Delete a quiz owned by the caller            |
| `DELETE` | `/quizzes/admin/{id}`       | Admin | Admin takedown of any quiz                   |
| `POST`   | `/quizzes/{id}/submit`      | ✓     | Score an attempt and return explanations     |

Full backend notes are in [`backend/README.md`](backend/README.md); frontend
notes are in [`frontend/README.md`](frontend/README.md).

## Configuration

The backend reads `.env` (see `backend/.env.example`):

| Variable                | Default                        | Notes                                          |
| ----------------------- | ------------------------------ | ---------------------------------------------- |
| `DATABASE_URL`          | `postgresql+psycopg2://...`    | Use `sqlite:///./quiz_gen.db` for local dev    |
| `SECRET_KEY`            | `change-me-in-production`      | JWT signing key — always change this          |
| `OPENAI_API_KEY`        | –                              | OpenAI key for real question generation        |
| `GOOGLE_API_KEY`        | –                              | Optional Gemini key; takes precedence if set   |
| `GEMINI_MODEL`          | `gemini-3.1-flash-lite`        | Gemini model used when `GOOGLE_API_KEY` is set |
| `QUIZ_FALLBACK_ENABLED` | `false`                        | Opt in to template questions on provider failure |

Set either `OPENAI_API_KEY` or `GOOGLE_API_KEY` for AI-generated questions.
When both are set, Gemini is used. By default provider failures are visible
rather than silently producing template questions. Set
`QUIZ_FALLBACK_ENABLED=true` only if offline template questions are desired.

The frontend only needs `VITE_API_BASE_URL` (default `/api`).

## Tests

```bash
cd backend && pytest          # API tests
cd frontend && npm run lint   # lint
cd frontend && npm run build  # type-check + production build
cd frontend && npm run e2e    # browser smoke test (needs both servers running)
```
