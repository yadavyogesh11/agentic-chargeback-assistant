import json
from pathlib import Path

from src.rule_engine import evaluate_case
from src.tools import (
    get_transaction,
    get_customer_history,
    get_delivery_status,
    get_prior_disputes,
    get_merchant_profile
)


BASE_DIR = Path(__file__).resolve().parent.parent
CASE_DIR = BASE_DIR / "data" / "cases"
EXPECTED_FILE = BASE_DIR / "evaluation" / "expected_results.json"


def load_expected_results():
    """
    Load expected decisions for all evaluation cases.
    """

    with open(EXPECTED_FILE, "r", encoding="utf-8") as f:
        results = json.load(f)

    return {
        item["case_id"]: item
        for item in results
    }


def load_case(case_id):
    """
    Load one synthetic case from data/cases.
    """

    case_file = CASE_DIR / f"{case_id}.json"

    with open(case_file, "r", encoding="utf-8") as f:
        return json.load(f)


def build_investigation_results(case):
    """
    Build investigation results using the same mock tools
    used by the chargeback assistant.

    The evaluator supports both case formats:

    Format 1:
        "transaction_id": "TXN-10001"

    Format 2:
        "transaction": {
            "transaction_id": "TXN-10001"
        }
    """

    investigation = {}

    # ---------------------------------------------------------
    # 1. Find transaction ID
    # ---------------------------------------------------------

    transaction_id = case.get("transaction_id")

    # Support older case structure
    if not transaction_id:

        transaction = case.get("transaction", {})

        if isinstance(transaction, dict):
            transaction_id = transaction.get("transaction_id")

    # If there is no transaction ID, we cannot investigate.
    if not transaction_id:
        return investigation

    # ---------------------------------------------------------
    # 2. Get transaction
    # ---------------------------------------------------------

    transaction_result = get_transaction(transaction_id)

    if not transaction_result.get("success"):
        return investigation

    transaction_data = transaction_result.get("data", {})

    if not transaction_data:
        return investigation

    investigation["transaction"] = transaction_data

    # IDs needed for other investigations
    customer_id = transaction_data.get("customer_id")
    merchant_id = transaction_data.get("merchant_id")

    # ---------------------------------------------------------
    # 3. Get customer history
    # ---------------------------------------------------------

    if customer_id:

        customer_result = get_customer_history(customer_id)

        if customer_result.get("success"):

            customer_data = customer_result.get("data", {})

            investigation["customer_history"] = customer_data

            # Cancellation evidence comes from customer history
            investigation["cancellation"] = customer_data

        # -----------------------------------------------------
        # 4. Get prior disputes
        # -----------------------------------------------------

        prior_result = get_prior_disputes(customer_id)

        if prior_result.get("success"):

            investigation["prior_disputes"] = (
                prior_result.get("data", {})
            )

    # ---------------------------------------------------------
    # 5. Get delivery status
    # ---------------------------------------------------------

    delivery_result = get_delivery_status(transaction_id)

    if delivery_result.get("success"):

        investigation["delivery"] = (
            delivery_result.get("data", {})
        )

    # ---------------------------------------------------------
    # 6. Get merchant profile
    # ---------------------------------------------------------

    if merchant_id:

        merchant_result = get_merchant_profile(merchant_id)

        if merchant_result.get("success"):

            investigation["merchant"] = (
                merchant_result.get("data", {})
            )

    return investigation


def evaluate_single_case(case_id, expected):
    """
    Run one case through investigation + deterministic rules.
    """

    case = load_case(case_id)

    investigation_results = build_investigation_results(case)

    actual = evaluate_case(
        case,
        investigation_results
    )

    expected_decision = expected["expected_decision"]

    actual_decision = actual["decision"]

    passed = expected_decision == actual_decision

    return {
        "case_id": case_id,
        "expected": expected_decision,
        "actual": actual_decision,
        "passed": passed,
        "reason": actual.get("reason"),
        "review_required": actual.get(
            "review_required",
            False
        )
    }


def main():

    expected_results = load_expected_results()

    total = 0
    passed = 0
    failed_cases = []

    print()
    print("==========================================")
    print("     CHARGEBACK ASSISTANT EVALUATION")
    print("==========================================")
    print()

    # ---------------------------------------------------------
    # Run every evaluation case
    # ---------------------------------------------------------

    for case_id, expected in expected_results.items():

        try:

            result = evaluate_single_case(
                case_id,
                expected
            )

            total += 1

            if result["passed"]:
                passed += 1
                status = "PASS"
            else:
                status = "FAIL"

                failed_cases.append(result)

            print(
                f"{status} | "
                f"{case_id} | "
                f"Expected: {result['expected']} | "
                f"Actual: {result['actual']}"
            )

        except Exception as e:

            total += 1

            failed_cases.append({
                "case_id": case_id,
                "expected": expected.get(
                    "expected_decision"
                ),
                "actual": "ERROR",
                "passed": False,
                "reason": str(e)
            })

            print(
                f"ERROR | "
                f"{case_id} | "
                f"{str(e)}"
            )

    # ---------------------------------------------------------
    # Calculate accuracy
    # ---------------------------------------------------------

    accuracy = (
        passed / total * 100
        if total
        else 0
    )

    print()
    print("------------------------------------------")
    print(f"Total cases : {total}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {total - passed}")
    print(f"Accuracy    : {accuracy:.2f}%")
    print("------------------------------------------")

    # ---------------------------------------------------------
    # Show failed cases with reasons
    # ---------------------------------------------------------

    if failed_cases:

        print()
        print("FAILED CASE DETAILS")
        print("------------------------------------------")

        for failure in failed_cases:

            print(
                f"\nCase: {failure['case_id']}"
            )

            print(
                f"Expected: "
                f"{failure.get('expected')}"
            )

            print(
                f"Actual:   "
                f"{failure.get('actual')}"
            )

            print(
                f"Reason:   "
                f"{failure.get('reason')}"
            )

            if failure.get("review_required") is not None:

                print(
                    f"Review required: "
                    f"{failure.get('review_required')}"
                )

    print()


if __name__ == "__main__":
    main()