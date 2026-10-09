Agentic Chargeback Dispute Resolution Assistant

Overview

A Python and Streamlit application that helps analysts investigate synthetic chargeback disputes using an LLM-powered agent and deterministic business rules.

The agent dynamically selects mock investigation tools to gather evidence. The rule engine evaluates that evidence and recommends "ACCEPT", "CONTEST", or "REQUEST_MORE_INFO".

Key Features

- Intake of dispute information from text, PDF, and image files.
- Structured case extraction and validation.
- Dynamic investigation using five mock tools.
- Rule-based evaluation across six chargeback reason codes.
- Evidence-based decision rationale and contest-letter generation.
- Human review with approve, edit, and reject actions.
- PII masking and prompt-injection safeguards.
- JSON audit records and investigation performance metrics.
- Automated tests and a 25-case synthetic evaluation dataset.

Technology Stack

- Python
- Streamlit
- OpenAI API ("gpt-5-mini")
- Pytest
- JSON
- Tesseract OCR for image-based intake

Project Structure

agentic-chargeback-assistant/
├── app.py
├── src/
│   ├── agents.py
│   ├── audit_logger.py
│   ├── case_schema.json
│   ├── dynamic_investigation.py
│   ├── intake.py
│   ├── pii_masking.py
│   ├── response_letter.py
│   ├── rule_engine.py
│   ├── tools.py
│   ├── tools_definitions.py
│   └── validate_case.py
├── data/
│   ├── cases/
│   ├── mock/
│   └── audit/
├── evaluation/
├── test/
├── docs/
├── .gitignore
└── README.md

Architecture and Workflow

1. Intake: Extract case information from dispute text, PDFs, or images.
2. Validation: Check extracted fields for missing or invalid information.
3. PII masking: Mask supported sensitive-data patterns before relevant text is sent to the LLM.
4. Investigation: The agent selects and calls mock tools to retrieve transaction, customer, delivery, prior-dispute, and merchant information.
5. Rule evaluation: Python business rules evaluate the collected evidence, required fields, contradictions, and response deadlines.
6. Decision: Recommend "ACCEPT", "CONTEST", or "REQUEST_MORE_INFO".
7. Response drafting: Generate a contest letter when the decision qualifies.
8. Human review: Allow an analyst to approve, edit, or reject the recommendation when review is required.
9. Audit and monitoring: Record investigation activity and display API-call, token-usage, and latency metrics.

Supported Chargeback Reason Codes

Reason Code| Dispute Type
Fraud / Card Not Present| Unauthorized transaction
Item Not Received| Goods or services not delivered
Duplicate Processing| Duplicate charge
Credit Not Processed| Expected refund not received
Not as Described| Goods or services differ from their description
Cancelled Recurring| Payment processed after cancellation

The rule engine uses configured evidence requirements to evaluate each reason code. The LLM assists with extraction and investigation; deterministic Python logic handles the rule-based recommendation.

Installation and Setup

Prerequisites

- Python 3.10 or later
- An OpenAI API key
- Tesseract OCR for image intake
- Git, if cloning the repository

1. Clone the repository

git clone https://github.com/yadavyogesh11/agentic-chargeback-assistant.git
cd agentic-chargeback-assistant

2. Create a virtual environment

python -m venv .venv
.\.venv\Scripts\Activate.ps1

3. Install dependencies

pip install openai python-dotenv streamlit pytest pypdf pillow pytesseract

4. Configure the API key

Create a ".env" file in the project root:

OPENAI_API_KEY=your_openai_api_key

Configure the Tesseract executable path in "app.py" if necessary. Never commit ".env" or expose the API key.

5. Run the application

python -m streamlit run app.py

Open the local URL displayed by Streamlit.

Evaluation and Testing

The project includes 25 synthetic cases with expected outcomes covering the six reason codes and edge cases such as incomplete evidence, expired deadlines, contradictory evidence, and prompt-injection attempts.

Run the evaluation:

python -m evaluation.run_evaluation

Run the automated tests:

python -m pytest .\test\ -v

The tests cover PII masking, rule evaluation, tool definitions and execution, intake, prompt-injection handling, response-letter generation, and the OpenAI API connection.

The previously executed synthetic evaluation achieved 25/25 expected outcomes, and the complete pytest suite passed. These results apply to the defined test cases and do not guarantee equivalent performance on real disputes.

Human Review, Audit and Security

- Cases are flagged for human review when configured confidence or transaction-amount thresholds are met.
- Analyst actions and comments are saved in JSON review records.
- Audit records include investigation events, tool-call information, the final response, and performance metrics.
- PII masking covers supported patterns, including card numbers, emails, Indian mobile numbers, and explicitly labelled names and addresses.
- Intake and investigation prompts instruct the LLM to treat document contents as untrusted evidence rather than instructions.

Limitations

Investigation tools use mock data. PII masking is pattern-based and may miss information in free-form text. The confidence value is not a statistically calibrated probability, and audit logging alone does not guarantee exact investigation replay.