import os


def get_api_keys():
    """
    Retrieve API keys from environment variables or a secure storage.
    """
    alpaca_api_key = os.getenv('ALPACA_API_KEY', 'your_default_api_key')
    alpaca_api_secret = os.getenv('ALPACA_API_SECRET', 'your_default_api_secret')
    return alpaca_api_key, alpaca_api_secret
