"""

Configuration module storing various variables for Flask app defined in api module (__init__.py).

.. module:: config
    :platform: Unix
    :synopsis: Configuration module for Flask app defined in api module (__init__.py).

.. moduleauthor:: Jakub Drahos <jakubdrahosJD@seznam.cz>

"""
import os


class BaseConfig:
    """

    Base configuration for the app.

    """
    TESTING = False
    DEBUG = False

    FIXER_LATEST_URL = 'http://data.fixer.io/api/latest'
    FIXER_SUPPORTED_URL = 'http://data.fixer.io/api/symbols'
    INVALID_OUTPUT_CURRENCY = 202
    FIXER_API_KEY = os.getenv('FIXER_API_KEY')
    if not FIXER_API_KEY:
        raise KeyError('No API key for the Fixer API (source of all the currency rates) was given!')

    SENTRY_DSN = os.getenv('SENTRY_DSN')
    CURRENCY_SYMBOLS = {
        '€': 'EUR',
        '£': 'GBP',
        '₽': 'RUB',
        '₺': 'TRY',
        '₴': 'UAH',
        '₪': 'ILS',
        '₦': 'NGN',
        '$': 'USD',
        '৳': 'BDT',
        '元': 'CNY',
        '₹': 'INR',
        '¥': 'JPY',
        '₱': 'PHP',
        '₩': 'KRW',
        '฿': 'THB',
        '₫': 'VND',
        '₿': 'BTC'
    }


class ProductionConfig(BaseConfig):
    """

    Configuration for production.

    """
    pass


class DevelopmentConfig(BaseConfig):
    """

    Configuration for development.

    """
    DEBUG = True


class TestingConfig(BaseConfig):
    """

    Configuration for testing.

    """
    TESTING = True
