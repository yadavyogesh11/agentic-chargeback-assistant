def generate_contest_letter(case, investigation_results, decision_result):
    """
    Generate a chargeback contest response using only
    case data and verified investigation evidence.
    """

    if decision_result.get("decision") != "CONTEST":
        return None

    transaction = investigation_results.get("transaction", {})
    delivery = investigation_results.get("delivery", {})

    case_id = case.get("case_id")
    transaction_id = case.get("transaction_id")
    amount = case.get("amount")
    currency = case.get("currency")
    transaction_date = case.get("transaction_date")
    delivery_status = delivery.get("delivery_status")

    letter = f"""
Subject: Chargeback Dispute Response - {case_id}

Dear Dispute Review Team,

We are contesting the chargeback associated with transaction {transaction_id}.

Transaction Details:
- Transaction Amount: {currency} {amount}
- Transaction Date: {transaction_date}
- Delivery Status: {delivery_status}

Investigation Findings:

The transaction was verified during the investigation. The delivery
evidence indicates that the disputed item was delivered.

Based on the available transaction and delivery evidence, we request
that the chargeback be rejected.

Regards,
Chargeback Dispute Team
"""

    return letter.strip()