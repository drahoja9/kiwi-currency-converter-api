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

    @classmethod
    def init(cls, url: str, params: dict):
        cls.url = url
        cls.params = params

    @classmethod
    def json(cls):
        pass


class MockedSupportedResponse(MockedResponse):
    supported = None

    @classmethod
    def json(cls):
        return cls.supported


class MockedRatesResponse(MockedResponse):
    rates = None

    @classmethod
    def json(cls):
        return cls.rates


@pytest.fixture
def mock_response(monkeypatch: MonkeyPatch):
    def mocked_get(*args, **kwargs) -> Type[MockedResponse]:
        if args[0] == current_app.config['FIXER_SUPPORTED_URL']:
            MockedSupportedResponse.init(args[0], kwargs['params'])
            return MockedSupportedResponse
        else:
            MockedRatesResponse.init(args[0], kwargs['params'])
            return MockedRatesResponse

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
    MockedSupportedResponse.supported = json_data

    supported = CurrencyResource.get_supported_currencies()
    assert supported == json_data['symbols']
    assert MockedSupportedResponse.url == current_app.config['FIXER_SUPPORTED_URL']
    assert MockedSupportedResponse.params == {'access_key': current_app.config['FIXER_API_KEY']}


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
    MockedSupportedResponse.supported = json_data

    with pytest.raises(FixerApiException) as e:
        CurrencyResource.get_supported_currencies()

    ref_exception = FixerApiException(url, error_code, info)
    assert e.value.display_msg == ref_exception.display_msg
    assert e.value.logger_msg == ref_exception.logger_msg


@pytest.mark.parametrize('output_currencies, fixer_api_symbols, rates, result', [
    (
            ['USD', 'CZK', 'EUR'],
            'USD,CZK,EUR,GBP',
            {'USD': 1.138, 'CZK': 25.4183, 'EUR': 1, 'GBP': 0.896032},
            {'USD': Decimal('1.270043927002606866931605697'), 'CZK': Decimal('28.36762526338344738236026116'),
             'EUR': Decimal('1.116031570301060613312779630')}
    ),
    (
            ['RUB'],
            'RUB,GBP',
            {'RUB': 72.06232, 'GBP': 0.896032, 'EUR': 1},
            {'RUB': Decimal('80.42382414913753'), 'GBP': Decimal('0.896032')}
    ),
    (
            [],
            '',
            {'USD': 1.138, 'CZK': 25.4183, 'EUR': 1, 'GBP': 0.896032, 'RUB': 72.06232},
            {'USD': Decimal('1.270043927002606866931605697'), 'CZK': Decimal('28.36762526338344738236026116'),
             'EUR': Decimal('1.116031570301060613312779630'), 'RUB': Decimal('80.42382414913753')}
    )
])
def test_get_currency_rates(
        test_app: Flask,
        mock_response,
        output_currencies: str,
        fixer_api_symbols: str,
        rates: dict,
        result: dict
):
    supported = {
        'success': True,
        'symbols': {
            'USD': 'United States Dollar',
            'CZK': 'Czech Crown',
            'GBP': 'Great Britain Pound',
            'EUR': 'Euro',
            'RUB': 'Russian Rouble'
        }
    }
    json_data = {
        'success': True,
        'rates': rates
    }
    MockedSupportedResponse.supported = supported
    MockedRatesResponse.rates = json_data

    result = CurrencyResource.get_currency_rates('GBP', output_currencies)
    assert result == result
    assert MockedSupportedResponse.url == current_app.config['FIXER_SUPPORTED_URL']
    assert MockedSupportedResponse.params == {'access_key': current_app.config['FIXER_API_KEY']}
    assert MockedRatesResponse.url == current_app.config['FIXER_LATEST_URL']
    assert MockedRatesResponse.params == {
        'access_key': current_app.config['FIXER_API_KEY'],
        'symbols': fixer_api_symbols
    }


def test_get_currency_rates_error(test_app: Flask, mock_response):
    supported = {
        'success': True,
        'symbols': {
            'USD': 'United States Dollar',
            'CZK': 'Czech Crown',
            'GBP': 'Great Britain Pound',
            'EUR': 'Euro',
            'RUB': 'Russian Rouble'
        }
    }
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
    MockedSupportedResponse.supported = supported
    MockedRatesResponse.rates = json_data

    with pytest.raises(FixerApiException) as e:
        CurrencyResource.get_currency_rates('GBP', ['EUR', 'USD'])

    ref_exception = FixerApiException(url, code, info)
    assert e.value.display_msg == ref_exception.display_msg
    assert e.value.logger_msg == ref_exception.logger_msg


def test_get_currency_rates_invalid_currency(test_app: Flask, mock_response):
    supported = {
        'success': True,
        'symbols': {
            'USD': 'United States Dollar',
            'CZK': 'Czech Crown',
            'GBP': 'Great Britain Pound',
            'EUR': 'Euro',
            'RUB': 'Russian Rouble'
        }
    }
    MockedSupportedResponse.supported = supported

    with pytest.raises(UnknownCurrencyException) as e:
        CurrencyResource.get_currency_rates('GBP', ['SOME', 'NONSENSE'])

    ref_exception = UnknownCurrencyException('SOME')
    assert e.value.display_msg == ref_exception.display_msg
    assert e.value.logger_msg == ref_exception.logger_msg
