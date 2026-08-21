# SmartWork AI

A GenAI productivity planner that turns a natural-language description of your
tasks and free time into a structured, schedulable timetable — and can
re-plan itself when something runs over.

**Stack:** React + TypeScript (frontend) · FastAPI (backend) · Gemini structured
outputs (planning engine)

## How it works

```
User (natural language)
        │
        ▼
   FastAPI backend
        │
        ▼
Gemini (JSON-schema structured output)
        │
        ▼
   Tasks + Schedule
        │
        ▼
   React timeline UI
```

Instead of asking Gemini for a paragraph and parsing it with regex, the
backend passes a JSON schema straight to the Gemini API's structured-output
mode, so the model is constrained to return exactly the shape the app needs
(tasks with duration/priority, and a time-blocked schedule with breaks).

## Setup

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # then paste your Gemini API key into .env
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000` — check `http://localhost:8000/docs`
for the interactive API docs.

Get a Gemini API key from Google AI Studio (ai.google.dev) if you don't have one.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

## Using it

1. Go to **AI Planner**, describe what you need to get done and when you're
   free (e.g. *"I have an exam tomorrow. I need to study DBMS for 2 hours and
   Java for 1 hour. I'm free from 5 PM to 10 PM."*)
2. Click **Generate plan** — Gemini returns tasks + a time-blocked schedule
   with breaks built in.
3. On the **Schedule** screen, if you don't finish a task in time, hit
   **🔄 Reschedule** on that block — the backend sends the unfinished task and
   the remaining schedule back to Gemini, which returns a revised plan for
   the rest of the day without touching what's already happened.
4. **Dashboard** shows today's tasks and a completion snapshot.

## What's next (Stage 2 / 3)

- Persist tasks in Postgres instead of in-memory storage
- Auth (per-user plans)
- "What should I do right now?" assistant endpoint
- Deploy (Render/Railway for backend, Vercel for frontend)

## Project structure

```
smart-work-ai/
├── backend/
│   ├── main.py            # FastAPI app + Gemini integration
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── App.tsx         # view routing (Dashboard/Planner/Schedule)
    │   ├── api.ts           # backend API client
    │   ├── types.ts
    │   └── components/
    │       ├── Dashboard.tsx
    │       ├── Planner.tsx
    │       └── Schedule.tsx
    └── package.json
```
