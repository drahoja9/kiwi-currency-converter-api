import logging
from typing import Type, List, Dict

import pytest
from _pytest.monkeypatch import MonkeyPatch
from flask.testing import FlaskClient

from api.converter import CurrencyConverter
from api.currencies import CurrencyResource
from api.exceptions import FixerApiException, CustomException, UnknownSymbolException, UnknownCurrencyException


# ------------------------------------------------------ Mocks --------------------------------------------------------


class MockedCurrencyConverter:
    amount = None
    input_currency = None
    output_currency = None

    @classmethod
    def convert(cls, amount: float, input_currency: str, output_currency: List[str]) -> Dict[str, float]:
        cls.amount = amount
        cls.input_currency = input_currency
        cls.output_currency = output_currency
        return {
            'OUTPUT_CURRENCY': 123.321
        }


@pytest.fixture
def mock_currency_resource(monkeypatch: MonkeyPatch):
    def mocked_get():
        return {
            'USD': 'United States Dollar',
            'CZK': 'Czech Crown',
            'GBP': 'Great Britain Pound'
        }

    monkeypatch.setattr(CurrencyResource, 'get_supported_currencies', mocked_get)


@pytest.fixture
def mock_currency_converter(monkeypatch: MonkeyPatch):
    monkeypatch.setattr(CurrencyConverter, 'convert', MockedCurrencyConverter.convert)


def mock_exception(monkeypatch: MonkeyPatch, exception_type: Type[CustomException]):
    class MockedException(exception_type):
        def __init__(self):
            self.logger_msg = 'logger_msg'
            self.display_msg = 'display_msg'

    def mocked_get():
        raise MockedException()

    monkeypatch.setattr(CurrencyResource, 'get_supported_currencies', mocked_get)


# ----------------------------------------------------- Tests ---------------------------------------------------------


def test_supported_currencies(test_client: FlaskClient, mock_currency_resource):
    response = test_client.get('/supported_currencies')
    assert response.status_code == 200
    assert response.json == {
        'USD': 'United States Dollar',
        'CZK': 'Czech Crown',
        'GBP': 'Great Britain Pound'
    }


@pytest.mark.parametrize('amount, input_currency, output_currency, result', [
    ('100', 'AUD', 'RUB', {
        'amount': 100.00,
        'input_currency': 'AUD',
        'output_currency': ['RUB']
    }),
    ('-10', 'CZK', 'CZK,CZK,CZK,CZK,CZK', {
        'amount': -10.00,
        'input_currency': 'CZK',
        'output_currency': ['CZK', 'CZK', 'CZK', 'CZK', 'CZK']
    }),
    ('1', 'PHP', 'JavaScript', {
        'amount': 1.00,
        'input_currency': 'PHP',
        'output_currency': ['JavaScript']
    }),
    ('', '', '', {
        'amount': 1.00,
        'input_currency': 'CZK',
        'output_currency': ['']
    }),
    ('9999999999999999999999999999999999999999999999999999999999999999999', '123', '!@$%^*(),_}{":?><', {
        'amount': 9999999999999999999999999999999999999999999999999999999999999999999.00,
        'input_currency': '123',
        'output_currency': ['!@$%^*()', '_}{":?><']
    }),
    ('abcd -- not a float', '&&&&&&&&&&&', '///////\\\\\\\\??????????', {
        'amount': 1.00,
        'input_currency': '',
        'output_currency': ['///////\\\\\\\\??????????']
    })
])
def test_convert(
        test_client: FlaskClient,
        mock_currency_converter,
        amount: str,
        input_currency: str,
        output_currency: str,
        result: dict
):
    url = '/currency_converter?'
    if amount:
        url += f'&amount={amount}'
    if input_currency:
        url += f'&input_currency={input_currency}'
    if output_currency:
        url += f'&output_currency={output_currency}'

    response = test_client.get(url)
    assert response.status_code == 200
    assert MockedCurrencyConverter.amount == result['amount']
    assert MockedCurrencyConverter.input_currency == result['input_currency']
    assert MockedCurrencyConverter.output_currency == result['output_currency']
    assert response.json == {
        'input': {
            'amount': result['amount'],
            'currency': result['input_currency']
        },
        'output': {
            'OUTPUT_CURRENCY': 123.321
        }
    }


def test_convert_symbols(test_client: FlaskClient, mock_currency_converter):
    response = test_client.get('/currency_converter?input_currency=£&output_currency=₺,₽,₦,₿')
    assert response.status_code == 200
    assert MockedCurrencyConverter.input_currency == 'GBP'
    assert MockedCurrencyConverter.output_currency == ['TRY', 'RUB', 'NGN', 'BTC']


def test_fixer_api_exception_handler(test_client: FlaskClient, monkeypatch: MonkeyPatch, caplog):
    mock_exception(monkeypatch, FixerApiException)
    response = test_client.get('/supported_currencies')
    assert response.status_code == 500
    assert caplog.record_tuples == [
        ('flask.app', logging.ERROR, 'logger_msg'),
    ]
    assert response.data.decode('utf-8') == '<h1>Internal server error</h1>' + 'display_msg'


@pytest.mark.parametrize('exception_type', [
    UnknownSymbolException,
    UnknownCurrencyException
])
def test_unknown_exception_handler(
        test_client: FlaskClient,
        monkeypatch: MonkeyPatch,
        caplog,
        exception_type
):
    mock_exception(monkeypatch, exception_type)
    response = test_client.get('/supported_currencies')
    assert response.status_code == 400
    assert caplog.record_tuples == [
        ('flask.app', logging.WARNING, 'logger_msg'),
    ]
    assert response.data.decode('utf-8') == '<h1>Bad request</h1>' + 'display_msg'
