from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from datetime import datetime
import json
import uuid
from typing import List, Dict
from sqlalchemy.orm import Session

# ---- Local imports ----
from models import (
    DecisionRequest, DecisionResponse, Receipt,
    VerifyRequest, ReplayRequest, TamperRequest, TamperResponse
)
from policy import PolicyEngine
from memory import DatabaseMemory
from crypto import load_or_generate_keys, sign_data, verify_signature
from logging_config import setup_logging
from database import get_db

# ---- Canonical JSON (recursive key sorting) ----
def canonical_json(obj):
    """Recursively sort dict keys and dump to JSON string with no extra spaces."""
    def _sort(d):
        if isinstance(d, dict):
            return {k: _sort(v) for k, v in sorted(d.items())}
        elif isinstance(d, list):
            return [_sort(v) for v in d]
        else:
            return d
    return json.dumps(_sort(obj), sort_keys=True, separators=(',', ':'))

# ---- Logging & app ----
logger = setup_logging()
app = FastAPI(
    title="PATHFINDER Runtime Governance",
    description="Policy‑aware transaction harness for intelligent decision engines.",
    version="1.0.0"
)

# ---- Load RSA keys ----
private_key, public_key = load_or_generate_keys()

# ---- Policy engine (loads from YAML) ----
policy_engine = PolicyEngine()

# ---- Helper to generate receipt (uses canonical JSON) ----
def generate_receipt(decision_id: str, request: DecisionRequest, response: DecisionResponse, policy_version: str) -> Receipt:
    # Use model_dump to get the exact serialized response (ensures reason matches stored)
    response_dict = response.model_dump(mode='json')
    payload = {
        "decision_id": decision_id,
        "request": request.model_dump(mode='json'),
        "response": {
            "allowed": response_dict["allowed"],
            "reason": response_dict["reason"],
            "timestamp": response_dict["timestamp"],
            "policy_version": response_dict["policy_version"]
        }
    }
    payload_str = canonical_json(payload)
    payload_bytes = payload_str.encode('utf-8')
    signature = sign_data(private_key, payload_bytes)
    receipt_id = str(uuid.uuid4())
    return Receipt(
        receipt_id=receipt_id,
        decision_id=decision_id,
        timestamp=datetime.utcnow(),
        policy_version=policy_version,
        signed_data_b64=payload_str,
        signature_b64=signature
    )
# ---- Endpoints ----

@app.post("/decide", response_model=DecisionResponse, status_code=status.HTTP_200_OK)
async def decide(
    request: DecisionRequest,
    db: Session = Depends(get_db)
):
    decision_id = request.decision_id or str(uuid.uuid4())
    memory = DatabaseMemory(db)
    if memory.get_decision(decision_id):
        raise HTTPException(status_code=409, detail="Decision ID already exists")

    allowed, reason, policy_version = policy_engine.evaluate(
        request.decision_data,
        request.context
    )

    response = DecisionResponse(
        decision_id=decision_id,
        allowed=allowed,
        reason=reason,
        timestamp=datetime.utcnow(),
        receipt=None,
        policy_version=policy_version
    )

    receipt = None
    if allowed:
        receipt = generate_receipt(decision_id, request, response, policy_version)
        response.receipt = receipt

    memory.store_decision(decision_id, request, response, receipt)

    memory.log_audit(
        action="decision_evaluation",
        details={
            "decision_id": decision_id,
            "allowed": allowed,
            "reason": reason,
            "policy_version": policy_version,
            "receipt_generated": receipt is not None
        }
    )

    logger.info(f"Decision {decision_id}: {allowed} - {reason} (policy {policy_version})")
    return response

@app.get("/receipt/{receipt_id}", response_model=Receipt)
async def get_receipt(receipt_id: str, db: Session = Depends(get_db)):
    memory = DatabaseMemory(db)
    receipt = memory.get_receipt(receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return receipt

@app.post("/verify", response_model=dict)
async def verify(verify_req: VerifyRequest, db: Session = Depends(get_db)):
    decision_id = verify_req.decision_id
    receipt = verify_req.receipt
    memory = DatabaseMemory(db)

    stored_entry = memory.get_decision(decision_id)
    if not stored_entry:
        raise HTTPException(status_code=404, detail="Decision not found")

    stored_receipt = memory.get_receipt_by_decision(decision_id)
    if not stored_receipt:
        return {"verified": False, "reason": "No receipt found", "tampered": False}
    if stored_receipt.receipt_id != receipt.receipt_id:
        return {"verified": False, "reason": "Receipt ID mismatch", "tampered": True}

    # Reconstruct the payload from the stored data using canonical JSON
    stored_payload = {
        "decision_id": decision_id,
        "request": stored_entry["request"],
        "response": {
            "allowed": stored_entry["response"]["allowed"],
            "reason": stored_entry["response"]["reason"],
            "timestamp": stored_entry["response"]["timestamp"],
            "policy_version": stored_entry["response"].get("policy_version", "unknown")
        }
    }
    stored_payload_str = canonical_json(stored_payload)
    stored_payload_bytes = stored_payload_str.encode('utf-8')
    

    # --- DEBUG: Print the two strings ---
    print("=== SIGNED_DATA_B64 ===")
    print(receipt.signed_data_b64)
    print("=== RECONSTRUCTED ===")
    print(stored_payload_str)
    # ---------------------------------

    if stored_payload_str != receipt.signed_data_b64:
        return {
            "verified": False,
            "reason": "Stored data does not match signed data (possible tampering)",
            "tampered": True
        }

    # Compare the JSON strings first
    if stored_payload_str != receipt.signed_data_b64:
        return {
            "verified": False,
            "reason": "Stored data does not match signed data (possible tampering)",
            "tampered": True
        }

    # Now verify the cryptographic signature
    try:
        valid = verify_signature(public_key, stored_payload_bytes, receipt.signature_b64)
        if not valid:
            return {"verified": False, "reason": "Invalid signature", "tampered": True}
    except Exception as e:
        return {"verified": False, "reason": f"Verification error: {str(e)}", "tampered": True}

    return {"verified": True, "reason": "Receipt is valid and data integrity confirmed", "tampered": False}

@app.post("/replay", response_model=dict)
async def replay(replay_req: ReplayRequest, db: Session = Depends(get_db)):
    decision_id = replay_req.decision_id
    memory = DatabaseMemory(db)
    stored_entry = memory.get_decision(decision_id)
    if not stored_entry:
        raise HTTPException(status_code=404, detail="Decision not found")

    request_data = stored_entry["request"]
    original_response = stored_entry["response"]

    allowed_now, reason_now, policy_version_now = policy_engine.evaluate(
        request_data["decision_data"],
        request_data.get("context")
    )

    original_allowed = original_response["allowed"]
    match = (allowed_now == original_allowed)

    memory.log_audit(
        action="replay",
        details={
            "decision_id": decision_id,
            "original_allowed": original_allowed,
            "replay_allowed": allowed_now,
            "match": match,
            "reason": reason_now,
            "current_policy_version": policy_version_now
        }
    )

    return {
        "decision_id": decision_id,
        "original_allowed": original_allowed,
        "replay_allowed": allowed_now,
        "match": match,
        "reason": reason_now,
        "policy_version": policy_version_now
    }

@app.post("/tamper", response_model=TamperResponse)
async def tamper(tamper_req: TamperRequest, db: Session = Depends(get_db)):
    decision_id = tamper_req.decision_id
    memory = DatabaseMemory(db)
    stored_entry = memory.get_decision(decision_id)
    if not stored_entry:
        raise HTTPException(status_code=404, detail="Decision not found")

    field = tamper_req.field or "decision_data.amount"
    new_value = tamper_req.new_value or 99999
    success = memory.tamper_decision(decision_id, field, new_value)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid tamper field or value")

    # Re‑fetch the updated entry after tampering
    stored_entry = memory.get_decision(decision_id)

    stored_receipt = memory.get_receipt_by_decision(decision_id)
    if not stored_receipt:
        return TamperResponse(
            decision_id=decision_id,
            tamper_detected=False,
            details="No receipt to verify; tamper not detectable"
        )

    # Reconstruct payload from the tampered data using canonical JSON
    try:
        stored_payload = {
            "decision_id": decision_id,
            "request": stored_entry["request"],
            "response": {
                "allowed": stored_entry["response"]["allowed"],
                "reason": stored_entry["response"]["reason"],
                "timestamp": stored_entry["response"]["timestamp"],
                "policy_version": stored_entry["response"].get("policy_version", "unknown")
            }
        }
        stored_payload_str = canonical_json(stored_payload)
        stored_payload_bytes = stored_payload_str.encode('utf-8')

        valid = verify_signature(public_key, stored_payload_bytes, stored_receipt.signature_b64)
        data_match = (stored_payload_str == stored_receipt.signed_data_b64)

        if not valid or not data_match:
            tamper_detected = True
            details = "Tamper detected: signature or data mismatch"
        else:
            tamper_detected = False
            details = "No tamper detected (unexpected)"
    except Exception as e:
        tamper_detected = True
        details = f"Verification error: {str(e)}"

    memory.log_audit(
        action="tamper_simulation",
        details={
            "decision_id": decision_id,
            "field": field,
            "new_value": new_value,
            "detected": tamper_detected
        }
    )

    return TamperResponse(
        decision_id=decision_id,
        tamper_detected=tamper_detected,
        details=details
    )

@app.get("/audit", response_model=List[Dict])
async def get_audit_log(db: Session = Depends(get_db)):
    memory = DatabaseMemory(db)
    return memory.get_audit_log()

@app.get("/decisions", response_model=List[str])
async def list_decisions(db: Session = Depends(get_db)):
    memory = DatabaseMemory(db)
    return memory.list_decisions()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/policy/reload")
async def reload_policy():
    policy_engine.reload()
    return {"status": "reloaded", "version": policy_engine.version}