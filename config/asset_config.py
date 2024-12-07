import json
import os

def get_asset_config(asset_type):
    """
    Retrieve asset-specific configurations from a JSON file.
    """
    config_file_path = os.getenv('ASSET_CONFIG_FILE_PATH', 'config/assets_config.json')
    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as config_file:
            asset_config = json.load(config_file)
            return asset_config.get(asset_type, {})
    return {}