# insurance_client.py
"""
Feeds the BDR-AI/insurance_decision_boundaries_v1 dataset into PATHFINDER.
Maps dataset fields to PATHFINDER's decision_data format.
"""
import requests
from datasets import load_dataset

BASE_URL = "http://localhost:8000"

# ---- Field mapping rules ----
# The dataset doesn't have "user" or "action" fields directly, so we derive them.
DOMAIN_TO_USER = {
    "motor_claims": "claims_adjuster",
    "health_claims": "health_adjuster",
    "life_insurance": "life_adjuster",
    "property_claims": "property_adjuster",
}

DECISION_TO_ACTION = {
    "claim_severity_assessment": "create",
    "fraud_detection": "update",
    "coverage_verification": "view",
    "claim_rejection": "delete",
}


def map_to_decision(example: dict) -> dict:
    """Convert one dataset row → PATHFINDER decision_data."""
    domain = example.get("decision_domain", "unknown")
    decision_type = example.get("decision_type", "claim_severity_assessment")
    features = example.get("input_features", {}) or {}

    return {
        "user": DOMAIN_TO_USER.get(domain, "unknown_adjuster"),
        "action": DECISION_TO_ACTION.get(decision_type, "view"),
        "amount": features.get("claim_amount", 0),
        "context": {
            "case_id": example.get("case_id"),
            "domain": domain,
            "decision_type": decision_type,
            "original_outcome": example.get("decision_outcome"),
            "audit_trace_id": example.get("audit_trace_id"),
        },
    }


def run():
    print("📥 Loading dataset from Hugging Face...")
    ds = load_dataset("BDR-AI/insurance_decision_boundaries_v1")
    train = ds["train"]
    print(f"✅ Loaded {len(train)} rows\n")

    for i, example in enumerate(train):
        payload = {"decision_data": map_to_decision(example)}
        try:
            resp = requests.post(f"{BASE_URL}/decide", json=payload, timeout=10)
            resp.raise_for_status()
            result = resp.json()
            verdict = "✅ ALLOW" if result.get("allowed") else "❌ DENY"
            print(f"[{i+1:02d}] {example['case_id']:<25} → {verdict}  |  {result.get('reason','')[:60]}")
        except Exception as e:
            print(f"[{i+1:02d}] {example['case_id']} → ERROR: {e}")

    print("\n🎉 Done. Check the frontend Audit Trail to see all decisions.")


if __name__ == "__main__":
    run()