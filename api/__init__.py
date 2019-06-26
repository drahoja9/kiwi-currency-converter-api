"""

.. module::
    :platform: Unix
    :synopsis: The main Flask application using

.. moduleauthor:: Jakub Drahos <jakubdrahosJD@seznam.cz>

"""
import os

from flask import Flask
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration


def _load_config(app: Flask, testing_config: dict):
    config = {
        'development': 'api.config.DevelopmentConfig',
        'testing': 'api.config.TestingConfig',
        'production': 'api.config.ProductionConfig'
    }
    flask_env = os.getenv('FLASK_ENV')
    if not flask_env or flask_env not in config.keys():
        raise ValueError('Invalid FLASK_ENV environment variable!')
    # Loading configuration from config.py depending on FLASK_ENV environment variable (e.g. passed through Docker)
    app.config.from_object(config[flask_env])
    # When testing_config is present, override any previous configuration
    if testing_config:
        app.config.from_mapping(testing_config)


def _set_sentry(app: Flask):
    sentry_dsn = app.config['SENTRY_DSN']
    if sentry_dsn:
        sentry_sdk.init(dsn=sentry_dsn, integrations=[FlaskIntegration()])


def create_app(testing_config: dict = None):
    app = Flask(__name__)

    _load_config(app, testing_config)
    _set_sentry(app)

    from api.views import currency_converter_bp
    app.register_blueprint(currency_converter_bp)

    return app
