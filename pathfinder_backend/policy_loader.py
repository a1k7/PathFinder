import yaml
import datetime
from typing import Dict, Any, List, Tuple
from pathlib import Path
from config import POLICY_FILE

def load_policies():
    with open(POLICY_FILE, 'r') as f:
        data = yaml.safe_load(f)
    return data.get("policies", [])

def evaluate_condition(condition: Dict, decision_data: Dict, context: Dict) -> bool:
    """
    Recursively evaluate a condition.
    Supports: eq, ne, gt, lt, gte, lte, in, not_in, between, time_of_day, and, or.
    """
    if isinstance(condition, dict):
        # AND/OR
        if "and" in condition:
            return all(evaluate_condition(sub, decision_data, context) for sub in condition["and"])
        if "or" in condition:
            return any(evaluate_condition(sub, decision_data, context) for sub in condition["or"])
        # Single operator
        for op, value in condition.items():
            if op == "eq":
                return decision_data.get("field") == value  # placeholder, we'll handle below
            # We'll process per field key
    # Flat field:value mappings
    # e.g., {"action": "create"} -> means action == "create"
    # We'll iterate over keys and check them against decision_data
    for field, expected in condition.items():
        actual = decision_data.get(field)
        if isinstance(expected, dict):
            # operator
            for op, op_value in expected.items():
                if op == "eq":
                    if actual != op_value:
                        return False
                elif op == "ne":
                    if actual == op_value:
                        return False
                elif op == "gt":
                    if not (isinstance(actual, (int, float)) and actual > op_value):
                        return False
                elif op == "lt":
                    if not (isinstance(actual, (int, float)) and actual < op_value):
                        return False
                elif op == "gte":
                    if not (isinstance(actual, (int, float)) and actual >= op_value):
                        return False
                elif op == "lte":
                    if not (isinstance(actual, (int, float)) and actual <= op_value):
                        return False
                elif op == "in":
                    if actual not in op_value:
                        return False
                elif op == "not_in":
                    if actual in op_value:
                        return False
                elif op == "between":
                    if not (isinstance(actual, (int, float)) and op_value[0] <= actual <= op_value[1]):
                        return False
                elif op == "time_of_day":
                    # expects value like ["09:00", "17:00"]
                    now = datetime.datetime.now().time()
                    start = datetime.datetime.strptime(op_value[0], "%H:%M").time()
                    end = datetime.datetime.strptime(op_value[1], "%H:%M").time()
                    if not (start <= now <= end):
                        return False
                elif op == "and" or op == "or":
                    # already handled above
                    pass
                else:
                    raise ValueError(f"Unsupported operator: {op}")
        else:
            # simple equality
            if actual != expected:
                return False
    return True

def evaluate_policy(policy: Dict, decision_data: Dict, context: Dict) -> Tuple[bool, str]:
    """
    Returns (allowed, reason)
    """
    rules = policy.get("rules", [])
    for rule in rules:
        cond = rule.get("condition")
        effect = rule.get("effect", "deny")
        if cond is None:
            continue
        if evaluate_condition(cond, decision_data, context):
            return effect == "allow", f"Rule matched: {rule}"
    return False, "No rule matched, default deny"
