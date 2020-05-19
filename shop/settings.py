import os

import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_path = os.path.join(BASE_DIR, 'config/shop.yaml')


def get_config(path):
    with open(path) as file:
        cfg = yaml.safe_load(file)
    return cfg


config = get_config(config_path)
