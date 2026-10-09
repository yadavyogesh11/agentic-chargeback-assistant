TOOL_DEFINITIONS = [
    {
        "type": "function",
        "name": "get_transaction",
        "description": "Retrieve transaction details using a transaction ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "transaction_id": {
                    "type": "string",
                    "description": "The transaction ID to look up."
                }
            },
            "required": ["transaction_id"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "get_customer_history",
        "description": "Retrieve customer account history and risk information using a customer ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "The customer ID to look up."
                }
            },
            "required": ["customer_id"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "get_delivery_status",
        "description": "Retrieve delivery and shipment status using a transaction ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "transaction_id": {
                    "type": "string",
                    "description": "The transaction ID associated with the delivery."
                }
            },
            "required": ["transaction_id"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "get_prior_disputes",
        "description": "Retrieve previous chargeback disputes for a customer.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "The customer ID to look up."
                }
            },
            "required": ["customer_id"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "get_merchant_profile",
        "description": "Retrieve merchant profile and chargeback history using a merchant ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "merchant_id": {
                    "type": "string",
                    "description": "The merchant ID to look up."
                }
            },
            "required": ["merchant_id"],
            "additionalProperties": False
        }
    }
]


if __name__ == "__main__":
    print("Available LLM tools:")

    for tool in TOOL_DEFINITIONS:
        print(f"- {tool['name']}: {tool['description']}")