import pytest
from flask.testing import FlaskClient


def test_one_to_one_conversion(test_client: FlaskClient):
    response = test_client.get('/currency_converter?amount=0.001&input_currency=GBP&output_currency=CZK')
    assert response.status_code == 200
    assert response.json['input'] == {
        'amount': 0.001,
        'currency': 'GBP'
    }
    assert 'CZK' in response.json['output']
    assert len(response.json['output']) == 1
    assert response.json['output']['CZK'] > 0.001


def test_one_to_many_conversion(test_client: FlaskClient):
    response = test_client.get('/currency_converter?amount=10.013291&input_currency=GBP&output_currency=CZK,EUR,RUB')
    assert response.status_code == 200
    assert response.json['input'] == {
        'amount': 10.013291,
        'currency': 'GBP'
    }
    assert 'CZK' in response.json['output']
    assert 'EUR' in response.json['output']
    assert 'RUB' in response.json['output']
    assert len(response.json['output']) == 3


def test_one_to_all(test_client: FlaskClient):
    response = test_client.get('/supported_currencies')
    supported_len = len(response.json.keys())

    response = test_client.get('/currency_converter?amount=5.2341&input_currency=GBP')
    assert response.status_code == 200
    assert response.json['input'] == {
        'amount': 5.2341,
        'currency': 'GBP'
    }
    assert len(response.json['output']) == supported_len - 1


def test_symbol_conversion(test_client: FlaskClient):
    response = test_client.get('/currency_converter?amount=10&input_currency=£&output_currency=€,₱,¥')
    assert response.status_code == 200
    assert response.json['input'] == {
        'amount': 10.00,
        'currency': 'GBP'
    }
    assert 'EUR' in response.json['output']
    assert 'PHP' in response.json['output']
    assert 'JPY' in response.json['output']
    assert len(response.json['output']) == 3


def test_default_values(test_client: FlaskClient):
    response = test_client.get('/supported_currencies')
    supported_len = len(response.json.keys())

    response = test_client.get('/currency_converter')
    assert response.status_code == 200
    assert response.json['input'] == {
        'amount': 1.00,
        'currency': 'CZK'
    }
    assert len(response.json['output']) == supported_len - 1


def test_one_to_many_same_values(test_client: FlaskClient):
    response = test_client.get('/currency_converter?input_currency=CZK&output_currency=EUR,EUR,RUB,EUR,EUR,RUB,EUR')
    assert response.status_code == 200
    assert response.json['input'] == {
        'amount': 1.00,
        'currency': 'CZK'
    }
    assert 'EUR' in response.json['output']
    assert 'RUB' in response.json['output']
    assert len(response.json['output']) == 2


@pytest.mark.parametrize('params', [
    'input_currency=INVALID_CURRENCY',
    'input_currency=INVALID_CURRENCY&output_currency=CZK,USD,€',
    'input_currency=GBP&output_currency=INVALID_CURRENCY',
    'output_currency=INVALID_CURRENCY'
])
def test_invalid_currency(test_client: FlaskClient, params: str):
    response = test_client.get(f'/currency_converter?{params}')
    assert response.status_code == 400
    assert (
            response.data.decode('utf-8')
            ==
            '<h1>Bad request</h1>' +
            'Unknown currency INVALID_CURRENCY. Please, revisit your request (or '
            'visit `/supported_currencies` for list of supported currencies).'
    )


@pytest.mark.parametrize('params', [
    'input_currency=%',
    'output_currency=@',
    'input_currency=|'
])
def test_invalid_symbol(test_client: FlaskClient, params: str):
    response = test_client.get(f'/currency_converter?{params}')
    assert response.status_code == 400
    assert (
            response.data.decode('utf-8')
            ==
            '<h1>Bad request</h1>' +
            f'Unknown currency symbol {params[-1]}. Please, revisit your request.'
    )


def test_invalid_amount(test_client: FlaskClient):
    response = test_client.get('/currency_converter?amount=aasdfcxzcv')
    assert response.status_code == 400
    assert (
            response.data.decode('utf-8')
            ==
            '<h1>Bad request</h1>' +
            'Invalid parameter `amount`. aasdfcxzcv is not a number'
    )
