from decimal import Decimal
from typing import List, Dict

from flask import current_app as app
import requests

from api.exceptions import FixerApiException, UnknownCurrencyException


class CurrencyResource:
    @classmethod
    def _dispatch_request(cls, url: str, params: Dict[str, str]) -> requests.Response:
        access_key = app.config['FIXER_API_KEY']
        params.update({'access_key': access_key})
        response = requests.get(url, params=params)
        cls._check_response(response.json(), url)
        return response

    @classmethod
    def _check_response(cls, response: dict, url: str):
        if response['success'] is False:
            code = response['error']['code']
            info = response['error']['info']
            if code == app.config['INVALID_OUTPUT_CURRENCY']:
                raise UnknownCurrencyException(url, code, info)
            raise FixerApiException(url, code, info)

    @classmethod
    def get_supported_currencies(cls) -> Dict[str, str]:
        url = app.config['FIXER_SUPPORTED_URL']
        response = cls._dispatch_request(url, {})
        return response.json()['symbols']

    @classmethod
    def get_currency_rates(cls, input_currency: str, output_currencies: List[str]) -> Dict[str, Decimal]:
        url = app.config['FIXER_LATEST_URL']
        output_currencies.append(input_currency)
        response = cls._dispatch_request(url, {'symbols': ','.join(output_currencies)})

        def _from_eur(eur_to_target: str, eur_to_base: str) -> Decimal:
            return Decimal(eur_to_target) / Decimal(eur_to_base)

        rates = response.json()['rates']
        result = {
            k: _from_eur(v, rates[input_currency]) for k, v in rates.items() if k != input_currency
        }

        return result
