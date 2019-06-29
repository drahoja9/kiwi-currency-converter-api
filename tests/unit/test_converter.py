from decimal import Decimal

from _pytest.monkeypatch import MonkeyPatch
from flask import Flask

from api.currencies import CurrencyResource
from api.converter import CurrencyConverter


# ----------------------------------------------------- Tests ---------------------------------------------------------


def test_convert(test_app: Flask, monkeypatch: MonkeyPatch):
    monkeypatch.setattr(CurrencyResource, 'get_currency_rates', lambda _i, _o: {
        'USD': Decimal(1.1),
        'GBP': Decimal(0.896032),
        'CZK': Decimal(25.4183),
    })
    result = CurrencyConverter.convert(2.2, 'EUR', ['USD', 'GBP', 'CZK'])
    assert result == {
        'USD': 2.42,
        'GBP': 1.97,
        'CZK': 55.92
    }


def test_rounding(test_app: Flask, monkeypatch: MonkeyPatch):
    monkeypatch.setattr(CurrencyResource, 'get_currency_rates', lambda _i, _o: {
        'USD': Decimal(1.19963),
        'GBP': Decimal(3.463),
        'CZK': Decimal(0.001),
        'RUB': Decimal(0.005),
        'TRY': Decimal(0.00449),
        'UAH': Decimal(0.0044444444444444444444444444444444444444444444445),
        'CNY': Decimal(199999.999999999999999999)
    })
    result = CurrencyConverter.convert(1.0, 'EUR', ['USD', 'GBP', 'CZK', 'RUB', 'TRY', 'UAH'])
    assert result == {
        'USD': 1.20,
        'GBP': 3.46,
        'CZK': 0.00,
        'RUB': 0.01,
        'TRY': 0.00,
        'UAH': 0.00,
        'CNY': 200000.00
    }
