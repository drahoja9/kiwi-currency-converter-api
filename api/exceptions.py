class CustomException(Exception):
    def __init__(self, display_msg: str, logger_msg: str):
        self.display_msg = display_msg
        self.logger_msg = logger_msg


class FixerApiException(CustomException):
    def __init__(self, url: str, code: int, info: str):
        display_msg = 'An error occurred when processing your request. Please, try it later.'
        logger_msg = f'An error occurred when requesting the Fixer API. URL: {url}, CODE: {code}, INFO: {info}'
        super().__init__(display_msg, logger_msg)


class UnknownSymbolException(CustomException):
    def __init__(self, symbol: str):
        display_msg = f'Unknown currency symbol {symbol}. Please, revisit your request.'
        logger_msg = f'Unknown currency symbol: {symbol}'
        super().__init__(display_msg, logger_msg)


class UnknownCurrencyException(CustomException):
    def __init__(self, currency: str):
        display_msg = (f'Unknown currency {currency}. Please, revisit your request (or visit '
                       f'`/supported_currencies` for list of supported currencies).')
        logger_msg = f'Unknown currency: {currency}'
        super().__init__(display_msg, logger_msg)


class InvalidAmountException(CustomException):
    def __init__(self, amount: str):
        display_msg = f'Invalid parameter `amount`. {amount} is not a number'
        logger_msg = f'Could not convert string {amount} to float'
        super().__init__(display_msg, logger_msg)


class CacheHitSignal(Exception):
    pass
