# BankGuard-RL 🏦🔍

**Bank Fraud Investigation RL Environment**

An OpenEnv-compliant reinforcement learning environment where an AI agent learns to investigate and flag fraudulent bank transactions.

## Environment Description

The agent observes transaction details (amount, merchant, location, risk score) and must decide to:
- `flag` → Mark as fraud
- `approve` → Mark as legitimate  
- `investigate` → Request further review

## Tasks

| Task | Difficulty | Description |
|------|-----------|-------------|
| easy | 🟢 Easy | Flag obviously fraudulent transactions (amount > 10000) |
| medium | 🟡 Medium | Detect fraud based on location mismatch and amount |
| hard | 🔴 Hard | Detect sophisticated fraud with subtle signals |

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/reset?task_id=easy` | POST | Reset environment |
| `/step` | POST | Take an action |
| `/state` | GET | Get current state |
| `/grade` | GET | Get final score |

## Setup

```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 7860
```

## Inference

```bash
export API_BASE_URL=https://api.openai.com/v1
export MODEL_NAME=gpt-4o-mini
export HF_TOKEN=your_token
python inference.py
```

## Team
- Ayush Korde (Lead)
- Neeraj Shinde
- Kashish Sonawane