
import re


def mask_pii(text):
    """
    Mask common personally identifiable information (PII)
    before sending text to an LLM.
    """

    # Mask card numbers
    text = re.sub(
        r"\b(?:\d[ -]?){13,19}\b",
        "[CARD_NUMBER]",
        text
    )

    # Mask email addresses
    text = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "[EMAIL]",
        text
    )

    # Mask Indian mobile numbers
    text = re.sub(
        r"\b(?:\+91[- ]?)?[6-9]\d{9}\b",
        "[PHONE]",
        text
    )

    # Mask names when explicitly labelled
    text = re.sub(
        r"(?im)^(\s*(?:Customer Name|Cardholder Name|Name)\s*:\s*)[^\r\n]+",
        r"\1[PERSON_NAME]",
        text
    )

    # Mask addresses when explicitly labelled
    text = re.sub(
        r"(?im)^(\s*(?:Customer Address|Billing Address|Shipping Address|Address)\s*:\s*)[^\r\n]+",
        r"\1[ADDRESS]",
        text
    )

    return text


if __name__ == "__main__":

    test_text = """
    Customer Name: Rahul Sharma
    Email: rahul.sharma@gmail.com
    Phone: 9876543210
    Card: 4111 1111 1111 1111
    Address: 25 MG Road, Mumbai
    """

    print("=== ORIGINAL ===")
    print(test_text)

    masked_text = mask_pii(test_text)

    print("=== MASKED ===")
    print(masked_text)
