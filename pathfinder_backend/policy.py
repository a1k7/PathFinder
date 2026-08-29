from policy_loader import load_policies, evaluate_policy
from typing import Tuple, Dict, Any
import datetime

class PolicyEngine:
    def __init__(self):
        self.policies = load_policies()
        self.current_policy = self.policies[0] if self.policies else None
        self.version = self.current_policy.get("version", "1.0.0") if self.current_policy else "1.0.0"

    def reload(self):
        self.policies = load_policies()
        self.current_policy = self.policies[0] if self.policies else None
        self.version = self.current_policy.get("version", "1.0.0") if self.current_policy else "1.0.0"

    def evaluate(self, decision_data: Dict[str, Any], context: Dict[str, Any] = None) -> Tuple[bool, str, str]:
        context = context or {}
        # Add time_of_day to context if not present
        if "time_of_day" not in context:
            context["time_of_day"] = datetime.datetime.now().strftime("%H:%M")
        if self.current_policy is None:
            return False, "No policy loaded", "0.0.0"
        allowed, reason = evaluate_policy(self.current_policy, decision_data, context)
        return allowed, reason, self.version