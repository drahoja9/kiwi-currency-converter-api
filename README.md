# kiwi-currency-converter-api [![Build Status](https://travis-ci.com/drahoja9/kiwi-currency-converter-api.svg?token=AVpR3g2py5uyCcLQsLSs&branch=master)](https://travis-ci.com/drahoja9/kiwi-currency-converter-api)
Currency converter API based on Python's Flask microframework using Fixer API (for currency rates). Because of this, you need to register at https://fixer.io/signup/free (for free) and get their API key to be able to run this app. There's also an option to monitor the runtime of this API with Sentry.io, if you specify your Sentry DSN.

### How to run
You can build the image yourself or use the latest image from DockerHub

#### Building the image yourself
1. Clone this repository: `git clone git@github.com:drahoja9/kiwi-currency-converter-api.git`
2. Build the Docker image: `docker build -t currency_converter_image .`

#### Run the image
1. Run the image in a container and specify:
    * On which `host's port` should be the container's port 8000 exposed
    * `FLASK_ENV` environment variable (set to `production` | `testing` | `development`)
    * `FIXER_API_KEY` environment variable (the API key from Fixer.io)
    * `SENTRY_DSN` envrionment variable (the DSN from Sentry.io; this is optional)
    * `name` of the image (depending on the previous steps, this could be either `drahoja9/kiwi-currency-converter-api` if you want to use the DockerHub image or the name you specified when building the image in step #2)

It can look something like this:
```
docker run --name=currency_converter -p 8000:8000 -e FLASK_ENV=production -e FIXER_API_KEY=$FIXER_API_KEY -e SENTRY_DSN=$SENTRY_DSN drahoja9/kiwi-currency-converter-api
```

#### Without the Docker
You can also just run the Flask server locally.

1. Create new virtual environment: `python3.7 -m venv venv`
2. Activate the virtual environment: `source venv/bin/activate`
3. Set the `FLASK_ENV`, `FLASK_APP` (pointing to the `create_app` function in `api/__init__.py`), `FIXER_API_KEY` and possibly the `SENTRY_DSN` environment variables
4. Run the app: `flask run`

#### Tests
All tests are run automatically by the Travis CI, but you can run them manually with `pytest` command (don't forget to set the `FLASK_ENV` variable to `testing` and your Fixer API key into `FIXER_API_KEY` variable).

### How to use
The whole API consist of only 2 endpoints: `/currency_converter` and `/supported_currencies`. The latter provides a dictionary with all the supported currency codes and their full names.

```
GET /supported_currencies HTTP/1.1
```
will return something like:
```
{
  "AED": "United Arab Emirates Dirham",
  "AFN": "Afghan Afghani",
  "ALL": "Albanian Lek",
  "AMD": "Armenian Dram",
}
```

The conversion itself:
```
GET /currency_converter HTTP/1.1
```
with 3 optional parametres:
* `amount` -- any float number; defaults to 1.0
* `input_currency` -- 3-letter currency code (e.g. "USD") or 1-letter currency symbol (e.g. "£"); defaults to "CZK"
* `output_currency` -- comma-separated list of 3-leter currency codes or 1-letter currenct symbols (e.g. "EUR,₽,₱,BTC"); defaults to "", which means that the result will contain transfer rates for all supported currencies

Example usage:
```
GET /currency_converter?amount=240.16&input_currency=GBP&output_currency=USD,CZK,€,¥ HTTP/1.1
```
will result in something like:
```
{
  "input": {
    "amount": 240.16
    "currency": "GBP"
  },
  "output": {
    "USD": 304.86,
    "CZK": 6815.30,
    "EUR": 267.98,
    "JPY": 32844.12
  }
}
```
