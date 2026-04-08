import random
from .models import Transaction, EnvironmentState, StepResult, AgentAction

TASKS = {
    "easy": {
        "description": "Flag obviously fraudulent transactions (amount > 10000)",
        "num_transactions": 5,
        "fraud_threshold": 10000,
    },
    "medium": {
        "description": "Detect fraud based on location mismatch and amount patterns",
        "num_transactions": 8,
        "fraud_threshold": 5000,
    },
    "hard": {
        "description": "Detect sophisticated fraud with subtle signals",
        "num_transactions": 12,
        "fraud_threshold": 2000,
    },
}

MERCHANTS = ["Amazon", "Walmart", "Unknown_Vendor", "ATM_Withdrawal", "Casino", "Grocery"]
LOCATIONS = ["Mumbai", "Delhi", "Foreign_IP", "Unknown", "Nashik", "Pune"]

def generate_transactions(task_id: str) -> list:
    config = TASKS[task_id]
    transactions = []
    for i in range(config["num_transactions"]):
        is_fraud = random.random() < 0.4  # 40% fraud rate
        amount = random.uniform(100, 20000)
        if is_fraud:
            amount = random.uniform(config["fraud_threshold"], 25000)
        transactions.append(Transaction(
            transaction_id=f"TXN_{task_id}_{i:03d}",
            amount=round(amount, 2),
            merchant=random.choice(MERCHANTS),
            location=random.choice(LOCATIONS),
            is_fraud=is_fraud,
            risk_score=round(random.uniform(0.6, 1.0) if is_fraud else random.uniform(0.0, 0.4), 2),
        ))
    return transactions

class BankGuardEnvironment:
    def __init__(self):
        self.task_id = "easy"
        self.transactions = []
        self.step_count = 0
        self.score = 0.0
        self.done = False
        self.correct = 0
        self.total = 0

    def reset(self, task_id: str = "easy") -> EnvironmentState:
        self.task_id = task_id
        self.transactions = generate_transactions(task_id)
        self.step_count = 0
        self.score = 0.0
        self.done = False
        self.correct = 0
        self.total = len(self.transactions)
        return self._get_state()

    def step(self, action: AgentAction) -> StepResult:
        reward = 0.0
        txn = next((t for t in self.transactions if t.transaction_id == action.transaction_id), None)

        if txn is None:
            return StepResult(
                state=self._get_state(),
                reward=-0.1,
                done=self.done,
                info={"error": "Transaction not found"}
            )

        # Grade the action
        if action.action == "flag" and txn.is_fraud:
            reward = 1.0  # Correct fraud detection
            self.correct += 1
        elif action.action == "approve" and not txn.is_fraud:
            reward = 0.8  # Correct approval
            self.correct += 1
        elif action.action == "investigate":
            reward = 0.3  # Partial credit for caution
        else:
            reward = -0.5  # Wrong call

        self.score += reward
        self.step_count += 1

        if self.step_count >= self.total:
            self.done = True

        return StepResult(
            state=self._get_state(),
            reward=round(reward, 2),
            done=self.done,
            info={"correct": self.correct, "total": self.total}
        )

    def _get_state(self) -> EnvironmentState:
        # Hide is_fraud from agent — only show risk_score
        visible_txns = []
        for t in self.transactions:
            visible = t.model_copy()
            visible.is_fraud = False  # agent can't see this
            visible_txns.append(visible)

        return EnvironmentState(
            task_id=self.task_id,
            transactions=visible_txns,
            step_count=self.step_count,
            score=round(self.score, 2),
            done=self.done,
            message=f"Step {self.step_count}/{self.total}"
        )

    def get_final_score(self) -> float:
        """Returns normalized score 0.0 to 1.0"""
        if self.total == 0:
            return 0.0
        return round(min(max(self.score / self.total, 0.0), 1.0), 4)

    def grade(self) -> dict:
        return {
            "task_id": self.task_id,
            "score": self.get_final_score(),
            "correct": self.correct,
            "total": self.total,
            "reward": self.get_final_score()
        }