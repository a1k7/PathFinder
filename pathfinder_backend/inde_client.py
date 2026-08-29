import requests
import random
import time
import json

BASE_URL = "http://localhost:8000"

def generate_decision():
    actions = ["create", "update", "view", "delete"]
    users = ["alice", "bob", "charlie", "blocked_user"]
    amounts = [100, 500, 1500, 2000]
    return {
        "decision_data": {
            "action": random.choice(actions),
            "amount": random.choice(amounts),
            "user": random.choice(users)
        },
        "context": {"source": "AI_agent"}
    }

if __name__ == "__main__":
    for i in range(10):
        payload = generate_decision()
        resp = requests.post(f"{BASE_URL}/decide", json=payload)
        if resp.status_code == 200:
            result = resp.json()
            print(f"Decision {i+1}: {result['decision_id'][:8]} -> {'ALLOWED' if result['allowed'] else 'DENIED'} (policy: {result.get('policy_version')})")
        else:
            print(f"Error: {resp.status_code} - {resp.text}")
        time.sleep(1)