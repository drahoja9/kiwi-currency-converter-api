# kiwi-currency-converter-api
Currency converter API based on Python's Flask microframework using Fixer API (for currency rates).


### How to run
TODO

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
