import json
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent
CASE_FILE = BASE_DIR / "data" / "cases" / "CASE-001.json"


# Required evidence by reason code
REQUIRED_EVIDENCE = {
    "FRAUD_CARD_NOT_PRESENT": [
        "transaction_record",
        "authentication_evidence"
    ],

    "ITEM_NOT_RECEIVED": [
        "transaction_record",
        "delivery_proof"
    ],

    "DUPLICATE_PROCESSING": [
        "transaction_record",
        "duplicate_transaction_evidence"
    ],

    "CREDIT_NOT_PROCESSED": [
        "transaction_record",
        "credit_evidence"
    ],

    "NOT_AS_DESCRIBED": [
        "transaction_record",
        "merchant_evidence"
    ],

    "CANCELLED_RECURRING": [
        "transaction_record",
        "cancellation_evidence"
    ]
}


def load_case():
    """
    Load the synthetic chargeback case from JSON.
    """

    with open(CASE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def check_required_evidence(case):
    """
    Check whether all evidence required for the reason code exists.

    Evidence is expected to be stored as a list of objects:

    {
        "evidence_id": "EVD-001",
        "type": "invoice",
        "source": "...",
        "content": "..."
    }
    """

    reason_code = case.get("reason_code")

    required = REQUIRED_EVIDENCE.get(reason_code, [])

    evidence = case.get("evidence", [])

    # Extract the actual evidence types from the case.
    evidence_types = set()

    if isinstance(evidence, list):

        for evidence_item in evidence:

            if isinstance(evidence_item, dict):

                evidence_type = evidence_item.get("type")

                if evidence_type:
                    evidence_types.add(
                        evidence_type.lower().strip()
                    )

    elif isinstance(evidence, dict):

        # Support dictionary-based evidence as well.
        for evidence_type, value in evidence.items():

            if value:
                evidence_types.add(
                    evidence_type.lower().strip()
                )

    missing = []

    for required_item in required:

        if required_item.lower() not in evidence_types:
            missing.append(required_item)

    return {
        "required": required,
        "available": sorted(evidence_types),
        "missing": missing,
        "complete": len(missing) == 0
    }


def check_deadline(case):
    """
    Check whether the response deadline exists,
    has a valid date format, and has expired.
    """

    dispute = case.get("dispute", {})

    deadline = dispute.get("response_deadline")

    if not deadline:

        return {
            "valid": False,
            "deadline": None,
            "expired": None,
            "reason": "Response deadline is missing."
        }

    try:

        deadline_date = datetime.fromisoformat(
            deadline.replace("Z", "+00:00")
        )

        # Handle dates such as 2026-10-05 which do not contain timezone info.
        if deadline_date.tzinfo is None:
            now = datetime.now()
        else:
            now = datetime.now(deadline_date.tzinfo)

        expired = deadline_date < now

        return {
            "valid": not expired,
            "deadline": deadline,
            "expired": expired
        }

    except ValueError as e:

        return {
            "valid": False,
            "deadline": deadline,
            "expired": None,
            "reason": f"Invalid deadline format: {e}"
        }


def evaluate_case(case):
    """
    Apply deterministic business rules.

    The rule engine does NOT use an LLM.
    It only checks evidence completeness and deadline validity.

    Final Accept/Contest reasoning will be handled later
    by the investigation/LLM layer.
    """

    evidence_result = check_required_evidence(case)

    deadline_result = check_deadline(case)

    # Rule 1:
    # Missing required evidence means we cannot make a final decision.
    if not evidence_result["complete"]:

        decision = "REQUEST_MORE_INFO"

        reason = "Required evidence is missing."

    # Rule 2:
    # Expired or invalid deadline requires escalation.
    elif not deadline_result.get("valid", False):

        decision = "ESCALATE"

        reason = "Response deadline is missing, invalid, or expired."

    # Rule 3:
    # Evidence and deadline are valid.
    # The LLM/investigation layer will determine Accept vs Contest.
    else:

        decision = "REVIEW_REQUIRED"

        reason = (
            "Required evidence is present and the response deadline is valid. "
            "Further investigation is required before making the final decision."
        )

    return {
        "case_id": case.get("case_id"),
        "reason_code": case.get("reason_code"),
        "decision": decision,
        "reason": reason,
        "evidence_check": evidence_result,
        "deadline_check": deadline_result
    }


def main():

    print("===================================")
    print("CHARGEBACK RULE ENGINE")
    print("===================================")

    try:

        case = load_case()

        print(f"Case ID: {case.get('case_id')}")
        print(f"Reason Code: {case.get('reason_code')}")
        print()

        result = evaluate_case(case)

        print("=== EVIDENCE CHECK ===")

        print(
            json.dumps(
                result["evidence_check"],
                indent=2
            )
        )

        print()

        print("=== DEADLINE CHECK ===")

        print(
            json.dumps(
                result["deadline_check"],
                indent=2
            )
        )

        print()

        print("=== DECISION ===")

        print(f"Decision: {result['decision']}")
        print(f"Reason: {result['reason']}")

        print()

        print("=== COMPLETE RESULT ===")

        print(
            json.dumps(
                result,
                indent=2
            )
        )

    except Exception as e:

        print("RULE ENGINE ERROR")
        print(str(e))


if __name__ == "__main__":
    main()