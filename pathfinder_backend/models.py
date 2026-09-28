from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from datetime import datetime

class DecisionRequest(BaseModel):
    decision_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    decision_data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None

class Receipt(BaseModel):
    receipt_id: str
    decision_id: str
    timestamp: datetime
    policy_version: str           # new field
    signed_data_b64: str
    signature_b64: str

class DecisionResponse(BaseModel):
    decision_id: str
    allowed: bool
    reason: str
    timestamp: datetime
    receipt: Optional[Receipt] = None
    policy_version: Optional[str] = None

# ... other models remain as before

class VerifyRequest(BaseModel):
    decision_id: str
    receipt: Receipt

class ReplayRequest(BaseModel):
    decision_id: str

class TamperRequest(BaseModel):
    decision_id: str
    # Optionally specify field to tamper with
    field: Optional[str] = None
    new_value: Optional[Any] = None

class TamperResponse(BaseModel):
    decision_id: str
    tamper_detected: bool
    details: str