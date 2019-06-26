from decimal import Decimal
from typing import List, Dict

from api.currencies import CurrencyResource


class CurrencyConverter:
    @classmethod
    def convert(cls, amount: float, input_currency: str, output_currency: List[str]) -> Dict[str, float]:
        decimal_amount = Decimal(amount)
        rates = CurrencyResource.get_currency_rates(input_currency, output_currency)
        cents = Decimal('0.01')
        return {
            k: float((decimal_amount * Decimal(v)).quantize(cents)) for k, v in rates.items()
        }
