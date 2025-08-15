
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

app = FastAPI(title="TrustLens Demo API", version="0.1.0")

class AuditRequest(BaseModel):
    dataset_id: str
    model_id: Optional[str] = None
    attributes: List[str]

class AuditResponse(BaseModel):
    run_id: str
    metrics: Dict[str, Any]
    generated_at: str

@app.get("/health")
def health():
    return {"status":"ok","timestamp":datetime.utcnow().isoformat()}

@app.post("/audit", response_model=AuditResponse)
def audit(req: AuditRequest):
    metrics = {a: {"demographic_parity_ratio": 0.82, "disparate_impact": 0.78} for a in req.attributes}
    return {"run_id": "AUD-" + datetime.utcnow().strftime("%H%M%S"),
            "metrics": metrics,
            "generated_at": datetime.utcnow().isoformat()}
