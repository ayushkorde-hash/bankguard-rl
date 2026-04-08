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
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>BankGuard-RL</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      background: #0a0f1e;
      color: #e2e8f0;
      font-family: 'Segoe UI', sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 40px 20px;
    }
    .badge {
      background: #1e3a5f;
      border: 1px solid #3b82f6;
      color: #60a5fa;
      padding: 4px 14px;
      border-radius: 999px;
      font-size: 12px;
      letter-spacing: 2px;
      text-transform: uppercase;
      margin-bottom: 20px;
    }
    h1 {
      font-size: 3rem;
      font-weight: 800;
      background: linear-gradient(135deg, #60a5fa, #a78bfa);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 10px;
      text-align: center;
    }
    .subtitle {
      color: #94a3b8;
      font-size: 1.1rem;
      margin-bottom: 40px;
      text-align: center;
    }
    .status-bar {
      background: #0d2137;
      border: 1px solid #1e40af;
      border-radius: 12px;
      padding: 12px 30px;
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 50px;
      font-size: 14px;
    }
    .dot {
      width: 10px; height: 10px;
      background: #22c55e;
      border-radius: 50%;
      animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.3; }
    }
    .cards {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 20px;
      width: 100%;
      max-width: 900px;
      margin-bottom: 50px;
    }
    .card {
      background: #0f172a;
      border: 1px solid #1e293b;
      border-radius: 16px;
      padding: 24px;
      transition: border-color 0.2s;
    }
    .card:hover { border-color: #3b82f6; }
    .card-icon { font-size: 2rem; margin-bottom: 10px; }
    .card h3 { font-size: 1rem; color: #f1f5f9; margin-bottom: 6px; }
    .card p { font-size: 0.85rem; color: #64748b; }
    .tasks {
      width: 100%;
      max-width: 900px;
      margin-bottom: 50px;
    }
    .tasks h2 {
      font-size: 1.3rem;
      color: #cbd5e1;
      margin-bottom: 16px;
      padding-left: 4px;
    }
    .task-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: #0f172a;
      border: 1px solid #1e293b;
      border-radius: 12px;
      padding: 16px 24px;
      margin-bottom: 10px;
    }
    .task-row .label { font-weight: 600; font-size: 1rem; }
    .task-row .desc { color: #64748b; font-size: 0.85rem; margin-top: 2px; }
    .pill {
      padding: 4px 12px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 600;
    }
    .easy { background: #14532d; color: #4ade80; }
    .medium { background: #713f12; color: #fbbf24; }
    .hard { background: #4c0519; color: #f87171; }
    .endpoints {
      width: 100%;
      max-width: 900px;
      margin-bottom: 50px;
    }
    .endpoints h2 {
      font-size: 1.3rem;
      color: #cbd5e1;
      margin-bottom: 16px;
      padding-left: 4px;
    }
    .endpoint {
      display: flex;
      align-items: center;
      gap: 16px;
      background: #0f172a;
      border: 1px solid #1e293b;
      border-radius: 10px;
      padding: 12px 20px;
      margin-bottom: 8px;
      font-family: monospace;
    }
    .method {
      padding: 3px 10px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 700;
    }
    .get { background: #1e3a5f; color: #60a5fa; }
    .post { background: #1a3322; color: #4ade80; }
    .path { color: #e2e8f0; }
    .edesc { color: #64748b; font-size: 13px; font-family: 'Segoe UI', sans-serif; margin-left: auto; }
    .footer {
      color: #334155;
      font-size: 13px;
      text-align: center;
    }
    .footer a { color: #3b82f6; text-decoration: none; }
    .team { color: #475569; margin-top: 6px; font-size: 12px; }
  </style>
</head>
<body>
  <div class="badge">⚡ OpenEnv Round 1 — Live</div>
  <h1>🏦 BankGuard-RL</h1>
  <p class="subtitle">Bank Fraud Investigation Reinforcement Learning Environment</p>

  <div class="status-bar">
    <div class="dot"></div>
    <span>Environment is <strong>online</strong> and ready for agent interaction</span>
  </div>

  <div class="cards">
    <div class="card">
      <div class="card-icon">🎯</div>
      <h3>3 Difficulty Tasks</h3>
      <p>Easy → Medium → Hard with progressive fraud complexity</p>
    </div>
    <div class="card">
      <div class="card-icon">🤖</div>
      <h3>Agent Actions</h3>
      <p>Flag, Approve, or Investigate each transaction</p>
    </div>
    <div class="card">
      <div class="card-icon">📊</div>
      <h3>Reward Signals</h3>
      <p>Continuous 0.0–1.0 scoring with partial credit</p>
    </div>
    <div class="card">
      <div class="card-icon">🔁</div>
      <h3>Full OpenEnv Spec</h3>
      <p>step() / reset() / state() — fully compliant</p>
    </div>
  </div>

  <div class="tasks">
    <h2>📋 Tasks</h2>
    <div class="task-row">
      <div><div class="label">Easy</div><div class="desc">Flag obviously fraudulent transactions (amount &gt; ₹10,000)</div></div>
      <span class="pill easy">EASY</span>
    </div>
    <div class="task-row">
      <div><div class="label">Medium</div><div class="desc">Detect fraud based on location mismatch and amount patterns</div></div>
      <span class="pill medium">MEDIUM</span>
    </div>
    <div class="task-row">
      <div><div class="label">Hard</div><div class="desc">Detect sophisticated fraud with subtle signals</div></div>
      <span class="pill hard">HARD</span>
    </div>
  </div>

  <div class="endpoints">
    <h2>🔌 API Endpoints</h2>
    <div class="endpoint"><span class="method post">POST</span><span class="path">/reset</span><span class="edesc">Reset environment for a task</span></div>
    <div class="endpoint"><span class="method post">POST</span><span class="path">/step</span><span class="edesc">Submit agent action</span></div>
    <div class="endpoint"><span class="method get">GET</span><span class="path">/state</span><span class="edesc">Get current environment state</span></div>
    <div class="endpoint"><span class="method get">GET</span><span class="path">/grade</span><span class="edesc">Get final score (0.0–1.0)</span></div>
    <div class="endpoint"><span class="method get">GET</span><span class="path">/tasks</span><span class="edesc">List all available tasks</span></div>
    <div class="endpoint"><span class="method get">GET</span><span class="path">/docs</span><span class="edesc">Interactive API documentation</span></div>
  </div>

  <div class="footer">
    Built for <strong>OpenEnv Round 1</strong> · 
    <a href="/docs">API Docs →</a>
    <div class="team">Team: The Vision · Ayush Korde · Neeraj Shinde · Kashish Sonawane</div>
  </div>
</body>
</html>
"""

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)