from typing import List

from flask import Blueprint, request, jsonify, current_app as app

from api.exceptions import FixerApiException, UnknownSymbolException, \
    UnknownCurrencyException, InvalidAmountException, CustomException
from api.converter import CurrencyConverter
from api.currencies import CurrencyResource


currency_converter_bp = Blueprint('currency_converter', __name__)


# ------------------------------------------------------ Helpers ------------------------------------------------------


def _translate_symbol(symbol: str) -> str:
    if len(symbol) != 1:
        return symbol
    translated = app.config['CURRENCY_SYMBOLS'].get(symbol)
    if translated is None:
        raise UnknownSymbolException(symbol)
    return translated


def _get_amount() -> float:
    amount = request.args.get('amount', default=1.0, type=str)
    try:
        return float(amount)
    except ValueError:
        raise InvalidAmountException(amount)


def _get_input_currency() -> str:
    input_currency = request.args.get('input_currency', default='CZK', type=str)
    return _translate_symbol(input_currency)


def _get_output_currency() -> List[str]:
    output_currency = request.args.get('output_currency', default='', type=str)
    output_currency = output_currency.split(',')
    return list(map(_translate_symbol, output_currency))


# ----------------------------------------------- Error handlers ------------------------------------------------------

def _warning(e: CustomException) -> (str, int):
    app.logger.warning(e.logger_msg)
    return '<h1>Bad request</h1>' + e.display_msg, 400


def _error(e: CustomException) -> (str, int):
    app.logger.error(e.logger_msg)
    return '<h1>Internal server error</h1>' + e.display_msg, 500


@currency_converter_bp.errorhandler(FixerApiException)
def handle_fixer_api_exception(e: FixerApiException) -> (str, int):
    return _error(e)


@currency_converter_bp.errorhandler(UnknownSymbolException)
def handle_unknown_symbol_exception(e: UnknownSymbolException) -> (str, int):
    return _warning(e)


@currency_converter_bp.errorhandler(UnknownCurrencyException)
def handle_unknown_currency_exception(e: UnknownCurrencyException) -> (str, int):
    return _warning(e)


@currency_converter_bp.errorhandler(InvalidAmountException)
def handle_invalid_amount_exception(e: InvalidAmountException) -> (str, int):
    return _warning(e)


# -------------------------------------------------- Routes -----------------------------------------------------------


@currency_converter_bp.route('/supported_currencies', methods=['GET'])
def supported_currencies() -> (str, int):
    result = CurrencyResource.get_supported_currencies()
    return jsonify(result), 200


@currency_converter_bp.route('/currency_converter', methods=['GET'])
def convert() -> (str, int):
    amount = _get_amount()
    input_currency = _get_input_currency()
    output_currency = _get_output_currency()
    result = CurrencyConverter.convert(amount, input_currency, output_currency)
    return jsonify({
        'input': {
            'amount': amount,
            'currency': input_currency
        },
        'output': result
    }), 200
