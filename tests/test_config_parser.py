import json

from src.config_parser import Complete_Analysis_Config


def config_parser():
    config_file = open("config_file.json", "r")
    config_file_json = json.load(config_file)
    config = Complete_Analysis_Config(config_file_json)
    assert True