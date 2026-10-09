
from src.response_letter import generate_contest_letter


def test_generates_letter_for_contest_decision():
    """Verify that a contest decision produces a response letter."""

    case = {
        "case_id": "CASE-CONTEST-001",
        "transaction_id": "TXN-10001",
        "amount": 12500,
        "currency": "INR",
        "transaction_date": "2026-09-10"
    }

    investigation_results = {
        "transaction": {
            "transaction_id": "TXN-10001"
        },
        "delivery": {
            "delivery_status": "DELIVERED"
        }
    }

    decision_result = {"decision": "CONTEST"}

    letter = generate_contest_letter(
        case,
        investigation_results,
        decision_result
    )

    assert isinstance(letter, str)
    assert len(letter.strip()) > 0
    assert "TXN-10001" in letter


def test_does_not_generate_letter_for_non_contest_decision():
    """Verify that non-contest decisions do not produce a contest letter."""

    case = {
        "case_id": "CASE-ACCEPT-001",
        "transaction_id": "TXN-10001",
        "amount": 12500,
        "currency": "INR",
        "transaction_date": "2026-09-10"
    }

    investigation_results = {
        "transaction": {"transaction_id": "TXN-10001"},
        "delivery": {"delivery_status": "DELIVERED"}
    }

    decision_result = {"decision": "ACCEPT"}

    letter = generate_contest_letter(
        case,
        investigation_results,
        decision_result
    )

    assert letter is None or letter == ""
