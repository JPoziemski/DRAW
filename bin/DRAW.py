import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# sys.path.append(os.path.join(os.path.dirname(sys.path[0]), 'src'))
sys.path.append(os.path.abspath('../src'))
sys.path.append(os.path.abspath('../'))

import config_parser
import global_variables
from config_exec import ConfigExec
from src.tools import Tool
import logging



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument("config_file_name", help="name of configuration file")
    args = parser.parse_args()

    config_file_path = os.path.join(global_variables.CONFIG_DIRECTORY, args.config_file_name)
    run_id = os.path.splitext(os.path.basename(args.config_file_name))[0]
    Path(os.path.join(global_variables.OUTPUT_DIRECTORY, run_id)).mkdir(parents=True, exist_ok=True)
    # os.mkdir(os.path.join(global_variables.OUTPUT_DIRECTORY, run_id))
    log_path = os.path.join(global_variables.OUTPUT_DIRECTORY, run_id, "log")
    logging.basicConfig(filename=log_path, filemode='w', format='%(asctime)s -%(levelname)s-%(message)s',
                        level=logging.DEBUG)
    logger = logging.getLogger()
    # logger.setLevel(logging.INFO)

    logger.info("Running DRAW.py")

    config_file = open(config_file_path, "r")
    config_file_json = json.load(config_file)

    logger.info("Successfully  load file: {}".format(config_file_path))

    if "run_type" in config_file_json:
        config_file_type = config_file_json["run_type"]
    else:
        logger.error("Incorrect value of 'runtype' in config file")
        raise KeyError("Missing 'run_type' in config file")

    if config_file_type == "complete_analysis":
        logger.info("Creating 'complete_analysis' config object")
        Config = config_parser.Complete_Analysis_Config(config_file_json, run_id)
    elif config_file_type == "sequence_prefiltering":
        logger.info("Creating 'sequence_prefiltering' config object")
        Config = config_parser.Sequence_Prefiltering_Config(config_file_json, run_id)
    elif config_file_type == "analysis":
        logger.info("Creating 'analysis' config object")
        Config = config_parser.Anlysis_Config(config_file_json, run_id)
    else:
        message = "Invalid 'run_type' value in config file "
        logger.error(message)
        raise ValueError(message)

    config_exec = ConfigExec(Config)
    config_exec.run()

    run_type = Config.get_config_variable("run_type")

    if run_type == "complete_analysis" or run_type == "analysis":
        try:
            run_analysis = Config.get_config_variable("run_downstream_analysis")
        except:
            run_analysis = False
        config_exec.prepare_data_for_deseq()

        if run_analysis:
            vis_path = os.path.join(config_exec.master_output_directory, "VISUALISATION")
            os.mkdir(vis_path)
            gene_count_matrix_path = os.path.join(config_exec.master_output_directory, "COUNTING",
                                                  "gene_count_matrix.csv")
            deseq2_command = "Rscript ./deseq2.R  {} {}".format(gene_count_matrix_path, run_id)
            logger.info("Preparing data to visualisation: {}".format(deseq2_command))
            process = subprocess.Popen([deseq2_command], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
            process.wait()

            Tool.check_process(process)

            vis_command = "python3 ./vis.py -id {} -dt vst".format(run_id)
            logger.info("Running visualisation {}".format(vis_command))
            process = subprocess.Popen([vis_command], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
            process.wait()

            Tool.check_process(process)
