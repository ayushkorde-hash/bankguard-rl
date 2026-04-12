from pydantic import BaseModel
from typing import List, Optional, Dict

class Transaction(BaseModel):
    transaction_id: str
    amount: float
    merchant: str
    merchant_category: str
    location: str
    time_of_day: str        # "morning", "afternoon", "night", "midnight"
    is_international: bool
    previous_fraud_flag: bool
    account_age_days: int
    risk_score: float       # visible hint to agent

class AgentAction(BaseModel):
    action: str             # "flag", "approve", "investigate", "escalate"
    transaction_id: str
    confidence: float       # 0.0 to 1.0 — agent's confidence
    reason: Optional[str] = None

class EnvironmentState(BaseModel):
    task_id: str
    transactions: List[Transaction]
    step_count: int
    total_transactions: int
    score: float
    done: bool
    message: str
    flagged_count: int
    approved_count: int
    investigated_count: int

class StepResult(BaseModel):
    state: EnvironmentState
    reward: float
    done: bool
    info: Dict

class GradeResult(BaseModel):
    task_id: str
    score: float
    reward: float
    correct_flags: int
    false_positives: int
    missed_frauds: int
    total: int
    accuracy: float