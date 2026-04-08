import os
import json
import httpx
from openai import OpenAI

# Load from environment variables
API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.environ.get("HF_TOKEN", "")
ENV_URL = os.environ.get("ENV_URL", "http://0.0.0.0:7860")

client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)

def get_agent_action(state: dict, task_id: str) -> dict:
    """Ask the LLM to decide what action to take."""
    transactions = state.get("transactions", [])
    if not transactions:
        return None
    
    # Pick first un-actioned transaction (simple strategy)
    txn = transactions[state.get("step_count", 0) % len(transactions)]
    
    prompt = f"""You are a bank fraud investigator.

Transaction details:
- ID: {txn['transaction_id']}
- Amount: ${txn['amount']}
- Merchant: {txn['merchant']}
- Location: {txn['location']}
- Risk Score: {txn['risk_score']}

Decide ONE action: "flag" (fraud), "approve" (legitimate), or "investigate" (uncertain).
Respond ONLY with valid JSON like: {{"action": "flag", "transaction_id": "{txn['transaction_id']}", "reason": "high risk score"}}"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
    )
    
    text = response.choices[0].message.content.strip()
    try:
        return json.loads(text)
    except:
        # Fallback if JSON parse fails
        return {"action": "investigate", "transaction_id": txn["transaction_id"], "reason": "parse error"}


def run_task(task_id: str):
    print(json.dumps({"type": "[START]", "task_id": task_id}))
    
    # Reset environment
    r = httpx.post(f"{ENV_URL}/reset", params={"task_id": task_id})
    state = r.json()
    
    step_num = 0
    total_reward = 0.0
    
    while not state.get("done", False):
        action_data = get_agent_action(state, task_id)
        if not action_data:
            break
        
        result = httpx.post(f"{ENV_URL}/step", json=action_data)
        result_data = result.json()
        
        reward = result_data.get("reward", 0.0)
        total_reward += reward
        state = result_data.get("state", state)
        
        print(json.dumps({
            "type": "[STEP]",
            "task_id": task_id,
            "step": step_num,
            "action": action_data.get("action"),
            "reward": reward,
        }))
        step_num += 1
        
        if result_data.get("done", False):
            break
    
    # Get final grade
    grade = httpx.get(f"{ENV_URL}/grade").json()
    final_score = grade.get("score", 0.0)
    
    print(json.dumps({
        "type": "[END]",
        "task_id": task_id,
        "total_steps": step_num,
        "total_reward": round(total_reward, 4),
        "final_score": final_score,
    }))
    
    return final_score


if __name__ == "__main__":
    tasks = ["easy", "medium", "hard"]
    scores = {}
    
    for task in tasks:
        score = run_task(task)
        scores[task] = score
    
    print(json.dumps({"type": "[SUMMARY]", "scores": scores}))