"""
MT5Trade exception classes
"""


class MT5TradeException(Exception):
    """
    MT5Trade base exception. Handled at the outermost level.
    All other exception types are subclasses of this exception type.
    """


class OperationalException(MT5TradeException):
    """
    Requires manual intervention and will stop the bot.
    Most of the time, this is caused by an invalid Configuration.
    """


class ConfigurationError(MT5TradeException):
    """
    Exception raised for configuration issues.
    This is a subclass of OperationalException.
    """


class InvalidOrderException(MT5TradeException):
    """
    This is returned when an order is not valid. E.g. trying to cancel a closed order
    """


class RetryableOrderError(InvalidOrderException):
    """
    This is returned when an order failed, but is retryable.
    """


class InsufficientFundsError(InvalidOrderException):
    """
    This exception is thrown when placing an order failed due to insufficient funds.
    """


class ExchangeError(MT5TradeException):
    """
    An exchange API error occurred
    """


class NetworkException(MT5TradeException):
    """
    Network connection related error.
    This could happen when an exchange is unreachable, and will usually be resolved by retrying.
    """


class DDosProtection(NetworkException):
    """
    Temporary network connection error.
    """


class TemporaryError(MT5TradeException):
    """
    Temporary network or exchange error.
    This error will usually be recovered from automatically.
    """


class StrategyError(MT5TradeException):
    """
    Errors with custom user-code deteced.
    Usually caused by errors in the strategy.
    """


class PricingError(MT5TradeException):
    """
    Pricing was not available for the requested pair.
    Could be temporary or permanent (de-listed).
    """
