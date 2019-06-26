from decimal import Decimal
from typing import Type

import pytest
import requests
from _pytest.monkeypatch import MonkeyPatch
from flask import current_app, Flask

from api.currencies import CurrencyResource
from api.exceptions import FixerApiException, UnknownCurrencyException


# ------------------------------------------------------ Mocks --------------------------------------------------------


class MockedResponse:
    url = None
    params = None
    _json = None

    @classmethod
    def init(cls, url: str, params: dict):
        cls.url = url
        cls.params = params

    @classmethod
    def json(cls):
        return cls._json


@pytest.fixture
def mock_response(monkeypatch: MonkeyPatch):
    def mocked_get(*args, **kwargs) -> Type[MockedResponse]:
        MockedResponse.init(args[0], kwargs['params'])
        return MockedResponse

    monkeypatch.setattr(requests, 'get', mocked_get)


# ----------------------------------------------------- Tests ---------------------------------------------------------


def test_get_supported_currencies(test_app: Flask, mock_response):
    json_data = {
        'success': True,
        'symbols': {
            'USD': 'United States Dollar',
            'CZK': 'Czech Crown',
            'GBP': 'Great Britain Pound'
        }
    }
    MockedResponse._json = json_data

    supported = CurrencyResource.get_supported_currencies()
    assert supported == json_data['symbols']
    assert MockedResponse.url == current_app.config['FIXER_SUPPORTED_URL']
    assert MockedResponse.params == {'access_key': current_app.config['FIXER_API_KEY']}


def test_get_supported_currencies_error(test_app: Flask, mock_response):
    error_code = 123
    info = 'Testing error info'
    url = current_app.config['FIXER_SUPPORTED_URL']
    json_data = {
        'success': False,
        'error': {
            'code': error_code,
            'info': info
        }
    }
    MockedResponse._json = json_data

    with pytest.raises(FixerApiException) as e:
        CurrencyResource.get_supported_currencies()

    ref_exception = FixerApiException(url, error_code, info)
    assert e.value.display_msg == ref_exception.display_msg
    assert e.value.logger_msg == ref_exception.logger_msg


def test_get_currency_rates(test_app: Flask, mock_response):
    json_data = {
        'success': True,
        'rates': {
            'USD': 1.138,
            'GBP': 0.896032,
            'EUR': 1,
            'CZK': 25.4183
        }
    }
    MockedResponse._json = json_data

    rates = CurrencyResource.get_currency_rates('GBP', ['USD', 'CZK', 'EUR'])
    assert rates == {
        'USD': Decimal('1.270043927002606866931605697'),
        'CZK': Decimal('28.36762526338344738236026116'),
        'EUR': Decimal('1.116031570301060613312779630')
    }
    assert MockedResponse.url == current_app.config['FIXER_LATEST_URL']
    assert MockedResponse.params == {
        'access_key': current_app.config['FIXER_API_KEY'],
        'symbols': 'USD,CZK,EUR,GBP'
    }


def test_get_currency_rates_error(test_app: Flask, mock_response):
    url = current_app.config['FIXER_LATEST_URL']
    code = 202
    info = 'Some error info'
    json_data = {
        'success': False,
        'error': {
            'code': code,
            'info': info
        }
    }
    MockedResponse._json = json_data

    with pytest.raises(UnknownCurrencyException) as e:
        CurrencyResource.get_currency_rates('GBP', ['SOME', 'NONSENSE'])

    ref_exception = UnknownCurrencyException(url, code, info)
    assert e.value.display_msg == ref_exception.display_msg
    assert e.value.logger_msg == ref_exception.logger_msg
