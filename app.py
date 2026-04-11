"""
FastAPI Server – exposes the environment as a REST API.
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Any, Dict, Optional

from environment import EmailTriageEnv

app = FastAPI(
    title="OpenEnv Email Triage",
    description="A real-world email triage environment for AI agents.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_envs: Dict[str, EmailTriageEnv] = {}


class ResetRequest(BaseModel):
    task: str = "easy"

class StepRequest(BaseModel):
    task: str = "easy"
    action: Dict[str, Any]


@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <html>
    <head><title>OpenEnv Email Triage</title></head>
    <body style="font-family:monospace; padding:2rem; background:#0f0f0f; color:#00ff88">
    <h1>📧 OpenEnv Email Triage</h1>
    <p>A real-world AI agent environment. Use the API to train agents on email triage.</p>
    <h2>Quick Start</h2>
    <pre>
POST /reset  {"task": "easy"}
POST /step   {"task": "easy", "action": {"action_type": "classify", "category": "urgent"}}
GET  /state?task=easy
    </pre>
    <p>→ <a href="/docs" style="color:#00ff88">Interactive API Docs</a></p>
    <p>→ <a href="/tasks" style="color:#00ff88">View all tasks</a></p>
    </body>
    </html>
    """


@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/tasks")
def list_tasks():
    return {
        "tasks": [
            {
                "name": "easy",
                "description": "Classify emails as urgent/important/normal/spam",
                "num_emails": 8,
                "passing_score": 0.70,
                "actions_needed": ["classify"],
            },
            {
                "name": "medium",
                "description": "Classify emails AND set priority (high/medium/low)",
                "num_emails": 8,
                "passing_score": 0.55,
                "actions_needed": ["classify", "priority"],
            },
            {
                "name": "hard",
                "description": "Classify, prioritize, AND write a professional reply",
                "num_emails": 6,
                "passing_score": 0.40,
                "actions_needed": ["classify", "priority", "respond"],
            },
        ]
    }


@app.post("/reset")
def reset(request: Optional[ResetRequest] = None):
    if request is None:
        request = ResetRequest()
    if request.task not in ("easy", "medium", "hard"):
        raise HTTPException(400, "task must be: easy | medium | hard")

    env = EmailTriageEnv(task=request.task)
    _envs[request.task] = env
    obs = env.reset()
    return {"observation": obs, "message": f"Episode started for task '{request.task}'"}


@app.post("/step")
def step(request: StepRequest):
    env = _envs.get(request.task)
    if env is None:
        raise HTTPException(400, f"No active episode for task '{request.task}'. Call /reset first.")

    try:
        obs, reward, done, info = env.step(request.action)
    except RuntimeError as e:
        raise HTTPException(400, str(e))

    return {
        "observation": obs,
        "reward": reward,
        "done": done,
        "info": info,
    }


@app.get("/state")
def state(task: str = "easy"):
    env = _envs.get(task)
    if env is None:
        raise HTTPException(400, f"No active episode for task '{task}'. Call /reset first.")
    return env.state()


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=7860, reload=False)
