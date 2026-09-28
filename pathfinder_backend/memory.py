from sqlalchemy.orm import Session
# memory.py

from sqlalchemy.orm import Session
from database import DecisionRecord, AuditLog
from models import DecisionRequest, DecisionResponse, Receipt
from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime

class DatabaseMemory:
    def __init__(self, db: Session):
        self.db = db

    def store_decision(self, decision_id: str, request: DecisionRequest,
                       response: DecisionResponse, receipt: Optional[Receipt] = None):
        # Convert Pydantic models to JSON‑serializable dicts
        # mode='json' converts datetimes to ISO strings
        record = DecisionRecord(
            decision_id=decision_id,
            request_data=request.model_dump(mode='json'),
            response_data=response.model_dump(mode='json'),
            receipt_data=receipt.model_dump(mode='json') if receipt else None,
            policy_version=response.policy_version,
            timestamp=datetime.utcnow()
        )
        self.db.add(record)
        self.db.commit()

    # ... rest of your methods unchanged ...

    def get_decision(self, decision_id: str) -> Optional[Dict]:
        record = self.db.query(DecisionRecord).filter(DecisionRecord.decision_id == decision_id).first()
        if not record:
            return None
        return {
            "request": record.request_data,
            "response": record.response_data,
            "receipt": record.receipt_data,
            "policy_version": record.policy_version,
            "timestamp": record.timestamp
        }

    def get_receipt(self, receipt_id: str) -> Optional[Receipt]:
        # For SQLite, we query all and filter (simple for demo)
        records = self.db.query(DecisionRecord).all()
        for rec in records:
            if rec.receipt_data and rec.receipt_data.get("receipt_id") == receipt_id:
                return Receipt(**rec.receipt_data)
        return None

    def get_receipt_by_decision(self, decision_id: str) -> Optional[Receipt]:
        record = self.db.query(DecisionRecord).filter(DecisionRecord.decision_id == decision_id).first()
        if not record or not record.receipt_data:
            return None
        return Receipt(**record.receipt_data)

    def log_audit(self, action: str, details: Dict):
        entry = AuditLog(
            action=action,
            details=details,
            timestamp=datetime.utcnow()
        )
        self.db.add(entry)
        self.db.commit()

    def list_decisions(self) -> List[str]:
        records = self.db.query(DecisionRecord.decision_id).all()
        return [r[0] for r in records]

    def get_audit_log(self) -> List[Dict]:
        logs = self.db.query(AuditLog).order_by(AuditLog.timestamp).all()
        return [{"action": l.action, "timestamp": l.timestamp.isoformat(), "details": l.details} for l in logs]

    def tamper_decision(self, decision_id: str, field: str, new_value: Any) -> bool:
        record = self.db.query(DecisionRecord).filter(DecisionRecord.decision_id == decision_id).first()
        if not record:
            return False
        request = record.request_data
        if field.startswith("decision_data."):
            key = field.split(".", 1)[1]
            request["decision_data"][key] = new_value
        elif field in request:
            request[field] = new_value
        else:
            if field in record.response_data:
                record.response_data[field] = new_value
            else:
                return False
        record.request_data = request
        self.db.commit()
        return True