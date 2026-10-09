import json
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
AUDIT_DIR = BASE_DIR / "data" / "audit"


def log_audit(
    case_id,
    investigation_rounds,
    tools_called,
    events,
    final_response,
    stop_reason,
    metrics
):
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    audit_record = {
        "case_id": case_id,
        "timestamp": datetime.now().isoformat(),
        "investigation_rounds": investigation_rounds,
        "tools_called": tools_called,
        "events": events,
        "stop_reason": stop_reason,
        "final_response": final_response,
        "metrics": metrics
    }

    audit_file = AUDIT_DIR / f"{case_id}_audit.json"

    with open(audit_file, "w", encoding="utf-8") as f:
        json.dump(audit_record, f, indent=2)

    return audit_file