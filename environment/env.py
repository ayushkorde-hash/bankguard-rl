import random
from .models import Transaction, EnvironmentState, StepResult, AgentAction, GradeResult

# ── Task Definitions ──────────────────────────────────────────────
TASKS = {
    "easy": {
        "description": "Detect obvious fraud: very high amounts from suspicious merchants",
        "num_transactions": 6,
        "fraud_rate": 0.5,
        "fraud_signals": "obvious",  # clear signals
    },
    "medium": {
        "description": "Detect fraud using combinations: location + time + merchant patterns",
        "num_transactions": 9,
        "fraud_rate": 0.4,
        "fraud_signals": "moderate",
    },
    "hard": {
        "description": "Detect sophisticated fraud: subtle signals, legitimate-looking transactions",
        "num_transactions": 14,
        "fraud_rate": 0.35,
        "fraud_signals": "subtle",
    },
}

MERCHANTS = {
    "legitimate": ["Grocery Store", "Salary Credit", "Netflix", "Electricity Bill", "Amazon India"],
    "suspicious": ["Unknown Vendor", "Crypto Exchange", "Foreign ATM", "Casino Online", "Wire Transfer"],
}

LOCATIONS = {
    "home": ["Mumbai", "Pune", "Nashik", "Delhi", "Bangalore"],
    "foreign": ["Foreign_IP", "Unknown_Location", "VPN_Detected", "Offshore"],
}

CATEGORIES = {
    "safe": ["groceries", "utilities", "entertainment", "salary"],
    "risky": ["crypto", "gambling", "wire_transfer", "atm_withdrawal"],
}

def generate_transaction(txn_id: str, task_id: str, force_fraud: bool = False) -> Transaction:
    config = TASKS[task_id]
    signals = config["fraud_signals"]
    is_fraud = force_fraud or (random.random() < config["fraud_rate"])

    if is_fraud:
        if signals == "obvious":
            # Very clear fraud signals
            amount = round(random.uniform(15000, 50000), 2)
            merchant = random.choice(MERCHANTS["suspicious"])
            merchant_category = random.choice(CATEGORIES["risky"])
            location = random.choice(LOCATIONS["foreign"])
            time_of_day = random.choice(["midnight", "night"])
            is_international = True
            previous_fraud_flag = random.random() < 0.7
            risk_score = round(random.uniform(0.75, 1.0), 2)
        elif signals == "moderate":
            # Mixed signals
            amount = round(random.uniform(5000, 20000), 2)
            merchant = random.choice(MERCHANTS["suspicious"] + MERCHANTS["legitimate"])
            merchant_category = random.choice(CATEGORIES["risky"])
            location = random.choice(LOCATIONS["foreign"] + LOCATIONS["home"])
            time_of_day = random.choice(["night", "midnight", "afternoon"])
            is_international = random.random() < 0.6
            previous_fraud_flag = random.random() < 0.4
            risk_score = round(random.uniform(0.5, 0.85), 2)
        else:
            # Subtle fraud — looks almost legitimate
            amount = round(random.uniform(1000, 8000), 2)
            merchant = random.choice(MERCHANTS["legitimate"])
            merchant_category = random.choice(CATEGORIES["safe"])
            location = random.choice(LOCATIONS["home"])
            time_of_day = random.choice(["morning", "afternoon", "night"])
            is_international = random.random() < 0.3
            previous_fraud_flag = random.random() < 0.2
            risk_score = round(random.uniform(0.35, 0.65), 2)
        account_age_days = random.randint(1, 90)
    else:
        # Legitimate transaction
        amount = round(random.uniform(100, 5000), 2)
        merchant = random.choice(MERCHANTS["legitimate"])
        merchant_category = random.choice(CATEGORIES["safe"])
        location = random.choice(LOCATIONS["home"])
        time_of_day = random.choice(["morning", "afternoon"])
        is_international = False
        previous_fraud_flag = False
        risk_score = round(random.uniform(0.0, 0.35), 2)
        account_age_days = random.randint(180, 3000)

    return Transaction(
        transaction_id=txn_id,
        amount=amount,
        merchant=merchant,
        merchant_category=merchant_category,
        location=location,
        time_of_day=time_of_day,
        is_international=is_international,
        previous_fraud_flag=previous_fraud_flag,
        account_age_days=account_age_days,
        risk_score=risk_score,
    )


# ── Environment Class ─────────────────────────────────────────────
class BankGuardEnvironment:
    def __init__(self):
        self.task_id = "easy"
        self.transactions = []
        self.ground_truth = {}   # txn_id → True/False (is_fraud)
        self.step_count = 0
        self.score = 0.0
        self.done = False
        self.correct_flags = 0
        self.false_positives = 0
        self.missed_frauds = 0
        self.flagged_count = 0
        self.approved_count = 0
        self.investigated_count = 0
        self.actions_taken = {}  # txn_id → action

    def reset(self, task_id: str = "easy") -> EnvironmentState:
        self.task_id = task_id
        config = TASKS[task_id]
        n = config["num_transactions"]
        self.transactions = []
        self.ground_truth = {}
        self.step_count = 0
        self.score = 0.0
        self.done = False
        self.correct_flags = 0
        self.false_positives = 0
        self.missed_frauds = 0
        self.flagged_count = 0
        self.approved_count = 0
        self.investigated_count = 0
        self.actions_taken = {}

        # Generate transactions
        for i in range(n):
            txn_id = f"TXN_{task_id.upper()}_{i:03d}"
            txn = generate_transaction(txn_id, task_id)
            self.transactions.append(txn)
            self.ground_truth[txn_id] = txn.is_fraud

        random.shuffle(self.transactions)
        return self._get_state()

    def step(self, action: AgentAction) -> StepResult:
        if self.done:
            return StepResult(
                state=self._get_state(),
                reward=0.0,
                done=True,
                info={"error": "Episode already done"}
            )

        txn = next((t for t in self.transactions if t.transaction_id == action.transaction_id), None)

        if txn is None:
            return StepResult(
                state=self._get_state(),
                reward=-0.2,
                done=self.done,
                info={"error": f"Transaction {action.transaction_id} not found"}
            )

        if action.transaction_id in self.actions_taken:
            return StepResult(
                state=self._get_state(),
                reward=-0.1,
                done=self.done,
                info={"error": "Transaction already processed"}
            )

        is_fraud = self.ground_truth[action.transaction_id]
        confidence = max(0.0, min(1.0, action.confidence))
        reward = 0.0

        if action.action == "flag":
            self.flagged_count += 1
            if is_fraud:
                # Correct fraud detection — reward scales with confidence
                reward = 0.7 + (0.3 * confidence)
                self.correct_flags += 1
            else:
                # False positive — penalize
                reward = -0.4 * confidence
                self.false_positives += 1

        elif action.action == "approve":
            self.approved_count += 1
            if not is_fraud:
                # Correct approval
                reward = 0.5 + (0.2 * confidence)
            else:
                # Missed fraud — heavy penalty
                reward = -0.8
                self.missed_frauds += 1

        elif action.action == "investigate":
            self.investigated_count += 1
            # Partial credit — agent is being cautious
            if is_fraud:
                reward = 0.3  # caught it but not decisively
            else:
                reward = 0.2  # unnecessary but not harmful

        elif action.action == "escalate":
            # Escalate to senior — partial credit
            if is_fraud:
                reward = 0.5
                self.correct_flags += 1
            else:
                reward = 0.1

        self.score += reward
        self.step_count += 1
        self.actions_taken[action.transaction_id] = action.action

        # Check if all transactions processed
        if len(self.actions_taken) >= len(self.transactions):
            self.done = True

        return StepResult(
            state=self._get_state(),
            reward=round(reward, 4),
            done=self.done,
            info={
                "correct_flags": self.correct_flags,
                "false_positives": self.false_positives,
                "missed_frauds": self.missed_frauds,
                "was_fraud": is_fraud,
            }
        )

    def _get_state(self) -> EnvironmentState:
        # Hide ground truth from agent
        visible = []
        for t in self.transactions:
            d = t.model_dump()
            d["is_fraud"] = False  # hidden
            visible.append(Transaction(**d))

        return EnvironmentState(
            task_id=self.task_id,
            transactions=visible,
            step_count=self.step_count,
            total_transactions=len(self.transactions),
            score=round(self.score, 4),
            done=self.done,
            message=f"Processed {len(self.actions_taken)}/{len(self.transactions)} transactions",
            flagged_count=self.flagged_count,
            approved_count=self.approved_count,
            investigated_count=self.investigated_count,
        )

    def get_final_score(self) -> float:
        total = len(self.transactions)
        if total == 0:
            return 0.0
        max_possible = total * 1.0  # max reward per transaction
        raw = self.score / max_possible
        return round(min(max(raw, 0.0), 1.0), 4)

    def grade(self) -> dict:
        total = len(self.transactions)
        fraud_total = sum(1 for v in self.ground_truth.values() if v)
        accuracy = (self.correct_flags + (total - fraud_total - self.false_positives)) / max(total, 1)
        return {
            "task_id": self.task_id,
            "score": self.get_final_score(),
            "reward": self.get_final_score(),
            "correct_flags": self.correct_flags,
            "false_positives": self.false_positives,
            "missed_frauds": self.missed_frauds,
            "total": total,
            "accuracy": round(accuracy, 4),
        }