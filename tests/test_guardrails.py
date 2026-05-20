import pytest

from data_analyst_agent.guardrails import check_pii_columns


@pytest.mark.parametrize(
    ("columns", "expected"),
    [
        (["name", "email", "sales"], ["email"]),
        (["order_id", "Phone Number", "total"], ["Phone Number"]),
        (["product", "quantity", "region"], []),
    ],
)
def test_check_pii_columns_flags_sensitive_names(columns, expected):
    assert check_pii_columns(columns) == expected
