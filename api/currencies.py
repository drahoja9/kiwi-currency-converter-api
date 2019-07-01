from decimal import Decimal
from typing import List, Dict

from flask import current_app as app
import requests

from api.exceptions import FixerApiException, UnknownCurrencyException, CacheHitSignal


class CurrencyResource:
    e_tag = None
    date = None
    supported = None

    @classmethod
    def _dispatch_request(cls, url: str, params: Dict[str, str], headers: Dict[str, str] = None) -> requests.Response:
        access_key = app.config['FIXER_API_KEY']
        response = requests.get(url, params={**params, 'access_key': access_key}, headers=headers)
        cls._check_response(response, url)
        return response

    @classmethod
    def _check_response(cls, response: requests.Response, url: str):
        if response.status_code == 200:
            response = response.json()
            if response['success'] is False:
                code = response['error']['code']
                info = response['error']['info']
                raise FixerApiException(url, code, info)
        elif response.status_code == 304:
            raise CacheHitSignal
        else:
            raise FixerApiException(response.url, response.status_code, response.reason)

    @classmethod
    def _check_currencies(cls, *currencies: str):
        supported = cls.get_supported_currencies()
        for currency in currencies:
            if currency not in supported.keys():
                raise UnknownCurrencyException(currency)

    @classmethod
    def get_supported_currencies(cls) -> Dict[str, str]:
        # Headers for ETags -- caching the previous result and reducing the response payload
        headers = {
            'If-None-Match': cls.e_tag,
            'If-Modified-Since': cls.date
        }
        url = app.config['FIXER_SUPPORTED_URL']
        try:
            response = cls._dispatch_request(url, {}, headers)
            # Following lines of code won't be executed if there's a `CacheHitSignal` -- the stored values
            # are still valid and they can be presented to the users
            cls.supported = response.json()['symbols']
            cls.e_tag = response.headers['Etag']
            cls.date = response.headers['Date']
        except CacheHitSignal:
            pass
        return cls.supported

    @classmethod
    def get_currency_rates(cls, input_currency: str, output_currencies: List[str]) -> Dict[str, Decimal]:
        url = app.config['FIXER_LATEST_URL']
        if len(output_currencies) > 0:
            output_currencies.append(input_currency)
        else:
            cls._check_currencies(input_currency)
        cls._check_currencies(*output_currencies)
        # The free plan for Fixer API does not allow changing the base currency, therefore we always get rates
        # for the EUR->(`output_currencies` + `input_currency`) conversion. For example we need the GBP->CZK
        # conversion -- from the Fixer API we get EUR->GBP and EUR->CZK -- from this we can compute GBP->CZK as
        # EUR->CZK / EUR->GBP
        response = cls._dispatch_request(url, {'symbols': ','.join(output_currencies)})

        def _from_eur(eur_to_target: str, eur_to_base: str) -> Decimal:
            return Decimal(eur_to_target) / Decimal(eur_to_base)

        rates = response.json()['rates']
        result = {
            k: _from_eur(v, rates[input_currency]) for k, v in rates.items() if k != input_currency
        }

        return result
