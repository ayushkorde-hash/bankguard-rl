# 🏦 BankGuard-RL

> **A real-world Reinforcement Learning environment for AI-powered bank fraud investigation**

[![OpenEnv](https://img.shields.io/badge/OpenEnv-compliant-blue)](https://openenv.dev)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Space-yellow)](https://huggingface.co/spaces/Ayuushhh/bankguard-rl)

## 🎯 Motivation

Bank fraud costs the global economy over **$32 billion annually**. Human investigators are overwhelmed — the average analyst reviews 200+ transactions per day with an 85% false positive rate. BankGuard-RL trains AI agents to assist human fraud investigators by learning to flag, approve, investigate, or escalate transactions — reducing false positives while catching real fraud.

This environment models the **exact decision loop** a fraud analyst faces: incomplete information, time pressure, and the cost asymmetry between missing fraud vs. blocking legitimate customers.

## 🤖 What the Agent Does

The agent receives a batch of bank transactions with observable features (amount, merchant, location, time, risk score) but **cannot see the ground truth fraud label**. It must decide for each transaction:

| Action | Description | When to use |
|--------|-------------|-------------|
| `flag` | Mark as fraud, block transaction | High confidence fraud detected |
| `approve` | Mark as legitimate, allow | High confidence legitimate |
| `investigate` | Request manual review | Uncertain, needs more info |
| `escalate` | Escalate to senior analyst | Complex, high-stakes case |

## 📊 Observation Space

Each transaction contains:

```json
{
  "transaction_id": "TXN_EASY_001",
  "amount": 45000.00,
  "merchant": "Foreign ATM",
  "merchant_category": "atm_withdrawal",
  "location": "Foreign_IP",
  "time_of_day": "midnight",
  "is_international": true,
  "previous_fraud_flag": true,
  "account_age_days": 12,
  "risk_score": 0.92
}
```

## 🎮 Tasks

### 🟢 Easy — Obvious Fraud Detection
- **Transactions**: 6
- **Fraud rate**: ~50%
- **Signals**: Clear — very high amounts, suspicious merchants, foreign IPs, midnight timing
- **Expected agent score**: 0.75+

### 🟡 Medium — Pattern-Based Detection
- **Transactions**: 9
- **Fraud rate**: ~40%
- **Signals**: Mixed — needs combination of signals (location + time + merchant)
- **Expected agent score**: 0.55–0.75

### 🔴 Hard — Sophisticated Fraud
- **Transactions**: 14
- **Fraud rate**: ~35%
- **Signals**: Subtle — fraudulent transactions look almost legitimate, low risk scores
- **Expected agent score**: 0.35–0.55

## 🏆 Reward Function

| Action | Correct | Incorrect |
|--------|---------|-----------|
| `flag` fraud | +0.7 to +1.0 (scales with confidence) | -0.4 (false positive) |
| `approve` legit | +0.5 to +0.7 | -0.8 (missed fraud) |
| `investigate` | +0.3 (fraud) / +0.2 (legit) | — |
| `escalate` | +0.5 (fraud) / +0.1 (legit) | — |

Rewards are **non-sparse** — every action gets a signal. Confidence is rewarded — high confidence correct decisions score higher.

## 🔌 API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Landing page |
| `/reset?task_id=easy` | POST | Start new episode |
| `/step` | POST | Submit agent action |
| `/state` | GET | Get current state |
| `/grade` | GET | Get final score (0.0–1.0) |
| `/tasks` | GET | List all tasks |
| `/docs` | GET | Interactive API docs |

## 🚀 Setup & Usage

```bash
# Clone
git clone https://github.com/ayushkorde-hash/bankguard-rl.git
cd bankguard-rl

# Install
pip install -r requirements.txt

# Run
uvicorn app:app --host 0.0.0.0 --port 7860

# Visit
open http://localhost:7860
```

## 🐳 Docker

```bash
docker build -t bankguard-rl .
docker run -p 7860:7860 bankguard-rl
```

## 🤖 Run Inference

```bash
export API_BASE_URL=https://api.openai.com/v1
export MODEL_NAME=gpt-4o-mini
export HF_TOKEN=your_token_here
export ENV_URL=http://localhost:7860

python inference.py
```

## 📈 Baseline Scores

| Task | Rule-Based Agent | GPT-4o-mini |
|------|-----------------|-------------|
| Easy | 0.71 | 0.78 |
| Medium | 0.52 | 0.61 |
| Hard | 0.38 | 0.45 |

## 👥 Team

**Team: The Vision** — OpenEnv Round 1, Meta x PyTorch x Scaler Hackathon

- Ayush Korde (Lead) — PVG's College of Engineering, Nashik
- Neeraj Shinde
- Kashish Sonawane