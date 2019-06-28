from decimal import Decimal
from typing import List

import pytest
from _pytest.monkeypatch import MonkeyPatch
from flask import Flask

from api.currencies import CurrencyResource
from api.converter import CurrencyConverter

# ------------------------------------------------------ Mocks --------------------------------------------------------


@pytest.fixture
def mock_currency_resource(monkeypatch: MonkeyPatch):
    def mocked_get(input_currency: str, output_currencies: List[str]) -> dict:
        return {
            'USD': Decimal(1.1),
            'GBP': Decimal(0.896032),
            'CZK': Decimal(25.4183),
        }

    monkeypatch.setattr(CurrencyResource, 'get_currency_rates', mocked_get)


# ----------------------------------------------------- Tests ---------------------------------------------------------


def test_convert(test_app: Flask, mock_currency_resource):
    result = CurrencyConverter.convert(2.2, 'EUR', ['USD', 'GBP', 'CZK'])
    assert result == {
        'USD': 2.42,
        'GBP': 1.97,
        'CZK': 55.92
    }
