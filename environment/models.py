from pydantic import BaseModel
from typing import List, Optional

class Transaction(BaseModel):
    transaction_id: str
    amount: float
    merchant: str
    location: str
    is_fraud: bool  # hidden from agent
    risk_score: float  # visible hint

class AgentAction(BaseModel):
    action: str  # "flag", "approve", "investigate"
    transaction_id: str
    reason: Optional[str] = None

class EnvironmentState(BaseModel):
    task_id: str
    transactions: List[Transaction]
    step_count: int
    score: float
    done: bool
    message: str

class StepResult(BaseModel):
    state: EnvironmentState
    reward: float
    done: bool
    info: dict