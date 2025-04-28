# tests/test_validators.py
import pytest
from app.utils.validators import validate_email_address

def test_validate_email_address_valid():
    valid_email = "test@gmail.com"  # ✅ instead of test@example.com
    assert validate_email_address(valid_email) is True

def test_validate_email_address_invalid():
    invalid_email = "invalid-email"
    assert validate_email_address(invalid_email) is False
