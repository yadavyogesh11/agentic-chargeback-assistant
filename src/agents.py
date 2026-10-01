import json
from pathlib import Path

from tools import (
    get_transaction,
    get_customer_history,
    get_delivery_status,
    get_prior_disputes,
    get_merchant_profile
)

TOOLS_REGISTRY = {
    "get_transaction": get_transaction,
    "get_customer_history": get_customer_history,
    "get_delivery_status": get_delivery_status,
    "get_prior_disputes": get_prior_disputes,
    "get_merchant_profile": get_merchant_profile
}

BASE_DIR = Path(__file__).resolve().parent.parent
CASE_FILE = BASE_DIR / "data" / "cases" / "CASE-001.json"


def load_case():
    with open(CASE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


class ChargebackAgent:

    def __init__(self, case):
        self.case = case
        self.tools_called = []
        self.findings = []
        self.investigate_state = {
            "selected_tools": [],
            "completed_tools": [],
            "findings": []
        }


    def select_tools(self):
        reason_code = self.case.get("reason_code")

        if reason_code == "ITEM_NOT_RECEIVED":
            return [
                "get_transaction",
                "get_delivery_status",
            ]

        elif reason_code == "FRAUD_CARD_NOT_PRESENT":
              return [
                    "get_transaction",
                    "get_customer_history",
                    "get_prior_disputes"
              ]

        elif reason_code == "DUPLICATE_PROCESSING":
              return [
                    "get_transaction",
                    "get_prior_disputes"
              ]

        elif reason_code == "CREDIT_CARD_NOT_PROCESSED":
              return [
                    "get_transaction",
                    "get_prior_disputes"
              ]

        elif reason_code == "NOT_AS_DESCRIBED":
              return [
                    "get_transaction",
                    "get_merchant_profile"
              ]

        elif reason_code == "CANCELLED_RECURRING":
              return [
                    "get_transaction",
                    "get_customer_history",
                    "get_merchant_profile"
              ]

        return [
            "get_transaction"
        ]


    def execute_tool(self, tool_name):
 # when the tool name is out of bound (not in list)       
        if tool_name not in  TOOLS_REGISTRY:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' is not registered."
            }
        
        tool = TOOLS_REGISTRY[tool_name]

        if tool_name == "get_transaction":
            return tool(self.case["transaction"]["transaction_id"])

        elif tool_name == "get_delivery_status":
                    return tool(self.case["transaction"]["transaction_id"])

        elif tool_name == "get_customer_history":
                            return tool(self.case["customer"]["customer_id"])

        elif tool_name == "get_prior_disputes":
                            return tool(self.case["customer"]["customer_id"])

        elif tool_name == "get_merchant_profile":
                            return tool(self.case["merchant"]["merchant_id"])
        

    def is_investigation_complete(self):
        selected_tools = self.investigate_state["selected_tools"]
        completed_tools = self.investigate_state["completed_tools"]

        completed_tool_names = {item["tool"] for item in completed_tools}

        return all(
              tool in completed_tool_names
              for tool in selected_tools
        )


    def build_summary(self):
        summary = {}

        for finding in self.findings:
            if not finding.get("success"):
                continue

            data = finding.get("data", {})

            if "transaction_id" in data:
                summary["transaction"] = {
                    "transaction_id": data.get("transaction_id"),
                    "amount": data.get("amount"),
                    "status": data.get("status")
                }

            if "delivery_status" in data:
                summary["delivery"] = {
                    "status": data.get("delivery_status"),
                    "delivery_date": data.get("delivery_date"),
                    "carrier": data.get("carrier")
                }

            if "risk_level" in data:
                summary["customer"] = {
                    "risk_level": data.get("risk_level"),
                    "previous_disputes": data.get("previous_disputes")
                }

            if "disputes" in data:
                summary["prior_disputes"] = data.get("disputes")

            if "merchant_name" in data:
                summary["merchant"] = {
                    "merchant_name": data.get("merchant_name"),
                    "account_status": data.get("account_status"),
                    "chargeback_rate": data.get("chargeback_rate")
                }

        return summary

    def investigate(self):
        selected_tools = self.select_tools()
        self.investigate_state["selected_tools"] = selected_tools

        for tool_name in selected_tools:
            print("Running tool:", tool_name)

            result = self.execute_tool(tool_name)
            status = "success" if result.get("success") else "failed"

            self.tools_called.append(tool_name)
            self.findings.append(result)
            self.investigate_state["completed_tools"].append({
                    "tool": tool_name,
                    "status": status
                    })
            self.investigate_state["findings"].append(result)
            summary = self.build_summary()
            self.is_investigation_complete()

        return {
                "case-id": self.case.get("case_id"),
                "tools_called": self.tools_called,
                "findings": self.findings,
                "summary": summary,
                "investigate_state": self.investigate_state,
                "investigation_complete": self.is_investigation_complete()
            }

def main():
    case = load_case()
    agent = ChargebackAgent(case)
    result = agent.investigate()

    print("\n=== INVESTIGATION RESULT ===")
  #  print(reason_code := case.get("reason_code"))
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()