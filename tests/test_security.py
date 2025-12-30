import pytest

from src.utils.security import hash_password, verify_password


def test_hash_and_verify_short_password():
    p = "secret"
    h = hash_password(p)
    assert verify_password(p, h) is True


def test_hash_and_verify_long_password():
    p = "a" * 300
    h = hash_password(p)
    assert verify_password(p, h) is True
