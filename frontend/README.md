# QuizGen Frontend (React + TypeScript + Vite + Tailwind)

The web client for the Quiz Generator API. It talks to the FastAPI backend in
`../backend` for authentication, quiz generation and attempt scoring.

## Stack

| Concern    | Choice                            |
| ---------- | --------------------------------- |
| Build      | Vite 8                            |
| UI         | React 19 + TypeScript             |
| Routing    | React Router 7 (declarative routes) |
| Server data| TanStack Query 5                  |
| Styling    | Tailwind CSS 4                    |

## Getting started

```bash
npm install
cp .env.example .env     # optional — the defaults already work in dev
npm run dev
```

The app is served on <http://localhost:5173>.

### Talking to the backend

In development the Vite dev server proxies `/api/*` to `http://127.0.0.1:8000`
(see `vite.config.ts`), so the browser only ever makes same-origin requests and
CORS never comes into play. Start the backend first:

```bash
cd ../backend
python -m uvicorn app.main:app --reload
```

For production builds set `VITE_API_BASE_URL` to the public API origin:

```bash
VITE_API_BASE_URL=https://api.example.com npm run build
```

## Scripts

| Script          | What it does                                        |
| --------------- | --------------------------------------------------- |
| `npm run dev`   | Dev server with HMR on port 5173                    |
| `npm run build` | Type-check (`tsc -b`) and bundle to `dist/`         |
| `npm run lint`  | Run oxlint over the source                          |
| `npm run e2e`   | Headless-browser smoke test of the whole user flow  |

## Project structure

```
src/
├── api/            # typed API layer
│   ├── client.ts   # fetch wrapper: auth header, JSON, error normalisation
│   ├── types.ts    # mirrors the FastAPI schemas in backend/app/schemas
│   ├── auth.ts     # register / login / current user
│   └── quizzes.ts  # generate / list / get / submit
├── auth/
│   ├── context.ts      # AuthContext definition
│   ├── AuthContext.tsx # provider: token state + "me" query
│   ├── useAuth.ts      # hook
│   └── ProtectedRoute.tsx
├── components/
│   ├── Layout.tsx  # navbar + shell
│   └── ui.tsx      # Button, Input, Card, Alert, Badge, Spinner, ...
├── lib/
│   ├── cx.ts        # class-name joiner
│   ├── storage.ts   # localStorage helpers for the token
│   └── queryClient.ts
├── pages/
│   ├── LoginPage.tsx
│   ├── RegisterPage.tsx
│   ├── DashboardPage.tsx
│   ├── GeneratePage.tsx
│   ├── QuizPage.tsx
│   └── NotFoundPage.tsx
└── App.tsx         # route table
```

## How it works

**Authentication.** The JWT returned by `POST /auth/token` is stored in
`localStorage` and attached as a `Bearer` header by `src/api/client.ts`. The
provider runs a `me` query whenever a token exists; a `401` clears the session
and bounces the user back to the login screen. Protected routes are wrapped in
`<ProtectedRoute>`, guest-only screens in `<GuestRoute>`.

**Data fetching.** TanStack Query owns every server request. Query keys are
`['me']`, `['quizzes']` and `['quiz', id]`. Mutations invalidate the relevant
key so the dashboard stays in sync after a quiz is generated.

**Taking a quiz.** `QuizPage` walks the questions one at a time with a progress
bar, then posts `{ quiz_id, answers: { "<question_id>": "A" } }` to
`POST /quizzes/{id}/submit`. The score comes back from the API; the per-question
review is derived on the client from the quiz payload. The correct answer is
only revealed after the attempt is submitted.

## End-to-end test

`npm run e2e` drives a headless Chromium browser through the entire flow —
register, generate, answer all five questions, submit, review, sign out — and
asserts on what is rendered. It talks to the DevTools protocol directly, so no
test runner or browser download is needed.

It expects the backend on port 8000 and the dev server on port 5173. Override
with `E2E_APP_URL`, `E2E_CDP_PORT` or `E2E_BROWSER`.
