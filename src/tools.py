import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
TRANSACTIONS_FILE = BASE_DIR / "data" / "mock" / "transactions.json"
CUSTOMER_HISTORY_FILE = BASE_DIR / "data" / "mock" / "customer_history.json"
DELIVERY_STATUS_FILE = BASE_DIR / "data" / "mock" / "delivery_status.json"
PRIOR_DISPUTE_FILE = BASE_DIR / "data" / "mock" / "prior_disputes.json"
MERCHANT_HISTORY_FILE = BASE_DIR / "data" / "mock" / "merchant_profile.json"


def get_transaction(transaction_id):
    with open(TRANSACTIONS_FILE, "r", encoding="utf-8") as f:
        transactions = json.load(f)
    for transaction in transactions:
        if transaction.get("transaction_id") == transaction_id:
            return {
                "success": True,
                "data": transaction
            }
    return {
        "success": False,
        "error": f"Transaction {transaction_id} was not found."
    }


def get_customer_history(customer_id):
    with open(CUSTOMER_HISTORY_FILE, "r", encoding="utf-8") as f:
        customer_history = json.load(f)
    for customer in customer_history:
        if customer.get("customer_id") == customer_id:
            return {
                "success": True,
                "data": customer
            }
    return {
        "success": False,
        "error": f"Customer history for {customer_id} was not found."
    }


def get_delivery_status(transaction_id):
    with open(DELIVERY_STATUS_FILE, "r", encoding="utf-8") as f:
        deliveries = json.load(f)
    for delivery in deliveries:
        if delivery.get("transaction_id") == transaction_id:
            return {
                "success": True,
                "data": delivery
            }
    return {
        "success": False,
        "error": f"Delivery status for {transaction_id} not found."
    }


def get_prior_disputes(customer_id):
    with open(PRIOR_DISPUTE_FILE, "r", encoding="utf-8") as f:
        disputes = json.load(f)
    for dispute in disputes:
        if dispute.get("customer_id") == customer_id:
            return {
                "success": True,
                "data": dispute
            }
    return {
        "success": False,
        "error": f"Prior disputes for {customer_id} not found."
    }


def get_merchant_profile(merchant_id):
    with open(MERCHANT_HISTORY_FILE, "r", encoding="utf-8") as f:
        merchants = json.load(f)
    for merchant in merchants:
        if merchant.get("merchant_id") == merchant_id:
            return {
                "success": True,
                "data": merchant
            }
    return {
        "success": False,
        "error": f"Merchant profile for {merchant_id} not found."
    }

if __name__ == "__main__":

    print(" === MOCK TOOLS TEST ===")
    transaction_result = get_transaction("TXN-10001")
    customer_result = get_customer_history("CUST-001")
    delivery_result = get_delivery_status("TXN-10001")
    prior_dispute_result = get_prior_disputes("CUST-001")
    merchant_profile_result = get_merchant_profile("MER-001")

    print("=== TRANSACTION RESULT ===")
    print(json.dumps(transaction_result, indent=2))

    print("=== CUSTOMER RESULT ===")
    print(json.dumps(customer_result, indent=2))

    print("=== DELIVERY STATUS ===")
    print(json.dumps(delivery_result, indent=2))

    print("=== PRIOR DISPUTES ===")
    print(json.dumps(prior_dispute_result, indent=2))

    print("=== MERCHANT PROFILE ===")
    print(json.dumps(merchant_profile_result, indent=2))
