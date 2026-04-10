import os
import json
import httpx
from openai import OpenAI

API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.environ.get("HF_TOKEN", "dummy-token")
ENV_URL = os.environ.get("ENV_URL", "http://0.0.0.0:7860")

try:
    client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)
except Exception as e:
    print(f"Warning: OpenAI client init failed: {e}", flush=True)
    client = None


def get_agent_action(state: dict, task_id: str) -> dict:
    """Ask LLM to decide action, with rule-based fallback."""
    transactions = state.get("transactions", [])
    if not transactions:
        return None

    step = state.get("step_count", 0)
    txn = transactions[step % len(transactions)]
    txn_id = txn.get("transaction_id", "TXN_000")
    amount = txn.get("amount", 0)
    risk_score = txn.get("risk_score", 0.5)

    # Try LLM first
    if client is not None:
        try:
            prompt = f"""You are a bank fraud investigator.

Transaction:
- ID: {txn_id}
- Amount: ${amount}
- Merchant: {txn.get('merchant', 'Unknown')}
- Location: {txn.get('location', 'Unknown')}
- Risk Score: {risk_score}

Choose ONE action: "flag" (fraud), "approve" (legitimate), "investigate" (uncertain).
Respond ONLY with valid JSON: {{"action": "flag", "transaction_id": "{txn_id}", "reason": "high risk"}}"""

            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                timeout=30,
            )
            text = response.choices[0].message.content.strip()
            # Clean up markdown if present
            text = text.replace("```json", "").replace("```", "").strip()
            result = json.loads(text)
            return result
        except Exception as e:
            print(f"Warning: LLM call failed ({e}), using rule-based fallback", flush=True)

    # Rule-based fallback (always works without API)
    if risk_score > 0.6 or amount > 8000:
        action = "flag"
        reason = "high risk score or large amount"
    elif risk_score < 0.3 and amount < 3000:
        action = "approve"
        reason = "low risk score and small amount"
    else:
        action = "investigate"
        reason = "moderate risk, needs review"

    return {
        "action": action,
        "transaction_id": txn_id,
        "reason": reason
    }


def run_task(task_id: str) -> float:
    print(f"[START] task={task_id} env=bankguard-rl model={MODEL_NAME}", flush=True)

    try:
        r = httpx.post(f"{ENV_URL}/reset", params={"task_id": task_id}, timeout=30)
        r.raise_for_status()
        state = r.json()
    except Exception as e:
        print(f"[END] success=false steps=0 score=0.00 rewards=", flush=True)
        return 0.0

    step_num = 0
    total_reward = 0.0
    rewards = []

    try:
        while not state.get("done", False):
            try:
                action_data = get_agent_action(state, task_id)
                if action_data is None:
                    break

                result = httpx.post(
                    f"{ENV_URL}/step",
                    json=action_data,
                    timeout=30
                )
                result.raise_for_status()
                result_data = result.json()

                reward = float(result_data.get("reward", 0.0))
                total_reward += reward
                rewards.append(round(reward, 2))
                state = result_data.get("state", state)
                step_num += 1

                done = result_data.get("done", False)
                error = result_data.get("info", {}).get("error", None)

                print(
                    f"[STEP] step={step_num} "
                    f"action={action_data.get('action')} "
                    f"reward={reward:.2f} "
                    f"done={str(done).lower()} "
                    f"error={error if error else 'null'}",
                    flush=True
                )

                if done:
                    break

                if step_num > 50:  # safety limit
                    break

            except Exception as e:
                print(f"Warning: step error: {e}", flush=True)
                break

        # Get final grade
        try:
            grade = httpx.get(f"{ENV_URL}/grade", timeout=30).json()
            final_score = float(grade.get("score", 0.0))
        except Exception:
            final_score = round(total_reward / max(step_num, 1), 4)
            final_score = min(max(final_score, 0.0), 1.0)

        rewards_str = ",".join(str(r) for r in rewards)
        success = final_score > 0.5

        print(
            f"[END] success={str(success).lower()} "
            f"steps={step_num} "
            f"score={final_score:.2f} "
            f"rewards={rewards_str}",
            flush=True
        )
        return final_score

    except Exception as e:
        print(f"[END] success=false steps={step_num} score=0.00 rewards=", flush=True)
        return 0.0


if __name__ == "__main__":
    tasks = ["easy", "medium", "hard"]
    all_scores = {}

    for task in tasks:
        try:
            score = run_task(task)
            all_scores[task] = score
        except Exception as e:
            print(f"[END] success=false steps=0 score=0.00 rewards=", flush=True)
            all_scores[task] = 0.0

    print(json.dumps({"summary": all_scores}), flush=True)