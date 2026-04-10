from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from environment import BankGuardEnvironment
from environment.models import AgentAction, EnvironmentState, StepResult
from typing import Optional
import uvicorn

app = FastAPI(title="BankGuard-RL", description="Bank Fraud Investigation RL Environment")

env = BankGuardEnvironment()

@app.get("/", response_class=HTMLResponse)
def root():
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>BankGuard-RL</title>
</head>
<body>
  <h1>BankGuard-RL</h1>
  <p>Bank Fraud Investigation RL Environment</p>
</body>
</html>"""

@app.post("/reset")
def reset(task_id: Optional[str] = "easy"):
    state = env.reset(task_id=task_id)
    return state

@app.post("/step")
def step(action: AgentAction):
    result = env.step(action)
    return result

@app.get("/state")
def state():
    return env._get_state()

@app.get("/tasks")
def list_tasks():
    return {
        "tasks": [
            {"id": "easy", "description": "Flag obviously fraudulent transactions (amount > 10000)"},
            {"id": "medium", "description": "Detect fraud based on location mismatch and amount patterns"},
            {"id": "hard", "description": "Detect sophisticated fraud with subtle signals"},
        ]
    }

@app.get("/grade")
def grade():
    return env.grade()

def main():
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()