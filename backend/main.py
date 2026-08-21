import os
import sys
import joblib
import json
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from sqlalchemy.orm import Session
from database import SessionLocal
from db_models import TaskDB, ProductivityLogDB

# ---------------------------------------------------------------
# ML MODEL
# ---------------------------------------------------------------

ML_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "ml",
    "productivity_model.pkl"
)

productivity_model = joblib.load(ML_PATH)

print("Productivity ML model loaded successfully!")

load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY is not set.")

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

app = FastAPI(title="SmartWork AI")
@app.on_event("startup")
def startup():

    db = SessionLocal()

    try:
        print("PostgreSQL database connected successfully!")
    finally:
        db.close()


# ---------------------------------------------------------------
# CORS
# ---------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------
# In-memory store
# ---------------------------------------------------------------


TASKS: List["Task"] = []
PRODUCTIVITY_LOGS: List["ProductivityLog"] = []
NEXT_ID = 1


# ---------------------------------------------------------------
# Models
# ---------------------------------------------------------------

class PlanRequest(BaseModel):
    prompt: str


class Task(BaseModel):
    id: int
    title: str
    duration: int
    priority: str
    completed: bool = False
    start: Optional[str] = None
    end: Optional[str] = None
class ProductivityLog(BaseModel):
    task_id: int
    title: str
    scheduled_start: Optional[str] = None
    scheduled_end: Optional[str] = None
    duration: int
    priority: str
    completed: bool
    completed_at: Optional[str] = None    
class ProductivityPredictionRequest(BaseModel):
    day_of_week: str
    hour: int
    task_duration: int
    difficulty: int
    previous_completion_rate: float
    category: str

class ScheduleBlock(BaseModel):
    task: str
    start: str
    end: str
    type: str


class PlanResponse(BaseModel):
    tasks: List[Task]
    schedule: List[ScheduleBlock]


class RescheduleRequest(BaseModel):
    unfinished_task: str
    remaining_schedule: List[ScheduleBlock]
    current_time: Optional[str] = None


# ---------------------------------------------------------------
# Gemini structured output schemas
# ---------------------------------------------------------------

SCHEDULE_ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "task": {
            "type": "string"
        },
        "start": {
            "type": "string"
        },
        "end": {
            "type": "string"
        },
        "type": {
            "type": "string",
            "enum": ["task", "break"]
        },
    },
    "required": ["task", "start", "end", "type"],
}


PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "tasks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string"
                    },
                    "duration": {
                        "type": "integer"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["HIGH", "MEDIUM", "LOW"],
                    },
                },
                "required": [
                    "title",
                    "duration",
                    "priority"
                ],
            },
        },
        "schedule": {
            "type": "array",
            "items": SCHEDULE_ITEM_SCHEMA
        },
    },
    "required": ["tasks", "schedule"],
}


RESCHEDULE_SCHEMA = {
    "type": "object",
    "properties": {
        "schedule": {
            "type": "array",
            "items": SCHEDULE_ITEM_SCHEMA
        }
    },
    "required": ["schedule"],
}


# ---------------------------------------------------------------
# Gemini helper
# ---------------------------------------------------------------
# ---------------------------------------------------------------
# Gemini helper
# ---------------------------------------------------------------

def call_gemini(
    system_instruction: str,
    user_prompt: str,
    schema: dict
) -> dict:

    if not GEMINI_API_KEY or client is None:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not set. Add it to backend/.env",
        )

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=user_prompt,
            config={
                "system_instruction": system_instruction,
                "response_mime_type": "application/json",
                "response_schema": schema,
            },
        )

        print("Gemini raw response:", response.text)

        if not response.text:
            raise Exception("Gemini returned an empty response.")

        return json.loads(response.text)

    except Exception as e:
        print("Gemini Error:", e)

        raise HTTPException(
            status_code=502,
            detail=f"Gemini call failed: {str(e)}",
        )

# ---------------------------------------------------------------
# Routes
# ---------------------------------------------------------------

@app.get("/")
def root():
    return {
        "status": "SmartWork AI backend running",
        "gemini": bool(GEMINI_API_KEY),
    }


# ---------------------------------------------------------------
# Generate AI plan
# ---------------------------------------------------------------
@app.post(
    "/api/generate-plan",
    response_model=PlanResponse
)
def generate_plan(req: PlanRequest):

    global NEXT_ID, TASKS

    system_instruction = """
You are SmartWork AI, an intelligent productivity and scheduling assistant.

Understand the user's natural-language request.

Extract their tasks, estimate realistic durations, assign priorities,
and create a practical schedule.

Rules:

1. Respect the user's available time.
2. Never schedule outside the provided time window.
3. Use HIGH, MEDIUM, or LOW priority.
4. Include short 10-15 minute breaks between longer tasks.
5. Do not create unnecessary tasks.
6. Keep the schedule realistic.
7. Return all times using 24-hour HH:MM format.
8. Duration must be in minutes.
"""

    data = call_gemini(
        system_instruction,
        req.prompt,
        PLAN_SCHEMA
    )
    TASKS.clear()
   

    tasks_out = []

    for t in data["tasks"]:

        task_schedule = next(
            (
                s
                for s in data["schedule"]
                if s["type"] == "task"
                and s["task"] == t["title"]
            ),
            None,
        )

        task = Task(
            id=NEXT_ID,
            title=t["title"],
            duration=t["duration"],
            priority=t["priority"],
            completed=False,
            start=task_schedule["start"] if task_schedule else None,
            end=task_schedule["end"] if task_schedule else None,
        )

        
        TASKS.append(task)
        tasks_out.append(task)

        db = SessionLocal()

        try:
            db_task = TaskDB(
                title=task.title,
                duration=task.duration,
                priority=task.priority,
                completed=task.completed,
                start=task.start,
                end=task.end,
           )

            db.add(db_task)
            db.commit()
            task.id = db_task.id

            print("Task saved to PostgreSQL:", task.title)

        finally:
            db.close()

            print("TASKS AFTER ADDING:", TASKS)

        NEXT_ID = 1

    

    schedule_out = [
        ScheduleBlock(**s)
        for s in data["schedule"]
    ]

    return PlanResponse(
        tasks=tasks_out,
        schedule=schedule_out
    )


# ---------------------------------------------------------------
# AI rescheduling
# ---------------------------------------------------------------

# ---------------------------------------------------------------
# AI rescheduling
# ---------------------------------------------------------------

@app.post(
    "/api/reschedule",
    response_model=List[ScheduleBlock]
)
def reschedule(req: RescheduleRequest):

    system_instruction = """
You are SmartWork AI.

A user failed to complete one task.

Create a new schedule starting from the current time.

Rules:

1. Schedule the unfinished_task exactly ONCE.
2. Schedule every task in remaining_schedule exactly ONCE.
3. NEVER duplicate any task.
4. Do not remove any remaining task.
5. Do not schedule anything before the current time.
6. Maintain realistic durations.
7. Include short 10-15 minute breaks when appropriate.
8. Return times using 24-hour HH:MM format.
9. Duration must be in minutes.

Before returning the schedule, make sure no task appears more than once.
"""

    user_prompt = json.dumps({
        "unfinished_task": req.unfinished_task,
        "remaining_schedule": [
            s.model_dump()
            for s in req.remaining_schedule
        ],
        "current_time": req.current_time,
    })

    data = call_gemini(
        system_instruction,
        user_prompt,
        RESCHEDULE_SCHEMA
    )

    return [
        ScheduleBlock(**s)
        for s in data["schedule"]
    ]


# ---------------------------------------------------------------
# Get tasks
# ---------------------------------------------------------------
@app.get(
    "/api/tasks",
    response_model=List[Task]
)
def get_tasks():

    db = SessionLocal()

    try:
        db_tasks = db.query(TaskDB).all()

        return [
            Task(
                id=t.id,
                title=t.title,
                duration=t.duration,
                priority=t.priority,
                completed=t.completed,
                start=t.start,
                end=t.end,
            )
            for t in db_tasks
        ]

    finally:
        db.close()
    


# ---------------------------------------------------------------
# Complete task
# ---------------------------------------------------------------
@app.patch(
    "/api/tasks/{task_id}/complete",
    response_model=Task
)
def complete_task(task_id: int):

    db = SessionLocal()

    try:
        db_task = db.query(TaskDB).filter(
            TaskDB.id == task_id
        ).first()

        if not db_task:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        db_task.completed = True

        log = ProductivityLogDB(
            task_id=db_task.id,
            title=db_task.title,
            scheduled_start=db_task.start,
            scheduled_end=db_task.end,
            duration=db_task.duration,
            priority=db_task.priority,
            completed=True,
            completed_at=datetime.now()
        )

        db.add(log)
        db.commit()

        print("Productivity log created:", db_task.title)

        return Task(
            id=db_task.id,
            title=db_task.title,
            duration=db_task.duration,
            priority=db_task.priority,
            completed=db_task.completed,
            start=db_task.start,
            end=db_task.end,
        )

    finally:
        db.close()
@app.get(
    "/api/productivity-logs",
    response_model=List[ProductivityLog]
)
def get_productivity_logs():

    db = SessionLocal()

    try:
        logs = db.query(ProductivityLogDB).all()

        return [
            ProductivityLog(
                task_id=log.task_id,
                title=log.title,
                scheduled_start=log.scheduled_start,
                scheduled_end=log.scheduled_end,
                duration=log.duration,
                priority=log.priority,
                completed=log.completed,
                completed_at=(
                    log.completed_at.isoformat()
                    if log.completed_at
                    else None
                ),
            )
            for log in logs
        ]

    finally:
        db.close()  
# ---------------------------------------------------------------
# ML PRODUCTIVITY PREDICTION
# ---------------------------------------------------------------
@app.post("/api/predict-productivity")
def predict_productivity(req: ProductivityPredictionRequest):

    # Encode values in the same way used during training
    day_encoder = LabelEncoder()
    day_encoder.fit([
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ])

    category_encoder = LabelEncoder()
    category_encoder.fit([
        "Study",
        "Coding",
        "Exercise",
        "Meeting",
        "Other"
    ])

    day_encoded = day_encoder.transform([req.day_of_week])[0]
    
    # Handle categories that were not present during training
    if req.category in category_encoder.classes_:
        category_encoded = category_encoder.transform([req.category])[0]
    else:
        category_encoded = 0
    input_data = pd.DataFrame([{
        "day_of_week": day_encoded,
        "hour": req.hour,
        "task_duration": req.task_duration,
        "difficulty": req.difficulty,
        "previous_completion_rate": req.previous_completion_rate,
        "category": category_encoded,
    }])

    prediction = productivity_model.predict(input_data)[0]

    return {
        "predicted_productivity": round(float(prediction), 2)
    }      


# ---------------------------------------------------------------
# Delete task
# ---------------------------------------------------------------

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):

    db = SessionLocal()

    try:
        db_task = db.query(TaskDB).filter(
            TaskDB.id == task_id
        ).first()

        if not db_task:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        db.delete(db_task)
        db.commit()

        print("Task deleted from PostgreSQL:", task_id)

        return {
            "status": "deleted"
        }

    finally:
        db.close()