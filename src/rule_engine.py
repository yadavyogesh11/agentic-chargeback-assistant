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


def normalize_evidence_name(value):
    """
    Convert evidence names into one consistent format.

    Example:
        "delivery proof" -> "delivery_proof"
        "delivery_proof" -> "delivery_proof"
    """

    return str(value).strip().lower().replace(" ", "_")


def load_case():
    """
    Load the synthetic chargeback case from JSON.
    """

    with open(CASE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def check_required_evidence(case):
    """
    Check whether the case itself contains the evidence required
    for its reason code.
    """

    reason_code = case.get("reason_code")

    required = REQUIRED_EVIDENCE.get(reason_code, [])

    evidence = case.get("evidence", [])

    evidence_types = set()

    if isinstance(evidence, list):

        for evidence_item in evidence:

            if isinstance(evidence_item, dict):

                evidence_type = evidence_item.get("type")

                if evidence_type:
                    evidence_types.add(
                        normalize_evidence_name(evidence_type)
                    )

    elif isinstance(evidence, dict):

        for evidence_type, value in evidence.items():

            if value:
                evidence_types.add(
                    normalize_evidence_name(evidence_type)
                )

    required_normalized = [
        normalize_evidence_name(item)
        for item in required
    ]

    missing = [
        item
        for item in required_normalized
        if item not in evidence_types
    ]

    return {
        "required": required_normalized,
        "available": sorted(evidence_types),
        "missing": missing,
        "complete": len(missing) == 0
    }


def check_deadline(case):
    """
    Check whether the response deadline exists,
    has a valid date format, and has expired.
    """

    deadline = case.get("response_deadline")

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


def evaluate_case(case, investigation_results=None):
    """
    Apply deterministic business rules.

    The rule engine does not use an LLM.

    It checks:
    1. Required evidence
    2. Investigation evidence
    3. Deadline validity
    4. Contradictory evidence
    5. Reason-code-specific decision rules
    """

    if investigation_results is None:
        investigation_results = {}

    evidence_result = check_required_evidence(case)
    deadline_result = check_deadline(case)

    # ---------------------------------------------------------
    # Evidence collected during investigation
    # ---------------------------------------------------------

    investigated_evidence = set()

    transaction = investigation_results.get("transaction", {})
    delivery = investigation_results.get("delivery", {})
    merchant = investigation_results.get("merchant", {})

    # Different parts of the project may call this
    # customer_history or cancellation.
    customer_history = investigation_results.get(
        "customer_history",
        {}
    )

    cancellation = investigation_results.get(
        "cancellation",
        {}
    )

    if transaction:
        investigated_evidence.add("transaction_record")

    if delivery:
        investigated_evidence.add("delivery_proof")

    if transaction.get("authentication_status"):
        investigated_evidence.add("authentication_evidence")

    if transaction.get("duplicate_status"):
        investigated_evidence.add(
            "duplicate_transaction_evidence"
        )

    if transaction.get("credit_status"):
        investigated_evidence.add("credit_evidence")

    if merchant.get("description_status"):
        investigated_evidence.add("merchant_evidence")

    if cancellation.get("cancellation_status"):
        investigated_evidence.add("cancellation_evidence")

    if customer_history.get("cancellation_status"):
        investigated_evidence.add("cancellation_evidence")

    # ---------------------------------------------------------
    # Combine case evidence + investigation evidence
    # ---------------------------------------------------------

    available_evidence = set(
        evidence_result.get("available", [])
    )

    available_evidence.update(
        investigated_evidence
    )

    # Normalize everything before comparison.
    available_evidence = {
        normalize_evidence_name(item)
        for item in available_evidence
    }

    required_evidence = [
        normalize_evidence_name(item)
        for item in evidence_result.get("required", [])
    ]

    missing_evidence = [
        item
        for item in required_evidence
        if item not in available_evidence
    ]

    evidence_result["available"] = sorted(
        available_evidence
    )

    evidence_result["missing"] = missing_evidence

    evidence_result["complete"] = (
        len(missing_evidence) == 0
    )

    # ---------------------------------------------------------
    # Check contradictory evidence
    # ---------------------------------------------------------

    contradictory_evidence = []

    investigated_credit_status = transaction.get(
        "credit_status"
    )

    case_credit_processed = False
    case_credit_not_processed = False

    for evidence in case.get("evidence", []):

        if not isinstance(evidence, dict):
            continue

        evidence_type = normalize_evidence_name(
            evidence.get("type", "")
        )

        content = str(
            evidence.get("content", "")
        ).lower()

        if evidence_type == "credit_evidence":

            if "credit evidence was processed" in content:
                case_credit_processed = True

        if evidence_type == "dispute_notice":

            if "credit was not processed" in content:
                case_credit_not_processed = True

    if (
        case_credit_processed
        and case_credit_not_processed
    ):
        contradictory_evidence.append(
            "The case contains conflicting credit evidence."
        )

    if (
        case_credit_not_processed
        and investigated_credit_status == "CREDIT_PROCESSED"
    ):
        contradictory_evidence.append(
            "The dispute notice conflicts with "
            "investigation transaction credit status."
        )

    # ---------------------------------------------------------
    # Prepare investigation data
    # ---------------------------------------------------------

    authentication = transaction
    duplicate_transaction = transaction
    credit = transaction

    review_required = False

    # ---------------------------------------------------------
    # Rule 1: Missing evidence
    # ---------------------------------------------------------

    if not evidence_result["complete"]:

        decision = "REQUEST_MORE_INFO"

        reason = (
            "Required evidence is missing."
        )

    # ---------------------------------------------------------
    # Rule 2: Invalid / expired deadline
    # ---------------------------------------------------------

    elif not deadline_result.get("valid", False):

        decision = "REQUEST_MORE_INFO"

        reason = (
            "Response deadline is missing, "
            "invalid, or expired."
        )

        review_required = True

    # ---------------------------------------------------------
    # Rule 3: Contradictory evidence
    # ---------------------------------------------------------

    elif contradictory_evidence:

        decision = "REQUEST_MORE_INFO"

        reason = (
            "The case contains contradictory "
            "evidence that requires analyst review."
        )

        review_required = True

    # ---------------------------------------------------------
    # Rule 4: Reason-code-specific deterministic rules
    # ---------------------------------------------------------

    else:

        reason_code = case.get("reason_code")

        # -----------------------------------------------------
        # ITEM NOT RECEIVED
        # -----------------------------------------------------

        if reason_code == "ITEM_NOT_RECEIVED":

            delivery_status = str(
                delivery.get("delivery_status", "")
            ).upper().replace("-", "_")

            if delivery_status == "DELIVERED":

                decision = "CONTEST"

                reason = (
                    "Delivery evidence confirms that "
                    "the disputed item was delivered."
                )

            elif delivery_status == "NOT_DELIVERED":

                decision = "ACCEPT"

                reason = (
                    "Delivery evidence confirms that "
                    "the disputed item was not delivered."
                )

            else:

                decision = "REQUEST_MORE_INFO"

                reason = (
                    "The delivery evidence is "
                    "inconclusive."
                )

        # -----------------------------------------------------
        # FRAUD / CARD NOT PRESENT
        # -----------------------------------------------------

        elif reason_code == "FRAUD_CARD_NOT_PRESENT":

            authentication_status = (
                authentication.get(
                    "authentication_status"
                )
            )

            if authentication_status == "AUTHENTICATED":

                decision = "CONTEST"

                reason = (
                    "Authentication evidence confirms "
                    "that the transaction was authenticated."
                )

            elif authentication_status == "NOT_AUTHENTICATED":

                decision = "ACCEPT"

                reason = (
                    "Authentication evidence does not "
                    "support the merchant's position."
                )

            else:

                decision = "REQUEST_MORE_INFO"

                reason = (
                    "Authentication evidence is "
                    "missing or inconclusive."
                )

        # -----------------------------------------------------
        # DUPLICATE PROCESSING
        # -----------------------------------------------------

        elif reason_code == "DUPLICATE_PROCESSING":

            duplicate_status = (
                duplicate_transaction.get(
                    "duplicate_status"
                )
            )

            if duplicate_status == "DUPLICATE_CONFIRMED":

                decision = "ACCEPT"

                reason = (
                    "Investigation confirms that the "
                    "transaction was processed more than once."
                )

            elif duplicate_status == "NO_DUPLICATE":

                decision = "CONTEST"

                reason = (
                    "Investigation confirms that no "
                    "duplicate transaction was identified."
                )

            else:

                decision = "REQUEST_MORE_INFO"

                reason = (
                    "Duplicate transaction evidence "
                    "is missing or inconclusive."
                )

        # -----------------------------------------------------
        # CREDIT NOT PROCESSED
        # -----------------------------------------------------

        elif reason_code == "CREDIT_NOT_PROCESSED":

            credit_status = credit.get(
                "credit_status"
            )

            if credit_status == "CREDIT_PROCESSED":

                decision = "CONTEST"

                reason = (
                    "Investigation confirms that the "
                    "requested credit was processed."
                )

            elif credit_status == "CREDIT_NOT_PROCESSED":

                decision = "ACCEPT"

                reason = (
                    "Investigation confirms that the "
                    "requested credit was not processed."
                )

            else:

                decision = "REQUEST_MORE_INFO"

                reason = (
                    "Credit processing evidence is "
                    "missing or inconclusive."
                )

        # -----------------------------------------------------
        # NOT AS DESCRIBED
        # -----------------------------------------------------

        elif reason_code == "NOT_AS_DESCRIBED":

            merchant_status = merchant.get(
                "description_status"
            )

            if merchant_status == "AS_DESCRIBED":

                decision = "CONTEST"

                reason = (
                    "Merchant evidence confirms that "
                    "the goods or services matched the description."
                )

            elif merchant_status == "NOT_AS_DESCRIBED":

                decision = "ACCEPT"

                reason = (
                    "Merchant evidence confirms that "
                    "the goods or services did not match "
                    "the description."
                )

            else:

                decision = "REQUEST_MORE_INFO"

                reason = (
                    "Merchant evidence is "
                    "missing or inconclusive."
                )

        # -----------------------------------------------------
        # CANCELLED RECURRING
        # -----------------------------------------------------

        elif reason_code == "CANCELLED_RECURRING":

            cancellation_status = (
                cancellation.get(
                    "cancellation_status"
                )
                or customer_history.get(
                    "cancellation_status"
                )
            )

            if (
                cancellation_status
                == "CANCELLED_BEFORE_BILLING"
            ):

                decision = "ACCEPT"

                reason = (
                    "Investigation confirms that the "
                    "recurring payment was cancelled "
                    "before billing."
                )

            elif cancellation_status == "NOT_CANCELLED":

                decision = "CONTEST"

                reason = (
                    "Investigation confirms that the "
                    "recurring payment had not been "
                    "cancelled before the disputed billing."
                )

            else:

                decision = "REQUEST_MORE_INFO"

                reason = (
                    "Cancellation evidence is "
                    "missing or inconclusive."
                )

        # -----------------------------------------------------
        # Unknown reason code
        # -----------------------------------------------------

        else:

            decision = "REQUEST_MORE_INFO"

            reason = (
                "Decision logic for this reason code "
                "has not yet been implemented."
            )

    # ---------------------------------------------------------
    # Final result
    # ---------------------------------------------------------

    return {
        "case_id": case.get("case_id"),
        "reason_code": case.get("reason_code"),
        "decision": decision,
        "reason": reason,
        "evidence_check": evidence_result,
        "deadline_check": deadline_result,
        "review_required": review_required
    }


def main():

    print("===================================")
    print("CHARGEBACK RULE ENGINE")
    print("===================================")

    try:

        case = load_case()

        print(
            f"Case ID: {case.get('case_id')}"
        )

        print(
            f"Reason Code: {case.get('reason_code')}"
        )

        print()

        result = evaluate_case(
            case,
            {}
        )

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

        print(
            f"Decision: {result['decision']}"
        )

        print(
            f"Reason: {result['reason']}"
        )

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