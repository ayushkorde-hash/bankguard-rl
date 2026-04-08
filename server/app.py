from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from environment import BankGuardEnvironment
from environment.models import AgentAction, EnvironmentState, StepResult
from typing import Optional
import uvicorn

app = FastAPI(title="BankGuard-RL", description="Bank Fraud Investigation RL Environment")

env = BankGuardEnvironment()

@app.get("/")
def root():
    return {"status": "ok", "environment": "BankGuard-RL", "version": "1.0"}

@app.post("/reset")
def reset(task_id: Optional[str] = "easy"):
    return env.reset(task_id=task_id)

@app.post("/step")
def step(action: AgentAction):
    return env.step(action)

@app.get("/state")
def state():
    return env._get_state()

@app.get("/grade")
def grade():
    return env.grade()

@app.get("/tasks")
def list_tasks():
    return {"tasks": [
        {"id": "easy", "description": "Flag obviously fraudulent transactions"},
        {"id": "medium", "description": "Detect fraud based on location mismatch"},
        {"id": "hard", "description": "Detect sophisticated fraud with subtle signals"},
    ]}

def main():
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
