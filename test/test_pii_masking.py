from src.pii_masking import mask_pii

def test_card_number_is_masked():
    text = "Card: 4111 1111 1111 1111"
    result = mask_pii(text)
    assert "[CARD_NUMBER]" in result
    assert "4111 1111 1111 1111" not in result


def test_email_is_masked():
    text = "Email: yogesh.yadav@gmail.com"
    result = mask_pii(text)
    assert "[EMAIL]" in result
    assert "yogesh.yadav@gmail.com" not in result


def test_phone_is_masked():
    text = "Phone: 9876543210"
    result = mask_pii(text)
    assert "[PHONE]" in result
    assert "9876543210" not in result

def test_customer_name_is_masked():
    text = "Customer Name: Rahul Sharma"
    result = mask_pii(text)
    assert "Rahul Sharma" not in result
    assert "[PERSON_NAME]" in result

def test_customer_address_is_masked():
    text = "Address: Mumbai"
    result = mask_pii(text)
    assert "Mumbai" not in result
    assert "[ADDRESS]" in result


if __name__ == "__main__":
    test_card_number_is_masked()
    test_email_is_masked()
    test_phone_is_masked()

    print("PII masking tests passed.")