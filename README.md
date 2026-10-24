# QuizGen

Create quizzes by generating questions from a topic, generating from pasted
study material, or writing questions yourself. AI-generated quizzes have eight
multiple-choice questions; manual quizzes can contain 1 to 50. Take quizzes,
review answers, share quizzes publicly, and browse the community leaderboard.

```
quiz-gen/
├── backend/    # FastAPI + SQLAlchemy + OpenAI
└── frontend/   # React 19 + TypeScript + Vite + Tailwind
```

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

AI quiz generation requires choosing General (broad, accessible questions) or
Niche (difficult questions on specialized details) and returns eight questions.
Users can also create a quiz manually with 1 to 50 questions or generate from
pasted source material.

| Method | Path                      | Auth | Purpose                              |
| ------ | ------------------------- | ---- | ------------------------------------ |
| `GET`  | `/health`                 | –    | Liveness check                       |
| `POST` | `/auth/register`          | –    | Create a user                        |
| `POST` | `/auth/token`             | –    | OAuth2 password login → JWT          |
| `GET`  | `/users/me`               | ✓    | Current user                         |
| `POST` | `/quizzes/generate`       | ✓    | Generate a quiz from a topic         |
| `POST` | `/quizzes/`               | ✓    | Create a quiz with your own questions|
| `GET`  | `/quizzes/`               | ✓    | List the caller's quizzes            |
| `GET`  | `/quizzes/{id}`           | ✓    | Fetch one quiz with its questions    |
| `POST` | `/quizzes/{id}/submit`    | ✓    | Score an attempt                     |

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
