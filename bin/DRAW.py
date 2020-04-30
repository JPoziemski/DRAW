import argparse
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(sys.path[0]), 'src'))
import config_parser
import logging

if __name__ == "__main__":
    logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s -%(levelname)s-%(message)s',
                        level=logging.DEBUG)
    logger = logging.getLogger()
    # logger.setLevel(logging.INFO)

    logger.info("Running DRAW.py")

    parser = argparse.ArgumentParser(description='')
    parser.add_argument("config_file_path", help="Path to configuration file")
    args = parser.parse_args()

    logger.info("Arguments parsed correctly")

    config_file = open(args.config_file_path, "r")
    config_file_json = json.load(config_file)

    logger.info("Successfully  load file: {}".format(args.config_file_path))

    if "run_type" in config_file_json:
        config_file_type = config_file_json["run_type"]
    else:
        logger.error("Incorrect value of 'runtype' in config file")
        raise KeyError("Missing 'run_type' in config file")

    if config_file_type == "complete_analysis":
        logger.info("Creating 'complete_analysis' config object")
        Config = config_parser.Complete_Analysis_Config(config_file_json)
    elif config_file_type == "sequence_prefiltering":
        logger.info("Creating 'sequence_prefiltering' config object")
        Config = config_parser.Sequence_Prefiltering_Config(config_file_json)
    elif config_file_type == "analysis":
        logger.info("Creating 'analysis' config object")
        Config = config_parser.Anlysis_Config(config_file_json)
    else:
        message = "Invalid 'run_type' value in config file "
        logger.error(message)
        raise ValueError(message)
