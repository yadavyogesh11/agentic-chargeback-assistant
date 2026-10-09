
from src.intake import extract_case_from_text


def test_extract_case_from_text():
    """Verify that intake extracts key fields from dispute notice text."""

    sample_text = """
    Chargeback dispute notice.

    Transaction ID: TXN-10001
    Customer ID: CUST-001
    Merchant ID: MER-001
    Amount: INR 12500
    Transaction Date: 2026-09-10

    The customer claims that the item was not received.

    Response deadline: 2026-10-15.
    """

    result = extract_case_from_text(sample_text)

    assert isinstance(result, dict)
    assert result.get("transaction_id") == "TXN-10001"
    assert result.get("customer_id") == "CUST-001"
    assert result.get("merchant_id") == "MER-001"
    assert result.get("reason_code") == "ITEM_NOT_RECEIVED"
