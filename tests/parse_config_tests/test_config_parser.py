import json
import sys
import os

sys.path.append(os.path.abspath('./../../src'))
from src.config_parser import Complete_Analysis_Config


# This script tests config_parser.py script, which parses config files
# As input it requires config file in current dir

def config_parser():
    config_file = open("config_file.json", "r")
    config_file_json = json.load(config_file)
    config = Complete_Analysis_Config(config_file_json)
    assert True
