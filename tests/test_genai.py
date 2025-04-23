import pytest
from app.services.genai import generate_summary

@pytest.mark.parametrize(
    "data, expected_output",
    [
        ([{"symbol": "BTC", "change_percent_24h": 5.0, "average_price_7d": 48000.00}], "BTC had a 5.0% change in the last 24 hours, with a weekly average price of $48000.0."),
        ([{"symbol": "ETH", "change_percent_24h": 2.0, "average_price_7d": 3000.00}], "ETH had a 2.0% change in the last 24 hours, with a weekly average price of $3000.0."),
    ]
)
def test_generate_summary(data, expected_output):
    result = generate_summary(data)
    assert expected_output in result
