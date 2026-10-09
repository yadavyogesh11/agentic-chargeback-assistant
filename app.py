import streamlit as st
import json
from pathlib import Path
from pypdf import PdfReader
import base64

from src.dynamic_investigation import run_investigation
from src.intake import extract_case_from_text

from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="Chargeback Dispute Resolution Assistant",
    layout="wide"
)

# ---------------------------------------------------------
# LOAD CASES
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
CASE_DIR = BASE_DIR / "data" / "cases"


def load_cases():
    cases = []
    for case_file in sorted(CASE_DIR.glob("*.json")):
        with open(case_file, "r", encoding="utf-8") as f:
            case = json.load(f)
        cases.append(case)

    return cases

cases = load_cases()


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("Agentic Chargeback Dispute Resolution Assistant")

st.write(
    "Investigate chargeback disputes, evaluate evidence, "
    "and generate a recommended resolution."
)

# ---------------------------------------------------------
# DISPUTE INTAKE
# ---------------------------------------------------------

st.header("Dispute Intake")

st.write("You can either paste the dispute notice/email or upload a PDF/image")

uploaded_file = st.file_uploader(
    "Upload dispute document",
    type = ["pdf","png","jpg","jpeg"],
    help = "Upload a PDF or image of the chargeback dispute notice."
)

intake_text = st.text_area(
    "Paste dispute notice or email",
    height=200,
    placeholder="Paste the chargeback dispute notice or email here..."
)

if st.button("Extract Case Information"):
    try:
        extracted_text = intake_text.strip()

        # If a PDF was uploaded, extract its text first.
        if uploaded_file is not None:
            if uploaded_file.name.lower().endswith(".pdf"):
                reader = PdfReader(uploaded_file)
                pdf_text = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        pdf_text += page_text + "\n"

                extracted_text = pdf_text.strip()

            elif uploaded_file.name.lower().endswith(
            (".png", ".jpg", ".jpeg")
    ):

                image = Image.open(uploaded_file)

                # Improve Quality of image before OCR
                image = image.convert("L")
                image = image.resize((image.width*2,image.height*2))
                image_text = pytesseract.image_to_string(image,config="--psm 6")
                extracted_text = image_text.strip()

        if not extracted_text:
            st.warning(
                "Please enter dispute text or upload a PDF/image."
            )

        else:
            with st.spinner("Extracting case information..."):

                # Send the extracted text to the existing intake function
                extracted_case = extract_case_from_text(
                    extracted_text
                )

                st.session_state["extracted_case"] = extracted_case

                # ---------------------------------------------------------
                # MATCH EXTRACTED TRANSACTION TO MOCK CASE
                # ---------------------------------------------------------

                transaction_id = extracted_case.get(
                    "transaction_id"
                )

                matched_case_id = None

                if transaction_id:
                    for case in cases:

                        case_transaction = case.get(
                            "transaction",
                            {}
                        )

                        case_transaction_id = (
                            case_transaction.get(
                                "transaction_id",
                                case.get("transaction_id")
                            )
                        )

                        if case_transaction_id == transaction_id:
                            matched_case_id = case.get(
                                "case_id"
                            )
                            break

                if matched_case_id:
                    st.session_state["matched_case_id"] = (
                        matched_case_id
                    )

                    st.success(
                        f"Intake matched to {matched_case_id}"
                    )

                else:
                    st.session_state["matched_case_id"] = None

                    st.info(
                        "Case information was extracted, "
                        "but no matching mock case was found."
                    )

    except Exception as e:
        st.error(f"Extraction Failed: {e}")


# ---------------------------------------------------------
# DISPLAY EXTRACTED CASE
# ---------------------------------------------------------

extracted_case = st.session_state.get("extracted_case")

if isinstance(extracted_case, dict):
    st.subheader("Extracted Case Information")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("**Transaction ID**")

        st.write(
            extracted_case.get(
                "transaction_id",
                "N/A"
            )
        )
    with col2:
        st.write("**Amount**")
        st.write(
            f"{extracted_case.get('currency', '')} "
            f"{extracted_case.get('amount', '')}"
        )

    with col3:
        st.write("**Reason Code**")
        st.write(
            extracted_case.get(
                "reason_code",
                "N/A"
            )
        )

    st.write(
        "**Merchant ID**",
        extracted_case.get(
            "merchant_id",
            "N/A"
        )
    )

    st.write(
        "**Transaction Date**",
        extracted_case.get(
            "transaction_date",
            "N/A"
        )
    )

    st.write(
        "**Response Deadline**",
        extracted_case.get(
            "response_deadline",
            "N/A"
        )
    )

# ---------------------------------------------------------
# MISSING FIELDS
# ---------------------------------------------------------

if isinstance(extracted_case, dict):
    missing_fields = extracted_case.get("missing_fields",[])
    if missing_fields:
        st.warning("Missing Information: "+ ", ".join(missing_fields))
    else:
        st.success("No missing fields detected")

    # ---------------------------------------------------------
    # CONFLICTS
    # ---------------------------------------------------------

    conflicts = extracted_case.get("conflicts",[])
    if conflicts:
        st.error("Conflicting information detected.")
        for conflict in conflicts:
            st.write(f"- {conflict}")


# ---------------------------------------------------------
# CASE SELECTION
# ---------------------------------------------------------

st.header("Case Investigation")
case_ids = [
    case.get(
        "case_id",
        "Unknown"
    )
    for case in cases
]


# ---------------------------------------------------------
# DETERMINE DEFAULT CASE
# ---------------------------------------------------------

matched_case_id = st.session_state.get(
    "matched_case_id"
)
if matched_case_id in case_ids:
    default_index = case_ids.index(
        matched_case_id
    )
else:
    default_index = 0
selected_case_id = st.selectbox(
    "Select a case",
    case_ids,
    index=default_index
)


# ---------------------------------------------------------
# SELECTED CASE
# ---------------------------------------------------------

selected_case = next(
    case
    for case in cases
    if case.get("case_id") == selected_case_id
)


transaction = selected_case.get(
    "transaction",
    {}
)

customer = selected_case.get(
    "customer",
    {}
)

merchant = selected_case.get(
    "merchant",
    {}
)


transaction_id = transaction.get(
    "transaction_id",
    selected_case.get(
        "transaction_id",
        "N/A"
    )
)


amount = transaction.get(
    "amount",
    selected_case.get(
        "amount",
        "N/A"
    )
)


currency = transaction.get(
    "currency",
    selected_case.get(
        "currency",
        "INR"
    )
)


customer_id = transaction.get(
    "customer_id",
    customer.get(
        "customer_id",
        selected_case.get(
            "customer_id",
            "N/A"
        )
    )
)


merchant_id = transaction.get(
    "merchant_id",
    merchant.get(
        "merchant_id",
        selected_case.get(
            "merchant_id",
            "N/A"
        )
    )
)


# ---------------------------------------------------------
# CASE DETAILS
# ---------------------------------------------------------

st.subheader("Case Details")
col1, col2, col3 = st.columns(3)
with col1:
    st.write("**Transaction ID**")
    st.write(transaction_id)
with col2:
    st.write("**Amount**")
    st.write(f"{currency} {amount}")
with col3:
    st.write("**Customer ID**")
    st.write(customer_id)
st.write(f"**Merchant ID:** {merchant_id}")
st.write(
    f"**Reason Code:** "
    f"{selected_case.get('reason_code', 'N/A')}"
)


# ---------------------------------------------------------
# INVESTIGATION BUTTON
# ---------------------------------------------------------

st.divider()
if st.button("Investigate Case",type="primary"):
    with st.spinner("Agent is investigating the chargeback..."):
        try:
            result = run_investigation(selected_case_id)
            st.subheader("Performance Metrics")
            metrics = result.get("metrics",{})

            col1,col2,col3 = st.columns(3)
            col1.metric("API Calls",metrics.get("api_calls",0))
            col2.metric("Total Tokens",metrics.get("total_tokens",0))
            col3.metric("Latency",
                        f"{metrics.get('latency_seconds',0):.2f}sec")

            with st.expander("Token Usage Details"):
                st.write("Input tokens:",metrics.get("input_tokens",0))
                st.write("Output tokens:",metrics.get("output_tokens",0))


            st.session_state["investigation_result"] = result
        except Exception as e:
            st.error(f"Investigation failed: {e}")

# ---------------------------------------------------------
# DISPLAY INVESTIGATION RESULT
# ---------------------------------------------------------

if "investigation_result" in st.session_state:
    result = st.session_state["investigation_result"]
    decision = result["decision"]
    st.divider()
    st.header("Investigation Result")

    # -----------------------------------------------------
    # SUMMARY METRICS
    # -----------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Decision",
            decision["decision"]
        )
    with col2:
        st.metric(
            "Confidence",
            f"{result['confidence']:.2f}"
        )
    with col3:
        st.metric(
            "Investigation Rounds",
            result["investigation_rounds"]
        )
    with col4:
        st.metric(
            "Human Review",
            "Required"
            if result["needs_human_review"]
            else "Not Required"
        )


    # -----------------------------------------------------
    # DECISION RATIONALE
    # -----------------------------------------------------

    st.subheader("Decision Rationale")
    st.write(decision.get("reason","No rationale available."))


    # -----------------------------------------------------
    # TOOLS USED
    # -----------------------------------------------------

    st.subheader("Tools Used")

    for tool in result["tools_called"]:
        st.write(f"✓ {tool}")


    # -----------------------------------------------------
    # INVESTIGATION SUMMARY
    # -----------------------------------------------------

    st.subheader("Agent Investigation Summary")
    st.write(result["model_response"])

    # -----------------------------------------------------
    # CONTEST LETTER
    # -----------------------------------------------------

    if result["contest_letter"]:
        st.subheader("Contest Letter")
        st.text_area(
            "Generated Response",
            result["contest_letter"],
            height=350
        )

    # -----------------------------------------------------
    # HUMAN-IN-THE-LOOP
    # -----------------------------------------------------

    if result["needs_human_review"]:
        st.divider()
        st.subheader("Human Review Required")
        st.warning(
            "This case requires analyst review "
            "before the recommended decision is finalized."
        )
        st.write(
            f"**Recommended Decision:** "
            f"{decision['decision']}"
        )
        st.write(
            f"**Confidence:** "
            f"{result['confidence']}"
        )
        st.write(
            "**Review Trigger:** "
            "Case amount exceeds the configured review "
            "limit or confidence is below threshold."
        )
        analyst_decision = st.radio(
            "Analyst Decision",
            ["Approve","Edit","Reject"],horizontal=True)
        final_decision = decision["decision"]

        if analyst_decision == "Edit":
            final_decision = st.selectbox("Revised Decision",
                                          ["ACCEPT","CONTEST","REQUEST_MORE_INFO"],
                                          index = ["ACCEPT","CONTEST","REQUEST_MORE_INFO"].index(
                                              decision["decision"]
                                          ) if decision["decision"] in [
                                              "ACCEPT","CONTEST","REQUEST_MORE_INFO"
                                          ] else 2
                                          )
        analyst_comments = st.text_area(
            "Analyst Comments",
            placeholder="Enter your review comments..."
        )
        if st.button("Submit Review",type="primary"):
            review_record = {
                "case_id": result["case_id"],
                "recommended_decision": decision["decision"],
                "final_decision": (final_decision
                                   if analyst_decision != "REJECT" else "REJECTED"),
                "confidence": result["confidence"],
                "analyst_decision": analyst_decision,
                "analyst_comments": analyst_comments
            }
            review_file = (
                Path(
                    result["audit_file"]
                ).parent
                / f"{result['case_id']}_human_review.json"
            )
            with open(
                review_file,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    review_record,
                    f,
                    indent=2
                )
            st.success(
                f"Review Submitted: "
                f"{analyst_decision}"
            )
            st.write(
                f"Review saved to "
                f"{review_file}"
            )


    # -----------------------------------------------------
    # AUDIT LOG
    # -----------------------------------------------------

    st.subheader("Audit Trail")
    st.write("Audit log saved to: "
        f"`{result['audit_file']}`"
    )