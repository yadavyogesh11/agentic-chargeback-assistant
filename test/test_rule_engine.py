from src.rule_engine import evaluate_case


test_cases = [
    {
        "reason_code": "FRAUD_CARD_NOT_PRESENT",
        "evidence": {
            "authentication_status": "AUTHENTICATED"
        },
        "expected": "CONTEST"
    },
    {
        "reason_code": "DUPLICATE_PROCESSING",
        "evidence": {
            "duplicate_status": "DUPLICATE_CONFIRMED"
        },
        "expected": "ACCEPT"
    },
    {
        "reason_code": "CREDIT_NOT_PROCESSED",
        "evidence": {
            "credit_status": "CREDIT_NOT_PROCESSED"
        },
        "expected": "ACCEPT"
    },
    {
        "reason_code": "NOT_AS_DESCRIBED",
        "evidence": {
            "description_status": "NOT_AS_DESCRIBED"
        },
        "expected": "ACCEPT"
    },
    {
        "reason_code": "CANCELLED_RECURRING",
        "evidence": {
            "cancellation_status": "CANCELLED_BEFORE_BILLING"
        },
        "expected": "ACCEPT"
    }
]

def test_all_reason_code_cases():
    for test in test_cases:

        case = {
            "case_id": f"TEST-{test['reason_code']}",
            "reason_code": test["reason_code"],
            "response_deadline": "2026-12-31",
            "evidence": [
                {
                    "type": evidence_type,
                    "content": "Synthetic evidence"
                }
                for evidence_type in []
            ]
        }

        investigation_results = {
            "transaction": {"transaction_id": "TEST-TXN"},
            "delivery": {},
            "merchant": {},
            "cancellation": {}
        }

        if test["reason_code"] == "FRAUD_CARD_NOT_PRESENT":
            investigation_results["transaction"] = test["evidence"]

        elif test["reason_code"] == "DUPLICATE_PROCESSING":
            investigation_results["transaction"] = test["evidence"]

        elif test["reason_code"] == "CREDIT_NOT_PROCESSED":
            investigation_results["transaction"] = test["evidence"]

        elif test["reason_code"] == "NOT_AS_DESCRIBED":
            investigation_results["merchant"] = test["evidence"]

        elif test["reason_code"] == "CANCELLED_RECURRING":
            investigation_results["cancellation"] = test["evidence"]

        result = evaluate_case(case, investigation_results)

        status = "PASS" if result["decision"] == test["expected"] else "FAIL"

        print(
            f"{status} | "
            f"{test['reason_code']} | "
            f"Expected: {test['expected']} | "
            f"Actual: {result['decision']}"
        )