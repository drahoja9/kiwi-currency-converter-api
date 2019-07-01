from flask.testing import FlaskClient


def test_supported_view(test_client: FlaskClient, spy_currency_resource):
    response = test_client.get('/supported_currencies')
    assert response.status_code == 200
    assert len(response.json) > 10
