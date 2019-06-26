import pytest
from flask import Flask
from flask.testing import FlaskClient

from api import create_app


@pytest.fixture
def test_app() -> Flask:
    """

    PyTest fixture for creating instance of the Flask app for each testing function.

    :return: instance of Flask

    """
    app = create_app()

    assert app.config['TESTING'] is True
    assert app.config['DEBUG'] is False

    with app.app_context():
        yield app


@pytest.fixture
def test_client(test_app) -> FlaskClient:
    """

    PyTest fixture for creating instance of testing client derived from Flask app for each testing function.

    :param test_app: instance of Flask
    :return: instance of Flask test client

    """
    with test_app.test_client() as client:
        yield client
