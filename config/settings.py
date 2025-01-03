import os
import json
import logging


def load_configurations():
    logging.info('Loading configuration settings...')

    # Load settings from environment
    config = {
        'sentiment_weight': float(os.getenv('SENTIMENT_WEIGHT', 0.5)),
        'technical_weight': float(os.getenv('TECHNICAL_WEIGHT', 0.5)),
        'buy_threshold': float(os.getenv('BUY_THRESHOLD', 20)),
        'sell_threshold': float(os.getenv('SELL_THRESHOLD', -20)),
        'database_url': os.getenv('DATABASE_URL', 'default_database_url'),
        'alpaca_api_key': os.getenv('ALPACA_API_KEY', 'default_api_key'),
        'alpaca_api_secret': os.getenv('ALPACA_API_SECRET', 'default_api_secret'),
        'pplx_api_key': os.getenv('PPLX_API_KEY', 'default_api_key'),
        'polygon_api_key': os.getenv('POLYGON_API_KEY', 'default_api')
    }

    logging.info(config)

    # Optionally, load settings from a JSON file
    config_file_path = os.getenv('CONFIG_FILE_PATH', 'config/settings.json')
    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as config_file:
            file_config = json.load(config_file)
            config.update(file_config)

    return config
